#!/usr/bin/env python3
"""
The Baron's clips for the Battlefront mod (rounds 44 and 45): from his Jak Animation Studio creation
(Jak 2's baron-highres model with the Mixamo motions the studio put on it, apply_mocap at 30 keys a
second), keep the animations alone, renamed and in the game's order, in
custom_assets/jak3/models/bf-baron-clips.glb. The file holds the joints' names and their keys, no
mesh, skin, texture nor rest pose of the game: at install, mod_models.py puts the clips on the model
it rips from the player's Jak 2 disc ("clip_file" in custom_assets/jak3/models/models.jsonc). A
translation that never moves (a bone's length) is left out, as are scales of 1: mod_models gives the
joint its rest value.

    python scripts/battlefront/make_baron_clips.py <creation .glb>

Each clip is cut to the part the game plays (an attack from its wind-up to its follow-through), and
a looping clip (idle, run, walk) closed: none of the captures ends on its first pose (the run 34
degrees off at a thigh, two or three keys' worth), so the game's loop jumped there once a cycle (the
author's report, round 45). The gap between the pose a clip would reach one key after its last and
its first pose is spread over the clip, a share a key, and that first pose is added as its last key.

The capture's root goes on `main`: the studio puts the Mixamo hips' travel on the `hips` joint, whose
sibling under `main` is the upper body (`chest`): his legs went up and down under a still torso, and
in his death they folded up under a torso left standing (`move_root`).

His sword in his right hand, his scabbard at his left hip: the model's sword is sheathed (its hilt on
the `sword` joint, its scabbard on `swordA` and `swordB`), and no capture moves it. Each key of each
clip moves the hilt (and the blade mod_models makes on that joint) rigidly into his right fist: the
grip (the hilt's handles) at the middle of the fist, the blade out of the fist on the index finger's
side, the guard turned with the fingers. Only the `sword` joint is keyed: the scabbard keeps its rest
place on him. The studio leaves the fingers at rest: both hands' are closed (`FIST`), each joint
turned toward the palm in its parent's frame, the right one around the grip. His hands stay 0.75 m
apart at least in every capture (his shoulders are broader than the capture's): for the two-handed
slash (`TWO_HANDED`) his left arm reaches the grip below his right fist (`left_on_grip`, an
analytic two-joint arm, its bend kept), coming and going over 0.15 and 0.2 s. In his death the sword
leaves his hand as his arm flies up, spins high and comes down to stand planted in his chest once
he lies still (`DEATH_THROW`, the clip held at its last pose to the end).

Round 46: his run's stride is widened (`STRIDE`, `widen_stride`): each leg joint's turn away from
its mean pose over the cycle, times the factor (his thighs and knees; his ankles half as much), and
his body's bounce with them, so that the game plays the run slower for the same speed (it looked
sped up, the author's report). The ground a clip's feet cover a second at rate 1 is measured from
the planted foot (`ground_per_second`) and printed: the game's BF_BARON_RUN_GROUND. His spin in the
air takes his legs from his jump at its top (`LEGS_FROM`).

The clips, in the order the game plays them (battlefront-baron.gc BF_BARON_CLIP_*), each from the
studio's animation of that name.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "modding"))
from mod_models import Glb, Writer  # noqa: E402

FPS = 30
# game clip name, the studio animation (the Mixamo file at 30 keys a second), the seconds kept
# (start, end; None: to its end), and whether it loops
CLIPS = [
    ("idle", "r45 idle", 0.0, None, True),
    ("run", "r45 run a", 0.0, None, True),            # Run With Sword: the one run straight ahead
    ("walk", "r45 walk a", 0.0, None, True),
    ("jump", "r45 jump a", 0.0, None, False),
    ("slash", "r45 slash 1", 0.0, 1.1, False),        # great sword slash: an overhead chop, it strikes 0.57 s in
    ("spin", "r45 spin", 0.0, 1.5, False),            # great sword high spin attack: a turn and a half, strikes 1.07 s in
    ("block", "r45 block a", 0.0, None, False),
    ("cast", "r45 slash 2", 0.1, 1.1, False),        # great sword slash (2): a diagonal cut, high on his right down to his left, 0.68 s in
    ("hit", "r45 hit", 0.0, None, False),
    ("death", "r45 death", 0.0, None, False),
    ("turn180", "r45 turn180 a", 0.0, None, False),   # great sword 180 turn: a reversal, 175 degrees
    ("plant", "r46 jump attack", 0.55, None, False),  # great sword jump attack: sword raised in the air, slammed down 0.65 s in
    ("airspin", "r45 spin", 0.0, 1.15, False),        # the spin's first full turn, his legs from his jump (LEGS_FROM)
]
# great sword jump attack.fbx goes through Blender first (imported, exported again as it is): the
# studio's FBX loader refuses the Mixamo file ("Unknown property type").

OUT = Path(__file__).resolve().parents[2] / "custom_assets" / "jak3" / "models" / "bf-baron-clips.glb"

# the sheathed sword in the model's rest pose (its mesh, measured): the middle of the hilt's
# handles and the scabbard's tip, which the blade points to
GRIP_REST = np.array([0.79, 2.09, 0.62])
TIP_REST = np.array([0.47, 0.65, -1.36])
# the fists: each finger joint turned toward the palm by these degrees (A at the knuckle)
FINGERS = {"index": (70, 85, 55), "middle": (75, 85, 55), "ring": (75, 85, 55), "pinky": (80, 85, 55),
           "thumb": (20, 35, 30)}
FIST = {side + finger: angles for side in "RL" for finger, angles in FINGERS.items()}
# the clips his left hand grips the sword in too, and where along the grip from the right fist's
# place (GRIP_REST) toward the pommel, in meters
TWO_HANDED = {"slash", "cast", "plant"}
LEFT_GRIP = -0.24
# his death: the sword leaves his hand at RELEASE s, lands planted in his chest at LAND s, the clip
# held to END s; its fall's gravity (m/s2), its turns in the air, how deep it stands in him (the
# point of the blade, along it, that sits at his chest joint: the blade ends 2.62 m from the grip)
DEATH_THROW = {"release": 1.35, "land": 2.75, "end": 3.4, "gravity": 20.0, "turns": 2, "depth": 2.2}
# the clips whose stride is widened, and by how much (round 46)
STRIDE = {"run": 1.6}
LEG_JOINTS = {"Lthigh": 1.0, "Lknee": 1.0, "Lankle": 0.5, "Rthigh": 1.0, "Rknee": 1.0, "Rankle": 0.5}
# the clips whose leg joints are held at another clip's pose: (that studio animation, its time)
LEGS_FROM = {"airspin": ("r45 jump a", 0.3)}


def quat_to_mat(q):
    x, y, z, w = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def mat_to_quat(m):
    t = np.trace(m)
    if t > 0:
        s = np.sqrt(t + 1.0) * 2
        q = [(m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s, 0.25 * s]
    elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = np.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2]) * 2
        q = [0.25 * s, (m[0, 1] + m[1, 0]) / s, (m[0, 2] + m[2, 0]) / s, (m[2, 1] - m[1, 2]) / s]
    elif m[1, 1] > m[2, 2]:
        s = np.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2]) * 2
        q = [(m[0, 1] + m[1, 0]) / s, 0.25 * s, (m[1, 2] + m[2, 1]) / s, (m[0, 2] - m[2, 0]) / s]
    else:
        s = np.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1]) * 2
        q = [(m[0, 2] + m[2, 0]) / s, (m[1, 2] + m[2, 1]) / s, 0.25 * s, (m[1, 0] - m[0, 1]) / s]
    q = np.array(q)
    return q / np.linalg.norm(q)


def axis_angle(axis, degrees):
    """The rotation matrix of DEGREES about unit AXIS."""
    a = np.radians(degrees)
    x, y, z = axis
    c, s, k = np.cos(a), np.sin(a), 1 - np.cos(a)
    return np.array([[c + x * x * k, x * y * k - z * s, x * z * k + y * s],
                     [y * x * k + z * s, c + y * y * k, y * z * k - x * s],
                     [z * x * k - y * s, z * y * k + x * s, c + z * z * k]])


def qmul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return np.array([aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
                     aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz])


def qinv(q):
    return np.array([-q[0], -q[1], -q[2], q[3]])


def qpow(q, f):
    """Q raised to F: its angle times F about its axis."""
    q = q if q[3] >= 0 else -q
    angle = 2 * np.arccos(min(1.0, q[3]))
    if angle < 1e-6:
        return np.array([0.0, 0.0, 0.0, 1.0])
    axis = q[:3] / np.sin(angle / 2)
    h = angle * f / 2
    return np.concatenate([axis * np.sin(h), [np.cos(h)]])


def frame(direction, up):
    """A rotation whose x axis is DIRECTION and y axis UP made perpendicular to it."""
    x = direction / np.linalg.norm(direction)
    y = up - x * np.dot(up, x)
    y /= np.linalg.norm(y)
    return np.column_stack([x, y, np.cross(x, y)])


class Pose:
    """The creation's skeleton: rest matrices, parents, and world matrices from a clip's keys."""

    def __init__(self, src: Glb):
        self.nodes = src.json["nodes"]
        self.parent = {c: i for i, n in enumerate(self.nodes) for c in n.get("children", [])}
        self.index = {n.get("name"): i for i, n in enumerate(self.nodes)}

    def rest(self, i):
        n = self.nodes[i]
        if "matrix" in n:
            return np.array(n["matrix"], dtype=float).reshape(4, 4).T
        m = np.eye(4)
        m[:3, :3] = quat_to_mat(n.get("rotation", [0, 0, 0, 1]))
        m[:3, 3] = n.get("translation", [0, 0, 0])
        return m

    def world(self, keys):
        """KEYS: (node, path) -> value. A function from a node to its world matrix."""
        cache = {}

        def local(i):
            m = self.rest(i)
            if (i, "rotation") in keys:
                m[:3, :3] = quat_to_mat(keys[(i, "rotation")])
            if (i, "translation") in keys:
                m[:3, 3] = keys[(i, "translation")]
            return m

        def get(i):
            if i not in cache:
                cache[i] = get(self.parent[i]) @ local(i) if i in self.parent else local(i)
            return cache[i]
        return get


def cut(times, values, start, end):
    """The keys from START to END (seconds), their times from 0."""
    keep = (times >= start - 1e-4) & (times <= (end if end is not None else 1e9) + 1e-4)
    if keep.sum() < 2:
        keep[:2] = True
    return times[keep] - times[keep][0], values[keep]


def close_loop(times, values, rotation):
    """A loop's keys, closed: the gap between the pose one key after the last (the last step
    repeated) and the first spread over the keys, and the first pose added after the last."""
    if len(values) < 3:
        return times, values
    if rotation:
        values = np.array([v if np.dot(v, values[0]) >= 0 else -v for v in values])
        step = qmul(values[-1], qmul(qinv(values[-2]), values[-1]))
        gap = qmul(qinv(step), values[0])
        n = len(values)
        out = np.array([qmul(v, qpow(gap, k / n)) for k, v in enumerate(values)])
        out = np.vstack([out, values[0]])
    else:
        step = values[-1] + (values[-1] - values[-2])
        gap = values[0] - step
        n = len(values)
        out = np.vstack([values + gap * (np.arange(n)[:, None] / n), values[0]])
    return np.append(times, times[-1] + 1.0 / FPS), out


def fist_rotations(pose: Pose):
    """Each finger joint's local rotation closed into a fist, from the rest pose: about the axis across
    its bone and its palm's normal, expressed in its parent's frame."""
    w = pose.world({})
    palms = {}
    for side in "RL":
        p = {n: w(pose.index[side + n])[:3, 3] for n in ("hand", "indexA", "pinkyA", "middleA")}
        palm = np.cross(p["indexA"] - p["pinkyA"], p["middleA"] - p["hand"])
        palm /= np.linalg.norm(palm)
        # the palm's side: the one the rest pose's fingers already bend toward
        mid = [w(pose.index[f"{side}middle{c}"])[:3, 3] for c in "ABC"]
        bend = (mid[2] - mid[1]) - (mid[1] - mid[0])
        palms[side] = palm if np.dot(bend, palm) >= 0 else -palm
    out = {}
    for finger, angles in FIST.items():
        palm = palms[finger[0]]
        for k, c in enumerate("ABC"):
            name = f"{finger}{c}"
            i = pose.index[name]
            child = f"{finger}{'ABC'[k + 1]}" if k < 2 else None
            head = w(i)[:3, 3]
            tail = w(pose.index[child])[:3, 3] if child else head + (head - w(pose.index[f"{finger}{'ABC'[k - 1]}"])[:3, 3])
            bone = (tail - head) / np.linalg.norm(tail - head)
            axis = np.cross(bone, palm)
            axis /= np.linalg.norm(axis)
            parent_rot = w(pose.parent[i])[:3, :3]
            parent_rot = parent_rot / np.linalg.norm(parent_rot, axis=0)
            local_axis = parent_rot.T @ axis
            rest_local = pose.rest(i)[:3, :3]
            rest_local = rest_local / np.linalg.norm(rest_local, axis=0)
            out[name] = mat_to_quat(axis_angle(local_axis, angles[k]) @ rest_local)
    return out


GROUP_REST = frame(TIP_REST - GRIP_REST, np.array([0.0, 1.0, 0.0]))
BLADE_REST = (TIP_REST - GRIP_REST) / np.linalg.norm(TIP_REST - GRIP_REST)


def fist_center(pose: Pose, w, side):
    names = [f"{side}hand", f"{side}indexA", f"{side}middleA", f"{side}ringA", f"{side}pinkyA"]
    return np.mean([w(pose.index[n])[:3, 3] for n in names], axis=0)


def hand_move(pose: Pose, w):
    """The rigid move that puts the sheathed sword (rest) into the right fist of the world W."""
    pos = {n: w(pose.index[n])[:3, 3] for n in ("Rhand", "RindexA", "RmiddleA", "RpinkyA")}
    hand = frame(pos["RindexA"] - pos["RpinkyA"], pos["RmiddleA"] - pos["Rhand"])
    rot = hand @ GROUP_REST.T
    move = np.eye(4)
    move[:3, :3] = rot
    move[:3, 3] = fist_center(pose, w, "R") - rot @ GRIP_REST
    return move


def slerp(q0, q1, f):
    if np.dot(q0, q1) < 0:
        q1 = -q1
    return qmul(q0, qpow(qmul(qinv(q0), q1), f))


def death_move(pose: Pose, keys_at, t, end_t):
    """The sword's move at T of his death (`DEATH_THROW`): in his fist until the release, then
    thrown: a fall under the throw's gravity, turning, to stand planted, blade down, its point in his
    chest as he lies at END_T."""
    d = DEATH_THROW
    if t <= d["release"]:
        return hand_move(pose, pose.world(keys_at(t)))
    start = hand_move(pose, pose.world(keys_at(d["release"])))
    last = pose.world(keys_at(end_t))
    chest = last(pose.index["chest"])[:3, 3]
    down = np.array([0.0, -1.0, 0.0])
    r1 = frame(down, np.array([0.0, 0.0, 1.0])) @ GROUP_REST.T
    g1 = chest - d["depth"] * down
    g0 = start[:3, :3] @ GRIP_REST + start[:3, 3]
    span = d["land"] - d["release"]
    f = min(1.0, (t - d["release"]) / span)
    gravity = np.array([0.0, -d["gravity"], 0.0])
    v0 = (g1 - g0 - 0.5 * gravity * span * span) / span
    tt = f * span
    grip = g0 + v0 * tt + 0.5 * gravity * tt * tt
    across = np.array([v0[0], 0.0, v0[2]])
    axis = np.cross(across, np.array([0.0, 1.0, 0.0])) if np.linalg.norm(across) > 1e-3 else np.array([1.0, 0.0, 0.0])
    axis /= np.linalg.norm(axis)
    q = slerp(mat_to_quat(start[:3, :3]), mat_to_quat(r1), f)
    rot = axis_angle(axis, 360.0 * d["turns"] * f) @ quat_to_mat(q)
    move = np.eye(4)
    move[:3, :3] = rot
    move[:3, 3] = grip - rot @ GRIP_REST
    return move


def sword_keys(pose: Pose, keys_at, times, death=False):
    """The `sword` joint's local translations and rotations at TIMES, the hilt moved into the right
    fist (see the docstring at the top), or with DEATH thrown and planted (`death_move`). KEYS_AT: a
    time -> that time's keys."""
    rest_world = pose.world({})
    trans, rots = [], []
    i = pose.index["sword"]
    for t in times:
        w = pose.world(keys_at(t))
        move = death_move(pose, keys_at, t, times[-1]) if death else hand_move(pose, w)
        local = np.linalg.inv(w(pose.parent[i])) @ (move @ rest_world(i))
        trans.append(local[:3, 3])
        rots.append(mat_to_quat(local[:3, :3]))
    return np.array(trans), np.array(rots)


