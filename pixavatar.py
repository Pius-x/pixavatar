"""pixavatar - GitHub-style avatar generator.

Generates mirror-symmetric identicons, letter glyphs and custom pixel art
with deterministic seeds, color palettes and transparent backgrounds.

The identicon algorithm is inspired by afkbrb/github-avatar-generator:
a half-grid is filled at random, mirrored, and retried until the fill
density lands inside a configured range. Colors are filtered so they are
neither washed out nor muddy.
"""

import argparse
import math
import random

from PIL import Image, ImageDraw

__version__ = "1.0.0"

DEFAULT_BACKGROUND = (241, 241, 241)


def check_color(r, g, b):
    """Return True when a color is bright, saturated and not washed out.

    Mirrors the three guards of the original Java implementation but fixes
    its typo (the blue channel was never checked).
    """
    bright, dark, gray = 210, 200, 30
    if r < bright and g < bright and b < bright:
        return False
    if r > dark and g > dark and b > dark:
        return False
    if abs(r - g) < gray and abs(g - b) < gray and abs(b - r) < gray:
        return False
    return True


def random_color(rng):
    """Pick a random color that passes check_color."""
    while True:
        color = (rng.randint(0, 254), rng.randint(0, 254), rng.randint(0, 254))
        if check_color(*color):
            return color


def generate_cells(cell_count, rng, density=(0.3, 0.8)):
    """Generate a mirror-symmetric 0/1 grid with a fill density in range."""
    half = (cell_count + 1) // 2
    half_square = (cell_count // 2) * cell_count
    low = math.floor(density[0] * half_square)
    high = math.ceil(density[1] * half_square)

    while True:
        grid = [[0] * cell_count for _ in range(cell_count)]
        filled = 0
        for row in range(cell_count):
            for col in range(half):
                value = rng.randint(0, 1)
                grid[row][col] = value
                grid[row][cell_count - 1 - col] = value
                filled += value
        if low <= filled <= high:
            return grid


def cells_from_mask(mask, cell_count):
    """Build a mirrored grid from the left half of a pattern.

    mask holds one string per row, each with half-width 0/1 characters.
    """
    half = (cell_count + 1) // 2
    if len(mask) != cell_count:
        raise SystemExit(f"mask needs {cell_count} rows, got {len(mask)}")

    grid = [[0] * cell_count for _ in range(cell_count)]
    for row_index, row in enumerate(mask):
        if len(row) != half:
            raise SystemExit(
                f"mask row {row_index + 1} needs {half} columns (left half), got {len(row)}"
            )
        for col_index, char in enumerate(row):
            value = 1 if char == "1" else 0
            grid[row_index][col_index] = value
            grid[row_index][cell_count - 1 - col_index] = value
    return grid


GLYPHS = {
    "A": ["00100", "01110", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "11110", "10001", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "11110", "10000", "10000", "10000", "11111"],
    "F": ["11111", "10000", "11110", "10000", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01110"],
    "H": ["10001", "10001", "11111", "10001", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10001", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "01110", "00001", "00001", "10001", "01110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "X": ["10001", "01010", "00100", "00100", "00100", "01010", "10001"],
    "Y": ["10001", "01010", "00100", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
}


def cells_from_letter(letter, cell_count):
    """Render a letter from the built-in 5x7 bitmap font, not mirrored."""
    glyph = GLYPHS.get(letter.upper())
    if glyph is None:
        raise SystemExit(f"unsupported letter: {letter}")
    if cell_count > 7:
        raise SystemExit("letter mode supports cell_count 5 to 7")

    rows = [glyph[round(i * 6 / (cell_count - 1))] for i in range(cell_count)]
    return [
        [1 if row[round(col * 4 / (cell_count - 1))] == "1" else 0 for col in range(cell_count)]
        for row in rows
    ]


def parse_hex(value):
    """Parse #RGB or #RRGGBB into an (r, g, b) tuple."""
    value = value.strip().lstrip("#")
    if len(value) == 3:
        value = "".join(c * 2 for c in value)
    if len(value) != 6:
        raise SystemExit(f"cannot parse color: {value}")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def render(grid, cell_size, padding, fore, back, transparent):
    """Render a grid to an image of size 2*padding + cells*cell_size."""
    count = len(grid)
    side = 2 * padding + count * cell_size
    if transparent:
        image = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        foreground = tuple(fore) + (255,)
    else:
        image = Image.new("RGB", (side, side), back)
        foreground = tuple(fore)

    draw = ImageDraw.Draw(image)
    for row in range(count):
        for col in range(count):
            if not grid[row][col]:
                continue
            x = padding + col * cell_size
            y = padding + row * cell_size
            draw.rectangle([x, y, x + cell_size - 1, y + cell_size - 1], fill=foreground)
    return image


def build_grid(args, rng):
    if args.mask:
        return cells_from_mask(args.mask.split(","), args.cell_count)
    if args.letter:
        return cells_from_letter(args.letter, args.cell_count)
    return generate_cells(args.cell_count, rng, (args.density_min, args.density_max))


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="pixavatar",
        description="Generate GitHub-style avatars.",
        epilog=(
            "examples:\n"
            "  pixavatar.py --seed 42 --color 2EA44F --out avatar.png\n"
            "  pixavatar.py --letter X --cell-count 7 --color 1B7C83 --out x.png\n"
            "  pixavatar.py --mask 010,111,001 --color 8250DF --out pattern.png\n"
            "  pixavatar.py --seed 42 --transparent --out avatar.png"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"pixavatar {__version__}")
    parser.add_argument("--seed", type=int, help="integer seed for a reproducible shape")
    parser.add_argument("--color", help="foreground color(s), comma separated, e.g. 2EA44F,0969DA")
    parser.add_argument("--bg", help="background color, default F1F1F1")
    parser.add_argument("--cell-count", type=int, default=5, help="grid size N x N, default 5")
    parser.add_argument("--cell-size", type=int, default=64, help="pixels per cell, default 64")
    parser.add_argument("--padding", type=int, default=32, help="padding in pixels, default 32")
    parser.add_argument("--transparent", action="store_true", help="transparent background")
    parser.add_argument("--density-min", type=float, default=0.3, help="min fill density, default 0.3")
    parser.add_argument("--density-max", type=float, default=0.8, help="max fill density, default 0.8")
    parser.add_argument("--mask", help="custom pattern, comma separated rows of the left half")
    parser.add_argument("--letter", help="letter A-Z, rendered from a 5x7 bitmap font")
    parser.add_argument("--count", type=int, default=1, help="number of avatars, default 1")
    parser.add_argument("--out", default="avatar.png", help="output file, or prefix when count > 1")
    args = parser.parse_args(argv)

    rng = random.Random(args.seed)
    pool = [parse_hex(c) for c in args.color.split(",")] if args.color else None
    back = parse_hex(args.bg) if args.bg else DEFAULT_BACKGROUND

    for index in range(args.count):
        grid = build_grid(args, rng)
        fore = rng.choice(pool) if pool else random_color(rng)
        image = render(grid, args.cell_size, args.padding, fore, back, args.transparent)
        if args.count == 1:
            path = args.out
        else:
            stem, _, ext = args.out.rpartition(".")
            path = f"{stem}-{index + 1}.{ext or 'png'}"
        image.save(path)
        foreground = "#%02X%02X%02X" % fore
        print(f"{path}: seed={args.seed} color={foreground} cells={len(grid)}")


if __name__ == "__main__":
    main()
