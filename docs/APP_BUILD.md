# App Build Guide

> How to build the Yu-Gi-Oh! Deck Archive for mobile and desktop

---

## Desktop (macOS / Windows / Linux)

Desktop runs directly with Python — no build step required.

```bash
python main.py
```

### Packaging as Standalone Executable

Use PyInstaller to create a distributable binary:

```bash
pip install pyinstaller

pyinstaller --onefile --windowed \
  --name "YGO Deck Archive" \
  --icon assets/icons/app-icon.ico \
  --add-data "assets:assets" \
  --add-data "theme:theme" \
  main.py
```

The binary will be in `dist/`.

---

## Android

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

The APK will be in `bin/`.

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
