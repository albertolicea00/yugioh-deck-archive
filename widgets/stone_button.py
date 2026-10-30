"""Stone slab button — textured button matching the temple menu style."""

from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty, ListProperty, NumericProperty, BooleanProperty
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window

from theme import (
    FRAME_RESTING, FRAME_ACTIVE, TEXT_PRIMARY,
    FONT_SIZE_BUTTON, SLAB_MIN_HEIGHT, menu_font,
)


class StoneButton(ButtonBehavior, BoxLayout):
    text = StringProperty("")
    font_size = NumericProperty(FONT_SIZE_BUTTON)
    text_color = ListProperty(list(TEXT_PRIMARY))
    hovered = BooleanProperty(False)

    def __init__(self, **kwargs):
        self._bg_rect = None
        self._bg_source = FRAME_RESTING
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = SLAB_MIN_HEIGHT
        self.padding = [10, 5]
        self.spacing = 10

        self._draw_bg()

        face = menu_font()
        self._label = Label(
            text=self.text,
            font_size=self.font_size,
            color=self.text_color,
            halign="center",
            valign="middle",
            bold=not face,
        )
        if face:
            self._label.font_name = face
        self._label.bind(size=self._label.setter("text_size"))

        self.add_widget(self._label)

        self.bind(text=self._on_text)
        self.bind(state=self._on_state)
        self.bind(hovered=self._on_hover_change)
        self.bind(pos=self._update_bg, size=self._update_bg)

        Window.bind(mouse_pos=self._on_mouse_pos)

    def _draw_bg(self):
        from kivy.core.image import Image as CoreImage
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, 1, 1, 1)
            tex = CoreImage(self._bg_source).texture
            self._bg_rect = Rectangle(
                texture=tex, pos=self.pos, size=self.size,
            )

    def _update_bg(self, *_):
        if self._bg_rect:
            self._bg_rect.pos = self.pos
            self._bg_rect.size = self.size

    def _on_text(self, *_):
        self._label.text = self.text

    def _on_mouse_pos(self, window, pos):
        inside = self.collide_point(*self.to_widget(*pos))
        if inside != self.hovered:
            self.hovered = inside

    def _on_hover_change(self, *_):
        if self.state != "down":
            self._bg_source = FRAME_ACTIVE if self.hovered else FRAME_RESTING
            self._draw_bg()

    def _on_state(self, instance, value):
        if value == "down":
            self._bg_source = FRAME_ACTIVE
        else:
            self._bg_source = FRAME_ACTIVE if self.hovered else FRAME_RESTING
        self._draw_bg()
