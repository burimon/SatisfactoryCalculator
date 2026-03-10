import { fetchJson } from "./api/client.js";
import { createBrowserController } from "./browser/controller.js";
import { itemById, itemLabelToId } from "./common/catalog.js";
import { els } from "./dom.js";
import { createPlannerController } from "./planner/controller.js";
import { createPlannerState } from "./planner/state.js";

const state = {
  mode: "browser",
  recipes: [],
  items: [],
  currentRecipeId: null,
  rateMode: "per_cycle",
  debug: false,
  outputItemId: null,
  planner: createPlannerState(),
};

function setStatus(message) {
  els.status.textContent = message;
}

function setMode(mode) {
  state.mode = mode;
  els.browserView.classList.toggle("active", mode === "browser");
  els.plannerView.classList.toggle("active", mode === "planner");
  els.modeButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.mode === mode);
  });
  setStatus(
    mode === "browser"
      ? `Loaded recipe: ${state.recipes.find((recipe) => recipe.id === state.currentRecipeId)?.name ?? "none"}`
      : "Planner mode active."
  );
}

const browser = createBrowserController({ state, els, setStatus });
const planner = createPlannerController({ els, setMode, setStatus, state });

async function bootstrap() {
  const [recipes, items] = await Promise.all([fetchJson("/api/recipes"), fetchJson("/api/items")]);
  state.recipes = recipes;
  state.items = items;
  state.currentRecipeId = recipes[0]?.id ?? null;
  state.outputItemId = items.find((item) => item.id === "iron_ingot")?.id ?? items[0]?.id ?? null;
  state.planner.selectedOutputItemId = state.outputItemId;
  await planner.refreshWorkflows();
  browser.renderOptions();
  planner.renderOptions();
  if (state.currentRecipeId) {
    await browser.loadRecipe(state.currentRecipeId);
  }
  await browser.searchByOutput();
  planner.render();
}

els.modeButtons.forEach((button) => {
  button.addEventListener("click", () => setMode(button.dataset.mode));
});

els.debugToggle.addEventListener("change", async () => {
  state.debug = els.debugToggle.checked;
  browser.renderOptions();
  planner.renderOptions();
  if (state.currentRecipeId) {
    await browser.loadRecipe(state.currentRecipeId);
  }
  await browser.searchByOutput();
  planner.render();
});

els.outputInput.addEventListener("change", () => {
  const itemId = itemLabelToId(state, els.outputInput.value);
  if (itemId) {
    state.outputItemId = itemId;
    state.planner.selectedOutputItemId = itemId;
    planner.renderOptions();
  }
});

bootstrap().catch((error) => {
  console.error(error);
  setStatus(`Failed to load app data: ${error.message}`);
});
