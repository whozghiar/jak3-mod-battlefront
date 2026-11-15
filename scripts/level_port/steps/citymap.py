"""The source game's city map as one 8-bit picture for the mod's menus (a GOAL file of static arrays,
read by the mod's GAME code): the textures the source game's minimap shows over its city grid,
assembled in world space, cropped to what they show and reduced to 255 colors.

Manifest, at the top:
  "city_map": {
    "file": the GOAL file written (only forms: the mod's GAME code reads them with read-data-file),
    "var": the names' stem: *<var>-texels*, *<var>-clut*, *<var>-size*, *<var>-corner*, *<var>-tex0*,
    "minimap": the source game's minimap code, whose *minimap-texture-name-array* and
               *minimap-corner-array* lay its textures out (goal_src/jak2/engine/ui/minimap.gc),
    "textures": [[the source texture page, [its textures]], ...]: where each one is,
    "max_size": [texels across, texels down] at most (256 across: the GS upload's buffer width)
  }
Inputs: the source game's texture PNGs, decompiler_out/<game>/textures/<page>/<texture>.png (the
extract step writes them when the manifest has a city_map).

How the minimap lays its textures out (Jak 2 and Jak 3, minimap.gc): the city is a grid of cells of
CELL (384 m); the texture of a cell covers SPAN (1024 m) from its corner in *minimap-corner-array*,
its cell in the middle, x along world x and y along world z. A texel of the map takes the texture of
its cell, else the nearest texture covering it; the textures' alpha is laid over black.

The picture's form is the PC port's map texture upload's (bigmap.gc pc-upload-map-texture): mt8
texels, 8 to a 64-bit word, row after row, and a 16 x 16 ct32 palette in the PS2 order (entry i at i
with bits 3 and 4 swapped, alpha 128 full), its stored width a multiple of 64 (the GS buffer width
unit), padded with black.
"""

import math
import os
import re
import struct

from ..common import files
from ..common import glb

METER = 4096.0
SPAN = 1024.0  # meters a minimap texture covers, whatever its size


def read_grid(path):
    """The source minimap's 35 cells: [(texture name or None, (corner x, corner z) meters)]."""
    text = open(path, encoding="utf-8").read()
    names_at = text.index("(define *minimap-texture-name-array*")
    names_block = text[names_at:text.index("(define", names_at + 10)]
    names = [None if t == "#f" else t.strip('"')
             for t in re.findall(r'(#f|"map-[a-z0-9-]+")', names_block)]
    corners_at = text.index("(define *minimap-corner-array*")
    corners_block = text[corners_at:text.index("(define", corners_at + 10)]
    corners = [(float(x) / METER, float(z) / METER) for x, z in re.findall(
        r":x (-?[0-9.]+) :z (-?[0-9.]+)", corners_block)]
    if len(names) != 35 or len(corners) != 35:
        raise ValueError(f"{path}: {len(names)} names and {len(corners)} corners, not 35")
    return list(zip(names, corners))


def swizzle(i):
    """Position of palette entry I in a PS2 ct32 palette (bits 3 and 4 swapped)."""
    return (i & 0xE7) | ((i & 8) << 1) | ((i & 16) >> 1)


def median_cut(counts, n):
    """At most N colors standing for the (r, g, b): count colors: [palette], {color: index}."""
    boxes = [list(counts)]
    while len(boxes) < n:
        # the box of the widest channel range among those with two colors or more
        best, best_range, best_ch = None, -1, 0
        for b in boxes:
            if len(b) < 2:
                continue
            for ch in range(3):
                vals = [c[ch] for c in b]
                r = max(vals) - min(vals)
                if r > best_range:
                    best, best_range, best_ch = b, r, ch
        if best is None or best_range == 0:
            break
        best.sort(key=lambda c: c[best_ch])
        total = sum(counts[c] for c in best)
        acc, cut = 0, 1
        for i, c in enumerate(best):
            acc += counts[c]
            if acc * 2 >= total:
                cut = max(1, min(len(best) - 1, i + 1))
                break
        boxes.remove(best)
        boxes += [best[:cut], best[cut:]]
    palette, index = [], {}
    for b in boxes:
        total = sum(counts[c] for c in b)
        palette.append(tuple(round(sum(c[ch] * counts[c] for c in b) / total) for ch in range(3)))
        for c in b:
            index[c] = len(palette) - 1
    return palette, index


