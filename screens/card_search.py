"""Card search — search by name, type, attribute."""

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image, AsyncImage
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle

from widgets.stone_button import StoneButton
from widgets.stone_panel import StonePanel
from widgets.card_grid import CardGrid
from core.card_api import card_image_url, card_image_url_full
from theme import (
    BG_VERTICAL, SCRIM, TEXT_PRIMARY, TEXT_SECONDARY,
    FONT_SIZE_TITLE, FONT_SIZE_LIST, FONT_SIZE_DETAIL, FONT_SIZE_SMALL,
    DARK_PANEL, GOLD_DIM,
)


class CardSearchScreen(Screen):
    def __init__(self, card_db=None, **kwargs):
        super().__init__(name="card_search", **kwargs)
        self._card_db = card_db
        self._build_ui()

    def _build_ui(self):
        root = FloatLayout()

        bg = Image(source=BG_VERTICAL, fit_mode="cover", size_hint=(1, 1))
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
            size_hint=(0.95, 0.95),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            spacing=6,
        )

        # Header
        header = BoxLayout(size_hint_y=None, height=50, spacing=10)
        back_btn = StoneButton(text="Back", size_hint_x=None, width=90)
        back_btn.bind(on_release=lambda _: setattr(self.manager, "current", "main_menu"))
        header.add_widget(back_btn)
        header.add_widget(Label(
            text="Card Search", font_size=FONT_SIZE_TITLE, color=TEXT_PRIMARY, bold=True,
        ))
        column.add_widget(header)

        # Search bar
        search_row = BoxLayout(size_hint_y=None, height=44, spacing=6)
        self._search_input = TextInput(
            hint_text="Search by name or description...",
            multiline=False,
            size_hint=(1, 1),
            background_color=list(DARK_PANEL),
            foreground_color=list(TEXT_PRIMARY),
            cursor_color=list(TEXT_PRIMARY),
        )
        self._search_input.bind(on_text_validate=lambda _: self._do_search())
        search_row.add_widget(self._search_input)
        search_btn = StoneButton(text="Search", size_hint_x=None, width=100)
        search_btn.bind(on_release=lambda _: self._do_search())
        search_row.add_widget(search_btn)
        column.add_widget(search_row)

        # Results count
        self._count_label = Label(
            text="", font_size=FONT_SIZE_SMALL, color=GOLD_DIM,
            size_hint_y=None, height=20, halign="left",
        )
        self._count_label.bind(size=self._count_label.setter("text_size"))
        column.add_widget(self._count_label)

        # Split: grid left, detail right
        body = BoxLayout(orientation="horizontal", spacing=8)

        # Card grid
        grid_panel = StonePanel(orientation="vertical", size_hint_x=0.55)
        self._grid = CardGrid(columns=3)
        grid_panel.add_widget(self._grid)
        body.add_widget(grid_panel)

        # Card detail
        detail_panel = StonePanel(orientation="vertical", size_hint_x=0.45)
        self._card_image = AsyncImage(
            size_hint=(1, None), height=200,
            fit_mode="contain",
        )
        detail_panel.add_widget(self._card_image)

        detail_scroll = ScrollView(do_scroll_x=False)
        self._detail = Label(
            text="Select a card to view details",
            font_size=FONT_SIZE_DETAIL,
            color=TEXT_SECONDARY,
            markup=True,
            size_hint_y=None,
            halign="left",
            valign="top",
        )
        self._detail.bind(texture_size=self._detail.setter("size"))
        self._detail.bind(size=lambda w, s: setattr(w, "text_size", (w.width, None)))
        detail_scroll.add_widget(self._detail)
        detail_panel.add_widget(detail_scroll)
        body.add_widget(detail_panel)

        column.add_widget(body)
        root.add_widget(column)
        self.add_widget(root)

    def _do_search(self):
        query = self._search_input.text.strip()
        if not query or not self._card_db:
            return
        results = self._card_db.search(query, limit=50)
        self._count_label.text = f"{len(results)} result(s)"
        display = [(r["id"], r["name"], 0) for r in results]
        self._grid.set_cards(
            display, image_fn=card_image_url,
            on_tap=self._show_detail,
        )

    def _show_detail(self, card_id):
        if not self._card_db:
            return
        card = self._card_db.get_card(card_id)
        if card is None:
            self._detail.text = f"Card {card_id} not found"
            return

        self._card_image.source = card_image_url_full(card_id)

        lines = []
        lines.append(f"[b]{card['name']}[/b]")
        lines.append("")

        card_type = card["type"]
        type_parts = []
        from theme import (
            TYPE_MONSTER, TYPE_SPELL, TYPE_TRAP, TYPE_FUSION,
            TYPE_SYNCHRO, TYPE_XYZ, TYPE_LINK, TYPE_PENDULUM, TYPE_RITUAL,
        )
        if card_type & TYPE_MONSTER:
            type_parts.append("Monster")
        if card_type & TYPE_SPELL:
            type_parts.append("Spell")
        if card_type & TYPE_TRAP:
            type_parts.append("Trap")
        if card_type & TYPE_FUSION:
            type_parts.append("Fusion")
        if card_type & TYPE_SYNCHRO:
            type_parts.append("Synchro")
        if card_type & TYPE_XYZ:
            type_parts.append("Xyz")
        if card_type & TYPE_LINK:
            type_parts.append("Link")
        if card_type & TYPE_PENDULUM:
            type_parts.append("Pendulum")
        if card_type & TYPE_RITUAL:
            type_parts.append("Ritual")
        lines.append(f"Type: {' / '.join(type_parts)}")

        if card_type & TYPE_MONSTER:
            atk = card["atk"]
            defn = card["def"]
            level = card["level"] & 0xFF
            if card_type & TYPE_LINK:
                lines.append(f"ATK: {atk}  LINK-{level}")
            elif card_type & TYPE_XYZ:
                lines.append(f"ATK: {atk}  DEF: {defn}  Rank {level}")
            else:
                lines.append(f"ATK: {atk}  DEF: {defn}  Level {level}")

        lines.append("")
        lines.append(card.get("desc", ""))
        lines.append("")
        lines.append(f"[i]ID: {card_id}[/i]")

        self._detail.text = "\n".join(lines)
