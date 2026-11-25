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
from make_baron_clips import (Pose, axis_angle, close_loop, cut, ground_per_second, mat_to_quat,  # noqa: E402
                              move_root, qinv, qmul, qpow, quat_to_mat, turn_between, unit_rot, widen_stride)
from mod_models import Glb, Writer  # noqa: E402

# file clip name, the studio animations (chained), the seconds kept (start, end; None: to its end),
# a loop, its height: "flat" (the game moves her up and down), "ground" (her lowest foot on the
# ground) or None; reversed
CLIPS = [
    ("jk-idle", ["j stance-loop"], 0.0, None, True, "ground", False),
    # her run: her own, her two pistols in her hands (round 56: Jak's "does not suit her original run
    # with her two weapons")
    ("jk-run", ["ashelin-run0"], 0.0, None, True, "ground", False),
    ("jk-walk", ["j walk"], 0.0, None, True, "ground", False),
    ("jk-walk-back", ["j gun-front-walk"], 0.0, None, True, "ground", True),
    ("jk-side", ["j gun-walk-side"], 0.0, None, True, "ground", False),
    # her walk aside to the right: the left one played backward, her arms as they are (round 56: the
    # mirror put her arms otherwise)
    ("jk-side-right", ["j gun-walk-side"], 0.0, None, True, "ground", True),
    ("jk-jump", ["j jump"], 0.15, None, False, "flat", False),
    ("jk-flip", ["j roll-flip"], 0.0, None, False, "flat", False),
    ("jk-crouch", ["j stance-to-duck"], 0.0, None, False, "ground", False),
    ("jk-crouch-idle", ["j duck-stance"], 0.0, None, True, "ground", False),
    ("jk-uncrouch", ["j stance-to-duck"], 0.0, None, False, "ground", True),
    ("jk-roll", ["j gun-duck-roll", "j gun-duck-roll-end"], 0.0, None, False, None, False),
    # her kick: a captured spinning kick (round 54's Mixamo "m kick"), the author finding Jak's rigid on
    # her (round 56: her leg raised stiff, her body still). Round 61 ("as fast as Jak's"): from 0.12 s,
    # its still start cut, the game playing it faster (battlefront-ashelin.gc BF_ASH_KICK_RATE)
    ("jk-kick", ["m kick"], 0.12, None, False, "ground", False),
    # her grenade throw (round 56), made on Jak's gun stance by make_throw
    ("jk-throw", ["j gun-stance"], 0.0, None, False, "ground", False),
    # her punch (Square, round 60, the author's wish: Jak's punch in place of round 56's pistol whip,
    # its fist growing as his: FIST_SCALE; round 61: her body and arms put back on Jak's, MATCH_JAK)
    ("jk-punch", ["j attack-punch", "j attack-punch-end"], 0.0, None, False, "ground", False),
    # her jump kick (Circle in the air, round 56): her spinning kick in the air, its turn and its kick
    # (0.2 to 1.3 s: facing ahead again), her standing leg folded as in Jak's jump (LEG_TUCK)
    ("jk-jumpkick", ["m kick"], 0.2, 1.3, False, "flat", False),
    # her reload, one pistol then the other (round 56), made by make_reload on her own lowering and
    # raising of her pistols
    ("jk-reload", ["ashelin-standing-to-waiting", "ashelin-waiting-to-standing"], 0.0, None, False, None, False),
    # her firing (round 56): her own shot and recoil, her head raised (her firing clip now takes her
    # chest, neck and head over her legs' clip, and she looked at the ground)
    ("jk-fire", ["ashelin-standing-fire"], 0.0, None, True, None, False),
    # her landings (round 58, the author's wish "as Jak"): Jak's out of a jump and out of his far flip
    ("jk-land", ["j jump-land"], 0.0, None, False, "ground", False),
    ("jk-flip-land", ["j roll-flip-land"], 0.0, None, False, "ground", False),
]
# her run's stride 1.3 times as wide (round 58: she runs 1.5 times as fast, the author wanting no
# sped-up run and no sliding feet): her ankles reach 2.46 m along her body instead of 1.99, 1.24
# times the ground (11.3 m a second, BF_ASH_RUN_GROUND), the game playing it 1.2 times as fast. The
# ground printed for it is off (its 18 keys leave too few with a foot down: 8.25 at 1.3, 13.8 at 1.5)
STRIDE: dict[str, float] = {"jk-run": 1.3}
BOUNCE: dict[str, float] = {}
# a leg held, all along, at its pose at that time of another studio animation: her standing leg folded
# under her in the air
LEG_TUCK = {"jk-jumpkick": ("j jump", 0.25, ("Lthigh", "Lknee", "Lankle", "Lball"))}
# not keyed: the root's travel, the joints mod_models sets (her fingers, her pistol), and her chest's
# two joints, which the studio pulls up to a metre away on Jak's moves (round 56: "a bone of her chest
# stretched")
SKIP = {"align", "prejoint", "gun", "LmiddleA", "LmiddleB", "LthumbA", "LthumbB",
        "RmiddleA", "RmiddleB", "RthumbA", "RthumbB", "ltitA", "rtitA"}
