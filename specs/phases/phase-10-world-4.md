# Phase 10 — World 4

> Fill the **Human** sections. Set **Status** to `Ready` when the agent may implement it.
> The agent fills the **Agent** sections and never edits the requirement sections.

**Status:** Ready  <!-- Draft | Ready -->
**Depends on:** Phase 9

---

## 🧑 Goal
World 4, **the Volcanic Lands**, has five playable levels, 4-1 to 4-5, each about 5 minutes long. The levels go from black-sand volcanic islands to grey ash plains, glowing lava fields and the enemy's giant foundries at night, and end over an erupting caldera. Each level has its own time of day, cloud cover and weather (a red dawn, an ash-dark noon, embers rising at dusk, a furnace-lit night). Each level has its own mini boss and final boss, ten new bosses in all. The levels get harder from 4-1 to 4-5, and World 4 as a whole is harder than World 3.

## 🧑 Requirements

> ID format `P10-Rxx`. Every requirement is **MUST** (no SHOULD / MAY).
> Write each requirement so it is testable. Add acceptance criteria when "done" isn't obvious.
> World 4 is built exactly like Worlds 2 and 3 (phases 8 and 9): the World 1 tools and rules (phases 4 to 7 and their review decisions), the level look (P08-R04) and the weather engine (P08-R05, P09-R05). Only what changes for World 4 is written here. Sizes are given relative to the medium player ship length (`L`). Numbers are listed in **Tunable values**.
> Lava (P10-R05) and the new weather kinds (P10-R06) are game-agnostic engine features; the World 4 levels, looks and bosses are data and models in `src/game/` (`01-engineering.md` §2.3).

### P10-R01 — World 4 in the level select  · MUST

The World 4 row of the level select grid shows `4-1` to `4-5`, all unlocked (P06-R01). World 5 stays greyed out. After `3-5` is completed, `level-select` shows with `4-1` highlighted; after `4-5`, with `4-5` highlighted.

**Acceptance criteria**
- [ ] Given `level-select`, then the World 4 row shows exactly `4-1` to `4-5`, all unlocked, each starting its level.
- [ ] Given `3-5` is completed, then `level-select` shows with `4-1` highlighted.
- [ ] Given a level of World 5, then it is still greyed out.

### P10-R02 — Duration  · MUST

Each World 4 level's scroll time at its ground speed is 300 s ± 10 s (as P08-R02).

**Acceptance criteria**
- [ ] Unit test: for each World 4 level, length ÷ ground speed is between 290 s and 310 s.

### P10-R03 — Scenery progression across World 4  · MUST

The player crosses a volcanic sea to the land of the enemy's war industry, deeper and deeper into fire. Each level begins on the kind of ground the previous one ended on (as in P06-R05).

| Level | Name | Sea / lava | Land | Habitations |
|-------|------|------------|------|-------------|
| 4-1 | Black sands | Mostly a dark, steaming sea between volcanic islands; a black-sand coast in the last 30 s. | Black rock islands with smoking vents, black-sand beaches, sparse hardy grass. | A few fishing huts, a geothermal well, a small harbour on the final coast. |
| 4-2 | Ash plains | No sea. | Flat grey ash plains, dead burnt forests, low cinder cones, a few hot springs. | Geothermal power plants, pipelines, cooling towers, ash-covered settlements along a road. |
| 4-3 | Lava fields | Rivers and pools of **lava** among the rock, more and more of them through the level. | Cooled black basalt with cracks, steep cinder cones, a volcano's flank. | Mining outposts on the cooled rock, lava pumps and heat collectors. |
| 4-4 | Forge belt | Slag rivers (lava) running out of the factories. | Scorched ground and basalt between the industrial sites. | The enemy's giant foundries: smelters, blast furnaces, chimney rows, rail lines, cranes, slag heaps, dense industry all along the level. |
| 4-5 | Caldera | The final stretch is a **magma lake** filling the caldera. | The volcano's slopes, then the caldera rim, then the lake. | The enemy's war factory on the rim (hangars, launch pads, armoured towers), a fortress city at the edge of the lake. |

The amount of lava goes up from 4-3 to 4-5, and the number of buildings goes up from 4-1 to 4-4 (4-5 trades buildings for its lake).

**Acceptance criteria**
- [ ] Unit test: 4-1 has a sea share ≥ 70 %, 4-2 to 4-5 have no sea section.
- [ ] Unit test: 4-1 and 4-2 have no lava; the share of the level's ground covered by lava goes up strictly from 4-3 to 4-5.
- [ ] Unit test (fixed seed): the number of buildings placed goes up from 4-1 to 4-4.
- [ ] Manual visual validation: volcanic islands, ash plains, lava fields, foundries and caldera can be told apart, and each level begins where the previous one ended.

