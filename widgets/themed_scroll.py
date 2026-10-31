"""Themed ScrollView — rounded gold scrollbar drawn outside the scroll area."""

from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, InstructionGroup
from kivy.clock import Clock

from theme import GOLD_DIM, DARK_PANEL_EDGE, scaled


SCROLLBAR_WIDTH = scaled(6)
SCROLLBAR_RADIUS = scaled(3)
SCROLLBAR_GAP = scaled(6)
SCROLLBAR_COLOR = GOLD_DIM[:3]
SCROLLBAR_TRACK = DARK_PANEL_EDGE[:3]


class ThemedScroll(ScrollView):
    def __init__(self, **kwargs):
        kwargs.setdefault("scroll_type", ["content"])
        super().__init__(**kwargs)
        self.bar_width = 0
        self._sb_group = None
        self._bar_opacity = 0
        self._fade_event = None
        self._redraw_event = None
        self._parent_bound = False
        self.bind(scroll_y=self._on_scroll)
        self.bind(size=self._schedule_redraw, pos=self._schedule_redraw)
        self.bind(parent=self._on_parent)

    def _on_parent(self, *_):
        if self.parent and not self._parent_bound:
            self._sb_group = InstructionGroup()
            self.parent.canvas.after.add(self._sb_group)
            self._parent_bound = True
            self.parent.bind(size=self._schedule_redraw, pos=self._schedule_redraw)

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
        if not self._sb_group:
            return
        self._sb_group.clear()

        if not self.children:
            return

        content_h = self.children[0].height
        view_h = self.height
        if content_h <= view_h or view_h <= 0:
            return

        bar_w = SCROLLBAR_WIDTH
        gap = SCROLLBAR_GAP
        radius = SCROLLBAR_RADIUS
        opacity = self._bar_opacity

        track_x = self.right + gap
        track_y = self.y + scaled(4)
        track_h = view_h - scaled(8)

        if track_h <= 0:
            return

        ratio = view_h / content_h
        thumb_h = max(scaled(20), track_h * ratio)
        scroll_range = track_h - thumb_h
        thumb_y = track_y + scroll_range * self.scroll_y

        self._sb_group.add(Color(*SCROLLBAR_TRACK, 0.08 * opacity))
        self._sb_group.add(RoundedRectangle(
            pos=(track_x, track_y),
            size=(bar_w, track_h),
            radius=[radius],
        ))
        self._sb_group.add(Color(*SCROLLBAR_COLOR, 0.18 * opacity))
        self._sb_group.add(RoundedRectangle(
            pos=(track_x, thumb_y),
            size=(bar_w, thumb_h),
            radius=[radius],
        ))
