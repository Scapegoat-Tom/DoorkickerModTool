# ── xml_gen.py ────────────────────────────────────────────────────────────────
# Generates mod.xml, filesystem_mount.xml, and the combined equipment XML.
# No tkinter imports.

from utils import sanitize_filename, mod_name_to_xml_filename, wrap_description
from constants import SHELL_DROP_FAMILIES, BULLET_TRACE


# ── mod.xml ───────────────────────────────────────────────────────────────────

def generate_mod_xml(data: dict) -> str:
    img_basename = sanitize_filename(data["mod_image_file"]) if data["mod_image_file"] else ""
    img_path     = f"gui/customization/mods/{img_basename}" if img_basename else ""
    return (
        '<!--\n'
        '"name" should be a short (and unique) name. Never update it in the Steam Workshop interface.\n'
        '"image" shows up in-game and on Steam Workshop. Should be a 512x512 or 256x256 PNG.\n'
        '"tags" only show up in Steam Workshop. Comma-separated values.\n'
        '"gameVersion" leave as-is.\n'
        '"changeNotes" only used when updating a published mod on Workshop.\n'
        '-->\n'
        f'<Mod\n'
        f'\tname="{data["mod_name"]}"\n'
        f'\tdescription="{data["mod_description"]}"\n'
        f'\timage="{img_path}"\n'
        f'\tauthor="{data["mod_author"]}"\n'
        f'\tgameVersion="1.1.6"\n'
        f'\ttags="{data["mod_tags"]}"\n'
        f'\tchangeNotes="{data["mod_change_notes"]}"\n'
        f'/>\n'
    )


# ── filesystem_mount.xml ──────────────────────────────────────────────────────

def generate_filesystem_mount_xml(data: dict) -> str:
    xml_filename = mod_name_to_xml_filename(data["mod_name"])
    return (
        '<filesystem_mount>\n\t<ObjectLibrary>\n\n'
        '\t\t<!-- equipment/abilities/doctrine need to load before humans -->\n'
        f'\t\t<MountFile name="data/xml/{xml_filename}"/>\n\n'
        '\t</ObjectLibrary>\n\n'
        '\t<Maps>\n\t\t\n\t</Maps>\n\n'
        '\t<RandomMaps>\n\t\t<!-- add more here -->\n\t</RandomMaps>\n\n'
        '\t<Campaigns>\n\t\t<!-- add more here -->\n\t</Campaigns>\n\n'
        '\t<Sounds>\n\t\t\n\t</Sounds>\n\n'
        '\t<GUI>\n\t\t<!-- add more here -->\n\t</GUI>\n\n'
        '\t<Portraits>\n\t\t<!-- add more here -->\n\t</Portraits>\n\n'
        '\t<EditorBrushes>\n\t\t<!-- add more here -->\n\t</EditorBrushes>\n'
        '</filesystem_mount>\n'
    )


# ── Weapon XML ────────────────────────────────────────────────────────────────

