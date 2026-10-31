"""Game tile — framed card for game grid navigation."""

from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.graphics import Color, Rectangle, RoundedRectangle

from theme import (
    FRAME_RESTING, FRAME_ACTIVE, TEXT_PRIMARY, GOLD_DIM, DARK_PANEL,
    FONT_SIZE_LIST, FONT_SIZE_SMALL, menu_font, scaled,
)

BADGE_SIZE = scaled(26)
BADGE_MARGIN = scaled(6)


class GameTile(ButtonBehavior, FloatLayout):
    game_name = StringProperty("")
    deck_count = NumericProperty(0)
    hovered = BooleanProperty(False)

    def __init__(self, **kwargs):
        self._bg_rect = None
        self._bg_source = FRAME_RESTING
        self._badge_bg = None
        super().__init__(**kwargs)
        self.size_hint = (1, None)
        self.height = scaled(80)

        self._draw_bg()

        face = menu_font()

        self._name_label = Label(
            text=self.game_name,
            font_size=FONT_SIZE_LIST,
            color=TEXT_PRIMARY,
            halign="center",
            valign="middle",
            bold=not face,
            size_hint=(1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        if face:
            self._name_label.font_name = face
        self._name_label.bind(size=self._name_label.setter("text_size"))
        self.add_widget(self._name_label)

        self._badge = Label(
            text="",
            font_size=FONT_SIZE_SMALL,
            color=TEXT_PRIMARY,
            halign="center",
            valign="middle",
            bold=True,
            size_hint=(None, None),
            size=(BADGE_SIZE, BADGE_SIZE),
        )
        self.add_widget(self._badge)

        self.bind(game_name=self._update_text)
        self.bind(deck_count=self._update_text)
        self.bind(state=self._on_state)
        self.bind(hovered=self._on_hover_change)
        self.bind(pos=self._on_layout, size=self._on_layout)

        from kivy.core.window import Window
        Window.bind(mouse_pos=self._on_mouse_pos)

        self._update_text()

    def _draw_bg(self):
        from kivy.core.image import Image as CoreImage
        old_pos = self._badge_bg.pos if self._badge_bg else (0, 0)
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, 1, 1, 1)
            tex = CoreImage(self._bg_source).texture
            self._bg_rect = Rectangle(
                texture=tex, pos=self.pos, size=self.size,
            )
            Color(*DARK_PANEL[:3], 0.85)
            self._badge_bg = RoundedRectangle(
                pos=old_pos, size=(BADGE_SIZE, BADGE_SIZE),
                radius=[BADGE_SIZE / 2],
            )

    def _on_layout(self, *_):
        if self._bg_rect:
            self._bg_rect.pos = self.pos
            self._bg_rect.size = self.size
        self._position_badge()

    def _position_badge(self):
        bx = self.right - BADGE_SIZE - BADGE_MARGIN
        by = self.top - BADGE_SIZE - BADGE_MARGIN
        if self._badge_bg:
            self._badge_bg.pos = (bx, by)
        if hasattr(self, "_badge"):
            self._badge.pos = (bx, by)

    def _update_text(self, *_):
        self._name_label.text = self.game_name
        self._badge.text = str(self.deck_count)

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
