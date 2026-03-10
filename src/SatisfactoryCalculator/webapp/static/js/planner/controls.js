export function bindPlannerControls({ controller, els, setStatus, state }) {
  els.plannerPopupSearch.addEventListener("click", () => void controller.findPlannerPopupRecipes());
  els.plannerPopupRecipe.addEventListener("change", () => {
    state.planner.popup.selectedRecipeId = els.plannerPopupRecipe.value || null;
  });
  els.plannerPopupConfirm.addEventListener("click", () => {
    if (!state.planner.popup.outputItemId || !state.planner.popup.selectedRecipeId) {
      setStatus("Choose an output item and recipe before adding a node.");
      return;
    }
    controller.addPlannerNodeAt(
      state.planner.popup.selectedRecipeId,
      state.planner.popup.outputItemId,
      state.planner.popup.canvasX,
      state.planner.popup.canvasY
    );
  });
  els.plannerPopupCancel.addEventListener("click", controller.closePlannerPopup);
  els.plannerTargetPopupSave.addEventListener("click", () => {
    const value = Number(els.plannerTargetPopupRate.value);
    if (Number.isNaN(value) || value < 0) {
      setStatus("Target amount must be a non-negative number.");
      return;
    }
    if (!state.planner.targetPopup.nodeId || !state.planner.targetPopup.itemId) return;
    controller.updatePlannerNode(state.planner.targetPopup.nodeId, {
      targetItemId: state.planner.targetPopup.itemId,
      targetRatePerMinute: value,
    });
    controller.closeTargetPopup();
  });
  els.plannerTargetPopupCancel.addEventListener("click", controller.closeTargetPopup);
  els.plannerZoomOut.addEventListener("click", () => {
    state.planner.zoom = Math.max(0.5, state.planner.zoom - 0.1);
    controller.renderSummary();
  });
  els.plannerZoomReset.addEventListener("click", () => {
    state.planner.zoom = 1;
    controller.renderSummary();
  });
  els.plannerZoomIn.addEventListener("click", () => {
    state.planner.zoom = Math.min(2.5, state.planner.zoom + 0.1);
    controller.renderSummary();
  });
  els.plannerDefaultBelt.addEventListener("change", () => {
    state.planner.defaultBeltCapacity = els.plannerDefaultBelt.value
      ? Number(els.plannerDefaultBelt.value)
      : null;
    controller.renderOptions();
    controller.render();
  });
  els.plannerWorkflowName.addEventListener("input", () => {
    state.planner.workflowName = els.plannerWorkflowName.value || "Untitled Workflow";
    controller.renderSummary();
  });
  els.plannerSavedWorkflows.addEventListener("change", () => {
    state.planner.selectedWorkflowFilename = els.plannerSavedWorkflows.value;
    controller.renderSummary();
  });
  els.newWorkflowButton.addEventListener("click", controller.resetPlannerWorkflow);
  els.plannerRefreshWorkflows.addEventListener("click", async () => {
    try {
      await controller.refreshWorkflows(state.planner.selectedWorkflowFilename);
      controller.renderSummary();
      setStatus("Refreshed saved workflows.");
    } catch (error) {
      setStatus(`Failed to refresh workflows: ${error.message}`);
    }
  });
  els.exportWorkflowButton.addEventListener("click", async () => {
    try {
      await controller.exportWorkflow();
    } catch (error) {
      setStatus(`Failed to export workflow: ${error.message}`);
    }
  });
  els.importWorkflowButton.addEventListener("click", async () => {
    try {
      await controller.importSelectedWorkflow();
    } catch (error) {
      setStatus(`Failed to import workflow: ${error.message}`);
    }
  });
  els.plannerSidebarToggle.addEventListener("click", () => {
    state.planner.sidebarCollapsed = !state.planner.sidebarCollapsed;
    els.plannerSidebar.classList.toggle("sidebar-collapsed", state.planner.sidebarCollapsed);
    els.plannerSidebarToggle.textContent = state.planner.sidebarCollapsed ? "\u203a" : "\u2039";
  });
  els.plannerHideBalancedToggle.addEventListener("change", (event) => {
    state.planner.hideBalancedNetItems = event.target.checked;
    controller.render();
  });
}
