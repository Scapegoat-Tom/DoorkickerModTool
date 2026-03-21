# ── constants.py ─────────────────────────────────────────────────────────────
# All static lookup tables and constant values for Doorkicker Mod Tool.
# No UI imports — safe to import from any module.

# ── Shared ────────────────────────────────────────────────────────────────────

CLASS_VALUES = ["Assaulter", "Breacher", "Pointman", "Shield", "Stealth"]

INVENTORY_BINDINGS_WEAPON = ["PrimaryWeapon", "SecondaryWeapon", "UtilityPouch"]
INVENTORY_BINDINGS_ARMOR  = ["Armor"]
INVENTORY_BINDINGS_GEAR   = ["UtilityPouch", "SupportGear", "SupportGear1"]

SKIN_BINDINGS = ["rifle", "pistol", "shotgun", "weaponless"]

# Steam Workshop tags — comma-separated in mod.xml; user picks 1+
MOD_TAGS = [
    "Weapons", "Armor", "Gear", "Levels", "Enemies",
    "Objects", "Sound", "Interface", "Total Conversions", "Other",
]

# ── Weapons ───────────────────────────────────────────────────────────────────

WEAPON_CATEGORIES    = ["rifle", "pistol", "shotgun", "tazer"]
WEAPON_SKIN_BINDINGS = ["rifle", "pistol", "shotgun"]

OPERATION_LABELS = [
    "Semi-Auto", "Full-Auto", "Full-Auto (2-round burst)", "Full-Auto (3-round burst)",
    "Bolt Action", "Pump Action", "Break-Open",
    "Double Action Only", "Double Action Revolver", "Single Shot",
]
OPERATION_VALUES = [
    "@firearm_operation_semiauto_name", "@firearm_operation_fullauto_name",
    "@firearm_operation_fullauto2burst_name", "@firearm_operation_fullauto3burst_name",
    "@firearm_operation_boltaction_name", "@firearm_operation_pumpaction_name",
    "@firearm_operation_breakopen_name", "@firearm_operation_doubleactiononly_name",
    "@firearm_operation_doubleactionrev_name", "@firearm_operation_singleshot_name",
]
OPERATION_LABEL_TO_VALUE = dict(zip(OPERATION_LABELS, OPERATION_VALUES))
OPERATION_VALUE_TO_LABEL = dict(zip(OPERATION_VALUES, OPERATION_LABELS))

CALIBER_TEXTS = [
    "@firearm_caliber_556x45_name",       "@firearm_caliber_762x51_name",
    "@firearm_caliber_762x39_name",       "@firearm_caliber_300BLK_name",
    "@firearm_caliber_300BLKsubsonic_name","@firearm_caliber_65x25_name",
    "@firearm_caliber_6x35_name",         "@firearm_caliber_9x19_name",
    "@firearm_caliber_9x19subsonic_name", "@firearm_caliber_40sw_name",
    "@firearm_caliber_40swsubsonic_name", "@firearm_caliber_45acp_name",
    "@firearm_caliber_46x30_name",        "@firearm_caliber_57x28_name",
    "@firearm_caliber_38special_name",    "@firearm_caliber_357mag_name",
    "@firearm_caliber_44mag_name",        "@firearm_caliber_12gauge_name",
    "@firearm_caliber_bzzzt_name",
]

