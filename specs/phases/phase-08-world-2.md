# Phase 08 — World 2

> Fill the **Human** sections. Set **Status** to `Ready` when the agent may implement it.
> The agent fills the **Agent** sections and never edits the requirement sections.

**Status:** Ready  <!-- Draft | Ready -->
**Depends on:** Phase 7

---

## 🧑 Goal
World 2, **the Industrial Desert**, has five playable levels, 2-1 to 2-5, each about 5 minutes long. The five levels are cut from one long journey: it starts in the deep desert, where World 1 ended, and the desert slowly gives way to mines, oil fields, refineries and finally dense factories, with slow transitions along the levels. Each level has its own time of day: three day levels, then dusk, then night (reworked at the reviewer's request, 2026-10-27; was: the Frozen North, from a cold sea with drifting ice to snowy fjords, a tundra, a glacier and a polar city at night, with snow, a blizzard and an aurora). Each level has its own mini boss and final boss, ten new bosses in all. The levels get harder from 2-1 to 2-5, and World 2 as a whole is harder than World 1.

## 🧑 Requirements

> ID format `P08-Rxx`. Every requirement is **MUST** (no SHOULD / MAY).
> Write each requirement so it is testable. Add acceptance criteria when "done" isn't obvious.
> World 2 is built with the World 1 tools and rules: terrain sections, sea, clouds, props and roads (P04-R01..R07, P06-R05/R06 and the phase 6 review rules D-046), wave scripts and fillers (P06-R07, D-051), level end, player damage, bonuses and the HUD (phase 6), and the boss engine with everything added in its review (P07-R01..R10, D-053..D-063). Only what changes for World 2 is written here. Sizes are given relative to the medium player ship length (`L`). Numbers are listed in **Tunable values**.
> The time of day, clouds and weather (P08-R04, P08-R05) are game-agnostic engine features (outside `src/game/`); the World 2 levels, their looks and their bosses are data and models in `src/game/` (`01-engineering.md` §2.3).

### P08-R01 — World 2 in the level select  · MUST

The World 2 row of the level select grid shows `2-1` to `2-5`, all unlocked, like World 1 (P06-R01: levels are never locked by progress). Worlds 3 to 5 stay greyed out. After `2-5`, the "Level complete" overlay goes back to `level-select` with `2-5` highlighted; after `1-5`, it highlights `2-1`.

**Acceptance criteria**
- [ ] Given `level-select`, then the World 2 row shows exactly `2-1` to `2-5`, all unlocked, and each starts its level on the `game` screen.
- [ ] Given a fresh start (no cookie), then `2-5` can be confirmed straight away.
- [ ] Given `1-5` is completed, then `level-select` shows with `2-1` highlighted.
- [ ] Given a level of worlds 3 to 5, then it is still greyed out.

### P08-R02 — Duration  · MUST

Each World 2 level lasts **about 5 minutes** (vision: 5 minutes for the levels after World 1): its scroll time at the level's ground speed is 300 s ± 10 s. The boss fights add to the time played (P07-R06).

**Acceptance criteria**
- [ ] Unit test: for each World 2 level, length ÷ ground speed is between 290 s and 310 s.

### P08-R03 — Scenery progression across World 2  · MUST

> Reworked at the reviewer's request (2026-10-27): World 2 starts in the desert and ends in the factories, with slow transitions along the levels. It was: a cold sea with ice floes, fjords, a tundra, a glacier and a polar city.

The five levels are one journey cut into five pieces: from the deep desert where World 1 ended, the desert is slowly taken over by industry, mines first, then oil fields, refineries, an industrial belt and dense factories at the end. The changes are slow: the ground cover goes from sand to concrete in small steps, the ground blends over a longer stretch between sections than in World 1, and each new kind of building first shows up mixed with the ones before it before it takes over. Each level begins on the same kind of ground the previous one ended on (as in P06-R05). There is no sea in World 2.

| Level | Name | Land | Habitations |
|-------|------|------|-------------|
| 2-1 | Sand sea | Open sand to the end: an oasis edge, great dunes, a sea of sand, then rocky desert. | Oasis homes and caravan outposts (water towers, solar farms, antennas), then desert outposts; the first mine headframes in the last 30 s. |
| 2-2 | Mining mesas | Rocky desert, mesas and a canyon, the sand trodden around the mines. | Mines and their outposts, a mining town with streets, then the first oil pumpjacks and storage tanks at the end. |
| 2-3 | Oil fields | Flat sand and rock, more and more of it paved. | Oil fields (pumpjacks, tanks), a company town, refineries and tank farms, the first factories at the end. |
| 2-4 | Industrial belt | Mostly paved ground, a little sand left between the plots. | Industrial outskirts, workers' suburbs, warehouses and container yards with streets, a power plant (cooling towers), then a factory district. |
| 2-5 | Factory district | Paved to the end. | Foundries and factories along streets, yards, then dense heavy industry, every block filled with plants and works at the end. |

The share of the ground covered by sand goes down from 2-1 to 2-5 and the paved share goes up; the number of props and of buildings goes up from 2-1 to 2-5, and in each level the second half has more props than the first.

**Acceptance criteria**
- [ ] Unit test: no World 2 level has a sea or a shore.
- [ ] Unit test: sand covers more of the ground than pavement in 2-1 and 2-2, pavement more than sand in 2-4 and 2-5, and the sand share goes down strictly from 2-1 to 2-5 while the paved share goes up.
- [ ] Unit test: the industrial and heavy-industry groups are not in 2-1; 2-5 ends on heavy industry only.
- [ ] Unit test (fixed seed): the number of props and the number of buildings go up from 2-1 to 2-5, and each level's second half has more props than its first.
- [ ] Unit test: two levels in a row: the next one starts with the same relief, ground cover and building groups as the previous one ended with; the World 2 sections blend over a longer stretch than the World 1 ones.
- [ ] Manual visual validation: desert, mines, oil fields, refineries and factories can be told apart, the changes are slow, and each level begins where the previous one ended.

### P08-R04 — Level look: time of day and clouds  · MUST

Each level has a **look** set in its data (as the World 1 looks already do in code): the time of day and the cloud cover. This phase makes it a documented part of every level, with these parameters:
- **time of day**: one of `dawn`, `morning`, `midday`, `afternoon`, `dusk`, `night`. It sets the sun's height and direction, the colour and strength of the sunlight, the sky and haze colours and the ambient light. At `night` the sun is replaced by a dim, cold moonlight;
- **cloud cover**: how much of each of the two cloud layers is covered (0 = clear sky, 1 = overcast), and the cloud colour, which follows the time of day (pink-orange at dawn and dusk, white at midday, dark grey under a storm, blue-grey at night);
- **haze**: how far the fog starts and ends (closer in a blizzard);
- **ground lights**: how strong the window, street and car lights are (off in daytime, on at dusk and night; the props and cars already have them, D-030);
- **look change**: a level may go from one look to another over a stretch of its length (for example dusk to night), blending every parameter smoothly. The blend follows the level's distance, so a debug jump (P06-R09) shows the right look.

Whatever the look, the game must stay readable: the player ship, enemies, shots, bonuses and HUD stand out from the ground as clearly as in the World 1 levels. At night the ground is dark but its shapes can still be seen (moonlight and ground lights), and the player ship and enemies get enough light to show their shape and colours.

**Acceptance criteria**
- [ ] Given each World 2 level, then its look sets the time of day and the cover of both cloud layers listed in the table of P08-R06 (unit test on the data).
- [ ] Given a level whose look changes from A to B between distances d1 and d2, then at d1 the look is A, at d2 it is B, and halfway every parameter is halfway (unit test in the engine).
- [ ] Given `?level=2-5&t=<a time after the change>`, then the level starts with the look of that distance, without a jump.
- [ ] Manual visual validation: each time of day reads at once (dawn, overcast midday, blizzard, night with aurora), and the player ship, enemy shots and bonuses stay clearly visible in every level, night included.

### P08-R05 — Weather: snow  · MUST

A level's look may have **weather**, with a kind and a strength from 0 (none) to 1 (heaviest). This phase adds the first kind, **snow**:
- snowflakes fall across the whole playfield, drifting slightly, at different depths between the clouds and the ground, and scroll with the ground;
- the strength sets how many flakes there are and how close the haze comes; at 1 (blizzard) the flakes are dense and streak sideways, but the flakes and the haze never hide the player ship, the enemies on screen, their shots or the bonuses: flakes are drawn behind them and stay faint;
- weather is only a look: it never changes how anything moves, shoots or takes damage;
- weather can also be part of a look change (P08-R04), so snow can start, stop or grow into a blizzard over a level.

The engine supports weather kinds as data, so the next worlds can add rain and falling ash without changing how levels use weather.

**Acceptance criteria**
- [ ] Given a look with snow of strength 0, then no flake is drawn; with strength 1, the most flakes allowed by **Tunable values** are drawn.
- [ ] Given the same level played with and without its weather (debug option `weather=0`), then the waves, enemy paths, shots and damage are the same (unit test: weather is not an input of the simulation).
- [ ] Manual visual validation: snow looks soft and falls with depth; in the 2-4 blizzard, enemy shots and bonuses are still easy to see.
- [ ] 60 FPS (ENG-101) during the 2-4 blizzard with the most enemies on screen.

### P08-R06 — Look of each World 2 level  · MUST

> Reworked at the reviewer's request (2026-10-27): a different time of day for each level, as in World 1 (P06-R10): three day levels, then dusk, then night. The time of day does not change within a level. No snow and no aurora any more (they belonged to the Frozen North). It was: dawn, morning, overcast midday with snow, an afternoon blizzard, dusk turning to night with an aurora.

| Level | Time of day | Clouds (low / high cover) | Weather | Notes |
|-------|-------------|---------------------------|---------|-------|
| 2-1 | morning | 0.15 / 0.1 | none | A clear desert morning, warm light, long shadows of the dunes. |
| 2-2 | midday | 0.2 / 0.15 | none | A high, hard sun over the mesas and the mines. |
| 2-3 | afternoon | 0.25 / 0.2 | none | Golden light over the oil fields; the first smoke greys the clouds a little. |
| 2-4 | dusk | 0.35 / 0.25, greyed by smog | none | A low sun through the smog over the industrial belt; the window, street and car lights come on. |
| 2-5 | night | 0.4 / 0.3, greyed by smog | none | Night over the factories, lit by their windows, neon, streets and cars; moonlight shows the ground's shapes. |

**Acceptance criteria**
- [ ] Unit test: each World 2 level's look data matches this table (time of day, cloud cover, no weather, no change within the level).
- [ ] Manual visual validation of each level against the table; the ships, shots and bonuses stay easy to see at dusk and at night.

### P08-R07 — Desert and industrial ground and props  · MUST

> Reworked at the reviewer's request (2026-10-27): World 2's ground is World 1's desert (P06-R06) slowly covered by the concrete and asphalt of the industry (the existing `paved` cover), with dark industrial roads. Its buildings are the World 1 desert homes and outposts, the Level Zero industrial buildings and the industrial buildings made of parts (P04, D-025), plus one new prop: an **oil pumpjack** (a nodding-donkey oil pump on a concrete pad, its walking beam and horse head, a small motor house and a warning light), as light in polygons as the existing props (D-031) and matte (D-024). The frozen ground and props below were built for the first version of World 2; their models stay in the game (`bosses/` and the props tests) but no World 2 level uses them any more.

Original requirement (2026-10-25), kept for the record — New generated ground and props for World 2 (GD-60, all made in code), as light in polygons as the existing ones (D-031) and matte (D-024):
- **Ground:** snow (bright, with a faint blue shade in the shadows), snow-covered rock that shows dark rock on steep slopes, glacier ice (blue-white, with crevasses as dark cuts made with the heightmap tools), and frozen lakes (flat, shiny ice with crack lines and a snowy edge).
- **Sea:** a dark, cold sea colour, with **ice floes** (flat white plates of different sizes) and **icebergs** (tall white-blue blocks) floating on it. They scroll with the ground and drift very slowly.
- **Vegetation:** snow-covered pines (dark green under white caps), bare frosted trees, and snowy bushes.
- **Habitations:** futuristic northern homes (steep-roofed, timber-and-metal chalets with neon trims and snow on the roofs), heated domes, lighthouses, radar domes, antennas, wind turbines, a pipeline on stilts, mining equipment (drill towers, conveyors, ore silos, cranes), and polar city towers. They follow the road rules of World 1 (D-046: no crossing roads, lone buildings and hamlets); the roads are snowy, with darker wheel tracks.

**Acceptance criteria**
- [ ] Manual visual validation: the sand, the paved industrial ground, the pumpjacks, refineries and factories read clearly from the playfield camera, and the slow change from desert to factories shows.
- [ ] Unit test: the pumpjack stays under the triangle budget in **Tunable values** and fits its footprint; the World 2 props use the desert, oil and industrial buildings and no frozen prop.

### P08-R08 — Enemy waves  · MUST

Each World 2 level has a wave script in `src/game/` (P06-R07), with fillers in the lulls (D-051). World 2 uses the eleven phase 5 enemy kinds; every kind can appear from 2-1 on, and each level puts weight on some of them:

| Level | Enemy kinds that lead the waves |
|-------|--------------------------------|
| 2-1 | Gnat, Hornet, Scout, Strafer, Weaver (low over the sea) |
| 2-2 | the 2-1 kinds plus Splitter, Lancer (along the fjords) |
| 2-3 | every kind, with Carrier and Spinner groups over the tundra |
| 2-4 | every kind, with Rocketeer and Bulwark in the blizzard |
| 2-5 | every kind, the heaviest mixes (Bulwark and Carrier together) |

**Acceptance criteria**
- [ ] Unit test: each World 2 wave script only uses the kinds listed for its level, and 2-3 to 2-5 use all eleven.
- [ ] Unit test: the waves are deterministic (same distances, same enemies, twice).

### P08-R09 — Increasing difficulty  · MUST

As in World 1 (P06-R08), each level is harder than the one before it, and World 2 continues where World 1 ended:
- from 2-1 to 2-5, these go up strictly: enemies spawned per minute of scroll, total enemy HP per minute, and the highest number of enemies on screen at the same time;
- the enemy bullet speed and fire rate factors never go down from 2-1 to 2-5;
- in each level, the second half has more total enemy HP than the first half;
- **across worlds:** 2-1 is at least as hard as 1-3 and 2-5 is harder than 1-5, on enemies per minute, HP per minute and the bullet speed and fire rate factors. 2-1 may be easier than 1-5, so a new world starts with a short breather.

**Acceptance criteria**
- [ ] Unit test: the strict increases from 2-1 to 2-5 above.
- [ ] Unit test: 2-1 ≥ 1-3 and 2-5 > 1-5 on the measures above.
- [ ] Unit test: in each World 2 level, the second half has more enemy HP than the first.
- [ ] Manual validation: 2-1 feels close to the middle of World 1, 2-5 clearly harder than 1-5.

### P08-R10 — The ten World 2 bosses  · MUST

Each World 2 level has its own mini boss (at half the level's length) and final boss (at its end), as in P07-R05 and P07-R06, with their own code-generated models in the World 2 theme (dark metal with neon, GD-61, plus frost, ice and snow details). The table gives each one's look and parts; the stage patterns (P07-R04) are designed by the agent and listed in the implementation report. Bosses with moving limbs use the limb tools of D-061.

| Level | Kind | Name | Look | Destroyable parts (weapons) | Fight ground speed |
|-------|------|------|------|-----------------------------|--------------------|
| 2-1 | Mini | Floe Breaker | An icebreaker hovership (3 L) with a sharp armoured bow, cyan neon | 2 side harpoon guns (aimed bursts), shield the core. Core: rings | ×0.5 |
| 2-1 | Final | Narwhal | A long flying submarine (5 L) with a spiral horn, teal neon along its back | 1 horn lance (warning line + laser), 2 torpedo tubes (homing missiles), 2 ballast pods (fans); the ballast pods shield the core. Core: spirals | ×1.5 (chase over the ice floes) |
| 2-2 | Mini | Fjord Lynx | A fast, low gunship (3 L) with two forward paws and tufted antennas, white and cyan neon | 2 paw cannons (aimed spreads), 1 radar mast (no weapon; while it stands, every other weapon aims at the player; once it is gone they fire in preset directions), shield the core. Core: fans | ×0.6 |
| 2-2 | Final | Harbour Kraken | A cargo crane-ship (5 L) with four crane arms swinging at the shoulder and elbow, orange neon | 4 crane arms, each with a grab cannon (aimed bursts), shield the core; 1 container bay (launches Gnat groups). Core: laser | ×0 (the ground stops over the harbour) |
| 2-3 | Mini | Snow Owl | A wide-winged recon drone (3 L), white neon, a big round sensor eye | 2 wing radar pods (fans), shield the core; 1 sensor eye (warning line + laser). Core: rings | ×0.5 |
| 2-3 | Final | Aurora Station | A flying research station (5 L) with a slowly turning dish, green and violet neon | 2 dish emitters (laser sweeps), 2 cryo cannons (slow big bullets that burst into small rings), shield the core; 1 drone hangar (launches Hornets). Core: spirals | ×0.4 |
| 2-4 | Mini | Avalanche | A heavy drilling machine (3.5 L) with two drill arms, yellow neon | 2 drill arms (moving limbs; aimed bursts), shield the core; 1 rock hopper (slow big bullets dropped in lines). Core: fans | ×1.4 (chase down the glacier) |
| 2-4 | Final | Glacier Colossus | A giant mining ship (5.5 L) with glowing heat vents, red-orange neon | 2 cutter lasers, 2 ore cannons (fans of big bullets), 1 missile pod, 1 heat sink (no weapon); the heat sink and the ore cannons shield the core | ×0.3 |
| 2-5 | Mini | Ice Queen | A slender crystal interceptor (3.5 L), pale blue and violet neon | 3 crystal shards on a turning ring (spirals), shield the core. Core: aimed bursts | ×0.6 |
| 2-5 | Final | Boreal Citadel | The polar city's flying fortress (6 L), aurora green and violet neon over its hull | 2 aurora cannons (lasers), 2 missile batteries, 2 dome generators (no weapon, shield the core). Core: every attack kind | ×0.25 |

Mini bosses have 2 or 3 destroyable parts and final bosses 4 to 6 (P07-R01). Within World 2, at least one fight stops the ground (×0) and at least one is a chase (> ×1).

**Acceptance criteria**
- [ ] Unit test: each World 2 level has exactly one mini boss and one final boss from this table, with 2–3 and 4–6 destroyable parts.
- [ ] Unit test: the Fjord Lynx's weapons aim at the player while its radar mast stands, and fire in preset directions once it is destroyed.
- [ ] Unit test: in a long simulated fight, every boss's hit circles stay inside the ship's reach (D-048).
- [ ] Manual visual validation of the ten models in `bosses/` (model and wireframe views).

### P08-R11 — Boss difficulty in World 2  · MUST

As in P07-R10:
- the full HP of the mini bosses goes up strictly from 2-1 to 2-5, and so does that of the final bosses; each final boss has more full HP than its level's mini boss;
- each World 2 boss has more full HP than the World 1 boss of the same level and kind (2-k mini > 1-k mini, 2-k final > 1-k final);
- the boss bullets use the level's bullet speed and fire rate factors;
- the fight times (simulation, balanced ship, guns at level 3, always firing at the boss) are within the ranges of **Tunable values**.

**Acceptance criteria**
- [ ] Unit test: the HP orderings above.
- [ ] Unit test (simulation, as in P07-R10): fight times within the ranges.
- [ ] Manual validation: the World 2 bosses feel harder than the World 1 ones, and the 2-5 ones clearly the hardest so far.

### P08-R12 — Debug options and the `bosses/` page  · MUST

- The debug URL options of the `game` screen (P06-R09, P07-R09) accept every World 2 level (`?level=2-4&t=150`, `?level=2-5&boss=final`).
- A `weather=0` option turns the weather off, and `look=<time of day>` forces a time of day, to compare looks (debug only).
- The `bosses/` page lists the World 2 bosses after the World 1 ones (grouped by world), each fighting over the scenery and look of its level.

**Acceptance criteria**
- [ ] Given `?level=2-4&t=150`, then 2-4 starts at 2:30 (its blizzard until the 2026-10-27 rework).
- [ ] Given `?level=2-3&weather=0`, then 2-3 shows no weather (it has none since the 2026-10-27 rework; the option is still tested on the worlds that have weather).
- [ ] Given `bosses/`, then every World 1 and World 2 boss can be picked without console errors.
- [ ] Given no debug option, then the look and weather are the level's own.

## 🧑 Tunable values
| Name | Value | Notes |
|------|-------|-------|
| level_duration | 300 s ± 10 s | P08-R02 |
| ground_speed 2-1 / 2-2 / 2-3 / 2-4 / 2-5 | 70 / 65 / 60 / 55 / 60 px/s | GD-01 |
| sea_share 2-1 → 2-5 | 0 % (was ≥ 80 % / ≤ 50 % / 0 / 0 / 0 before the 2026-10-27 rework) | P08-R03 |
| time_of_day 2-1 / 2-2 / 2-3 / 2-4 / 2-5 | morning / midday / afternoon / dusk / night | P08-R06 (reviewer, 2026-10-27) |
| section_transition | longer than World 1's (420 units) | P08-R03, slow transitions (reviewer, 2026-10-27) |
| peak_on_screen 2-1 / 2-2 / 2-3 / 2-4 / 2-5 | 10 / 11 / 13 / 15 / 17 | P08-R09; the agent may adjust while balancing, keeping the order |
| enemy_bullet_speed_factor 2-1 → 2-5 | 0.9 / 0.95 / 1.0 / 1.1 / 1.15 | P08-R09 |
| enemy_fire_rate_factor 2-1 → 2-5 | 0.9 / 0.95 / 1.0 / 1.1 / 1.15 | P08-R09 |
| look_change_length | the stretch given in P08-R06 (2-5: first third) | P08-R04 |
| snow_flakes_max | 1 500 (at strength 1) | P08-R05; the agent may lower it for ENG-101 |
| blizzard_fog | fog end at 55 % of the clear-weather distance | P08-R05, P08-R06 |
| mini_fight_time 2-1 → 2-5 | 30–40 s → 45–55 s | P08-R11, balanced ship, guns level 3, always on target |
| final_fight_time 2-1 → 2-5 | 60–80 s → 100–130 s | P08-R11, same |
| boss_triangles | ≤ 6 000 per boss | as in phase 7 |
| prop_triangles | within the range of the phase 6 props | P08-R07, D-031 |

## 🧑 Out of scope for this phase
- Worlds 3 to 5 and their weather kinds (rain, lightning, falling ash).
- New regular enemy kinds (bosses may launch the phase 5 ones).
- Gameplay effects of the weather or the ground (slippery controls, wind, cold): weather is only a look.
- Bombs, extra lives, score, high score, pause, music and sound effects (GD-20, GD-32, GD-50, GD-51, GD-70, GD-71).
- Changing the World 1 looks: they only move to the new look parameters (P08-R04) if needed, keeping how they look.

## 🧑 Engineering additions for this phase
- The look parameters, the look change and the weather (P08-R04, P08-R05) are game-agnostic engine code, unit tested; the World 2 levels, looks, props, wave scripts and bosses are data and views in `src/game/`.
- The World 1 levels keep passing their phase 6 and 7 tests unchanged.
- An e2e test confirms each World 2 level from the menu and checks it starts without console errors.
- An e2e test opens `?level=2-1&boss=final`, destroys the boss with K and the debug fire, and reaches the "Level complete" overlay.
- 60 FPS (ENG-101) during the 2-4 blizzard with the most enemies on screen, and during the 2-5 final boss fight at night over the city.

## 🧑 Manual validation checklist
- [ ] Runs on GitHub Pages / `make dev` without console errors
- [ ] `2-1` to `2-5` can be picked in the level select; worlds 3 to 5 stay locked
- [ ] Each level lasts about 5 minutes of scroll, plus its two boss fights
- [ ] Desert, mines, oil fields, refineries and factories across the five levels, changing slowly; each level begins where the previous one ended (reworked 2026-10-27)
- [ ] Each level has its own time of day: morning, midday, afternoon, dusk, night (reworked 2026-10-27)
- [ ] The night level stays readable: ship, enemies, shots and bonuses clearly visible
- [ ] The ten World 2 bosses look good in `bosses/` and each part changes the attack
- [ ] Difficulty clearly goes up from 2-1 to 2-5; 2-1 feels like a fresh start, not a wall
- [ ] 60 fps in the busiest part of 2-5 and in the 2-5 final boss fight at night over the factories

## 🧑 Notes, references, sketches
- **Drafted by the agent at the reviewer's request (2026-10-25); open choices for the reviewer, defaults proposed:**
  1. World themes: World 2 the Frozen North, World 3 the Jungle (phase 9), World 4 the Volcanic Lands (phase 10). World 4 is the last world (World 5 dropped by the reviewer, 2026-10-26).
  2. No new regular enemy kinds in Worlds 2 to 4; the eleven phase 5 kinds come in harder mixes. Alternative: two or three new kinds per world, in their own phase or in each world phase.
  3. Levels last 5 minutes of scroll from World 2 on (vision); the boss fights add to it.
  4. A new world starts a little easier than the end of the previous one (2-1 ≥ 1-3, not ≥ 1-5).
  5. Boss fight times assume guns at level 3, as in World 1, so the numbers can be compared.
  6. The time of day, clouds and weather tools are built in this phase and reused by Worlds 3 and 4.
  7. Boss names, looks and parts are suggestions; the stage patterns are left to the agent and reported.
- Photosensitivity: no flashing look effect in World 2 (the lightning comes in World 3 with its own limits).

---

## 🧑 Review feedback
> After the agent reports, write corrections here, then say **"Fix phase 08"**.
> The agent ticks each item when fixed.

- [x] (reviewer, in chat, 2026-10-27) Rework World 2: start in the desert and end in factories, with slow transitions along the levels; like World 1, a different time of day for each level (3 days, 1 night). — Done (D-110): P08-R03, R06 and R07 amended. World 2 is now the Industrial Desert: 2-1 Sand sea, 2-2 Mining mesas, 2-3 Oil fields, 2-4 Industrial belt, 2-5 Factory district, one gradient from World 1's sand to dense factories. Slow transitions: sections blend over 900 units (World 1: 420), the sand steps down to concrete a little in each section, and each new building group comes in mixed with the previous one; each level starts on the section the previous one ended on. Time of day: morning, midday, afternoon, dusk, night, fixed within each level; no snow, no aurora. New prop: an oil pumpjack. Props per level 2 982 / 6 548 / 9 087 / 11 182 / 12 049, each second half fuller than the first. Bosses and waves unchanged (their frost names now fly over the desert).
- [x] (reviewer, in chat, 2026-10-25) Make the weapons level persistent when the user finished a level. — Done (D-071): when a level is completed, the weapon in use and the level of each weapon are saved (`<game id>_weapons` in the cookie storage, `app/saved-weapons.ts`), and every level started afterwards starts with them, after a reload too (`LevelRunOptions.startWeapons`). A game over saves nothing: the next attempt starts with the weapons of the last level completed; Continue still restarts with the checkpoint's weapons (P07-R08). Unit tests: `saved-weapons.test.ts`, `game-session.test.ts`, `level-run-bosses.test.ts`.
- [x] (reviewer, in chat, 2026-10-25) Make the enemy bullets easier to see, more contrast, without making them bigger; then reduce the dark ring around them; then remove the dark ring and make them a colourful blob of energy with fading borders; then make the centre brighter and pulsating. — Done (D-069 revised): no dark backing any more; each bullet is a disc of the same size, a white-hot core going over to its colour, held to its edge while its opacity fades out (`ENEMY_LOOK.bullets.fade`), drawn blended instead of added (`blendedTemplate`), so its colour shows over bright snow instead of washing out to white. A white-hot glow is added over its centre (0.6 of its radius), swelling and shrinking by 30 % 2.5 times a second from when it is fired (`ENEMY_LOOK.bullets.core`; unit test in `enemy-renderers.test.ts`).
- [x] (reviewer, in chat, 2026-10-25) Add more diversity to the enemy laser colours; a laser may follow the player (on a rotating turret) but once locked it keeps its direction. — Done (D-072): a boss's lasers are drawn in its neon colour (`withOwnLasers` gives them the boss's kind as style; `EnemyLasers` colours each style, `laserPalette`), the Lancer's stay red: the ten bosses that fire lasers each have their own (yellow, green, red, violet, teal, orange, ice white…; the Aurora Station's and the Boreal Citadel's greens are close). The warning line follows its owner's heading; when the beam starts firing it locks that heading and keeps it (a sweep turns from it), still leaving from the emitter (`EnemyShots`). Unit tests: `enemy-shots.test.ts`, `boss-lasers.test.ts`, `enemy-renderers.test.ts`.
- [x] (reviewer, in chat, 2026-10-25) The Boreal Citadel's laser still rotates while firing: fix all the bosses; put the lasers on rotating turrets if needed, but keep the laser straight once it starts firing. — Done (D-073): no laser turns while it fires any more. The sweeping lasers are gone from the engine (`EnemyLaserSpec.sweepDeg` removed); a laser can be on its piece's turret instead (`Guns.turretLaser`): the turret aims at the player before and during the warning line, then holds still while the beam fires, the beam keeping that heading (D-072). On turrets now: the Boreal Citadel's aurora cannons (each turns on a turntable), the Aurora Station's dish emitters (the dish turns on its pylon) and the Glacier Colossus's cutters (each turns on a mount); the Harbour Kraken's and the Citadel's core lasers fire straight down. Unit tests: `boss-pattern.test.ts` (a laser turret aims, follows during the warning, holds while firing), `muzzles.test.ts` (the turned models draw the laser tips where the beams leave).
- [x] (reviewer, in chat, 2026-10-25) Add a flare effect at the base of the enemy lasers, like the player's. — Done: the small emitter glow is replaced by the player's laser flare (`ENEMY_LOOK.laser.flare`, as `SHOT_LOOK.laser.muzzle`): round and smooth (24 sides, a soft falloff from white-hot to the laser's colour), sized by the beam's width, stretched 1.3× along the beam and pulsing at 9 / 17 Hz (`EnemyLasers`; unit test in `enemy-renderers.test.ts`).
- [x] (reviewer, in chat, 2026-10-25, screenshot of the Snow Owl) The laser looks like it fires from under the round eye. — Done: enemy laser warning lines, beams and flares are drawn over the models (`additiveTemplate(…, onTop)`: no depth test), so a beam leaving a lens set into a raised hull is seen leaving the lens instead of from under the hull around it (unit test in `enemy-renderers.test.ts`; checked in screenshots of the Snow Owl).
- [x] (reviewer, in chat, 2026-10-25) Lower the laser turrets' homing turn speed: it is impossible to escape the laser. — Done: a laser turret aims at the player at the turrets' 150°/s before its laser fires, but follows the player at only 20°/s while the warning line shows (`BossTurretSpec.laserTurnRateDeg`, `BOSS_TIMING.laserTurnDeg`): about half as fast as the ship crosses its aim from 300 px away, so the beam can be outrun (unit test in `boss-pattern.test.ts`).
- [x] (reviewer, in chat, 2026-10-25) Rework the enemy bullet so it feels like a ball of energy / plasma. — Done (D-074): each bullet is, back to front, a faint flickering aura, a deep-coloured blended body darker at its rim, two curled swirls of brighter plasma (`buildSwirl`) spinning opposite ways, and a smaller pulsing core (`ENEMY_LOOK.bullets`). Each layer of each colour is one mesh of thin instances, so all bullets cost at most 30 draw calls however many fly. Unit tests: `enemy-renderers.test.ts` (positions, aura, opposite spins, pulsing core), `shot-geometry.test.ts` (`buildSwirl`); checked in zoomed screenshots of a boss fight.
- [ ] 

---

## 🤖 Implementation report
> Filled by the agent. Do not edit (comment in Review feedback instead).

### Questions / blockers
None. The spec was implemented as written; the few interpretations are listed under Deviations.

### Plan
| Task | Requirement IDs |
|------|-----------------|
| Engine atmosphere: time-of-day presets, cloud cover, haze, ground lights, look changes along the distance (`core/scenery/atmosphere.ts`, `sky-look.ts`, `config/time-of-day.ts`, `render/scenery/sky-layers.ts`) | P08-R04 |
| Engine weather as data (`config/weather.ts`), GPU snow particles, aurora sheet | P08-R05, R06 |
| Frozen ground tools: lakes, crevasses, floating ice with drift, prop lines, cracked textures | P08-R03, R07 |
| World 2 props (22 hand-made models, 3 families of 8) | P08-R07 |
| World 2 scenery, looks, waves, difficulty, level assembly and registration | P08-R01..R03, R06, R08, R09 |
| Boss engine additions (`needs` / `after` volleys, lasers on turrets, bursting bullets); ten bosses (designs + models) and their tuning | P08-R10, R11 |
| Debug options `weather=0`, `look=`; bosses page grouped by world | P08-R12 |
| Readability: enemy bullets as blended blobs of energy (D-069); screenshots of every level under software WebGL | P08-R04, R05 |
| Unit and e2e tests, docs, decisions | all |

### Requirement traceability
| ID | Status (Done / Partial / Not done) | Code | Tests | Notes |
|----|-----------------------------------|------|-------|-------|
| P08-R01 | Done | `game/sim/world-2.ts`, `game/sim/levels.ts` (`GAME_LEVELS`) | `world-2.test.ts`, `game-definition.test.ts`, e2e `world-2.spec.ts` | 1-5 → 2-1 and 2-5 → 2-5 follow from the level grid order |
| P08-R02 | Done | `game/config/world-2/scenery-*.ts` (300 s each) | `world-2.test.ts`, e2e | speeds 70 / 65 / 60 / 55 / 60 |
| P08-R03 | Done | `world-2/scenery.ts` (reworked, D-110; was `scenery-coast.ts`, `scenery-inland.ts`) | `world-2.test.ts` (no sea, sand → pavement, groups, props and halves, continuity, transitions) | Reworked in review (D-110): desert → factories. Sand 0.89 / 0.67 / 0.39 / 0.17 / 0.05, paved 0.005 / 0.14 / 0.40 / 0.67 / 0.89; props 2 982 / 6 548 / 9 087 / 11 182 / 12 049; buildings 1 553 / 4 883 / 8 570 / 11 039 / 12 049. Manual check needed |
| P08-R04 | Done | `core/scenery/atmosphere.ts`, `sky-look.ts`, `config/time-of-day.ts`, `render/scenery/sky-layers.ts`, `atmosphere-of.ts` | `atmosphere.test.ts`, `sky-look.test.ts`, `sky-layers.test.ts`, e2e | D-064 |
| P08-R05 | Done | `config/weather.ts`, `render/scenery/weather-layer.ts`, `weather-material.visual.ts` | `sky-look.test.ts`, `sky-layers.test.ts`, `game-play.test.ts` (weather not an input), e2e | D-065; 60 FPS: manual |
| P08-R06 | Done | `game/config/world-2/looks.ts` | `world-2.test.ts`, e2e `world-2.spec.ts` | Reworked in review (D-110): morning, midday, afternoon, dusk, night; no weather, no change within a level. Manual check needed |
| P08-R07 | Done | `world-2/props.ts`, `world-2/looks.ts`, `game/view/props/oil-props.ts` (pumpjack); `polar-*.ts` kept, unused | `prop-models.test.ts` | Reworked in review (D-110): desert, oil and industrial props; D-066 for the frozen ones |
| P08-R08 | Done | `game/config/world-2/waves.ts` | `world-2.test.ts` | D-067 |
| P08-R09 | Done | `waves.ts`, `world-2/difficulty.ts` | `world-2.test.ts` | numbers below |
| P08-R10 | Done | `game/config/bosses/world-2/*`, `game/view/bosses/world-2/*`, `core/systems/boss-pattern.ts`, `enemy-shots.ts` | `bosses-world-2.test.ts`, `muzzles.test.ts`, `boss-models.test.ts`, e2e | D-068; patterns below |
| P08-R11 | Done | the ten designs' health | `bosses-world-2.test.ts` | fight times below |
| P08-R12 | Done | `app/debug-options.ts`, `game-session.ts`, `start-boss-viewer.ts`, `ui/enemy-viewer-panel.ts` | `debug-options.test.ts`, `sky-layers.test.ts`, e2e `world-2.spec.ts`, `bosses.spec.ts` | D-070 |

**Balance (P08-R09)**, measured without shooting (seed 606), per minute of scroll: enemies 116.8 / 120.4 / 121.4 / 172.0 / 233.4, HP 2 466 / 3 384 / 3 666 / 6 016 / 7 360, peak on screen 22 / 23 / 36 / 37 / 51 for 2-1 … 2-5 (World 1 now: 1-3 104.8 enemies and 2 235 HP a minute, 1-5 130.3 and 4 150). Every second half carries more HP. As in World 1 (D-051), the peaks are far above the tunable 10 … 17, in the same order.

**Bosses (P08-R10, R11).** Fight times with the D-055 bot (guns level 3, always on target), mini / final: 2-1 32.8 / 66.7 s, 2-2 40.3 / 86.7 s, 2-3 41.1 / 97.0 s, 2-4 45.4 / 108.0 s, 2-5 51.3 / 113.6 s. Full health: mini 2 720 / 2 880 / 3 550 / 3 800 / 4 200, final 6 500 / 7 000 / 8 600 / 13 000 / 17 500 (World 1: 2 200 … 3 910 and 5 770 … 15 780). Models: 2 244–4 172 triangles, within 7 % of their sizes. Stage patterns (parts fire the same in every stage; the core changes each stage, its last stage a new ring or spiral):
- **Floe Breaker** (2-1 mini, ×0.5): two harpoon turrets fire 3-shot bursts; core fan 3 → aimed spread 3 → ring of 10 + fan 5. Angry: curtain.
- **Narwhal** (2-1 final, ×1.5 chase): horn lance laser, two torpedo tubes (2 homing missiles), two ballast pods (fans crossing, they shield the core); core aimed 1 → aimed 3 → burst 4 → fan 5 → fan 7 + aimed → two counter-turning spirals. Angry: vortex.
- **Fjord Lynx** (2-2 mini, ×0.6): while its radar mast stands, the paw turrets fire aimed spreads and the core aimed shots (1 → spread 3 → burst 4); once the mast is gone, they all fire preset fans instead (paws ±18°, core 3 → 5); last stage fan 7 + spiral 12. Angry: vortex.
- **Harbour Kraken** (2-2 final, ×0): four crane arms swinging at shoulder and elbow, each with a grab cannon firing aimed bursts; a container bay launching 3 Gnats every 7 s; core laser → laser + aimed → laser + fan 5 → laser + spread 3 → laser + fan 7 → laser + spiral 14. Angry: vortex.
- **Snow Owl** (2-3 mini, ×0.5): two wing radar pods (fans crossing), a sensor eye (laser); core aimed 1 → spread 3 → burst 4 → ring 12 + aimed. Angry: flower.
- **Aurora Station** (2-3 final, ×0.4): two dish emitters (lasers on turrets: aimed at the player during the warning line, held still while firing), two cryo cannon turrets (slow shells bursting into rings of 8), a drone hangar launching Hornets; core aimed 1 → spread 3 → burst 4 → fan 5 → fan 7 + aimed → two spirals. Angry: spirals.
- **Avalanche** (2-4 mini, ×1.4 chase): two drill arms on joints (bursts), a rock hopper dropping lines of big slow rocks; core fan 3 → 5 → 7 → spiral 12 + fan 5. Angry: spirals.
- **Glacier Colossus** (2-4 final, ×0.3): two cutter lasers (on turrets, aimed as the Aurora Station's), two ore cannons (fans of big shells), a missile pod, a heat sink; core aimed 1 → spread 3 → burst 4 → ring 8 → fan 7 + burst → spiral 10 + aimed → two spirals. Angry: flower.
- **Ice Queen** (2-5 mini, ×0.6): three crystal shards on a turning ring firing spirals; core bursts 3 → 4 → 5 + spread → spiral 14 + burst. Angry: flower.
- **Boreal Citadel** (2-5 final, ×0.25): two aurora cannons (lasers on turrets, aimed as the Aurora Station's), two missile batteries, two dome generators shielding the core; core aimed spread → fan 5 → burst 4 → missiles + aimed → laser + fan 7 → ring 10 + burst → spiral 16 + laser + missiles + fan 5 (every attack kind). Angry: curtain + spirals.

### Gate results
```
Light verification (implementation): make typecheck ✔ · make build ✔ · make e2e ✔ (65 tests: a full run gave 62 passed / 3 failed — two phase 1 / 6 tests still expecting World 2 locked, and the new 2-4 test waiting on a time held by the mini boss, both fixed; the touch flow timed out under load — the menu-pointer, world-2 and bosses specs then re-run: 19 / 19 passed)
Lint, unit tests and coverage are deferred to /validate-phase (make check).

Full gate (validation, 2026-10-25): make check ✔ — lint ✔ · prettier ✔ · typecheck ✔ · 1084 unit tests ✔ · coverage 98.5 % statements, 88.04 % branches, 98.57 % functions, 99.26 % lines ✔ · build ✔ · 65 e2e ✔ (4.4 min).
Fixed on the way: three unit tests (World 2 storage tanks and lone antenna mast slightly over their footprints; the P06-R01 level test and Level Zero's prop list updated for World 2 unlocked and its own props), and e2e tests tied to the frame rate under software WebGL, failing on CI (D-075: the tests advance the level clock through the test API, entering a level gets the loading timeout, e2e builds draw a quarter of the pixels).
```

### How to test manually
- `make dev`, then Start → a ship → the level select: the World 2 row (`2-1` … `2-5`) is unlocked, worlds 3 to 5 stay locked. After 1-5's "Level complete", `2-1` is highlighted.
- Each level: `?level=2-1` … `?level=2-5` (with `&t=<seconds>`; F ×4, ← / → jump 10 s). Look for: 2-1 dawn over a dark sea with ice floes and icebergs, rocky islets, a harbour coast at the end; 2-2 morning fjords, light snow in the second half; 2-3 overcast tundra, snow falling, frozen lakes with cracks, a pipeline on stilts, radar domes and turbines; 2-4 afternoon glacier with crevasses and dark rock sides, mining outposts then a mining complex, the blizzard from 2:30 (`?level=2-4&t=150`), clearing near the end; 2-5 dusk turning to night over the first 100 s, the aurora's green and violet curtains at the top of the screen, the lit polar city.
- Debug: `&weather=0` (no snow, e.g. `?level=2-3&weather=0`), `&look=dawn|morning|midday|afternoon|dusk|night` (e.g. `?level=2-5&t=200&look=midday`), `&boss=mini|final` (K destroys the next part).
- Bosses: `bosses/` lists World 1 then World 2 under "World 1" / "World 2" headings; each boss comes in over its level's scenery and look; M / V show the model and wireframe.
- Weapons kept (review): pick up weapon bonuses in a level and finish it (`&boss=final` then K to destroy the final boss quickly), then start another one: it starts with the same weapon and levels, after a page reload too. Lose all lives instead: nothing new is kept.
- Readability: enemy bullets are now blobs of colour with a pulsing white-hot core and a fading border, the same size as before; check them over snow (2-3, 2-4 blizzard) and at night (2-5).
- 60 FPS: the 2-4 blizzard with the most enemies (`?level=2-4&t=230`) and the 2-5 final fight (`?level=2-5&boss=final`), with the F3 / debug FPS tile.

### Deviations from spec
- P08-R10, Aurora Station "2 dish emitters (laser sweeps)": at the reviewer's request no laser turns while it fires; the dish emitters aim their lasers from turrets instead (D-073).
- P08-R06, 2-4: "snow 0.5, growing to a blizzard in the second half": the blizzard grows over 2:05–2:30 so that the level is in a full blizzard from the middle on (P08-R12's acceptance test: `?level=2-4&t=150` starts in the blizzard); it clears to 0.3 over 4:30–4:52, before the final boss.
- P08-R05: flakes fill the air from the ground up to just under the flight altitude, so some are between the camera and the clouds (drawn over them); they are never drawn over the ships, shots or bonuses.
- P08-R10, Harbour Kraken: "the ground stops over the harbour": the final fight is at 2-2's end, which is inland (2-2 must end where 2-3 begins); the harbour is at 2-2's start.
- P08-R09 tunable `peak_on_screen` (10 … 17): measured 22 … 51, order kept (as World 1, D-051).
- The enemy bullets' new look (D-069) also shows in World 1.
- Balance and fight-time numbers were measured with throw-away simulation scripts (not the unit test runner), as the implement procedure forbids running unit tests before validation.

### Known limitations
- 60 FPS (ENG-101) could not be measured here: only software WebGL is available (it shows 10–27 FPS for every level, World 1 included). The polar city centre draws about 0.95 M triangles at its densest, like 1-5's city (D-027).
- Lint, unit tests and coverage have not been run (deferred to `/validate-phase`).
- Ice floes of one kind drift together (one mesh per kind). The weather buoy's light does not blink.
- The night look keeps the ships readable through a lit reflection gradient and a moon of 0.6; this is to be judged by eye.

### Suggestions for future phases
- Rain (World 3) and ash (World 4) are new entries in `config/weather.ts`; streaks along the fall direction for rain may want a `slant` parameter.