def _weapon_block(w: dict) -> str:
    img_basename = sanitize_filename(w["render_image"]) if w.get("render_image") else ""
    texture_path = f"data/gui/customization/items/{img_basename}" if img_basename else ""
    cat          = w.get("category", "rifle")
    bullet_trace = BULLET_TRACE["shotgun"] if cat == "shotgun" else BULLET_TRACE["default"]

    class_lines = "\n".join(f'\t\t<Class value="{c}"/>'           for c in w.get("classes", []))
    at_lines    = "\n".join(f'\t\t\t<AttackType name="{a}"/>'     for a in w.get("attack_types", [])[:4])
    fs_lines    = "\n".join(f'\t\t\t<FireSingle name="{s}"/>'     for s in w.get("fire_single_sounds", []))
    fr_lines    = "\n".join(f'\t\t\t<FireRapid name="{s}"/>'      for s in w.get("fire_rapid_sounds", []))
    sd_drops    = SHELL_DROP_FAMILIES.get(w.get("shell_family", "Rifle"), [])
    sd_lines    = "\n".join(f'\t\t\t<ShellDrop name="{s}"/>'      for s in sd_drops)

    silenced      = "1" if w.get("silenced")      else "0"
    closed_bolt   = "1" if w.get("closed_bolt")   else "0"
    cyclic_reload = "1" if w.get("cyclic_reload")  else "0"
    desc_wrapped, _ = wrap_description(w.get("description", ""))

    return (
        f'\t<Firearm name="{w["name"]}" inventoryBinding="{w["inventory_binding"]}" category="{cat}">\n'
        f'{class_lines}\n'
        f'\t\t<MobilityModifiers moveSpeedLocalModifierPercent="{w["move_speed"]}" turnSpeedLocalModifierPercent="{w["turn_speed"]}"/>\n'
        f'\t\t<RenderObject2D texture="{texture_path}"/>\n'
        f'\t\t<Skin binding="{w["skin_binding"]}"/>\n'
        f'\t\t<Description value="{desc_wrapped}"/>\n'
        f'\t\t<ModifiableParams\n'
        f'\t\t\tmuzzleDropDistanceMeters="{w["muzzle_drop"]}"\n'
        f'\t\t\tnumPellets="{w["num_pellets"]}"\n'
        f'\t\t\troundsPerMagazine="{w["rounds_mag"]}"\n'
        f'\t\t\troundsPerSecond="{w["rounds_sec"]}"\n'
        f'\t\t\tdamagePerBullet="{w["damage"]}"\n'
        f'\t\t\tarmorPiercingLevel="{w["armor_piercing"]}"\n'
        f'\t\t\tspreadAt10Meters="{w["spread"]}"\n'
        f'\t\t\tsilenced="{silenced}"\n'
        f'\t\t\tshotSoundMeters="{w["shot_sound_meters"]}"\n'
        f'\t\t\tclosedBolt="{closed_bolt}"\n\n'
        f'\t\t\tcyclicReload="{cyclic_reload}"\n'
        f'\t\t\treloadTime="{w["reload_time"]}"\n'
        f'\t\t\treloadEmptyTime="{w["reload_empty_time"]}"\n'
        f'\t\t\tchangeInTime="{w["change_in_time"]}"\n'
        f'\t\t\tchangeOutTime="{w["change_out_time"]}"\n'
        f'\t\t\treadyTime="{w["ready_time"]}"\n'
        f'\t\t\tguardTime="{w["guard_time"]}"\n'
        f'\t\t/>\n\n'
        f'\t\t<Params\n'
        f'\t\t\tcaliberInfoText="{w["caliber"]}"\n'
        f'\t\t\toperationInfoText="{w["operation"]}"\n'
        f'\t\t/>\n\n'
        f'\t\t<AttackTypes>\n{at_lines}\n\t\t</AttackTypes>\n\n'
        f'\t\t<MuzzleFlash muzzlePointOffset="28 -6" textureAnimation="ANIM_FX_MUZZLE_FLASH_M4">\n'
        f'\t\t\t<BulletTrace durationMSec="550">\n'
        f'\t\t\t\t<RenderObject2D texture="{bullet_trace}" sizeX="512" sizeY="8" blendMode="add_masked"/>\n'
        f'\t\t\t</BulletTrace>\n'
        f'\t\t\t<Flares>\n'
        f'\t\t\t\t<RenderObject2D texture="data/textures/fx/muzzle_flash_flare1.tga" sizeX="200" sizeY="200" layer="11" blendMode="add"/>\n'
        f'\t\t\t\t<RenderObject2D texture="data/textures/fx/muzzle_flash_flare2.tga" sizeX="200" sizeY="200" layer="11" blendMode="add"/>\n'
        f'\t\t\t\t<RenderObject2D texture="data/textures/fx/muzzle_flash_flare3.tga" sizeX="200" sizeY="200" layer="11" blendMode="add"/>\n'
        f'\t\t\t</Flares>\n'
        f'\t\t</MuzzleFlash>\n\n'
        f'\t\t<Sounds>\n'
        f'\t\t\t<Equip name="SFX_M4_EQUIP"/>\n'
        f'\t\t\t<Unequip name="SFX_M4_UNEQP"/>\n'
        f'\t\t\t<Reload name="{w["reload_sound"]}"/>\n'
        f'\t\t\t<ReloadEmpty name="{w["reload_empty_sound"]}"/>\n'
        f'{fs_lines}\n{fr_lines}\n{sd_lines}\n'
        f'\t\t</Sounds>\n'
        f'\t</Firearm>\n'
    )


