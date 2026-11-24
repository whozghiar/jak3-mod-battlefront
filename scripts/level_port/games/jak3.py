"""Jak 3 as a target game: its level heap, and the GOAL text of its level-load-infos and continue
points."""

NAME = "jak3"
TITLE = "Jak 3"
ISO = "iso_data/jak3"
FR3 = "out/jak3/fr3"
METER = 4096.0
# the sound banks always loaded (game/overlord/jak3/sbank.cpp: common), the ones of Jak's state
# (its "mode" bank: gun, board, Dark Jak...) and the ones of a language (commonj: Japanese), for
# the sound check (steps/sound_check.py)
ALWAYS_LOADED_BANKS = ["common"]
STATE_BANK_PREFIXES = ["mode"]
LANGUAGE_BANKS = ["commonj"]

# Jak 3's level heap is 18 chunks. A level of each memory mode takes one of these chunk sets (the
# plain case of level-group::alloc-levels!, goal_src/jak3/engine/level/level.gc, no micro or tiny
# level loaded), so levels fit together when they can take chunk sets that don't overlap. Jak 2's
# load-buffer-mode has the same four names (small-edge when a level has none).
CHUNKS = {
    "large": [0xFFF, 0x3FFC0],
    "medium": [0x1FF, 0x3FE00],
    "small-center": [0xFC0],
    "small-edge": [0x3F, 0x3F000],
}
CHUNK_COUNT = {mode: bin(masks[0]).count("1") for mode, masks in CHUNKS.items()}
# the memory modes, smallest first
MEMORY_ORDER = ["small-edge", "small-center", "medium", "large"]


def fits(modes):
    """Can levels of these memory modes be loaded together?"""
    def place(i, used):
        return i == len(modes) or any(not mask & used and place(i + 1, used | mask)
                                      for mask in CHUNKS[modes[i]])
    return place(0, 0)


def int16(x):
    return max(-32768, min(32767, int(round(x * 32767))))


def continue_point(cont_name, level, trans, camera_trans, quat, camera_rot, flags, wants,
                   want_sound="#f #f #f", indent=6):
    """A continue-point (positions in game units, rotations as floats)."""
    pad = " " * indent
    t, c, q = trans, camera_trans, quat
    rot = " ".join(str(int16(x)) for x in camera_rot)
    want_lines = "\n".join(
        f"{pad}    (new 'static 'level-buffer-state-small :name '{name} :display? {disp})"
        for name, disp in wants
    )
    flags_line = f"{pad}  :flags (continue-flags {' '.join(flags)})\n" if flags else ""
    return f"""{pad}(new 'static 'continue-point
{pad}  :name "{cont_name}"
{pad}  :level '{level}
{pad}  :trans (static-vectorm {t[0] / METER:.4f} {t[1] / METER:.4f} {t[2] / METER:.4f})
{pad}  :camera-trans (static-vectorm {c[0] / METER:.4f} {c[1] / METER:.4f} {c[2] / METER:.4f})
{pad}  :quat (new 'static 'vector4h :data (new 'static 'array int16 4 {int16(q[0])} {int16(q[1])} {int16(q[2])} {int16(q[3])}))
{pad}  :camera-rot (new 'static 'array int16 9 {rot})
{flags_line}{pad}  :on-goto #f
{pad}  :vis-nick '{level}
{pad}  :vehicle-type #x1b
{pad}  :want-count {len(wants)}
{pad}  :want (new 'static 'inline-array level-buffer-state-small {len(wants)}
{want_lines}
{pad}    )
{pad}  :want-sound (new 'static 'array symbol 3 {want_sound})
{pad}  )"""


