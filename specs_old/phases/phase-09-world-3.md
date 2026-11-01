# Phase 09 — World 3

> Fill the **Human** sections. Set **Status** to `Ready` when the agent may implement it.
> The agent fills the **Agent** sections and never edits the requirement sections.

**Status:** Ready  <!-- Draft | Ready -->
**Depends on:** Phase 8

---

## 🧑 Goal
World 3, **the Industrial Towns** (first the Jungle; reworked at the reviewer's request, 2026-10-27), has five playable levels, 3-1 to 3-5, each about 5 minutes long. The levels are one journey from the factories World 2 ended on, along canals and docks, through the workers' quarters and their terraces, to suburbs and garden villages of small houses (no skyscraper, no tower), with slow transitions along the levels. No sea: canals, rivers and ponds only. Each level has its own time of day, cloud cover and weather (morning mist, rain showers, a thunderstorm with lightning, night rain). Each level has its own mini boss and final boss, ten new bosses in all. The levels get harder from 3-1 to 3-5, and World 3 as a whole is harder than World 2.

## 🧑 Requirements

> ID format `P09-Rxx`. Every requirement is **MUST** (no SHOULD / MAY).
> Write each requirement so it is testable. Add acceptance criteria when "done" isn't obvious.
> World 3 is built exactly like World 2 (phase 8): the World 1 tools and rules (phases 4 to 7 and their review decisions), the level look (P08-R04) and the weather engine (P08-R05). Only what changes for World 3 is written here. Sizes are given relative to the medium player ship length (`L`). Numbers are listed in **Tunable values**.
> The new weather kinds (P09-R05) are game-agnostic engine features; the World 3 levels, looks and bosses are data and models in `src/game/` (`01-engineering.md` §2.3).

### P09-R01 — World 3 in the level select  · MUST

The World 3 row of the level select grid shows `3-1` to `3-5`, all unlocked (P06-R01). Worlds 4 and 5 stay greyed out. After `2-5` is completed, `level-select` shows with `3-1` highlighted; after `3-5`, with `3-5` highlighted.

**Acceptance criteria**
- [ ] Given `level-select`, then the World 3 row shows exactly `3-1` to `3-5`, all unlocked, each starting its level.
- [ ] Given `2-5` is completed, then `level-select` shows with `3-1` highlighted.
- [ ] Given a level of worlds 4 and 5, then it is still greyed out.

### P09-R02 — Duration  · MUST

Each World 3 level's scroll time at its ground speed is 300 s ± 10 s (as P08-R02).

**Acceptance criteria**
- [ ] Unit test: for each World 3 level, length ÷ ground speed is between 290 s and 310 s.

### P09-R03 — Scenery progression across World 3  · MUST

**Reworked at the reviewer's request (2026-10-27):** World 3 starts in the factories (where World 2 ends) and ends in habitations, small buildings only (no skyscrapers), with slow transitions along the levels; no sea (canals and rivers are allowed, as in World 2). The table below replaces the Jungle one (river delta, rainforest, lost temples, swamp works, canopy city).

The player flies from the great works World 2 ended on, along a canal through the factories and the docks, over the workers' quarters, to the suburbs and the garden villages. Each level begins on the very ground the previous one ended on (3-1 on 2-5's), and the changes are slow, as in World 2 (P08-R03): the sections blend over a long stretch, the concrete gives way to grass a little in each section, and each new kind of building first comes in mixed with the one before it.

| Level | Name | Water | Ground | Buildings |
|-------|------|-------|--------|-----------|
| 3-1 | Canal works | A canal between stone walls, from the second section on. | All concrete. | The great works 2-5 ended on, foundries along the canal, rail yards, canal docks, factory yards, the first workshops. |
| 3-2 | Docklands | The canal, wider at the docks. | Concrete, the first patches of grass. | Warehouses on the docks, workshop streets, old mills, then the first workers' flats. |
| 3-3 | Workers' quarter | The canal, a park along it, then a river. | Concrete and grass about even by the end. | Small blocks of flats, terraced streets, a canal park, brick terraces, then the first houses. |
| 3-4 | Suburbs | A river between grassy banks. | Mostly grass and gardens. | Houses with gardens, terraces, a town park, leafy avenues, then the first garden villages. No industry. |
| 3-5 | Garden villages | The river, ponds among the gardens. | Grass and gardens. | Houses, farmhouses, greenhouses and small modern homes; garden villages only at the end. No industry, no tower. |

