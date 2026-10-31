"""Deck tile — framed card for deck grid navigation."""

from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window

from theme import (
    FRAME_RESTING, FRAME_ACTIVE, TEXT_PRIMARY, GOLD_DIM, TEXT_WARNING,
    FONT_SIZE_LIST, FONT_SIZE_SMALL, menu_font, scaled,
)


class DeckTile(ButtonBehavior, FloatLayout):
    deck_name = StringProperty("")
    main_count = NumericProperty(0)
    extra_count = NumericProperty(0)
    side_count = NumericProperty(0)
    hovered = BooleanProperty(False)

    def __init__(self, **kwargs):
        self._bg_rect = None
        self._bg_source = FRAME_RESTING
        super().__init__(**kwargs)
        self.size_hint = (1, None)
        self.height = max(60, int(Window.height * 0.06))

        self._draw_bg()

        face = menu_font()

        self._name_label = Label(
            font_size=FONT_SIZE_LIST,
            color=TEXT_PRIMARY,
            halign="center",
            valign="bottom",
            bold=not face,
            size_hint=(0.9, 0.55),
            pos_hint={"center_x": 0.5, "top": 0.92},
            shorten=True,
            shorten_from="right",
        )
        if face:
            self._name_label.font_name = face
        self._name_label.bind(size=self._name_label.setter("text_size"))
        self.add_widget(self._name_label)

        self._counts_label = Label(
            font_size=FONT_SIZE_SMALL,
            color=GOLD_DIM,
            halign="center",
            valign="top",
            size_hint=(0.9, 0.35),
            pos_hint={"center_x": 0.5, "y": 0.04},
        )
        if face:
            self._counts_label.font_name = face
        self._counts_label.bind(size=self._counts_label.setter("text_size"))
        self.add_widget(self._counts_label)

        self.bind(deck_name=self._update_text)
        self.bind(main_count=self._update_text)
        self.bind(extra_count=self._update_text)
        self.bind(side_count=self._update_text)
        self.bind(state=self._on_state)
        self.bind(hovered=self._on_hover_change)
        self.bind(pos=self._on_layout, size=self._on_layout)

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

    def _on_layout(self, *_):
        if self._bg_rect:
            self._bg_rect.pos = self.pos
            self._bg_rect.size = self.size

    def _update_text(self, *_):
        self._name_label.text = self.deck_name
        self._counts_label.text = f"{self.main_count} / {self.extra_count} / {self.side_count}"

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
