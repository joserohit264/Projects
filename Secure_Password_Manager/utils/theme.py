# utils/theme.py
import tkinter as tk
from tkinter import ttk

# store current mode globally (module-level)
CURRENT_MODE = "light"

LIGHT = {
    "bg": "#F6F6F6",
    "fg": "#202020",
    "accent": "#4E8BF5",
    "panel": "#FFFFFF",
    "muted": "#6B6B6B",
    "heading": "#111111",
    "tree_bg": "#FFFFFF",
    "tree_heading": "#EEEEEE",
    "button_active": "#6EA0F8"
}

DARK = {
    "bg": "#1F2226",
    "fg": "#EDEDED",
    "accent": "#4E8BF5",
    "panel": "#2A2E33",
    "muted": "#B8B8B8",
    "heading": "#FFFFFF",
    "tree_bg": "#222426",
    "tree_heading": "#2E3236",
    "button_active": "#6EA0F8"
}


def apply_theme(root: tk.Tk, mode: str = "light") -> ttk.Style:
    """
    Apply theme to the given root. mode = "light" or "dark".
    Returns ttk.Style object.
    """
    global CURRENT_MODE
    CURRENT_MODE = mode
    pal = LIGHT if mode == "light" else DARK

    style = ttk.Style(root)
    # Use clam for easy config
    try:
        style.theme_use("clam")
    except Exception:
        pass

    root.configure(bg=pal["bg"])

    # base font
    style.configure(".", font=("Segoe UI", 11), background=pal["bg"], foreground=pal["fg"])
    style.configure("TLabel", background=pal["bg"], foreground=pal["fg"])
    style.configure("TFrame", background=pal["bg"])
    style.configure("Card.TFrame", background=pal["panel"], relief="flat", borderwidth=0)
    style.configure("Accent.TButton",
                    background=pal["accent"], foreground="white", padding=8, relief="flat")
    style.map("Accent.TButton", background=[("active", pal["button_active"])])

    style.configure("TButton", padding=6)
    style.configure("TEntry", padding=6)
    style.configure("TSeparator", background=pal["muted"])

    style.configure("Treeview",
                    background=pal["tree_bg"],
                    fieldbackground=pal["tree_bg"],
                    foreground=pal["fg"],
                    rowheight=26)
    style.configure("Treeview.Heading",
                    background=pal["tree_heading"],
                    foreground=pal["heading"],
                    font=("Segoe UI", 11, "bold"))

    return style


def toggle_theme(root: tk.Tk):
    """Toggle between light and dark theme on root."""
    global CURRENT_MODE
    CURRENT_MODE = "dark" if CURRENT_MODE == "light" else "light"
    apply_theme(root, CURRENT_MODE)
    # force widget redraw: reconfigure background on root
    root.configure(bg=(LIGHT if CURRENT_MODE == "light" else DARK)["bg"])
    return CURRENT_MODE