**Acceptance criteria**
- [ ] Unit test: no World 3 level has a sea section (no coast, no ground under the water level, nothing floating); canals, rivers and ponds are not sea.
- [ ] Unit test: every World 3 level has some canal, river or pond water.
- [ ] Unit test: the concrete cover goes down and the grass cover goes up from 3-1 to 3-5 (more concrete than grass in 3-1 to 3-3, more grass in 3-4 and 3-5).
- [ ] Unit test: heavy industry in 3-1, no industry in 3-4 and 3-5, no suburb or village in 3-1, garden villages only in the last section of 3-5.
- [ ] Unit test (fixed seed): the number of props and of buildings placed goes up from 3-1 to 3-5, and each level's second half has more props than its first.
- [ ] Unit test: each level begins on the ground (relief, cover, streets, buildings, canal or river) the previous one ended on, 3-1 on 2-5's; the sections blend over the same long stretch as World 2's.
- [ ] Manual visual validation: factories, docks, workers' quarter, suburbs and garden villages can be told apart, the changes are slow, and no tall building stands in the suburbs and villages.

### P09-R04 — Look of each World 3 level  · MUST

Each level's look (P08-R04):

| Level | Time of day | Clouds (low / high cover) | Weather | Notes |
|-------|-------------|---------------------------|---------|-------|
| 3-1 | morning | 0.3 / 0.2, white | none | A low, warm sun and a **morning mist**: the haze is close and white over the factories at the start and lifts (moves away) over the first half (look change). |
| 3-2 | midday | 0.5 / 0.3, tall white cumulus | rain 0.4 over the middle third, then clearing | Bright, humid light (the green canopy tint was dropped with the rework, 2026-10-27). |
| 3-3 | afternoon, thunderstorm | 0.9 / 0.9, dark blue-grey | rain 0.8 with lightning | The storm builds over the first quarter (look change from 0.5 cloud and no rain); dark, with lightning lighting the ground. |
| 3-4 | dusk | 0.6 / 0.4, orange to purple | rain 0.3 | Ground lights come on (the windows and neon of the houses, the streets). |
| 3-5 | night | 0.6 / 0.4 clearing to 0.2 / 0.1 | rain 0.5, stopping before the final boss | The villages' windows and neon are lit and glow in the mist; after the rain, the clouds open on a moonlit sky. |

**Acceptance criteria**
- [ ] Unit test: each World 3 level's look data matches this table, look changes included.
- [ ] Manual visual validation of each level against the table; the player ship, enemies, shots and bonuses stay clearly visible in every level, the night and the storm included.

### P09-R05 — Weather: rain and lightning  · MUST

Two new weather kinds for the weather engine (P08-R05), used as data like snow:
- **Rain:** thin, light streaks falling fast at a slight slant, at different depths, scrolling with the ground. The strength sets how many streaks there are and how close and grey the haze comes. Water surfaces (sea, rivers, swamps) show faint rain rings. Rain is drawn behind the ships, shots and bonuses and never hides them.
- **Lightning:** a storm option on top of rain. A flash lights the whole scene for a short moment (ambient and sky brighter), sometimes with a bolt drawn inside the clouds. Flashes come at random times from the level's seed (deterministic). For players with photosensitivity, the flashes stay mild: at most **3 flashes in any 1 s**, on average one every few seconds (see **Tunable values**), and the brightness rise of a flash is limited so that the playfield never turns white.
- Weather is only a look (P08-R05): rain and lightning never change the simulation.

**Acceptance criteria**
- [ ] Given a look with rain of strength 0, then no streak is drawn; with strength 1, the most streaks allowed by **Tunable values** are drawn.
- [ ] Unit test: over a long simulated storm, there are never more than 3 flashes in any 1 s window, and the average gap is within **Tunable values**.
- [ ] Unit test: the same level played twice has its flashes at the same times.
- [ ] Unit test: weather is not an input of the simulation (as in P08-R05).
- [ ] Manual visual validation: rain looks light and fast, lightning is dramatic but not blinding; shots and bonuses stay visible through the storm.
- [ ] 60 FPS (ENG-101) during the 3-3 storm with the most enemies on screen.

### P09-R06 — Jungle ground and props  · MUST

**Reworked at the reviewer's request (2026-10-27):** the ground is World 2's stained industrial concrete giving way to grass, with damp dark earth between, grey stone on the canal walls and mud along the water; grey-green canal and river water flowing down the screen; asphalt roads. The buildings are Level Zero's industrial ones and those made of parts, then new homes (small blocks of flats, rows of terraced houses, houses with a pitched roof and a garage), Level Zero's modern homes and World 1's farmhouses and greenhouses; the plants are Level Zero's (dead trees by the factories, broadleaf trees, conifers and bushes in the streets, parks and gardens). The jungle ground and props below were built for the first World 3 and stay in the game, but no level uses them.

