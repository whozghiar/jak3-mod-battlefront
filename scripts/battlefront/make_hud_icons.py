"""Make the Battlefront gun HUD's pixel-art icons (goal_src/jak3/pc/features/battlefront/battlefront-icons.gc).

Each source is one of the mod author's pixel-art drawings on black (ICONS). Its art pixels are CELL
picture pixels wide: each is sampled at its middle, the colors are reduced to COLORS, the black
around the drawing (dark art pixels reached from its border) is left out, the icon is cropped to
the drawing, and each row is cut into runs of one color. An icon with a tint has its colors tinted (TINT), each keeping its brightness
against the most used one. The gun HUD draws each run as a flat rectangle (battlefront.gc
`bf-draw-pixel-icon`), so the icons need no texture.

Usage: python scripts/battlefront/make_hud_icons.py
"""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / "goal_src" / "jak3" / "pc" / "features" / "battlefront" / "battlefront-icons.gc"

CELL = 8     # picture pixels across one art pixel
COLORS = 6   # colors kept
BLACK = 60   # an art pixel this dark or darker, reached from the border, is the background
TINT = (125, 102, 150)  # the dark gun's HUD icon (the game's hud-gunpurple-03a texture), round 37

# name in the GOAL file, source picture, tint (None: its own colors)
ICONS = [
    ("rocket", HERE / "rocket-icon.png", TINT),    # the jetpack's rockets (round 36, purple since 37)
    ("grenade", HERE / "grenade-icon.png", None),  # the robotguard's grenades (round 38)
]


def lum(c):
    """Brightness of color C (r, g, b)."""
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def background(art):
    """The set of art pixels (x, y) of ART that are dark and reached from its border through dark ones."""
    w, h = art.size
    dark = lambda x, y: max(art.getpixel((x, y))) <= BLACK
    seen = set()
    todo = [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for x in (0, w - 1) for y in range(h)]
    while todo:
        x, y = todo.pop()
        if (x, y) in seen or not (0 <= x < w and 0 <= y < h) or not dark(x, y):
            continue
        seen.add((x, y))
        todo += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return seen


def runs_of(src):
    """The icon's size in art pixels, its colors (r, g, b) and its runs (x, y, length, color)."""
    w, h = round(src.width / CELL), round(src.height / CELL)
    art = Image.new("RGB", (w, h))
    for y in range(h):
        for x in range(w):
            sx = min(src.width - 1, int((x + 0.5) * src.width / w))
            sy = min(src.height - 1, int((y + 0.5) * src.height / h))
            art.putpixel((x, y), src.getpixel((sx, sy)))
    back = background(art)
    q = art.quantize(colors=COLORS + 1, method=Image.Quantize.MEDIANCUT)
    pal, idx = q.getpalette(), q.load()
    used, runs = {}, []
    for y in range(h):
        x = 0
        while x < w:
            if (x, y) in back:
                x += 1
                continue
            c, n = idx[x, y], 1
            while x + n < w and idx[x + n, y] == c and (x + n, y) not in back:
                n += 1
            runs.append((x, y, n, used.setdefault(c, len(used))))
            x += n
    colors = [tuple(pal[3 * c: 3 * c + 3]) for c in sorted(used, key=used.get)]
    # cropped to the drawing: no margin of background around it
    x0, y0 = min(r[0] for r in runs), min(r[1] for r in runs)
    w, h = max(r[0] + r[2] for r in runs) - x0, max(r[1] for r in runs) + 1 - y0
    return w, h, colors, [(x - x0, y - y0, n, c) for x, y, n, c in runs]


def tinted(colors, runs, tint):
    """COLORS in TINT: the most used one (in art pixels) becomes TINT, the others as much brighter
    or darker as they were."""
    count = [0] * len(colors)
    for _, _, n, c in runs:
        count[c] += n
    ref = lum(colors[count.index(max(count))])
    return [tuple(min(255, round(t * lum(c) / ref)) for t in tint) for c in colors]


def rows(values, per):
    return "\n".join("    " + " ".join(f"#x{v:08x}" for v in values[i:i + per]) for i in range(0, len(values), per))


def icon_gc(name, src, tint):
    """The GOAL definitions of one icon, and a line about it."""
    w, h, colors, runs = runs_of(Image.open(src).convert("RGB"))
    if tint:
        colors = tinted(colors, runs, tint)
    assert w < 256 and h < 256 and len(colors) < 256
    words = [x | (y << 8) | (n << 16) | (c << 24) for x, y, n, c in runs]
    rgba = [r | (g << 8) | (b << 16) | (0x80 << 24) for r, g, b in colors]
    up = name.upper()
    gc = f""";; The {name} icon ({src.name}{", tinted" if tint else ""}): {w} x {h} art pixels.
;; Its colors (rgba, alpha 128: opaque).
(define *bf-{name}-icon-colors*
  (new 'static 'array uint32 {len(rgba)}
{rows(rgba, 8)}
    )
  )

;; Its runs, row after row: x, y and length in art pixels, then the color's index, a byte each
;; (x | y << 8 | length << 16 | color << 24).
(define *bf-{name}-icon-runs*
  (new 'static 'array uint32 {len(words)}
{rows(words, 8)}
    )
  )

(defconstant BF_{up}_ICON_W {w})       ;; the icon's art pixels across
(defconstant BF_{up}_ICON_H {h})        ;; and down
(defconstant BF_{up}_ICON_RUNS {len(words)}) ;; its runs
"""
    return gc, f"{name}: {w} x {h}, {len(colors)} colors, {len(words)} runs"


def main():
    parts, notes = [], []
    for name, src, tint in ICONS:
        gc, note = icon_gc(name, src, tint)
        parts.append(gc)
        notes.append(note)
    OUT.write_text(""";;-*-Lisp-*-
(in-package goal)

;; name: battlefront-icons.gc
;; name in dgo: battlefront-icons
;; dgos: GAME

#|
  Battlefront mod -- the gun HUD's pixel-art icons (battlefront.gc `bf-draw-pixel-icon`): the
  jetpack's rocket and the robotguard's grenade.

  GENERATED by scripts/battlefront/make_hud_icons.py from the mod author's drawings in
  scripts/battlefront/: do not edit by hand. Each picture as runs of one color.
|#

""" + "\n".join(parts), encoding="utf-8", newline="\n")
    print(f"{OUT.relative_to(ROOT)}: " + "; ".join(notes))


if __name__ == "__main__":
    main()
