import { itemById, itemNameById } from "../common/catalog.js";
import { BELT_CAPACITY_OPTIONS } from "../common/constants.js";
import { defaultBeltLabel, formatAmount, titleCase } from "../common/format.js";
import {
  buildPlannerNetBalanceRows,
  isPlannerNetBalanced,
  plannerNetBalanceClass,
  plannerNetBalanceValue,
} from "./computation.js";
import { getPlannerNode, selectedWorkflowRecord } from "./state.js";

function plannerSortIndicator(sortState, key) {
  if (sortState.key !== key) {
    return "<>";
  }
  return sortState.direction === "asc" ? "^" : "v";
}

export function renderPlannerOptions({ state, els }) {
  els.plannerDefaultBelt.innerHTML = `
    <option value="">Unlimited</option>
    ${BELT_CAPACITY_OPTIONS.map((capacity) => `
      <option
        value="${capacity}"
        ${state.planner.defaultBeltCapacity === capacity ? "selected" : ""}
      >
        ${defaultBeltLabel(capacity)}
      </option>
    `).join("")}
  `;
  els.plannerDefaultBelt.value =
    state.planner.defaultBeltCapacity === null ? "" : String(state.planner.defaultBeltCapacity);
  els.plannerWorkflowName.value = state.planner.workflowName;

  const workflowOptions = state.planner.availableWorkflows.length
    ? state.planner.availableWorkflows.map((workflow) => `
        <option
          value="${workflow.filename}"
          ${workflow.filename === state.planner.selectedWorkflowFilename ? "selected" : ""}
        >
          ${workflow.name}
        </option>
      `).join("")
    : '<option value="">No saved workflows yet</option>';
  els.plannerSavedWorkflows.innerHTML = workflowOptions;
  els.plannerSavedWorkflows.value = state.planner.selectedWorkflowFilename ||
    state.planner.availableWorkflows[0]?.filename ||
    "";
  els.plannerSavedWorkflows.disabled = state.planner.availableWorkflows.length === 0;
  els.plannerWorkflowDirectory.textContent = state.planner.workflowDirectory
    ? `Workflow library: ${state.planner.workflowDirectory}`
    : "Workflow library unavailable.";

  // Populate popup datalist from items
  els.plannerPopupOutputOptions.innerHTML = "";
  state.items.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.name;
    els.plannerPopupOutputOptions.appendChild(option);
  });
}

export function renderPlannerPopup({ state, els }) {
  if (!state.planner.popup.visible) {
    els.plannerAddPopup.hidden = true;
    return;
  }
  els.plannerAddPopup.hidden = false;
  els.plannerAddPopup.style.left = `${state.planner.popup.screenX}px`;
  els.plannerAddPopup.style.top = `${state.planner.popup.screenY}px`;
  const selectedItem = itemById(state, state.planner.popup.outputItemId);
  els.plannerPopupOutputInput.value = selectedItem?.name ?? "";
  els.plannerPopupRecipe.innerHTML = state.planner.popup.candidateRecipes.length
    ? state.planner.popup.candidateRecipes.map((recipe) => `
        <option
          value="${recipe.id}"
          ${recipe.id === state.planner.popup.selectedRecipeId ? "selected" : ""}
        >
          ${recipe.name} | ${titleCase(recipe.building || "unknown")}
        </option>
      `).join("")
    : '<option value="">Select output and find recipes</option>';
  els.plannerPopupRecipe.value = state.planner.popup.selectedRecipeId ?? "";
}

export function renderTargetPopup({ state, els }) {
  if (!state.planner.targetPopup.visible) {
    els.plannerTargetPopup.hidden = true;
    return;
  }
  const node = getPlannerNode(state.planner, state.planner.targetPopup.nodeId);
  if (!node) {
    els.plannerTargetPopup.hidden = true;
    return;
  }
  els.plannerTargetPopup.hidden = false;
  els.plannerTargetPopup.style.left = `${state.planner.targetPopup.screenX}px`;
  els.plannerTargetPopup.style.top = `${state.planner.targetPopup.screenY}px`;
  els.plannerTargetPopupTitle.textContent = itemNameById(state, state.planner.targetPopup.itemId);
  els.plannerTargetPopupRate.value = formatAmount(node.targetRatePerMinute);
}

export function renderPlannerNetBalance({ state, els, onSort }) {
  if (!state.planner.nodes.length) {
    els.plannerNetBalance.innerHTML = '<div class="empty">Add nodes to see net balance.</div>';
    return;
  }

  const rows = buildPlannerNetBalanceRows(state);
  const visibleRows = state.planner.hideBalancedNetItems
    ? rows.filter((row) => !isPlannerNetBalanced(row.netRate))
    : rows;

  // Sync the summary checkbox with state
  els.plannerHideBalancedToggle.checked = state.planner.hideBalancedNetItems;

  els.plannerNetBalance.innerHTML = `
    <table class="planner-net-balance-table">
      <thead>
        <tr>
          <th>
            <button
              type="button"
              class="planner-sort-button ${state.planner.netBalanceSort.key === "item" ? "active" : ""}"
              data-net-sort-key="item"
            >
              Item
              <span class="planner-sort-indicator">
                ${plannerSortIndicator(state.planner.netBalanceSort, "item")}
              </span>
            </button>
          </th>
          <th class="planner-net-col-number">Prod</th>
          <th class="planner-net-col-number">Cons</th>
          <th class="planner-net-col-number">
            <button
              type="button"
              class="planner-sort-button ${state.planner.netBalanceSort.key === "net" ? "active" : ""}"
              data-net-sort-key="net"
            >
              Net
              <span class="planner-sort-indicator">
                ${plannerSortIndicator(state.planner.netBalanceSort, "net")}
              </span>
            </button>
          </th>
        </tr>
      </thead>
      <tbody>
        ${visibleRows.length ? visibleRows.map((row) => `
          <tr>
            <td class="planner-net-balance-item">${row.itemName}</td>
            <td class="planner-net-balance-number planner-net-col-number">${formatAmount(row.producedRate)}</td>
            <td class="planner-net-balance-number planner-net-col-number">${formatAmount(row.consumedRate)}</td>
            <td class="planner-net-balance-number planner-net-col-number planner-net-col-bold ${plannerNetBalanceClass(row.netRate)}">
              ${plannerNetBalanceValue(row.netRate)}
            </td>
          </tr>
        `).join("") : `
          <tr>
            <td colspan="4" class="empty">No unbalanced items match the current filter.</td>
          </tr>
        `}
      </tbody>
    </table>
  `;

  els.plannerNetBalance.querySelectorAll("[data-net-sort-key]").forEach((button) => {
    button.addEventListener("click", () => {
      onSort(button.dataset.netSortKey);
    });
  });
}

export function renderPlannerSummary({ state, els }) {
  const selectedWorkflowName = selectedWorkflowRecord(state.planner)?.name ?? "unsaved";
  els.plannerSummary.textContent =
    `${state.planner.nodes.length} node(s), ${state.planner.edges.length} connection(s) | ` +
    `saved ${selectedWorkflowName} | zoom ${Math.round(state.planner.zoom * 100)}%`;
  els.plannerZoomReset.textContent = `${Math.round(state.planner.zoom * 100)}%`;
  els.plannerEmpty.style.display = state.planner.nodes.length ? "none" : "flex";
}