ATTACK_TYPE_GROUPS = {
    "7.62 Rifle":        ["SWAT_762RapidFire","SWAT_762RapidFireMed","SWAT_762AimedFire","SWAT_762AimedFireXX"],
    "Carbine / Generic": ["SWAT_RapidFire","SWAT_RapidFireMed","SWAT_CarbineAimedFire","SWAT_CarbineAimedFireXX","AimedFire","AimedFireLongXX","RapidFire"],
    "635 PDW":           ["SWAT_635PDWAimedFire","SWAT_635PDWAimedFireXX","SWAT_635PDWAuto","SWAT_635PDWRapidFire","SWAT_635PDWRapidFireMed"],
    "Bren":              ["SWAT_BrenAimedFire","SWAT_BrenAimedFireXX","SWAT_BrenRapidFire","SWAT_BrenRapidFireMed"],
    "HB / Sniper":       ["SWAT_HBAimedFire","SWAT_HBAimedFireXX","SWAT_HBRapidFire","SWAT_SniperFire"],
    "MCX 300":           ["SWAT_MCX300AimedFire","SWAT_MCX300AimedFireXX","SWAT_MCX300RapidFire","SWAT_MCX300RapidFireMed"],
    "MP7":               ["SWAT_MP7AimedFire","SWAT_MP7AimedFireLong","SWAT_MP7AimedFireLongXX","SWAT_MP7FullAuto","SWAT_MP7RapidFire"],
    "SMG (9mm)":         ["SWAT_SMGAimedFire","SWAT_SMGAimedFireLong","SWAT_SMGAimedFireLongXX","SWAT_SMGRapidFire","SWAT_SMG2rdBurst","SWAT_SMG3rdBurst"],
    "SMG (.45)":         ["SWAT_SMG45AimedFire","SWAT_SMG45AimedFireLong","SWAT_SMG45AimedFireLongXX","SWAT_SMG45RapidFire"],
    "Vector":            ["SWAT_VectorAimedFire","SWAT_VectorAimedFireLong","SWAT_VectorAimedFireLongXX","SWAT_VectorRangedBurst","SWAT_Vector2rdBurst"],
    "Pistol":            ["SWAT_PistolAimedFire","SWAT_PistolAimedFireShort","SWAT_PistolAimedFireLong","SWAT_PistolAimedFireLongXX","SWAT_ControlledPair","SWAT_DoubleTap","SWAT_Mozambique","SWAT_MozambiqueLong","SWAT_EmergencyFire"],
    "Shotgun / Pump":    ["SWAT_PumpAimedFire","SWAT_PumpAimedFireLong","SWAT_PumpAimedFireLongXX","SWAT_PumpCloseFire","SWAT_ShortPumpAimedFire","SWAT_ShortPumpAimedFireLong"],
    "AK":                ["AKStrafe","AKStrafeLong","AKStrafeMed"],
    "Operator":          ["Operator_AimedBurst","Operator_AimedBurstLong","Operator_Auto","Operator_Burst"],
    "Wild / Reckless":   ["WildFire","WildBurst","WildBurstLong","WildBurstLongXX"],
    "Tazer":             ["SWAT_Tazer","SWAT_TazerLong"],
}

# ── Sound system ──────────────────────────────────────────────────────────────

NO_RAPID_VARIANT = {
    "1911","686PLUS","BREACHSHOT","FSAP","G17","GLK40","HB","HK45","HK45SD",
    "JCSHOT","KSG","M590","M870CQC","MAG44","MK23","MK23SD","MP40","MP7SD",
    "P226","P226SD","REV38","S12K","SIX12","SIX12SD","SNIPER","SP01","TAZER",
    "TRR8","UMP45SD","VECTORSD","VET","XD4P",
}

SOUND_GROUPS = {
    "Rifles": [
        "AK47","BREN805","G36C","HB","HK416D10","HK416SD","M4","M4CQB",
        "MCX300","Mk16PDW","Mk17LB","OSW","S553C","SNIPER","TV18",
    ],
    "SMGs / PDWs": [
        "EVO3","MAC10","MP40","MP5A3","MP5A3SD","MP5SD","MP7","MP7SD",
        "MP9SD","MPX40","MPXSD40","P90","P90SD","UMP45","UMP45SD","X635",
    ],
    "Pistols": [
        "1911","686PLUS","FSAP","G17","GLK40","HK45","HK45SD","JCSHOT",
        "MAG44","MK23","MK23SD","P226","P226SD","REV38","SP01","TRR8","VET","XD4P",
    ],
    "Shotguns": ["BREACHSHOT","KSG","M590","M870CQC","S12K","SIX12","SIX12SD"],
    "Other":    ["TAZER","VECTOR","VECTORSD"],
}

def build_sound_preset(prefix):
    fs = [f"SFX_{prefix}_FIRE", f"SFX_{prefix}_FIREa"]
    fr = list(fs) if prefix in NO_RAPID_VARIANT else [f"SFX_{prefix}_RAPID_FIRE", f"SFX_{prefix}_RAPID_FIREa"]
    return fs, fr

# ── Shell / reload presets ────────────────────────────────────────────────────

SHELL_DROP_FAMILIES = {
    "Rifle":   ["SFX_RIFLE_SHELL_DROPe","SFX_RIFLE_SHELL_DROPa","SFX_RIFLE_SHELL_DROPb","SFX_RIFLE_SHELL_DROPc"],
    "Pistol":  ["SFX_PISTOL_SHELL_DROPe","SFX_PISTOL_SHELL_DROPf","SFX_PISTOL_SHELL_DROPc","SFX_PISTOL_SHELL_DROPd"],
    "Shotgun": ["SFX_SHOTGUN_SHELL_DROPa","SFX_SHOTGUN_SHELL_DROPb","SFX_SHOTGUN_SHELL_DROPc","SFX_SHOTGUN_SHELL_DROPd"],
    "None":    [],
}
SHELL_DROP_FAMILY_NAMES = list(SHELL_DROP_FAMILIES.keys())

