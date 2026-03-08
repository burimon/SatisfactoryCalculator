HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Satisfactory Recipe Browser</title>
  <style>
    :root {
      --bg: #eef3f7;
      --panel: #fbfdff;
      --panel-alt: #e5edf5;
      --accent: #2d6da3;
      --accent-dark: #1f4d74;
      --text: #18222c;
      --muted: #5d6b79;
      --line: #c3d0db;
      --input: #e8f4ee;
      --output: #edf2fb;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", sans-serif;
      background: radial-gradient(circle at top left, #f7fbff 0%, var(--bg) 48%, #e8eef4 100%);
      color: var(--text);
    }
    .page {
      max-width: 1320px;
      margin: 0 auto;
      padding: 18px;
    }
    .hero {
      background: linear-gradient(135deg, var(--accent-dark), var(--accent));
      color: white;
      padding: 22px 24px;
      border-radius: 18px;
      box-shadow: 0 16px 32px rgba(31, 77, 116, 0.16);
    }
    .hero h1 {
      margin: 0 0 8px;
      font-family: Georgia, serif;
      font-size: 2rem;
    }
    .hero p {
      margin: 0;
      color: #e7f2fb;
      max-width: 900px;
      line-height: 1.5;
    }
    .content {
      display: grid;
      grid-template-columns: minmax(0, 1.55fr) minmax(320px, 0.95fr);
      gap: 20px;
      margin-top: 18px;
    }
    .panel {
      background: rgba(251, 253, 255, 0.92);
      border: 1px solid rgba(195, 208, 219, 0.95);
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 10px 24px rgba(24, 34, 44, 0.06);
      backdrop-filter: blur(10px);
    }
    .panel h2 {
      margin: 0;
      font-family: Georgia, serif;
      font-size: 1.35rem;
    }
    .panel .subtext {
      margin: 6px 0 16px;
      color: var(--muted);
      line-height: 1.45;
    }
    .controls {
      display: grid;
      grid-template-columns: minmax(0, 1.2fr) 160px auto;
      gap: 12px;
      align-items: end;
      margin-bottom: 14px;
    }
    .field label,
    .toggle {
      display: block;
      font-size: 0.82rem;
      color: var(--muted);
      margin-bottom: 6px;
    }
    select,
    input[list],
    button {
      width: 100%;
      min-height: 42px;
      border-radius: 12px;
      border: 1px solid var(--line);
      padding: 0 12px;
      font: inherit;
    }
    select,
    input[list] {
      background: white;
      color: var(--text);
    }
    button {
      background: linear-gradient(135deg, var(--accent), #4f8bc0);
      color: white;
      border: none;
      cursor: pointer;
      font-weight: 600;
      box-shadow: 0 10px 20px rgba(45, 109, 163, 0.18);
    }
    button:hover { filter: brightness(1.04); }
    input[type="checkbox"] { transform: translateY(1px); }
    .summary {
      display: grid;
      grid-template-columns: minmax(0, 1.15fr) repeat(3, minmax(120px, 1fr));
      gap: 12px;
      background: var(--panel-alt);
      border-radius: 14px;
      padding: 14px;
      margin-bottom: 14px;
    }
    .summary .name {
      font-family: Georgia, serif;
      font-size: 1.2rem;
      font-weight: 700;
    }
    .summary .debug-id {
      margin-top: 4px;
      font-family: Consolas, monospace;
      font-size: 0.8rem;
      color: var(--muted);
      display: none;
    }
    .summary .metric-label {
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--muted);
    }
    .summary .metric-value {
      margin-top: 4px;
      font-weight: 600;
    }
    .io-sections {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
    }
    .io-card {
      border-radius: 14px;
      padding: 14px;
      border: 1px solid var(--line);
    }
    .io-card.inputs { background: var(--input); }
    .io-card.outputs { background: var(--output); }
    .io-card h3 {
      margin: 0 0 10px;
      font-family: Georgia, serif;
      font-size: 1rem;
    }
    .row-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .row-item {
      background: rgba(255, 255, 255, 0.72);
      border: 1px solid rgba(195, 208, 219, 0.9);
      border-radius: 12px;
      padding: 10px 12px;
    }
    .row-top {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      align-items: baseline;
    }
    .row-name {
      font-weight: 600;
    }
    .row-amount {
      color: var(--muted);
      white-space: nowrap;
    }
    .row-id {
      margin-top: 4px;
      color: var(--muted);
      font-size: 0.78rem;
      font-family: Consolas, monospace;
      display: none;
    }
    .search-box {
      background: var(--panel-alt);
      border-radius: 14px;
      padding: 14px;
      margin-bottom: 16px;
    }
    .results-list {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .result-card {
      padding: 12px 14px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: white;
      cursor: pointer;
      transition: transform 120ms ease, box-shadow 120ms ease, border-color 120ms ease;
    }
    .result-card:hover {
      transform: translateY(-1px);
      border-color: #8db0ce;
      box-shadow: 0 10px 18px rgba(24, 34, 44, 0.08);
    }
    .result-card.active {
      border-color: var(--accent);
      box-shadow: 0 0 0 2px rgba(45, 109, 163, 0.12);
    }
    .result-card .title {
      font-weight: 700;
    }
    .result-card .meta {
      margin-top: 4px;
      color: var(--muted);
      font-size: 0.9rem;
    }
    .status {
      margin-top: 14px;
      color: var(--muted);
      font-size: 0.92rem;
    }
    .empty {
      color: var(--muted);
      padding: 10px 0;
    }
    @media (max-width: 980px) {
      .content { grid-template-columns: 1fr; }
    }
    @media (max-width: 760px) {
      .controls,
      .summary,
      .io-sections { grid-template-columns: 1fr; }
      .page { padding: 12px; }
    }
  </style>
</head>
<body>
  <div class="page">
    <section class="hero">
      <h1>Satisfactory Recipe Browser</h1>
      <p>
        Browse recipe details, switch between per-cycle and throughput views,
        and find recipes by output item in a real browser UI.
      </p>
    </section>
    <section class="content">
      <section class="panel">
        <h2>Recipe Details</h2>
        <p class="subtext">
          Inspect the selected recipe as structured data with readable inputs and outputs.
        </p>
        <div class="controls">
          <div class="field">
            <label for="recipe-input">Recipe</label>
            <input id="recipe-input" list="recipe-options" type="search" autocomplete="off">
            <datalist id="recipe-options"></datalist>
          </div>
          <div class="field">
            <label for="rate-select">Rate View</label>
            <select id="rate-select">
              <option value="per_cycle">Per Cycle</option>
              <option value="per_second">Per Second</option>
              <option value="per_minute">Per Minute</option>
            </select>
          </div>
          <label class="toggle"><input id="debug-toggle" type="checkbox"> Debug ids</label>
        </div>
        <div class="summary">
          <div>
            <div id="recipe-name" class="name"></div>
            <div id="recipe-id" class="debug-id"></div>
          </div>
          <div>
            <div class="metric-label">Building</div>
            <div id="recipe-building" class="metric-value"></div>
          </div>
          <div>
            <div class="metric-label">Cycle Time</div>
            <div id="recipe-cycle" class="metric-value"></div>
          </div>
          <div>
            <div class="metric-label">Rate View</div>
            <div id="recipe-rate" class="metric-value"></div>
          </div>
        </div>
        <div class="io-sections">
          <section class="io-card inputs">
            <h3>Inputs</h3>
            <div id="inputs-list" class="row-list"></div>
          </section>
          <section class="io-card outputs">
            <h3>Outputs</h3>
            <div id="outputs-list" class="row-list"></div>
          </section>
        </div>
      </section>
      <section class="panel">
        <h2>Find Recipes By Output</h2>
        <p class="subtext">
          Use official item labels in the UI, then load any result back into the detail view.
        </p>
        <div class="search-box">
          <div class="field">
            <label for="output-input">Output Item</label>
            <input id="output-input" list="output-options" type="search" autocomplete="off">
            <datalist id="output-options"></datalist>
          </div>
          <div style="margin-top: 10px;">
            <button id="search-button" type="button">Find Recipes</button>
          </div>
        </div>
        <div id="results-list" class="results-list"></div>
      </section>
    </section>
    <div id="status" class="status">Loading recipes...</div>
  </div>
  <script>
    const state = {
      recipes: [],
      items: [],
      currentRecipeId: null,
      rateMode: "per_cycle",
      debug: false,
      outputItemId: null
    };

    const els = {
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
      if (Number.isInteger(amount)) return String(amount);
      return Number(amount).toFixed(2).replace(/\\.00$/, "").replace(/0$/, "");
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

    function renderOptions() {
      els.recipeOptions.innerHTML = "";
      state.recipes.forEach((recipe) => {
        const option = document.createElement("option");
        option.value = recipeOptionLabel(recipe);
        els.recipeOptions.appendChild(option);
      });
      const selectedRecipe = state.recipes.find((recipe) => recipe.id === state.currentRecipeId);
      els.recipeInput.value = selectedRecipe ? recipeOptionLabel(selectedRecipe) : "";

      els.outputOptions.innerHTML = "";
      state.items.forEach((item) => {
        const option = document.createElement("option");
        option.value = itemOptionLabel(item);
        els.outputOptions.appendChild(option);
      });
      const selectedItem = state.items.find((item) => item.id === state.outputItemId);
      els.outputInput.value = selectedItem ? itemOptionLabel(selectedItem) : "";
    }

    function createRow(entry, verb, duration) {
      const itemName = state.debug ? `${entry.item.name} [${entry.item.id}]` : entry.item.name;
      return `
        <div class="row-item">
          <div class="row-top">
            <div class="row-name">${itemName}</div>
            <div class="row-amount">${
              amountSubtitle(verb, entry.amount, duration, state.rateMode)
            }</div>
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

    function titleCase(value) {
      return value.replace(/_/g, " ").replace(/\\b\\w/g, (ch) => ch.toUpperCase());
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
      els.status.textContent = `Loaded recipe: ${recipe.name}`;
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
                ${titleCase(recipe.building || "unknown")} • ${recipe.duration_seconds}s cycle
              </div>
            </button>
          `).join("")
        : '<div class="empty">No recipes found.</div>';

      els.resultsList.querySelectorAll("[data-recipe-id]").forEach((button) => {
        button.addEventListener("click", () => loadRecipe(button.dataset.recipeId));
      });
      const selectedItem = state.items.find((item) => item.id === itemId);
      els.status.textContent =
        `Found ${recipes.length} recipe(s) producing ` +
        `${selectedItem ? selectedItem.name : itemId}.`;
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
      renderOptions();
      await loadRecipe(state.currentRecipeId);
      await searchByOutput();
    }

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

    bootstrap().catch((error) => {
      console.error(error);
      els.status.textContent = `Failed to load app data: ${error.message}`;
    });
  </script>
</body>
</html>
"""
