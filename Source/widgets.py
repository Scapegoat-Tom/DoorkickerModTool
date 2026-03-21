# ── widgets.py ────────────────────────────────────────────────────────────────
# Equipment editor tab widgets: WeaponTab, ArmorTab, ShieldTab, GrenadeTab.

import tkinter as tk
from tkinter import ttk, filedialog

from constants import (
    CLASS_VALUES,
    WEAPON_CATEGORIES, WEAPON_SKIN_BINDINGS,
    INVENTORY_BINDINGS_WEAPON,
    OPERATION_LABELS, OPERATION_LABEL_TO_VALUE, OPERATION_VALUE_TO_LABEL,
    CALIBER_TEXTS, RELOAD_PRESETS, RELOAD_OPTIONS, RELOAD_EMPTY_OPTIONS,
    SHELL_DROP_FAMILIES, SHELL_DROP_FAMILY_NAMES,
    PROTECTION_INFO_TEXTS, ARMOR_DEFAULTS,
    SHIELD_INFO_TEXTS, SHIELD_DEFAULTS,
    WEAPON_PRESET_LABELS, WEAPON_PRESETS,
    DESC_MAX_LINES,
    build_sound_preset,
)
from dialogs import make_scrollable, AttackTypeDialog, FireSoundDialog
from utils import get_image_size, wrap_description


# ── Shared layout helpers ─────────────────────────────────────────────────────

def _lbl(parent, text, r, c, **kw):
    ttk.Label(parent, text=text).grid(row=r, column=c, sticky="w", padx=6, pady=3, **kw)

def _entry(parent, r, c, width=28):
    v = tk.StringVar()
    ttk.Entry(parent, textvariable=v, width=width).grid(row=r, column=c, sticky="w", padx=6, pady=3)
    return v

def _combo(parent, r, c, values, width=28, state="readonly"):
    cb = ttk.Combobox(parent, values=values, width=width, state=state)
    cb.grid(row=r, column=c, sticky="w", padx=6, pady=3)
    return cb

def _sep(parent, r, colspan=4):
    ttk.Separator(parent, orient="horizontal").grid(
        row=r, column=0, columnspan=colspan, sticky="ew", pady=4)

def _hdr(parent, text, r, colspan=4):
    ttk.Label(parent, text=f"── {text} ──", font=("", 9, "bold")).grid(
        row=r, column=0, columnspan=colspan, sticky="w", padx=6)

def _spinbox(parent, from_, to, default, width=8):
    v  = tk.StringVar(value=str(default))
    sb = ttk.Spinbox(parent, from_=from_, to=to, textvariable=v, width=width)
    return sb, v


def _desc_block(parent, row_start):
    """Two-column raw-text / in-game-preview description block."""
    r = row_start
    _sep(parent, r);  r += 1
    _hdr(parent, f"Description  (42 chars/line, max {DESC_MAX_LINES} lines)", r); r += 1

    desc_frame = ttk.Frame(parent)
    desc_frame.grid(row=r, column=0, columnspan=4, sticky="ew", padx=6, pady=3)
    r += 1

    ttk.Label(desc_frame, text="Raw text (type freely)").grid(row=0, column=0, sticky="w", padx=4)
    ttk.Label(desc_frame, text="In-game preview").grid(row=0, column=1, sticky="w", padx=4)

    raw_frame = ttk.Frame(desc_frame)
    raw_frame.grid(row=1, column=0, sticky="nsew", padx=4)
    raw_text = tk.Text(raw_frame, width=38, height=8, wrap="word",
                       font=("Courier", 9), relief="sunken", bd=1)
    raw_sb   = ttk.Scrollbar(raw_frame, orient="vertical", command=raw_text.yview)
    raw_text.configure(yscrollcommand=raw_sb.set)
    raw_text.pack(side="left", fill="both", expand=True)
    raw_sb.pack(side="right", fill="y")

    preview = tk.Text(desc_frame, width=44, height=8, state="disabled",
                      font=("Courier", 9), relief="sunken", bd=1)
    preview.grid(row=1, column=1, sticky="nsew", padx=4)
    desc_frame.columnconfigure(0, weight=1)
    desc_frame.columnconfigure(1, weight=1)

    status = ttk.Label(parent, text="", foreground="gray")
    status.grid(row=r, column=0, columnspan=4, sticky="w", padx=6)
    r += 1
    return raw_text, preview, status, r


