# App Architecture

> Yu-Gi-Oh! Deck Manager — Kivy cross-platform application

---

## Overview

Kivy-based deck management tool for Yu-Gi-Oh! TCG. Supports browsing, editing, creating, validating, and importing/exporting decks across multiple formats.

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

### Card Database (`data/cards.cdb`)
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
