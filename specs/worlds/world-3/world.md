# World 3 — The Industrial Towns

> **Area:** worlds · **Prefix:** `WLD-3` · **Related:** [3-1](3-1-canal-works.md), [3-2](3-2-docklands.md), [3-3](3-3-workers-quarter.md), [3-4](3-4-suburbs.md), [3-5](3-5-garden-villages.md), [World 2](../world-2/world.md), [World 4](../world-4/world.md), [level flow](../../gameplay/level-flow.md), [level select](../../ui/level-select.md), [terrain](../../graphics/terrain.md), [water](../../graphics/water.md), [sky and light](../../graphics/sky-and-light.md), [weather](../../graphics/weather.md), [roads](../../graphics/roads.md), [buildings](../../graphics/buildings.md), [enemies](../../enemies/common.md), [bosses](../../bosses/common.md), [music](../../audio/music.md)

World 3, **the Industrial Towns**, is the third world of the game: five levels, 3-1 to 3-5, of about
five minutes each. Together they are one journey from the great works World 2 ends on, through the
canal works and the docks, over the workers' quarters and their terraces, to suburbs and garden
villages of small houses. The changes are slow, the day goes on from a misty morning to a rainy
night, and every level has its own mini boss and final boss. World 3 is harder than World 2, and its
levels get harder from 3-1 to 3-5. It is no longer the Jungle it first was (reworked at the
reviewer's request, 2026-10-27, D-111): there is no rainforest, no ruin, no swamp and no sea.

This file holds what the five levels share. Each level file holds the level's own sections, look,
waves, difficulty and bosses. The engines they use (terrain, roads, buildings, sky, weather, waves,
bosses) are described in `graphics/`, `gameplay/` and `bosses/common.md`.

## Requirements

### WLD-3-01 — World 3 in the game · MUST

World 3 is the third of the game's four worlds. Its levels are, in this order: `3-1` Canal works,
`3-2` Docklands, `3-3` Workers' quarter, `3-4` Suburbs, `3-5` Garden villages. They fill the third row
of the level select, all unlocked; after `2-5` is completed the level select highlights `3-1`, and
after `3-5` it highlights `4-1` (the rules of the grid are in [level select](../../ui/level-select.md)).

**Acceptance criteria**
- Given the game's levels, then World 3 is the five levels `3-1` … `3-5` in this order, after `2-5` and before `4-1`.
- Given `level-select`, then its third row shows exactly `3-1` to `3-5`, all unlocked, each starting its level.
- Given `2-5` (or `3-5`) is completed, then `level-select` shows with `3-1` (or `4-1`) highlighted.

*Sources: P09-R01, P10-R01, D-111.*

### WLD-3-02 — Five-minute levels · MUST

Each World 3 level's scroll time, its length divided by its ground speed, is `level_duration`. The
lengths and speeds are in the level files.

**Acceptance criteria**
- Given each World 3 level, then its length ÷ its ground speed is between 290 s and 310 s.

*Sources: P09-R02.*

### WLD-3-03 — One journey, from the factories to the garden villages · MUST

The five levels follow one another as a single journey. Each has its theme, in this order:

| Level | Name | Ground | Buildings |
|-------|------|--------|-----------|
| 3-1 | Canal works | All concrete. | The great works 2-5 ended on, foundries, rail yards, the canal docks, factory yards, the first workshops. |
| 3-2 | Docklands | Concrete, the first patches of grass. | Warehouses on the docks, workshop streets, old mills, then the first workers' flats. |
| 3-3 | Workers' quarter | Concrete and grass about even by the end. | Small blocks of flats, terraced streets, a park, brick terraces, then the first houses. |
| 3-4 | Suburbs | Mostly grass and gardens. | Houses with gardens, a town park, leafy avenues, then the first garden villages. No industry. |
| 3-5 | Garden villages | Grass and gardens. | Small houses only, garden villages to the end. No industry, no tower. |

**Acceptance criteria**
- Manual visual validation: factories, docks, workers' quarter, suburbs and garden villages can be told apart across the five levels.

*Sources: P09-R03, D-111.*

### WLD-3-04 — Each level begins where the previous one ended · MUST

Each World 3 level begins on the very ground the previous level ended on: its first section is the
previous level's last section (same relief, cover, streets and building groups), shortened to 40 s.
3-1 begins on 2-5's last section, the great works filling every block (see
[2-5](../world-2/2-5-factory-district.md)). 3-5's last section is where World 4 begins (see
[WLD-4](../world-4/world.md)).

