"""Main menu — stone slabs over temple background."""

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle

from widgets.stone_button import StoneButton
from theme import (
    BG_VERTICAL, SCRIM, TEXT_PRIMARY, GOLD_DIM,
    FONT_SIZE_TITLE, FONT_SIZE_SMALL, SLAB_MIN_HEIGHT,
)


MENU_ENTRIES = [
    {"id": "games", "label": "My Decks"},
    {"id": "create", "label": "New Deck"},
    {"id": "search", "label": "Card Search"},
    {"id": "import", "label": "Import / Export"},
    {"id": "settings", "label": "Settings"},
]


class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="main_menu", **kwargs)
        root = FloatLayout()

        bg = Image(
            source=BG_VERTICAL,
            fit_mode="fill",
            size_hint=(1, 1),
        )
        root.add_widget(bg)

        # Scrim overlay
        scrim = Widget(size_hint=(1, 1))
        with scrim.canvas:
            Color(*SCRIM)
            self._scrim_rect = Rectangle(pos=scrim.pos, size=scrim.size)
        scrim.bind(
            pos=lambda w, v: setattr(self._scrim_rect, "pos", v),
            size=lambda w, v: setattr(self._scrim_rect, "size", v),
        )
        root.add_widget(scrim)

        # Center column
        column = BoxLayout(
            orientation="vertical",
            size_hint=(0.85, None),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            spacing=12,
            padding=[0, 20],
        )

        # Title
        title = Label(
            text="Yu-Gi-Oh!",
            font_size=FONT_SIZE_TITLE + 8,
            color=TEXT_PRIMARY,
            bold=True,
            size_hint_y=None,
            height=50,
        )
        subtitle = Label(
            text="Deck Manager",
            font_size=FONT_SIZE_TITLE,
            color=GOLD_DIM,
            size_hint_y=None,
            height=36,
        )
        column.add_widget(title)
        column.add_widget(subtitle)
        column.add_widget(Widget(size_hint_y=None, height=20))

        # Menu buttons
        for entry in MENU_ENTRIES:
            btn = StoneButton(
                text=entry["label"],
            )
            btn.bind(on_release=lambda _, eid=entry["id"]: self._navigate(eid))
            column.add_widget(btn)
            column.add_widget(Widget(size_hint_y=None, height=6))

        # Status line
        self._status = Label(
            text="",
            font_size=FONT_SIZE_SMALL,
            color=GOLD_DIM,
            size_hint_y=None,
            height=24,
        )
        column.add_widget(self._status)

        column.height = sum(c.height for c in column.children) + column.spacing * len(column.children)
        root.add_widget(column)
        self.add_widget(root)

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

    def show_message(self, text):
        self._status.text = text
