"""Make the Battlefront class page's pictures (goal_src/jak3/pc/features/battlefront/battlefront-portraits.gc).

The pictures come from smoke scenario 53 (docs/modding/current_mod/battlefront_smoke.gc
`smoke-s53`), Baron Praxis's from scenario 128 (round 45), Ashelin's from scenario 139 (round 53):
each class model alone on black, a screenshot each, `smoke-portrait-<class>.png`.
The game runs in a 640 x 480 window and its screenshots come out 1280 x 720, stretched across: they
are squeezed back to 960 x 720 first. Each picture keeps the model's whole height and a width of
two thirds of it around the model's middle, shrunk to CELL_W x CELL_H texels, its black background
transparent. The ten cells (51 texels wide since round 53, 56 for nine before) sit side by side in one 512 x 128 texture of 8-bit palette indices, one
256-color palette for all (index 0 transparent), uploaded and drawn as the war zone's map is
(battlefront.gc `bf-draw-portrait`). A cell for each slot of the class page (side times 4 plus row,
Ashelin, the Freedom League's fifth row, slot 9):
round 46's Freedom League robotguard and spider robot (slots 2 and 3) are the red ones' pictures
with the red turned blue by the models' rule (models.jsonc "recolor", mod_models.py
`recolor_pixels`), as their models are.

Usage: python scripts/battlefront/make_portraits.py [shots folder]  (default out/smoke/53, then out/smoke/128, out/smoke/r53-ashelin)
"""

import math
import struct
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "modding"))
from mod_models import recolor_pixels  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SHOTS = [Path(sys.argv[1])] if len(sys.argv) > 1 else [ROOT / "out" / "smoke" / "53", ROOT / "out" / "smoke" / "128",
                                                       ROOT / "out" / "smoke" / "r53-ashelin"]
OUT = ROOT / "goal_src" / "jak3" / "pc" / "features" / "battlefront" / "battlefront-portraits.gc"

# the page's slots (side x 4 + row): blue guard, blue jetpack, blue robotguard, blue spider, red guard,
# red jetpack, robotguard, spider, Baron, Ashelin (slot 9, round 53); each the picture of a class
# (BF_CLASS_*), recolored blue for slots 2 and 3
CLASSES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
PICTURE = {2: 6, 3: 7}
BLUE = {"hues": [-15, 15], "rotate": 217, "min_saturation": 0.3}  # models.jsonc's bf-robot-blue rule
CELL_W, CELL_H = 51, 93
TEX_W, TEX_H = 512, 128
BLACK = 14  # a pixel this dark or darker is the background


def swizzle(i: int) -> int:
    """Position of palette entry I in a PS2 ct32 palette (bits 3 and 4 swapped)."""
    return (i & 0xE7) | ((i & 8) << 1) | ((i & 16) >> 1)


