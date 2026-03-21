# ── publish.py ────────────────────────────────────────────────────────────────
# Steam Workshop publish / update / delete via DoorKickers.exe command-line flags.
# Parses log.txt to confirm success. No tkinter imports.

import os
import subprocess
import threading
import time


# ── Log-file helpers ──────────────────────────────────────────────────────────

def get_documents_folder() -> str:
    """
    Locate the real Windows Documents folder, correctly handling OneDrive
    folder relocation (common on Windows 11).
    """
    try:
        import ctypes
        import ctypes.wintypes
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(0, 5, 0, 0, buf)
        if buf.value:
            return buf.value
    except Exception:
        pass
    for var in ("USERPROFILE", "HOME"):
        base = os.environ.get(var, "")
        if base:
            docs = os.path.join(base, "Documents")
            if os.path.isdir(docs):
                return docs
    return os.path.expanduser("~")


def find_log_path() -> str:
    """Return the expected DoorKickers log.txt path."""
    return os.path.join(get_documents_folder(), "KillHouseGames", "DoorKickers", "log.txt")


# Success tokens matched against the last session block in log.txt
_SUCCESS_TOKENS = {
    "-publish":          "PublishFile OK",
    "-update_published": "UpdateFile OK",
    "-delete_published": "DeleteFile OK",
}


def parse_log_result(log_path: str, action_flag: str) -> tuple[bool, str]:
    """
    Read log.txt and return (success, detail_string).
    Only the most recent game session (after the last 'Entry point.' line) is checked.
    """
    success_token = _SUCCESS_TOKENS.get(action_flag, "OK !")
    try:
        with open(log_path, encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception as e:
        return False, f"Could not read log.txt:\n{e}"

    marker  = "Entry point."
    idx     = content.rfind(marker)
    session = content[idx:] if idx != -1 else content

    if success_token in session:
        return True, success_token

    for line in session.splitlines():
        if "SteamAnswerReceiver" in line and "OK" not in line and line.strip():
            return False, line.strip()

    return False, (
        "No success confirmation found in log.txt. "
        "The operation may have failed or Steam was not running."
    )


# ── Publisher ─────────────────────────────────────────────────────────────────

class Publisher:
    """
    Wraps the DoorKickers.exe publish workflow.

    Usage:
        pub = Publisher(exe_path, mod_folder_path)
        pub.run(flag, on_done_callback)

    *on_done_callback* is called on the main thread with (success: bool, detail: str, label: str).
    The caller is responsible for scheduling the callback back onto the UI thread
    (e.g. via root.after(0, ...)).
    """

    def __init__(self, exe_path: str, mod_folder: str):
        self.exe_path   = exe_path
        self.mod_folder = mod_folder

    def run(self, flag: str, label: str, schedule_fn, on_done) -> None:
        """
        Launch DK.exe in a daemon thread.
        *schedule_fn* — e.g. ``root.after`` — marshals the result back to the UI thread.
        """
        threading.Thread(
            target=self._worker,
            args=(flag, label, schedule_fn, on_done),
            daemon=True,
        ).start()

    def _worker(self, flag: str, label: str, schedule_fn, on_done) -> None:
        try:
            proc = subprocess.Popen(
                [self.exe_path, flag, self.mod_folder],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            proc.wait()
            time.sleep(0.5)   # let DK finish flushing the log
            success, detail = parse_log_result(find_log_path(), flag)
        except Exception as e:
            success, detail = False, str(e)

        schedule_fn(0, lambda: on_done(success, detail, label))
