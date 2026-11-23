.PHONY: run install db-en db-es convert validate icons clean lint version app dmg

PYTHON ?= python
PIP ?= pip

# Version source: VERSION holds VERSION_NAME (e.g. 0.1.0) and VERSION_CODE
# (an integer bumped on every release). `make version` checks both.
-include VERSION

APP_NAME := YGO Deck Archive
BUILD_VENV := .venv-build
BUILD_PY := $(BUILD_VENV)/bin/python
BUILD_STAMP := $(BUILD_VENV)/.installed
MAC_BUILD := build/macos
APP_BUNDLE := $(MAC_BUILD)/dist/$(APP_NAME).app
DMG := dist/yugioh-deck-manager-v$(VERSION_NAME)-$(VERSION_CODE)-release.dmg

run:
	$(PYTHON) main.py

install:
	$(PIP) install -r requirements.txt

db-en:
	mkdir -p data
	curl -L -o data/cards.cdb \
		"https://raw.githubusercontent.com/ryoken08/CDBEsp/master/cards.cdb"

convert:
	$(PYTHON) scripts/deck-convert.py

validate:
	$(PYTHON) scripts/deck-validate.py

icons:
	$(PYTHON) scripts/generate-icons.py

lint:
	$(PYTHON) -m py_compile main.py
	$(PYTHON) -m py_compile theme/__init__.py
	find core screens widgets -name '*.py' -exec $(PYTHON) -m py_compile {} +

version:
	@test -f VERSION || { echo "VERSION file missing at the repository root"; exit 1; }
	@test -n "$(VERSION_NAME)" || { echo "VERSION_NAME missing in VERSION"; exit 1; }
	@test -n "$(VERSION_CODE)" || { echo "VERSION_CODE missing in VERSION"; exit 1; }
	@echo "$(VERSION_NAME) ($(VERSION_CODE))"

# Project-local build environment with PyInstaller and the app requirements.
$(BUILD_STAMP): requirements.txt
	$(PYTHON) -m venv $(BUILD_VENV)
	$(BUILD_PY) -m pip install --upgrade pip
	$(BUILD_PY) -m pip install pyinstaller -r requirements.txt
	touch $(BUILD_STAMP)

# macOS .app bundle, ad-hoc signed (no Developer ID, not notarized).
app: version $(BUILD_STAMP)
	@test "$$(uname)" = Darwin || { echo "make app/dmg only runs on macOS"; exit 1; }
	KIVY_LOG_MODE=PYTHON VERSION_NAME=$(VERSION_NAME) VERSION_CODE=$(VERSION_CODE) \
		$(BUILD_PY) -m PyInstaller --noconfirm --clean \
		--distpath $(MAC_BUILD)/dist --workpath $(MAC_BUILD)/work \
		packaging/yugioh-deck-manager.spec
	codesign --force --deep -s - "$(APP_BUNDLE)"
	codesign --verify --deep --strict "$(APP_BUNDLE)"

# Disk image with the .app and an /Applications shortcut.
dmg: app
	rm -rf $(MAC_BUILD)/dmg
	mkdir -p $(MAC_BUILD)/dmg dist
	cp -R "$(APP_BUNDLE)" $(MAC_BUILD)/dmg/
	ln -s /Applications $(MAC_BUILD)/dmg/Applications
	hdiutil create -volname "$(APP_NAME) $(VERSION_NAME)" \
		-srcfolder $(MAC_BUILD)/dmg -ov -format UDZO "$(DMG)"
	hdiutil verify "$(DMG)"
	@echo "Built $(DMG)"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name '*.pyc' -delete
	rm -rf build dist *.spec .kivy
