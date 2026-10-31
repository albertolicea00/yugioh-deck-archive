"""Main menu — stone slabs over temple background with optional video and BGM."""

import os

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.video import Video
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.clock import Clock

from widgets.stone_button import StoneButton
from kivy.uix.scrollview import ScrollView
from theme import (
    BG_VERTICAL, BG_HORIZONTAL, VIDEO_VERTICAL, VIDEO_HORIZONTAL, MENU_BGM,
    SCRIM, TEXT_PRIMARY, GOLD_DIM,
    FONT_SIZE_TITLE, FONT_SIZE_SMALL, SLAB_MIN_HEIGHT,
    menu_font, scaled,
)


MENU_ENTRIES = [
    {"id": "games", "label": "My Decks"},
    {"id": "create", "label": "New Deck"},
    {"id": "search", "label": "Card Search"},
    {"id": "import", "label": "Import / Export"},
    {"id": "resource_packs", "label": "Resources"},
    {"id": "settings", "label": "Settings"},
]

MAX_COLUMN_WIDTH = scaled(380)


class MainMenuScreen(Screen):
    def __init__(self, app_settings=None, **kwargs):
        super().__init__(name="main_menu", **kwargs)
        self._app_settings = app_settings
        self._video = None
        self._bgm = None
        self._root = FloatLayout()

        # Static image fallback (always present, behind video)
        self._bg = Image(
            source=BG_VERTICAL,
            fit_mode="cover",
            size_hint=(1, 1),
        )
        self._root.add_widget(self._bg)

        # Video background placeholder
        self._video_slot = Widget(size_hint=(1, 1))
        self._root.add_widget(self._video_slot)

        # Scrim
        scrim = Widget(size_hint=(1, 1))
        with scrim.canvas:
            Color(*SCRIM)
            self._scrim_rect = Rectangle(pos=scrim.pos, size=scrim.size)
        scrim.bind(
            pos=lambda w, v: setattr(self._scrim_rect, "pos", v),
            size=lambda w, v: setattr(self._scrim_rect, "size", v),
        )
        self._root.add_widget(scrim)

        face = menu_font()

        self._title_label = Label(
            text="Yu-Gi-Oh!",
            font_size=scaled(122),
            color=TEXT_PRIMARY,
            bold=not face,
            size_hint_y=None,
            height=scaled(38),
        )
        if face:
            self._title_label.font_name = face

        self._subtitle_label = Label(
            text="Deck Archive",
            font_size=scaled(40),
            color=TEXT_PRIMARY,
            bold=not face,
            size_hint_y=None,
            height=scaled(44),
        )
        if face:
            self._subtitle_label.font_name = face

        self._top_margin = scaled(50)
        self._title_zone = scaled(132)
        self._fade_h = scaled(140)
        self._status_h = scaled(36)

        column = FloatLayout(
            size_hint=(None, 1),
            pos_hint={"center_x": 0.5},
        )

        btn_list = BoxLayout(
            orientation="vertical", size_hint_y=None,
            spacing=scaled(10),
            padding=[0, self._top_margin + self._title_zone + scaled(20),
                     0, scaled(10)],
        )
        for entry in MENU_ENTRIES:
            btn = StoneButton(text=entry["label"])
            btn.bind(on_release=lambda _, eid=entry["id"]: self._navigate(eid))
            btn_list.add_widget(btn)
        btn_list.bind(minimum_height=btn_list.setter("height"))

        scroll = ScrollView(
            do_scroll_x=False, bar_width=0,
            scroll_type=["content"],
            size_hint=(1, 1), pos_hint={"x": 0, "y": 0},
        )
        self._btn_list = btn_list
        self._scroll = scroll
        scroll.add_widget(btn_list)
        column.add_widget(scroll)

        scroll.bind(scroll_y=self._on_menu_scroll,
                    size=lambda *_: self._on_menu_scroll())

        title_box = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=scaled(112) + self._top_margin,
            pos_hint={"center_x": 0.5, "top": 1},
            spacing=scaled(10),
            padding=[0, self._top_margin + scaled(20), 0, 0],
        )
        title_box.add_widget(self._title_label)
        title_box.add_widget(self._subtitle_label)
        self._title_box = title_box
        column.add_widget(title_box)

        self._status = Label(
            text="",
            font_size=FONT_SIZE_SMALL,
            color=GOLD_DIM,
            size_hint=(1, None),
            height=self._status_h,
            pos_hint={"x": 0, "y": 0},
        )
        if face:
            self._status.font_name = face
        column.add_widget(self._status)

        column.width = MAX_COLUMN_WIDTH
        column.bind(parent=self._clamp_width)
        column.bind(size=lambda *_: self._deferred_layout())
        self._root.bind(size=lambda *_: self._clamp_width())

        self._root.add_widget(column)
        self._column = column
        self.add_widget(self._root)

        Window.bind(size=self._on_window_resize)
        Clock.schedule_once(self._deferred_layout, 0)

    def _use_video(self):
        if not self._app_settings:
            return False
        return self._app_settings.get("video_background", True) and os.path.exists(VIDEO_VERTICAL)

    def _use_bgm(self):
        if not self._app_settings:
            return False
        return self._app_settings.get("background_music", True) and os.path.exists(MENU_BGM)

    def on_enter(self):
        Clock.schedule_once(self._deferred_layout, 0)
        if self._use_video():
            self._start_video()
        else:
            self._stop_video()

        if self._use_bgm():
            self._start_bgm()

    def on_leave(self):
        self._stop_video()
        self._stop_bgm()

    def _start_video(self):
        if self._video:
            self._video.state = "play"
            return

        w, h = Window.size
        source = VIDEO_VERTICAL if h >= w else VIDEO_HORIZONTAL

        self._video = Video(
            source=source,
            state="play",
            options={"eos": "loop"},
            size_hint=(1, 1),
            fit_mode="cover",
        )
        self._video.opacity = 1
        idx = self._root.children.index(self._video_slot)
        self._root.remove_widget(self._video_slot)
        self._root.add_widget(self._video, index=idx)

    def _stop_video(self):
        if self._video:
            self._video.state = "stop"
            idx = self._root.children.index(self._video)
            self._root.remove_widget(self._video)
            self._video.unload()
            self._video = None
            self._root.add_widget(self._video_slot, index=idx)

    def _start_bgm(self):
        if self._bgm and self._bgm.state == "play":
            return
        if not self._bgm:
            self._bgm = SoundLoader.load(MENU_BGM)
        if self._bgm:
            self._bgm.loop = True
            self._bgm.volume = 0.4
            self._bgm.play()

    def _stop_bgm(self):
        if self._bgm and self._bgm.state == "play":
            self._bgm.stop()

    def _clamp_width(self, *_):
        if not hasattr(self, "_column") or not self._column.parent:
            return
        pw = self._column.parent.width
        ph = self._column.parent.height or Window.height
        if ph >= pw:
            col_w = int(pw * 0.78)
        else:
            col_w = int(pw * 0.40)
        self._column.width = min(col_w, int(ph * 0.45))

    def _on_menu_scroll(self, *_):
        fade_h = self._fade_h
        tb = self._title_box
        if not tb.parent:
            return

        content_h = self._btn_list.height
        view_h = self._scroll.height
        if content_h <= view_h:
            for btn in self._btn_list.children:
                btn.opacity = 1
            return

        _, title_bot = tb.to_window(0, tb.y)
        top_edge = title_bot - int(Window.height * 0.02)

        for btn in self._btn_list.children:
            _, btn_top = btn.to_window(0, btn.top)

            if btn_top <= top_edge:
                btn.opacity = 1
            else:
                vis = min(btn_top, top_edge + fade_h)
                dist = (vis - top_edge) / fade_h
                btn.opacity = max(0, 1 - dist)


    def _navigate(self, destination):
        if destination == "games":
            self.manager.current = "game_list"
        elif destination == "create":
            self.manager.current = "deck_editor"
        elif destination == "search":
            self.manager.current = "card_search"
        elif destination == "import":
            self.manager.current = "import_export"
        elif destination == "resource_packs":
            self.manager.current = "resource_packs"
        elif destination == "settings":
            self.manager.current = "settings"

    def _deferred_layout(self, *_):
        self._clamp_width()
        self._update_top_margin(Window.height)
        self._on_menu_scroll()

    def _update_top_margin(self, h):
        col_w = self._column.width or int(h * 0.4)

        title_fs = min(int(h * 0.14), int(col_w * 0.32))
        self._title_label.font_size = max(40, title_fs)
        self._title_label.height = int(title_fs * 0.31)

        sub_fs = min(int(h * 0.05), int(col_w * 0.10))
        self._subtitle_label.font_size = max(16, sub_fs)
        self._subtitle_label.height = int(sub_fs * 1.1)

        sp = int(h * 0.006)
        title_zone = self._title_label.height + self._subtitle_label.height + sp
        self._title_zone = title_zone
        self._title_box.spacing = sp

        self._fade_h = int(h * 0.08)

        btn_h = int(h * 0.065)
        for btn in self._btn_list.children:
            btn.height = btn_h
            btn.font_size = int(btn_h * 0.38)

        margin = int(h * 0.10)
        pad_top = int(h * 0.012)
        box_h = title_zone + margin + pad_top
        self._title_box.height = box_h
        self._title_box.padding = [0, margin + pad_top, 0, 0]

        btn_gap = int(h * 0.025)
        self._btn_list.padding = [0, margin + title_zone + btn_gap, 0, int(h * 0.006)]
        self._btn_list.spacing = int(h * 0.012)

    def _on_window_resize(self, window, size):
        w, h = size
        portrait = h >= w
        self._bg.source = BG_VERTICAL if portrait else BG_HORIZONTAL
        if self._video and self._video.state == "play":
            self._video.source = VIDEO_VERTICAL if portrait else VIDEO_HORIZONTAL
        self._clamp_width()
        self._update_top_margin(h)

    def show_message(self, text):
        self._status.text = text
