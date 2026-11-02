# World 4 — The Metropolis

> **Area:** worlds · **Prefix:** `WLD-4` · **Related:** [4-1](4-1-garden-town.md), [4-2](4-2-inner-town.md), [4-3](4-3-midtown.md), [4-4](4-4-business-district.md), [4-5](4-5-downtown.md), [World 3](../world-3/world.md), [level flow](../../gameplay/level-flow.md), [level select](../../ui/level-select.md), [terrain](../../graphics/terrain.md), [sky and light](../../graphics/sky-and-light.md), [weather](../../graphics/weather.md), [roads](../../graphics/roads.md), [buildings](../../graphics/buildings.md), [shots](../../graphics/shots.md), [enemies](../../enemies/common.md), [bosses](../../bosses/common.md), [music](../../audio/music.md)

World 4, **the Metropolis**, is the fourth and last world of the game: five levels, 4-1 to 4-5, of
about five minutes each. Together they are one journey from the garden villages of small houses
World 3 ends on, through a town, mid-rise blocks and offices, to the towers of a business district and
a downtown of skyscrapers. It is a bright midday city of buildings and roads only: no sea, no river,
no lava, no grass and no trees. Every level has its own mini boss and final boss; the 4-5 final boss is
the game's last. World 4 is harder than World 3, and its levels get harder from 4-1 to 4-5. It is no
longer the Volcanic Lands it first was (reworked at the reviewer's request, 2026-10-27, D-112).

This file holds what the five levels share. Each level file holds the level's own sections, look,
waves, difficulty and bosses. The engines they use are described in `graphics/`, `gameplay/` and
`bosses/common.md`.

## Requirements

### WLD-4-01 — World 4 in the game · MUST

World 4 is the fourth and last of the game's worlds. Its levels are, in this order: `4-1` Garden town,
`4-2` Inner town, `4-3` Midtown, `4-4` Business district, `4-5` Downtown. They fill the fourth and last
row of the level select, all unlocked; after `3-5` is completed the level select highlights `4-1`, and
after `4-5`, the game's last level, it keeps `4-5` highlighted (the rules of the grid are in
[level select](../../ui/level-select.md)).

**Acceptance criteria**
- Given the game's levels, then World 4 is the five levels `4-1` … `4-5` in this order, the last five of the game.
- Given `level-select`, then its fourth row shows exactly `4-1` to `4-5`, all unlocked, and the grid has 20 levels, none locked.
- Given `3-5` (or `4-5`) is completed, then `level-select` shows with `4-1` (or `4-5`) highlighted.

*Sources: P10-R01, D-112.*

### WLD-4-02 — Five-minute levels · MUST

Each World 4 level's scroll time, its length divided by its ground speed, is `level_duration`. The
lengths and speeds are in the level files.

**Acceptance criteria**
- Given each World 4 level, then its length ÷ its ground speed is between 290 s and 310 s.

*Sources: P10-R02.*

### WLD-4-03 — One journey, from the houses to the skyscrapers · MUST

The five levels follow one another as a single journey into a growing city. Each has its theme, in
this order:

| Level | Name | Buildings |
|-------|------|-----------|
| 4-1 | Garden town | The garden villages 3-5 ended on, suburban lanes, suburbs, terraced streets, flats, then a town centre with the first mid-rise blocks. |
| 4-2 | Inner town | Town streets, the ring road, mid-rise flats, a city park, then mid-rise blocks among the first offices. |
| 4-3 | Midtown | Offices among mid-rise blocks, office blocks, river quays, plazas, then the first city towers. No skyscraper. |
| 4-4 | Business district | City towers, a tower park, the financial district with the first skyscrapers, high rise, then the first skyline. |
| 4-5 | Downtown | Skyscrapers, a central park, then skyscrapers filling every block; skyscrapers only at the end. |

**Acceptance criteria**
- Manual visual validation: garden town, inner town, midtown, business district and downtown can be told apart, and downtown reads as a skyline of skyscrapers.

*Sources: P10-R03, D-112.*

### WLD-4-04 — Each level begins on the buildings the previous one ended on · MUST

Each World 4 level's first section is the previous level's last section (same streets and building
groups), shortened to 40 s. 4-1's first section is 3-5's last, the garden villages, with the very same
building group and lanes; its ground is the city's (WLD-4-08), so 4-1 does not blend in from 3-5's
grass.

