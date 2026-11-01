# World 1 — From the sea to the desert

> **Area:** Worlds · **Prefix:** `WLD-1` · **Related:** [1-1 Open sea](1-1-open-sea.md), [1-2 Green coast](1-2-green-coast.md), [1-3 Green country](1-3-green-country.md), [1-4 Dry lands](1-4-dry-lands.md), [1-5 Deep desert](1-5-deep-desert.md), [World 2](../world-2/world.md), [level flow](../../gameplay/level-flow.md), [level select](../../ui/level-select.md), [music](../../audio/music.md), [terrain](../../graphics/terrain.md), [sky and light](../../graphics/sky-and-light.md), [props](../../graphics/props.md), [buildings](../../graphics/buildings.md), [roads](../../graphics/roads.md), [enemies](../../enemies/common.md), [bosses](../../bosses/common.md)

World 1 is the first world of the game: five levels of about four minutes, cut from one long journey
that starts over the open sea, crosses green grassland and dries out into an American desert of red
land, cracked dry lakes, mesas and buttes, with more and more buildings along the way. It teaches the
eleven basic enemy kinds one level after the other, and each level is harder than the one before it.
This file holds what the five levels share; each level's own content is in its level file. How a
level runs (scroll, waves by distance, bosses, checkpoint, level end) is in
[level-flow.md](../../gameplay/level-flow.md); the terrain, sky, road, building and prop engines are
in [`graphics/`](../../graphics/).

## Requirements

### Identity

#### WLD-1-01 — Five levels, one journey · MUST

World 1 has five levels, in this order and with these names: `1-1` Open sea, `1-2` Green coast, `1-3`
Green country, `1-4` Dry lands, `1-5` Deep desert. The five levels are one journey cut into five
pieces: the open sea, then green grassland, then the desert (WLD-1-05). There is no other level in
World 1.

**Acceptance criteria**
- Given the game's levels, then World 1 is exactly `1-1` … `1-5`, in this order, each named as above (unit test).

*Sources: P06-R05, D-109.*

#### WLD-1-02 — First row of the level select · MUST

World 1 is the first row of the level select grid: `1-1` to `1-5`, all unlocked from a fresh start
(the grid and its rules: [level-select.md](../../ui/level-select.md)). After a World 1 level is
completed, the level select highlights the next level: `1-2` after `1-1`, and so on, and `2-1`
after `1-5`.

**Acceptance criteria**
- Given `level-select`, then the first row shows exactly `1-1` … `1-5`, none locked (e2e).
- Given `1-5` is completed, when Confirm is pressed on "Level complete", then `level-select` shows with `2-1` highlighted (e2e).

*Sources: P06-R01, P06-R03, P08-R01, D-089.*

#### WLD-1-03 — About four minutes a level · MUST

Each World 1 level lasts about 4 minutes: its scroll time, its length divided by its ground speed, is
`level_duration`. The boss fights add to the time played.

**Acceptance criteria**
- Given each World 1 level, then its length ÷ its ground speed is between 230 s and 250 s (e2e on the level's `duration`; the length is the sum of its sections' seconds at its speed, unit test).

*Sources: P06-R04, D-054.*

#### WLD-1-04 — A ground speed per level · MUST

Each level scrolls at its own ground speed (`ground_speed`), the fastest over the sea: 1-1 is the
fastest, 1-2 a little slower, 1-3 to 1-5 the slowest.

**Acceptance criteria**
- Given each World 1 level, then its `scrollSpeed` is the one in **Tunable values** (unit test on the data).

*Sources: GD-01, P06-R02, P06-R04.*

### Scenery

#### WLD-1-05 — Sea, green grass, desert · MUST

The five levels follow one gradient, each level a piece of it (sections, durations and what each
shows: in the level files):

