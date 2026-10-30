#!/usr/bin/env python3
"""Yu-Gi-Oh! Deck Validator

Validates deck JSON files with selectable checks.

Usage:
    python scripts/deck-validate.py                           # interactive
    python scripts/deck-validate.py --check ids --deep        # verify card IDs (all decks)
    python scripts/deck-validate.py --check limits --deep     # deck size limits (all decks)
    python scripts/deck-validate.py --check ids,limits --deep # both (all decks)
    python scripts/deck-validate.py --debug --deep            # all checks verbose
    python scripts/deck-validate.py --check limits "decks/[PS1] Forbidden Memories"
    python scripts/deck-validate.py deck.json                 # single file
"""

import json
import os
import sys
import time
import urllib.request

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)
DECKS_DIR = os.path.join(PROJECT_DIR, "decks")
NAMES_CACHE_FILE = os.path.join(SCRIPTS_DIR, ".card_names_cache.json")

# ══════════════════════════════════════
# Colors
# ══════════════════════════════════════

BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
YELLOW = "\033[0;33m"
RED = "\033[0;31m"
NC = "\033[0m"

# ══════════════════════════════════════
# Deck rules
# ══════════════════════════════════════

RULES = {
    "main_min": 40,
    "main_max": 60,
    "extra_max": 15,
    "side_max": 15,
    "max_copies": 3,
}

# Per-game rule overrides (folder name prefix → rule overrides)
# Games with non-standard deck limits get relaxed validation.
GAME_RULES = {
    # Video games — NPC/AI decks don't enforce TCG minimums, and retro games allow Extra deck up to 30
    "[PS1] Forbidden Memories": {"main_min": 0, "extra_max": 30, "side_max": 0},
    "[Mobile] Duel Links": {"main_min": 20, "main_max": 30, "extra_max": 8, "side_max": 0},
    "[PS2] Capsule Monster Coliseum": {"main_min": 0, "extra_max": 30, "side_max": 0},
    "[PS2] Duelist of the Roses": {"main_min": 0, "extra_max": 30, "side_max": 0},
    "[GBA] Sacred Cards": {"main_min": 0, "extra_max": 30, "side_max": 0},
    "[GBA] Reshef of Destruction": {"main_min": 0, "extra_max": 30, "side_max": 0},
    "[GBA] World Championship Tournament 2004": {"main_min": 0, "extra_max": 30},
    "[GBA] World Championship Tournament 2005": {"main_min": 0, "extra_max": 30},
    "[GBA] World Championship Tournament 2006": {"main_min": 0, "extra_max": 30},
    "[DS] GX Spirit Caller": {"main_min": 0, "extra_max": 30},
    "[DS] World Championship 2007": {"main_min": 0, "extra_max": 30},
    "[DS] World Championship 2008": {"main_min": 0, "extra_max": 30},
    "[DS] Stardust Accelerator": {"main_min": 0},
    "[DS] Reverse of Arcadia": {"main_min": 0},
    "[DS] Over the Nexus": {"main_min": 0},
    "[PSP] GX Tag Force 1": {"main_min": 0, "extra_max": 30},
    "[PSP] GX Tag Force 2": {"main_min": 0, "extra_max": 30},
    "[PSP] GX Tag Force 3": {"main_min": 0, "extra_max": 30},
    "[PSP] 5D's Tag Force 4": {"main_min": 0},
    "[PSP] 5D's Tag Force 5": {"main_min": 0},
    "[PSP] 5D's Tag Force 6": {"main_min": 0},
    "[PSP] ARC-V Tag Force Special": {"main_min": 0},
    "[3DS] ZEXAL World Duel Carnival": {"main_min": 0},
    "[Multi] Legacy of the Duelist Link Evolution": {"main_min": 0},
    # Anime — partial decks, only cards shown on screen
    "[TV] Duel Monsters": {"main_min": 0, "extra_max": 30},
    "[TV] GX": {"main_min": 0, "extra_max": 30},
    "[TV] 5Ds": {"main_min": 0},
    "[TV] ZEXAL": {"main_min": 0},
    "[TV] ARC-V": {"main_min": 0},
    "[TV] VRAINS": {"main_min": 0},
    "[TV] SEVENS": {"main_min": 0},
    "[TV] GO RUSH": {"main_min": 0},
}