**Acceptance criteria**
- Given 4-2 … 4-5, then each one's first section is the previous level's last section, but for its length (40 s).
- Given 4-1, then its first section has 3-5's last section's streets and building group (garden villages), on the city ground.

*Sources: P10-R03, D-112, D-126.*

### WLD-4-05 — Slow transitions · MUST

The city grows slowly, as Worlds 2 and 3 change. Two sections blend over `section_transition`, and each
taller building group first comes in mixed with the one before it (garden villages with residences,
residences with workers' flats, flats with the town centre, the town centre with mid-rise, mid-rise
with offices, offices with towers, towers with skyscrapers, skyscrapers with downtown) before it
stands alone.

**Acceptance criteria**
- Given each World 4 level, then its sections blend over `section_transition`.
- Given each section that brings in a taller building group, then the section before it, or the section itself, also has the group it replaces.

*Sources: P10-R03, D-112.*

### WLD-4-06 — Buildings grow taller · MUST

On each level's own seed, the mean height of the buildings placed goes up from 3-5 through 4-1 to 4-5,
and in each level the second half's is higher than the first's. (The number of buildings may go down
as they grow.)

**Acceptance criteria**
- Unit test (fixed seed): the mean building height goes up strictly from 3-5, 4-1, … to 4-5.
- Unit test (fixed seed): in each World 4 level, the second half's mean building height is higher than the first's.

*Sources: P10-R03, D-112, D-164.*

**Gap:** no unit test checks it since the Python port.

### WLD-4-07 — Where the tall buildings stand · MUST

The buildings of World 4 come from its building groups (see **Tunable values** and
[buildings](../../graphics/buildings.md)): World 3's garden villages, residences and workers' flats,
then the town centre, mid-rise, offices, towers, skyscrapers and downtown groups.
- No city tower and no skyscraper stands in 4-1 or 4-2.
- No skyscraper stands in 4-3; its last sections bring in the first city towers.
- The first skyscrapers stand in 4-4's financial district.
- The last section of 4-5 holds skyscrapers only.
- Every skyscraper stands taller than every city tower.

**Acceptance criteria**
- Unit test: the groups of each World 4 section follow the rules above.
- Unit test: the lowest skyscraper model is taller than the tallest city tower model.

*Sources: P10-R03, P10-R08, D-112, D-160.*

