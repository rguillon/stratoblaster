# Roadmap: Stratoblaster

## Overview

Stratoblaster is an old-school vertical shoot 'em up with modern 3D graphics (Babylon.js), running entirely in the browser. This is a brownfield roadmap: the first release (4 worlds x 5 levels, World 5 dropped by D-089) was built in twelve spec-driven phases, and all twelve are validated (see `specs/PROGRESS.md`). The journey: a main menu and the three player ships (Phases 1-2), the player's weapons (3), the generated-level technology proven on Level Zero (4), the first 21 enemy kinds (5), then four worlds of five levels each with their bosses (6-10), then the score / lives / bombs core loop (11) and pause, generated music and settings (12).

`specs/` is the single source of truth (human-owned); this file is a derived view. On any conflict, `specs/` and `specs/DECISIONS.md` win. No phase beyond 12 is defined yet: the next phase is created by the human with `/new-phase`.

## Milestones

- ✅ **v1.0 First release** - Phases 1-12 (complete: all twelve phases validated, last on 2026-10-27)

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work, numbered exactly as in `specs/PROGRESS.md`
- Decimal phases (2.1, 2.2): Urgent insertions (none so far)

Phase 2 has no dependency and was implemented before Phase 1 (2026-10-22). Phase 0 (project scaffold: tooling, Makefile, git hooks, CI, deploy; 2026-10-22) is logged in `specs/PROGRESS.md` but is not a board phase.

- [x] **Phase 1: Main Menu** - Loading screen, darksynth title, ship select and level select with keyboard, gamepad and touch (validated 2026-10-23)
- [x] **Phase 2: Player Ships** - Three code-generated player ships (balanced, heavy, light) and the `player_ship/` viewer (validated 2026-10-22)
- [x] **Phase 3: Player Shots** - Bullet, laser and missile weapons with five levels each and the `player_shots/` viewer (validated 2026-10-23)
- [x] **Phase 4: Level Zero** - Generated terrain, sea, clouds, roads and props on a 3-minute test level under the tilted playfield camera (validated 2026-10-23)
- [x] **Phase 5: First Enemies** - 21 enemy kinds (11 base, 5 veteran, 5 elite) with generated models, movement and attacks, plus the `enemies/` viewer (validated 2026-10-24)
- [x] **Phase 6: World 1** - First playable levels 1-1 to 1-5 (sea to green grass to desert), wave scripts and rising difficulty (validated 2026-10-25)
- [x] **Phase 7: Bosses** - Boss engine plus ten World 1 bosses, boss health bar, mini boss checkpoint and level end on the final boss (validated 2026-10-25)
- [x] **Phase 8: World 2** - Industrial Desert levels 2-1 to 2-5, atmosphere and weather engine, ten new bosses (validated 2026-10-25)
- [x] **Phase 9: World 3** - Industrial Towns levels 3-1 to 3-5, rain and lightning, ten new bosses (validated 2026-10-26)
- [x] **Phase 10: World 4** - Metropolis levels 4-1 to 4-5, ash and embers weather, ten new bosses ending with the Caldera Throne (validated 2026-10-26)
- [x] **Phase 11: Score, Lives and Bombs** - Score and saved high score, extra lives, bombs and their bonuses (validated 2026-10-26)
- [x] **Phase 12: Pause, Music and Settings** - Pause menu, generated music and sound effects, volume settings (validated 2026-10-27)
- [ ] **Phase 13: Perf** - Instant button feedback, fast level loading, no freezes in play (Worlds 3 and 4)

## Phase Details

Every phase below is Validated. For each: the spec file under `specs/phases/` holds the human-owned requirements and the agent's implementation report; the branch is `phase-NN`; the squash-merge tag is `v0.NN.0` per `specs/PROGRESS.md`. Where human-owned spec text is stale against a later decision, the decision wins (14 approved warnings in `.planning/INGEST-CONFLICTS.md`); success criteria below already follow the decision-adjusted behaviour.

### Phase 1: Main Menu

