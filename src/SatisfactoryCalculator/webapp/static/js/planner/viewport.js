import { clampZoom } from "../common/format.js";

export function createPlannerViewport({ plannerState, workspaceEl, worldEl }) {
  function workspaceRect() {
    return workspaceEl.getBoundingClientRect();
  }

  function screenToWorld(point) {
    const rect = workspaceRect();
    return {
      x: (point.x - rect.left - plannerState.panX) / plannerState.zoom,
      y: (point.y - rect.top - plannerState.panY) / plannerState.zoom,
    };
  }

  function worldToScreen(point) {
    const rect = workspaceRect();
    return {
      x: rect.left + plannerState.panX + point.x * plannerState.zoom,
      y: rect.top + plannerState.panY + point.y * plannerState.zoom,
    };
  }

  function applyTransform(element = worldEl) {
    element.style.transform =
      `translate(${plannerState.panX}px, ${plannerState.panY}px) scale(${plannerState.zoom})`;
  }

  function zoomAroundScreenPoint(clientX, clientY, delta) {
    const rect = workspaceRect();
    const cursorX = clientX - rect.left;
    const cursorY = clientY - rect.top;
    const worldPoint = screenToWorld({ x: clientX, y: clientY });
    plannerState.zoom = clampZoom(plannerState.zoom + delta);
    plannerState.panX = cursorX - worldPoint.x * plannerState.zoom;
    plannerState.panY = cursorY - worldPoint.y * plannerState.zoom;
    applyTransform();
  }

  return {
    applyTransform,
    screenToWorld,
    worldToScreen,
    zoomAroundScreenPoint,
  };
}