New generated ground and props for World 3 (GD-60, made in code), as light in polygons as the existing ones (D-031) and matte (D-024):
- **Ground:** dark, wet jungle soil, moss-green on slopes, red-brown mud banks, grey-green cliff rock, and old paved stone around the ruins.
- **Water:** rivers (muddy green-brown water in a channel cut with the heightmap tools, flowing down the screen), swamp water (dark, still, with reeds and lily pads), a lake, and **waterfalls** (white falling water with spray where a river drops over a cliff).
- **Vegetation:** a dense **canopy** (big round broadleaf crowns in several greens, packed edge to edge so little ground shows), palms, giant ferns, mangroves on stilt roots, twisted swamp trees, vines on the ruins. The canopy is the main cost of this world, so it is instanced and stays within the triangle budget.
- **Habitations:** stilt huts and villages, river ports, logging camps, overgrown stepped pyramids, stone statues and causeways, enemy outposts in the ruins (antennas, gun pits, neon gates), bio-labs, pipelines, pumping stations, the giant dam with its power plant, tree-top platforms, and city towers linked by sky bridges with trees on their roofs. They follow the road rules of World 1 (D-046); jungle roads are red dirt tracks.

**Acceptance criteria**
- [ ] Manual visual validation: the canopy reads as a thick jungle from the playfield camera, the rivers flow, and World 3 does not look like World 1 or 2 with another colour.
- [ ] Unit test: each new prop model stays under the triangle budget in **Tunable values**.

### P09-R07 — Enemy waves  · MUST

Each World 3 level has a wave script with fillers (P06-R07, D-051), using the eleven phase 5 kinds, every kind allowed from 3-1 on:

| Level | Enemy kinds that lead the waves |
|-------|--------------------------------|
| 3-1 | Gnat, Hornet, Scout, Strafer, Weaver, Splitter (skimming the delta) |
| 3-2 | every kind, with Hornet swarms diving out of the canopy and Lancers along the river |
| 3-3 | every kind, with Spinner and Rocketeer groups around the temples |
| 3-4 | every kind, with Carriers over the swamp |
| 3-5 | every kind, the heaviest mixes (Bulwarks escorting Carriers) |

**Acceptance criteria**
- [ ] Unit test: each World 3 wave script only uses the kinds listed for its level, and 3-2 to 3-5 use all eleven.
- [ ] Unit test: the waves are deterministic.

### P09-R08 — Increasing difficulty  · MUST

As in P08-R09:
- from 3-1 to 3-5, enemies per minute of scroll, total enemy HP per minute and the peak enemies on screen go up strictly; the bullet speed and fire rate factors never go down;
- in each level, the second half has more enemy HP than the first half;
- **across worlds:** 3-1 is at least as hard as 2-3, and 3-5 is harder than 2-5, on the same measures.

**Acceptance criteria**
- [ ] Unit test: the strict increases from 3-1 to 3-5.
- [ ] Unit test: 3-1 ≥ 2-3 and 3-5 > 2-5.
- [ ] Unit test: in each World 3 level, the second half has more enemy HP than the first.
- [ ] Manual validation: 3-1 feels like a fresh start, 3-5 clearly harder than 2-5.

### P09-R09 — The ten World 3 bosses  · MUST

Each World 3 level has its own mini boss and final boss (P07-R05, P07-R06), code-generated in the World 3 theme (dark metal with neon, GD-61, plus moss, vines, stone and animal shapes). Stage patterns are designed by the agent and reported. Moving limbs use D-061.

| Level | Kind | Name | Look | Destroyable parts (weapons) | Fight ground speed |
|-------|------|------|------|-----------------------------|--------------------|
| 3-1 | Mini | Mangrove Croc | A long, low hover-gunboat (3 L) with jaws that open and close, green neon eyes | 1 jaw cannon (opens to fire aimed bursts), 2 side pontoon guns (fans), the pontoons shield the core. Core: rings | ×1.4 (chase up the delta) |
| 3-1 | Final | River Leviathan | A segmented serpent-ship (6 L long) whose body sways from side to side, teal neon along its spine | 4 body segments, each with a turret (rings, in turn), shield the core; 1 tail missile rack. Core (the head): laser | ×0.5 |
| 3-2 | Mini | Toucan | A stubby gunship (3 L) with a huge bright beak, yellow and orange neon | 1 beak cannon (warning line + laser), 2 wing pods (fans), the pods shield the core. Core: aimed bursts | ×0.6 |
| 3-2 | Final | Canopy Spider | A four-legged walker-ship (5 L) hanging over the canopy, its legs stepping in turn, red neon eyes | 4 legs, each with a gun (aimed spreads), shield the core; 1 egg sac (launches Gnat groups). Core: spirals | ×0.4 |
| 3-3 | Mini | Stone Idol | A flying stone head (3 L) with neon cracks, glowing eyes and mouth | 2 eyes (warning line + lasers), shield the core; 1 mouth (rings of slow, big bullets). Core: fans | ×0 (the ground stops over the temple) |
| 3-3 | Final | Sky Temple | A flying stepped pyramid fortress (5.5 L) with four corner obelisks, gold and cyan neon | 4 obelisks (spirals), shield the core; 1 summit beacon (homing missiles). Core: every bullet pattern | ×0.3 |
| 3-4 | Mini | Mosquito | A thin, fast bio-drone (3 L) with buzzing wings, pink neon | 2 wings (fans), shield the core; 1 proboscis (warning line + laser). Core: aimed bursts | ×0.6 |
| 3-4 | Final | Dam Breaker | A giant armoured barge (5.5 L) with sluice gates and glowing chemical tanks, toxic green neon | 2 sluice cannons (waves of slow big bullets), 2 chemical tanks (burst into a ring of bullets when destroyed), 1 drone hangar (launches Hornets), 1 armour plate (no weapon); the cannons and the plate shield the core | ×0.3 |
| 3-5 | Mini | Jaguar | A sleek stealth interceptor (3.5 L) with spotted armour, amber neon | 2 claw guns (aimed spreads), shield the core; 1 tail cannon (laser). Core: spirals | ×0.6 |
| 3-5 | Final | Verdant Crown | A city-ship (6 L) carrying a glass garden dome, emerald and magenta neon | 2 thorn cannons (lasers), 2 seed batteries (homing missiles), 2 root generators (no weapon, shield the core). Core: every attack kind | ×0.25 |

