"""Deck format converters — ported from scripts/deck-convert.py."""

import base64
import json
import struct


def read_json(path):
    with open(path) as f:
        return json.load(f)


def write_json(path, deck):
    with open(path, "w") as f:
        json.dump(deck, f, indent=2)
        f.write("\n")


# --- YDK ---

def json_to_ydk(deck):
    lines = ["#created by yugioh-deck-manager", "#main"]
    for c in deck.get("main", []):
        lines.append(str(c))
    lines.append("#extra")
    for c in deck.get("extra", []):
        lines.append(str(c))
    lines.append("!side")
    for c in deck.get("side", []):
        lines.append(str(c))
    return "\n".join(lines) + "\n"


def ydk_to_json(text):
    main, extra, side = [], [], []
    current = None
    for line in text.splitlines():
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
    return {"main": main, "extra": extra, "side": side}


def read_ydk(path):
    with open(path) as f:
        return ydk_to_json(f.read())


def write_ydk(path, deck):
    with open(path, "w") as f:
        f.write(json_to_ydk(deck))


# --- YDKE ---

def _encode_ydke(cards):
    return base64.b64encode(
        b"".join(struct.pack("<I", int(c)) for c in cards)
    ).decode()


def _decode_ydke(encoded):
    data = base64.b64decode(encoded)
    return [struct.unpack("<I", data[i:i+4])[0] for i in range(0, len(data), 4)]


def json_to_ydke(deck):
    main = _encode_ydke(deck.get("main", []))
    extra = _encode_ydke(deck.get("extra", []))
    side = _encode_ydke(deck.get("side", []))
    return f"ydke://{main}!{extra}!{side}!"


def ydke_to_json(ydke_str):
    ydke_str = ydke_str.strip()
    if ydke_str.startswith("ydke://"):
        ydke_str = ydke_str[7:]
    parts = ydke_str.rstrip("!").split("!")
    main = _decode_ydke(parts[0]) if len(parts) > 0 and parts[0] else []
    extra = _decode_ydke(parts[1]) if len(parts) > 1 and parts[1] else []
    side = _decode_ydke(parts[2]) if len(parts) > 2 and parts[2] else []
    return {"main": main, "extra": extra, "side": side}


# --- TXT (human readable) ---

def json_to_txt(deck, name_fn=None):
    if name_fn is None:
        name_fn = str
    lines = []
    for label, key in [("Main Deck", "main"), ("Extra Deck", "extra"), ("Side Deck", "side")]:
        cards = deck.get(key, [])
        if not cards:
            continue
        lines.append(f"== {label} ==")
        counted = _count_cards(cards)
        for cid, n in counted:
            name = name_fn(cid)
            lines.append(f"{n}x {name}" if n > 1 else name)
        lines.append("")
    return "\n".join(lines) + "\n"


def _count_cards(cards):
    counted = {}
    order = []
    for c in cards:
        if c not in counted:
            order.append(c)
            counted[c] = 0
        counted[c] += 1
    return [(cid, counted[cid]) for cid in order]


def count_unique(cards):
    return _count_cards(cards)