def unit_rot(m):
    r = m[:3, :3]
    return r / np.linalg.norm(r, axis=0)


def turn_between(a, b):
    """The rotation matrix turning direction A onto direction B."""
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    axis = np.cross(a, b)
    sin = np.linalg.norm(axis)
    if sin < 1e-8:
        return np.eye(3)
    return axis_angle(axis / sin, np.degrees(np.arctan2(sin, np.dot(a, b))))


def left_on_grip(pose: Pose, channels, keys_at, times):
    """The two-handed grip: his left wrist moved, at each of TIMES, so that his left fist sits on the
    sword's grip LEFT_GRIP m from his right fist toward the pommel, coming in over the first 0.15 s and
    letting go over the last 0.2 s; his upper arm and forearm turned in the plane of their bend (an
    analytic two-joint arm), his hand with his forearm. Writes the `Lshoulder` and `Lelbow` rotation
    channels."""
    sh, el, wr = pose.index["Lshoulder"], pose.index["Lelbow"], pose.index["Lhand"]
    end = times[-1]
    q_sh, q_el = [], []
    for t in times:
        w = pose.world(keys_at(t))
        move = hand_move(pose, w)
        on_grip = move[:3, :3] @ (GRIP_REST + LEFT_GRIP * BLADE_REST) + move[:3, 3]
        s_pos, e_pos, w_pos = w(sh)[:3, 3], w(el)[:3, 3], w(wr)[:3, 3]
        target = on_grip - (fist_center(pose, w, "L") - w_pos)
        weight = min(1.0, t / 0.15, max(0.0, (end - t) / 0.2))
        weight = weight * weight * (3 - 2 * weight)
        target = w_pos + weight * (target - w_pos)
        a, b = np.linalg.norm(e_pos - s_pos), np.linalg.norm(w_pos - e_pos)
        reach = target - s_pos
        d = min(max(np.linalg.norm(reach), abs(a - b) + 1e-3), a + b - 1e-3)
        u = reach / np.linalg.norm(reach)
        pole = (e_pos - s_pos) - u * np.dot(e_pos - s_pos, u)
        pole = pole / np.linalg.norm(pole) if np.linalg.norm(pole) > 1e-6 else np.cross(u, [0.0, 1.0, 0.0])
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


