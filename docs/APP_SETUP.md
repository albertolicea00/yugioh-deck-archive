# App Setup Guide

> How to set up and run the Yu-Gi-Oh! Deck Manager app

---

## Prerequisites

- Python 3.10+
- pip

---

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- **Kivy** — cross-platform UI framework
- **Pillow** — image processing
- **requests** — HTTP client for API calls

---

## 2. Card Database (Optional but Recommended)

The app can browse decks without it, but card search, names, and validation need the database.

```bash
mkdir -p data

# Download the EDOPro card database (English)
curl -L -o data/cards.cdb \
  "https://raw.githubusercontent.com/ProjectIgnis/BabelCDB/master/cards.cdb"
```

For Spanish:
```bash
curl -L -o data/cards.cdb \
  "https://raw.githubusercontent.com/ryoken08/CDBEsp/master/cards.cdb"
```

---

## 3. Run

```bash
python main.py
```

The app will open a window with the Egyptian temple menu. Navigate to "My Decks" to browse the `decks/` folder.

---

## 4. User Decks

User-created decks are saved to `user_decks/` at the project root (sibling of `decks/`). This directory is created automatically.

---

## Project Structure

```
yugioh-deck-manager/
├── main.py          # Entry point — run this
├── requirements.txt # Python dependencies
├── decks/           # Repository decks (read-only from app)
├── user_decks/      # User-created decks (read-write)
├── screens/         # Kivy screens
├── widgets/         # UI components
├── core/            # Business logic
├── theme/           # Visual constants
├── assets/          # UI assets (backgrounds, frames, icons)
├── data/            # Card database goes here (gitignored)
├── scripts/         # CLI tools (deck-convert.py, etc.)
└── docs/            # Documentation
```

---

## Troubleshooting

### "Card database not found"
Place `cards.cdb` in `data/`. See step 2.

### No card images loading
Card images are fetched from YGOPRODeck's public API. Requires internet connection. Cached by Kivy's AsyncImage.

### Kivy window too small / too large
Kivy respects the system's DPI settings. To force a size:
```bash
KIVY_METRICS_DENSITY=1 python main.py
```

### Import errors on startup
Make sure you're running from the project root so Python can find the local modules.
