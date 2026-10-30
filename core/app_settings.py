"""Persistent app settings — JSON file in data/."""

import json
import os

DEFAULTS = {
    "ui_scale": 1.0,
    "language": "en",
    "video_background": True,
    "background_music": True,
}

SCALE_MIN = 0.8
SCALE_MAX = 2.0
SCALE_STEP = 0.1


class AppSettings:
    def __init__(self, path):
        self._path = path
        self._data = dict(DEFAULTS)
        self._load()

    def _load(self):
        if os.path.exists(self._path):
            try:
                with open(self._path, "r") as f:
                    stored = json.load(f)
                self._data.update(stored)
            except (json.JSONDecodeError, OSError):
                pass

    def save(self):
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, "w") as f:
            json.dump(self._data, f, indent=2)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value

    @property
    def ui_scale(self):
        return max(SCALE_MIN, min(SCALE_MAX, float(self._data.get("ui_scale", 1.0))))

    @ui_scale.setter
    def ui_scale(self, value):
        self._data["ui_scale"] = max(SCALE_MIN, min(SCALE_MAX, round(value, 1)))
