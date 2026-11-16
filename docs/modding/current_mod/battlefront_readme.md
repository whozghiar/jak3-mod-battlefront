# Battlefront — developer guide

This guide explains how the Battlefront mod for Jak 3 works, for developers and agents who change
it: the ideas it rests on, how a battle runs, where the code lives, which engine limits it raises
and how to test it. Players read the root [`README.md`](../../../README.md); the smoke tests are in
[`battlefront_tests.md`](battlefront_tests.md).

**Contents:** [1. The idea](#1-the-idea) · [2. Key notions](#2-key-notions) ·
[3. How a battle runs](#3-how-a-battle-runs) · [4. Files](#4-files) ·
[5. Engine limits](#5-engine-limits) · [6. Build and test](#6-build-and-test) ·
[7. Known limits](#7-known-limits)

---

## 1. The idea

Jak 3's Haven City already runs a war. Its **traffic engine** spawns Freedom League guards and
Krimzon Guard robots in the streets, and its **attack controller** makes each one fight the other
faction. The mod writes no AI of its own. It borrows that machinery and adds what a Battlefront
game needs:

| Battlefront needs | The mod gives it |
|---|---|
| Two armies | The city's own units, two of them dressed as Jak 2 models (§2.2) |
| A battlefield | Jak 2's Haven City, rebuilt as one Jak 3 level from the player's discs (§2.8) |
| Objectives | Headquarters and control points that units capture (§2.5) |
| Reinforcements | Troop transports and drops from the sky at held points (§2.6) |
| A soldier to play | Jak, hidden, with a unit's model, moves and weapons drawn over him (§2.4) |
| A game around it | Menus built as pages of the game's START menu (§2.9) |

Everything ships on by default: the mode's switch (`*mod-battlefront-enable*`, `battlefront-h.gc`)
starts `#t` at every boot and is not saved. Switching it off in the Mods menu (L3 + SELECT) gives
the stock game back until the next boot.

## 2. Key notions

### 2.1 The director and the battle state

One process, `bf-director` (`battlefront.gc`), runs the whole battle. It lives in `*pc-pool*`, so it
survives level changes and Jak's deaths. The battle's data sits in one static structure, `*bf*`:
the phase, the reserves, the points, the player's class, his respawn point, and the handles of the
director and of the class model.

The battle moves through four phases (`BF_PHASE_*`, `battlefront-h.gc`):

| Phase | What happens |
|---|---|
| `off` | No battle. Every hook the mod placed in stock code answers like the stock game. |
| `deploy` | The war zone loads under the class page; Jak waits at the spawn until he stands on solid ground. |
| `fight` | The battle runs: points, reinforcements, HUD, the class model. |
| `over` | The result page; X goes back to the title menu. |

> [!IMPORTANT]
> Keep a process as a **handle**, never as a pointer, across frames. Processes live in dead-pool
> heaps that compact and reuse their slots, so a stale pointer names another process. A global
> symbol holds only 32 of a handle's 64 bits, so the handles live in `*bf*` fields.

### 2.2 Units are the city's traffic

A unit of the battle is a citizen of Haven City's traffic. Three ideas explain how the mod drives
them:

- **Pools.** The traffic keeps one pool per unit type. A pool spawns its processes once; a unit
  that dies goes back to sleep in its pool and comes out again later. It is never respawned, so
  its look is chosen once, when the pool spawns it.
- **Asleep or awake.** A sleeping unit costs nothing. The traffic wakes units onto the streets near
  the camera and puts them back to sleep when they leave its view. During a fight the mod wakes
  them itself (§2.6) and keeps them awake wherever the camera looks (`bf-keep-unit?`).
- **Caps.** Each pool has a `want-count`, rewritten every frame by `traffic-manager-method-22`.
  The mod's one-line change there asks `bf-want-count`, which returns the battle's caps
  (`*bf-pool-caps*`) during a fight.

| Unit | Process type | Pool | Side |
|---|---|---|---|
| Blue guard | `crimson-guard` | `guard-a` | Freedom League (stock) |
| Red Krimzon Guard (Jak 2 model) | `crimson-guard` | `guard-a` | Krimzon Guard: registers as a robot, so the stock hatred sends it against the guards |
| Blue jetpack guard (Jak 2 model) | `flying-turret` | `flying-turret` | Freedom League: registers as a rifle guard |
| Red jetpack guard (Jak 2 model) | `flying-turret` | `flying-turret` | Krimzon Guard |
| Robotguard | `roboguard-city` | `roboguard` | Krimzon Guard (stock) |
| Spider robot | `spydroid` | `spydroid` | Krimzon Guard (stock) |

Two sides share the `guard-a` and `flying-turret` pools. Each new process takes the look furthest
below its share (`*bf-look-share*`, `bf-guard-skel-name`, `bf-turret-skel-name`), from counts the
director makes every frame. The setup's **units at once** sets the caps (`bf-caps-set!`): at 100,
the Freedom League fields 72 guards and 28 jetpacks, the Krimzon Guard 40 red guards, 20 jetpacks,
20 robotguards and 20 spiders.

**Reserves and losses.** The setup's **units per side** (500 by default) are the reserves, the
Battlefront tickets. A unit really dies once, in `traffic-tracker` `set-process-to-killed`
(`traffic-engine.gc`), which calls `bf-unit-killed`: the loss is counted there, and a pickup may be
queued (`bf-queue-drop`, spawned later by the director: the unit's death runs on the traffic
manager's small stack).

**Speed.** Every unit moves faster than the stock one: its walk and run speeds and its clips'
ground per cycle are scaled together (`*bf-unit-pace*`), so the legs keep pace with the body.

**Units at NaN.** The stock unit code assumes it fights the player. In unit-against-unit fights a
jetpack's turn could become NaN, then its shots, then the guards those shots knocked: a unit at NaN
never dies and keeps its side's place. `bf-hover-turn-fix!` mends the jetpack's turn, and
`bf-city-nan-sweep` puts any unit at NaN back to sleep.

### 2.3 Sides, targets and damage

**Who fights whom.** The attack controller (`cty-attack-controller.gc`) picks each unit's target
from a hatred table indexed by unit type. During a fight `bf-city-apply-hatred` writes the battle's
table every frame (the stock game rebuilds it at each reset), and twice a second
`bf-city-retarget` makes units look again: the nearest foe they can see, a foe within 40 m stopping
their march. A thin background probe from the unit's eyes to its foe (`bf-city-sees?`) passes over
a foe behind a wall. The player's own side never targets him.

**One 24-point scale.** Every class and unit has its health in points (guards and robotguards 24,
jetpack guards 18, spiders 12) and every attack its damage in points (rifle 8, grenade 20, tazer
24, blow 10). Two wrappers turn points into the game's units:

- For units, a `damage-enemy-from-attack!` method on `nav-enemy` takes the attack's share of the
  unit's hit points, nothing from a unit of the same side, and counts the player's kills.
- For the player, the `target-attacked` wrapper refuses his own side's attacks and scales the
  others to Jak's health.

The player's shots and blows deal twice a unit's (`BF_PLAYER_DAMAGE`).

### 2.4 The player is Jak in disguise

The player stays Jak: his collision, physics, health and death are Jak's. A class only changes how
he looks and moves.

- **The class model.** `bf-avatar` (`battlefront-player.gc`) draws the class's model in Jak's place
  and hides Jak (`no-draw`). It runs before Jak in the frame, so it places itself again once he
  has moved (`bf-avatar-cam-post`, a camera-post hook), or it would trail one frame behind.
- **The moves.** The class speed goes through the `speed-mult` setting; jetpack flight, the spider's
  leap and sprint and the robotguard's roll are changes to Jak's velocity. A guard's dodge and roll
  send Jak the stock `'launch` event.
- **The camera.** `bf-cam-rig` drives the stock point-of-view camera (`cam-pov`, the one the
  city's sniper turret uses) from a bone it moves itself: behind the class's right shoulder, turned
  by the right stick.
- **The aim.** `bf-free-aim` casts a ray once a frame from the camera through the crosshair, 80 m
  long; the class weapons fire at the point it hits. Only the tazer locks a foe by itself.
- **The weapons.** Rifle shots are stock `guard-shot`s with Jak as their parent, grenades the guard
  grenade, the jetpack's rocket and the robotguard's grenade a `guard-shot` dressed as the dark and
  red guns' projectiles (`bf-rocket`, `bf-grenade`). The guard weapons spend Jak's own gun ammo, so
  the stock ammo pickups refill them; the battle saves Jak's ammo at its start and gives it back at
  its end.
- **The HUD.** It reuses the stock pieces: the gun HUD (fed by an `update-values!` wrapper), the
  health ring's eco gauges for the class gauge (`bf-hud-health-gauges`, called from `hud-classes.gc`).
  The reserves meter, the crosshair, the rocket and grenade icons and the maps are drawn by the mod.

Its settings (`gun`, `board`, `darkjak`...) belong to the avatar and leave with it, so Jak gets his
moves back when it goes.

### 2.5 Points and victory

Each side has two **headquarters**, held for good, and each of the 13 other districts has a
**control point**, neutral at the start, lettered A to M from the palace to the slums. Four times a
second `bf-update-points` counts each side's units within `BF_POINT_RADIUS` (35 m): the side with
more units captures the point in `BF_CAPTURE_TIME` (30 s); a neutral point goes faster the larger
the majority, down to `BF_CAPTURE_MIN_TIME` (10 s). Each point shows as a beam of light in its
holder's color.

`bf-check-victory` ends a fight: every control point held for 20 s (`BF_HOLD_WIN`, the **Control
points** condition), the time limit (more points wins, then more units), or a side out of units.

### 2.6 Reinforcements

A side's new units come down where it holds ground, as Battlefront's armies come from their
command posts:

| Where | How |
|---|---|
| A headquarters | A troop transport hovers over it (`bf-transport.gc`, Jak 2's drop-ship ported from the mod Haven City: New Dawn). It wakes a sleeping unit of its pool and sends it out through the stock `exit-transport` state: a guard jumps, a robotguard rolls out as a ball, a spider drops, a jetpack flies. |
| A held control point | No ship: the unit appears 30 m up over a nav poly within 250 m of the point (`BF_SPAWN_REACH`, `bf-city-spawn-spot`) and falls onto it (`bf-city-spawn-tick`). |

Each try picks one of the side's headquarters and held points at random (`bf-transport-draw`) and
brings up to 3 units, each of the kind its side lacks most against its caps
(`bf-transport-next-kind`). A fallen unit's place stays counted for 5 s. One unit in four dropped
at a control point is **posted** there (3 at most) and guards it while foes come within 150 m.

### 2.7 How units find their way

The city's walking lanes are loops inside one district: a unit following them never reaches a far
point. So a unit away from its goal **marches over the nav meshes**, which join the districts:

1. **A goal.** `bf-city-unit-goal` gives each unit a point: a contested point within 350 m first,
   then the point it is posted on, else one its side does not hold, drawn at random by its process
   id and kept until its side holds it.
2. **The ways.** Every 10 s `bf-ways-build` searches, from each point's nav mesh, every mesh's links
   breadth first: each mesh keeps its link back toward the point (`*bf-ways*`). Meshes that touch
   without a link get a bridge (`bf-ways-bridges`).
3. **The march.** Twice a second `bf-march-plan` sets the unit's destination to the next link on its
   way; every frame `bf-march-apply` moves it onto the next mesh when it stands on the link. Within
   12 m of its point (`BF_MARCH_NEAR`) the unit walks the lanes around it instead.

### 2.8 The war zone: Jak 2's Haven City

**A Jak 3 level made at install.** The level port manifest
`custom_assets/jak3/ports/battlefront-havenj2/port.jsonc` tells `scripts/level_port` (copied from
the mod Haven City: New Dawn) how to merge Jak 2's city and its 15 districts into one Jak 3 level,
`bf-havenj2` (DGO `BFH`): background, collision, props, water, and the traffic's navigation (26 nav
meshes). Its code is Jak 3's city code, so the traffic engine, squads and attack controller come
with it. Jak 2's doors to the interiors are background in their closed pose, with a collision box.

**Nothing of Jak 2 is in git.** `task level-port` writes the level from the player's own Jak 2 and
Jak 3 extractions; a launcher install runs it. Without Jak 2 the port is skipped, `*bfh-built*` is
`#f` and the war zone page greys the zone.

**The units' levels.** The unit art lives in two borrowed levels, `ctypesa` (guards) and `ctypesc`
(jetpacks and robots). They borrow from their master level only, so `bf-zone-select!` makes
`bf-havenj2` their master for a battle and gives `ctywide` back at its end.

**The Jak 2 models.** `custom_assets/jak3/models/models.jsonc` tells master-dev's `mod_models` how
to build the red guard, the jetpack guards and the transports from the player's discs
([guide](../guides/models_from_the_discs.md)); `game.gp` builds their art groups with
`build-actor`, and `task extract` bakes them into `ctypesa` and `ctypesc`. The red guard plays the
blue guard's clips (`bf-guard-clips`), so the stock guard code drives it unchanged.

**The map.** The level port's `citymap` step lays Jak 2's minimap textures out into one picture
(`bf-havenj2-map.gc`, generated), drawn on the menus and on L3; the HUD's minimap shows Jak 2's
textures through a minimap page the level registers when it loads.

Jak 3's own city is still in the code (zone 0, its six street sections loaded at once), but the
war zone page no longer offers it.

### 2.9 Menus are pages of the START menu

Every battle page (title menu, war zone, setup, class, respawn, pause, result) is a page of the
game's START menu, the progress state `'battlefront`. Its one option (`menu-bf-page-option`) hands
the pad to the director (`bf-menu-input`), which draws the page inside the menu's ring
(`bf-menu-draw`). The title menu's options are replaced (`set-menu-options` wrapper), and START in
a battle opens the battle's pause page (an `activate-progress` wrapper).

**The battle never pauses.** Under every page of a fight the game keeps running
(`bf-live-update`): the menu's process mask is undone and pad 0 is hidden from the world
(`bf-input`) while the menus read it.

**Outside the campaign.** During a battle no mission starts (`exclusive-task` none), no vehicle can
be taken (`pilot` off), and Save, Load Game and Secrets are greyed and refused. A load or a new
game ends the battle first (`game-info` `initialize!` wrapper, `bf-stop-now!`).

## 3. How a battle runs

1. **Title.** START on the title screen opens the battle's title menu: Start a battle, Options,
   Quit.
2. **Setup.** The war zone, then the battle setup (`*bf-config*`): time limit, units per side,
   units at once, victory condition, side. Next starts a new game at the zone's continue point.
3. **Class and deployment.** The class page opens while the zone loads under it (phase `deploy`).
   `bf-caps-set!` sets the caps, the stock faction settings bring both armies, and Jak is respawned
   the way a death does (`initialize!` `'life`), so every pool spawns again with the battle's looks.
4. **Fight.** Start the battle puts the player in as his class, with a 3 s spawn shield. Every
   frame the director runs the city side (hatred, marches, drops), the class model, the points and
   the HUD.
5. **Death.** During a fight the code of Jak's `target-death` state is `bf-target-death`: his class
   dies its own way, the camera follows a living ally, then X respawns him at his respawn point and
   Triangle opens the Respawn page. He comes down from the sky (`bf-sky-drop!`), his controls back
   once he lands.
6. **Redeploy.** START > Redeploy opens the same page: free after 30 s out of combat
   (`BF_REDEPLOY_CALM`), one unit of his side otherwise.
7. **End.** The result page; X (or Quit the battle) calls `bf-to-title!`: a new game at the title's
   continue point, as the stock demo's return to the title does, so the whole game is reset.

## 4. Files

| File | Role |
|---|---|
| `goal_src/jak3/pc/features/battlefront/battlefront-h.gc` | `*bf*`, the tables (zones, points, classes, caps, texts in English and French) and every function the stock code calls into |
| `.../battlefront/battlefront-player.gc` | The class model (`bf-avatar`), its moves and weapons, the camera rig, the shield |
| `.../battlefront/battlefront.gc` | The director: phases, menus, points, HUD, deaths, respawns, the stock wrappers |
| `.../battlefront/battlefront-havenj2-info.gc` | Reads the generated Jak 2 level's load info and map at compile time |
| `.../battlefront/battlefront-icons.gc`, `-minimaps.gc`, `-portraits.gc` | Generated pictures: HUD icons, Jak 3's city map, class portraits |
| `goal_src/jak3/levels/city/battlefront/battlefront-city.gc` | The city side (CWI): hatred, goals, marches, drops, posts, NaN sweep |
| `goal_src/jak3/levels/city/battlefront/bf-transport.gc` | The troop transport (CWI) |
| `goal_src/jak3/levels/bf-havenj2/` | The Jak 2 city level's code; the rest of the folder is generated by `task level-port` |
| Stock files marked `;; MOD battlefront` | One-line hooks into the traffic, guards, turrets, HUD, minimap, loading, and the raised limits of §5 |
| `custom_assets/jak3/models/models.jsonc` | The Jak 2 models' recipe |
| `custom_assets/jak3/ports/battlefront-havenj2/port.jsonc` | The Jak 2 city's level port manifest |
| `scripts/battlefront/` | The generators of the icons, maps and portraits |
| `scripts/level_port/`, `decompiler/level_extractor/`, `goalc/build_level/`, `tools/fr3_check.cpp` | The level port tooling of the mod Haven City: New Dawn, which builds Jak 2's city as a Jak 3 level |
| `game/graphics/opengl_renderer/foreground/Shadow2.cpp` | A shadow that no longer fits the buffers is dropped instead of stopping the game |

`battlefront-city.gc` and `bf-transport.gc` are level code: they need Haven City's types, which only
CWI knows. The GAME files must work whatever level is loaded, so `battlefront-h.gc` defines every
function the level code calls, answering like the stock game outside a battle.

> [!WARNING]
> **Art-group order in `ctypesa.gd` and `ctypesc.gd` matters.** Keep each block sorted by
> decreasing size (sizes are in the comments). Out of order, loading Haven City prints
> `dgo file header ... has overrun heap`.

## 5. Engine limits

A battle of 200 units goes past several fixed sizes of the engine. The mod raises them:

| Limit | Stock | Mod | File | What overflowed |
|---|---|---|---|---|
| Frame's global DMA buffer | 1280 KB | 2560 KB | `engine/gfx/hw/display.gc` | Each drawn unit writes about 6.5 KB there, unchecked; 200 units in view filled 1.3 MB and corrupted the memory after it |
| Default nav mesh users | 128 | 255 | `engine/nav/nav-mesh.gc` | Every new pool unit holds one until it is first woken |
| Traffic tracker's awake list | 126 | 224 | `levels/city/traffic/traffic-engine-h.gc` | 100 units a side |
| Sleeping units per pool | 20 | 128 guards, 64 turrets | `levels/city/traffic/traffic-engine.gc` | A pool spawned a new unit every frame past 20 |
| Attack controller's attackers | 64 | 256 | `levels/wascity/cty-attack-controller.gc` | Units without one corrupted memory |
| Touching-prims records | 64 | 256 | `engine/collide/collide-touch-h.gc` | Crowds at the ships |
| Background trees per kind | 11 | 32 | `engine/gfx/background/background-h.gc` | Jak 3's whole city loaded at once |

Two constraints set the next ceiling, about 120 units a side:

- **The level heap must end below 256 MB** (above it, adgif shader links break). The DMA buffers are
  allocated before it, so they can only double, not quadruple as Jak 2's do. With 2560 KB the level
  heap ends at `#xf6eec00`.
- **Several counts are bytes.** The default nav mesh holds 255 users at most, and 160 to 200 are
  taken at the start of a battle at 100 a side; the robotguard and spider pools already fill their
  stock 20 sleeping slots.

The Lisp wiki records how to measure the DMA buffer's use from a process
([jak3.md, Memory](../../../.agents/skills/goal-lisp/wiki/jak3.md)).

## 6. Build and test

| Step | Command |
|---|---|
| Select the game | `task set-game-jak3` |
| Build every binary: the renderer, the level builder and the decompiler changed | `task build-release` |
| Build the Jak 2 models from the discs (`iso_data/jak2`, `iso_data/jak3`) | `task modding-models` |
| Bake them into the unit levels | `task extract` |
| Build the Jak 2 city level | `task level-port -- custom_assets/jak3/ports/battlefront-havenj2/port.jsonc` |
| Compile (the first time in a worktree: `(make-group "iso" :force #t)`) | `task compile-check` |
| Boot as a player does, through the title | `task boot-game-retail` |

After a first `task level-port`, compile `battlefront-havenj2-info.gc` again: the build does not
see the generated file as its input.

The smoke tests drive the real menus with the pad in a retail boot:
[`battlefront_tests.md`](battlefront_tests.md) lists them and how to run one.

| Symptom | Cause |
|---|---|
| A red guard or a jetpack guard is invisible or untextured | `task extract` not run since the models changed |
| `multiple ways to make output out/jak3/obj/bf-...-ag.go` | The art groups' pre-marks in `game.gp` are missing |
| `dgo file header ... has overrun heap` while loading Haven City | `ctypesa.gd` or `ctypesc.gd` no longer sorted by decreasing size |
| The war zone is greyed | Jak 2 not extracted, or `battlefront-havenj2-info.gc` not compiled again after `task level-port` |
| A native crash (`0xC0000005`) with no GOAL message | Often an engine buffer overflowed (§5); a temporary vectored exception handler in the runtime names the function (`smoke-tests` skill, `game-control.md`) |

## 7. Known limits

- **About 100 units at once a side** is the tested maximum (§5); the count dips under it in heavy
  fights, since a fallen unit's replacement comes on a later drop.
- **The class is Jak underneath:** hits, health and death are Jak's, and the robotguard's roll or the
  spider's leap are Jak's physics with another speed.
- **No aim assist** but the tazer's lock.
- **Sounds:** the red guards shout no lines (Jak 2's are streamed audio, which Jak 3 cannot add yet),
  the transports are silent, and the robotguard's shield may be.
- **The red guards' death** is a burst of sparks: their models cannot take the stock dissolve.
- **Jetpack guards are flying turrets:** they explode into robot debris.
- **A guard drawn with its legs only** was seen once; its cause is not found.
- **Quit the battle froze the game once** while the title loaded, after a long battle in Jak 2's
  city (a smoke run, 2026-11-16: no crash report, nothing printed after "Opening TITLE DGO"); not
  investigated.
- **About 10 units go NaN** in the first minute of a battle and are put back to sleep; the cause is
  not found.
- **Nothing is saved:** a battle ends with the session, and the ammo it uses is Jak's.
- **No Naughty Dog asset in git:** the Jak 2 models and city are made from the player's discs at
  install.
