from __future__ import annotations

from ..recipes import RECIPES, Item, Recipe


def display_name(raw_id: str) -> str:
    return " ".join(part.capitalize() for part in raw_id.split("_"))


def item_label(item: Item) -> str:
    return display_name(item.value)


def recipe_option(recipe: Recipe, debug: bool) -> str:
    return f"{recipe.name} [{recipe.id}]" if debug else recipe.name


def build_recipe_options(show_debug_ids: bool) -> tuple[list[str], dict[str, str]]:
    options = [recipe_option(recipe, show_debug_ids) for recipe in RECIPES.values()]
    option_to_id = {recipe_option(recipe, show_debug_ids): recipe.id for recipe in RECIPES.values()}
    return sorted(options), option_to_id


def build_item_options(show_debug_ids: bool) -> tuple[list[str], dict[str, Item]]:
    options: list[str] = []
    option_to_item: dict[str, Item] = {}
    for item in Item:
        label = item_label(item)
        option = f"{label} [{item.value}]" if show_debug_ids else label
        options.append(option)
        option_to_item[option] = item
    return sorted(options), option_to_item