# Jak looks at the ground (his head 50 to 70 degrees down running, jumping, crouching): on her, the
# author saw her head down. These clips get her head raised to her idle's pitch (round 56)
LEVEL_HEAD = {"jk-walk-back", "jk-jump", "jk-crouch", "jk-crouch-idle", "jk-uncrouch",
              "jk-roll", "jk-throw", "jk-punch", "jk-fire", "jk-land", "jk-flip-land"}
HEAD_PITCH = -5.0   # degrees: her idle's (Jak's stance)
BLEND = 0.25        # seconds: two chained animations fade into each other over this
THROW_TIME = 1.35   # seconds: her throw (battlefront-ashelin.gc BF_ASH_THROW_TIME)
# her fighter's guard (`guard_legs`, her throw and her pistol whip): her feet this far ahead and
# behind her hips, her hips lowered this share of her leg (round 56: Jak's gun stance "too wide")
BOX_STEP = 0.2
BOX_BEND = 0.13
BOX_WIDE = 1.3     # her feet apart this many times her hips (her shoulders' width)
RELOAD_HOLD = 1.1   # seconds: her two magazines changed between her pistols' lowering and raising
FEET = ("Lankle", "Rankle", "Lball", "Rball")

OUT = Path(__file__).resolve().parents[2] / "custom_assets" / "jak3" / "models" / "bf-ashelin-clips.glb"
# Jak's punch grows his fist (round 60, the author's wish "the same deformation"): his fingers' scale
# keys (up to 2.58 times), which the studio does not carry over, read from the extraction's Jak
# (jakb-lod0) and put on her fingers. Not on her hand (round 61): her pistol is skinned to her hand, and
# it grew with it, the author seeing her arm swollen. The game scales each joint alone (a child does
# not take its parent's scale), so each finger gets its own keys, as Jak's do.
JAK_RIP = Path(__file__).resolve().parents[2] / "decompiler_out" / "jak3" / "levels" / "common" / "jakb-lod0.glb"
FIST_SCALE = {"jk-punch": ("jakb-attack-punch", "jakb-attack-punch-end")}
FIST_JOINTS = {"rthumA": "RthumbA", "rthumB": "RthumbB", "rmidA": "RmiddleA", "rmidB": "RmiddleB",
               "lthumA": "LthumbA", "lthumB": "LthumbB", "lmidA": "LmiddleA", "lmidB": "LmiddleB"}
