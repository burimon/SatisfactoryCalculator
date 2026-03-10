import { fetchJson, postJson } from "../api/client.js";
import { findItemByName, itemNameById, recipeById } from "../common/catalog.js";
import { DEFAULT_NODE_HEIGHT, DEFAULT_NODE_WIDTH } from "../common/constants.js";
import { recipeEntryRatePerMinute, buildPlannerAllocationMap, buildPlannerComputedMap, getConnectionCompatibility, getPlannerNodeComputed } from "./computation.js";
import { bindPlannerControls } from "./controls.js";
import { bindPlannerInteractions } from "./interactions.js";
import { renderPlannerEdges } from "./render-edges.js";
import { renderPlannerNodes } from "./render-nodes.js";
import { renderPlannerNetBalance, renderPlannerOptions, renderPlannerPopup, renderPlannerSummary, renderTargetPopup } from "./render-panels.js";
import { createPlannerViewport } from "./viewport.js";
import { createPlannerPopup, createTargetPopup, getPlannerNode, newEdgeId, newNodeId, resetDragConnection } from "./state.js";
import { importWorkflowIntoState, workflowPayload } from "./workflows.js";

export function createPlannerController({ els, setMode, setStatus, state }) {
  const viewport = createPlannerViewport({
    plannerState: state.planner,
    workspaceEl: els.plannerWorkspace,
    worldEl: els.plannerWorld,
  });

  function renderOptions() {
    renderPlannerOptions({ state, els });
  }

  function renderSummary() {
    viewport.applyTransform();
    renderPlannerSummary({ state, els });
  }

  function renderPopups() {
    renderPlannerPopup({ state, els });
    renderTargetPopup({ state, els });
  }

  function renderEdges() {
    const computedMap = buildPlannerComputedMap(state);
    const allocationMap = buildPlannerAllocationMap(state, computedMap);
    renderPlannerEdges({ state, els, allocationMap });
  }

  function render() {
    renderSummary();
    renderPlannerNetBalance({
      state,
      els,
      onSort: setPlannerNetBalanceSort,
    });
    const computedMap = buildPlannerComputedMap(state);
    const allocationMap = buildPlannerAllocationMap(state, computedMap);
    renderPlannerNodes({ state, els, computedMap, allocationMap });
    renderPlannerEdges({ state, els, allocationMap });
    renderPopups();
  }

  function closePlannerPopup() {
    state.planner.popup = createPlannerPopup();
    renderPlannerPopup({ state, els });
  }

  function openPlannerPopup(clientX, clientY) {
    const workspaceRect = els.plannerWorkspace.getBoundingClientRect();
    const canvasPoint = viewport.screenToWorld({ x: clientX, y: clientY });
    state.planner.popup.visible = true;
    state.planner.popup.canvasX = canvasPoint.x;
    state.planner.popup.canvasY = canvasPoint.y;
    state.planner.popup.screenX = Math.max(12, clientX - workspaceRect.left);
    state.planner.popup.screenY = Math.max(12, clientY - workspaceRect.top);
    state.planner.popup.outputItemId = null;
    state.planner.popup.candidateRecipes = [];
    state.planner.popup.selectedRecipeId = null;
    renderPlannerPopup({ state, els });
    els.plannerPopupOutputInput.focus();
  }

  function closeTargetPopup() {
    state.planner.targetPopup = createTargetPopup();
    renderTargetPopup({ state, els });
  }

  function openTargetPopup(nodeId, itemId, clientX, clientY) {
    const workspaceRect = els.plannerWorkspace.getBoundingClientRect();
    state.planner.targetPopup.visible = true;
    state.planner.targetPopup.nodeId = nodeId;
    state.planner.targetPopup.itemId = itemId;
    state.planner.targetPopup.screenX = Math.max(12, clientX - workspaceRect.left);
    state.planner.targetPopup.screenY = Math.max(12, clientY - workspaceRect.top);
    renderTargetPopup({ state, els });
    els.plannerTargetPopupRate.focus();
    els.plannerTargetPopupRate.select();
  }

  function resetPlannerWorkflow() {
    state.planner.workflowName = "Blank";
    state.planner.nodes = [];
    state.planner.edges = [];
    state.planner.selectedNodeId = null;
    state.planner.selectedWorkflowFilename = "";
    state.planner.nextNodeNumber = 1;
    state.planner.nextEdgeNumber = 1;
    closePlannerPopup();
    closeTargetPopup();
    resetDragConnection(state.planner);
    renderOptions();
    render();
    setMode("planner");
    setStatus("Started a new blank plan.");
  }

  async function refreshWorkflows(preferredFilename = null) {
    const payload = await fetchJson("/api/workflows");
    state.planner.workflowDirectory = payload.directory ?? "";
    state.planner.availableWorkflows = Array.isArray(payload.files) ? payload.files : [];
    state.planner.selectedWorkflowFilename = preferredFilename &&
      state.planner.availableWorkflows.some((workflow) => workflow.filename === preferredFilename)
      ? preferredFilename
      : state.planner.availableWorkflows.some(
          (workflow) => workflow.filename === state.planner.selectedWorkflowFilename
        )
        ? state.planner.selectedWorkflowFilename
        : state.planner.availableWorkflows[0]?.filename ?? "";
    renderOptions();
  }

  async function findPlannerPopupRecipes() {
    const item = findItemByName(state, els.plannerPopupOutputInput.value);
    if (!item) {
      setStatus("Choose a valid output item for the new node.");
      return;
    }
    state.planner.popup.outputItemId = item.id;
    state.planner.popup.candidateRecipes = await fetchJson(`/api/recipes/by-output/${item.id}`);
    state.planner.popup.selectedRecipeId = state.planner.popup.candidateRecipes[0]?.id ?? null;
    renderPlannerPopup({ state, els });
  }

  function addPlannerNodeAt(recipeId, targetItemId, canvasX, canvasY) {
    const recipe = recipeById(state, recipeId);
    if (!recipe) return;
    const targetRatePerMinute = recipeEntryRatePerMinute(recipe, targetItemId) ?? 0;
    const columnOffset = state.planner.nodes.length % 3;
    const rowOffset = Math.floor(state.planner.nodes.length / 3);
    const node = {
      id: newNodeId(state.planner),
      recipeId,
      targetItemId,
      targetRatePerMinute,
      beltCapacity: null,
      x: canvasX ?? 28 + columnOffset * 300,
      y: canvasY ?? 28 + rowOffset * 260,
      width: DEFAULT_NODE_WIDTH,
      height: DEFAULT_NODE_HEIGHT,
    };
    state.planner.nodes.push(node);
    state.planner.selectedNodeId = node.id;
    closePlannerPopup();
    render();
    setStatus(`Added planner node for ${recipe.name}.`);
  }

  function removePlannerNode(nodeId) {
    state.planner.nodes = state.planner.nodes.filter((node) => node.id !== nodeId);
    state.planner.edges = state.planner.edges.filter(
      (edge) => edge.sourceNodeId !== nodeId && edge.targetNodeId !== nodeId
    );
    if (state.planner.selectedNodeId === nodeId) {
      state.planner.selectedNodeId = state.planner.nodes[0]?.id ?? null;
    }
    render();
  }

  function updatePlannerNode(nodeId, changes) {
    const node = getPlannerNode(state.planner, nodeId);
    if (!node) return;
    Object.assign(node, changes);
    render();
  }

  function selectNode(nodeId) {
    state.planner.selectedNodeId = nodeId;
    render();
  }

  function addPlannerConnection(sourceNodeId, targetNodeId, itemId) {
    if (!sourceNodeId || !targetNodeId || sourceNodeId === targetNodeId || !itemId) {
      setStatus("Choose valid source, target, and item values.");
      return;
    }
    if (
      state.planner.edges.some(
        (edge) =>
          edge.sourceNodeId === sourceNodeId &&
          edge.targetNodeId === targetNodeId &&
          edge.itemId === itemId
      )
    ) {
      setStatus("That connection already exists.");
      return;
    }
    const compatible = getConnectionCompatibility(state, sourceNodeId, targetNodeId);
    if (!compatible.some((item) => item.id === itemId)) {
      setStatus("Selected nodes are not compatible for that item.");
      return;
    }
    state.planner.edges.push({
      id: newEdgeId(state.planner),
      sourceNodeId,
      targetNodeId,
      itemId,
    });
    render();
    setStatus(`Connected ${itemNameById(state, itemId)} between nodes.`);
  }

  function removePlannerConnection(edgeId) {
    state.planner.edges = state.planner.edges.filter((edge) => edge.id !== edgeId);
    render();
  }

  function setPlannerNetBalanceSort(key) {
    if (state.planner.netBalanceSort.key === key) {
      state.planner.netBalanceSort.direction =
        state.planner.netBalanceSort.direction === "asc" ? "desc" : "asc";
    } else {
      state.planner.netBalanceSort.key = key;
      state.planner.netBalanceSort.direction = key === "net" ? "desc" : "asc";
    }
    render();
  }

  async function exportWorkflow() {
    const result = await postJson("/api/workflows", workflowPayload(state));
    await refreshWorkflows(result.filename);
    renderSummary();
    setStatus(`Exported workflow JSON to ${result.path}.`);
  }

  async function importSelectedWorkflow() {
    const filename = els.plannerSavedWorkflows.value || state.planner.selectedWorkflowFilename;
    if (!filename) {
      setStatus("Choose a saved workflow to import.");
      return;
    }
    const payload = await fetchJson(`/api/workflows/${encodeURIComponent(filename)}`);
    importWorkflowIntoState(state, payload);
    state.planner.selectedWorkflowFilename = filename;
    renderOptions();
    render();
    setMode("planner");
    setStatus(`Imported workflow JSON from ${filename}.`);
  }

  bindPlannerControls({
    controller: {
      addPlannerNodeAt,
      closePlannerPopup,
      closeTargetPopup,
      exportWorkflow,
      findPlannerPopupRecipes,
      importSelectedWorkflow,
      refreshWorkflows,
      render,
      renderOptions,
      renderSummary,
      resetPlannerWorkflow,
      updatePlannerNode,
    },
    els,
    setStatus,
    state,
  });
  bindPlannerInteractions({ controller: {
    addPlannerConnection,
    closePlannerPopup,
    closeTargetPopup,
    getPlannerNodeComputed: (node) => getPlannerNodeComputed(state, node),
    itemNameById: (itemId) => itemNameById(state, itemId),
    openPlannerPopup,
    openTargetPopup,
    removePlannerConnection,
    removePlannerNode,
    render,
    renderEdges,
    renderSummary,
    selectNode,
    updatePlannerNode,
  }, els, setStatus, state, viewport });

  return {
    closePlannerPopup,
    closeTargetPopup,
    exportWorkflow,
    findPlannerPopupRecipes,
    getPlannerNodeComputed: (node) => getPlannerNodeComputed(state, node),
    importSelectedWorkflow,
    itemNameById: (itemId) => itemNameById(state, itemId),
    openPlannerPopup,
    openTargetPopup,
    refreshWorkflows,
    render,
    renderEdges,
    renderOptions,
    renderSummary,
    resetPlannerWorkflow,
  };
}