def _class_block(parent, row_start, default_classes=None):
    if default_classes is None:
        default_classes = ["Assaulter"]
    r = row_start
    _sep(parent, r);  r += 1
    _hdr(parent, "Classes", r); r += 1
    class_vars = {}
    cb_frame   = ttk.Frame(parent)
    cb_frame.grid(row=r, column=0, columnspan=4, sticky="w", padx=6, pady=3)
    for cls in CLASS_VALUES:
        var = tk.BooleanVar(value=(cls in default_classes))
        class_vars[cls] = var
        ttk.Checkbutton(cb_frame, text=cls, variable=var).pack(side="left", padx=8)
    r += 1
    return class_vars, r


def _mobility_block(parent, row_start, default_move="0", default_turn="0"):
    r = row_start
    _sep(parent, r);  r += 1
    _hdr(parent, "Mobility Modifiers", r); r += 1
    _lbl(parent, "Move Speed Modifier %", r, 0)
    move_var = _entry(parent, r, 1, 10); move_var.set(default_move)
    _lbl(parent, "Turn Speed Modifier %", r, 2)
    turn_var = _entry(parent, r, 3, 10); turn_var.set(default_turn)
    r += 1
    return move_var, turn_var, r


def _image_block(parent, row_start, size=(362, 157), label="Equipment Image"):
    r = row_start
    _sep(parent, r);  r += 1
    _hdr(parent, f"{label}  (must be {size[0]}x{size[1]})", r); r += 1
    _lbl(parent, "Image File (.tga/.png)", r, 0)
    image_var = tk.StringVar()
    ttk.Entry(parent, textvariable=image_var, width=38, state="readonly").grid(
        row=r, column=1, columnspan=2, sticky="w", padx=6, pady=3)
    warn = ttk.Label(parent, text="", foreground="red")

    def browse():
        path = filedialog.askopenfilename(
            title=f"Select image (must be {size[0]}x{size[1]})",
            filetypes=[("Image files", "*.tga *.png"), ("All files", "*.*")])
        if not path:
            return
        image_var.set(path)
        dims = get_image_size(path)
        if dims is None:
            warn.config(text="Could not read image dimensions.", foreground="red")
        elif dims != size:
            warn.config(text=f"Image is {dims[0]}x{dims[1]} - must be {size[0]}x{size[1]}.", foreground="red")
        else:
            warn.config(text=f"Correct size ({size[0]}x{size[1]})", foreground="green")

    ttk.Button(parent, text="Browse...", command=browse).grid(row=r, column=3, padx=6, pady=3)
    r += 1
    warn.grid(row=r, column=1, columnspan=3, sticky="w", padx=6)
    r += 1
    return image_var, warn, r


def _sync_desc(raw_text, preview, status, desc_errors_list):
    raw            = raw_text.get("1.0", "end-1c")
    wrapped, count = wrap_description(raw)
    preview_text   = wrapped.replace("\\n", "\n") if wrapped else ""
    preview.config(state="normal")
    preview.delete("1.0", "end")
    preview.insert("1.0", preview_text)
    preview.config(state="disabled")
    if count > DESC_MAX_LINES:
        status.config(text=f"{count} lines - exceeds {DESC_MAX_LINES}-line limit.", foreground="red")
        desc_errors_list[:] = ["overflow"]
    else:
        status.config(text=f"{count}/{DESC_MAX_LINES} lines" if count else "", foreground="gray")
        desc_errors_list[:] = []


# ─────────────────────────────────────────────────────────────────────────────
# WeaponPresetDialog
# ─────────────────────────────────────────────────────────────────────────────