**Goal**: The player opens the game, sees a loading screen then a darksynth title screen, and walks Title -> Select Ship -> Select Level -> Game, able to go back at each step, with keyboard, gamepad or touch/mouse.
**Depends on**: Phase 2 (ship select shows the player ships)
**Requirements**: P01-R01, P01-R02, P01-R03, P01-R04, P01-R05, P01-R06, P01-R07, P01-R08, P01-R09, P01-R10, P01-R11, P01-R12, P01-R13, P01-R14, P01-R15
**Success Criteria** (what must be TRUE):

1. A real-progress loading bar leads automatically to a title screen that shows the high score (0 when absent or unreadable), the version with commit hash and a controls hint; a browser without WebGL2 sees a friendly explanation and no console error
2. The player can go Title -> Select Ship -> Select Level -> game and back at each step using only the keyboard (arrows/WASD by key position, so AZERTY works), only a gamepad, or only mouse/taps
3. Ship select shows the three ships rotating with name, speed and health, wraps with Left/Right, and the last chosen ship is remembered across reloads
4. Level select shows the 4 x 5 grid 1-1 to 4-5, and every menu stays fully visible at 800x600, 1920x1080 and 390x844 with the selected entry identifiable without colour
   **Plans**: n/a (delivered through the spec-driven loop: `specs/phases/phase-01-main-menu.md`)
   **UI hint**: yes
   **Validation**: 2026-10-23, branch `phase-01`, tag `v0.01.0`; 99.61 % lines, 96.53 % branches, 228 unit tests, 23 e2e
   **Supersessions**: in the game screen Esc/Back leaving directly is superseded by Phase 12 (pause); look is darksynth per D-103 (the "striped sun" wording is stale; the sun emblem was removed); the P01 grid tunable "5 x 5" is stale (4 x 5, D-089)

### Phase 2: Player Ships

**Goal**: The three player ships exist as code-generated, low-poly 3D models with their speed and health stored as data, and can be viewed together on the `player_ship/` page.
**Depends on**: Nothing (first implemented; no dependency)
**Requirements**: P02-R01, P02-R02, P02-R03
**Success Criteria** (what must be TRUE):

1. The `player_ship/` page shows the three ships rotating side by side with a shiny grey/blue look and blue light effects behind each reactor
2. The balanced ship (VF-31J-inspired, dual reactor), the heavy ship (flying-wing bomber) and the light ship (four wings with a reactor each) are recognisably distinct on manual review
3. Speed factors and health are data: balanced 1.0 / 100 HP, heavy 0.8 / 140 HP, light 1.4 / 80 HP; the base speed is 225 px/s (D-047; the phase 2 Goal text saying 100 px/s is stale)
4. Each ship stays under 2,000 triangles and the viewer shows the triangle count
   **Plans**: n/a (`specs/phases/phase-02-player-ships.md`)
   **Validation**: 2026-10-22, branch `phase-02`, tag `v0.02.0`; 99.51 % lines, 98.05 % branches, 100 unit tests, 3 e2e

### Phase 3: Player Shots

**Goal**: Each player ship can fire three weapon kinds (bullet, laser, missile), each upgradable over five levels, viewable on the `player_shots/` page.
**Depends on**: Phase 2
**Requirements**: P03-R01, P03-R02, P03-R03, P03-R10, P03-R11
**Success Criteria** (what must be TRUE):

1. The `player_shots/` page shows each ship firing bullets, laser and missiles at levels 1 to 5, with the layouts of the spec (single, dual, diagonal fans)
2. Bullets do 10 damage at 8 shots per second; the laser is a focused piercing beam doing 80/140/200/260/320 dps (GD-33, D-059); missiles accelerate, home on the closest enemy within about 320 px and do 14 damage
3. When a level has several streams they fire one after the other, evenly spaced, without changing the overall rate
4. Shots start at each ship's nose and show particle hit effects, with an FPS / polygons tile on the page
   **Plans**: n/a (`specs/phases/phase-03-player-shots.md`)
   **Validation**: 2026-10-23, branch `phase-03`, tag `v0.03.0`; 99.45 % lines, 90.8 % branches, 314 unit tests, 27 e2e

