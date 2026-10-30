"""Lightweight list row — for scrollable lists inside panels."""

from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.graphics import Color, RoundedRectangle

from theme import (
    TEXT_PRIMARY, SELECTED_FILL, SELECTED_EDGE, GOLD_DIM,
    FONT_SIZE_LIST, menu_font, scaled,
)


class ListItem(ButtonBehavior, BoxLayout):
    text = StringProperty("")
    font_size = NumericProperty(FONT_SIZE_LIST)
    text_color = ListProperty(list(TEXT_PRIMARY))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = scaled(48)
        self.padding = [scaled(16), scaled(8)]

        self._bg_rect = None
        self._hovered = False
        self._draw_bg()

        face = menu_font()
        self._label = Label(
            text=self.text,
            font_size=self.font_size,
            color=self.text_color,
            halign="left",
            valign="middle",
        )
        if face:
            self._label.font_name = face
        self._label.bind(size=self._label.setter("text_size"))
        self.add_widget(self._label)

        self.bind(text=self._on_text)
        self.bind(state=self._on_state)
        self.bind(pos=self._draw_bg, size=self._draw_bg)

        from kivy.core.window import Window
        Window.bind(mouse_pos=self._on_mouse_pos)

    def _draw_bg(self, *_):
        self.canvas.before.clear()
        if self.state == "down" or self._hovered:
            with self.canvas.before:
                Color(*SELECTED_FILL)
                self._bg_rect = RoundedRectangle(
                    pos=self.pos, size=self.size, radius=[scaled(6)],
                )
        else:
            self._bg_rect = None

    def _on_text(self, *_):
        self._label.text = self.text

    def _on_mouse_pos(self, window, pos):
        inside = self.collide_point(*self.to_widget(*pos))
        if inside != self._hovered:
            self._hovered = inside
            self._draw_bg()

    def _on_state(self, *_):
        self._draw_bg()
