"""Resource Packs — install card databases and manage content."""

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle

from widgets.stone_button import StoneButton
from widgets.stone_panel import StonePanel
from widgets.themed_scroll import ThemedScroll
from theme import (
    scaled,
    BG_VERTICAL, BG_HORIZONTAL, SCRIM, TEXT_PRIMARY, TEXT_SECONDARY,
    GOLD, GOLD_DIM, FONT_SIZE_TITLE, FONT_SIZE_LIST, FONT_SIZE_DETAIL,
    FONT_SIZE_SMALL, menu_font,
)


class ResourcePacksScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="resource_packs", **kwargs)
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
        back_btn = StoneButton(text="Back", size_hint_x=None, width=scaled(100))
        back_btn.bind(on_release=lambda _: setattr(self.manager, "current", "main_menu"))
        header.add_widget(back_btn)
        title_lbl = Label(
            text="Resources", font_size=FONT_SIZE_TITLE, color=TEXT_PRIMARY,
            bold=not face,
        )
        if face:
            title_lbl.font_name = face
        header.add_widget(title_lbl)
        column.add_widget(header)

        panel = StonePanel(orientation="vertical", size_hint=(1, 1))
        scroll = ThemedScroll(do_scroll_x=False)
        content = BoxLayout(
            orientation="vertical", size_hint_y=None, spacing=scaled(12),
            padding=[scaled(8), scaled(8)],
        )
        content.bind(minimum_height=content.setter("height"))

        # Card Database section
        content.add_widget(self._section_label("Card Database", face))
        content.add_widget(self._desc_label(
            "Card names, effects, stats. Required for card details and search."
        ))
        db_row = BoxLayout(size_hint_y=None, height=scaled(50), spacing=scaled(8))
        self._db_en_btn = StoneButton(text="English (EN)", font_size=FONT_SIZE_DETAIL)
        self._db_en_btn.height = 50
        self._db_en_btn.bind(on_release=lambda _: self._download_db("en"))
        db_row.add_widget(self._db_en_btn)
        self._db_es_btn = StoneButton(text="Spanish (ES)", font_size=FONT_SIZE_DETAIL)
        self._db_es_btn.height = 50
        self._db_es_btn.bind(on_release=lambda _: self._download_db("es"))
        db_row.add_widget(self._db_es_btn)
        content.add_widget(db_row)

        self._db_status = Label(
            text="", font_size=FONT_SIZE_SMALL, color=GOLD_DIM,
            size_hint_y=None, height=scaled(24), halign="left",
        )
        self._db_status.bind(size=self._db_status.setter("text_size"))
        content.add_widget(self._db_status)

        content.add_widget(Widget(size_hint_y=None, height=scaled(16)))

        # Card Images section
        content.add_widget(self._section_label("Card Images", face))
        content.add_widget(self._desc_label(
            "Images load on demand from the internet. No bulk download needed."
        ))

        content.add_widget(Widget(size_hint_y=None, height=scaled(16)))

        # Status
        content.add_widget(self._section_label("Status", face))
        self._info = Label(
            text="",
            font_size=FONT_SIZE_DETAIL, color=TEXT_SECONDARY,
            size_hint_y=None, height=scaled(60), halign="left", valign="top",
        )
        self._info.bind(size=self._info.setter("text_size"))
        content.add_widget(self._info)

        scroll.add_widget(content)
        panel.add_widget(scroll)
        column.add_widget(panel)
        root.add_widget(column)
        self.add_widget(root)

        from kivy.core.window import Window
        Window.bind(size=self._on_resize)

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
        self._check_status()

    def _check_status(self):
        import os
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(root, "data", "cards.cdb")
        if os.path.exists(db_path):
            size_mb = os.path.getsize(db_path) / (1024 * 1024)
            self._info.text = f"Card database: installed ({size_mb:.1f} MB)"
            self._db_status.text = "Database found"
            self._db_status.color = (0.533, 0.867, 0.533, 1)
        else:
            self._info.text = "Card database: not installed"
            self._db_status.text = "No database — install one below"
            self._db_status.color = list(GOLD_DIM)

    def _download_db(self, lang):
        import os
        import threading

        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(root, "data")
        os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, "cards.cdb")

        if lang == "en":
            url = "https://raw.githubusercontent.com/ProjectIgnis/BabelCDB/master/cards.cdb"
        else:
            url = "https://raw.githubusercontent.com/ryoken08/CDBEsp/master/cards.cdb"

        self._db_status.text = f"Installing ({lang.upper()})..."
        self._db_status.color = list(GOLD_DIM)

        def _do_download():
            import urllib.request
            try:
                req = urllib.request.Request(
                    url, headers={"User-Agent": "YGO-Deck-Archive/1.0"}
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = resp.read()
                with open(db_path, "wb") as f:
                    f.write(data)
                from kivy.clock import Clock
                Clock.schedule_once(lambda _: self._on_download_done(True), 0)
            except Exception as e:
                from kivy.clock import Clock
                Clock.schedule_once(lambda _, err=str(e): self._on_download_done(False, err), 0)

        t = threading.Thread(target=_do_download, daemon=True)
        t.start()

    def _on_download_done(self, success, error=""):
        if success:
            self._db_status.text = "Installed!"
            self._db_status.color = (0.533, 0.867, 0.533, 1)
            self._check_status()
        else:
            self._db_status.text = f"Failed: {error}"
            self._db_status.color = (0.867, 0.533, 0.533, 1)

    def _on_resize(self, window, size):
        w, h = size
        self._bg.source = BG_VERTICAL if h >= w else BG_HORIZONTAL
