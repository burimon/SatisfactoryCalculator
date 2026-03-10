import { MIN_NODE_HEIGHT, MIN_NODE_WIDTH } from "../common/constants.js";
import { buildPlannerComputedMap, getItemRate } from "./computation.js";
import { portAnchorInWorld } from "./geometry.js";
import { getPlannerNode, resetDragConnection } from "./state.js";

function dragTargetFromClientPoint(clientX, clientY, itemId, sourceNodeId) {
  const element = document.elementFromPoint(clientX, clientY);
  const port = element?.closest?.('[data-port-type="input"]');
  if (!port || port.dataset.portItemId !== itemId || port.dataset.portNodeId === sourceNodeId) {
    return null;
  }
  return { nodeId: port.dataset.portNodeId, itemId: port.dataset.portItemId };
}

export function bindPlannerInteractions({ controller, els, setStatus, state, viewport }) {
  els.plannerConnectionLabels.addEventListener("click", (event) => {
    const button = event.target.closest("[data-remove-edge-id]");
    if (!button) return;
    event.stopPropagation();
    controller.removePlannerConnection(button.dataset.removeEdgeId);
  });

  els.plannerNodeLayer.addEventListener("click", (event) => {
    const removeNodeButton = event.target.closest("[data-remove-node-id]");
    if (removeNodeButton) {
      event.stopPropagation();
      controller.removePlannerNode(removeNodeButton.dataset.removeNodeId);
      return;
    }

    const inputPort = event.target.closest('[data-port-type="input"]');
    if (inputPort) {
      event.stopPropagation();
      const node = getPlannerNode(state.planner, inputPort.dataset.portNodeId);
      const computed = controller.getPlannerNodeComputed(node);
      if (!node || !computed) return;
      const currentRate = getItemRate(computed.inputs, inputPort.dataset.portItemId);
      controller.updatePlannerNode(node.id, {
        targetItemId: inputPort.dataset.portItemId,
        targetRatePerMinute: currentRate,
      });
      controller.openTargetPopup(node.id, inputPort.dataset.portItemId, event.clientX, event.clientY);
      return;
    }

    const nodeEl = event.target.closest(".planner-node");
    if (!nodeEl || event.target.closest("button, input")) {
      return;
    }
    controller.selectNode(nodeEl.dataset.nodeId);
  });

  els.plannerNodeLayer.addEventListener("pointerdown", (event) => {
    if (event.button !== 0) return;

    const resizeHandle = event.target.closest("[data-resize-node]");
    if (resizeHandle) {
      const node = getPlannerNode(state.planner, resizeHandle.dataset.resizeNode);
      const nodeEl = resizeHandle.closest(".planner-node");
      if (!node || !nodeEl) return;
      event.stopPropagation();
      const edge = resizeHandle.dataset.resizeEdge;
      const startPoint = viewport.screenToWorld({ x: event.clientX, y: event.clientY });
      const startNode = {
        x: node.x,
        y: node.y,
        width: node.width ?? nodeEl.offsetWidth,
        height: node.height ?? nodeEl.offsetHeight,
      };
      resizeHandle.setPointerCapture(event.pointerId);
      resizeHandle.onpointermove = (moveEvent) => {
        const point = viewport.screenToWorld({ x: moveEvent.clientX, y: moveEvent.clientY });
        const dx = point.x - startPoint.x;
        const dy = point.y - startPoint.y;
        if (edge.includes("right")) {
          node.width = Math.max(MIN_NODE_WIDTH, startNode.width + dx);
        }
        if (edge.includes("left")) {
          const nextWidth = Math.max(MIN_NODE_WIDTH, startNode.width - dx);
          node.x = startNode.x + (startNode.width - nextWidth);
          node.width = nextWidth;
        }
        if (edge.includes("bottom")) {
          node.height = Math.max(MIN_NODE_HEIGHT, startNode.height + dy);
        }
        if (edge.includes("top")) {
          const nextHeight = Math.max(MIN_NODE_HEIGHT, startNode.height - dy);
          node.y = startNode.y + (startNode.height - nextHeight);
          node.height = nextHeight;
        }
        nodeEl.style.left = `${node.x}px`;
        nodeEl.style.top = `${node.y}px`;
        nodeEl.style.width = `${node.width}px`;
        nodeEl.style.height = `${node.height}px`;
        controller.renderEdges();
      };
      resizeHandle.onpointerup = () => {
        resizeHandle.onpointermove = null;
        resizeHandle.onpointerup = null;
        controller.render();
      };
      return;
    }

    const outputPort = event.target.closest('[data-port-type="output"]');
    if (outputPort) {
      event.stopPropagation();
      controller.closeTargetPopup();
      const node = getPlannerNode(state.planner, outputPort.dataset.portNodeId);
      const nodeEl = outputPort.closest(".planner-node");
      if (!node || !nodeEl) return;
      const anchor = portAnchorInWorld(node, nodeEl, outputPort, "right");
      state.planner.dragConnection = {
        active: true,
        sourceNodeId: outputPort.dataset.portNodeId,
        itemId: outputPort.dataset.portItemId,
        startX: anchor.x,
        startY: anchor.y,
        currentX: anchor.x,
        currentY: anchor.y,
        validTargetNodeId: null,
      };
      const startClientX = event.clientX;
      const startClientY = event.clientY;
      outputPort.setPointerCapture(event.pointerId);
      outputPort.onpointermove = (moveEvent) => {
        const point = viewport.screenToWorld({ x: moveEvent.clientX, y: moveEvent.clientY });
        state.planner.dragConnection.currentX = point.x;
        state.planner.dragConnection.currentY = point.y;
        const target = dragTargetFromClientPoint(
          moveEvent.clientX,
          moveEvent.clientY,
          outputPort.dataset.portItemId,
          outputPort.dataset.portNodeId
        );
        state.planner.dragConnection.validTargetNodeId = target?.nodeId ?? null;
        setStatus(
          target
            ? `Release to connect ${controller.itemNameById(outputPort.dataset.portItemId)}.`
            : "Drag to a matching input to create a connection."
        );
        controller.renderEdges();
      };
      outputPort.onpointerup = (upEvent) => {
        const moved = Math.abs(upEvent.clientX - startClientX) > 4 ||
          Math.abs(upEvent.clientY - startClientY) > 4;
        const target = dragTargetFromClientPoint(
          upEvent.clientX,
          upEvent.clientY,
          outputPort.dataset.portItemId,
          outputPort.dataset.portNodeId
        );
        if (moved) {
          if (target) {
            controller.addPlannerConnection(outputPort.dataset.portNodeId, target.nodeId, target.itemId);
          } else {
            setStatus("Release on a matching input to create a connection.");
          }
        } else {
          const computed = controller.getPlannerNodeComputed(node);
          if (computed) {
            const currentRate = getItemRate(computed.outputs, outputPort.dataset.portItemId);
            controller.updatePlannerNode(node.id, {
              targetItemId: outputPort.dataset.portItemId,
              targetRatePerMinute: currentRate,
            });
            controller.openTargetPopup(
              node.id,
              outputPort.dataset.portItemId,
              upEvent.clientX,
              upEvent.clientY
            );
          }
        }
        resetDragConnection(state.planner);
        outputPort.onpointermove = null;
        outputPort.onpointerup = null;
        controller.render();
      };
      return;
    }

    const header = event.target.closest(".planner-node-header");
    if (!header || event.target.closest("[data-remove-node-id]")) {
      return;
    }
    const nodeEl = header.closest(".planner-node");
    const node = getPlannerNode(state.planner, nodeEl.dataset.nodeId);
    if (!node) return;
    state.planner.selectedNodeId = node.id;
    const startPoint = viewport.screenToWorld({ x: event.clientX, y: event.clientY });
    const offsetX = startPoint.x - node.x;
    const offsetY = startPoint.y - node.y;
    header.setPointerCapture(event.pointerId);
    header.onpointermove = (moveEvent) => {
      const point = viewport.screenToWorld({ x: moveEvent.clientX, y: moveEvent.clientY });
      node.x = point.x - offsetX;
      node.y = point.y - offsetY;
      nodeEl.style.left = `${node.x}px`;
      nodeEl.style.top = `${node.y}px`;
      controller.renderEdges();
    };
    header.onpointerup = () => {
      header.onpointermove = null;
      header.onpointerup = null;
      controller.render();
    };
  });

  let isPanning = false;
  let panPointerId = null;
  let panStartX = 0;
  let panStartY = 0;

  els.plannerWorkspace.addEventListener(
    "wheel",
    (event) => {
      event.preventDefault();
      viewport.zoomAroundScreenPoint(event.clientX, event.clientY, event.deltaY < 0 ? 0.1 : -0.1);
      controller.renderSummary();
    },
    { passive: false }
  );

  els.plannerWorkspace.addEventListener("pointerdown", (event) => {
    if (event.button !== 0) return;
    if (
      event.target.closest(".planner-node") ||
      event.target.closest(".planner-add-popup") ||
      event.target.closest(".planner-target-popup") ||
      event.target.closest(".planner-connection-label") ||
      event.target.closest("button, input, select, option, label")
    ) {
      return;
    }
    isPanning = true;
    panPointerId = event.pointerId;
    panStartX = event.clientX - state.planner.panX;
    panStartY = event.clientY - state.planner.panY;
    els.plannerWorkspace.setPointerCapture(event.pointerId);
  });

  els.plannerWorkspace.addEventListener("pointermove", (event) => {
    if (!isPanning || event.pointerId !== panPointerId) return;
    state.planner.panX = event.clientX - panStartX;
    state.planner.panY = event.clientY - panStartY;
    viewport.applyTransform();
  });

  const stopPanning = (event) => {
    if (!isPanning || event.pointerId !== panPointerId) return;
    isPanning = false;
    panPointerId = null;
    controller.renderSummary();
  };

  els.plannerWorkspace.addEventListener("pointerup", stopPanning);
  els.plannerWorkspace.addEventListener("pointercancel", stopPanning);

  els.plannerWorkspace.addEventListener("contextmenu", (event) => {
    event.preventDefault();
    if (
      event.target.closest(".planner-node") ||
      event.target.closest(".planner-add-popup") ||
      event.target.closest(".planner-target-popup")
    ) {
      return;
    }
    controller.closeTargetPopup();
    controller.openPlannerPopup(event.clientX, event.clientY);
  });

  window.addEventListener("resize", () => controller.renderEdges());
}
