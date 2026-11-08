#!/usr/bin/env python3
"""
Write the Battlefront mod's zone minimaps: for each war zone, the in-game minimap of its levels (or,
for the whole city, of every minimap cell with a texture), as the zone and side pages of the battle
menu and the respawn page show it.

    python scripts/battlefront/make_minimaps.py [--png <folder>]

Inputs:
    goal_src/jak3/engine/level/level-info.gc       each district level's `city-map-bits`
    decompiler_out/jak3/textures/*-minimap/*.png   the city sections' minimap textures, written by
                                                   `task extract` (map-ctyporta, map-ctyinda...)

Output:
    goal_src/jak3/pc/features/battlefront/battlefront-minimaps.gc
    (with --png, each zone's map as a PNG in <folder> too, to look at)

How the minimap places its textures (engine/ui/minimap.gc): Haven City is a grid of 5 x 7 cells of
384 m, a cell's column `(x + 768 m) / 384 m` and row `(z + 768 m) / 384 m`; each cell names a
texture covering 1024 m (256 x 256 texels of 4 m; on the city's south edge 256 x 128, 8 m high) whose top left corner is at `*minimap-corner-array*`, x and z each
-1088 m + 384 m per column or row, so a texture covers its cell and 320 m around it. A level lists
the cells it covers in its `city-map-bits` (level-info.gc). A zone's map covers the bounding box of
its levels' cells, at most 256 texels a side: a texel of a cell of the zone takes the texture of
its cell (or, for a cell with none, of another cell of the zone covering it); a texel of a cell out
of the zone is black.

The maps are 8-bit images with one shared palette, in the form the PC port's map texture upload
reads (bigmap.gc `pc-upload-map-texture`): mt8 texels, and a 16 x 16 ct32 palette in the PS2 order,
where entry i sits at position i with bits 3 and 4 swapped. Each map's stored width is a multiple
of 64 (the GS buffer width unit), padded with black.

Every path is relative to the jak-project root. Needs Pillow.
"""
from __future__ import annotations

import math
import pathlib
import re
import struct
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
LEVEL_INFO = ROOT / "goal_src/jak3/engine/level/level-info.gc"
TEXTURES = ROOT / "decompiler_out/jak3/textures"
OUT = ROOT / "goal_src/jak3/pc/features/battlefront/battlefront-minimaps.gc"

# The war zones in `*bf-zones*` order (battlefront-h.gc) and their levels; None for the whole city
# (every cell with a minimap texture), the battlefield since round 17.
ZONES = [
    ("Haven City", None),
]

# engine/ui/minimap.gc *minimap-texture-name-array*, 5 columns by 7 rows
CELLS = [
    None, None, "map-stadium", "map-ctyslumc", None,
    None, "map-ctygena", "map-ctygenb", "map-ctyslumb", None,
    None, "map-ctyfarma", "map-ctygenc", None, "map-ctysluma",
    None, "map-ctymarka", "map-ctypala", "map-ctymarkb", "map-ctyindb",
    None, "map-ctyfarmb", "map-ctypalb", None, "map-ctyinda",
    None, "map-ctyporta", "map-ctyportb", "map-ctyportc", None,
    None, "map-ctyportd", "map-ctyporte", "map-ctyportf", None,
]
CELL = 1572864.0          # 384 m in game units (4096 a meter)
CELL_ORIGIN = -3145728.0  # x (or z) where column (or row) 0 starts: -768 m
CORNER0 = -4456448.0      # a texture's top left corner for column (or row) 0: -1088 m
SPAN = 4194304.0          # 1024 m, the side a minimap texture covers
SIDE = 256                # most texels on a side of a zone's map
BLACK = (0, 0, 0, 128)