**Discrepancy:** the offices group (from 4-2's last section on) holds a city tower model
(`tile-tower-2x2-6`, 73 high), so a city tower can stand in 4-2; the towers group (from 4-3's plazas
on) holds a skyscraper model (`tile-skyscraper-3x3`, 106 high), so a skyscraper can stand in 4-3
(`TILE_GROUPS`, `src/game/config/tile_buildings.py`). The lowest skyscraper (77) is still taller than
every tower.

### WLD-4-08 — A city of buildings and roads only · MUST

Every World 4 section holds only buildings and roads: its ground is flat (the city ground, WLD-4-10)
and fully paved, with no grass and no tree. The sections named after parks (city park, tower park,
central park) are parks by their fewer buildings only.

**Acceptance criteria**
- Given each World 4 section, then its paved cover is 1, its grass cover 0, its tree density 0, and its relief the city ground.
- Manual visual validation: World 4 reads as a city, with no green.

*Sources: D-126.*

### WLD-4-09 — No water and no lava · MUST

No World 4 level has water or lava:
- no sea: the levels set no sea level, so no water plane and no rain rings are drawn under the city;
- no river, canal, lake or pond, and no shore;
- no lava (the lava look stays in the engine, unused).

**Acceptance criteria**
- Unit test: no World 4 level has a sea, and no section has a channel, lakes, a shore or flattened ground.
- Given 4-2, 4-4 and 4-5 in play, then the sky state reports no lava.

*Sources: P10-R03, P10-R05, D-112, D-126, D-147.*

### WLD-4-10 — The city ground stays under the clouds · MUST

World 4's ground is the city ground, `city_ground`, lower than World 3's flat ground: low enough that
the tallest roof, the terrain's highest point plus the tallest building model, scaled by the
playfield's ground scale, stays the clouds' clearance under the lowest cloud layer, so no skyscraper
pokes through a cloud layer or meets one. The ground stays above the props' minimum height. The
building heights are not lowered for it.

**Acceptance criteria**
- Unit test: for each World 4 level, (terrain ceiling + tallest building model) × ground scale + cloud clearance ≤ the lowest cloud layer's altitude.
- Unit test: the city ground's lowest point is above the props' `minHeight`.

*Sources: D-196.*

### WLD-4-11 — The city ground look · MUST

World 4 uses World 3's town ground look (WLD-3-11); being fully paved, only its industrial concrete
paving and its roads show. Its flat ground casts no shadows (it has nothing to shade). The ground is
toned with World 4's share of its colour (see [readability](../../graphics/readability.md)).

**Acceptance criteria**
- Given each World 4 level's look, then its terrain is World 3's town terrain with shadows off.

*Sources: P10-R08, D-112, D-126, D-151.*

### WLD-4-12 — Boulevards · MUST

World 4's street grids have wide, straight boulevards along some of their rows (across the level):
3 lanes each way on `boulevard_3_share` of the lines and 4 lanes each way on `boulevard_4_share`,
chosen by a hash of the line. A boulevard is built along its whole line (see
[roads](../../graphics/roads.md) for how it crosses the streets and its markings).

**Acceptance criteria**
- Given World 4's roads, then they list boulevards of 3 and 4 lanes each way with these shares.
- Manual visual validation: wide boulevards cross the city's street grids.

*Sources: D-136.*

**Discrepancy:** World 4 has 3-lane boulevards only, 3 tiles wide, on 20 % of the rows; the 4-lane
ones were dropped in phase 15 ("the 4-lane ones dropped, 3 x 3 is enough", reviewer 2026-10-28, in
`src/game/config/world_4/props.py`; commit "4x4 boulevards dropped"). No decision records it.

### WLD-4-13 — Street grids in every section · MUST

Every World 4 section is laid out as a grid of streets and blocks on the grid of tiles, with cars in the
streets (see [roads](../../graphics/roads.md), [traffic](../../graphics/traffic.md)). The block sizes are
World 3's (`street_blocks`): the closest lanes and village streets where 4-1 begins, the wide city
streets from the flats on, the suburb blocks in 4-2's city park. The last two sections of 4-5 fill every
block with buildings side by side. The street grids reach only just past the ground in view
(`streets_offscreen_x`).

**Acceptance criteria**
- Given each World 4 section, then it has one of World 3's street grids.
- Given 4-5's downtown and city heart, then their blocks are filled side by side.

*Sources: P10-R03, D-112, D-139.*

### WLD-4-14 — A bright midday city · MUST

Every World 4 level is at **midday**, brighter than the plain midday (sun and ambient light ×
`daylight_brightness`), with the windows and the cars lit as at night (ground lights ×
`daylight_ground_lights`), all along the level, look changes included. Its clouds are white: they keep
the time of day's colours whatever the level's storm, cloud tint or glow from below. Each level keeps
its own clouds, haze, storm, glow from below and weather (see the level files).

**Acceptance criteria**
- Given each World 4 look, then its start and every change are at midday with brightness 1.3, ground lights 1.5 and plain clouds.
- Manual visual validation: a bright, sunny city; the player ship, enemies, shots and bonuses stay clearly visible in every level.

*Sources: P10-R04, D-126, D-196.*

**Note:** D-126 also set the cloud cover of every World 4 level to 0. The clouds came back, kept
white, at the reviewer's request on 2026-10-29 (code comment in `src/game/config/world_4/looks.py`,
phase 15 commit), without a decision of their own; D-196 (reviewer, 2026-10-30) then lowered the
city ground to keep the skyscrapers under them, so this requirement follows the clouds of today.

### WLD-4-15 — Ash, embers and the city's glow · MUST

World 4's weather is falling ash and embers (see [weather](../../graphics/weather.md)), and its clouds
and haze can be lit from below by the city's glow: none in 4-1 (a smoke haze), falling ash under an
ash cloud in 4-2, embers and a growing orange glow in 4-3, ash and embers together under an orange
glow in 4-4, embers growing to their strongest under a deep red eruption glow in 4-5 (a volcano erupts
somewhere beyond downtown). No World 4 level has rain, snow, lightning or an aurora.

**Acceptance criteria**
- Given each World 4 look, then its weather and glow match its level file, look changes included.
- Given `?level=4-2&weather=0`, then 4-2 shows no falling ash.
- Manual validation: the embers are never confused with enemy bullets, even in the 4-5 eruption.

*Sources: P10-R04, P10-R06, D-112.*

### WLD-4-16 — Contrast shots in World 4's looks · MUST

