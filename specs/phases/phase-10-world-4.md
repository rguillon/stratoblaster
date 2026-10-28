# Phase 10 — World 4

> Fill the **Human** sections. Set **Status** to `Ready` when the agent may implement it.
> The agent fills the **Agent** sections and never edits the requirement sections.

**Status:** Ready  <!-- Draft | Ready -->
**Depends on:** Phase 9

---

## 🧑 Goal
World 4, **the Metropolis** (first the Volcanic Lands; reworked at the reviewer's request, 2026-10-27), has five playable levels, 4-1 to 4-5, each about 5 minutes long. The levels are one journey from the garden villages of small houses World 3 ended on, through a town, mid-rise blocks and offices, to the towers of a business district and a downtown of skyscrapers, with slow transitions along the levels. No sea and no lava: a river runs through the town and the city. Each level has its own time of day, cloud cover and weather (a red dawn, an ash-dark noon, embers rising at dusk, a furnace-lit night). Each level has its own mini boss and final boss, ten new bosses in all. The levels get harder from 4-1 to 4-5, and World 4 as a whole is harder than World 3.

## 🧑 Requirements

> ID format `P10-Rxx`. Every requirement is **MUST** (no SHOULD / MAY).
> Write each requirement so it is testable. Add acceptance criteria when "done" isn't obvious.
> World 4 is built exactly like Worlds 2 and 3 (phases 8 and 9): the World 1 tools and rules (phases 4 to 7 and their review decisions), the level look (P08-R04) and the weather engine (P08-R05, P09-R05). Only what changes for World 4 is written here. Sizes are given relative to the medium player ship length (`L`). Numbers are listed in **Tunable values**.
> Lava (P10-R05) and the new weather kinds (P10-R06) are game-agnostic engine features; the World 4 levels, looks and bosses are data and models in `src/game/` (`01-engineering.md` §2.3).

### P10-R01 — World 4 in the level select  · MUST

The World 4 row of the level select grid shows `4-1` to `4-5`, all unlocked (P06-R01). World 4 is the last row of the grid (World 5 dropped by the reviewer, 2026-10-26). After `3-5` is completed, `level-select` shows with `4-1` highlighted; after `4-5`, with `4-5` highlighted.

**Acceptance criteria**
- [ ] Given `level-select`, then the World 4 row shows exactly `4-1` to `4-5`, all unlocked, each starting its level.
- [ ] Given `3-5` is completed, then `level-select` shows with `4-1` highlighted.
- [ ] Given `level-select`, then the grid has exactly 4 rows (`1-1` … `4-5`) and no level is locked.

### P10-R02 — Duration  · MUST

Each World 4 level's scroll time at its ground speed is 300 s ± 10 s (as P08-R02).

**Acceptance criteria**
- [ ] Unit test: for each World 4 level, length ÷ ground speed is between 290 s and 310 s.

### P10-R03 — Scenery progression across World 4  · MUST

**Reworked at the reviewer's request (2026-10-27):** World 4 starts with houses (where World 3 ends) and ends with skyscrapers. The table below replaces the volcanic one (black sands, ash plains, lava fields, forge belt, caldera); the slow transitions are World 2's and World 3's (P08-R03, P09-R03).

The player flies from the garden villages 3-5 ended on into a growing city. Each level begins on the very ground the previous one ended on (4-1 on 3-5's), the sections blend over a long stretch, the grass gives way to concrete a little in each section, and each taller kind of building first comes in mixed with the one before it.

| Level | Name | Water | Ground | Buildings |
|-------|------|-------|--------|-----------|
| 4-1 | Garden town | World 3's river between grassy banks, then stone quays. | Mostly grass and gardens. | Garden villages, suburban lanes, suburbs, terraced streets, flats, then a town centre with the first mid-rise blocks. |
| 4-2 | Inner town | The river between quays, wider at a park. | Grass and concrete about even. | Town streets, the ring road, mid-rise flats, a city park, then mid-rise blocks among the first offices. |
| 4-3 | Midtown | The river quays. | Mostly concrete. | Offices among mid-rise blocks, office blocks, river quays, plazas, then the first city towers. No skyscraper. |
| 4-4 | Business district | The river quays. | Concrete, a park among the towers. | City towers, a tower park, the financial district with the first skyscrapers, high rise, then the first skyline. |
| 4-5 | Downtown | The river quays. | All concrete, a central park. | Skyscrapers, a central park, then skyscrapers filling every block; skyscrapers only at the end. |

**Acceptance criteria**
- [ ] Unit test: no World 4 level has a sea section or lava; every level has some river water.
- [ ] Unit test: the concrete cover goes up and the grass cover goes down from 4-1 to 4-5 (more grass than concrete in 4-1, more concrete in 4-3 to 4-5).
- [ ] Unit test: 4-1 starts on garden villages; no city tower or skyscraper in 4-1 and 4-2, no skyscraper in 4-3; skyscrapers only in the last section of 4-5.
- [ ] Unit test (fixed seed): the mean height of the buildings placed goes up from 3-5 through 4-1 to 4-5, and in each level the second half's is higher than the first's; the skyscrapers stand taller than every city tower.
- [ ] Unit test: each level begins on the ground (relief, cover, streets, buildings, river) the previous one ended on, 4-1 on 3-5's; the sections blend over the same long stretch as World 2's.
- [ ] Manual visual validation: garden town, inner town, midtown, business district and downtown can be told apart, the city grows slowly, and downtown reads as a skyline of skyscrapers.

### P10-R04 — Look of each World 4 level  · MUST

Each level's look (P08-R04):

| Level | Time of day | Clouds (low / high cover) | Weather | Notes |
|-------|-------------|---------------------------|---------|-------|
| 4-1 | dawn | 0.4 / 0.3, ash-tinted pink and grey | none | A red rising sun behind a smoke haze over the garden town. |
| 4-2 | midday, under an ash cloud | 0.9 / 0.9, brown-grey | falling ash 0.5 | A dim, flat, yellowish light, as if the sun were behind smoke; weak shadows. |
| 4-3 | dusk | 0.5 / 0.4, dark grey lit orange from below | embers 0.4 | The sunset fades while the city's glow takes over (look change over the level: the sun dims, the glow from below grows). |
| 4-4 | night | 0.6 / 0.5, smoke lit orange from below | falling ash 0.3, embers 0.3 | Lit by the towers' windows and neon; ground lights at their strongest. |
| 4-5 | night, eruption | 0.7 / 0.6, red-lit | embers 0.6, growing to 1.0 at the final boss | A volcano erupts beyond downtown during the level (look change: the sky haze turns deep red and the embers grow). |

Since the rework (reviewer, 2026-10-27) the times of day, clouds and weather are kept; the glow from below is the city's, not the lava's.

**Acceptance criteria**
- [ ] Unit test: each World 4 level's look data matches this table, look changes included.
- [ ] Manual visual validation of each level against the table; the player ship, enemies, shots and bonuses stay clearly visible in every level. Red and orange enemy shots must still stand out from the lava and the red sky (see P10-R07).

### P10-R05 — Lava  · MUST

**Since the reviewer's rework (2026-10-27)** no World 4 level has lava: the engine feature below stays, with its own tests, for later use.

A new kind of liquid ground, used for lava rivers, lava pools, slag rivers and the magma lake:
- it glows by itself (bright orange-yellow in its cracks, dark red crust plates on top), so it is visible at night and lights the haze above it;
- it flows slowly down the screen in rivers and churns slowly in pools and the lake, the crust plates drifting and breaking;
- it meets the rock with a bright, hot edge;
- it is only a look: flying over it does no damage.

The glow uses the existing glow tools (as the city lights, D-030); it does not light the ships with real lights (cost).

**Acceptance criteria**
- [ ] Manual visual validation: the lava reads as molten and moving from the playfield camera, by day and by night.
- [ ] Unit test: lava is not an input of the simulation (flying over it does nothing).
- [ ] 60 FPS (ENG-101) over the 4-5 magma lake.

### P10-R06 — Weather: falling ash and embers  · MUST

Two new weather kinds for the weather engine (P08-R05):
- **Falling ash:** grey flakes falling slowly and drifting, like a dull snow; the strength sets how many and how close and brown-grey the haze comes.
- **Embers:** small glowing orange sparks rising from the ground and drifting up past the camera, flickering as they cool. The embers are small and dim enough to never be mistaken for enemy bullets: they are smaller than any bullet, have no outline or glow ring, and move up the screen (never down at the player).
- Both are drawn behind the ships, shots and bonuses, and are only a look (P08-R05). Ash and embers can be used together.

**Acceptance criteria**
- [ ] Given a look with ash or embers of strength 0, then nothing is drawn; with strength 1, the most allowed by **Tunable values** are drawn.
- [ ] Unit test: weather is not an input of the simulation.
- [ ] Manual validation: embers are never confused with enemy bullets, even in the 4-5 eruption.
- [ ] 60 FPS (ENG-101) during the 4-5 eruption with the most enemies on screen.

### P10-R07 — Readable shots over fire  · MUST

World 4's ground and sky are red, orange and dark. So the player can always tell enemy shots apart, enemy bullets in World 4 keep the phase 5 colours but get a light, contrasting outline or core (e.g. a white core and a dark rim), so they stand out on the lava and the red sky as clearly as on the World 1 desert. The same applies to the boss shots and the laser warning lines.

**Acceptance criteria**
- [ ] Manual validation: in 4-3, 4-4 and 4-5, every enemy and boss bullet kind and the laser warning lines are easy to see over the lava, the furnaces and the red sky.
- [ ] Unit test: the shot look used in World 4 levels has the contrast outline or core on (data), and the other worlds are unchanged.

### P10-R08 — Volcanic ground and props  · MUST

**Reworked at the reviewer's request (2026-10-27):** the ground is World 3's (grass and gardens, damp earth, concrete that covers more and more of it, stone quays, river water flowing down the screen, asphalt roads). The buildings are World 3's houses, terraces and flats, Level Zero's city blocks and towers made of parts, and a new family of 8 skyscrapers made of parts (110 to 170 high at full scale, taller than every city tower, under 600 triangles each). The plants are World 3's. The volcanic ground and props below were built for the first World 4 and stay in the game, but no level uses them.

New generated ground and props for World 4 (GD-60, made in code), as light in polygons as the existing ones (D-031) and matte (D-024):
- **Ground:** black volcanic sand, black and dark grey basalt with cracks (glowing cracks near the lava), grey ash covering the ground in drifts, rust-red and sulphur-yellow mineral stains around the vents.
- **Sea:** a dark sea with **steam** rising where the coast is hot.
- **Vegetation:** hardy grass tufts on the islands, burnt dead trees and stumps on the ash plains, nothing in the lava fields.
- **Smoke:** vents and cinder cones send up slow smoke columns (soft, see-through, not hiding the shots).
- **Habitations:** geothermal wells and power plants, cooling towers, pipelines, ash-covered huts, mining outposts, lava pumps and heat collectors, giant foundries (smelters, blast furnaces with glowing mouths, chimney rows, cranes, rail lines with moving ore wagons, slag heaps), and the war factory (hangars, launch pads, armoured towers). They follow the road rules of World 1 (D-046); roads are dark, cracked and ash-dusted.

**Acceptance criteria**
- [ ] Manual visual validation: World 4 reads as volcanic and industrial, and does not look like World 1's desert or wasteland with another colour.
- [ ] Unit test: each new prop model stays under the triangle budget in **Tunable values**.

### P10-R09 — Enemy waves  · MUST

Each World 4 level has a wave script with fillers (P06-R07, D-051), using the eleven phase 5 kinds, all of them from 4-1 on:

| Level | Enemy kinds that lead the waves |
|-------|--------------------------------|
| 4-1 | every kind, with Weavers and Strafers low over the sea |
| 4-2 | every kind, with Splitters and Spinners over the plains |
| 4-3 | every kind, with Lancers and Rocketeers along the lava rivers |
| 4-4 | every kind, with Carriers and Bulwarks out of the foundries |
| 4-5 | every kind, the heaviest mixes of the game so far |

**Acceptance criteria**
- [ ] Unit test: each World 4 wave script uses all eleven kinds.
- [ ] Unit test: the waves are deterministic.

### P10-R10 — Increasing difficulty  · MUST

As in P08-R09:
- from 4-1 to 4-5, enemies per minute of scroll, total enemy HP per minute and the peak enemies on screen go up strictly; the bullet speed and fire rate factors never go down;
- in each level, the second half has more enemy HP than the first half;
- **across worlds:** 4-1 is at least as hard as 3-3, and 4-5 is harder than 3-5, on the same measures.

The game must stay beatable by a casual player (vision): 4-5 is the hardest level so far, but with weapons at level 4 or 5 a careful player gets through it. If the peak numbers in **Tunable values** cannot hold 60 FPS, the agent lowers them (keeping the order) and reports it.

**Acceptance criteria**
- [ ] Unit test: the strict increases from 4-1 to 4-5.
- [ ] Unit test: 4-1 ≥ 3-3 and 4-5 > 3-5.
- [ ] Unit test: in each World 4 level, the second half has more enemy HP than the first.
- [ ] Manual validation: 4-1 feels like a fresh start, 4-5 is the hardest level of the game so far and still beatable.

### P10-R11 — The ten World 4 bosses  · MUST

Each World 4 level has its own mini boss and final boss (P07-R05, P07-R06), code-generated in the World 4 theme (dark metal with neon, GD-61, plus soot, heat glow, molten seams and heavy industry). Stage patterns are designed by the agent and reported. Moving limbs use D-061.

| Level | Kind | Name | Look | Destroyable parts (weapons) | Fight ground speed |
|-------|------|------|------|-----------------------------|--------------------|
| 4-1 | Mini | Cinder Crab | A wide, low crab-ship (3 L) with two claws that open and close, orange neon | 2 claws (moving limbs; aimed spreads), shield the core; 1 back mortar (slow big bullets). Core: rings | ×0.5 |
| 4-1 | Final | Steam Dreadnought | A flying battleship (5 L) with two smokestacks puffing steam, red neon | 2 smokestacks (rings of bullets), 2 broadside turrets (aimed bursts), shield the core; 1 missile rack. Core: warning line + laser | ×0.6 |
| 4-2 | Mini | Ash Wraith | A ragged, grey stealth gunship (3 L) trailing ash, pale cyan neon | 2 shroud pods (fans), shield the core; 1 eye cannon (warning line + laser). Core: spirals | ×1.5 (chase over the plains) |
| 4-2 | Final | Geyser Rig | A flying drilling rig (5 L) with two drill heads and steam vents, yellow neon | 2 drill heads (moving limbs; aimed bursts), 2 steam vents (spirals), shield the core; 1 drone hangar (launches Hornets). Core: fans | ×0.4 |
| 4-3 | Mini | Magma Salamander | A segmented lizard-ship (3.5 L) with a molten glow between its plates, orange-yellow neon | 2 back fins (fans), shield the core; 1 tail (sweeping bullet lines). Core: aimed bursts | ×0.6 |
| 4-3 | Final | Obsidian Golem | A massive armoured flying fortress (5.5 L) with two huge fists, magma seams | 2 fists (moving limbs; slow big bullets in rings), 2 shoulder cannons (aimed spreads), 1 chest emitter (laser), 1 armour plate (no weapon); the fists and the plate shield the core | ×0.3 |
| 4-4 | Mini | Furnace Drake | A dragon-shaped gunship (3.5 L) with beating wings, red and orange neon | 2 wings (moving limbs; fans), shield the core; 1 jaw (a short flame of dense bullets, aimed). Core: spirals | ×0.5 |
| 4-4 | Final | Foundry Ark | A huge flying foundry (6 L) carrying glowing crucibles and a chimney row | 2 crucibles (burst into a ring of bullets when destroyed), 2 rail cannons (warning line + laser), 1 missile battery, 1 chimney row (no weapon); the cannons and the chimneys shield the core | ×0.3 |
| 4-5 | Mini | Ember Herald | A fast, spiky interceptor (3.5 L) wreathed in embers, gold neon | 3 ember lances on a turning ring (spirals), shield the core. Core: aimed bursts | ×1.4 (chase down the volcano's slope) |
| 4-5 | Final | Caldera Throne | The enemy's war fortress rising from the magma lake (6.5 L), crimson and gold neon over its whole hull | 2 magma cannons (lasers), 2 missile batteries, 2 heat shield generators (no weapon, shield the core). Core: every attack kind | ×0 (the ground stops over the magma lake) |

Mini bosses have 2 or 3 destroyable parts and final bosses 4 to 6 (P07-R01). Within World 4, at least one fight stops the ground (×0) and at least one is a chase (> ×1).

**Acceptance criteria**
- [ ] Unit test: each World 4 level has exactly one mini boss and one final boss from this table, with 2–3 and 4–6 destroyable parts.
- [ ] Unit test: in a long simulated fight, every boss's hit circles stay inside the ship's reach (D-048), moving limbs included.
- [ ] Manual visual validation of the ten models in `bosses/` (model and wireframe views), the moving claws, fists, wings and drills included.

### P10-R12 — Boss difficulty in World 4  · MUST

As in P08-R11: mini boss and final boss full HP go up strictly from 4-1 to 4-5; each final boss has more full HP than its level's mini boss; each World 4 boss has more full HP than the World 3 boss of the same level and kind; boss bullets use the level's factors; the fight times (simulation, balanced ship, guns at level 3, always firing at the boss) are within **Tunable values**.

**Acceptance criteria**
- [ ] Unit test: the HP orderings above.
- [ ] Unit test (simulation): fight times within the ranges.
- [ ] Manual validation: the Caldera Throne is the hardest boss of the game so far, and still beatable.

### P10-R13 — Debug options and the `bosses/` page  · MUST

- The debug URL options (P06-R09, P07-R09, P08-R12) accept every World 4 level, `weather=0` and `look=<time of day>` included.
- The `bosses/` page lists the World 4 bosses after the World 3 ones, each over the scenery and look of its level.

**Acceptance criteria**
- [ ] Given `?level=4-5&boss=final`, then 4-5 starts at its final boss's arrival, over the magma lake, in the eruption look.
- [ ] Given `?level=4-2&weather=0`, then 4-2 shows no falling ash.
- [ ] Given `bosses/`, then every boss of Worlds 1 to 4 can be picked without console errors.

## 🧑 Tunable values
| Name | Value | Notes |
|------|-------|-------|
| level_duration | 300 s ± 10 s | P10-R02 |
| ground_speed 4-1 / 4-2 / 4-3 / 4-4 / 4-5 | 70 / 65 / 60 / 55 / 55 px/s | GD-01 |
| sea_share | 0 % in every level | P10-R03 (reviewer, 2026-10-27; was ≥ 70 % in 4-1) |
| lava_share | 0 % in every level | P10-R03 (reviewer, 2026-10-27; was ~10 / 20 / 35 % in 4-3 … 4-5) |
| section_transition | 900 units, as World 2 | P10-R03 (reviewer, 2026-10-27) |
| skyscraper_height | 110–170 at full scale (55–110 drawn) | P10-R08 (reviewer, 2026-10-27) |
| peak_on_screen 4-1 / 4-2 / 4-3 / 4-4 / 4-5 | 15 / 16 / 17 / 19 / 21 | P10-R10; the agent may lower them for ENG-101, keeping the order |
| enemy_bullet_speed_factor 4-1 → 4-5 | 1.1 / 1.15 / 1.2 / 1.3 / 1.35 | P10-R10 |
| enemy_fire_rate_factor 4-1 → 4-5 | 1.1 / 1.15 / 1.2 / 1.3 / 1.35 | P10-R10 |
| ash_flakes_max | 1 500 (at strength 1) | P10-R06 |
| embers_max | 800 (at strength 1) | P10-R06; the agent may lower them for ENG-101 |
| ember_size | smaller than the smallest enemy bullet | P10-R06 |
| mini_fight_time 4-1 → 4-5 | 40–50 s → 55–65 s | P10-R12, balanced ship, guns level 3, always on target |
| final_fight_time 4-1 → 4-5 | 80–100 s → 120–150 s | P10-R12, same |
| boss_triangles | ≤ 6 000 per boss (Caldera Throne ≤ 7 000) | as in phase 7 |
| prop_triangles | within the range of the phase 6 props | P10-R08, D-031 |

## 🧑 Out of scope for this phase
- New regular enemy kinds.
- Gameplay effects of the lava, heat or weather (damage from lava, heat haze blurring the view): they are only a look.
- Real lights cast by the lava on the ships (only glow).
- Bombs, extra lives, score, high score, pause, music and sound effects.
- Changing the levels of Worlds 1 to 3 (P10-R07 only changes the shot look in World 4).

## 🧑 Engineering additions for this phase
- Lava, falling ash and embers are game-agnostic engine features, unit tested; the World 4 levels, looks, props, wave scripts and bosses are data and views in `src/game/`.
- The levels of Worlds 1 to 3 keep passing their tests unchanged.
- An e2e test confirms each World 4 level from the menu and checks it starts without console errors.
- An e2e test opens `?level=4-1&boss=final`, destroys the boss with K and the debug fire, and reaches the "Level complete" overlay.
- 60 FPS (ENG-101) in the 4-4 forge belt (densest industry, at night), and in the 4-5 final boss fight over the magma lake during the eruption.

## 🧑 Manual validation checklist
- [ ] Runs on GitHub Pages / `make dev` without console errors
- [ ] `4-1` to `4-5` can be picked in the level select; the grid ends with World 4
- [ ] Garden town, inner town, midtown, business district and downtown across the five levels, slow changes, from houses to skyscrapers; each level begins where the previous one ended, 4-1 where 3-5 ended
- [ ] A red dawn in 4-1, a dim ash-dark noon in 4-2, dusk giving way to lava glow in 4-3, a furnace-lit night in 4-4, the eruption in 4-5
- [ ] The river flows; downtown reads as a skyline
- [ ] Falling ash and embers look right, and embers are never mistaken for bullets
- [ ] Enemy and boss shots stay easy to see over lava and red skies
- [ ] The ten World 4 bosses look good in `bosses/`; claws, fists, wings and drills move
- [ ] Difficulty clearly goes up from 4-1 to 4-5; 4-5 is the hardest so far and still beatable
- [ ] 60 fps in the forge belt and the 4-5 final boss fight

## 🧑 Notes, references, sketches
- **Drafted by the agent at the reviewer's request (2026-10-25); open choices, defaults proposed:** the same as phase 8 (themes, no new enemy kinds, 5-minute levels, a softer start for each world, fight times with guns at level 3, boss designs as suggestions), plus:
  1. P10-R07 (contrast outline on shots) only in World 4. Alternative: on every world, which would change the look of the validated worlds.
  2. The difficulty numbers keep climbing; with no new enemy kinds, World 4 leans on denser mixes and faster bullets. The reviewer may prefer to cap the bullet factors around 1.3 for kids.
- World 4 is the last world: the Caldera Throne (4-5 final) is the game's last boss (World 5 dropped by the reviewer, 2026-10-26).

---

## 🧑 Review feedback
> After the agent reports, write corrections here, then say **"Fix phase 10"**.
> The agent ticks each item when fixed.

- [x] (reviewer, in chat, 2026-10-26) Remove World 5 from the specs and the code. — Done (D-089): the grid is 4 worlds × 5 levels (`LEVELS_CONFIG.worlds` 4), 20 levels, all unlocked; 4-5 is the last level, so it stays highlighted after it is completed. Specs updated with a dated note: vision, P01-R07 (20 entries `1-1` … `4-5`), P06-R01, phase 8 notes, P10-R01 (its World 5 criterion now checks the 4-row grid with no locked level), phase 10 out of scope and notes. Tests: `levels.test.ts`, `world-2/3/4.test.ts`, e2e `world-1/2/3/4.spec.ts`; the menu pointer e2e no longer tries a locked level (none is left in the game); the "locked" feedback stays unit tested with sample grids (`menu-overlay.test.ts`, `menu-controller.test.ts`).
- [x] (reviewer, in chat, 2026-10-26) Create 10 new, harder kinds of enemies, some with moving parts like the bosses; add them to the spec (in the phase 5 spec, the one describing the first enemies) and to the harder worlds. — Done (D-090): P05-R13 to P05-R24 added to `phase-05-first-enemies.md`.
  - Engine: `JointedEnemy` and `EnemyPart` (`core/entities/jointed-enemy.ts`), sweeping lasers (`EnemyLaserSpec.sweeps`); the `enemies/` wireframe draws the parts' hit circles.
  - Five veteran kinds: Wasp, Mortar, Mantis (moving arms), Phantom (cloaks), Minelayer.
  - Five elite kinds, four of them with moving parts: Hydra (three heads), Orbiter (orbiting drones), Scissor (two laser arms closing), Juggernaut (swinging cannons and shield plates), and the Hive (launches Wasps).
  - Waves: World 3 brings in one veteran kind a level. World 4 uses all five veteran kinds in every level and brings in the elites two in 4-1, then one more a level. P10-R09's "eleven kinds" now reads together with P05-R24.
  - Gaps and growth re-tuned in 3-3 to 3-5 and in all World 4 levels; every ordering of P09-R08 and P10-R10 still holds (numbers in D-090).
  - Tests:
    - New: `jointed-enemy.test.ts`, `veteran-enemies.test.ts`, `elite-enemies.test.ts`, `veteran-models.test.ts`, `elite-models.test.ts`, `enemy-close-up.test.ts`.
    - Updated: `enemy-kinds.test.ts`, `enemy-models.test.ts`, `enemy-shots.test.ts`, the World 1–4 kind tests, and the e2e `enemies.spec.ts` (21 kinds).
  - Manual check needed: the ten models in `enemies/` (model and wireframe views), and how hard 3-3 to 3-5 and World 4 feel.
- [x] (reviewer, in chat, 2026-10-27, after validation) Rework World 4: start with houses and end up with skyscrapers. → P10-R03, R04 (notes), R05 (note), R08 amended; D-112.

---

## 🤖 Implementation report
> Filled by the agent. Do not edit (comment in Review feedback instead).

### Questions / blockers
None. The spec was implemented as written; the interpretations are listed under Deviations.

### Plan
| Task | Requirement IDs |
|------|-----------------|
| Engine weather: a second weather at once, `ash` and `embers` kinds (added on, flickering, fading as they rise), cloud tint and glow from below in the look (`config/weather.ts`, `config/time-of-day.ts`, `core/scenery/sky-look.ts`, `atmosphere.ts`, `render/scenery/weather-layer.ts`, `weather-material.visual.ts`) | P10-R04, R06 |
| Engine lava: `SeaLook.lava`, a self-lit shader, the hot edge and cracks in the terrain plugin, the glow layer with the terrain as occluder (`lava-material.visual.ts`, `terrain-blend-plugin.visual.ts`, `scenery-kit*.ts`, `scenery-stage.ts`, `app/level-scene.ts`) | P10-R05 |
| Engine plumes (smoke, steam) from props and moving line pieces (`config/plumes.ts`, `plume-layer.ts`, `plume-material.visual.ts`, `prop-field.ts`, `PropLine.drift`) | P10-R08 |
| Shot style per level (`SceneryLook.shotStyle`, `EnemyBindings.shots(scene, style)`) and the game's contrast style | P10-R07 |
| World 4 levels, looks, ground textures (sub-agent) | P10-R02, R03, R04 |
| World 4 props and prop rules, 31 models (sub-agent) | P10-R08 |
| Waves and difficulty, measured and tuned | P10-R09, R10 |
| Ten bosses, designs + models, tuned with the D-055 bot (five sub-agents, one per level) | P10-R11, R12 |
| Registration, test API (second weather, lava, plumes, shot style), debug options and `bosses/` page follow from the data | P10-R01, R13 |
| Unit and e2e tests, docs, decisions | all |

### Requirement traceability
| ID | Status (Done / Partial / Not done) | Code | Tests | Notes |
|----|-----------------------------------|------|-------|-------|
| P10-R01 | Done | `game/sim/world-4.ts`, `game/sim/levels.ts` | `world-4.test.ts`, `levels.test.ts`, e2e `world-4.spec.ts`, `world-3.spec.ts` (after 3-5 → 4-1), `menu-pointer.spec.ts` | |
| P10-R02 | Done | `game/config/world-4/scenery-*.ts` (300 s each) | `world-4.test.ts`, e2e | speeds 70 / 65 / 60 / 55 / 55 |
| P10-R03 | Done (reworked 2026-10-27) | `world-4/scenery.ts` (replaces `scenery-islands.ts` and `scenery-fire.ts`), `world-4/city-props.ts` | `world-4.test.ts` | D-112, D-136, D-139; mean building height 6.1 / 16.3 / 27.6 / 45.0 / 81.4 (3-5: 5.5; 2026-10-28, with the boulevards and the narrower street grids) |
| P10-R04 | Done | `game/config/world-4/looks.ts`, `core/scenery/sky-look.ts` (cloud tint, underglow, second weather) | `world-4.test.ts`, `sky-look-volcanic.test.ts`, e2e | D-082, D-083; look: manual |
| P10-R05 | Done | `render/scenery/lava-material.visual.ts`, `terrain-blend-plugin.visual.ts`, `scenery-kit*.ts`, `scenery-stage.ts` (`lava`, `watchTerrain`), `app/level-scene.ts` | `volcanic-layers.test.ts`, `game-play-weather.test.ts` (not an input), `world-4.test.ts`, e2e | D-084; 60 FPS: manual |
| P10-R06 | Done | `config/weather.ts` (`ash`, `embers`), `weather-layer.ts`, `weather-material.visual.ts` | `sky-look-volcanic.test.ts`, `volcanic-layers.test.ts`, `game-play-weather.test.ts`, e2e | D-082 |
| P10-R07 | Done | `render/game-view.ts`, `app/enemy-viewer-shots.ts`, `game/config/enemy-look.ts` (`contrast`), `game/view/enemies/enemy-shot-renderer.ts`, `enemy-lasers.ts` | `contrast-shots.test.ts`, e2e | D-086; readability: manual |
| P10-R08 | Done (reworked 2026-10-27) | `game/view/props/skyscraper-props.ts` (new), `volcanic-*.ts` (kept, unused), `prop-models.ts`, `prop-look.ts`, `world-4/props.ts`, `world-4/city-props.ts`, `config/plumes.ts`, `plume-*.ts` | `world-4-skyscrapers.test.ts`, `prop-models.test.ts`, `volcanic-layers.test.ts` | D-085, D-112; 31 volcanic props ≤ 336 triangles; skyscrapers < 600 |
| P10-R09 | Done | `game/config/world-4/waves.ts` | `world-4.test.ts` | D-087 |
| P10-R10 | Done | `waves.ts`, `world-4/difficulty.ts` | `world-4.test.ts` | numbers below |
| P10-R11 | Done | `game/config/bosses/world-4/*`, `game/view/bosses/world-4/*`, `world-4/bosses.ts` | `bosses-world-4.test.ts`, `boss-models.test.ts`, `muzzles.test.ts`, e2e | patterns below |
| P10-R12 | Done | the ten designs' health | `bosses-world-4.test.ts` | fight times below |
| P10-R13 | Done | level data (debug options, `bosses/` page take every level), `app/game-play.ts` (test API) | e2e `world-4.spec.ts`, `bosses.spec.ts` | |

**Scenery (P10-R03).** 4-1: every section is sea (islands rising from relief under the water, the black-sand coast with a shore), 74.1 % of the ground under the water. 4-2: no sea, no liquid. 4-3 / 4-4 / 4-5: lava under the liquid level on 11.4 / 22.7 / 36.6 % of the ground (4-3 section by section 0, 1, 12, 14, 16, 23 %); no section with a shore or relief under the level. Buildings placed (seed of each level): 107 / 1 535 / 1 982 / 3 838 / 931.

**Balance (P10-R10)**, measured without shooting (seed 606), per minute of scroll: enemies 220.8 / 246.0 / 247.2 / 298.6 / 388.8, HP 7 004 / 8 178 / 9 472 / 9 668 / 12 544, peak on screen 53 / 54 / 57 / 64 / 66 for 4-1 … 4-5 (3-3: 215.0, 6 884, 47; 3-5: 308.4, 10 506, 58). Every second half carries more HP. Factors 1.1 / 1.15 / 1.2 / 1.3 / 1.35.

**Bosses (P10-R11, R12).** Fight times with the D-055 bot (guns level 3, always on target), mini / final: 4-1 44.4 / 89.2 s, 4-2 48.0 / 100.7 s, 4-3 53.2 / 112.4 s, 4-4 56.3 / 126.2 s, 4-5 59.7 / 137.6 s. Full health: mini 3 650 / 4 180 / 4 500 / 5 150 / 5 550, final 7 800 / 9 700 / 12 400 / 14 800 / 21 200 (World 3: 3 200 … 5 100 and 6 800 … 19 500). Models 1 828–3 588 triangles, all come in within 4.1–4.8 s. Angry heat goes on from World 3's 9: minis 9.5 / 10.5 / 11 / 12.5 / 13.5, finals 10 / 11 / 12 / 13 / 14. Stage patterns (parts fire the same while they stand; the core changes each stage):
- **Cinder Crab** (4-1 mini, ×0.5): two claws on arm joints with snapping fingers (aimed spreads of 3, they shield the core), a back mortar (slow big slag, aimed); core ring 10 → ring 12 → two alternating rings → ring 16 + 3-arm counter-spiral. Angry: curtain.
- **Steam Dreadnought** (4-1 final, ×0.6): two smokestacks (rings of 10), two broadside turrets (aimed bursts of 4), all four shield the core; a missile rack (2 homing missiles); core laser every stage, plus nothing → aimed 3 → fan 5 → ring 12 → fan 7 + aimed → two opposite spirals. Angry: flower.
- **Ash Wraith** (4-2 mini, ×1.5 chase): two shroud pods (fans of 3, they shield the core), an eye cannon (laser on a turret); core spiral 3 → reversed spiral 4 → slow spiral 6 → twin spirals of 5. Angry: vortex.
- **Geyser Rig** (4-2 final, ×0.4): two drill heads on shoulder joints (aimed bursts of 4), two steam vents (spirals of 3), all four shield the core; a drone hangar (2 Hornets every 7 s); core fan 3 → fan 5 → two leaning fans of 4 → fan 7 → fan 9 + quick fan 3 → five sweeping fans of 5. Angry: curtain.
- **Magma Salamander** (4-3 mini, ×0.6): two back fins (fans of 3, they shield the core), a tail on two joints (sweeping lines of 20 drops); core burst 3 → burst 4 → bursts of 3 + 5 → spiral 6 + bursts of 4. Angry: curtain.
- **Obsidian Golem** (4-3 final, ×0.3): two fists on shoulder and elbow joints (rings of 8 slow big globs), two shoulder cannons (aimed spreads of 3, on turrets), a chest emitter (laser), an armour plate; the fists and the plate shield the core; core aimed → burst 4 → fan 5 → spiral 10 → fan 7 + burst 3 → ring 12 + aimed 3 → magma bombs bursting into rings of 10 + two counter-turning spirals of 12. Angry: flower + vortex.
- **Furnace Drake** (4-4 mini, ×0.5): two beating wings on joints (fans of 3, they shield the core), a jaw on a swaying neck (a flame: a burst of 9 small fast bullets + an aimed spray of 4); core spiral 3 → spiral 4 the other way → spiral 5 → twin opposite spirals of 5 and 6. Angry: flower.
- **Foundry Ark** (4-4 final, ×0.3): two rail cannons (lasers on turrets) and a chimney row shield the core, a missile battery on the bow, two crucibles bursting into a ring of 14 when destroyed; core burst 4 → fan 5 → slag blob (ring 9) + aimed 3 → ring 12 + burst 3 → fan 7 + spiral 4 → two opposite spirals of 5 → two opposite rings of 16 + three slag blobs + burst 4. Angry: curtain + spirals.
- **Ember Herald** (4-5 mini, ×1.4 chase): three ember lances on a turning ring (spirals of 3), all shielding the core; core bursts 4 → bursts 5 → bursts 5 + spread 3 → two crossing spirals of 5 + bursts 4. Angry: spirals.
- **Caldera Throne** (4-5 final, ×0): two magma cannons (lasers on turrets), two missile batteries, two heat shield generators shielding the core; core bursts 4 → fan 7 → magma bomb (ring 9) + spread 3 → spiral 12 + bursts 3 → missiles + fan 5 + bursts 3 → laser + ring 14 + magma bomb → spiral 18 + laser + missiles + three magma bombs + bursts 4 + spread 3 (every attack kind). Angry: spirals + vortex.

### Gate results
```
Light verification (implementation): make typecheck ✔ · make build ✔ · make e2e: 88 / 88 passed (6.0 min); after small refactors for the pre-commit lint (file and function sizes), again typecheck ✔ · build ✔ · 88 / 88 e2e (6.4 min)
Lint, unit tests and coverage are deferred to /validate-phase (make check).

Rework (2026-10-27, D-112): make check ✔ — lint ✔ · prettier ✔ · typecheck ✔ · 1591 unit tests ✔ · coverage 98.61 % statements, 87.87 % branches, 98.69 % functions, 99.4 % lines ✔ · build ✔ · 117 e2e ✔ (5.6 min).
Review fixes (World 5 dropped; ten new enemy kinds): typecheck ✔ · build ✔ · 88 / 88 e2e each time (6.1 and 6.9 min).

Full gate (validation, 2026-10-26): make check ✔ — lint ✔ · prettier ✔ · typecheck ✔ · 1384 unit tests ✔ · coverage 98.66 % statements, 87 % branches, 98.74 % functions, 99.42 % lines ✔ (phase 9: 98.61 / 87.25 / 98.65 / 99.35) · build ✔ · 88 e2e ✔ (5.8 min).
Fixed on the way (first run: 3 of 1384 unit tests failed, all earlier tests not updated for this phase):
- game-definition.test.ts: the registered levels now include World 4, and the enemy kinds are 21 (P05-R24).
- scenery-levels.test.ts (P04-R04): Level Zero's prop check now leaves out the World 4 props, which only World 4 uses, as it does for Worlds 1–3.
```

### How to test manually
- `make dev`, then Start → a ship → the level select: the World 4 row (`4-1` … `4-5`) is unlocked and is the last row (20 levels, none locked). After 3-5's "Level complete", `4-1` is highlighted; after 4-5's, `4-5`.
- Each level (reworked 2026-10-27, D-112): `?level=4-1` … `?level=4-5` (with `&t=<seconds>`; F ×4, ← / → jump 10 s; add `&look=midday&weather=0` to see the ground under the clouds). Look for: 4-1 a pink-grey dawn over the garden villages 3-5 ended on, suburbs, terraces, flats and a town centre at the end (`t=250`); 4-2 an ash-dark midday over town streets, the ring road, mid-rise flats and a city park; 4-3 midtown's offices and mid-rise blocks, the river quays, the first city towers at the end, dusk turning to night; 4-4 the towers of the business district at night, the first skyscrapers in the financial district (`t=200`); 4-5 a skyline of skyscrapers, a central park, then skyscrapers filling every block under the red sky of the eruption (`t=250`, `&boss=final`).
- Debug: `&weather=0` (no ash, no embers: `?level=4-4&t=60&weather=0`), `&look=dawn|morning|midday|afternoon|dusk|night`, `&boss=mini|final` (K destroys the next part).
- Shots: in 4-3, 4-4 and 4-5 every bullet has a dark rim and a white heart, laser warning lines a white core; compare with any World 1–3 level (unchanged).
- Bosses: `bosses/` lists Worlds 1 to 4 under their headings; each boss comes in over its level's scenery and look; M / V show the model and wireframe (the Crab's claws, the Rig's drills, the Golem's fists, the Drake's wings).
- 60 FPS: the 4-4 forge belt (`?level=4-4&t=150`), the 4-5 final fight (`?level=4-5&boss=final`), with the debug FPS tile.

### Deviations from spec
- Rework (2026-10-27, D-112): the World 4 bosses and wave scripts are unchanged, so the volcanic bosses (Steam Dreadnought, Magma Salamander, Caldera Throne…) now fly over the town and the city. The times of day, clouds and weather (ash, embers, the eruption's red sky) are kept, as in the World 3 rework; the volcano erupts somewhere beyond the city. Lava, the volcanic props, their set pieces and lines (smoke vents, pipelines, rail lines with ore wagons) stay in the engine and the game, unused.
- P10-R03 "sea section": as D-079, a section with a coast or relief under the liquid level. 4-1 is entirely sea sections (islands rise from sea-floor relief). The lava of 4-3 … 4-5 fills channels and lakes cut below the liquid level, so those levels have no sea section; "lava share" is the ground under that level, measured as the sea share (D-084).
- P10-R04 4-3 "look change: the sun dims, the lava glow grows": a change from dusk to night over 60–280 s with the glow from below growing from 0.25 to 0.8 (D-083).
- P10-R04 4-5 "growing to 1.0 at the final boss": embers 0.6 → 1 and the red glow 0.6 → 1 over 180–300 s of ground; the ground is past 300 s when the final boss comes (the mini boss's chase runs it ahead).
- P10-R08 sea steam: a floating prop with a steam plume, placed on the sea by the sections' float density (denser near the islands and the hot coast; the engine has no "near the coast" rule). Ore wagons all move together, straight along the level.
- P10-R08 two prop ids got a `volcanic-` prefix (`volcanic-crane`, `volcanic-cooling-tower`): the plain ids already belonged to earlier props.
- P10-R10 tunable `peak_on_screen` (15 … 21): measured 53 … 66, order kept (as Worlds 1–3).
- P10-R11: some parts placed or sized for the bot's spread to reach them within the health bands (as D-081): the Crab's claws ±24, the Dreadnought's turrets ±56, the Rig's vents ±35, the Ark's rails ±72 and crucibles ±60; the Ark's missile battery sits on the bow ahead of the chimney row; the Drake's flame is a burst plus a spray (no stream shape in the engine).
- Angry heats were evened out by the lead after the five boss agents (D-063 rate, going up from 4-1 to 4-5).
- Tests of earlier phases that said World 4 was locked (P06-R01, P08-R01, P09-R01 unit and e2e, the menu pointer test) now say every level is unlocked and the grid is 4 × 5 (World 5 dropped, D-089); after 3-5 the level select highlights 4-1; the boss count is 40; the boss triangle test allows 7 000 for the Caldera Throne. No World 1–3 level data changed.
- Balance and fight-time numbers were measured with throw-away simulation scripts (not the unit-test runner).

### Known limitations
- 60 FPS (ENG-101) could not be measured here: only software WebGL is available (10–13 FPS for every level, as before). The lava levels draw the terrain once more into the glow map.
- Lint, unit tests and coverage have not been run (deferred to `/validate-phase`).
- One lava drift per level: 4-5's lake flows like a slow river rather than churning in place (its plates churn).
- The steam on the bosses' models is static geometry; the props' plumes move.
- Nothing was checked by eye under GPU rendering; lava, plumes and models were looked at in software-rendered screenshots only. The 4-4 smoke clouds (cover 0.6) hide a good part of the industry below.

### Suggestions for future phases
- A "near the coast" rule for floating props, and wagons that follow their line's heading and height.
- A props viewer page (like `bosses/`) would make the 31 new props easier to review.
