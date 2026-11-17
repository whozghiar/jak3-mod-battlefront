# Battlefront: smoke tests

The in-game smoke tests of Battlefront: what each scenario is for, what it does, and its last
result. The scenarios live in [`battlefront_smoke.gc`](battlefront_smoke.gc), one numbered scenario
per run; the `smoke-tests` skill explains the runner. Each one boots the game as a player does
(retail), loads save slot 1 and drives the mod's real menus with the pad, checking each step with a
`SMOKE PASS` or `SMOKE FAIL` line. Nothing is saved.

## Run a test

```bash
python scripts/modding/smoke_test.py install jak3 docs/modding/current_mod/battlefront_smoke.gc --scenario <n>
task compile-check
python scripts/modding/smoke_test.py run jak3 <test-id> --retail --timeout 540
python scripts/modding/smoke_test.py remove jak3
task compile-check
```

- The build compiles the installed copy: edit the scenario in `battlefront_smoke.gc`, then install
  it again.
- `run` stops the game when the scenario prints `SMOKE DONE`, or at the timeout. Its log,
  screenshots and recorded frames land in `out/smoke/<test-id>/`. A `SMOKE step <action>` line
  comes before each action, so the last one before a crash names it.
- Run `remove` and compile again before a commit: no smoke-test file may reach one.

## Kinds of scenario

| Kind | What it gives |
|---|---|
| Check | `SMOKE PASS` / `SMOKE FAIL` lines on facts measured in the game |
| Diagnosis | A log read by hand, to find the cause of a bug; no pass or fail |
| Capture | Screenshots or recorded frames, for the README or the generated pictures |

## Scenarios in Jak 2's Haven City

The war zone the mod offers. These scenarios match the current game.