def get_rules_for_path(path):
    rel = os.path.relpath(path, DECKS_DIR)
    parts = rel.split(os.sep)
    if len(parts) >= 2:
        game_folder = parts[0]
        if game_folder in GAME_RULES:
            merged = dict(RULES)
            merged.update(GAME_RULES[game_folder])
            return merged
    return RULES

# ══════════════════════════════════════
# Available checks registry
# ══════════════════════════════════════

CHECKS = {
    "ids": {
        "name": "Card IDs",
        "description": "Verify passcodes exist in YGOPRODECK API",
    },
    "limits": {
        "name": "Deck Limits",
        "description": "Main 40-60, Extra ≤15, Side ≤15, max 3 copies",
    },
}

# ══════════════════════════════════════
# Card name cache
# ══════════════════════════════════════

_card_cache = None
_card_cache_dirty = False


def _load_card_cache():
    global _card_cache
    if _card_cache is None:
        if os.path.exists(NAMES_CACHE_FILE):
            with open(NAMES_CACHE_FILE) as f:
                _card_cache = json.load(f)
        else:
            _card_cache = {}
    return _card_cache


def _save_card_cache():
    if _card_cache_dirty and _card_cache:
        with open(NAMES_CACHE_FILE, "w") as f:
            json.dump(_card_cache, f, indent=1, sort_keys=True)


def lookup_card(passcode):
    global _card_cache_dirty
    cache = _load_card_cache()
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
                _card_cache_dirty = True
                return name
    except Exception:
        pass
    return None


def card_name(passcode):
    cache = _load_card_cache()
    return cache.get(str(passcode), str(passcode))


# ══════════════════════════════════════
# Issue reporting
# ══════════════════════════════════════

class Issue:
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

    def __init__(self, level, check, message, detail=None):
        self.level = level
        self.check = check
        self.message = message
        self.detail = detail

    def __str__(self):
        icons = {
            self.ERROR: f"{RED}✗ ERROR{NC}",
            self.WARNING: f"{YELLOW}⚠ WARN {NC}",
            self.INFO: f"{DIM}ℹ INFO {NC}",
        }
        tag = f"{DIM}[{self.check}]{NC}" if self.check else ""
        s = f"  {icons[self.level]}  {self.message}  {tag}"
        if self.detail:
            s += f"\n           {DIM}{self.detail}{NC}"
        return s


# ══════════════════════════════════════
# Base structure validation (always runs)
# ══════════════════════════════════════

def check_structure(deck, path):
    issues = []

    if not isinstance(deck, dict):
        issues.append(Issue(Issue.ERROR, "structure", "JSON root must be an object"))
        return issues, None, None, None

    for key in ("main", "extra", "side"):
        if key not in deck:
            issues.append(Issue(Issue.WARNING, "structure", f'Missing "{key}" key'))
        elif not isinstance(deck[key], list):
            issues.append(Issue(Issue.ERROR, "structure", f'"{key}" must be an array'))

    main = deck.get("main", [])
    extra = deck.get("extra", [])
    side = deck.get("side", [])

    unexpected = set(deck.keys()) - {"main", "extra", "side"}
    if unexpected:
        issues.append(Issue(Issue.INFO, "structure", f"Extra keys: {', '.join(sorted(unexpected))}"))

    bad_types = 0
    for section_name, cards in [("main", main), ("extra", extra), ("side", side)]:
        for i, c in enumerate(cards):
            if not isinstance(c, int):
                bad_types += 1
                if bad_types <= 3:
                    issues.append(Issue(Issue.ERROR, "structure", f"{section_name}[{i}]: expected int, got {type(c).__name__}", repr(c)))
    if bad_types > 3:
        issues.append(Issue(Issue.ERROR, "structure", f"...and {bad_types - 3} more type errors"))

    if len(main) == 0 and len(extra) == 0:
        issues.append(Issue(Issue.WARNING, "structure", "Deck is empty"))
        return issues, main, extra, side

    return issues, main, extra, side


