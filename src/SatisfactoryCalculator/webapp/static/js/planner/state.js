export function createPlannerPopup() {
  return {
    visible: false,
    canvasX: 0,
    canvasY: 0,
    screenX: 12,
    screenY: 12,
    outputItemId: null,
    candidateRecipes: [],
    selectedRecipeId: null,
  };
}

export function createTargetPopup() {
  return {
    visible: false,
    nodeId: null,
    itemId: null,
    screenX: 12,
    screenY: 12,
  };
}

export function createDragConnection() {
  return {
    active: false,
    sourceNodeId: null,
    itemId: null,
    startX: 0,
    startY: 0,
    currentX: 0,
    currentY: 0,
    validTargetNodeId: null,
  };
}

export function createPlannerState() {
  return {
    workflowName: "Untitled Workflow",
    workflowDirectory: "",
    availableWorkflows: [],
    selectedWorkflowFilename: "",
    selectedOutputItemId: null,
    defaultBeltCapacity: 60,
    candidateRecipes: [],
    popup: createPlannerPopup(),
    targetPopup: createTargetPopup(),
    dragConnection: createDragConnection(),
    nodes: [],
    edges: [],
    netBalanceSort: {
      key: "item",
      direction: "asc",
    },
    hideBalancedNetItems: false,
    panX: 0,
    panY: 0,
    zoom: 1,
    selectedNodeId: null,
    nextNodeNumber: 1,
    nextEdgeNumber: 1,
  };
}

export function resetDragConnection(plannerState) {
  plannerState.dragConnection = createDragConnection();
}

export function getPlannerNode(plannerState, nodeId) {
  return plannerState.nodes.find((node) => node.id === nodeId) ?? null;
}

export function newNodeId(plannerState) {
  const id = `node_${plannerState.nextNodeNumber}`;
  plannerState.nextNodeNumber += 1;
  return id;
}

export function newEdgeId(plannerState) {
  const id = `edge_${plannerState.nextEdgeNumber}`;
  plannerState.nextEdgeNumber += 1;
  return id;
}

export function selectedWorkflowRecord(plannerState) {
  return plannerState.availableWorkflows.find(
    (workflow) => workflow.filename === plannerState.selectedWorkflowFilename
  ) ?? null;
}

export function plannerNodeBeltCapacity(state, node) {
  return node.beltCapacity ?? state.planner.defaultBeltCapacity ?? null;
}
