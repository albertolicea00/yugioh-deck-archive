"""Deck viewer — shows cards in a deck with images and validation."""

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from widgets.themed_scroll import ThemedScroll
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
from theme import (
    scaled,
    BG_VERTICAL, SCRIM, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_WARNING, TEXT_SUCCESS,
    FONT_SIZE_TITLE, FONT_SIZE_LIST, FONT_SIZE_DETAIL, GOLD_DIM,
)


class DeckViewScreen(Screen):
    def __init__(self, deck_manager=None, card_db=None, **kwargs):
        super().__init__(name="deck_view", **kwargs)
        self._dm = deck_manager
        self._card_db = card_db
        self._deck_info = None
        self._deck = None
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
            spacing=scaled(6),
        )

        # Header
        header = BoxLayout(size_hint_y=None, height=scaled(50), spacing=scaled(8))
        back_btn = StoneButton(text="Back", size_hint_x=None, width=scaled(90))
        back_btn.bind(on_release=lambda _: setattr(self.manager, "current", "deck_list"))
        header.add_widget(back_btn)
        self._title = Label(
            text="Deck", font_size=FONT_SIZE_TITLE, color=TEXT_PRIMARY, bold=True,
        )
        header.add_widget(self._title)

        edit_btn = StoneButton(text="Edit", size_hint_x=None, width=scaled(90))
        edit_btn.bind(on_release=lambda _: self._edit())
        header.add_widget(edit_btn)
        column.add_widget(header)

        # Validation status
        self._status = Label(
            text="", font_size=FONT_SIZE_DETAIL, color=TEXT_SUCCESS,
            size_hint_y=None, height=scaled(24), halign="left",
        )
        self._status.bind(size=self._status.setter("text_size"))
        column.add_widget(self._status)

        # Tab bar: Main / Extra / Side
        tabs = BoxLayout(size_hint_y=None, height=scaled(40), spacing=scaled(4))
        self._tab_btns = {}
        for tab_name in ["Main", "Extra", "Side"]:
            btn = StoneButton(text=tab_name, font_size=16)
            btn.bind(on_release=lambda _, t=tab_name.lower(): self._show_tab(t))
            tabs.add_widget(btn)
            self._tab_btns[tab_name.lower()] = btn
        column.add_widget(tabs)

        # Card grid
        panel = StonePanel(orientation="vertical", size_hint=(1, 1))
        self._grid = CardGrid(columns=4)
        panel.add_widget(self._grid)
        column.add_widget(panel)

        root.add_widget(column)
        self.add_widget(root)
        self._current_tab = "main"

    def on_enter(self):
        self._load()

    def _load(self):
        if self._deck_info is None or self._dm is None:
            return
        self._title.text = self._deck_info["name"]
        self._deck = self._dm.read_deck(self._deck_info["path"])
        self._validate()
        self._show_tab("main")

    def _validate(self):
        if self._deck is None:
            return
        from core.validation import validate_deck
        issues = validate_deck(self._deck, self._card_db)
        errors = [m for s, m in issues if s == "error"]
        warnings = [m for s, m in issues if s == "warning"]
        if errors:
            self._status.text = f"{len(errors)} error(s)"
            self._status.color = list(TEXT_WARNING)
        elif warnings:
            self._status.text = f"{len(warnings)} warning(s)"
            self._status.color = [0.9, 0.8, 0.4, 1]
        else:
            self._status.text = "Valid deck"
            self._status.color = list(TEXT_SUCCESS)

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
        self._grid.set_cards(display, image_fn=card_image_url)

    def _edit(self):
        if self._deck_info is None:
            return
        editor = self.manager.get_screen("deck_editor")
        editor.set_deck(self._deck_info)
        self.manager.current = "deck_editor"