RELOAD_PRESETS = {
    "rifle":   {"reload": "SFX_1911_RELD",  "reload_empty": "SFX_M4_RELDEMPT",   "shell_family": "Rifle"},
    "pistol":  {"reload": "SFX_1911_RELD",  "reload_empty": "SFX_1911_RELDEMPT", "shell_family": "Pistol"},
    "shotgun": {"reload": "SFX_SG870_RELD", "reload_empty": "SFX_SG870_CHARGE",  "shell_family": "Shotgun"},
    "tazer":   {"reload": "SFX_TAZER_RELD", "reload_empty": "SFX_M4_RELDEMPT",   "shell_family": "None"},
}
RELOAD_OPTIONS       = ["SFX_1911_RELD","SFX_SG870_RELD","SFX_REV38_RELD","SFX_MP5SD_RELDEMPT","SFX_TAZER_RELD"]
RELOAD_EMPTY_OPTIONS = ["SFX_M4_RELDEMPT","SFX_1911_RELDEMPT","SFX_MP5SD_RELDEMPT","SFX_SG870_CHARGE"]

BULLET_TRACE = {
    "shotgun": "data/textures/fx/bullet_trace_shotgun.dds",
    "default": "data/textures/fx/bullet_trace.dds",
}

# ── Weapon presets ────────────────────────────────────────────────────────────
# Default value sets offered when the user adds a new weapon.

WEAPON_PRESET_LABELS = ["M4 Carbine (Rifle)", "MP5A3 (SMG)", "G17 (Pistol)", "M590 (Shotgun)"]

WEAPON_PRESETS = {
    "M4 Carbine (Rifle)": {
        "name": "", "category": "rifle", "inventory_binding": "PrimaryWeapon",
        "skin_binding": "rifle", "caliber": "@firearm_caliber_556x45_name",
        "operation": "@firearm_operation_fullauto_name", "description": "",
        "classes": ["Assaulter"], "move_speed": "-14", "turn_speed": "-5",
        "render_image": "", "silenced": False, "closed_bolt": True, "cyclic_reload": False,
        "attack_types": ["SWAT_RapidFire","SWAT_RapidFireMed","SWAT_CarbineAimedFire","SWAT_CarbineAimedFireXX"],
        "fire_single_sounds": ["SFX_M4_FIRE","SFX_M4_FIREa"],
        "fire_rapid_sounds":  ["SFX_M4_RAPID_FIRE","SFX_M4_RAPID_FIREa"],
        "sound_preset": "M4", "reload_sound": "SFX_1911_RELD",
        "reload_empty_sound": "SFX_M4_RELDEMPT", "shell_family": "Rifle",
        "muzzle_drop": "0.95", "num_pellets": "1", "rounds_mag": "25",
        "rounds_sec": "10", "damage": "11", "armor_piercing": "5",
        "spread": "0.1", "shot_sound_meters": "40",
        "reload_time": "2200", "reload_empty_time": "2700",
        "change_in_time": "300", "change_out_time": "80",
        "ready_time": "320", "guard_time": "140",
    },
    "MP5A3 (SMG)": {
        "name": "", "category": "rifle", "inventory_binding": "PrimaryWeapon",
        "skin_binding": "rifle", "caliber": "@firearm_caliber_9x19_name",
        "operation": "@firearm_operation_fullauto_name", "description": "",
        "classes": ["Assaulter"], "move_speed": "-8", "turn_speed": "-3",
        "render_image": "", "silenced": False, "closed_bolt": True, "cyclic_reload": False,
        "attack_types": ["SWAT_SMGAimedFire","SWAT_SMGAimedFireLong","SWAT_SMGRapidFire","SWAT_SMGAimedFireLongXX"],
        "fire_single_sounds": ["SFX_MP5A3_FIRE","SFX_MP5A3_FIREa"],
        "fire_rapid_sounds":  ["SFX_MP5A3_RAPID_FIRE","SFX_MP5A3_RAPID_FIREa"],
        "sound_preset": "MP5A3", "reload_sound": "SFX_1911_RELD",
        "reload_empty_sound": "SFX_M4_RELDEMPT", "shell_family": "Pistol",
        "muzzle_drop": "0.95", "num_pellets": "1", "rounds_mag": "30",
        "rounds_sec": "13", "damage": "9", "armor_piercing": "4",
        "spread": "0.12", "shot_sound_meters": "25",
        "reload_time": "2000", "reload_empty_time": "2500",
        "change_in_time": "280", "change_out_time": "80",
        "ready_time": "300", "guard_time": "120",
    },
    "G17 (Pistol)": {
        "name": "", "category": "pistol", "inventory_binding": "SecondaryWeapon",
        "skin_binding": "pistol", "caliber": "@firearm_caliber_9x19_name",
        "operation": "@firearm_operation_semiauto_name", "description": "",
        "classes": ["Assaulter","Breacher","Pointman","Stealth"],
        "move_speed": "0", "turn_speed": "0",
        "render_image": "", "silenced": False, "closed_bolt": True, "cyclic_reload": False,
        "attack_types": ["SWAT_PistolAimedFire","SWAT_PistolAimedFireShort","SWAT_DoubleTap","SWAT_ControlledPair"],
        "fire_single_sounds": ["SFX_G17_FIRE","SFX_G17_FIREa"],
        "fire_rapid_sounds":  ["SFX_G17_FIRE","SFX_G17_FIREa"],
        "sound_preset": "G17", "reload_sound": "SFX_1911_RELD",
        "reload_empty_sound": "SFX_1911_RELDEMPT", "shell_family": "Pistol",
        "muzzle_drop": "0.95", "num_pellets": "1", "rounds_mag": "17",
        "rounds_sec": "4", "damage": "9", "armor_piercing": "3",
        "spread": "0.18", "shot_sound_meters": "25",
        "reload_time": "1800", "reload_empty_time": "2200",
        "change_in_time": "250", "change_out_time": "60",
        "ready_time": "280", "guard_time": "100",
    },
    "M590 (Shotgun)": {
        "name": "", "category": "shotgun", "inventory_binding": "PrimaryWeapon",
        "skin_binding": "shotgun", "caliber": "@firearm_caliber_12gauge_name",
        "operation": "@firearm_operation_pumpaction_name", "description": "",
        "classes": ["Assaulter","Breacher"], "move_speed": "-16", "turn_speed": "-6",
        "render_image": "", "silenced": False, "closed_bolt": False, "cyclic_reload": True,
        "attack_types": ["SWAT_PumpAimedFire","SWAT_PumpAimedFireLong","SWAT_PumpCloseFire","SWAT_PumpAimedFireLongXX"],
        "fire_single_sounds": ["SFX_M590_FIRE","SFX_M590_FIREa"],
        "fire_rapid_sounds":  ["SFX_M590_FIRE","SFX_M590_FIREa"],
        "sound_preset": "M590", "reload_sound": "SFX_SG870_RELD",
        "reload_empty_sound": "SFX_SG870_CHARGE", "shell_family": "Shotgun",
        "muzzle_drop": "0.5", "num_pellets": "9", "rounds_mag": "6",
        "rounds_sec": "1.4", "damage": "9", "armor_piercing": "3",
        "spread": "2.5", "shot_sound_meters": "50",
        "reload_time": "3500", "reload_empty_time": "4000",
        "change_in_time": "400", "change_out_time": "100",
        "ready_time": "400", "guard_time": "180",
    },
}