def move_root(pose: Pose, channels):
    """The capture's travel of the hips onto `main`, the hips at their rest place on it: the whole body
    follows (see the docstring at the top)."""
    hips, main = pose.index["hips"], pose.index["main"]
    if (hips, "translation") not in channels:
        return
    times, values = channels.pop((hips, "translation"))
    rest_h = pose.rest(hips)[:3, 3]
    rest_m = pose.rest(main)
    moved = rest_m[:3, 3] + (unit_rot(rest_m) @ (values - rest_h).T).T
    channels[(main, "translation")] = (times, moved)


def widen_stride(pose: Pose, channels, k):
    """The run's stride K times as wide: each joint of LEG_JOINTS turned away from its mean pose over
    the clip K times as far (an ankle 1 + (K - 1) / 2), and `main`'s height away from its mean as
    well (the body's bounce). A closed loop stays closed: its first and last keys move alike."""
    for name, share in LEG_JOINTS.items():
        key = (pose.index[name], "rotation")
        if key not in channels:
            continue
        times, q = channels[key]
        q = np.array([v if np.dot(v, q[0]) >= 0 else -v for v in q])
        mean = q.mean(0)
        mean /= np.linalg.norm(mean)
        f = 1.0 + (k - 1.0) * share
        channels[key] = (times, np.array([qmul(mean, qpow(qmul(qinv(mean), v), f)) for v in q]))
    key = (pose.index["main"], "translation")
    if key in channels:
        times, v = channels[key]
        # the world's up in main's parent frame
        up = unit_rot(pose.world({})(pose.parent[pose.index["main"]])).T @ np.array([0.0, 1.0, 0.0])
        h = v @ up
        channels[key] = (times, v + np.outer((h - h.mean()) * (k - 1.0), up))


