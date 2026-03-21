# Doorkicker Mod Tool

A desktop application for creating and publishing custom equipment mods for **Door Kickers** by KillHouse Games. Build weapons, armor, and shields through a guided interface and export valid XML mod files ready to load in-game or publish to the Steam Workshop — no manual XML editing required.

---

## Features

- **Weapons** — Full firearm editor with ballistics, timing, sound presets, attack types, and caliber selection. Four built-in starting presets (M4 Carbine, MP5A3, G17 Pistol, M590 Shotgun) pre-fill sensible defaults when adding a new weapon.
- **Armor** — Vest editor with three protection arc zones (Front, Sides, Full), mobility modifiers, and class assignments. Defaults based on the Raider Vest.
- **Shields** — Shield editor with a single protection arc, field-of-view settings, and mobility modifiers. Defaults based on the Enforcer Shield (Level IIIA).
- **Grenades** — Section reserved for a future update. Grenade XML is complex and will be implemented in a later release.
- **Live description preview** — The in-game description field wraps text in real time and warns you if you exceed the 10-line limit.
- **Multi-weapon / multi-armor mods** — Add as many items as you need; each gets its own editor tab.
- **Steam Workshop publishing** — Publish, update, and delete mods directly from the app via DoorKickers.exe command-line flags.
- **Dark and light theme** — Toggleable night mode that applies immediately without restarting.
- **Project files** — Save and reopen your work as `.dkmt` project files. Double-clicking a `.dkmt` file opens it directly in the tool (requires installer).

---

## Equipment Reference

### Weapons

| Field | Notes |
|---|---|
| Category | `rifle`, `pistol`, `shotgun`, `tazer` |
| Inventory Binding | Where the weapon appears in the trooper's loadout |
| Skin Binding | Which animation rig the weapon uses |
| Caliber / Operation | Informational text shown in the in-game stats panel |
| Attack Types | Up to 4 AI behaviour nodes that control how troopers use the weapon |
| Damage per Bullet | Valid range: 7–14 |
| Armor Piercing Level | Valid range: 2–7 |
| Closed Bolt / Cyclic Reload | Affects how the reload animation is triggered |
| Fire Sound Preset | Selects from all weapon sound prefixes present in the base game |
| Shell Drop Family | `Rifle`, `Pistol`, `Shotgun`, or `None` |

### Armor

Armor has three fixed protection arc zones that together describe full 360° coverage:

| Zone | Arc Degrees | Description |
|---|---|---|
| Front | 90° | Narrow frontal plate |
| Sides | 270° | Wraps around sides and rear |
| Full | 360° | Omnidirectional baseline layer |

Each zone has a **Coverage %** (percentage of bullets that pass through) and a **Piercing Level** (bullets with a piercing level at or above this value bypass the coverage reduction entirely).

### Shields

Shields use a single protection arc and a field-of-view block:

- **Arc Degrees** — Angular width of the shield's protection cone (e.g. 75 ≈ a quarter turn)
- **Coverage %** — Percentage of bullets that pass through the protected arc
- **Piercing Level** — Bullets at or above this level ignore coverage reduction
- **FOV Degrees** — The trooper's field of view is reduced to this angle while the shield is equipped
- **Eye Radius** — Detection radius in metres; leave at `0.4` unless you have a specific reason to change it

---

## Getting Started

### Running from source

Python 3.10 or later is required. No third-party packages are needed — the tool uses only the Python standard library.

```bash
python main.py
```

### First-time setup

1. Go to **File → Settings**
2. Set your **Default Output Folder** — this is where mod folders and project files will be saved
3. Optionally set your **Default Author Name** and the path to **DoorKickers.exe** (required for Workshop publishing)

### Creating a mod

1. Fill in the **Mod Info** section at the top — name, description, tags, and an optional 512×512 PNG cover image
2. Click **+ Add Weapon** (or Armor / Shield) and choose a starting preset
3. Fill in the item details across the tabs
4. Press **Ctrl+S** (or **File → Save**) to generate the mod folder and save a `.dkmt` project file

### Saving outputs

Each save writes three files into `<Output Folder>/<Mod Name>/`:

```
<Mod Name>/
  mod.xml                          ← Steam Workshop metadata
  filesystem_mount.xml             ← tells the game what to load
  data/xml/<Mod Name>.xml          ← all equipment definitions
  gui/customization/items/         ← copied weapon/armor images
  gui/customization/mods/          ← copied mod cover image
```

---

## Steam Workshop Publishing

Before publishing, ensure:
- Your mod has been saved at least once (**File → Save**)
- **DoorKickers.exe** path is set in **File → Settings**
- Steam is running and you are logged in

| Menu Item | Action |
|---|---|
| Publish → Publish to Workshop | Uploads the mod for the first time |
| Publish → Update Workshop Mod | Prompts for change notes, rewrites `mod.xml`, then updates the existing Workshop item |
| Publish → Delete from Workshop | Permanently removes the mod and unsubscribes all subscribers |

The tool launches DoorKickers.exe with the appropriate command-line flag, waits for it to finish, then reads `log.txt` from your Documents folder to confirm success or report an error.

> **Note:** The mod name in `mod.xml` must never be changed after a mod is published. Steam uses it as the unique identifier for your Workshop item.

---

## Image Requirements

| Image | Size | Format |
|---|---|---|
| Mod cover image | 512×512 | PNG |
| Weapon / Armor / Shield render | 362×157 | PNG or TGA |

The tool validates dimensions when you browse for an image and shows a warning if they are incorrect.

---

## Project Files

Projects are saved as `.dkmt` files (JSON) alongside the generated mod folder. They store all field values so you can reopen and continue editing at any time.

- **File → Open** — browse for a `.dkmt` file
- **Double-click** a `.dkmt` file in Explorer — opens directly in the tool (installer required for file association)
- Settings (output folder, author, exe path, theme) are stored separately in `dmt_settings.json` next to the executable

---

## Packaging (Developers)

To build a standalone executable from source:

```bash
pip install pyinstaller
pyinstaller --onedir --windowed --name "DoorkickerModTool" main.py
```

To build the installer (requires [Inno Setup](https://jrsoftware.org/isinfo.php)):

1. Open `installer.iss` in Inno Setup
2. Press **F9** to compile
3. The installer is written to `installer_output/DoorkickerModTool_Setup.exe`

The installer registers the `.dkmt` file association so double-clicking project files launches the tool automatically.

---

## File Structure (source)

```
doorkicker_mod_tool/
  main.py        — Application window, menus, project save/load
  widgets.py     — WeaponTab, ArmorTab, ShieldTab, GrenadeTab
  dialogs.py     — All popup dialogs (settings, tag picker, attack types, sounds)
  xml_gen.py     — XML generation for mod.xml, filesystem_mount.xml, equipment XML
  publish.py     — Steam Workshop publish/update/delete logic
  theme.py       — Dark and light theme application
  utils.py       — Settings persistence, file helpers, description word-wrap
  constants.py   — All lookup tables, weapon presets, armor/shield defaults
```

---

## Known Limitations

- **Grenades** are not yet supported. The Grenades section is a placeholder for a future update.
- **Publishing** requires DoorKickers.exe and Steam to be running on the same machine. It cannot publish remotely.
- **Mod names** cannot be changed after a mod is first published to the Workshop without creating a new Workshop item.
- The tool targets **Door Kickers version 1.1.6**. Compatibility with other versions is not guaranteed.

---

## License

This tool is not affiliated with or endorsed by KillHouse Games. Door Kickers is a trademark of KillHouse Games. Use of this tool is at your own risk.