| Level | Sea | Land | Habitations |
|-------|-----|------|-------------|
| 1-1 | Almost all sea, with small wooded green islands and reefs. The first coast comes in the last 30 s. | Small islands, then a green coast with beaches. | None on the islands; a fishing village and coast homes on the final coast. |
| 1-2 | It starts along the coast, with beaches and bays; the sea is gone after the first 110 s. | Green coastal land, then green meadows, groves and farmland, wooded. | Coastal villages along the coast road, then villages and farms. |
| 1-3 | No sea. | Farmland, woods and green hills; in the last minute the grass turns yellow, then dry. | Farms, villages and a market town with streets. |
| 1-4 | No sea. | Dry grassland, then the red desert: scrub, rock, a cracked dry lake, an oasis, a canyon and mesas. | Dry-land villages, desert homes and outposts, an oasis town and a desert town with streets. |
| 1-5 | No sea. | Red desert to the end: buttes, a rocky pass. | Desert homes and outposts, oasis villages, desert towns, then a great oasis town on dense streets to the end. |

**Acceptance criteria**
- Manual visual validation: the sea, then green grass, then the desert can be seen across the five levels.

*Sources: P06-R05, D-109, D-200.*

#### WLD-1-06 — The sea recedes · MUST

The share of each level that is over the sea goes down from 1-1 to 1-3 (`sea_share`): 1-1 is almost
all sea, 1-2 has sea only along its first sections, and 1-3, 1-4 and 1-5 have no sea at all (no sea
level, no shore).

**Acceptance criteria**
- Given the five level definitions, then 1-1 is at least 80 % over sea, 1-2 at most 50 %, and 1-3, 1-4 and 1-5 have no sea and no shore section (unit test).

*Sources: P06-R05.*

#### WLD-1-07 — Green first, then dry · MUST

Grass covers the ground of 1-2 and 1-3 more than any other cover, and the desert's cover (the
sections' `sandy` cover, drawn as red desert dirt in the dry levels, WLD-1-10) covers 1-4 and 1-5
more than grass (`cover_share`, by section time).

**Acceptance criteria**
- Given the five level definitions, then the grass share is the largest cover in 1-2 and 1-3, and the sandy share is larger than the grass share in 1-4 and 1-5 (unit test).

*Sources: P06-R05, D-109, D-200.*

#### WLD-1-08 — Each level begins where the previous one ended · MUST

Each level starts on the very section the previous level ended on, with the same relief, ground
cover, shore and building groups: 1-2 on the green coast 1-1 ends on, 1-3 on the farmland 1-2 ends
on, 1-4 on the dry grassland 1-3 ends on, and 1-5 on the desert outskirts 1-4 ends on.

**Acceptance criteria**
- Given two World 1 levels in a row, then the first section of the next one has the relief, cover, shore and groups of the last section of the previous one (unit test).
- Manual visual validation: each level begins where the previous one ended.

*Sources: P06-R05, D-109.*

#### WLD-1-09 — More and more buildings · MUST