def tex0(w, h):
    """GS TEX0 of a map: tbp0 8, tbw w / 64, psm mt8 (#x13), tw and th their log2, cld 1."""
    tw = max(1, math.ceil(math.log2(w)))
    th = max(1, math.ceil(math.log2(h)))
    return 8 | ((w // 64) << 14) | (0x13 << 20) | (tw << 26) | (th << 30) | (1 << 61)


def rows(values, per_line, fmt):
    return "\n".join("    " + " ".join(fmt(v) for v in values[i:i + per_line])
                     for i in range(0, len(values), per_line))


def texture_paths(port):
    """{texture name: its PNG} of the city_map's textures, and the source level of each page."""
    cfg = port["city_map"]
    out = {}
    for page, names in cfg["textures"]:
        for name in names:
            out[name] = f"decompiler_out/{port.source.NAME}/textures/{page}/{name}.png"
    return out


def run(port):
    if "city_map" not in port.data:
        return
    cfg = port["city_map"]
    grid = read_grid(cfg["minimap"])
    cell = grid[1][1][0] - grid[0][1][0]          # 384 m
    margin = (SPAN - cell) / 2                    # a texture's corner is this far before its cell
    origin = grid[0][1][0] + margin               # where column (and row) 0 starts
    paths = texture_paths(port)
    tiles = {}
    for k, (name, corner) in enumerate(grid):
        if name:
            w, h, px = glb.png_decode(open(paths[name], "rb").read())
            tiles[k] = (corner, w, h, px)

    def sample(x, z):
        """(r, g, b) of the map at world x, z (meters), its alpha laid over black; None outside
        every texture."""
        col, row = int((x - origin) // cell), int((z - origin) // cell)
        own = row * 5 + col if 0 <= col < 5 and 0 <= row < 7 else -1
        order = sorted(tiles, key=lambda k: (k != own, (k % 5 - col) ** 2 + (k // 5 - row) ** 2))
        for k in order:
            (cx, cz), w, h, px = tiles[k]
            tx, ty = int((x - cx) * w // SPAN), int((z - cz) * h // SPAN)
            if 0 <= tx < w and 0 <= ty < h:
                i = 4 * (ty * w + tx)
                a = px[i + 3]
                return tuple(px[i + ch] * a // 255 for ch in range(3)), a
        return None

    # the area the textures show (alpha), on a 8 m grid
    x0 = min(c[0] for c, _, _, _ in tiles.values())
    z0 = min(c[1] for c, _, _, _ in tiles.values())
    x1 = max(c[0] for c, _, _, _ in tiles.values()) + SPAN
    z1 = max(c[1] for c, _, _, _ in tiles.values()) + SPAN
    lo_x, lo_z, hi_x, hi_z = x1, z1, x0, z0
    step = 8.0
    z = z0
    while z < z1:
        x = x0
        while x < x1:
            s = sample(x, z)
            if s and s[1] > 16 and sum(s[0]) > 24:
                lo_x, lo_z, hi_x, hi_z = min(lo_x, x), min(lo_z, z), max(hi_x, x), max(hi_z, z)
            x += step
        z += step
    lo_x, lo_z, hi_x, hi_z = lo_x - 16, lo_z - 16, hi_x + 16 + step, hi_z + 16 + step
    max_w, max_h = cfg.get("max_size", [256, 384])
    texel = max((hi_x - lo_x) / max_w, (hi_z - lo_z) / max_h)
    w_valid = min(max_w, round((hi_x - lo_x) / texel))
    h = min(max_h, round((hi_z - lo_z) / texel))
    w = math.ceil(w_valid / 64) * 64

    pixels = []
    for v in range(h):
        z = lo_z + (v + 0.5) * texel
        for u in range(w):
            s = sample(lo_x + (u + 0.5) * texel, z) if u < w_valid else None
            pixels.append(s[0] if s else (0, 0, 0))
    counts = {}
    for c in pixels:
        counts[c] = counts.get(c, 0) + 1
    palette, index = median_cut(counts, 256)
    texels = bytes(index[c] for c in pixels)
    words = struct.unpack(f"<{len(texels) // 8}Q", texels)
    clut = [0] * 256
    for i, (r, g, b) in enumerate(palette):
        clut[swizzle(i)] = r | (g << 8) | (b << 16) | (128 << 24)

    var = cfg["var"]
    lines = port.generated_lines()
    text = "\n".join([
        ";;-*-Lisp-*-",
        "",
        *lines,
        f";; The source game's city map ({w_valid} x {h} texels of {texel:.2f} m, stored {w} wide,",
        f";; {len(palette)} colors), read by the mod's GAME code (read-data-file): scripts/level_port/steps/citymap.py.",
        "",
        ";; Its texels: 8-bit palette indices, row after row.",
        f"(define *{var}-texels*",
        f"  (new 'static 'array uint64 {len(words)}",
        rows(words, 6, lambda x: f"#x{x:016x}"),
        "    )",
        "  )",
        "",
        ";; Its palette, 16 x 16 ct32 in the PS2 order (entry i at i with bits 3 and 4 swapped).",
        f"(define *{var}-clut*",
        "  (new 'static 'array uint32 256",
        rows(clut, 8, lambda x: f"#x{x:08x}"),
        "    )",
        "  )",
        "",
        ";; Its stored width, height, and the width the map fills (the rest is padding).",
        f"(define *{var}-size* (new 'static 'array int32 3 {w} {h} {w_valid}))",
        "",
        ";; World x and z of its top left corner, and the world units a texel covers.",
        f"(define *{var}-corner* (new 'static 'array float 3 {lo_x * METER:.1f} {lo_z * METER:.1f} {texel * METER:.1f}))",
        "",
        ";; GS TEX0 of the map as uploaded (tbp 8, its buffer width, mt8, its size, palette loaded).",
        f"(define *{var}-tex0* (new 'static 'array uint64 1 #x{tex0(w, h):x}))",
        "",
    ])
    files.write_if_changed(cfg["file"], text)
    print(f"  {cfg['file']}: {w_valid} x {h} texels of {texel:.2f} m from x {lo_x:.0f} z {lo_z:.0f} m, "
          f"{len(palette)} colors, {len(tiles)} textures")
