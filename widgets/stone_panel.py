"""Dark content panel with sandstone edge — for readable text over temple backgrounds."""

from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.properties import ListProperty, NumericProperty

from theme import DARK_PANEL, DARK_PANEL_EDGE, scaled


class StonePanel(BoxLayout):
    bg_color = ListProperty(list(DARK_PANEL))
    edge_color = ListProperty(list(DARK_PANEL_EDGE))
    corner_radius = NumericProperty(8)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = [scaled(16), scaled(12)]
        self.spacing = scaled(8)
        self.bind(pos=self._draw, size=self._draw)
        self._draw()

    def _draw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(
                pos=self.pos, size=self.size,
                radius=[self.corner_radius],
            )
            Color(*self.edge_color)
            Line(
                rounded_rectangle=[
                    self.x, self.y,
                    self.width, self.height,
                    self.corner_radius,
                ],
                width=1.2,
            )
