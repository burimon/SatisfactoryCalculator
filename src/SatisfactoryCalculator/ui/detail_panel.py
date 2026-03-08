from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ..recipes import Recipe
from .presenters import RateMode, amount_subtitle, item_label


def update_detail_panel(
    summary_name_var: tk.StringVar,
    summary_building_var: tk.StringVar,
    summary_cycle_var: tk.StringVar,
    summary_rate_var: tk.StringVar,
    summary_id_var: tk.StringVar,
    inputs_table: ttk.Treeview,
    outputs_table: ttk.Treeview,
    recipe: Recipe,
    show_debug_ids: bool,
    rate_mode: RateMode,
) -> None:
    summary_name_var.set(recipe.name)
    summary_building_var.set((recipe.building or "unknown").title())
    summary_cycle_var.set(f"{recipe.duration_seconds:g} seconds")
    summary_rate_var.set(
        {"per_cycle": "Per Cycle", "per_second": "Per Second", "per_minute": "Per Minute"}[
            rate_mode
        ]
    )
    summary_id_var.set(recipe.id if show_debug_ids else "")

    inputs_table.delete(*inputs_table.get_children())
    outputs_table.delete(*outputs_table.get_children())

    for item, amount in recipe.inputs.items():
        item_name = item_label(item)
        if show_debug_ids:
            item_name = f"{item_name} [{item.value}]"
        inputs_table.insert(
            "",
            tk.END,
            values=(
                item_name,
                amount_subtitle("Consumes", amount, recipe.duration_seconds, rate_mode),
            ),
        )

    for item, amount in recipe.outputs.items():
        item_name = item_label(item)
        if show_debug_ids:
            item_name = f"{item_name} [{item.value}]"
        outputs_table.insert(
            "",
            tk.END,
            values=(
                item_name,
                amount_subtitle("Produces", amount, recipe.duration_seconds, rate_mode),
            ),
        )
