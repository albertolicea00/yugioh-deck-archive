"""Generate platform-specific app icons from the master 512x512 source."""

import os
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("Pillow required: pip install Pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONS_DIR = os.path.join(ROOT, "assets", "icons")
SOURCE = os.path.join(ICONS_DIR, "app-icon.png")


def _resize(img, size):
    return img.resize((size, size), Image.LANCZOS)


def _round_mask(size, radius_fraction=0.22):
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    r = int(size * radius_fraction)
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=255)
    return mask


def _circle_mask(size):
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse([0, 0, size - 1, size - 1], fill=255)
    return mask


def generate_macos(img):
    """macOS: rounded-rectangle icons at standard sizes."""
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    for s in sizes:
        icon = _resize(img, s)
        mask = _round_mask(s)
        result = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        result.paste(icon, mask=mask)
        result.save(os.path.join(ICONS_DIR, f"app-icon-macos-{s}.png"))
    print(f"  macOS: {len(sizes)} sizes")


def generate_ios(img):
    """iOS: square icons (iOS applies its own mask)."""
    sizes = [40, 60, 80, 87, 120, 152, 167, 180, 1024]
    for s in sizes:
        icon = _resize(img, s)
        icon.save(os.path.join(ICONS_DIR, f"app-icon-ios-{s}.png"))
    print(f"  iOS: {len(sizes)} sizes")


def generate_android(img):
    """Android: adaptive foreground/background + round legacy icons."""
    # Adaptive icon foreground (centered in 108dp safe zone)
    fg_size = 512
    fg = Image.new("RGBA", (fg_size, fg_size), (0, 0, 0, 0))
    inset = int(fg_size * 0.25)
    inner = _resize(img, fg_size - 2 * inset)
    fg.paste(inner, (inset, inset))
    fg.save(os.path.join(ICONS_DIR, "app-icon-android-foreground.png"))

    # Solid background
    bg = Image.new("RGB", (fg_size, fg_size), (15, 10, 8))
    bg.save(os.path.join(ICONS_DIR, "app-icon-android-background.png"))

    # Round legacy icons
    round_sizes = [48, 72, 96, 144, 192]
    for s in round_sizes:
        icon = _resize(img, s)
        mask = _circle_mask(s)
        result = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        result.paste(icon, mask=mask)
        result.save(os.path.join(ICONS_DIR, f"app-icon-android-round-{s}.png"))
    print(f"  Android: foreground + background + {len(round_sizes)} round")


def generate_windows(img):
    """Windows: multi-resolution .ico file."""
    ico_sizes = [16, 32, 48, 64, 128, 256]
    ico_path = os.path.join(ICONS_DIR, "app-icon.ico")
    img.save(ico_path, format="ICO", sizes=[(s, s) for s in ico_sizes])
    print(f"  Windows: .ico with {len(ico_sizes)} sizes")


def main():
    if not os.path.exists(SOURCE):
        sys.exit(f"Source icon not found: {SOURCE}")

    img = Image.open(SOURCE).convert("RGBA")
    print(f"Source: {SOURCE} ({img.size[0]}x{img.size[1]})")

    generate_macos(img)
    generate_ios(img)
    generate_android(img)
    generate_windows(img)

    print("Done.")


if __name__ == "__main__":
    main()
