"""
Ashelin's clips for the Battlefront mod (round 55: Jak's own moves on her body, the author's wish):
from her Jak Animation Studio creation (Jak 3's ashelin-lod0 with Jak's clips of the player's
extraction, jakb-lod0's, each put on her with apply_mocap at 30 keys a second, named "j <clip>"
without its "jakb-"; and round 54's Mixamo pistol captures), keep those animations alone, cut,
chained, reversed, renamed, in custom_assets/jak3/models/bf-ashelin-clips.glb. The file holds the
joints' names and their keys, nothing of the game: at install, mod_models.py makes her clips from it
and from the rip ("made_from" and "made_clips" of bf-ashelin in custom_assets/jak3/models/models.jsonc),
her fingers, pistols and firing set there.

    python scripts/battlefront/make_ashelin_clips.py <creation .glb>

As for the Baron (make_baron_clips.py, whose helpers this reuses): the capture's hips' travel goes on
`main` (her upper body hangs on `main`, beside the hips: crouching, her legs folded under a torso left
standing), the loops are closed, the root's travel across (`align`) is dropped. Jak runs and crouches
on bent legs: her body is lowered until her lowest foot touches the ground (her rest pose's), and her
run's bounce is halved (his legs short). Her jump and flip keep their height
flat (the game lifts her). The ground a loop's feet cover a second at rate 1 is printed: the game's
BF_ASH_*_GROUND, her clips played at the rate that keeps her feet from sliding.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "modding"))
from make_baron_clips import Pose, close_loop, cut, ground_per_second, move_root, unit_rot, widen_stride  # noqa: E402
from mod_models import Glb, Writer  # noqa: E402

# file clip name, the studio animations (chained), the seconds kept (start, end; None: to its end),
# a loop, its height: "flat" (the game moves her up and down), "ground" (her lowest foot on the
# ground) or None; reversed
CLIPS = [
    ("jk-idle", ["j stance-loop"], 0.0, None, True, "ground", False),
    ("jk-run", ["j run"], 0.0, None, True, "ground", False),
    ("jk-walk", ["j walk"], 0.0, None, True, "ground", False),
    ("jk-walk-back", ["j walk"], 0.0, None, True, "ground", True),
    ("jk-side", ["j gun-walk-side"], 0.0, None, True, "ground", False),
    ("jk-jump", ["j jump"], 0.15, None, False, "flat", False),
    ("jk-flip", ["j roll-flip"], 0.0, None, False, "flat", False),
    ("jk-crouch", ["j stance-to-duck"], 0.0, None, False, "ground", False),
    ("jk-crouch-idle", ["j duck-stance"], 0.0, None, True, "ground", False),
    ("jk-uncrouch", ["j stance-to-duck"], 0.0, None, False, "ground", True),
    ("jk-roll", ["j gun-duck-roll", "j gun-duck-roll-end"], 0.0, None, False, None, False),
    ("jk-kick", ["j attack-from-stance", "j attack-from-stance-end"], 0.0, None, False, "ground", False),
]
STRIDE: dict[str, float] = {}
BOUNCE = {"jk-run": 0.5}
# not keyed: the root's travel, and the joints mod_models sets (her fingers, her pistol)
SKIP = {"align", "prejoint", "gun", "LmiddleA", "LmiddleB", "LthumbA", "LthumbB",
        "RmiddleA", "RmiddleB", "RthumbA", "RthumbB"}
FEET = ("Lankle", "Rankle", "Lball", "Rball")

OUT = Path(__file__).resolve().parents[2] / "custom_assets" / "jak3" / "models" / "bf-ashelin-clips.glb"


def keys_of(channels):
    """A function from a time to every channel's key at it (the last key before)."""
    def keys_at(t):
        out_keys = {}
        for k, (times, values) in channels.items():
            i = max(0, min(int(np.searchsorted(times, t + 1e-6, side="right") - 1), len(values) - 1))
            out_keys[k] = values[i]
        return out_keys
    return keys_at


def low_foot(pose: Pose, keys):
    w = pose.world(keys)
    return min(w(pose.index[f])[1, 3] for f in FEET)


def lift_main(pose: Pose, channels, dy):
    """`main` raised by DY metres (an array a key, or one number) along the world's up."""
    key = (pose.index["main"], "translation")
    times, v = channels[key]
    up = unit_rot(pose.world({})(pose.parent[pose.index["main"]])).T @ np.array([0.0, 1.0, 0.0])
    channels[key] = (times, v + np.outer(np.broadcast_to(dy, (len(v),)), up))


