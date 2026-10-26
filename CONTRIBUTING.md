# Contributing

Contributions to deck research, corrections, scripts, documentation, and the interface are welcome. Please follow the [Code of Conduct](CODE_OF_CONDUCT.md) and read the [Legal Notice](LEGAL_NOTICE.md).

## Issues and suggestions

Search existing issues before opening a new one. Use the issue forms for bugs, deck additions or corrections, feature requests, and rights concerns. For a larger change, explain the proposal in an issue first so its scope can be discussed.

## Deck contributions

- Store decks as `.json` under `decks/[Platform] Game/` or `decks/[TV] Series Name/`.
- Follow nearby naming conventions: `[Platform] Game - Character.json` or `[Platform] Game - Opponent - Deck Name.json`. Use `[TV] Series Name - Character.json` for TV decks.
- Include `main`, `extra`, and `side` arrays of integer card passcodes. Repeat an ID for each copy. Use empty arrays for unused sections.
- Link the source in the pull request. Identify the game version, character, variant, or episode when relevant. Distinguish confirmed cards from inferred cards and explain substitutions.
- Preserve historical deck recipes. Some games and anime use different rules, unavailable cards, or nonstandard deck sizes. Explain validation exceptions rather than changing a sourced recipe just to satisfy modern limits.
- Do not present an empty placeholder as a completed or tested deck. State what was verified and what remains unknown.
- Do not commit generated `.ydk`, `.ydke`, `.txt`, or `.cod` exports or script caches.

Example:

```json
{
  "main": [89631139, 89631139, 46986414],
  "extra": [],
  "side": []
}
```

This example demonstrates the schema, not a complete deck.

## Local checks

The scripts use Python 3 and its standard library. Run checks on the files or directory you changed:

```bash
python3 scripts/deck-validate.py --check limits "decks/[PS1] Forbidden Memories"
python3 scripts/deck-validate.py --check ids,limits "decks/[PS1] Forbidden Memories"
python3 scripts/deck-convert.py ydk "decks/[PS1] Forbidden Memories"
```

ID checks query YGOPRODECK when IDs are not cached. Record unresolved IDs and known game-specific exceptions in the PR. For converter changes, exercise each affected format and check the resulting deck sections and card counts. For UI changes, include a screenshot or a short demonstration when useful.

If deck files are added, renamed, or removed, refresh the generated index and platform counts:

```bash
python3 .github/scripts/update-readme.py
```

## Pull requests

Fork the repository, create a focused branch, and submit a PR using the template. Explain the change, include sources for deck data, and report the checks you actually ran. Keep unrelated formatting and generated exports out of the PR.

## Rights and licensing

Submit original work or material you have permission to contribute, and identify any applicable third-party terms. Original code and original documentation contributions are submitted under the repository's [MIT License](LICENSE). This does not relicense third-party deck recipes, artwork, card text, trademarks, or other franchise material; see the [Legal Notice](LEGAL_NOTICE.md).

Link to reference material instead of uploading copyrighted assets without permission. Never include ROMs, extracted game assets, full card-image collections, episode files, credentials, or personal information.