Mini bosses have 2 or 3 destroyable parts and final bosses 4 to 6 (P07-R01). Within World 3, at least one fight stops the ground (×0) and at least one is a chase (> ×1).

**Acceptance criteria**
- [ ] Unit test: each World 3 level has exactly one mini boss and one final boss from this table, with 2–3 and 4–6 destroyable parts.
- [ ] Unit test: in a long simulated fight, every boss's hit circles stay inside the ship's reach (D-048), the River Leviathan's swaying segments included.
- [ ] Manual visual validation of the ten models in `bosses/` (model and wireframe views), the moving jaws, legs and segments included.

### P09-R10 — Boss difficulty in World 3  · MUST

As in P08-R11: mini boss and final boss full HP go up strictly from 3-1 to 3-5; each final boss has more full HP than its level's mini boss; each World 3 boss has more full HP than the World 2 boss of the same level and kind; boss bullets use the level's factors; the fight times (simulation, balanced ship, guns at level 3, always firing at the boss) are within **Tunable values**.

**Acceptance criteria**
- [ ] Unit test: the HP orderings above.
- [ ] Unit test (simulation): fight times within the ranges.
- [ ] Manual validation: the World 3 bosses feel harder than the World 2 ones.

### P09-R11 — Debug options and the `bosses/` page  · MUST

- The debug URL options (P06-R09, P07-R09, P08-R12) accept every World 3 level, `weather=0` and `look=<time of day>` included.
- The `bosses/` page lists the World 3 bosses after the World 2 ones, each over the scenery and look of its level.

**Acceptance criteria**
- [ ] Given `?level=3-3&t=120`, then 3-3 starts at 2:00 in its thunderstorm.
- [ ] Given `?level=3-3&weather=0`, then 3-3 shows no rain and no lightning.
- [ ] Given `bosses/`, then every boss of Worlds 1 to 3 can be picked without console errors.

## 🧑 Tunable values
| Name | Value | Notes |
|------|-------|-------|
| level_duration | 300 s ± 10 s | P09-R02 |
| ground_speed 3-1 / 3-2 / 3-3 / 3-4 / 3-5 | 70 / 60 / 55 / 60 / 60 px/s | GD-01; slower in the storm |
| sea_share | 0 % in every level | P09-R03 (reviewer, 2026-10-27; was ≤ 30 % in 3-1) |
| section_transition | 900 units, as World 2 | P09-R03 (reviewer, 2026-10-27) |
| peak_on_screen 3-1 / 3-2 / 3-3 / 3-4 / 3-5 | 13 / 14 / 15 / 17 / 19 | P09-R08; the agent may adjust while balancing, keeping the order |
| enemy_bullet_speed_factor 3-1 → 3-5 | 1.0 / 1.05 / 1.1 / 1.2 / 1.25 | P09-R08 |
| enemy_fire_rate_factor 3-1 → 3-5 | 1.0 / 1.05 / 1.1 / 1.2 / 1.25 | P09-R08 |
| rain_streaks_max | 2 000 (at strength 1) | P09-R05; the agent may lower it for ENG-101 |
| lightning_gap | 4–10 s, random from the seed | P09-R05 |
| lightning_max_flashes | 3 in any 1 s | P09-R05, photosensitivity |
| lightning_flash | about 0.15 s, brightness at most ×1.8 the storm's | P09-R05 |
| morning_mist (3-1) | fog end at 40 % of the clear distance, lifting to 100 % over the first half | P09-R04 |
| mini_fight_time 3-1 → 3-5 | 35–45 s → 50–60 s | P09-R10, balanced ship, guns level 3, always on target |
| final_fight_time 3-1 → 3-5 | 70–90 s → 110–140 s | P09-R10, same |
| boss_triangles | ≤ 6 000 per boss | as in phase 7 |
| prop_triangles | within the range of the phase 6 props; the canopy crowns lighter still | P09-R06, D-031 |

