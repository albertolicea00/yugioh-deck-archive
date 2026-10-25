# Yu-Gi-Oh! Deck Archive

Collection of Yu-Gi-Oh! video game decks in `.ydk` format, organized by platform and game.

## Platforms

| Platform | Console | Decks | Done | Progress | Tested |
|----------|---------|-------|------|----------|--------|
| PSP | PlayStation Portable | 82 | 0 | 0% | 0 |
| GBA | Game Boy Advance | 58 | 0 | 0% | 0 |
| DS | Nintendo DS | 46 | 0 | 0% | 0 |
| Multi | PC / Switch / PS4 / Xbox | 23 | 0 | 0% | 0 |
| PS2 | PlayStation 2 | 16 | 0 | 0% | 0 |
| PS1 | PlayStation 1 | 13 | 0 | 0% | 0 |
| Mobile | iOS / Android | 12 | 0 | 0% | 0 |
| 3DS | Nintendo 3DS | 11 | 0 | 0% | 0 |
| **Total** | | **261** | **0** | **0%** | **0** |

## Structure

```
decks/
├── [Platform] Game/
│   ├── [Platform] Game - Character.ydk
│   └── [Platform] Game - Boss Card - Deck Name.ydk
```

Each `.ydk` file follows the standard YGOPro deck format:
```
#created by @albertolicea00
#main
<card passcodes>
#extra
<card passcodes>
!side
<card passcodes>
```

See [decks/README.md](./decks/README.md) for the full index with links to every deck.

## Sources

- [YGOPRODeck](https://ygoprodeck.com/) — Community-uploaded decks with downloadable YDK files
- [Yugipedia - Deck Recipes](https://yugipedia.com/wiki/Deck_Recipes) — Complete character deck recipes per game with card names
- [Yugipedia - Forbidden Memories Card List](https://yugipedia.com/wiki/Yu-Gi-Oh!_Forbidden_Memories:_Card_List) — Full 722-card database with passcodes
- [Yu-Gi-Oh! Fandom Wiki](https://yugioh.fandom.com/) — Character pages with deck lists per game