**Acceptance criteria**
- Given 3-2 … 3-5, then each one's first section is the previous level's last section, but for its length (40 s).
- Given 3-1, then its first section is 2-5's great works (relief, cover, streets, filled blocks), with World 3's heavy industry group.

*Sources: P09-R03, D-111.*

### WLD-3-05 — Slow transitions · MUST

The changes along World 3 are slow, as in World 2. Two sections blend over `section_transition`
(World 2's), and each new building group first comes in mixed with the one before it (heavy industry
with industrial, industrial with docks, workshops with industrial, workshops with workers' flats,
flats with residences, residences with garden villages) before it stands alone.

**Acceptance criteria**
- Given each World 3 level, then its sections blend over `section_transition`.
- Given each section that brings in a new building group, then the section before it, or the section itself, also has the group it replaces.
- Manual visual validation: no change of district is abrupt.

*Sources: P09-R03, D-111.*

### WLD-3-06 — Concrete gives way to grass · MUST

From 3-1 to 3-5, the share of paved ground (concrete) goes down and the share of grass and gardens
goes up, a little in each section. Averaged over a level, by its sections' lengths, the paved cover
and the grass cover are about the values of `paved_share` and `grass_share`: more concrete than
grass in 3-1 to 3-3, more grass than concrete in 3-4 and 3-5.

**Acceptance criteria**
- Given the five levels, then the mean paved cover goes down strictly from 3-1 to 3-5 and the mean grass cover goes up strictly.
- Given 3-1, 3-2 and 3-3, then their mean paved cover is above their mean grass cover; given 3-4 and 3-5, below it.

*Sources: P09-R03, D-111.*

### WLD-3-07 — From industry to small homes · MUST

The buildings of World 3 come from its building groups (see the table under **Tunable values** and
[buildings](../../graphics/buildings.md)): heavy industry, industrial, docks, workshops, workers'
flats, residences and garden villages. Where they stand:
- heavy industry (large foundries and plants) stands in 3-1 only;
- no residence and no garden village stands in 3-1;
- no industrial, dock or workshop group stands in 3-4 or 3-5;
- the workers' flats stop in 3-3: 3-4 and 3-5 have homes only;
- the last section of 3-5 holds garden villages only;
- no tower and no skyscraper stands anywhere in World 3, and every home of the garden villages is lower than a factory.

**Acceptance criteria**
- Given each World 3 section, then its groups are among the seven World 3 groups and follow the rules above.
- Given the residences and garden villages groups, then their tallest model is lower than the lowest model of the factories.
- Manual visual validation: no tall building stands in the suburbs and the villages.

*Sources: P09-R03, P09-R06, D-111, D-160.*

### WLD-3-08 — More buildings and props as the world goes on · MUST

On each level's own seed, the number of buildings and props placed goes up from 3-1 to 3-5 (the
homes are smaller and their streets closer than the factories'), and in each level the second half
has more props than the first.

**Acceptance criteria**
- Unit test (fixed seed): the buildings and props placed go up strictly from 3-1 to 3-5.
- Unit test (fixed seed): in each World 3 level, the second half has more props than the first.

*Sources: P09-R03, D-111, D-139, D-164.*

**Gap:** no unit test checks it since the Python port.

### WLD-3-09 — No sea · MUST

No World 3 level has a sea: no coast or shore, no ground under the sea level, nothing floating. Canals,
rivers and ponds (WLD-3-10) are not sea.

**Acceptance criteria**
- Unit test: no World 3 section has a shore, and no level's relief lies under a sea level.

*Sources: P09-R03, D-111.*

### WLD-3-10 — A canal, then a river · MUST

