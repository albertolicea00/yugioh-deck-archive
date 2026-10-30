"""Deck list — decks within a selected game."""

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle

from widgets.stone_button import StoneButton
from widgets.stone_panel import StonePanel
from widgets.list_item import ListItem
from theme import (
    BG_VERTICAL, SCRIM, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_WARNING,
    FONT_SIZE_TITLE, FONT_SIZE_LIST, FONT_SIZE_SMALL, GOLD_DIM,
)


class DeckListScreen(Screen):
    def __init__(self, deck_manager=None, **kwargs):
        super().__init__(name="deck_list", **kwargs)
        self._dm = deck_manager
        self._game = None
        self._build_ui()

    def set_game(self, game):
        self._game = game

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
            size_hint=(0.92, 0.92),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            spacing=8,
        )

        # Header
        header = BoxLayout(size_hint_y=None, height=50, spacing=10)
        back_btn = StoneButton(text="Back", size_hint_x=None, width=100)
        back_btn.bind(on_release=lambda _: setattr(self.manager, "current", "game_list"))
        header.add_widget(back_btn)
        self._title = Label(
            text="Decks", font_size=FONT_SIZE_TITLE, color=TEXT_PRIMARY, bold=True,
        )
        header.add_widget(self._title)
        column.add_widget(header)

        # Deck list
        panel = StonePanel(orientation="vertical", size_hint=(1, 1))
        scroll = ScrollView(do_scroll_x=False)
        self._list = BoxLayout(
            orientation="vertical", size_hint_y=None, spacing=6, padding=[4, 4],
        )
        self._list.bind(minimum_height=self._list.setter("height"))
        scroll.add_widget(self._list)
        panel.add_widget(scroll)
        column.add_widget(panel)

        root.add_widget(column)
        self.add_widget(root)

    def on_enter(self):
        self._refresh()

    def _refresh(self):
        self._list.clear_widgets()
        if self._game is None or self._dm is None:
            return

        self._title.text = self._game["name"]
        decks = self._dm.list_decks(self._game["path"])

        if not decks:
            self._list.add_widget(Label(
                text="No decks in this game.",
                font_size=FONT_SIZE_LIST, color=TEXT_SECONDARY,
                size_hint_y=None, height=60, halign="center",
            ))
            return

        for deck in decks:
            main_c, extra_c, side_c = deck["main"], deck["extra"], deck["side"]
            warning = ""
            if main_c < 40:
                warning = "  [short]"
            elif main_c > 60:
                warning = "  [over]"

            label = f"{deck['name']}  ({main_c}/{extra_c}/{side_c}){warning}"
            item = ListItem(text=label)
            item.bind(on_release=lambda _, d=deck: self._open_deck(d))
            self._list.add_widget(item)

    def _open_deck(self, deck_info):
        view = self.manager.get_screen("deck_view")
        view.set_deck(deck_info)
        self.manager.current = "deck_view"
