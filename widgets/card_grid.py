"""Scrollable grid of card images with selection support."""

from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.properties import ListProperty, NumericProperty, ObjectProperty

from theme import SELECTED_FILL, SELECTED_EDGE, TEXT_PRIMARY, FONT_SIZE_SMALL


class CardCell(ButtonBehavior, BoxLayout):
    card_id = NumericProperty(0)
    on_card_tap = ObjectProperty(None)
    on_card_long = ObjectProperty(None)
    selected = ObjectProperty(False)

    def __init__(self, card_id, image_url="", name="", count=1, **kwargs):
        super().__init__(**kwargs)
        self.card_id = card_id
        self.orientation = "vertical"
        self.size_hint = (None, None)
        self.size = (90, 140)
        self.padding = [2, 2]

        self._img = AsyncImage(
            source=image_url,
            fit_mode="contain",
            size_hint=(1, 1),
        )
        self.add_widget(self._img)

        if count > 1:
            badge = Label(
                text=f"x{count}",
                font_size=FONT_SIZE_SMALL,
                color=TEXT_PRIMARY,
                size_hint=(1, None),
                height=18,
                bold=True,
            )
            self.add_widget(badge)

        self.bind(pos=self._draw, size=self._draw)

    def on_press(self):
        if self.on_card_tap:
            self.on_card_tap(self.card_id)

    def on_long_press(self, *_):
        if self.on_card_long:
            self.on_card_long(self.card_id)

    def _draw(self, *_):
        self.canvas.before.clear()
        if self.selected:
            with self.canvas.before:
                Color(*SELECTED_FILL)
                RoundedRectangle(pos=self.pos, size=self.size, radius=[4])
                Color(*SELECTED_EDGE)
                Line(
                    rounded_rectangle=[
                        self.x, self.y, self.width, self.height, 4,
                    ],
                    width=1.5,
                )


class CardGrid(ScrollView):
    def __init__(self, columns=4, **kwargs):
        super().__init__(**kwargs)
        self.do_scroll_x = False
        self._grid = GridLayout(
            cols=columns,
            spacing=8,
            padding=[8, 8],
            size_hint_y=None,
        )
        self._grid.bind(minimum_height=self._grid.setter("height"))
        super().add_widget(self._grid)
        self._cells = {}

    def set_cards(self, cards, image_fn=None, on_tap=None, on_long=None):
        """cards: list of (card_id, name, count) tuples."""
        self._grid.clear_widgets()
        self._cells.clear()
        for card_id, name, count in cards:
            url = image_fn(card_id) if image_fn else ""
            cell = CardCell(
                card_id=card_id,
                image_url=url,
                name=name,
                count=count,
            )
            cell.on_card_tap = on_tap
            cell.on_card_long = on_long
            self._grid.add_widget(cell)
            self._cells[card_id] = cell

    def highlight(self, card_id, selected=True):
        cell = self._cells.get(card_id)
        if cell:
            cell.selected = selected
            cell._draw()

    def clear_selection(self):
        for cell in self._cells.values():
            cell.selected = False
            cell._draw()
