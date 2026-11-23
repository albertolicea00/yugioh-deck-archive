# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the desktop app. Run through `make dmg` (macOS).

The version comes from the repository's VERSION file; the Makefile passes it
as VERSION_NAME and VERSION_CODE environment variables. On Windows the same
spec builds the .exe (run PyInstaller there; the BUNDLE step is skipped).
"""

import os
import sys

ROOT = os.path.dirname(SPECPATH)

VERSION_NAME = os.environ.get("VERSION_NAME")
VERSION_CODE = os.environ.get("VERSION_CODE")
if not VERSION_NAME or not VERSION_CODE:
    sys.exit("VERSION_NAME and VERSION_CODE must be set (see the VERSION file)")

APP_NAME = "YGO Deck Archive"
BUNDLE_ID = "com.albertolicea00.yugiohdeckmanager"


def _files(folder, ext=None):
    """(source, destination dir) pairs for every non-hidden file in folder."""
    pairs = []
    for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, folder)):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for name in filenames:
            if name.startswith(".") or (ext and not name.endswith(ext)):
                continue
            src = os.path.join(dirpath, name)
            pairs.append((src, os.path.relpath(dirpath, ROOT)))
    return pairs


# Read-only runtime resources. User data (data/, user_decks/) is written
# outside the bundle (see core/paths.py) and is never bundled.
datas = _files("assets") + _files("decks", ".json")

a = Analysis(
    [os.path.join(ROOT, "main.py")],
    pathex=[ROOT],
    datas=datas,
    hiddenimports=[],
    excludes=["tkinter"],
    noarchive=False,
)
pyz = PYZ(a.pure)

if sys.platform == "win32":
    icon = os.path.join(ROOT, "assets", "icons", "app-icon.ico")
else:
    icon = os.path.join(ROOT, "assets", "icons", "app-icon-macos-1024.png")

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    console=False,
    icon=icon,
)
coll = COLLECT(exe, a.binaries, a.datas, name=APP_NAME)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name=f"{APP_NAME}.app",
        icon=icon,
        bundle_identifier=BUNDLE_ID,
        version=VERSION_NAME,
        info_plist={
            "CFBundleName": APP_NAME,
            "CFBundleDisplayName": APP_NAME,
            "CFBundleShortVersionString": VERSION_NAME,
            "CFBundleVersion": VERSION_CODE,
            "NSHighResolutionCapable": True,
        },
    )
