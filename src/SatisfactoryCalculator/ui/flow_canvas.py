from __future__ import annotations

import tkinter as tk

from ..recipes import Recipe
from .presenters import item_label
from .styles import (
    ACCENT,
    INPUT_FILL,
    INPUT_LINE,
    INPUT_OUTLINE,
    MUTED,
    NODE_FILL,
    OUTPUT_FILL,
    OUTPUT_LINE,
    OUTPUT_OUTLINE,
    PANEL_ALT,
    TEXT,
)


def _draw_box(
    canvas: tk.Canvas,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    fill: str,
    outline: str,
    title: str,
    subtitle: str,
    zoom: float,
    debug_text: str | None = None,
) -> None:
    title_size = max(8, int(11 * zoom))
    subtitle_size = max(7, int(10 * zoom))
    inner_pad_x = max(8, int(12 * zoom))
    inner_pad_y = max(7, int(10 * zoom))
    show_subtitle = zoom >= 0.8
    show_debug_text = debug_text is not None and zoom >= 0.95

    canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=2)
    canvas.create_text(
        x1 + inner_pad_x,
        y1 + inner_pad_y,
        text=title,
        anchor="nw",
        fill=TEXT,
        font=("Georgia", title_size, "bold"),
    )
    if show_subtitle:
        canvas.create_text(
            x1 + inner_pad_x,
            y1 + inner_pad_y + title_size + max(5, int(8 * zoom)),
            text=subtitle,
            anchor="nw",
            fill=MUTED,
            font=("Segoe UI", subtitle_size),
        )
    if show_debug_text:
        assert debug_text is not None
        canvas.create_text(
            x1 + inner_pad_x,
            y2 - max(7, int(10 * zoom)),
            text=debug_text,
            anchor="sw",
            fill=MUTED,
            font=("Consolas", max(7, int(8 * zoom))),
        )


def draw_recipe_flow(canvas: tk.Canvas, recipe: Recipe, show_debug_ids: bool, zoom: float) -> None:
    canvas.delete("all")
    canvas.update_idletasks()

    width = max(canvas.winfo_width(), 420)
    height = max(canvas.winfo_height(), 260)
    compact = width < 620
    canvas.configure(bg=PANEL_ALT)

    center_x = width / 2
    node_width = (160 if compact else 190) * zoom
    node_height = (78 if compact else 92) * zoom
    node_left = center_x - (node_width / 2)
    node_right = center_x + (node_width / 2)
    node_top = (height / 2) - (node_height / 2)
    node_bottom = node_top + node_height

    _draw_box(
        canvas,
        node_left,
        node_top,
        node_right,
        node_bottom,
        fill=NODE_FILL,
        outline=ACCENT,
        title=recipe.name,
        subtitle=f"{(recipe.building or 'Unknown').title()}  |  {recipe.duration_seconds:g}s",
        zoom=zoom,
        debug_text=recipe.id if show_debug_ids else None,
    )

    inputs = list(recipe.inputs.items())
    outputs = list(recipe.outputs.items())
    side_margin = (14 if compact else 18) * zoom
    side_width = (150 if compact else 190) * zoom
    box_height = (44 if compact else 52) * zoom
    vertical_gap = (10 if compact else 14) * zoom
    input_total = len(inputs) * (box_height + vertical_gap) - vertical_gap
    output_total = len(outputs) * (box_height + vertical_gap) - vertical_gap
    input_start = max(28 * zoom, (height / 2) - (input_total / 2))
    output_start = max(28 * zoom, (height / 2) - (output_total / 2))

    for index, (item, amount) in enumerate(inputs):
        top = input_start + index * (box_height + vertical_gap)
        left = float(side_margin)
        right = float(min(left + side_width, node_left - (20 * zoom)))
        bottom = top + box_height
        _draw_box(
            canvas,
            left,
            top,
            right,
            bottom,
            fill=INPUT_FILL,
            outline=INPUT_OUTLINE,
            title=item_label(item),
            subtitle=f"Consumes {amount:g}",
            zoom=zoom,
            debug_text=item.value if show_debug_ids else None,
        )
        canvas.create_line(
            right,
            top + box_height / 2,
            node_left,
            top + box_height / 2,
            fill=INPUT_LINE,
            width=2,
        )
        canvas.create_polygon(
            node_left,
            top + box_height / 2,
            node_left - (9 * zoom),
            top + box_height / 2 - (5 * zoom),
            node_left - (9 * zoom),
            top + box_height / 2 + (5 * zoom),
            fill=INPUT_LINE,
            outline=INPUT_LINE,
        )

    for index, (item, amount) in enumerate(outputs):
        top = output_start + index * (box_height + vertical_gap)
        right = float(width - side_margin)
        left = float(max(right - side_width, node_right + (20 * zoom)))
        bottom = top + box_height
        _draw_box(
            canvas,
            left,
            top,
            right,
            bottom,
            fill=OUTPUT_FILL,
            outline=OUTPUT_OUTLINE,
            title=item_label(item),
            subtitle=f"Produces {amount:g}",
            zoom=zoom,
            debug_text=item.value if show_debug_ids else None,
        )
        canvas.create_line(
            node_right,
            top + box_height / 2,
            left,
            top + box_height / 2,
            fill=OUTPUT_LINE,
            width=2,
        )
        canvas.create_polygon(
            left,
            top + box_height / 2,
            left - (9 * zoom),
            top + box_height / 2 - (5 * zoom),
            left - (9 * zoom),
            top + box_height / 2 + (5 * zoom),
            fill=OUTPUT_LINE,
            outline=OUTPUT_LINE,
        )

    canvas.create_text(
        18 * zoom,
        18 * zoom,
        text="Inputs",
        anchor="nw",
        fill=MUTED,
        font=("Georgia", max(9, int(11 * zoom)), "bold"),
    )
    canvas.create_text(
        width - (18 * zoom),
        18 * zoom,
        text="Outputs",
        anchor="ne",
        fill=MUTED,
        font=("Georgia", max(9, int(11 * zoom)), "bold"),
    )