### Phase 4: Level Zero

**Goal**: A generated test level proves the technology used to build the real levels: terrain, sea, clouds, roads and props seen from the tilted playfield camera, on the `level_zero/` page.
**Depends on**: Phase 3
**Requirements**: P04-R01, P04-R02, P04-R03, P04-R04, P04-R05, P04-R06, P04-R07
**Success Criteria** (what must be TRUE):

1. The `level_zero/` page scrolls a roughly 3-minute generated level seen from a camera tilted 35 degrees to the back
2. Terrain comes from a software-sculpted heightmap with generated textures fading by slope and altitude; the sea reflects the sun with sand beach, shallows and surf; clouds always float above the terrain
3. Randomly generated roads and paths cross the map and buildings appear only along them, with industrial, technical, futuristic-home and dead-tree props
4. Level Zero is not listed in the level select (D-020, reviewer-accepted); it is reached through the `level_zero/` page
   **Plans**: n/a (`specs/phases/phase-04-level-zero.md`)
   **Validation**: 2026-10-23, branch `phase-04`, tag `v0.04.0`; 99.35 % lines, 89.94 % branches, 545 unit tests, 35 e2e
   **Supersessions**: the Goal wording "reachable from the main menu as the first level" is stale (D-020)

### Phase 5: First Enemies

**Goal**: The game has its enemy roster: 21 kinds, each with its own code-generated model, movement and attack, all watchable and shootable on the `enemies/` page.
**Depends on**: Phase 4
**Requirements**: P05-R01, P05-R02, P05-R03, P05-R04, P05-R05, P05-R06, P05-R07, P05-R08, P05-R09, P05-R10, P05-R11, P05-R12, P05-R13, P05-R14, P05-R15, P05-R16, P05-R17, P05-R18, P05-R19, P05-R20, P05-R21, P05-R22, P05-R23, P05-R24
**Success Criteria** (what must be TRUE):

1. The `enemies/` page lists all 21 kinds, every one can be picked without console errors, and each can be viewed as a model, as a wireframe with hit circles, and shot by an invulnerable player ship with hit particles and explosions
2. The eleven base kinds (Gnat, Hornet, Scout, Strafer, Weaver, Spinner, Lancer, Rocketeer, Bulwark, Splitter, Carrier) each show their distinct path and attack: aimed bullets, fans, spirals, a laser with a 1 s warning line, missiles the player can shoot down, divers and launchers
3. The five veteran kinds (Wasp, Mortar, Mantis, Phantom, Minelayer) and five elite kinds (Hydra, Orbiter, Scissor, Juggernaut, Hive) work, including parts on swinging or orbiting joints that can be destroyed without killing the enemy
4. Veteran kinds appear in World 3 and World 4 waves and elites in World 4 only, while Worlds 1 and 2 are unchanged
   **Plans**: n/a (`specs/phases/phase-05-first-enemies.md`)
   **Validation**: 2026-10-24, branch `phase-05`, tag `v0.05.0`; 99.27 % lines, 88.83 % branches, 668 unit tests, 40 e2e
   **Supersessions**: the "first 10 kinds" Goal predates P05-R12 (Carrier) and P05-R13..R24 (ten more kinds, D-090)

### Phase 6: World 1

**Goal**: World 1 has five playable levels, 1-1 to 1-5, each about 4 minutes long, cut from one journey over open sea, green grassland and desert; the player flies the chosen ship, shoots waves of the phase 5 enemies, and each level is harder than the last.
**Depends on**: Phase 5
**Requirements**: P06-R01, P06-R02, P06-R03, P06-R04, P06-R05, P06-R06, P06-R07, P06-R08, P06-R09, P06-R10
**Success Criteria** (what must be TRUE):