# Jak's clips whose body and arms hers are put back on (round 61, `match_jak`): the studio's punch
# kept Jak's swing of his torso but not its start (his shoulders turned back 90 degrees), and ended
# turned 90 degrees too far, her fist out to her side
MATCH_JAK = {"jk-punch": ("jakb-attack-punch", "jakb-attack-punch-end")}
# Jak's joints, hers: hips' and shoulders' lines, arms (shoulder, elbow, wrist)
JAK_ARM = {"L": ("Larm", "Lforarm", "sk_lhand"), "R": ("Rarm", "Rforarm", "sk_rhand")}


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


def fist_scale(pose: Pose, channels, clips):
    """Jak's hand and finger scale keys of his clips CLIPS (the extraction's, chained as `chain` chains
    the studio's: the next one 1/30 s after the last one's end) on her joints (FIST_JOINTS), at the
    clip's own key times."""
    jak = Glb(JAK_RIP)
    names = [n.get("name") for n in jak.json["nodes"]]
    times = max((t for t, _ in channels.values()), key=len)
    spans = []
    offset = 0.0
    for name in clips:
        anim = next(a for a in jak.json["animations"] if a["name"] == name)
        tracks, length = {}, 0.0
        for c in anim["channels"]:
            if c["target"]["path"] != "scale":
                continue
            s = anim["samplers"][c["sampler"]]
            t = jak.accessor(s["input"])[:, 0].astype(float)
            tracks[names[c["target"]["node"]]] = (t, jak.accessor(s["output"]).astype(float))
            length = max(length, float(t[-1]))
        spans.append((offset, tracks))
        offset += length + 1.0 / 30
    for jak_joint, her_joint in FIST_JOINTS.items():
        out = []
        for t in times:
            start, tracks = [sp for sp in spans if sp[0] <= t + 1e-6][-1]
            jt, jv = tracks[jak_joint]
            out.append([np.interp(t - start, jt, jv[:, i]) for i in range(3)])
        channels[(pose.index[her_joint], "scale")] = (times, np.array(out))


def jak_keys(clips):
    """The extraction's Jak and a function from a time to his keys (node, path) along his clips CLIPS,
    chained as `chain` chains the studio's (the next one 1/30 s after the last one's end)."""
    jak = Glb(JAK_RIP)
    spans, offset = [], 0.0
    for name in clips:
        anim = next(a for a in jak.json["animations"] if a["name"] == name)
        tracks, length = {}, 0.0
        for c in anim["channels"]:
            s = anim["samplers"][c["sampler"]]
            t = jak.accessor(s["input"])[:, 0].astype(float)
            tracks[(c["target"]["node"], c["target"]["path"])] = (t, jak.accessor(s["output"]).astype(float))
            length = max(length, float(t[-1]))
        spans.append((offset, keys_of(tracks)))
        offset += length + 1.0 / 30

    def at(t):
        start, keys = [sp for sp in spans if sp[0] <= t + 1e-6][-1]
        return keys(t - start)
    return jak, at


def yaw_of(v):
    """The heading of V across, in degrees (0 ahead, +z; 90 to +x)."""
    return float(np.degrees(np.arctan2(v[0], v[2])))