The number of props placed (buildings and trees) and the number of buildings both go up from 1-1 to
1-5, and in each level the second half has more props than the first (each level's own seed).

**Acceptance criteria**
- Given the five levels placed with their seeds, then the number of buildings and the number of props go up strictly from 1-1 to 1-5, and each level's second half has more of them than its first (unit test).

**Discrepancy:** the buildings follow the rule (76 / 1 466 / 8 034 / 14 909 / 35 919, each second
half fuller), but since the woods of D-212 and D-214 the trees outnumber them: buildings and trees in
view are about 15 k / 199 k / 177 k / 19 k / 39 k, so the props go down from 1-2 to 1-4, and 1-3's
second half (the yellowing and dry grass) has fewer than its first.

*Sources: P06-R05, D-109.*

#### WLD-1-10 — An American desert, not sand dunes · MUST

The desert of 1-4 and 1-5 is an American desert: dried land, not sand. Its bare ground is a warm
dried brown earth; the sections' `sandy` cover is a red-orange dirt with dark pebbles and sage-grey
scrub; the low flats are the pale grey-pink hardpan of dry lakes, cracked into plates; the steep
ground (the walls of the mesas, buttes and canyon) is red rock in strong layers. No World 1 section
has sand dunes, and no snow ever lies on the flat tops of the mesas and buttes. Sand shows only on
the beaches of 1-1 and 1-2.

**Acceptance criteria**
- Given the World 1 sections, then none has dunes (unit test).
- Given the 1-4 and 1-5 looks, then their ground is dried earth, their sandy cover the desert dirt, their low ground the cracked hardpan, their steep ground the mesa rock, and their snow height out of reach (unit test).
- Manual visual validation: dried red land, cracked dry lakes, mesas and buttes; nothing like sand dunes.

*Sources: D-200, P06-R06.*

#### WLD-1-11 — No factory and no city · MUST

World 1 has no industrial zone, no heavy industry and no city centre: no section places the
industrial or heavy-industry building groups, and no section fills its blocks with towers. They are
for other worlds. The towns of World 1 are villages, a market town, oasis towns and desert towns.

**Acceptance criteria**
- Given the World 1 sections, then none lists the `industrial` or `heavy-industry` group and none has city blocks (unit test).

*Sources: P06-R05, P06-R06, D-109.*

#### WLD-1-12 — One ground for the world · MUST

The five levels share one ground, so the land fades from green to desert through the sections'
cover shares (`surface`): a dry olive earth by default, fresh green grass with a few yellow tufts as
the lush cover, a warm fine sand as the sandy cover of the beaches, pavement in the towns, and a
turquoise sea going from bright shallows to a deep blue. 1-4 and 1-5 use the dry ground of WLD-1-10
on the same covers.

**Acceptance criteria**
- Given the World 1 looks, then 1-1 to 1-3 share one terrain and 1-4 and 1-5 the dry one, and every look has every part the scenery reads (unit test).
- Manual visual validation: grass, sand and the sea read clearly from the playfield camera.

*Sources: P06-R06, D-109.*

#### WLD-1-13 — Building groups · MUST

Each section picks its buildings from World 1's building groups, all drawn from the buildings of the
grid of tiles ([buildings.md](../../graphics/buildings.md)); World 1 has no hand-made prop of its
own:

| Group | Models | Where |
|-------|--------|-------|
| `fishing` | the docks: containers, dock cranes, warehouses, tanks | 1-1's coast, 1-2's coast road |
| `coast-homes` | the homes of the future (homesteads) | the green coast, bays, coast farms |
| `villages` | the homes of the future (homesteads) | the bays, meadows, farmland, green hills, the market town, the drying grass |
| `farms` | the outposts: water towers, solar farms, radio masts, depots | coast farms, meadows, groves, farmland, woods, the yellowing grass |
| `desert-homes` | adobe homes and courtyard homes | the desert villages and towns |
| `outposts` | the outposts: water towers, solar farms, radio masts, depots | the dry grassland and the desert |

**Acceptance criteria**
- Given the World 1 sections, then every group they name is one of the props table (unit test), and each group has weighted models (unit test).

*Sources: P06-R06, D-207, D-160.*

#### WLD-1-14 — Woods on the grass, dead trees in the desert · MUST

Trees grow in woods wherever there is grass: every green section has tree density 1, so its grass
share sets how much is wooded, full on the green land, less on the coast, the islands, the market
town and the drying grass. The living woods are oaks, pines, birches, poplars, bushes and a few copper
beeches. The yellowing grass and the dry grassland are dying woods: living and dead trees mixed. The
desert sections grow sparse patches of dead trees (dead oaks, dead pines, snags and dry brush), a
few standing alone between them; the dry lake has only a lone dead tree here and there. How woods
are placed and drawn: [props.md](../../graphics/props.md).

**Acceptance criteria**
- Manual visual validation: woods on the green land of 1-1 to 1-3, dying woods where the grass dries, sparse dead trees in the desert.

*Sources: D-212, D-214, D-207.*

#### WLD-1-15 — Roads, lone buildings and hamlets · MUST

The World 1 levels use one road layout ([roads.md](../../graphics/roads.md)): two main roads, one
of them a two-by-two highway (one main road only in 1-1), paths branching off them, and no road
crossing another (only a path joining a road). A few lone buildings stand away from the roads, and
hamlets of 5 to 9 buildings come from time to time in sections with buildings and no street grid.
The towns are street grids on tiles.

**Acceptance criteria**
- Given a World 1 level, then no two roads cross on screen (unit test of the road rules).
- Manual visual validation: a few buildings away from the roads, and hamlets from time to time.

*Sources: D-046.*

### Light

#### WLD-1-16 — Later and later in the day · MUST

Each level has its own time of day, later level after level: midday in 1-1, early afternoon in 1-2,
late afternoon in 1-3, sunset in 1-4 and dusk in 1-5, with the town lights on. The sun is highest in
1-1 and lower in each level after it (`sun_elevation`). The time of day does not change within a
level, and no World 1 level has weather. Each level's light is in its level file.

**Acceptance criteria**
- Given the five looks, then the sun's elevation goes down strictly from 1-1 to 1-5 (unit test).
- Manual visual validation: the light and the shadows change from level to level, and the ships stay easy to see at sunset and dusk.

*Sources: P06-R10, D-109.*

### Enemies and difficulty

#### WLD-1-17 — A new kind or two in each level · MUST

The eleven basic enemy kinds are brought in over the world, so each level teaches something new.
Each level's waves, fillers included, use only these kinds:

| Level | Enemy kinds |
|-------|-------------|
| 1-1 | Gnat, Hornet, Scout, Strafer |
| 1-2 | the 1-1 kinds plus Weaver and Splitter |
| 1-3 | the 1-2 kinds plus Carrier and Spinner |
| 1-4 | the 1-3 kinds plus Lancer and Rocketeer |
| 1-5 | every basic kind, Bulwark included |

**Acceptance criteria**
- Given each World 1 wave script, then it only uses the kinds listed for its level, and the kinds new in each level appear in it (unit test).

*Sources: P06-R07.*

#### WLD-1-18 — Basic kinds only · MUST

No veteran or elite enemy kind ever comes in World 1: they are for Worlds 3 and 4.

**Acceptance criteria**
- Given the World 1 wave scripts, then they use none of the veteran or elite kinds (unit test).

*Sources: P05-R24.*

#### WLD-1-19 — Waves written as beats · MUST

Each World 1 level's waves are a list of beats written in seconds from the start of the level, for
readability: `[seconds, kind, groups, seconds between groups, side, position (0..1), spread]`. A
beat's seconds are turned into a distance at the level's ground speed, as waves are triggered by
distance ([level-flow.md](../../gameplay/level-flow.md)). A Gnat group is five Gnats; a group of any
other kind is one enemy. The scripts are data, the same at every play.

**Acceptance criteria**
- Given a beat at `t` seconds, then its wave is at `t × ground speed` (unit test).
- Given the same level played twice, then its waves come at the same distances with the same enemies (unit test).

*Sources: P06-R07.*

#### WLD-1-20 — Denser waves · MUST

Every beat brings `wave_density` times its groups, rounded half up. When a beat of one group gets
more, its extra groups come `density_gap` apart and, from the top, `density_spread` across the
screen (from a side, a little lower each), so they do not come in on top of each other. The beats
stay written as before (×1).

**Acceptance criteria**
- Given a beat of 3 groups, then the script has 5 (rounded half up); given a beat of one group, then it gets 2 groups 1.5 s apart and a spread (unit test).

*Sources: D-044.*

#### WLD-1-21 — Filler groups in the lulls · MUST

Light filler groups fill the lulls between the written beats, so the screen is seldom empty: after
each beat, one group from the top every `max_gap` seconds, the last at least half a gap before the
next beat. The filler's kinds come in turn and its entry positions alternate (`fill_positions`).
`max_gap` goes down from its start at the first beat to its end at the last, so each level fills up
as it goes. The density of WLD-1-20 applies to the fillers too. Each level's filler kinds and gaps
are in its level file.

**Acceptance criteria**
- Given beats with a long lull, then filler groups of the filler's kinds come in it, every `max_gap` seconds, and none comes within half a gap of the next beat (unit test).
- Given each World 1 filler, then its kinds are known kinds and its gap shrinks (unit test).

*Sources: D-051.*

#### WLD-1-22 — Each level harder than the one before · MUST

From 1-1 to 1-5, these go up strictly, level after level: the number of enemies spawned in the
level, their total HP, and the highest number of enemies on screen at the same time. They are
measured by a play-through with a ship that never fires, counting every enemy added (the Gnats a
Carrier launches included), and the most enemy centres over the playfield at once.

**Acceptance criteria**
- Given the five levels played through without shooting, then enemy count, total enemy HP and peak on screen go up strictly from 1-1 to 1-5 (unit test).
- Manual validation: 1-5 feels clearly harder than 1-1.

*Sources: P06-R08, D-038, D-044, D-051.*

#### WLD-1-23 — Enemy bullet speed and fire rate · MUST

Each level sets two factors on the basic enemy values: the enemy bullet speed and the enemy fire
rate (`bullet_speed_factor`, `fire_rate_factor`). Neither ever goes down from 1-1 to 1-5, and from
level to level at least one goes up.

**Acceptance criteria**
- Given the World 1 difficulty table, then each factor never goes down from 1-1 to 1-5 (unit test).

*Sources: P06-R08, D-038.*

#### WLD-1-24 — Harder second halves · MUST

Within each level the waves get harder from the start to the end: the second half of a level has
more total enemy HP than its first half.

**Acceptance criteria**
- Given each World 1 level, then the HP of the enemies spawned in its second half is more than in its first half (unit test).

*Sources: P06-R08, D-051.*

#### WLD-1-25 — 1-1 is easy, even for a kid · MUST

1-1 is the gentlest level of the game: its filler groups are only Hornets and Gnats, which do not
shoot, and its enemy factors the lowest (0.8). Its bosses stay beatable for a kid.

**Acceptance criteria**
- Given the 1-1 filler, then it brings only Hornets and Gnats (unit test).
- Manual validation: 1-1 feels easy, even for a kid.

*Sources: P06-R08, P07-R10, D-051.*

### Bosses

#### WLD-1-26 — Ten bosses, two in each level · MUST

Each World 1 level has its own mini boss, at the middle of its length, and its own final boss, at
its end: ten different bosses, none used twice in the world.

| Level | Mini boss | Final boss |
|-------|-----------|------------|
| 1-1 | [Reef Warden](../../bosses/mini/1-1-reef-warden.md) | [Storm Petrel](../../bosses/final/1-1-storm-petrel.md) |
| 1-2 | [Breakwater](../../bosses/mini/1-2-breakwater.md) | [Gull Mothership](../../bosses/final/1-2-gull-mothership.md) |
| 1-3 | [Dust Devil](../../bosses/mini/1-3-dust-devil.md) | [Mesa Fortress](../../bosses/final/1-3-mesa-fortress.md) |
| 1-4 | [Scorpion](../../bosses/mini/1-4-scorpion.md) | [Refinery Titan](../../bosses/final/1-4-refinery-titan.md) |
| 1-5 | [Sentinel](../../bosses/mini/1-5-sentinel.md) | [Overlord](../../bosses/final/1-5-overlord.md) |

**Acceptance criteria**
- Given each World 1 level, then it names one mini boss and one final boss of the game, two different bosses, and no boss is used in two World 1 levels (unit test).

*Sources: GD-41, P07-R05, P07-R06.*

#### WLD-1-27 — Boss health grows across the world · MUST

Like the levels, the bosses get harder from 1-1 to 1-5. A boss's full health is that of its core and
every part, its hidden weapons included (the full length of its health bar,
[bosses/common.md](../../bosses/common.md)):
- the full health of the mini bosses goes up strictly from 1-1 to 1-5, and so does that of the final bosses;
- each final boss has more full health than its level's mini boss.

**Acceptance criteria**
- Given the ten World 1 bosses, then mini boss full health and final boss full health each go up strictly from 1-1 to 1-5, and each final boss has more than its level's mini boss (unit test).
- Manual validation: the 1-1 bosses feel easy, the 1-5 bosses clearly harder.

**Discrepancy:** with the hidden weapons of D-221 counted (as the health bar counts them), the
final bosses go 10 420 / 9 740 / 15 000 / 19 210 / 22 760: the Gull Mothership (1-2) has less than
the Storm Petrel (1-1). Counting only the core and the parts there from the start, the orders hold
(mini 2 200 / 2 600 / 3 090 / 3 660 / 3 910, final 5 770 / 5 960 / 8 100 / 12 690 / 15 780). No unit
test checks these orders since the Python port.

*Sources: P07-R10, D-055.*

#### WLD-1-28 — Boss bullets follow the level · MUST

A boss's bullets use its level's enemy bullet speed and fire rate factors (WLD-1-23), like the
enemies'.

**Acceptance criteria**
- Given a level's difficulty factors, then the bosses fought in it get the same bullet speed and fire rate factors as its enemies (unit test).

*Sources: P07-R10.*

#### WLD-1-29 — Boss fight times · MUST

With the balanced ship, guns at level 3, always firing at the boss, each fight lasts within
`mini_fight_time` and `final_fight_time`, longer from 1-1 to 1-5.

**Acceptance criteria**
- Given a simulated fight of each World 1 boss (balanced ship, guns level 3, always on target), then it lasts within the ranges of **Tunable values** (unit test).

*Sources: P07-R10, D-055.*

### Music

#### WLD-1-30 — World 1's music · MUST

The World 1 levels play World 1's music style ([music.md](../../audio/music.md)): the outrun drive
of darksynth, a heavy four-on-the-floor kick, a gated snare, a pumping eighth-note saw bass, dark
pads, plucked arpeggios and a saw lead, in minor, harmonic minor or phrygian keys, at
`music_tempo`. Each level has its own track, generated from its id (`level-1-1` …); the World 1
bosses share one boss track (`boss-1`), faster and tenser, in the same instruments.

**Acceptance criteria**
- Given a World 1 level, then its track is its own and uses World 1's style; given a World 1 boss fight, then the track is `boss-1` (unit test).
- Manual validation by ear: the World 1 tracks sound alike and differ from the other worlds'.

*Sources: P12-R06, P12-R07, D-098, D-099, D-100.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| level_duration | 240 s ± 10 s (every level is exactly 240 s) | WLD-1-03; sections' `seconds` in `src/game/config/world_1/scenery_*.py` |
| ground_speed 1-1 / 1-2 / 1-3 / 1-4 / 1-5 | 70 / 65 / 60 / 60 / 60 units/s | WLD-1-04; `LEVEL_1_x.scrollSpeed` |
| section_transition | 420 units | sections blend over this length; `transition` |
| sea_share 1-1 / 1-2 / 1-3 / 1-4 / 1-5 | ≥ 80 % / ≤ 50 % / 0 / 0 / 0 | WLD-1-06; measured 90 % / 18 % (ground under the sea level, x −240…240, each level's seed); 1-1 has 210 s of water sections, 1-2 110 s of shore sections |
| cover_share (lush / sandy) | 0.71 / 0.03 · 0.92 / 0.08 · 0.79 / 0 · 0.07 / 0.69 · 0.08 / 0.84 | WLD-1-07; share of section time, 1-1 … 1-5 |
| sun_elevation 1-1 / 1-2 / 1-3 / 1-4 / 1-5 | 72° / 55° / 35° / 14° / 8° | WLD-1-16; `src/game/config/world_1/looks.py` |
| time_of_day 1-1 / 1-2 / 1-3 / 1-4 / 1-5 | midday / early afternoon / late afternoon / sunset / dusk | WLD-1-16 |
| bullet_speed_factor 1-1 / 1-2 / 1-3 / 1-4 / 1-5 | 0.8 / 0.85 / 0.9 / 1.0 / 1.1 | WLD-1-23; `src/game/config/world_1/difficulty.py` `WORLD_1_DIFFICULTY` |
| fire_rate_factor 1-1 / 1-2 / 1-3 / 1-4 / 1-5 | 0.8 / 0.85 / 0.9 / 1.0 / 1.1 | WLD-1-23; same |
| wave_density | 1.5 | WLD-1-20; `src/game/config/world_1/waves.py` `WAVE_DENSITY` |
| density_gap / density_spread | 1.5 s / 0.3 (from a side: −0.15) | WLD-1-20; `DENSITY_GAP`, `DENSITY_SPREAD` |
| fill_positions | 0.3, 0.7, 0.5, 0.2, 0.8 | WLD-1-21; `FILL_POSITIONS` |
| max_gap 1-1 … 1-5 | 4.5 → 3 / 3.5 → 2.4 / 3.3 → 2.2 / 3.2 → 2 / 3 → 1.6 s | WLD-1-21; `WORLD_1_FILLERS` |
| enemies written 1-1 … 1-5 | 265 / 321 / 339 / 372 / 401 | WLD-1-22; from the scripts, density and fillers in, Carrier launches and Splitter pods out |
| enemy HP written 1-1 … 1-5 | 4 290 / 6 100 / 8 140 / 11 250 / 15 400 (halves 1 890 / 2 400 · 2 680 / 3 420 · 3 760 / 4 380 · 4 750 / 6 500 · 6 140 / 9 260) | WLD-1-22, WLD-1-24; same count |
| measured with Carrier launches | 1-3: 104.8 enemies and 2 235 HP a minute; 1-5: 130.3 and 4 150 | D-067 (play-through without shooting, seed 606) |
| peak_on_screen (last measured) | 16 / 20 / 24 / 30 / 32 | D-051, before the boss phase; the old tunables (6 … 15) and enemy counts (~60 … ~140) are superseded by the reviewer's denser waves (D-044, D-051) |
| boss full health, mini 1-1 … 1-5 | 3 200 / 3 900 / 4 090 / 4 760 / 5 150 (core and original parts: 2 200 / 2 600 / 3 090 / 3 660 / 3 910) | WLD-1-27; `src/game/config/bosses/mini_bosses.py` |
| boss full health, final 1-1 … 1-5 | 10 420 / 9 740 / 15 000 / 19 210 / 22 760 (core and original parts: 5 770 / 5 960 / 8 100 / 12 690 / 15 780) | WLD-1-27; `src/game/config/bosses/final_bosses.py` |
| mini_fight_time 1-1 → 1-5 | 25–35 s → 40–50 s | WLD-1-29; measured 30 / 33 / 38 / 43 / 44 s (D-055, before the hidden weapons) |
| final_fight_time 1-1 → 1-5 | 50–70 s → 90–120 s | WLD-1-29; measured 59 / 72 / 82 / 92 / 104 s (D-055, same) |
| music_tempo | 128–140 BPM; the boss track 20–30 BPM faster | WLD-1-30; `src/game/view/audio/music_styles.py` `WORLD_STYLES[1]` |
| hamlets / lone buildings | hamlets every 700–1 400 units, 5–9 buildings within 32, 2 apart, 18 from the roads; lone buildings one per 150-unit square at chance 0.15 × density, 18 from the roads | WLD-1-15; `src/game/config/world_1/props.py` `WORLD_1_PROPS` |
| roads | 2 main roads (1-1: 1), spread 200, paths every 260–560 units, no crossing within 30 | WLD-1-15; `WORLD_1_ROADS` |
| world tone | 0.55 | the ground and props darkened for readability ([readability.md](../../graphics/readability.md)) |

## Notes

- History: World 1 was first drafted as the open sea, a dry coast, then desert, desert towns and a
  desert city (2026-10-24). The reviewer reworked it into one gradient, sea → green grass → desert
  (2026-10-26, D-109), then had 1-5 end in the desert, with no factory or city (2026-10-27), and the
  desert turned into an American desert without sand dunes (2026-10-30, D-200). The bosses were
  named before the rework, so some (the Dust Devil, the Mesa Fortress over 1-3's green country) fly
  over greener land than they were named for.
- The hand-made World 1 props (desert homes, huts, palms, cacti, farmhouses, greenhouses, grain
  silos, wind turbines) and the lone huts and masts of 1-1's islands are gone (D-207); the groups
  draw from the grid's buildings, and the trees came back as woods of imposters (D-212, D-214).
- The `industrial` and `heavy-industry` groups are still defined in `WORLD_1_PROPS` but no section
  uses them (WLD-1-11).
- The dry grassland where 1-3 ends and 1-4 begins is the same section in both, but 1-3 draws its bare
  ground with the olive dry earth and 1-4 with D-200's warmer dried earth.
- The progression checks of the old phase 6 (sea share, cover shares, continuity, props growth,
  kinds per level, strict difficulty increases, sun lower each level) and the boss orderings and fight
  times of P07-R10 have no unit test since the Python port; the counts above were measured from the
  configs for this file.