1. From level select the player can start any of 1-1 to 1-5 (levels are never locked by progress) and fly the chosen ship over scrolling scenery, staying inside the playfield, shooting with Space, button or touch, with enemies, hit particles and explosions
2. The five levels read as one journey: open sea, Green coast, Green country, Dry lands, Deep desert, with props rising per level and a fixed time of day per level from midday to dusk (D-109)
3. Each level lasts 240 s +/- 10 s, enemy waves are deterministic and triggered by scrolled distance, new kinds are introduced level by level, and enemy count, total HP and peak on-screen count rise strictly from 1-1 to 1-5
4. Debug URL options (`?level=1-3&t=120`, F fast-forward, 10 s jumps) start any level at any time and do nothing without a debug option
   **Plans**: n/a (`specs/phases/phase-06-world-1.md`)
   **Validation**: 2026-10-25, branch `phase-06`, tag `v0.06.0`; 99.33 % lines, 89.5 % branches, 789 unit tests, 50 e2e
   **Post-validation rework**: D-109 (2026-10-26/27, reviewer-requested: sea -> green grass -> desert gradient, time of day per level, farms; 1-5 ends on "Deep desert"); light verification green (typecheck, build, 116 e2e); awaiting the reviewer's check (open item in `STATE.md`)
   **Supersessions**: weapon levels carry across completed levels (D-071), replacing "every level starts at guns level 1"; level end is the final boss (P07-R06); Esc leaving the level is superseded by pause (P12-R01); the enemy-count tunables are stale (279 / 335 / 433 / 498 / 537 enemies, D-044 and D-051)

### Phase 7: Bosses

**Goal**: Every World 1 level has a mini boss around its middle and a final boss at its end, each a large generated ship of destroyable parts with its own health bar, changing attack pattern per destroyed part, and a level completes when its final boss dies.
**Depends on**: Phase 6
**Requirements**: P07-R01, P07-R02, P07-R03, P07-R04, P07-R05, P07-R06, P07-R07, P07-R08, P07-R09, P07-R10
**Success Criteria** (what must be TRUE):

1. Ten distinct World 1 bosses (a mini boss and a final boss per level, Reef Warden / Storm Petrel to Sentinel / Overlord) arrive from the top, take no damage until in place, and show destroyable parts that flash, smoke, explode and change the attack pattern when destroyed
2. A slim vertical boss health bar on the left edge shows the boss name and a notch per part; the ground scroll eases over 2 s to the boss's fight speed and back after the kill, and no new waves spawn while a boss lives
3. Destroyed parts may drop weapon bonuses deterministically and a final boss core always drops one
4. Destroying the mini boss saves a checkpoint; after game over the player can Continue just after it or return to level select; the level completes only after the final boss is destroyed
5. The `bosses/` page lets every boss be picked, viewed as a model or wireframe and advanced part by part (K) for manual validation
   **Plans**: n/a (`specs/phases/phase-07-bosses.md`)
   **Validation**: 2026-10-25, branch `phase-07`, tag `v0.07.0`; 99.34 % lines, 88.69 % branches, 939 unit tests, 54 e2e

### Phase 8: World 2

**Goal**: World 2, the Industrial Desert, has five playable levels, 2-1 to 2-5, about 5 minutes each, running from the deep desert to dense factories with a time of day per level, ten new bosses, and difficulty above World 1.
**Depends on**: Phase 7
**Requirements**: P08-R01, P08-R02, P08-R03, P08-R04, P08-R05, P08-R06, P08-R07, P08-R08, P08-R09, P08-R10, P08-R11, P08-R12
**Success Criteria** (what must be TRUE):