def match_jak(pose: Pose, channels, clips):
    """Her body and arms put on Jak's along his clips CLIPS (round 61): at each key, her hips turned
    about the up axis to face as his do (the line of their thighs), her chest then as his shoulders,
    and each arm reaching (`arm_ik`) where his does from his shoulder, in the share of his arm's length,
    its elbow pointing as his."""
    jak, jak_at = jak_keys(clips)
    jp = Pose(jak)
    jw0 = jp.world({})
    times = max((t for t, _ in channels.values()), key=len)
    up = np.array([0.0, 1.0, 0.0])

    def jak_line(t, left, right):
        w = jp.world(jak_at(t))
        return yaw_of(w(jp.index[right])[:3, 3] - w(jp.index[left])[:3, 3])

    for joint, (jl, jr), (hl, hr) in (("main", ("Lthigh", "Rthigh"), ("Lthigh", "Rthigh")),
                                      ("chest", ("Larm", "Rarm"), ("Lshoulder", "Rshoulder"))):
        keys_at = keys_of(channels)
        rots = []
        for t in times:
            w = pose.world(keys_at(t))
            mine = yaw_of(w(pose.index[hr])[:3, 3] - w(pose.index[hl])[:3, 3])
            turn = (jak_line(t, jl, jr) - mine + 180.0) % 360.0 - 180.0
            rots.append(axis_angle(up, turn) @ unit_rot(w(pose.index[joint])))
        set_rot(pose, channels, times, joint, rots)
    w0 = pose.world({})
    for side, (js, je, jh) in JAK_ARM.items():
        jak_len = sum(np.linalg.norm(jw0(jp.index[b])[:3, 3] - jw0(jp.index[a])[:3, 3]) for a, b in ((js, je), (je, jh)))
        her = [pose.index[side + n] for n in ("shoulder", "elbow", "hand")]
        her_len = sum(np.linalg.norm(w0(b)[:3, 3] - w0(a)[:3, 3]) for a, b in ((her[0], her[1]), (her[1], her[2])))

        def target_at(t, w, js=js, je=je, jh=jh, scale=her_len / jak_len, sh=her[0]):
            jw = jp.world(jak_at(t))
            s, e, h = (jw(jp.index[n])[:3, 3] for n in (js, je, jh))
            return w(sh)[:3, 3] + (h - s) * scale, e - (s + h) * 0.5
        arm_ik(pose, channels, times, side, target_at)


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
                values = fade_in(values, times, v0[-1], c["target"]["path"] == "rotation")
                channels[key] = (np.append(t0, times + offset), np.vstack([v0, values]))
            elif n == 0:
                channels[key] = (times, values)
        offset += length + 1.0 / 30
    for key, (times, values) in list(channels.items()):
        channels[key] = cut(times, values, start, end)
    return channels