def level_cells(name: str) -> list[int]:
    """The minimap cells level NAME covers (its city-map-bits, level-info.gc)."""
    text = LEVEL_INFO.read_text(encoding="utf-8")
    start = text.index(f"(define {name} (new 'static 'level-load-info")
    m = re.search(r":city-map-bits \(city-map-bits ([^)]*)\)", text[start:start + 3000])
    if not m:
        sys.exit(f"{name}: no city-map-bits")
    return [int(b[3:]) for b in m.group(1).split()]


def texture(name: str) -> Image.Image:
    """The decompiled minimap texture NAME, from its city section's own minimap page."""
    hits = sorted(TEXTURES.glob(f"cty*-minimap/{name}.png"))
    if not hits:
        sys.exit(f"{name}.png not found under {TEXTURES} (run `task extract` first)")
    return Image.open(hits[0]).convert("RGBA")


def swizzle(i: int) -> int:
    """Position of palette entry I in a PS2 ct32 palette (bits 3 and 4 swapped)."""
    return (i & 0xE7) | ((i & 8) << 1) | ((i & 16) >> 1)


def tex0(w: int, h: int) -> int:
    """GS TEX0 of a map: tbp0 8, tbw w / 64, psm mt8 (#x13), tw and th their log2, cld 1."""
    tw = max(1, math.ceil(math.log2(w)))
    th = max(1, math.ceil(math.log2(h)))
    return 8 | ((w // 64) << 14) | (0x13 << 20) | (tw << 26) | (th << 30) | (1 << 61)


def zone_map(levels):
    """The map of a zone made of LEVELS (None: every cell with a texture, the whole city): its image
    and (x0, z0, texel, width, height, valid width, texture names)."""
    if levels is None:
        # the stadium's texture page is not among the extracted ones: its cell stays black
        cells = [c for c in range(len(CELLS)) if CELLS[c] and any(TEXTURES.glob(f"cty*-minimap/{CELLS[c]}.png"))]
    else:
        cells = sorted({c for lev in levels for c in level_cells(lev)})
    cols = [c % 5 for c in cells]
    rows = [c // 5 for c in cells]
    x0 = CELL_ORIGIN + min(cols) * CELL
    z0 = CELL_ORIGIN + min(rows) * CELL
    width = (max(cols) - min(cols) + 1) * CELL
    height = (max(rows) - min(rows) + 1) * CELL
    texel = max(width, height) / SIDE
    w_valid = round(width / texel)
    h = round(height / texel)
    w = math.ceil(w_valid / 64) * 64
    tiles = {c: texture(CELLS[c]) for c in cells if CELLS[c]}
    img = Image.new("RGBA", (w, h), BLACK)
    px = img.load()
    for v in range(h):
        z = z0 + (v + 0.5) * texel
        row = int((z - CELL_ORIGIN) // CELL)
        for u in range(w_valid):
            x = x0 + (u + 0.5) * texel
            col = int((x - CELL_ORIGIN) // CELL)
            cell = row * 5 + col
            if cell not in cells:
                continue
            order = ([cell] if cell in tiles else []) + [c for c in tiles if c != cell]
            for c in order:
                # a texture covers 1024 m whatever its size (the south edge's are 128 high)
                tx = int((x - (CORNER0 + (c % 5) * CELL)) * tiles[c].size[0] // SPAN)
                ty = int((z - (CORNER0 + (c // 5) * CELL)) * tiles[c].size[1] // SPAN)
                if 0 <= tx < tiles[c].size[0] and 0 <= ty < tiles[c].size[1]:
                    px[u, v] = tiles[c].getpixel((tx, ty))
                    break
    return img, (x0, z0, texel, w, h, w_valid, [CELLS[c] for c in cells if CELLS[c]]), cells


def rows(values, per_line, fmt):
    return "\n".join("    " + " ".join(fmt(v) for v in values[i:i + per_line])
                     for i in range(0, len(values), per_line))


def main() -> None:
    png_dir = pathlib.Path(sys.argv[sys.argv.index("--png") + 1]) if "--png" in sys.argv else None
    images = []
    infos = []
    for label, levels in ZONES:
        img, info, cells = zone_map(levels)
        images.append(img)
        infos.append(info)
        print(f"{label}: levels {levels}, cells {cells}, {info[5]} x {info[4]} texels of "
              f"{info[2] / 4096:.1f} m (stored {info[3]} wide), textures {info[6]}")
        if png_dir:
            img.convert("RGB").save(png_dir / f"zone-{label.replace(' ', '-').lower()}.png")

    colors: list[tuple[int, int, int, int]] = []
    index = {}
    words = []
    offsets = []
    for img in images:
        data = img.tobytes()
        out = bytearray()
        for i in range(0, len(data), 4):
            color = tuple(data[i:i + 4])
            if color not in index:
                index[color] = len(colors)
                colors.append(color)
            out.append(index[color])
        offsets.append(len(words))
        words.extend(struct.unpack(f"<{len(out) // 8}Q", bytes(out)))
    if len(colors) > 256:
        sys.exit(f"{len(colors)} colors: more than a palette holds")
    clut = [0] * 256
    for i, (r, g, b, a) in enumerate(colors):
        clut[swizzle(i)] = r | (g << 8) | (b << 16) | (a << 24)
    print(f"{len(colors)} colors, {len(words) * 8} bytes of texels")

    names = " ".join('"' + " ".join(i[6]) + '"' for i in infos)
    n = len(ZONES)
    OUT.write_text(f""";;-*-Lisp-*-
(in-package goal)

;; name: battlefront-minimaps.gc
;; name in dgo: battlefront-minimaps
;; dgos: GAME

#|
  Battlefront mod -- the minimap of each war zone's whole district, for the zone and side pages of
  the battle menu (battlefront.gc `bf-draw-zone-minimap`).

  GENERATED by scripts/battlefront/make_minimaps.py from the decompiled minimap textures: do not
  edit by hand. Each zone's map covers the minimap cells of its levels, made of the textures the
  game's minimap shows there; x along world x, y along world z; the cells of other levels are
  black. The city sections keep their minimap textures in their own texture pages, loaded only
  with the section: the menu needs every zone's, wherever the player stands.
|#

;; DECOMP BEGINS

;; Texels of the zones' maps, one after the other: 8-bit palette indices, row after row.
(define *bf-zone-minimap-texels*
  (new 'static 'array uint64 {len(words)}
{rows(words, 6, lambda v: f"#x{v:016x}")}
    )
  )

;; Their shared palette, 16 x 16 ct32 in the PS2 order (entry i at i with bits 3 and 4 swapped).
(define *bf-zone-minimap-clut*
  (new 'static 'array uint32 256
{rows(clut, 8, lambda v: f"#x{v:08x}")}
    )
  )

;; Where each zone's texels start in `*bf-zone-minimap-texels*`, in 64-bit words.
(define *bf-zone-minimap-offset* (new 'static 'array int32 {n} {" ".join(str(o) for o in offsets)}))

;; Each zone's map: stored width, height, and the width the map fills (the rest is padding).
(define *bf-zone-minimap-size*
  (new 'static 'array int32 {3 * n}
{rows([v for i in infos for v in (i[3], i[4], i[5])], 3, str)}
    )
  )

;; World x and z of each map's top left corner, and the world units a texel covers.
(define *bf-zone-minimap-corner*
  (new 'static 'array float {3 * n}
{rows([v for i in infos for v in (i[0], i[1], i[2])], 3, lambda v: f"{v:.1f}")}
    )
  )

;; GS TEX0 of each map as uploaded (tbp 8, its buffer width, mt8, its size, palette loaded).
(define *bf-zone-minimap-tex0*
  (new 'static 'array uint64 {n} {" ".join(f"#x{tex0(i[3], i[4]):x}" for i in infos)})
  )

;; The minimap textures each zone's map is made of, as engine/ui/minimap.gc names them.
(define *bf-zone-minimap-name* (new 'static 'boxed-array :type string {names}))
""", encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
