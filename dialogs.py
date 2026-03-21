# ── dialogs.py ────────────────────────────────────────────────────────────────
# All modal popup dialogs for Doorkicker Mod Tool.

import tkinter as tk
from tkinter import ttk, filedialog

from constants import ATTACK_TYPE_GROUPS, SOUND_GROUPS, MOD_TAGS


# ── Scrollable canvas helper (shared by dialogs) ──────────────────────────────

def make_scrollable(parent):
    canvas  = tk.Canvas(parent, borderwidth=0, highlightthickness=0)
    vscroll = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vscroll.set)
    vscroll.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    inner = ttk.Frame(canvas)
    win   = canvas.create_window((0, 0), window=inner, anchor="nw")
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))

    def _scroll(event):
        try:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except tk.TclError:
            pass

    canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _scroll))
    canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
    return canvas, inner


# ── Settings ──────────────────────────────────────────────────────────────────

class SettingsDialog(tk.Toplevel):
    """File → Settings dialog."""

    def __init__(self, parent, settings: dict):
        super().__init__(parent)
        self.title("Settings")
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)
        self._settings = settings
        self._result   = None
        self._build()
        self.geometry("560x250")

    def _build(self):
        f = ttk.Frame(self, padding=16)
        f.pack(fill="both", expand=True)

        # Output folder
        ttk.Label(f, text="Default Output Folder").grid(row=0, column=0, sticky="w", pady=6, padx=4)
        self._out_var = tk.StringVar(value=self._settings.get("last_output_dir", ""))
        ttk.Entry(f, textvariable=self._out_var, width=44, state="readonly").grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(f, text="Browse…", command=self._browse_out).grid(row=0, column=2, padx=(4, 12))

        # Author
        ttk.Label(f, text="Default Author Name").grid(row=1, column=0, sticky="w", pady=6, padx=4)
        self._author_var = tk.StringVar(value=self._settings.get("default_author", ""))
        ttk.Entry(f, textvariable=self._author_var, width=44).grid(row=1, column=1, sticky="ew", padx=4)

        # DoorKickers.exe
        ttk.Label(f, text="DoorKickers.exe").grid(row=2, column=0, sticky="w", pady=6, padx=4)
        self._exe_var = tk.StringVar(value=self._settings.get("dk_exe_path", ""))
        ttk.Entry(f, textvariable=self._exe_var, width=44, state="readonly").grid(row=2, column=1, sticky="ew", padx=4)
        ttk.Button(f, text="Browse…", command=self._browse_exe).grid(row=2, column=2, padx=(4, 12))

        # Night mode
        ttk.Label(f, text="Night Mode").grid(row=3, column=0, sticky="w", pady=6, padx=4)
        self._dark_var = tk.BooleanVar(value=self._settings.get("dark_mode", False))
        ttk.Checkbutton(f, variable=self._dark_var).grid(row=3, column=1, sticky="w", padx=4)

        f.columnconfigure(1, weight=1)

        btn = ttk.Frame(f)
        btn.grid(row=4, column=0, columnspan=3, pady=12)
        ttk.Button(btn, text="Save",   command=self._save).pack(side="left", padx=6)
        ttk.Button(btn, text="Cancel", command=self.destroy).pack(side="left", padx=6)

    def _browse_out(self):
        d = filedialog.askdirectory(
            title="Select default output folder",
            initialdir=self._out_var.get() or "~")
        if d:
            self._out_var.set(d)

    def _browse_exe(self):
        initial = (
            self._exe_var.get().rsplit("/", 1)[0]
            if self._exe_var.get()
            else "C:/Program Files (x86)/Steam/steamapps/common/DoorKickers"
        )
        p = filedialog.askopenfilename(
            title="Locate DoorKickers.exe",
            initialdir=initial,
            filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
        )
        if p:
            self._exe_var.set(p)

    def _save(self):
        self._result = {
            "last_output_dir": self._out_var.get(),
            "default_author":  self._author_var.get().strip(),
            "dk_exe_path":     self._exe_var.get().strip(),
            "dark_mode":       self._dark_var.get(),
        }
        self.destroy()


# ── Change Notes ──────────────────────────────────────────────────────────────

class ChangeNotesDialog(tk.Toplevel):
    def __init__(self, parent, prefill: str = ""):
        super().__init__(parent)
        self.title("Change Notes")
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)
        self.result = None
        self._build(prefill)
        self.geometry("420x160")

    def _build(self, prefill):
        f = ttk.Frame(self, padding=16)
        f.pack(fill="both", expand=True)
        ttk.Label(f, text="Describe what changed in this update:").pack(anchor="w", pady=(0, 6))
        self._var = tk.StringVar(value=prefill)
        ttk.Entry(f, textvariable=self._var, width=52).pack(fill="x")
        btn = ttk.Frame(f)
        btn.pack(pady=12)
        ttk.Button(btn, text="OK",     command=self._ok).pack(side="left", padx=6)
        ttk.Button(btn, text="Cancel", command=self.destroy).pack(side="left", padx=6)

    def _ok(self):
        self.result = self._var.get().strip()
        self.destroy()


# ── Tag Picker ────────────────────────────────────────────────────────────────

