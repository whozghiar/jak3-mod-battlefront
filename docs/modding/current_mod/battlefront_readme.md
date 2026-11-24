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
starts `#t` at every boot and is not saved. The Mods menu's L3 + SELECT opens nothing while it is on
(the author's wish, `bf-menu-hook`), so the mod is the game from every boot.

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
| Blue robotguard (round 46) | `roboguard-city` | `roboguard` | Freedom League: registers as a rifle guard |
| Blue spider robot (round 46) | `spydroid` | `spydroid` | Freedom League: registers as a rifle guard |

The two sides share every pool. Each new process takes the look of its kind furthest below its
share (`*bf-look-share*`, `bf-guard-skel-name`, `bf-turret-skel-name`, `bf-bot-skel-name`), from
counts the director makes every frame; its side follows from its look (`bf-unit-team`). The setup's
**units at once** count the whole city, both sides (60 to 200, 200 by default; round 45: a side
until then), half a side, which sets the caps (`bf-caps-set!`), the same for both sides since round
46: at 100 a side, 40 guards, 20 jetpacks, 20 robotguards and 20 spiders. The red guards carry three
rifles for one grenade launcher, and so do the blue ones (one in four by its pid, `bf-guard-weapon`).

**The blue robots.** Jak 3's own robotguard and spider robot, their red texels turned blue
(`bf-robot-blue` and `bf-spider-blue` in `models.jsonc`, the transport's rule; a turn of 210
degrees, matched on screen to the blue guards' armor: 217 put the robots at a hue of 221 against
the guards' 214), built with one clip
each: like the red guard, they take the stock art group (`roboguard-city`, `spydroid`) as the one
their clips are looked up in (`bf-guard-clips`), the skeletons being the same. They register with
the attack controller as rifle guards, as the blue jetpack does (`bf-attacker-type`, called by each
type's `citizen-method-215` in `roboguard-city.gc` and `spydroid.gc`). Until round 47 those two
methods still gave the Krimzon Guard's types (9 and 11): the blue robots and the blue guards took
each other as foes and fought at no damage all battle long, so the blue guards never marched, and
the red guards found no foe (none of their samples hostile in a minute).

**Reloads.** The stock rifle guard plays its reload between two bursts of one to three shots, and
loops it while its foe is dead; the grenade guard plays its own whenever it stands at its spot.
During a battle a guard with rounds left keeps its ground instead (`bf-guard-hold?`), one with a
full magazine and no foe walks on (`bf-guard-calm!`), and a reload fills the magazine
(`bf-guard-reload-count`): the guards were seen reloading most of the time.

**The guards' drill.** The stock rifle guard fires up to three shots a burst, skips its pause between
bursts in its faction's war mode, and fires as its fire clip begins, wherever it faces. A battle's
guard (`bf-guard-drill?`, `guard-rifle.gc`) fires one or two shots a burst, waits 2 s more than the
stock pause between bursts (`bf-guard-pause`: 4.5 to 6.5 s), aims 0.3 s, its rifle shouldered and
turning to its foe, before its first shot, holds each shot's pose through the clip's blend, and
holds its fire at a foe more than 20 degrees off its way. In scenario 138, 7.3 shots a guard a minute
before (29 of 366 off the foe's way), 3.7 after (none of 228).

**No blows.** The guards and robotguards of a battle keep to their guns: each way into a rifle butt
or a robotguard's punch asks `bf-melee-ok?` (six MOD lines in `guard-rifle.gc`, `guard-grenade.gc`,
`guard-tazer.gc`, `guard-states.gc`, `guard.gc` and `roboguard-city.gc`), and a robotguard shoots at
close range too. The spider robots bite and Baron Praxis strikes as before.

**Shots in a side's color.** A Freedom League unit's guard shot (the player's too) is drawn with
blue copies of the shot's parts (parts 5227 to 5231 swapped into `*part-id-table*` for the call,
`bf-shot-swap!`), in guard-shot's two draw methods; the jetpacks' shots, a type derived from it in
level code, take them at their creation.

**Allies pass through the player.** During a fight a collide-cache fill for Jak leaves out the units
of his side (`bf-cache-drop-allies!`), and a fill or an overlap test for one of them leaves Jak out,
his root prim's collide-as cleared for the call (`bf-fill-for`, the `find-overlapping-shapes`
wrapper). Foes still collide.

**No reaction to a hit from one's own side.** A unit's own side's hits already dealt no damage
(`damage-enemy-from-attack!`), but the stock reaction still came (`msg-for-incoming-attack`: a
flinch, a knock-down), and a knocked flying turret explodes: the Freedom League's jetpack guards
died that way, every one of its 74 jetpack deaths in 90 s (round 46, scenario 132). During a fight
the reaction step returns none for a hit from the unit's own side (the `nav-enemy` override, which
`citizen` and `roboguard-city` call as their parent method).

**The units alive.** The top left corner counts each side's units awake on the map, the player on
theirs (`bf-draw-alive`, from `*bf-unit-dots*`), each in its side's color.

**Reserves and losses.** The setup's **units per side** (500 by default) are the reserves, the
Battlefront tickets. A unit really dies once, in `traffic-tracker` `set-process-to-killed`
(`traffic-engine.gc`), which calls `bf-unit-killed`: the loss is counted there, and a pickup may be
queued (`bf-queue-drop`, spawned later by the director: the unit's death runs on the traffic
manager's small stack).

**Deaths out of view.** A unit knocked to 0 hit points by another unit, out of view or over 110 m
from the camera, skips its death: the stock knocked state sends it to `die-fast` at once. There, a
guard's process ended (the state's code returns at once, and a process whose code returns is
deactivated), and a robotguard, spider or jetpack went to sleep: the traffic engine heard of
neither, so no loss, no pickup and no respawn wait were counted. Most deaths of a battle happen
there: round 47 counted no guard death in 150 s. During a battle the mod's `die-fast` for
`crimson-guard` and `kg-squad-member` (`battlefront-city.gc`, round 48) reports the death
(`cleanup-for-death`: `'child-killed`, then asleep). Jak 3's protect missions put their own units to
sleep the same way (`assault-enemies.gc`), without the report.

**Speed.** The units walk and run faster than the stock ones (`*bf-unit-pace*`): the guards 1.6
times the stock, the jetpacks 1.5, the robotguards 3, the spiders 2.4. A clip covers its stock
ground times the kind's stride (`*bf-unit-stride*`), and plays at the pace over the stride: the
guards' stride of 1.3 plays their walk and run 1.23 times as fast. With the stock ground (round 36)
the guards' clips played 1.6 times as fast and looked sped up; with a stride of 1.6 their feet slide.

**Pickups the battle does not know.** A stock unit's random ammo pickup (`ammo-random`, 43) at
times reached `birth-pickup-at-point` unresolved, which printed "ERROR: unknown type of eco 43"
(179 times in one 150 s battle); during a battle `verify-pickup-type` turns it into none.

**The Freedom League's shine.** A build-actor model's envmap shine is tinted by the merc extra info
build-actor writes for each effect, always orange (255, 161, 102). The blue robotguard, spider,
jetpack and transport, recolored from red, shone orange; `bf-blue-shine!` (`battlefront-h.gc`)
writes the mirrored blue tint (102, 161, 255) into their loaded art, once a second during a battle
and as each blue transport starts. The blue robotguard takes the stock robotguard's own dim grey
(85, 85, 85, `*bf-robot-shine*`, read from `roboguard-city`'s art) instead: the blue tint made it
about three times as bright as the red one (round 52).

**The champions.** Once a side has lost 20 % of its units (100 with unlimited units), its champion
comes to fight for it, once a battle (`bf-boss-update`, `battlefront-baron.gc`), at its point nearest
the player: Baron Praxis for the Krimzon Guard (round 49), Ashelin for the Freedom League (round 53).
Each process knows its side (`bf-boss` and `bf-boss-body` `team`, `bf-boss-team`); the globals are
arrays by side (`*bf-boss-ref*` champ, `*bf-boss-done*`, `*bf-boss-hps*`, `*bf-boss-pos*`). The
Baron, as the first champion:

- **Two processes, as the player has.** `bf-boss` is the Baron drawn and moving himself, a
  `bf-avatar` of the Baron's class: the class's code reads his own pad (`bf-baron-pad-of`), side
  (`bf-baron-team`) and aim, so his moves, blows and eco ball are the player's Baron's.
  `bf-boss-body` is the shape the units aim at and hit: a process-focusable with the guards'
  collision, registered in the attack controller as a unit of his side (`bf-city-boss-attacker!`:
  a Krimzon Guard robotguard, type 9; Ashelin's as a Freedom League rifle guard, type 4), put at his
  chest each frame.
- **His thinking** (`bf-boss-think`) presses his pad: the nearest foe within 80 m, else the nearest
  Freedom League unit anywhere, else a point to take; a slash, a spin among two foes or more, a jump
  and plant every fourth blow, his eco ball at 8 to 40 m; a jump, then a way around, when stuck.
- **His health** is 100 points on the 24 point scale, about four guards' (`BF_BOSS_HP`; 480 until
  round 52). His health bar shows within
  60 m of the player (`bf-draw-boss-bar`, Ashelin's blue bar above his red one). The other side's
  units within 40 m turn onto a champion (`bf-city-retarget`, `bf-city-boss-pull!`): the battle's
  hatred keeps a unit on its foe until it dies, so none picked him before.

**Ashelin, the Freedom League's special character** (round 53, `battlefront-ashelin.gc`), on its
class page's fifth row with the setup's special characters on (as the Baron on the Krimzon Guard's),
36 points of health as a class, 100 as the champion:

- **Her model** is Jak 3's own (DESOASIS's `ashelin-lod0`), made at install by `mod_models.py`
  (`models.jsonc` `bf-ashelin`, CTYPESC): her red (top, shoulder pad, buckle, shoe plates, badge)
  turned 216 degrees to the blue guards' blue, her hair and face kept. Her model has one pistol, on
  a `gun` joint the clips key into her right hand; `mirror_props` copies it into her left hand,
  mirrored through the grip read from her firing clip.
- **Her clips** (round 54) are the author's Mixamo pistol motions (`third-party/animations/Ashelin`,
  not in git) and the Baron's `great sword kick` (a spinning kick), put on her skeleton with the Jak
  Animation Studio (`apply_mocap`, 30 keys a second), then cut and renamed by
  `scripts/battlefront/make_ashelin_clips.py` into `custom_assets/jak3/models/bf-ashelin-clips.glb`
  (joint keys only, as the Baron's): the capture's hips' travel goes on `main` (kneeling, her legs
  folded under a torso left standing), the loops are closed, the root's travel across dropped, her
  jump cut to its part in the air with her height flat, her run's stride widened 1.6 times. At install
  `mod_models.py` makes her clips from that file and from her rip (`made_from`, `made_clips`): her
  fingers closed on her grips as in her own firing clip (`pose_from`, `mirror_limbs` for the left
  hand), her right pistol kept in her right hand (`attach`); a tucked front flip from her jump's top;
  her own cartwheel to the left and its mirror to the right; an overhand throw of her left hand (her
  arm back and up, over her shoulder, down in front, her chest turning); her holstering and drawing
  as her reload; her hit and her death. The mirror takes each joint's skinning matrix from the other
  side's, mirrored across x (S K S), so it needs no knowledge of the joints' axes. Their order is
  `battlefront-h.gc` `BF_ASHELIN_CLIP_*`.
- **Her moves** (round 54, the author's buttons) are the Baron's (his collision, probes, stick,
  acceleration and lean): she runs at 10 m/s, her run clip at 1.55 times its pace at most (16 m/s
  looked sped up); X jumps 4.5 m, X again in the air 3.5 m more with her flip (0.2 s after the first
  at the soonest: a press was read on two frames); Square held fires her two pistols in turn toward
  the crosshair (a shot every 0.18 s, 4 points each, blue: the guards' shot), facing it and walking
  at 3.5 m/s with her walk, her strafes or her walk backward by the way she goes; 10 rounds a
  magazine (`*bf*` mag `BF_WEAPON_PISTOL`), 150 more carried (Jak's yellow ammo, the stock pickups
  refill it), an empty magazine or Triangle reloading it (1.13 s); L1 held kneels (her kneel, then
  her kneeling clip; let go, she stands up); Circle kicks all around her (14 points within 3.2 m,
  `bf-baron-strike`); R2 with the stick to a side flips her 9.8 m that way across the camera's
  heading; R1 throws a grenade overhand (`bf-lob`, the robotguard's red gun 3 grenade falling in an
  arc, 10 a life). The gun HUD shows her magazine (10 yellow shells), her grenades (10 dark shells
  beside them) and "magazine/carried".
- **As the champion** (`bf-ashelin-think`) she keeps 10 to 24 m from her foe, kicks one within 3 m,
  fires bursts within 36 m (her magazine reloading itself, without end), throws a grenade at a foe
  beyond 12 m every 4 s, flips aside every 2.5 to 4.5 s, and jumps twice, then goes around, when
  stuck.

**Hard landings.** A respawn's drop from the sky (30 m) lands Jak in his hard landing
(`target-hit-ground-hard`), whose code waits for his painful-land clips on his root channel. Jak
hidden under the class model, they never ended, and he stood until a jump took him out. After 0.8 s
there, `bf-hard-land-release` sends him to `target-stance`.

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

**Baron Praxis is not Jak in disguise.** The Krimzon Guard's fifth class (`BF_CLASS_BARON`,
`battlefront-baron.gc`), a special character: on the class page only when the battle setup's
**Special characters** is Yes (`*bf-config*` special, `bf-class-count`; No by default). He moves on
his own: `bf-pad-lock!` copies pad 0 into `*bf-baron-pad*` and
clears it for Jak (START, SELECT, L3 and the right stick stay, for the menus and the camera), and
`bf-baron-update` runs him from it every frame: his run on the left stick, his jump, gravity and
collision on probes of the scenery (`bf-baron-step`), his attacks. Jak, hidden, is put where he
stands each frame, so the camera, the units' aim and the hits taken are still Jak's. His moves:

| Button | Move | Code |
|---|---|---|
| Left stick | Run (16 m/s, the player's guard's pace) toward the stick, against the camera; a light push walks (under 4 m/s) | `BF_BARON_RUN`, `bf-baron-stick` |
| Left stick back at a run | He turns about on the spot (his 180 degree turn's clip), then runs off the other way | `BF_BARON_TURN_TIME` |
| X | Jump, the height of Jak's double jump (6 m) | `BF_BARON_JUMP` |
| Square | Overhead sword chop ahead, Jak's punch reach (3.2 m), 16 damage | `bf-baron-strike` |
| Circle | Spinning slash all around, Jak's spin-kick reach (3.4 m), 14 damage, twice | `bf-baron-strike` |
| R2 | Jak 1's yellow eco ball straight ahead (`bf-eco-ball`, 24 damage) at the blow of a diagonal cut, a quarter of his yellow gauge, which fills in 20 s | `bf-baron-cast` |
| X then Square (in the air, or both at once) | He dives (14 m/s), his sword raised, and plants it on landing: 20 damage within 5 m, the red gun 3's blast on the ground | `bf-baron-plant-blow` |
| X then Circle (in the air, or both at once) | A full spin of his sword, his fall slowed to 30 %: 14 damage within 3.4 m and 6 m under him, twice | `BF_BARON_AIRSPIN_*` |
| L2 held | A white barrier for Light Jak's: the robotguard's shield sphere (`bf-shield-raise!`), white; no damage taken, foes within 4 m thrown out, a slow walk | `bf-baron-shield` |

He moves as Jak does (round 45): he speeds up and slows down over a few frames (`BF_BARON_ACCEL`,
`BF_BARON_DECEL`), turns toward the stick at up to 720 degrees a second and leans into the turn by
its rate and his speed (`BF_BARON_LEAN`, `bf-baron-face!`). His run and walk loop as fast as his feet
cover the ground he covers (`bf-baron-play`: the clip's ground a second at rate 1,
`BF_BARON_RUN_GROUND` 8.41 m and `BF_BARON_WALK_GROUND` 1.91 m, measured on the captures put on him
moving); his walk's capture goes 27.6 degrees off the way it faces, so his model turns that much
while he walks (`BF_BARON_WALK_YAW`). His run's stride is widened 1.6 times (round 46): played 2.6
times as fast at 16 m/s, the capture looked sped up; now 1.9 times. His attacks play their clips
whole, 1.3 times as fast, the blows landing as the clips strike (`BF_BARON_SLASH_AT`,
`BF_BARON_SPIN_AT`, `BF_BARON_CAST_AT`). In the air his attacks are the two combos above; his body
stops at the foes he runs into (`bf-baron-push-out!`, from `*bf-unit-dots*`), and a faint green aura
rises along his blade (part 5232, `bf-baron-aura`: the blade's two ends in the `sword` joint's
frame, node-list 41).

His model is Jak 2's `baron-highres` (`LDJAKBRN.DGO`), made at install like the other Jak 2 models
(`bf-baron` in `models.jsonc`). Its clips are Mixamo sword motions put on that skeleton with the Jak
Animation Studio (30 keys a second), then cut, renamed and given the sword by
`scripts/battlefront/make_baron_clips.py`; the result, `custom_assets/jak3/models/bf-baron-clips.glb`,
holds joint keys only, and `mod_models.py` puts it on the ripped model (`clip_file`). The script:

- **closes the loops.** None of the captures ends on its first pose (the run 34 degrees off at a
  thigh): the gap is spread over the clip and the first pose added as its last key, so the loop
  never jumps.
- **puts the sword in his right fist** (`sword_keys`): only the hilt's joint (`sword`) moves; the
  scabbard (`swordA`, `swordB`) stays at his left hip. The model has no blade (sheathed, only the
  hilt is modeled): `mod_models.py` makes one along the scabbard it fits (`blades` in
  `models.jsonc`), bound to the hilt's joint.
- **closes his right fist** around the grip (`FIST`): the studio leaves the fingers at rest.
- **widens his run's stride** (`STRIDE`, round 46): each leg joint turned away from its mean pose
  over the cycle 1.6 times as far, his bounce with it, and prints the ground the feet cover.
- **keeps his legs tucked** in his spin in the air (`LEGS_FROM`: his jump's top).

His plant's capture, `great sword jump attack.fbx`, goes through Blender first (imported and
exported again unchanged): the studio's FBX loader refuses the Mixamo file ("Unknown property
type").

His one eye (the other is under his helmet) is drawn with his eye texture (`texture_files`:
`ldjakbrn-pris/baron-eye.png`): Jak 2 draws its characters' eyes at run time over a 4 x 4
placeholder, `programmer_eye_left`, which the ripped mesh keeps.

### 2.5 Points and victory

Each side has two **headquarters**, held for good, and each of the 13 other districts has a
**control point**, neutral at the start, lettered A to M from the palace to the slums. Four times a
second `bf-update-points` counts each side's units within `BF_POINT_RADIUS` (50 m), and the side
with more units takes the point in two steps (`bf-capture-step!`): a point the other side holds
turns neutral in `BF_NEUTRALIZE_TIME` (20 s), then a neutral point is captured in `BF_CAPTURE_TIME`
(15 s). The holder's majority takes a neutralization back down; equal numbers of both sides
contest it: the progress holds (`bf-point-contested?`). Under the reserves, the point the player
stands in shows as its radar mark filling clockwise in the taking side's color, blinking while
contested (`bf-draw-capture-icon`). Each point shows as a beam of light in its
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

While the other side takes one of its control points, a side's units come down at the point
nearest it, the attacked point itself until it turns neutral (`bf-transport-attacked`). Otherwise
each try picks one of the side's headquarters and held points at random (`bf-transport-draw`) and
brings up to 3 units, each of the kind its side lacks most against its caps
(`bf-transport-next-kind`). A fallen unit's place stays counted for 5 s. One unit in four dropped
at a control point is **posted** there (3 at most) and guards it while foes come within 150 m.

**The ships leave.** A ship that brought `*bf-ship-load*` units (100) rises into the sky for good, and
its headquarters is no longer a place to come down (`ship-done?`, round 45, the author's wish); so
are all of a side's once it brought as many units as the setup gives it (`*bf*` spawned,
`bf-ships-gone?`; never with unlimited units). The side's units and its player then come down at
the control points it holds. A headquarters stands, with its ship, on the most open ground within
30 m of its continue point (`bf-transport-spot`, `bf-transport-openness`: the free ground in eight
ways), round 45: the first open spot put the Palace, Slums and Stadium HQs' ships in cramped
corners.

### 2.7 How units find their way

The city's walking lanes are loops inside one district: a unit following them never reaches a far
point. So a unit away from its goal **marches over the nav meshes**, which join the districts:

1. **A goal.** `bf-city-unit-goal` gives each unit a point: a contested point within 350 m first,
   then the point it is posted on, else one its side does not hold, drawn at random by its process
   id and kept until its side holds it. On its way, a unit fights the foes it meets (the stock
   attack, `bf-city-foe-ok?`), then goes on (round 45; round 44 let 40 % of them pass by).
2. **The ways.** Every 10 s `bf-ways-build` searches, from each point's nav mesh, every mesh's links
   breadth first: each mesh keeps its link back toward the point (`*bf-ways*`). Meshes that touch
   without a link get a bridge (`bf-ways-bridges`).
3. **The march.** Twice a second `bf-march-plan` sets the unit's destination to the next link on its
   way; every frame `bf-march-apply` moves it onto the next mesh when it stands on the link. Within
   12 m of its point (`BF_MARCH_NEAR`) the unit walks the lanes around it instead.
4. **The seams.** Jak 2's meshes overlap where they link, a link poly inside the other mesh's
   ground. A unit coming from that side stops 4 m short of its destination (a citizen's arrival
   distance), never steps on the link poly, and stood there until its stuck hop. Within 12 m of its
   link (`BF_CROSS_REACH`), a unit standing on its next mesh's ground (a poly of it under its feet,
   within 4 m up or down, `bf-mesh-covers?`) moves onto that mesh (`bf-march-cross!`). There it can
   stand on the new mesh's own link poly back, which sent it back at once (the stock
   `nav-enemy-method-188`): for 1 s after such a crossing, no link poly sends it back to the mesh it
   left (`bf-link-hold!`, the method's override in `battlefront.gc`). A unit still stuck 4 s near its
   waypoint, off its point's own mesh, is put onto it (`BF_STUCK_HOP`): 26 in 150 s of battle, 175
   in 3 minutes before round 47.

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

### 2.8b The war zone: Spargus

**A level made at install, from Jak 3 alone.** `custom_assets/jak3/ports/battlefront-spargus/port.jsonc`
ports Jak 3's own Spargus (`wascitya`, `wascityb` and `waswide`) into one level, `bf-spargus` (DGO
`BFS`), the way the Jak 2 city is made: `scripts/level_port` takes Jak 3 as a source game too
(`games/jak3.py`, `convert/jak3_jak3.py`). Spargus's own code (`WWD`, `WASALL`) defines the traffic
engine again, so Haven City's city code can't run beside Spargus's levels: the port carries the
city code in its own DGO and loads none of Spargus's.

**Nothing of Spargus's actors comes along.** No Wastelander, animal, ladder, turret or elevator. Its
props are background (`mesh.props`, with `RIP_NAMES` for the classes whose rip has another name),
and the doors to the places the zone leaves out stand closed with a collision box: the garage's
(`wascity-airlock-small`), the arena's and the palace elevator's.

**Its lanes are Haven City's territory.** Spargus's lanes belong to territory 128, which Haven City's
faction manager doesn't know: each unit put on one went to sleep ("Going inactive", citizen.gc
`enemy-common-post`). The nav step's `clock` gives every lane territory 0 and clock-mask 1, as Jak 2's
city has them.

**Few lanes.** Spargus has 233 lane segments (Jak 2's city 8955), and a unit out of a ship could
stand on none. Two stock paths read the lane all the same and crashed the game: the lane picker
(`bf-city-choose-branch`) and a guard's flight (flee-info method 13). Both give up on a unit on no
lane, and `bf-city-give-lane!` puts a battle unit on no lane onto the lane nearest it within 150 m.

**Two districts, one link.** Spargus's nav meshes of `wascitya` and `wascityb` stop 17 to 19 m apart
at the pass between them, with no link: its people never cross it. The port's nav `links` adds a strip
of polys across the gap to both meshes and a nav-mesh-link between them, laid out as Jak 3 links its
own (`level_port/steps/nav.py`, `link_meshes`): the units walk across and change mesh on the way, as
between Haven City's districts. Wascitya's main nav mesh (the strip hangs off its second) still
reaches the strip's far end with a 5 m bridge, which its units hop.

**More than 16 guards on one foe.** `ff-squad-control` method 16 lists the Freedom League guards
aiming at one foe in two 16-entry stack arrays; in a battle more than 16 did, and the 17th wrote
past them (a crash as Spargus's fight began). It lists 16 at most (a MOD line in
`city/common/ff-squad-control.gc`).

**The destruction of an objective** (round 54, the author's wish; `battlefront-artifact.gc`,
`bf-objective?`). A precursor artifact stands by the precursor game's door (Jak 3's `waspgame`
actor `was-pre-game`, 1477, 28, -371 m), on the nav poly nearest it, in `wascityb`. The Freedom
League defends it, the Krimzon Guard comes to destroy it:

- **The artifact** is Jak 3's precursor generator C (`precur-generator-c-ag`, the precursor core's),
  which the port's `traffic.art` puts into `BFS` with its textures, drawn at 0.4 of its size on its
  legs (`bf-artifact`, a process-focusable: a solid sphere the shots meet, 800 points of health on
  the units' 24 point scale, the player's hits twice as hard). It is a Freedom League rifle guard in
  the attack controller (`bf-city-artifact-attacker!`): the Krimzon Guard's units hate it. Its bar
  shows under the reserves (`bf-draw-artifact-bar`). Destroyed, it bursts into the pieces of its
  exploded model (a `joint-exploder`) in the Krimzon Guard's explosions.
