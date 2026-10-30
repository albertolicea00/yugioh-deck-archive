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
    {"id": "settings", "label": "Settings"},
]

MAX_COLUMN_WIDTH = scaled(520)


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

        column = BoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            spacing=scaled(10),
            padding=[0, scaled(20)],
        )

        face = menu_font()

        title = Label(
            text="Yu-Gi-Oh!",
            font_size=FONT_SIZE_TITLE + scaled(18),
            color=TEXT_PRIMARY,
            bold=not face,
            size_hint_y=None,
            height=scaled(60),
        )
        if face:
            title.font_name = face

        subtitle = Label(
            text="Deck Manager",
            font_size=FONT_SIZE_TITLE,
            color=GOLD_DIM,
            bold=not face,
            size_hint_y=None,
            height=scaled(36),
        )
        if face:
            subtitle.font_name = face

        column.add_widget(title)
        column.add_widget(subtitle)
        column.add_widget(Widget(size_hint_y=None, height=scaled(16)))

        for entry in MENU_ENTRIES:
            btn = StoneButton(text=entry["label"])
            btn.bind(on_release=lambda _, eid=entry["id"]: self._navigate(eid))
            column.add_widget(btn)

        self._status = Label(
            text="",
            font_size=FONT_SIZE_SMALL,
            color=GOLD_DIM,
            size_hint_y=None,
            height=scaled(56),
        )
        if face:
            self._status.font_name = face
        column.add_widget(self._status)

        column.height = sum(c.height for c in column.children) + column.spacing * len(column.children)
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

    def _navigate(self, destination):
        if destination == "games":
            self.manager.current = "game_list"
        elif destination == "create":
            self.manager.current = "deck_editor"
        elif destination == "search":
            self.manager.current = "card_search"
        elif destination == "import":
            self.manager.current = "import_export"
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
