from __future__ import annotations

from typing import Any

from ..recipes import RECIPES, Item, Recipe, find_recipes_by_output, get_recipe
from .workflow_store import list_workflows_payload, load_workflow_payload, save_workflow_payload


def display_name(raw_id: str) -> str:
    return " ".join(part.capitalize() for part in raw_id.split("_"))


def item_payload(item: Item) -> dict[str, str]:
    return {"id": item.value, "name": display_name(item.value)}


def recipe_payload(recipe: Recipe) -> dict[str, object]:
    return {
        "id": recipe.id,
        "name": recipe.name,
        "building": recipe.building,
        "duration_seconds": recipe.duration_seconds,
        "inputs": [
            {"item": item_payload(item), "amount": amount} for item, amount in recipe.inputs.items()
        ],
        "outputs": [
            {"item": item_payload(item), "amount": amount}
            for item, amount in recipe.outputs.items()
        ],
    }


def list_recipes() -> list[dict[str, object]]:
    return sorted(
        [recipe_payload(RECIPES[recipe_id]) for recipe_id in RECIPES],
        key=lambda recipe: str(recipe["name"]),
    )


def list_items() -> list[dict[str, str]]:
    return sorted([item_payload(item) for item in Item], key=lambda item: item["name"])


def get_recipe_payload(recipe_id: str) -> dict[str, object]:
    return recipe_payload(get_recipe(recipe_id))


def find_recipe_payloads_by_output(item_id: str) -> list[dict[str, object]]:
    item = Item(item_id)
    return [recipe_payload(recipe) for recipe in find_recipes_by_output(item)]


def list_workflows() -> dict[str, object]:
    return list_workflows_payload()


def get_workflow_payload(filename: str) -> dict[str, Any]:
    return load_workflow_payload(filename)


def save_workflow(payload: dict[str, object]) -> dict[str, object]:
    return save_workflow_payload(payload)