World 3 has inland water: a canal between stone walls from 3-1's second section on, wider at the docks
in 3-2; in 3-3 the canal runs along a park and becomes a river among the brick terraces; in 3-4 the
river runs between grassy banks; in 3-5 the river runs on and ponds lie among the gardens. The canal
and the river are channels cut below the water level, so they hold water; the water is grey-green and
flows down the screen (see [water](../../graphics/water.md)). Every World 3 level has some canal, river
or pond water.

**Acceptance criteria**
- Unit test: every World 3 level has some canal, river or pond water.
- Manual visual validation: the canal and the river flow down the screen.

*Sources: P09-R03, P09-R06, D-111.*

**Discrepancy:** World 3 has no water at all: no section has a channel or ponds and the levels set no
sea level (`src/game/config/world_3/scenery.py`, "No water (reviewer, 2026-10-28)"; phase 15 commit
"World 3 without water"). No decision records this change. The river and pond shapes
(`river`, `PONDS` in the same file) are only used by World 4's sections, which drop them (WLD-4-09).

### WLD-3-11 — The town ground · MUST

All five levels share one ground look: World 2's stained industrial concrete as the paved cover,
World 1's grass as the grass of the gardens and parks, damp dark earth between them, mud low by the
water, grey stone on steep slopes (the canal walls and embankments), and the town's water colour
flowing down the screen. The relief is flat in the factories and the streets (`flat_relief`) and gently
rolling in the suburbs and villages (`rolling_relief`). The ground is toned with World 3's share of
its colour (see [readability](../../graphics/readability.md)).

**Acceptance criteria**
- Given each World 3 level, then its look uses the town terrain (paving, grass, earth, mud, stone).
- Manual visual validation: World 3 does not look like World 1 or 2 with another colour.

*Sources: P09-R06, D-111.*

### WLD-3-12 — No plants, no jungle props · MUST

No plant grows in World 3: its sections have no tree density and its props no tree kind. The jungle
props and canopy families built for the first World 3 are not part of the game.

**Acceptance criteria**
- Given World 3's props, then their tree list is empty and no section has a tree density above 0.

*Sources: P09-R06, D-163, D-207.*

### WLD-3-13 — Street grids in every section · MUST

Every World 3 section is laid out as a grid of streets and blocks on the grid of tiles (see
[roads](../../graphics/roads.md)), with cars in the streets (see [traffic](../../graphics/traffic.md)).
The block sizes depend on the district (`street_blocks`): the widest in the factories, narrower ones in
the terraced streets, the smallest in the suburbs, avenues and village lanes. World 3 uses World 1's
road rules, with the street grids reaching only just past the ground in view (`streets_offscreen_x`).

**Acceptance criteria**
- Given each World 3 section, then it has a street grid from the table under **Tunable values**.
- Given World 3's roads, then the street grids end beyond `streets_offscreen_x` on each side.

*Sources: P09-R03, P09-R06, D-111, D-139.*

### WLD-3-14 — A day passing over World 3 · MUST

Each World 3 level has its own look (time of day, clouds, weather, light), later in the day from
level to level: a misty morning (3-1), a midday shower (3-2), an afternoon thunderstorm with
lightning (3-3), a rainy dusk (3-4), a rainy night clearing to a moonlit sky (3-5). The weather of
World 3 is rain, and lightning in 3-3 only (see [weather](../../graphics/weather.md)); no World 3
level uses snow, falling ash, embers or an aurora. The levels' looks are in their files.

**Acceptance criteria**
- Given each World 3 level, then its look matches its level file, look changes included.
- Manual visual validation: the player ship, enemies, shots and bonuses stay clearly visible in every World 3 level, the night and the storm included.

*Sources: P09-R04, P09-R05, D-111.*

### WLD-3-15 — Enemy roster · MUST

World 3 uses the eleven basic enemy kinds and brings in the five veteran kinds, one more at each level;
no elite kind comes in World 3 (see [enemies](../../enemies/common.md)):