## 🧑 Out of scope for this phase
- Worlds 4 and 5 and their weather kinds (falling ash, embers).
- New regular enemy kinds.
- Gameplay effects of the weather, water or ground (wind, slowing mud): weather is only a look.
- Wet ground reflections and puddle reflections (costly); the rain rings on water are enough.
- Bombs, extra lives, score, high score, pause, music and sound effects.
- Changing the World 1 and World 2 levels.

## 🧑 Engineering additions for this phase
- Rain and lightning are new weather kinds in the game-agnostic weather engine, unit tested; the World 3 levels, looks, props, wave scripts and bosses are data and views in `src/game/`.
- The World 1 and World 2 levels keep passing their tests unchanged.
- An e2e test confirms each World 3 level from the menu and checks it starts without console errors.
- An e2e test opens `?level=3-1&boss=final`, destroys the boss with K and the debug fire, and reaches the "Level complete" overlay.
- 60 FPS (ENG-101) in the 3-2 rainforest (densest canopy), in the 3-3 storm, and in the 3-5 final boss fight at night.

## 🧑 Manual validation checklist
- [ ] Runs on GitHub Pages / `make dev` without console errors
- [ ] `3-1` to `3-5` can be picked in the level select; worlds 4 and 5 stay locked
- [ ] Factories, docks, workers' quarter, suburbs and garden villages across the five levels, slow changes; each level begins where the previous one ended, 3-1 where 2-5 ended; no tall building in the suburbs and villages
- [ ] Morning mist lifting in 3-1, a rain shower in 3-2, the 3-3 thunderstorm, rainy dusk in 3-4, rainy night clearing in 3-5
- [ ] Lightning is dramatic but never blinding or fast-flashing
- [ ] Canals and rivers flow
- [ ] The ten World 3 bosses look good in `bosses/`; jaws, legs and segments move
- [ ] Difficulty clearly goes up from 3-1 to 3-5, and 3-5 is harder than 2-5
- [ ] 60 fps in the rainforest, the storm and the 3-5 final boss fight

## 🧑 Notes, references, sketches
- **Drafted by the agent at the reviewer's request (2026-10-25); open choices, defaults proposed:** the same as phase 8 (themes, no new enemy kinds, 5-minute levels, a softer start for each world, fight times with guns at level 3, boss designs as suggestions).
- Photosensitivity: the lightning limits follow the usual web accessibility rule (no more than three flashes in any one second).
- The River Leviathan and the Canopy Spider are the most complex limb animations so far (D-061); if they cost too much, the agent reports it before simplifying.

---

## 🧑 Review feedback
> After the agent reports, write corrections here, then say **"Fix phase 09"**.
> The agent ticks each item when fixed.

- [x] (2026-10-27, after validation) Rework World 3: start in the factories and end in habitations (small buildings only, no skyscrapers), with slow transitions along the levels. → P09-R03, R04 (notes), R06 amended; D-111.

---

## 🤖 Implementation report
> Filled by the agent. Do not edit (comment in Review feedback instead).

### Questions / blockers
None. The spec was implemented as written; the interpretations are listed under Deviations.

### Plan
| Task | Requirement IDs |
|------|-----------------|
| Engine weather: `rain` kind (streaks along the fall, greyer haze, rings on the water), lightning (seeded schedule, capped flash, bolt), mist and ambient tint in the look (`config/weather.ts`, `core/scenery/lightning.ts`, `sky-look.ts`, `render/scenery/rain-rings*.ts`, `lightning-layer.ts`, `weather-material.visual.ts`) | P09-R04, R05 |
| Engine placement: set pieces (`PropRules.landmarks`) and prop lines over water (`PropLine.overWater`) | P09-R03, R06 |
| World 3 scenery (delta, rainforest, temples, swamp and dam, canopy city), looks, waves, difficulty, level assembly and registration | P09-R01..R04, R07, R08 |
| World 3 props: 29 hand-made models and two families of 8 (sub-agent) | P09-R06 |
| Ten bosses, designs + models, tuned with the D-055 bot (five sub-agents, one per level) | P09-R09, R10 |
| Debug options and `bosses/` page (follow from the level data); test API sky state | P09-R11 |
| Unit and e2e tests, docs, decisions | all |

