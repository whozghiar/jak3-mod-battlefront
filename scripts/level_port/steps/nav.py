"""Traffic navigation data: the source levels' city-level-infos and nav meshes for one level
(<level>-nav.json, read by the level builder as the level .jsonc's "nav_data"): a level holding one
district gets that district's as they are, a level holding several gets them merged.

Jak 2 gives each district of its city its own city-level-info (the traffic: a grid of cells holding
the nav segments, and a nav graph of nodes and branches, linked to the neighbor districts' graphs)
and its own nav meshes (where citizens and guards walk). The traffic engine (Jak 2's and Jak 3's,
the same) links the city-level-infos of at most 2 displayed levels, its 2 districts, and only
spawns objects in their active cells: a district level keeps its own data, as it is (links to its
neighbors' graphs included, resolved by graph id when both are linked), so the traffic only lives
where the city is displayed. A level merging several districts (one bsp, one city-level-info) gets
them merged into one, over one grid covering them all, with one nav graph (the links between
districts become plain branches). The nav meshes are kept as they are (their ids too, which
the nav graph uses). Jak 2 and Jak 3 share these layouts (city-level-info, vis-cell, nav-segment,
nav-graph, nav-node, nav-branch, nav-graph-link, nav-mesh).

The traffic engine keeps a citizen or a vehicle alive only while it is in an active cell, and a
cell is active by the camera's distance to its sphere (and the view frustum), at most 255 at once.
Like Jak 2's, every cell has a sphere around the whole cell, empty or not: an object entering a
cell that is never active disappears in front of the player (and one appears again where its
segments are). Jak 2's districts have 25m, 40m or 50m cells; the merged grid has 50m cells (every
25m or 50m cell falls in one of them), and each segment goes in the cell that holds its middle.

It can also copy the source game's traffic height map (how high the vehicles fly) into the level's
code, in place of the target game's, which follows its own city.

Manifest, on the level:
  "nav": {
    "cell": 50.0,              meters, the merged grid's cells (the districts' grids are aligned on
                               multiples of their cell size)
    "outside_depth": 10000.0,  meters under the level of the spheres of cells no district covers
    "height_map": {"source": the source game's traffic-height-map.gc},
    "clock": [clock-type, clock-mask] every merged lane gets (optional: the source's; Jak 3's
             Spargus lanes are territory 128, which Haven City's faction manager sends to sleep),
    "sources": [the source levels whose navigation it holds, else the level's own; none: only the
                height map (a city's hub: its districts hold their own)],
    "links": [{"a": [source level, nav mesh index, poly, edge], "b": [the same]}, ...] (optional,
              a merged level only): a walkable strip across the gap between poly a's free edge
              (from its vertex `edge` to the next) and poly b's, cut in three, and a nav-mesh-link
              between the two meshes, the way Jak 3 links its own (link_meshes)
  }
A level whose sources have nav meshes but no traffic data (a place outside the city) gets their
nav meshes alone, as they are (write_meshes): where the mod's actors walk.
Inputs: decompiler_out/<game>/entities/<level>-city.json and <level>-nav.json of the level's
sources (see decompiler/level_extractor/extract_nav.h).
"""

import json
import math
import os
import re
import struct

from ..common import data_blob
from ..common.data_blob import patch
from ..common.files import write_if_changed

# a branch's destination above this is ~(link index)
LINK_BASE = 100000
NO_CELL = 0xffff