1. Level select shows 2-1 to 2-5 all playable; finishing 1-5 highlights 2-1; each level lasts 300 s +/- 10 s
2. The levels read as one journey, Great erg, Mining mesas, Oil fields, Industrial belt, Factory district, with no sea, slow transitions, sand giving way to paved industrial ground, and morning / midday / afternoon / dusk / night times of day that stay readable
3. The engine supports a time-of-day and cloud atmosphere and a weather system with strength 0 to 1 that never changes the simulation (the snow kind is kept but no World 2 level uses it since the rework)
4. Ten new World 2 bosses (Floe Breaker / Narwhal to Ice Queen / Boreal Citadel) are each above the World 1 boss of the same level and kind; difficulty rises strictly from 2-1 to 2-5 and 2-5 is harder than 1-5
5. Debug options accept World 2 levels with `weather=0` and `look=<time of day>`, and the `bosses/` page lists World 2 bosses after World 1
   **Plans**: n/a (`specs/phases/phase-08-world-2.md`)
   **Validation**: 2026-10-25, branch `phase-08`, tag `v0.08.0`; 99.26 % lines, 88.04 % branches, 1084 unit tests, 65 e2e
   **Post-validation rework**: D-110 (2026-10-27, reviewer-requested: Frozen North replaced by the Industrial Desert); full gate green (1573 unit tests, 99.41 % lines, 117 e2e); awaiting the reviewer's check (open item in `STATE.md`)
   **Supersessions**: "blizzard", "aurora", "sea", "fjords" and "tundra" in the requirement text are historical (D-110); the "eleven kinds" wording is read with P05-R24

### Phase 9: World 3

**Goal**: World 3, the Industrial Towns, has five playable levels, 3-1 to 3-5, about 5 minutes each, running from the factories along canals and docks to garden villages of small houses, with rain and a thunderstorm, ten new bosses, and difficulty above World 2.
**Depends on**: Phase 8
**Requirements**: P09-R01, P09-R02, P09-R03, P09-R04, P09-R05, P09-R06, P09-R07, P09-R08, P09-R09, P09-R10, P09-R11
**Success Criteria** (what must be TRUE):

1. Level select shows 3-1 to 3-5 all playable; finishing 2-5 highlights 3-1; each level lasts 300 s +/- 10 s
2. The levels read as one journey from factories to garden villages of small houses (canals, rivers and ponds, no sea, no skyscraper), each level beginning where the previous one ended
3. Each level has its own look: 3-1 morning mist, 3-2 midday with rain, 3-3 afternoon thunderstorm, 3-4 dusk rain, 3-5 night rain stopping before the final boss; lightning flashes at most 3 times in any second and is the same for the same level
4. Ten new World 3 bosses (Mangrove Croc / River Leviathan to Jaguar / Verdant Crown), each above the World 2 boss of the same level and kind; difficulty rises strictly from 3-1 to 3-5 and 3-5 is harder than 2-5
5. Debug options accept World 3 levels with `weather=0` and `look=`, and the `bosses/` page lists World 3 bosses after World 2
   **Plans**: n/a (`specs/phases/phase-09-world-3.md`)
   **Validation**: 2026-10-26, branch `phase-09`, tag `v0.09.0`; 99.35 % lines, 87.25 % branches, 1210 unit tests, 77 e2e
   **Post-validation rework**: D-111 (2026-10-27, reviewer-requested: Jungle replaced by factories to garden villages); full gate green (1580 unit tests, 99.41 % lines); awaiting the reviewer's check (open item in `STATE.md`)
   **Supersessions**: "Worlds 4 and 5 stay greyed out" is a phase-time statement (all 20 levels are unlocked, D-089); "all eleven kinds" is read with P05-R24

### Phase 10: World 4

**Goal**: World 4, the Metropolis, has five playable levels, 4-1 to 4-5, about 5 minutes each, running from garden-village houses through a town and mid-rise blocks to a downtown of skyscrapers, with ten new bosses ending with the Caldera Throne, the last boss of the game.
**Depends on**: Phase 9
**Requirements**: P10-R01, P10-R02, P10-R03, P10-R04, P10-R05, P10-R06, P10-R07, P10-R08, P10-R09, P10-R10, P10-R11, P10-R12, P10-R13
**Success Criteria** (what must be TRUE):