### Requirement traceability
| ID | Status (Done / Partial / Not done) | Code | Tests | Notes |
|----|-----------------------------------|------|-------|-------|
| P09-R01 | Done | `game/sim/world-3.ts`, `game/sim/levels.ts` | `world-3.test.ts`, `levels.test.ts`, e2e `world-3.spec.ts`, `menu-pointer.spec.ts` | 2-5 → 3-1 and 3-5 → 3-5 follow from the grid order |
| P09-R02 | Done | `game/config/world-3/scenery.ts` (300 s each) | `world-3.test.ts`, e2e | speeds 70 / 60 / 55 / 60 / 60 |
| P09-R03 | Done (reworked 2026-10-27) | `world-3/scenery.ts` (replaces `scenery-river.ts` and `scenery-inland.ts`), `world-3/props.ts` | `world-3.test.ts` | D-111, D-139; no sea; props 6 919 / 7 283 / 8 540 / 10 181 / 10 872, buildings 6 919 / 7 225 / 7 354 / 7 556 / 7 942 (2026-10-28: street grids only as wide as the ground that shows; were 11 085 / … / 14 909 and 11 085 / … / 13 514) |
| P09-R04 | Done | `game/config/world-3/looks.ts`, `core/scenery/sky-look.ts` (mist, tint, lightning) | `world-3.test.ts`, `sky-look.test.ts`, e2e | D-078; readability: manual; the rework keeps the sky scripts, minus 3-2's green tint (D-111) |
| P09-R05 | Done | `config/weather.ts`, `core/scenery/lightning.ts`, `render/scenery/rain-rings*.ts`, `lightning-layer.ts`, `sky-layers.ts`, `weather-material.visual.ts` | `lightning.test.ts`, `sky-look.test.ts`, `storm-layers.test.ts`, `game-play-weather.test.ts` (not an input), e2e | D-076, D-077; 60 FPS: manual |
| P09-R06 | Done (reworked 2026-10-27) | `game/view/props/suburb-props.ts` (new homes), `jungle-*.ts` (kept, unused), `world-3/props.ts`, `world-3/looks.ts` | `world-3-homes.test.ts`, `prop-models.test.ts` | homes 36 / 66 / 50 triangles; hand-made jungle props ≤ 336 (dam 553 ≤ 600), canopy 111 / 110 |
| P09-R07 | Done | `game/config/world-3/waves.ts` | `world-3.test.ts` | D-080 |
| P09-R08 | Done | `waves.ts`, `world-3/difficulty.ts` | `world-3.test.ts` | numbers below |
| P09-R09 | Done | `game/config/bosses/world-3/*`, `game/view/bosses/world-3/*` | `bosses-world-3.test.ts`, `boss-models.test.ts`, `muzzles.test.ts`, e2e | D-081; patterns below |
| P09-R10 | Done | the ten designs' health | `bosses-world-3.test.ts` | fight times below |
| P09-R11 | Done | level data (the debug options and `bosses/` page take every level), `app/game-play.ts` (sky state) | `debug-options.test.ts`, `storm-layers.test.ts`, e2e `world-3.spec.ts`, `bosses.spec.ts` | |

**Balance (P09-R08)**, measured without shooting (seed 606), per minute of scroll: enemies 178.8 / 194.4 / 215.0 / 262.6 / 308.4, HP 4 214 / 5 694 / 6 884 / 8 068 / 10 506, peak on screen 38 / 41 / 47 / 55 / 58 for 3-1 … 3-5 (2-3: 121.4, 3 666, 36; 2-5: 233.4, 7 360, 51). Every second half carries more HP. As in Worlds 1 and 2, the peaks are far above the tunable 13 … 19, in the same order.

