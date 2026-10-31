"""Themed ScrollView — rounded gold scrollbar matching the Egyptian UI."""

from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, InstructionGroup
from kivy.clock import Clock

from theme import GOLD_DIM, DARK_PANEL_EDGE, scaled


SCROLLBAR_WIDTH = scaled(8)
SCROLLBAR_RADIUS = scaled(4)
SCROLLBAR_MARGIN = scaled(3)
SCROLLBAR_COLOR = GOLD_DIM[:3]
SCROLLBAR_TRACK = DARK_PANEL_EDGE[:3]


class ThemedScroll(ScrollView):
    def __init__(self, **kwargs):
        kwargs.setdefault("scroll_type", ["content"])
        super().__init__(**kwargs)
        self.bar_width = 0
        self._sb_group = InstructionGroup()
        self.canvas.add(self._sb_group)
        self._bar_opacity = 0
        self._fade_event = None
        self.bind(scroll_y=self._on_scroll)
        self.bind(size=self._schedule_redraw, pos=self._schedule_redraw)
        self._redraw_event = None

    def _schedule_redraw(self, *_):
        if self._redraw_event:
            return
        self._redraw_event = Clock.schedule_once(self._do_redraw, 0)

    def _on_scroll(self, *_):
        self._bar_opacity = 1
        self._do_redraw()
        if self._fade_event:
            self._fade_event.cancel()
        self._fade_event = Clock.schedule_once(self._fade_out, 1.2)

    def _fade_out(self, *_):
        self._bar_opacity = 0
        self._do_redraw()

    def _do_redraw(self, *_):
        self._redraw_event = None
        self._sb_group.clear()

        if not self.children:
            return

        content_h = self.children[0].height
        view_h = self.height
        if content_h <= view_h or view_h <= 0:
            return

        bar_w = SCROLLBAR_WIDTH
        margin = SCROLLBAR_MARGIN
        radius = SCROLLBAR_RADIUS
        opacity = self._bar_opacity

        track_x = self.right - bar_w - margin
        track_y = self.y + margin
        track_h = view_h - 2 * margin

        if track_h <= 0:
            return

        ratio = view_h / content_h
        thumb_h = max(scaled(24), track_h * ratio)
        scroll_range = track_h - thumb_h
        thumb_y = track_y + scroll_range * self.scroll_y

        self._sb_group.add(Color(*SCROLLBAR_TRACK, 0.25 * opacity))
        self._sb_group.add(RoundedRectangle(
            pos=(track_x, track_y),
            size=(bar_w, track_h),
            radius=[radius],
        ))
        self._sb_group.add(Color(*SCROLLBAR_COLOR, 0.6 * opacity))
        self._sb_group.add(RoundedRectangle(
            pos=(track_x, thumb_y),
            size=(bar_w, thumb_h),
            radius=[radius],
        ))