class WeaponPresetDialog(tk.Toplevel):
    """Shown when the user adds a new weapon. result is a WEAPON_PRESET_LABELS key or None."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Choose Weapon Starting Point")
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)
        self.result = None
        self._build()
        self.geometry("340x240")

    def _build(self):
        f = ttk.Frame(self, padding=16)
        f.pack(fill="both", expand=True)
        ttk.Label(f, text="Select a base preset for the new weapon:").pack(anchor="w", pady=(0, 10))
        self._var = tk.StringVar(value=WEAPON_PRESET_LABELS[0])
        for label in WEAPON_PRESET_LABELS:
            ttk.Radiobutton(f, text=label, variable=self._var, value=label).pack(anchor="w", pady=3)
        btn = ttk.Frame(f)
        btn.pack(pady=(14, 0))
        ttk.Button(btn, text="Add Weapon", command=self._ok).pack(side="left", padx=6)
        ttk.Button(btn, text="Cancel",     command=self.destroy).pack(side="left", padx=6)

    def _ok(self):
        self.result = self._var.get()
        self.destroy()


# ─────────────────────────────────────────────────────────────────────────────
# WeaponTab
# ─────────────────────────────────────────────────────────────────────────────

class WeaponTab(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._fire_single_sounds = []
        self._fire_rapid_sounds  = []
        self._sound_prefix       = "M4"
        self._attack_types       = []
        self._desc_errors        = []
        self._build()

    def _build(self):
        _, f = make_scrollable(self)
        row  = 0

        _sep(f, row);  row += 1
        _hdr(f, "Weapon Identity", row); row += 1

        _lbl(f, "Weapon Name", row, 0)
        self.name = _entry(f, row, 1)
        self.name.trace_add("write", self._on_name_change)
        _lbl(f, "Category", row, 2)
        self.category = _combo(f, row, 3, WEAPON_CATEGORIES, 16)
        self.category.set("rifle")
        self.category.bind("<<ComboboxSelected>>", self._on_category_change)
        row += 1

        _lbl(f, "Inventory Binding", row, 0)
        self.inv_binding = _combo(f, row, 1, INVENTORY_BINDINGS_WEAPON, 24)
        self.inv_binding.set("PrimaryWeapon")
        _lbl(f, "Skin Binding", row, 2)
        self.skin_binding = _combo(f, row, 3, WEAPON_SKIN_BINDINGS, 16)
        self.skin_binding.set("rifle")
        row += 1

        _lbl(f, "Caliber", row, 0)
        self.caliber = ttk.Combobox(f, values=CALIBER_TEXTS, width=28)
        self.caliber.grid(row=row, column=1, sticky="w", padx=6, pady=3)
        self.caliber.set("@firearm_caliber_556x45_name")
        _lbl(f, "Operation", row, 2)
        self.operation = _combo(f, row, 3, OPERATION_LABELS, 26)
        self.operation.set("Semi-Auto")
        row += 1

        self._raw_text, self._desc_preview, self._desc_status, row = _desc_block(f, row)
        self._raw_text.bind("<KeyRelease>", self._on_desc_change)
        self._raw_text.bind("<<Paste>>",    lambda e: self.after(10, self._on_desc_change))

        self._class_vars, row = _class_block(f, row, ["Assaulter"])
        self.move_speed, self.turn_speed, row = _mobility_block(f, row, "-14", "-5")
        self.render_image_var, self._img_warn, row = _image_block(f, row, (362, 157), "Weapon Image")

        _sep(f, row);  row += 1
        _hdr(f, "Ballistics & Performance", row); row += 1
        self._param_vars = {}

        for ltext, key, default, rtext, rkey, rdefault in [
            ("Muzzle Drop Distance (m)", "muzzle_drop",       "0.95", "Num Pellets",             "num_pellets",       "1"),
            ("Rounds per Magazine",      "rounds_mag",         "25",   "Rounds per Second",       "rounds_sec",        "6"),
            ("Spread at 10m",            "spread",             "0.1",  "Shot Sound Distance (m)", "shot_sound_meters", "30"),
        ]:
            _lbl(f, ltext, row, 0); self._param_vars[key]  = _entry(f, row, 1, 12); self._param_vars[key].set(default)
            _lbl(f, rtext, row, 2); self._param_vars[rkey] = _entry(f, row, 3, 12); self._param_vars[rkey].set(rdefault)
            row += 1

        _lbl(f, "Damage per Bullet  (7-14)", row, 0)
        self._dmg_spin, self._param_vars["damage"] = _spinbox(f, 7, 14, 12)
        self._dmg_spin.grid(row=row, column=1, sticky="w", padx=6, pady=3)
        _lbl(f, "Armor Piercing Level  (2-7)", row, 2)
        self._ap_spin, self._param_vars["armor_piercing"] = _spinbox(f, 2, 7, 6)
        self._ap_spin.grid(row=row, column=3, sticky="w", padx=6, pady=3)
        row += 1

        self.silenced  = tk.BooleanVar(value=False)
        ttk.Checkbutton(f, text="Silenced", variable=self.silenced).grid(
            row=row, column=0, sticky="w", padx=6, pady=3)
        self.bolt_mode = tk.StringVar(value="closed_bolt")
        ttk.Radiobutton(f, text="Closed Bolt",   variable=self.bolt_mode, value="closed_bolt").grid(
            row=row, column=1, sticky="w", padx=6, pady=3)
        ttk.Radiobutton(f, text="Cyclic Reload", variable=self.bolt_mode, value="cyclic_reload").grid(
            row=row, column=2, sticky="w", padx=6, pady=3)
        row += 1

        _sep(f, row);  row += 1
        _hdr(f, "Timing  (milliseconds)", row); row += 1
        for ltext, key, default, rtext, rkey, rdefault in [
            ("Reload Time",    "reload_time",     "2200", "Reload Empty Time", "reload_empty_time", "2700"),
            ("Change In Time", "change_in_time",  "300",  "Change Out Time",   "change_out_time",   "80"),
            ("Ready Time",     "ready_time",       "320",  "Guard Time",        "guard_time",        "140"),
        ]:
            _lbl(f, ltext, row, 0); self._param_vars[key]  = _entry(f, row, 1, 12); self._param_vars[key].set(default)
            _lbl(f, rtext, row, 2); self._param_vars[rkey] = _entry(f, row, 3, 12); self._param_vars[rkey].set(rdefault)
            row += 1

        _sep(f, row);  row += 1
        _hdr(f, "Attack Types", row); row += 1
        self._at_label = ttk.Label(f, text=self._at_summary(), width=54, anchor="w",
                                   relief="sunken", padding=3)
        self._at_label.grid(row=row, column=0, columnspan=3, sticky="w", padx=6, pady=3)
        ttk.Button(f, text="Choose...", command=self._open_attack_dialog).grid(
            row=row, column=3, padx=6, pady=3)
        row += 1

        _sep(f, row);  row += 1
        _hdr(f, "Sounds", row); row += 1

        _lbl(f, "Fire Sound Preset", row, 0)
        self._sound_label = ttk.Label(f, text=self._sound_prefix, width=18,
                                      relief="sunken", anchor="w", padding=3)
        self._sound_label.grid(row=row, column=1, sticky="w", padx=6, pady=3)
        ttk.Button(f, text="Choose...", command=self._open_sound_dialog).grid(
            row=row, column=2, sticky="w", padx=6, pady=3)
        row += 1

        _lbl(f, "Reload Sound", row, 0)
        self.reload_sound = _combo(f, row, 1, RELOAD_OPTIONS, 24)
        self.reload_sound.set("SFX_1911_RELD")
        _lbl(f, "Reload Empty Sound", row, 2)
        self.reload_empty_sound = _combo(f, row, 3, RELOAD_EMPTY_OPTIONS, 24)
        self.reload_empty_sound.set("SFX_M4_RELDEMPT")
        row += 1

        _lbl(f, "Shell Drop Family", row, 0)
        self._shell_family = tk.StringVar(value="Rifle")
        sf_frame = ttk.Frame(f)
        sf_frame.grid(row=row, column=1, columnspan=3, sticky="w", padx=6, pady=3)
        for name in SHELL_DROP_FAMILY_NAMES:
            ttk.Radiobutton(sf_frame, text=name, variable=self._shell_family, value=name).pack(side="left", padx=6)

    def _on_name_change(self, *_):
        try:
            self.master.tab(self, text=self.name.get().strip() or "Weapon")
        except Exception:
            pass

    def _at_summary(self):
        return ", ".join(self._attack_types) if self._attack_types else "(none selected)"

    def _on_category_change(self, _=None):
        cat    = self.category.get()
        preset = RELOAD_PRESETS.get(cat, RELOAD_PRESETS["rifle"])
        if cat == "shotgun":
            self.caliber.set("@firearm_caliber_12gauge_name")
        self.reload_sound.set(preset["reload"])
        self.reload_empty_sound.set(preset["reload_empty"])
        self._shell_family.set(preset["shell_family"])

    def _open_sound_dialog(self):
        dlg = FireSoundDialog(self, self._sound_prefix)
        self.wait_window(dlg)
        if dlg.result:
            self._sound_prefix = dlg.result
            self._sound_label.config(text=dlg.result)
            fs, fr = build_sound_preset(dlg.result)
            self._fire_single_sounds = fs
            self._fire_rapid_sounds  = fr

    def _on_desc_change(self, _=None):
        _sync_desc(self._raw_text, self._desc_preview, self._desc_status, self._desc_errors)

    def _open_attack_dialog(self):
        dlg = AttackTypeDialog(self, self._attack_types)
        self.wait_window(dlg)
        if dlg.result is not None:
            self._attack_types = dlg.result
            self._at_label.config(text=self._at_summary())

    def get_data(self) -> dict:
        op_label = self.operation.get()
        return {
            "name":               self.name.get(),
            "category":           self.category.get(),
            "inventory_binding":  self.inv_binding.get(),
            "skin_binding":       self.skin_binding.get(),
            "caliber":            self.caliber.get(),
            "operation":          OPERATION_LABEL_TO_VALUE.get(op_label, op_label),
            "description":        self._raw_text.get("1.0", "end-1c"),
            "classes":            [c for c, v in self._class_vars.items() if v.get()],
            "move_speed":         self.move_speed.get(),
            "turn_speed":         self.turn_speed.get(),
            "render_image":       self.render_image_var.get(),
            "silenced":           self.silenced.get(),
            "closed_bolt":        self.bolt_mode.get() == "closed_bolt",
            "cyclic_reload":      self.bolt_mode.get() == "cyclic_reload",
            "attack_types":       self._attack_types[:4],
            "fire_single_sounds": self._fire_single_sounds,
            "fire_rapid_sounds":  self._fire_rapid_sounds,
            "sound_preset":       self._sound_prefix,
            "reload_sound":       self.reload_sound.get(),
            "reload_empty_sound": self.reload_empty_sound.get(),
            "shell_family":       self._shell_family.get(),
            **{k: v.get() for k, v in self._param_vars.items()},
        }

    def load_data(self, d: dict):
        self.name.set(d.get("name", ""))
        self._on_name_change()
        self.category.set(d.get("category", "rifle"))
        self.inv_binding.set(d.get("inventory_binding", "PrimaryWeapon"))
        self.skin_binding.set(d.get("skin_binding", "rifle"))
        self.caliber.set(d.get("caliber", ""))
        self.operation.set(OPERATION_VALUE_TO_LABEL.get(d.get("operation", ""), d.get("operation", "")))
        self._raw_text.delete("1.0", "end")
        self._raw_text.insert("1.0", d.get("description", ""))
        self._on_desc_change()
        for cls, var in self._class_vars.items():
            var.set(cls in d.get("classes", []))
        self.move_speed.set(d.get("move_speed", "-14"))
        self.turn_speed.set(d.get("turn_speed", "-5"))
        self.render_image_var.set(d.get("render_image", ""))
        self.silenced.set(d.get("silenced", False))
        self.bolt_mode.set("closed_bolt" if d.get("closed_bolt", True) else "cyclic_reload")
        self._attack_types = d.get("attack_types", [])
        self._at_label.config(text=self._at_summary())
        preset = d.get("sound_preset", "M4")
        self._sound_prefix = preset
        self._sound_label.config(text=preset)
        self._fire_single_sounds = d.get("fire_single_sounds", [])
        self._fire_rapid_sounds  = d.get("fire_rapid_sounds",  [])
        self.reload_sound.set(d.get("reload_sound", "SFX_1911_RELD"))
        self.reload_empty_sound.set(d.get("reload_empty_sound", "SFX_M4_RELDEMPT"))
        self._shell_family.set(d.get("shell_family", "Rifle"))
        for k, v in self._param_vars.items():
            if k in d:
                v.set(d[k])

    def validate(self) -> str | None:
        if not self.name.get().strip():
            return "Weapon name is required."
        if self._desc_errors:
            return f"Description exceeds {DESC_MAX_LINES}-line limit. Please shorten it."
        try:
            dmg = int(self._param_vars["damage"].get())
            if not (7 <= dmg <= 14):
                return f"Damage per Bullet must be 7-14 (got {dmg})."
        except ValueError:
            return "Damage per Bullet must be a whole number."
        try:
            ap = int(self._param_vars["armor_piercing"].get())
            if not (2 <= ap <= 7):
                return f"Armor Piercing Level must be 2-7 (got {ap})."
        except ValueError:
            return "Armor Piercing Level must be a whole number."
        return None


# ─────────────────────────────────────────────────────────────────────────────
# ArmorTab
# ─────────────────────────────────────────────────────────────────────────────

class ArmorTab(tk.Frame):
    """Defaults based on Raider Vest: all classes, no mobility penalty. No unlock cost."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._desc_errors = []
        self._build()

    def _build(self):
        _, f = make_scrollable(self)
        row  = 0

        _sep(f, row);  row += 1
        _hdr(f, "Armor Identity", row); row += 1
        _lbl(f, "Armor Name", row, 0)
        self.name = _entry(f, row, 1)
        self.name.trace_add("write", self._on_name_change)
        row += 1

        self._raw_text, self._desc_preview, self._desc_status, row = _desc_block(f, row)
        self._raw_text.bind("<KeyRelease>", self._on_desc_change)
        self._raw_text.bind("<<Paste>>",    lambda e: self.after(10, self._on_desc_change))

        self._class_vars, row = _class_block(f, row, ARMOR_DEFAULTS["classes"])
        self.move_speed, self.turn_speed, row = _mobility_block(
            f, row, ARMOR_DEFAULTS["move_speed"], ARMOR_DEFAULTS["turn_speed"])
        self.render_image_var, self._img_warn, row = _image_block(f, row, (362, 157), "Armor Image")

        _sep(f, row);  row += 1
        _hdr(f, "Protection Parameters", row); row += 1

        _lbl(f, "Protection Info Text", row, 0)
        self.protection_info = _combo(f, row, 1, PROTECTION_INFO_TEXTS, 28)
        self.protection_info.set(ARMOR_DEFAULTS["protection_info_text"])
        row += 1

        hdr_f = ttk.Frame(f)
        hdr_f.grid(row=row, column=0, columnspan=4, sticky="w", padx=6, pady=(6, 0))
        for ci, text in enumerate(["Zone", "Arc Degrees", "Coverage %", "Piercing Level"]):
            ttk.Label(hdr_f, text=text, font=("", 9, "bold"), width=16, anchor="center").grid(
                row=0, column=ci, padx=4)
        row += 1

        self._arc_vars = []
        zone_labels = ["Front  (90)", "Sides  (270)", "Full   (360)"]
        for label, arc_def in zip(zone_labels, ARMOR_DEFAULTS["protection_arcs"]):
            arc_f = ttk.Frame(f)
            arc_f.grid(row=row, column=0, columnspan=4, sticky="w", padx=6, pady=2)
            ttk.Label(arc_f, text=label, width=14, anchor="w").grid(row=0, column=0, padx=4)
            deg_var = tk.StringVar(value=arc_def["degrees"])
            ttk.Entry(arc_f, textvariable=deg_var, width=10, state="readonly").grid(row=0, column=1, padx=4)
            cov_var = tk.StringVar(value=arc_def["coverage"])
            ttk.Spinbox(arc_f, from_=0, to=100, textvariable=cov_var, width=8).grid(row=0, column=2, padx=4)
            pier_var = tk.StringVar(value=arc_def["piercing"])
            ttk.Spinbox(arc_f, from_=0, to=7, textvariable=pier_var, width=8).grid(row=0, column=3, padx=4)
            self._arc_vars.append({"degrees": deg_var, "coverage": cov_var, "piercing": pier_var})
            row += 1

        ttk.Label(f, text=(
            "Coverage %: percentage of bullets that pass through\n"
            "Piercing Level: bullets with piercing >= this bypass coverage reduction"
        ), foreground="gray", font=("", 8)).grid(
            row=row, column=0, columnspan=4, sticky="w", padx=6, pady=(2, 6))

    def _on_name_change(self, *_):
        try:
            self.master.tab(self, text=self.name.get().strip() or "Armor")
        except Exception:
            pass

    def _on_desc_change(self, _=None):
        _sync_desc(self._raw_text, self._desc_preview, self._desc_status, self._desc_errors)

    def get_data(self) -> dict:
        return {
            "name":                 self.name.get(),
            "description":          self._raw_text.get("1.0", "end-1c"),
            "classes":              [c for c, v in self._class_vars.items() if v.get()],
            "move_speed":           self.move_speed.get(),
            "turn_speed":           self.turn_speed.get(),
            "render_image":         self.render_image_var.get(),
            "protection_info_text": self.protection_info.get(),
            "protection_arcs": [
                {"degrees": av["degrees"].get(), "coverage": av["coverage"].get(), "piercing": av["piercing"].get()}
                for av in self._arc_vars
            ],
        }

    def load_data(self, d: dict):
        self.name.set(d.get("name", ""))
        self._on_name_change()
        self._raw_text.delete("1.0", "end")
        self._raw_text.insert("1.0", d.get("description", ""))
        self._on_desc_change()
        for cls, var in self._class_vars.items():
            var.set(cls in d.get("classes", ARMOR_DEFAULTS["classes"]))
        self.move_speed.set(d.get("move_speed", ARMOR_DEFAULTS["move_speed"]))
        self.turn_speed.set(d.get("turn_speed", ARMOR_DEFAULTS["turn_speed"]))
        self.render_image_var.set(d.get("render_image", ""))
        self.protection_info.set(d.get("protection_info_text", ARMOR_DEFAULTS["protection_info_text"]))
        saved_arcs = d.get("protection_arcs", ARMOR_DEFAULTS["protection_arcs"])
        for i, av in enumerate(self._arc_vars):
            if i < len(saved_arcs):
                av["coverage"].set(saved_arcs[i].get("coverage", "40"))
                av["piercing"].set(saved_arcs[i].get("piercing", "5"))

    def validate(self) -> str | None:
        if not self.name.get().strip():
            return "Armor name is required."
        if self._desc_errors:
            return f"Description exceeds {DESC_MAX_LINES}-line limit. Please shorten it."
        return None