def level_load_info(name, nick, index, memory_mode, flags, mood, continues, callbacks, ocean,
                    comment, draw_priority, outdoor, part_engine_max=0, music="#f",
                    extra_sound_bank="#f", city_map_bits=0, borrow_sizes=None):
    """A level-load-info, and its registration in *level-load-list*. city_map_bits: the squares of
    the city's 5x7 minimap grid (bit 5 * row + column) whose map the level holds. borrow_sizes:
    the sizes (KB, at most 5) of the borrow heaps the level hosts at the top of its heap, where the
    game loads a borrow level (Jak 3's vinroom: one of 3000, for its power game's board, powergd);
    none: no borrow heap."""
    flags_line = f"    :level-flags (level-flags {flags})\n" if flags else ""
    bits = " ".join(f"cmb{i}" for i in range(34) if city_map_bits >> i & 1)
    map_line = f"    :city-map-bits (city-map-bits {bits})\n" if bits else ""
    if outdoor:
        # the weather of an outdoor level: clouds and fog anywhere in 0..1, rain when both are high
        weather = ("    :max-rain 1.0\n"
                   "    :mood-range (new 'static 'mood-range :max-cloud 1.0 :max-fog 1.0)\n")
    else:
        weather = "    :max-rain 0.0\n    :mood-range (new 'static 'mood-range)\n"
    ocean_value = f"'{ocean}" if ocean else "#f"
    if borrow_sizes:
        sizes = " ".join(str(int(x)) for x in (list(borrow_sizes) + [0] * 5)[:5])
        borrow = ("(new 'static 'level-borrow-info :alias #f :borrow-size (new 'static 'array uint16 5 "
                  f"{sizes}) :borrow-info (new 'static 'array object 5 #f #f #f #f #f))")
    else:
        borrow = "#f"
    callback_list = (
        "'(" + " ".join(f"({slot} . {fn})" for slot, fn in callbacks) + ")" if callbacks else "'()"
    )
    return f"""{comment}
(define {name}
  (new 'static 'level-load-info
    :name '{name}
    :visname '{name}-vis
    :nickname '{nick}
    :dbname '{name}
    :taskname 'default
    :index #x{index:x}
    :master-level #f
{flags_line}    :packages '()
    :run-packages '("common")
    :memory-mode (level-memory-mode {memory_mode})
    :music-bank {music}
    :extra-sound-bank {extra_sound_bank}
    :mood-func '{mood}
    :special-mood #f
    :ocean {ocean_value}
    :ocean-alpha 1.0
    :priority 100
    :draw-priority {draw_priority}
{map_line}    :part-engine-max {part_engine_max}
    :base-task-mask (task-mask task0)
    :bigmap-id (bigmap-id none)
    :continues '(
{chr(10).join(continues)}
      )
    :callback-list {callback_list}
    :borrow {borrow}
    :bottom-height (meters -100)
    :fog-height (meters 80)
{weather}    :fog-mult 1.0
    )
  )

(cons! *level-load-list* '{name})
"""


# Jak 3 as a source game ##########################################################################
# A port can take Jak 3's own levels too (the Battlefront mod's Spargus: wascitya and wascityb as
# one level that runs Haven City's traffic code). The decompiler's dumps have Jak 2's layouts:
#   - decompiler_out/jak3/entities/<level>-actors.json, -cameras.json, -nav.json, -city.json,
#   - decompiler_out/jak3/levels/<level>/*.glb: its model rips (rip_levels),
#   - out/jak3/fr3/<level>.fr3: its background, collision and textures.
# Only what such a port uses is read: no story (every actor of a dump is spawned), no regions.

import functools  # noqa: E402
import glob  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import re  # noqa: E402

ENTITIES = "decompiler_out/jak3/entities"
RIPS = "decompiler_out/jak3/levels"
RAW_OBJ = "decompiler_out/jak3/raw_obj"
LEVEL_INFO = "goal_src/jak3/engine/level/level-info.gc"

# the background's sun directions, as Jak 2's (palettes 1-4 of the time of day; mesh.py lights the
# props baked into the background with them)
SUN_DIRECTIONS = [
    (0.906, 0.397, 0.143),
    (0.5, 0.814, 0.296),
    (-0.5, 0.814, 0.296),
    (-0.906, 0.397, 0.143),
]

# Jak 3's classes whose rip has another name (mesh.py find_rip): the art group their code spawns
RIP_NAMES = {
    "wascity-market-basket-a": "market-basket-a",
    "wascity-market-basket-b": "market-basket-b",
    "wascity-market-crate": "market-crate",
    "wascity-market-sack-a": "market-sack-a",
    "wascity-market-sack-b": "market-sack-b",
    "wascity-fruit-stand": "cty-fruit-stand",
    "wascity-cactus": "des-cactus-a",
}


@functools.lru_cache(maxsize=None)
def _level_actor_dump(level):
    path = os.path.join(ENTITIES, level + "-actors.json")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f) or []


def dump_actors(level):
    """Every actor of a level's dump."""
    return list(_level_actor_dump(level))


class Story:
    """Jak 3 as a source has no story state: every actor of a dump is spawned and every background
    prototype shown."""

    def __init__(self, state="end", open_tasks=(), level_open_tasks=None):
        pass

    def closed(self, task, open_tasks=(), level=None):
        return True

    def task_mask(self, level):
        return 0

    def spawned(self, actor, level):
        return True

    def level_actors(self, level):
        return list(_level_actor_dump(level))

    def all_actors(self):
        by_name = {}
        for path in glob.glob(f"{ENTITIES}/*-actors.json"):
            level = os.path.basename(path)[: -len("-actors.json")]
            for actor in _level_actor_dump(level):
                by_name[(level, actor["lump"].get("name"))] = actor
        return by_name

    def hidden_prototypes(self, levels):
        return []