| Level | Basic kinds | Veteran kinds |
|-------|-------------|---------------|
| 3-1 | Gnat, Hornet, Scout, Strafer, Weaver, Splitter | [Wasp](../../enemies/wasp.md) |
| 3-2 | all eleven | Wasp, [Mortar](../../enemies/mortar.md) |
| 3-3 | all eleven | Wasp, Mortar, [Minelayer](../../enemies/minelayer.md) |
| 3-4 | all eleven | Wasp, Mortar, Minelayer, [Mantis](../../enemies/mantis.md) |
| 3-5 | all eleven | all five, with the [Phantom](../../enemies/phantom.md) |

**Acceptance criteria**
- Unit test: the kinds of each World 3 level's waves (plan and filler) are exactly those of its row.
- Unit test: no World 3 level uses an elite kind.

*Sources: P09-R07, P05-R24, D-080, D-090.*

**Gap:** the unit tests check only that the kinds exist, not the table.

### WLD-3-16 — Wave plans · SHOULD

Each World 3 level's waves are written as a wave plan, as in World 2: from 4 s to 292 s, a beat
every gap seconds, the gap shrinking over the level, each beat the next phrase of the level's cycle
(a kind, a number of groups, the seconds between groups, a side and a place on it, a spread), its
groups growing over the level by the plan's growth. A filler of light kinds fills the lulls (its
largest gap shrinking over the level), and nothing new comes in the quiet stretch before each boss
(see [level flow](../../gameplay/level-flow.md)). The waves are deterministic. Each level's plan
(lead kinds, gaps, growth) is in its file.

**Acceptance criteria**
- Unit test: each World 3 plan composes beats in time order, inside its `from` … `to`, naming known kinds and sides.
- Unit test: the same level built twice has the same waves.

*Sources: P09-R07, D-080.*

### WLD-3-17 — Harder level after level · MUST

From 3-1 to 3-5:
- the enemies per minute of scroll, the enemy HP per minute (hulls only) and the most enemies on screen at once go up strictly, measured by a play-through without shooting;
- the bullet speed and fire rate factors never go down;
- in each level, the second half has more enemy HP than the first.

**Acceptance criteria**
- Unit test: the strict increases from 3-1 to 3-5 (play-through without shooting, fixed seed).
- Unit test: the factors never go down from 3-1 to 3-5.
- Unit test: in each World 3 level, the second half has more enemy HP than the first.

*Sources: P09-R08, D-080, D-090.*

**Gap:** since the Python port only the factors are unit tested; the play-through measures are not.

### WLD-3-18 — Harder than World 2 · MUST

On the same measures as WLD-3-17, 3-1 is at least as hard as 2-3, a fresh start, and 3-5 is harder
than 2-5.

**Acceptance criteria**
- Unit test: 3-1 ≥ 2-3 and 3-5 > 2-5 on enemies per minute, HP per minute, peak on screen and the two factors.
- Manual validation: 3-1 feels like a fresh start, 3-5 clearly harder than 2-5.

*Sources: P09-R08, D-080, D-090.*

**Gap:** not unit tested since the Python port.

### WLD-3-19 — Ten bosses · MUST

Each World 3 level has its own mini boss, at the middle of the level, and its own final boss, at its
end; no boss is used twice. Within World 3 at least one fight stops the ground (×0) and at least one
is a chase (faster than ×1). The bosses themselves are described in their files:

| Level | Mini boss | Final boss |
|-------|-----------|------------|
| 3-1 | [Mangrove Croc](../../bosses/mini/3-1-mangrove-croc.md) (×1.4, a chase) | [River Leviathan](../../bosses/final/3-1-river-leviathan.md) |
| 3-2 | [Toucan](../../bosses/mini/3-2-toucan.md) | [Canopy Spider](../../bosses/final/3-2-canopy-spider.md) |
| 3-3 | [Stone Idol](../../bosses/mini/3-3-stone-idol.md) (×0, the ground stops) | [Sky Temple](../../bosses/final/3-3-sky-temple.md) |
| 3-4 | [Mosquito](../../bosses/mini/3-4-mosquito.md) | [Dam Breaker](../../bosses/final/3-4-dam-breaker.md) |
| 3-5 | [Jaguar](../../bosses/mini/3-5-jaguar.md) | [Verdant Crown](../../bosses/final/3-5-verdant-crown.md) |