**Bosses (P09-R09, R10).** Fight times with the D-055 bot (guns level 3, always on target), mini / final: 3-1 41.6 / 87.5 s, 3-2 44.4 / 90.6 s, 3-3 47.3 / 102.4 s, 3-4 51.4 / 115.2 s, 3-5 54.7 / 127.1 s. Full health: mini 3 200 / 3 780 / 4 200 / 4 500 / 5 100, final 6 800 / 9 050 / 9 950 / 14 000 / 19 500 (World 2: 2 720 … 4 200 and 6 500 … 17 500). Models 1 628–3 966 triangles, within 6 % of their sizes. Stage patterns (parts fire the same while they stand; the core changes each stage):
- **Mangrove Croc** (3-1 mini, ×1.4 chase): two pontoons (fans of 3, they shield the core) and a jaw cannon (aimed bursts of 3) between jaws on two hinge joints that open in time with the bursts; core ring 10 → ring 12 → two alternating rings → spiral 4 + ring 14. Angry: vortex.
- **River Leviathan** (3-1 final, ×0.5): a head and four segments on a five-joint spine, a wave running from head to tail; each segment's turret fires rings of 8 in turn (1.1 s apart), a tail rack homing missiles; the head's laser every stage, plus aimed 3 → fan 5 → burst 4 → fan 7 → two spirals. Angry: spirals.
- **Toucan** (3-2 mini, ×0.6): two wing pods (fans), a beak laser; core bursts 3 → 4 → 4 + spread 3 → spiral 12 + bursts 3. Angry: curtain.
- **Canopy Spider** (3-2 final, ×0.4): four legs on hip and knee joints stepping in turn, each with a gun firing aimed spreads; an egg sac launching 3 Gnats every 7 s; core ring 8 → ring 9 → ring 10 → two spirals → ring 11 + slow ring 7 → double spiral 12. Angry: flower.
- **Stone Idol** (3-3 mini, ×0): two eyes (lasers on turrets), a mouth (rings of 9 slow big bullets); core fan 3 → fan 5 → two leaning fans of 5 → spiral 5 + fan 7. Angry: flower.
- **Sky Temple** (3-3 final, ×0.3): four obelisks (spirals of 4), a summit beacon (homing missiles); core aimed → spread 3 → burst 4 → fan 5 → ring 12 + fan 7 → two spirals + burst 3 (every bullet pattern). Angry: vortex + flower.
- **Mosquito** (3-4 mini, ×0.6): two buzzing wings (fans crossing), a proboscis (laser on a turret); core bursts 3 → 4 → 5 + spread 3 → ring 12 + bursts 3. Angry: vortex.
- **Dam Breaker** (3-4 final, ×0.3): two sluice cannons (waves of slow big bullets), an armour plate, two chemical tanks (a ring of 12 when destroyed), a drone hangar (2 Hornets every 7 s); core aimed → spread 3 → burst 4 → fan 5 → fan 7 + burst → ring 10 + aimed → two spirals of 14. Angry: curtain.
- **Jaguar** (3-5 mini, ×0.6): two claw guns (aimed spreads, on turrets), a tail cannon (laser on a turret); core spiral 3 → 4 → 5 → twin spirals of 5. Angry: curtain.
- **Verdant Crown** (3-5 final, ×0.25): two thorn cannons (lasers on turrets), two seed batteries (homing missiles), two root generators shielding the core; core bursts 4 → fans 5 → a seed pod bursting into a ring + spread 3 → missiles + bursts → laser + fan 7 → ring 12 + seed pods → spiral 16 + laser + missiles + seed pods + bursts (every attack kind). Angry: flower + spirals.

### Gate results
```
Light verification (implementation): make typecheck ✔ · make build ✔ · make e2e: 77 tests, 76 passed / 1 failed (a phase 6 test still expecting World 3 locked; fixed), then after a lint refactor of the prop placer, a full re-run: typecheck ✔ · build ✔ · 77 / 77 e2e passed (5.6 min)
Lint, unit tests and coverage are deferred to /validate-phase (make check).

Rework (2026-10-27, D-111): make check ✔ — lint ✔ · prettier ✔ · typecheck ✔ · 1580 unit tests ✔ · coverage 98.62 % statements, 87.97 % branches, 98.71 % functions, 99.41 % lines ✔ · build ✔ · 117 e2e ✔ (6.0 min).

Full gate (validation, 2026-10-26): make check ✔ — lint ✔ · prettier ✔ · typecheck ✔ · 1210 unit tests ✔ · coverage 98.61 % statements, 87.25 % branches, 98.65 % functions, 99.35 % lines ✔ (phase 8: 98.5 / 88.04 / 98.57 / 99.26) · build ✔ · 77 e2e ✔ (5.8 min).
Fixed on the way (first run: 6 of 1210 unit tests failed):
- set pieces were missed by the placer's bucketed neighbour search past ~64 units from their centre, so trees and buildings could stand on them: every placement now checks the set pieces and lines too (World 3 only; earlier layouts unchanged);
- a lightning flash could push a haze channel to 1 (white): the flashed haze is capped at 0.85 (`LIGHTNING.maxHaze`);
- the River Leviathan took 7.1 s to come in (P07-R05: under 6.5 s): it stops higher (0.72 of the screen), and its core went 2 800 → 2 500 HP to stay in its fight range (full 6 800, 87.5 s);
- three earlier tests counted the registered levels, the bosses and Level Zero's props without World 3; the set-piece test used a place past the end of the small sample level.
```

