"""Egyptian temple theme — colors, fonts, paths, scaled sizes."""

import json
import os

from kivy.metrics import sp, dp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")

BG_VERTICAL = os.path.join(ASSETS_DIR, "backgrounds", "background-menu-v.jpeg")
BG_HORIZONTAL = os.path.join(ASSETS_DIR, "backgrounds", "background-menu-h.jpeg")
FRAME_RESTING = os.path.join(ASSETS_DIR, "frames", "frame-menu.png")
FRAME_ACTIVE = os.path.join(ASSETS_DIR, "frames", "frame-menu-active.png")

VIDEO_VERTICAL = os.path.join(ASSETS_DIR, "videos", "background-menu-v-pingpong.mp4")
VIDEO_HORIZONTAL = os.path.join(ASSETS_DIR, "videos", "background-menu-h-pingpong.mp4")
MENU_BGM = os.path.join(ASSETS_DIR, "sounds", "menu-bgm.mp3")
PAPYRUS_PATH = "/System/Library/Fonts/Supplemental/Papyrus.ttc"

# UI scale factor — loaded once at import from settings file
_SETTINGS_PATH = os.path.join(ROOT_DIR, "data", "settings.json")
_UI_SCALE = 1.0
if os.path.exists(_SETTINGS_PATH):
    try:
        with open(_SETTINGS_PATH) as _f:
            _UI_SCALE = max(0.8, min(2.0, float(json.load(_f).get("ui_scale", 1.0))))
    except (json.JSONDecodeError, OSError, ValueError):
        pass


def scaled(value):
    return int(value * _UI_SCALE)


def menu_font():
    if os.path.exists(PAPYRUS_PATH):
        return PAPYRUS_PATH
    return ""


# Colors (RGBA 0-1)
GOLD = (0.957, 0.902, 0.776, 1)
GOLD_LIGHT = (0.957, 0.918, 0.827, 1)
GOLD_DIM = (0.745, 0.612, 0.329, 1)
SANDSTONE = (0.886, 0.843, 0.741, 1)
DARK_PANEL = (0.08, 0.06, 0.04, 0.92)
DARK_PANEL_EDGE = (0.31, 0.24, 0.12, 1)
SELECTED_FILL = (0.31, 0.24, 0.12, 0.9)
SELECTED_EDGE = (0.745, 0.612, 0.329, 1)
SCRIM = (0, 0, 0, 0.35)
TEXT_PRIMARY = (0.957, 0.902, 0.776, 1)
TEXT_SECONDARY = (0.886, 0.843, 0.741, 1)
TEXT_WARNING = (0.867, 0.533, 0.533, 1)
TEXT_SUCCESS = (0.533, 0.867, 0.533, 1)
BG_DARK = (0.06, 0.04, 0.03, 1)

FONT_SIZE_TITLE = scaled(28)
FONT_SIZE_BUTTON = scaled(30)
FONT_SIZE_LIST = scaled(18)
FONT_SIZE_DETAIL = scaled(16)
FONT_SIZE_SMALL = scaled(14)

SLAB_MIN_HEIGHT = scaled(88)
SLAB_PADDING = (scaled(20), scaled(12))

# TCG deck limits
MAIN_MIN = 40
MAIN_MAX = 60
EXTRA_MAX = 15
SIDE_MAX = 15
MAX_COPIES = 3

# Card type flags (from EDOPro cards.cdb `datas.type` bitmask)
TYPE_MONSTER = 0x1
TYPE_SPELL = 0x2
TYPE_TRAP = 0x4
TYPE_FUSION = 0x40
TYPE_RITUAL = 0x80
TYPE_SYNCHRO = 0x2000
TYPE_XYZ = 0x800000
TYPE_PENDULUM = 0x1000000
TYPE_LINK = 0x4000000
TYPE_TOKEN = 0x4000

EXTRA_TYPES = TYPE_FUSION | TYPE_SYNCHRO | TYPE_XYZ | TYPE_LINK
