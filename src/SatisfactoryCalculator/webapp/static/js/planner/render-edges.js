import { EDGE_PADDING } from "../common/constants.js";
import {
  bezierMidpoint,
  connectionAnchorPoint,
  edgeControlPoints,
  includePoint,
  includeRect,
  nodeRect,
  portAnchorInWorld,
} from "./geometry.js";
import { getPlannerNode } from "./state.js";

function appendArrowMarker(svg) {
  const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
  const marker = document.createElementNS("http://www.w3.org/2000/svg", "marker");
  marker.setAttribute("id", "planner-edge-arrow");
  marker.setAttribute("markerWidth", "8");
  marker.setAttribute("markerHeight", "8");
  marker.setAttribute("refX", "7");
  marker.setAttribute("refY", "4");
  marker.setAttribute("orient", "auto-start-reverse");
  marker.setAttribute("markerUnits", "strokeWidth");

  const markerPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
  markerPath.setAttribute("d", "M 0 0 L 8 4 L 0 8 z");
  markerPath.setAttribute("fill", "currentColor");
  marker.appendChild(markerPath);
  defs.appendChild(marker);
  svg.appendChild(defs);
}

function svgPath(start, control1, control2, end, minX, minY) {
  return `M ${start.x - minX} ${start.y - minY} ` +
    `C ${control1.x - minX} ${control1.y - minY}, ` +
    `${control2.x - minX} ${control2.y - minY}, ${end.x - minX} ${end.y - minY}`;
}

export function renderPlannerEdges({ state, els, allocationMap }) {
  els.plannerConnectionsSvg.innerHTML = "";
  els.plannerConnectionLabels.innerHTML = "";
  appendArrowMarker(els.plannerConnectionsSvg);

  let bounds = null;
  const drawings = [];
  state.planner.nodes.forEach((node) => {
    const nodeEl = els.plannerNodeLayer.querySelector(`[data-node-id="${node.id}"]`);
    if (nodeEl) {
      bounds = includeRect(bounds, nodeRect(node, nodeEl), EDGE_PADDING);
    }
  });

  state.planner.edges.forEach((edge) => {
    const sourceNode = getPlannerNode(state.planner, edge.sourceNodeId);
    const targetNode = getPlannerNode(state.planner, edge.targetNodeId);
    const sourceEl = els.plannerNodeLayer.querySelector(`[data-node-id="${edge.sourceNodeId}"]`);
    const targetEl = els.plannerNodeLayer.querySelector(`[data-node-id="${edge.targetNodeId}"]`);
    if (!sourceNode || !targetNode || !sourceEl || !targetEl) return;

    const sourcePortEl = sourceEl.querySelector(
      `[data-port-item-id="${edge.itemId}"][data-port-type="output"]`
    );
    const targetPortEl = targetEl.querySelector(
      `[data-port-item-id="${edge.itemId}"][data-port-type="input"]`
    );
    const sourceRect = nodeRect(sourceNode, sourceEl);
    const targetRect = nodeRect(targetNode, targetEl);
    const start = sourcePortEl
      ? portAnchorInWorld(sourceNode, sourceEl, sourcePortEl, "right")
      : connectionAnchorPoint(sourceRect, targetRect);
    const end = targetPortEl
      ? portAnchorInWorld(targetNode, targetEl, targetPortEl, "left")
      : connectionAnchorPoint(targetRect, sourceRect);
    const { control1, control2 } = edgeControlPoints(start, end);
    const labelPoint = bezierMidpoint(start, control1, control2, end);
    const status = allocationMap.get(edge.id)?.status ?? "balanced";

    [start, end, control1, control2].forEach((point) => {
      bounds = includePoint(bounds, point, EDGE_PADDING);
    });
    drawings.push({ control1, control2, edgeId: edge.id, end, labelPoint, start, status });
  });

  const dragState = state.planner.dragConnection;
  let preview = null;
  if (dragState.active && dragState.sourceNodeId && dragState.itemId) {
    const { control1, control2 } = edgeControlPoints(
      { x: dragState.startX, y: dragState.startY },
      { x: dragState.currentX, y: dragState.currentY }
    );
    preview = {
      start: { x: dragState.startX, y: dragState.startY },
      control1,
      control2,
      end: { x: dragState.currentX, y: dragState.currentY },
      status: dragState.validTargetNodeId ? "balanced" : "target_shortage",
    };
    [preview.start, preview.end, preview.control1, preview.control2].forEach((point) => {
      bounds = includePoint(bounds, point, EDGE_PADDING);
    });
  }

  if (!bounds) {
    els.plannerConnectionsSvg.style.left = "0px";
    els.plannerConnectionsSvg.style.top = "0px";
    els.plannerConnectionsSvg.style.width = "1px";
    els.plannerConnectionsSvg.style.height = "1px";
    els.plannerConnectionsSvg.setAttribute("viewBox", "0 0 1 1");
    return;
  }

  const svgWidth = Math.max(1, bounds.maxX - bounds.minX);
  const svgHeight = Math.max(1, bounds.maxY - bounds.minY);
  els.plannerConnectionsSvg.style.left = `${bounds.minX}px`;
  els.plannerConnectionsSvg.style.top = `${bounds.minY}px`;
  els.plannerConnectionsSvg.style.width = `${svgWidth}px`;
  els.plannerConnectionsSvg.style.height = `${svgHeight}px`;
  els.plannerConnectionsSvg.setAttribute("viewBox", `0 0 ${svgWidth} ${svgHeight}`);

  drawings.forEach((drawing) => {
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute(
      "d",
      svgPath(drawing.start, drawing.control1, drawing.control2, drawing.end, bounds.minX, bounds.minY)
    );
    path.setAttribute("class", `edge-line ${drawing.status}`);
    path.setAttribute("marker-end", "url(#planner-edge-arrow)");
    els.plannerConnectionsSvg.appendChild(path);

    const label = document.createElement("div");
    label.className = `planner-connection-label ${drawing.status}`;
    label.style.left = `${drawing.labelPoint.x}px`;
    label.style.top = `${drawing.labelPoint.y - 22}px`;
    label.innerHTML = `
      <button type="button" class="connection-delete-button" data-remove-edge-id="${drawing.edgeId}">
        x
      </button>
    `;
    els.plannerConnectionLabels.appendChild(label);
  });

  if (preview) {
    const previewPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
    previewPath.setAttribute(
      "d",
      svgPath(preview.start, preview.control1, preview.control2, preview.end, bounds.minX, bounds.minY)
    );
    previewPath.setAttribute("class", `edge-line ${preview.status} edge-preview`);
    previewPath.setAttribute("marker-end", "url(#planner-edge-arrow)");
    els.plannerConnectionsSvg.appendChild(previewPath);
  }
}
