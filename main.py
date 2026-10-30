"""Yu-Gi-Oh! Deck Manager — Kivy app entry point."""

import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

REPO_DECKS_DIR = os.path.join(ROOT_DIR, "decks")
USER_DECKS_DIR = os.path.join(ROOT_DIR, "user_decks")
CARD_DB_PATH = os.path.join(ROOT_DIR, "data", "cards.cdb")
CACHE_DIR = os.path.join(ROOT_DIR, "data", "cache")

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window

from screens.main_menu import MainMenuScreen
from screens.game_list import GameListScreen
from screens.deck_list import DeckListScreen
from screens.deck_view import DeckViewScreen
from screens.deck_editor import DeckEditorScreen
from screens.card_search import CardSearchScreen
from screens.import_export import ImportExportScreen
from screens.settings import SettingsScreen
from core.deck_manager import DeckManager
from core.card_db import CardDB
from core.app_settings import AppSettings


class DeckManagerApp(App):
    title = "Yu-Gi-Oh! Deck Manager"

    def build(self):
        Window.clearcolor = (0.06, 0.04, 0.03, 1)

        settings_path = os.path.join(ROOT_DIR, "data", "settings.json")
        self._app_settings = AppSettings(settings_path)

        from kivy.metrics import Metrics
        Metrics.density = self._app_settings.ui_scale

        self._dm = DeckManager(REPO_DECKS_DIR, USER_DECKS_DIR)

        self._card_db = None
        if os.path.exists(CARD_DB_PATH):
            try:
                self._card_db = CardDB(CARD_DB_PATH)
            except Exception as e:
                print(f"Warning: Could not load card database: {e}")

        sm = ScreenManager(transition=FadeTransition(duration=0.2))

        sm.add_widget(MainMenuScreen(app_settings=self._app_settings))
        sm.add_widget(GameListScreen(deck_manager=self._dm))
        sm.add_widget(DeckListScreen(deck_manager=self._dm))
        sm.add_widget(DeckViewScreen(deck_manager=self._dm, card_db=self._card_db))
        sm.add_widget(DeckEditorScreen(deck_manager=self._dm, card_db=self._card_db))
        sm.add_widget(CardSearchScreen(card_db=self._card_db))
        sm.add_widget(ImportExportScreen(deck_manager=self._dm, card_db=self._card_db))
        sm.add_widget(SettingsScreen(app_settings=self._app_settings))

        return sm

    def on_stop(self):
        if self._card_db:
            self._card_db.close()


if __name__ == "__main__":
    DeckManagerApp().run()
