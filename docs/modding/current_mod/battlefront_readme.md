# Battlefront — Mod Readme

- **Game:** Jak 3
- **Repository:** `whozghiar/jak3-mod-battlefront` (prepared locally as `mods/jak3-mod-battlefront`, not published yet)
- **Status:** In development, no release. Round 14 (2026-11-06: health and damage on one 24 point scale, guard rolls and strafes, smaller magazines and the tazer's recharge, the jetpack's boost, the robotguard's timed shield and ball, the spider's 11 m leap, targeting by side, kill counter, class help with the pad's icons) passed its smoke tests in game, as did round 13 (third-person camera, class page right after the side page, Mods menu on L3 + SELECT) ([`battlefront_tests.md`](battlefront_tests.md)). Earlier rounds were tested by automated runs on 2026-10-31 and 2026-11-01 ([§3.1](#31-what-the-in-game-runs-checked)); the author played the second round once; the rounds since, which answer their notes, are checked by automated runs only.

This is the developer and agent documentation of the mod: what it changes, how it works, how to
test it, its limits, and its change log. Players read the root [`README.md`](../../../README.md).

**Contents:** [1. What the mod does](#1-what-the-mod-does) · [2. Architecture](#2-architecture) · [3. How to test](#3-how-to-test) · [4. Status and known limits](#4-status-and-known-limits) · [5. Change log](#5-change-log)

---

## 1. What the mod does

The mod turns a section of Haven City into a battlefield between the Freedom League and the
Krimzon Guard. Each side has 500 units in stock; every death of a unit or of the player takes one
from its side, and the first side down to 0 loses. The player fights on one side, as any of its
four classes.

| Side | AI units | Playable classes |
|---|---|---|
| Freedom League (French: Ligue de la liberté) | blue guards, blue jetpack guards | Blue Guard, Blue Guard (Jetpack) |
| Krimzon Guard (French: Grenagarde) | red Krimzon Guards, red jetpack guards, robotguards, spider robots | Red Krimzon Guard, Red Krimzon Guard (Jetpack), Robotguard, Spider Robot |

The red Krimzon Guard and the jetpack guard are Jak 2 models brought into Jak 3 (§2.3). Jak himself
was a Freedom League class until the fifth round, the Spargus Citizen until the twelfth; neither is
playable any more.

### Switching it on

Open the Mods menu (**L3 + SELECT**, as every mod, works in a retail boot), then `battlefront` >
**Battlefront mode**: the mode's switch, off at every boot. On, it adds a **Gamemode** entry to
START > Options; off during a battle, it loads the last save (the slot last loaded or saved), or,
with no save since the boot, ends the battle at the side's spawn.

START > Options > Gamemode > Battlefront:

| Entry | Effect |
|---|---|
| New battle | Out of a battle: closes the START menu and opens the battle menu. Grey during a battle. |
| Change class | During a fight: the class page, then the player goes on as the new class; the battle goes on. |
| Restart the battle | During a fight: the same zone, side and class from 500 units each, back at the spawn with fresh ammo. |
| Quit the battle | Ends the battle and restores the stock game. |

The entries that do not apply are grey. The battle menu has three pages, war zone, side, class.
X on the side starts the deployment and opens the class page at once: the classes on the left, and
in a frame on the right the class under the cursor, turning a full circle every 4 seconds, as soon
as the unit levels holding the class models are loaded. The game runs under the page while the
zone loads ("Loading the war zone..."); once Jak stands at his spawn it pauses, and X ("Deploy")
puts him in the battle as that class with fresh ammo. The class page has no Back (the battle has
started). X selects, Circle goes back. The texts are French when the game language is French,
English otherwise.

Every page is drawn on black: the world is not drawn under it. The war zone and side pages show,
in the right frame, the zone under the cursor (or the one picked): its whole district on the
game's own minimap textures (dark gray ground, white streets, blue water), the other districts
black, the Freedom League spawn in blue, the Krimzon Guard spawn in red, and Jak in white when he
is in it. North is up, as on the minimap.

The battlefield is a whole district: every place of its Haven City sections.

| War zone | Sections | Freedom League spawn | Krimzon Guard spawn |
|---|---|---|---|
| Port | `ctyport` | `ctyport-bbush-6` (west docks) | `ctyport-bombbot` (east docks, by the war zone) |
| Industrial Zone | `ctyinda`, `ctyindb` | `ctyindb-start` | `ctyinda-bbush-5` |
| Slums | `ctysluma` | `ctysluma-alley` | `ctysluma-bbush-3` |
| Freedom HQ | `ctyslumb`, `ctyslumc` | `ctyslumc-freehq` | `ctyslumb-bbush-4` |

The spawns are stock continue points at the two ends of each district. A force field holds the
player on foot in the district's sections, and a jetpack class under a ceiling 30 m above the
higher spawn; touching either shows "FORCE FIELD" with Light Jak's shield sparks. The player cannot
get into a vehicle during a battle.

### During a battle

- **Armies:** at most 20 units per side on the street at once. Freedom League: 14 blue guards, 6
  blue jetpack guards. Krimzon Guard: 4 red riflemen, 4 red grenadiers, 4 red jetpack guards, 4
  robotguards, 4 spider robots. A unit standing on the battlefield stays there wherever the camera
  looks (§2.2). No citizen walks or drives in the city during a battle.
- **HUD:** the reserves at the top middle, after the reinforcement meter of Star Wars Battlefront
  (2004): the player's side's bar runs left from the middle in green, the enemy's right in red, each
  as long as its reserve, with both counts under them; the player's kills, small, on the left
  ("Kills: n"); the crosshair in the middle (red when it is on a foe); top right, the stock gun HUD
  showing the weapon in hand (yellow gun 1 for the rifle, blue gun 2 for the tazer, red gun 3 for
  the grenade launcher), under it the guard's own rounds: the rifle's magazine as 10 shells and
  "magazine/carried" (10/20), the grenades as 5 shells and their count, for the tazer no ammo, only
  the seconds left while it recharges, in red (§2.8); Jak's stock health HUD kept shown, its eco
  gauges showing the class's gauge: the jetpack's boost in the dark eco gauge, the spider's blue
  eco in the light eco gauge in blue, the robotguard's shield in the light eco gauge in red
  (draining while it is up, refilling until it can go up again). No weapon name, no class model in
  the ring.
- **Health and damage:** one 24 point scale for every class and unit (§2.8): guards and
  robotguards 24, jetpack guards 18, spider robots 12; a rifle shot takes 8, a grenade's blast 20,
  the tazer 24, a close attack 10 (rifle butt, punch, dive kick), a spider's bite 12, a jetpack's
  shot 6, a robotguard's shot 4. A side's own fire takes nothing from its units or from the player;
  Jak running or jumping into a unit takes nothing from it. Every close attack plays Jak's punch
  sound ("punch-hit").
- **Targeting:** each unit fights the nearest foe and keeps it until one of them dies; the other
  side turns onto the player within 50 m of him; his own side never takes him as a target (§2.8).
  No guard of the battle carries the tazer: a blue guard the squad gives it gets the rifle or the
  grenade launcher instead (by its process id, for good), the red guards the weapon their model
  holds.
- **Outside the campaign:** while a battle runs, no mission or activity can start, no vehicle can
  be taken, and the START menu's Save, Load Game and Secrets are grey and refused (the stock
  refusal beep); a load from elsewhere (or a new game) ends the battle and loads the save normally.
- **Pickups:** a dead unit may leave a stock pickup: yellow ammo (12 %), red ammo (7 %), health
  (6 %) or dark eco (5 %, three pills); 30 % in all, a little more than the 27 % of rounds 12 and
  13. Dark eco is the jetpack's boost: one drop fills its gauge. Jak's light and dark eco are set aside for the battle and given back at its end, and the
  "endless dark eco" and "endless light eco" secrets are off during a battle (they would keep every
  jetpack full and the light eco gauge lit).
- **Death:** the player's side loses a unit; for 4 seconds the camera follows a living unit of his
  side ("YOU WERE KILLED", "Back in 4 ... 1"), then he is back at his side's spawn as the same class,
  with full health, fresh ammo and 2 seconds of invulnerability. The battle's units keep fighting
  meanwhile.
- **End:** a result page (victory or defeat, losses of both sides); X leaves the battle.

### Class controls

The player stays Jak underneath: camera, collision, health and stock moves are Jak's. A class
hides him, draws its own model in his place with its own clips, and changes some moves.

| Class | Moves | R1 | Square | Other |
|---|---|---|---|---|
| Blue Guard / Red Krimzon Guard | 24 points; run speed x0.95; L2 + left stick: roll toward the stick (ahead when it rests), from the ground, a jump 0.8 m high at 11 m/s (3.8 m measured each way), the stock guards' sideways jump clip toward the roll's side, no attack meanwhile, 0.4 s before the next one; R2 held + left stick: strafe at x0.75, facing ahead, the sidestep clip | the weapon in hand, its clip on the upper body while the legs walk or run: rifle shot (8) at the crosshair, one every 0.5 s, 10 to a magazine reloaded from 20 carried (Jak's yellow ammo); tazer strike (24), 12 m, locked by itself on the nearest foe ahead, then 20 s before the next, no ammo and no reload clip (the weapon joint drawn at 0.55: a short baton); grenade (20), lands on the crosshair's point, 35 m away at most, one a second, from the 5 carried (Jak's red ammo). An empty magazine reloads (the stock guards' reload, about 2 s) | rifle butt (10, 4 m), 1.5 s between two | D-pad: left tazer, down rifle, up grenade launcher |
| Blue / Red Jetpack | 18 points; X held climbs (6 m/s measured), slowing into a hover under the ceiling; Circle held comes down (7 m/s); neither holds the height reached, still, for as long as the player likes; R2 held: a boost at 24 m/s toward the left stick (ahead when it rests) while the gauge lasts, 3 s in a full one (18 m in 1 s measured); only dark eco refills it, 6 units for a full gauge; the model floats 0.8 m above the ground | a salvo of two quick shots (6 each) at the crosshair, 0.8 s between salvos; built-in guns, no ammo | dive kick at the foe ahead (22 m/s, 10 on contact within 1 s), 0.6 s between two | |
| Robotguard | 24 points; run speed x0.7; R2: rolls as a ball at x1.6 until R2 again (45 m in 3 s measured), no attack meanwhile | a salvo of two shots (4 each), 0.9 s between salvos; built-in guns, no ammo | punch: wind-up, punch, back (0.9 s), 10 within 6.5 m, 1.5 s between two | Circle: the Dark Makers' shield sphere around it, glowing red, for 5 s, then 25 s before the next one; Jak's shield level stops every attack meanwhile, and the robot walks and jumps behind it (9.5 m in 1.5 s measured), without attacking |
| Spider Robot | 12 points; run speed x1.5; X: a leap 11 m high (11.03 m measured); R2 held: blue eco sprint at x2 while the gauge lasts (10 s), refilled in 10 s | nothing | nothing | Circle: bite, a leap at the nearest foe ahead, 12 within 7 m, 1 s between two |

Aiming is free for every class: the right stick turns the third-person camera (§2.4) and the
camera aims. The shots and grenades go where the crosshair's line of sight (the middle of the
screen) meets the scenery or a unit (80 m at most), and a class turns to face that point while it
fires. Only the tazer aims by itself, at short range; the crosshair then moves onto the foe it
locked. Square attacks and the spider's lunge go for the nearest foe within 70 m and 60 degrees of
the camera's heading. Each attack plays the unit's own clip (guard rifle, tazer and
grenade throw, roboguard punch, spider attack jump, jetpack forward
flight). A close attack (Square, the spider's Circle) plays its clip once, to its end, and the
next one waits for that end, 0.6 s at least (measured clips: blue guard rifle butt 1 s,
red guard rifle butt 0.22 s, robotguard punch 0.93 s, spider bite 0.38 s); a jetpack's dive kick
also waits for the previous one to hit or miss. The jetpacks keep one clip while they fire: their
hover, or above 2.5 m/s (back under 1 m/s) the flight clip toward where they fly against the
camera's heading (forward, right, left or back), never the firing clip. Without
ammo, R1 fires nothing and the HUD shows the count in red. Jak's own gun, melee,
board, Dark Jak and Light Jak are off while a class is played.

---

## 2. Architecture

### 2.1 Files added or changed

| File | Change | Why |
|---|---|---|
| `goal_src/jak3/pc/features/battlefront/battlefront-h.gc` (new, GAME) | Battle state `*bf*`, zone and class tables (English and French), skeleton groups of the Jak 2 models, army caps (no citizens during a battle) and look shares, the pickups dead units leave, every function the stock level code calls, and a wrapper of `effect-control` `do-effect` (no death effect on the mod's build-actor models). | The stock files that call into the mod are level code, linked with CWI, CTYPESA, CTYPESC, DESRESC or WWD; the functions they call must exist whatever is loaded, and answer like the stock game while no battle runs. The wrapper: §2.4. |
| `goal_src/jak3/pc/features/battlefront/battlefront-player.gc` (new, GAME) | `bf-avatar`: the class model drawn in Jak's place, its moves, weapons, salvos, dodges, ammo, gauges and the robotguard's shield (`bf-shield`); `bf-cam-rig`: the third-person camera; `bf-icon`: a class model drawn over the game (class page preview). | See §2.4 and §2.6. |
| `goal_src/jak3/pc/features/battlefront/battlefront.gc` (new, GAME) | `bf-director` (battle life cycle, menu pages, HUD, force field, pickups); the code of Jak's `target-death` state during a fight (`bf-target-death`); wrappers of `target-attacked`, `game-info` `initialize!`, the START menu's ring options, `progress` `set-menu-options` and `game-text-info` `lookup-text!`; the START menu's Gamemode pages; the Mods menu entry. | The director lives in `*pc-pool*` so it outlives level changes and deaths; it owns the battle's settings. |
| `docs/modding/current_mod/battlefront_smoke.gc`, `battlefront_tests.md` (new) | The smoke test scenarios and their notebook (§3). | Never in a build: `smoke_test.py install` copies a scenario into GAME for a run. |
| `goal_src/jak3/pc/features/battlefront/battlefront-minimaps.gc` (new, GAME, generated) | The four war zones' maps: each district's minimap cells, 256 texels on the long side, one palette, their world corners. | The zone pages show each district on the game's own minimap textures, loaded by the game only with their city section (§2.6). |
| `goal_src/jak3/levels/city/battlefront/battlefront-city.gc` (new, CWI) | Attack-controller hatred edits, periodic faction commands, reinforcements on the district's lanes, `bf-keep-unit?`, the player's grenade throw; installs `*bf-city-hook*` and `*bf-city-grenade*`. | These need Haven City's types (the grenade is `vehicle-grenade-deflect`, a lane is a `nav-branch`, a unit a `citizen`), only known in CWI. |
| `goal_src/jak3/engine/ui/hud-classes.gc` | `hud-health`'s `draw` calls `bf-hud-health-gauges` just before it draws its sprites. | During a battle, the class gauge takes one of the stock eco gauges, with its color (§2.6); a no-op otherwise. |
| `goal_src/jak3/levels/city/traffic/traffic-manager.gc` | `traffic-manager-method-22` takes each pool size from `bf-want-count`. | It writes every traffic pool's `want-count` from the faction spawn levels every frame: the army caps must be applied there (§2.2). |
| `game/graphics/opengl_renderer/foreground/Shadow2.cpp`, `Shadow2.h` | A shadow that no longer fits the frame's vertex or index buffers is dropped instead of stopping the game; the buffers are twice as large; the overflow skip loop tests `!=`. | A battle draws dozens of shadow casters: the stock buffers filled and the `alloc_verts` assertion closed the game (seen in the first deployment). Needs `task build-release-game`. |
| `goal_src/jak3/levels/city/traffic/traffic-engine.gc` | `set-process-to-killed` calls `bf-unit-killed`; `activate-one-vehicle` takes the number of units of a type it may wake from `bf-want-count`; the per-frame check of the awake pedestrians keeps a unit when `bf-keep-unit?` (`battlefront-city.gc`) says so. | The first is reached once per real unit death (recycled units never go there): the loss counter. The second replaces the squad controls' count, which starved the Port. The third keeps the units on the district's lanes awake out of the camera's cells (§2.2). |
| `goal_src/jak3/levels/city/traffic/citizen/guard.gc` | `init-enemy!` takes its skeleton from `bf-guard-skel-name`; `crimson-guard-method-267` registers red guards as roboguards and takes its weapon from `bf-guard-weapon`, and method 270 compares the weapon that would give; `citizen-method-215` registers with `bf-attacker-type`; `citizen-method-194` calls `bf-guard-activated`. | Red guards run the stock guard code (§2.2); no guard of a battle carries the tazer (§2.8). |
| `goal_src/jak3/levels/city/protect/flying-turret.gc` | `init-enemy!` takes its skeleton from `bf-turret-skel-name` and its scale from `bf-unit-scale`; `citizen-method-215` registers with `bf-attacker-type`; `enemy-common-post` calls `bf-hover-animate`. | Jetpack guards run the stock flying-turret code (§2.2). |
| `goal_src/jak3/dgos/game.gd` | `battlefront-h.o`, `battlefront-player.o`, `battlefront-minimaps.o`, `battlefront.o` at the end. | After the engine code they use (enemy, guard-projectile) and `mods-menu.o`. |
| `goal_src/jak3/dgos/cwi.gd` | `battlefront-city.o` after `mh-squad-control.o`. | After every type it uses. |
| `goal_src/jak3/dgos/ctypesa.gd` | `bf-red-guard-ag.go`, `bf-red-guard-gl-ag.go`; art groups sorted by decreasing size. | Units drawn by CTYPESA processes (§2.3). |
| `goal_src/jak3/dgos/ctypesc.gd` | `bf-hover-red-ag.go`, `bf-hover-blue-ag.go`; art groups sorted by decreasing size. | Jetpack guards are flying-turret processes, whose level is CTYPESC. |
| `goal_src/jak3/game.gp` | Four `build-actor` steps (`:framerate 15.0`), and the four art groups pre-marked in `*file-entry-map*` before `cgo-file "game.gd"`. | Without the pre-mark, `cgo-file` also adds a copy step from the decompiler output for the same `.go` and the build stops ("multiple ways to make output"). |
| `custom_assets/jak3/models/models.jsonc` (new) | The four models' recipe for master-dev's `mod_models` (`task modding-models`; at an install, the extractor runs it). | §2.3. |
| `scripts/battlefront/make_minimaps.py` (new) | Writes `battlefront-minimaps.gc` from the decompiled minimap textures. | §2.6. |
| `custom_assets/jak3/models/custom_levels/bf-*.glb`, `custom_assets/jak3/models/ctypesa/bf-red-guard*-lod0.glb`, `custom_assets/jak3/models/ctypesc/bf-hover-*-lod0.glb` (made, ignored by git) | The models `mod_models` writes (same content in both folders). | `custom_levels/` is read by `build-actor`; `<level>/` is baked into that level's `.fr3` by `task extract`. |

### 2.2 Units: everything runs on stock code

Haven City already runs the war between the two factions: its traffic engine spawns Freedom
League guards (traffic type `guard-a`, art in borrow level CTYPESA) and KG robots (`roboguard`,
`spydroid`, `flying-turret`, CTYPESC), and its attack controller (`cty-attack-controller.gc`) makes
each unit target the other faction with a hatred table indexed by unit type. The mod reuses it:

| Unit | Process type | Pool | How it changes side or look |
|---|---|---|---|
| Blue guard | `crimson-guard` | guard-a | stock |
| Red Krimzon Guard | `crimson-guard` | guard-a | half the guard-a processes spawned during a battle get a red model, `skel-bf-red-guard` (rifle) or `skel-bf-red-guard-gl` (grenade launcher); it registers as a roboguard (type 9), so the stock table sends it against the guards; its weapon is the one the stock code picks |
| Blue jetpack guard | `flying-turret` | flying-turret | half the processes get `skel-bf-hover-blue` and register as a rifle guard (type 4) |
| Red jetpack guard | `flying-turret` | flying-turret | the other half get `skel-bf-hover-red` and stay a turret (type 10) |

Each new guard or jetpack guard takes the look furthest below its share of the pool
(`*bf-look-share*`: guard-a 8 blue, 3 red riflemen, 3 red grenadiers; flying-turret 4 blue, 2 red;
`bf-guard-skel-name`, `bf-turret-skel-name`). The director counts the live units of each look every
frame of a battle (`bf-count-looks!`, in its own process); the two functions only read the counts
and add the unit they dress. An alternation was tried first: the traffic kills and spawns units all
the time (trims, section changes), and in game the guard pool drifted from 7 blue of 14 to none.
Counting inside the unit's init crashed the game: the traffic manager sets units up on its small
stack.
| Robotguard | `roboguard-city` | roboguard | stock |
| Spider robot | `spydroid` | spydroid | stock |

The skin is chosen when a process is spawned, and a traffic unit is spawned once: when it dies
it goes back to its pool and comes out again, it is never respawned. The director therefore
respawns the player at both ends of a battle the way a death does (`initialize!` with `'life`):
`reset-actors` kills every actor and the traffic manager with its units, then runs each active
level's activate function, so Haven City's traffic spawns every pool again, with the battle's
skins (deployment) or the stock ones (end). Measured in game: 13 guards in the pool, 4 of them red
riflemen and 3 or 4 red grenadiers; none left after the end. A `start` alone resets no actor, and
restarting the traffic on its own (`ctywide-activate`) left the pools empty (see the Lisp wiki,
jak3 4.30).

**No Spargus citizen in the armies.** The first version brought wastelanders into Haven City's
traffic (code and art in CTYPESA, a traffic pool of 8, their `target-counts` written so the
engine woke them). With them, ten-minute battles froze or crashed the game: the engine thread
stuck (or faulted) in the background collision query `fill-bg-using-line-sphere-new`, in two
battles of two; a battle without them ran ten minutes clean. They were removed;
`wlander-male.gc` is stock again. The Spargus Citizen class went in the twelfth round, with its
code and art in CTYPESA.

**Counts.** The battle's faction commands (`*bf-faction-commands*` in `battlefront-h.gc`) give both
factions strength 20 everywhere and Metal Heads -20, set the guards to the stock "combat" spawn
level and the KG to "war", civilians, vehicles and Metal Heads to none. They are applied through
the stock `faction-command` setting and again every 2 seconds by `battlefront-city.gc`, because a
death reset or a task change restores the stock faction state. With positive strengths the stock
faction manager requests both CTYPESA and CTYPESC (`borrow-city`); the director also sets the stock
`borrow` setting for the three Haven City aliases (`*bf-borrow*`).

**Army caps.** A traffic pool spawns units up to its `want-count` and deactivates the sleeping ones
above it; for these types the engine does not check `target-count` (`activate-by-type` skips it
below type 17). `traffic-manager-method-22` writes every `want-count` from the faction spawn levels
(`*want-count-levels*`) every frame, so its one changed line asks `bf-want-count` instead: during a
battle guard-a 22, flying-turret 10, roboguard 4, spydroid 4 (stock "war": 13, 6, 6, 9, and 17
Metal Heads), which with the look shares above (14 blue, 4 red riflemen, 4 red grenadiers, 6 blue
and 4 red jetpacks) gives 20 units per side at most. Measured in game, units awake on the street:
20 Freedom League and 20 Krimzon Guard in each of the four zones (12 per side before the caps
were raised; 19 for the Freedom League in two zones of the eleventh round's last runs).

**Units out of the camera's view.** Every frame the traffic engine sends `'traffic-off` to each awake
pedestrian (guards, turrets, roboguards and spydroids included) standing outside the city cells
marked `active-pedestrian`, the ones the camera's cell can see, and the unit goes back to its pool
(`traffic-engine.gc`, `sphere-in-loaded-city-infos?` with bit 1). Units fighting on the far side of
the battlefield, behind buildings, vanished that way, and with them the fight the reserves count.
During a fight that test also accepts a unit on a lane of the district (`bf-keep-unit?`, one `or`
in the stock line), or on no lane (a flying unit). A unit's lane is its `controller` `branch`; it
belongs to a section when its address lies in that section's nav-graph `branch-array` (the traffic
engine points each segment's branch there when the section links, `level-link`). A unit that
walked onto the next section's lanes, which the game loads at the district's edge, goes back to its
pool as in the stock game: no death, so the reserves keep it.

**Sections loaded.** Haven City holds its base (ctywide) and two sections at most: the traffic
engine has two `level-data-array` slots. In a one-section district (Port, Slums) the stock loading
stays: the force field keeps the player in the section, so the game always wants it, and the next
section the game loads at an edge carries part of the district's ground (the Port's war zone,
`ctyport-warzone`, stands on `ctyinda`'s collision: without it, no ground there). In a two-section
district (Industrial Zone, Freedom HQ) a wrapper of `load-state` `add-borrow-levels`
(`bf-want-zone-levels`) keeps the two sections wanted and drops every other section, interior or
mission level: walking toward a third section would otherwise unload one of the district's. A
respawn waits until every level its continue point lists is active (`target-death.gc`
`target-continue`), so a camp's list must fit that rule: the camps list only their district's
sections. The Port's war zone (`ctyport-warzone`) was its Krimzon Guard camp at first: it stands on
`ctyinda`'s ground, and after a death at the west docks the respawn there found `mhcitya` loaded
instead and no ground; the camp is now `ctyport-bombbot`, 176 m away on `ctyport`'s ground.

**Waking units: the Port.** The pool size is not all: the unit picker, `activate-one-vehicle`,
wakes a type only while it has fewer awake units than its `target-counts` entry for the faction
mode of the segment's territory, which the squad controls (`ff-squad-control.gc`,
`kg-squad-control.gc`) rewrite from their alert state. At the Port it allowed 7 guards, 1 flying
turret and no roboguard, so the picker's call takes `bf-want-count` there too. And the traffic wakes
units only on segments entering its active cells, one a frame (`update-traffic-amount`), and on
cells that just became active (`handle-new-vis-cell`): around the Port's two spawns it found so few
that, with the player standing, the dead were not replaced. Measured with the squads' counts lifted
alone: 3 to 5 guards awake of 14, 0 to 3 Freedom League units. The battle therefore sends
reinforcements (`bf-city-reinforce`, `battlefront-city.gc`): four times a second, up to three
times, it takes the battle's traffic type furthest below its cap, picks a random pedestrian
segment on a lane of the district (`bf-city-zone-branch?`) at least 30 m from the player, three times
likelier within 150 m of him, that passes the stock spawn's tests, and
wakes one unit of that type there with `activate-by-type` (every stock check of a spawn). A spawn
can be refused (a unit on the spot, the territory's faction rules): it tries another segment, three
in all, until the type's awake count rises. One unit a tick with no retry held the armies of 20 at
14 to 19 per side; three with retries reached 20 per side in every zone (§3.1). Calling the stock picker
(`activate-one-vehicle`) instead left inactive guards in the Industrial Zone: it weighs every
traffic type. Measured at the Port as the Krimzon Guard: 4 to 11 Freedom League and 6 to 12
Krimzon Guard units awake, both reserves dropping (9 and 23 losses in 72 seconds, against 2 and 10
in 45 seconds before).

**Pickups.** `bf-unit-killed` also queues, at the unit's position, a stock pickup type
(`bf-queue-drop`); the director spawns it with `birth-pickup-at-point` in its own process (the
queue exists because the unit's death runs on the traffic manager's small stack). Ammo pickups give
10 yellow or blue, or 5 red; `verify-pickup-type` turns red and blue into yellow when Jak lacks
that gun.

**Hatred.** `bf-city-apply-hatred` saves three groups of hatred entries once, then writes the
battle's values every frame of the fight: each player death runs `ctywide-activate`, whose
`cty-attack-reset` rebuilds the stock table. The saved entries are written back at the end:

| Entries | During a battle |
|---|---|
| robots towards Jak (0), Krimzon Guard player only | 0 (no attack) |
| guards (3-5) towards Jak, Krimzon Guard player only | the robots' hatred of Jak |

**Losses.** `traffic-tracker set-process-to-killed` (`traffic-engine.gc`) runs once per tracked unit
that really dies; `bf-unit-killed` finds its side from its type and art group (`bf-unit-team`) and
calls `bf-count-loss`. The player's deaths are counted by `bf-target-death` (§2.5).

### 2.3 The Jak 2 models

They are not kept in the repository: `custom_assets/jak3/models/models.jsonc` describes them, and
master-dev's `mod_models` makes them from the player's own Jak 2 and Jak 3 discs, ripping only the
DGOs it needs (`task modding-models`; at a launcher install the extractor runs it before its
decompile; [guide](../guides/models_from_the_discs.md)):

| Model | Built from | Notes |
|---|---|---|
| `bf-red-guard` | Jak 2 `dig1/crimson-guard-lod0.glb` (mesh, red textures) on Jak 3 `ctypesa/crimson-guard-lod0.glb` (skeleton, 52 clips) | The Jak 3 guard is the Jak 2 guard plus three joints (`back`, `right_wrist`, `left_wrist`), with identical bind poses (checked by the script) and identically named textures. The Jak 2 vertices are remapped to the Jak 3 joint indices and two padding clips put every clip at its stock `crimson-guard-ag` index, so the stock guard code drives it unchanged. The rip carries every mesh segment without its segment flag, and a build-actor model draws them all, so each weapon is its own model: this one has the body, the normal armor and the rifle. |
| `bf-red-guard-gl` | the same | The body, the normal armor and the guards' other weapon, the one the stock code shows for both the grenade launcher and the tazer (mask bit 4). |
| `bf-hover-red` | Jak 2 `drillmtn/crimson-guard-hover-lod0.glb` | Clips reordered so the three the flying-turret code plays are at its indices: 2 idle, 3 fly-forward (its "hover"), 4 shoot0 (its "fire"). |
| `bf-hover-blue` | the same, with the Jak 3 guard's `cguardgame-*` textures | The two games use the same texture names for the guards. |

The rips share their vertex attributes with every model of their level; the script keeps the
vertices the mesh uses. `build-actor` stores clip k at art-group index 2 + k and names the art
group after the file, so the skeleton groups in `battlefront-h.gc` reference `bf-red-guard`,
`bf-hover-red` and `bf-hover-blue`.

> [!WARNING]
> **Art-group order in `ctypesa.gd` and `ctypesc.gd` is load-bearing.** Once the first art group
> logs in, each DGO buffer shrinks to the object it held plus 2 KB, and the object two slots
> later lands in it. Keep each block sorted by decreasing size (sizes in the `.gd` comments).
> Breaking it prints `dgo file header ... has overrun heap`, then fails the klink `version == 5`
> assert (battle-of-spargus mod, WWD).

### 2.4 Playing a class

`bf-avatar` (`battlefront-player.gc`) is spawned to `*entity-pool*` with the class's skeleton group,
bound to the level that holds its art (`*bf-class-art*`: ctypesa for the guards, ctypesc for the
jetpacks and the robots). Each frame it:

1. copies Jak's position, faces the camera's heading (turned up to 50 degrees toward its walk, its
   walk or run clip reversed when it walks backward; facing the aim point while it fires), and sets
   `no-draw` on Jak (Daxter, the gun and the board copy Jak's draw status);
2. sets the class speed through `*setting-control*` `user-default speed-mult`, which the target
   reads every frame (`logic-target.gc`);
3. applies the class moves to Jak's velocity (jetpack lift on its fuel gauge, spider jump and blue
   eco sprint, roboguard roll) and raises or lowers the robotguard's shield;
4. reads the guard classes' D-pad weapon choice, then takes the aim (`bf-avatar-update-aim`): the
   free aim of the frame (`bf-free-aim`), or, for the tazer, the nearest foe within 12 m ahead of
   its gun (`locked?`), onto which the HUD moves the crosshair;
5. on R1, if the weapon's ammo lasts, fires it: a stock `guard-shot` with Jak as its parent
   (`spawn-guard-projectile`), so the shot skips Jak's collision and counts as Jak's; a guard
   grenade (`vehicle-grenade-deflect`, thrown by `battlefront-city.gc` on the grenade guards' arc);
   or the tazer's arc; the spider sends a melee `attack` from Jak instead;
6. plays the class clip for Jak's motion (idle, walk, run, in the air, shooting, rolling): in the
   air only when Jak is off a surface and more than 0.6 m above his ground probe's point (the
   on-surface flag goes off for single frames on the run); walk and run switch with some slack
   (run above 7 m/s, back to walk under 5), and idle, walk and run each play 0.25 s at least, so a
   speed jittering against a wall does not flip them. The model is placed again once Jak has moved
   this frame (`bf-avatar-cam-post`, a `*cam-post-hook-engine*` connection, then `do-joint-math`):
   the avatar runs in `*entity-pool*`, before Jak, and placed from its own run it showed him where
   he was the frame before, a gap that changed with each change of speed and shook the jetpack.
   The same connection computes Jak's own bones (`bf-target-bones!`): hidden, the game skips their
   math, and his collision follows them; moved by a respawn or the force field, he fell through the
   ground at 5 of the Port's 9 continue points (Lisp wiki jak3 4.34).

**The red guards' clips.** The red guard model's own clips (build-actor at 15 frames a second)
played too fast. A red guard, an AI unit (`guard.gc` init-enemy!, right after its skeleton) or the
class's avatar, now plays the blue guard's clips: `bf-guard-clips` sets its draw's art group to
`crimson-guard-ag` (same 41 joints and bind pose) and gives it an effect-control for the clips'
sounds and death effect, the method of the mod Haven City: New Dawn. A unit is therefore told by its
skeleton, not its art group: `bf-art-name` reads the joint geometry's name (`bf-red-guard-lod0`,
`bf-hover-blue-lod0`...).

**The spider's legs.** The avatar loops its walk and run clips at the rate of the ground it covers
over the ground the clip covers (`bf-avatar-loop-rate`: spydroid.gc's walk 4 m/s, run 8 m/s, rate
0.5 to 4) for the spider; the other classes keep rate 1. At rate 1 the spider, at Jak's speed times
1.5 (twice that boosting), slid over the ground.

**The camera.** A third-person shooter camera, as in Star Wars Battlefront (2004): `bf-cam-rig`,
a process spawned with the avatar under Jak (so it runs after him, before the camera) and killed
with it. It drives the stock point-of-view camera (`cam-pov`, as the city's sniper turret uses
it), which looks from a bone of a process: the rig is a process-drawable with a node list of one
cspace whose bone lives in the process itself (a heap compaction moves both). Every frame it turns
the view (`*bf*` view-yaw, view-pitch, kept across class changes and respawns) by the right stick,
160 degrees a second sideways and 100 up and down (40 up, 45 down at most), and sets the bone: the
view's rotation, placed behind a pivot at 80 % of the class's height by 1.6 times that height (5.5
m at least), 0.3 times it to the right and 0.8 m above, pulled in front of any wall between the
pivot and there (a 0.4 m sphere probe). The crosshair sits in the middle of the screen (256, 208).
Two engine facts set its signs: the camera's rvec points to the screen's left (looking along +z,
+x is on the left), and the PC settings' default third-person inversions keep the original game's
camera, which turns the view left for the stick pushed right; the rig turns the other way, as a
shooter, and follows a change of those settings. The view starts as Jak's facing at the spawn, and
a respawn looks toward the battlefield. A death's spectating gives the stock camera back, further
back.

**Guard dodges.** L2 or R2 sends Jak a stock `'launch` (`target-standard-event-handler`: a jump of
the given height with the given velocity) 0.8 m high at 11 m/s along the camera's left or right,
and keeps that speed across while it flies; it ends as Jak lands. An upward speed set by hand did
not lift him: 1.2 m along the ground. The model plays the stock guards' sideways jumps (`jump-right`
40, `jump-left` 41: the stock roll-right state throws a guard along its +x, its left, with
jump-left).

**The red guards' deaths.** Their skeleton plays `crimson-guard-ag`'s clips with an effect-control
(above), so their death clip's `'event-death` ran the stock guard's `death-default` effect
(`guard.gc`), which sets the draw-control's `death-timer`. On PC a model with a death timer is drawn
through generic merc (`foreground.gc`, the PC reassign), and a build-actor model has only a dummy
merc-ctrl for it (`build_actor.cpp`): the game crashed in `mercneric_convert` (mips2c
`generic_merc.cpp`, found with a temporary vectored exception handler) seconds into battles, as
units died. A `do-effect` wrapper (`battlefront-h.gc`) skips the death effects of the mod's
build-actor models (`bf-custom-model?`): the body goes with its death clip, without the dissolve.

**The jetpack clips' pace.** The jetpack guard's clips are the Jak 2 rip's frames at 15 a second,
which build-actor stores with a speed of one frame per 60th of a second (measured: speed 1.0): the
player's jetpack looped its 16-frame hover clip four times a second and its legs shook, the units'
own (0.5 a frame) twice too fast. Both play at `BF_HOVER_RATE`, 0.25 (measured 0.249 a frame).

**Health by class.** The player keeps Jak's health (8, the health HUD's 8 segments); the
`target-attacked` wrapper scales the damage of each attack during a fight by the class's
`*bf-class-damage*` (the attack's damage, or Jak's default `health-single-inc`): guards 1.0 (8
hits), jetpacks and spider 1.333 (6 hits), robotguard 0.5 (16 hits).

**Grenade guards against guards.** A grenade guard reloading broke off for any target within half
its keep-away distance; with another guard there, the reload, the backing away and the grenade
state chained within one frame until the stack overflowed (Lisp wiki jak3 4.40).
`bf-reload-break-ok?` (`guard-grenade.gc`) breaks it off for the player only during a battle.

**Free aim.** `bf-free-aim` (once a frame, keyed on the real clock's frame counter) casts a ray from
the camera through the crosshair's screen point (256, 208 of the 512 x 416 screen), 80 m long, with
`fill-and-probe-using-line-sphere` against the scenery and the units (Jak's own collision skipped).
The ray's direction is the crosshair's offset from the screen point of a spot 1 m ahead of the
camera, turned into meters with the projections of the camera's right and up axes there (the method
of `bf-icon-place`). Its end goes to `*bf*` `aim`, and the foe it meets to `aim-foe`. The class
weapons fire from their muzzle at that point.

**Ammo.** The guard weapons spend Jak's own gun ammo (`*game-info*` gun-ammo:
0 yellow, 1 red, 2 blue), so the stock ammo pickups refill them with no new pickup code; the
jetpacks' and the robotguard's built-in guns spend none, their salvos are paced by a delay. The director saves Jak's ammo,
light eco and dark eco when a battle starts and writes them back when it ends; each deployment
(the first class page, a respawn after a death, a restart) tops the ammo up to 60 yellow, 10 red
and 50 blue, and fills the guard weapons' magazines.
During the battle the avatar turns any dark eco Jak picks up into jetpack fuel (6 units, one drop,
fill a tank) and keeps his at 0. The "endless dark eco" secret sets Jak's dark eco to its maximum
every frame (`target-eco-process`, `powerups.gc`): the director clears its bit for the battle and
sets it again at the end.

**Weapons of the guard classes.** The blue guard shows the weapon in hand with the stock mesh
segments (rifle 8, tazer and grenade launcher 16, `crimson-guard-method-267`); the red guard's tazer
and grenade launcher are its second model, so a change between them asks the director to draw the
class again (`*bf*` `redraw?`). The tazer is the guards' own lightning (`lightning-control`, spec 19
built, drawn with spec 20 and 9 points between the gun and the aim, as their tazer draws a miss).
The lightning-control lives in the avatar's heap: the avatar's `relocate` method moves its pointer
when the dead-pool heap compacts (as crimson-guard's `l-control`); without it the first tazer shot
crashed the game.

**Guard magazines and upper-body clips.** The guard classes fire from magazines, the stock
guards' sizes (`crimson-guard-method-286`): 6 rifle shots, 2 grenades, kept in `*bf*` `mag` so a red
guard drawn again with its other weapon keeps them; the tazer has none. The shot that empties one
starts a reload (`reload?`), which waits for the shot's clip to end, plays the stock rifle guard's
reload (`guard-rifle.gc` `rifle-reload`: `grenade-reload` at 1.1 times, then `cock-gun` at half speed),
then fills the magazine from Jak's ammo; R1 does nothing meanwhile, and an empty magazine with ammo
left reloads on the next R1. A weapon change or a rifle butt drops a reload in progress. These clips
play on the upper body only, the engine's `top-anim` mechanism that plays Jak's gun clips on his
arms (`process-drawable.gc` `top-anim-joint-control`): the avatar of a guard class carries one with
the joints above the hips (`BF_GUARD_UPPER`), and `bf-avatar-top-play` pushes a clip, with its frame
range, onto it; the legs keep their idle, walk, run or jump clip. A rifle shot is `gun-attack`; a
grenade, the stock grenade guard's two parts of `grenade-attack` (artist frames 1 to 12 at 1.5
times, then 22 to 37, `guard-grenade.gc`); the tazer thrusts with `stab-attack` and holds
`stab-idle-loop` while its arc lasts. Before, the guard switched its whole body to a firing clip for
0.4 to 0.7 s per shot (the legs stopped on the run), and the grenade throw played `grenade-attack`
from its first frame, a clip that runs on to the launcher's reload.

**Robotguard punch.** Square plays the stock roboguard's punch, as `roboguard-city.gc` does:
wind-up (`punch-close-rotate`), punch (`punch-close-go`), back (`punch-close-end`), 0.9 s in all
(`*bf-punch-clips*`, `melee-step`); the hit lands as the punch clip starts, on the nearest foe ahead
within 6.5 m (`bf-avatar-punch`). The punch clip alone, 0.18 s, read as a twitch, and 4 m reached
few foes from a 4.8 m tall robot.

**Robotguard shield.** Circle held spawns `bf-shield`, a subtype of the Dark Makers' shield sphere
(`shield-sphere`, `engine/common-obs/shield-sphere.gc`, GAME code; its art is in CTYPESA): 3 m
around Jak, 2.2 m up, strength 3. It takes the mech shield's collision (an obstacle the shots hit,
which neither pushes nor hurts Jak), and its post adds a constant red emissive to the stock heat
glow. Shots heat it; past 1.0 it breaks into its stock shards, and the avatar, which polls it with
`'active`, waits 5 s before the next one. Its init binds it to CTYPESA first: `initialize-skeleton`
looks the art up in the process's level, and without it the shield went straight to
`process-drawable-art-error`. While it is up, and while the robotguard rolls, the wrapper of
`target-attacked` in `battlefront.gc` sets Jak's shield level for each attack: 1 when the sender
is a `projectile` or an `explosion`, 0 for anything else (a blow, sent by the attacker itself), so
the blasts and the shots that still reach Jak are stopped.

The settings `gun`, `attack`, `board`, `darkjak` and `lightjak` are owned by the avatar and leave
with it; its `deactivate` gives Jak back his model and speed. When the avatar disappears (its level
unloads, a death reset kills `*entity-pool*`) the director spawns it again. The mod keeps the
avatar and the director as handles, in `*bf*` (`avatar`, `director`): both come from dead-pool
heaps, whose freed records the next spawned process reuses, so a stale ppointer would name an
unrelated process, and a global symbol holds only 32 of a handle's 64 bits. Kept in globals,
the handles never resolved: the director spawned a new avatar every frame until the game ran out
of memory, and the class page never opened after a death (both seen in game).

The avatar blends into each new clip (0.1 s). With two blends still running, the new clip waits
for one to end (0.3 s at most, then it switches at once): a clip that changes every few frames (in
flight) would fill the joint-control's 6 channels ("could not do (ja-channel-push! 1)", seen in
game), and switching at once, as it did before, popped the guard's pose (2 of 14 clip changes in a
guard run, 0 of 13 since). The jetpack dive and the spider pounce lift Jak off the
ground and steer him at the foe every frame until they reach it: on the ground, Jak's own stance
code cancels a single push.

