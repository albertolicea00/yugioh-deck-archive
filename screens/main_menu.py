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

        title = Label(
            text="Yu-Gi-Oh!",
            font_size=scaled(122),
            color=TEXT_PRIMARY,
            bold=not face,
            size_hint_y=None,
            height=scaled(38),
        )
        if face:
            title.font_name = face

        subtitle = Label(
            text="Deck Archive",
            font_size=scaled(40),
            color=TEXT_PRIMARY,
            bold=not face,
            size_hint_y=None,
            height=scaled(44),
        )
        if face:
            subtitle.font_name = face

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
            padding=[0, self._top_margin + self._title_zone + self._fade_h,
                     0, self._status_h + self._fade_h],
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

        scroll.bind(scroll_y=self._on_menu_scroll)

        self._top_grad = Widget(
            size_hint=(1, None),
            height=self._fade_h,
            pos_hint={"x": 0},
        )
        self._bot_grad = Widget(
            size_hint=(1, None),
            height=self._fade_h,
            pos_hint={"x": 0},
        )
        column.add_widget(self._top_grad)
        column.add_widget(self._bot_grad)

        title_box = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=scaled(112) + self._top_margin,
            pos_hint={"center_x": 0.5, "top": 1},
            spacing=scaled(10),
            padding=[0, self._top_margin + scaled(20), 0, 0],
        )
        title_box.add_widget(title)
        title_box.add_widget(subtitle)
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
        self._root.bind(size=lambda *_: self._clamp_width())

        self._root.add_widget(column)
        self._column = column
        self.add_widget(self._root)

        Window.bind(size=self._on_window_resize)

    def _use_video(self):
        if not self._app_settings:
            return False
        return self._app_settings.get("video_background", True) and os.path.exists(VIDEO_VERTICAL)

    def _use_bgm(self):
        if not self._app_settings:
            return False
        return self._app_settings.get("background_music", True) and os.path.exists(MENU_BGM)

    def on_enter(self):
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
        parent_w = self._column.parent.width
        self._column.width = min(MAX_COLUMN_WIDTH, parent_w * 0.85)

    def _on_menu_scroll(self, *_):
        fade_h = self._fade_h
        tb = self._title_box
        st = self._status
        if not tb.parent or not st.parent:
            return

        _, title_bot = tb.to_window(0, tb.y)
        _, status_top = st.to_window(0, st.top)

        top_edge = title_bot - scaled(30)
        bot_edge = status_top + scaled(20)

        for btn in self._btn_list.children:
            _, btn_top = btn.to_window(0, btn.top)
            _, btn_bot = btn.to_window(0, btn.y)
            btn_h = max(btn.height, 1)

            vis_top = min(btn_top, top_edge)
            vis_bot = max(btn_bot, bot_edge)
            visible = max(0, vis_top - vis_bot) / btn_h

            if btn_top > top_edge:
                dist = (btn_top - top_edge) / fade_h
                visible *= max(0, 1 - dist)
            if btn_bot < bot_edge:
                dist = (bot_edge - btn_bot) / fade_h
                visible *= max(0, 1 - dist)

            btn.opacity = max(0, min(1, visible))

        self._draw_grad(self._top_grad, top_edge, fade_h, going_up=True)
        self._draw_grad(self._bot_grad, bot_edge, fade_h, going_up=False)

    def _draw_grad(self, w, edge_y, fade_h, going_up):
        w.canvas.clear()
        steps = 12
        step_h = fade_h / steps
        bg = (0.06, 0.04, 0.03)
        max_a = 0.25

        _, wy = w.parent.to_window(0, 0)

        if going_up:
            w.y = w.parent.y + (edge_y - wy) - fade_h
            for i in range(steps):
                a = ((i + 1) / steps) * max_a
                with w.canvas:
                    Color(*bg, a)
                    Rectangle(
                        pos=(w.x, w.y + step_h * i),
                        size=(w.width, step_h + 1),
                    )
        else:
            w.y = w.parent.y + (edge_y - wy)
            for i in range(steps):
                a = (1 - i / steps) * max_a
                with w.canvas:
                    Color(*bg, a)
                    Rectangle(
                        pos=(w.x, w.y + step_h * i),
                        size=(w.width, step_h + 1),
                    )

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

    def _on_window_resize(self, window, size):
        w, h = size
        portrait = h >= w
        self._bg.source = BG_VERTICAL if portrait else BG_HORIZONTAL
        if self._video and self._video.state == "play":
            self._video.source = VIDEO_VERTICAL if portrait else VIDEO_HORIZONTAL

    def show_message(self, text):
        self._status.text = text
