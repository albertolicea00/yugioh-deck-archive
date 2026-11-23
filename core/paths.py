"""Where the app reads bundled resources and writes user data.

From source both are the repository root. In a PyInstaller build the bundle is
read-only (and signed), so user data (`data/`, `user_decks/`) goes to the
platform's per-user application data folder instead.
"""

import os
import sys

APP_NAME = "YGO Deck Archive"

# Bundled, read-only resources: assets/, decks/, theme/.
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _user_data_dir():
    if sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    elif sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    return os.path.join(base, APP_NAME)


# Writable user data: data/ (settings, card database, cache) and user_decks/.
USER_DIR = _user_data_dir() if getattr(sys, "frozen", False) else ROOT_DIR
DATA_DIR = os.path.join(USER_DIR, "data")
