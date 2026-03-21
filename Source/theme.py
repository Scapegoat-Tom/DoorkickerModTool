# ── theme.py ──────────────────────────────────────────────────────────────────
# Dark / light theme palettes and application helpers.

import tkinter as tk
from tkinter import ttk

THEME_DARK = {
    "bg":          "#2b2b2b",
    "fg":          "#f0f0f0",
    "entry_bg":    "#3c3f41",
    "entry_fg":    "#f0f0f0",
    "select_bg":   "#2d6099",
    "select_fg":   "#ffffff",
    "disabled_bg": "#3c3c3c",
    "disabled_fg": "#888888",
    "border":      "#555555",
    "button_bg":   "#4c5052",
    "button_fg":   "#f0f0f0",
    "sep":         "#555555",
    "preview_bg":  "#313335",
}
THEME_LIGHT = {
    "bg":          "#f0f0f0",
    "fg":          "#000000",
    "entry_bg":    "#ffffff",
    "entry_fg":    "#000000",
    "select_bg":   "#0078d7",
    "select_fg":   "#ffffff",
    "disabled_bg": "#e0e0e0",
    "disabled_fg": "#6d6d6d",
    "border":      "#adadad",
    "button_bg":   "#e1e1e1",
    "button_fg":   "#000000",
    "sep":         "#adadad",
    "preview_bg":  "#f0f0f0",
}


def apply_theme(root: tk.Tk, dark: bool) -> None:
    """
    Apply dark or light theme to *root* and all existing child widgets.
    Forces the 'clam' ttk theme so colours are respected on all platforms.
    """
    t     = THEME_DARK if dark else THEME_LIGHT
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".",
        background=t["bg"],        foreground=t["fg"],
        fieldbackground=t["entry_bg"], troughcolor=t["disabled_bg"],
        bordercolor=t["border"],   darkcolor=t["bg"],  lightcolor=t["bg"],
        selectbackground=t["select_bg"], selectforeground=t["select_fg"],
        insertcolor=t["fg"],       relief="flat",
    )
    style.configure("TFrame",             background=t["bg"])
    style.configure("TLabelframe",        background=t["bg"], bordercolor=t["border"], relief="groove")
    style.configure("TLabelframe.Label",  background=t["bg"], foreground=t["fg"])
    style.configure("TLabel",             background=t["bg"], foreground=t["fg"])
    style.configure("TSeparator",         background=t["border"])

    style.configure("TEntry",
        fieldbackground=t["entry_bg"], foreground=t["entry_fg"],
        insertcolor=t["fg"],           bordercolor=t["border"], relief="flat",
    )
    style.map("TEntry",
        fieldbackground=[("disabled", t["disabled_bg"]), ("readonly", t["disabled_bg"])],
        foreground=[("disabled", t["disabled_fg"]),      ("readonly", t["fg"])],
    )

    style.configure("TSpinbox",
        fieldbackground=t["entry_bg"], foreground=t["entry_fg"],
        background=t["button_bg"],     arrowcolor=t["fg"],
        bordercolor=t["border"],       relief="flat",
    )
    style.map("TSpinbox",
        fieldbackground=[("disabled", t["disabled_bg"])],
        foreground=[("disabled",      t["disabled_fg"])],
        background=[("active",        t["button_bg"])],
    )

    style.configure("TCombobox",
        fieldbackground=t["entry_bg"],   foreground=t["entry_fg"],
        background=t["button_bg"],       arrowcolor=t["fg"],
        selectbackground=t["entry_bg"],  selectforeground=t["entry_fg"],
        bordercolor=t["border"],         relief="flat",
    )
    style.map("TCombobox",
        fieldbackground=[("readonly", t["entry_bg"]),    ("disabled", t["disabled_bg"])],
        foreground=[("readonly",      t["entry_fg"]),    ("disabled", t["disabled_fg"])],
        background=[("active",        t["button_bg"]),   ("readonly", t["button_bg"])],
        arrowcolor=[("disabled",      t["disabled_fg"])],
    )
    root.option_add("*TCombobox*Listbox.Background",       t["entry_bg"],  "interactive")
    root.option_add("*TCombobox*Listbox.Foreground",       t["entry_fg"],  "interactive")
    root.option_add("*TCombobox*Listbox.selectBackground", t["select_bg"], "interactive")
    root.option_add("*TCombobox*Listbox.selectForeground", t["select_fg"], "interactive")

    style.configure("TButton",
        background=t["button_bg"], foreground=t["button_fg"],
        bordercolor=t["border"],   relief="raised", padding=4,
    )
    style.map("TButton",
        background=[("active", t["select_bg"]), ("pressed", t["select_bg"]), ("disabled", t["disabled_bg"])],
        foreground=[("active", t["select_fg"]), ("pressed", t["select_fg"]), ("disabled", t["disabled_fg"])],
        relief=[("pressed", "sunken")],
    )

    for w in ("TCheckbutton", "TRadiobutton"):
        style.configure(w,
            background=t["bg"],               foreground=t["fg"],
            indicatorbackground=t["entry_bg"], indicatorforeground=t["fg"],
        )
        style.map(w,
            background=[("active", t["bg"])],
            foreground=[("disabled", t["disabled_fg"])],
            indicatorbackground=[("selected", t["select_bg"]), ("active", t["entry_bg"])],
        )

    for w in ("TScrollbar", "Vertical.TScrollbar", "Horizontal.TScrollbar"):
        style.configure(w,
            background=t["button_bg"], troughcolor=t["disabled_bg"],
            arrowcolor=t["fg"],        bordercolor=t["border"], relief="flat",
        )
        style.map(w, background=[("active", t["select_bg"])])

    style.configure("TNotebook",     background=t["bg"], bordercolor=t["border"], relief="flat")
    style.configure("TNotebook.Tab",
        background=t["button_bg"], foreground=t["fg"],
        padding=[8, 4], width=0,   bordercolor=t["border"],
    )
    style.map("TNotebook.Tab",
        background=[("selected", t["bg"]), ("active", t["entry_bg"])],
        foreground=[("selected", t["fg"])],
    )

    root.configure(bg=t["bg"])
    root.option_add("*Background",                 t["bg"],          "interactive")
    root.option_add("*Foreground",                 t["fg"],          "interactive")
    root.option_add("*activeBackground",           t["select_bg"],   "interactive")
    root.option_add("*activeForeground",           t["select_fg"],   "interactive")
    root.option_add("*disabledForeground",         t["disabled_fg"], "interactive")
    root.option_add("*Text.Background",            t["entry_bg"],    "interactive")
    root.option_add("*Text.Foreground",            t["entry_fg"],    "interactive")
    root.option_add("*Text.insertBackground",      t["fg"],          "interactive")
    root.option_add("*Text.selectBackground",      t["select_bg"],   "interactive")
    root.option_add("*Text.selectForeground",      t["select_fg"],   "interactive")
    root.option_add("*Listbox.Background",         t["entry_bg"],    "interactive")
    root.option_add("*Listbox.Foreground",         t["entry_fg"],    "interactive")
    root.option_add("*Listbox.selectBackground",   t["select_bg"],   "interactive")
    root.option_add("*Listbox.selectForeground",   t["select_fg"],   "interactive")
    root.option_add("*Canvas.Background",          t["bg"],          "interactive")
    root.option_add("*Canvas.highlightBackground", t["border"],      "interactive")
    root.option_add("*Menu.Background",            t["button_bg"],   "interactive")
    root.option_add("*Menu.Foreground",            t["fg"],          "interactive")
    root.option_add("*Menu.activeBackground",      t["select_bg"],   "interactive")
    root.option_add("*Menu.activeForeground",      t["select_fg"],   "interactive")
    root.option_add("*Menu.relief",                "flat",           "interactive")

    _repaint_tk_widgets(root, t)


