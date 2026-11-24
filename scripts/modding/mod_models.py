#!/usr/bin/env python3
"""
Make a mod's models from the games' own discs, as its manifest describes, so that a mod ships no
model taken from a game: custom_assets/<game>/models/models.jsonc.

    python scripts/modding/mod_models.py                 # every game with a manifest
    python scripts/modding/mod_models.py --game jak3     # one game's
    python scripts/modding/mod_models.py --check         # only list what is missing

At a mod's install from the OpenGOAL Launcher, the mod's extractor runs this tool (a one-file
executable, mod_models, that the release builds) before its decompile, whose level extraction
bakes the models into their levels (decompiler/extractor/main.cpp, run_mod_models): --root is then
the mod's data/ folder, --iso the games' extracted discs of the player's install, --extractor that
extractor, which rips the levels the models come from.

The manifest (comments allowed):

  {
    "games": ["jak2", "jak3"],                 // the discs it needs (the extractor checks that
                                               // the player has them)
    "rips": {"jak2/forresca": "FRA.DGO"},      // each rip folder used below, and its DGO
    "models": {
      "<name>": {
        "level": "ctypesa",                    // the level whose .fr3 gets the mesh (optional)
        "mesh": "jak2/forresca/crimson-guard-lod0.glb",    // <game>/<rip folder>/<rip file>
        "prims": [4, 5, 6],                    // the mesh's primitives kept (optional: all)
        "skeleton": "jak3/ctypesa/crimson-guard-lod0.glb", // skeleton and clips from another rip
                                               // (same joint names and bind poses; optional)
        "padding": 2,                          // copies of the first clip before the others
        "clips": ["idle", "walk"],             // the clips in this order (optional: the rip's)
        "clip_prefix": "",                     // the rip's clip names start with it
        "textures_from": "jak3/ctypesa/crimson-guard-lod0.glb", // images of the same name taken
        "texture_prefix": "cguardgame-",       // from this rip (those starting with the prefix)
        "recolor": {"hues": [-15, 15], "rotate": 217, "min_saturation": 0.3},
                                               // a color variant: the texels of a hue in hues
                                               // (degrees, lo below 0 wraps around red) and that
                                               // saturated turned by rotate degrees; "textures":
                                               // [names] limits it to those images (optional)
        "extra": [{"mesh": "jak3/ctypesa/crimson-guard-lod0.glb", "prims": [4, 5], "suffix": "j3"}],
                                               // primitives of other rips added to the mesh, with
                                               // their own textures, each image renamed
                                               // <image>-<suffix> (the same names as the mesh's
                                               // stay apart); their joints matched by name to the
                                               // skeleton, same bind poses (optional)
        "clip_file": "custom_assets/jak3/models/bf-baron-clips.glb",
                                               // the mod's own clips, added after the rip's: a
                                               // .glb of the repo with joints (names) and
                                               // animations only, made from the game's skeleton
                                               // (Jak Animation Studio); each channel goes to the
                                               // joint of that name, a joint a clip leaves out
                                               // keeps its rest pose (optional)
        "rip_clips": 1,                        // how many of the rip's clips come first (optional:
                                               // all of them)
        "texture_files": {"programmer_eye_left": "jak2/ldjakbrn-pris/baron-eye.png"},
                                               // an image of the mesh replaced by a texture of the
                                               // disc (<game>/<tpage>/<texture>.png, which the
                                               // extraction writes with the DGO the rips give for
                                               // <game>/<tpage>; optional)
        "blades": [{"joint": "sword", "base": [0.74, 1.86, 0.3], "tip": [0.45, 0.57, -1.47],
                    "flat": [0.28, -0.8, 0.53], "width": 0.2, "thickness": 0.045,
                    "material": "baron-brushedmetal-envmap"}]
                                               // a straight blade made here (no rip): a diamond
                                               // section from base to a point at tip, its width
                                               // along flat, bound to the joint, drawn with a
                                               // material of the mesh (optional)
        "mirror_props": [{"prims": [0, 1, 2, 16], "joint": "gun", "holder": "Rhand", "to": "Lhand",
                          "clip": "ashelin-standing-fire"}],
                                               // a copy of those primitives of the rip (a prop on
                                               // `joint`, held by `holder` in that clip of the rip)
                                               // in the other hand `to`, mirrored across x through
                                               // the hold, bound to `to` alone (optional)
        "attach": {"joint": "gun", "holder": "Rhand", "clip": "ashelin-standing-fire"},
                                               // every made clip keeps `joint` held by `holder` as
                                               // in that clip of the rip (optional)
        "made_from": "custom_assets/jak3/models/bf-ashelin-clips.glb",
                                               // a clip file (as clip_file's) the made clips may
                                               // also draw on by name, the rip's first (optional)
        "made_clips": [{"name": "roll-left", "like": "roll-right", "mirror": true}, ...]
                                               // clips made from the rip's own, after the others,
                                               // at 30 keys a second (optional): each from "from"
                                               // (a rip clip), "concat" (rip or made clips in turn)
                                               // or "like" (a made clip); then "keys" [a, b] (keys a
                                               // to b - 1), "hold" [key, count] (that pose, count
                                               // keys), "flat_root" (`main` keeps its rest place
                                               // across), "mirror" (the whole clip mirrored across
                                               // x, left and right joints swapped), "mirror_limbs"
                                               // ([joints]: each limb from that joint turned as the
                                               // mirror of the other side's), "turns" ([{"joint",
                                               // "axis", "deg", "to", "smooth"}]: a joint turned in
                                               // the model's space, by deg, or from deg to `to`
                                               // over the clip), "lift" (main raised along a sine),
                                               // "pose_from" ([{"clip", "key", "joints"}]: those
                                               // joints held at their turn in that key of a clip);
                                               // "temp": a step for other recipes, not a clip
      }
    },
    "files": {"custom_assets/jak3/music/X.MUS": "jak2/MUS/DANGER4.MUS"}  // copies from a disc
  }

An image a recolor rule changes is renamed <image>-<model>: two variants of one rip baked into
the same level keep their own textures. Each model is written twice, same content: custom_assets/<game>/models/custom_levels/<name>.glb,
which build-actor reads (art group <name>-ag), and custom_assets/<game>/models/<level>/
<name>-lod0.glb, which the level extraction (task extract) bakes into <level>.fr3 for the
renderer. A missing rip is extracted first: the decompiler of out/build/Release/bin on
iso_data/<game> (rip_levels, only the DGOs needed), or the --extractor given. A file is only
rewritten when its content changes. Needs numpy.
"""
from __future__ import annotations

import argparse
import base64
import colorsys
import json
import os
import re
import struct
import subprocess
import sys
import zlib
from pathlib import Path

import numpy as np

EXE = ".exe" if os.name == "nt" else ""
VERSION = "ntsc_v1"

COMPONENT = {5126: np.float32, 5125: np.uint32, 5123: np.uint16, 5121: np.uint8}
WIDTH = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


