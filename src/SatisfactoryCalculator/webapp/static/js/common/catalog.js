export function recipeById(state, recipeId) {
  return state.recipes.find((recipe) => recipe.id === recipeId) ?? null;
}

export function itemById(state, itemId) {
  return state.items.find((item) => item.id === itemId) ?? null;
}

export function findItemByName(state, name) {
  return state.items.find((item) => item.name === name) ?? null;
}

export function itemNameById(state, itemId) {
  return itemById(state, itemId)?.name ?? itemId;
}

export function recipeOptionLabel(state, recipe) {
  return state.debug ? `${recipe.name} [${recipe.id}]` : recipe.name;
}

export function itemOptionLabel(state, item) {
  return state.debug ? `${item.name} [${item.id}]` : item.name;
}

export function recipeLabelToId(state, label) {
  return state.recipes.find((recipe) => recipeOptionLabel(state, recipe) === label)?.id ?? null;
}

export function itemLabelToId(state, label) {
  return state.items.find((item) => itemOptionLabel(state, item) === label)?.id ?? null;
}