### How to test manually
- `make dev`, then Start → a ship → the level select: the World 3 row (`3-1` … `3-5`) is unlocked, worlds 4 and 5 stay locked. After 2-5's "Level complete", `3-1` is highlighted; after 3-5's, `3-5`.
- Each level (reworked 2026-10-27, D-111): `?level=3-1` … `?level=3-5` (with `&t=<seconds>`; F ×4, ← / → jump 10 s; add `&look=midday&weather=0` to see the ground under the rain clouds). Look for: 3-1 the great works 2-5 ended on under a white morning mist lifting by 2:30, then a canal between stone walls through foundries, rail yards, docks and factory yards, the first workshops at the end; 3-2 warehouses on the canal docks, workshop streets, old mills, the first workers' flats, a rain shower from 1:40 to 3:20 with rings on the canal; 3-3 the storm building over the first 75 s over blocks of flats, terraced streets, a park along the canal, brick terraces where the canal becomes a river, the first houses; 3-4 a rainy dusk over garden suburbs, houses along the river, a town park, leafy avenues; 3-5 a rainy night over garden villages (houses, farmhouses, greenhouses, ponds), no tall building, the clouds opening on a moonlit sky before the final boss (`?level=3-5&t=280`). The slow changes: the concrete turns to grass and the buildings change a little in each section.
- Debug: `&weather=0` (no rain, no rings, no lightning: `?level=3-3&t=120&weather=0`), `&look=dawn|morning|midday|afternoon|dusk|night`, `&boss=mini|final` (K destroys the next part).
- Bosses: `bosses/` lists Worlds 1, 2 and 3 under their headings; each boss comes in over its level's scenery and look; M / V show the model and wireframe (check the Croc's jaws, the Leviathan's swaying body, the Spider's legs, the Mosquito's wings).
- Lightning: dramatic but not blinding; no more than two flashes in a second (a strike may flicker twice).
- 60 FPS: the 3-2 rainforest (`?level=3-2&t=150`), the 3-3 storm with the most enemies (`?level=3-3&t=280`), the 3-5 final fight (`?level=3-5&boss=final`), with the F3 / debug FPS tile.

### Deviations from spec
- Rework (2026-10-27, D-111): the World 3 bosses and wave scripts are unchanged, so the jungle-themed bosses (Mangrove Croc, River Leviathan, Canopy Spider, Stone Idol, Sky Temple, Dam Breaker, Verdant Crown…) now fly over factories and suburbs; the Stone Idol still stops the ground (×0), over the workers' quarter. The jungle props, the set pieces (waterfalls, great pyramid, dam) and the prop lines (causeway, swamp pipelines) stay in the game, unused. The time of day and weather of each level are kept (morning mist, midday shower, afternoon storm, rainy dusk, rainy night), only 3-2's green canopy tint is dropped.
- P09-R03 "sea section": a section with a coast or whose relief lies under the water level; rivers, swamps, lakes and pools hold water at the same level as the sea, in channels, low relief or basins (D-079). 3-1's sea sections (open sea, delta mouth) are 80 of its 300 s and 23 % of its ground under water.
- P09-R06 waterfalls: the river is at one level above and below a fall; the drop is a set piece (a rock ledge across the river, a falling white sheet and spray), four of them in 3-3 (D-079).
- P09-R05 `lightning_gap`: measured between strikes (4–10 s, about 7 on average); a strike flickers twice with a chance of 0.35, so the flashes come about every 5 s and never more than 2 in a second (cap 3).
- P09-R05: a flash also never brightens a haze channel past 0.85, so the far haze never turns white.
- P09-R05: the flash follows the scene's clock (seconds since the level's scene was built), not the level's progress (D-077).
- P09-R08 tunable `peak_on_screen` (13 … 19): measured 38 … 58, order kept (as Worlds 1 and 2).
- P09-R09: some boss parts were placed or sized for the bot's spread to reach them within the health bands (Spider forelegs raised forward, Stone Idol eyes 64 apart, Verdant Crown roots 64 apart, larger hit circles on the Leviathan and the Jaguar; D-081). The Croc's jaws open with its bursts in its first stage only.
- Tests of earlier phases that said World 3 was locked (P06-R01, P08-R01 unit and e2e) now say worlds 4 and 5 are (P09-R01); the atmosphere test fixtures got the new `lightning` field. No World 1 or 2 level data changed.
- Balance and fight-time numbers were measured with throw-away simulation scripts (not the unit-test runner), as the implement procedure forbids running unit tests before validation.

### Known limitations
- 60 FPS (ENG-101) could not be measured here: only software WebGL is available. The canopy is about 8 clusters of ~110 triangles per 50 × 50 cell in the rainforest.
- Lint, unit tests and coverage have not been run (deferred to `/validate-phase`).
- The water is one colour per level (3-4's darker); the falling water and spray are not self-lit at night.
- The Croc's jaws and its bursts drift apart after the first destroyed part (keeping them in step would need an engine change). The Leviathan's ring turrets turn but fire from their axis.
- Nothing was checked by eye under GPU rendering; the boss models were looked at in software-rendered screenshots only.

### Suggestions for future phases
- Falling ash (World 4) can reuse the rain's `align` / `haze` fields; embers could be a weather kind with self-lit particles.
- A props viewer page (like `bosses/`) would make the prop models easier to review.
