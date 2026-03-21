# ── main.py ───────────────────────────────────────────────────────────────────
# Doorkicker Mod Tool — main application window and entry point.
#
# Module layout:
#   main.py      — App (tk.Tk), menus, mod-info panel, project save/load
#   widgets.py   — WeaponTab, ArmorTab, ShieldTab, GrenadeTab
#   dialogs.py   — SettingsDialog, ChangeNotesDialog, TagPickerDialog,
#                  AttackTypeDialog, FireSoundDialog
#   xml_gen.py   — generate_mod_xml / filesystem_mount_xml / equipment_xml
#   publish.py   — Steam Workshop publish/update/delete via DK.exe
#   theme.py     — apply_theme, _repaint_tk_widgets
#   utils.py     — load/save settings, sanitize_filename, wrap_description, …
#   constants.py — all lookup tables, static data, and weapon/armor presets

import os
import sys
import json
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from utils      import load_settings, save_settings, sanitize_filename, mod_name_to_xml_filename, get_image_size
from theme      import apply_theme
from xml_gen    import generate_mod_xml, generate_filesystem_mount_xml, generate_equipment_xml
from publish    import Publisher
from dialogs    import SettingsDialog, ChangeNotesDialog, TagPickerDialog
from widgets    import WeaponTab, ArmorTab, ShieldTab, GrenadeTab, WeaponPresetDialog
from constants  import WEAPON_PRESETS


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Doorkicker Mod Tool")
        self.geometry("980x800")
        self.resizable(True, True)

        self.settings        = load_settings()
        self.weapon_tabs:    list[WeaponTab]  = []
        self.armor_tabs:     list[ArmorTab]   = []
        self.shield_tabs:    list[ShieldTab]  = []
        self.grenade_tabs:   list[GrenadeTab] = []
        self._project_path:  str | None       = None

        self._build_ui()
        self._apply_settings_defaults()
        apply_theme(self, self.settings.get("dark_mode", False))

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_menu()
        self._build_mod_info()
        self._build_equipment_section()

    def _build_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New",                command=self._new,              accelerator="Ctrl+N")
        file_menu.add_command(label="Open...",            command=self._open,             accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save",               command=self._save,             accelerator="Ctrl+S")
        file_menu.add_command(label="Save & Update...",   command=self._save_update,      accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Settings...",        command=self._open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Open Output Folder", command=self._open_output_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit",               command=self.quit)

        pub_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Publish", menu=pub_menu)
        pub_menu.add_command(label="Publish to Workshop...", command=lambda: self._run_publish("-publish",          "Publish"))
        pub_menu.add_command(label="Update Workshop Mod...", command=lambda: self._run_publish("-update_published", "Update"))
        pub_menu.add_separator()
        pub_menu.add_command(label="Delete from Workshop...",command=lambda: self._run_publish("-delete_published", "Delete"))

        self.bind_all("<Control-n>", lambda e: self._new())
        self.bind_all("<Control-o>", lambda e: self._open())
        self.bind_all("<Control-s>", lambda e: self._save())
        self.bind_all("<Control-S>", lambda e: self._save_update())

    def _build_mod_info(self):
        mf = ttk.LabelFrame(self, text="Mod Info", padding=8)
        mf.pack(fill="x", padx=10, pady=(10, 4))

        def lbl(text, r, c):
            ttk.Label(mf, text=text).grid(row=r, column=c, sticky="w", padx=6, pady=3)

        def entry(r, c, width=28):
            v = tk.StringVar()
            ttk.Entry(mf, textvariable=v, width=width).grid(row=r, column=c, sticky="w", padx=6, pady=3)
            return v

        lbl("Mod Name",    0, 0); self.mod_name = entry(0, 1, 36)
        lbl("Description", 1, 0); self.mod_desc = entry(1, 1, 56)
        mf.grid_columnconfigure(1, weight=1)

        lbl("Tags", 2, 0)
        self._tags_var = tk.StringVar(value="Weapons")
        tag_frame = ttk.Frame(mf)
        tag_frame.grid(row=2, column=1, sticky="w", padx=6, pady=3)
        ttk.Entry(tag_frame, textvariable=self._tags_var, width=36, state="readonly").pack(side="left")
        ttk.Button(tag_frame, text="Choose...", command=self._pick_tags).pack(side="left", padx=(6, 0))

        lbl("Mod Image  (512x512 PNG)", 3, 0)
        self.mod_image_var = tk.StringVar()
        ttk.Entry(mf, textvariable=self.mod_image_var, width=52, state="readonly").grid(
            row=3, column=1, columnspan=2, sticky="w", padx=6, pady=3)
        ttk.Button(mf, text="Browse...", command=self._browse_mod_image).grid(row=3, column=3, padx=6, pady=3)
        self.mod_img_warn = ttk.Label(mf, text="", foreground="red")
        self.mod_img_warn.grid(row=4, column=1, columnspan=3, sticky="w", padx=6)

        self.mod_author       = tk.StringVar()
        self.mod_change_notes = tk.StringVar()
        self.output_dir       = tk.StringVar(value=self.settings.get("last_output_dir", ""))

    def _build_equipment_section(self):
        """Four sub-notebooks (Weapons / Armor / Shield / Grenades) inside a top-level notebook."""
        eq_nb = ttk.Notebook(self)
        eq_nb.pack(fill="both", expand=True, padx=10, pady=4)

        # Weapons
        wpn_frame = ttk.Frame(eq_nb)
        eq_nb.add(wpn_frame, text="  Weapons  ")
        self._build_sub_notebook(
            parent        = wpn_frame,
            tab_list_attr = "weapon_tabs",
            tab_class     = WeaponTab,
            default_label = "Weapon",
            add_label     = "+ Add Weapon",
            rm_label      = "- Remove Last Weapon",
            add_fn        = self._add_weapon_with_preset,
        )

        # Armor
        arm_frame = ttk.Frame(eq_nb)
        eq_nb.add(arm_frame, text="  Armor  ")
        self._build_sub_notebook(
            parent        = arm_frame,
            tab_list_attr = "armor_tabs",
            tab_class     = ArmorTab,
            default_label = "Armor",
            add_label     = "+ Add Armor",
            rm_label      = "- Remove Last Armor",
        )

        # Shield
        shd_frame = ttk.Frame(eq_nb)
        eq_nb.add(shd_frame, text="  Shields  ")
        self._build_sub_notebook(
            parent        = shd_frame,
            tab_list_attr = "shield_tabs",
            tab_class     = ShieldTab,
            default_label = "Shield",
            add_label     = "+ Add Shield",
            rm_label      = "- Remove Last Shield",
        )

        # Grenades (placeholder)
        gren_frame = ttk.Frame(eq_nb)
        eq_nb.add(gren_frame, text="  Grenades  ")
        self._build_sub_notebook(
            parent        = gren_frame,
            tab_list_attr = "grenade_tabs",
            tab_class     = GrenadeTab,
            default_label = "Grenade",
            add_label     = "+ Add Grenade",
            rm_label      = "- Remove Last Grenade",
        )

    def _build_sub_notebook(self, parent, tab_list_attr, tab_class,
                             default_label, add_label, rm_label, add_fn=None):
        """
        Generic helper that wires up a notebook for one equipment category.
        If add_fn is provided it replaces the default add behaviour (used for weapon preset dialog).
        """
        nf = ttk.LabelFrame(parent, padding=4)
        nf.pack(fill="both", expand=True, padx=4, pady=4)

        btn_row = ttk.Frame(nf)
        btn_row.pack(fill="x", pady=(0, 4))

        nb = ttk.Notebook(nf)
        nb.pack(fill="both", expand=True)

        nb_attr = f"_nb_{tab_list_attr}"
        setattr(self, nb_attr, nb)

        def default_add():
            tab_list = getattr(self, tab_list_attr)
            tab      = tab_class(nb)
            tab_list.append(tab)
            nb.add(tab, text=default_label)
            nb.select(tab)

        def remove():
            tab_list = getattr(self, tab_list_attr)
            if not tab_list:
                messagebox.showwarning("Cannot Remove", f"No {default_label.lower()} items to remove.")
                return
            nb.forget(tab_list[-1])
            tab_list.pop()

        actual_add = add_fn if add_fn is not None else default_add

        ttk.Button(btn_row, text=add_label, command=actual_add).pack(side="left", padx=4)
        ttk.Button(btn_row, text=rm_label,  command=remove).pack(side="left", padx=4)

        setattr(self, f"_add_{tab_list_attr}",    actual_add)
        setattr(self, f"_remove_{tab_list_attr}",  remove)

    # ── Weapon preset add ─────────────────────────────────────────────────────

    def _add_weapon_with_preset(self):
        """Show preset picker; add WeaponTab only if user confirms."""
        dlg = WeaponPresetDialog(self)
        self.wait_window(dlg)
        if dlg.result is None:
            return
        preset_data = WEAPON_PRESETS[dlg.result].copy()
        nb       = self._nb_weapon_tabs
        tab      = WeaponTab(nb)
        self.weapon_tabs.append(tab)
        nb.add(tab, text="Weapon")
        nb.select(tab)
        tab.load_data(preset_data)

    # ── Tag picker ────────────────────────────────────────────────────────────

    def _pick_tags(self):
        dlg = TagPickerDialog(self, self._tags_var.get())
        self.wait_window(dlg)
        if dlg.result is not None:
            self._tags_var.set(dlg.result)

    # ── Settings ──────────────────────────────────────────────────────────────

    def _apply_settings_defaults(self):
        if not self.mod_author.get():
            self.mod_author.set(self.settings.get("default_author", ""))
        self.output_dir.set(self.settings.get("last_output_dir", ""))

    def _open_settings(self):
        dlg = SettingsDialog(self, self.settings)
        self.wait_window(dlg)
        if dlg._result:
            self.settings.update(dlg._result)
            save_settings(self.settings)
            self.output_dir.set(self.settings.get("last_output_dir", ""))
            self.mod_author.set(self.settings.get("default_author", ""))
            apply_theme(self, self.settings.get("dark_mode", False))

    def _open_output_folder(self):
        mod_name   = self.mod_name.get().strip()
        output_dir = self.output_dir.get().strip()
        if not output_dir:
            messagebox.showwarning("No Output Folder",
                "No output folder set. Go to File -> Settings to set one.")
            return
        target = Path(output_dir) / mod_name if mod_name else Path(output_dir)
        if not target.exists():
            target = Path(output_dir)
        os.startfile(str(target))

    # ── Publish ───────────────────────────────────────────────────────────────

    def _run_publish(self, flag: str, label: str):
        exe_path   = self.settings.get("dk_exe_path", "").strip()
        mod_name   = self.mod_name.get().strip()
        output_dir = self.output_dir.get().strip()

        if not exe_path or not os.path.isfile(exe_path):
            messagebox.showerror("DoorKickers.exe Not Set",
                "Please set the path to DoorKickers.exe in File -> Settings before publishing.")
            return
        if not mod_name or not output_dir:
            messagebox.showerror("No Mod Saved",
                "Please save your mod first (File -> Save) before publishing.")
            return

        mod_folder = Path(output_dir) / mod_name
        if not mod_folder.is_dir():
            messagebox.showerror("Mod Folder Not Found",
                f"Expected mod folder not found:\n{mod_folder}\n\nPlease save your mod first.")
            return

        if flag == "-delete_published":
            if not messagebox.askyesno("Confirm Delete",
                f"This will permanently DELETE '{mod_name}' from the Steam Workshop "
                f"and unsubscribe all current subscribers.\n\nAre you sure?",
                icon="warning"):
                return

        if flag == "-update_published":
            dlg = ChangeNotesDialog(self, prefill=self.mod_change_notes.get().strip())
            self.wait_window(dlg)
            if dlg.result is None:
                return
            self.mod_change_notes.set(dlg.result)
            self._rewrite_mod_xml()

        pub = Publisher(exe_path, str(mod_folder))
        pub.run(flag, label, self.after, self._publish_done)

    def _publish_done(self, success: bool, detail: str, label: str):
        mod_name = self.mod_name.get().strip()
        if success:
            messagebox.showinfo(f"{label} Successful",
                f"'{mod_name}' was {label.lower()}ed successfully on the Steam Workshop.")
        else:
            messagebox.showerror(f"{label} Failed",
                f"The {label.lower()} operation did not complete successfully.\n\nDetail:\n{detail}")

    def _rewrite_mod_xml(self):
        mod_name   = self.mod_name.get().strip()
        output_dir = self.output_dir.get().strip()
        if not mod_name or not output_dir:
            return
        try:
            (Path(output_dir) / mod_name / "mod.xml").write_text(
                generate_mod_xml(self._collect_mod_data()), encoding="utf-8")
        except Exception as e:
            messagebox.showerror("Write Error", f"Could not update mod.xml:\n{e}")

    # ── File menu ─────────────────────────────────────────────────────────────

    def _new(self):
        if not messagebox.askyesno("New Project", "Discard current work and start a new project?"):
            return
        self.mod_name.set("")
        self.mod_desc.set("")
        self._tags_var.set("Weapons")
        self.mod_image_var.set("")
        self.mod_img_warn.config(text="")

        for nb_attr, tab_list_attr in [
            ("_nb_weapon_tabs",  "weapon_tabs"),
            ("_nb_armor_tabs",   "armor_tabs"),
            ("_nb_shield_tabs",  "shield_tabs"),
            ("_nb_grenade_tabs", "grenade_tabs"),
        ]:
            nb       = getattr(self, nb_attr)
            tab_list = getattr(self, tab_list_attr)
            for tab in tab_list:
                nb.forget(tab)
            tab_list.clear()

        self._project_path = None
        self.title("Doorkicker Mod Tool")
        self._apply_settings_defaults()
        apply_theme(self, self.settings.get("dark_mode", False))

    def _open(self):
        path = filedialog.askopenfilename(
            title="Open project",
            initialdir=self.settings.get("last_output_dir", os.path.expanduser("~")),
            filetypes=[("Doorkicker Mod Tool files", "*.dkmt"), ("All files", "*.*")]
        )
        if not path:
            return
        self._open_path(path)

    def _open_path(self, path: str):
        """Load a project from an absolute file path (used by File->Open and argv handler)."""
        try:
            with open(path, encoding="utf-8") as f:
                project = json.load(f)
            self._load_project(project)
            self._project_path = path
            self.title(f"Doorkicker Mod Tool - {Path(path).stem}")
        except Exception as e:
            messagebox.showerror("Open Failed", f"Could not open project:\n{e}")

    def _save(self, change_notes_override=None):
        mod_name = self.mod_name.get().strip()
        if not mod_name:
            messagebox.showerror("Validation Error", "Mod name is required.")
            return False
        if not self.output_dir.get():
            messagebox.showerror("Validation Error",
                "No output folder set. Go to File -> Settings to set one.")
            return False

        weapons, armors, shields = [], [], []

        for i, wt in enumerate(self.weapon_tabs):
            err = wt.validate()
            if err:
                messagebox.showerror(f"Validation Error - Weapon {i+1}", err)
                self._nb_weapon_tabs.select(wt)
                return False
            weapons.append(wt.get_data())

        for i, at in enumerate(self.armor_tabs):
            err = at.validate()
            if err:
                messagebox.showerror(f"Validation Error - Armor {i+1}", err)
                self._nb_armor_tabs.select(at)
                return False
            armors.append(at.get_data())

        for i, st in enumerate(self.shield_tabs):
            err = st.validate()
            if err:
                messagebox.showerror(f"Validation Error - Shield {i+1}", err)
                self._nb_shield_tabs.select(st)
                return False
            shields.append(st.get_data())

        # Grenades are placeholder — no validation or XML output yet
        if change_notes_override is not None:
            self.mod_change_notes.set(change_notes_override)

        mod_data = self._collect_mod_data()

        try:
            base      = Path(self.output_dir.get()) / mod_name
            items_dir = base / "gui" / "customization" / "items"
            mods_dir  = base / "gui" / "customization" / "mods"
            xml_dir   = base / "data" / "xml"
            for d in [base, items_dir, mods_dir, xml_dir]:
                d.mkdir(parents=True, exist_ok=True)

            (base / "mod.xml").write_text(
                generate_mod_xml(mod_data), encoding="utf-8")
            (base / "filesystem_mount.xml").write_text(
                generate_filesystem_mount_xml(mod_data), encoding="utf-8")
            xml_fn = mod_name_to_xml_filename(mod_name)
            (xml_dir / xml_fn).write_text(
                generate_equipment_xml(weapons, armors, shields), encoding="utf-8")

            if mod_data["mod_image_file"] and os.path.isfile(mod_data["mod_image_file"]):
                shutil.copy2(mod_data["mod_image_file"],
                             mods_dir / sanitize_filename(mod_data["mod_image_file"]))
            for item in weapons + armors + shields:
                img = item.get("render_image", "")
                if img and os.path.isfile(img):
                    shutil.copy2(img, items_dir / sanitize_filename(img))

            project          = self._collect_project(mod_data, weapons, armors, shields)
            project_filename = mod_name.replace(" ", "_") + ".dkmt"
            project_path     = Path(self.output_dir.get()) / project_filename
            project_path.write_text(json.dumps(project, indent=2), encoding="utf-8")
            self._project_path = str(project_path)
            self.title(f"Doorkicker Mod Tool - {project_filename}")

            messagebox.showinfo("Saved", f"Mod files generated and project saved!\n\n{base}")
            return True

        except Exception as e:
            messagebox.showerror("Save Failed", f"Failed to save:\n{e}")
            return False

    def _save_update(self):
        dlg = ChangeNotesDialog(self, prefill=self.mod_change_notes.get().strip())
        self.wait_window(dlg)
        if dlg.result is None:
            return
        self._save(change_notes_override=dlg.result)

    # ── Project serialization ─────────────────────────────────────────────────

    def _collect_mod_data(self) -> dict:
        return {
            "mod_name":         self.mod_name.get().strip(),
            "mod_description":  self.mod_desc.get().strip(),
            "mod_author":       self.mod_author.get().strip(),
            "mod_tags":         self._tags_var.get(),
            "mod_change_notes": self.mod_change_notes.get().strip(),
            "mod_image_file":   self.mod_image_var.get(),
        }

    def _collect_project(self, mod_data, weapons, armors, shields) -> dict:
        return {
            "version":    3,
            "mod":        mod_data,
            "output_dir": self.output_dir.get(),
            "weapons":    weapons,
            "armors":     armors,
            "shields":    shields,
        }

    def _load_project(self, project: dict):
        mod = project.get("mod", {})
        self.mod_name.set(mod.get("mod_name", ""))
        self.mod_author.set(mod.get("mod_author", ""))
        self.mod_desc.set(mod.get("mod_description", ""))
        self._tags_var.set(mod.get("mod_tags", "Weapons"))
        self.mod_change_notes.set(mod.get("mod_change_notes", ""))
        self.mod_image_var.set(mod.get("mod_image_file", ""))
        self.mod_img_warn.config(text="")
        if project.get("output_dir"):
            self.output_dir.set(project["output_dir"])

        for nb_attr, tab_list_attr in [
            ("_nb_weapon_tabs",  "weapon_tabs"),
            ("_nb_armor_tabs",   "armor_tabs"),
            ("_nb_shield_tabs",  "shield_tabs"),
            ("_nb_grenade_tabs", "grenade_tabs"),
        ]:
            nb       = getattr(self, nb_attr)
            tab_list = getattr(self, tab_list_attr)
            for tab in tab_list:
                nb.forget(tab)
            tab_list.clear()

        for w in project.get("weapons", []):
            nb  = self._nb_weapon_tabs
            tab = WeaponTab(nb)
            self.weapon_tabs.append(tab)
            nb.add(tab, text="Weapon")
            tab.load_data(w)

        for a in project.get("armors", []):
            nb  = self._nb_armor_tabs
            tab = ArmorTab(nb)
            self.armor_tabs.append(tab)
            nb.add(tab, text="Armor")
            tab.load_data(a)

        for s in project.get("shields", []):
            nb  = self._nb_shield_tabs
            tab = ShieldTab(nb)
            self.shield_tabs.append(tab)
            nb.add(tab, text="Shield")
            tab.load_data(s)

        apply_theme(self, self.settings.get("dark_mode", False))

    # ── Browse helpers ────────────────────────────────────────────────────────

    def _browse_mod_image(self):
        mod_name   = self.mod_name.get().strip()
        output_dir = self.output_dir.get().strip()
        initial    = os.path.expanduser("~")
        if mod_name and output_dir:
            mods_dir = Path(output_dir) / mod_name / "gui" / "customization" / "mods"
            initial  = str(mods_dir) if mods_dir.is_dir() else (output_dir or initial)
        path = filedialog.askopenfilename(
            title="Select mod image (512x512 PNG)",
            initialdir=initial,
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if not path:
            return
        self.mod_image_var.set(path)
        size = get_image_size(path)
        if size is None:
            self.mod_img_warn.config(text="Could not read image dimensions.", foreground="red")
        elif size != (512, 512):
            self.mod_img_warn.config(text=f"Image is {size[0]}x{size[1]} - should be 512x512.", foreground="red")
        else:
            self.mod_img_warn.config(text="Correct size (512x512)", foreground="green")


if __name__ == "__main__":
    app = App()
    # If launched by double-clicking a .dkmt file, Windows passes the path as argv[1]
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.isfile(path):
            app.after(100, lambda: app._open_path(path))
    app.mainloop()