1. Level select shows 4-1 to 4-5 all playable as the last row (World 5 dropped, D-089); finishing 3-5 highlights 4-1; each level lasts 300 s +/- 10 s
2. The levels read as one journey from houses to skyscrapers with a river and slow transitions, no sea and no lava, each level beginning where the previous one ended, with ash and ember weather kept
3. World 4 enemy bullets get a light contrasting outline so they stay readable on red, orange and dark backgrounds
4. Ten new World 4 bosses (Cinder Crab / Steam Dreadnought to Ember Herald / Caldera Throne), each above the World 3 boss of the same level and kind; difficulty rises strictly from 4-1 to 4-5, stays beatable by a casual player, and the Caldera Throne is the hardest boss so far
5. Debug options accept World 4 levels with `weather=0` and `look=`, and the `bosses/` page lists World 4 bosses after World 3
   **Plans**: n/a (`specs/phases/phase-10-world-4.md`)
   **Validation**: 2026-10-26, branch `phase-10`, tag `v0.10.0`; 99.42 % lines, 87 % branches, 1384 unit tests, 88 e2e
   **Post-validation rework**: D-112 (2026-10-27, reviewer-requested: Volcanic Lands replaced by the Metropolis); full gate green (1591 unit tests, 99.4 % lines, 117 e2e); awaiting the reviewer's check (open item in `STATE.md`)
   **Supersessions**: lava (P10-R05), "magma lake" and "eruption look" criteria are historical (D-112, lava engine kept unused); "all eleven kinds" is read with P05-R24

### Phase 11: Score, Lives and Bombs

**Goal**: The player scores points for every enemy and boss part destroyed, sees the score and high score in the HUD, beats a saved high score shown on the title screen, collects extra lives and bombs, and can fire a bomb that clears enemy fire and damages every enemy on screen, completing the core loop of the vision.
**Depends on**: Phase 10
**Requirements**: P11-R01, P11-R02, P11-R03, P11-R04, P11-R05, P11-R06, P11-R07, P11-R08
**Success Criteria** (what must be TRUE):

1. The HUD shows a 7-digit score top-centre and a HI line (the larger of the saved high score and the current score), readable at 800x600 and 390x844 without overlap
2. Destroyed enemies add their kind's points (shot, bomb or ramming; leaving the screen scores nothing); a boss part scores 10 % of the boss points and its core the full points
3. When an attempt ends (complete, game over or leaving) a higher score is saved to the high score cookie and the Level complete and Game over panels show the score and "New high score!"; Continue from the mini boss checkpoint restarts with the checkpoint score
4. The player starts with 3 bombs; one press fires a bomb for 1 s (R or Left Shift, gamepad X or LB, touch BOMB button; E still switches weapon) that clears bullets, missiles and lasers, makes the player invincible and deals 100 damage once to every on-screen enemy and boss part
5. Pink-heart life bonuses and orange-B bomb bonuses drop from enemies, the mini boss core always drops a life, and full stocks convert to points
   **Plans**: n/a (`specs/phases/phase-11-score-lives-bombs.md`)
   **UI hint**: yes
   **Validation**: 2026-10-26, branch `phase-11`, tag `v0.11.0`; 99.42 % lines, 87.18 % branches, 1432 unit tests, 95 e2e

### Phase 12: Pause, Music and Settings

**Goal**: The player can pause a level at any time, resume, open settings or leave to the main menu; the game pauses itself when the tab is hidden; every level has its own generated music, boss fights switch to a more intense track, every action has a generated sound, and music and effect volumes are set in a saved settings screen.
**Depends on**: Phase 11
**Requirements**: P12-R01, P12-R02, P12-R03, P12-R04, P12-R05, P12-R06, P12-R07, P12-R08, P12-R09, P12-R10, P12-R11, P12-R12
**Success Criteria** (what must be TRUE):