def _repaint_tk_widgets(widget, t: dict) -> None:
    """Recursively repaint already-created plain tk (non-ttk) widgets."""
    is_ttk = isinstance(widget, ttk.Widget)
    cls    = widget.__class__.__name__

    if not is_ttk:
        try:
            if cls in ("Tk", "Toplevel"):
                widget.configure(bg=t["bg"])
            elif cls == "Frame":
                widget.configure(bg=t["bg"])
            elif cls == "Label":
                widget.configure(bg=t["bg"], fg=t["fg"])
            elif cls == "Canvas":
                widget.configure(bg=t["bg"],
                                 highlightbackground=t["border"],
                                 highlightcolor=t["border"])
            elif cls == "Text":
                state = str(widget.cget("state"))
                bg = t["preview_bg"] if state == "disabled" else t["entry_bg"]
                widget.configure(
                    bg=bg, fg=t["entry_fg"],
                    insertbackground=t["fg"],
                    selectbackground=t["select_bg"],
                    selectforeground=t["select_fg"],
                )
            elif cls == "Listbox":
                widget.configure(
                    bg=t["entry_bg"],          fg=t["entry_fg"],
                    selectbackground=t["select_bg"],
                    selectforeground=t["select_fg"],
                )
            elif cls == "Menu":
                widget.configure(
                    bg=t["button_bg"],         fg=t["fg"],
                    activebackground=t["select_bg"],
                    activeforeground=t["select_fg"],
                    relief="flat",
                )
        except Exception:
            pass

    for child in widget.winfo_children():
        _repaint_tk_widgets(child, t)