def chain(src: Glb, by_name, studios, start, end):
    """The studio animations STUDIOS one after the other, their channels by (node, path), cut."""
    channels, offset = {}, 0.0
    for n, studio in enumerate(studios):
        anim = by_name[studio]
        length = 0.0
        for c in anim["channels"]:
            s = anim["samplers"][c["sampler"]]
            times = src.accessor(s["input"])[:, 0].astype(float)
            values = src.accessor(s["output"]).astype(float)
            length = max(length, float(times[-1]))
            key = (c["target"]["node"], c["target"]["path"])
            if key in channels and n > 0:
                t0, v0 = channels[key]
                channels[key] = (np.append(t0, times + offset), np.vstack([v0, values]))
            elif n == 0:
                channels[key] = (times, values)
        offset += length + 1.0 / 30
    for key, (times, values) in list(channels.items()):
        channels[key] = cut(times, values, start, end)
    return channels


def main() -> int:
    src = Glb(Path(sys.argv[1]))
    pose = Pose(src)
    nodes = src.json["nodes"]
    by_name = {a.get("name"): a for a in src.json.get("animations", [])}
    missing = sorted({st for _, studios, *_ in CLIPS for st in studios if st not in by_name})
    if missing:
        sys.exit(f"{src.path}: no animation {missing}")
    out = Writer()
    node_ids: dict[str, int] = {}

    def node(name: str) -> int:
        if name not in node_ids:
            out.json["nodes"].append({"name": name})
            node_ids[name] = len(out.json["nodes"]) - 1
        return node_ids[name]

    main_rest = pose.rest(pose.index["main"])[:3, 3]
    ground = low_foot(pose, {})
    for game, studios, start, end, loop, height, backward in CLIPS:
        channels = chain(src, by_name, studios, start, end)
        if backward:
            for k, (times, values) in channels.items():
                channels[k] = (times, values[::-1].copy())
        if loop:
            for k, (times, values) in channels.items():
                channels[k] = close_loop(times, values, k[1] == "rotation")
        move_root(pose, channels)
        key = (pose.index["main"], "translation")
        keys_at = keys_of(channels)
        all_times = max((ts for ts, _ in channels.values()), key=len)
        if height == "flat" and key in channels:
            times, v = channels[key]
            v = v.copy()
            v[:, 1] = main_rest[1]
            channels[key] = (times, v)
        if game in STRIDE:
            widen_stride(pose, channels, STRIDE[game])
        if height == "ground" and key in channels:
            lows = np.array([low_foot(pose, keys_at(t)) for t in channels[key][0]])
            if game in BOUNCE:
                # the bounce scaled about its lowest: her body nearer the ground in the air
                lift_main(pose, channels, (lows - lows.min()) * (BOUNCE[game] - 1.0))
                lows = np.array([low_foot(pose, keys_at(t)) for t in channels[key][0]])
            lift_main(pose, channels, ground - lows.min())
        if loop:
            g = ground_per_second(pose, keys_at, all_times)
            drift = side_drift(pose, keys_at, all_times)
            print(f"  {game}: its feet cover {g:.2f} m a second at rate 1, the body going {drift}")
        samplers, chans = [], []
        for (nd, path), (times, values) in channels.items():
            name = nodes[nd]["name"]
            if name in SKIP:
                continue
            if path == "translation" and name != "main" and float(np.abs(values - values[0]).max()) < 1e-4:
                continue
            if path == "scale" and float(np.abs(values - 1.0).max()) < 1e-4:
                continue
            t_acc = out.accessor(np.asarray(times, np.float32).reshape(-1, 1), "SCALAR", 5126, minmax=True)
            samplers.append({"input": t_acc, "output": out.accessor(np.asarray(values, np.float32),
                                                                    "VEC4" if path == "rotation" else "VEC3", 5126),
                             "interpolation": "LINEAR"})
            chans.append({"sampler": len(samplers) - 1, "target": {"node": node(name), "path": path}})
        out.json["animations"].append({"name": game, "samplers": samplers, "channels": chans})
        print(f"  {game:16s} {' + '.join(studios):40s} {all_times[-1]:.2f} s, {len(all_times)} keys{' (loop)' if loop else ''}")
    out.json["scenes"][0]["nodes"] = list(range(len(out.json["nodes"])))
    OUT.write_bytes(out.save_bytes())
    print(f"{OUT}: {len(CLIPS)} clips, {len(out.json['nodes'])} joints, {OUT.stat().st_size // 1024} KB")
    return 0


def side_drift(pose: Pose, keys_at, times):
    """Where the body goes, from the way its planted feet slide under it: "forward", "backward", "to
    her left" (+x) or "to her right"."""
    pos = []
    for t in times:
        w = pose.world(keys_at(t))
        pos.append([w(pose.index[f])[:3, 3] for f in ("Lankle", "Rankle")])
    pos = np.array(pos)
    moves = []
    for f in range(2):
        y = pos[:, f, 1]
        low = y.min() + 0.05
        for i in range(len(times) - 1):
            if y[i] < low and y[i + 1] < low:
                moves.append(pos[i + 1, f] - pos[i, f])
    if not moves:
        return "nowhere"
    d = -np.mean(moves, axis=0)
    if abs(d[0]) > abs(d[2]):
        return "to her left" if d[0] > 0 else "to her right"
    return "forward" if d[2] > 0 else "backward"


if __name__ == "__main__":
    sys.exit(main())