class Glb:
    """A parsed .glb: its JSON and binary chunk, with typed accessor reads."""

    def __init__(self, path: Path):
        data = path.read_bytes()
        json_len = struct.unpack_from("<I", data, 12)[0]
        self.json = json.loads(data[20:20 + json_len])
        off = 20 + json_len
        bin_len = struct.unpack_from("<I", data, off)[0]
        self.bin = data[off + 8:off + 8 + bin_len]
        self.path = path

    def accessor(self, index: int) -> np.ndarray:
        acc = self.json["accessors"][index]
        view = self.json["bufferViews"][acc["bufferView"]]
        dtype = COMPONENT[acc["componentType"]]
        width = WIDTH[acc["type"]]
        start = view.get("byteOffset", 0) + acc.get("byteOffset", 0)
        stride = view.get("byteStride", 0)
        item = np.dtype(dtype).itemsize * width
        if stride and stride != item:
            raw = np.frombuffer(self.bin, dtype=np.uint8, count=stride * acc["count"], offset=start)
            raw = raw.reshape(acc["count"], stride)[:, :item].copy()
            return raw.view(dtype).reshape(acc["count"], width)
        return np.frombuffer(self.bin, dtype=dtype, count=acc["count"] * width,
                             offset=start).reshape(acc["count"], width).copy()

    def view_bytes(self, index: int) -> bytes:
        view = self.json["bufferViews"][index]
        start = view.get("byteOffset", 0)
        return self.bin[start:start + view["byteLength"]]

    def joint_names(self) -> list[str]:
        skin = self.json["skins"][0]
        return [self.json["nodes"][i]["name"] for i in skin["joints"]]


class Writer:
    """Collects glTF objects and one binary buffer, then writes a .glb."""

    def __init__(self):
        self.json = {"asset": {"version": "2.0", "generator": "OpenGOAL mod_models.py"},
                     "scene": 0, "scenes": [{"nodes": []}], "nodes": [], "meshes": [],
                     "materials": [], "textures": [], "images": [], "samplers": [],
                     "accessors": [], "bufferViews": [], "skins": [], "animations": []}
        self.bin = bytearray()

    def view(self, data: bytes, target: int | None = None) -> int:
        while len(self.bin) % 4:
            self.bin.append(0)
        view = {"buffer": 0, "byteOffset": len(self.bin), "byteLength": len(data)}
        if target:
            view["target"] = target
        self.bin.extend(data)
        self.json["bufferViews"].append(view)
        return len(self.json["bufferViews"]) - 1

    def accessor(self, array: np.ndarray, kind: str, component: int, target: int | None = None,
                 minmax: bool = False) -> int:
        array = np.ascontiguousarray(array, dtype=COMPONENT[component])
        acc = {"bufferView": self.view(array.tobytes(), target), "componentType": component,
               "count": int(array.shape[0]), "type": kind}
        if minmax:
            acc["min"] = [float(x) for x in array.reshape(array.shape[0], -1).min(axis=0)]
            acc["max"] = [float(x) for x in array.reshape(array.shape[0], -1).max(axis=0)]
        self.json["accessors"].append(acc)
        return len(self.json["accessors"]) - 1

    def copy_accessor(self, src: Glb, index: int, target: int | None = None) -> int:
        acc = src.json["accessors"][index]
        return self.accessor(src.accessor(index), acc["type"], acc["componentType"], target,
                             "min" in acc)

    def save_bytes(self) -> bytes:
        for key in [k for k, v in self.json.items() if v == []]:
            del self.json[key]
        self.json["buffers"] = [{"byteLength": len(self.bin)}]
        js = json.dumps(self.json, separators=(",", ":")).encode()
        js += b" " * (-len(js) % 4)
        self.bin.extend(b"\0" * (-len(self.bin) % 4))
        out = bytearray(struct.pack("<III", 0x46546C67, 2, 28 + len(js) + len(self.bin)))
        out += struct.pack("<II", len(js), 0x4E4F534A) + js
        out += struct.pack("<II", len(self.bin), 0x004E4942) + self.bin
        return bytes(out)


def image_bytes(src: Glb, image: dict) -> tuple[bytes, str]:
    """Pixels of an image of `src`, embedded (bufferView) or as a data URI."""
    if "bufferView" in image:
        return src.view_bytes(image["bufferView"]), image.get("mimeType", "image/png")
    uri = image["uri"]
    head, payload = uri.split(",", 1)
    return base64.b64decode(payload), head[5:].split(";")[0]


