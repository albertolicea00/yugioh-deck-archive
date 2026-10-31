"""Breadcrumb navigation bar — framed tiles showing navigation path."""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty, BooleanProperty
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window

from theme import (
    FRAME_RESTING, FRAME_ACTIVE, TEXT_PRIMARY, GOLD_DIM,
    FONT_SIZE_LIST, FONT_SIZE_SMALL, menu_font, scaled,
)


class _Crumb(ButtonBehavior, FloatLayout):
    text = StringProperty("")
    active = BooleanProperty(False)
    hovered = BooleanProperty(False)

    def __init__(self, **kwargs):
        self._bg_rect = None
        super().__init__(**kwargs)
        self.size_hint = (None, 1)

        face = menu_font()
        self._label = Label(
            text=self.text,
            font_size=FONT_SIZE_SMALL,
            color=TEXT_PRIMARY,
            halign="center",
            valign="middle",
            bold=not face,
            size_hint=(1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        if face:
            self._label.font_name = face
        self.add_widget(self._label)

        self.bind(text=self._on_text)
        self.bind(active=lambda *_: self._draw_bg())
        self.bind(state=self._on_state)
        self.bind(hovered=self._on_hover)
        self.bind(pos=self._on_layout, size=self._on_layout)

        Window.bind(mouse_pos=self._on_mouse_pos)
        self._on_text()
        self._draw_bg()

    def _on_text(self, *_):
        self._label.text = self.text

    def _on_layout(self, *_):
        if self._bg_rect:
            self._bg_rect.pos = self.pos
            self._bg_rect.size = self.size
        self._label.text_size = (self.width, self.height)

    def _draw_bg(self, *_):
        from kivy.core.image import Image as CoreImage
        if self.active or self.state == "down" or self.hovered:
            source = FRAME_ACTIVE
        else:
            source = FRAME_RESTING
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, 1, 1, 1)
            tex = CoreImage(source).texture
            self._bg_rect = Rectangle(
                texture=tex, pos=self.pos, size=self.size,
            )

    def _on_mouse_pos(self, window, pos):
        inside = self.collide_point(*self.to_widget(*pos))
        if inside != self.hovered:
            self.hovered = inside

    def _on_hover(self, *_):
        if self.state != "down":
            self._draw_bg()

    def _on_state(self, *_):
        self._draw_bg()


class BreadcrumbBar(BoxLayout):
    """
    Usage:
        bar = BreadcrumbBar(height=scaled(40))
        bar.set_crumbs([
            {"label": "Menu", "screen": "main_menu"},
            {"label": "Yu-Gi-Oh!", "screen": "game_list"},
            {"label": "Dark Magician Deck", "screen": None},  # current, no nav
        ])
        bar.bind(on_navigate=lambda _, screen: ...)
    """

    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", scaled(40))
        kwargs.setdefault("spacing", 6)
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self._crumbs_data = []
        self.register_event_type("on_navigate")

    def on_navigate(self, screen_name):
        pass

    def set_crumbs(self, crumbs):
        self._crumbs_data = crumbs
        self._rebuild()

    def _rebuild(self):
        self.clear_widgets()
        crumbs = self._crumbs_data
        if not crumbs:
            return

        bar_h = self.height
        max_crumbs = max(2, int(self.width / (bar_h * 2.5))) if self.width > 0 else 5

        display = crumbs
        ellipsis_at = -1
        if len(crumbs) > max_crumbs:
            keep_start = 1
            keep_end = max_crumbs - 2
            display = crumbs[:keep_start] + [{"label": "...", "screen": None, "ellipsis": True}] + crumbs[-keep_end:]
            ellipsis_at = keep_start

        for i, crumb in enumerate(display):
            is_last = (i == len(display) - 1)
            is_ellipsis = crumb.get("ellipsis", False)

            c = _Crumb(text=crumb["label"], active=is_last)
            c.width = self._crumb_width(crumb["label"], bar_h)

            if not is_last and not is_ellipsis and crumb.get("screen"):
                screen = crumb["screen"]
                c.bind(on_release=lambda _, s=screen: self.dispatch("on_navigate", s))

            self.add_widget(c)

    def _crumb_width(self, text, bar_h):
        base = max(bar_h * 1.8, len(text) * bar_h * 0.28)
        return min(base, bar_h * 6)

    def on_size(self, *_):
        if getattr(self, "_crumbs_data", None):
            self._rebuild()
