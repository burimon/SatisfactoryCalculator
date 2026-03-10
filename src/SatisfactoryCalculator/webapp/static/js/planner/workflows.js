import {
  DEFAULT_NODE_HEIGHT,
  DEFAULT_NODE_WIDTH,
  MIN_NODE_HEIGHT,
  MIN_NODE_WIDTH,
  WORKFLOW_VERSION,
} from "../common/constants.js";
import { recipeById } from "../common/catalog.js";
import { getConnectionCompatibility } from "./computation.js";
import { resetDragConnection } from "./state.js";

function normalizeOptionalNumber(value) {
  return value === null || value === undefined || value === "" ? null : Number(value);
}

function normalizeNodePayload(node) {
  return {
    id: String(node.id),
    recipeId: String(node.recipeId),
    targetItemId: String(node.targetItemId),
    targetRatePerMinute: Number(node.targetRatePerMinute),
    beltCapacity: normalizeOptionalNumber(node.beltCapacity),
    width: normalizeOptionalNumber(node.width) ?? DEFAULT_NODE_WIDTH,
    height: normalizeOptionalNumber(node.height) ?? DEFAULT_NODE_HEIGHT,
    x: Number(node.x),
    y: Number(node.y),
  };
}

export function workflowPayload(state) {
  return {
    version: WORKFLOW_VERSION,
    name: state.planner.workflowName,
    defaultBeltCapacity: state.planner.defaultBeltCapacity,
    nodes: state.planner.nodes.map((node) => ({
      id: node.id,
      recipeId: node.recipeId,
      targetItemId: node.targetItemId,
      targetRatePerMinute: node.targetRatePerMinute,
      beltCapacity: node.beltCapacity,
      width: node.width ?? DEFAULT_NODE_WIDTH,
      height: node.height ?? DEFAULT_NODE_HEIGHT,
      x: node.x,
      y: node.y,
    })),
    edges: state.planner.edges.map((edge) => ({
      id: edge.id,
      sourceNodeId: edge.sourceNodeId,
      targetNodeId: edge.targetNodeId,
      itemId: edge.itemId,
    })),
  };
}

export function validateWorkflowPayload(state, payload) {
  if (!payload || payload.version !== WORKFLOW_VERSION) {
    throw new Error(`Unsupported workflow version: ${payload?.version}`);
  }
  if (!Array.isArray(payload.nodes) || !Array.isArray(payload.edges)) {
    throw new Error("Workflow must contain nodes and edges arrays.");
  }

  const workflowName = typeof payload.name === "string"
    ? payload.name
    : payload.name === undefined || payload.name === null
      ? ""
      : String(payload.name);
  const defaultBeltCapacity = normalizeOptionalNumber(payload.defaultBeltCapacity);
  if (defaultBeltCapacity !== null && ![60, 120, 270, 480, 780].includes(defaultBeltCapacity)) {
    throw new Error(`Unsupported default belt capacity: ${defaultBeltCapacity}`);
  }
  if (workflowName.length > 80) {
    throw new Error("Workflow name must be 80 characters or fewer.");
  }

  const importedNodes = payload.nodes.map(normalizeNodePayload);
  const nodeIds = new Set();
  importedNodes.forEach((node) => {
    if (!node.id || nodeIds.has(node.id)) {
      throw new Error("Workflow node ids must be unique.");
    }
    nodeIds.add(node.id);
    const recipe = recipeById(state, node.recipeId);
    if (!recipe) throw new Error(`Unknown recipe id: ${node.recipeId}`);
    if (!state.items.some((item) => item.id === node.targetItemId)) {
      throw new Error(`Unknown item id: ${node.targetItemId}`);
    }
    const recipeUsesTarget =
      recipe.outputs.some((entry) => entry.item.id === node.targetItemId) ||
      recipe.inputs.some((entry) => entry.item.id === node.targetItemId);
    if (!recipeUsesTarget) {
      throw new Error(`Recipe ${node.recipeId} does not use ${node.targetItemId}`);
    }
    if (node.beltCapacity !== null && ![60, 120, 270, 480, 780].includes(node.beltCapacity)) {
      throw new Error(`Unsupported belt capacity: ${node.beltCapacity}`);
    }
    if (!Number.isFinite(node.width) || node.width < MIN_NODE_WIDTH) {
      throw new Error(`Node ${node.id} width is invalid.`);
    }
    if (!Number.isFinite(node.height) || node.height < MIN_NODE_HEIGHT) {
      throw new Error(`Node ${node.id} height is invalid.`);
    }
  });

  const importedState = { ...state, planner: { ...state.planner, nodes: importedNodes, edges: [] } };
  payload.edges.forEach((edge) => {
    if (!edge.id) throw new Error("Workflow edge id is required.");
    if (!nodeIds.has(edge.sourceNodeId)) throw new Error(`Unknown source node: ${edge.sourceNodeId}`);
    if (!nodeIds.has(edge.targetNodeId)) throw new Error(`Unknown target node: ${edge.targetNodeId}`);
    if (!state.items.some((item) => item.id === edge.itemId)) {
      throw new Error(`Unknown item id: ${edge.itemId}`);
    }
    const compatible = getConnectionCompatibility(importedState, edge.sourceNodeId, edge.targetNodeId);
    if (!compatible.some((item) => item.id === edge.itemId)) {
      throw new Error(
        `Nodes ${edge.sourceNodeId} and ${edge.targetNodeId} are not compatible for ${edge.itemId}`
      );
    }
    importedState.planner.edges.push({
      id: String(edge.id),
      sourceNodeId: String(edge.sourceNodeId),
      targetNodeId: String(edge.targetNodeId),
      itemId: String(edge.itemId),
    });
  });
}

export function importWorkflowIntoState(state, payload) {
  validateWorkflowPayload(state, payload);
  state.planner.workflowName =
    typeof payload.name === "string" && payload.name.trim() ? payload.name.trim() : "Untitled Workflow";
  state.planner.defaultBeltCapacity = normalizeOptionalNumber(payload.defaultBeltCapacity);
  state.planner.nodes = payload.nodes.map(normalizeNodePayload);
  state.planner.edges = payload.edges.map((edge) => ({
    id: String(edge.id),
    sourceNodeId: String(edge.sourceNodeId),
    targetNodeId: String(edge.targetNodeId),
    itemId: String(edge.itemId),
  }));
  state.planner.selectedNodeId = state.planner.nodes[0]?.id ?? null;
  state.planner.popup.visible = false;
  state.planner.targetPopup.visible = false;
  resetDragConnection(state.planner);
  state.planner.nextNodeNumber = Math.max(
    0,
    ...state.planner.nodes.map((node) => Number(node.id.split("_")[1]) || 0)
  ) + 1;
  state.planner.nextEdgeNumber = Math.max(
    0,
    ...state.planner.edges.map((edge) => Number(edge.id.split("_")[1]) || 0)
  ) + 1;
}
