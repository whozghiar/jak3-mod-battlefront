#!/usr/bin/env python3
"""
Ashelin's motion-capture clips for the Battlefront mod (round 54): from her Jak Animation Studio
creation (Jak 3's ashelin-lod0 with the Mixamo pistol motions of third-party/animations/Ashelin, and
the Baron's "great sword kick" for her roundhouse kick, put on it with apply_mocap at 30 keys a
second), keep those animations alone, cut, renamed, in custom_assets/jak3/models/bf-ashelin-clips.glb.
The file holds the joints' names and their keys, nothing of the game: at install, mod_models.py makes
her clips from it and from the rip ("made_from" and "made_clips" of bf-ashelin in
custom_assets/jak3/models/models.jsonc), her fingers and pistols set there.

    python scripts/battlefront/make_ashelin_clips.py <creation .glb>

As for the Baron (make_baron_clips.py, whose helpers this reuses): the capture's hips' travel goes on
`main` (her upper body hangs on `main`, beside the hips: kneeling, her legs folded under a torso left
standing), the loops are closed, the root's travel across (`align`, studio clips not made in place)
is dropped, and her run's stride is widened so the game plays it slower for the same speed (the
author's wish: no sped-up run). Her jump keeps its part in the air, her height flat (the game lifts
her). The ground a loop's feet cover a second at rate 1 is printed: the game's BF_ASH_*_GROUND.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "modding"))
from make_baron_clips import Pose, close_loop, cut, ground_per_second, move_root, widen_stride  # noqa: E402
from mod_models import Glb, Writer  # noqa: E402

# file clip name, the studio animation, the seconds kept (start, end; None: to its end), loops,
# her height kept flat (the game moves her up and down)
CLIPS = [
    ("mx-idle", "m idle", 0.0, None, True, False),              # pistol idle
    ("mx-run", "m run", 0.0, None, True, False),                # pistol run
    ("mx-walk", "m walk", 0.0, None, True, False),              # pistol walk
    ("mx-jump", "n jump", 0.75, 1.3, False, True),              # pistol jump: off the ground to its top
    ("mx-kneel", "n kneel", 0.0, None, False, False),           # pistol stand to kneel
    ("mx-kneel-idle", "n kneel idle", 0.0, None, True, False),  # pistol kneeling idle
    ("mx-unkneel", "n unkneel", 0.0, None, False, False),       # pistol kneel to stand
    ("mx-strafe-left", "m strafe", 0.0, None, True, False),     # pistol strafe: to her left (+x)
    ("mx-strafe-right", "m strafe2", 0.0, None, True, False),   # pistol strafe (2): to her right
    ("mx-walk-back", "m walk back", 0.0, None, True, False),    # pistol walk backward
    ("mx-kick", "m kick", 0.0, None, False, False),             # great sword kick: a spinning kick
]
STRIDE = {"mx-run": 1.6}
# not keyed: the root's travel, and the joints mod_models sets (her fingers, her pistol)
SKIP = {"align", "prejoint", "gun", "LmiddleA", "LmiddleB", "LthumbA", "LthumbB",
        "RmiddleA", "RmiddleB", "RthumbA", "RthumbB"}

OUT = Path(__file__).resolve().parents[2] / "custom_assets" / "jak3" / "models" / "bf-ashelin-clips.glb"


def main() -> int:
    src = Glb(Path(sys.argv[1]))
    pose = Pose(src)
    nodes = src.json["nodes"]
    by_name = {a.get("name"): a for a in src.json.get("animations", [])}
    missing = [studio for _, studio, *_ in CLIPS if studio not in by_name]
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
    for game, studio, start, end, loop, flat in CLIPS:
        anim = by_name[studio]
        channels = {}
        for c in anim["channels"]:
            s = anim["samplers"][c["sampler"]]
            nd, path = c["target"]["node"], c["target"]["path"]
            times, values = cut(src.accessor(s["input"])[:, 0], src.accessor(s["output"]).astype(float), start, end)
            if loop:
                times, values = close_loop(times, values, path == "rotation")
            channels[(nd, path)] = (times, values)
        move_root(pose, channels)
        key = (pose.index["main"], "translation")
        if flat and key in channels:
            times, v = channels[key]
            v = v.copy()
            v[:, 1] = main_rest[1]
            channels[key] = (times, v)

        def keys_at(t, channels=channels):
            out_keys = {}
            for k, (times, values) in channels.items():
                i = max(0, min(int(np.searchsorted(times, t + 1e-6, side="right") - 1), len(values) - 1))
                out_keys[k] = values[i]
            return out_keys

        all_times = max((ts for ts, _ in channels.values()), key=len)
        if loop:
            before = ground_per_second(pose, keys_at, all_times)
            if game in STRIDE:
                widen_stride(pose, channels, STRIDE[game])
            after = ground_per_second(pose, keys_at, all_times)
            print(f"  {game}: its feet cover {before:.2f} m a second at rate 1" +
                  (f", {after:.2f} widened x{STRIDE[game]}" if game in STRIDE else ""))
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
        print(f"  {game:16s} {studio:14s} {all_times[-1]:.2f} s, {len(all_times)} keys{' (loop)' if loop else ''}")
    out.json["scenes"][0]["nodes"] = list(range(len(out.json["nodes"])))
    OUT.write_bytes(out.save_bytes())
    print(f"{OUT}: {len(CLIPS)} clips, {len(out.json['nodes'])} joints, {OUT.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
