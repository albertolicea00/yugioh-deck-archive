"""Game tile — framed card for game grid navigation."""

from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.graphics import Color, Rectangle

from theme import (
    FRAME_RESTING, FRAME_ACTIVE, TEXT_PRIMARY, GOLD_DIM,
    FONT_SIZE_LIST, FONT_SIZE_SMALL, menu_font, scaled,
)


class GameTile(ButtonBehavior, BoxLayout):
    game_name = StringProperty("")
    deck_count = NumericProperty(0)
    hovered = BooleanProperty(False)

    def __init__(self, **kwargs):
        self._bg_rect = None
        self._bg_source = FRAME_RESTING
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint = (1, None)
        self.height = scaled(120)
        self.padding = [scaled(16), scaled(16)]
        self.spacing = scaled(4)

        self._draw_bg()

        face = menu_font()

        self._name_label = Label(
            text=self.game_name,
            font_size=FONT_SIZE_LIST,
            color=TEXT_PRIMARY,
            halign="center",
            valign="bottom",
            bold=not face,
            size_hint_y=0.65,
        )
        if face:
            self._name_label.font_name = face
        self._name_label.bind(size=self._name_label.setter("text_size"))

        self._count_label = Label(
            text="",
            font_size=FONT_SIZE_SMALL,
            color=GOLD_DIM,
            halign="center",
            valign="top",
            size_hint_y=0.35,
        )
        if face:
            self._count_label.font_name = face
        self._count_label.bind(size=self._count_label.setter("text_size"))

        self.add_widget(self._name_label)
        self.add_widget(self._count_label)

        self.bind(game_name=self._update_text)
        self.bind(deck_count=self._update_text)
        self.bind(state=self._on_state)
        self.bind(hovered=self._on_hover_change)
        self.bind(pos=self._update_bg, size=self._update_bg)

        from kivy.core.window import Window
        Window.bind(mouse_pos=self._on_mouse_pos)

        self._update_text()

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

    def _update_text(self, *_):
        self._name_label.text = self.game_name
        self._count_label.text = f"{self.deck_count} decks"

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
