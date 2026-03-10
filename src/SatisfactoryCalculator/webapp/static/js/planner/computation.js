import { recipeById } from "../common/catalog.js";
import { clampPercentage, formatAmount, isPowerItem, perMachineRate } from "../common/format.js";
import { getPlannerNode, plannerNodeBeltCapacity } from "./state.js";

export function recipeEntryRatePerMinute(recipe, itemId) {
  const output = recipe.outputs.find((entry) => entry.item.id === itemId);
  if (output) {
    return isPowerItem(itemId) ? output.amount : (output.amount * 60) / recipe.duration_seconds;
  }
  const input = recipe.inputs.find((entry) => entry.item.id === itemId);
  if (input) {
    return isPowerItem(itemId) ? input.amount : (input.amount * 60) / recipe.duration_seconds;
  }
  return null;
}

export function scaledRecipeRates(recipe, targetItemId, targetRatePerMinute, beltCapacity = null) {
  const targetBaseRate = recipeEntryRatePerMinute(recipe, targetItemId);
  if (!targetBaseRate) {
    throw new Error(`Recipe ${recipe.id} does not use ${targetItemId}`);
  }

  const multiplier = targetRatePerMinute / targetBaseRate;
  const entryRatePerMinute = (entry) =>
    isPowerItem(entry.item.id) ? entry.amount : (entry.amount * 60) / recipe.duration_seconds;
  const scaleEntries = (entries) =>
    entries.map((entry) => ({
      item: entry.item,
      amount_per_minute: entryRatePerMinute(entry) * multiplier,
    }));
  const scaledRequirements = [...recipe.inputs, ...recipe.outputs].map((entry) => {
    const baseRate = entryRatePerMinute(entry);
    const cappedRate = perMachineRate(entry.item.id, baseRate, beltCapacity);
    const totalRate = baseRate * multiplier;
    return cappedRate === 0 ? 0 : totalRate / cappedRate;
  });

  return {
    multiplier,
    machine_count: scaledRequirements.length ? Math.max(...scaledRequirements) : 0,
    per_machine_rate: perMachineRate(targetItemId, targetBaseRate, beltCapacity),
    requested_target_rate: targetRatePerMinute,
    inputs: scaleEntries(recipe.inputs),
    outputs: scaleEntries(recipe.outputs),
  };
}

export function getItemRate(entries, itemId) {
  return entries.find((entry) => entry.item.id === itemId)?.amount_per_minute ?? 0;
}

export function buildPlannerComputedMap(state) {
  const computedById = new Map();
  state.planner.nodes.forEach((node) => {
    const recipe = recipeById(state, node.recipeId);
    if (!recipe) return;
    computedById.set(node.id, {
      recipe,
      ...scaledRecipeRates(
        recipe,
        node.targetItemId,
        node.targetRatePerMinute,
        plannerNodeBeltCapacity(state, node)
      ),
    });
  });
  return computedById;
}

export function getPlannerNodeComputed(state, node, computedMap = null) {
  if (!node) return null;
  const plannerComputed = computedMap ?? buildPlannerComputedMap(state);
  return plannerComputed.get(node.id) ?? null;
}

export function calculateAllocatedRate(state, edge, computedMap) {
  const sourceComputed = computedMap.get(edge.sourceNodeId);
  const targetComputed = computedMap.get(edge.targetNodeId);
  if (!sourceComputed || !targetComputed) {
    return {
      sourceRate: 0,
      targetRate: 0,
      incomingEdgeCount: 0,
      outgoingEdgeCount: 0,
      totalIncomingSourceRate: 0,
      totalOutgoingTargetRate: 0,
      incomingShare: 0,
      outgoingShare: 0,
      allocatedRate: 0,
      delta: 0,
      status: "balanced",
    };
  }

  const sourceRate = getItemRate(sourceComputed.outputs, edge.itemId);
  const targetRate = getItemRate(targetComputed.inputs, edge.itemId);
  const incomingEdges = state.planner.edges.filter(
    (candidate) =>
      candidate.targetNodeId === edge.targetNodeId && candidate.itemId === edge.itemId
  );
  const outgoingEdges = state.planner.edges.filter(
    (candidate) =>
      candidate.sourceNodeId === edge.sourceNodeId && candidate.itemId === edge.itemId
  );
  const totalIncomingSourceRate = incomingEdges.reduce((total, candidate) => {
    const candidateComputed = computedMap.get(candidate.sourceNodeId);
    return total + getItemRate(candidateComputed?.outputs ?? [], edge.itemId);
  }, 0);
  const totalOutgoingTargetRate = outgoingEdges.reduce((total, candidate) => {
    const candidateComputed = computedMap.get(candidate.targetNodeId);
    return total + getItemRate(candidateComputed?.inputs ?? [], edge.itemId);
  }, 0);
  const incomingLimitedTotal = Math.min(totalIncomingSourceRate, targetRate);
  const outgoingLimitedTotal = Math.min(sourceRate, totalOutgoingTargetRate);
  const incomingShare = incomingEdges.length > 1 && totalIncomingSourceRate > 0
    ? incomingLimitedTotal * (sourceRate / totalIncomingSourceRate)
    : targetRate;
  const outgoingShare = outgoingEdges.length > 1 && totalOutgoingTargetRate > 0
    ? outgoingLimitedTotal * (targetRate / totalOutgoingTargetRate)
    : sourceRate;
  const allocatedRate = Math.min(incomingShare, outgoingShare);
  const delta = sourceRate - targetRate;

  return {
    sourceRate,
    targetRate,
    incomingEdgeCount: incomingEdges.length,
    outgoingEdgeCount: outgoingEdges.length,
    totalIncomingSourceRate,
    totalOutgoingTargetRate,
    incomingShare,
    outgoingShare,
    allocatedRate,
    delta,
    status: delta > 0.01 ? "source_surplus" : delta < -0.01 ? "target_shortage" : "balanced",
  };
}

