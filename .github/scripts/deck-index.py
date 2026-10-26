#!/usr/bin/env python3
"""Yu-Gi-Oh! Deck Index Generator

Scans decks/**/*.json and regenerates both README files:
  - decks/README.md  — full index with links to every deck
  - README.md        — updates the Platforms table counts

Preserves existing game/platform descriptions from decks/README.md.

Usage:
    python scripts/deck-index.py              # interactive confirmation
    python scripts/deck-index.py --yes        # skip confirmation
    python scripts/deck-index.py --dry-run    # preview without writing
"""

import os
import re
import sys
import urllib.parse

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)
DECKS_DIR = os.path.join(PROJECT_DIR, "decks")
DECKS_README = os.path.join(DECKS_DIR, "README.md")
ROOT_README = os.path.join(PROJECT_DIR, "README.md")

BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
YELLOW = "\033[0;33m"
RED = "\033[0;31m"
NC = "\033[0m"

PLATFORM_CONSOLES = {
    "3DS": "Nintendo 3DS",
    "DS": "Nintendo DS",
    "GBA": "Game Boy Advance",
    "Mobile": "iOS / Android",
    "Multi": "PC / Switch / PS4 / Xbox",
    "PS1": "PlayStation 1",
    "PS2": "PlayStation 2",
    "PSP": "PlayStation Portable",
    "TV": "Anime Series",
}

PLATFORM_BLURBS = {
    "3DS": "Nintendo 3DS — Portable console with stereoscopic 3D.",
    "DS": "Nintendo DS — Dual-screen portable console.",
    "GBA": "Game Boy Advance — Nintendo's 32-bit handheld.",
    "Mobile": "iOS / Android mobile devices.",
    "Multi": "Multi-Platform — Available on PC, Switch, PS4, Xbox and/or mobile.",
    "PS1": "PlayStation 1 — Sony's first home console.",
    "PS2": "PlayStation 2 — Sony's best-selling home console.",
    "PSP": "PlayStation Portable — Sony's first handheld console.",
    "TV": "TV Series — Anime character decks from every Yu-Gi-Oh! series.",
}


def scan_decks():
    """Scan decks/ for directories and .json files. Returns {dir_name: [filenames]}."""
    results = {}
    for entry in sorted(os.listdir(DECKS_DIR)):
        full = os.path.join(DECKS_DIR, entry)
        if not os.path.isdir(full):
            continue
        files = sorted(
            f for f in os.listdir(full) if f.endswith(".json")
        )
        if files:
            results[entry] = files
    return results


def parse_dir_name(dirname):
    """'[PSP] GX Tag Force 2' → ('PSP', 'GX Tag Force 2')"""
    m = re.match(r"^\[([^\]]+)\]\s+(.+)$", dirname)
    if m:
        return m.group(1), m.group(2)
    return None, dirname


def parse_deck_name(filename, dirname):
    """'[PSP] GX Tag Force 2 - Jaden Yuki.json' → 'Jaden Yuki'"""
    base = filename.rsplit(".", 1)[0]
    prefix = dirname + " - "
    if base.startswith(prefix):
        return base[len(prefix):]
    return base


def url_encode_path(dirname, filename):
    """Build URL-encoded relative link."""
    encoded_dir = urllib.parse.quote(dirname)
    encoded_file = urllib.parse.quote(filename)
    return f"./{encoded_dir}/{encoded_file}"


def parse_existing_descriptions(path):
    """Parse decks/README.md for game descriptions. Returns {game_name: description_line}."""
    descriptions = {}
    if not os.path.exists(path):
        return descriptions
    with open(path) as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if line.startswith("### "):
            game = line[4:].strip()
            if i + 1 < len(lines) and lines[i + 1].strip() and not lines[i + 1].startswith("-") and not lines[i + 1].startswith("#"):
                descriptions[game] = lines[i + 1].rstrip()
        i += 1
    return descriptions


def generate_decks_readme(deck_map, descriptions):
    """Generate full decks/README.md content."""
    platforms = {}
    for dirname, files in deck_map.items():
        plat, game = parse_dir_name(dirname)
        if plat is None:
            plat = "Other"
        if plat not in platforms:
            platforms[plat] = []
        platforms[plat].append((game, dirname, files))

    for plat in platforms:
        platforms[plat].sort(key=lambda x: x[0])

    lines = ["# Decks Index", "", "Collection of Yu-Gi-Oh! decks organized by platform, game, and TV series.", ""]

    for plat in sorted(platforms.keys()):
        blurb = PLATFORM_BLURBS.get(plat, "")
        lines.append(f"## {plat}")
        if blurb:
            lines.append(blurb)
        lines.append("")

        for game, dirname, files in platforms[plat]:
            lines.append(f"### {game}")
            desc = descriptions.get(game, "")
            if desc:
                lines.append(desc)
            for f in files:
                name = parse_deck_name(f, dirname)
                link = url_encode_path(dirname, f)
                lines.append(f"- [{name}]({link})")
            lines.append("")

        lines.append("---")
        lines.append("")

    if lines and lines[-1] == "":
        lines.pop()
    if lines and lines[-1] == "---":
        lines.pop()

    lines.append("")
    return "\n".join(lines)