def hold_legs(pose: Pose, channels, src: Glb, studio: str, at: float):
    """The leg joints (LEG_JOINTS) held, over the whole clip, at their pose AT s into the studio's
    animation STUDIO."""
    anim = [a for a in src.json["animations"] if a.get("name") == studio][0]
    for c in anim["channels"]:
        nd, path = c["target"]["node"], c["target"]["path"]
        if path != "rotation" or src.json["nodes"][nd].get("name") not in LEG_JOINTS:
            continue
        s = anim["samplers"][c["sampler"]]
        times, values = src.accessor(s["input"])[:, 0], src.accessor(s["output"]).astype(float)
        k = max(0, min(int(np.searchsorted(times, at + 1e-6, side="right") - 1), len(values) - 1))
        span = max((ts for ts, _ in channels.values()), key=len)
        channels[(nd, path)] = (np.array([0.0, float(span[-1])]), np.array([values[k], values[k]]))


def ground_per_second(pose: Pose, keys_at, times):
    """The ground a looping clip's feet cover a second at rate 1: the speed at which the lower foot
    goes back under the body while it is down (its ankle within 5 cm of its lowest), the median of
    those frames."""
    speeds = []
    feet = [pose.index["Lankle"], pose.index["Rankle"]]
    pos = []
    for t in times:
        w = pose.world(keys_at(t))
        hips = w(pose.index["hips"])[:3, 3]
        pos.append([w(f)[:3, 3] - np.array([hips[0], 0.0, hips[2]]) for f in feet])
    pos = np.array(pos)
    for f in range(2):
        y = pos[:, f, 1]
        low = y.min() + 0.05
        for i in range(len(times) - 1):
            if y[i] < low and y[i + 1] < low:
                d = pos[i + 1, f] - pos[i, f]
                speeds.append(np.hypot(d[0], d[2]) / (times[i + 1] - times[i]))
    return float(np.median(speeds)) if speeds else 0.0


