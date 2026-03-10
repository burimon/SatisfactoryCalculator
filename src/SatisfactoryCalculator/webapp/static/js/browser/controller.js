import { fetchJson } from "../api/client.js";
import {
  itemById,
  itemLabelToId,
  itemOptionLabel,
  recipeById,
  recipeLabelToId,
  recipeOptionLabel,
} from "../common/catalog.js";
import { amountSubtitle, formatAmount, isPowerItem, rateLabel, titleCase } from "../common/format.js";

export function createBrowserController({ state, els, setStatus }) {
  function renderOptions() {
    els.recipeOptions.innerHTML = "";
    state.recipes.forEach((recipe) => {
      const option = document.createElement("option");
      option.value = recipeOptionLabel(state, recipe);
      els.recipeOptions.appendChild(option);
    });
    els.recipeInput.value = recipeById(state, state.currentRecipeId)
      ? recipeOptionLabel(state, recipeById(state, state.currentRecipeId))
      : "";

    els.outputOptions.innerHTML = "";
    state.items.forEach((item) => {
      const option = document.createElement("option");
      option.value = itemOptionLabel(state, item);
      els.outputOptions.appendChild(option);
    });
    els.outputInput.value = itemById(state, state.outputItemId)
      ? itemOptionLabel(state, itemById(state, state.outputItemId))
      : "";
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

  async function loadRecipe(recipeId) {
    const recipe = await fetchJson(`/api/recipes/${recipeId}`);
    state.currentRecipeId = recipe.id;
    renderOptions();
    renderRecipe(recipe);
    if (state.mode === "browser") {
      setStatus(`Loaded recipe: ${recipe.name}`);
    }
  }

  async function searchByOutput() {
    const itemId = itemLabelToId(state, els.outputInput.value) ?? state.outputItemId;
    if (!itemId) {
      setStatus("Choose a valid output item from the list.");
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
      button.addEventListener("click", () => {
        void loadRecipe(button.dataset.recipeId);
      });
    });

    const selectedItem = itemById(state, itemId);
    if (state.mode === "browser") {
      setStatus(
        `Found ${recipes.length} recipe(s) producing ${selectedItem ? selectedItem.name : itemId}.`
      );
    }
  }

  function bindEvents() {
    els.recipeInput.addEventListener("change", () => {
      const recipeId = recipeLabelToId(state, els.recipeInput.value);
      if (recipeId) {
        void loadRecipe(recipeId);
      } else {
        setStatus("Choose a valid recipe from the list.");
      }
    });

    els.rateSelect.addEventListener("change", () => {
      state.rateMode = els.rateSelect.value;
      if (state.currentRecipeId) {
        void loadRecipe(state.currentRecipeId);
      }
    });

    els.outputInput.addEventListener("change", () => {
      const itemId = itemLabelToId(state, els.outputInput.value);
      if (itemId) {
        state.outputItemId = itemId;
      }
    });

    els.searchButton.addEventListener("click", () => {
      void searchByOutput();
    });
  }

  return {
    bindEvents,
    loadRecipe,
    renderOptions,
    renderRecipe,
    searchByOutput,
  };
}