def decode_city(blob):
    """The city-level-info of a blob: grid, cells, segments and nav graph, as dicts. In the file,
    the cells' segments, the segments' branches, the nodes' branches and the branches' nodes are
    indices (the traffic engine turns them into pointers when a level is linked, see
    traffic-engine level-link)."""
    base = blob.roots["city-level-info"]
    grid = {
        "axis_scale": [blob.f32(base + 4 * i) for i in range(3)],
        "dims": [blob.s8(base + 12 + i) for i in range(3)],
        "box_min": [blob.f32(base + 16 + 4 * i) for i in range(4)],
        "box_max": [blob.f32(base + 32 + 4 * i) for i in range(4)],
        "cell_size": [blob.f32(base + 48 + 4 * i) for i in range(4)],
    }
    cell_array = blob.ptr(base + 64)
    segment_count = blob.s16(base + 68)
    cell_count = blob.u16(base + 70)
    segment_array = blob.ptr(base + 72)
    graph = blob.ptr(base + 76)
    camera_ceiling = blob.f32(base + 80)
    cells = []
    for i in range(cell_count):
        c = cell_array + 32 * i
        cells.append({
            "sphere": [blob.f32(c + 4 * k) for k in range(4)],
            "segment_start": blob.u32(c + 16),
            "vis_id": blob.u16(c + 20),
            "id": blob.u16(c + 22),
            "incoming": blob.s8(c + 24),
            "segment_count": blob.s8(c + 25),
            "flags": blob.u8(c + 26),
            "pad": blob.u32(c + 28),
        })
    segments = []
    for i in range(segment_count):
        s = segment_array + 48 * i
        segments.append({
            "raw": blob.raw(s, 48),
            "v0": [blob.f32(s + 4 * k) for k in range(4)],
            "v1": [blob.f32(s + 16 + 4 * k) for k in range(4)],
            "branch": blob.u32(s + 32),
            "nav_mesh_id": blob.u32(s + 36),
            "id": blob.u16(s + 40),
            "cell_id": blob.u16(s + 42),
            "from_cell_id": blob.u16(s + 44),
            "tracker_id": blob.s8(s + 46),
        })
    # nav-graph (a basic: fields from its type tag, 4 bytes before the pointer)
    g = graph - 4
    node_count = blob.s16(g + 4)
    branch_count = blob.s16(g + 6)
    node_array = blob.ptr(g + 8)
    branch_array = blob.ptr(g + 12)
    link_count = blob.s16(g + 16)
    link_array = blob.ptr(g + 20)
    nodes = []
    for i in range(node_count):
        n = node_array + 32 * i
        nodes.append({
            "raw": blob.raw(n, 32),
            "pos": [blob.f32(n + 4 * k) for k in range(3)],
            "id": blob.u16(n + 14),
            "branch_count": blob.s8(n + 17),
            "branch_start": blob.u32(n + 20),
            "nav_mesh_id": blob.u32(n + 24),
            "level": blob.symbols.get((n + 28) // 4),
        })
    branches = []
    for i in range(branch_count):
        b = branch_array + 16 * i
        branches.append({
            "raw": blob.raw(b, 16),
            "src": blob.u32(b),
            "dest": blob.u32(b + 4),
        })
    links = []
    for i in range(link_count):
        k = link_array + 48 * i
        links.append({
            "id": blob.u32(k),
            "dest_graph_id": blob.u32(k + 4),
            "src_branch_id": blob.u16(k + 8),
            "dest_node_id": blob.u16(k + 10),
        })
    return {
        "grid": grid, "cells": cells, "segments": segments, "camera_ceiling": camera_ceiling,
        "graph": {"id": blob.u32(g + 32), "first_node": blob.s16(g + 24), "nodes": nodes,
                  "branches": branches, "links": links},
    }


def merge(districts, mesh_aids, cell_size, outside_depth):
    """One city (grid, cells, segments, nodes, branches) from the districts' decoded ones.
    mesh_aids: the aids of the nav meshes the level has. cell_size and outside_depth in game
    units."""
    CELL = cell_size
    lo = [min(c["grid"]["box_min"][i] for c in districts.values()) for i in range(3)]
    hi = [max(c["grid"]["box_max"][i] for c in districts.values()) for i in range(3)]
    lo[0] = math.floor(lo[0] / CELL) * CELL
    lo[2] = math.floor(lo[2] / CELL) * CELL
    dims = [math.ceil((hi[0] - lo[0]) / CELL), 1, math.ceil((hi[2] - lo[2]) / CELL)]
    assert max(dims) < 128, dims
    height = hi[1] - lo[1]

    def global_cell(x, z):
        ix = max(0, min(int((x - lo[0]) / CELL), dims[0] - 1))
        iz = max(0, min(int((z - lo[2]) / CELL), dims[2] - 1))
        return ix + iz * dims[0]

    graph_ids = {c["graph"]["id"]: name for name, c in districts.items()}
    node_base, branch_base = {}, {}
    n_nodes = n_branches = 0
    for name, c in districts.items():
        node_base[name] = n_nodes
        branch_base[name] = n_branches
        n_nodes += len(c["graph"]["nodes"])
        n_branches += len(c["graph"]["branches"])

    nodes, branches, placed = [], [], []
    for name, c in districts.items():
        for s in c["segments"]:
            branch = s["branch"] + branch_base[name]
            raw = patch(s["raw"], 32, "<I", branch)
            # a pedestrian segment on a nav mesh no level has (Jak 2's ctygenc has some): nav mesh
            # 0, which the traffic engine never spawns citizens on (a spawn needs its nav mesh)
            if s["tracker_id"] == 1 and s["nav_mesh_id"] not in mesh_aids:
                raw = patch(raw, 36, "<I", 0)
            v0 = struct.unpack_from("<3f", raw, 0)
            v1 = struct.unpack_from("<3f", raw, 16)
            cell = global_cell((v0[0] + v1[0]) / 2, (v0[2] + v1[2]) / 2)
            placed.append((branch, v0, v1, cell, s["from_cell_id"] != NO_CELL, raw))
        for n in c["graph"]["nodes"]:
            raw = patch(n["raw"], 14, "<H", len(nodes))
            raw = patch(raw, 20, "<I", n["branch_start"] + branch_base[name])
            nodes.append(raw)
        links = c["graph"]["links"]
        for b in c["graph"]["branches"]:
            src = b["src"] + node_base[name]
            if b["dest"] > LINK_BASE:
                link = links[0xffffffff - b["dest"]]
                dest_name = graph_ids[link["dest_graph_id"]]
                dest_ids = {n["id"]: node_base[dest_name] + i
                            for i, n in enumerate(districts[dest_name]["graph"]["nodes"])}
                dest = dest_ids[link["dest_node_id"]]
            else:
                dest = b["dest"] + node_base[name]
            raw = patch(b["raw"], 0, "<I", src)
            raw = patch(raw, 4, "<I", dest)
            branches.append(raw)

    # from-cell-id: the cell of the segment before it on its branch (Jak 2 splits a branch into one
    # segment per cell it crosses; the one before ends where it starts), none (#xffff) on the first.
    # The engine spawns objects at the edge of the active cells, on the segments coming from an
    # inactive cell.
    cell_before = {(branch, v1): cell for branch, _, v1, cell, _, _ in placed}
    cell_segments = {}
    for branch, v0, _, cell, follows, raw in placed:
        before = cell_before.get((branch, v0), NO_CELL) if follows else NO_CELL
        assert not follows or before != NO_CELL, "a segment without the one before it"
        raw = patch(raw, 42, "<H", cell)
        raw = patch(raw, 44, "<H", before)
        cell_segments.setdefault(cell, []).append(raw)

    # cells: their segments in a row, the ones coming from another cell first. A cell's sphere
    # (what the engine activates it by), like Jak 2's: the whole cell, from the bottom to the top of
    # the districts over it; far under the city for the cells no district covers.
    boxes = [(c["grid"]["box_min"], c["grid"]["box_max"]) for c in districts.values()]
    cells, segments = [], []
    for i in range(dims[0] * dims[2]):
        segs = cell_segments.get(i, [])
        incoming = [s for s in segs if struct.unpack_from("<H", s, 44)[0] not in (NO_CELL, i)]
        own = [s for s in segs if struct.unpack_from("<H", s, 44)[0] in (NO_CELL, i)]
        assert len(segs) < 128, f"cell {i}: {len(segs)} segments"
        start = len(segments)
        for s in incoming + own:
            segments.append(patch(s, 40, "<H", len(segments)))
        ix, iz = i % dims[0], i // dims[0]
        x0, z0 = lo[0] + ix * CELL, lo[2] + iz * CELL
        heights = [(b_lo[1], b_hi[1]) for b_lo, b_hi in boxes
                   if b_lo[0] < x0 + CELL and b_hi[0] > x0 and b_lo[2] < z0 + CELL and b_hi[2] > z0]
        center = [x0 + CELL / 2, lo[1] - outside_depth, z0 + CELL / 2]
        radius = 0.0
        if heights:
            y_lo, y_hi = min(h[0] for h in heights), max(h[1] for h in heights)
            center[1] = (y_lo + y_hi) / 2
            radius = math.sqrt(2 * (CELL / 2) ** 2 + ((y_hi - y_lo) / 2) ** 2)
        assert radius > 0 or not segs, f"cell {i}: segments out of every district"
        cells.append(struct.pack("<4fIHHbbBBI", *center, radius, start, 0, i, len(incoming),
                                 len(segs), 0, 0, 0))
    assert len(segments) < 32768
    grid = {"lo": lo, "hi": hi, "dims": dims, "height": height, "cell": CELL}
    return grid, cells, segments, nodes, branches


def write_city(w, grid, cells, segments, nodes, branches, camera_ceiling, level_name):
    """The merged city-level-info at the start of the writer's blob."""
    lo, hi, dims, height, CELL = grid["lo"], grid["hi"], grid["dims"], grid["height"], grid["cell"]
    info = w.bytes(bytes(144))
    w.blob.roots["city-level-info"] = info
    header = struct.pack("<3f3bB", 1.0 / CELL, 1.0 / height, 1.0 / CELL, dims[0], dims[1], dims[2],
                         0)
    header += struct.pack("<4f4f4f", lo[0], lo[1], lo[2], 1.0, hi[0], hi[1], hi[2], 1.0,
                          CELL, height, CELL, 1.0)
    header += struct.pack("<IhHIIf", 0, len(segments), len(cells), 0, 0, camera_ceiling)
    w.blob.words[info // 4: info // 4 + len(header) // 4] = list(
        struct.unpack("<%dI" % (len(header) // 4), header))
    w.align()
    cell_array = w.bytes(b"".join(cells))
    w.align()
    segment_array = w.bytes(b"".join(segments))
    # nav-graph, a basic: its type tag at a 16-byte boundary
    w.align()
    tag = w.pos()
    w.bytes(bytes(64))
    w.blob.types[tag // 4] = "nav-graph"
    graph = tag + 4
    struct_words = struct.pack("<hhIIhHIhHII", len(nodes), len(branches), 0, 0, 0, 0, 0, 0, 0, 0,
                               1000)
    w.blob.words[(tag + 4) // 4: (tag + 4) // 4 + len(struct_words) // 4] = list(
        struct.unpack("<%dI" % (len(struct_words) // 4), struct_words))
    w.blob.symbols[(tag + 28) // 4] = "#f"  # patched
    w.align()
    node_array = w.bytes(b"".join(nodes))
    for i in range(len(nodes)):
        w.blob.symbols[(node_array + 32 * i + 28) // 4] = level_name
    w.align()
    branch_array = w.bytes(b"".join(branches))
    w.pointer(info + 64, cell_array)
    w.pointer(info + 72, segment_array)
    w.pointer(info + 76, graph)
    w.pointer(tag + 8, node_array)
    w.pointer(tag + 12, branch_array)


def height_map_path(port, level):
    return f"{port.code_dir}/{level.name}-height-map.gc"


def write_height_map(port, level, source):
    """The source game's *traffic-height-map* as a target game source file (same xz-height-map
    layout), its heights one grid row per line. Returns the grid's dimensions."""
    text = open(source).read()
    start = text.index("(define *traffic-height-map*")
    data = text.index(":data (new 'static 'array int8", start)
    header = text[start:text.index("\n", data)]
    dims = [int(v.replace("#x", "0x"), 0)
            for v in re.search(r":dim \(new 'static 'array int16 2 (\S+) (\S+)\)", header).groups()]
    count = int(re.search(r"array int8 (\d+)", header[data - start:]).group(1))
    values = re.findall(r"-?\d+", text[text.index("\n", data): text.rindex(")", 0,
                                                                          text.rindex(")"))])
    assert count == dims[0] * dims[1] == len(values), (count, dims, len(values))
    indent = " " * 33
    rows = [indent + " ".join(values[i: i + dims[0]]) for i in range(0, count, dims[0])]
    name = f"{level.name}-height-map"
    out = [
        ";;-*-Lisp-*-",
        "(in-package goal)",
        "",
        f";; name: {name}.gc",
        f";; name in dgo: {name}",
        f";; dgos: {level.dgo}",
        "",
        *port.generated_lines(),
        f";; {port.source.TITLE}'s traffic height map ({source}): the height the",
        f";; vehicles fly at. {level.name}'s DGO has it in place of {port.target.TITLE}'s.",
        "",
        header,
        *rows,
        "                                 )",
        "                               )",
        "        )",
        "",
    ]
    write_if_changed(height_map_path(port, level), "\n".join(out))
    return dims


def nav_path(level):
    return f"{level.folder}/{level.name}-nav.json"


def city_sources(port, level):
    """The source levels of a level's "nav" that have traffic data (a city-level-info)."""
    return [src for src in nav_sources(port, level)
            if os.path.exists(os.path.join(port.source.ENTITIES, src + "-city.json"))]


def nav_sources(port, level):
    """The source levels of a level's "nav" that have navigation data: a city-level-info or nav
    meshes (empty: no nav_data)."""
    if "nav" not in level:
        return []
    return [src for src in sorted(level["nav"].get("sources", level.sources))
            if any(os.path.exists(os.path.join(port.source.ENTITIES, f"{src}-{kind}.json"))
                   for kind in ("city", "nav"))]


def write_district(port, level, src):
    """One source level's city-level-info and nav meshes, as they are: its own grid, cells and nav
    graph, with its links to its neighbors' graphs. Its node levels (the level it was loaded in, a
    symbol) become ours: when a level is unloaded, the traffic engine stops the vehicles heading to
    a node of that level by its name (deactivate-all-from-level). Its pedestrian segments on a nav
    mesh it doesn't have go to nav mesh 0, which no citizen spawns on."""
    entities = port.source.ENTITIES
    city = data_blob.Blob(os.path.join(entities, src + "-city.json"))
    nav_file = os.path.join(entities, src + "-nav.json")
    meshes = data_blob.Blob(nav_file) if os.path.exists(nav_file) else None
    mesh_aids = {meshes.u32(byte + 44) for byte in meshes.roots.values()} if meshes else set()
    for w, name in city.symbols.items():
        if name == src:
            city.symbols[w] = level.name
    base = city.roots["city-level-info"]
    segment_count = city.s16(base + 68)
    segment_array = city.ptr(base + 72)
    moved = 0
    for i in range(segment_count):
        seg = segment_array + 48 * i
        if city.s8(seg + 46) == 1 and city.u32(seg + 36) not in mesh_aids | {0}:
            city.words[(seg + 36) // 4] = 0
            moved += 1
    w = data_blob.Writer()
    offset = w.append_blob(city)
    w.blob.roots["city-level-info"] = base + offset
    if meshes:
        offset = w.append_blob(meshes)
        for root, byte in meshes.roots.items():
            w.blob.roots[f"nav-mesh-{src}-{root}"] = byte + offset
    write_if_changed(nav_path(level), json.dumps(w.blob.to_json(), separators=(",", ":")))
    info = decode_city(city)
    print(f"  {level.name}: {src}'s navigation as it is: grid {info['grid']['dims']}, "
          f"{len(info['cells'])} cells, {segment_count} segments ({moved} on no nav mesh), "
          f"{len(info['graph']['nodes'])} nodes, {len(info['graph']['links'])} links, "
          f"{len(mesh_aids)} nav meshes, {len(w.blob.words) * 4 // 1024} KB")


def write_meshes(port, level, sources):
    """The nav meshes alone of source levels without traffic data (a place's, where its enemies
    walked), as they are, with their ids: an actor finds its own by id (its nav-mesh-actor lump,
    entity-nav-mesh-by-aid: a binary search over the bsp's nav meshes, which the level builder
    sorts by id), or the nearest one (find-nearest-nav-mesh)."""
    w = data_blob.Writer()
    aids = []
    for src in sources:
        blob = data_blob.Blob(os.path.join(port.source.ENTITIES, src + "-nav.json"))
        base = w.append_blob(blob)
        for root, byte in blob.roots.items():
            w.blob.roots[f"nav-mesh-{src}-{root}"] = byte + base
            aids.append(blob.u32(byte + 44))
    assert len(set(aids)) == len(aids), f"{level.name}: two nav meshes with the same id"
    write_if_changed(nav_path(level), json.dumps(w.blob.to_json(), separators=(",", ":")))
    print(f"  {level.name}: the nav meshes of {', '.join(sources)}: {len(aids)} nav meshes, "
          f"{len(w.blob.words) * 4 // 1024} KB")


def mesh_tag(blob, root):
    """Byte of the type tag of the nav-mesh of entity-nav-mesh ROOT (its field after the aid)."""
    return blob.ptr(blob.roots[root] + 48) - 4


def mesh_poly(blob, tag, i):
    """Poly I of the nav mesh at TAG: its vertices (world), adjacent polys (one per edge, from
    vertex k to k + 1, 255 none), pat and link. A poly is 64 bytes: 4 vertices local to the mesh's
    origin, their w words id, pat, vertex count and link (bytes), the adjacent polys (bytes), min-y,
    max-y (local)."""
    origin = [blob.f32(tag + 48 + 4 * k) for k in range(3)]
    at = blob.ptr(tag + 8) + 64 * i
    count = blob.u8(at + 14)
    return {"v": [[blob.f32(at + 16 * j + 4 * k) + origin[k] for k in range(3)] for j in range(count)],
            "adj": [blob.u8(at + 28 + j) for j in range(4)]}


def poly_raw(origin, i, verts, adj, pat=0, link=255):
    """64 bytes of a nav-poly (see mesh_poly): VERTS in world coordinates."""
    local = [[v[k] - origin[k] for k in range(3)] for v in verts]
    ys = [v[1] for v in local]
    out = b""
    for j in range(4):
        v = local[j] if j < len(local) else [0.0, 0.0, 0.0]
        w = [struct.pack("<4B", i, pat, len(local), link), bytes(adj), struct.pack("<f", min(ys)),
             struct.pack("<f", max(ys))][j]
        out += struct.pack("<3f", *v) + w
    return out


def add_polys(blob, tag, polys, link):
    """The nav mesh at TAG with POLYS (dicts of v, adj, pat, link; their ids follow the mesh's) after
    its own, and LINK (a nav-mesh-link's id, dest-mesh-id, src-link-poly-id, src-switch-poly-id) in
    its link-array: a new poly array, route table and link array at the blob's end, and the new
    polys' bits in its poly-hash. The new polys hang off one old poly (`anchor`, their only way to
    the rest of the mesh), whose free edge toward them the caller set in `anchor_edge`."""
    n = blob.u8(tag + 13)
    total = n + len(polys)
    assert total <= 255, "a nav mesh has at most 255 polys"
    origin = [blob.f32(tag + 48 + 4 * k) for k in range(3)]
    old_array = blob.ptr(tag + 8)
    adj = [mesh_poly(blob, tag, i)["adj"] for i in range(n)] + [p["adj"] for p in polys]
    anchor, anchor_edge = polys[0]["anchor"], polys[0]["anchor_edge"]
    adj[anchor][anchor_edge] = n

    def put_ptr(field, target):
        blob.pointers[(tag + field) // 4] = target
        blob.words[(tag + field) // 4] = 0

    def append(data):
        while len(blob.words) % 4:
            blob.words.append(0)
        start = len(blob.words) * 4
        data += b"\0" * (-len(data) % 16)
        blob.words += list(struct.unpack("<%dI" % (len(data) // 4), data))
        return start

    # the polys: the old ones as they are but the anchor's adjacency, then the new ones
    raw = bytearray(blob.raw(old_array, 64 * n))
    raw[64 * anchor + 28 + anchor_edge] = n
    for i, p in enumerate(polys):
        raw += poly_raw(origin, n + i, p["v"], p["adj"], p.get("pat", 0), p.get("link", 255))
    put_ptr(8, append(bytes(raw)))
    blob.words[(tag + 12) // 4] = (blob.words[(tag + 12) // 4] & ~0xff00) | (total << 8)

    # the route table: 2 bits per (from, to), the index of from's edge toward to. Old pairs keep
    # theirs; an old poly reaches a new one through the anchor; a new one walks its strip.
    old_route = blob.ptr(tag + 16)

    def old_hop(a, b):
        bit = (b + a * n) * 2
        return (blob.u8(old_route + bit // 8) >> (bit % 8)) & 3

    def strip_hop(a, b):
        """The edge of new poly A toward B (a new poly, or the anchor for any old one)."""
        seen, todo = {a: None}, [a]
        while todo:
            cur = todo.pop(0)
            for k, nb in enumerate(adj[cur]):
                if nb != 255 and nb not in seen and (nb >= n or nb == anchor):
                    seen[nb] = k if cur == a else seen[cur]
                    todo.append(nb)
        return seen[b]

    route = bytearray((total * total * 2 + 7) // 8)
    for a in range(total):
        for b in range(total):
            if a == b:
                continue
            if a < n and b < n:
                hop = old_hop(a, b)
            elif a < n:
                hop = adj[anchor].index(n) if a == anchor else old_hop(a, anchor)
            else:
                hop = strip_hop(a, b if b >= n else anchor)
            bit = (b + a * total) * 2
            route[bit // 8] |= hop << (bit % 8)
    put_ptr(16, append(bytes(route)))

    # the poly-hash: each new poly's bit in the cells its box covers (as setup-search-box)
    hash_tag = blob.ptr(tag + 20) - 4
    size = blob.s16(hash_tag + 14)
    assert total <= 8 * size, "the poly-hash's buckets have no bit left for the new polys"
    scale = [blob.f32(hash_tag + 16 + 4 * k) for k in range(3)]
    dims = [blob.s8(hash_tag + 28 + k) for k in range(3)]
    box_min = [blob.f32(hash_tag + 36 + 4 * k) for k in range(3)]
    buckets = blob.ptr(hash_tag + 32)
    for i, p in enumerate(polys):
        local = [[v[k] - origin[k] for k in range(3)] for v in p["v"]]
        cell = [[max(0, min(int((f(v[k] for v in local) - box_min[k]) * scale[k]), dims[k] - 1))
                 for f in (min, max)] for k in range(3)]
        for x in range(cell[0][0], cell[0][1] + 1):
            for y in range(cell[1][0], cell[1][1] + 1):
                for z in range(cell[2][0], cell[2][1] + 1):
                    byte = buckets + x * size + z * dims[0] * size + y * dims[0] * dims[2] * size \
                        + (n + i) // 8
                    blob.words[byte // 4] |= 1 << ((n + i) % 8 + 8 * (byte % 4))
    blob.words[(hash_tag + 60) // 4] = (blob.words[(hash_tag + 60) // 4] & ~0xffff) | total

    # the link array: the old links, then this one (its dest-mesh #f until both meshes are born)
    count = blob.u8(tag + 72)
    old_links = blob.ptr(tag + 68)
    links = bytearray(blob.raw(old_links, 16 * count) if count else b"")
    lid, dest, link_poly, switch_poly = link
    links += struct.pack("<II4BI", lid, dest, link_poly, switch_poly, 255, 255, 0)
    start = append(bytes(links))
    for k in range(count):
        if (old_links + 16 * k + 12) // 4 in blob.symbols:
            blob.symbols[(start + 16 * k + 12) // 4] = blob.symbols[(old_links + 16 * k + 12) // 4]
        elif (old_links + 16 * k + 12) // 4 in blob.pointers:
            blob.pointers[(start + 16 * k + 12) // 4] = blob.pointers[(old_links + 16 * k + 12) // 4]
    blob.symbols[(start + 16 * count + 12) // 4] = "#f"
    put_ptr(68, start)
    blob.words[(tag + 72) // 4] = (blob.words[(tag + 72) // 4] & ~0xff) | (count + 1)
    return n


def link_meshes(meshes, cfg, link_id):
    """A walkable strip between two nav meshes and a nav-mesh-link between them, the way Jak 3 links
    its own (ctyslumc and ctyslumb): the strip from poly a's free edge to poly b's, cut in three, A
    taking its first two thirds, B all three. Each mesh has a landing poly (pat 0) and a switch poly
    (pat 4, its link field the link's index) over the other's landing poly: a nav-enemy on a switch
    poly moves onto the other mesh (nav-enemy-method-188), where it stands on a landing poly. A
    gets [landing 0-1/3, switch 1/3-2/3]; B [switch 0-1/3, landing 1/3-2/3, 2/3-1 to its poly]."""
    sides = []
    for key in ("a", "b"):
        src, index, poly, edge = cfg[key]
        blob = meshes[src]
        tag = mesh_tag(blob, f"nav-mesh-{index}")
        p = mesh_poly(blob, tag, poly)
        assert p["adj"][edge] == 255, f"{src} mesh {index} poly {poly} edge {edge} isn't free"
        sides.append((blob, tag, poly, edge, p["v"][edge], p["v"][(edge + 1) % len(p["v"])],
                      blob.u32(blob.roots[f"nav-mesh-{index}"] + 44)))
    (blob_a, tag_a, poly_a, edge_a, a0, a1, aid_a), (blob_b, tag_b, poly_b, edge_b, b0, b1, aid_b) = sides
    # the two edges face each other: a0 across from b1, a1 from b0
    assert math.dist(a0, b1) < math.dist(a0, b0), "the edges don't face each other"

    def at(t):
        return ([a0[k] + (b1[k] - a0[k]) * t for k in range(3)], [a1[k] + (b0[k] - a1[k]) * t for k in range(3)])

    def quad(t0, t1):
        """The strip from T0 to T1, wound as the meshes' polys: edge 0 toward t0, edge 2 toward t1."""
        (l0, r0), (l1, r1) = at(t0), at(t1)
        return [r0, l0, l1, r1]

    third = 1.0 / 3.0
    n_a, n_b = blob_a.u8(tag_a + 13), blob_b.u8(tag_b + 13)
    link_a, link_b = blob_a.u8(tag_a + 72), blob_b.u8(tag_b + 72)
    add_polys(blob_a, tag_a, [
        {"v": quad(0, third), "adj": [poly_a, 255, n_a + 1, 255], "anchor": poly_a, "anchor_edge": edge_a},
        {"v": quad(third, 2 * third), "adj": [n_a, 255, 255, 255], "pat": 4, "link": link_a},
    ], (link_id, aid_b, n_a, n_a + 1))
    add_polys(blob_b, tag_b, [
        {"v": quad(2 * third, 1), "adj": [n_b + 1, 255, poly_b, 255], "anchor": poly_b, "anchor_edge": edge_b},
        {"v": quad(third, 2 * third), "adj": [n_b + 2, 255, n_b, 255]},
        {"v": quad(0, third), "adj": [255, 255, n_b + 1, 255], "pat": 4, "link": link_b},
    ], (link_id, aid_a, n_b + 1, n_b + 2))
    print(f"  linked {cfg['a']} and {cfg['b']} across {math.dist(a0, b1) / 4096:.1f} to "
          f"{math.dist(a1, b0) / 4096:.1f} m (link id {link_id:#x})")


def write_level(port, level):
    cfg = level["nav"]
    meter = port.source.METER
    entities = port.source.ENTITIES
    if "height_map" in cfg:
        dims = write_height_map(port, level, cfg["height_map"]["source"])
        print(f"  wrote {height_map_path(port, level)} ({dims[0]} x {dims[1]} heights)")
    sources = city_sources(port, level)
    if len(sources) == 1:
        write_district(port, level, sources[0])
        return
    if not sources:
        if nav_sources(port, level):
            write_meshes(port, level, nav_sources(port, level))
        return
    districts, meshes = {}, {}
    for src in sources:
        city_path = os.path.join(entities, src + "-city.json")
        districts[src] = decode_city(data_blob.Blob(city_path))
        nav_path_src = os.path.join(entities, src + "-nav.json")
        if os.path.exists(nav_path_src):
            meshes[src] = data_blob.Blob(nav_path_src)
    mesh_aids = {blob.u32(byte + 44) for blob in meshes.values() for byte in blob.roots.values()}
    for k, link in enumerate(cfg.get("links", [])):
        link_meshes(meshes, link, 0x7f000000 + k)
    grid, cells, segments, nodes, branches = merge(districts, mesh_aids, cfg["cell"] * meter,
                                                   cfg["outside_depth"] * meter)
    if "clock" in cfg:
        # every lane's territory (clock-type, byte 10) and clock-mask (byte 11): the target game's
        # city code sends a citizen on a lane of a territory its faction manager doesn't know to
        # sleep (citizen.gc enemy-common-post): Jak 3's Spargus lanes are territory 128
        kind, mask = cfg["clock"]
        branches = [patch(patch(b, 10, "<B", kind), 11, "<B", mask) for b in branches]
    w = data_blob.Writer()
    write_city(w, grid, cells, segments, nodes, branches,
               max(c["camera_ceiling"] for c in districts.values()), level.name)
    n_meshes = 0
    for src, blob in meshes.items():
        base = w.append_blob(blob)
        for root, byte in blob.roots.items():
            w.blob.roots[f"nav-mesh-{src}-{root}"] = byte + base
            n_meshes += 1
    write_if_changed(nav_path(level), json.dumps(w.blob.to_json(), separators=(",", ":")))
    print(f"  {level.name}: {len(districts)} districts: grid {grid['dims']}, {len(cells)} cells, "
          f"{len(segments)} segments, {len(nodes)} nodes, {len(branches)} branches, "
          f"{n_meshes} nav meshes, {len(w.blob.words) * 4 // 1024} KB")


def run(port):
    for level in port.levels:
        if "nav" in level:
            write_level(port, level)