### P10-R04 — Look of each World 4 level  · MUST

Each level's look (P08-R04):

| Level | Time of day | Clouds (low / high cover) | Weather | Notes |
|-------|-------------|---------------------------|---------|-------|
| 4-1 | dawn | 0.4 / 0.3, ash-tinted pink and grey | none | A red rising sun behind a smoke haze; steam over the sea. |
| 4-2 | midday, under an ash cloud | 0.9 / 0.9, brown-grey | falling ash 0.5 | A dim, flat, yellowish light, as if the sun were behind smoke; weak shadows. |
| 4-3 | dusk | 0.5 / 0.4, dark grey lit orange from below | embers 0.4 | The sunset fades while the lava's glow takes over (look change over the level: the sun dims, the lava glow grows). |
| 4-4 | night | 0.6 / 0.5, smoke lit orange from below | falling ash 0.3, embers 0.3 | Lit by the furnaces, slag rivers and factory lights; ground lights at their strongest. |
| 4-5 | night, eruption | 0.7 / 0.6, red-lit | embers 0.6, growing to 1.0 at the final boss | The volcano erupts during the level (look change: the sky haze turns deep red and the embers grow as the caldera comes near). |

**Acceptance criteria**
- [ ] Unit test: each World 4 level's look data matches this table, look changes included.
- [ ] Manual visual validation of each level against the table; the player ship, enemies, shots and bonuses stay clearly visible in every level. Red and orange enemy shots must still stand out from the lava and the red sky (see P10-R07).

### P10-R05 — Lava  · MUST

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
| sea_share 4-1 / 4-2..4-5 | ≥ 70 % / 0 % | P10-R03 |
| lava_share 4-3 / 4-4 / 4-5 | ~10 % / ~20 % / ~35 % of the ground | P10-R03 |
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
- World 5.
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
- [ ] `4-1` to `4-5` can be picked in the level select; World 5 stays locked
- [ ] Volcanic islands, ash plains, lava fields, foundries and caldera across the five levels; each level begins where the previous one ended
- [ ] A red dawn in 4-1, a dim ash-dark noon in 4-2, dusk giving way to lava glow in 4-3, a furnace-lit night in 4-4, the eruption in 4-5
- [ ] Lava glows and moves; smoke and steam rise without hiding the shots
- [ ] Falling ash and embers look right, and embers are never mistaken for bullets
- [ ] Enemy and boss shots stay easy to see over lava and red skies
- [ ] The ten World 4 bosses look good in `bosses/`; claws, fists, wings and drills move
- [ ] Difficulty clearly goes up from 4-1 to 4-5; 4-5 is the hardest so far and still beatable
- [ ] 60 fps in the forge belt and the 4-5 final boss fight

## 🧑 Notes, references, sketches
- **Drafted by the agent at the reviewer's request (2026-10-25); open choices, defaults proposed:** the same as phase 8 (themes, no new enemy kinds, 5-minute levels, a softer start for each world, fight times with guns at level 3, boss designs as suggestions), plus:
  1. P10-R07 (contrast outline on shots) only in World 4. Alternative: on every world, which would change the look of the validated worlds.
  2. The difficulty numbers keep climbing; with no new enemy kinds, World 4 leans on denser mixes and faster bullets. The reviewer may prefer to cap the bullet factors around 1.3 for kids.
- World 5 is left free; a natural end for the game after the Caldera Throne would be the enemy's capital in the sky or in orbit.

---

## 🧑 Review feedback
> After the agent reports, write corrections here, then say **"Fix phase 10"**.
> The agent ticks each item when fixed.

- [ ] 

---

## 🤖 Implementation report
> Filled by the agent. Do not edit (comment in Review feedback instead).

### Questions / blockers
<!-- Ambiguities found before implementing. If non-empty, agent stops and waits. -->

### Plan
| Task | Requirement IDs |
|------|-----------------|
| | |

### Requirement traceability
| ID | Status (Done / Partial / Not done) | Code | Tests | Notes |
|----|-----------------------------------|------|-------|-------|
| P10-R01 | | | | |

### Gate results
```
make check output summary: lint ✔ / typecheck ✔ / tests N passed / coverage xx% / build ✔
```

### How to test manually
<!-- Steps, keys, debug toggles, URL. -->

### Deviations from spec
<!-- Anything done differently and why. Also logged in DECISIONS.md. -->

### Known limitations
-

### Suggestions for future phases
-