- **No point is taken.** Spargus's points are the two camps and the artifact's, the Freedom
  League's from the start; `bf-update-points` counts the units at it but never captures it, and the
  victory by holding every point is off. The artifact destroyed, the Krimzon Guard wins; the time
  up, or the Krimzon Guard out of units, the Freedom League.
- **Each side in its district.** The Freedom League comes down from the sky west of the pass (x
  under 1990 m, `wascityb`, the precursor game's side), the Krimzon Guard east of it (x over 2110 m,
  `wascitya`): `bf-city-spawn-tick` sets `*bf-spawn-x*`, which `bf-city-spawn-spot` keeps to when it
  draws a poly anywhere. The camps swapped with it: the Freedom League's is the port's `bfs-kg-camp`
  (west), the Krimzon Guard's `bfs-ff-camp` (east), the names of rounds 50 to 53.
- **The attackers go for it.** The Krimzon Guard's units march to its point; once over the pass,
  each turns onto the artifact unless its foe stands within 10 m (`bf-city-artifact-pull!`). Turned
  onto it from farther, they stood at the pass's east end: a unit with a foe chases it with its stock
  moves, which stop at the end of its nav mesh, and only the march crosses the pass. Turned onto it
  within 45 or 150 m only, the defenders massed around it held them 130 m off and none fired at it;
  a Freedom League sent to meet them held them at the pass (round 54's tests).
- **The defenders hunt** (round 55, the author's wish: they stood around the artifact). Each
  Freedom League unit marches at the Krimzon Guard unit nearest it, wherever it stands
  (`bf-city-hunt`, in place of the points' goals): the march routes by the artifact's point when that
  foe is west of the pass (x under 1968 m), by the Krimzon Guard's camp when east of it, so the
  defenders cross the pass after it.
- In scenario 140, 197 Freedom League units came down west and 259 Krimzon Guard units east in 3
  minutes, none in the other's district; up to 80 attackers aimed at the artifact, which lost 284 of
  its 800 points. With the hunt (round 55), 1 % of the Freedom League's units stood within 60 m of the
  artifact and up to 51 were east of the pass; the fight stayed at the pass, and no Krimzon Guard
  unit came within 500 m of the artifact in 3 minutes.

Until round 53 Spargus had four control points (Market and Western Heights in `wascityb`, the Pass
and the Square in `wascitya`), and round 52 dropped every unit anywhere on the map (scenario 138). The
menus' map is the START menu's map of Spargus (`make_minimaps.py`, bigmap id 23). The HUD's corner
minimap shows nothing in Spargus.

### 2.9 Menus are pages of the START menu

Every battle page (title menu, war zone, setup, class, respawn, pause, result) is a page of the
game's START menu, the progress state `'battlefront`. Its one option (`menu-bf-page-option`) hands
the pad to the director (`bf-menu-input`), which draws the page inside the menu's ring
(`bf-menu-draw`). The title menu's options are replaced (`set-menu-options` wrapper), and START in
a battle opens the battle's pause page (an `activate-progress` wrapper).

**START pauses the battle.** The START menu (the pause page and its Controls page of every class's
buttons) pauses the fight as the stock game does, the game's still copy of the screen behind it
(`*bf-start-paused?*`). The pause page has no Options entry (round 45, the author's wish): the
game's own menu does not open in a battle. Under the pages after a death the game keeps running
(`bf-live-update`): the menu's process mask is undone and pad 0 is hidden from the world
(`bf-input`) while the menus read it.

**Outside the campaign.** During a battle no mission starts (`exclusive-task` none), no vehicle can
be taken (`pilot` off), and Save, Load Game and Secrets are greyed and refused. A load or a new
game ends the battle first (`game-info` `initialize!` wrapper, `bf-stop-now!`).

## 3. How a battle runs

1. **Title.** START on the title screen opens the battle's title menu: Start a battle, Options,
   Quit.
2. **Setup.** The war zone, then the battle setup (`*bf-config*`): time limit, units per side,
   units at once, victory condition, special characters (Yes or No), side. Next starts a new game
   at the zone's continue point.
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
| `.../battlefront/battlefront-baron.gc` | Baron Praxis: his controls, movement, sword, eco ball and shield; the champions of both sides |
| `.../battlefront/battlefront-ashelin.gc` | Ashelin: her controls, jumps, side flips, kneel, kick, pistols and magazine, thrown grenade, and her thinking as the Freedom League's champion |
| `.../battlefront/battlefront-artifact.gc` | Spargus's precursor artifact and the destruction of an objective |
| `.../battlefront/battlefront.gc` | The director: phases, menus, points, HUD, deaths, respawns, the stock wrappers |
| `.../battlefront/battlefront-havenj2-info.gc` | Reads the generated Jak 2 level's load info and map at compile time |
| `.../battlefront/battlefront-spargus-info.gc` | Reads the generated Spargus level's load info at compile time |
| `.../battlefront/battlefront-icons.gc`, `-minimaps.gc`, `-portraits.gc` | Generated pictures: HUD icons, Jak 3's city map, class portraits |
| `goal_src/jak3/levels/city/battlefront/battlefront-city.gc` | The city side (CWI): hatred, goals, marches, drops, posts, NaN sweep |
| `goal_src/jak3/levels/city/battlefront/bf-transport.gc` | The troop transport (CWI) |
| `goal_src/jak3/levels/bf-havenj2/` | The Jak 2 city level's code; the rest of the folder is generated by `task level-port` |
| `goal_src/jak3/levels/bf-spargus/bf-spargus-obs.gc` | The Spargus level's mood; the rest of the folder is generated by `task level-port` |
| Stock files marked `;; MOD battlefront` | One-line hooks into the traffic, guards, turrets, HUD, minimap, loading, and the raised limits of §5 |
| `custom_assets/jak3/models/models.jsonc` | The Jak 2 models' recipe |
| `custom_assets/jak3/ports/battlefront-havenj2/port.jsonc` | The Jak 2 city's level port manifest |
| `custom_assets/jak3/ports/battlefront-spargus/port.jsonc` | Spargus's level port manifest |
| `scripts/battlefront/` | The generators of the icons, maps and portraits, and of the Baron's and Ashelin's clips (`bf-baron-clips.glb`, `bf-ashelin-clips.glb`) |
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

A battle of 400 units (200 a side) goes past several fixed sizes of the engine. The mod raises them:

| Limit | Stock | Mod | File | What overflowed |
|---|---|---|---|---|
| Frame's global DMA buffer | 1280 KB | 2560 KB | `engine/gfx/hw/display.gc` | Each drawn unit writes about 6.5 KB there, unchecked; 200 units in view filled 1.3 MB and corrupted the memory after it |
| Default nav mesh users | 128 | 255 | `engine/nav/nav-mesh.gc` | Every new pool unit holds one until it is first woken |
| Traffic tracker's awake list | 126 | 448, its count a uint16 | `levels/city/traffic/traffic-engine-h.gc` | 200 units a side |
| A traffic type's counts | int8 | uint8 | `levels/city/traffic/traffic-engine-h.gc` | 224 guards wrapped past 127 |
| A Jak 2 city nav mesh's users | 64 | 200 | `engine/nav/nav-mesh.gc` (`bf-nav-max-users`) | A headquarters' mesh after a redeploy's reset |
| Animated processes a frame | 384 | 1024 | `engine/engine/engines.gc` | 340 units: its `break!` ended the game |
| Process heap | 4960 KB | 8032 KB | `kernel/gkernel-h.gc` | A unit takes about 9.4 KB |
| Sleeping units per pool | 20 | 256 guards, 128 turrets, 64 robotguards and spiders | `levels/city/traffic/traffic-engine.gc` | A pool spawned a new unit every frame past 20 |
| Attack controller's attackers | 64 | 512 | `levels/wascity/cty-attack-controller.gc` | Units without one corrupted memory |
| Touching-prims records | 64 | 256 | `engine/collide/collide-touch-h.gc` | Crowds at the ships |
| Background trees per kind | 11 | 32 | `engine/gfx/background/background-h.gc` | Jak 3's whole city loaded at once |

During a fight a pool keeps only 24 units asleep above its units awake (`bf-pool-size`): every
unit a pool spawns holds one of the default nav mesh's 255 nav-controls until first woken. Past 240
units the farthest from the camera are not drawn (`bf-city-draw-cap`), so the DMA buffer below
holds. A unit's sounds beyond 60 m are not sent, and a budget holds those from 20 to 60 m
(`bf-sound-allowed?`): the sound player takes 128 commands a frame.

**The log of a big battle.** Three stock lines repeated by the hundred in a battle of 200 a side
(round 45's census, scenario 129) are no longer printed, the game doing what it did:

| Line | Cause | Now |
|---|---|---|
| `enemy::move-to-ground: failed to locate ground` | Units woken in the sky or in a ship's hatch, over 10 m above the ground they fall to | Not printed for a battle's unit (`move-to-ground` wrapper, battlefront-h.gc) |
| `could not do (ja-channel-push! 2) because it has 4/6 channels`, with `invalid type ptr` and `call_method_of_type failed` | A unit switching clips while its last two blends run; its type sits in a level heap above 128 MB, which the kernel's printing refuses | The same switch without a blend, unprinted during a fight (`ja-channel-push!` wrapper, battlefront.gc) |
| `Exceeded max number of collide-cache prims!` | A guard's collision in a crowd: the cache keeps 100 prims and skips the rest | Not printed (`game/mips2c/jak3_functions/collide_cache.cpp`, a line a prim skipped) |

**Stuck units.** Robotguards and spiders falling from the sky or a ship's hatch go through
everything until 3 m over the floor they land on. That floor was a nav poly's middle, which lies
under the floor (meters on a stair); at the Palace HQ they went through it and, 6 km under the city,
kept their side's places (12 spiders at one census). Now:

- The fall ends on the floor a probe finds within 4 m of the poly's middle (`bf-city-floor`), and
  a unit that passes that floor with no collision to stop it (the ported city has nav meshes where
  its scenery's collision is missing) is put on it and walks (`bf-city-land!`): its fall
  (`exit-transport`) ends only on touching ground. The falls followed are 64 at once (16 before).
- Out of a hatch, the poly is the one under the hatch's end, or none drops there
  (`bf-transport-hatch-ground`).
- A unit lower than 100 m under the city goes back to its pool (`bf-city-nan-sweep`), or onto its
  mesh's floor while it is still on its way out (`bf-city-rescue!`): no sleep takes such a unit out
  of the awake list, and one robotguard was put to sleep 7368 times in a run.
- A spider idle in its wait for a foe (`'wait-for-vulnerable`) with none left walks again
  (`bf-city-robot-free`).

Two constraints bound the memory:

- **The level heap must end below 256 MB** (above it, adgif shader links break). The DMA buffers and
  the process heap are allocated before it, so they can only grow a little: with the DMA buffers at
  2560 KB and 3 MB more process heap, the level heap ends at `#xfa2c2c0`.
- **Several counts are bytes.** The default nav mesh holds 255 users at most (`max-nav-control-count`
  is a uint8), and so does each of the city's meshes.

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
| The war zone is greyed | Jak 2 not extracted, or `battlefront-havenj2-info.gc` (`battlefront-spargus-info.gc` for Spargus) not compiled again after `task level-port` |
| A change of a port's navigation (`*-nav.json`) has no effect | The level's build doesn't follow its `nav_data`: touch its `.jsonc` (generated) to rebuild it |
| A native crash (`0xC0000005`) with no GOAL message | Often an engine buffer overflowed (§5); a temporary vectored exception handler in the runtime names the function (`smoke-tests` skill, `game-control.md`) |

## 7. Known limits

- **200 units at once in the city** (100 a side) is the setup's maximum since round 45; the engine
  limits of §5 hold 200 a side (scenario 125, round 44). The count dips under it in heavy fights,
  since a fallen unit's replacement comes on a later drop.
- **The class is Jak underneath:** hits, health and death are Jak's, and the robotguard's roll or the
  spider's leap are Jak's physics with another speed.
- **No aim assist** but the tazer's lock.
- **Baron Praxis's** barrier is the robotguard's sphere in white: Light Jak's own shield model is
  not loaded in Jak 2's city. His blade is a plain steel diamond made by `mod_models.py`, and his
  eye looks straight ahead (no blinking: Jak 2 animates eyes at run time).
- **Jak 1's blue eco arcs** are drawn with Jak 3's lightning frames: Jak 1's own zigzag textures are
  on the Jak 1 disc, which the mod does not ask for.
- **The START menu's still picture** shows Jak in place of the class model.
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
