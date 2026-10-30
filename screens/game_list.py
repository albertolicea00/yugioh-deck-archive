"""Game list — browse games/platforms that contain decks."""

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
    BG_VERTICAL, SCRIM, TEXT_PRIMARY, TEXT_SECONDARY, GOLD_DIM,
    FONT_SIZE_TITLE, FONT_SIZE_LIST, FONT_SIZE_SMALL,
)


class GameListScreen(Screen):
    def __init__(self, deck_manager=None, **kwargs):
        super().__init__(name="game_list", **kwargs)
        self._dm = deck_manager
        self._build_ui()

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
        back_btn.bind(on_release=lambda _: setattr(self.manager, "current", "main_menu"))
        header.add_widget(back_btn)
        header.add_widget(Label(
            text="Games", font_size=FONT_SIZE_TITLE, color=TEXT_PRIMARY, bold=True,
        ))
        column.add_widget(header)

        # Scrollable game list
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
        if self._dm is None:
            return
        games = self._dm.list_games()
        if not games:
            self._list.add_widget(Label(
                text="No games found.\nAdd deck files to the decks/ folder.",
                font_size=FONT_SIZE_LIST, color=TEXT_SECONDARY,
                size_hint_y=None, height=80, halign="center",
            ))
            return

        for game in games:
            item = ListItem(
                text=f"{game['name']}  ({game['deck_count']} decks)",
            )
            item.bind(on_release=lambda _, g=game: self._open_game(g))
            self._list.add_widget(item)

    def _open_game(self, game):
        deck_list = self.manager.get_screen("deck_list")
        deck_list.set_game(game)
        self.manager.current = "deck_list"
