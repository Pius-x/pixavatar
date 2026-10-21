[简体中文](README.md) | **English**

# pixavatar

Generate GitHub-style avatars in Python: mirror-symmetric identicons, letter glyphs and custom pixel art.

**Live demo: https://pius-x.github.io/pixavatar/** — runs entirely in the browser, no install needed. Deterministic seeds, full color control, transparent backgrounds, any output size.

![examples](examples/sheet.png)

## Features

- **Identicons** — mirror-symmetric 5×5 grids with a 30–80% fill density, so results never look empty or muddy
- **Deterministic** — `--seed` reproduces the exact same shape, every time
- **Colors** — a single color or a palette to pick from, custom background, transparent output
- **Letters** — A–Z from a built-in 5×7 bitmap font
- **Custom pixel art** — `--mask` takes the left half of a pattern and mirrors it automatically
- **Any size** — `--cell-size` and `--padding` control the output resolution (1024px and up)

## Install

Requires Python 3.8+ and [Pillow](https://python-pillow.org/).

```bash
pip install pillow
```

No other dependencies.

## Usage

```bash
# Random avatar
python pixavatar.py --out avatar.png

# Reproducible shape with a fixed color
python pixavatar.py --seed 42 --color 2EA44F --out avatar.png

# Pick a random color from a palette
python pixavatar.py --seed 42 --color 2EA44F,0969DA,8250DF --out avatar.png

# Letter avatar on a 7×7 grid
python pixavatar.py --letter X --cell-count 7 --color 1B7C83 --out letter.png

# Custom pixel art: 5 rows, 3 characters each (the left half), mirrored automatically
python pixavatar.py --mask 010,111,001,011,001 --color 8250DF --out pattern.png

# Transparent background, 1024px canvas
python pixavatar.py --seed 42 --color E36209 --cell-size 128 --padding 64 --transparent --out avatar.png

# Generate six candidates at once
python pixavatar.py --count 6 --color 2EA44F,0969DA,8250DF --out candidate.png
```

## Options

| Option | Default | Description |
|---|---|---|
| `--seed` | random | Integer seed for a reproducible shape |
| `--color` | random | Foreground color(s) as hex, comma separated |
| `--bg` | `F1F1F1` | Background color |
| `--cell-count` | `5` | Grid size (N×N) |
| `--cell-size` | `64` | Pixels per cell |
| `--padding` | `32` | Pixels of padding around the grid |
| `--transparent` | off | Transparent background |
| `--density-min` / `--density-max` | `0.3` / `0.8` | Fill density range for identicons |
| `--mask` | — | Custom pattern, comma separated rows of the left half |
| `--letter` | — | Letter `A`–`Z` |
| `--count` | `1` | Number of avatars to generate |
| `--out` | `avatar.png` | Output file, or prefix when `--count` > 1 |

## Custom masks

`--mask` takes one string per row, where each string is the **left half** of the pattern (`0` = empty, `1` = filled). The right half is mirrored automatically.

A 5×5 heart, for example:

```
010
111
111
011
001
```

```bash
python pixavatar.py --mask 010,111,111,011,001 --color D1242F --out heart.png
```

The number of columns must be `ceil(cell_count / 2)` and the number of rows must equal `cell_count`.

## How identicons work

The algorithm is inspired by [afkbrb/github-avatar-generator](https://github.com/afkbrb/github-avatar-generator):

1. Fill the left half of an N×N grid at random, mirror it to the right half.
2. Count filled cells and retry the whole grid unless the count lands between 30% and 80% of the half-grid area — this keeps avatars from looking nearly empty or nearly solid.
3. Pick a random foreground color, rejecting colors that are too dark, too bright, or too close to gray.

Unlike the original, output is deterministic for a given seed, and you can set a palette, use a bitmap font, or supply your own pattern.

## Credits

Inspired by [afkbrb/github-avatar-generator](https://github.com/afkbrb/github-avatar-generator) (Java AWT). This is an independent Python implementation with extras: deterministic seeds, color palettes, letter glyphs, custom masks and transparent output.

## License

[MIT](LICENSE)