Every World 4 look names the contrast shot style, so the enemy and boss bullets and the laser warning
lines are drawn with their light, contrasting core (see [shots](../../graphics/shots.md)).

**Acceptance criteria**
- Given each World 4 level in play, then its shot style is `contrast`.

*Sources: P10-R07, D-086.*

### WLD-4-17 — Enemy roster · MUST

Every World 4 level uses the eleven basic enemy kinds and the five veteran kinds; the five elite kinds
come in two in 4-1, then one more a level, so 4-4 and 4-5 use all five (see
[enemies](../../enemies/common.md)):

| Level | Elite kinds |
|-------|-------------|
| 4-1 | [Hydra](../../enemies/hydra.md), [Orbiter](../../enemies/orbiter.md) |
| 4-2 | Hydra, Orbiter, [Scissor](../../enemies/scissor.md) |
| 4-3 | Hydra, Orbiter, Scissor, [Hive](../../enemies/hive.md) |
| 4-4 | all five, with the [Juggernaut](../../enemies/juggernaut.md) |
| 4-5 | all five |

**Acceptance criteria**
- Unit test: each World 4 level's waves use all eleven basic kinds, all five veteran kinds, and exactly the elite kinds of its row.

*Sources: P10-R09, P05-R24, D-087, D-090.*

**Gap:** the unit tests check only that the kinds exist, not the table.

### WLD-4-18 — Wave plans · SHOULD

Each World 4 level's waves are written as a wave plan, as in World 3 (WLD-3-16): from 4 s to 292 s,
every kind in every cycle, the level's lead kinds two or three times a cycle, its gap and growth chosen
by sweeping them with the play-through. A filler of light kinds fills the lulls. The waves are
deterministic. Each level's plan is in its file.

**Acceptance criteria**
- Unit test: each World 4 plan composes beats in time order, inside its `from` … `to`, naming known kinds and sides.
- Unit test: the same level built twice has the same waves.

*Sources: P10-R09, D-087.*

### WLD-4-19 — Harder level after level · MUST

From 4-1 to 4-5:
- the enemies per minute of scroll, the enemy HP per minute (hulls only) and the most enemies on screen at once go up strictly, measured by a play-through without shooting;
- the bullet speed and fire rate factors never go down;
- in each level, the second half has more enemy HP than the first.

If the peaks on screen are lowered to hold the frame rate, their order is kept.

**Acceptance criteria**
- Unit test: the strict increases from 4-1 to 4-5 (play-through without shooting, fixed seed).
- Unit test: the factors never go down from 4-1 to 4-5.
- Unit test: in each World 4 level, the second half has more enemy HP than the first.

*Sources: P10-R10, D-087, D-090.*

**Gap:** since the Python port only the factors are unit tested; the play-through measures are not.

### WLD-4-20 — Harder than World 3, and still beatable · MUST

On the same measures as WLD-4-19, 4-1 is at least as hard as 3-3, and 4-5 is harder than 3-5: 4-5 is
the hardest level of the game. The game stays beatable by a casual player: with weapons at level 4 or
5, a careful player gets through 4-5.

**Acceptance criteria**
- Unit test: 4-1 ≥ 3-3 and 4-5 > 3-5 on enemies per minute, HP per minute, peak on screen and the two factors.
- Manual validation: 4-1 feels like a fresh start; 4-5 is the hardest level of the game and still beatable.

*Sources: P10-R10, D-087, D-090.*

**Gap:** not unit tested since the Python port.

### WLD-4-21 — Ten bosses · MUST

Each World 4 level has its own mini boss, at the middle of the level, and its own final boss, at its
end; no boss is used twice. Within World 4 at least one fight stops the ground (×0) and at least one
is a chase (faster than ×1). The Caldera Throne, 4-5's final boss, is the game's last boss. The bosses
themselves are described in their files:

| Level | Mini boss | Final boss |
|-------|-----------|------------|
| 4-1 | [Cinder Crab](../../bosses/mini/4-1-cinder-crab.md) | [Steam Dreadnought](../../bosses/final/4-1-steam-dreadnought.md) |
| 4-2 | [Ash Wraith](../../bosses/mini/4-2-ash-wraith.md) (×1.5, a chase) | [Geyser Rig](../../bosses/final/4-2-geyser-rig.md) |
| 4-3 | [Magma Salamander](../../bosses/mini/4-3-magma-salamander.md) | [Obsidian Golem](../../bosses/final/4-3-obsidian-golem.md) |
| 4-4 | [Furnace Drake](../../bosses/mini/4-4-furnace-drake.md) | [Foundry Ark](../../bosses/final/4-4-foundry-ark.md) |
| 4-5 | [Ember Herald](../../bosses/mini/4-5-ember-herald.md) (×1.4, a chase) | [Caldera Throne](../../bosses/final/4-5-caldera-throne.md) (×0, the ground stops) |

