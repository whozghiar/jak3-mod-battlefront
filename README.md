# Battlefront — Jak 3

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%203-orange.svg" alt="Target Game">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

> **Contents:** [Overview](#overview) · [Key Features](#key-features) · [How to Play](#how-to-play) · [Download & Play](#download--play-via-opengoal-launcher-players) · [Developer Setup](#developer-setup--local-compilation) · [Demo Video](#demonstration-video) · [Technical Documentation](#technical-documentation)

---

## Overview
Battlefront for Jak 3: the Freedom League and the Krimzon Guard fight over a war zone with 500 units each, and you play any class of either side.

<p align="center">
  <img src="docs/img/mod/red-guard.gif" width="640" alt="Playing a red Krimzon Guard from Jak 2 against the Freedom League's blue guards">
</p>

- **Target Game:** Jak 3
- **Repository:** [`whozghiar/jak3-mod-battlefront`](https://github.com/whozghiar/jak3-mod-battlefront), created from the modding base [`whozghiar/jak-project`](https://github.com/whozghiar/jak-project)

## Key Features
- **Battles over the whole of Haven City:** pick a side and a class; the battlefield is the whole city, with no force field. Each side starts with 500 units; every death takes one, and the first side down to 0 loses. Up to 20 units per side fight at once around you, and they stay on the battlefield wherever you look.
- **Battle points:** each side has a base (the Freedom League's at the entrance of its headquarters, the Krimzon Guard's on the Port's east docks), and each district has a control point: the Port, the Industrial Zone, the Slums and Freedom HQ. They are neutral at the start, each a beam of light in its holder's color (white while neutral). A side with more units than the other within 15 m of a point for 30 seconds captures it. Units walk the streets toward their side's points: half of them guard a point it holds, the others march on the nearest one it does not hold. Far from you, where no unit is drawn, the points still change hands: a side fights for a point from the points next to it.
- **Troop transports:** each side's units arrive by the A-G troop transport of Jak 2, red for the Krimzon Guard and blue for the Freedom League. It comes down over a point its side holds, the one nearest you first, where nothing stands above it (no roof, no bridge), and its units leave it each their own way: a guard jumps down from the hatch, a robotguard rolls out as a ball, a spider robot drops, a jetpack guard flies out.
- **Two armies:** the Freedom League (blue guards, jetpack guards) against the Krimzon Guard (red Krimzon Guards from Jak 2, jetpack guards, robotguards, spider robots).
- **Play any class:** each of the six classes has its own model, moves and weapons, previewed turning on the class page with what it does and its own buttons, shown as the pad's icons: switch between tazer, rifle and grenade launcher, roll and strafe as a guard, fly as long as you like and boost on dark eco with the jetpack, roll as a ball and raise a red shield as a robotguard, or leap 11 m high and sprint on blue eco as a spider robot.
- **A third-person shooter camera:** as in Star Wars Battlefront (2004), over your class's right shoulder. The right stick turns it left and right and tilts it up and down, the crosshair stays in the middle of the screen, and your class faces where you aim while the left stick moves it forward, back and sideways.
- **Free aim:** every class shoots where the crosshair points; only the tazer locks onto the nearest foe by itself.
- **Health and damage on one 24 point scale:** guards and robotguards have 24 points, jetpack guards 18, spider robots 12. A rifle shot takes 8, a grenade 20, the tazer 24, a close attack 10 (a spider's bite 12), a jetpack's shot 6 and a robotguard's shot 4. Running into a foe does not hurt it.
- **Friends and foes:** your side never hurts or targets you; the enemy goes for you when you come within 50 m; every unit fights the nearest foe until one of them falls.
- **Ammo and pickups:** a guard's rifle holds 10 rounds with 20 more carried, its grenade launcher 5 grenades; the tazer needs no ammo but recharges for 20 s after each strike. The battle's guards on both sides carry rifles and grenade launchers: the tazer is yours alone. Three fallen units in every ten drop something: ammo, health, or dark eco, which refills a jetpack's boost.
- **A soldier's HUD:** the reserves at the top, as bars in the style of Star Wars Battlefront (2004) (yours in green, the enemy's in red), your kills on the left, the crosshair, your gun's icon at the top right with its rounds as shells and a count (10/20 for the rifle, the grenades left, nothing for the tazer but its recharge seconds), and your class's gauge in Jak's eco gauges: jetpack boost as dark eco, spider blue eco in blue, robotguard shield in red.
- **Outside the campaign:** during a battle no mission can start, no vehicle can be taken, and Save, Load Game and Secrets are greyed out in the START menu.
- **The streets only:** doors to the interiors stay shut, and no mission, vehicle or parked car is there. A ceiling keeps the jetpacks over the streets.
- **Jak 2 models in Jak 3:** the red Krimzon Guard and the jetpack guard of Jak 2.
- **Watch, then respawn where you like:** when you fall, the camera follows one of your side's units for 4 seconds, then you pick where you come back on the map of the whole city, your base or a control point your side holds, and deploy there with your class and fresh ammo.
- **Redeploy:** 30 seconds after your last shot, blow or hit taken, START > Options > Gamemode > Battlefront > **Redeploy** takes you to the same map, without counting a death.
- **Off by default:** nothing changes until you turn it on in the Mods menu.

## How to Play
1. In game, open the Mods menu with **L3 + SELECT**, then switch on **battlefront > Battlefront mode**.
2. Open the START menu: **Options > Gamemode > Battlefront > New battle**.
3. Choose the war zone, Haven City, then your side; the whole city is shown on its minimap, with both bases and the control points.
4. The class page follows at once, while your side's spawn loads behind it: the class under the cursor turns in a frame next to the list as soon as the models are in, its health, what it does and its buttons under the list. Once "Loading the war zone..." gives way to "Deploy", X deploys you with fresh ammo.
5. The reserves of both sides are shown at the top of the screen: your side's bar and count in green, the enemy's in red. Under them, the control points A (Port), B (Industrial Zone), C (Slums) and D (Freedom HQ) in their holder's color, with the capture under way in percent.
6. When you fall, you watch the battle for 4 seconds, then the D-pad picks your base or one of the control points your side holds on the city's map, and X deploys you there (the game loads that district first when it is far). You keep your class and get fresh ammo.
7. During a battle, the same START page has **Change class** (the battle goes on), **Restart the battle**, **Quit the battle**, and **Redeploy** once you have been out of combat for 30 seconds.
8. Switching the mode off in the Mods menu during a battle loads your last save.

<p align="center">
  <img src="docs/img/mod/menu.gif" width="480" alt="The four war zones, each district on its minimap, then the side">
  <img src="docs/img/mod/class.gif" width="480" alt="The class page: the class under the cursor turns in a frame next to the list">
</p>

When a side's reserve reaches 0, the result page shows the winner and the losses of both sides; X ends the battle and gives you the city back.

### The battlefield

The whole of Haven City. The game loads the city's sections around you as it does outside a battle; the units are where you are, and the points away from you are fought for without them.

| Point | Where |
|---|---|
| Freedom League base | the entrance of the Freedom League's headquarters |
| Krimzon Guard base | the Port's east docks, by the Krimzon Guard's war zone |
| A: Port | a street of the Port, between its docks |
| B: Industrial Zone | the middle of the Industrial Zone |
| C: Slums | the old slums by the Industrial Zone |
| D: Freedom HQ | the slums south of the headquarters |

| Port | Industrial Zone |
|---|---|
| <img src="docs/img/mod/zone-port.gif" width="400" alt="A blue guard running and firing at the west docks, then at other spots of the Port"> | <img src="docs/img/mod/zone-industrial.gif" width="400" alt="A blue guard running through spots all over the Industrial Zone"> |
| **Slums** | **Freedom HQ** |
| <img src="docs/img/mod/zone-slums.gif" width="400" alt="A blue guard running through spots all over the Slums"> | <img src="docs/img/mod/zone-freehq.gif" width="400" alt="A blue guard running through spots all over the slums around the Freedom HQ"> |

*Recorded in game in an earlier version, when a battle held one district: its streets are the same.*

<p align="center">
  <img src="docs/img/mod/victory.png" width="480" alt="Result page of a Freedom League victory">
</p>

### Classes

| Class | Controls |
|---|---|
| Blue Guard, Red Krimzon Guard | 24 points. R1: fire, while you walk. The rifle holds 10 rounds, with 20 more carried: the guard reloads from them when the magazine is empty. The grenade launcher throws the 5 grenades you carry. The tazer strikes once, 24 points (a whole health bar) within 12 m, then recharges for 20 s, with no reload. Square: rifle butt, one every 1.5 s. L2 + left stick: a roll that way, head over heels, about 4 m. Hold R2 + left stick: strafe, still facing ahead. The tazer's strike is a stab, and you keep walking while you strike. D-pad: left tazer (the guard holds a short stun baton), down rifle, up grenade launcher |
| Jetpack guards | 18 points. Hold X to climb, hold Circle to come down, let go of both to hover, for as long as you like. Hold R2: boost toward the left stick (ahead when it rests) while the gauge lasts, 3 s in a full one; only dark eco refills it. The jetpack always floats a little above the ground. R1: two quick shots. Square: dive kick |
| Robotguard | 24 points. Slower. R1: two shots. Square: a full punch, one every 1.5 s. R2: roll as a ball, as far as you like; R2 again stands it up. Circle: a red shield for 5 s that stops every shot, blast and blow while you keep moving, then 25 s to recharge |
| Spider Robot | 12 points. Faster. X: a leap 11 m high. Circle: bite, one a second. Hold R2: blue eco sprint at double speed for 10 s; the gauge refills in 10 s |

Aim with the right stick: pushed right the view turns right, pushed up it looks up (switching a third-person camera inversion in the game's camera options turns that axis the other way). Shots and grenades go where the crosshair points, and it turns red on a foe. The tazer reaches 12 m and aims by itself at the nearest foe in front of you. The rifles spend yellow ammo and the grenade launcher red ammo; the tazer, the jetpacks' and the robotguard's guns need none. Every close attack lands with the sound of Jak's punch. No citizens walk the streets during a battle.

<p align="center">
  <img src="docs/img/mod/hud.png" width="720" alt="Left: a blue guard's tazer with its gun icon and ammo. Middle: a jetpack's fuel in the dark eco gauge. Right: the robotguard's red shield and its roll gauge">
</p>

| Blue Guard | Blue Guard (Jetpack) |
|---|---|
| <img src="docs/img/mod/blue-guard.gif" width="400" alt="Blue Guard: rifle, tazer arc, grenade launcher and rifle butt, with their gun icons"> | <img src="docs/img/mod/jetpack.gif" width="400" alt="Blue jetpack guard: climb, salvos while hovering, coming down, dive kick"> |
| **Red Krimzon Guard** | **Red Krimzon Guard (Jetpack)** |
| <img src="docs/img/mod/red-guard.gif" width="400" alt="Red Krimzon Guard: rifle, tazer arc, grenade launcher and rifle butt"> | <img src="docs/img/mod/red-jetpack.gif" width="400" alt="Red jetpack guard: climb, salvos while hovering, coming down, dive kick"> |
| **Robotguard** | **Spider Robot** |
| <img src="docs/img/mod/robotguard.gif" width="400" alt="Robotguard: salvos, the red shield, a roll as a ball, a punch"> | <img src="docs/img/mod/spider.gif" width="400" alt="Spider Robot: blue eco sprint, leap, bites"> |

*Recorded in game, at the Port: every weapon of every class.*

| Camera | Guard rolls | Jetpack hovering still |
|---|---|---|
| <img src="docs/img/mod/tps-camera.gif" width="260" alt="The right stick turns the view right then left while a blue guard stays over the camera's shoulder, then the guard strafes and walks forward"> | <img src="docs/img/mod/guard-roll.gif" width="260" alt="A blue guard rolls head over heels to the right, then ahead, with L2 and the left stick"> | <img src="docs/img/mod/jetpack-hover.gif" width="260" alt="A blue jetpack guard hovering 10 m up, left alone"> |

*Recorded in game, at the Port.*

Menus are in French when the game language is French.

## Download & Play via OpenGOAL Launcher (Players)

> [!TIP]
> **No developer environment required!** Players can install and play this mod directly using the official OpenGOAL Launcher:

### Option A — Add Custom Mod Source (Recommended)
1. In the **OpenGOAL Launcher**, navigate to **Settings ▸ Mods ▸ Add Custom Mod Source**.
2. Paste this catalog URL:
   ```text
   https://raw.githubusercontent.com/whozghiar/jak3-mod-battlefront/main/index.json
   ```
3. Go to the **Mods** tab, locate **Battlefront**, and click **Install**.
4. Select your clean PS2 game ISO when prompted. The launcher will automatically extract assets and launch the game!

### Option B — Manual Installation from GitHub Releases
1. Download the pre-built package for your operating system from the [Releases](https://github.com/whozghiar/jak3-mod-battlefront/releases) tab (`windows-v*.zip` or `linux-v*.zip`).
2. Extract the archive into your OpenGOAL Launcher features directory:
   - **Windows:** `%APPDATA%\OpenGOAL-Launcher\features\jak3\mods\_local\battlefront\`
   - **Linux:** `~/.config/OpenGOAL-Launcher/features/jak3/mods/_local/battlefront/`
3. Launch the game from the OpenGOAL Launcher.

---

## Developer Setup & Local Compilation

If you want to modify or compile this mod locally from source:

### 0. Get the Source
Already working in a clone of [`whozghiar/jak-project`](https://github.com/whozghiar/jak-project)? Switch to this mod there, keeping your extracted game data:
```bash
task modding-switch -- jak3-mod-battlefront
```
Otherwise clone it on its own; the knowledge base used by AI agents is a submodule, so clone with it:
```bash
git clone --recurse-submodules https://github.com/whozghiar/jak3-mod-battlefront.git
```
To pull the latest modding base into this mod later, run `task modding-sync-branch`.

### 1. Select the Active Game
Make sure your environment is targeting Jak 3:
```bash
task set-game-jak3
```

### 2. Binary Compilation
- **Status:** Required: the mod changes the renderer (`Shadow2.cpp`, so that a battle full of shadows does not stop the game), so build the game with `task build-release-game`.
- **Details:** The decompiler is master-dev's.
```bash
# GOAL-only mod: nothing to build — go straight to the REPL below.
# Engine / compiler C++ changed:
task build-release-game
# Decompiler or decompiler/config changed (then step 3 is mandatory):
task build-release-decomp
```

### 3. Asset Extraction
- **Status:** Required, with your Jak 2 and Jak 3 disc files in `iso_data/jak2` and `iso_data/jak3`.
- **Details:** The Jak 2 models are not in the repository: `task modding-models` makes them from your own discs (`custom_assets/jak3/models/models.jsonc`), then `task extract` bakes them into the Haven City unit levels. A launcher install does both by itself, and needs Jak 2 installed in the launcher.
```bash
task modding-models
task extract
```

### 4. Launch the Game
Run the game natively:
```bash
task boot-game
```
*(Or launch via the OpenGOAL REPL using `task repl`, then compile and run with `(mi)` and `(r)`).*

## Demonstration Video

[![Demonstration Video](https://img.youtube.com/vi/{YOUTUBE_ID}/maxresdefault.jpg)](https://youtu.be/{YOUTUBE_ID})

**[Watch the demonstration video on YouTube](https://youtu.be/{YOUTUBE_ID})**

> [!NOTE]
> *Demonstration videos must be hosted externally on YouTube to prevent repository bloating. Replace `{YOUTUBE_ID}` with your YouTube video ID (e.g. `MnqnybexhSA` from `https://youtu.be/MnqnybexhSA`).*

## Technical Documentation
For the complete technical breakdown, architecture, developer notes and change log, refer to:
- [`docs/modding/current_mod/battlefront_readme.md`](docs/modding/current_mod/battlefront_readme.md)

---
*(AI-assisted)*