1. Escape, P, gamepad Start or Select and a touch pause button pause the level with nothing advancing, and resume is exact; Backspace and gamepad B do nothing in the game; the pause menu offers Resume, Settings and Main menu with a "Leave the level?" confirmation
2. The page being hidden or the gamepad in use disconnecting pauses the game automatically, which never resumes by itself
3. A settings screen reachable from the title and the pause menu sets Music (default 6) and Sound effects (default 8) on 0-10 sliders saved in cookies, with audible feedback
4. Every level 1-1 to 4-5 has its own generated darksynth music, boss fights cross-fade to a faster, more stressful boss track, the menus share one looping theme, and every game event plays its own generated sound, with no audio file in the build
5. Audio freezes with pause and suspends when the page is hidden, and at most 16 sound effects play at once with priority replacement
   **Plans**: n/a (`specs/phases/phase-12-pause-music-settings.md`)
   **UI hint**: yes
   **Validation**: 2026-10-27, branch `phase-12`, tag `v0.12.0` (PR #23); validated by the reviewer without re-running `make check` for this phase; coverage from the latest full gate (after the World 4 rework): 99.4 % lines, 87.87 % branches, 1591 unit tests, 117 e2e

### Phase 13: Perf

**Goal**: The game feels instant: every button press gets visible feedback straight away, a level starts within a couple of seconds, and play in every level (Worlds 3 and 4 included) runs without freezes. Nothing about the look, content or rules changes.
**Depends on**: Phase 12
**Requirements**: P13-R01, P13-R02, P13-R03, P13-R04, P13-R05
**Success Criteria** (what must be TRUE):

1. The causes of the button lag, slow loading and World 3/4 freezes are measured and named; long frames, longest frame and loading time show in the F3 overlay and the e2e test API
2. Every menu and pause-menu button reacts visibly within 100 ms on the reference machine
3. Every level 1-1 to 4-5 is playable within 2 s of being confirmed, with a moving loading screen past 300 ms
4. After the first second of any level no frame exceeds 100 ms, and at most 3 frames per minute exceed 50 ms
5. Look, content, simulation results and bundle budget are unchanged
   **Plans**: n/a (`specs/phases/phase-13-perf.md`, Draft)
   **Supersessions**: P12-R06 still names the original World 2-4 themes (Frozen North, Jungle, Volcanic Lands), superseded by D-110 to D-112; P12-R05 explicitly scopes ENG-120's audio file formats out (all audio generated, D-097)

## Progress

**Execution Order:**
Phases execute in numeric order, except that Phase 2 (no dependency) was implemented first: 2 -> 1 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9 -> 10 -> 11 -> 12

| Phase                         | Plans Complete | Status      | Completed  |
| ----------------------------- | -------------- | ----------- | ---------- |
| 1. Main Menu                  | n/a            | Complete    | 2026-10-23 |
| 2. Player Ships               | n/a            | Complete    | 2026-10-22 |
| 3. Player Shots               | n/a            | Complete    | 2026-10-23 |
| 4. Level Zero                 | n/a            | Complete    | 2026-10-23 |
| 5. First Enemies              | n/a            | Complete    | 2026-10-24 |
| 6. World 1                    | n/a            | Complete    | 2026-10-25 |
| 7. Bosses                     | n/a            | Complete    | 2026-10-25 |
| 8. World 2                    | n/a            | Complete    | 2026-10-25 |
| 9. World 3                    | n/a            | Complete    | 2026-10-26 |
| 10. World 4                   | n/a            | Complete    | 2026-10-26 |
| 11. Score, Lives and Bombs    | n/a            | Complete    | 2026-10-26 |
| 12. Pause, Music and Settings | n/a            | Complete    | 2026-10-27 |
| 13. Perf                      | n/a            | Not started | -          |

## Next

No phase after 12 is defined. The human creates the next phase with `/new-phase 13 <name>` (requirements are human-owned and live in `specs/phases/`), after which `/implement-phase 13` follows the spec-driven loop. Per `CLAUDE.md`, a spec change after validation is a regression requirement of the next phase; the pending check of the World 1-4 reworks (D-109..D-112) is tracked in `STATE.md`.

---

_Roadmap derived: 2026-10-27 from the ingest of `specs/` (see `.planning/intel/SYNTHESIS.md`); `specs/` and `specs/DECISIONS.md` win on conflict._