def _level_blocks():
    src = open(LEVEL_INFO, encoding="utf-8").read()
    for block in re.split(r"\n\(define ", src):
        if "level-load-info" in block[:200]:
            yield block


def level_names():
    """Every Jak 3 level name (a level-load-info's :name is alone on its line)."""
    src = open(LEVEL_INFO, encoding="utf-8").read()
    return set(re.findall(r"^\s*:name '([a-z0-9-]+)\s*$", src, re.M))


@functools.cache
def _nicknames():
    out = {}
    for block in _level_blocks():
        name = re.search(r":name '([\w-]+)", block)
        nick = re.search(r":nickname '([\w-]+)", block)
        if name and nick:
            out[name.group(1)] = nick.group(1)
    return out


def dgo_of(level):
    """The DGO holding a level: its nickname's (wascitya: WCA.DGO)."""
    return _nicknames()[level].upper() + ".DGO"


def memory_modes():
    """Jak 3 level -> its level-memory-mode."""
    out = {}
    for block in _level_blocks():
        name = re.search(r":name '([\w-]+)", block)
        mode = re.search(r":memory-mode \(level-memory-mode ([\w-]+)\)", block)
        if name:
            out[name.group(1)] = mode.group(1) if mode else "small-edge"
    return out


def music_banks():
    """Jak 3 level -> its music (level-load-info :music-bank), for the levels with one."""
    out = {}
    for block in _level_blocks():
        name = re.search(r":name '([\w-]+)", block)
        music = re.search(r":music-bank '([\w-]+)", block)
        if name and music:
            out[name.group(1)] = music.group(1)
    return out


def cameras(level):
    """A level's fixed cameras (<level>-cameras.json), [] if it has none."""
    path = f"{ENTITIES}/{level}-cameras.json"
    if not os.path.exists(path):
        return []
    return json.load(open(path))


def _vector(block, key):
    """A continue's vector field (game units): (new 'static 'vector :x ...) or (static-vectorm x y
    z) in meters (the test continues)."""
    m = re.search(r":" + key + r" \(static-vectorm ([^)]*)\)", block)
    if m:
        return [float(x) * METER for x in m.group(1).split()] + [1.0]
    m = re.search(r":" + key + r" \(new 'static 'vector([^)]*)\)", block)
    values = {"x": 0.0, "y": 0.0, "z": 0.0, "w": 0.0}
    for k, v in re.findall(r":([xyzw]) (-?[0-9.e+-]+)", m.group(1)):
        values[k] = float(v)
    return [values["x"], values["y"], values["z"], values["w"]]


def _int16s(text):
    """The values of a GOAL int16 array (#x... above #x7fff are negative)."""
    out = []
    for x in text.split():
        v = int(x[2:], 16) if x.startswith("#x") else int(x)
        out.append(v - 0x10000 if v > 0x7fff else v)
    return out


def continues():
    """Jak 3's continue points: name -> level, trans, quat, camera_trans, camera_rot (game units,
    the rotations as floats), flags, wants (the level list: (level, display?))."""
    src = open(LEVEL_INFO, encoding="utf-8").read()
    result = {}
    for block in re.split(r"\(new 'static 'continue-point", src)[1:]:
        head, _, rest = block.partition(":want ")
        name = re.search(r':name "([^"]+)"', head).group(1)
        quat = re.search(r":quat \(new 'static 'vector4h :data \(new 'static 'array int16 4 ([^)]*)\)",
                         head)
        rot = re.search(r":camera-rot \(new 'static 'array int16 9 ([^)]*)\)", head)
        flags = re.search(r":flags \(continue-flags([^)]*)\)", head)
        wants = re.findall(r"level-buffer-state-small :name '([a-z0-9-]+) :display\? ('?[a-z#]+)",
                           rest.split(":want-sound")[0])
        sounds = re.search(r":want-sound \(new 'static 'array symbol 3 ([^)]*)\)", rest)
        result[name] = dict(
            level=re.search(r":level '([a-z0-9-]+)", head).group(1),
            trans=_vector(head, "trans"),
            quat=[x / 32767.0 for x in _int16s(quat.group(1))],
            camera_trans=_vector(head, "camera-trans"),
            camera_rot=[x / 32767.0 for x in _int16s(rot.group(1))],
            flags=set(flags.group(1).split()) if flags else set(),
            wants=wants,
            want_sound=[None if x == "#f" else x.lstrip("'") for x in sounds.group(1).split()]
            if sounds else [None] * 3,
        )
    return result


def regions():
    """No region of Jak 3 is ported (its load and camera regions concern its own levels)."""
    return {}
