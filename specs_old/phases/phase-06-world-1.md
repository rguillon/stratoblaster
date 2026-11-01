# Phase 06 — World 1

**Status:** Ready  <!-- Draft | Ready -->
**Depends on:** Phase 5

---

## 🧑 Goal
World 1 has five playable levels, 1-1 to 1-5, each about 4 minutes long. The five levels are cut from one long journey: it starts over the open sea, crosses green grassland, then dries out into the desert, with more and more props along the way (reworked at the reviewer's request, 2026-10-26; was: the open sea, then more and more desert land and denser towns). From the level select screen, the player flies the chosen ship through a level, shoots the phase 5 enemies as they come in waves, and reaches the end of the level. Each level is harder than the one before it.

## 🧑 Requirements

> ID format `P06-Rxx`. Every requirement is **MUST** (no SHOULD / MAY).
> Write each requirement so it is testable. Add acceptance criteria when "done" isn't obvious.
> The scenery uses the phase 4 terrain tools (heightmap, sea, clouds, props, roads; P04-R01 to P04-R07) and the phase 5 enemies (P05-R01 to P05-R12). Durations, speeds and wave counts are listed in **Tunable values**.

### P06-R01 — World 1 in the level select  · MUST

World 1 has **5 levels**, like every world (vision, P01-R07). The World 1 row of the level select grid shows `1-1` to `1-5`, and all five are unlocked. Levels are never locked by progress: the player can pick any existing level at any time, without finishing the levels before it (reviewer's choice, 2026-10-24). Worlds 2 to 4 do not exist yet, so they stay greyed out, 5 levels each, until they are built (World 5 dropped by the reviewer, 2026-10-26). Which levels exist and which are unlocked still comes from `src/game/` data (ENG-142/144).

**Acceptance criteria**
- [ ] Given `level-select`, then the World 1 row shows exactly `1-1`, `1-2`, `1-3`, `1-4` and `1-5`, all unlocked.
- [ ] Given any World 1 level is confirmed, then the `game` screen starts that level.
- [ ] Given a fresh start (no cookie), then `1-5` can be confirmed straight away, without playing `1-1` to `1-4`.
- [ ] Given a level of worlds 2 to 4, then it is still greyed out (not built yet).

### P06-R02 — Playable level  · MUST

The `game` screen no longer shows the placeholder (P01-R08). It plays the chosen level:
- the level's scenery scrolls under the tilted playfield camera (P04-R05), at that level's ground speed (GD-01);
- the chosen ship (phase 2) is at the bottom of the playfield, moves with the game controls (GD-02 table, GD-10) and stays inside the playfield;
- the ship shoots with Space, the gamepad button or the touch button. It starts every level with the guns at level 1 (phase 3);
- enemies spawn from the level's wave script (P06-R07) and can be shot and destroyed, with hit particles and explosions (GD-62);
- Back (Esc) still goes back to the title screen (P01-R01).

**Acceptance criteria**
- [ ] Given level `1-1` is confirmed with the heavy ship, then the heavy ship flies over the scrolling 1-1 scenery and can move and shoot.
- [ ] Given the ship is pushed against an edge of the playfield, then it stays on screen.
- [ ] Given a player shot hits an enemy until its HP reaches 0, then the enemy explodes and is removed.
- [ ] Given the `game` screen, when Back is pressed, then the screen is `title`.

### P06-R03 — Level end  · MUST

When a level's scroll reaches the level's length, no more enemies spawn. Once the enemies still on screen are gone (destroyed or off screen, at most 10 s later), a "Level complete" overlay shows the level (e.g. `1-2`) and how many enemies were destroyed out of how many spawned. Confirm goes back to `level-select`, with the next level highlighted (or `1-5` again after `1-5`).

**Acceptance criteria**
- [ ] Given a level reaches its length, then no enemy spawns after that point.
- [ ] Given the overlay is shown after level `1-2`, then it shows `1-2` and the destroyed / spawned counts.
- [ ] Given the overlay, when Confirm is pressed, then the screen is `level-select` with `1-3` highlighted.

### P06-R04 — Duration  · MUST

Each World 1 level lasts **about 4 minutes**: the time from the start of the level to the end of its scroll (P06-R03) is 240 s ± 10 s at that level's ground speed.

**Acceptance criteria**
- [ ] Unit test: for each World 1 level, length ÷ ground speed is between 230 s and 250 s.

### P06-R05 — Scenery progression across the world  · MUST

> Reworked at the reviewer's request (2026-10-26): the five levels are cut from one gradient, sea → green grass → desert, with more and more props along the way. It was: open sea, a dry coast, then desert, desert towns and a desert city.
>
> Amended at the reviewer's request (2026-10-27): 1-5 ends in the desert too. No factory and no city in World 1: they are for other worlds.

The five levels are one journey cut into five pieces: the ground goes from the open sea to green grassland, then dries out into the desert, and there are more and more props (plants and buildings) along the way. Each level's ground is built from terrain sections (as in Level Zero), in this order:

| Level | Name | Sea | Land | Habitations |
|-------|------|-----|------|-------------|
| 1-1 | Open sea | Almost all sea, with small green islands and reefs. The first coast comes in the last 30 s. | Small islands with palms and bushes, then a green coast. | Almost none: a few lone huts or masts on the islands, a small fishing village on the final coast. |
| 1-2 | Green coast | It starts along the coast, with beaches and bays. The sea is gone after the first half. | Green coastal land, then green meadows with trees and groves. | Coastal villages along a coast road, then villages and farms in the meadows. |
| 1-3 | Green country | No sea. | Green meadows, woods and hills; in the last part, the grass turns dry and yellow. | Farms, villages and a market town with streets. |
| 1-4 | Dry lands | No sea. At most an oasis. | Dry grassland and scrub, then sand and rock, dunes, an oasis, a canyon and mesas. | Dry-land villages, then desert towns, outposts and mines. |
| 1-5 | Deep desert | No sea. | Sand to the end, dunes, a rocky pass. | Desert outskirts, great dunes, oasis villages, a rocky pass, desert towns, then a great oasis town on the sand at the end of the level. No factory, no city (reviewer, 2026-10-27). |

The number of props goes up from level to level, and within each level (the second half has more than the first). Each level begins on the same kind of ground the previous level ended on: 1-2 starts on the green coast where 1-1 ended, 1-3 on the meadows 1-2 ended on, 1-4 on the dry grassland 1-3 ended on, and 1-5 on the desert outskirts 1-4 ended on.

**Acceptance criteria**
- [ ] Given the 5 level definitions, then the share of the level that is over sea goes down from 1-1 to 1-3 (unit test), and 1-3, 1-4 and 1-5 have no sea section.
- [ ] Given the 5 level definitions, then grass covers the ground of 1-2 and 1-3 more than any other cover, and sand covers 1-4 and 1-5 more than grass (unit test).
- [ ] Given the 5 level definitions, then the number of props placed (plants and buildings) and the number of buildings both go up from 1-1 to 1-5, and in each level the second half has more props than the first (unit test, fixed seed).
- [ ] Given two levels in a row, then the next one starts with the same relief, ground cover and shore as the previous one ended with (unit test).
- [ ] Manual visual validation: sea, then green grass, then desert can be seen across the five levels, with more and more props, and each level begins where the previous one ended.

### P06-R06 — Green land, desert ground and props  · MUST

New generated ground and props for World 1 (GD-60, all made in code):
- **Ground:** a sand texture that fades into the existing rock texture with slope and altitude (P04-R01), and sand dunes: ripple-shaped heights, made with the heightmap tools. Grass (the existing `lush` cover) on the green land, fading through dry earth into the sand (added at the reviewer's request, 2026-10-26).
- **Vegetation:** dry bushes, palm trees (islands, oases, coast) and cacti-like plants, plus the existing dead trees; the existing broadleaf trees, conifers and bushes on the green land.
- **Habitations:** futuristic desert homes (flat-roofed, thick-walled blocks with neon trims, solar panels or wind catchers on the roof) and desert outposts (water tanks, antennas, solar farms). They are placed along roads like the other buildings (P04-R07). World 1 has no industrial zone and no city centre: those are for other worlds (reviewer, 2026-10-27).
- **Farms** (added at the reviewer's request, 2026-10-26): a futuristic farmhouse, a greenhouse and grain silos, with the existing wind turbines, for the green land of 1-2 and 1-3.

The new props are as light in polygons as the existing ones (D-031) and keep the matte look of the props (D-024).

**Acceptance criteria**
- [ ] Manual visual validation: grass, sand, dunes, farms and desert props read clearly from the playfield camera, and the desert does not look like the Level Zero wasteland with another colour.

### P06-R07 — Enemy waves by distance  · MUST

Each level has a wave script in `src/game/`: a list of waves, each one triggered by how far the level has scrolled (GD-40). A wave gives the enemy kind, how many there are, where they come in (side, x position) and the delay between them. Many waves can be on screen at the same time. The engine runs wave scripts without knowing the enemy kinds (`01-engineering.md` §2.3).

The kinds are introduced over the world, so each level teaches something new:

| Level | Enemy kinds |
|-------|-------------|
| 1-1 | Gnat, Hornet, Scout, Strafer |
| 1-2 | the 1-1 kinds plus Weaver, Splitter |
| 1-3 | the 1-2 kinds plus Carrier, Spinner |
| 1-4 | the 1-3 kinds plus Lancer, Rocketeer |
| 1-5 | every kind, Bulwark included |

**Acceptance criteria**
- [ ] Given a wave triggered at a given distance, when the level scrolls past that distance, then its enemies spawn, and not before (unit test in `core/`).
- [ ] Given the 1-1 wave script, then it only uses Gnat, Hornet, Scout and Strafer (unit test); the same for each level's list above.
- [ ] Given the same level played twice, then the waves come at the same distances (the script is deterministic).

### P06-R08 — Increasing difficulty  · MUST

Each level is harder than the one before it. From 1-1 to 1-5, these go up strictly, level after level:
- the number of enemies spawned in the level;
- the total HP of the enemies spawned in the level;
- the highest number of enemies on screen at the same time.

These go up or stay the same (one or more must go up from level to level): the enemy bullet speed and the enemy fire rate, as per-level factors on the phase 5 values.

Within a level, the waves also get harder from the start to the end: the second half of a level has more enemy HP than the first half.

**Acceptance criteria**
- [ ] Unit test: for the 5 wave scripts, enemy count, total enemy HP and peak enemies on screen go up strictly from 1-1 to 1-5.
- [ ] Unit test: the bullet speed and fire rate factors never go down from 1-1 to 1-5.
- [ ] Unit test: in each level, the second half has more total enemy HP than the first half.
- [ ] Manual validation: 1-1 feels easy, even for a kid (vision), and 1-5 feels clearly harder.

### P06-R09 — Debug shortcuts for the levels  · MUST

So the 4-minute levels can be checked by hand, the `game` screen takes debug options from the URL (for example `?level=1-3&t=120`): start any World 1 level straight away (with the balanced ship unless `ship=` is given), start at a given time, and use the Level Zero playback keys (F ×4 fast forward, ← / → jump 10 s). Without these URL options, the game ignores those keys. The FPS / polygons debug tile is shown when debug is on.

**Acceptance criteria**
- [ ] Given the URL `?level=1-3&t=120`, then level 1-3 starts at 2:00, with the waves that come before 2:00 skipped.
- [ ] Given no debug option, then F, ← and → do not change the level's time.

### P06-R10 — Time of day per level  · MUST

> Added at the reviewer's request (2026-10-26).

Each level has its own time of day, which sets the sun's height, direction and colour, the sky and the ambient light. 1-1 is at midday; the next levels come later and later in the day: early afternoon (1-2), late afternoon (1-3), sunset (1-4) and dusk with the town lights on (1-5) (`time_of_day`). The time does not change within a level.

**Acceptance criteria**
- [ ] Unit test: the sun is highest in 1-1 (midday) and lower in each level after it.
- [ ] Manual visual validation: the light and the shadows change from level to level, and the ships stay easy to see at sunset and dusk.

## 🧑 Tunable values
| Name | Value | Notes |
|------|-------|-------|
| level_duration | 240 s ± 10 s | P06-R04 |
| ground_speed 1-1 / 1-2 / 1-3 / 1-4 / 1-5 | 70 / 65 / 60 / 60 / 60 px/s | GD-01; faster over the sea |
| level_end_wait | 10 s at most | P06-R03 |
| enemies_spawned 1-1 / 1-2 / 1-3 / 1-4 / 1-5 | ~60 / ~80 / ~100 / ~120 / ~140 | P06-R08; the agent may adjust while balancing, keeping the order |
| peak_on_screen 1-1 / 1-2 / 1-3 / 1-4 / 1-5 | 6 / 8 / 10 / 12 / 15 | P06-R08 |
| enemy_bullet_speed_factor 1-1 / 1-2 / 1-3 / 1-4 / 1-5 | 0.8 / 0.85 / 0.9 / 1.0 / 1.1 | P06-R08 |
| enemy_fire_rate_factor 1-1 / 1-2 / 1-3 / 1-4 / 1-5 | 0.8 / 0.85 / 0.9 / 1.0 / 1.1 | P06-R08 |
| start_weapon | guns, level 1 | P06-R02; weapon bonuses raise it in the level (reviewer, D-049) |
| sea_share 1-1 / 1-2 / 1-3 / 1-4 / 1-5 | ≥ 80 % / ≤ 50 % / 0 % / 0 % / 0 % | P06-R05 |
| time_of_day 1-1 / 1-2 / 1-3 / 1-4 / 1-5 | midday / early afternoon / late afternoon / sunset / dusk | P06-R10 (reviewer, 2026-10-26) |

## 🧑 Out of scope for this phase
- (Moved into this phase by the reviewer, D-050: damage to the player, health bar, lives, invincibility and game over, GD-20..GD-22.)
- Bombs (GD-32) and the other bonuses (extra lives, GD-20). Weapon bonuses (GD-31) were moved into this phase by the reviewer (review feedback, D-049).
- Score display, points and high score (GD-50, GD-51). The overlay only counts enemies.
- Mini bosses, final bosses and checkpoints (GD-41, GD-42, GD-46).
- Pause (GD flow §7), music and sound effects (GD-70, GD-71).
- Worlds 2 to 5.
- New enemy kinds.

## 🧑 Engineering additions for this phase
- The wave runner (distance triggers, spawn queue) and level end logic are pure `core/` code and unit tested; the five levels (terrain sections, props, wave scripts, tunables) are data in `src/game/`.
- An e2e test confirms each World 1 level from the menu and checks that it starts without console errors.
- An e2e test opens `?level=1-1&t=235` (or similar) and reaches the "Level complete" overlay.
- 60 FPS (ENG-101) with the busiest moment of 1-5 (the most enemies on screen over the great oasis town).

## 🧑 Manual validation checklist
- [ ] Runs on GitHub Pages / `make dev` without console errors
- [ ] `1-1` to `1-5` can be picked in the level select; the other worlds stay locked
- [ ] Each level lasts about 4 minutes and ends with the "Level complete" overlay
- [ ] 1-1 is mostly sea; green grass in 1-2 and 1-3, then the desert in 1-4 and 1-5, with more and more props; each level begins where the previous one ended
- [ ] Each level has its own time of day, from midday in 1-1 to dusk in 1-5
- [ ] Desert sand, dunes and props look good from the playfield camera
- [ ] New enemy kinds appear level after level, and the difficulty clearly goes up
- [ ] 60 fps in the busiest part of 1-5

## 🧑 Notes, references, sketches
- **Differences from earlier specs, settled by the reviewer (2026-10-24):**
  - World 1 has 5 levels, matching the 5 × 5 grid of `00-vision.md` and P01-R07 (P06-R01).
  - The World 1 levels last about 4 minutes (P06-R04); `00-vision.md` is updated to match.
  - GD-41 asks for a mini boss and a final boss in each level; they are out of scope here, so World 1 levels end without a boss until the boss phase. This is accepted.
- Suggested look for a boss phase later: leave a calm stretch around the middle of each level (mini boss / checkpoint, GD-42) and at its end (final boss).
- Level Zero (`level_zero/`) and its tools stay as they are; the World 1 levels are new level definitions next to it.

---

## 🧑 Review feedback
> After the agent reports, write corrections here, then say **"Fix phase 06"**.
> The agent ticks each item when fixed.

- [x] (reviewer, in chat, 2026-10-27) Make 1-5 end on the desert; the factory and the city are for other worlds. — Done (D-109 amended): 1-5 "Deep desert": desert outskirts, great dunes, oasis villages, a rocky pass, desert towns, a great oasis town on the sand. 1-4 ends on the desert outskirts instead of the mining outskirts, and its mesas lose their mines. No industrial, heavy-industry or city group in World 1 (unit test). Props per level 406 / 4 829 / 5 898 / 6 042 / 9 486, each second half fuller than the first.
- [x] (reviewer, in chat, 2026-10-26) Rework World 1: start on the sea, then green grass, then desert, with more and more props along the way; the 5 levels are cut in this single gradient. Level 1 at midday, the other levels at other times of day. — Done (D-109): P06-R05 and P06-R06 amended, P06-R10 added. 1-1 open sea with green islands, a green coast at the end; 1-2 green coast, meadows, groves, farmland; 1-3 green country (woods, hills, a market town), the grass yellowing at the end; 1-4 dry lands (scrub, sand and rock, dunes, an oasis town, a canyon, mesas and mines, a desert town); 1-5 desert city. New farm props (farmhouse, greenhouse, grain silos, with World 2's wind turbines). Props per level 406 / 4 829 / 5 898 / 5 959 / 8 756, buildings 43 / 1 475 / 2 797 / 3 889 / 7 974, each second half fuller than the first. Sun at 72° (midday), 55°, 35°, 14° (sunset) and 8° (dusk, city lights on).
- [x] (reviewer, in chat, 2026-10-25) The e2e tests fail on the pipeline (shard 1/3: level_zero/ tests timed out at 30 s). — Fixed: not a slowdown of the page (Level Zero's roads and props build as fast as on main, and on main the same tests take the same 21–28 s on 4 cores, against the 30 s default); shard 1 runs the three heaviest pages (level_zero/, enemies/, the menu flows) side by side under software WebGL, and a slower runner tips them over. The level_zero/ spec now has 90 s per test like the other heavy specs, and the "every enemy kind" test 150 s (it takes about 70 s against its 90 s). With 4 cores and 2 workers, as on CI, the three shards pass: 17, 17 and 16 tests.
- [x] (reviewer, in chat, 2026-10-25) The unit tests fail. — Fixed (9 failures): two real bugs, (1) without crossings, removing dead ends could go round for ever (a street went on, was cut back because it would make a crossing, then the street behind it went on again…) and stopped after 500 passes with dead ends left; a street cut back is no longer built again (`street-grid.ts`), and (2) a path could start where a main road piece comes in from the side and run on top of it before crossing it; without crossings paths start only where their main road runs along the level (`road-paths.ts`) (D-052); also the gamepad's `fire` flag leaked into the `move` direction (`game-controls.ts`). The other tests were out of date with the review changes: the Level Zero props test now leaves out the World 1 models (P06-R06), the World 1 wave script test includes the fillers (D-051), the game-play completion and HUD tests use a hull that takes no damage (the sample enemies now hit the still ship, D-050), the weapon-level test switches weapon once per step instead of an even number of times, and the app overlay test waits past the 1 s input delay (ten 0.1 s ticks left 1e-16 s of it).
- [x] (reviewer, in chat, 2026-10-24) Remove the CRT overlay (scanlines drew lines over the levels). — Done: `#stage::after` removed (D-040).
- [x] (reviewer, in chat, 2026-10-24) Avoid roads crossing each other (only a path joining a road is allowed); add a few props not connected to roads; allow places where a bunch of buildings stand close together, spawned from time to time. — Done for World 1 (D-046): main roads never cross (the second follows the first at a distance), paths start on a main road and end off screen or on another main road or street, the street grids have T-junctions only; a few lone buildings and hamlets of 5–9 buildings stand away from the roads (`noCrossings`, `loners`, `hamlets` rules; `road-network.test.ts`, `prop-placement.test.ts`). Crossings on screen went from up to 266 per level to 0. Level Zero (phase 4) keeps its roads.
- [x] (reviewer, in chat, 2026-10-24) Make the player ship roll when moving left / right, and add a little more acceleration to its movements. — Done: the ship banks up to 35° with its sideways speed, easing in and out; full speed is reached in 0.18 s instead of 0.08 s (D-045).
- [x] (reviewer, in chat, 2026-10-24) Add more enemy waves, the levels feel empty. — Done: light filler groups come in the lulls between the written waves, every 4.5 s at the start of 1-1 down to every 1.6 s at the end of 1-5 (1-1: Hornets and Gnats only, which do not shoot). With a player shooting all the time, the screen is empty 30 % (1-1) to 6 % (1-5) of the time instead of 54 % to 14 %, with about twice as many enemies; counts, HP and peaks still go up from 1-1 to 1-5 (D-051, `world-1.test.ts`).
- [x] (reviewer, in chat, 2026-10-24) Implement player damage for bullet hits and ship collisions. Scope (asked): full GD-20/21/22; all enemy shots and ramming; "Game over" panel, then level select. — Done: a 5 px hitbox (GD-21); bullets take 10, missiles 20, a laser beam 25 (once per beam), ramming 30 (the rammed enemy takes 40); 2 s of invincibility after a hit, the ship blinking (GD-22); 3 lives, each a full health bar; out of lives the ship blows up and a red "Game over" panel shows after 2 s, Confirm goes back to level select on the same level. The HUD shows the real health (red when low) and the lives (D-050; `player-hull.test.ts`, `player-hits.test.ts`, `level-run.test.ts`, `game-play.test.ts`, `game-hud.test.ts`, `menu-flow.test.ts`, `menu-view-builder.test.ts`, `menu-overlay.test.ts`).
- [x] (reviewer, in chat, 2026-10-24) Create bonuses dropped by some exploded enemies: weapons level up. Scope (asked): in phase 6, bombs and extra lives still out; each weapon keeps its own level; drop chance by toughness. — Done: a destroyed enemy drops a weapon bonus with a chance growing with its health (6 % for the small ones to 20 % for a Bulwark or Carrier); it falls down the screen (within the ship's reach) and flying over it raises the weapon in use by a level, up to 5; E switches weapons, each keeping its level. The bonus is a yellow hexagon badge with cyan chevrons, swinging over a pulsing halo, with a ring flash on pickup; the HUD shows the new level (D-049; `bonus-world.test.ts`, `level-run.test.ts`, `game-play.test.ts`, `bonus-renderer.test.ts`).
- [x] (reviewer, in chat, 2026-10-24) Enemies spawning from the top must stay in the horizontal range of the bottom of the screen: with the camera angle, the player cannot shoot at ships too far in the upper corners. — Done: the kinds coming in from the top, and the Gnat and Splitter paths, keep to the ship's reach at the bottom of the screen (x 107–373 of 480) (D-048, `enemy-kinds.test.ts`, `level-run.test.ts`).
- [x] (reviewer, in chat, 2026-10-24) Increase the ships' base speed by 50 % again. — Done: base speed 225 px/s (balanced 225, heavy 180, light 315); acceleration time unchanged (0.18 s to full speed), so the ships also pick up speed faster (D-047).
- [x] (reviewer, in chat, 2026-10-24) Increase the player base speed by 50 %, and increase the enemy density. — Done: base speed 150 px/s (balanced 150, heavy 120, light 210); every wave brings 50 % more groups (D-044). `phase-02-player-ships.md` still says 100 px/s: to be updated by the reviewer.
- [x] (reviewer, in chat, 2026-10-24) Add a button to switch between weapons: the E key (AZERTY). — Done: E (by key position, so the same key on AZERTY and QWERTY) cycles bullet → laser → missile, each at level 1, once per press; the HUD shows the weapon (D-043).
- [x] (reviewer, in chat, 2026-10-24) Sometimes the light of an explosion appears at the wrong place. — Fixed: enemies could be shot (and blew up) before coming into view, just above the top edge or beside the narrower bottom of the view; only enemies on screen can be hit now (D-042, `level-run.test.ts`).
- [x] (reviewer, in chat, 2026-10-24) Still a misplaced white halo when an enemy explodes (screenshots: a soft glow away from the blast, for one frame). — Fixed: the explosion layers set their new instance count after uploading the positions, and Babylon uploads only `thinInstanceCount` of them, so in the frame a blast began its new particles were drawn, in their new colours, where older particles had been. The count is now set first (`blast-renderer.ts`, `enemy-renderers.test.ts`). Reproduced before the fix with frame-by-frame captures around kills; D-042 stays (it fixed blasts out of view).
- [x] (reviewer, in chat, 2026-10-24) Remove the Back button from the in-game view, and add a basic HUD: health, weapon level, etc. — Done: no Back button in game (Esc / gamepad B still go back to the title, P06-R02); `ui/game-hud.ts` shows the ship and its health bar, the weapon and its level, the level's progress and the enemies destroyed (D-041).

---

## 🤖 Implementation report
> Filled by the agent. Do not edit (comment in Review feedback instead).

### Questions / blockers
<!-- Ambiguities found before implementing. If non-empty, agent stops and waits. -->
- Settled by the reviewer on 2026-10-24 before implementation: World 1 has 5 levels (not 4), each about 4 minutes; levels end without bosses for now. The spec was updated accordingly (status `Ready`).

### Plan
| Task | Requirement IDs |
|------|-----------------|
| Level catalog: every World 1 level unlocked, from `src/game/` data | P06-R01 |
| `GameLevel` contract, pure `LevelRun` (scroll, waves, enemies, shots, ship), `PlayerFlight` | P06-R02, R03, R07 |
| Game screen: `GamePlay` over a shared `LevelScene`, `GameSession`, controls (keys, gamepad, touch), overlay | P06-R02 |
| Level end: stop spawning, wait for the last enemies (≤ 10 s), "Level complete" overlay, Confirm → next level | P06-R03 |
| Five scenery levels of 240 s at 70/65/60/60/60 px/s | P06-R04, R05 |
| Sand cover, dunes, desert looks, 9 new props (homes, outposts, plants, huts, mine) | P06-R06 |
| Distance-triggered `WaveRunner`, wave entries, five wave scripts | P06-R07 |
| Difficulty factors (bullet speed, fire rate), balance measured by a play-through | P06-R08 |
| URL debug options, playback keys, FPS / polygons tile | P06-R09 |
| Unit tests with requirement IDs, e2e for every level, the level end and the debug options | all |

### Requirement traceability
| ID | Status (Done / Partial / Not done) | Code | Tests | Notes |
|----|-----------------------------------|------|-------|-------|
| P06-R01 | Done | `src/game/sim/levels.ts`, `src/game/config/levels.ts`, `src/game/sim/world-1.ts` | `levels.test.ts`, `world-1.test.ts`, `menu-flow.test.ts`, e2e `world-1.spec.ts`, `menu-pointer.spec.ts` | 5 × 5 grid; 1-1 … 1-5 unlocked, never locked by progress; worlds 2–5 locked |
| P06-R02 | Done | `src/core/systems/level-run.ts`, `player-flight.ts`, `src/app/game-play.ts`, `game-session.ts`, `level-scene.ts`, `src/input/game-controls.ts`, `src/ui/screens/game-screen.ts`, `src/app/start-app.ts` | `level-run.test.ts`, `player-flight.test.ts`, `game-controls.test.ts`, `game-play.test.ts`, `start-app.test.ts`, `menu-overlay.test.ts`, e2e `world-1.spec.ts`, `smoke.spec.ts` | Replaces the P01-R08 placeholder; guns level 1 at every start; Back (Esc) → title |
| P06-R03 | Done | `LevelRun` phases, `MenuFlow.completeLevel`, `menu-view-builder.ts`, `game-screen.ts` | `level-run.test.ts`, `menu-flow.test.ts`, `menu-view-builder.test.ts`, `start-app.test.ts`, e2e `world-1.spec.ts` (`?level=1-1&t=237`) | Overlay ignores input for 1 s; next level highlighted (1-5 again after 1-5) |
| P06-R04 | Done | `src/game/config/world-1/scenery-*.ts` | `world-1.test.ts` | Every level is exactly 240 s |
| P06-R05 | Done | `scenery-coast.ts`, `scenery-country.ts`, `scenery-desert.ts`, `looks.ts` | `world-1.test.ts` (sea share, ground cover, props and buildings, halves, continuity) | Reworked in review (D-109): sea → grass → desert. Props 406 / 4 829 / 5 898 / 5 959 / 8 756; buildings 43 / 1 475 / 2 797 / 3 889 / 7 974 (seed of each level). Manual check needed |
| P06-R06 | Done | `height-field.ts` (dunes), `terrain-geometry.ts`, `terrain-blend-plugin.visual.ts` (sand), `desert-props.ts`, `desert-plants.ts`, `farm-props.ts`, `world-1/props.ts` | `height-field.test.ts`, `terrain-geometry.test.ts`, `prop-models.test.ts`, `world-1.test.ts` | Manual visual check needed (D-037) |
| P06-R07 | Done | `src/core/systems/wave-runner.ts`, `EnemySpawnArea.entry`, `enemy-kinds.ts`, `world-1/waves.ts` | `wave-runner.test.ts`, `level-run.test.ts`, `enemy-kinds.test.ts`, `world-1.test.ts` | Kinds: 1-1 Gnat/Hornet/Scout/Strafer; +Weaver/Splitter; +Carrier/Spinner; +Lancer/Rocketeer; +Bulwark |
| P06-R08 | Done | `world-1/difficulty.ts`, `EnemyWorld` difficulty, `ctx.fireRate` in the enemies | `enemy-world.test.ts`, `world-1.test.ts` | See D-038 for the numbers; manual "feel" check needed |
| P06-R09 | Done | `src/app/debug-options.ts`, `GamePlay.debugKey`, `game-session.ts`, `main.ts` | `debug-options.test.ts`, `game-play.test.ts`, `start-app.test.ts`, `menu-flow.test.ts`, e2e `world-1.spec.ts` | Works in every build (D-039) |
| P06-R10 | Done | `src/game/config/world-1/looks.ts` | `world-1.test.ts` (sun lower level after level) | Added in review (D-109): midday 72°, early afternoon 55°, late afternoon 35°, sunset 14°, dusk 8°. Manual check needed |

### Gate results
```
Light verification (2026-10-24): make typecheck ✔ / make build ✔ (ENG-52 leak check ✔) / make e2e ✔ 50 passed
After the in-chat review items (CRT overlay, HUD, no Back button, explosions out of view):
make typecheck ✔ / make build ✔ / make e2e ✔ 50 passed (the gamepad menu flow now enters a level:
its timeout is 90 s, it ran 29–36 s against the 30 s default)
After E weapon switch, speed / density +50 %, ship roll and slower acceleration:
make typecheck ✔ / make build ✔ / make e2e ✔ 50 passed (the enemies/ page test also got a
90 s timeout: it ran 29–35 s)
After the stray explosion glow fix: make typecheck ✔ / make build ✔ / make e2e ✔ 50 passed
After no road crossings, lone buildings and hamlets: make typecheck ✔ / make build ✔ / make e2e ✔
50 passed (1-4 and 1-5 load as fast as before, about 13 s per test)
After the base speed raised to 225 px/s: make typecheck ✔ / make build ✔ / make e2e ✔ 50 passed
After enemies from the top kept within the ship's reach: make typecheck ✔ / make build ✔ / make e2e ✔ 50 passed
After weapon bonuses: make typecheck ✔ / make build ✔ / make e2e ✔ 50 passed
After player damage, lives and game over: make typecheck ✔ / make build ✔ / make e2e ✔ 50 passed
After the filler waves: make typecheck ✔ / make build ✔ / make e2e ✔ 50 passed
After the unit test fixes: vitest 789 passed (run on request) / make typecheck ✔ / make build ✔ /
make e2e ✔ 50 passed
After the CI e2e timeouts: the 3 shards as on CI (4 cores, 2 workers, CI=1) ✔ 17 + 17 + 16 passed
Lint, unit tests and coverage are deferred to /validate-phase (make check).
```

**Final gate (`/validate-phase 6`, 2026-10-25, on `main` after the squash merge #16): `make check` green at the first run.**
```
make lint       ✔ (ESLint, 0 warnings; Prettier)
make typecheck  ✔
make coverage   ✔ 789 tests in 114 files; 99.33 % lines, 89.5 % branches, 98.3 % functions, 98.34 % statements (thresholds met)
make build      ✔
make e2e        ✔ 50 passed
```

### How to test manually
- `make dev`, open http://localhost:5173/ → Start → pick a ship → the World 1 row shows `1-1` … `1-5`, all unlocked; worlds 2–5 are padlocked.
- In a level: arrows / WASD (or left stick / D-pad) to fly, Space (or gamepad A / right trigger) to shoot; on a touch screen, drag anywhere to fly and hold the yellow Fire button. Esc (or gamepad B) returns to the title.
- Weapons: E switches to the next weapon (bullet → laser → missile → bullet), each keeping its own level (level 1 at first); the HUD's top right shows it.
- Damage: let enemy bullets hit the ship: the HP bar drops and the ship blinks for 2 s (no damage meanwhile); ram an enemy: −30 HP, and small enemies blow up. At 0 HP a life goes (`♥ 2`), the ship blows up and comes back full. Out of lives: the ship blows up, and after 2 s a red "Game over" panel shows; Enter goes back to level select on the same level. Staying still in the middle of `?level=1-1` gets there in about 80 s.
- Weapon bonuses: some destroyed enemies drop a swinging yellow hexagon badge with cyan chevrons; fly over it and the weapon in use goes up a level (HUD `Lv 2/5`…, a cyan ring flashes). `?level=1-5&t=30` and shooting gets the first ones within about a minute.
- HUD: top left the ship, its lives (`♥ 3`) and health bar (red under 30 %), top right the weapon and its level (`Bullet · Lv 1/5`), under the level label a bar of the level's progress, bottom left the enemies destroyed.
- Debug URL options: `?level=1-3` starts 1-3 straight away with the balanced ship, `&t=120` starts at 2:00 (waves before it skipped), `&ship=heavy` (or `light`) picks the ship. With them, F toggles ×4 fast forward, ← / → jump 10 s back / on (A / D still steer), and the FPS / polygons tile shows top right. Without them, F, ← and → do nothing to the time.
- Level end: `?level=1-1&t=235` → after the scroll ends and the last enemies leave (≤ 10 s), "Level complete!" shows `1-1` and "Enemies destroyed: N / M"; Enter / Space / tap → level select on `1-2`.
- Scenery: `?level=1-1&t=0`, `1-1&t=210` (first coast), `1-2&t=0` (coast), `1-2&t=200` (sand and rock), `1-3&t=30` (dunes), `1-3&t=145` (canyon), `1-4&t=200` (desert town), `1-5&t=200` (great oasis town). Each level begins on the ground the previous one ended on.
- 60 FPS check: `?level=1-5&t=225` (most enemies on screen over the great oasis town), FPS on the debug tile.

### Deviations from spec
- Enemy counts and peaks are above the tunables: after the reviewer's +50 % density (D-044) and the filled lulls (D-051), 279 / 335 / 433 / 498 / 537 enemies (tunables ~60 … ~140; Carriers' Gnats included) and peaks 16 / 20 / 24 / 30 / 32 on screen (tunables 6 … 15); they still go up strictly from 1-1 to 1-5 (P06-R08).
- Player base speed is 225 px/s (two reviewer's requests, D-044 then D-047), not the 100 px/s of P02.
- Lone huts and masts on the 1-1 islands are scattered like plants (no road reaches an island, and buildings only stand along roads, P04-R07).
- The debug URL options work in production builds too, and in debug mode ← / → are the playback keys rather than steering (D-039).
- At the reviewer's request during implementation, the CRT scanline / vignette overlay of the stage is removed: it drew lines across the levels (D-040).
- At the reviewer's request, the game screen has no on-screen Back button (Esc / Backspace / gamepad B still go back, as P06-R02 asks), and shows a HUD (D-041). On a touch screen without a keyboard, a level can then only be left at its end, until pause comes.

### Known limitations
- Lives and health start again full in every level; there is no checkpoint (mini bosses, GD-42, are out of scope).
- No score, bosses, bombs, extra lives, pause, music or sound (out of scope). Weapon bonuses only raise the weapon level within a level: every level starts again at level 1.
- Starting a level builds its scenery synchronously: a short freeze after Confirm (longer for 1-5's city).
- 60 FPS in the busiest part of 1-5 (city centre, about 0.8 M triangles drawn) is not verified on real hardware here: the e2e browser renders in software (about 10–15 FPS there for every level).

### Suggestions for future phases
- Leave the calm stretch around 1:45–2:10 of each level for the mini boss / checkpoint (GD-41, GD-42), and the last ~15 s for the final boss.
- A small loading screen while a level's scenery is generated.
- Quality presets (ENG-102) could thin the city centre for weaker GPUs.
