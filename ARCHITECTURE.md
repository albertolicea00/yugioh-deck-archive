# App Architecture

> Yu-Gi-Oh! Deck Manager — Kivy cross-platform application

---

## Overview

The app lives in `app/` and is a Kivy-based deck management tool for Yu-Gi-Oh! TCG. It supports browsing, editing, creating, validating, and importing/exporting decks across multiple formats.

---

## Directory Structure

```
app/
├── main.py              # Entry point — Kivy App, ScreenManager, DI
├── requirements.txt     # Python dependencies
├── assets/              # UI assets
│   ├── backgrounds/     # Temple background images (vertical + horizontal)
│   ├── frames/          # Stone slab nine-patch textures
│   └── icons/           # Menu icons, app icon
├── data/                # Runtime data (not committed)
│   ├── cards.cdb        # EDOPro card database (user-supplied)
│   └── cache/           # API response cache
├── screens/             # Kivy Screen subclasses
│   ├── main_menu.py     # Home — navigation to all features
│   ├── game_list.py     # Browse games/platforms
│   ├── deck_list.py     # Decks within a game
│   ├── deck_view.py     # View deck contents + validation
│   ├── deck_editor.py   # Edit/create decks with card search
│   ├── card_search.py   # Search card database
│   └── import_export.py # Import YDK/YDKE, export formats
├── widgets/             # Reusable themed widgets
│   ├── stone_button.py  # Stone slab button (nine-patch)
│   ├── stone_panel.py   # Dark panel with sandstone edge
│   └── card_grid.py     # Scrollable card image grid
├── core/                # Business logic (no Kivy dependency)
│   ├── deck_manager.py  # Deck CRUD (repo + user decks)
│   ├── card_db.py       # SQLite reader for cards.cdb
│   ├── card_api.py      # YGOPRODeck API client
│   ├── formats.py       # YDK/YDKE/TXT/COD converters
│   └── validation.py    # TCG rule validation
└── theme/               # Visual constants
    └── __init__.py      # Colors, fonts, paths, TCG limits, type flags
```

---

## Layers

```
┌────────────────────────────────┐
│         screens/               │  UI — Kivy Screens
├────────────────────────────────┤
│         widgets/               │  Themed components
├────────────────────────────────┤
│         theme/                 │  Visual constants
├────────────────────────────────┤
│         core/                  │  Business logic (pure Python)
└────────────────────────────────┘
```

**Rule: `core/` never imports Kivy.** All business logic is testable without a GUI.

---

## Data Sources

### Repo Decks (`decks/`)
- Read-only from the app's perspective
- JSON files organized by game: `decks/[Platform] Game Name/*.json`
- Format: `{"main": [int], "extra": [int], "side": [int]}`
- Card IDs are EDOPro passcodes (integers)

### User Decks (`user_decks/`)
- Created at runtime, writable
- Same JSON format as repo decks
- Organized by game folder

### Card Database (`app/data/cards.cdb`)
- EDOPro SQLite database — user-supplied, not committed
- Tables: `datas` (stats, type flags) + `texts` (name, description)
- ~14,700+ cards
- Source: [ProjectIgnis/BabelCDB](https://github.com/ProjectIgnis/BabelCDB)

---

## TCG Validation Rules

Enforced in `core/validation.py`:

| Rule | Constraint |
|---|---|
| Main deck size | 40–60 cards |
| Extra deck size | 0–15 cards |
| Side deck size | 0–15 cards |
| Card copies | Max 3 across all zones |
| Card placement | Extra deck monsters (Fusion/Synchro/Xyz/Link) must be in extra deck |
| Tokens | Cannot be in any deck |

### Card Type Flags (from `datas.type` bitmask)

| Flag | Value | Description |
|---|---|---|
| `TYPE_MONSTER` | `0x1` | Monster card |
| `TYPE_SPELL` | `0x2` | Spell card |
| `TYPE_TRAP` | `0x4` | Trap card |
| `TYPE_FUSION` | `0x40` | Fusion monster |
| `TYPE_RITUAL` | `0x80` | Ritual monster |
| `TYPE_SYNCHRO` | `0x2000` | Synchro monster |
| `TYPE_XYZ` | `0x800000` | Xyz monster |
| `TYPE_PENDULUM` | `0x1000000` | Pendulum monster |
| `TYPE_LINK` | `0x4000000` | Link monster |
| `TYPE_TOKEN` | `0x4000` | Token (not deckable) |

Extra deck = Fusion | Synchro | Xyz | Link.

---

## Navigation

```
MainMenu
├── GameList → DeckList → DeckView → DeckEditor
├── DeckEditor (new deck)
├── CardSearch
├── ImportExport
└── Settings (planned)
```

All navigation uses Kivy `ScreenManager`. Screens receive dependencies (deck_manager, card_db) via constructor injection.

---

## Deck Formats

| Format | Read | Write | Notes |
|---|---|---|---|
| JSON | ✓ | ✓ | Source of truth |
| YDK | ✓ | ✓ | EDOPro/YGOPro standard |
| YDKE | ✓ | ✓ | URL-encoded (clipboard sharing) |
| TXT | — | ✓ | Human readable, needs card names |
| COD | — | ✓ | Cockatrice XML |

---

## Card Images

Fetched from YGOPRODeck API:
- Small: `https://images.ygoprodeck.com/images/cards_small/{id}.jpg`
- Full: `https://images.ygoprodeck.com/images/cards/{id}.jpg`

Kivy `AsyncImage` handles lazy loading and caching.
