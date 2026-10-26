# Architecture

## Deck File Formats

All formats share the same card identification system: **Konami passcodes**. These are unique 8-digit numbers assigned to each card, printed on the physical cards. A passcode like `89631139` (Blue-Eyes White Dragon) is the same across every format, platform, and region.

The difference between formats is structure, not data.

### YDK

The standard deck format used by most simulators.

```
#created by yourusername
#main
89631139
46986414
#extra
39030163
!side
```

- Plain text, one passcode per line
- Sections: `#main`, `#extra`, `!side`
- First line `#created by` is optional metadata
- Used by: [YGOPro](https://github.com/Fluorohydride/ygopro), [EDOPro](https://projectignis.github.io/), [Dueling Nexus](https://duelingnexus.com/), [Dueling Book](https://www.duelingbook.com/)
- This project uses YDK as its primary format

### YDKE

Compact URL format used by EDOPro and YGOPRODeck for deck sharing.

```
ydke://<main_b64>!<extra_b64>!<side_b64>!
```

- Each segment is base64-encoded passcodes packed as 32-bit little-endian integers
- Empty segments allowed (e.g. `ydke://rvTMAhLZoAI=!/WccAA==!!` — no side deck)
- Convertible 1:1 to/from YDK — same passcode data, different encoding
- Used by: [EDOPro](https://projectignis.github.io/), [YGOPRODeck](https://ygoprodeck.com/)

### YDOG

Native format for YGO Omega.

- Binary/proprietary format
- Contains deck metadata + passcodes
- Used by: [YGO Omega](https://omega.duelistsunite.org/)
- Omega also supports importing YDK files

### JSON

Structured format with card metadata.

```json
{
  "main": [89631139, 46986414],
  "extra": [39030163],
  "side": []
}
```

- Machine-readable, easy to parse programmatically
- Often includes card names, types, and other metadata alongside passcodes
- Used by: [YGOPRODeck API](https://ygoprodeck.com/api-guide/), custom tools
- YGOPRODeck API endpoint: `https://db.ygoprodeck.com/api/v7/cardinfo.php`

### KDE

Legacy format from Kaiba Dueling Engine.

- XML-based structure
- Mostly obsolete
- Used by: Kaiba Dueling Engine (discontinued)

### COD

Cockatrice deck format.

```xml
<cockatrice_deck>
  <zone name="main">
    <card number="3" name="Blue-Eyes White Dragon"/>
  </zone>
</cockatrice_deck>
```

- XML-based, uses card names instead of passcodes
- Multi-TCG tool (Magic, Yu-Gi-Oh!, Pokemon)
- Used by: [Cockatrice](https://cockatrice.github.io/)

### TXT

Plain text card name lists.

```
3x Blue-Eyes White Dragon
2x Dark Magician
1x Pot of Greed
```

- Human-readable, no standard structure
- Varies by source (some use `3x`, some use `3 `, some just list names)
- Used by: Forum posts, deck sharing sites, casual sharing

### DEC

Legacy format from early dueling programs.

- Plain text with card names
- No universal standard
- Used by: Various discontinued simulators

## Passcode System

Konami assigns a unique passcode to every card. This number is:

- Printed on the bottom-left corner of physical cards
- Consistent across OCG (Japan) and TCG (international) versions
- Permanent — never changes once assigned
- The universal identifier used by all digital platforms

Example passcodes:

| Passcode | Card |
|----------|------|
| `89631139` | Blue-Eyes White Dragon |
| `46986414` | Dark Magician |
| `24094653` | Polymerization |
| `55144522` | Pot of Greed |
| `53129443` | Mystical Space Typhoon |

## Converting Between Formats

Since all formats reference the same passcodes, conversion is lossless:

- **YDK → JSON**: Parse lines, wrap in JSON structure
- **JSON → YDK**: Extract passcode arrays, write one per line
- **TXT → YDK**: Look up card names → passcodes via [YGOPRODeck API](https://db.ygoprodeck.com/api/v7/cardinfo.php?name=Blue-Eyes%20White%20Dragon)
- **YDK → TXT**: Look up passcodes → card names via [YGOPRODeck API](https://db.ygoprodeck.com/api/v7/cardinfo.php?id=89631139)

## Official Konami Apps & Games

None of Konami's official apps export deck files natively. Decks live on Konami's servers, tied to a Konami ID.

| App/Game | Export nativo | Interop |
|----------|--------------|---------|
| **Neuron** (companion app) | ✗ | Via browser extension → .ydk. Decks stored internally, linked to Konami ID. |
| **Master Duel** | ✗ | Via [Deck Transfer extension](https://ygoprodeck.com/decks/transfer-tool) → .ydk/ydke://. Routes through Konami DB (db.yugioh-card.com). |
| **Duel Links** | ✗ | Manual entry or screenshot OCR. Sites like [DuelLinksMeta](https://www.duellinksmeta.com/) have their own URL sharing. |

The community standard for interchange remains `.ydk` — all transfer tools convert to/from it.

## APIs and Data Sources

| Source | URL | Provides |
|--------|-----|----------|
| YGOPRODeck API | https://db.ygoprodeck.com/api/v7/cardinfo.php | Card data, images, passcodes, prices |
| Yugipedia | https://yugipedia.com/ | Game-specific deck recipes, card lists, character info |
| Yu-Gi-Oh! Fandom Wiki API | https://yugioh.fandom.com/api.php | Game decklists via MediaWiki API (wikitext parsing) |
| YGOJSON | https://github.com/iconmaster5326/YGOJSON | Machine-readable JSON card database |
| Konami Card DB | https://www.db.yugioh-card.com/ | Official card database with rulings |
