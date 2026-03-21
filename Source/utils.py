# ── utils.py ──────────────────────────────────────────────────────────────────
# Pure-logic helpers. No tkinter imports.

import os
import struct
import json
from constants import DESC_MAX_LINES, DESC_LINE_WIDTH

# ── Settings persistence ──────────────────────────────────────────────────────

# Saved next to the script so it's easy to find, not buried in AppData.
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dmt_settings.json")

def load_settings() -> dict:
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_settings(s: dict) -> None:
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(s, f, indent=2)
    except Exception:
        pass

# ── File / name helpers ───────────────────────────────────────────────────────

def sanitize_filename(path: str) -> str:
    """Return a filesystem-safe basename: spaces → underscores, extension preserved."""
    base, ext = os.path.splitext(os.path.basename(path))
    return base.replace(" ", "_") + ext

def mod_name_to_xml_filename(mod_name: str) -> str:
    return mod_name.strip().replace(" ", "_") + ".xml"

# ── Image validation ──────────────────────────────────────────────────────────

def get_image_size(path: str):
    """
    Return (width, height) for PNG or TGA files, or None on failure.
    Reads only the header bytes — does not load the full image.
    """
    try:
        ext = os.path.splitext(path)[1].lower()
        with open(path, "rb") as f:
            if ext == ".png":
                if f.read(8) != b"\x89PNG\r\n\x1a\n":
                    return None
                f.read(8)                                # skip length + "IHDR"
                return struct.unpack(">II", f.read(8))   # width, height
            elif ext == ".tga":
                f.seek(12)
                return struct.unpack("<HH", f.read(4))   # width, height
    except Exception:
        pass
    return None

# ── Description word-wrap ─────────────────────────────────────────────────────

def wrap_description(text: str) -> tuple[str, int]:
    """
    Word-wrap *text* to DESC_LINE_WIDTH chars per line.
    Returns (escaped_string, line_count) where newlines are encoded as \\n
    for embedding directly in XML attribute values.
    """
    if not text.strip():
        return "", 0
    words = text.split()
    lines, current = [], ""
    for word in words:
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= DESC_LINE_WIDTH:
            current += " " + word
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return "\\n".join(lines), len(lines)
