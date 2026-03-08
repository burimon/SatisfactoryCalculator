SCRIPT = r"""
    const WORKFLOW_VERSION = 1;
    const POWER_ITEM_ID = "power";
    const BELT_CAPACITY_OPTIONS = [60, 120, 270, 480, 780];
    const DEFAULT_NODE_WIDTH = 280;
    const DEFAULT_NODE_HEIGHT = 210;
    const MIN_NODE_WIDTH = 220;
    const MIN_NODE_HEIGHT = 160;
    const state = {
      mode: "browser",
      recipes: [],
      items: [],
      currentRecipeId: null,
      rateMode: "per_cycle",
      debug: false,
      outputItemId: null,
      planner: {
        workflowName: "Untitled Workflow",
        workflowDirectory: "",
        availableWorkflows: [],
        selectedWorkflowFilename: "",
        selectedOutputItemId: null,
        defaultBeltCapacity: 60,
        candidateRecipes: [],
        popup: {
          visible: false,
          canvasX: 0,
          canvasY: 0,
          screenX: 12,
          screenY: 12,
          outputItemId: null,
          candidateRecipes: [],
          selectedRecipeId: null
        },
        targetPopup: {
          visible: false,
          nodeId: null,
          itemId: null,
          screenX: 12,
          screenY: 12
        },
        dragConnection: {
          active: false,
          sourceNodeId: null,
          itemId: null,
          startX: 0,
          startY: 0,
          currentX: 0,
          currentY: 0,
          validTargetNodeId: null
        },
        nodes: [],
        edges: [],
        panX: 0,
        panY: 0,
        zoom: 1,
        selectedNodeId: null,
        connectSourcePort: null,
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
      plannerWorkflowName: document.getElementById("planner-workflow-name"),
      plannerSavedWorkflows: document.getElementById("planner-saved-workflows"),
      plannerWorkflowDirectory: document.getElementById("planner-workflow-directory"),
      plannerRefreshWorkflows: document.getElementById("planner-refresh-workflows"),
      newWorkflowButton: document.getElementById("new-workflow-button"),
      plannerOutputInput: document.getElementById("planner-output-input"),
      plannerOutputOptions: document.getElementById("planner-output-options"),
      plannerSearchButton: document.getElementById("planner-search-button"),
      plannerRecipeResults: document.getElementById("planner-recipe-results"),
      plannerWorkspace: document.getElementById("planner-workspace"),
      plannerCanvas: document.getElementById("planner-canvas"),
      plannerConnectionsSvg: document.getElementById("planner-connections-svg"),
      plannerConnectionLabels: document.getElementById("planner-connection-labels"),
      plannerTargetPopup: document.getElementById("planner-target-popup"),
      plannerTargetPopupTitle: document.getElementById("planner-target-popup-title"),
      plannerTargetPopupRate: document.getElementById("planner-target-popup-rate"),
      plannerTargetPopupSave: document.getElementById("planner-target-popup-save"),
      plannerTargetPopupCancel: document.getElementById("planner-target-popup-cancel"),
      plannerAddPopup: document.getElementById("planner-add-popup"),
      plannerPopupOutputInput: document.getElementById("planner-popup-output-input"),
      plannerPopupOutputOptions: document.getElementById("planner-popup-output-options"),
      plannerPopupSearch: document.getElementById("planner-popup-search"),
      plannerPopupRecipe: document.getElementById("planner-popup-recipe"),
      plannerPopupConfirm: document.getElementById("planner-popup-confirm"),
      plannerPopupCancel: document.getElementById("planner-popup-cancel"),
      plannerEmpty: document.getElementById("planner-empty"),
      plannerSummary: document.getElementById("planner-summary"),
      plannerZoomOut: document.getElementById("planner-zoom-out"),
      plannerZoomReset: document.getElementById("planner-zoom-reset"),
      plannerZoomIn: document.getElementById("planner-zoom-in"),
      exportWorkflowButton: document.getElementById("export-workflow-button"),
      importWorkflowButton: document.getElementById("import-workflow-button"),
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

    function perMachineRate(targetItemId, baseRate, beltCapacity) {
      if (isPowerItem(targetItemId) || beltCapacity === null) {
        return baseRate;
      }
      return Math.min(baseRate, beltCapacity);
    }

    function defaultBeltLabel(capacity) {
      if (capacity === null) {
        return "Unlimited";
      }
      const beltMk = BELT_CAPACITY_OPTIONS.indexOf(capacity) + 1;
      return `Mk ${beltMk} (${capacity}/min)`;
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
      return formatAmount(entry.amount_per_minute);
    }

    function itemRateLabel(itemId, amount) {
      const prefix = amount > 0.01 ? "+" : "";
      return `${prefix}${formatAmount(amount)}`;
    }

    function clampZoom(zoom) {
      return Math.min(Math.max(zoom, 0.5), 2.5);
    }

    function clientToCanvasPoint(clientX, clientY) {
      const rect = els.plannerWorkspace.getBoundingClientRect();
      return {
        x: (clientX - rect.left - state.planner.panX) / state.planner.zoom,
        y: (clientY - rect.top - state.planner.panY) / state.planner.zoom
      };
    }

    function selectedWorkflowRecord() {
      return state.planner.availableWorkflows.find(
        (workflow) => workflow.filename === state.planner.selectedWorkflowFilename
      ) ?? null;
    }

    function closePlannerPopup() {
      state.planner.popup.visible = false;
      state.planner.popup.outputItemId = null;
      state.planner.popup.candidateRecipes = [];
      state.planner.popup.selectedRecipeId = null;
      renderPlannerPopup();
    }

    function openTargetPopup(nodeId, itemId, clientX, clientY) {
      const node = getPlannerNode(nodeId);
      if (!node) return;
      const workspaceRect = els.plannerWorkspace.getBoundingClientRect();
      state.planner.targetPopup.visible = true;
      state.planner.targetPopup.nodeId = nodeId;
      state.planner.targetPopup.itemId = itemId;
      state.planner.targetPopup.screenX = Math.max(12, clientX - workspaceRect.left);
      state.planner.targetPopup.screenY = Math.max(12, clientY - workspaceRect.top);
      renderTargetPopup();
      els.plannerTargetPopupRate.focus();
      els.plannerTargetPopupRate.select();
    }

    function closeTargetPopup() {
      state.planner.targetPopup.visible = false;
      state.planner.targetPopup.nodeId = null;
      state.planner.targetPopup.itemId = null;
      renderTargetPopup();
    }

    function resetPlannerWorkflow() {
      state.planner.workflowName = "Blank";
      state.planner.nodes = [];
      state.planner.edges = [];
      state.planner.selectedNodeId = null;
      state.planner.connectSourcePort = null;
      state.planner.selectedWorkflowFilename = "";
      state.planner.nextNodeNumber = 1;
      state.planner.nextEdgeNumber = 1;
      closePlannerPopup();
      closeTargetPopup();
      renderOptions();
      renderPlanner();
      setMode("planner");
      els.status.textContent = "Started a new blank plan.";
    }

    function openPlannerPopup(clientX, clientY) {
      const canvasPoint = clientToCanvasPoint(clientX, clientY);
      const workspaceRect = els.plannerWorkspace.getBoundingClientRect();
      state.planner.popup.visible = true;
      state.planner.popup.canvasX = canvasPoint.x;
      state.planner.popup.canvasY = canvasPoint.y;
      state.planner.popup.screenX = Math.max(12, clientX - workspaceRect.left);
      state.planner.popup.screenY = Math.max(12, clientY - workspaceRect.top);
      state.planner.popup.outputItemId = null;
      state.planner.popup.candidateRecipes = [];
      state.planner.popup.selectedRecipeId = null;
      renderPlannerPopup();
      els.plannerPopupOutputInput.focus();
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

    function recipeEntryRatePerMinute(recipe, itemId) {
      const output = recipe.outputs.find((entry) => entry.item.id === itemId);
      if (output) {
        return isPowerItem(itemId) ? output.amount : (output.amount * 60) / recipe.duration_seconds;
      }
      const input = recipe.inputs.find((entry) => entry.item.id === itemId);
      if (input) {
        return isPowerItem(itemId) ? input.amount : (input.amount * 60) / recipe.duration_seconds;
      }
      return null;
    }

    function scaledRecipeRates(recipe, targetItemId, targetRatePerMinute, beltCapacity = null) {
      const targetBaseRate = recipeEntryRatePerMinute(recipe, targetItemId);
      if (!targetBaseRate) {
        throw new Error(`Recipe ${recipe.id} does not use ${targetItemId}`);
      }
      const multiplier = targetRatePerMinute / targetBaseRate;
      const entryRatePerMinute = (entry) =>
        isPowerItem(entry.item.id)
          ? entry.amount
          : (entry.amount * 60) / recipe.duration_seconds;
      const scaledRequirements = [...recipe.inputs, ...recipe.outputs].map((entry) => {
        const baseRate = entryRatePerMinute(entry);
        const cappedRate = perMachineRate(entry.item.id, baseRate, beltCapacity);
        const totalRate = baseRate * multiplier;
        return cappedRate === 0 ? 0 : totalRate / cappedRate;
      });
      const machineCount = scaledRequirements.length
        ? Math.max(...scaledRequirements)
        : 0;
      const machineRate = perMachineRate(targetItemId, targetBaseRate, beltCapacity);
      const scaleEntries = (entries) => entries.map((entry) => ({
        item: entry.item,
        amount_per_minute: entryRatePerMinute(entry) * multiplier
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
          state.planner.defaultBeltCapacity ?? null
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

    function totalIncomingRate(targetNodeId, itemId) {
      return state.planner.edges
        .filter((edge) => edge.targetNodeId === targetNodeId && edge.itemId === itemId)
        .reduce((total, edge) => {
          const sourceComputed = getPlannerNodeComputed(getPlannerNode(edge.sourceNodeId));
          return total + getItemRate(sourceComputed?.outputs ?? [], itemId);
        }, 0);
    }

    function getConnectionStatus(edge) {
      const sourceComputed = getPlannerNodeComputed(getPlannerNode(edge.sourceNodeId));
      const targetComputed = getPlannerNodeComputed(getPlannerNode(edge.targetNodeId));
      if (!sourceComputed || !targetComputed) return null;
      const sourceRate = getItemRate(sourceComputed.outputs, edge.itemId);
      const targetRate = getItemRate(targetComputed.inputs, edge.itemId);
      const totalSourceRate = totalIncomingRate(edge.targetNodeId, edge.itemId);
      const delta = totalSourceRate - targetRate;
      let status = "balanced";
      if (delta > 0.01) status = "source_surplus";
      if (delta < -0.01) status = "target_shortage";
      return { sourceRate, totalSourceRate, targetRate, delta, status };
    }

    function connectionAnchorPoint(fromRect, toRect) {
      const fromCenterX = fromRect.x + fromRect.width / 2;
      const fromCenterY = fromRect.y + fromRect.height / 2;
      const toCenterX = toRect.x + toRect.width / 2;
      const toCenterY = toRect.y + toRect.height / 2;
      const dx = toCenterX - fromCenterX;
      const dy = toCenterY - fromCenterY;
      const halfWidth = fromRect.width / 2;
      const halfHeight = fromRect.height / 2;

      if (Math.abs(dx) < 0.0001 && Math.abs(dy) < 0.0001) {
        return { x: fromCenterX + halfWidth, y: fromCenterY };
      }

      const scaleX = halfWidth / Math.max(Math.abs(dx), 0.0001);
      const scaleY = halfHeight / Math.max(Math.abs(dy), 0.0001);
      const scale = Math.min(scaleX, scaleY);

      return {
        x: fromCenterX + dx * scale,
        y: fromCenterY + dy * scale
      };
    }

    function portAnchorPoint(portEl, side) {
      const rect = portEl.getBoundingClientRect();
      const clientX = side === "left" ? rect.left : rect.right;
      const clientY = rect.top + rect.height / 2;
      return clientToCanvasPoint(clientX, clientY);
    }

    function dragTargetFromClientPoint(clientX, clientY, itemId, sourceNodeId) {
      const element = document.elementFromPoint(clientX, clientY);
      const port = element?.closest?.('[data-port-type="input"]');
      if (!port) return null;
      if (port.dataset.portItemId !== itemId) return null;
      if (port.dataset.portNodeId === sourceNodeId) return null;
      return {
        nodeId: port.dataset.portNodeId,
        itemId: port.dataset.portItemId
      };
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
            ${defaultBeltLabel(capacity)}
          </option>
        `).join("")}
      `;
      els.plannerDefaultBelt.value =
        state.planner.defaultBeltCapacity === null
          ? ""
          : String(state.planner.defaultBeltCapacity);
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
      if (
        state.planner.selectedWorkflowFilename &&
        state.planner.availableWorkflows.some(
          (workflow) => workflow.filename === state.planner.selectedWorkflowFilename
        )
      ) {
        els.plannerSavedWorkflows.value = state.planner.selectedWorkflowFilename;
      } else {
        els.plannerSavedWorkflows.value = state.planner.availableWorkflows[0]?.filename ?? "";
      }
      els.plannerSavedWorkflows.disabled = state.planner.availableWorkflows.length === 0;
      els.plannerWorkflowDirectory.textContent = state.planner.workflowDirectory
        ? `Workflow library: ${state.planner.workflowDirectory}`
        : "Workflow library unavailable.";
      els.plannerPopupOutputOptions.innerHTML = els.plannerOutputOptions.innerHTML;
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

    async function postJson(path, payload) {
      const response = await fetch(path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || `Request failed: ${response.status}`);
      }
      return response.json();
    }

    async function refreshWorkflows(preferredFilename = null) {
      const payload = await fetchJson("/api/workflows");
      state.planner.workflowDirectory = payload.directory ?? "";
      state.planner.availableWorkflows = Array.isArray(payload.files) ? payload.files : [];
      if (
        preferredFilename &&
        state.planner.availableWorkflows.some((workflow) => workflow.filename === preferredFilename)
      ) {
        state.planner.selectedWorkflowFilename = preferredFilename;
      } else if (
        state.planner.selectedWorkflowFilename &&
        state.planner.availableWorkflows.some(
          (workflow) => workflow.filename === state.planner.selectedWorkflowFilename
        )
      ) {
        state.planner.selectedWorkflowFilename = state.planner.selectedWorkflowFilename;
      } else {
        state.planner.selectedWorkflowFilename =
          state.planner.availableWorkflows[0]?.filename ?? "";
      }
      renderOptions();
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
      addPlannerNodeAt(recipeId, targetItemId, null, null);
    }

    function addPlannerNodeAt(recipeId, targetItemId, canvasX, canvasY) {
      const recipe = recipeById(recipeId);
      if (!recipe) return;
      const targetRatePerMinute = recipeEntryRatePerMinute(recipe, targetItemId) ?? 0;
      const columnOffset = state.planner.nodes.length % 3;
      const rowOffset = Math.floor(state.planner.nodes.length / 3);
      const node = {
        id: newNodeId(),
        recipeId,
        targetItemId,
        targetRatePerMinute,
        beltCapacity: null,
        x: canvasX ?? 28 + columnOffset * 300,
        y: canvasY ?? 28 + rowOffset * 260,
        width: DEFAULT_NODE_WIDTH,
        height: DEFAULT_NODE_HEIGHT
      };
      state.planner.nodes.push(node);
      state.planner.selectedNodeId = node.id;
      closePlannerPopup();
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

    async function findPlannerPopupRecipes() {
      const item = state.items.find(
        (candidate) => candidate.name === els.plannerPopupOutputInput.value
      );
      if (!item) {
        els.status.textContent = "Choose a valid output item for the new node.";
        return;
      }
      state.planner.popup.outputItemId = item.id;
      state.planner.popup.candidateRecipes = await fetchJson(`/api/recipes/by-output/${item.id}`);
      state.planner.popup.selectedRecipeId = state.planner.popup.candidateRecipes[0]?.id ?? null;
      renderPlannerPopup();
    }

    function renderPlannerPopup() {
      if (!state.planner.popup.visible) {
        els.plannerAddPopup.hidden = true;
        return;
      }
      els.plannerAddPopup.hidden = false;
      els.plannerAddPopup.style.left = `${state.planner.popup.screenX}px`;
      els.plannerAddPopup.style.top = `${state.planner.popup.screenY}px`;
      const selectedItem = state.items.find(
        (item) => item.id === state.planner.popup.outputItemId
      );
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

    function renderTargetPopup() {
      if (!state.planner.targetPopup.visible) {
        els.plannerTargetPopup.hidden = true;
        return;
      }
      const node = getPlannerNode(state.planner.targetPopup.nodeId);
      if (!node) {
        closeTargetPopup();
        return;
      }
      els.plannerTargetPopup.hidden = false;
      els.plannerTargetPopup.style.left = `${state.planner.targetPopup.screenX}px`;
      els.plannerTargetPopup.style.top = `${state.planner.targetPopup.screenY}px`;
      els.plannerTargetPopupTitle.textContent = itemNameById(state.planner.targetPopup.itemId);
      els.plannerTargetPopupRate.value = formatAmount(node.targetRatePerMinute);
    }

    function plannerIoMarkup(node, computed, entries, portType) {
      return entries.length
        ? entries.map((entry) => {
            const isTarget = entry.item.id === node.targetItemId;
            return `
              <button
                type="button"
                class="mini-list-row planner-port ${isTarget ? "is-target" : ""}"
                data-port-node-id="${node.id}"
                data-port-item-id="${entry.item.id}"
                data-port-type="${portType}"
              >
                <span class="planner-port-handle ${portType}"></span>
                <span class="planner-port-name">
                  ${entry.item.name}
                </span>
                <span class="planner-port-amount">${plannerEntryAmount(entry)}</span>
              </button>
            `;
          }).join("")
        : '<div class="empty">None</div>';
    }

    function renderPlannerNodes() {
      els.plannerCanvas.querySelectorAll(".planner-node").forEach((node) => node.remove());
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
        nodeEl.style.width = `${node.width ?? DEFAULT_NODE_WIDTH}px`;
        nodeEl.style.height = `${node.height ?? DEFAULT_NODE_HEIGHT}px`;
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
            <div class="planner-node-meta compact">
              <div class="metric-card wide">
                <div class="label">Machines Needed</div>
                <div class="value">${formatAmount(computed.machine_count)}</div>
              </div>
            </div>
            <div class="planner-node-grid">
              <section class="planner-io-column inputs">
                <h4>Inputs</h4>
                <div class="mini-list">
                  ${plannerIoMarkup(node, computed, computed.inputs, "input")}
                </div>
              </section>
              <section class="planner-io-column outputs">
                <h4>Outputs</h4>
                <div class="mini-list">
                  ${plannerIoMarkup(node, computed, computed.outputs, "output")}
                </div>
              </section>
            </div>
          </div>
          <div
            class="planner-resize-handle left"
            data-resize-node="${node.id}"
            data-resize-edge="left"
          ></div>
          <div
            class="planner-resize-handle right"
            data-resize-node="${node.id}"
            data-resize-edge="right"
          ></div>
          <div
            class="planner-resize-handle top"
            data-resize-node="${node.id}"
            data-resize-edge="top"
          ></div>
          <div
            class="planner-resize-handle bottom"
            data-resize-node="${node.id}"
            data-resize-edge="bottom"
          ></div>
        `;
        nodeEl.addEventListener("click", (event) => {
          if (event.target.closest("button, input")) {
            return;
          }
          state.planner.selectedNodeId = node.id;
          renderPlanner();
        });
        els.plannerCanvas.appendChild(nodeEl);
      });

      els.plannerCanvas.querySelectorAll("[data-remove-node-id]").forEach((button) => {
        button.addEventListener("click", (event) => {
          event.stopPropagation();
          removePlannerNode(button.dataset.removeNodeId);
        });
      });

      els.plannerCanvas.querySelectorAll('[data-port-type="input"]').forEach((button) => {
        button.addEventListener("click", (event) => {
          event.stopPropagation();
          const nodeId = button.dataset.portNodeId;
          const itemId = button.dataset.portItemId;
          const node = getPlannerNode(nodeId);
          const computed = getPlannerNodeComputed(node);
          if (!node || !computed) return;
          const currentRate = getItemRate(computed.inputs, itemId);
          updatePlannerNode(nodeId, {
            targetItemId: itemId,
            targetRatePerMinute: currentRate
          });
          openTargetPopup(nodeId, itemId, event.clientX, event.clientY);
        });
      });

      els.plannerCanvas.querySelectorAll('[data-port-type="output"]').forEach((button) => {
        button.addEventListener("pointerdown", (event) => {
          if (event.button !== 0) return;
          event.stopPropagation();
          closeTargetPopup();
          const anchor = portAnchorPoint(button, "right");
          state.planner.dragConnection = {
            active: true,
            sourceNodeId: button.dataset.portNodeId,
            itemId: button.dataset.portItemId,
            startX: anchor.x,
            startY: anchor.y,
            currentX: anchor.x,
            currentY: anchor.y,
            validTargetNodeId: null
          };
          button.dataset.dragging = "false";
          button.dataset.pointerHandled = "false";
          const startClientX = event.clientX;
          const startClientY = event.clientY;
          button.setPointerCapture(event.pointerId);
          button.onpointermove = (moveEvent) => {
            const point = clientToCanvasPoint(moveEvent.clientX, moveEvent.clientY);
            state.planner.dragConnection.currentX = point.x;
            state.planner.dragConnection.currentY = point.y;
            const target = dragTargetFromClientPoint(
              moveEvent.clientX,
              moveEvent.clientY,
              button.dataset.portItemId,
              button.dataset.portNodeId
            );
            state.planner.dragConnection.validTargetNodeId = target?.nodeId ?? null;
            if (
              Math.abs(moveEvent.clientX - startClientX) > 4 ||
              Math.abs(moveEvent.clientY - startClientY) > 4
            ) {
              button.dataset.dragging = "true";
            }
            els.status.textContent = target
              ? `Release to connect ${itemNameById(button.dataset.portItemId)}.`
              : "Drag to a matching input to create a connection.";
            renderPlannerEdges();
          };
          button.onpointerup = (upEvent) => {
            const target = dragTargetFromClientPoint(
              upEvent.clientX,
              upEvent.clientY,
              button.dataset.portItemId,
              button.dataset.portNodeId
            );
            if (button.dataset.dragging === "true") {
              if (target) {
                addPlannerConnection(button.dataset.portNodeId, target.nodeId, target.itemId);
              } else {
                els.status.textContent = "Release on a matching input to create a connection.";
              }
            } else {
              const nodeId = button.dataset.portNodeId;
              const itemId = button.dataset.portItemId;
              const node = getPlannerNode(nodeId);
              const computed = getPlannerNodeComputed(node);
              if (node && computed) {
                const currentRate = getItemRate(computed.outputs, itemId);
                updatePlannerNode(nodeId, {
                  targetItemId: itemId,
                  targetRatePerMinute: currentRate
                });
                openTargetPopup(nodeId, itemId, upEvent.clientX, upEvent.clientY);
              }
            }
            button.dataset.pointerHandled = "true";
            state.planner.dragConnection = {
              active: false,
              sourceNodeId: null,
              itemId: null,
              startX: 0,
              startY: 0,
              currentX: 0,
              currentY: 0,
              validTargetNodeId: null
            };
            button.onpointermove = null;
            button.onpointerup = null;
            renderPlanner();
          };
        });
        button.addEventListener("click", (event) => {
          event.stopPropagation();
          if (button.dataset.pointerHandled === "true") {
            button.dataset.pointerHandled = "false";
            button.dataset.dragging = "false";
            return;
          }
        });
      });

      bindPlannerDragging();
    }

    function renderPlannerEdges() {
      const worldPadding = 240;
      const workspaceRect = els.plannerWorkspace.getBoundingClientRect();
      const topLeft = clientToCanvasPoint(workspaceRect.left, workspaceRect.top);
      const bottomRight = clientToCanvasPoint(workspaceRect.right, workspaceRect.bottom);
      let minX = topLeft.x - worldPadding;
      let minY = topLeft.y - worldPadding;
      let maxX = bottomRight.x + worldPadding;
      let maxY = bottomRight.y + worldPadding;
      els.plannerConnectionsSvg.innerHTML = "";
      els.plannerConnectionLabels.innerHTML = "";
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
      els.plannerConnectionsSvg.appendChild(defs);
      const dragState = state.planner.dragConnection;
      state.planner.edges.forEach((edge) => {
        const sourceEl = els.plannerCanvas.querySelector(
          `[data-node-id="${edge.sourceNodeId}"]`
        );
        const targetEl = els.plannerCanvas.querySelector(
          `[data-node-id="${edge.targetNodeId}"]`
        );
        const sourcePortEl = els.plannerCanvas.querySelector(
          `[data-port-node-id="${edge.sourceNodeId}"][data-port-item-id="${edge.itemId}"][data-port-type="output"]`
        );
        const targetPortEl = els.plannerCanvas.querySelector(
          `[data-port-node-id="${edge.targetNodeId}"][data-port-item-id="${edge.itemId}"][data-port-type="input"]`
        );
        if (!sourceEl || !targetEl) return;
        const sourceNode = getPlannerNode(edge.sourceNodeId);
        const targetNode = getPlannerNode(edge.targetNodeId);
        if (!sourceNode || !targetNode) return;
        const sourceRect = {
          x: sourceNode.x,
          y: sourceNode.y,
          width: sourceEl.offsetWidth,
          height: sourceEl.offsetHeight
        };
        const targetRect = {
          x: targetNode.x,
          y: targetNode.y,
          width: targetEl.offsetWidth,
          height: targetEl.offsetHeight
        };
        const sourceAnchor = sourcePortEl
          ? portAnchorPoint(sourcePortEl, "right")
          : connectionAnchorPoint(sourceRect, targetRect);
        const targetAnchor = targetPortEl
          ? portAnchorPoint(targetPortEl, "left")
          : connectionAnchorPoint(targetRect, sourceRect);
        const x1 = sourceAnchor.x;
        const y1 = sourceAnchor.y;
        const x2 = targetAnchor.x;
        const y2 = targetAnchor.y;
        minX = Math.min(minX, sourceNode.x - worldPadding, targetNode.x - worldPadding);
        minY = Math.min(minY, sourceNode.y - worldPadding, targetNode.y - worldPadding);
        maxX = Math.max(
          maxX,
          sourceNode.x + sourceRect.width + worldPadding,
          targetNode.x + targetRect.width + worldPadding
        );
        maxY = Math.max(
          maxY,
          sourceNode.y + sourceRect.height + worldPadding,
          targetNode.y + targetRect.height + worldPadding
        );
        const dx = x2 - x1;
        const dy = y2 - y1;
        const curve = Math.max(80, Math.min(220, Math.abs(dx) * 0.45 + Math.abs(dy) * 0.15));
        const control1X = x1 + Math.sign(dx || 1) * curve;
        const control1Y = y1;
        const control2X = x2 - Math.sign(dx || 1) * curve;
        const control2Y = y2;
        const status = getConnectionStatus(edge);

        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        path.setAttribute(
          "d",
          `M ${x1 - minX} ${y1 - minY} ` +
          `C ${control1X - minX} ${control1Y - minY}, ` +
          `${control2X - minX} ${control2Y - minY}, ${x2 - minX} ${y2 - minY}`
        );
        path.setAttribute("class", `edge-line ${status?.status ?? "balanced"}`);
        path.setAttribute("marker-end", "url(#planner-edge-arrow)");
        els.plannerConnectionsSvg.appendChild(path);
        const labelWorldX = (
          0.125 * x1 +
          0.375 * control1X +
          0.375 * control2X +
          0.125 * x2
        );
        const labelWorldY = (
          0.125 * y1 +
          0.375 * control1Y +
          0.375 * control2Y +
          0.125 * y2
        ) - 22;
        const label = document.createElement("div");
        label.className = `planner-connection-label ${status?.status ?? "balanced"}`;
        label.innerHTML = `
          <span>
            ${itemNameById(edge.itemId)} ${itemRateLabel(edge.itemId, status?.delta ?? 0)}
          </span>
          <button type="button" class="connection-delete-button" data-remove-edge-id="${edge.id}">
            x
          </button>
        `;
        label.style.left =
          `${labelWorldX * state.planner.zoom + state.planner.panX}px`;
        label.style.top =
          `${labelWorldY * state.planner.zoom + state.planner.panY}px`;
        label.style.transform = `translate(-50%, -50%) scale(${state.planner.zoom})`;
        els.plannerConnectionLabels.appendChild(label);
      });
      if (dragState.active && dragState.sourceNodeId && dragState.itemId) {
        const dragStatus = dragState.validTargetNodeId ? "balanced" : "target_shortage";
        const previewDx = dragState.currentX - dragState.startX;
        const previewCurve = Math.max(80, Math.min(220, Math.abs(previewDx) * 0.45));
        const previewPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
        previewPath.setAttribute(
          "d",
          `M ${dragState.startX - minX} ${dragState.startY - minY} ` +
          `C ${dragState.startX + previewCurve - minX} ${dragState.startY - minY}, ` +
          `${dragState.currentX - previewCurve - minX} ${dragState.currentY - minY}, ` +
          `${dragState.currentX - minX} ${dragState.currentY - minY}`
        );
        previewPath.setAttribute("class", `edge-line ${dragStatus} edge-preview`);
        previewPath.setAttribute("marker-end", "url(#planner-edge-arrow)");
        els.plannerConnectionsSvg.appendChild(previewPath);
      }
      const svgWidth = Math.max(1, maxX - minX);
      const svgHeight = Math.max(1, maxY - minY);
      els.plannerConnectionsSvg.style.left = `${minX}px`;
      els.plannerConnectionsSvg.style.top = `${minY}px`;
      els.plannerConnectionsSvg.style.width = `${svgWidth}px`;
      els.plannerConnectionsSvg.style.height = `${svgHeight}px`;
      els.plannerConnectionsSvg.setAttribute("viewBox", `0 0 ${svgWidth} ${svgHeight}`);

      els.plannerConnectionLabels.querySelectorAll("[data-remove-edge-id]").forEach((button) => {
        button.addEventListener("click", (event) => {
          event.stopPropagation();
          removePlannerConnection(button.dataset.removeEdgeId);
        });
      });
    }

    function renderPlannerSummary() {
      const nodeCount = state.planner.nodes.length;
      const edgeCount = state.planner.edges.length;
      const selectedWorkflowName = selectedWorkflowRecord()?.name ?? "unsaved";
      const zoomText = ` | zoom ${Math.round(state.planner.zoom * 100)}%`;
      els.plannerSummary.textContent =
        `${nodeCount} node(s), ${edgeCount} connection(s) | saved ${selectedWorkflowName}` +
        zoomText;
      els.plannerEmpty.style.display = nodeCount ? "none" : "flex";
    }

    function renderPlanner() {
      els.plannerCanvas.style.transform =
        `translate(${state.planner.panX}px, ${state.planner.panY}px) scale(${state.planner.zoom})`;
      els.plannerZoomReset.textContent = `${Math.round(state.planner.zoom * 100)}%`;
      renderPlannerRecipeCandidates();
      renderPlannerNodes();
      renderPlannerEdges();
      renderPlannerPopup();
      renderTargetPopup();
      renderPlannerSummary();
    }

    function workflowPayload() {
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
      const workflowName =
        typeof payload.name === "string"
          ? payload.name
          : payload.name === undefined || payload.name === null
            ? ""
            : String(payload.name);
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
      if (workflowName.length > 80) {
        throw new Error("Workflow name must be 80 characters or fewer.");
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
        width:
          node.width === null || node.width === undefined || node.width === ""
            ? DEFAULT_NODE_WIDTH
            : Number(node.width),
        height:
          node.height === null || node.height === undefined || node.height === ""
            ? DEFAULT_NODE_HEIGHT
            : Number(node.height),
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
        const recipeUsesTarget =
          recipe.outputs.some((entry) => entry.item.id === node.targetItemId) ||
          recipe.inputs.some((entry) => entry.item.id === node.targetItemId);
        if (!recipeUsesTarget) {
          throw new Error(`Recipe ${node.recipeId} does not use ${node.targetItemId}`);
        }
        if (node.beltCapacity !== null && !BELT_CAPACITY_OPTIONS.includes(node.beltCapacity)) {
          throw new Error(`Unsupported belt capacity: ${node.beltCapacity}`);
        }
        if (!Number.isFinite(node.width) || node.width < MIN_NODE_WIDTH) {
          throw new Error(`Node ${node.id} width is invalid.`);
        }
        if (!Number.isFinite(node.height) || node.height < MIN_NODE_HEIGHT) {
          throw new Error(`Node ${node.id} height is invalid.`);
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
      state.planner.workflowName =
        typeof payload.name === "string" && payload.name.trim()
          ? payload.name.trim()
          : "Untitled Workflow";
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
        width:
          node.width === null || node.width === undefined || node.width === ""
            ? DEFAULT_NODE_WIDTH
            : Number(node.width),
        height:
          node.height === null || node.height === undefined || node.height === ""
            ? DEFAULT_NODE_HEIGHT
            : Number(node.height),
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
      state.planner.connectSourcePort = null;
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
      renderOptions();
      renderPlanner();
    }

    async function exportWorkflow() {
      const result = await postJson("/api/workflows", workflowPayload());
      await refreshWorkflows(result.filename);
      renderPlannerSummary();
      els.status.textContent =
        `Exported workflow JSON to ${result.path}.`;
    }

    async function importSelectedWorkflow() {
      const filename = els.plannerSavedWorkflows.value || state.planner.selectedWorkflowFilename;
      if (!filename) {
        els.status.textContent = "Choose a saved workflow to import.";
        return;
      }
      const payload = await fetchJson(`/api/workflows/${encodeURIComponent(filename)}`);
      importWorkflow(payload);
      state.planner.selectedWorkflowFilename = filename;
      renderOptions();
      renderPlannerSummary();
      setMode("planner");
      const workflow = selectedWorkflowRecord();
      els.status.textContent =
        `Imported workflow JSON from ${workflow?.name ?? filename}.`;
    }

    function bindPlannerDragging() {
      els.plannerCanvas.querySelectorAll(".planner-node-header").forEach((header) => {
        header.onpointerdown = (event) => {
          if (event.target.closest("[data-remove-node-id]")) return;
          const nodeEl = header.closest(".planner-node");
          const node = getPlannerNode(nodeEl.dataset.nodeId);
          if (!node) return;
          state.planner.selectedNodeId = node.id;
          const startPoint = clientToCanvasPoint(event.clientX, event.clientY);
          const offsetX = startPoint.x - node.x;
          const offsetY = startPoint.y - node.y;
          header.setPointerCapture(event.pointerId);
          header.onpointermove = (moveEvent) => {
            const point = clientToCanvasPoint(moveEvent.clientX, moveEvent.clientY);
            node.x = point.x - offsetX;
            node.y = point.y - offsetY;
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

      els.plannerCanvas.querySelectorAll("[data-resize-node]").forEach((handle) => {
        handle.onpointerdown = (event) => {
          event.stopPropagation();
          const node = getPlannerNode(handle.dataset.resizeNode);
          const nodeEl = els.plannerCanvas.querySelector(
            `[data-node-id="${handle.dataset.resizeNode}"]`
          );
          if (!node || !nodeEl) return;
          const edge = handle.dataset.resizeEdge;
          const startPoint = clientToCanvasPoint(event.clientX, event.clientY);
          const startX = startPoint.x;
          const startY = startPoint.y;
          const startNode = {
            x: node.x,
            y: node.y,
            width: node.width ?? nodeEl.offsetWidth,
            height: node.height ?? nodeEl.offsetHeight
          };
          handle.setPointerCapture(event.pointerId);
          handle.onpointermove = (moveEvent) => {
            const point = clientToCanvasPoint(moveEvent.clientX, moveEvent.clientY);
            const dx = point.x - startX;
            const dy = point.y - startY;
            if (edge === "right") {
              node.width = Math.max(MIN_NODE_WIDTH, startNode.width + dx);
            }
            if (edge === "left") {
              const nextWidth = Math.max(MIN_NODE_WIDTH, startNode.width - dx);
              node.x = startNode.x + (startNode.width - nextWidth);
              node.width = nextWidth;
            }
            if (edge === "bottom") {
              node.height = Math.max(MIN_NODE_HEIGHT, startNode.height + dy);
            }
            if (edge === "top") {
              const nextHeight = Math.max(MIN_NODE_HEIGHT, startNode.height - dy);
              node.y = startNode.y + (startNode.height - nextHeight);
              node.height = nextHeight;
            }
            nodeEl.style.left = `${node.x}px`;
            nodeEl.style.top = `${node.y}px`;
            nodeEl.style.width = `${node.width}px`;
            nodeEl.style.height = `${node.height}px`;
            renderPlannerEdges();
          };
          handle.onpointerup = () => {
            handle.onpointermove = null;
            handle.onpointerup = null;
            renderPlanner();
          };
        };
      });
    }

    function bindPlannerWorkspaceInteractions() {
      let isPanning = false;
      let panStartX = 0;
      let panStartY = 0;
      let pointerId = null;
      let spacePressed = false;

      document.addEventListener("keydown", (event) => {
        if (event.code === "Space") {
          spacePressed = true;
        }
      });
      document.addEventListener("keyup", (event) => {
        if (event.code === "Space") {
          spacePressed = false;
        }
      });

      els.plannerWorkspace.addEventListener(
        "wheel",
        (event) => {
          event.preventDefault();
          const rect = els.plannerWorkspace.getBoundingClientRect();
          const cursorX = event.clientX - rect.left;
          const cursorY = event.clientY - rect.top;
          const canvasPoint = clientToCanvasPoint(event.clientX, event.clientY);
          const delta = event.deltaY < 0 ? 0.1 : -0.1;
          state.planner.zoom = clampZoom(state.planner.zoom + delta);
          state.planner.panX = cursorX - canvasPoint.x * state.planner.zoom;
          state.planner.panY = cursorY - canvasPoint.y * state.planner.zoom;
          renderPlanner();
        },
        { passive: false }
      );

      els.plannerWorkspace.addEventListener("pointerdown", (event) => {
        const clickedNode = event.target.closest(".planner-node");
        const clickedOverlay = event.target.closest(
          ".planner-add-popup, .planner-target-popup, .planner-connection-label"
        );
        const clickedControl = event.target.closest("button, input, select, option, label");
        if (clickedNode || clickedOverlay || clickedControl) {
          return;
        }
        if (event.button === 0 || (event.button === 0 && spacePressed)) {
          isPanning = true;
          pointerId = event.pointerId;
          panStartX = event.clientX - state.planner.panX;
          panStartY = event.clientY - state.planner.panY;
          els.plannerWorkspace.setPointerCapture(event.pointerId);
          closePlannerPopup();
        }
      });

      els.plannerWorkspace.addEventListener("pointermove", (event) => {
        if (!isPanning || event.pointerId !== pointerId) {
          return;
        }
        state.planner.panX = event.clientX - panStartX;
        state.planner.panY = event.clientY - panStartY;
        renderPlanner();
      });

      const stopPanning = (event) => {
        if (event.pointerId === pointerId) {
          isPanning = false;
          pointerId = null;
        }
      };
      els.plannerWorkspace.addEventListener("pointerup", stopPanning);
      els.plannerWorkspace.addEventListener("pointercancel", stopPanning);

      els.plannerWorkspace.addEventListener("click", (event) => {
        if (isPanning || spacePressed) {
          return;
        }
        if (event.button !== 0) {
          return;
        }
        if (
          event.target.closest(".planner-node") ||
          event.target.closest(".planner-add-popup") ||
          event.target.closest(".planner-target-popup")
        ) {
          return;
        }
      });

      els.plannerWorkspace.addEventListener("contextmenu", (event) => {
        event.preventDefault();
        if (
          event.target.closest(".planner-node") ||
          event.target.closest(".planner-add-popup") ||
          event.target.closest(".planner-target-popup")
        ) {
          return;
        }
        closeTargetPopup();
        openPlannerPopup(event.clientX, event.clientY);
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
      await refreshWorkflows();
      renderOptions();
      await loadRecipe(state.currentRecipeId);
      await searchByOutput();
      bindPlannerWorkspaceInteractions();
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
    els.plannerPopupSearch.addEventListener("click", findPlannerPopupRecipes);
    els.plannerPopupRecipe.addEventListener("change", () => {
      state.planner.popup.selectedRecipeId = els.plannerPopupRecipe.value || null;
    });
    els.plannerPopupConfirm.addEventListener("click", () => {
      if (!state.planner.popup.outputItemId || !state.planner.popup.selectedRecipeId) {
        els.status.textContent = "Choose an output item and recipe before adding a node.";
        return;
      }
      addPlannerNodeAt(
        state.planner.popup.selectedRecipeId,
        state.planner.popup.outputItemId,
        state.planner.popup.canvasX,
        state.planner.popup.canvasY
      );
    });
    els.plannerPopupCancel.addEventListener("click", closePlannerPopup);
    els.plannerTargetPopupSave.addEventListener("click", () => {
      const value = Number(els.plannerTargetPopupRate.value);
      if (Number.isNaN(value) || value < 0) {
        els.status.textContent = "Target amount must be a non-negative number.";
        return;
      }
      if (!state.planner.targetPopup.nodeId || !state.planner.targetPopup.itemId) {
        return;
      }
      updatePlannerNode(state.planner.targetPopup.nodeId, {
        targetItemId: state.planner.targetPopup.itemId,
        targetRatePerMinute: value
      });
      closeTargetPopup();
    });
    els.plannerTargetPopupCancel.addEventListener("click", closeTargetPopup);
    els.plannerZoomOut.addEventListener("click", () => {
      state.planner.zoom = clampZoom(state.planner.zoom - 0.1);
      renderPlanner();
    });
    els.plannerZoomReset.addEventListener("click", () => {
      state.planner.zoom = 1;
      renderPlanner();
    });
    els.plannerZoomIn.addEventListener("click", () => {
      state.planner.zoom = clampZoom(state.planner.zoom + 0.1);
      renderPlanner();
    });
    els.plannerDefaultBelt.addEventListener("change", () => {
      state.planner.defaultBeltCapacity = els.plannerDefaultBelt.value
        ? Number(els.plannerDefaultBelt.value)
        : null;
      renderOptions();
      renderPlanner();
    });
    els.plannerWorkflowName.addEventListener("input", () => {
      state.planner.workflowName = els.plannerWorkflowName.value || "Untitled Workflow";
      renderPlannerSummary();
    });
    els.plannerSavedWorkflows.addEventListener("change", () => {
      state.planner.selectedWorkflowFilename = els.plannerSavedWorkflows.value;
      renderPlannerSummary();
    });
    els.newWorkflowButton.addEventListener("click", resetPlannerWorkflow);
    els.plannerRefreshWorkflows.addEventListener("click", async () => {
      try {
        await refreshWorkflows(state.planner.selectedWorkflowFilename);
        renderPlannerSummary();
        els.status.textContent = "Refreshed saved workflows.";
      } catch (error) {
        els.status.textContent = `Failed to refresh workflows: ${error.message}`;
      }
    });
    els.exportWorkflowButton.addEventListener("click", async () => {
      try {
        await exportWorkflow();
      } catch (error) {
        els.status.textContent = `Failed to export workflow: ${error.message}`;
      }
    });
    els.importWorkflowButton.addEventListener("click", async () => {
      try {
        await importSelectedWorkflow();
      } catch (error) {
        els.status.textContent = `Failed to import workflow: ${error.message}`;
      }
    });
    window.addEventListener("resize", renderPlannerEdges);

    bootstrap().catch((error) => {
      console.error(error);
      els.status.textContent = `Failed to load app data: ${error.message}`;
    });
"""
