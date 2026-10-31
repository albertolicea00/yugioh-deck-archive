"""Game list — browse games/platforms as a grid of framed tiles."""

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from widgets.themed_scroll import ThemedScroll
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window

from widgets.game_tile import GameTile
from widgets.breadcrumb_bar import BreadcrumbBar
from theme import (
    scaled,
    BG_VERTICAL, BG_HORIZONTAL, SCRIM, TEXT_SECONDARY,
    FONT_SIZE_LIST,
)

TILE_BASE_RATIO = 0.94


class GameListScreen(Screen):
    def __init__(self, deck_manager=None, **kwargs):
        super().__init__(name="game_list", **kwargs)
        self._dm = deck_manager
        self._games = []
        self._build_ui()

    def _build_ui(self):
        root = FloatLayout()

        self._bg = Image(source=BG_VERTICAL, fit_mode="cover", size_hint=(1, 1))
        root.add_widget(self._bg)

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
            size_hint=(0.94, 0.94),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            spacing=8,
        )

        self._breadcrumb = BreadcrumbBar(height=scaled(40))
        self._breadcrumb.set_crumbs([
            {"label": "Menu", "screen": "main_menu"},
            {"label": "My Decks", "screen": None},
        ])
        self._breadcrumb.bind(on_navigate=self._on_breadcrumb_nav)
        column.add_widget(self._breadcrumb)

        scroll = ThemedScroll(do_scroll_x=False)
        self._grid = GridLayout(
            cols=2,
            size_hint_y=None,
            spacing=scaled(10),
            padding=[scaled(8), scaled(8), scaled(20), scaled(8)],
        )
        self._grid.bind(minimum_height=self._grid.setter("height"))
        scroll.add_widget(self._grid)
        column.add_widget(scroll)

        root.add_widget(column)
        self.add_widget(root)

        Window.bind(size=self._on_resize)

    def on_enter(self):
        self._refresh()

    def _on_resize(self, window, size):
        w, h = size
        self._bg.source = BG_VERTICAL if h >= w else BG_HORIZONTAL
        avail = w * TILE_BASE_RATIO
        min_w = max(550, int(w * 0.20))
        cols = max(1, int(avail / min_w))
        if self._grid.cols != cols:
            self._grid.cols = cols
            if self._games:
                self._rebuild_grid()

    def _refresh(self):
        self._games = []
        self._grid.clear_widgets()
        if self._dm is None:
            return
        self._games = self._dm.list_games()
        if not self._games:
            self._grid.cols = 1
            self._grid.add_widget(Label(
                text="No games found.\nAdd deck files to the decks/ folder.",
                font_size=FONT_SIZE_LIST, color=TEXT_SECONDARY,
                size_hint_y=None, height=scaled(80), halign="center",
            ))
            return

        w = Window.width
        avail = w * TILE_BASE_RATIO
        min_w = max(550, int(w * 0.20))
        self._grid.cols = max(1, int(avail / min_w))
        self._rebuild_grid()

    def _rebuild_grid(self):
        self._grid.clear_widgets()
        for game in self._games:
            tile = GameTile(
                game_name=game["name"],
                deck_count=game["deck_count"],
            )
            tile.bind(on_release=lambda _, g=game: self._open_game(g))
            self._grid.add_widget(tile)

    def _on_breadcrumb_nav(self, _, screen_name):
        self.manager.current = screen_name

    def _open_game(self, game):
        deck_list = self.manager.get_screen("deck_list")
        deck_list.set_game(game)
        self.manager.current = "deck_list"