The stock units pick their mesh segments in their own init; the avatar does it for the classes
that have several: the blue guard shows the rifle and the normal armor (masks of
`crimson-guard-method-267`).

### 2.5 Battle life cycle

| Phase (`*bf*` `phase`) | What the director does |
|---|---|
| off | nothing; every hook answers like the stock game |
| deploy | sets the `borrow` and `faction-command` settings and the continue point, respawns the player there with `initialize!` `'life` (every unit pool spawned again with the battle's skins), and holds him there (`bf-hold-at-spawn`) until he stands on the ground: the battle's Haven City alias reloads the city's collision, and Jak used to fall through the map and die. When ctywide, ctypesa and ctypesc are active and Jak has stood (state `target-stance`, after at least 2 s): Haven City side `BF_CITY_PREPARE` (hatred saved, wastelander level), then fight. Gives up after 60 s. |
| fight | class page first (the deployment's), then `BF_CITY_UPDATE` each frame (hatred, faction commands), avatar upkeep, force field (`bf-keep-in-zone`, §2.6), pickups of dead units, HUD |
| over | result page; X ends the battle |

Ending a battle switches the phase off first, then calls `BF_CITY_RESET` (hatred written back),
removes the director's settings and respawns the player at his spawn with
`initialize!` `'life`, so every unit comes back with its stock skin. While Jak drives, the end
waits until he is on foot.

**START > Options > Gamemode.** While the mode is on, `bf-update-options-entry` swaps the Options
page's list (`*options-options-pc*`) for one with a sixth entry, the offsets spread again; off, the
stock list and offsets are back. Its `next-state` `'bf-gamemode`, and the Battlefront page's
`'bf-battlefront`, are routed by a wrapper of `progress` `set-menu-options` to two generic scrolling
pages (`*bf-gamemode-page*`, `*bf-battlefront-page*`). Their labels are text ids past the game's own
(`BF_TEXT_*`, from `#x7f00`), answered by a wrapper of `game-text-info` `lookup-text!` in English or
French: the game's text files stay as they are. A Battlefront button hands its request to the
director (`bf-menu-request`) and closes the START menu (`'go-away`); the director runs it once the
master mode is `'game` again. Restart (`bf-restart-battle!`) gives Jak back what the battle set aside
and starts the same battle again, so the new start sets Jak's own aside once more.

**Switched off in a battle.** The director sees the mode off while a battle runs, closes its page,
and once the Mods menu has closed (that menu closes itself on this toggle) loads the last save
(`bf-leave-to-save!`): `(auto-save-command 'restore 0 (-> *game-info* auto-save-which) ...)`, as the
START menu's Load Game, the slot the game last loaded or saved (`*setting-control*` `user-default`
`auto-save` is set once one was). The load's `initialize!` 'game ends the battle (`bf-stop-now!`).
With no save since the boot it ends the battle as Quit does.

**Death and spectator.** During a fight the code of Jak's `target-death` state is `bf-target-death`
(the state's `code` slot set at load, the stock code kept in a `define-perm` and run outside a
fight). It sets what the stock death sets that the game reads (dead focus status, attacks off, gun
away), counts the loss, removes the class model, and for `BF_RESPAWN_TIME` (4 s) hands the camera
to a living unit of the player's side (`'change-target`, as cutscenes' `camera-look-at` do; the
nearest within 150 m, another when it dies), 10 to 14 m behind it (the camera's string settings: by
default a guard filled the screen), while the HUD counts down. Then it moves Jak to his spawn and,
still hidden, wants the levels the camp's continue point lists as a respawn there does
(`bf-want-camp-levels`) and waits until they are active, 10 s at most. It makes the spawn the force
field's safe place,
turns him toward the district's middle, fills his health and ammo, gives him 2 s of invulnerability
(`target-timed-invulnerable`), gives the camera back 6 m behind him (`'change-target`,
`'teleport-to-vector-start-string`) and goes to `target-stance`; the director draws the class
again. The stock death froze the enemies for its length (a `'process-mask`
setting), could play a death movie, and its reset (`initialize!` 'life) spawned every unit of
Haven City again: the battle's units vanished at each death and came back at their pools' places.

The battle menu sets `*popup-menu-open*` while it is up, as the popup menus do: in the 'menu
master mode the pause buttons (`toggle-pause`) would otherwise resume the game under the page, and
the Mods menu would open over it. A page draws its panel and all its text into one DMA buffer,
panel first (with separate buffers the panel covered the text); centered text has its origin at
x 256 of the 512-unit screen (the font's `middle` flag centers on the origin); descriptions wrap
at 44 characters. The texts follow the PC text language (`*pc-settings*` `text-language`), the one
the game's own texts use; a loaded save sets the stock `language` setting to its own. French
texts avoid the ASCII apostrophe, which the game's font draws as an acute accent.

The deployment comes before the class choice: the class models, and the class page's preview of
them, live in CTYPESA and CTYPESC, which only the battle's alias levels load.

### 2.6 Class models over the game, HUD and force field

`bf-icon` (`battlefront-player.gc`) draws a class model playing its idle clip: the class page's
preview (a child of the director, 230 screen units tall, turning 90 degrees per second) and the
class icon in Jak's health HUD (a child of the HUD process `hud-health`, 34 units tall, which shows
and hides it with its 'draw events). It runs on the real clock with the menu and pause masks
cleared, so it moves while the class page pauses the game.

It is drawn with the world, not through the HUD's model path. Jak 3's HUD icons
(`hud-create-icon`) draw with `foreground-draw-hud`, which feeds the PS2 generic renderer
(`foreground-generic-merc`); build-actor models have no data for it, and the red guard's preview
crashed the game in native code. `bf-icon-place` instead stands the model a few meters in front of
the camera (3 m for the preview, 1.5 m for the icon), facing it: the screen scale at that depth
comes from projecting the camera's right and up axes with `transform-point-vector!` (screen origin
at (1792, 1840)), and each class's model height comes from the bind pose of its rip (guards 3.8,
jetpack guards 4.3, robotguard 4.8, spider 2.0, in game meters).
Guessed human heights (2 m) drew them twice too large. The director gives each model its screen
spot every frame, and a `*cam-post-hook-engine*` connection of the model puts it there again
right after the frame's camera is set (`update-camera`, `main.gc`), then computes its joints again
(`do-joint-math`), before anything is drawn. Placed from the process run alone, the model used the
previous frame's camera and its joints were computed before the camera moved: it trailed a moving
camera, and a screenshot taken while the camera settled showed the HUD icon at the bottom of the
ring. Jak's preview uses `target-skel-group`, the
skeleton group with his outfit's geometry (skel-jchar alone draws one flat quad), with a heap large
enough for its cloth, turned on as the target does for that outfit.