def png_decode(data: bytes) -> tuple[int, int, bytearray]:
    """(width, height, pixels) of an 8 bit RGB or RGBA PNG (the rips' textures): pixels is a
    bytearray of RGBA, row after row."""
    width, height, depth, color = struct.unpack(">IIBB", data[16:26])
    channels = {2: 3, 6: 4}.get(color)
    if depth != 8 or not channels:
        raise ValueError(f"PNG of bit depth {depth}, color type {color}: only 8 bit RGB(A)")
    pos, idat = 8, b""
    while pos < len(data):
        size, kind = struct.unpack(">I4s", data[pos:pos + 8])
        if kind == b"IDAT":
            idat += data[pos + 8:pos + 8 + size]
        pos += 12 + size
    raw = zlib.decompress(idat)
    stride = width * channels
    prev = bytearray(stride)
    out = bytearray()
    for y in range(height):
        kind = raw[y * (stride + 1)]
        row = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            a = row[i - channels] if i >= channels else 0
            b = prev[i]
            c = prev[i - channels] if i >= channels else 0
            if kind == 1:
                row[i] = (row[i] + a) & 255
            elif kind == 2:
                row[i] = (row[i] + b) & 255
            elif kind == 3:
                row[i] = (row[i] + (a + b) // 2) & 255
            elif kind == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                row[i] = (row[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        prev = row
        if channels == 3:
            for x in range(width):
                out += row[3 * x:3 * x + 3] + b"\xff"
        else:
            out += row
    return width, height, out


def png_encode(width: int, height: int, pixels: bytearray) -> bytes:
    """An RGBA PNG (no filter) of pixels (RGBA, row after row)."""
    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(
            ">I", zlib.crc32(kind + body) & 0xFFFFFFFF)
    stride = width * 4
    raw = b"".join(b"\0" + bytes(pixels[y * stride:(y + 1) * stride]) for y in range(height))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def recolor_pixels(pixels: bytearray, hues: list[float], rotate: float, min_saturation: float) -> int:
    """Turn by rotate degrees the hue of the texels whose hue is in hues ([lo, hi] degrees, lo may
    be negative: a window around red) and whose saturation is at least min_saturation, in place
    (RGBA pixels). Returns the number of texels changed. The mod Haven City: New Dawn's rule
    (scripts/level_port/common/glb.py there)."""
    lo, hi = hues
    changed = 0
    for i in range(0, len(pixels), 4):
        h, s, v = colorsys.rgb_to_hsv(pixels[i] / 255, pixels[i + 1] / 255, pixels[i + 2] / 255)
        deg = h * 360.0
        if s >= min_saturation and (lo <= deg <= hi or lo <= deg - 360.0 <= hi):
            r, g, b = colorsys.hsv_to_rgb(((deg + rotate) % 360.0) / 360.0, s, v)
            pixels[i:i + 3] = bytes(int(round(c * 255)) for c in (r, g, b))
            changed += 1
    return changed


def copy_skeleton(out: Writer, src: Glb) -> tuple[int, dict[int, int]]:
    """Copy every node of `src` (meshes detached), its skin and its scene roots.
    Returns the index of the node that carried the skinned mesh and the node index map."""
    node_map = {i: i for i in range(len(src.json["nodes"]))}
    mesh_node = None
    for i, node in enumerate(src.json["nodes"]):
        node = dict(node)
        if "mesh" in node:
            mesh_node = i
            node.pop("mesh")
            node.pop("skin", None)
        out.json["nodes"].append(node)
    skin = dict(src.json["skins"][0])
    skin["inverseBindMatrices"] = out.copy_accessor(src, skin["inverseBindMatrices"])
    out.json["skins"].append(skin)
    out.json["scenes"][0]["nodes"] = list(src.json["scenes"][src.json.get("scene", 0)]["nodes"])
    if mesh_node is None:
        sys.exit(f"{src.path}: no skinned mesh node")
    return mesh_node, node_map


def copy_mesh(out: Writer, src: Glb, mesh_node: int, keep: list[int] | None,
              joint_remap: np.ndarray | None, textures_from: dict[str, tuple[bytes, str]] | None,
              recolor: dict | None = None, model: str = "", append: bool = False,
              image_suffix: str = ""):
    """Copy the skinned mesh of `src` onto node `mesh_node` of `out`.

    keep          primitive indices to keep (None: all)
    joint_remap   JOINTS_0 value map from `src`'s skin to `out`'s (None: unchanged)
    textures_from image name -> pixels replacing `src`'s image of that name
    recolor      the model's recolor rule (None: none); an image it changes is renamed
                 <image>-<model>
    append       add the primitives to the mesh already on `mesh_node` (an "extra" entry)
    image_suffix every image renamed <image>-<suffix> (an "extra" entry's)"""
    mesh = src.json["meshes"][0]
    prims = mesh["primitives"] if keep is None else [mesh["primitives"][i] for i in keep]
    attr_map: dict[tuple[str, int], int] = {}
    image_map: dict[int, int] = {}
    texture_map: dict[int, int] = {}
    material_map: dict[int, int] = {}
    sampler_map: dict[int, int] = {}

    def image(index: int) -> int:
        if index not in image_map:
            img = src.json["images"][index]
            data, mime = image_bytes(src, img)
            if textures_from and img.get("name") in textures_from:
                data, mime = textures_from[img["name"]]
            name = img.get("name", f"image{index}")
            if image_suffix:
                name = f"{name}-{image_suffix}"
            if (recolor and mime == "image/png"
                    and ("textures" not in recolor or name in recolor["textures"])):
                width, height, pixels = png_decode(data)
                if recolor_pixels(pixels, recolor["hues"], recolor["rotate"],
                                  recolor.get("min_saturation", 0.0)):
                    data, name = png_encode(width, height, pixels), f"{name}-{model}"
            out.json["images"].append({"name": name, "mimeType": mime,
                                       "bufferView": out.view(data)})
            image_map[index] = len(out.json["images"]) - 1
        return image_map[index]

    def texture(index: int) -> int:
        if index not in texture_map:
            tex = dict(src.json["textures"][index])
            if "source" in tex:
                tex["source"] = image(tex["source"])
            if "sampler" in tex:
                s = tex["sampler"]
                if s not in sampler_map:
                    out.json["samplers"].append(dict(src.json["samplers"][s]))
                    sampler_map[s] = len(out.json["samplers"]) - 1
                tex["sampler"] = sampler_map[s]
            out.json["textures"].append(tex)
            texture_map[index] = len(out.json["textures"]) - 1
        return texture_map[index]

    def remap_textures(obj):
        # in a material, every dict holding "index" is a texture reference
        if isinstance(obj, dict):
            return {k: texture(v) if k == "index" and isinstance(v, int) else remap_textures(v)
                    for k, v in obj.items()}
        if isinstance(obj, list):
            return [remap_textures(x) for x in obj]
        return obj

    def material(index: int) -> int:
        if index not in material_map:
            out.json["materials"].append(remap_textures(src.json["materials"][index]))
            material_map[index] = len(out.json["materials"]) - 1
        return material_map[index]

    # The rips' vertex attributes cover every merc model of the level (the Jak 2 drillmtn hover
    # guard uses 2447 of 107332 vertices; the others are bound to other skeletons): keep the
    # vertices this mesh's indices reach, renumbered in order.
    if len({json.dumps(p["attributes"], sort_keys=True) for p in prims}) != 1:
        sys.exit(f"{src.path}: primitives do not share their vertex attributes")
    used = np.unique(np.concatenate([src.accessor(p["indices"]).ravel() for p in prims]))
    renumber = np.full(int(used.max()) + 1, -1, dtype=np.int64)
    renumber[used] = np.arange(len(used))

    new_prims = []
    for prim in prims:
        attrs = {}
        for name, acc in prim["attributes"].items():
            key = (name, acc)
            if key not in attr_map:
                info = src.json["accessors"][acc]
                data = src.accessor(acc)[used]
                if name == "JOINTS_0" and joint_remap is not None:
                    data = joint_remap[data.astype(np.int64)]
                if name == "JOINTS_0" and data.max() >= len(out.json["skins"][0]["joints"]):
                    sys.exit(f"{src.path}: a kept vertex is bound to a joint outside the skin")
                attr_map[key] = out.accessor(data, info["type"], info["componentType"], 34962,
                                             name == "POSITION")
            attrs[name] = attr_map[key]
        indices = renumber[src.accessor(prim["indices"]).ravel()]
        new = {"attributes": attrs,
               "indices": out.accessor(indices.reshape(-1, 1), "SCALAR", 5125, 34963),
               "mode": prim.get("mode", 4)}
        if "material" in prim:
            new["material"] = material(prim["material"])
        new_prims.append(new)
    if append:
        out.json["meshes"][out.json["nodes"][mesh_node]["mesh"]]["primitives"].extend(new_prims)
        return
    out.json["meshes"].append({"name": mesh.get("name", "mesh"), "primitives": new_prims})
    node = out.json["nodes"][mesh_node]
    node["mesh"] = len(out.json["meshes"]) - 1
    node["skin"] = 0


def add_blade(out: Writer, mesh_node: int, blade: dict):
    """A straight blade on the mesh of `mesh_node`, in the model's rest space, every vertex bound to
    `blade["joint"]`: a diamond section (its width along `flat`, its thickness across) from `base`,
    narrowing a little toward a point at `tip`; flat-shaded, drawn with the mesh's material named
    `blade["material"]`. Its vertex attributes are the mesh's own kinds (the game's merc reads
    them all)."""
    joints = [out.json["nodes"][j].get("name") for j in out.json["skins"][0]["joints"]]
    if blade["joint"] not in joints:
        sys.exit(f"blade: no joint {blade['joint']}")
    names = [m.get("name") for m in out.json["materials"]]
    if blade["material"] not in names:
        sys.exit(f"blade: no material {blade['material']} ({names})")
    base, tip = np.array(blade["base"], float), np.array(blade["tip"], float)
    axis = (tip - base) / np.linalg.norm(tip - base)
    flat = np.array(blade["flat"], float)
    flat -= axis * np.dot(flat, axis)
    flat /= np.linalg.norm(flat)
    side = np.cross(axis, flat)
    hw, ht = blade["width"] / 2, blade["thickness"] / 2

    def ring(p, k):
        return [p + flat * hw * k, p + side * ht, p - flat * hw * k, p - side * ht]

    near = base + (tip - base) * 0.85
    r0, r1 = ring(base, 1.0), ring(near, 0.8)
    tris = []
    for i in range(4):
        a, b = i, (i + 1) % 4
        tris += [(r0[a], r1[a], r1[b]), (r0[a], r1[b], r0[b]), (r1[a], tip, r1[b])]
    tris += [(r0[0], r0[2], r0[1]), (r0[0], r0[3], r0[2])]
    pos, nrm, uv = [], [], []
    for t in tris:
        n = np.cross(t[1] - t[0], t[2] - t[0])
        n /= np.linalg.norm(n) + 1e-12
        for p in t:
            pos.append(p)
            nrm.append(n)
            along = np.dot(p - base, axis) / np.linalg.norm(tip - base)
            uv.append([0.5 + 0.5 * np.dot(p - base, flat) / hw, along])
    count = len(pos)
    mesh = out.json["meshes"][out.json["nodes"][mesh_node]["mesh"]]
    kinds = mesh["primitives"][0]["attributes"]
    data = {"POSITION": np.array(pos, np.float32), "NORMAL": np.array(nrm, np.float32),
            "TEXCOORD_0": np.array(uv, np.float32),
            "COLOR_0": np.full((count, 4), [0.5, 0.5, 0.5, 1.0], np.float32),
            "JOINTS_0": np.tile(np.array([joints.index(blade["joint"]), 0, 0, 0]), (count, 1)),
            "WEIGHTS_0": np.tile(np.array([1.0, 0.0, 0.0, 0.0], np.float32), (count, 1))}
    attrs = {}
    for name, acc in kinds.items():
        info = out.json["accessors"][acc]
        if name not in data:
            sys.exit(f"blade: the mesh has an attribute {name} a blade does not make")
        arr = data[name].astype(COMPONENT[info["componentType"]])
        attrs[name] = out.accessor(arr, info["type"], info["componentType"], 34962, name == "POSITION")
    indices = np.arange(count, dtype=np.uint32).reshape(-1, 1)
    mesh["primitives"].append({"attributes": attrs, "indices": out.accessor(indices, "SCALAR", 5125, 34963),
                               "mode": 4, "material": names.index(blade["material"])})


def copy_animations(out: Writer, src: Glb, node_map: dict[int, int], padding: int,
                    names: list[str] | None = None, prefix: str = ""):
    """Copy every clip of `src`, after `padding` copies of its first clip; with `names`, in that
    order (prefix + name), failing when one is missing."""
    anims = src.json.get("animations", [])
    if names:
        by_name = {a.get("name"): a for a in anims}
        missing = [n for n in names if prefix + n not in by_name]
        if missing or len(names) != len(anims):
            sys.exit(f"{src.path}: clips {missing} missing, or clips left out of the list")
        anims = [by_name[prefix + n] for n in names]
    order = [anims[0]] * padding + anims
    acc_map: dict[int, int] = {}
    for i, anim in enumerate(order):
        samplers = []
        for s in anim["samplers"]:
            for key in ("input", "output"):
                if s[key] not in acc_map:
                    acc_map[s[key]] = out.copy_accessor(src, s[key])
            samplers.append({"input": acc_map[s["input"]], "output": acc_map[s["output"]],
                             "interpolation": s.get("interpolation", "LINEAR")})
        channels = [{"sampler": c["sampler"],
                     "target": {"node": node_map[c["target"]["node"]], "path": c["target"]["path"]}}
                    for c in anim["channels"]]
        name = anim.get("name", f"clip{i}") if i >= padding else f"padding-{i}"
        out.json["animations"].append({"name": name, "samplers": samplers, "channels": channels})


def node_rest(node: dict) -> dict:
    """A node's rest translation, rotation (quaternion x y z w) and scale, from its TRS or its
    matrix (the decompiler writes a matrix)."""
    if "matrix" not in node:
        return {"translation": node.get("translation", [0.0, 0.0, 0.0]),
                "rotation": node.get("rotation", [0.0, 0.0, 0.0, 1.0]),
                "scale": node.get("scale", [1.0, 1.0, 1.0])}
    m = np.array(node["matrix"], dtype=float).reshape(4, 4).T
    scale = np.linalg.norm(m[:3, :3], axis=0)
    r = m[:3, :3] / scale
    t = np.trace(r)
    if t > 0:
        k = np.sqrt(t + 1.0) * 2
        q = [(r[2, 1] - r[1, 2]) / k, (r[0, 2] - r[2, 0]) / k, (r[1, 0] - r[0, 1]) / k, 0.25 * k]
    elif r[0, 0] > r[1, 1] and r[0, 0] > r[2, 2]:
        k = np.sqrt(1.0 + r[0, 0] - r[1, 1] - r[2, 2]) * 2
        q = [0.25 * k, (r[0, 1] + r[1, 0]) / k, (r[0, 2] + r[2, 0]) / k, (r[2, 1] - r[1, 2]) / k]
    elif r[1, 1] > r[2, 2]:
        k = np.sqrt(1.0 + r[1, 1] - r[0, 0] - r[2, 2]) * 2
        q = [(r[0, 1] + r[1, 0]) / k, 0.25 * k, (r[1, 2] + r[2, 1]) / k, (r[0, 2] - r[2, 0]) / k]
    else:
        k = np.sqrt(1.0 + r[2, 2] - r[0, 0] - r[1, 1]) * 2
        q = [(r[0, 2] + r[2, 0]) / k, (r[1, 2] + r[2, 1]) / k, 0.25 * k, (r[1, 0] - r[0, 1]) / k]
    q = np.array(q) / np.linalg.norm(q)
    return {"translation": list(m[:3, 3]), "rotation": list(q), "scale": list(scale)}


def add_clip_file(out: Writer, clips: Glb, skel: Glb, node_map: dict[int, int]):
    """Add every clip of `clips` (an animation-only .glb: joint nodes by name, animations) to `out`,
    each channel on the joint of `skel` of the same name. A joint a clip leaves out, or one of its
    paths, gets its rest value from `out`'s node as two keys over the clip: build-actor puts a joint
    without keys at the origin."""
    joint_of = {skel.json["nodes"][j]["name"]: node_map[j] for j in skel.json["skins"][0]["joints"]}
    kinds = {"rotation": "VEC4", "translation": "VEC3", "scale": "VEC3"}
    for anim in clips.json.get("animations", []):
        samplers, channels, keyed, end = [], [], {}, 0.0
        for c in anim["channels"]:
            name = clips.json["nodes"][c["target"]["node"]].get("name")
            if name not in joint_of:
                sys.exit(f"{clips.path}: clip {anim.get('name')} keys {name}, not a joint of {skel.path}")
            s = anim["samplers"][c["sampler"]]
            times = clips.accessor(s["input"])
            end = max(end, float(times.max()))
            samplers.append({"input": out.accessor(times, "SCALAR", 5126, minmax=True),
                             "output": out.copy_accessor(clips, s["output"]), "interpolation": "LINEAR"})
            channels.append({"sampler": len(samplers) - 1,
                             "target": {"node": joint_of[name], "path": c["target"]["path"]}})
            keyed.setdefault(joint_of[name], set()).add(c["target"]["path"])
        span = out.accessor(np.array([[0.0], [max(end, 1.0 / 60.0)]], dtype=np.float32), "SCALAR", 5126,
                            minmax=True)
        for node in joint_of.values():
            rest = node_rest(out.json["nodes"][node])
            for path, kind in kinds.items():
                if path in keyed.get(node, ()):
                    continue
                value = np.array([rest[path]] * 2, dtype=np.float32)
                samplers.append({"input": span, "output": out.accessor(value, kind, 5126),
                                 "interpolation": "LINEAR"})
                channels.append({"sampler": len(samplers) - 1, "target": {"node": node, "path": path}})
        out.json["animations"].append({"name": anim.get("name"), "samplers": samplers, "channels": channels})



# ---------------------------------------------------------------------------------------------
# Clips made from the rip's own ("made_clips"), and props mirrored to the other hand
# ("mirror_props"): the Battlefront mod's Ashelin (round 53). Everything runs on the rip at install,
# so the repository keeps recipes, never keys taken from a game.
# ---------------------------------------------------------------------------------------------

MADE_FPS = 30.0
MIRROR = np.diag([-1.0, 1.0, 1.0, 1.0])  # the model's left and right swap across x


def quat_to_mat(q) -> np.ndarray:
    """3 x 3 rotation of quaternion q (x y z w)."""
    x, y, z, w = q / np.linalg.norm(q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def mat_to_quat(r: np.ndarray) -> np.ndarray:
    """Quaternion (x y z w) of 3 x 3 rotation r (node_rest's conversion)."""
    m = np.eye(4)
    m[:3, :3] = r
    return np.array(node_rest({"matrix": list(m.T.reshape(-1))})["rotation"])


def axis_quat(axis, degrees: float) -> np.ndarray:
    a = np.array(axis, float)
    a /= np.linalg.norm(a)
    h = np.radians(degrees) / 2
    return np.array([*(a * np.sin(h)), np.cos(h)])


def slerp(a: np.ndarray, b: np.ndarray, u: float) -> np.ndarray:
    if np.dot(a, b) < 0:
        b = -b
    d = min(1.0, float(np.dot(a, b)))
    if d > 0.9995:
        q = a + (b - a) * u
    else:
        th = np.arccos(d)
        q = (np.sin((1 - u) * th) * a + np.sin(u * th) * b) / np.sin(th)
    return q / np.linalg.norm(q)


def trs_mat(t, r, s) -> np.ndarray:
    m = np.eye(4)
    m[:3, :3] = quat_to_mat(r) * np.array(s)
    m[:3, 3] = t
    return m


class Rig:
    """The rip's skeleton: its joints in order (each after its parent), their parents, rest TRS,
    bind matrices (model space) and inverses."""

    def __init__(self, src: Glb):
        nodes = src.json["nodes"]
        skin = src.json["skins"][0]
        self.names = [nodes[j]["name"] for j in skin["joints"]]
        self.node = dict(zip(self.names, skin["joints"]))
        parent_node = {c: i for i, n in enumerate(nodes) for c in n.get("children", [])}
        by_node = {j: n for n, j in self.node.items()}
        self.parent = {n: by_node.get(parent_node.get(self.node[n])) for n in self.names}
        self.rest = {n: node_rest(nodes[self.node[n]]) for n in self.names}
        ibm = src.accessor(skin["inverseBindMatrices"]).reshape(-1, 4, 4)
        self.ib = {n: ibm[k].T.astype(float) for k, n in enumerate(self.names)}
        self.b = {n: np.linalg.inv(m) for n, m in self.ib.items()}

    def partner(self, name: str) -> str:
        """The joint across from NAME (Lhand and Rhand, lburnA and rburnA), else NAME."""
        for a, b in (("L", "R"), ("R", "L"), ("l", "r"), ("r", "l")):
            if name.startswith(a) and b + name[1:] in self.node:
                return b + name[1:]
        return name


class Clip:
    """A clip at MADE_FPS: per joint, its local translation, rotation (x y z w) and scale a key."""

    def __init__(self, n: int, rig: Rig):
        self.n = n
        self.t = {j: np.tile(rig.rest[j]["translation"], (n, 1)).astype(float) for j in rig.names}
        self.r = {j: np.tile(rig.rest[j]["rotation"], (n, 1)).astype(float) for j in rig.names}
        self.s = {j: np.tile(rig.rest[j]["scale"], (n, 1)).astype(float) for j in rig.names}

    def copy(self, rig: Rig, keys=None) -> "Clip":
        keys = range(self.n) if keys is None else list(keys)
        out = Clip(len(keys), rig)
        for j in rig.names:
            out.t[j], out.r[j], out.s[j] = self.t[j][keys].copy(), self.r[j][keys].copy(), self.s[j][keys].copy()
        return out

    def local(self, j: str, k: int) -> np.ndarray:
        return trs_mat(self.t[j][k], self.r[j][k], self.s[j][k])

    def globals(self, rig: Rig, k: int) -> dict:
        g = {}
        for j in rig.names:
            p = rig.parent[j]
            g[j] = (g[p] if p else np.eye(4)) @ self.local(j, k)
        return g

    def set_local(self, j: str, k: int, m: np.ndarray, rotation_only: bool = False):
        scale = np.linalg.norm(m[:3, :3], axis=0)
        self.r[j][k] = mat_to_quat(m[:3, :3] / scale)
        if not rotation_only:
            self.t[j][k] = m[:3, 3]
            self.s[j][k] = scale


def rip_clip(src: Glb, rig: Rig, name: str, more: "Glb | None" = None) -> Clip:
    """Clip NAME of the rip, or else of MORE (the entry's "made_from" file: its channels by joint
    name), sampled at MADE_FPS (linear, rotations slerped). A joint the clip leaves out keeps its rest
    pose."""
    anim = next((a for a in src.json.get("animations", []) if a.get("name") == name), None)
    if anim is None and more is not None:
        src = more
        anim = next((a for a in src.json.get("animations", []) if a.get("name") == name), None)
    if anim is None:
        sys.exit(f"made_clips: no clip {name} in the rip" + (" nor in made_from" if more else ""))
    tracks, end = [], 0.0
    for c in anim["channels"]:
        joint = src.json["nodes"][c["target"]["node"]].get("name")
        joint = joint if joint in rig.node else None
        s = anim["samplers"][c["sampler"]]
        times = src.accessor(s["input"])[:, 0].astype(float)
        end = max(end, float(times[-1]))
        if joint:
            tracks.append((joint, c["target"]["path"], times, src.accessor(s["output"]).astype(float)))
    n = max(2, int(round(end * MADE_FPS)) + 1)
    clip = Clip(n, rig)
    for joint, path, times, vals in tracks:
        dest = {"translation": clip.t, "rotation": clip.r, "scale": clip.s}[path][joint]
        for k in range(n):
            tk = min(k / MADE_FPS, times[-1])
            i = int(np.searchsorted(times, tk, side="right")) - 1
            i = max(0, min(i, len(times) - 2)) if len(times) > 1 else 0
            if len(times) == 1:
                dest[k] = vals[0]
                continue
            u = float(np.clip((tk - times[i]) / max(times[i + 1] - times[i], 1e-9), 0.0, 1.0))
            dest[k] = slerp(vals[i], vals[i + 1], u) if path == "rotation" else vals[i] + (vals[i + 1] - vals[i]) * u
    return clip


def concat(rig: Rig, clips: list) -> Clip:
    out = Clip(sum(c.n for c in clips), rig)
    for j in rig.names:
        out.t[j] = np.concatenate([c.t[j] for c in clips])
        out.r[j] = np.concatenate([c.r[j] for c in clips])
        out.s[j] = np.concatenate([c.s[j] for c in clips])
    return out


def mirror_clip(rig: Rig, clip: Clip) -> Clip:
    """The clip played by the model's mirror image: each joint takes its partner's skinning matrix
    mirrored across x (S K S, K = global times inverse bind), whatever the joints' own axes."""
    out = clip.copy(rig)
    for k in range(clip.n):
        g = clip.globals(rig, k)
        new = {}
        for j in rig.names:
            p = rig.partner(j)
            new[j] = MIRROR @ g[p] @ rig.ib[p] @ MIRROR @ rig.b[j]
        for j in rig.names:
            par = rig.parent[j]
            out.set_local(j, k, (np.linalg.inv(new[par]) if par else np.eye(4)) @ new[j])
    return out


def mirror_limb(rig: Rig, clip: Clip, root: str):
    """The limb from joint ROOT down (Lshoulder: the left arm, its fingers) turned as the mirror of
    its partner's, its bones' lengths kept, in place."""
    limb = [j for j in rig.names if j == root or root in ancestors(rig, j)]
    for k in range(clip.n):
        g = clip.globals(rig, k)
        for j in limb:
            p = rig.partner(j)
            want = MIRROR @ g[p] @ rig.ib[p] @ MIRROR @ rig.b[j]
            par = g[rig.parent[j]]
            rot = (par[:3, :3] / np.linalg.norm(par[:3, :3], axis=0)).T @ (want[:3, :3] / np.linalg.norm(want[:3, :3], axis=0))
            clip.r[j][k] = mat_to_quat(rot)
            g[j] = par @ clip.local(j, k)


def ancestors(rig: Rig, j: str) -> list:
    out = []
    while rig.parent[j]:
        j = rig.parent[j]
        out.append(j)
    return out


def turn_joint(rig: Rig, clip: Clip, joint: str, axis, degrees, keys=None):
    """Joint JOINT (and what hangs on it) turned about its own origin by DEGREES about AXIS, in the
    model's space; DEGREES a number, or one a key (a ramp)."""
    for k in (range(clip.n) if keys is None else keys):
        deg = degrees[k] if hasattr(degrees, "__len__") else degrees
        par = rig.parent[joint]
        pr = clip.globals(rig, k)[par][:3, :3] if par else np.eye(3)
        pr = pr / np.linalg.norm(pr, axis=0)
        q = quat_to_mat(axis_quat(axis, deg))
        clip.r[joint][k] = mat_to_quat(pr.T @ q @ pr @ quat_to_mat(clip.r[joint][k]))


def attach(rig: Rig, clip: Clip, joint: str, holder: str, grip: np.ndarray):
    """Joint JOINT held by HOLDER every key: its skinning matrix HOLDER's times GRIP."""
    for k in range(clip.n):
        g = clip.globals(rig, k)
        want = g[holder] @ rig.ib[holder] @ grip @ rig.b[joint]
        par = rig.parent[joint]
        clip.set_local(joint, k, (np.linalg.inv(g[par]) if par else np.eye(4)) @ want)


def grip_of(rig: Rig, clip: Clip, joint: str, holder: str, key: int = 0) -> np.ndarray:
    """JOINT's skinning matrix relative to HOLDER's at KEY of CLIP (a prop's hold in a hand)."""
    g = clip.globals(rig, key)
    return np.linalg.inv(g[holder] @ rig.ib[holder]) @ (g[joint] @ rig.ib[joint])


def make_clip(src: Glb, rig: Rig, recipe: dict, made: dict, more: "Glb | None" = None) -> Clip:
    """One recipe of "made_clips" (see the manifest's docstring); MORE the "made_from" file."""
    if "from" in recipe:
        clip = rip_clip(src, rig, recipe["from"], more)
    elif "concat" in recipe:
        clip = concat(rig, [made[n].copy(rig) if n in made else rip_clip(src, rig, n, more) for n in recipe["concat"]])
    elif "like" in recipe:
        clip = made[recipe["like"]].copy(rig)
    else:
        sys.exit(f"made_clips {recipe.get('name')}: no from, concat or like")
    if "keys" in recipe:
        a, b = recipe["keys"]
        clip = clip.copy(rig, range(a, min(b, clip.n)))
    if "hold" in recipe:
        key, count = recipe["hold"]
        clip = clip.copy(rig, [min(key, clip.n - 1)] * count)
    if recipe.get("flat_root"):
        j = recipe.get("root", "main")
        clip.t[j][:, 0] = rig.rest[j]["translation"][0]
        clip.t[j][:, 2] = rig.rest[j]["translation"][2]
    for pose in recipe.get("pose_from", []):
        # joints held all along at their local rotation in a key of another clip (fingers on a grip)
        held = rip_clip(src, rig, pose["clip"], more)
        key = min(pose.get("key", 0), held.n - 1)
        for j in pose["joints"]:
            clip.r[j][:] = held.r[j][key]
    if recipe.get("mirror"):
        clip = mirror_clip(rig, clip)
    for limb in recipe.get("mirror_limbs", []):
        mirror_limb(rig, clip, limb)
    for turn in recipe.get("turns", []):
        deg = turn["deg"]
        if "to" in turn:
            u = np.linspace(0.0, 1.0, clip.n)
            deg = deg + (turn["to"] - deg) * (u * u * (3 - 2 * u) if turn.get("smooth") else u)
        turn_joint(rig, clip, turn["joint"], turn["axis"], deg)
    if "lift" in recipe:
        j = recipe.get("root", "main")
        u = np.linspace(0.0, 1.0, clip.n)
        clip.t[j][:, 1] += recipe["lift"] * np.sin(np.pi * u)
    return clip


def add_made_clips(out: Writer, src: Glb, node_map: dict[int, int], entry: dict, more: "Glb | None" = None):
    """Every recipe of entry["made_clips"], in order, as clips of `out` after its others, drawing on
    the rip's clips and on MORE's (entry["made_from"]); with entry["attach"], each made clip keeps
    that prop in that hand."""
    rig = Rig(src)
    made = {}
    hold = entry.get("attach")
    grip = None
    if hold:
        grip = grip_of(rig, rip_clip(src, rig, hold["clip"]), hold["joint"], hold["holder"], hold.get("key", 0))
    for recipe in entry["made_clips"]:
        clip = make_clip(src, rig, recipe, made, more)
        if hold and not recipe.get("free"):
            attach(rig, clip, hold["joint"], hold["holder"], grip)
        made[recipe["name"]] = clip
        if recipe.get("temp"):
            continue
        times = np.arange(clip.n, dtype=np.float32).reshape(-1, 1) / MADE_FPS
        tacc = out.accessor(times, "SCALAR", 5126, minmax=True)
        samplers, channels = [], []
        for j in rig.names:
            for path, vals, kind in (("translation", clip.t[j], "VEC3"), ("rotation", clip.r[j], "VEC4"),
                                     ("scale", clip.s[j], "VEC3")):
                samplers.append({"input": tacc, "output": out.accessor(vals.astype(np.float32), kind, 5126),
                                 "interpolation": "LINEAR"})
                channels.append({"sampler": len(samplers) - 1,
                                 "target": {"node": node_map[rig.node[j]], "path": path}})
        out.json["animations"].append({"name": recipe["name"], "samplers": samplers, "channels": channels})


def add_mirror_prop(out: Writer, src: Glb, mesh_node: int, prop: dict):
    """A copy of the rip's primitives prop["prims"] (a prop on joint prop["joint"], held by
    prop["holder"] in the rip's clip prop["clip"]) in the other hand, prop["to"]: each vertex mirrored
    across x through the hold (`grip_of`), bound to prop["to"] alone, its triangles turned back."""
    rig = Rig(src)
    grip = grip_of(rig, rip_clip(src, rig, prop["clip"]), prop["joint"], prop["holder"], prop.get("key", 0))
    place = MIRROR @ grip
    joints = [out.json["nodes"][j].get("name") for j in out.json["skins"][0]["joints"]]
    to = joints.index(prop["to"])
    mesh = out.json["meshes"][out.json["nodes"][mesh_node]["mesh"]]
    names = [m.get("name") for m in out.json["materials"]]
    for index in prop["prims"]:
        prim = src.json["meshes"][0]["primitives"][index]
        idx = src.accessor(prim["indices"])[:, 0].astype(np.int64)
        used, inv = np.unique(idx, return_inverse=True)
        attrs = {}
        for name, acc in prim["attributes"].items():
            info = src.json["accessors"][acc]
            vals = src.accessor(acc)[used].astype(float)
            if name == "POSITION":
                vals = (place @ np.c_[vals, np.ones(len(vals))].T).T[:, :3]
            elif name == "NORMAL":
                vals = (place[:3, :3] @ vals.T).T
                vals /= np.linalg.norm(vals, axis=1, keepdims=True) + 1e-12
            elif name == "JOINTS_0":
                vals = np.tile([to, 0, 0, 0], (len(vals), 1))
            elif name == "WEIGHTS_0":
                vals = np.tile([1.0, 0.0, 0.0, 0.0], (len(vals), 1))
            attrs[name] = out.accessor(vals.astype(COMPONENT[info["componentType"]]), info["type"],
                                       info["componentType"], 34962, name == "POSITION")
        tris = inv.reshape(-1, 3)[:, [0, 2, 1]].reshape(-1, 1).astype(np.uint32)
        material = src.json["materials"][prim["material"]].get("name")
        if material not in names:
            sys.exit(f"mirror_props: no material {material} in the model")
        mesh["primitives"].append({"attributes": attrs, "indices": out.accessor(tris, "SCALAR", 5125, 34963),
                                   "mode": prim.get("mode", 4), "material": names.index(material)})


def read_jsonc(path: Path) -> dict:
    """A JSON file with // comments (outside strings)."""
    text = path.read_text("utf8")
    text = re.sub(r'("(?:\\.|[^"\\])*")|//[^\n]*', lambda m: m.group(1) or "", text)
    return json.loads(text)


class Context:
    """Where the tool reads and writes: the root (the repository, or a mod release's data/), the
    games' discs, and the extractor to rip with."""

    def __init__(self, root: Path, isos: dict, extractor):
        self.root = root
        self.isos = isos
        self.extractor = extractor

    def iso(self, game: str) -> Path:
        return Path(self.isos[game]) if game in self.isos else self.root / "iso_data" / game

    def rip_path(self, ref: str) -> Path:
        game, folder, file = ref.split("/", 2)
        return self.root / "decompiler_out" / game / "levels" / folder / file

    def texture_path(self, ref: str) -> Path:
        """A texture the extraction wrote: <game>/<tpage>/<texture>.png."""
        game, tpage, file = ref.split("/", 2)
        return self.root / "decompiler_out" / game / "textures" / tpage / file

    def extract(self, game: str, dgos: list):
        """Rip these DGOs of game: the extractor on its disc (at an install), else the decompiler."""
        overrides = json.dumps({"decompile_code": False, "levels_extract": True, "allowed_objects": [],
                                "rip_levels": True, "levels_to_extract": dgos, "save_texture_pngs": True})
        if self.extractor:
            cmd = [self.extractor, str(self.iso(game)), "--folder", "--decompile", "--game", game,
                   "--proj-path", str(self.root), "--decomp-config-override", overrides]
        else:
            decompiler = self.root / "out" / "build" / "Release" / "bin" / f"decompiler{EXE}"
            if not decompiler.exists():
                sys.exit(f"no {decompiler}: build it with task build-release-decomp")
            cmd = [str(decompiler), f"./decompiler/config/{game}/{game}_config.jsonc", "./iso_data",
                   "./decompiler_out", "--version", VERSION, "--config-override", overrides]
        print("  running: " + " ".join(cmd), flush=True)
        # OG_MOD_MODELS: the extractor skips its own run of this tool in this extraction
        subprocess.run(cmd, check=True, cwd=self.root, env={**os.environ, "OG_MOD_MODELS": "1"})


def needed_rips(manifest: dict) -> set:
    refs = set()
    for entry in manifest.get("models", {}).values():
        for key in ("mesh", "skeleton", "textures_from"):
            if key in entry:
                refs.add(entry[key])
        for extra in entry.get("extra", []):
            refs.add(extra["mesh"])
    return refs


def needed_textures(manifest: dict) -> set:
    return {ref for entry in manifest.get("models", {}).values()
            for ref in entry.get("texture_files", {}).values()}


def make_rips(ctx: Context, manifest: dict):
    """Extract the rips and textures that are missing, a game at a time, only their DGOs."""
    missing = sorted(r for r in needed_rips(manifest) if not ctx.rip_path(r).exists())
    missing += sorted(r for r in needed_textures(manifest) if not ctx.texture_path(r).exists())
    by_game = {}
    for ref in missing:
        game, folder, _ = ref.split("/", 2)
        dgo = manifest.get("rips", {}).get(f"{game}/{folder}")
        if not dgo:
            sys.exit(f"{ref}: its folder {game}/{folder} has no DGO in the manifest's rips")
        by_game.setdefault(game, set()).add(dgo)
    for game, dgos in sorted(by_game.items()):
        print(f"  {game}: ripping {', '.join(sorted(dgos))}", flush=True)
        ctx.extract(game, sorted(dgos))
    still = [r for r in missing if not (ctx.texture_path(r) if r.endswith(".png") else ctx.rip_path(r)).exists()]
    if still:
        sys.exit("the extraction did not write: " + ", ".join(still))


def build_model(ctx: Context, name: str, entry: dict) -> "Writer":
    """One model of the manifest (see the docstring at the top)."""
    cache = {}

    def rip(ref: str) -> Glb:
        if ref not in cache:
            cache[ref] = Glb(ctx.rip_path(ref))
        return cache[ref]

    mesh = rip(entry["mesh"])
    textures = None
    if "textures_from" in entry:
        src = rip(entry["textures_from"])
        prefix = entry.get("texture_prefix", "")
        textures = {img.get("name"): image_bytes(src, img) for img in src.json["images"]
                    if img.get("name", "").startswith(prefix)}
    for image, ref in entry.get("texture_files", {}).items():
        textures = textures or {}
        textures[image] = (ctx.texture_path(ref).read_bytes(), "image/png")
    out = Writer()
    anim_src, remap = mesh, None
    if "skeleton" in entry:
        anim_src = rip(entry["skeleton"])
        names_m, names_s = mesh.joint_names(), anim_src.joint_names()
        missing = [n for n in names_m if n not in names_s]
        if missing:
            sys.exit(f"{name}: joints of the mesh missing from the skeleton: {missing}")
        remap = np.array([names_s.index(n) for n in names_m], dtype=np.int64)
        ibm_m = mesh.accessor(mesh.json["skins"][0]["inverseBindMatrices"])
        ibm_s = anim_src.accessor(anim_src.json["skins"][0]["inverseBindMatrices"])
        worst = float(np.abs(ibm_m - ibm_s[remap]).max())
        if worst > 1e-3:
            sys.exit(f"{name}: the bind poses of the mesh and the skeleton differ (max {worst})")
    mesh_node, node_map = copy_skeleton(out, anim_src)
    copy_mesh(out, mesh, mesh_node, entry.get("prims"), remap, textures, entry.get("recolor"), name)
    for extra in entry.get("extra", []):
        src = rip(extra["mesh"])
        names_e, names_s = src.joint_names(), anim_src.joint_names()
        missing = [n for n in names_e if n not in names_s]
        if missing:
            sys.exit(f"{name}: joints of {extra['mesh']} missing from the skeleton: {missing}")
        extra_remap = np.array([names_s.index(n) for n in names_e], dtype=np.int64)
        ibm_e = src.accessor(src.json["skins"][0]["inverseBindMatrices"])
        ibm_s = anim_src.accessor(anim_src.json["skins"][0]["inverseBindMatrices"])
        worst = float(np.abs(ibm_e - ibm_s[extra_remap]).max())
        if worst > 1e-3:
            sys.exit(f"{name}: the bind poses of {extra['mesh']} and the skeleton differ (max {worst})")
        copy_mesh(out, src, mesh_node, extra.get("prims"), extra_remap, None, None, name,
                  append=True, image_suffix=extra.get("suffix", "extra"))
    for blade in entry.get("blades", []):
        add_blade(out, mesh_node, blade)
    for prop in entry.get("mirror_props", []):
        add_mirror_prop(out, anim_src, mesh_node, prop)
    copy_animations(out, anim_src, node_map, entry.get("padding", 0), entry.get("clips"),
                    entry.get("clip_prefix", ""))
    if "rip_clips" in entry:
        del out.json["animations"][entry["rip_clips"]:]
    if "clip_file" in entry:
        add_clip_file(out, Glb(ctx.root / entry["clip_file"]), anim_src, node_map)
    if "made_clips" in entry:
        more = Glb(ctx.root / entry["made_from"]) if "made_from" in entry else None
        add_made_clips(out, anim_src, node_map, entry, more)
    out.json["meshes"][0]["name"] = f"{name}-lod0"
    return out


def write_if_changed(path: Path, data: bytes) -> bool:
    if path.exists() and path.read_bytes() == data:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return True


def model_paths(game: str, name: str, entry: dict) -> list:
    """Where a model is written: for build-actor, and for its level's extraction."""
    base = Path("custom_assets") / game / "models"
    paths = [base / "custom_levels" / f"{name}.glb"]
    if entry.get("level"):
        paths.append(base / entry["level"] / f"{name}-lod0.glb")
    return paths


def run_game(ctx: Context, game: str, check: bool) -> int:
    manifest = read_jsonc(ctx.root / "custom_assets" / game / "models" / "models.jsonc")
    if check:
        wanted = [p for n, e in manifest.get("models", {}).items() for p in model_paths(game, n, e)]
        wanted += [Path(p) for p in manifest.get("files", {})]
        bad = [str(p) for p in wanted if not (ctx.root / p).exists()]
        print(f"  {'missing: ' + ', '.join(bad) if bad else 'everything is there'}")
        return 1 if bad else 0
    make_rips(ctx, manifest)
    for name, entry in manifest.get("models", {}).items():
        model = build_model(ctx, name, entry)
        data = model.save_bytes()
        changed = False
        for path in model_paths(game, name, entry):
            changed |= write_if_changed(ctx.root / path, data)
        print(f"  {name}: {len(model.json['meshes'][0]['primitives'])} primitives, "
              f"{len(model.json.get('animations', []))} clips" + ("" if changed else " (unchanged)"))
    for dest, ref in manifest.get("files", {}).items():
        src_game, rel = ref.split("/", 1)
        src = ctx.iso(src_game) / rel
        if not src.exists():
            sys.exit(f"{dest}: no {src} (the disc of {src_game})")
        changed = write_if_changed(ctx.root / dest, src.read_bytes())
        print(f"  {dest}: from {ref}" + ("" if changed else " (unchanged)"))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--game", help="one game's manifest (default: every game's)")
    parser.add_argument("--check", action="store_true", help="only list the missing outputs")
    parser.add_argument("--root", help="the repository root (default), or a mod release's data/")
    parser.add_argument("--iso", action="append", default=[], metavar="GAME=PATH",
                        help="a game's extracted disc (default: iso_data/<game>), repeatable")
    parser.add_argument("--extractor", help="rip with this OpenGOAL extractor (a mod release's) "
                                            "instead of the decompiler of out/build/Release/bin")
    args = parser.parse_args()
    # the one-file executable has no repository around it: --root is then required
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[2]
    isos = {}
    for item in args.iso:
        game, sep, path = item.partition("=")
        if not sep:
            parser.error(f"--iso {item}: expected GAME=PATH")
        isos[game] = str(Path(path).resolve())
    ctx = Context(root, isos, str(Path(args.extractor).resolve()) if args.extractor else None)
    games = [args.game] if args.game else sorted(
        p.parent.parent.name for p in (root / "custom_assets").glob("*/models/models.jsonc"))
    if not games:
        print("no custom_assets/<game>/models/models.jsonc")
        return 0
    code = 0
    for game in games:
        print(f"{game}:", flush=True)
        code |= run_game(ctx, game, args.check)
    return code


if __name__ == "__main__":
    sys.exit(main())
