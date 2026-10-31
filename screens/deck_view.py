"""Deck viewer — split layout: card grid left, preview + details right."""

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image, AsyncImage
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle

from widgets.stone_button import StoneButton
from widgets.stone_panel import StonePanel
from widgets.card_grid import CardGrid
from widgets.breadcrumb_bar import BreadcrumbBar
from widgets.themed_scroll import ThemedScroll
from core.card_api import card_image_url, card_image_url_full
from theme import (
    scaled,
    BG_VERTICAL, SCRIM, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_WARNING, TEXT_SUCCESS,
    FONT_SIZE_TITLE, FONT_SIZE_LIST, FONT_SIZE_DETAIL, FONT_SIZE_SMALL, GOLD_DIM,
    TYPE_MONSTER, TYPE_SPELL, TYPE_TRAP, TYPE_FUSION,
    TYPE_SYNCHRO, TYPE_XYZ, TYPE_LINK, TYPE_PENDULUM, TYPE_RITUAL,
    menu_font,
)


class DeckViewScreen(Screen):
    def __init__(self, deck_manager=None, card_db=None, **kwargs):
        super().__init__(name="deck_view", **kwargs)
        self._dm = deck_manager
        self._card_db = card_db
        self._deck_info = None
        self._deck = None
        self._current_tab = "main"
        self._build_ui()

    def set_deck(self, deck_info, game_name=""):
        self._deck_info = deck_info
        self._game_name = game_name

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
            spacing=scaled(6),
        )

        face = menu_font()

        header = BoxLayout(size_hint_y=None, height=scaled(40), spacing=scaled(8))
        self._breadcrumb = BreadcrumbBar(height=scaled(40), size_hint_x=1)
        self._breadcrumb.bind(on_navigate=self._on_breadcrumb_nav)
        header.add_widget(self._breadcrumb)

        edit_btn = StoneButton(text="Edit", size_hint_x=None, width=scaled(90))
        edit_btn.bind(on_release=lambda _: self._edit())
        header.add_widget(edit_btn)
        column.add_widget(header)

        # Status + tabs row
        info_row = BoxLayout(size_hint_y=None, height=scaled(36), spacing=scaled(8))
        self._status = Label(
            text="", font_size=FONT_SIZE_SMALL, color=TEXT_SUCCESS,
            size_hint_x=0.4, halign="left", valign="middle",
        )
        self._status.bind(size=self._status.setter("text_size"))
        info_row.add_widget(self._status)

        for tab_name in ["Main", "Extra", "Side"]:
            btn = StoneButton(text=tab_name, font_size=FONT_SIZE_SMALL)
            btn.bind(on_release=lambda _, t=tab_name.lower(): self._show_tab(t))
            info_row.add_widget(btn)
        column.add_widget(info_row)

        # Split body: grid left, preview right
        body = BoxLayout(orientation="horizontal", spacing=scaled(8))

        # Left: card grid
        grid_panel = StonePanel(orientation="vertical", size_hint_x=0.55)
        self._grid = CardGrid(columns=5)
        grid_panel.add_widget(self._grid)
        body.add_widget(grid_panel)

        # Right: card preview + details
        right = BoxLayout(orientation="vertical", size_hint_x=0.45, spacing=scaled(6))

        # Card image
        img_panel = StonePanel(orientation="vertical", size_hint_y=0.55)
        self._card_image = AsyncImage(
            size_hint=(1, 1),
            fit_mode="contain",
        )
        img_panel.add_widget(self._card_image)
        right.add_widget(img_panel)

        # Card details
        detail_panel = StonePanel(orientation="vertical", size_hint_y=0.45)
        detail_scroll = ThemedScroll(do_scroll_x=False)
        self._detail = Label(
            text="Tap a card to view details",
            font_size=FONT_SIZE_DETAIL,
            color=TEXT_SECONDARY,
            markup=True,
            size_hint_y=None,
            halign="left",
            valign="top",
            padding=[scaled(8), scaled(8)],
        )
        self._detail.bind(
            texture_size=lambda w, s: setattr(w, "height", s[1] + scaled(16)),
        )
        self._detail.bind(
            size=lambda w, s: setattr(w, "text_size", (w.width - scaled(16), None)),
        )
        detail_scroll.add_widget(self._detail)
        detail_panel.add_widget(detail_scroll)
        right.add_widget(detail_panel)

        body.add_widget(right)
        column.add_widget(body)

        root.add_widget(column)
        self.add_widget(root)

    def on_enter(self):
        self._load()

    def _on_breadcrumb_nav(self, _, screen_name):
        self.manager.current = screen_name

    def _load(self):
        if self._deck_info is None or self._dm is None:
            return
        game = getattr(self, "_game_name", "")
        crumbs = [{"label": "Menu", "screen": "main_menu"},
                  {"label": "My Decks", "screen": "game_list"}]
        if game:
            crumbs.append({"label": game, "screen": "deck_list"})
        crumbs.append({"label": self._deck_info["name"], "screen": None})
        self._breadcrumb.set_crumbs(crumbs)
        self._deck = self._dm.read_deck(self._deck_info["path"])
        self._card_image.source = ""
        self._detail.text = "Tap a card to view details"
        self._detail.color = list(TEXT_SECONDARY)
        self._validate()
        self._show_tab("main")

    def _validate(self):
        if self._deck is None:
            return
        from core.validation import validate_deck
        issues = validate_deck(self._deck, self._card_db)
        errors = [m for s, m in issues if s == "error"]
        warnings = [m for s, m in issues if s == "warning"]
        m = len(self._deck.get("main", []))
        e = len(self._deck.get("extra", []))
        s = len(self._deck.get("side", []))
        counts = f"Main: {m}  Extra: {e}  Side: {s}"
        if errors:
            self._status.text = f"{counts} — {len(errors)} error(s)"
            self._status.color = list(TEXT_WARNING)
        elif warnings:
            self._status.text = f"{counts} — {len(warnings)} warning(s)"
            self._status.color = [0.9, 0.8, 0.4, 1]
        else:
            self._status.text = f"{counts} — Valid"
            self._status.color = list(TEXT_SUCCESS)

    def _show_tab(self, tab):
        self._current_tab = tab
        if self._deck is None:
            return
        cards = self._deck.get(tab, [])

        def name_fn(cid):
            if self._card_db:
                return self._card_db.get_name(cid)
            return str(cid)

        display = [(cid, name_fn(cid), 1) for cid in cards]
        self._grid.set_cards(
            display, image_fn=card_image_url,
            on_tap=self._show_card,
        )

    def _show_card(self, card_id):
        self._card_image.source = card_image_url_full(card_id)

        if not self._card_db:
            self._detail.text = f"Card ID: {card_id}"
            self._detail.color = list(TEXT_PRIMARY)
            return

        card = self._card_db.get_card(card_id)
        if card is None:
            self._detail.text = f"Card {card_id} not in database"
            self._detail.color = list(TEXT_SECONDARY)
            return

        lines = [f"[b]{card['name']}[/b]", ""]

        card_type = card["type"]
        type_parts = []
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
        lines.append(" / ".join(type_parts))

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

        self._detail.text = "\n".join(lines)
        self._detail.color = list(TEXT_PRIMARY)

    def _edit(self):
        if self._deck_info is None:
            return
        editor = self.manager.get_screen("deck_editor")
        editor.set_deck(self._deck_info)
        self.manager.current = "deck_editor"