# ─────────────────────────────────────────────────────────────────────────────
# ShieldTab
# ─────────────────────────────────────────────────────────────────────────────

class ShieldTab(tk.Frame):
    """
    Editor for a single <Shield> entry (inventoryBinding=SupportGear).
    One ProtectionArc + FieldOfView. No unlock cost.
    Defaults based on Enforcer Shield (Level IIIA).
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._desc_errors = []
        self._build()

    def _build(self):
        _, f = make_scrollable(self)
        row  = 0

        _sep(f, row);  row += 1
        _hdr(f, "Shield Identity", row); row += 1
        _lbl(f, "Shield Name", row, 0)
        self.name = _entry(f, row, 1)
        self.name.trace_add("write", self._on_name_change)
        row += 1

        self._raw_text, self._desc_preview, self._desc_status, row = _desc_block(f, row)
        self._raw_text.bind("<KeyRelease>", self._on_desc_change)
        self._raw_text.bind("<<Paste>>",    lambda e: self.after(10, self._on_desc_change))

        self._class_vars, row = _class_block(f, row, SHIELD_DEFAULTS["classes"])
        self.move_speed, self.turn_speed, row = _mobility_block(
            f, row, SHIELD_DEFAULTS["move_speed"], SHIELD_DEFAULTS["turn_speed"])
        self.render_image_var, self._img_warn, row = _image_block(f, row, (362, 157), "Shield Image")

        _sep(f, row);  row += 1
        _hdr(f, "Protection Parameters", row); row += 1

        _lbl(f, "Protection Info Text", row, 0)
        self.protection_info = _combo(f, row, 1, SHIELD_INFO_TEXTS, 28)
        self.protection_info.set(SHIELD_DEFAULTS["protection_info_text"])
        row += 1

        _hdr(f, "Protection Arc", row); row += 1
        arc_f = ttk.Frame(f)
        arc_f.grid(row=row, column=0, columnspan=4, sticky="w", padx=6, pady=4)
        for ci, text in enumerate(["Arc Degrees", "Coverage %", "Piercing Level"]):
            ttk.Label(arc_f, text=text, font=("", 9, "bold"), width=16, anchor="center").grid(
                row=0, column=ci, padx=4)

        self._arc_deg  = tk.StringVar(value=SHIELD_DEFAULTS["arc_degrees"])
        self._arc_cov  = tk.StringVar(value=SHIELD_DEFAULTS["arc_coverage"])
        self._arc_pier = tk.StringVar(value=SHIELD_DEFAULTS["arc_piercing"])
        ttk.Entry(arc_f, textvariable=self._arc_deg, width=10).grid(row=1, column=0, padx=4, pady=3)
        ttk.Spinbox(arc_f, from_=0, to=100, textvariable=self._arc_cov,  width=8).grid(row=1, column=1, padx=4)
        ttk.Spinbox(arc_f, from_=0, to=7,   textvariable=self._arc_pier, width=8).grid(row=1, column=2, padx=4)
        row += 1

        ttk.Label(f, text=(
            "Arc Degrees: angular width of the shield's protection (e.g. 75 = ~quarter turn)\n"
            "Coverage %: percentage of bullets that pass through\n"
            "Piercing Level: bullets with piercing >= this bypass coverage reduction"
        ), foreground="gray", font=("", 8)).grid(
            row=row, column=0, columnspan=4, sticky="w", padx=6, pady=(0, 6))
        row += 1

        _sep(f, row);  row += 1
        _hdr(f, "Field of View", row); row += 1
        fov_f = ttk.Frame(f)
        fov_f.grid(row=row, column=0, columnspan=4, sticky="w", padx=6, pady=4)
        ttk.Label(fov_f, text="FOV Degrees", width=16, anchor="w").grid(row=0, column=0, padx=4)
        self._fov_deg = tk.StringVar(value=SHIELD_DEFAULTS["fov_degrees"])
        ttk.Entry(fov_f, textvariable=self._fov_deg, width=8).grid(row=0, column=1, padx=4)
        ttk.Label(fov_f, text="Eye Radius (m)", width=16, anchor="w").grid(row=0, column=2, padx=4)
        self._fov_eye = tk.StringVar(value=SHIELD_DEFAULTS["fov_eye_radius"])
        ttk.Entry(fov_f, textvariable=self._fov_eye, width=8).grid(row=0, column=3, padx=4)
        row += 1

        ttk.Label(f, text=(
            "FOV Degrees: trooper's field of view is reduced to this angle while the shield is equipped\n"
            "Eye Radius: detection radius in metres (leave at 0.4)"
        ), foreground="gray", font=("", 8)).grid(
            row=row, column=0, columnspan=4, sticky="w", padx=6, pady=(0, 6))

    def _on_name_change(self, *_):
        try:
            self.master.tab(self, text=self.name.get().strip() or "Shield")
        except Exception:
            pass

    def _on_desc_change(self, _=None):
        _sync_desc(self._raw_text, self._desc_preview, self._desc_status, self._desc_errors)

    def get_data(self) -> dict:
        return {
            "name":                 self.name.get(),
            "description":          self._raw_text.get("1.0", "end-1c"),
            "classes":              [c for c, v in self._class_vars.items() if v.get()],
            "move_speed":           self.move_speed.get(),
            "turn_speed":           self.turn_speed.get(),
            "render_image":         self.render_image_var.get(),
            "protection_info_text": self.protection_info.get(),
            "arc_degrees":          self._arc_deg.get(),
            "arc_coverage":         self._arc_cov.get(),
            "arc_piercing":         self._arc_pier.get(),
            "fov_degrees":          self._fov_deg.get(),
            "fov_eye_radius":       self._fov_eye.get(),
        }

    def load_data(self, d: dict):
        self.name.set(d.get("name", ""))
        self._on_name_change()
        self._raw_text.delete("1.0", "end")
        self._raw_text.insert("1.0", d.get("description", ""))
        self._on_desc_change()
        for cls, var in self._class_vars.items():
            var.set(cls in d.get("classes", SHIELD_DEFAULTS["classes"]))
        self.move_speed.set(d.get("move_speed", SHIELD_DEFAULTS["move_speed"]))
        self.turn_speed.set(d.get("turn_speed", SHIELD_DEFAULTS["turn_speed"]))
        self.render_image_var.set(d.get("render_image", ""))
        self.protection_info.set(d.get("protection_info_text", SHIELD_DEFAULTS["protection_info_text"]))
        self._arc_deg.set(d.get("arc_degrees",    SHIELD_DEFAULTS["arc_degrees"]))
        self._arc_cov.set(d.get("arc_coverage",   SHIELD_DEFAULTS["arc_coverage"]))
        self._arc_pier.set(d.get("arc_piercing",  SHIELD_DEFAULTS["arc_piercing"]))
        self._fov_deg.set(d.get("fov_degrees",    SHIELD_DEFAULTS["fov_degrees"]))
        self._fov_eye.set(d.get("fov_eye_radius", SHIELD_DEFAULTS["fov_eye_radius"]))

    def validate(self) -> str | None:
        if not self.name.get().strip():
            return "Shield name is required."
        if self._desc_errors:
            return f"Description exceeds {DESC_MAX_LINES}-line limit. Please shorten it."
        return None


# ─────────────────────────────────────────────────────────────────────────────
# GrenadeTab  (placeholder)
# ─────────────────────────────────────────────────────────────────────────────

class GrenadeTab(tk.Frame):
    """
    Placeholder tab for grenade / throwable equipment.
    Full implementation pending deeper research into the grenade XML schema
    (multi-range EffectRange, FX definitions, shrapnel, explosion timing, etc.)
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._build()

    def _build(self):
        f = ttk.Frame(self)
        f.pack(fill="both", expand=True, padx=20, pady=60)
        ttk.Label(f, text="Grenade Editor", font=("", 14, "bold")).pack(pady=(0, 16))
        ttk.Label(f, text=(
            "Grenade support is coming in a future update.\n\n"
            "Grenades require multi-range effect zones, FX definitions,\n"
            "shrapnel settings, and explosion timing parameters — all of which\n"
            "need deeper research before a proper editor can be built.\n\n"
            "This section is reserved as a placeholder."
        ), justify="center", foreground="gray").pack()

    def get_data(self) -> dict:
        return {}

    def load_data(self, d: dict):
        pass

    def validate(self) -> str | None:
        return None
