"""TCG deck validation rules."""

from theme import (
    MAIN_MIN, MAIN_MAX, EXTRA_MAX, SIDE_MAX, MAX_COPIES,
    TYPE_TOKEN, EXTRA_TYPES, TYPE_MONSTER,
)


def is_extra_deck_card(card_type):
    return bool(card_type & EXTRA_TYPES)


def is_token(card_type):
    return bool(card_type & TYPE_TOKEN)


def validate_deck(deck, card_db=None):
    """Validate a deck dict against TCG rules.

    Returns list of (severity, message) tuples.
    severity: 'error' | 'warning'
    """
    issues = []
    main = deck.get("main", [])
    extra = deck.get("extra", [])
    side = deck.get("side", [])

    # Size checks
    if len(main) < MAIN_MIN:
        issues.append(("error", f"Main deck too small: {len(main)}/{MAIN_MIN} minimum"))
    if len(main) > MAIN_MAX:
        issues.append(("error", f"Main deck too large: {len(main)}/{MAIN_MAX} maximum"))
    if len(extra) > EXTRA_MAX:
        issues.append(("error", f"Extra deck too large: {len(extra)}/{EXTRA_MAX} maximum"))
    if len(side) > SIDE_MAX:
        issues.append(("error", f"Side deck too large: {len(side)}/{SIDE_MAX} maximum"))

    # Copy count across all zones
    all_cards = main + extra + side
    counts = {}
    for cid in all_cards:
        counts[cid] = counts.get(cid, 0) + 1

    for cid, n in counts.items():
        if n > MAX_COPIES:
            name = str(cid)
            if card_db:
                name = card_db.get_name(cid)
            issues.append(("error", f"Too many copies of {name}: {n}/{MAX_COPIES}"))

    # Card placement validation (needs card_db)
    if card_db:
        for cid in main:
            card = card_db.get_card(cid)
            if card is None:
                issues.append(("warning", f"Unknown card ID in main deck: {cid}"))
                continue
            if is_token(card["type"]):
                issues.append(("error", f"Token in main deck: {card_db.get_name(cid)}"))
            if is_extra_deck_card(card["type"]):
                issues.append((
                    "error",
                    f"Extra deck card in main deck: {card_db.get_name(cid)}",
                ))

        for cid in extra:
            card = card_db.get_card(cid)
            if card is None:
                issues.append(("warning", f"Unknown card ID in extra deck: {cid}"))
                continue
            if not is_extra_deck_card(card["type"]):
                issues.append((
                    "error",
                    f"Non-extra card in extra deck: {card_db.get_name(cid)}",
                ))

    return issues


def deck_summary(deck):
    """Return (main_count, extra_count, side_count)."""
    return (
        len(deck.get("main", [])),
        len(deck.get("extra", [])),
        len(deck.get("side", [])),
    )


def is_valid(deck, card_db=None):
    issues = validate_deck(deck, card_db)
    return not any(sev == "error" for sev, _ in issues)