**Acceptance criteria**
- Unit test: each World 4 level has exactly this mini boss and final boss, and no boss of the world is used twice.
- Unit test: among the ten fights, one has a ground speed factor of 0 and one above 1.

*Sources: P10-R11, D-112.*

### WLD-4-22 — Boss difficulty across World 4 · MUST

- The mini bosses' full HP goes up strictly from 4-1 to 4-5, and so does the final bosses'.
- Each final boss has more full HP than its level's mini boss.
- Each World 4 boss has more full HP than the World 3 boss of the same level number and rank.
- Boss bullets use the level's bullet speed and fire rate factors.
- The fight times (simulation, balanced ship, guns at level 3, always firing at the boss) are within `mini_fight_time` and `final_fight_time`.
- The Caldera Throne is the hardest boss of the game, and still beatable.

Full HP is the boss's health bar at its arrival, the hidden weapons it reveals included (see
[bosses](../../bosses/common.md)).

**Acceptance criteria**
- Unit test: the HP orderings above.
- Unit test (simulation): the fight times within their ranges.
- Manual validation: the Caldera Throne is the hardest boss of the game, and still beatable.

*Sources: P10-R12.*

**Discrepancy:** with the hidden weapons counted (D-221), two orderings with World 3 break: the 4-3
Magma Salamander (5 940) has less full HP than the 3-3 Stone Idol (6 480), and the 4-3 Obsidian Golem
(19 760) less than the 3-3 Sky Temple (20 510). Counted on the core and the parts they arrive with,
every ordering holds (see **Tunable values**).

**Gap:** neither the orderings nor the fight times are unit tested since the Python port; the fight
times were last measured before the hidden weapons (D-221) made the fights longer.

### WLD-4-23 — Music · MUST

The five World 4 levels share World 4's music style, the heaviest of the game, and differ in key,
tempo, chords, melody and rhythm (see [music](../../audio/music.md)): darksynth on slow heavy kicks
and low toms with the gated snare, a rolling, growling sixteenth bass, dark pads, a plucked arpeggio
and a brass lead, in phrygian, harmonic minor or minor keys, at `music_tempo`. World 4's boss track is
faster, in phrygian.

**Acceptance criteria**
- Given a World 4 level, then its music is composed in World 4's style; given a World 4 boss fight, then World 4's boss track plays.

