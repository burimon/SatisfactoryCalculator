SCRIPT = r"""
    const WORKFLOW_VERSION = 1;
    const POWER_ITEM_ID = "power";
    const BELT_CAPACITY_OPTIONS = [60, 120, 270, 480, 780];

    const state = {
      mode: "browser",
      recipes: [],
      items: [],
      currentRecipeId: null,
      rateMode: "per_cycle",
      debug: false,
      outputItemId: null,
      planner: {
        selectedOutputItemId: null,
        defaultBeltCapacity: 60,
        candidateRecipes: [],
        nodes: [],
        edges: [],
        selectedNodeId: null,
        connectSourceNodeId: null,
        nextNodeNumber: 1,
        nextEdgeNumber: 1
      }
    };
    
    const els = {
      browserView: document.getElementById("browser-view"),
      plannerView: document.getElementById("planner-view"),
      modeButtons: document.querySelectorAll("[data-mode]"),
      recipeInput: document.getElementById("recipe-input"),
      recipeOptions: document.getElementById("recipe-options"),
      rateSelect: document.getElementById("rate-select"),
      debugToggle: document.getElementById("debug-toggle"),
      recipeName: document.getElementById("recipe-name"),
      recipeId: document.getElementById("recipe-id"),
      recipeBuilding: document.getElementById("recipe-building"),
      recipeCycle: document.getElementById("recipe-cycle"),
      recipeRate: document.getElementById("recipe-rate"),
      inputsList: document.getElementById("inputs-list"),
      outputsList: document.getElementById("outputs-list"),
      outputInput: document.getElementById("output-input"),
      outputOptions: document.getElementById("output-options"),
      searchButton: document.getElementById("search-button"),
      resultsList: document.getElementById("results-list"),
      plannerDefaultBelt: document.getElementById("planner-default-belt"),
      plannerOutputInput: document.getElementById("planner-output-input"),
      plannerOutputOptions: document.getElementById("planner-output-options"),
      plannerSearchButton: document.getElementById("planner-search-button"),
      plannerRecipeResults: document.getElementById("planner-recipe-results"),
      connectionSource: document.getElementById("connection-source"),
      connectionTarget: document.getElementById("connection-target"),
      connectionItem: document.getElementById("connection-item"),
      addConnectionButton: document.getElementById("add-connection-button"),
      plannerConnections: document.getElementById("planner-connections"),
      plannerWorkspace: document.getElementById("planner-workspace"),
      plannerConnectionsSvg: document.getElementById("planner-connections-svg"),
      plannerEmpty: document.getElementById("planner-empty"),
      plannerSummary: document.getElementById("planner-summary"),
      exportWorkflowButton: document.getElementById("export-workflow-button"),
      importWorkflowButton: document.getElementById("import-workflow-button"),
      importWorkflowInput: document.getElementById("import-workflow-input"),
      status: document.getElementById("status")
    };

    function rateLabel(mode) {
      return {
        per_cycle: "Per Cycle",
        per_second: "Per Second",
        per_minute: "Per Minute"
      }[mode];
    }

    function formatAmount(amount) {
      if (Math.abs(amount) < 0.00001) return "0";
      if (Number.isInteger(amount)) return String(amount);
      return Number(amount).toFixed(2).replace(/\.00$/, "").replace(/(\.\d*[1-9])0+$/, "$1");
    }

    function isPowerItem(itemId) {
      return itemId === POWER_ITEM_ID;
    }

    function beltCapacityLabel(capacity) {
      if (capacity === null) {
        return "Unlimited";
      }
      const beltMk = BELT_CAPACITY_OPTIONS.indexOf(capacity) + 1;
      return `Mk ${beltMk} (${capacity}/min)`;
    }

    function perMachineRate(targetItemId, baseRate, beltCapacity) {
      if (isPowerItem(targetItemId) || beltCapacity === null) {
        return baseRate;
      }
      return Math.min(baseRate, beltCapacity);
    }

    function scaledAmount(amount, duration, rateMode) {
      if (rateMode === "per_cycle") return amount;
      if (rateMode === "per_second") return amount / duration;
      return (amount * 60) / duration;
    }

    function amountSubtitle(verb, amount, duration, rateMode) {
      const scaled = formatAmount(scaledAmount(amount, duration, rateMode));
      const unit = { per_cycle: "per cycle", per_second: "/s", per_minute: "/min" }[rateMode];
      return `${verb} ${scaled} ${unit}`;
    }

    function plannerEntryAmount(entry) {
      return isPowerItem(entry.item.id)
        ? `${formatAmount(entry.amount_per_minute)} MW`
        : `${formatAmount(entry.amount_per_minute)}/min`;
    }

    function itemRateLabel(itemId, amount) {
      return isPowerItem(itemId) ? `${formatAmount(amount)} MW` : `${formatAmount(amount)}/min`;
    }

    function titleCase(value) {
      return value.replace(/_/g, " ").replace(/\b\w/g, (ch) => ch.toUpperCase());
    }

    function itemNameById(itemId) {
      return state.items.find((item) => item.id === itemId)?.name ?? itemId;
    }

    function recipeOptionLabel(recipe) {
      return state.debug ? `${recipe.name} [${recipe.id}]` : recipe.name;
    }

    function itemOptionLabel(item) {
      return state.debug ? `${item.name} [${item.id}]` : item.name;
    }

    function recipeLabelToId(label) {
      return state.recipes.find((recipe) => recipeOptionLabel(recipe) === label)?.id ?? null;
    }

    function itemLabelToId(label) {
      return state.items.find((item) => itemOptionLabel(item) === label)?.id ?? null;
    }

    function recipeById(recipeId) {
      return state.recipes.find((recipe) => recipe.id === recipeId) ?? null;
    }

    function newNodeId() {
      const id = `node_${state.planner.nextNodeNumber}`;
      state.planner.nextNodeNumber += 1;
      return id;
    }

    function newEdgeId() {
      const id = `edge_${state.planner.nextEdgeNumber}`;
      state.planner.nextEdgeNumber += 1;
      return id;
    }

    function recipeOutputRatePerMinute(recipe, itemId) {
      const output = recipe.outputs.find((entry) => entry.item.id === itemId);
      if (!output) return null;
      if (isPowerItem(itemId)) return output.amount;
      return (output.amount * 60) / recipe.duration_seconds;
    }

    function scaledRecipeRates(recipe, targetItemId, targetRatePerMinute, beltCapacity = null) {
      const targetBaseRate = recipeOutputRatePerMinute(recipe, targetItemId);
      if (!targetBaseRate) {
        throw new Error(`Recipe ${recipe.id} does not produce ${targetItemId}`);
      }
      const machineRate = perMachineRate(targetItemId, targetBaseRate, beltCapacity);
      const machineCount = machineRate === 0 ? 0 : targetRatePerMinute / machineRate;
      const multiplier = targetRatePerMinute / targetBaseRate;
      const scaleEntries = (entries) => entries.map((entry) => ({
        item: entry.item,
        amount_per_minute: isPowerItem(entry.item.id)
          ? entry.amount * multiplier
          : (entry.amount * 60 / recipe.duration_seconds) * multiplier
      }));
      return {
        multiplier,
        machine_count: machineCount,
        per_machine_rate: machineRate,
        requested_target_rate: targetRatePerMinute,
        inputs: scaleEntries(recipe.inputs),
        outputs: scaleEntries(recipe.outputs)
      };
    }

    function getPlannerNode(nodeId) {
      return state.planner.nodes.find((node) => node.id === nodeId) ?? null;
    }

    function getPlannerNodeComputed(node) {
      if (!node) return null;
      const recipe = recipeById(node.recipeId);
      if (!recipe) return null;
      return {
        recipe,
        ...scaledRecipeRates(
          recipe,
          node.targetItemId,
          node.targetRatePerMinute,
          node.beltCapacity ?? null
        )
      };
    }

    function getItemRate(entries, itemId) {
      return entries.find((entry) => entry.item.id === itemId)?.amount_per_minute ?? 0;
    }

    function getConnectionCompatibility(sourceNodeId, targetNodeId) {
      const sourceComputed = getPlannerNodeComputed(getPlannerNode(sourceNodeId));
      const targetComputed = getPlannerNodeComputed(getPlannerNode(targetNodeId));
      if (!sourceComputed || !targetComputed) return [];
      return sourceComputed.outputs
        .filter((output) => getItemRate(targetComputed.inputs, output.item.id) > 0)
        .map((output) => output.item);
    }

    function getConnectionStatus(edge) {
      const sourceComputed = getPlannerNodeComputed(getPlannerNode(edge.sourceNodeId));
      const targetComputed = getPlannerNodeComputed(getPlannerNode(edge.targetNodeId));
      if (!sourceComputed || !targetComputed) return null;
      const sourceRate = getItemRate(sourceComputed.outputs, edge.itemId);
      const targetRate = getItemRate(targetComputed.inputs, edge.itemId);
      const delta = sourceRate - targetRate;
      let status = "balanced";
      if (delta > 0.01) status = "source_surplus";
      if (delta < -0.01) status = "target_shortage";
      return { sourceRate, targetRate, delta, status };
    }

    function renderOptions() {
      els.recipeOptions.innerHTML = "";
      state.recipes.forEach((recipe) => {
        const option = document.createElement("option");
        option.value = recipeOptionLabel(recipe);
        els.recipeOptions.appendChild(option);
      });
      const selectedRecipe = recipeById(state.currentRecipeId);
      els.recipeInput.value = selectedRecipe ? recipeOptionLabel(selectedRecipe) : "";

      els.outputOptions.innerHTML = "";
      els.plannerOutputOptions.innerHTML = "";
      state.items.forEach((item) => {
        const browserOption = document.createElement("option");
        browserOption.value = itemOptionLabel(item);
        els.outputOptions.appendChild(browserOption);

        const plannerOption = document.createElement("option");
        plannerOption.value = item.name;
        els.plannerOutputOptions.appendChild(plannerOption);
      });

      const selectedItem = state.items.find((item) => item.id === state.outputItemId);
      els.outputInput.value = selectedItem ? itemOptionLabel(selectedItem) : "";

      const plannerItem = state.items.find(
        (item) => item.id === state.planner.selectedOutputItemId
      );
      els.plannerOutputInput.value = plannerItem?.name ?? "";

      els.plannerDefaultBelt.innerHTML = `
        <option value="">Unlimited</option>
        ${BELT_CAPACITY_OPTIONS.map((capacity) => `
          <option
            value="${capacity}"
            ${state.planner.defaultBeltCapacity === capacity ? "selected" : ""}
          >
            ${beltCapacityLabel(capacity)}
          </option>
        `).join("")}
      `;
      els.plannerDefaultBelt.value =
        state.planner.defaultBeltCapacity === null
          ? ""
          : String(state.planner.defaultBeltCapacity);
    }

    function createRow(entry, verb, duration) {
      const itemName = state.debug ? `${entry.item.name} [${entry.item.id}]` : entry.item.name;
      const amountText = isPowerItem(entry.item.id)
        ? `${verb} ${formatAmount(entry.amount)} MW`
        : amountSubtitle(verb, entry.amount, duration, state.rateMode);
      return `
        <div class="row-item">
          <div class="row-top">
            <div class="row-name">${itemName}</div>
            <div class="row-amount">${amountText}</div>
          </div>
          <div class="row-id" style="display:${state.debug ? "block" : "none"}">
            ${entry.item.id}
          </div>
        </div>
      `;
    }

    function renderRecipe(recipe) {
      els.recipeName.textContent = recipe.name;
      els.recipeId.textContent = recipe.id;
      els.recipeId.style.display = state.debug ? "block" : "none";
      els.recipeBuilding.textContent = recipe.building ? titleCase(recipe.building) : "Unknown";
      els.recipeCycle.textContent = `${recipe.duration_seconds}s`;
      els.recipeRate.textContent = rateLabel(state.rateMode);
      els.inputsList.innerHTML =
        recipe.inputs
          .map((entry) => createRow(entry, "Consumes", recipe.duration_seconds))
          .join("") || '<div class="empty">No inputs</div>';
      els.outputsList.innerHTML =
        recipe.outputs
          .map((entry) => createRow(entry, "Produces", recipe.duration_seconds))
          .join("") || '<div class="empty">No outputs</div>';
    }

    async function fetchJson(path) {
      const response = await fetch(path);
      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }
      return response.json();
    }

    async function loadRecipe(recipeId) {
      const recipe = await fetchJson(`/api/recipes/${recipeId}`);
      state.currentRecipeId = recipe.id;
      renderOptions();
      renderRecipe(recipe);
      if (state.mode === "browser") {
        els.status.textContent = `Loaded recipe: ${recipe.name}`;
      }
    }

    async function searchByOutput() {
      const itemId = itemLabelToId(els.outputInput.value) ?? state.outputItemId;
      if (!itemId) {
        els.status.textContent = "Choose a valid output item from the list.";
        return;
      }
      state.outputItemId = itemId;
      renderOptions();
      const recipes = await fetchJson(`/api/recipes/by-output/${itemId}`);
      els.resultsList.innerHTML = recipes.length
        ? recipes.map((recipe) => `
            <button
              class="result-card ${recipe.id === state.currentRecipeId ? "active" : ""}"
              data-recipe-id="${recipe.id}"
            >
              <div class="title">${recipe.name}</div>
              <div class="meta">
                ${titleCase(recipe.building || "unknown")} | ${recipe.duration_seconds}s cycle
              </div>
            </button>
          `).join("")
        : '<div class="empty">No recipes found.</div>';

      els.resultsList.querySelectorAll("[data-recipe-id]").forEach((button) => {
        button.addEventListener("click", () => loadRecipe(button.dataset.recipeId));
      });
      const selectedItem = state.items.find((item) => item.id === itemId);
      if (state.mode === "browser") {
        els.status.textContent =
          `Found ${recipes.length} recipe(s) producing ` +
          `${selectedItem ? selectedItem.name : itemId}.`;
      }
    }

    function setMode(mode) {
      state.mode = mode;
      els.browserView.classList.toggle("active", mode === "browser");
      els.plannerView.classList.toggle("active", mode === "planner");
      els.modeButtons.forEach((button) => {
        button.classList.toggle("active", button.dataset.mode === mode);
      });
      els.status.textContent =
        mode === "browser"
          ? `Loaded recipe: ${recipeById(state.currentRecipeId)?.name ?? "none"}`
          : "Planner mode active.";
    }

    async function findPlannerRecipes() {
      const item = state.items.find((candidate) => candidate.name === els.plannerOutputInput.value);
      if (!item) {
        els.status.textContent = "Choose a valid planner output item from the list.";
        return;
      }
      state.planner.selectedOutputItemId = item.id;
      renderOptions();
      state.planner.candidateRecipes = await fetchJson(`/api/recipes/by-output/${item.id}`);
      renderPlannerRecipeCandidates();
      els.status.textContent =
        `Found ${state.planner.candidateRecipes.length} planner recipe option(s) for ${item.name}.`;
    }

    function addPlannerNode(recipeId, targetItemId) {
      const recipe = recipeById(recipeId);
      if (!recipe) return;
      const targetRatePerMinute = recipeOutputRatePerMinute(recipe, targetItemId) ?? 0;
      const columnOffset = state.planner.nodes.length % 3;
      const rowOffset = Math.floor(state.planner.nodes.length / 3);
      const node = {
        id: newNodeId(),
        recipeId,
        targetItemId,
        targetRatePerMinute,
        beltCapacity: isPowerItem(targetItemId) ? null : state.planner.defaultBeltCapacity,
        x: 28 + columnOffset * 300,
        y: 28 + rowOffset * 260
      };
      state.planner.nodes.push(node);
      state.planner.selectedNodeId = node.id;
      renderPlanner();
      els.status.textContent = `Added planner node for ${recipe.name}.`;
    }

    function removePlannerNode(nodeId) {
      state.planner.nodes = state.planner.nodes.filter((node) => node.id !== nodeId);
      state.planner.edges = state.planner.edges.filter(
        (edge) => edge.sourceNodeId !== nodeId && edge.targetNodeId !== nodeId
      );
      if (state.planner.selectedNodeId === nodeId) {
        state.planner.selectedNodeId = state.planner.nodes[0]?.id ?? null;
      }
      renderPlanner();
    }

    function updatePlannerNode(nodeId, changes) {
      const node = getPlannerNode(nodeId);
      if (!node) return;
      Object.assign(node, changes);
      if (isPowerItem(node.targetItemId)) {
        node.beltCapacity = null;
      }
      renderPlanner();
    }

    function addPlannerConnection(sourceNodeId, targetNodeId, itemId) {
      if (!sourceNodeId || !targetNodeId || sourceNodeId === targetNodeId || !itemId) {
        els.status.textContent = "Choose valid source, target, and item values.";
        return;
      }
      const duplicate = state.planner.edges.find(
        (edge) =>
          edge.sourceNodeId === sourceNodeId &&
          edge.targetNodeId === targetNodeId &&
          edge.itemId === itemId
      );
      if (duplicate) {
        els.status.textContent = "That connection already exists.";
        return;
      }
      const compatible = getConnectionCompatibility(sourceNodeId, targetNodeId);
      if (!compatible.some((item) => item.id === itemId)) {
        els.status.textContent = "Selected nodes are not compatible for that item.";
        return;
      }
      state.planner.edges.push({
        id: newEdgeId(),
        sourceNodeId,
        targetNodeId,
        itemId
      });
      renderPlanner();
      els.status.textContent = `Connected ${itemNameById(itemId)} between nodes.`;
    }

    function removePlannerConnection(edgeId) {
      state.planner.edges = state.planner.edges.filter((edge) => edge.id !== edgeId);
      renderPlanner();
    }

    function renderPlannerRecipeCandidates() {
      const targetItemId = state.planner.selectedOutputItemId;
      els.plannerRecipeResults.innerHTML = state.planner.candidateRecipes.length
        ? state.planner.candidateRecipes.map((recipe) => `
            <button
              class="result-card"
              data-add-recipe-id="${recipe.id}"
              data-target-item-id="${targetItemId}"
            >
              <div class="title">${recipe.name}</div>
              <div class="meta">
                ${titleCase(recipe.building || "unknown")} | target ${itemNameById(targetItemId)}
              </div>
            </button>
          `).join("")
        : '<div class="empty">No producer recipes found.</div>';

      els.plannerRecipeResults.querySelectorAll("[data-add-recipe-id]").forEach((button) => {
        button.addEventListener("click", () => {
          addPlannerNode(button.dataset.addRecipeId, button.dataset.targetItemId);
        });
      });
    }

    function renderPlannerConnectionOptions() {
      const nodes = state.planner.nodes;
      const buildOptions = (includePrompt) => {
        const options = [];
        if (includePrompt) {
          options.push('<option value="">Choose node</option>');
        }
        nodes.forEach((node) => {
          const recipe = recipeById(node.recipeId);
          options.push(
            `<option value="${node.id}">${recipe?.name ?? node.recipeId} (${node.id})</option>`
          );
        });
        return options.join("");
      };
      const previousSource = els.connectionSource.value;
      const previousTarget = els.connectionTarget.value;
      els.connectionSource.innerHTML = buildOptions(true);
      els.connectionTarget.innerHTML = buildOptions(true);
      els.connectionSource.value = nodes.some((node) => node.id === previousSource)
        ? previousSource
        : "";
      els.connectionTarget.value = nodes.some((node) => node.id === previousTarget)
        ? previousTarget
        : "";
      refreshConnectionItemOptions();
    }

    function refreshConnectionItemOptions() {
      const compatibleItems = getConnectionCompatibility(
        els.connectionSource.value,
        els.connectionTarget.value
      );
      els.connectionItem.innerHTML = compatibleItems.length
        ? compatibleItems.map((item) => `<option value="${item.id}">${item.name}</option>`).join("")
        : '<option value="">No shared items</option>';
    }

    function renderPlannerConnectionsList() {
      els.plannerConnections.innerHTML = state.planner.edges.length
        ? state.planner.edges.map((edge) => {
            const source = getPlannerNode(edge.sourceNodeId);
            const target = getPlannerNode(edge.targetNodeId);
            const sourceRecipe = recipeById(source?.recipeId ?? "");
            const targetRecipe = recipeById(target?.recipeId ?? "");
            const status = getConnectionStatus(edge);
            const statusLabel = {
              balanced: "Balanced",
              source_surplus: "Source surplus",
              target_shortage: "Target shortage"
            }[status?.status ?? "balanced"];
            const pillClass = {
              balanced: "planner-status-balanced",
              source_surplus: "planner-status-source-surplus",
              target_shortage: "planner-status-target-shortage"
            }[status?.status ?? "balanced"];
            return `
              <div class="planner-connection-card">
                <div class="planner-connection-top">
                  <strong>${itemNameById(edge.itemId)}</strong>
                  <span class="planner-status-pill ${pillClass}">${statusLabel}</span>
                </div>
                <div class="planner-connection-meta">
                  ${sourceRecipe?.name ?? edge.sourceNodeId}
                  -> ${targetRecipe?.name ?? edge.targetNodeId}
                </div>
                <div class="planner-connection-rates">
                  Source ${itemRateLabel(edge.itemId, status?.sourceRate ?? 0)}
                  | Target ${itemRateLabel(edge.itemId, status?.targetRate ?? 0)}
                </div>
                <div class="stack-gap">
                  <button
                    type="button"
                    class="connection-remove-button"
                    data-remove-edge-id="${edge.id}"
                  >
                    Remove
                  </button>
                </div>
              </div>
            `;
          }).join("")
        : '<div class="empty">No connections yet.</div>';

      els.plannerConnections.querySelectorAll("[data-remove-edge-id]").forEach((button) => {
        button.addEventListener("click", () => {
          removePlannerConnection(button.dataset.removeEdgeId);
        });
      });
    }

    function plannerIoMarkup(entries) {
      return entries.length
        ? entries.map((entry) => `
            <div class="mini-list-row">
              <span>${entry.item.name}</span>
              <span>${plannerEntryAmount(entry)}</span>
            </div>
          `).join("")
        : '<div class="empty">None</div>';
    }

    function renderPlannerNodes() {
      els.plannerWorkspace.querySelectorAll(".planner-node").forEach((node) => node.remove());
      state.planner.nodes.forEach((node) => {
        const computed = getPlannerNodeComputed(node);
        if (!computed) return;
        const nodeEl = document.createElement("article");
        nodeEl.className = `planner-node ${
          state.planner.selectedNodeId === node.id ? "selected" : ""
        }`;
        nodeEl.dataset.nodeId = node.id;
        nodeEl.style.left = `${node.x}px`;
        nodeEl.style.top = `${node.y}px`;
        nodeEl.innerHTML = `
          <div class="planner-node-header">
            <div>
              <div class="planner-node-title">${computed.recipe.name}</div>
              <div class="planner-node-building">
                ${titleCase(computed.recipe.building || "unknown")} | ${node.id}
              </div>
            </div>
            <button
              type="button"
              class="node-remove-button"
              data-remove-node-id="${node.id}"
            >
              Remove
            </button>
          </div>
          <div class="planner-node-body">
            <div class="planner-node-meta">
              <div class="metric-card">
                <div class="label">Cycle</div>
                <div class="value">${computed.recipe.duration_seconds}s</div>
              </div>
              <div class="metric-card">
                <div class="label">Machines</div>
                <div class="value">
                  ${formatAmount(computed.machine_count)}
                </div>
              </div>
            </div>
            <div class="planner-node-meta">
              <div class="metric-card">
                <div class="label">Per Machine</div>
                <div class="value">
                  ${isPowerItem(node.targetItemId)
                    ? `${formatAmount(computed.per_machine_rate)} MW`
                    : `${formatAmount(computed.per_machine_rate)}/min`}
                </div>
              </div>
              <div class="metric-card">
                <div class="label">Requested</div>
                <div class="value">
                  ${isPowerItem(node.targetItemId)
                    ? `${formatAmount(computed.requested_target_rate)} MW`
                    : `${formatAmount(computed.requested_target_rate)}/min`}
                </div>
              </div>
            </div>
            <div class="planner-node-actions">
              <div class="field">
                <label>Target Output</label>
                <select class="planner-select" data-node-target-item="${node.id}">
                  ${computed.recipe.outputs.map((entry) => `
                    <option
                      value="${entry.item.id}"
                      ${entry.item.id === node.targetItemId ? "selected" : ""}
                    >
                      ${entry.item.name}
                    </option>
                  `).join("")}
                </select>
              </div>
              <div class="field">
                <label>${isPowerItem(node.targetItemId) ? "Target MW" : "Target / min"}</label>
                <input
                  class="planner-rate-input"
                  type="number"
                  min="0"
                  step="0.1"
                  value="${formatAmount(node.targetRatePerMinute)}"
                  data-node-rate="${node.id}"
                >
              </div>
            </div>
            <div class="planner-node-actions">
              <div class="field">
                <label>Belt Limit</label>
                <select
                  class="planner-select"
                  data-node-belt-capacity="${node.id}"
                  ${isPowerItem(node.targetItemId) ? "disabled" : ""}
                >
                  <option value="">Unlimited</option>
                  ${BELT_CAPACITY_OPTIONS.map((capacity) => `
                    <option value="${capacity}" ${node.beltCapacity === capacity ? "selected" : ""}>
                      ${beltCapacityLabel(capacity)}
                    </option>
                  `).join("")}
                </select>
              </div>
              <div class="field">
                <label>Canvas Action</label>
                <button
                  type="button"
                  class="secondary-button"
                  data-start-connect-node="${node.id}"
                >
                  ${state.planner.connectSourceNodeId === node.id ? "Connecting..." : "Connect"}
                </button>
              </div>
            </div>
            <div class="planner-node-grid">
              <section class="planner-io-column inputs">
                <h4>Inputs</h4>
                <div class="mini-list">${plannerIoMarkup(computed.inputs)}</div>
              </section>
              <section class="planner-io-column outputs">
                <h4>Outputs</h4>
                <div class="mini-list">${plannerIoMarkup(computed.outputs)}</div>
              </section>
            </div>
          </div>
        `;
        nodeEl.addEventListener("click", (event) => {
          if (
            event.target.closest(
              "button, input, select, option, label, .field, .planner-node-actions"
            )
          ) {
            return;
          }
          if (state.planner.connectSourceNodeId && state.planner.connectSourceNodeId !== node.id) {
            const sourceNodeId = state.planner.connectSourceNodeId;
            const compatibleItems = getConnectionCompatibility(sourceNodeId, node.id);
            if (compatibleItems.length === 1) {
              addPlannerConnection(sourceNodeId, node.id, compatibleItems[0].id);
              state.planner.connectSourceNodeId = null;
              renderPlanner();
              return;
            }
            if (!compatibleItems.length) {
              els.status.textContent = "These nodes do not share a compatible item.";
            } else {
              els.status.textContent =
                "Multiple compatible items exist. Use the connection controls to choose one.";
            }
            state.planner.connectSourceNodeId = null;
            renderPlanner();
            return;
          }
          state.planner.selectedNodeId = node.id;
          renderPlanner();
        });
        els.plannerWorkspace.appendChild(nodeEl);
      });

      els.plannerWorkspace.querySelectorAll("[data-remove-node-id]").forEach((button) => {
        button.addEventListener("click", (event) => {
          event.stopPropagation();
          removePlannerNode(button.dataset.removeNodeId);
        });
      });

      els.plannerWorkspace.querySelectorAll("[data-node-rate]").forEach((input) => {
        input.addEventListener("change", () => {
          const value = Number(input.value);
          if (Number.isNaN(value) || value < 0) {
            els.status.textContent = "Target output rate must be a non-negative number.";
            return;
          }
          updatePlannerNode(input.dataset.nodeRate, { targetRatePerMinute: value });
        });
      });

      els.plannerWorkspace.querySelectorAll("[data-node-target-item]").forEach((select) => {
        select.addEventListener("change", () => {
          const node = getPlannerNode(select.dataset.nodeTargetItem);
          const recipe = recipeById(node.recipeId);
          const nextRate =
            recipeOutputRatePerMinute(recipe, select.value) ?? node.targetRatePerMinute;
          updatePlannerNode(node.id, {
            targetItemId: select.value,
            targetRatePerMinute: nextRate
          });
        });
      });

      els.plannerWorkspace.querySelectorAll("[data-node-belt-capacity]").forEach((select) => {
        select.addEventListener("change", () => {
          const beltCapacity = select.value ? Number(select.value) : null;
          updatePlannerNode(select.dataset.nodeBeltCapacity, { beltCapacity });
        });
      });

      els.plannerWorkspace.querySelectorAll("[data-start-connect-node]").forEach((button) => {
        button.addEventListener("click", (event) => {
          event.stopPropagation();
          const nodeId = button.dataset.startConnectNode;
          state.planner.connectSourceNodeId =
            state.planner.connectSourceNodeId === nodeId ? null : nodeId;
          renderPlanner();
          if (state.planner.connectSourceNodeId) {
            els.status.textContent = "Select a target node on the canvas to create a connection.";
          }
        });
      });

      bindPlannerDragging();
    }

    function renderPlannerEdges() {
      const bounds = els.plannerWorkspace.getBoundingClientRect();
      els.plannerConnectionsSvg.setAttribute("viewBox", `0 0 ${bounds.width} ${bounds.height}`);
      els.plannerConnectionsSvg.innerHTML = "";
      state.planner.edges.forEach((edge) => {
        const sourceEl = els.plannerWorkspace.querySelector(
          `[data-node-id="${edge.sourceNodeId}"]`
        );
        const targetEl = els.plannerWorkspace.querySelector(
          `[data-node-id="${edge.targetNodeId}"]`
        );
        if (!sourceEl || !targetEl) return;
        const sourceRect = sourceEl.getBoundingClientRect();
        const targetRect = targetEl.getBoundingClientRect();
        const x1 = sourceRect.left - bounds.left + sourceRect.width;
        const y1 = sourceRect.top - bounds.top + sourceRect.height / 2;
        const x2 = targetRect.left - bounds.left;
        const y2 = targetRect.top - bounds.top + targetRect.height / 2;
        const midX = (x1 + x2) / 2;
        const status = getConnectionStatus(edge);

        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        path.setAttribute("d", `M ${x1} ${y1} C ${midX} ${y1}, ${midX} ${y2}, ${x2} ${y2}`);
        path.setAttribute("class", `edge-line ${status?.status ?? "balanced"}`);
        els.plannerConnectionsSvg.appendChild(path);

        const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
        label.setAttribute("x", String(midX));
        label.setAttribute("y", String((y1 + y2) / 2 - 6));
        label.setAttribute("text-anchor", "middle");
        label.setAttribute("class", "edge-label");
        label.textContent =
          `${itemNameById(edge.itemId)} ` +
          `${itemRateLabel(edge.itemId, status?.delta ?? 0)}`;
        els.plannerConnectionsSvg.appendChild(label);
      });
    }

    function renderPlannerSummary() {
      const nodeCount = state.planner.nodes.length;
      const edgeCount = state.planner.edges.length;
      const connectText = state.planner.connectSourceNodeId
        ? ` | connect from ${state.planner.connectSourceNodeId}`
        : "";
      els.plannerSummary.textContent =
        `${nodeCount} node(s), ${edgeCount} connection(s)` + connectText;
      els.plannerEmpty.style.display = nodeCount ? "none" : "flex";
    }

    function renderPlanner() {
      renderPlannerRecipeCandidates();
      renderPlannerNodes();
      renderPlannerEdges();
      renderPlannerConnectionOptions();
      renderPlannerConnectionsList();
      renderPlannerSummary();
    }

    function workflowPayload() {
      return {
        version: WORKFLOW_VERSION,
        defaultBeltCapacity: state.planner.defaultBeltCapacity,
        nodes: state.planner.nodes.map((node) => ({
          id: node.id,
          recipeId: node.recipeId,
          targetItemId: node.targetItemId,
          targetRatePerMinute: node.targetRatePerMinute,
          beltCapacity: node.beltCapacity,
          x: node.x,
          y: node.y
        })),
        edges: state.planner.edges.map((edge) => ({
          id: edge.id,
          sourceNodeId: edge.sourceNodeId,
          targetNodeId: edge.targetNodeId,
          itemId: edge.itemId
        }))
      };
    }

    function validateWorkflowPayload(payload) {
      if (!payload || payload.version !== WORKFLOW_VERSION) {
        throw new Error(`Unsupported workflow version: ${payload?.version}`);
      }
      if (!Array.isArray(payload.nodes) || !Array.isArray(payload.edges)) {
        throw new Error("Workflow must contain nodes and edges arrays.");
      }
      const defaultBeltCapacity =
        payload.defaultBeltCapacity === null ||
        payload.defaultBeltCapacity === undefined ||
        payload.defaultBeltCapacity === ""
          ? null
          : Number(payload.defaultBeltCapacity);
      if (
        defaultBeltCapacity !== null &&
        !BELT_CAPACITY_OPTIONS.includes(defaultBeltCapacity)
      ) {
        throw new Error(`Unsupported default belt capacity: ${defaultBeltCapacity}`);
      }
      const importedNodes = payload.nodes.map((node) => ({
        id: String(node.id),
        recipeId: String(node.recipeId),
        targetItemId: String(node.targetItemId),
        targetRatePerMinute: Number(node.targetRatePerMinute),
        beltCapacity:
          node.beltCapacity === null || node.beltCapacity === undefined || node.beltCapacity === ""
            ? null
            : Number(node.beltCapacity),
        x: Number(node.x),
        y: Number(node.y)
      }));
      const nodeIds = new Set();
      importedNodes.forEach((node) => {
        if (!node.id || nodeIds.has(node.id)) throw new Error("Workflow node ids must be unique.");
        nodeIds.add(node.id);
        const recipe = recipeById(node.recipeId);
        if (!recipe) throw new Error(`Unknown recipe id: ${node.recipeId}`);
        if (!state.items.some((item) => item.id === node.targetItemId)) {
          throw new Error(`Unknown item id: ${node.targetItemId}`);
        }
        if (!recipe.outputs.some((entry) => entry.item.id === node.targetItemId)) {
          throw new Error(`Recipe ${node.recipeId} does not produce ${node.targetItemId}`);
        }
        if (node.beltCapacity !== null && !BELT_CAPACITY_OPTIONS.includes(node.beltCapacity)) {
          throw new Error(`Unsupported belt capacity: ${node.beltCapacity}`);
        }
      });

      const getImportedNode = (nodeId) => importedNodes.find((node) => node.id === nodeId);
      payload.edges.forEach((edge) => {
        if (!edge.id) throw new Error("Workflow edge id is required.");
        if (!nodeIds.has(edge.sourceNodeId)) {
          throw new Error(`Unknown source node: ${edge.sourceNodeId}`);
        }
        if (!nodeIds.has(edge.targetNodeId)) {
          throw new Error(`Unknown target node: ${edge.targetNodeId}`);
        }
        if (!state.items.some((item) => item.id === edge.itemId)) {
          throw new Error(`Unknown item id: ${edge.itemId}`);
        }
        const sourceComputed = getPlannerNodeComputed(getImportedNode(edge.sourceNodeId));
        const targetComputed = getPlannerNodeComputed(getImportedNode(edge.targetNodeId));
        const compatible = sourceComputed.outputs
          .filter((output) => getItemRate(targetComputed.inputs, output.item.id) > 0)
          .map((output) => output.item.id);
        if (!compatible.includes(edge.itemId)) {
          throw new Error(
            `Nodes ${edge.sourceNodeId} and ${edge.targetNodeId} ` +
            `are not compatible for ${edge.itemId}`
          );
        }
      });
    }

    function importWorkflow(payload) {
      validateWorkflowPayload(payload);
      state.planner.defaultBeltCapacity =
        payload.defaultBeltCapacity === null ||
        payload.defaultBeltCapacity === undefined ||
        payload.defaultBeltCapacity === ""
          ? null
          : Number(payload.defaultBeltCapacity);
      state.planner.nodes = payload.nodes.map((node) => ({
        id: String(node.id),
        recipeId: String(node.recipeId),
        targetItemId: String(node.targetItemId),
        targetRatePerMinute: Number(node.targetRatePerMinute),
        beltCapacity:
          node.beltCapacity === null || node.beltCapacity === undefined || node.beltCapacity === ""
            ? null
            : Number(node.beltCapacity),
        x: Number(node.x),
        y: Number(node.y)
      }));
      state.planner.edges = payload.edges.map((edge) => ({
        id: String(edge.id),
        sourceNodeId: String(edge.sourceNodeId),
        targetNodeId: String(edge.targetNodeId),
        itemId: String(edge.itemId)
      }));
      state.planner.selectedNodeId = state.planner.nodes[0]?.id ?? null;
      state.planner.connectSourceNodeId = null;
      const maxNode = Math.max(
        0,
        ...state.planner.nodes.map((node) => Number(node.id.split("_")[1]) || 0)
      );
      const maxEdge = Math.max(
        0,
        ...state.planner.edges.map((edge) => Number(edge.id.split("_")[1]) || 0)
      );
      state.planner.nextNodeNumber = maxNode + 1;
      state.planner.nextEdgeNumber = maxEdge + 1;
      renderPlanner();
    }

    function exportWorkflow() {
      const blob = new Blob([JSON.stringify(workflowPayload(), null, 2)], {
        type: "application/json"
      });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "satisfactory-workflow.json";
      anchor.click();
      URL.revokeObjectURL(url);
      els.status.textContent = "Exported workflow JSON.";
    }

    function bindPlannerDragging() {
      els.plannerWorkspace.querySelectorAll(".planner-node-header").forEach((header) => {
        header.onpointerdown = (event) => {
          if (event.target.closest("[data-remove-node-id]")) return;
          const nodeEl = header.closest(".planner-node");
          const node = getPlannerNode(nodeEl.dataset.nodeId);
          if (!node) return;
          state.planner.selectedNodeId = node.id;
          const workspaceRect = els.plannerWorkspace.getBoundingClientRect();
          const nodeRect = nodeEl.getBoundingClientRect();
          const offsetX = event.clientX - nodeRect.left;
          const offsetY = event.clientY - nodeRect.top;
          header.setPointerCapture(event.pointerId);
          header.onpointermove = (moveEvent) => {
            const maxX = Math.max(0, workspaceRect.width - nodeRect.width);
            const maxY = Math.max(0, workspaceRect.height - nodeRect.height);
            node.x = Math.min(Math.max(0, moveEvent.clientX - workspaceRect.left - offsetX), maxX);
            node.y = Math.min(Math.max(0, moveEvent.clientY - workspaceRect.top - offsetY), maxY);
            nodeEl.style.left = `${node.x}px`;
            nodeEl.style.top = `${node.y}px`;
            renderPlannerEdges();
          };
          header.onpointerup = () => {
            header.onpointermove = null;
            header.onpointerup = null;
            renderPlanner();
          };
        };
      });
    }

    async function bootstrap() {
      const [recipes, items] = await Promise.all([
        fetchJson("/api/recipes"),
        fetchJson("/api/items")
      ]);
      state.recipes = recipes;
      state.items = items;
      state.currentRecipeId = recipes[0]?.id ?? null;
      state.outputItemId =
        items.find((item) => item.id === "iron_ingot")?.id ?? items[0]?.id ?? null;
      state.planner.selectedOutputItemId = state.outputItemId;
      renderOptions();
      await loadRecipe(state.currentRecipeId);
      await searchByOutput();
      renderPlanner();
    }

    els.modeButtons.forEach((button) => {
      button.addEventListener("click", () => setMode(button.dataset.mode));
    });
    els.recipeInput.addEventListener("change", () => {
      const recipeId = recipeLabelToId(els.recipeInput.value);
      if (recipeId) {
        loadRecipe(recipeId);
      } else {
        els.status.textContent = "Choose a valid recipe from the list.";
      }
    });
    els.rateSelect.addEventListener("change", async () => {
      state.rateMode = els.rateSelect.value;
      await loadRecipe(state.currentRecipeId);
    });
    els.debugToggle.addEventListener("change", async () => {
      state.debug = els.debugToggle.checked;
      renderOptions();
      await loadRecipe(state.currentRecipeId);
      await searchByOutput();
    });
    els.outputInput.addEventListener("change", () => {
      const itemId = itemLabelToId(els.outputInput.value);
      if (itemId) {
        state.outputItemId = itemId;
      }
    });
    els.searchButton.addEventListener("click", searchByOutput);
    els.plannerSearchButton.addEventListener("click", findPlannerRecipes);
    els.plannerDefaultBelt.addEventListener("change", () => {
      state.planner.defaultBeltCapacity = els.plannerDefaultBelt.value
        ? Number(els.plannerDefaultBelt.value)
        : null;
      renderOptions();
    });
    els.connectionSource.addEventListener("change", refreshConnectionItemOptions);
    els.connectionTarget.addEventListener("change", refreshConnectionItemOptions);
    els.addConnectionButton.addEventListener("click", () => {
      addPlannerConnection(
        els.connectionSource.value,
        els.connectionTarget.value,
        els.connectionItem.value
      );
    });
    els.exportWorkflowButton.addEventListener("click", exportWorkflow);
    els.importWorkflowButton.addEventListener("click", () => els.importWorkflowInput.click());
    els.importWorkflowInput.addEventListener("change", async () => {
      const file = els.importWorkflowInput.files?.[0];
      if (!file) return;
      try {
        importWorkflow(JSON.parse(await file.text()));
        setMode("planner");
        els.status.textContent = "Imported workflow JSON.";
      } catch (error) {
        els.status.textContent = `Failed to import workflow: ${error.message}`;
      } finally {
        els.importWorkflowInput.value = "";
      }
    });
    window.addEventListener("resize", renderPlannerEdges);

    bootstrap().catch((error) => {
      console.error(error);
      els.status.textContent = `Failed to load app data: ${error.message}`;
    });
"""