# ── Armor XML ─────────────────────────────────────────────────────────────────

def _armor_block(a: dict) -> str:
    img_basename = sanitize_filename(a["render_image"]) if a.get("render_image") else ""
    texture_path = f"data/gui/customization/items/{img_basename}" if img_basename else ""
    class_lines  = "\n".join(f'\t\t<Class value="{c}"/>' for c in a.get("classes", []))
    desc_wrapped, _ = wrap_description(a.get("description", ""))

    arcs = a.get("protection_arcs", [
        {"degrees": "90",  "coverage": "40", "piercing": "5"},
        {"degrees": "270", "coverage": "20", "piercing": "4"},
        {"degrees": "360", "coverage": "40", "piercing": "5"},
    ])
    arc_lines = "\n".join(
        f'\t\t\t<ProtectionArc degrees="{arc["degrees"]}" '
        f'coveragePercent="{arc["coverage"]}" '
        f'piercingProtectionLevel="{arc["piercing"]}"/>'
        for arc in arcs
    )


    return (
        f'\t<Armor name="{a["name"]}" inventoryBinding="Armor">\n'
        f'\t\t<RenderObject2D texture="{texture_path}"/>\n'
        f'\t\t<Skin binding="weaponless"/>\n'
        f'{class_lines}\n'
        f'\t\t<Description value="{desc_wrapped}"/>\n'
        f'\t\t<MobilityModifiers moveSpeedLocalModifierPercent="{a["move_speed"]}" turnSpeedLocalModifierPercent="{a["turn_speed"]}"/>\n'
        f'\t\t<Parameters protectionInfoText="{a["protection_info_text"]}">\n'
        f'{arc_lines}\n'
        f'\t\t</Parameters>\n'
        f'\t</Armor>\n'
    )


# ── Shield XML ────────────────────────────────────────────────────────────────

def _shield_block(s: dict) -> str:
    img_basename = sanitize_filename(s["render_image"]) if s.get("render_image") else ""
    texture_path = f"data/gui/customization/items/{img_basename}" if img_basename else ""
    class_lines  = "\n".join(f'\t\t<Class value="{c}"/>' for c in s.get("classes", []))
    desc_wrapped, _ = wrap_description(s.get("description", ""))

    return (
        f'\t<Shield name="{s["name"]}" inventoryBinding="SupportGear">\n'
        f'\t\t<RenderObject2D texture="{texture_path}"/>\n'
        f'\t\t<Skin binding="weaponless"/>\n'
        f'\t\t<Description value="{desc_wrapped}"/>\n'
        f'{class_lines}\n'
        f'\t\t<MobilityModifiers moveSpeedLocalModifierPercent="{s["move_speed"]}" turnSpeedLocalModifierPercent="{s["turn_speed"]}"/>\n'
        f'\t\t<Parameters protectionInfoText="{s["protection_info_text"]}">\n'
        f'\t\t\t<ProtectionArc degrees="{s["arc_degrees"]}" coveragePercent="{s["arc_coverage"]}" piercingProtectionLevel="{s["arc_piercing"]}"/>\n'
        f'\t\t\t<FieldOfView degrees="{s["fov_degrees"]}" eyeRadiusMeters="{s["fov_eye_radius"]}" rangeMeters="99999"/>\n'
        f'\t\t\t<Indicator_RenderObject texture="data/textures/fx/shield01.tga"/>\n'
        f'\t\t</Parameters>\n'
        f'\t</Shield>\n'
    )


# ── Combined equipment XML ────────────────────────────────────────────────────

def generate_equipment_xml(weapons: list, armors: list, shields: list) -> str:
    """
    Produce the single <Equipment> XML file containing all weapons, armors, and shields.
    Grenades are not yet supported and are silently skipped.
    """
    lines = ["<Equipment>"]
    for w in weapons:
        lines.append(_weapon_block(w))
    for a in armors:
        lines.append(_armor_block(a))
    for s in shields:
        lines.append(_shield_block(s))
    lines.append("</Equipment>")
    return "\n".join(lines)
