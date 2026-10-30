"""YGOPRODeck API client for card images and data."""

import os
import json
import urllib.request

API_BASE = "https://db.ygoprodeck.com/api/v7"
IMAGE_BASE = "https://images.ygoprodeck.com/images/cards_small"


def card_image_url(card_id):
    return f"{IMAGE_BASE}/{card_id}.jpg"


def card_image_url_full(card_id):
    return f"https://images.ygoprodeck.com/images/cards/{card_id}.jpg"


class CardAPI:
    def __init__(self, cache_dir=None):
        self._cache_dir = cache_dir
        self._names_cache = {}
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
            cache_file = os.path.join(cache_dir, "names.json")
            if os.path.exists(cache_file):
                with open(cache_file) as f:
                    self._names_cache = json.load(f)

    def _save_cache(self):
        if self._cache_dir:
            cache_file = os.path.join(self._cache_dir, "names.json")
            with open(cache_file, "w") as f:
                json.dump(self._names_cache, f, indent=1)

    def lookup_name(self, card_id):
        key = str(card_id)
        if key in self._names_cache:
            return self._names_cache[key]
        url = f"{API_BASE}/cardinfo.php?id={card_id}"
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "YGO-Deck-Manager/1.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                if "data" in data and data["data"]:
                    name = data["data"][0]["name"]
                    self._names_cache[key] = name
                    self._save_cache()
                    return name
        except Exception:
            pass
        return key

    def lookup_card(self, card_id):
        url = f"{API_BASE}/cardinfo.php?id={card_id}"
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "YGO-Deck-Manager/1.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                if "data" in data and data["data"]:
                    return data["data"][0]
        except Exception:
            pass
        return None

    def search(self, query, limit=20):
        url = f"{API_BASE}/cardinfo.php?fname={urllib.parse.quote(query)}&num={limit}"
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "YGO-Deck-Manager/1.0"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                return data.get("data", [])
        except Exception:
            return []