def update_root_readme(deck_map):
    """Update Platforms table in README.md with current counts."""
    if not os.path.exists(ROOT_README):
        return False

    platform_counts = {}
    for dirname, files in deck_map.items():
        plat, _ = parse_dir_name(dirname)
        if plat is None:
            plat = "Other"
        platform_counts[plat] = platform_counts.get(plat, 0) + len(files)

    with open(ROOT_README) as f:
        content = f.read()

    table_pattern = re.compile(
        r"(\| Platform \| Console \| Decks \| Done \| Progress \| Tested \|\n"
        r"\|[-|]+\|\n)"
        r"((?:\|[^\n]*\n)*)"
        r"(\| \*\*Total\*\*[^\n]*\n)",
        re.MULTILINE,
    )

    m = table_pattern.search(content)
    if not m:
        return False

    existing_rows = {}
    for row_line in m.group(2).strip().split("\n"):
        cols = [c.strip() for c in row_line.split("|")]
        if len(cols) >= 7:
            plat_name = cols[1]
            existing_rows[plat_name] = {
                "console": cols[2],
                "done": cols[4],
                "progress": cols[5],
                "tested": cols[6],
            }

    new_rows = []
    total = 0
    total_done = 0
    for plat in sorted(platform_counts.keys()):
        count = platform_counts[plat]
        total += count
        console = PLATFORM_CONSOLES.get(plat, "")
        done = "0"
        progress = "0%"
        tested = "0"
        if plat in existing_rows:
            console = existing_rows[plat]["console"] or console
            done = existing_rows[plat]["done"]
            progress = existing_rows[plat]["progress"]
            tested = existing_rows[plat]["tested"]
        try:
            total_done += int(done)
        except ValueError:
            pass
        new_rows.append(f"| {plat} | {console} | {count} | {done} | {progress} | {tested} |")

    total_progress = f"{round(total_done / total * 100)}%" if total > 0 else "0%"
    total_line = f"| **Total** | | **{total}** | **{total_done}** | **{total_progress}** | **0** |"

    replacement = m.group(1) + "\n".join(new_rows) + "\n" + total_line + "\n"
    new_content = content[:m.start()] + replacement + content[m.end():]

    with open(ROOT_README, "w") as f:
        f.write(new_content)
    return True


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    auto_yes = "--yes" in args

    print(f"{BOLD}Scanning decks...{NC}")
    deck_map = scan_decks()

    total_dirs = len(deck_map)
    total_files = sum(len(f) for f in deck_map.values())

    platform_counts = {}
    for dirname in deck_map:
        plat, _ = parse_dir_name(dirname)
        if plat:
            platform_counts[plat] = platform_counts.get(plat, 0) + len(deck_map[dirname])

    print(f"  {CYAN}{total_dirs}{NC} game directories")
    print(f"  {CYAN}{total_files}{NC} deck files")
    print(f"  {CYAN}{len(platform_counts)}{NC} platforms: {', '.join(f'{k} ({v})' for k, v in sorted(platform_counts.items()))}")
    print()

    if dry_run:
        print(f"{YELLOW}Dry run — no files written.{NC}")
        return

    if not auto_yes:
        answer = input(f"Regenerate both READMEs? [y/N]: ").strip().lower()
        if answer != "y":
            print(f"{DIM}Cancelled.{NC}")
            return

    descriptions = parse_existing_descriptions(DECKS_README)
    print(f"  {DIM}Preserved {len(descriptions)} game descriptions{NC}")

    decks_content = generate_decks_readme(deck_map, descriptions)
    with open(DECKS_README, "w") as f:
        f.write(decks_content)
    print(f"{GREEN}Updated: decks/README.md{NC}")

    if update_root_readme(deck_map):
        print(f"{GREEN}Updated: README.md (Platforms table){NC}")
    else:
        print(f"{YELLOW}Warning: Could not find Platforms table in README.md{NC}")

    print(f"\n{GREEN}Done. {total_files} decks indexed.{NC}")


if __name__ == "__main__":
    main()