**Acceptance criteria**
- Unit test: each World 3 level has exactly this mini boss and final boss, and no boss of the world is used twice.
- Unit test: among the ten fights, one has a ground speed factor of 0 and one above 1.

*Sources: P09-R09, D-111.*

### WLD-3-20 — Boss difficulty across World 3 · MUST

- The mini bosses' full HP goes up strictly from 3-1 to 3-5, and so does the final bosses'.
- Each final boss has more full HP than its level's mini boss.
- Each World 3 boss has more full HP than the World 2 boss of the same level number and rank.
- Boss bullets use the level's bullet speed and fire rate factors.
- The fight times (simulation, balanced ship, guns at level 3, always firing at the boss) are within `mini_fight_time` and `final_fight_time`.

Full HP is the boss's health bar at its arrival: its core and all its parts, the hidden weapons it
reveals as it transforms included (see [bosses](../../bosses/common.md)).

**Acceptance criteria**
- Unit test: the HP orderings above.
- Unit test (simulation): the fight times within their ranges.
- Manual validation: the World 3 bosses feel harder than the World 2 ones.

*Sources: P09-R10.*

**Discrepancy:** with the hidden weapons counted (D-221), two orderings break: the 3-3 Stone Idol
(6 480) has more full HP than the 3-4 Mosquito (6 100), and the 3-1 River Leviathan (10 040) has less
than the 2-1 Narwhal (10 460). Counted on the core and the parts they arrive with, every ordering
holds (see **Tunable values**).

**Gap:** neither the orderings nor the fight times are unit tested since the Python port; the fight
times were last measured before the hidden weapons (D-221) made the fights longer.

### WLD-3-21 — Music · MUST

The five World 3 levels share World 3's music style and differ in key, tempo, chords, melody and
rhythm (see [music](../../audio/music.md)): dark synthwave on tribal toms and shakers, the heavy kick
and gated snare, a plucked syncopated bass, dark pads, a square arpeggio and a square lead, in
phrygian, minor or harmonic minor keys, at `music_tempo`. World 3's boss track is faster, in phrygian.

**Acceptance criteria**
- Given a World 3 level, then its music is composed in World 3's style; given a World 3 boss fight, then World 3's boss track plays.

