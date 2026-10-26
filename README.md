# Yu-Gi-Oh! Deck Archive

Manage, explore, and preserve Yu-Gi-Oh! decks from video games and TV series. Decks stored in `.json` format, organized by platform and game.

## Platforms

| Platform | Console | Decks | Done | Progress | Tested |
|----------|---------|-------|------|----------|--------|
| TV | Anime Series | 118 | 0 | 0% | 0 |
| PSP | PlayStation Portable | 82 | 0 | 0% | 0 |
| GBA | Game Boy Advance | 53 | 0 | 0% | 0 |
| DS | Nintendo DS | 46 | 0 | 0% | 0 |
| Multi | PC / Switch / PS4 / Xbox | 23 | 0 | 0% | 0 |
| PS2 | PlayStation 2 | 16 | 0 | 0% | 0 |
| PS1 | PlayStation 1 | 13 | 0 | 0% | 0 |
| Mobile | iOS / Android | 12 | 0 | 0% | 0 |
| 3DS | Nintendo 3DS | 11 | 0 | 0% | 0 |
| **Total** | | **374** | **0** | **0%** | **0** |

## Structure

```
decks/
├── [Platform] Game/
│   ├── [Platform] Game - Character.json
│   └── [Platform] Game - Opponent - Deck Name.json
├── [TV] Series Name/
│   └── [TV] Series Name - Character.json
scripts/
├── deck-convert.py    # Format converter (JSON ↔ YDK, YDKE, TXT, COD)
└── deck-validate.py   # Deck validator (structure, limits, card IDs)
```

Each `.json` deck file is the source of truth:
```json
{
  "main": [89631139, 46986414],
  "extra": [39030163],
  "side": []
}
```

Other formats (`.ydk`, `.ydke`, `.txt`, `.cod`) are generated via `deck-convert.py` and gitignored.

## Tools

```bash
python scripts/deck-convert.py      # Convert between formats (JSON ↔ YDK, YDKE, TXT, COD)
python scripts/deck-validate.py     # Validate decks (structure, limits, card IDs)
```

Both have interactive menus. Run without arguments to use.

## Documentation

- [decks/README.md](./decks/README.md) — Full index with links to every deck
- [ARCHITECTURE.md](./ARCHITECTURE.md) — Deck file formats, passcode system, Konami apps, APIs and conversion
- [CHANGELOG.md](./CHANGELOG.md) — Version history

## Related Project

[Project Kaiba](https://github.com/albertolicea00/ProjectKaiba) — My personal, fan-made Yu-Gi-Oh! game for mobile, built for offline duels and playing with friends.

## Contributing and Community

See [CONTRIBUTING.md](./CONTRIBUTING.md) for deck conventions, sources, validation, and pull requests. Please follow the [Code of Conduct](./CODE_OF_CONDUCT.md). Use the repository's issue forms to report bugs, suggest features, request deck changes, or raise rights concerns.

## License and Legal Notice

Original code and original documentation are licensed under the [MIT License](./LICENSE). Third-party artwork, images, logos, trademarks, card text, and other Yu-Gi-Oh! material are excluded and remain the property of Konami and their respective rights holders. No license to third-party rights in sourced deck recipes is granted here.

This is an unofficial fan project, not affiliated with or endorsed by Konami. See [LEGAL_NOTICE.md](./LEGAL_NOTICE.md) for the full scope and rights reporting process.

## Sources

- [YGOPRODeck](https://ygoprodeck.com/) — Community-uploaded decks with downloadable YDK files
- [YGOPRODeck API](https://db.ygoprodeck.com/api/v7/cardinfo.php) — Card data, images, passcodes
- [Yugipedia - Deck Recipes](https://yugipedia.com/wiki/Deck_Recipes) — Complete character deck recipes per game
- [Yugipedia - Forbidden Memories Card List](https://yugipedia.com/wiki/Yu-Gi-Oh!_Forbidden_Memories:_Card_List) — Full 722-card database
- [Yu-Gi-Oh! Fandom Wiki](https://yugioh.fandom.com/) — Character pages with deck lists per game
- [YGOJSON](https://github.com/iconmaster5326/YGOJSON) — Machine-readable JSON card database
- [Konami Card Database](https://www.db.yugioh-card.com/) — Official card database with rulings
