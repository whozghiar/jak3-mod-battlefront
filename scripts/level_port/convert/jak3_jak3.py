"""Jak 3 -> Jak 3: a port of Jak 3's own levels into a custom level of Jak 3 (the Battlefront mod's
Spargus). The layouts are the same: what jak2_jak3 translates is kept as it is, Jak 2's names
aside. Such a port ports no actor, script, particle or region, so only the tables the steps read
anyway are given.
"""

from .jak2_jak3 import (ABSENT_FOCUS, DROPPED_CALLS, ELEVATOR_FLAGS,  # noqa: F401
                        KEPT_CONTINUE_FLAGS, KEPT_OTHER_EVENTS, KEPT_QUERIES, KEPT_SELF_EVENTS,
                        SKIPPED_CONTINUE_FLAGS, SKIPPED_CONTINUE_NAMES, TARGET_CALLBACKS,
                        TARGET_TPAGES, ocean_map_forms, top_level_forms)

SOURCE = "jak3"
TARGET = "jak3"

# no class to translate: the port bakes the props into the background and ports no door
DOOR_ETYPES = {}
ART_GROUPS = {}
WARP_GATE_ETYPES = {}
CRATES = {}
PICKUPS = {n: n for n in range(64)}
# the particles' flags and pages are the same game's
GROUP_FLAGS = {}
ITEM_FLAGS = {}
STATIC_GROUP_FLAG = "sp8"
CPUINFO_FLAGS = {}
TPAGE_EQUIVALENTS = {}
