"""Settings screen — UI scale, video background, and music toggles."""

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from widgets.themed_scroll import ThemedScroll
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle

from widgets.stone_button import StoneButton
from widgets.stone_panel import StonePanel
from theme import (
    scaled,
    BG_VERTICAL, BG_HORIZONTAL, SCRIM, TEXT_PRIMARY, TEXT_SECONDARY,
    GOLD_DIM, GOLD, FONT_SIZE_TITLE, FONT_SIZE_LIST, FONT_SIZE_DETAIL,
    menu_font,
)
from core.app_settings import SCALE_MIN, SCALE_MAX, SCALE_STEP


class SettingsScreen(Screen):
    def __init__(self, app_settings=None, **kwargs):
        super().__init__(name="settings", **kwargs)
        self._settings = app_settings
        self._build_ui()

    def _build_ui(self):
        root = FloatLayout()

        self._bg = Image(source=BG_VERTICAL, fit_mode="cover", size_hint=(1, 1))
        root.add_widget(self._bg)

        scrim = Widget(size_hint=(1, 1))
        with scrim.canvas:
            Color(*SCRIM)
            self._scrim_rect = Rectangle(pos=scrim.pos, size=scrim.size)
        scrim.bind(
            pos=lambda w, v: setattr(self._scrim_rect, "pos", v),
            size=lambda w, v: setattr(self._scrim_rect, "size", v),
        )
        root.add_widget(scrim)

        column = BoxLayout(
            orientation="vertical",
            size_hint=(0.92, 0.92),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            spacing=scaled(8),
        )

        face = menu_font()

        header = BoxLayout(size_hint_y=None, height=scaled(50), spacing=scaled(10))
        back_btn = StoneButton(text="Back", size_hint_x=None, width=scaled(120))
        back_btn.bind(on_release=lambda _: self._go_back())
        header.add_widget(back_btn)
        title_lbl = Label(
            text="Settings", font_size=FONT_SIZE_TITLE, color=TEXT_PRIMARY,
            bold=not face,
        )
        if face:
            title_lbl.font_name = face
        header.add_widget(title_lbl)
        column.add_widget(header)

        panel = StonePanel(orientation="vertical", size_hint=(1, 1))
        scroll = ThemedScroll(do_scroll_x=False)
        content = BoxLayout(
            orientation="vertical", size_hint_y=None, spacing=scaled(8), padding=[scaled(4), scaled(4)],
        )
        content.bind(minimum_height=content.setter("height"))

        # --- UI Scale ---
        content.add_widget(self._section_label("UI Scale", face))
        content.add_widget(self._desc_label("Make everything bigger or smaller"))

        slider_row = BoxLayout(size_hint_y=None, height=scaled(48), spacing=scaled(12))
        self._scale_label = Label(
            text="100%", font_size=FONT_SIZE_LIST, color=TEXT_PRIMARY,
            size_hint_x=None, width=scaled(70), halign="center", bold=True,
        )
        if face:
            self._scale_label.font_name = face
        self._slider = Slider(
            min=SCALE_MIN, max=SCALE_MAX, step=SCALE_STEP,
            value=1.0, cursor_size=(28, 28),
        )
        self._slider.bind(value=self._on_scale_change)
        slider_row.add_widget(self._slider)
        slider_row.add_widget(self._scale_label)
        content.add_widget(slider_row)

        preset_row = BoxLayout(size_hint_y=None, height=scaled(50), spacing=scaled(8))
        for pct in [100, 125, 150, 175, 200]:
            val = pct / 100.0
            btn = StoneButton(text=f"{pct}%", font_size=FONT_SIZE_DETAIL)
            btn.height = 50
            btn.bind(on_release=lambda _, v=val: self._set_scale(v))
            preset_row.add_widget(btn)
        content.add_widget(preset_row)

        content.add_widget(Widget(size_hint_y=None, height=scaled(16)))

        # --- Video Background ---
        content.add_widget(self._section_label("Video Background", face))
        content.add_widget(self._desc_label("Animated temple background on main menu"))

        video_row = BoxLayout(size_hint_y=None, height=scaled(50), spacing=scaled(8))
        self._video_on_btn = StoneButton(text="ON", font_size=FONT_SIZE_DETAIL)
        self._video_on_btn.height = 50
        self._video_on_btn.bind(on_release=lambda _: self._set_toggle("video_background", True))
        self._video_off_btn = StoneButton(text="OFF", font_size=FONT_SIZE_DETAIL)
        self._video_off_btn.height = 50
        self._video_off_btn.bind(on_release=lambda _: self._set_toggle("video_background", False))
        video_row.add_widget(self._video_on_btn)
        video_row.add_widget(self._video_off_btn)
        content.add_widget(video_row)

        content.add_widget(Widget(size_hint_y=None, height=scaled(16)))

        # --- Background Music ---
        content.add_widget(self._section_label("Background Music", face))
        content.add_widget(self._desc_label("Menu music on main screen"))

        music_row = BoxLayout(size_hint_y=None, height=scaled(50), spacing=scaled(8))
        self._music_on_btn = StoneButton(text="ON", font_size=FONT_SIZE_DETAIL)
        self._music_on_btn.height = 50
        self._music_on_btn.bind(on_release=lambda _: self._set_toggle("background_music", True))
        self._music_off_btn = StoneButton(text="OFF", font_size=FONT_SIZE_DETAIL)
        self._music_off_btn.height = 50
        self._music_off_btn.bind(on_release=lambda _: self._set_toggle("background_music", False))
        music_row.add_widget(self._music_on_btn)
        music_row.add_widget(self._music_off_btn)
        content.add_widget(music_row)

        content.add_widget(Widget(size_hint_y=None, height=scaled(16)))

        # --- Preview ---
        content.add_widget(self._section_label("Preview", face))
        self._preview = Label(
            text="Yu-Gi-Oh! Deck Manager\nThis is how text will look at this scale.",
            font_size=FONT_SIZE_LIST, color=TEXT_PRIMARY,
            size_hint_y=None, height=scaled(80), halign="center", valign="middle",
        )
        if face:
            self._preview.font_name = face
        self._preview.bind(size=self._preview.setter("text_size"))
        content.add_widget(self._preview)

        content.add_widget(Widget(size_hint_y=None, height=scaled(16)))

        # Apply
        apply_btn = StoneButton(text="Apply & Save")
        apply_btn.bind(on_release=lambda _: self._apply())
        content.add_widget(apply_btn)

        self._status = Label(
            text="", font_size=FONT_SIZE_DETAIL, color=GOLD_DIM,
            size_hint_y=None, height=scaled(30), halign="center",
        )
        self._status.bind(size=self._status.setter("text_size"))
        content.add_widget(self._status)

        scroll.add_widget(content)
        panel.add_widget(scroll)
        column.add_widget(panel)
        root.add_widget(column)
        self.add_widget(root)

        from kivy.core.window import Window
        Window.bind(size=self._on_window_resize)

    def _section_label(self, text, face):
        lbl = Label(
            text=text, font_size=FONT_SIZE_LIST, color=GOLD,
            size_hint_y=None, height=scaled(36), halign="left", valign="middle",
            bold=not face,
        )
        if face:
            lbl.font_name = face
        lbl.bind(size=lbl.setter("text_size"))
        return lbl

    def _desc_label(self, text):
        lbl = Label(
            text=text, font_size=FONT_SIZE_DETAIL, color=TEXT_SECONDARY,
            size_hint_y=None, height=scaled(24), halign="left", valign="middle",
        )
        lbl.bind(size=lbl.setter("text_size"))
        return lbl

    def on_enter(self):
        if self._settings:
            self._slider.value = self._settings.ui_scale
        self._on_scale_change(None, self._slider.value)
        self._update_toggle_labels()

    def _on_scale_change(self, instance, value):
        pct = int(round(value * 100))
        self._scale_label.text = f"{pct}%"
        self._preview.font_size = FONT_SIZE_LIST * value

    def _set_scale(self, value):
        self._slider.value = value

    def _set_toggle(self, key, value):
        if self._settings:
            self._settings.set(key, value)
        self._update_toggle_labels()

    def _update_toggle_labels(self):
        if not self._settings:
            return
        vid = self._settings.get("video_background", True)
        self._video_on_btn.text = "ON  *" if vid else "ON"
        self._video_off_btn.text = "OFF  *" if not vid else "OFF"

        mus = self._settings.get("background_music", True)
        self._music_on_btn.text = "ON  *" if mus else "ON"
        self._music_off_btn.text = "OFF  *" if not mus else "OFF"

    def _apply(self):
        if not self._settings:
            return
        self._settings.ui_scale = self._slider.value
        self._settings.save()
        self._status.text = f"Saved at {int(self._slider.value * 100)}%. Restart app to apply."

    def _go_back(self):
        self.manager.current = "main_menu"

    def _on_window_resize(self, window, size):
        w, h = size
        self._bg.source = BG_VERTICAL if h >= w else BG_HORIZONTAL
