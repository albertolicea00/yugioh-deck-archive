"""Settings screen — UI scale and preferences."""

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.metrics import Metrics

from widgets.stone_button import StoneButton
from widgets.stone_panel import StonePanel
from theme import (
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
            spacing=8,
        )

        face = menu_font()

        header = BoxLayout(size_hint_y=None, height=50, spacing=10)
        back_btn = StoneButton(text="Back", size_hint_x=None, width=120)
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

        # --- UI Scale ---
        scale_header = Label(
            text="UI Scale", font_size=FONT_SIZE_LIST, color=GOLD,
            size_hint_y=None, height=36, halign="left", valign="middle",
            bold=not face,
        )
        if face:
            scale_header.font_name = face
        scale_header.bind(size=scale_header.setter("text_size"))
        panel.add_widget(scale_header)

        scale_desc = Label(
            text="Make everything bigger or smaller",
            font_size=FONT_SIZE_DETAIL, color=TEXT_SECONDARY,
            size_hint_y=None, height=24, halign="left", valign="middle",
        )
        scale_desc.bind(size=scale_desc.setter("text_size"))
        panel.add_widget(scale_desc)
        panel.add_widget(Widget(size_hint_y=None, height=8))

        slider_row = BoxLayout(size_hint_y=None, height=48, spacing=12)

        self._scale_label = Label(
            text="100%", font_size=FONT_SIZE_LIST, color=TEXT_PRIMARY,
            size_hint_x=None, width=70, halign="center",
            bold=True,
        )
        if face:
            self._scale_label.font_name = face

        self._slider = Slider(
            min=SCALE_MIN, max=SCALE_MAX, step=SCALE_STEP,
            value=1.0,
            cursor_size=(28, 28),
        )
        self._slider.bind(value=self._on_scale_change)

        slider_row.add_widget(self._slider)
        slider_row.add_widget(self._scale_label)
        panel.add_widget(slider_row)

        # Preset buttons
        preset_row = BoxLayout(size_hint_y=None, height=50, spacing=8)
        for pct in [100, 125, 150, 175, 200]:
            val = pct / 100.0
            btn = StoneButton(text=f"{pct}%", font_size=FONT_SIZE_DETAIL)
            btn.height = 50
            btn.bind(on_release=lambda _, v=val: self._set_scale(v))
            preset_row.add_widget(btn)
        panel.add_widget(preset_row)

        panel.add_widget(Widget(size_hint_y=None, height=16))

        # --- Preview ---
        preview_header = Label(
            text="Preview", font_size=FONT_SIZE_LIST, color=GOLD,
            size_hint_y=None, height=36, halign="left", valign="middle",
            bold=not face,
        )
        if face:
            preview_header.font_name = face
        preview_header.bind(size=preview_header.setter("text_size"))
        panel.add_widget(preview_header)

        self._preview = Label(
            text="Yu-Gi-Oh! Deck Manager\nThis is how text will look at this scale.",
            font_size=FONT_SIZE_LIST, color=TEXT_PRIMARY,
            size_hint_y=None, height=80, halign="center", valign="middle",
        )
        if face:
            self._preview.font_name = face
        self._preview.bind(size=self._preview.setter("text_size"))
        panel.add_widget(self._preview)

        panel.add_widget(Widget(size_hint_y=1))

        # Apply button
        apply_btn = StoneButton(text="Apply & Restart")
        apply_btn.bind(on_release=lambda _: self._apply())
        panel.add_widget(apply_btn)

        self._status = Label(
            text="", font_size=FONT_SIZE_DETAIL, color=GOLD_DIM,
            size_hint_y=None, height=30, halign="center",
        )
        self._status.bind(size=self._status.setter("text_size"))
        panel.add_widget(self._status)

        column.add_widget(panel)
        root.add_widget(column)
        self.add_widget(root)

        from kivy.core.window import Window
        Window.bind(size=self._on_window_resize)

    def on_enter(self):
        if self._settings:
            self._slider.value = self._settings.ui_scale
        self._on_scale_change(None, self._slider.value)

    def _on_scale_change(self, instance, value):
        pct = int(round(value * 100))
        self._scale_label.text = f"{pct}%"
        self._preview.font_size = FONT_SIZE_LIST * value

    def _set_scale(self, value):
        self._slider.value = value

    def _apply(self):
        if not self._settings:
            return
        scale = self._slider.value
        self._settings.ui_scale = scale
        self._settings.save()

        from kivy.metrics import Metrics
        Metrics.density = scale
        self._status.text = f"Scale set to {int(scale * 100)}%. Restart app for full effect."

    def _go_back(self):
        self.manager.current = "main_menu"

    def _on_window_resize(self, window, size):
        w, h = size
        self._bg.source = BG_VERTICAL if h >= w else BG_HORIZONTAL