The class page's preview is the only `bf-icon` left; the health HUD keeps its stock look, with no
model in its ring. The class gauge takes one of the ring's eco gauges: `hud-health`'s `draw`
(`hud-classes.gc`) calls `bf-hud-health-gauges` once it has set its sprites and before it draws
them, and during a fight that function sets the scale and color of sprite 2 (the dark eco gauge,
the right half: the jetpack's fuel, in the bright color the gauge takes when Jak has eco enough for
a dark bomb) or sprite 1 (the light eco gauge, the left half: the spider's blue eco in blue, the
robotguard's roll in red), with the stock gauges' pulse kept between 0.5 and 1 (the stock 0 to 1
made the fuel vanish on the dark disc half the time). The battle keeps Jak's own light and dark eco
at 0, so the other gauge stays empty. The ring's windows shape the gauges because they are drawn
before it: a gauge in a later sprite (5) was hidden behind the ring, which writes its depth on its
whole square. The director asks the health HUD to show every second (`'show`), within its 2-second
display time.

The gun icon is the stock gun HUD itself (`hud-classes.gc` `hud-gun`), top right. It only shows
while Jak's own gun is out, which the battle forbids, so `battlefront.gc` replaces its
`update-values!` (a `define-perm` wrapper): during a fight, with an ammo weapon, it sets the HUD's
gun (`*bf-hud-guns*`, the pickup-type of the BF_AMMO_* in use) and ammo values and asks it to show,
then runs the base `hud` update; the stock `draw` does the rest (icon, shell column, "ammo/max"
count). Otherwise the stock update runs and hides it. The battle's `'gun #f` setting also hides the
stock gun arrows. The crosshair is the HUD's `hud-gun-reticle` texture drawn as a centered `hud-sprite` in
the HUD's sprite bucket, at its fixed point or, while the tazer locks a foe, at the foe's
projection.

**Pages on black.** While a battle page is open, `bf-black-set!` sets the menu renderer mask
(`*display*` `vu1-enable-user-menu`, which `drawable.gc` copies into the frame's mask every frame,
as the stock progress menu's "menu mode" does) to the foreground renderers only (`generic`, `merc`,
`emerc`): no sky, scenery, ocean, particles or shadows. It also sets `no-draw` on every drawn
`process-drawable` except the `bf-icon` previews, keeping their handles (1024 at most) to clear the
flag on exactly those when the page closes. The screen behind is black, with the class preview
alone.

**Zone map.** The zone and side pages draw the zone's whole district on the game's minimap
textures. Haven City's minimap is a grid of 5 x 7 cells of 384 m, each naming a texture that covers
1024 m around its cell: 256 x 256 texels of 4 m, or 256 x 128 on the city's south edge, 8 m tall
(`engine/ui/minimap.gc` `*minimap-texture-name-array*` and `*minimap-corner-array*`). A level lists
the cells it covers in its `city-map-bits` (`level-info.gc`). The textures live in each city
section's own minimap texture page, loaded only with the section, and the menu needs every zone's
wherever the player stands: the mod carries them. `scripts/battlefront/make_minimaps.py` builds each
zone's map over the bounding box of its sections' cells, at most 256 texels on a side: a texel of a
cell of the zone takes its cell's texture, sampled at that texture's own size; a texel of a cell of
another level is black; the width is padded to a multiple of 64. It writes
`battlefront-minimaps.gc`: 8-bit texels, one palette of 34 colors in the PS2 order (entry i at i
with bits 3 and 4 swapped), each map's stored and drawn size, its world corner and texel size, and
its `tex0`. `bf-zone-view!` fits the whole map in the right frame, its shape kept (a texel is
`0.923 relative-x-scale` times wider than tall in screen units); `bf-draw-zone-minimap` uploads the
zone's texels as the START menu's map does (`pc-upload-map-texture` into the texture at tbp 8) and
draws them as one sprite in its own bucket (`bf-map-sprite`, the stock `sprite-dma` with the view's
texels and box), then marks the default level's VRAM dirty, as the START menu's map does.
`bf-draw-zone-marks` draws the frame, the spawns and Jak over it with the same projection. The START
menu's own map, used before, has the same streets over a textured ground: it did not look like the
minimap.

**Reserves.** `bf-draw-reserves` draws them top middle, after the reinforcement meter of Star
Wars Battlefront (2004) (its manual: "the numbers and bars represent the strength of
reinforcements for each faction. The player's faction is Green, the enemy is Red"): a dark panel,
two bars of `draw-sprite2d-xy` from the middle out, 76 screen units each when full (`BF_BAR_HALF`,
`BF_RESERVE` units), the player's side left in green and the enemy right in red, and the counts
under them on either side of a divider. The panel ends left of the stock gun HUD. The zone and
class line it replaced is gone.

**Jetpack flight.** `bf-avatar-moves` sets Jak's vertical speed every frame he is in the air on
fuel: X keeps a jump's own speed or climbs at 7 m/s; Circle comes down at 6 m/s; neither steers to
the height held (`hover-y`) at 4 times the gap, so the hover settles and stays still. Out of fuel
the fall is capped at 3 m/s (4 measured, gravity included). The model is drawn 0.8 m above Jak
(`bf-avatar-follow`), on the ground too. Landed means Jak is `on-surface` AND within 0.5 m of his
ground probe's point (`gspot-pos`): hovering 2 m up, `on-surface` came on for a frame once a second,
reset the held height and let the jetpack sink a step every second (seen in game, Lisp wiki jak3
4.33).

**Force field.** The battlefield is the district's sections, and the game tells which level the
player is in: `*load-state*` `vis-nick`, which the sections' region scripts switch as he crosses
into another. vis-nick alone is not enough: with the Port's war zone loading `ctyinda`, Jak stood
in the Industrial Zone and the game still saw him in `ctyport`. So he must also be in a minimap
cell of the zone's sections (`bf-zone-cell?`, the cells of their `city-map-bits`, written by
`make_minimaps.py` as `*bf-zone-cells*`; a place past the grid's edge counts as the edge cell's:
the Slums' alley is east of the last column). Cells are 384 m, and some are shared by two
districts: there vis-nick decides. `bf-keep-in-zone` takes his safe place every 0.5 s while he
stands in the zone (`*bf*` `safe`, and `safe-level`, the vis-nick there). When he is out of the
zone, or 20 m below his safe place (a hole, or a place whose ground is not loaded), it puts him
back there (`move-to-point!`), cancels his speed, sets vis-nick back, and shows the sparks.
A jetpack class more than 2 m above the ceiling (only a jump takes it there) has its rise turned
into a 2 m/s fall. Under the ceiling the jetpack's own lift fades (4 times the gap to the ceiling,
in m/s, at most 7). The first version cut the thrust at the ceiling, refilled the fuel while X
stayed held after it ran dry (a thrust every other frame), and the force field pushed down right
above the ceiling: the mod's author saw the jetpack jerk in flight. The current rules were measured
frame by frame (§3.1). Both spawn Light Jak's shield-hit sparks (`group-lightjak-shield-hit`) and
play `shield-hit`; a jetpack holding X stopped at 0.1 m above the ceiling.

### 2.7 Outside the campaign

| What | How |
|---|---|
| No vehicle | The director sets `'pilot` to #f with its other settings: a vehicle takes the player only with it on (`vehicle-util.gc` `check-player-get-on`). It goes with the director too. |
| No mission or activity starts | The director sets `exclusive-task` to `(game-task none)` with its other settings: a task node is open only if its task is one the setting names (`task-control.gc` `game-task-node-info-method-12`), and no node has the task none. NPC prompts, burning bushes, task managers and their minimap icons follow that gate. The setting goes with the director. A mission already running stays open. |
| Save, Load Game and Secrets grey and refused | Wrappers of `menu-main-menu-option` `respond-progress` (X on one of them, `bf-locked-option?`: the stock refusal beep, nothing opens) and `draw-option` (the stock label, in the PC menus' disabled color) in `battlefront.gc`. A load would end the battle in the middle of the menu; the secrets would change the fight. |
| A load ends the battle | A wrapper of `game-info` `initialize!`: a `'game` reset (the START menu's load, a new game, the title) or a `'boot` during a battle calls `bf-stop-now!` first, before the reset and the save's data: the avatar and the Haven City side go, Jak gets back what the battle set aside, the mode is switched off and the director goes with every setting it owns. The battle's own respawns (`'life`) go on as before. |

### 2.8 Health, damage and targeting

**One 24 point scale.** `battlefront-h.gc` gives every class and unit its full health in points
(`*bf-class-hp*`, `bf-unit-hp`) and every attack its points (`bf-attack-damage`, told by the
sender's type: `guard-shot` 8, or the player's class gun through `bf-shot-damage`; an explosion
20; a unit's own blow 10, a spider's 12; the player's own attacks carry theirs in `*bf*`
`own-attack` while `bf-send-attack` sends them, so Jak's body running into a unit deals 0). Two
wrappers turn the points into the game's units:

- Units: a `damage-enemy-from-attack!` method on `nav-enemy` takes the attack's share of the
  unit's stock hit points (`default-hit-points`, which caps them first), 0 when the attacker is of
  the unit's side, and counts the kill in `*bf*` kills when the attacker is the player. It is set
  on `nav-enemy`, the parent of every unit of the battle: the city's units are defined in level
  code linked after GAME and copy it at their creation, and GAME itself links with method-set
  propagation on (Lisp wiki jak3 4.10). Measured: a rifle hit took 1.33 of a guard's 4 hit points (8 of 24).
- The player: `target-attacked` refuses an attack from his own side (no hit reaction) and sets any
  other's damage to its points times `health-max / 24` (Jak's 16 health: a guard's blow 6.67,
  measured). His health at a deployment, a respawn or a restart is his class's share of
  `health-max` (`bf-class-health`: the spider half the bar). While the robotguard's shield is up,
  `*bf*` `shield?` sets Jak's shield level, and the stock handler refuses every attack. The flag
  is set to `#f` at load: a symbol field of a static structure starts as 0, which tests true, and
  until this round no attack ever hurt the player in a battle (Lisp wiki common 1.4.16).

**Targeting.** `battlefront-city.gc` pushes two hatreds into Haven City's attack controller
(`bf-city-push-hatreds`: the nearest foe first, kept until it dies, the player twice as hated as a
unit), writes the attacker/target table of every battle type by side (`bf-city-apply-hatred`, 0
within a side, the player's row and column included) and clears the guards' anger callbacks.
Twice a second `bf-city-retarget` makes three kinds of unit look again: the other side's within
50 m of the player whose foe is farther than him, any whose foe went beyond 150 m, and any of the
player's side that has him as its foe (a target taken with the stock table while the zone loaded
was kept for good: a red guard and a red jetpack aiming at a Krimzon Guard player, seen in a smoke
run). The units' weapon goes through `bf-guard-weapon` in `crimson-guard-method-267`, and method
270 compares the weapon it would give (Lisp wiki jak3 4.37): no tazer in a battle. The squads
give the blue guards the tazer mostly: turned into the launcher alone, it left no rifle among them
(13 launchers, 0 rifles near the player); split by the guard's pid, 7 and 3.

**Guard ammo and the gun HUD.** The rifle's magazine is `*bf*` mag (10), its reserve Jak's
yellow ammo (capped at 20 every frame), the grenades Jak's red ammo (capped at 5). The `hud-gun`
`draw` wrapper draws the stock icon with its count and shells scaled to nothing (they would show
Jak's ammo against its stock maximum), then the guard's own (`bf-draw-gun-ammo`, the stock shell
sprite 14 and string position).

**The tazer.** One strike on the foe the free aim locked within 12 m (`bf-avatar-tazer`), then
`*bf*` tazer-time holds the next for 20 s, across a class change or a respawn. Its look: a
`joint-mod` in `joint-set*` mode on node 13, the guard skeleton's `gun` joint
(`joint-nodes.gc`), scaled to 0.55 while the tazer is in hand (`bf-avatar-gun-look`). The avatar
comes from a dead-pool heap: its `relocate` moves the `gun-jm` field with the process, or the
scale written through the old address crashed the game seconds after a guard deployed (Lisp
wiki jak3, process heaps move).

**Class help.** Each class's lines (`*bf-guard-help*`, the robot's and spider's inline) are drawn
under the list by `bf-draw-class-help`; their `<PAD_...>` tags become the font's button icons, and
the D-pad's left arrow is drawn from the font's D-pad parts (`~3L`, `~22L` colors and `~+nH`,
`~-nV` offsets). A line holds about 30 characters in the left frame. The preview fits each class's
height in the frame, the spider robot its 4.4 m leg span (`bf-icon-size`): at its 2 m height it
spilled out of the frame.

---

## 3. How to test

1. Select the game: `task set-game-jak3`.
2. Models: `task modding-models`, with both games' disc files in `iso_data/jak2` and
   `iso_data/jak3` (`-- --check` only lists what is missing).
3. Re-extract, so `ctypesa.fr3` gets the red guard and `ctypesc.fr3` the jetpack guards:
   `task extract`. The log should show `Adding custom model bf-red-guard-lod0 to ctypesa` and the
   two `bf-hover` models for ctypesc.
4. Compile: `task compile-check`, or `(make-group "iso" :force #t)` for the first compile in this
   worktree.
5. Boot cold: `task boot-game-retail` (proves the Mods menu works in a retail boot). Use a save
   where Haven City is open. To rebuild the zone minimaps, `python scripts/battlefront/make_minimaps.py`
   after `task extract`.
6. In a stock area first, check nothing changed (guards blue, flying turrets, no red guard in
   Haven City).
7. Mods menu (L3 + SELECT) > battlefront > Battlefront mode, then START > Options > Gamemode >
   Battlefront > New battle, and for each zone and side:

   | Check | Expected |
   |---|---|
   | Zone and side pages | black screen; the whole district on its minimap (dark gray ground, white streets, blue water), the other districts black, blue and red spawns |
   | Class page, deployment | right after the side page, black, "Loading the war zone..." while the zone loads under it; the preview turns once the models are in; then the game pauses and "Deploy" shows |
   | Class page | two Freedom League classes, four Krimzon Guard ones; the class under the cursor stands in the right frame and turns; X deploys, HUD with 500 / 500 |
   | Camera | over the class's right shoulder, the crosshair in the middle; the right stick pushed right turns right, pushed up looks up; the class faces where it aims and walks sideways and backward |
   | Guard rolls and strafes | L2 with the left stick rolls about 4 m that way (right, left or ahead), with the guards' sideways jump; R2 held with the stick strafes, the guard facing ahead |
   | Units | blue guards and red Krimzon Guards in the streets, jetpack guards in the air, robotguards, spider robots; the two sides shoot each other; at most 20 per side, still there when the camera turns away; no citizen |
   | Losses | each kill lowers the right side's reserve; pickups appear where units die, dark eco now and then |
   | Each class | its model in Jak's place, its clips, the moves, R1, Square and Circle of §1 |
   | Guard weapons | D-pad left, down, up: tazer (a short baton in hand; one strike on the nearest foe within 12 m, then 20 s), rifle (10/20, a reload when the magazine is empty), grenades (5); firing while walking keeps the legs walking |
   | Free aim | shots and grenades go where the crosshair points, for every class and for Jak; the crosshair turns red on a foe |
   | HUD | stock health ring, no model; "Kills" on the left; the stock gun icon top right for the guards with 10/20 and 10 shells for the rifle, the grenades left and 5 shells, nothing but the recharge seconds for the tazer; jetpack boost in the dark eco gauge, spider blue eco and robotguard shield in the light eco gauge, blue and red |
   | Robotguard | R2 rolls as a ball until R2 again; Circle: red shield sphere for 5 s, every attack stopped, the robot walking behind it, then 25 s before the next; R1: salvos of two shots; Square: a full punch |
   | Outside the campaign | no mission prompt; START menu: Save, Load Game and Secrets grey, X refused |
   | Jetpack | X climbs, Circle comes down, neither hovers still, for as long as you like; R2 boosts toward the stick while the gauge lasts; dark eco alone refills it; the model floats above the ground, its legs calm when it stands still |
   | Reserves HUD | top middle: your side's bar in green to the left, the enemy's in red to the right, the counts under them |
   | Vehicles | Triangle by a vehicle does nothing during a battle |
   | Player death | the side loses 1; 4 s on a unit of the side with a countdown; back at the spawn as the same class |
   | Whole district | every street of the district's sections can be walked; crossing into the next district puts the player back where he last stood in this one, with sparks and "FORCE FIELD"; a jetpack stops at the ceiling |
   | Change class, Restart | START > Options > Gamemode > Battlefront: the class page with the battle going on; a restart back to 500 / 500 at the spawn, same class |
   | End | START > ... > Quit the battle: stock Haven City again (blue guards, turrets), Jak's ammo as before; the mode switched off in the Mods menu during a battle: the last save loads |

The smoke tests, from round 13 on, are in the test notebook,
[`battlefront_tests.md`](battlefront_tests.md): each one is a scenario of
[`battlefront_smoke.gc`](battlefront_smoke.gc) that boots the game retail, loads save slot 1 and
drives the mod's real menus with the pad.

### 3.1 What the in-game runs checked

The runs used a copy of the user's settings and save slot 1 (Haven City open, 100 %), each
launched cold. Pad input was injected by replacing `cpad-get-data`, screenshots were taken with
`pc-screen-shot`, state lines were printed to the game's output. The final runs used a pure retail
boot (`-boot -fakeiso`) with a temporary scenario file compiled into GAME (not part of the mod), so
no REPL took part: title, slot 1, Mods menu, battle, each class of the side, a battle of two to ten
minutes, forced victory, end of battle.

| Check | Result |
|---|---|
| Mods menu in a retail boot (L3 + SELECT), `battlefront` submenu, the three pages, French texts | Opened and navigated by pad; pages laid out inside their panel |
| Deployment, Port (Krimzon Guard) and Industrial Zone (Freedom League) | Jak stands at his side's spawn; fight phase, 500 / 500 |
| Units | Both sides present and fighting: 7 blue guards, 4 red riflemen and 3 red grenadiers, 2 or 3 blue and red jetpack guards, 5 robotguards, 4 or 5 spider robots; the looks stayed balanced for ten minutes; both reserves drop |
| Player death | His side loses 1, respawn at the spawn, class page with "Déployer" |
| Each Krimzon Guard class | Model in Jak's place; Red Guard rifle and rifle butt kill; Red Jetpack climbs from 4.8 to 27.9 m holding X, its rifle and dive kick kill; Robotguard runs at 6.9 m/s, rolls at 15.9 m/s, its fists and punch kill; Spider Robot runs at 12.9 m/s, jumps 5.5 m (other classes 3.5 m), its lunge and pounce hit |
| Each Freedom League class | Blue Guard runs at 8.7 m/s, its rifle and rifle butt kill; Blue Jetpack climbs to 14.8 m, its rifle and dive kick kill; Spargus Citizen runs, its rifle and rifle butt hit; Jak's own gun and punch kill |
| Change class (Mods menu) | Class page, new model |
| Victory | Foe reserve at 0: result page "VICTOIRE", winner and losses; X ends the battle (both sides) |
| End of battle (result page, Mods menu "End the battle") | Stock city again: 8 blue guards, 3 stock flying turrets, no red guard, no jetpack guard; Jak himself |
| Stability | After the last fixes, three long runs in a row ended clean: a ten-minute battle as a Blue Guard (118 deaths), the full Freedom League scenario and the full Krimzon Guard scenario |

The second round (weapons, ammo, crosshair, HUD, gauges, shield, army caps, force field) ran the
same way, one Freedom League and one Krimzon Guard scenario in the Industrial Zone, two minutes
each, with screenshots and state lines every half second:

| Check | Result |
|---|---|
| Class page | Opens at the spawn after the deployment; the preview stands in its frame at its size for the eight classes, Jak included, and turns |
| Guard weapons (Blue Guard) | Rifle: yellow 100 to 95; tazer (D-pad left): arc drawn to the foe, blue 180 to 172 in 1.6 s; grenade launcher (up): one grenade bursts, red 28 to 27; back to the rifle (down) |
| Crosshair | On the foe and red when one is ahead, white 30 m ahead otherwise |
| Health HUD | Shown all the fight; the class model (blue guard, red guard, spider) stands inside the pips; weapon and ammo beside it |
| Jetpack | Fuel drained at 0.25 per second of thrust, climb stopped at the ceiling (38.1 m for 38.0 m); refilled at 0.1 per second |
| Spider blue eco | The gauge drains while Circle is held |
| Robotguard shield | Circle held: shield level 1, Light Jak's shield model; shots and blasts stopped, blows let through (logged attacks, §2.4) |
| Army caps | Awake units on the street: at most 11 Freedom League and 12 Krimzon Guard |
| Pickups | Up to 12 ammo pickups and 1 health pickup on the ground at once |
| Force field | Held at 0.1 to 0.3 m inside the edge while running out; "FORCE FIELD" and sparks |
| Crashes found and fixed | The first tazer shot (pointer to the arc not relocated); the red guard's preview (HUD model path) |

A third round measured each war zone with the reinforcements and the final zone table: one battle
per zone, the player standing at his spawn for 90 seconds as the first class of his side, units
counted every 3 seconds (awake, alive, drawn, outside the player), then a jetpack climb holding X
and a run out of the battlefield from 5 m beyond its edge:

| Zone (player's side) | Units awake, mean (max) | Losses in 90 s | Jetpack top / ceiling | Force field |
|---|---|---|---|---|
| Port (Freedom League) | 8.0 (12) FL, 7.9 (12) KG | 19 FL, 23 KG | 37.26 / 37.17 m | held at 148.06 to 148.15 m, radius 148.30 m |
| Industrial Zone (Krimzon Guard) | 6.7 (10) FL, 5.4 (11) KG | 1 FL, 9 KG | 38.03 / 37.99 m | held at 140.04 to 140.26 m, radius 140.29 m |
| Slums (Freedom League) | 5.6 (10) FL, 6.0 (11) KG | 24 FL, 25 KG | 38.22 / 38.13 m | held at 145.49 m, radius 145.74 m |
| Freedom HQ (Krimzon Guard) | 5.5 (12) FL, 7.8 (12) KG | 7 FL, 11 KG | 31.91 / 31.88 m | held at 140.36 m, radius 140.61 m |

The force field rows come from a last pair of runs that put Jak 4 m beyond the edge on ground
found by a downward probe (a first try without the probe dropped him off the map in the Industrial
Zone and the Slums). The same runs timed the gauges from empty, once a second: the jetpack's fuel
and the spider's blue eco both went 0.0, 0.1, 0.2 ... 0.9, 1.0 in 10 seconds.

No crash in these runs. Before the reinforcements, the Port as the Krimzon Guard held 2 to 6
Freedom League units; the first Slums pair 1.1 Freedom League unit on average; Main Town none.

A fourth round followed the author's first play (jetpack jerks, gauges, free aim, citizens,
previews on black, dark eco): Freedom League runs at the Port and in the Slums, Krimzon Guard runs in the Slums,
with screenshots, the jetpack's height logged every frame, and state lines:

| Check | Result |
|---|---|
| Pages | Zone, side and class pages on a black screen; the four zone maps with their lanes, spawns and edge; the class preview alone in its frame |
| Free aim | The crosshair's ray ends on the crosshair: its end projects back to (256.0, 196.0) within 0.07 units; it met guards at 19 to 25 m (crosshair red); a rifle shot burst on the crosshair's point; a grenade landed 0.73 m from it |
| Jak's gun | With the plain blaster, his shot flew straight at the free aim's point (direction to the point: dot 1.000) |
| Tazer | Locked by itself on a guard 4.7 to 5.4 m away; the crosshair moved onto it, in red |
| Jetpack | Holding X: 239 frames of climb at 6.0 to 10.9 m/s with no frame going down, fuel from 1.0 to 0 in 4 s, then a fall; refilled at 0.1 per second on the ground. Near the ceiling the climb slowed into a hover 0.26 m under it |
| Dark eco | Left by units killed in battle: 1 of 7 pickups in a Port battle (10 deaths), 4 of 26 in a Slums battle (44 deaths). Each drop is 3 pills; a jetpack brought onto them went from 0.22 to 0.56, 0.93 and 1.0 at the Port, from 0.21 to 0.55, 0.91 and 1.0 in the Slums, one pill each, Jak's dark eco staying 0; the ring's yellow bar went from a sliver to full. A drop spawned by hand at 0.41 filled it at once. The test save had the endless dark eco secret on: before the fix the fuel never went down |
| Gauges | Jetpack fuel in yellow and spider blue eco in blue on the ring's left, the class model beside them |
| Citizens | 2 to 6 awake and 18 to 22 in their pool before a battle, none during it |
| HUD icon | While the camera swung at full right stick for 3 s, and for 1.5 s after a camera teleport, the drawn icon stayed within 0.06 screen units of its spot in the ring (its root projected with the frame's camera, every frame) |

A fifth round followed the author's second set of notes (HUD with the stock gauges and gun icons, robotguard, salvos, spider, no Jak, save pictures, outside the campaign): one Freedom League and one Krimzon Guard scenario at the Port, two minutes each, plus a shield test with guard shots fired at the robotguard:

| Check | Result |
|---|---|
| Pages | Zone and side pages with the city's save picture above the zone map; three Freedom League classes, four Krimzon Guard ones |
| Gun icon | Top left: yellow gun 1 "100/300" (rifle), blue gun 2 "180/300" (tazer), red gun 3 "28/150" (grenade launcher), yellow gun 1 for the Spargus citizen; none for the jetpack. Moved top right afterwards (below) |
| Gauges | The stock ring, no model; jetpack fuel at 0.62 in the dark eco gauge (purple); spider blue eco in blue and robotguard roll in red in the light eco gauge |
| Salvos | Jetpack: two shots 0.13 s apart, 0.8 s between salvos; robotguard: 0.13 s, then 0.9 s |
| Robotguard roll | 9 m/s walking, 14 to 16 m/s rolling for 1.2 s; the red gauge drained, then refilled from 0 to 1 in 5 s; R2 during the refill did not roll |
| Robotguard shield | Up while Circle was held; a guard shot heated it to 0.42, the second broke it into red shards; Jak's health stayed 16 |
| Spider | 14.9 m/s, 18 to 25 m/s with R2 held; Circle bit a guard 4.4 m away |
| Missions | Open task nodes: 15 before the battle, 0 during it, 15 after the load |
| Save | START menu: "Save Game" grey; X on it left the ring as it was |
| Load | Loading slot 1 during the battle: mode off, phase off, no director, no avatar, Jak at the save's place in `target-stance`, 8 stock blue guards |

A sixth run, Freedom League at the Port, checked the gun icon once moved into the stock gun HUD:
top right, yellow gun 1 with "100/300" and its shell column (rifle), blue gun 2 "180/300"
(tazer), red gun 3 "28/150" (grenade launcher), yellow gun 1 "99/300" for the Spargus citizen,
nothing for the jetpack; the gun HUD's values read back as gun 29, ammo 99, state `hud-in`.

A seventh round followed the author's third notes. One Freedom League run at the Port logged the
jetpack every 0.25 s; then one GIF run per side recorded every weapon of every class:

| Check | Result |
|---|---|
| Reserves HUD | Top middle: "500" in green and "498" in red under their bars, clear of the gun HUD |
| Vehicles and missions | `user-current pilot` #f during the fight; open task nodes 15 before, 0 during |
| Jetpack on the ground | Model 0.80 m above Jak, fuel refilling at 0.1 per second |
| Jetpack climb (X) | 6.0 m/s, fuel down 0.0625 per 0.25 s |
| Jetpack hover | From 17.89 m it settled at 17.54 m within 1.5 s and stayed; later held 10.4058 m for 4 s |
| Jetpack down (Circle) | 7.0 m/s |
| Out of fuel | 4.0 m/s down, landed, model 0.80 m above the ground |
| GIFs | Blue and red guard: rifle, tazer, grenade, rifle butt; jetpacks: climb, salvos while hovering, Circle down, dive kick; Spargus citizen: rifle, rifle butt; robotguard: salvos, shield, roll, punch; spider: sprint, leap, bite |

Found and fixed in these runs: the hover sank a step every second (Jak's `on-surface` flag),
fixed by the ground probe test (§2.6).

An eighth round followed the author's fourth notes. One run per side logged the shots, the close
attacks (Square or Circle tapped every 0.15 s for 3 s), the grenades and the jetpack's clip
changes; then the seven GIFs were recorded again:

| Check | Result |
|---|---|
| Rifle cadence | R1 held 2.5 s: a shot every 150 ticks (0.5 s), blue guard and Spargus citizen |
| Grenade after a rifle shot | Red guard: red ammo 33 to 32 and one more grenade in flight, 0.6 s after the rifle shot; blue guard: 28 to 27 |
| Close attacks | Blue guard and Spargus: clip end at 1.0 s, next attack at 1.05 s; red guard, robotguard, spider: clip end at 0.22, 0.18 and 0.38 s, next attack at 0.6 s |
| Jetpack clip | 4 s hovering: 1 clip; moving: hover to forward flight once; 3 s of salvos: no change (before: the firing clip on and off every 0.4 s) |
| GIFs | The guards' grenade now flies and bursts in both guard GIFs |

Before this round the GIFs never showed a grenade: the clip pressed R1 within a second of the last
tazer tick, and the grenade launcher shared the rifle's and the tazer's timer.

A ninth round followed the author's fifth notes. One Krimzon Guard run, repeated after each fix,
logged the jetpack's drawn model, the robotguard's shield and punch and the spider's clips:

| Check | Result |
|---|---|
| Zone pages | The four zones and the side page on the world map, the spawns on the streets, the circle around them |
| Jetpack | Drawn model on Jak's height of that frame at every frame of a climb (gap 0.0000 m, Jak moving 0.10 to 0.19 m a frame) |
| Robotguard shield | Circle tapped: no shield 0.1 s later; held: up, R1 fired nothing, R2 did not roll, the stick moved it 0.1 m/s, X did not jump; let go: gone |
| Robotguard punch | Wind-up, punch, back: clips at 0, 0.20 and 0.40 s, idle at 0.93 s; a guard 5.3 m away went from 6 to 2 health |
| Spider | Half stick: walk; full stick: run; R2: run; no clip change within 0.25 s, no jump clip on flat ground |
| GIFs | All seven recorded again; the menu GIF from the four zone pages and the side page |

Found and fixed in these runs: a speed multiplier of 0 under the shield (the game crashed once,
Jak walking with it; Jak's surfaces scale their speeds by it and his walk divides by them), now
0.01; the spider's clips flipping between idle and walk against a wall.

A tenth round followed the author's sixth notes. Freedom League runs at the Port, the menus driven
by pad, logged the START menu's page after each press, the guard's magazine and clips frame by
frame, the units awake every 2 s, and two deaths:

| Check | Result |
|---|---|
| Mods menu | L1 + SELECT opened and closed it (bind `#x401`); Battlefront mode on: START > Options went from 5 to 6 entries, Gamemode last; off out of a battle: 5 again |
| START pages | Options, down to Gamemode (option 5), X: the Gamemode page; X: the Battlefront page; X on New battle: the START menu closed and the war zone page opened |
| Zone pages | The four zones on their own minimap textures, the spawns on the streets |
| Units | Up to 17 Freedom League and 14 Krimzon Guard awake, Jak at the battlefield's edge included (12 per side before) |
| Force field | Jak running outward for 3 s held at 148.11 m of a 148.30 m radius |
| Guard rifle | R1 held: 6 shots 0.5 s apart, then `grenade-reload` and `cock-gun` on the upper body (2.0 s), then shots again; firing while walking: legs on `walk`, upper body on `gun-attack` |
| Guard grenades and tazer | 2 grenades, then the reload; the tazer's thrust held while its arc lasts |
| Death | Jak in his death state 4 s, the camera on a blue guard of his side, "YOU WERE KILLED", "Back in 4" to "1"; then at his spawn (0.02 m away), 16 health, his class drawn, his side's loss counted; 20 of 21 units the same processes before and after |
| Change class | START > ... > Battlefront > Change class: the class page, class 0 to 1, the fight and its reserves going on |
| Restart, Quit | Restart: 500 / 500 at once, the deployment, then the fight with the same class; Quit: the battle off at once |
| Mode off in a battle | The save loaded at once (a second `AUTO SAVE COMMAND restore` in the log), Jak back at the save's place, mode off, START > Options at 5 entries |

Found in these runs: the test's own navigation (the generic pages read no input while the menu
moves, and keep the line of the last visit), and the test save's invulnerability secret, which
refuses plain attacks (the death test sends `'attack-invinc`).

Two proof runs then played a battle in each of the four zones, each started from START > Options >
Gamemode > Battlefront and ended with Quit: the zone page's map, the units awake every 0.5 s for
30 s with Jak at his spawn, the force field in four directions (Jak put 3 m inside the edge, running
outward 3 s with a jump), a death, and in the Port the guard's clips frame by frame. The second run
had the reinforcement retries and the clip wait (§2.2, §2.4); both ran with no crash.

| Check | Port | Industrial Zone | Slums | Freedom HQ |
|---|---|---|---|---|
| Minimap texture: the game's for the battlefield's center cell, the HUD minimap's with Jak there, the zone page's | `map-ctyportc`, all three | `map-ctyinda`, all three | `map-ctysluma`, all three | `map-ctyslumc`, all three |
| Zone page's drawn map against each zone's texture (correlation of the pixels) | 0.978 own, 0.29 at most others | 0.970 own, 0.37 | 0.957 own, 0.38 | 0.927 own, 0.19 |
| Units awake, most per side (Freedom League / Krimzon Guard), first run | 19 / 20 | 20 / 20 | 20 / 20 | 20 / 20 |
| Units awake, most per side, second run (samples at 20 of 60) | 20 / 20 (14 / 8) | 20 / 20 (45 / 58) | 20 / 20 (24 / 32) | 20 / 20 (38 / 44) |
| Force field: farthest past the edge in four directions, both runs | -0.03 m (inside) | -0.02 m | -1.28 m | -0.0004 m |
| Death: 4 s on a unit of the side, back at the spawn (0.00 to 0.02 m), 16 health, units the same processes | 26 of 32 | 30 of 32 | 22 of 32 | 27 of 32 |

Guard, Port (standing fire 4 s, walking fire 3 s, running fire with a jump, a rifle butt, the
grenade launcher 4 s, the tazer): the reload clips started 6 times (3 reloads), each with the
weapon's magazine at 0; the legs' clip changed 14 times in the first run, 2 of them at once (no
blend), and 13 times in the second, all blended.

An eleventh round made each war zone a whole district (§1, §2.2, §2.6) and proved it in two final
runs, each battle started from START > Options > Gamemode > Battlefront and ended with Quit, Jak a
blue guard of the Freedom League. In each district every stock continue point of its sections was
reached: Jak grabbed, held 1 s at the point and released, then four 3-second runs from it, north,
east, south and west, with a jump. Then three edge runs, 8 s outward from the district's middle;
a teleport to a point of the next district; the units awake every 0.5 s for 20 s at the camp; a
death. The demo GIFs of the README are those runs (the camp's run, then the first run from four
points).

| Check | Port | Industrial Zone | Slums | Freedom HQ |
|---|---|---|---|---|
| Continue points stood on in the zone, with ground | 9 of 9 | 9 of 10: at `ctyinda-start` Jak landed 2.7 m below the point, then ran in all four directions | 5 of 5 | 8 of 9: at `ctyslumc-burning-bush` he fell into the water 9.9 m below |
| Runs from the points stopped by the field, ending out of the zone | 0 of 36, 0 | 0 of 40, 0 | 0 of 20, 0 | 0 of 36, 0 |
| Edge runs ending in the zone | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 (from the burning bush, 12 sparks: the field held him over the water) |
| Teleport to the next district's point | back at once (`ctyinda-bbush-5`) | back at once (`ctyport-bombbot`) | back at once (`ctyslumb-bbush-3`) | back at once (`ctysluma-bbush-1`) |
| Units awake, most per side, samples at 20 of 40 | 20 / 20 (35 / 39) | 19 / 20 (0 / 40) | 19 / 21 (0 / 26) | 20 / 20 (40 / 39) |
| Units awake on another section's lanes | 0 | 0 | 0 | 0 |
| Death, then back at the camp standing | yes | yes | yes | yes |

Krimzon Guard battles in the Port and the Industrial Zone: the deployment at the camp
(`ctyport-bombbot`, `ctyinda-bbush-5`), the teleport into the next district (back at once), a
death after a trip to the other camp (back at the camp standing: 0.15 m and 0 m away). A walk from
the Port's war zone toward the Industrial Zone met a wall 34 m on, still in the Port's cells.

Found on the way, all fixed: hidden under the class model, Jak fell through the ground after a
teleport at 5 of the Port's 9 points (his bones' math skipped, §2.4); the battle's level filter
hung the respawn of a camp whose list named another level; the stock loading of the Port took
`mhcitya` instead of `ctyinda` for a respawn at the war zone (the camp moved); and the game kept
seeing Jak in the Port while he stood in the Industrial Zone (the minimap cell test). The test's
own teleport first left Jak swimming in the air (he had ended a run in the water) and took the
field's safe place from his old spot: it now grabs him and sets the safe place after.

Found and fixed in the earlier runs: a texture upload into a bucket the PC renderer wants empty (the save pictures, `bf-picture-set!`), a freeze from a DMA bucket opened inside another (the gun icon), a gauge hidden behind the ring (now drawn in the stock gauge sprites), and a shield that died at once (its art level).

The game's output also shows `call_method_of_type failed` lines ("has invalid type ptr"): the
kernel prints an object through its type and calls any type above 128 MB invalid, while this
build's level heaps sit above it (`engine-internals` skill). They come with the stock warning
"could not do (ja-channel-push! 1) because it has 5/6 channels" of a unit whose code is level
code (its name cannot be printed); the object is sound.

### 3.2 Troubleshooting

| Symptom | Cause |
|---|---|
| A red guard or a jetpack guard is invisible or untextured | `task extract` not run since the models changed |
| `multiple ways to make output out/jak3/obj/bf-...-ag.go` | the `*file-entry-map*` pre-marks are missing from `game.gp` |
| `dgo file header ... has overrun heap` while loading Haven City | art groups of `ctypesa.gd` / `ctypesc.gd` no longer sorted by decreasing size |
| "battlefront: the war zone did not load" in the console | ctypesa or ctypesc never became active within 60 s |

---

## 4. Status and known limits

- **Little hand play.** The author played the second round once; everything since was checked by
  automated runs (§3.1). The feel of each class (camera, free aim, balance) needs a player, and
  battles longer than ten minutes were not run.
- **Earlier builds crashed in long battles.** Each cause found was fixed (§5): the shadow
  buffers, the avatar flood, the Spargus citizens in the traffic, the forced guard weapon, a
  process-tree walk in a unit's init, the red guards' death effect (§2.4). Crashes whose cause was
  not identified could remain; a crash ends the game with no message (exit code `0xC0000005`). A
  temporary vectored exception handler in the runtime names the faulting GOAL function, or the
  runtime module and offset of a native one (`smoke-tests` skill, game-control).
- **20 per side is a ceiling, not a constant.** Each zone reached 20 per side, held for 8 to 52 of
  60 samples of 30 s (§3.1); in the eleventh round's last runs the Freedom League stayed at 19 in
  the Industrial Zone and the Slums for the 20 s watched. A unit that dies counts until it has
  left, and its replacement wakes on the next reinforcement, so the count dips below 20 in a heavy
  fight.
- **Hit rate of some attacks.** The spider's pounce and the citizen's rifle butt missed a moving
  foe in some runs: they only reach a foe still within range when Jak arrives.
- **The zone minimaps are carried texels.** Generated from the user's decompiled minimap textures
  (Naughty Dog assets, like the models), 4 m a texel: soft once framed on a battlefield. A new war
  zone needs the script run again.
- **A death leaves Jak where he fell, hidden,** until the respawn: a unit can still bump into him,
  and the stock death's movies and its reset of the area do not happen during a fight.
- **A mission already running stays open** during a battle (the `exclusive-task` setting closes the
  others); the battle does not stop it.
- **The robotguard shield's sounds may be silent:** its stock sounds are in level banks that Haven
  City does not load.
- **No aim assist.** A shot needs the crosshair's line of sight to touch a unit's collision; only
  the tazer aims by itself. The camera's speeds, distance and shoulder offset are the author's to
  tune by hand (`battlefront-player.gc` BF_YAW_RATE and `bf-cam-rig-update`).
- **Hidden Jak runs, the class walks.** Jak, hidden, turns toward where he runs; the class model
  faces the camera's heading, turned 50 degrees at most toward its walk. The guards and robots
  have no sideways walk clip: a sideways walk is their forward walk turned that way.
- **The red guards die without the dissolve:** their death effects are skipped (§2.4), the
  build-actor models have no data for the renderer path the dissolve takes.
- **The class models over the game are lit by the place.** The preview and the health icon are
  drawn with the world, a few meters in front of the camera: the level's lights color them, and
  scenery nearer than that can cover them. With the icon, the health HUD keeps only its pips.
- **The ammo is Jak's.** The battle spends and refills Jak's gun ammo and gives it back at its end;
  a save made during a battle keeps the battle's amounts. Without the scatter gun or the vulcan,
  the red and blue pickups turn yellow (stock `verify-pickup-type`).
- **Symbol names in logs.** In a retail boot the game's own name of a symbol (printed with `~A`,
  e.g. the master mode) can come out garbled after level loads: the kernel keeps some names in the
  top of the global heap, which DGO loading reuses. The values are right; only printing is
  affected.
- **Jetpack guards fly on the flying-turret code:** they explode into KG robot debris, and the
  turret's aim joint mod pitches their chest. A direct blow (`bf-send-attack`) on one in flight
  took nothing in a smoke run: the close attacks reach the ground units.
- **Classes are drawn over Jak:** hits, health and death are Jak's; the class model only follows him.
  The Robotguard's roll, the dives and the leaps are Jak's own physics with a changed speed or
  velocity, not the robots' own movement code.
- **The tazer's baton is the guard's weapon drawn smaller,** not a model of its own (§2.8).
- **Zones are Haven City districts only.** Spargus would need the city's unit code and art in WWD
  (the battle-of-spargus mod does it for the guards).
- **A two-section district holds its own sections only.** In the Industrial Zone and Freedom HQ
  no other section, interior or mission level loads during a battle (Haven City holds two
  sections at most): a continue point whose list names another level cannot be a camp there (a
  respawn would wait for ever).
- **Nothing is saved:** the battle ends with the session.
- **The Jak 2 models are Naughty Dog assets** converted from the user's rips: the mod repository is
  meant to stay private.

---

## 5. Change log

| Date | Touched/Created Files | Technical Description | Objective |
|---|---|---|---|
| 2026-11-04 | `battlefront-h.gc`, `battlefront-player.gc`, `battlefront.gc`, `battlefront-city.gc`, `guard.gc`, `guard-grenade.gc`, `ctypesa.gd`, `jak3_config.jsonc`, `README.md`, `docs/img/mod/spargus.gif` (removed) | Red guards (AI and avatar) play the blue guard's clips (`bf-guard-clips`), units told by their skeleton (`bf-art-name`); the spider's walk and run follow its speed (`bf-avatar-loop-rate`); pickups 27 % instead of 67 %; a third-person camera held by the avatar (`bf-avatar-camera`); damage scaled by class (`*bf-class-damage*`: guards 8 hits, jetpacks and spider 6, robotguard 16); the Spargus Citizen class removed, with its code and art in CTYPESA and the decompiler config; grenade guards break off a reload for the player only (`bf-reload-break-ok?`, Lisp wiki jak3 4.40). `traffic-engine.gc` asks `bf-keep-unit?` (CWI code) during a fight only: the file also runs in Spargus, where calling it, undefined there, crashed the game at boot with a save in Spargus (seen twice). Compiled; a smoke run (Port, mode on, 4 minutes) showed red guards on the blue guard's clips and no crash; the battle itself could not be started from the test scenario, so the camera, the damage by class, the spider and the pickups are not checked in a fight yet. | The author's round 12 goal: animations, spider legs, rarer pickups, a Battlefront camera, health by class, no Spargus Citizen. |
| 2026-11-01 | `battlefront-h.gc`, `battlefront-player.gc`, `battlefront.gc`, `battlefront-minimaps.gc`, `battlefront-city.gc`, `traffic-engine.gc`, `scripts/battlefront/make_minimaps.py`, `README.md`, `docs/img/mod/zone-port.gif`, `zone-industrial.gif`, `zone-slums.gif`, `zone-freehq.gif` (new) | War zones are whole districts: the Port, the Industrial Zone (`ctyinda`, `ctyindb`), the Slums (`ctysluma`), Freedom HQ (`ctyslumb`, `ctyslumc`), with new camps at their ends and maps of the whole district. Force field on the game's level of the player (vis-nick), the district's minimap cells (`bf-zone-cell?`, `*bf-zone-cells*`) and a 20 m fall, putting him back at his last safe place. Loading: the stock one in a one-section district, the two sections kept in a two-section one (`bf-want-zone-levels`, an `add-borrow-levels` wrapper). Reinforcements and units kept out of view on the district's lanes only (`bf-city-zone-branch?`, `bf-keep-unit?` moved to `battlefront-city.gc`, the stock hook passes the unit). A respawn wants its camp's levels and waits for them (`bf-want-camp-levels`). Jak's bones computed while he is hidden (`bf-target-bones!`): he fell through the ground after teleports. Verified in game in the four districts and at both sides' camps (§3.1). | The author's note: each zone must be its whole district, tested in each with a demo GIF. |
| 2026-11-01 | `battlefront-h.gc`, `battlefront-player.gc`, `battlefront.gc`, `battlefront-minimaps.gc` (new), `traffic-engine.gc`, `game.gd`, `scripts/battlefront/make_minimaps.py` (new), `README.md`, `docs/img/mod/menu.gif` | Mods menu on L1 + SELECT, with the mode's switch alone; START > Options > Gamemode > Battlefront (new battle, change class, restart, quit), labels through a `lookup-text!` wrapper; the mode switched off in a battle loads the last save; zone pages on each zone's own minimap texture; armies of 20 per side, the battlefield's units kept awake out of the camera's cells (`bf-keep-unit?`); guard magazines (6 rifle shots, 2 grenades), a reload only when one is empty, the weapon clips on the upper body (`top-anim`), every clip change blended (`anim-wait`); reinforcements of up to three units a tick with retried spawns; a death watches the battle 4 s on a unit of the side, then respawns at the spawn as the same class, with no reset of the city. Verified in game in the four zones (§3.1). | The author's sixth notes. |
| 2026-11-01 | `battlefront.gc`, `battlefront-player.gc`, `README.md`, `docs/img/mod/menu.gif`, `blue-guard.gif`, `jetpack.gif`, `spargus.gif`, `red-guard.gif`, `red-jetpack.gif`, `robotguard.gif`, `spider.gif` | Zone and side pages on the game's world map of Haven City framed on the battlefield (`bf-zone-view!`, `bf-draw-zone-minimap`, `bf-draw-zone-marks`); the save picture, the lane map and its stored lanes removed. The class model placed again after the camera (`bf-avatar-cam-post`). Robotguard: full punch (three clips, 6.5 m), standing still behind its shield (no move, jump, roll or shot). Jump clip only when clearly airborne; walk and run with slack; 0.25 s per locomotion clip. Verified in game (§3.1). | The author's fifth notes. |
| 2026-11-01 | `battlefront-player.gc`, `docs/img/mod/blue-guard.gif`, `jetpack.gif`, `spargus.gif`, `red-guard.gif`, `red-jetpack.gif`, `robotguard.gif`, `spider.gif` | Rifle every 0.5 s (guards, Spargus citizen). The grenade launcher on its own timer (`grenade-time`). A close attack holds its clip to its end (`ja-done?`), the next one waits for it, and for a dive kick's end. The jetpacks' clip by speed only, with slack, never the firing clip. GIFs recorded again (the grenade flies). Verified in game (§3.1). | The author's fourth notes. |
| 2026-11-01 | `battlefront.gc`, `battlefront-player.gc`, `battlefront-h.gc`, `README.md`, `docs/img/mod/hud.png`, `blue-guard.gif`, `jetpack.gif`, `spargus.gif` (new), `red-guard.gif`, `red-jetpack.gif` (new), `robotguard.gif`, `spider.gif` | Reserves HUD after Star Wars Battlefront (2004) (`bf-draw-reserves`), the zone and class line removed. Jetpacks: X climbs, Circle comes down, neither hovers still (`hover-y`), slow descent out of fuel, model 0.8 m above Jak; landing tested against the ground probe. `'pilot` #f during a battle: no vehicle. One GIF per class showing each of its weapons. Verified in game (§3.1). | The author's third notes. |
| 2026-11-01 | `battlefront.gc`, `README.md`, `docs/img/mod/hud.png` | The class's gun in the stock gun HUD, top right, with its shells and ammo count: a `hud-gun` `update-values!` wrapper feeds it the gun and ammo during a fight; the mirrored copy of its sprites top left, its white count and the unused `bf-weapon-name` removed. Verified in game (§3.1). | The author's note: the gun where the original game puts it, with the same ammo view. |
| 2026-11-01 | `battlefront-h.gc`, `battlefront-player.gc`, `battlefront.gc`, `hud-classes.gc`, `gun-util.gc` (hook removed), `README.md`, `docs/img/mod/menu.gif`, `class.gif`, `hud.png`, `blue-guard.gif`, `jetpack.gif`, `red-guard.gif`, `robotguard.gif`, `spider.gif` | HUD: the stock gun icon of the weapon in hand top left with its ammo, no weapon name, no class model in the ring, the class gauge in a stock eco gauge through a hook in `hud-health` draw (jetpack dark, spider blue, robotguard roll red). Robotguard: R2 roll with a 5 s recharge, shots and blasts stopped while it rolls, Circle the Dark Makers' red shield sphere (`bf-shield`), which breaks under fire, R1 salvos of two shots. Jetpacks: salvos of two shots, 0.8 s apart. Jetpacks and robotguard spend no ammo. Spider: x1.5, R2 blue eco x2, Circle bite. Jak no longer playable. Zone and side pages: the save menu's picture above the map (`*bigmap*`, menu texture mask). Outside the campaign: `exclusive-task` none, Save grey and refused, a load ends the battle (`initialize!` wrapper). Endless light eco secret set aside too. Verified in game (§3.1). | The author's second set of notes. |
| 2026-10-31 | `battlefront-h.gc`, `battlefront-player.gc`, `battlefront.gc`, `gun-util.gc`, `README.md`, `docs/img/mod/menu.gif`, `class.gif`, `hud.png` | Free aim for every class: a ray from the camera through a fixed crosshair (`bf-free-aim`), followed by the class weapons and, through a hook in Jak's gun post, by Jak's gun; the tazer alone locks the nearest foe within 12 m. Jetpack: steady thrust until the fuel is gone, lift fading under the ceiling, no refill while X stays held after it ran dry, force field push only 2 m above the ceiling. Fuel and blue eco gauges in the health ring (HUD sprites 5 and 6). No citizens during a battle (`bf-want-count`). Dark eco drops (6 %) refill the jetpacks; Jak's dark eco and the endless dark eco secret set aside for the battle. Pages on black (renderer mask, other models hidden) and a zone map on the zone and side pages, with the lanes of each zone read in game (`*bf-lanes*`). English texts without ASCII apostrophes. Class models over the game placed again after each camera update (`bf-icon-cam-post`), so the health icon no longer trails a moving camera. Verified in game (§3.1). | The author's notes after their first play. |
| 2026-10-31 | `docs/img/mod/blue-guard.gif`, `jetpack.gif`, `red-guard.gif`, `robotguard.gif`, `spider.gif`, `README.md` | Class GIFs recorded again with the second round's HUD and moves (weapon change and tazer, fuel gauge, shield, blue eco sprint), same method (§3.1). | The README shows the mode as it is. |
| 2026-10-31 | `battlefront-h.gc`, `battlefront-city.gc`, `traffic-engine.gc`, `README.md` | Port stall fixed: the unit picker's count per territory (`activate-one-vehicle`) asks `bf-want-count`, and reinforcements (`bf-city-reinforce`) wake the battle's type furthest below its cap on a battlefield segment 30 m or more from the player, four times a second. Slums moved to `ctysluma-alley` / `ctysluma-bbush-2` and Main Town replaced by Freedom HQ (`ctyslumc-freehq` / `ctyslumc-bbush-2`): the first pairs had almost no unit lanes. Measured per zone in game: awake units, reserves, jetpack ceiling, force field (§3.1). | Battles that keep going in every zone. |
| 2026-10-31 | `battlefront-h.gc`, `battlefront-player.gc`, `battlefront.gc`, `battlefront-city.gc`, `traffic-manager.gc`, `README.md`, `docs/img/mod/menu.gif`, `class.gif`, `hud.png` | Class page after the deployment, with the class under the cursor turning in a frame (`bf-icon`, drawn with the world in front of the camera; the HUD model path crashed on build-actor models); guard weapons on the D-pad (tazer arc from the guards' lightning, rifle, guard grenades through `*bf-city-grenade*`); class weapons on Jak's ammo, saved and given back, topped up at each deployment; stock ammo and health pickups left by dead units; crosshair (`hud-gun-reticle`); health HUD kept shown with the class model among its pips; jetpack fuel gauge (4 s, refilled in 10 s); spider blue eco sprint; robotguard shield (Light Jak's, `target-attacked` wrapper lets blows through); army caps of 12 per side (`bf-want-count` in `traffic-manager-method-22`, look shares); force field and jetpack ceiling replacing the countdown on foot; avatar `relocate` for the tazer arc; class model heights from the rips. | The second request of the mod's author: weapons, ammo, crosshair, HUD, gauges, shield, caps, force field. |
| 2026-10-31 | `README.md`, `docs/img/mod/*.gif`, `docs/img/mod/victory.png` | README gallery recorded in game: a retail boot with a temporary scenario file (not part of the mod) saved one frame in four at 640x360 with `pc-screen-shot`, and ffmpeg assembled them at game speed (480 px, 64 colors, no dither). The recording runs found the Port stall of §4. | Show the mode to players. |
| 2026-10-31 | `battlefront-h.gc`, `battlefront.gc`, `battlefront-city.gc`, `guard.gc`, `wlander-male.gc` | Stability fixes from ten-minute battles: the AI Spargus citizens removed (they froze the game in `fill-bg-using-line-sphere-new`; `wlander-male.gc` stock again); the red guards keep the weapon the stock code gives (forcing it in `crimson-guard-method-267` crashed a weapon change); the looks of new guards and jetpack guards balanced from live counts made by the director (an alternation drifted to no blue guard; counting inside a unit's init crashed). | Long battles run clean. |
| 2026-10-31 | `battlefront-h.gc`, `battlefront-player.gc`, `battlefront.gc`, `battlefront-city.gc`, `Shadow2.cpp`, `Shadow2.h` | Fixes from the in-game runs: shadow buffers no longer stop the game in a crowd; Jak held at the spawn until he stands, and put back after a fall; avatar and director handles in `*bf*` (no avatar flood, class page after a death); player respawned like a death (`initialize!` 'life) at both ends of a battle, so every unit pool is spawned again (battle's skins, then stock skins); spider jump pushed up during its rise; dive and pounce steered to the foe; avatar blend channels capped; menu panel and text in one buffer, centered text, wrapped descriptions, PC text language, no ASCII apostrophe in French; HUD and losses line resized. | The mod works in game as specified. |
| 2026-10-31 | `README.md`, `index.json` | Mod branch prepared from master-dev by `create_mod_repo.py --prepare-only` (repository not published). | Start the mod. |
| 2026-10-31 | `battlefront-player.gc`, `battlefront-h.gc`, `make_models.py`, `ctypesa.gd`, `game.gp` | Square attack for every class from its unit (rifle butt, punch, dive kick, pounce), the roboguard roll on L1; a second red guard model with the grenade launcher, given to one red guard in two (grenadier). Review fixes: handles for the avatar and the director, `*popup-menu-open*` while the battle menu is up, hatred written every frame, avatar mesh segments, end of battle deferred while Jak drives. | Each class uses its unit's moves and attacks; red guards fight with both weapons of the Jak 2 guard. |
| 2026-10-31 | `battlefront-h.gc`, `battlefront-player.gc`, `battlefront.gc`, `battlefront-city.gc` (new)<br>`traffic-engine.gc`, `guard.gc`, `flying-turret.gc`, `wlander-male.gc`<br>`game.gd`, `cwi.gd`, `ctypesa.gd`, `ctypesc.gd`, `game.gp`, `jak3_config.jsonc`<br>`scripts/battlefront/make_models.py`, `custom_assets/jak3/models/**/bf-*.glb` (new) | First version: Mods menu entry, three-page battle menu (English/French), four Haven City war zones, reserves of 500 per side, loss counting on unit and player deaths, result page, battlefield bounds; Jak 2 red Krimzon Guard on the stock guard code and Jak 2 jetpack guard (red and blue) on the stock flying-turret code; Spargus citizens in Haven City; eight playable classes drawn over Jak with their own moves and R1 weapons. | The Battlefront mod as specified. |