# ══════════════════════════════════════
# Check: limits
# ══════════════════════════════════════

def check_limits(main, extra, side, rules=None, debug=False):
    rules = rules or RULES
    issues = []
    mc, ec, sc = len(main), len(extra), len(side)

    if debug:
        issues.append(Issue(Issue.INFO, "limits", f"Size: {mc}m / {ec}e / {sc}s"))

    if mc < rules["main_min"]:
        issues.append(Issue(Issue.ERROR, "limits", f"Main deck: {mc} cards (min {rules['main_min']})"))
    elif mc > rules["main_max"]:
        issues.append(Issue(Issue.ERROR, "limits", f"Main deck: {mc} cards (max {rules['main_max']})"))
    elif debug:
        issues.append(Issue(Issue.INFO, "limits", f"Main deck size OK ({mc})"))

    if ec > rules["extra_max"]:
        issues.append(Issue(Issue.ERROR, "limits", f"Extra deck: {ec} cards (max {rules['extra_max']})"))

    if sc > rules["side_max"]:
        issues.append(Issue(Issue.ERROR, "limits", f"Side deck: {sc} cards (max {rules['side_max']})"))

    # Copy limit
    all_cards = list(main) + list(extra) + list(side)
    card_counts = {}
    for c in all_cards:
        card_counts[c] = card_counts.get(c, 0) + 1

    over_limit = [(cid, cnt) for cid, cnt in card_counts.items() if cnt > rules["max_copies"]]
    for cid, cnt in sorted(over_limit, key=lambda x: -x[1]):
        name = card_name(cid)
        issues.append(Issue(Issue.ERROR, "limits", f"{name}: {cnt} copies (max {rules['max_copies']})"))

    if debug and not over_limit:
        issues.append(Issue(Issue.INFO, "limits", "All cards within copy limit"))

    return issues


# ══════════════════════════════════════
# Check: ids
# ══════════════════════════════════════

def check_ids(main, extra, side, debug=False):
    issues = []
    all_cards = list(main) + list(extra) + list(side)
    unique_ids = set(all_cards)

    # Sanity
    for cid in sorted(unique_ids):
        if isinstance(cid, int):
            if cid <= 0:
                issues.append(Issue(Issue.ERROR, "ids", f"Invalid passcode: {cid} (must be positive)"))
            elif cid > 99999999:
                issues.append(Issue(Issue.WARNING, "ids", f"Unusual passcode: {cid} (>8 digits — anime/alt art?)"))

    # API verification
    unresolved = []
    checked = 0
    for cid in sorted(unique_ids):
        if not isinstance(cid, int) or cid <= 0:
            continue
        name = lookup_card(cid)
        checked += 1
        if name is None:
            unresolved.append(cid)
        if checked % 100 == 0:
            print(f"    {DIM}Checked {checked}/{len(unique_ids)} IDs...{NC}", file=sys.stderr)
            time.sleep(0.02)

    if unresolved:
        issues.append(Issue(Issue.WARNING, "ids", f"{len(unresolved)} card(s) not found in YGOPRODECK", f"IDs: {unresolved[:10]}{'...' if len(unresolved) > 10 else ''}"))
    elif debug:
        issues.append(Issue(Issue.INFO, "ids", f"All {len(unique_ids)} unique cards verified"))

    return issues


# ══════════════════════════════════════
# Validation orchestrator
# ══════════════════════════════════════

def validate_deck(path, enabled_checks, debug=False):
    try:
        with open(path) as f:
            deck = json.load(f)
    except json.JSONDecodeError as e:
        return [Issue(Issue.ERROR, "structure", "Invalid JSON", str(e))]
    except Exception as e:
        return [Issue(Issue.ERROR, "structure", "Cannot read file", str(e))]

    issues, main, extra, side = check_structure(deck, path)

    # If structure failed hard or deck empty, skip further checks
    if main is None or (len(main) == 0 and len(extra) == 0):
        return issues

    if "limits" in enabled_checks:
        rules = get_rules_for_path(path)
        issues.extend(check_limits(main, extra, side, rules, debug))

    if "ids" in enabled_checks:
        issues.extend(check_ids(main, extra, side, debug))

    return issues