*Sources: P12-R06, D-098, D-099, D-101.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| level_duration | 300 s ± 10 s | WLD-3-02; every World 3 level is 300 s |
| section_transition | 900 units | WLD-3-05; World 2's `TRANSITION`, `src/game/config/world_2/scenery.py` |
| paved_share 3-1 → 3-5 | about 0.92 / 0.77 / 0.54 / 0.29 / 0.13 | WLD-3-06; mean of the sections' `surface.paved`, `src/game/config/world_3/scenery.py` |
| grass_share 3-1 → 3-5 | about 0.01 / 0.07 / 0.26 / 0.55 / 0.76 | WLD-3-06; mean of the sections' `surface.lush` |
| flat_relief | 32 ± 2, features 600 across | WLD-3-11; `FLAT` (factories, yards, streets) |
| rolling_relief | 30 ± 6, features 560 across | WLD-3-11; `ROLLING` (suburbs, villages) |
| building groups | heavy industry (foundries, plants, 34–38 high), industrial (works, factories, tanks, 6–25), docks (containers, cranes, warehouses, 8–18), workshops (7–8), workers' flats (14–19), residences (homes of the future, 5–9), garden villages (small homes, 4–11) | WLD-3-07; `WORLD_3_GROUPS`, `WORLD_3_PROPS`, `src/game/config/world_3/props.py`; models in `TILE_GROUPS`, `src/game/config/tile_buildings.py`; heights in model units |
| loners / hamlets | a lone building in 15 % of 150-unit cells; hamlets of 5–9 buildings every 700–1 400 | `WORLD_3_PROPS.loners`, `.hamlets` |
| street_blocks (rows × columns) | streets 45–90 × 50–110; terraced streets 33–56 × 38–76; suburbs 40–70 × 50–95; garden suburbs 36–62 × 46–88; avenues 36–62 × 40–78; village streets 40–70 × 45–90; lanes 35–60 × 40–80 | WLD-3-13; `STREETS` … `LANES`, `src/game/config/world_3/scenery.py` |
| streets_offscreen_x | 640 (240 before D-249) | WLD-3-13; `WORLD_3_ROADS.offscreenX` (D-139) |
| background tone | 0.45 | WLD-3-11; `READABILITY.tones.world3`, `src/game/config/readability.py` |
| water colour / flow | RGB 0.1, 0.13, 0.12; drift 0, 16 | WLD-3-10; `WATER`, `RIVER_FLOW`, `src/game/config/world_3/looks.py` (unused while World 3 has no water) |
| enemy_bullet_speed_factor 3-1 → 3-5 | 1 / 1.05 / 1.1 / 1.2 / 1.25 | WLD-3-17; `WORLD_3_DIFFICULTY`, `src/game/config/world_3/difficulty.py` |
| enemy_fire_rate_factor 3-1 → 3-5 | 1 / 1.05 / 1.1 / 1.2 / 1.25 | WLD-3-17; same |
| enemies per minute 3-1 → 3-5 | 180.8 / 184.0 / 190.0 / 219.0 / 247.8 | WLD-3-17; last measured (D-090), seed 606, without shooting (2-3: 121.4, 2-5: 233.4, D-080) |
| enemy HP per minute 3-1 → 3-5 | 4 384 / 5 494 / 6 452 / 7 744 / 8 952 | WLD-3-17; same (2-3: 3 666, 2-5: 7 360) |
| peak_on_screen 3-1 → 3-5 | 37 / 38 / 45 / 50 / 53 | WLD-3-17; same (2-3: 36, 2-5: 51); the first target (13 … 19) was never met, the order is kept (D-080) |
| boss full HP, mini 3-1 → 3-5 | 4 200 / 5 020 / 6 480 / 6 100 / 6 860 (core and first parts: 3 200 / 3 780 / 4 200 / 4 500 / 5 100) | WLD-3-20; `src/game/config/bosses/world_3/*.py`; World 2: 3 760 / 3 840 / 5 590 / 5 240 / 5 540 |
| boss full HP, final 3-1 → 3-5 | 10 040 / 13 550 / 20 510 / 20 840 / 27 780 (core and first parts: 6 800 / 9 050 / 9 950 / 14 000 / 19 500) | WLD-3-20; World 2: 10 460 / 10 240 / 13 100 / 19 840 / 26 960 |
| mini_fight_time 3-1 → 3-5 | 35–45 s → 50–60 s | WLD-3-20; last measured 41.6 / 44.4 / 47.3 / 51.4 / 54.7 s (phase 9, before D-221) |
| final_fight_time 3-1 → 3-5 | 70–90 s → 110–140 s | WLD-3-20; last measured 87.5 / 90.6 / 102.4 / 115.2 / 127.1 s (phase 9, before D-221) |
| music_tempo | 120–132 BPM; boss track 20–30 BPM above the fastest | WLD-3-21; `WORLD_STYLES[3]`, `src/game/view/audio/music_styles.py` |

## Notes

- World 3 was first the Jungle (a sea delta, a rainforest, lost temples, a swamp with a dam, a canopy
  city), with its own jungle props, set pieces and canopy. The rework of 2026-10-27 (D-111) kept the
  times of day, the weather and the ten bosses, so the jungle-themed bosses (a croc, a spider, a stone
  idol, a temple, a dam breaker…) now fly over the factories and the suburbs. The jungle models were
  removed later (D-163).
- The first home models of the rework (a small block of flats, a row of terraced houses, a house with
  a pitched roof and a garage) and World 1's farmhouses and greenhouses were replaced by the models
  made for the grid of tiles (D-160, D-207): today the residences and the garden villages are small
  homes of the future on paved plots.
- The woods of tree imposters (D-212) are World 1's only: World 3's grass has none.
- How the per-level measures are taken (a play-through without shooting, hulls only) is in
  [level flow](../../gameplay/level-flow.md) and the decisions D-038, D-080, D-090.
