"""Deck CRUD — reads repo decks + user custom decks."""

import json
import os
import glob


class DeckManager:
    def __init__(self, repo_decks_dir, user_decks_dir):
        self._repo_dir = repo_decks_dir
        self._user_dir = user_decks_dir
        os.makedirs(self._user_dir, exist_ok=True)

    # --- List games (top-level folders) ---

    def list_games(self):
        games = []
        for d in (self._repo_dir, self._user_dir):
            if not os.path.isdir(d):
                continue
            for name in sorted(os.listdir(d)):
                path = os.path.join(d, name)
                if os.path.isdir(path) and not name.startswith("."):
                    source = "user" if d == self._user_dir else "repo"
                    deck_count = len(self._json_files(path))
                    if deck_count > 0:
                        games.append({
                            "name": name,
                            "path": path,
                            "source": source,
                            "deck_count": deck_count,
                        })
        return games

    def list_decks(self, game_path):
        decks = []
        for path in self._json_files(game_path):
            try:
                deck = self._read(path)
                name = os.path.splitext(os.path.basename(path))[0]
                decks.append({
                    "name": name,
                    "path": path,
                    "main": len(deck.get("main", [])),
                    "extra": len(deck.get("extra", [])),
                    "side": len(deck.get("side", [])),
                    "source": "user" if self._user_dir in path else "repo",
                })
            except (json.JSONDecodeError, OSError):
                continue
        return sorted(decks, key=lambda d: d["name"])

    def read_deck(self, path):
        return self._read(path)

    # --- User deck CRUD ---

    def create_deck(self, game_name, deck_name, deck=None):
        if deck is None:
            deck = {"main": [], "extra": [], "side": []}
        game_dir = os.path.join(self._user_dir, game_name)
        os.makedirs(game_dir, exist_ok=True)
        path = os.path.join(game_dir, f"{deck_name}.json")
        self._write(path, deck)
        return path

    def save_deck(self, path, deck):
        self._write(path, deck)

    def delete_deck(self, path):
        if os.path.exists(path) and self._user_dir in path:
            os.remove(path)
            return True
        return False

    def duplicate_deck(self, src_path, new_name=None):
        deck = self._read(src_path)
        game_dir = os.path.dirname(src_path)
        if new_name is None:
            base = os.path.splitext(os.path.basename(src_path))[0]
            new_name = f"{base} (copy)"
        dest = os.path.join(game_dir, f"{new_name}.json")
        # If dest is in repo dir, copy to user dir instead
        if self._repo_dir in dest:
            game_name = os.path.basename(game_dir)
            return self.create_deck(game_name, new_name, deck)
        self._write(dest, deck)
        return dest

    def create_game(self, game_name):
        path = os.path.join(self._user_dir, game_name)
        os.makedirs(path, exist_ok=True)
        return path

    # --- Internals ---

    def _json_files(self, directory):
        return sorted(glob.glob(glob.escape(directory) + "/*.json"))

    def _read(self, path):
        with open(path) as f:
            return json.load(f)

    def _write(self, path, deck):
        with open(path, "w") as f:
            json.dump(deck, f, indent=2)
            f.write("\n")

    def is_user_deck(self, path):
        return self._user_dir in path