# ══════════════════════════════════════
# Display
# ══════════════════════════════════════

def print_result(path, issues):
    filename = os.path.relpath(path, PROJECT_DIR)
    errors = sum(1 for i in issues if i.level == Issue.ERROR)
    warnings = sum(1 for i in issues if i.level == Issue.WARNING)

    if errors:
        status = f"{RED}FAIL{NC}"
    elif warnings:
        status = f"{YELLOW}WARN{NC}"
    else:
        status = f"{GREEN}PASS{NC}"

    print(f"\n{BOLD}{filename}{NC}  [{status}]")
    for issue in issues:
        print(str(issue))


def print_summary(results):
    total = len(results)
    passed = sum(1 for r in results if not any(i.level == Issue.ERROR for i in r["issues"]))
    warned = sum(1 for r in results if any(i.level == Issue.WARNING for i in r["issues"]) and not any(i.level == Issue.ERROR for i in r["issues"]))
    failed = sum(1 for r in results if any(i.level == Issue.ERROR for i in r["issues"]))
    empty = sum(1 for r in results if any(i.message == "Deck is empty" for i in r["issues"]))

    print(f"\n{BOLD}{'═' * 50}{NC}")
    print(f"{BOLD}Summary:{NC}  {total} decks")
    print(f"  {GREEN}✓ Pass:{NC}  {passed}")
    if warned:
        print(f"  {YELLOW}⚠ Warn:{NC}  {warned}")
    if failed:
        print(f"  {RED}✗ Fail:{NC}  {failed}")
    if empty:
        print(f"  {DIM}○ Empty: {empty}{NC}")
    print()


# ══════════════════════════════════════
# File collection
# ══════════════════════════════════════

def collect_files(path):
    files = []
    if os.path.isfile(path) and path.endswith(".json"):
        files.append(path)
    elif os.path.isdir(path):
        for root, _, names in os.walk(path):
            for name in sorted(names):
                if name.endswith(".json"):
                    files.append(os.path.join(root, name))
    return sorted(files)


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
            count = len([f for f in os.listdir(os.path.join(DECKS_DIR, d)) if f.endswith(".json")])
            print(f"  {CYAN}{i:2}){NC} {d}  {DIM}({count} decks){NC}")
        print()
        try:
            num = int(input("Game number: ").strip())
        except ValueError:
            print(f"{RED}Invalid{NC}")
            sys.exit(1)
        if 1 <= num <= len(dirs):
            return os.path.join(DECKS_DIR, dirs[num - 1])
        print(f"{RED}Invalid{NC}")
        sys.exit(1)

    elif scope == "f":
        print()
        all_files = collect_files(DECKS_DIR)
        if not all_files:
            print(f"{RED}No deck files found{NC}")
            sys.exit(1)
        shown = all_files[-20:]
        for i, f in enumerate(shown, 1):
            print(f"  {CYAN}{i:2}){NC} {os.path.relpath(f, PROJECT_DIR)}")
        print()
        choice = input("Number or path: ").strip()
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(shown):
                return shown[idx - 1]
        if os.path.isfile(choice):
            return choice
        print(f"{RED}Not found{NC}")
        sys.exit(1)

    return DECKS_DIR


def choose_checks():
    print()
    print(f"{BOLD}Checks to run:{NC}  {DIM}(structure always runs){NC}")
    for key, info in CHECKS.items():
        print(f"  {CYAN}{key:10}{NC}  {info['description']}")
    print()
    print(f"  {CYAN}1){NC} limits only")
    print(f"  {CYAN}2){NC} ids only")
    print(f"  {CYAN}3){NC} limits + ids")
    print(f"  {CYAN}4){NC} limits + ids + debug")
    print()
    choice = input("Choice [1/2/3/4]: ").strip()
    options = {
        "1": ({"limits"}, False),
        "2": ({"ids"}, False),
        "3": ({"limits", "ids"}, False),
        "4": ({"limits", "ids"}, True),
    }
    return options.get(choice, ({"limits"}, False))


