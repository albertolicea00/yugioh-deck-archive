#!/usr/bin/env python3
"""Yu-Gi-Oh! Deck Format Converter

Source of truth: decks/**/*.json
Converts JSON ↔ YDK, JSON → YDKE, JSON → TXT, JSON → COD

Usage:
    python scripts/deck-convert.py                          # interactive menu
    python scripts/deck-convert.py ydk                      # export all → ydk
    python scripts/deck-convert.py ydk "decks/[PS1] Forbidden Memories"
    python scripts/deck-convert.py import deck.ydk          # import ydk → json
"""

import base64
import json
import os
import struct
import sys
import time
import urllib.request
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)
DECKS_DIR = os.path.join(PROJECT_DIR, "decks")
NAMES_CACHE_FILE = os.path.join(SCRIPTS_DIR, ".card_names_cache.json")

BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
YELLOW = "\033[0;33m"
RED = "\033[0;31m"
NC = "\033[0m"

# ══════════════════════════════════════
# Card name cache (for TXT and COD)
# ══════════════════════════════════════

_names_cache = None
_names_dirty = False


def _load_names_cache():
    global _names_cache
    if _names_cache is None:
        if os.path.exists(NAMES_CACHE_FILE):
            with open(NAMES_CACHE_FILE) as f:
                _names_cache = json.load(f)
        else:
            _names_cache = {}
    return _names_cache


def _save_names_cache():
    if _names_dirty and _names_cache:
        with open(NAMES_CACHE_FILE, "w") as f:
            json.dump(_names_cache, f, indent=1, sort_keys=True)


def lookup_name(passcode):
    global _names_dirty
    cache = _load_names_cache()
    key = str(passcode)
    if key in cache:
        return cache[key]
    url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?id={passcode}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "YGO-Deck-Manager/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            if "data" in data and data["data"]:
                name = data["data"][0]["name"]
                cache[key] = name
                _names_dirty = True
                return name
    except Exception:
        pass
    return key


# ══════════════════════════════════════
# JSON helpers
# ══════════════════════════════════════

def read_deck(path):
    with open(path) as f:
        return json.load(f)


def write_deck(path, deck):
    with open(path, "w") as f:
        json.dump(deck, f, indent=2)
        f.write("\n")


def count_cards(cards):
    counted = {}
    order = []
    for c in cards:
        if c not in counted:
            order.append(c)
            counted[c] = 0
        counted[c] += 1
    return [(name, counted[name]) for name in order]


# ══════════════════════════════════════
# Converters
# ══════════════════════════════════════

def json_to_ydk(src):
    deck = read_deck(src)
    dst = os.path.splitext(src)[0] + ".ydk"
    with open(dst, "w") as f:
        f.write("#created by yugioh-deck-manager\n")
        f.write("#main\n")
        for c in deck.get("main", []):
            f.write(f"{c}\n")
        f.write("#extra\n")
        for c in deck.get("extra", []):
            f.write(f"{c}\n")
        f.write("!side\n")
        for c in deck.get("side", []):
            f.write(f"{c}\n")


def json_to_ydke(src):
    deck = read_deck(src)
    dst = os.path.splitext(src)[0] + ".ydke"

    def encode(cards):
        return base64.b64encode(
            b"".join(struct.pack("<I", int(c)) for c in cards)
        ).decode()

    main = encode(deck.get("main", []))
    extra = encode(deck.get("extra", []))
    side = encode(deck.get("side", []))
    with open(dst, "w") as f:
        f.write(f"ydke://{main}!{extra}!{side}!\n")


def json_to_txt(src):
    deck = read_deck(src)
    dst = os.path.splitext(src)[0] + ".txt"
    lines = []
    for label, key in [("Main Deck", "main"), ("Extra Deck", "extra"), ("Side Deck", "side")]:
        cards = deck.get(key, [])
        if not cards:
            continue
        lines.append(f"== {label} ==")
        resolved = [(lookup_name(c), c) for c in cards]
        for name, n in count_cards([r[0] for r in resolved]):
            lines.append(f"{n}x {name}" if n > 1 else name)
        lines.append("")
    with open(dst, "w") as f:
        f.write("\n".join(lines) + "\n")


def json_to_cod(src):
    deck = read_deck(src)
    dst = os.path.splitext(src)[0] + ".cod"
    root = Element("cockatrice_deck", version="1")
    root.set("generator", "yugioh-deck-manager")
    for zone, key in [("main", "main"), ("extra", "extra"), ("side", "side")]:
        cards = deck.get(key, [])
        if not cards:
            continue
        z = SubElement(root, "zone", name=zone)
        for name, n in count_cards([lookup_name(c) for c in cards]):
            SubElement(z, "card", number=str(n), name=name)
    xml = parseString(tostring(root, encoding="unicode")).toprettyxml(indent="  ")
    xml = "\n".join(l for l in xml.split("\n") if l.strip())
    with open(dst, "w") as f:
        f.write(xml + "\n")


def ydk_to_json(src):
    main, extra, side = [], [], []
    current = None
    with open(src) as f:
        for line in f:
            line = line.strip()
            if line.startswith("#main"):
                current = main
            elif line.startswith("#extra"):
                current = extra
            elif line.startswith("!side"):
                current = side
            elif line.startswith("#") or line.startswith("!") or not line:
                continue
            elif current is not None and line.isdigit():
                current.append(int(line))
    dst = os.path.splitext(src)[0] + ".json"
    write_deck(dst, {"main": main, "extra": extra, "side": side})


CONVERTERS = {
    "ydk": json_to_ydk,
    "ydke": json_to_ydke,
    "txt": json_to_txt,
    "cod": json_to_cod,
}


