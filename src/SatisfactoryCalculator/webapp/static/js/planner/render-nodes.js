import { DEFAULT_NODE_HEIGHT, DEFAULT_NODE_WIDTH } from "../common/constants.js";
import { formatAmount, plannerEntryAmount, titleCase } from "../common/format.js";
import { buildNodeBalanceRows } from "./computation.js";

function plannerBalanceMarkup(state, node, computed, allocationMap) {
  const rows = [
    ...buildNodeBalanceRows(state, node, computed, allocationMap, "input").map((row) => ({
      ...row,
      label: "In",
    })),
    ...buildNodeBalanceRows(state, node, computed, allocationMap, "output").map((row) => ({
      ...row,
      label: "Out",
    })),
  ];
  return rows.length
    ? rows.map((row) => `
        <div class="planner-balance-row ${row.status}">
          <span class="planner-balance-side">${row.label}</span>
          <span class="planner-balance-item">${row.itemName}</span>
          <div class="planner-balance-meter">
            <div class="planner-balance-fill ${row.status}" style="width:${row.progress}%"></div>
          </div>
          <span class="planner-balance-rates">
            ${formatAmount(row.connectedRate)} / ${formatAmount(row.expectedRate)}
          </span>
        </div>
      `).join("")
    : '<div class="empty">No connected flow</div>';
}

function plannerIoMarkup(node, entries, portType) {
  return entries.length
    ? entries.map((entry) => `
        <button
          type="button"
          class="mini-list-row planner-port ${entry.item.id === node.targetItemId ? "is-target" : ""}"
          data-port-node-id="${node.id}"
          data-port-item-id="${entry.item.id}"
          data-port-type="${portType}"
        >
          <span class="planner-port-handle ${portType}"></span>
          <span class="planner-port-name">${entry.item.name}</span>
          <span class="planner-port-amount">${plannerEntryAmount(entry)}</span>
        </button>
      `).join("")
    : '<div class="empty">None</div>';
}

export function renderPlannerNodes({ state, els, computedMap, allocationMap }) {
  els.plannerNodeLayer.innerHTML = state.planner.nodes.map((node) => {
    const computed = computedMap.get(node.id);
    if (!computed) return "";
    return `
      <article
        class="planner-node ${state.planner.selectedNodeId === node.id ? "selected" : ""}"
        data-node-id="${node.id}"
        style="
          left:${node.x}px;
          top:${node.y}px;
          width:${node.width ?? DEFAULT_NODE_WIDTH}px;
          height:${node.height ?? DEFAULT_NODE_HEIGHT}px;
        "
      >
        <div class="planner-node-header">
          <div>
            <div class="planner-node-title">${computed.recipe.name}</div>
            <div class="planner-node-building">
              ${titleCase(computed.recipe.building || "unknown")} | ${node.id}
            </div>
          </div>
          <button type="button" class="node-remove-button" data-remove-node-id="${node.id}">
            Remove
          </button>
        </div>
        <div class="planner-node-body">
          <div class="planner-node-meta compact">
            <div class="metric-card wide">
              <div class="label">Machines Needed</div>
              <div class="value">${formatAmount(computed.machine_count)}</div>
            </div>
            <div class="metric-card">
              <div class="label">Balance</div>
              <div class="planner-balance-list">
                ${plannerBalanceMarkup(state, node, computed, allocationMap)}
              </div>
            </div>
          </div>
          <div class="planner-node-grid">
            <section class="planner-io-column inputs">
              <h4>Inputs</h4>
              <div class="mini-list">${plannerIoMarkup(node, computed.inputs, "input")}</div>
            </section>
            <section class="planner-io-column outputs">
              <h4>Outputs</h4>
              <div class="mini-list">${plannerIoMarkup(node, computed.outputs, "output")}</div>
            </section>
          </div>
        </div>
        <div class="planner-resize-handle left" data-resize-node="${node.id}" data-resize-edge="left"></div>
        <div class="planner-resize-handle right" data-resize-node="${node.id}" data-resize-edge="right"></div>
        <div class="planner-resize-handle top" data-resize-node="${node.id}" data-resize-edge="top"></div>
        <div class="planner-resize-handle bottom" data-resize-node="${node.id}" data-resize-edge="bottom"></div>
        <div class="planner-resize-handle top-left" data-resize-node="${node.id}" data-resize-edge="top-left"></div>
        <div class="planner-resize-handle top-right" data-resize-node="${node.id}" data-resize-edge="top-right"></div>
        <div class="planner-resize-handle bottom-left" data-resize-node="${node.id}" data-resize-edge="bottom-left"></div>
        <div class="planner-resize-handle bottom-right" data-resize-node="${node.id}" data-resize-edge="bottom-right"></div>
      </article>
    `;
  }).join("");
}