def interactive_menu():
    print(f"{BOLD}╔══════════════════════════════════════╗{NC}")
    print(f"{BOLD}║     Yu-Gi-Oh! Deck Validator         ║{NC}")
    print(f"{BOLD}╚══════════════════════════════════════╝{NC}")
    print()

    target = choose_scope()
    enabled, debug = choose_checks()
    run_validation(target, enabled, debug)


# ══════════════════════════════════════
# Runner
# ══════════════════════════════════════

def run_validation(target, enabled_checks, debug=False):
    files = collect_files(target)
    if not files:
        # Check if there are non-JSON deck files
        other_exts = set()
        if os.path.isdir(target):
            for root, _, names in os.walk(target):
                for name in names:
                    ext = os.path.splitext(name)[1]
                    if ext in (".ydk", ".ydke", ".cod", ".txt"):
                        other_exts.add(ext)
        if other_exts:
            fmts = ", ".join(sorted(other_exts))
            print(f"{RED}No .json deck files found, but found {fmts} files.{NC}")
            print(f"  Convert first with:")
            print(f"  {CYAN}python scripts/deck-convert.py import \"{target}\"{NC}")
        else:
            print(f"{RED}No .json deck files found{NC}")
        sys.exit(1)

    checks_str = ", ".join(sorted(enabled_checks)) if enabled_checks else "structure only"
    print(f"\n{BOLD}Validating {len(files)} deck(s){NC}  {DIM}[{checks_str}]{NC}")

    results = []
    for f in files:
        issues = validate_deck(f, enabled_checks, debug)
        results.append({"path": f, "issues": issues})
        has_problems = any(i.level in (Issue.ERROR, Issue.WARNING) for i in issues)
        if has_problems or debug:
            print_result(f, issues)

    _save_card_cache()
    print_summary(results)
    if any(issue.level == Issue.ERROR for result in results for issue in result["issues"]):
        sys.exit(1)


# ══════════════════════════════════════
# CLI
# ══════════════════════════════════════

def main():
    args = sys.argv[1:]

    debug = "--debug" in args
    deep = "--deep" in args
    flags = {"--debug", "--deep"}

    # Parse --check ids,limits
    enabled_checks = set()
    i = 0
    remaining = []
    while i < len(args):
        if args[i] in flags:
            i += 1
        elif args[i] == "--check" and i + 1 < len(args):
            for c in args[i + 1].split(","):
                c = c.strip()
                if c in CHECKS:
                    enabled_checks.add(c)
                else:
                    print(f"{RED}Unknown check: {c}{NC}")
                    print(f"Available: {', '.join(CHECKS.keys())}")
                    sys.exit(1)
            i += 2
        else:
            remaining.append(args[i])
            i += 1

    # Default: all checks if debug, limits if no --check given
    if not enabled_checks:
        if debug:
            enabled_checks = set(CHECKS.keys())
        else:
            enabled_checks = {"limits"}

    if not remaining and not deep:
        interactive_menu()
        return

    # --deep with no path = all decks
    if deep and not remaining:
        target = DECKS_DIR
    elif remaining:
        target = remaining[0]
    else:
        target = DECKS_DIR

    if not os.path.exists(target):
        print(f"{RED}Not found: {target}{NC}")
        sys.exit(1)

    # Check if user passed a non-JSON file
    if os.path.isfile(target) and not target.endswith(".json"):
        ext = os.path.splitext(target)[1]
        print(f"{RED}✗ Cannot validate {ext} files directly.{NC}")
        print(f"  Convert to JSON first with:")
        print(f"  {CYAN}python scripts/deck-convert.py import \"{target}\"{NC}")
        sys.exit(1)

    run_validation(target, enabled_checks, debug)


if __name__ == "__main__":
    main()
