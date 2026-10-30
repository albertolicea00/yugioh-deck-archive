"""Import/Export screen — convert between deck formats."""

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.uix.filechooser import FileChooserListView

from widgets.stone_button import StoneButton
from widgets.stone_panel import StonePanel
from core import formats
from theme import (
    BG_VERTICAL, SCRIM, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_SUCCESS, TEXT_WARNING,
    FONT_SIZE_TITLE, FONT_SIZE_LIST, FONT_SIZE_DETAIL, FONT_SIZE_SMALL,
    DARK_PANEL, GOLD_DIM,
)


class ImportExportScreen(Screen):
    def __init__(self, deck_manager=None, card_db=None, **kwargs):
        super().__init__(name="import_export", **kwargs)
        self._dm = deck_manager
        self._card_db = card_db
        self._build_ui()

    def _build_ui(self):
        root = FloatLayout()

        bg = Image(source=BG_VERTICAL, fit_mode="fill", size_hint=(1, 1))
        root.add_widget(bg)

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

        # Header
        header = BoxLayout(size_hint_y=None, height=50, spacing=10)
        back_btn = StoneButton(text="Back", size_hint_x=None, width=90)
        back_btn.bind(on_release=lambda _: setattr(self.manager, "current", "main_menu"))
        header.add_widget(back_btn)
        header.add_widget(Label(
            text="Import / Export", font_size=FONT_SIZE_TITLE, color=TEXT_PRIMARY, bold=True,
        ))
        column.add_widget(header)

        # Import section
        import_panel = StonePanel(orientation="vertical", size_hint_y=0.5)
        import_panel.add_widget(Label(
            text="Import", font_size=FONT_SIZE_LIST, color=TEXT_PRIMARY, bold=True,
            size_hint_y=None, height=30,
        ))

        # YDKE paste
        ydke_row = BoxLayout(size_hint_y=None, height=40, spacing=6)
        self._ydke_input = TextInput(
            hint_text="Paste YDKE URL here (ydke://...)",
            multiline=False,
            background_color=list(DARK_PANEL),
            foreground_color=list(TEXT_PRIMARY),
            cursor_color=list(TEXT_PRIMARY),
        )
        ydke_row.add_widget(self._ydke_input)
        ydke_btn = StoneButton(text="Import", size_hint_x=None, width=100)
        ydke_btn.bind(on_release=lambda _: self._import_ydke())
        ydke_row.add_widget(ydke_btn)
        import_panel.add_widget(ydke_row)

        # YDK paste
        ydk_row = BoxLayout(size_hint_y=None, height=40, spacing=6)
        self._ydk_input = TextInput(
            hint_text="Paste YDK content here...",
            multiline=True,
            background_color=list(DARK_PANEL),
            foreground_color=list(TEXT_PRIMARY),
            cursor_color=list(TEXT_PRIMARY),
            size_hint_y=1,
        )
        import_panel.add_widget(self._ydk_input)

        ydk_btn = StoneButton(text="Import YDK", size_hint_x=None, width=120)
        ydk_btn.bind(on_release=lambda _: self._import_ydk())
        import_panel.add_widget(ydk_btn)

        column.add_widget(import_panel)

        # Export section
        export_panel = StonePanel(orientation="vertical", size_hint_y=0.3)
        export_panel.add_widget(Label(
            text="Export", font_size=FONT_SIZE_LIST, color=TEXT_PRIMARY, bold=True,
            size_hint_y=None, height=30,
        ))
        export_panel.add_widget(Label(
            text="Open a deck and use the export options from the deck view.",
            font_size=FONT_SIZE_DETAIL, color=TEXT_SECONDARY,
            size_hint_y=None, height=40, halign="center",
        ))

        export_row = BoxLayout(size_hint_y=None, height=40, spacing=6)
        for fmt in ["YDK", "YDKE", "TXT"]:
            btn = StoneButton(text=f"Export {fmt}", font_size=14)
            btn.bind(on_release=lambda _, f=fmt: self._export(f))
            export_row.add_widget(btn)
        export_panel.add_widget(export_row)
        column.add_widget(export_panel)

        # Status
        self._status = Label(
            text="", font_size=FONT_SIZE_SMALL, color=TEXT_SUCCESS,
            size_hint_y=None, height=24,
        )
        column.add_widget(self._status)

        root.add_widget(column)
        self.add_widget(root)

    def _import_ydke(self):
        text = self._ydke_input.text.strip()
        if not text.startswith("ydke://"):
            self._status.text = "Invalid YDKE URL"
            self._status.color = list(TEXT_WARNING)
            return
        try:
            deck = formats.ydke_to_json(text)
            path = self._dm.create_deck("Imported", "YDKE Import", deck)
            self._status.text = f"Imported! Saved to {path}"
            self._status.color = list(TEXT_SUCCESS)
        except Exception as e:
            self._status.text = f"Import failed: {e}"
            self._status.color = list(TEXT_WARNING)

    def _import_ydk(self):
        text = self._ydk_input.text.strip()
        if not text:
            self._status.text = "Paste YDK content first"
            self._status.color = list(TEXT_WARNING)
            return
        try:
            deck = formats.ydk_to_json(text)
            path = self._dm.create_deck("Imported", "YDK Import", deck)
            self._status.text = f"Imported! Saved to {path}"
            self._status.color = list(TEXT_SUCCESS)
        except Exception as e:
            self._status.text = f"Import failed: {e}"
            self._status.color = list(TEXT_WARNING)

    def _export(self, fmt):
        self._status.text = "Select a deck first from My Decks"
        self._status.color = list(GOLD_DIM)