| # | Objective | What it does | Last result |
|---|---|---|---|
| 72 | Jak 2's city loads as a Jak 3 level | Out of a battle, sends Jak to the level's continue point; checks that it loads, that Jak 3's city code starts, and that Jak stands and walks | PASS 2026-11-15 |
| 73 | A battle starts in Jak 2's city | From the title menu as a red guard: the zone's points, the unit levels borrowed into the city level, both armies, the L3 map | PASS 2026-11-15 |
| 74 | Stability at 63 units a side | Three minutes of battle, the armies counted every 30 s | PASS 2026-11-15 |
| 76 | 100 units a side at 60 frames a second | Sets units at once to 100 on the setup page; three minutes, the awake units and the game's pace measured | PASS 2026-11-15 |
| 77 | Forward ships and goals ranked by the front (an earlier design) | Four minutes at 60 a side, each drop and each unit's goal logged | PASS 2026-11-15; the design changed since (headquarters and random drops) |
| 78 | Menus fit the screen | Shoots every battle page on a 4:3 then a 16:9 screen | PASS 2026-11-15 |
| 79 | Jak 2's doors stay closed | At five doors to interiors, shoots each from both sides, probes it and walks Jak into it | PASS 2026-11-15 |
| 80 | The HUD's minimap shows Jak 2's map | Checks the level's minimap page, then shoots the HUD at three places | PASS 2026-11-15 |
| 81 | The battle as designed: headquarters, drops, capture | Two headquarters a side with a ship each, drops drawn among held points, a neutral point captured faster by a larger majority, 100 a side, three class changes | PASS 2026-11-15 |
| 82 | Rocket and grenade icons in the stock icon's box | Redeploys as each class with an icon and shoots the gun HUD | Checked on the screenshots 2026-11-15 |
| 83 | Diagnosis: where the guards go | Every 15 s for two minutes, why each guard aims at its point | 2026-11-15 |
| 84 | No crash at 100 units a side | Scenario 81 at 100 a side, printing the global DMA buffer's peak use and checking the level heap ends below 256 MB | PASS 2026-11-15, twice: peaks of 1304 and 1326 KB in the 2560 KB buffer |
| 85 | Capture: the README's Freedom League pictures | The setup page, a fight filmed behind a blue guard, the HUD, the blue classes' moves, the L3 map, the Respawn page after a death; GIFs made from the frames with ffmpeg | 2026-11-16. A first run that ended with Quit the battle froze while the title loaded (seen once, not investigated), so the pictures are split over two scenarios |
| 86 | Capture: the README's Krimzon Guard pictures | The class page, the four red classes' moves, their HUDs, the result page of a won battle | 2026-11-16 |
| 87 | Capture: the trailer's teaser | A cinematic camera, HUD hidden, at the fiercest clashes of three districts: a blue ship dropping troops, orbits, a crane, the city from high up, a jetpack seen from the ground, a chase, drops from the sky, the closing pull-back | 2026-11-16 |
| 88 | Capture: the trailer's Freedom League classes | The blue guard and blue jetpack at a fight, HUD on, then orbited with the HUD hidden; a point capture; the fall from the sky after a respawn | 2026-11-16 |
| 89 | Capture: the trailer's Krimzon Guard footage | A red ship at the stadium, an orbit at another clash, the four red classes at a fight and orbited, the spider's blast in slow motion | 2026-11-16 |
| 90 | Capture: the capture and the respawn fall again | At the battle's start, while points are empty: a point taken, its beam changing color; the player's fall seen from the ground | 2026-11-16 |
| 91 | Capture: the red jetpack and the spider again | The same two classes at a bright clash near the Palace Plaza | 2026-11-16 |
| 92 to 98 | Capture: the trailer's second version | Each unit type leaving its side's ship; both armies sent to one point (an override of `bf-city-unit-goal`) for dense wide shots in six districts; the player's point of view with the view tracking an enemy and the fire held only while the aim is on one; the player's class filmed inside the battle; the spider's blast | 2026-11-16 |
| 99 to 109 | Capture: the trailer's third version | Drops filmed from open spots found by probes around each ship; fronts where both armies meet at one neutral point, each battle clip kept only when units of both sides die within 40 m of the camera's target (a log of every unit death); a camera chasing a jetpack's rocket to its burst; each class's moves from a camera suited to it; the spider's blast from 40 m | 2026-11-16: 18 battle clips of 49 met the criterion |
| 110 to 120 | Capture: the trailer's fourth version | The light compared at four hours (noon kept); the city from the palace tower's height; drops while no control point is held, so every reinforcement comes by ship, from close spots chosen by probes (the ship and the landing within the view's 38.7 degree height, open sky over the lens, no ground rising in front); each class's ranged attacks from a still camera beside it; points of view with and without the HUD, the scenery between the camera and the unit or its target logged frame by frame; the spider sprinting into the enemies then its blast seen wide; pull-backs over the Palace Plaza | 2026-11-16: the game froze twice under a flood of sound commands (scenarios 112 and 116); probes miss visual-only walls and the palace stairs; 2 of the 8 battle clips recorded met the criterion |
| 121 | Capture: the mod's thumbnail | 1920 x 1080 bursts at noon, no HUD, at the Palace Plaza: the spider's run and blast, the red jetpack's rocket, a dense fight from low and from 30 m with the palace behind it | 2026-11-17: the spider's run gave the frame kept (a wall of blue guards aiming at it, the palace behind); no rocket flew; the fights were thin (1 to 8 units of each side) and a 30 m take faced a visual-only wall |

## Earlier scenarios, in Jak 3's Haven City

These scenarios (all but scenario 1) fight in Jak 3's city, which the war zone page no longer
offers. To run one again,
set its battle's zone to Jak 2's city (`smoke-battle-start` takes the zone); its places and points
are Jak 3's and need the same change.

| # | Objective | What it does | Last result |
|---|---|---|---|
| 1 | The Mods menu and START | L3 + SELECT opens the Mods menu; with the mode on, START opens the battle's page and its Options entry the game's menu; switched off, no battle | Changed after its last run (2026-11-06 PASS) |
| 2 | The blue classes play | Freedom League: page order, camera checks, each blue class's moves for twenty seconds, then Quit | PASS 2026-11-06 |
| 3 | The red classes play | Krimzon Guard: the same for the four red classes | PASS 2026-11-06 |
| 4 | A jetpack left alone keeps still | Films the jetpack on the ground and hovering; films the camera, a strafe and the guard's rolls | PASS 2026-11-06 |
| 5, 6 | Endurance | Each class in a long fight, the player killed and respawned after each, then Restart and Quit (one side each) | PASS 2026-11-06 |
| 7 | Capture: the jetpack's clip pace | Films the jetpack at the old clip pace, then at the fixed one | 2026-11-05 |
| 8, 9 | Class help, health, damage, ammo, targeting | Per side: each class's health, a foe's blow, a rifle hit, the guard's ammo and tazer, the robotguard's shield and ball, the spider's leap and sprint, who aims at whom | PASS 2026-11-08 |
| 10 | The author's crash as a blue guard | Deploys the blue guard at once, checks the guards' armor, the tazer's stab and the jetpack's flames, then a long fight | PASS 2026-11-06, the crash not reproduced |
| 16 | The whole city as a battlefield | Points, transports, a capture and its defenders, the respawn page, the redeploy, the fight away from the player | PASS 2026-11-08 |
| 17 | Zone page, spawn shield, ships, aim | The war zone page, 3 s of invulnerability, a ship over each held point swapped at a capture, every class aiming, live units on the map | PASS 2026-11-08 |
| 18, 20 | Units conquer and defend on foot | The player out of the way; units walk to a neutral point, take it, and defend it when the other side comes (one side each) | PASS 2026-11-08 |
| 19 | Points on open ground | Redeploys to three districts; each point sits on open ground with its holder's ship over it | PASS 2026-11-08 |
| 21 | Reinforcements from the edge, force fields, doors | A side with no point nearby brings units from the edge; the force fields hold Jak; six doors stay shut | PASS 2026-11-08 |
| 22 | Every street section loaded at once | Checks the level slots and heap chunks, every point live, armies across the city, the stock levels back after the battle | PASS 2026-11-09 |
| 23 | 40 units a side, pause page, minimap marks | START's page, ships at random held points, the marks by side, the guards' speed, the first fight, the class facing the crosshair | PASS 2026-11-09 |
| 24 | Frame rate | 20 units a side, then 40, frames counted over wall time | PASS 2026-11-09: 60 frames a second |
| 25 | Diagnosis: the nav meshes | Lists each mesh, its links, and the gaps between the south and the north | 2026-11-09 |
| 26 | A contested point | Puts 6 foes on a held point; checks both sides fight in its radius and the holder clears it | PASS 2026-11-09 |
| 27 | A battle left alone | Fifteen minutes at most: the armies leave their bases, then fight over a point | 2026-11-09: FAIL on the 90 s departure check only |
| 28 | Guard crouch, dodge, roll; R3 map | Measures the rifle's spread standing, moving and kneeling; the dodge and roll toward the stick | PASS 2026-11-09 |
| 29 | L3 map, tazer stab, pickups, speeds, marches | L3's kills and map, the tazer's whole stab, a pickup gone after 10 s, unit speeds, robots marching, drops at the front | PASS 2026-11-09 |
| 30 | Capture: an AI guard's legs | Films an AI guard running beside the player's guard, to compare their pace | 2026-11-09 |
| 31 | Class page, drops, deaths, shield, spider | The class previews, bursts of 3 from the ships, goals spread, each class's death, the robotguard firing behind its shield, the spider's sprint and headbutt | PASS 2026-11-11 |
| 32 | The spider's headbutt | A minute of battle, then a headbutt on the nearest foe | PASS 2026-11-11 |
| 33 | Diagnosis: guards drawn with legs only | Scans the guards' armor masks 40 times | 2026-11-11: none found |
| 34 | Rifle 20/100, blue ammo, spawns, sight, pickups, jetpack | The rifle's ammo, blue ammo recharging the tazer, units at the most advanced point, no foe behind a wall, the pickups' shares, the jetpack's controls | PASS 2026-11-11 |
| 35 | Drops from the sky and the player's fall | The jetpack's flames, the robotguard's ball, units falling onto their poly, the player's respawn from the sky | PASS 2026-11-12 |
| 36 | Diagnosis: islands and walkways | The meshes' islands and heights, then 4 minutes with every unit reported every 10 s | 2026-11-12 |
| 37 | Grenade throw, rifle on the run, falls, music, START page | The throw on the whole body, the falls of robots and spiders, the war music, Redeploy's cost, the locked menu entries | PASS 2026-11-12 |
| 38, 39 | Robots fall at once | Watches each robot and spider out of the ship and out of the sky until it lands | PASS 2026-11-12 |
| 40 | Reload, eight points, a 6-minute battle | Triangle's reload, the points' letters, the jetpacks' height, posts and goals every 10 s | PASS 2026-11-13 |
| 41 | Diagnosis: the Sewer Exit's point | Respawns there and lists the nav polys and meshes around it | 2026-11-13 |
| 42 | A point's minimap mark | Films the mark and its letter at two points | PASS 2026-11-13 |
| 43 | Diagnosis: the bridge between two slums | Logs the bridges and the units near them every 3 s | 2026-11-13 |
| 44 | Capture: a red guard's death | Films the player's red guard and an AI red guard dying | 2026-11-13 |
| 45 | The page on switching on, the rifle's shot, deaths, redeploy | The battle's page at once, the shot on the whole body, a red guard's dissolve, the spectator's choice, the spawns' reach | PASS 2026-11-13 |
| 46 | Capture: the rifle's shot | Traces the shot frame by frame and films a dissolve | 2026-11-13 |
| 47 | Diagnosis: the class's sounds | Logs Jak's sounds and effects as three classes take a hit and jump | 2026-11-14 |
| 48 | Damage, health pack, one jump | Kills a guard of each side with the rifle, a health pack, a guard's single jump | PASS 2026-11-14 |
| 49 | Diagnosis: targets | Every 5 s for 3 minutes, each unit's foe and march | 2026-11-14 |
| 50 | Reserves meter, goals kept, minimap marks | Three minutes of battle; the stuck units put back on their way; a point's letter and share | PASS 2026-11-14 |
| 51 | Title menu, setup, victory | The title menu, the setup page, a points victory, then a battle ended by its time limit | PASS 2026-11-14 |
| 52 | Class page and respawn point | The three-column class page, a death and its respawn point, a redeploy | PASS 2026-11-14 |
| 53 | Capture: class portraits | Shoots each class model alone on black, for `make_portraits.py` | 2026-11-14 |
| 54 | The battle under the menus, deaths, falls | The battle running under the pause page, the death's frame and choices, fall damage and the class's cry | PASS 2026-11-14 |
| 55 | Diagnosis: page scrolling and the respawn camera | Down held on the pause page; the camera after a redeploy and a respawn | 2026-11-14 |
| 56, 57 | Diagnosis: targets and stuck units | Logs each unit's foe, place and goal every 5 s | 2026-11-14 |
| 58 | Pickups fall to the ground | Queues four pickups 15 m up; they rest on the ground | PASS 2026-11-14 |
| 59, 60 | Diagnosis: units at NaN | Seven minutes, every unit's state every 10 s, then a trap on the first NaN | 2026-11-15 |
| 61 | The red guard's jump, strafes, weapon change, speeds | X held, L2 and R2 sideways only, the weapon change on one model, Quit to the title | PASS 2026-11-15 |
| 62 | Jump height, left strafe, run speeds | The jump held and tapped, the mirrored strafe, three classes' speeds | PASS 2026-11-15 |
| 63, 64 | Diagnosis: the spider's speed, the jump's frames | Logs the spider at two speeds, and the jump's first 0.3 s | 2026-11-15 |
| 65 | Capture radius, camera zoom, clips | The player counted 30 m from a point, L3 + right stick zoom, the run clip's rate | PASS 2026-11-15 |
| 66 | Capture: the guards' weapons | Shoots the blue and red guards with each weapon on black | 2026-11-15 |
| 67, 68 | The jetpack's rocket and boost | Rockets fly and hurt, R2's boost, no dive kick, the rocket icon, rockets dropped by fallen jetpacks | PASS 2026-11-15 |
| 69 | The robotguard's grenades | Ten a life from each fist in turn, their damage and icon, grenades dropped by fallen robotguards | PASS 2026-11-15 |
| 70, 71 | The spider's chain shock and blast | The shock jumping to 2 more foes; the charged blast, its cloud and the far camera | PASS 2026-11-15 (the headbutt's 12 m reach not measured) |
| 75 | Stability at 63 units a side | Two minutes with Jak 3's six street sections loaded | PASS 2026-11-15 |