# ══════════════════════════════════════
# File collection
# ══════════════════════════════════════

def collect_files(path, ext):
    files = []
    if os.path.isfile(path):
        if path.endswith(ext):
            files.append(path)
    elif os.path.isdir(path):
        for root, _, names in os.walk(path):
            for name in sorted(names):
                if name.endswith(ext):
                    files.append(os.path.join(root, name))
    return sorted(files)


# ══════════════════════════════════════
# Batch processing
# ══════════════════════════════════════

def batch_convert(fmt, target, converter, src_ext):
    files = collect_files(target, src_ext)
    total = len(files)
    print(f"{YELLOW}Converting {total} files to {fmt.upper()}...{NC}")
    for i, f in enumerate(files, 1):
        converter(f)
        if i % 50 == 0:
            print(f"  {DIM}{i}/{total}...{NC}")
    _save_names_cache()
    print(f"{GREEN}Converted: {total}{NC}")


def do_export(fmt, target):
    if fmt == "all":
        for f, conv in CONVERTERS.items():
            batch_convert(f, target, conv, ".json")
    else:
        batch_convert(fmt, target, CONVERTERS[fmt], ".json")


# ══════════════════════════════════════
# Interactive menu
# ══════════════════════════════════════

def choose_scope():
    print(f"{BOLD}Scope:{NC}")
    print(f"  {CYAN}a){NC} All decks")
    print(f"  {CYAN}d){NC} Choose a game directory")
    print(f"  {CYAN}f){NC} Single file")
    print()
    scope = input("Choice [a/d/f]: ").strip().lower()

    if scope == "d":
        print()
        print(f"{BOLD}Available games:{NC}")
        dirs = sorted(
            d for d in os.listdir(DECKS_DIR)
            if os.path.isdir(os.path.join(DECKS_DIR, d))
        )
        for i, d in enumerate(dirs, 1):
            print(f"  {CYAN}{i}){NC} {d}")
        print()
        num = int(input("Game number: ").strip())
        if 1 <= num <= len(dirs):
            return os.path.join(DECKS_DIR, dirs[num - 1])
        print(f"{RED}Invalid{NC}")
        sys.exit(1)
    elif scope == "f":
        path = input("File path: ").strip()
        if not os.path.isfile(path):
            print(f"{RED}Not found{NC}")
            sys.exit(1)
        return path
    else:
        return DECKS_DIR


def interactive_menu():
    print(f"{BOLD}╔══════════════════════════════════════╗{NC}")
    print(f"{BOLD}║   Yu-Gi-Oh! Deck Format Converter    ║{NC}")
    print(f"{BOLD}╚══════════════════════════════════════╝{NC}")
    print()
    print(f"{BOLD}Export from JSON to:{NC}")
    print(f"  {CYAN}1){NC} YDK      {DIM}— YGOPro / EDOPro / simulators{NC}")
    print(f"  {CYAN}2){NC} YDKE     {DIM}— compact URL (clipboard sharing){NC}")
    print(f"  {CYAN}3){NC} TXT      {DIM}— human-readable card list{NC}")
    print(f"  {CYAN}4){NC} COD      {DIM}— Cockatrice XML{NC}")
    print(f"  {CYAN}5){NC} All      {DIM}— all formats at once{NC}")
    print()
    print(f"{BOLD}Import to JSON from:{NC}")
    print(f"  {CYAN}6){NC} YDK      {DIM}— import .ydk into project{NC}")
    print()
    print(f"  {CYAN}0){NC} Exit")
    print()

    choice = input("Choice: ").strip()
    fmt_map = {"1": "ydk", "2": "ydke", "3": "txt", "4": "cod", "5": "all"}

    if choice in fmt_map:
        target = choose_scope()
        do_export(fmt_map[choice], target)
    elif choice == "6":
        path = input("Path to .ydk file or directory: ").strip()
        if os.path.isfile(path):
            ydk_to_json(path)
            print(f"{GREEN}Imported: {os.path.basename(path)}{NC}")
        elif os.path.isdir(path):
            batch_convert("JSON", path, ydk_to_json, ".ydk")
        else:
            print(f"{RED}Not found{NC}")
            sys.exit(1)
    elif choice == "0":
        sys.exit(0)
    else:
        print(f"{RED}Invalid{NC}")
        sys.exit(1)


# ══════════════════════════════════════
# CLI entry point
# ══════════════════════════════════════

def main():
    args = sys.argv[1:]

    if not args:
        interactive_menu()
        return

    cmd = args[0]
    target = args[1] if len(args) > 1 else DECKS_DIR

    if cmd in ("ydk", "ydke", "txt", "cod", "all"):
        if os.path.isfile(target):
            if cmd == "all":
                for conv in CONVERTERS.values():
                    conv(target)
            else:
                CONVERTERS[cmd](target)
            _save_names_cache()
            print(f"{GREEN}Done{NC}")
        else:
            do_export(cmd, target)
    elif cmd == "import":
        if os.path.isfile(target):
            ydk_to_json(target)
            print(f"{GREEN}Imported: {os.path.basename(target)}{NC}")
        elif os.path.isdir(target):
            batch_convert("JSON", target, ydk_to_json, ".ydk")
        else:
            print(f"{RED}Not found: {target}{NC}")
            sys.exit(1)
    else:
        print(f"Usage: {sys.argv[0]} [ydk|ydke|txt|cod|all|import] [path]")
        print(f"       {sys.argv[0]}   (interactive menu)")
        sys.exit(1)


if __name__ == "__main__":
    main()