def tex0(w: int, h: int) -> int:
    """GS TEX0: tbp0 8, tbw w / 64, psm mt8 (#x13), tw and th their log2, tcc (texture alpha), cld 1."""
    tw = max(1, math.ceil(math.log2(w)))
    th = max(1, math.ceil(math.log2(h)))
    return 8 | ((w // 64) << 14) | (0x13 << 20) | (tw << 26) | (th << 30) | (1 << 34) | (1 << 61)


def cell(path: Path) -> Image.Image:
    """One class's picture: un-stretched, cropped around the model, CELL_W x CELL_H, RGBA."""
    img = Image.open(path).convert("RGB").resize((960, 720), Image.LANCZOS)
    px = img.load()
    xs, ys, wsum, xsum = [], [], 0, 0
    for y in range(720):
        for x in range(960):
            if max(px[x, y]) > BLACK:
                xs.append(x)
                ys.append(y)
                wsum += 1
                xsum += x
    if not xs:
        sys.exit(f"{path.name}: nothing but black")
    top, bottom = min(ys), max(ys)
    height = bottom - top + 1
    width = height * CELL_W // CELL_H
    mid = xsum // wsum
    left = max(0, min(960 - width, mid - width // 2))
    box = img.crop((left, top, left + width, top + height)).resize((CELL_W, CELL_H), Image.LANCZOS)
    rgba = Image.new("RGBA", box.size)
    out = rgba.load()
    src = box.load()
    for y in range(CELL_H):
        for x in range(CELL_W):
            r, g, b = src[x, y]
            out[x, y] = (r, g, b, 0 if max(r, g, b) <= BLACK else 255)
    return rgba


def main():
    atlas = Image.new("RGBA", (TEX_W, TEX_H), (0, 0, 0, 0))
    for k, c in enumerate(CLASSES):
        src = PICTURE.get(c, c)
        found = [d / f"smoke-portrait-{src}.png" for d in SHOTS if (d / f"smoke-portrait-{src}.png").exists()]
        if not found:
            sys.exit(f"smoke-portrait-{src}.png missing from {SHOTS}: run smoke scenario 53 (128 for the Baron, 139 for Ashelin) first")
        pic = cell(found[0])
        if c in PICTURE:
            pixels = bytearray(pic.tobytes())
            recolor_pixels(pixels, BLUE["hues"], BLUE["rotate"], BLUE["min_saturation"])
            pic = Image.frombytes("RGBA", pic.size, bytes(pixels))
        atlas.paste(pic, (k * CELL_W, 0))
    # one palette for every picture: 255 colors for the model, index 0 transparent
    rgb = atlas.convert("RGB").quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    pal = rgb.getpalette()[: 255 * 3]
    alpha = atlas.getchannel("A").load()
    idx = rgb.load()
    texels = bytearray()
    for y in range(TEX_H):
        for x in range(TEX_W):
            texels.append(0 if alpha[x, y] == 0 else idx[x, y] + 1)
    clut = [0] * 256
    for i in range(255):
        r, g, b = pal[3 * i: 3 * i + 3]
        clut[swizzle(i + 1)] = r | (g << 8) | (b << 16) | (0x80 << 24)
    words = struct.unpack(f"<{len(texels) // 8}Q", bytes(texels))
    cells = [-1] * len(CLASSES)
    for k, c in enumerate(CLASSES):
        cells[c] = k

    def rows(values, per, fmt):
        return "\n".join("    " + " ".join(fmt(v) for v in values[i:i + per]) for i in range(0, len(values), per))

    OUT.write_text(f""";;-*-Lisp-*-
(in-package goal)

;; name: battlefront-portraits.gc
;; name in dgo: battlefront-portraits
;; dgos: GAME

#|
  Battlefront mod -- the class page's picture of each class (battlefront.gc `bf-draw-portrait`).

  GENERATED by scripts/battlefront/make_portraits.py from smoke scenarios 53, 128 and 139's screenshots (each
  class model alone on black): do not edit by hand. One {TEX_W} x {TEX_H} texture of 8-bit palette
  indices, a {CELL_W} x {CELL_H} cell for each class side by side, palette index 0 transparent.
|#

;; DECOMP BEGINS

;; Texels, row after row ({TEX_W} a row).
(define *bf-portrait-texels*
  (new 'static 'array uint64 {len(words)}
{rows(words, 6, lambda v: f"#x{v:016x}")}
    )
  )

;; The palette, ct32 in the PS2's swizzled order.
(define *bf-portrait-clut*
  (new 'static 'array uint32 256
{rows(clut, 8, lambda v: f"#x{v:08x}")}
    )
  )

;; GS TEX0 of the texture as uploaded (tbp 8, mt8, {TEX_W} x {TEX_H}, its alpha used, palette loaded).
(define *bf-portrait-tex0* (new 'static 'array uint64 1 #x{tex0(TEX_W, TEX_H):x}))

;; The cell of each slot of the class page (side x 4 + row: BF_CLASS_* but the Freedom League's
;; blue robotguard and spider robot, 2 and 3; Ashelin, its fifth row, 9), -1 for none.
(define *bf-portrait-cell* (new 'static 'array int32 {len(cells)} {" ".join(str(v) for v in cells)}))

(defconstant BF_PORTRAIT_W {CELL_W}) ;; a cell's texels across
(defconstant BF_PORTRAIT_H {CELL_H}) ;; and down
(defconstant BF_PORTRAIT_TEX_W {TEX_W})
(defconstant BF_PORTRAIT_TEX_H {TEX_H})
""", encoding="utf-8", newline="\n")
    print(f"{OUT.relative_to(ROOT)}: {len(CLASSES)} pictures, {len(texels)} bytes of texels")


if __name__ == "__main__":
    main()
