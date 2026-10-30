"""Deck editor — add/remove cards, create new decks, validate against TCG rules."""

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

from widgets.stone_button import StoneButton
from widgets.stone_panel import StonePanel
from widgets.card_grid import CardGrid
from core.card_api import card_image_url
from core.formats import count_unique
from core.validation import validate_deck, is_extra_deck_card
from theme import (
    BG_VERTICAL, SCRIM, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_WARNING, TEXT_SUCCESS,
    FONT_SIZE_TITLE, FONT_SIZE_LIST, FONT_SIZE_DETAIL, FONT_SIZE_SMALL,
    GOLD_DIM, DARK_PANEL, MAX_COPIES,
)


class DeckEditorScreen(Screen):
    def __init__(self, deck_manager=None, card_db=None, **kwargs):
        super().__init__(name="deck_editor", **kwargs)
        self._dm = deck_manager
        self._card_db = card_db
        self._deck_info = None
        self._deck = None
        self._current_tab = "main"
        self._search_results = []
        self._build_ui()

    def set_deck(self, deck_info):
        self._deck_info = deck_info

    def _build_ui(self):
        root = FloatLayout()

        bg = Image(source=BG_VERTICAL, fit_mode="cover", size_hint=(1, 1))
        root.add_widget(bg)

        scrim = Widget(size_hint=(1, 1))
        with scrim.canvas:
            Color(*SCRIM)
            self._scrim_rect = Rectangle(pos=scrim.pos, size=scrim.size)
        scrim.bind(
            pos=lambda w, v: setattr(self._scrim_rect, "pos", v),
            size=lambda w, v: setattr(self._scrim_rect, "size", v),
        )
        root.add_widget(scrim)

        column = BoxLayout(
            orientation="vertical",
            size_hint=(0.95, 0.95),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            spacing=4,
        )

        # Header
        header = BoxLayout(size_hint_y=None, height=44, spacing=6)
        back_btn = StoneButton(text="Back", size_hint_x=None, width=80)
        back_btn.bind(on_release=lambda _: self._go_back())
        header.add_widget(back_btn)
        self._title = Label(
            text="New Deck", font_size=FONT_SIZE_TITLE - 2, color=TEXT_PRIMARY, bold=True,
        )
        header.add_widget(self._title)
        save_btn = StoneButton(text="Save", size_hint_x=None, width=80)
        save_btn.bind(on_release=lambda _: self._save())
        header.add_widget(save_btn)
        column.add_widget(header)

        # Validation line
        self._status = Label(
            text="", font_size=FONT_SIZE_SMALL, color=TEXT_SUCCESS,
            size_hint_y=None, height=20, halign="left",
        )
        self._status.bind(size=self._status.setter("text_size"))
        column.add_widget(self._status)

        # Tabs
        tabs = BoxLayout(size_hint_y=None, height=36, spacing=4)
        for tab_name in ["Main", "Extra", "Side"]:
            btn = StoneButton(text=tab_name, font_size=14)
            btn.bind(on_release=lambda _, t=tab_name.lower(): self._show_tab(t))
            tabs.add_widget(btn)
        column.add_widget(tabs)

        # Deck cards grid (top half)
        deck_panel = StonePanel(orientation="vertical", size_hint=(1, 0.45))
        self._deck_grid = CardGrid(columns=5)
        deck_panel.add_widget(self._deck_grid)
        column.add_widget(deck_panel)

        # Search bar
        search_row = BoxLayout(size_hint_y=None, height=40, spacing=6)
        self._search_input = TextInput(
            hint_text="Search cards...",
            multiline=False,
            size_hint=(1, 1),
            background_color=list(DARK_PANEL),
            foreground_color=list(TEXT_PRIMARY),
            cursor_color=list(TEXT_PRIMARY),
        )
        self._search_input.bind(on_text_validate=lambda _: self._do_search())
        search_row.add_widget(self._search_input)
        search_btn = StoneButton(text="Search", size_hint_x=None, width=90)
        search_btn.bind(on_release=lambda _: self._do_search())
        search_row.add_widget(search_btn)
        column.add_widget(search_row)

        # Search results grid (bottom half)
        results_panel = StonePanel(orientation="vertical", size_hint=(1, 0.35))
        self._results_grid = CardGrid(columns=5)
        results_panel.add_widget(self._results_grid)
        column.add_widget(results_panel)

        root.add_widget(column)
        self.add_widget(root)

    def on_enter(self):
        if self._deck_info:
            self._title.text = self._deck_info["name"]
            self._deck = self._dm.read_deck(self._deck_info["path"])
        else:
            self._title.text = "New Deck"
            self._deck = {"main": [], "extra": [], "side": []}
        self._refresh()

    def _refresh(self):
        self._show_tab(self._current_tab)
        self._update_status()

    def _show_tab(self, tab):
        self._current_tab = tab
        if self._deck is None:
            return
        cards = self._deck.get(tab, [])
        unique = count_unique(cards)

        def name_fn(cid):
            if self._card_db:
                return self._card_db.get_name(cid)
            return str(cid)

        display = [(cid, name_fn(cid), n) for cid, n in unique]
        self._deck_grid.set_cards(
            display, image_fn=card_image_url,
            on_tap=self._remove_card, on_long=self._remove_card,
        )

    def _do_search(self):
        query = self._search_input.text.strip()
        if not query or not self._card_db:
            return
        results = self._card_db.search(query, limit=40)
        display = [(r["id"], r["name"], 0) for r in results]
        self._results_grid.set_cards(
            display, image_fn=card_image_url,
            on_tap=self._add_card,
        )

    def _add_card(self, card_id):
        if self._deck is None:
            return

        all_cards = self._deck["main"] + self._deck["extra"] + self._deck["side"]
        current_count = all_cards.count(card_id)
        if current_count >= MAX_COPIES:
            self._status.text = f"Already have {MAX_COPIES} copies"
            self._status.color = list(TEXT_WARNING)
            return

        # Auto-place in correct zone
        if self._card_db:
            card = self._card_db.get_card(card_id)
            if card and is_extra_deck_card(card["type"]):
                self._deck["extra"].append(card_id)
                if self._current_tab != "extra":
                    self._current_tab = "extra"
            else:
                self._deck[self._current_tab].append(card_id)
        else:
            self._deck[self._current_tab].append(card_id)

        self._refresh()

    def _remove_card(self, card_id):
        if self._deck is None:
            return
        cards = self._deck.get(self._current_tab, [])
        if card_id in cards:
            cards.remove(card_id)
        self._refresh()

    def _update_status(self):
        if self._deck is None:
            return
        issues = validate_deck(self._deck, self._card_db)
        m = len(self._deck.get("main", []))
        e = len(self._deck.get("extra", []))
        s = len(self._deck.get("side", []))
        errors = sum(1 for sev, _ in issues if sev == "error")
        base = f"Main: {m}  Extra: {e}  Side: {s}"
        if errors:
            self._status.text = f"{base}  — {errors} error(s)"
            self._status.color = list(TEXT_WARNING)
        else:
            self._status.text = f"{base}  — Valid"
            self._status.color = list(TEXT_SUCCESS)

    def _save(self):
        if self._deck is None or self._dm is None:
            return
        if self._deck_info:
            if self._dm.is_user_deck(self._deck_info["path"]):
                self._dm.save_deck(self._deck_info["path"], self._deck)
                self._status.text = "Saved!"
            else:
                path = self._dm.duplicate_deck(self._deck_info["path"])
                self._deck_info["path"] = path
                self._status.text = "Saved as copy (repo decks are read-only)"
        else:
            path = self._dm.create_deck("Custom", "New Deck", self._deck)
            self._deck_info = {"name": "New Deck", "path": path}
            self._status.text = "Created!"
        self._status.color = list(TEXT_SUCCESS)

    def _go_back(self):
        self._deck_info = None
        self._deck = None
        self.manager.current = "deck_view" if self._deck_info else "main_menu"
