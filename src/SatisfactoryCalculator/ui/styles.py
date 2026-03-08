from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

SURFACE = "#eef3f7"
PANEL = "#fbfdff"
PANEL_ALT = "#e5edf5"
ACCENT = "#2d6da3"
ACCENT_DARK = "#1f4d74"
TEXT = "#18222c"
MUTED = "#5d6b79"
LINE = "#c3d0db"
INPUT_FILL = "#e8f4ee"
OUTPUT_FILL = "#edf2fb"
NODE_FILL = "#f9fcff"
INPUT_OUTLINE = "#8ab08f"
OUTPUT_OUTLINE = "#c78b5b"
INPUT_LINE = "#7a8d7d"
OUTPUT_LINE = "#b87342"


def configure_styles(root: tk.Tk) -> None:
    root.configure(bg=SURFACE)

    title_font = tkfont.Font(family="Georgia", size=24, weight="bold")
    section_font = tkfont.Font(family="Georgia", size=13, weight="bold")
    body_font = tkfont.Font(family="Segoe UI", size=10)
    small_font = tkfont.Font(family="Segoe UI", size=9)
    debug_font = tkfont.Font(family="Consolas", size=9)

    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")

    style.configure(".", background=SURFACE, foreground=TEXT, font=body_font)
    style.configure("App.TFrame", background=SURFACE)
    style.configure("Hero.TFrame", background=ACCENT_DARK)
    style.configure("Panel.TFrame", background=PANEL)
    style.configure("Inset.TFrame", background=PANEL_ALT)
    style.configure("Title.TLabel", background=ACCENT_DARK, foreground="white", font=title_font)
    style.configure("HeroBody.TLabel", background=ACCENT_DARK, foreground="#fbeee3", font=body_font)
    style.configure("Section.TLabel", background=PANEL, foreground=TEXT, font=section_font)
    style.configure("Body.TLabel", background=PANEL, foreground=MUTED, font=body_font)
    style.configure("Small.TLabel", background=PANEL, foreground=MUTED, font=small_font)
    style.configure("Status.TLabel", background=SURFACE, foreground=MUTED, font=body_font)
    style.configure("Debug.TCheckbutton", background=PANEL, foreground=MUTED, font=small_font)
    style.map(
        "Debug.TCheckbutton",
        background=[("active", PANEL)],
        foreground=[("active", TEXT)],
    )
    style.configure(
        "App.TCombobox",
        fieldbackground="white",
        selectbackground="#f7dcc8",
        selectforeground=TEXT,
        arrowsize=16,
        padding=7,
    )
    style.configure(
        "App.TButton",
        background=ACCENT,
        foreground="white",
        borderwidth=0,
        focusthickness=0,
        focuscolor=ACCENT,
        padding=(12, 9),
    )
    style.map("App.TButton", background=[("active", "#255a87")])
    style.configure(
        "Results.Treeview",
        background="#fffdf9",
        fieldbackground="#fffdf9",
        foreground=TEXT,
        rowheight=30,
        bordercolor=LINE,
    )
    style.configure(
        "Compact.Treeview",
        background="#fffdf9",
        fieldbackground="#fffdf9",
        foreground=TEXT,
        rowheight=24,
        bordercolor=LINE,
    )
    style.configure(
        "Results.Treeview.Heading",
        background=PANEL_ALT,
        foreground=TEXT,
        font=section_font,
        relief="flat",
    )
    style.configure(
        "Compact.Treeview.Heading",
        background=PANEL_ALT,
        foreground=TEXT,
        font=small_font,
        relief="flat",
    )
    style.map(
        "Results.Treeview",
        background=[("selected", "#dbe8f4")],
        foreground=[("selected", TEXT)],
    )
    style.map(
        "Compact.Treeview",
        background=[("selected", "#dbe8f4")],
        foreground=[("selected", TEXT)],
    )

    root.option_add("*TCombobox*Listbox.background", "white")
    root.option_add("*TCombobox*Listbox.foreground", TEXT)
    root.option_add("*TCombobox*Listbox.selectBackground", "#dbe8f4")
    root.option_add("*TCombobox*Listbox.selectForeground", TEXT)
    root.option_add("*DebugId.Font", debug_font)
