"""Main menu — stone slabs over temple background."""

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

from kivy.core.window import Window

from widgets.stone_button import StoneButton
from theme import (
    BG_VERTICAL, BG_HORIZONTAL, SCRIM, TEXT_PRIMARY, GOLD_DIM,
    FONT_SIZE_TITLE, FONT_SIZE_SMALL, SLAB_MIN_HEIGHT,
    menu_font,
)


MENU_ENTRIES = [
    {"id": "games", "label": "My Decks"},
    {"id": "create", "label": "New Deck"},
    {"id": "search", "label": "Card Search"},
    {"id": "import", "label": "Import / Export"},
    {"id": "settings", "label": "Settings"},
]

MAX_COLUMN_WIDTH = 520


class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="main_menu", **kwargs)
        root = FloatLayout()

        self._bg = Image(
            source=BG_VERTICAL,
            fit_mode="cover",
            size_hint=(1, 1),
        )
        root.add_widget(self._bg)
        Window.bind(size=self._on_window_resize)

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
            size_hint=(None, None),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            spacing=10,
            padding=[0, 20],
        )

        face = menu_font()

        title = Label(
            text="Yu-Gi-Oh!",
            font_size=FONT_SIZE_TITLE + 18,
            color=TEXT_PRIMARY,
            bold=not face,
            size_hint_y=None,
            height=60,
        )
        if face:
            title.font_name = face

        subtitle = Label(
            text="Deck Manager",
            font_size=FONT_SIZE_TITLE,
            color=GOLD_DIM,
            bold=not face,
            size_hint_y=None,
            height=36,
        )
        if face:
            subtitle.font_name = face

        column.add_widget(title)
        column.add_widget(subtitle)
        column.add_widget(Widget(size_hint_y=None, height=16))

        for entry in MENU_ENTRIES:
            btn = StoneButton(
                text=entry["label"],
            )
            btn.bind(on_release=lambda _, eid=entry["id"]: self._navigate(eid))
            column.add_widget(btn)

        self._status = Label(
            text="",
            font_size=FONT_SIZE_SMALL,
            color=GOLD_DIM,
            size_hint_y=None,
            height=56,
        )
        if face:
            self._status.font_name = face
        column.add_widget(self._status)

        column.height = sum(c.height for c in column.children) + column.spacing * len(column.children)
        column.width = MAX_COLUMN_WIDTH
        column.bind(parent=self._clamp_width)
        root.bind(size=lambda *_: self._clamp_width())

        root.add_widget(column)
        self._column = column
        self.add_widget(root)

    def _clamp_width(self, *_):
        if not hasattr(self, "_column") or not self._column.parent:
            return
        parent_w = self._column.parent.width
        self._column.width = min(MAX_COLUMN_WIDTH, parent_w * 0.85)

    def _navigate(self, destination):
        if destination == "games":
            self.manager.current = "game_list"
        elif destination == "create":
            self.manager.current = "deck_editor"
        elif destination == "search":
            self.manager.current = "card_search"
        elif destination == "import":
            self.manager.current = "import_export"
        elif destination == "settings":
            self._status.text = "Settings — coming soon"

    def _on_window_resize(self, window, size):
        w, h = size
        portrait = h >= w
        self._bg.source = BG_VERTICAL if portrait else BG_HORIZONTAL

    def show_message(self, text):
        self._status.text = text