export function buildPlannerAllocationMap(state, computedMap) {
  return new Map(
    state.planner.edges.map((edge) => [edge.id, calculateAllocatedRate(state, edge, computedMap)])
  );
}

export function buildNodeBalanceRows(state, node, computed, allocationMap, portType) {
  const entries = portType === "input" ? computed.inputs : computed.outputs;
  return entries.map((entry) => {
    const connectedRate = state.planner.edges.reduce((total, edge) => {
      const matchesNode = portType === "input"
        ? edge.targetNodeId === node.id
        : edge.sourceNodeId === node.id;
      if (!matchesNode || edge.itemId !== entry.item.id) {
        return total;
      }
      return total + (allocationMap.get(edge.id)?.allocatedRate ?? 0);
    }, 0);
    const expectedRate = entry.amount_per_minute;
    const delta = portType === "input"
      ? connectedRate - expectedRate
      : expectedRate - connectedRate;
    return {
      itemName: entry.item.name,
      connectedRate,
      expectedRate,
      status: delta > 0.01 ? "source_surplus" : delta < -0.01 ? "target_shortage" : "balanced",
      progress: expectedRate <= 0
        ? 100
        : clampPercentage((Math.min(connectedRate, expectedRate) / expectedRate) * 100),
    };
  });
}

export function buildPlannerNetBalanceRows(state, computedMap = null) {
  const plannerComputed = computedMap ?? buildPlannerComputedMap(state);
  const totals = new Map();

  const ensureRow = (item) => {
    const existing = totals.get(item.id);
    if (existing) return existing;
    const row = { itemId: item.id, itemName: item.name, producedRate: 0, consumedRate: 0, netRate: 0 };
    totals.set(item.id, row);
    return row;
  };

  state.planner.nodes.forEach((node) => {
    const computed = plannerComputed.get(node.id);
    if (!computed) return;
    computed.outputs.forEach((entry) => {
      ensureRow(entry.item).producedRate += entry.amount_per_minute;
    });
    computed.inputs.forEach((entry) => {
      ensureRow(entry.item).consumedRate += entry.amount_per_minute;
    });
  });

  return [...totals.values()]
    .map((row) => ({ ...row, netRate: row.producedRate - row.consumedRate }))
    .sort((left, right) => {
      const direction = state.planner.netBalanceSort.direction === "asc" ? 1 : -1;
      if (state.planner.netBalanceSort.key === "net") {
        return direction * (left.netRate - right.netRate) || left.itemName.localeCompare(right.itemName);
      }
      return direction * left.itemName.localeCompare(right.itemName) || right.netRate - left.netRate;
    });
}

export function isPlannerNetBalanced(netRate) {
  return Math.abs(netRate) <= 0.01;
}

export function plannerNetBalanceClass(netRate) {
  if (netRate > 0.01) return "net-positive";
  if (netRate < -0.01) return "net-negative";
  return "net-neutral";
}

export function plannerNetBalanceValue(netRate) {
  return `${netRate > 0.01 ? "+" : ""}${formatAmount(netRate)}`;
}

export function getConnectionCompatibility(state, sourceNodeId, targetNodeId, computedMap = null) {
  const plannerComputed = computedMap ?? buildPlannerComputedMap(state);
  const sourceComputed = getPlannerNodeComputed(
    state,
    getPlannerNode(state.planner, sourceNodeId),
    plannerComputed
  );
  const targetComputed = getPlannerNodeComputed(
    state,
    getPlannerNode(state.planner, targetNodeId),
    plannerComputed
  );
  if (!sourceComputed || !targetComputed) return [];
  return sourceComputed.outputs
    .filter((output) => getItemRate(targetComputed.inputs, output.item.id) > 0)
    .map((output) => output.item);
}