class TagPickerDialog(tk.Toplevel):
    """
    Multi-select tag picker.  result is a comma-separated string of chosen tags,
    e.g. "Weapons,Armor" — ready to drop straight into mod.xml.
    """

    def __init__(self, parent, current_tags: str = ""):
        super().__init__(parent)
        self.title("Select Mod Tags")
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)
        self.result = None
        # Parse the comma-separated current selection
        selected = {t.strip() for t in current_tags.split(",") if t.strip()}
        self._vars = {tag: tk.BooleanVar(value=(tag in selected)) for tag in MOD_TAGS}
        self._build()
        self.geometry("320x340")

    def _build(self):
        f = ttk.Frame(self, padding=16)
        f.pack(fill="both", expand=True)
        ttk.Label(f, text="Choose one or more tags:").pack(anchor="w", pady=(0, 8))

        box = ttk.Frame(f)
        box.pack(fill="x")
        for tag in MOD_TAGS:
            ttk.Checkbutton(box, text=tag, variable=self._vars[tag]).pack(anchor="w", pady=2)

        btn = ttk.Frame(f)
        btn.pack(pady=(12, 0))
        ttk.Button(btn, text="OK",     command=self._ok).pack(side="left", padx=6)
        ttk.Button(btn, text="Cancel", command=self.destroy).pack(side="left", padx=6)

    def _ok(self):
        chosen = [tag for tag in MOD_TAGS if self._vars[tag].get()]
        # Require at least one tag
        if not chosen:
            chosen = ["Weapons"]
        self.result = ",".join(chosen)
        self.destroy()


# ── Attack Types ──────────────────────────────────────────────────────────────

class AttackTypeDialog(tk.Toplevel):
    """Grouped checkbox picker, max 4 selections."""

    def __init__(self, parent, current_selection: list):
        super().__init__(parent)
        self.title("Select Attack Types  (max 4)")
        self.resizable(False, True)
        self.result   = None
        self._vars    = {}
        self._current = list(current_selection)
        self._build()
        self.grab_set()
        self.transient(parent)
        self.geometry("480x560")

    def _build(self):
        outer         = ttk.Frame(self)
        outer.pack(fill="both", expand=True, padx=8, pady=8)
        canvas, inner = make_scrollable(outer)

        self._status = ttk.Label(inner, text="", foreground="red")
        self._status.pack(anchor="w", padx=6, pady=(4, 0))

        for group_name, items in ATTACK_TYPE_GROUPS.items():
            grp = ttk.LabelFrame(inner, text=group_name, padding=4)
            grp.pack(fill="x", padx=4, pady=3)
            for item in items:
                var = tk.BooleanVar(value=(item in self._current))
                self._vars[item] = var
                ttk.Checkbutton(grp, text=item, variable=var,
                                command=self._on_toggle).pack(anchor="w")

        btn_row = ttk.Frame(self)
        btn_row.pack(fill="x", padx=8, pady=6)
        ttk.Button(btn_row, text="OK",        command=self._ok).pack(side="left",  padx=4)
        ttk.Button(btn_row, text="Cancel",    command=self.destroy).pack(side="left",  padx=4)
        ttk.Button(btn_row, text="Clear All", command=self._clear).pack(side="right", padx=4)

    def _on_toggle(self):
        selected = [k for k, v in self._vars.items() if v.get()]
        if len(selected) > 4:
            for k, v in self._vars.items():
                if v.get() and k not in self._current:
                    v.set(False)
                    break
            self._status.config(text="Maximum 4 attack types allowed.")
        else:
            self._status.config(text="")
        self._current = [k for k, v in self._vars.items() if v.get()]

    def _clear(self):
        for v in self._vars.values():
            v.set(False)
        self._current = []
        self._status.config(text="")

    def _ok(self):
        self.result = [k for k, v in self._vars.items() if v.get()][:4]
        self.destroy()


# ── Fire Sound ────────────────────────────────────────────────────────────────

class FireSoundDialog(tk.Toplevel):
    """Grouped radio-button picker for weapon fire sound prefix."""

    def __init__(self, parent, current_prefix: str):
        super().__init__(parent)
        self.title("Select Fire Sound Preset")
        self.resizable(True, True)
        self.result   = None
        self._current = current_prefix
        self._build()
        self.grab_set()
        self.transient(parent)
        self.geometry("700x500")

    def _build(self):
        self._var = tk.StringVar(value=self._current)
        grid = ttk.Frame(self, padding=10)
        grid.pack(fill="both", expand=True)

        for col, (group_name, prefixes) in enumerate(SOUND_GROUPS.items()):
            grp = ttk.LabelFrame(grid, text=group_name, padding=6)
            grp.grid(row=0, column=col, sticky="nsew", padx=4, pady=4)
            grid.columnconfigure(col, weight=1)
            for prefix in prefixes:
                ttk.Radiobutton(grp, text=prefix,
                                variable=self._var, value=prefix).pack(anchor="w")

        btn_row = ttk.Frame(self)
        btn_row.pack(fill="x", padx=10, pady=6)
        ttk.Button(btn_row, text="OK",     command=self._ok).pack(side="left", padx=4)
        ttk.Button(btn_row, text="Cancel", command=self.destroy).pack(side="left", padx=4)

    def _ok(self):
        self.result = self._var.get()
        self.destroy()
