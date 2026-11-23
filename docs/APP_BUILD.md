# App Build Guide

> How to build the Yu-Gi-Oh! Deck Archive for mobile and desktop

---

## Desktop (macOS / Windows / Linux)

Desktop runs directly with Python — no build step required to develop.

```bash
python main.py
```

### Version

`VERSION` at the repository root is the single version source:

```
VERSION_NAME=0.1.0
VERSION_CODE=1
```

`VERSION_NAME` is the user-facing version; `VERSION_CODE` is an integer bumped on every release. `make version` prints both and stops if the file or either value is missing; every build target runs it first.

### macOS disk image

```bash
make dmg
```

This produces `dist/yugioh-deck-manager-v<VERSION_NAME>-<VERSION_CODE>-release.dmg` containing `YGO Deck Archive.app` and an `/Applications` shortcut. Steps:

1. Creates `.venv-build/` (git-ignored) with PyInstaller and `requirements.txt`, using `$(PYTHON)`. That Python must be built with a shared library (pyenv and Homebrew builds are).
2. Builds the `.app` from `packaging/yugioh-deck-manager.spec` into `build/macos/` (`make app` stops here). Bundle id `com.albertolicea00.yugiohdeckmanager`; `CFBundleShortVersionString` is `VERSION_NAME` and `CFBundleVersion` is `VERSION_CODE`. The icon is `assets/icons/app-icon-macos-1024.png`.
3. Signs the bundle **ad-hoc** (`codesign --force --deep -s -`). There is no Apple Developer ID, so the app is not notarized.
4. Creates the image with `hdiutil create ... -format UDZO` and checks it with `hdiutil verify`.

Bundled resources: `assets/` and the `decks/**/*.json` files. When the app runs from the bundle it writes user data (`data/` with settings and the card database, and `user_decks/`) to `~/Library/Application Support/YGO Deck Archive/` instead of next to the code (see `core/paths.py`). Running from source is unchanged.

**First launch (Gatekeeper):** because the app is only ad-hoc signed, macOS blocks a double-click on a downloaded copy. Right-click the app → **Open**, then confirm; or allow it in System Settings → Privacy & Security. Later launches open normally.

### Windows

Not built by the Makefile. The `.exe` must be built on Windows with the same spec (it uses `assets/icons/app-icon.ico` and skips the macOS bundle step):

```bat
set VERSION_NAME=0.1.0
set VERSION_CODE=1
pyinstaller --noconfirm packaging/yugioh-deck-manager.spec
```

Linux packages are not provided.

---

## Android

> **Status: not set up.** The repository has no `buildozer.spec`, no `make` target for Android, no version or version code source, and no release signing. Nothing here has produced an APK. `keys/release.properties` is git-ignored but nothing reads it. The steps below are a starting point for setting Buildozer up, not a working build.
>
> When an Android build is added, name its outputs `yugioh-deck-manager-v<version>-<versionCode>-<debug|release>.apk` (and `.aab`), taking both numbers from a single version source, and document the real signing mechanism here.

### Prerequisites

- Linux or macOS (Buildozer does not work on Windows natively)
- Java JDK 17
- Android SDK + NDK (Buildozer downloads these automatically)

### Setup Buildozer

```bash
pip install buildozer
pip install cython

buildozer init
```

### Configure `buildozer.spec`

Key settings to update in the generated `buildozer.spec`:

```ini
[app]
title = YGO Deck Archive
package.name = ygodeckmanager
package.domain = com.yugioh
source.dir = .
source.include_exts = py,png,jpg,jpeg,json,cdb
version = 0.1.0

requirements = python3,kivy,pillow,requests,sqlite3

# Android permissions
android.permissions = INTERNET

# Orientation
orientation = portrait

# Icon
icon.filename = assets/icons/app-icon.png

# Presplash
presplash.filename = assets/backgrounds/background-menu-v.jpeg
```

### Build APK

```bash
buildozer -v android debug
```

First build downloads SDK/NDK (~2GB). Subsequent builds are faster.

Buildozer writes the APK to `bin/` with its own default name (`<package.name>-<version>-<arch>-debug.apk`).

### Deploy to Device

```bash
buildozer android deploy run logcat
```

---

## iOS

### Prerequisites

- macOS with Xcode
- Apple Developer account ($99/year)
- kivy-ios toolchain

### Setup

```bash
pip install kivy-ios
toolchain build python3 kivy pillow

toolchain create YGO-Deck-Manager .
```

### Build and Run

Open the generated Xcode project and build to a device or simulator.

---

## Notes

- Card database (`cards.cdb`) is NOT bundled — users supply it
- Card images are fetched at runtime from YGOPRODeck API
- Assets from `assets/` folder are bundled with the app
- `user_decks/` on mobile uses the app's writable storage directory