def main() -> int:
    src = Glb(Path(sys.argv[1]))
    pose = Pose(src)
    nodes = src.json["nodes"]
    by_name = {a.get("name"): a for a in src.json.get("animations", [])}
    missing = [studio for _, studio, *_ in CLIPS if studio not in by_name]
    if missing:
        sys.exit(f"{src.path}: no animation {missing}; it has {sorted(by_name)}")
    fist = fist_rotations(pose)
    out = Writer()
    node_ids: dict[str, int] = {}

    def node(name: str) -> int:
        if name not in node_ids:
            out.json["nodes"].append({"name": name})
            node_ids[name] = len(out.json["nodes"]) - 1
        return node_ids[name]

    for game, studio, start, end, loop in CLIPS:
        anim = by_name[studio]
        channels = {}   # (node, path) -> (times, values), cut and closed
        for c in anim["channels"]:
            s = anim["samplers"][c["sampler"]]
            nd, path = c["target"]["node"], c["target"]["path"]
            times, values = cut(src.accessor(s["input"])[:, 0], src.accessor(s["output"]).astype(float), start, end)
            if loop:
                times, values = close_loop(times, values, path == "rotation")
            channels[(nd, path)] = (times, values)
        move_root(pose, channels)
        if game in LEGS_FROM:
            hold_legs(pose, channels, src, *LEGS_FROM[game])
        death = game == "death"
        if death:
            # held at its last pose to the end of the sword's fall
            for key, (times, values) in list(channels.items()):
                channels[key] = (np.append(times, DEATH_THROW["end"]), np.vstack([values, values[-1]]))

        def keys_at(t, channels=channels):
            out_keys = {}
            for key, (times, values) in channels.items():
                k = max(0, min(int(np.searchsorted(times, t + 1e-6, side="right") - 1), len(values) - 1))
                out_keys[key] = values[k]
            return out_keys

        all_times = max((ts for ts, _ in channels.values()), key=len)
        if death:
            all_times = np.arange(0.0, DEATH_THROW["end"] + 1e-6, 1.0 / FPS)
        if game in TWO_HANDED:
            left_on_grip(pose, channels, keys_at, all_times)
        if loop:
            before = ground_per_second(pose, keys_at, all_times)
            if game in STRIDE:
                widen_stride(pose, channels, STRIDE[game])
            after = ground_per_second(pose, keys_at, all_times)
            print(f"  {game}: its feet cover {before:.2f} m a second at rate 1" +
                  (f", {after:.2f} widened x{STRIDE[game]}" if game in STRIDE else ""))
        samplers, chans = [], []

        def add(name, path, times, values, kind):
            t_acc = out.accessor(np.asarray(times, np.float32).reshape(-1, 1), "SCALAR", 5126, minmax=True)
            samplers.append({"input": t_acc, "output": out.accessor(np.asarray(values, np.float32), kind, 5126),
                             "interpolation": "LINEAR"})
            chans.append({"sampler": len(samplers) - 1, "target": {"node": node(name), "path": path}})

        for (nd, path), (times, values) in channels.items():
            name = nodes[nd]["name"]
            if name in ("sword", "swordA") or name in fist:
                continue
            if path == "translation" and name != "main" and float(np.abs(values - values[0]).max()) < 1e-4:
                continue
            if path == "scale" and float(np.abs(values - 1.0).max()) < 1e-4:
                continue
            kind = "VEC4" if path == "rotation" else "VEC3"
            add(name, path, times, values, kind)
        trans, rots = sword_keys(pose, keys_at, all_times, death)
        add("sword", "translation", all_times, trans, "VEC3")
        add("sword", "rotation", all_times, rots, "VEC4")
        span = [0.0, float(all_times[-1])]
        for name, q in fist.items():
            add(name, "rotation", span, [q, q], "VEC4")
        out.json["animations"].append({"name": game, "samplers": samplers, "channels": chans})
        print(f"  {game:10s} {studio:24s} {all_times[-1]:.2f} s, {len(all_times)} keys{' (loop)' if loop else ''}")
    out.json["scenes"][0]["nodes"] = list(range(len(out.json["nodes"])))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(out.save_bytes())
    print(f"{OUT}: {len(CLIPS)} clips, {len(out.json['nodes'])} joints, {OUT.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