# ── Armor ─────────────────────────────────────────────────────────────────────
# Each Armor has three ProtectionArc zones:
#   Front  (degrees=90)  — frontal coverage
#   Sides  (degrees=270) — side / rear coverage
#   Full   (degrees=360) — omnidirectional layer
# Each zone has coveragePercent (0-100) and piercingProtectionLevel (0-7).

PROTECTION_INFO_TEXTS = [
    "@equipment_protect0",
    "@equipment_protect1",
    "@equipment_protect2",
    "@equipment_protect3",
]

# Default values based on Raider Vest (all classes, no mobility penalty)
ARMOR_DEFAULTS = {
    "name": "", "description": "",
    "classes": ["Assaulter","Breacher","Pointman","Shield","Stealth"],
    "move_speed": "0", "turn_speed": "0", "render_image": "",
    "protection_info_text": "@equipment_protect2",
    "protection_arcs": [
        {"degrees": "90",  "coverage": "40",  "piercing": "5"},
        {"degrees": "270", "coverage": "100", "piercing": "0"},
        {"degrees": "360", "coverage": "40",  "piercing": "5"},
    ],
}

# ── Shield ────────────────────────────────────────────────────────────────────
# Shield uses inventoryBinding="SupportGear" and has one ProtectionArc + FieldOfView.

SHIELD_INFO_TEXTS = [
    "@equipment_protect1",
    "@equipment_protect2",
]

# Default values based on Enforcer Shield (Level IIIA)
SHIELD_DEFAULTS = {
    "name": "", "description": "",
    "classes": ["Shield"], "move_speed": "-18", "turn_speed": "-60",
    "render_image": "",
    "protection_info_text": "@equipment_protect1",
    "arc_degrees":    "75",
    "arc_coverage":   "75",
    "arc_piercing":   "4",
    "fov_degrees":    "60",
    "fov_eye_radius": "0.4",
}

# ── Description wrapping ──────────────────────────────────────────────────────

DESC_MAX_LINES  = 10
DESC_LINE_WIDTH = 42