*Sources: P12-R06, D-098, D-099, D-100, D-101.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| level_duration | 300 s ± 10 s | WLD-4-02; every World 4 level is 300 s |
| section_transition | 900 units | WLD-4-05; World 2's `TRANSITION` |
| city_ground | 8 ± 2, features 600 across | WLD-4-10; `CITY_GROUND`, `src/game/config/world_4/scenery.py`, applied by `city_only` |
| ground scale / cloud clearance / lowest cloud layer | 2 / 15 / 265 | WLD-4-10; `PLAYFIELD_CAMERA.groundScale`, `SCENERY_STAGE_CONFIG.cloud_clearance`, `BASE_SCENERY_LOOK.clouds` |
| tallest building model | 112.2 high (`tile-skyscraper-3x3-3`) | WLD-4-10; roofs reach about 245 |
| building groups | garden villages (4–11 high), residences (5–9), workers' flats (14–19), town centre (mid-rise 21–34, flats, one office 44), mid-rise (18–37, one office 41), offices (34–42, one tower 73), towers (55–69, one skyscraper 106), skyscrapers (77–112), downtown (skyscrapers 86–112 on 3×3 and 4×4 tiles) | WLD-4-07; `WORLD_4_GROUPS`, `WORLD_4_PROPS`, `src/game/config/world_4/city_props.py`; models in `TILE_GROUPS`, `src/game/config/tile_buildings.py`; heights in model units |
| mean building height 3-5 → 4-5 | 5.5 → 6.1 / 16.3 / 27.6 / 45.0 / 81.4 | WLD-4-06; last measured in phase 10 (2026-10-28), before the grid of tiles |
| boulevard_3_share | 0.12 (3 lanes each way, 18 wide) | WLD-4-12; D-136; today 0.2 (`WORLD_4_ROADS.boulevards`, `src/game/config/world_4/props.py`) |
| boulevard_4_share | 0.08 (4 lanes each way, 24 wide) | WLD-4-12; D-136; today none |
| street_blocks | World 3's (WLD-3-13) | WLD-4-13 |
| streets_offscreen_x | 640 (240 before D-249) | WLD-4-13; World 3's roads |
| daylight_brightness | 1.3 | WLD-4-14; `DAYLIGHT`, `src/game/config/world_4/looks.py` |
| daylight_ground_lights | 1.5 | WLD-4-14; same |
| background tone | 0.55 | WLD-4-11; `READABILITY.tones.world4`, `src/game/config/readability.py` (D-162) |
| enemy_bullet_speed_factor 4-1 → 4-5 | 1.1 / 1.15 / 1.2 / 1.3 / 1.35 | WLD-4-19; `WORLD_4_DIFFICULTY`, `src/game/config/world_4/difficulty.py` |
| enemy_fire_rate_factor 4-1 → 4-5 | 1.1 / 1.15 / 1.2 / 1.3 / 1.35 | WLD-4-19; same |
| enemies per minute 4-1 → 4-5 | 195.2 / 204.4 / 211.2 / 225.0 / 302.0 | WLD-4-19; last measured (D-090), seed 606, without shooting (3-3: 190.0, 3-5: 247.8) |
| enemy HP per minute 4-1 → 4-5 | 7 496 / 9 216 / 10 644 / 11 238 / 13 752 | WLD-4-19; same (3-3: 6 452, 3-5: 8 952) |
| peak_on_screen 4-1 → 4-5 | 53 / 55 / 57 / 62 / 64 | WLD-4-19; same (3-3: 45, 3-5: 53); the first target (15 … 21) was never met, the order is kept (D-087) |
| boss full HP, mini 4-1 → 4-5 | 4 450 / 5 500 / 5 940 / 6 910 / 7 470 (core and first parts: 3 650 / 4 180 / 4 500 / 5 150 / 5 550) | WLD-4-22; `src/game/config/bosses/world_4/*.py`; World 3: 4 200 / 5 020 / 6 480 / 6 100 / 6 860 |
| boss full HP, final 4-1 → 4-5 | 12 170 / 14 380 / 19 760 / 25 840 / 33 160 (core and first parts: 7 800 / 9 700 / 12 400 / 14 800 / 21 200) | WLD-4-22; World 3: 10 040 / 13 550 / 20 510 / 20 840 / 27 780 |
| mini_fight_time 4-1 → 4-5 | 40–50 s → 55–65 s | WLD-4-22; last measured 44.4 / 48.0 / 53.2 / 56.3 / 59.7 s (phase 10, before D-221) |
| final_fight_time 4-1 → 4-5 | 80–100 s → 120–150 s | WLD-4-22; last measured 89.2 / 100.7 / 112.4 / 126.2 / 137.6 s (phase 10, before D-221) |
| music_tempo | 104–116 BPM; boss track 20–30 BPM above the fastest | WLD-4-23; `WORLD_STYLES[4]`, `src/game/view/audio/music_styles.py` |

## Notes

- World 4 was first the Volcanic Lands (a steaming sea, ash plains, lava fields, foundries, a caldera
  with a magma lake). The rework of 2026-10-27 (D-112) kept the ten bosses, the waves and the sky
  scripts, so the volcanic bosses (a cinder crab, a steam dreadnought, a magma salamander, a caldera
  throne…) fly over the city, and the ash, the embers and the red eruption sky stay. The volcanic
  props were removed (D-129); the lava look and the smoke and steam plumes stay in the engine, unused.
- After the rework, World 4's sections ran on World 3's river, between grassy banks then stone quays,
  with the grass giving way to concrete level after level. Since D-126 every section goes through
  `city_only`, which drops the channels (quays), lakes and grass: the section data still names them
  (`quays(...)`, `river(...)`, `surface`), but they are not drawn. Some sections keep their old names
  (river quays, city park, tower park, central park).
- The skyscraper family made of parts (D-112) was replaced by the models made for the grid of tiles
  (D-160).
- D-126's background veil (0.42) was later replaced by darkening the background at the source (D-130).
