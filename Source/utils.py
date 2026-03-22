# ── utils.py ──────────────────────────────────────────────────────────────────
# Pure-logic helpers. No tkinter imports.

import os
import struct
import json
from constants import DESC_MAX_LINES, DESC_LINE_WIDTH

# ── Settings persistence ──────────────────────────────────────────────────────

# Store settings in %APPDATA%\Roaming\DoorkickerModTool\dmt_settings.json
#
# Folder choice rationale:
#   %APPDATA%      → C:\Users\<name>\AppData\Roaming   ← we use this
#   %LOCALAPPDATA% → C:\Users\<name>\AppData\Local
#   LocalLow                                            ← low-integrity processes only
#
# Roaming is the right home for a small settings JSON: it's machine-independent
# user preferences that could follow a roaming profile, it's always writable by
# the current user (even from a compiled/installed exe), and it matches what
# most desktop tools (VS Code, Notepad++, etc.) use for user config.
# Local would be fine too, but Roaming is the stronger convention for settings.
#
# Note: %APPDATA% already expands to the Roaming sub-folder — it does NOT point
# to the AppData root.  Writing directly to %APPDATA% without a sub-folder would
# litter the Roaming directory, so we always nest under "DoorkickerModTool\".

def _settings_path() -> str:
    # %APPDATA% → Roaming; fall back to home dir on non-Windows / unusual setups
    appdata = os.environ.get("APPDATA") or os.path.expanduser("~")
    folder  = os.path.join(appdata, "DoorkickerModTool")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "dmt_settings.json")

SETTINGS_FILE = _settings_path()


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


# FIX 3: Provide a sensible default output directory — the game's own mods
# folder under Documents.  This mirrors where DoorKickers looks for mods.

def default_output_dir() -> str:
    """
    Return C:\\Users\\<name>\\Documents\\KillHouseGames\\DoorKickers\\mods
    (or the equivalent path resolved via the real Documents folder,
    which may be relocated to OneDrive on Windows 11).
    """
    # Try the shell API first (handles OneDrive folder redirection)
    try:
        import ctypes
        import ctypes.wintypes
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(0, 5, 0, 0, buf)
        if buf.value:
            docs = buf.value
        else:
            raise RuntimeError("empty path")
    except Exception:
        docs = os.path.join(os.path.expanduser("~"), "Documents")

    return os.path.join(docs, "KillHouseGames", "DoorKickers", "mods")


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
