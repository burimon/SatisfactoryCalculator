from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ..recipes import RECIPES, Item, find_recipes_by_output, get_recipe
from .flow_canvas import draw_recipe_flow
from .presenters import build_item_options, build_recipe_options, item_label, recipe_option
from .styles import LINE, PANEL_ALT, configure_styles


def run_recipe_ui() -> None:
    root = tk.Tk()
    root.title("Satisfactory Recipe Browser")
    root.geometry("1140x720")
    root.minsize(820, 620)
    configure_styles(root)

    default_recipe = get_recipe(sorted(RECIPES)[0])
    show_debug_ids = tk.BooleanVar(value=False)
    zoom_var = tk.DoubleVar(value=1.0)
    recipe_choice_var = tk.StringVar()
    output_choice_var = tk.StringVar()
    status_var = tk.StringVar(value="Browse recipes visually or search by output item.")

    app = ttk.Frame(root, style="App.TFrame", padding=18)
    app.pack(fill=tk.BOTH, expand=True)
    app.columnconfigure(0, weight=1)
    app.rowconfigure(1, weight=1)

    hero = ttk.Frame(app, style="Hero.TFrame", padding=22)
    hero.grid(row=0, column=0, sticky="ew")
    hero.columnconfigure(0, weight=1)
    ttk.Label(hero, text="Satisfactory Recipe Browser", style="Title.TLabel").grid(
        row=0, column=0, sticky="w"
    )
    ttk.Label(
        hero,
        text="Recipe names stay human-readable; enable debug mode only when you need internal ids.",
        style="HeroBody.TLabel",
    ).grid(row=1, column=0, sticky="w", pady=(8, 0))

    content = ttk.Frame(app, style="App.TFrame", padding=(0, 18, 0, 0))
    content.grid(row=1, column=0, sticky="nsew")
    content.columnconfigure(0, weight=5)
    content.columnconfigure(1, weight=3)
    content.rowconfigure(0, weight=1)
    content.rowconfigure(1, weight=1)

    flow_panel = ttk.Frame(content, style="Panel.TFrame", padding=18)
    flow_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    flow_panel.columnconfigure(0, weight=1)
    flow_panel.rowconfigure(3, weight=1)

    ttk.Label(flow_panel, text="Recipe Flow", style="Section.TLabel").grid(
        row=0, column=0, sticky="w"
    )
    ttk.Label(
        flow_panel,
        text=(
            "A visual recipe card that scales better once recipes have multiple inputs and outputs."
        ),
        style="Body.TLabel",
    ).grid(row=1, column=0, sticky="w", pady=(4, 14))

    controls = ttk.Frame(flow_panel, style="Panel.TFrame")
    controls.grid(row=2, column=0, sticky="ew", pady=(0, 14))
    controls.columnconfigure(1, weight=1)
    controls.columnconfigure(2, weight=0)
    controls.columnconfigure(3, weight=0)

    ttk.Label(controls, text="Recipe", style="Small.TLabel").grid(
        row=0, column=0, sticky="w", padx=(0, 10)
    )
    recipe_combo = ttk.Combobox(
        controls,
        textvariable=recipe_choice_var,
        state="readonly",
        style="App.TCombobox",
    )
    recipe_combo.grid(row=0, column=1, sticky="ew")
    debug_toggle = ttk.Checkbutton(
        controls,
        text="Debug ids",
        variable=show_debug_ids,
        style="Debug.TCheckbutton",
    )
    debug_toggle.grid(row=0, column=2, sticky="e", padx=(14, 0))
    zoom_controls = ttk.Frame(controls, style="Panel.TFrame")
    zoom_controls.grid(row=0, column=3, sticky="e", padx=(14, 0))
    zoom_out_button = ttk.Button(zoom_controls, text="-", style="App.TButton", width=3)
    zoom_out_button.grid(row=0, column=0)
    zoom_label = ttk.Label(zoom_controls, style="Small.TLabel", width=6, anchor="center")
    zoom_label.grid(row=0, column=1, padx=8)
    zoom_in_button = ttk.Button(zoom_controls, text="+", style="App.TButton", width=3)
    zoom_in_button.grid(row=0, column=2)

    flow_canvas = tk.Canvas(
        flow_panel,
        bg=PANEL_ALT,
        highlightthickness=1,
        highlightbackground=LINE,
        relief="flat",
    )
    flow_canvas.grid(row=3, column=0, sticky="nsew")

    side_panel = ttk.Frame(content, style="Panel.TFrame", padding=18)
    side_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
    side_panel.columnconfigure(0, weight=1)
    side_panel.rowconfigure(5, weight=1)

    ttk.Label(side_panel, text="Find Recipes By Output", style="Section.TLabel").grid(
        row=0, column=0, sticky="w"
    )
    ttk.Label(
        side_panel,
        text="Use official item labels in the UI, then load any result back into the flow view.",
        style="Body.TLabel",
    ).grid(row=1, column=0, sticky="w", pady=(4, 14))

    search_box = ttk.Frame(side_panel, style="Inset.TFrame", padding=14)
    search_box.grid(row=2, column=0, sticky="ew")
    search_box.columnconfigure(0, weight=1)

    ttk.Label(search_box, text="Output Item", style="Small.TLabel").grid(
        row=0, column=0, sticky="w"
    )
    output_combo = ttk.Combobox(
        search_box,
        textvariable=output_choice_var,
        state="readonly",
        style="App.TCombobox",
    )
    output_combo.grid(row=1, column=0, sticky="ew", pady=(6, 10))
    search_button = ttk.Button(search_box, text="Find Recipes", style="App.TButton")
    search_button.grid(row=2, column=0, sticky="ew")

    ttk.Label(side_panel, text="Matching Recipes", style="Section.TLabel").grid(
        row=3, column=0, sticky="w", pady=(16, 8)
    )
    results_table = ttk.Treeview(
        side_panel,
        style="Results.Treeview",
        columns=("recipe", "building", "seconds"),
        show="headings",
        selectmode="browse",
    )
    results_table.heading("recipe", text="Recipe")
    results_table.heading("building", text="Building")
    results_table.heading("seconds", text="Seconds")
    results_table.column("recipe", width=210, anchor="w")
    results_table.column("building", width=110, anchor="center")
    results_table.column("seconds", width=80, anchor="center")
    results_table.grid(row=5, column=0, sticky="nsew")

    status_bar = ttk.Frame(app, style="App.TFrame", padding=(0, 10, 0, 0))
    status_bar.grid(row=2, column=0, sticky="ew")
    status_bar.columnconfigure(0, weight=1)
    ttk.Separator(status_bar).grid(row=0, column=0, sticky="ew", pady=(0, 8))
    ttk.Label(status_bar, textvariable=status_var, style="Status.TLabel").grid(
        row=1, column=0, sticky="w"
    )

    recipe_option_to_id: dict[str, str] = {}
    item_option_to_item: dict[str, Item] = {}
    current_recipe_id = default_recipe.id

    def layout_content(width: int) -> None:
        if width < 980:
            flow_panel.grid_configure(row=0, column=0, padx=0, pady=(0, 10))
            side_panel.grid_configure(row=1, column=0, padx=0, pady=(10, 0))
            content.columnconfigure(0, weight=1)
            content.columnconfigure(1, weight=0)
        else:
            flow_panel.grid_configure(row=0, column=0, padx=(0, 10), pady=0)
            side_panel.grid_configure(row=0, column=1, padx=(10, 0), pady=0)
            content.columnconfigure(0, weight=5)
            content.columnconfigure(1, weight=3)

    def refresh_selectors() -> None:
        nonlocal recipe_option_to_id, item_option_to_item

        recipe_options, recipe_option_to_id = build_recipe_options(show_debug_ids.get())
        item_options, item_option_to_item = build_item_options(show_debug_ids.get())

        recipe_combo.configure(values=recipe_options)
        output_combo.configure(values=item_options)

        current_recipe = get_recipe(current_recipe_id)
        recipe_choice_var.set(recipe_option(current_recipe, show_debug_ids.get()))

        current_item = item_option_to_item.get(output_choice_var.get(), Item.IRON_INGOT)
        current_item_label = (
            f"{item_label(current_item)} [{current_item.value}]"
            if show_debug_ids.get()
            else item_label(current_item)
        )
        output_choice_var.set(current_item_label)

    def selected_recipe_id() -> str:
        return recipe_option_to_id[recipe_choice_var.get()]

    def selected_item() -> Item:
        return item_option_to_item[output_choice_var.get()]

    def show_recipe(*_: object) -> None:
        nonlocal current_recipe_id
        recipe_id = selected_recipe_id()
        current_recipe_id = recipe_id
        recipe = get_recipe(recipe_id)
        draw_recipe_flow(flow_canvas, recipe, show_debug_ids.get(), zoom_var.get())
        zoom_label.configure(text=f"{int(zoom_var.get() * 100)}%")
        status_var.set(f"Loaded recipe: {recipe.name}")

    def search_by_output(*_: object) -> None:
        item = selected_item()
        matches = find_recipes_by_output(item)
        results_table.delete(*results_table.get_children())
        for recipe in matches:
            results_table.insert(
                "",
                tk.END,
                iid=recipe.id,
                values=(
                    recipe.name,
                    (recipe.building or "unknown").title(),
                    f"{recipe.duration_seconds:g}",
                ),
            )
        status_var.set(f"Found {len(matches)} recipe(s) producing {item_label(item)}.")
        if matches:
            results_table.selection_set(matches[0].id)
            results_table.focus(matches[0].id)

    def load_selected_result(*_: object) -> None:
        selection = results_table.selection()
        if not selection:
            return
        recipe = get_recipe(selection[0])
        recipe_choice_var.set(recipe_option(recipe, show_debug_ids.get()))
        show_recipe()

    def on_toggle_debug() -> None:
        refresh_selectors()
        show_recipe()
        search_by_output()

    def set_zoom(value: float) -> None:
        zoom_var.set(max(0.7, min(1.7, round(value, 2))))
        show_recipe()

    def zoom_in() -> None:
        set_zoom(zoom_var.get() + 0.1)

    def zoom_out() -> None:
        set_zoom(zoom_var.get() - 0.1)

    def handle_zoom(event: tk.Event[tk.Misc]) -> None:
        delta = getattr(event, "delta", 0)
        if delta > 0:
            zoom_in()
        elif delta < 0:
            zoom_out()

    refresh_selectors()
    recipe_combo.bind("<<ComboboxSelected>>", show_recipe)
    output_combo.bind("<<ComboboxSelected>>", search_by_output)
    results_table.bind("<<TreeviewSelect>>", load_selected_result)
    results_table.bind("<Double-1>", load_selected_result)
    search_button.configure(command=search_by_output)
    debug_toggle.configure(command=on_toggle_debug)
    zoom_in_button.configure(command=zoom_in)
    zoom_out_button.configure(command=zoom_out)
    flow_canvas.bind("<Configure>", lambda _event: show_recipe())
    flow_canvas.bind("<MouseWheel>", handle_zoom)
    content.bind("<Configure>", lambda event: layout_content(event.width))

    layout_content(content.winfo_width())
    show_recipe()
    search_by_output()
    root.mainloop()
