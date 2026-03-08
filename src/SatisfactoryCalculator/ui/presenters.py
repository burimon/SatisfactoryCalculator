from __future__ import annotations

from typing import Literal

from ..recipes import RECIPES, Item, Recipe

RateMode = Literal["per_cycle", "per_second", "per_minute"]


def display_name(raw_id: str) -> str:
    return " ".join(part.capitalize() for part in raw_id.split("_"))


def item_label(item: Item) -> str:
    return display_name(item.value)


def recipe_option(recipe: Recipe, debug: bool) -> str:
    return f"{recipe.name} [{recipe.id}]" if debug else recipe.name


def rate_mode_label(rate_mode: RateMode) -> str:
    return {
        "per_cycle": "Per Cycle",
        "per_second": "Per Second",
        "per_minute": "Per Minute",
    }[rate_mode]


def build_rate_options() -> tuple[list[str], dict[str, RateMode]]:
    option_to_mode: dict[str, RateMode] = {
        rate_mode_label("per_cycle"): "per_cycle",
        rate_mode_label("per_second"): "per_second",
        rate_mode_label("per_minute"): "per_minute",
    }
    return list(option_to_mode), option_to_mode


def scale_amount(amount: float, duration_seconds: float, rate_mode: RateMode) -> float:
    if rate_mode == "per_cycle":
        return amount
    if rate_mode == "per_second":
        return amount / duration_seconds
    return (amount * 60) / duration_seconds


def format_amount(amount: float | int) -> str:
    if isinstance(amount, int):
        return str(amount)
    if amount.is_integer():
        return str(int(amount))
    return f"{amount:.2f}".rstrip("0").rstrip(".")


def amount_subtitle(verb: str, amount: float, duration_seconds: float, rate_mode: RateMode) -> str:
    scaled = format_amount(scale_amount(amount, duration_seconds, rate_mode))
    unit = {
        "per_cycle": "per cycle",
        "per_second": "/s",
        "per_minute": "/min",
    }[rate_mode]
    return f"{verb} {scaled} {unit}"


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