def smooth(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def fade_in(values, times, last, rotation):
    """An animation chained after another starting where it ends: its keys moved from LAST (the
    other's last key) over its first BLEND seconds. Jak's game blends his two halves of a move; read
    one after the other, his kick's right thigh turned 94 degrees in a key (round 56)."""
    out = values.copy()
    if rotation:
        first = values[0] if np.dot(values[0], last) >= 0 else -values[0]
        gap = qmul(last, qinv(first))
        for i, t in enumerate(times):
            out[i] = qmul(qpow(gap, 1.0 - smooth(t / BLEND)), values[i])
    else:
        for i, t in enumerate(times):
            out[i] = values[i] + (last - values[0]) * (1.0 - smooth(t / BLEND))
    return out


def set_rot(pose: Pose, channels, times, name, world_rots):
    """The rotation channel of joint NAME made from its world rotations WORLD_ROTS (one a time of
    TIMES), its parent's taken from the channels as they are."""
    i = pose.index[name]
    keys_at = keys_of(channels)
    q = [mat_to_quat(unit_rot(pose.world(keys_at(t))(pose.parent[i])).T @ r) for t, r in zip(times, world_rots)]
    channels[(i, "rotation")] = (np.array(times), np.array(q))


def level_head(pose: Pose, channels, times):
    """Her head held as in her idle (HEAD_PITCH down, upright, looking ahead the way she goes), half
    the turn by her neck, half by her head: Jak's head on her looked down, turned and tilted aside
    (and following her hips, it swung left and right as she ran, round 56). The less her chest stands
    up (a roll), the less (none under 20%)."""
    w0 = pose.world({})
    head, neck, chest = (pose.index[n] for n in ("head", "neck", "chest"))
    target = axis_angle([1.0, 0.0, 0.0], -HEAD_PITCH) @ unit_rot(w0(head))
    chest_up = unit_rot(w0(chest)).T @ np.array([0.0, 1.0, 0.0])
    keys_at = keys_of(channels)
    necks, heads = [], []
    for t in times:
        w = pose.world(keys_at(t))
        h = unit_rot(w(head))
        weight = smooth(((unit_rot(w(chest)) @ chest_up)[1] - 0.2) / 0.5)
        turn = qpow(mat_to_quat(target @ h.T), weight)
        half = quat_to_mat(qpow(turn, 0.5))
        necks.append(half @ unit_rot(w(neck)))
        heads.append(quat_to_mat(turn) @ h)
    set_rot(pose, channels, times, "neck", necks)
    set_rot(pose, channels, times, "head", heads)


def arm_ik(pose: Pose, channels, times, side, target_at, limb=("shoulder", "elbow", "hand")):
    """Her SIDE ("L" or "R") arm reaching, at each of TIMES, the place TARGET_AT(t, w) gives for her
    wrist (w her world matrices), with its elbow pointing its way (None: the arm as it is): an analytic
    two-joint arm (as make_baron_clips.left_on_grip), her hand turning with her forearm. LIMB names
    another chain of two joints and its end (her leg: thigh, knee, ankle)."""
    sh, el, wr = (pose.index[side + n] for n in limb)
    keys_at = keys_of(channels)
    q_sh, q_el = [], []
    for t in times:
        w = pose.world(keys_at(t))
        s_pos, e_pos, w_pos = w(sh)[:3, 3], w(el)[:3, 3], w(wr)[:3, 3]
        target, pole = target_at(t, w)
        a, b = np.linalg.norm(e_pos - s_pos), np.linalg.norm(w_pos - e_pos)
        reach = target - s_pos
        d = min(max(np.linalg.norm(reach), abs(a - b) + 1e-3), a + b - 1e-3)
        u = reach / np.linalg.norm(reach)
        pole = pole - u * np.dot(pole, u)
        pole /= np.linalg.norm(pole)
        cos_a = (a * a + d * d - b * b) / (2 * a * d)
        new_e = s_pos + u * a * cos_a + pole * a * np.sqrt(max(0.0, 1 - cos_a * cos_a))
        r1 = turn_between(e_pos - s_pos, new_e - s_pos)
        w1 = s_pos + r1 @ (w_pos - s_pos)
        r2 = turn_between(w1 - new_e, s_pos + u * d - new_e)
        sh_w = r1 @ unit_rot(w(sh))
        el_w = r2 @ r1 @ unit_rot(w(el))
        q_sh.append(mat_to_quat(unit_rot(w(pose.parent[sh])).T @ sh_w))
        q_el.append(mat_to_quat(sh_w.T @ el_w))
    channels[(sh, "rotation")] = (np.array(times), np.array(q_sh))
    channels[(el, "rotation")] = (np.array(times), np.array(q_el))


def track(points, t):
    """The value at T along POINTS ((time, value)...), eased from one to the next."""
    for (t0, v0), (t1, v1) in zip(points, points[1:]):
        if t <= t1:
            return v0 + (v1 - v0) * smooth((t - t0) / max(t1 - t0, 1e-6))
    return points[-1][1]


def guard_legs(pose: Pose, channels):
    """Her legs in a fighter's guard (the author's wish, round 56: "as a boxer's guard"): her feet
    BOX_WIDE times her hips' width apart, her left foot BOX_STEP ahead and her right one behind, her hips lowered
    BOX_BEND of her leg's length (her knees bent, pointing ahead), her feet flat, her back one turned
    30 degrees out. Her hips stay as the channels have them; two-joint legs (`arm_ik`)."""
    w0 = pose.world({})
    hips = pose.index["hips"]
    times = max((t for t, _ in channels.values()), key=len)
    X, Y, Z = np.eye(3)
    for side, sgn, step, toe in (("L", 1.0, BOX_STEP, 10.0), ("R", -1.0, -BOX_STEP, -30.0)):
        thigh, ankle = pose.index[side + "thigh"], pose.index[side + "ankle"]
        drop = (w0(thigh)[1, 3] - w0(ankle)[1, 3]) * (1.0 - BOX_BEND)
        half = abs(w0(thigh)[0, 3] - w0(hips)[0, 3]) * BOX_WIDE

        def target_at(t, w, sgn=sgn, step=step, drop=drop, half=half, thigh=thigh):
            c = w(hips)[:3, 3]
            return c + sgn * half * X + step * Z + (w(thigh)[1, 3] - drop - c[1]) * Y, 0.25 * sgn * X + Z
        arm_ik(pose, channels, times, side, target_at, ("thigh", "knee", "ankle"))
        flat = axis_angle([0.0, 1.0, 0.0], toe) @ unit_rot(w0(ankle))
        set_rot(pose, channels, times, side + "ankle", [flat] * len(times))


def make_throw(pose: Pose, channels):
    """Her grenade throw on Jak's gun stance (its first key held THROW_TIME s, knees bent), the
    author's wish (round 56): her left hand to the pocket on her left hip, the grenade brought up
    before her chest where her right hand (her pistol in it) pulls the pin, her chest turned and her
    arm back and up, then over her shoulder and down across her, her chest leaning into it, and back
    to her stance. Body directions: her left +x, up +y, forward +z (the rest pose's)."""
    times = np.round(np.arange(0.0, THROW_TIME + 1e-6, 1.0 / 30), 4)
    for k, (ts, v) in list(channels.items()):
        channels[k] = (times, np.repeat(v[:1], len(times), axis=0))
    guard_legs(pose, channels)
    keys_at = keys_of(channels)
    chest = pose.index["chest"]
    # her chest: turned (her left shoulder back) to wind up, then the other way and leaning forward
    yaw = [(0.0, 0.0), (0.25, 10.0), (0.6, 5.0), (0.8, 35.0), (0.98, -25.0), (1.12, -20.0), (THROW_TIME, 0.0)]
    lean = [(0.0, 0.0), (0.25, 8.0), (0.6, 4.0), (0.8, -8.0), (0.98, 18.0), (1.12, 15.0), (THROW_TIME, 0.0)]
    rots = []
    for t in times:
        r = unit_rot(pose.world(keys_at(t))(chest))
        rots.append(axis_angle([0.0, 1.0, 0.0], track(yaw, t)) @ axis_angle([1.0, 0.0, 0.0], track(lean, t)) @ r)
    set_rot(pose, channels, times, "chest", rots)
    X, Y, Z = np.eye(3)

    def body(w):
        """Her chest's turn from its rest: body directions to the world's."""
        return unit_rot(w(chest)) @ unit_rot(pose.world({})(chest)).T

    def left_at(t, w):
        b = body(w)
        sh = w(pose.index["Lshoulder"])[:3, 3]
        hip = w(pose.index["Lthigh"])[:3, 3]
        rest = w(pose.index["Lhand"])[:3, 3]
        rest_pole = w(pose.index["Lelbow"])[:3, 3] - (sh + rest) / 2
        places = [  # (time, wrist, elbow's way)
            (0.0, rest, rest_pole),
            (0.22, hip + 0.13 * X - 0.06 * Z + 0.02 * Y, X - Z),                    # in her pocket
            (0.32, hip + 0.13 * X - 0.04 * Z + 0.06 * Y, X - Z),
            (0.52, sh + b @ (0.26 * Z - 0.22 * Y - 0.12 * X), b @ (X - Y)),         # before her chest
            (0.66, sh + b @ (0.28 * Z - 0.20 * Y - 0.12 * X), b @ (X - Y)),
            (0.82, sh + b @ (-0.32 * Z + 0.30 * Y + 0.10 * X), b @ (X - Z - 0.3 * Y)),  # back and up
            (0.96, sh + b @ (0.40 * Z + 0.30 * Y - 0.05 * X), b @ (X + Y)),          # over her shoulder
            (1.12, sh + b @ (0.38 * Z - 0.35 * Y - 0.30 * X), b @ (X - Y)),          # down across her
            (THROW_TIME, rest, rest_pole),
        ]
        return track([(p[0], p[1]) for p in places], t), track([(p[0], p[2]) for p in places], t)

    def right_at(t, w):
        b = body(w)
        sh = w(pose.index["Rshoulder"])[:3, 3]
        lsh = w(pose.index["Lshoulder"])[:3, 3]
        rest = w(pose.index["Rhand"])[:3, 3]
        rest_pole = w(pose.index["Relbow"])[:3, 3] - (sh + rest) / 2
        pin = lsh + b @ (0.30 * Z - 0.16 * Y - 0.20 * X)  # beside the grenade before her chest
        places = [
            (0.0, rest, rest_pole), (0.40, rest, rest_pole),
            (0.55, pin, b @ (-X - Y)), (0.60, pin, b @ (-X - Y)),
            (0.72, sh + b @ (0.30 * Z - 0.10 * Y - 0.20 * X), b @ (-X - Y)),     # the pin pulled out
            (0.95, rest, rest_pole), (THROW_TIME, rest, rest_pole),
        ]
        return track([(p[0], p[1]) for p in places], t), track([(p[0], p[2]) for p in places], t)

    arm_ik(pose, channels, times, "L", left_at)
    arm_ik(pose, channels, times, "R", right_at)


def hold_stance(pose: Pose, channels, stance):
    """Her hips and legs held all along as at STANCE's first key (channels of another animation): her
    hips' place and their facing in the world, her legs' joints as they are there."""
    times = max((t for t, _ in channels.values()), key=len)
    first = {k: v[0] for k, (t, v) in stance.items()}
    hips = pose.index["hips"]
    hips_world = unit_rot(pose.world(first)(hips))
    for name in ("Lthigh", "Lknee", "Lankle", "Lball", "Rthigh", "Rknee", "Rankle", "Rball"):
        k = (pose.index[name], "rotation")
        if k in first:
            channels[k] = (times, np.repeat(first[k][None], len(times), axis=0))
    if (hips, "translation") in first:
        channels[(hips, "translation")] = (times, np.repeat(first[(hips, "translation")][None], len(times), axis=0))
    set_rot(pose, channels, times, "hips", [hips_world] * len(times))


def make_reload(pose: Pose, down, up):
    """Her reload, one pistol then the other (the author's wish, round 56): her own lowering of her
    pistols (DOWN), RELOAD_HOLD s of her magazines, her own raising of them (UP). Her right pistol
    comes before her chest while her left hand takes a magazine at the pouch on her left hip and
    pushes it up into its grip; then her left pistol, her right hand's magazine from her right hip.
    The magazines are full at the lowering's end plus 0.9 s (battlefront-ashelin.gc
    BF_ASH_RELOAD_AT). Body directions as in make_throw."""
    span_d = max(float(t[-1]) for t, _ in down.values())
    span_u = max(float(t[-1]) for t, _ in up.values())
    total = span_d + RELOAD_HOLD + span_u
    times = np.round(np.arange(0.0, total + 1e-6, 1.0 / 30), 4)
    at_d, at_u = keys_of(down), keys_of(up)
    channels = {}
    for k in down:
        if k not in up:
            continue
        vals = []
        for t in times:
            if t <= span_d + RELOAD_HOLD:
                vals.append(at_d(min(t, span_d))[k])
            else:
                vals.append(at_u(t - span_d - RELOAD_HOLD)[k])
        channels[k] = (times, np.array(vals))
    t0 = span_d
    X, Y, Z = np.eye(3)

    def spots(w):
        """Her hands' places, in her heading's directions (her chest leans and turns in her waiting
        pose: places taken in its frame put her forearms through her chest, round 56), from the
        middle of her shoulders: her arms reach 0.93 m, her chest stands out about 0.3 m ahead."""
        lsh, rsh = w(pose.index["Lshoulder"])[:3, 3], w(pose.index["Rshoulder"])[:3, 3]
        mid = (lsh + rsh) / 2
        r_up = mid + 0.50 * Z - 0.30 * Y - 0.10 * X       # her right pistol before her chest
        l_up = mid + 0.50 * Z - 0.30 * Y + 0.10 * X
        return {
            "r_up": (r_up, -X - Y), "l_up": (l_up, X - Y),
            "l_pouch": (w(pose.index["Lthigh"])[:3, 3] + 0.20 * X, X - 0.6 * Z),   # outside her hip
            "r_pouch": (w(pose.index["Rthigh"])[:3, 3] - 0.20 * X, -X - 0.6 * Z),
            "under_r": (r_up - 0.14 * Y + 0.03 * X, X - Y + 0.3 * Z),   # her left hand under its grip
            "under_l": (l_up - 0.14 * Y - 0.03 * X, -X - Y + 0.3 * Z),
        }

    def arm(side, plan):
        hand, sh, el = (pose.index[side + n] for n in ("hand", "shoulder", "elbow"))

        def target_at(t, w):
            rest = w(hand)[:3, 3]
            rest_pole = w(el)[:3, 3] - (w(sh)[:3, 3] + rest) / 2
            at = spots(w)
            pts = [(0.0, rest, rest_pole)] + [(t0 + dt, *(at[n] if n else (rest, rest_pole))) for dt, n in plan]                 + [(total, rest, rest_pole)]
            return track([(q[0], q[1]) for q in pts], t), track([(q[0], q[2]) for q in pts], t)
        return target_at

    # (seconds after the lowering, spot; None her own arm)
    right = [(0.0, None), (0.15, "r_up"), (0.55, "r_up"), (0.68, "r_pouch"), (0.74, "r_pouch"),
             (0.88, "under_l"), (0.93, "under_l"), (1.05, None)]
    left = [(0.0, None), (0.12, "l_pouch"), (0.24, "l_pouch"), (0.40, "under_r"), (0.46, "under_r"),
            (0.58, None), (0.66, "l_up"), (0.98, "l_up"), (1.1, None)]
    arm_ik(pose, channels, times, "R", arm("R", right))
    arm_ik(pose, channels, times, "L", arm("L", left))
    print(f"  jk-reload: lowered by {t0:.2f} s, full at {t0 + 0.9:.2f} s, {total:.2f} s in all")
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
        if game == "jk-reload":
            channels = make_reload(pose, chain(src, by_name, studios[:1], 0.0, None),
                                   chain(src, by_name, studios[1:], 0.0, None))
        else:
            channels = chain(src, by_name, studios, start, end)
        if game == "jk-throw":
            make_throw(pose, channels)
        if game in LEG_TUCK:
            studio, at, legs = LEG_TUCK[game]
            held = keys_of(chain(src, by_name, [studio], 0.0, None))(at)
            times = max((t for t, _ in channels.values()), key=len)
            for name in legs:
                k = (pose.index[name], "rotation")
                if k in held:
                    channels[k] = (times, np.repeat(held[k][None], len(times), axis=0))
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
        if game in MATCH_JAK:
            match_jak(pose, channels, MATCH_JAK[game])
        if game in LEVEL_HEAD:
            level_head(pose, channels, all_times)
        if game in FIST_SCALE:
            fist_scale(pose, channels, FIST_SCALE[game])
        if loop:
            g = ground_per_second(pose, keys_at, all_times)
            drift = side_drift(pose, keys_at, all_times)
            print(f"  {game}: its feet cover {g:.2f} m a second at rate 1, the body going {drift}")
        samplers, chans = [], []
        for (nd, path), (times, values) in channels.items():
            name = nodes[nd]["name"]
            # her fingers' scale is kept (her fist growing, FIST_SCALE): mod_models sets their rotation alone
            if name in SKIP and not (path == "scale" and game in FIST_SCALE and name in FIST_JOINTS.values()):
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
