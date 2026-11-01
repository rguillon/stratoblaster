# World 2 — The Industrial Desert

> **Area:** Worlds · **Prefix:** `WLD-2` · **Related:** [2-1 Great erg](2-1-great-erg.md), [2-2 Mining mesas](2-2-mining-mesas.md), [2-3 Oil fields](2-3-oil-fields.md), [2-4 Industrial belt](2-4-industrial-belt.md), [2-5 Factory district](2-5-factory-district.md), [World 1](../world-1/world.md), [level flow](../../gameplay/level-flow.md), [level select](../../ui/level-select.md), [music](../../audio/music.md), [terrain](../../graphics/terrain.md), [sky and light](../../graphics/sky-and-light.md), [weather](../../graphics/weather.md), [buildings](../../graphics/buildings.md), [roads](../../graphics/roads.md), [enemies](../../enemies/common.md), [bosses](../../bosses/common.md)

World 2, the Industrial Desert, has five levels of about five minutes, cut from one long journey: it
starts in the deep desert where World 1 ended, and the desert is slowly taken over by industry,
mines first, then oil fields, refineries, an industrial belt and dense factories at the end. The
changes are slow. There is no sea in World 2. Each level has its own time of day, three day levels,
then dusk, then night. World 2 uses the eleven basic enemy kinds in harder mixes, and as a whole it
is harder than World 1. This file holds what the five levels share; each level's own content is in
its level file. World 2 is built with World 1's rules where nothing else is said: its beats,
density and fillers ([World 1](../world-1/world.md)), its roads.

## Requirements

### Identity

#### WLD-2-01 — The Industrial Desert, five levels · MUST

World 2 is called the Industrial Desert. It has five levels, in this order and with these names:
`2-1` Great erg, `2-2` Mining mesas, `2-3` Oil fields, `2-4` Industrial belt, `2-5` Factory
district. The five levels are one journey from the desert to the factories (WLD-2-05). There is no
other level in World 2.

**Acceptance criteria**
- Given the game's levels, then World 2 is exactly `2-1` … `2-5`, in this order, each named as above (unit test).

*Sources: P08-R03, D-110.*

#### WLD-2-02 — Second row of the level select · MUST

World 2 is the second row of the level select grid: `2-1` to `2-5`, all unlocked from a fresh start
(the grid and its rules: [level-select.md](../../ui/level-select.md)). After `1-5` is completed the
level select highlights `2-1`; after a World 2 level, the next one, and `3-1` after `2-5`.

**Acceptance criteria**
- Given `level-select`, then the second row shows exactly `2-1` … `2-5`, none locked, and each starts its level (e2e).
- Given `2-1` is completed, then `level-select` shows with `2-2` highlighted (e2e).

*Sources: P08-R01, D-089.*

#### WLD-2-03 — About five minutes a level · MUST

Each World 2 level lasts about 5 minutes: its scroll time, its length divided by its ground speed, is
`level_duration`. The boss fights add to the time played.

**Acceptance criteria**
- Given each World 2 level, then its length ÷ its ground speed is between 290 s and 310 s (e2e on the level's `duration`).

*Sources: P08-R02.*

#### WLD-2-04 — A ground speed per level · MUST

Each level scrolls at its own ground speed (`ground_speed`): fastest over the open sand of 2-1,
slowest over the dense industrial belt of 2-4.

**Acceptance criteria**
- Given each World 2 level, then its `scrollSpeed` is the one in **Tunable values** (unit test on the data).

*Sources: GD-01, P08-R02.*

### Scenery

#### WLD-2-05 — From the desert to the factories · MUST

The five levels follow one gradient, each level a piece of it (sections, durations and what each
shows: in the level files):

| Level | Land | Habitations |
|-------|------|-------------|
| 2-1 | Open sand to the end: an oasis edge, great dunes, a dune field, then rocky desert. | Oasis homes and caravan outposts, then desert outposts; the first mines in the last 30 s. |
| 2-2 | Rocky desert, mesas and a canyon, the sand trodden around the mines. | Mines and their outposts, a mining town with streets, open pits, then the first oil wells at the end. |
| 2-3 | Flat sand and rock, more and more of it paved. | Oil fields, a company town, refineries and tank farms, the first factories at the end. |
| 2-4 | Mostly paved ground, a little sand left between the plots. | Workers' suburbs, warehouses and yards with streets, a power plant, factory yards, then a factory district. |
| 2-5 | Paved to the end. | Factories and foundries along streets, rail yards, heavy industry, then great works filling every block. |

**Acceptance criteria**
- Manual visual validation: desert, mines, oil fields, refineries and factories follow each other across the five levels, and the changes are slow.

*Sources: P08-R03, D-110.*

#### WLD-2-06 — No sea; rivers allowed · MUST

No World 2 level has open sea: no sea level, no shore, no sea-bed section and no floating ice.
Rivers (channels cut in the ground) are allowed, as long as no open sea, coast or shore comes with
them.

**Acceptance criteria**
- Given the World 2 levels, then none has a sea, a shore section, a sea-bed section or floating props (unit test); a channel is allowed.

*Sources: P08-R03, D-110.*

#### WLD-2-07 — Sand gives way to concrete · MUST

The share of the ground covered by sand goes down strictly from 2-1 to 2-5 and the paved share goes
up strictly (`cover_share`, by section time): sand covers more of the ground than pavement in 2-1
and 2-2, pavement more than sand in 2-4 and 2-5, and the two are about even in 2-3.

**Acceptance criteria**
- Given the five level definitions, then the sand share goes down strictly and the paved share up strictly from 2-1 to 2-5, sand > pavement in 2-1 and 2-2, pavement > sand in 2-4 and 2-5 (unit test).

*Sources: P08-R03, D-110.*

#### WLD-2-08 — Slow transitions · MUST

The changes along World 2 are slow, three ways:
- the sections blend over `section_transition`, about 15 s of scrolling, twice World 1's;
- the ground cover goes from sand to concrete in small steps, a little in each section;
- each new building group first comes in mixed with the one before it, before it takes over: outposts and desert homes, then outposts and mines, mines, mines and worker homes, mines and oil, oil, oil and worker homes, oil and refineries, refineries, refineries and industry, industry and worker homes, industry, industry and heavy industry, heavy industry.

**Acceptance criteria**
- Given the World 2 levels, then their sections blend over a longer stretch than World 1's (unit test).
- Given two sections in a row, then a building group new in the second is mixed with one of the first's (unit test).

*Sources: P08-R03, D-110.*

#### WLD-2-09 — Industry in its order · MUST

The industrial and heavy-industry groups never come in 2-1, and 2-5 ends on heavy industry only.

**Acceptance criteria**
- Given 2-1's sections, then none lists the industrial or heavy-industry group; given 2-5's last section, then it lists only heavy industry (unit test).

*Sources: P08-R03.*

#### WLD-2-10 — Each level begins where the previous one ended · MUST

Each level starts on the very section the previous level ended on, with the same relief, ground
cover and building groups: 2-2 on the prospect mines 2-1 ends on, 2-3 on the oil edge 2-2 ends on,
2-4 on the industrial edge 2-3 ends on, and 2-5 on the factory district 2-4 ends on. 2-1 starts in
the deep desert, at an oasis edge, as World 1 ended at a great oasis town.

**Acceptance criteria**
- Given two World 2 levels in a row, then the first section of the next one has the relief, cover and groups of the last section of the previous one (unit test).
- Manual visual validation: each level begins where the previous one ended.

*Sources: P08-R03, D-110.*

#### WLD-2-11 — More and more buildings · MUST

The number of props placed and the number of buildings go up from 2-1 to 2-5, and in each level the
second half has more props than the first (each level's own seed). World 2 grows no trees, so its
props are its buildings.

**Acceptance criteria**
- Given the five levels placed with their seeds, then the number of buildings goes up strictly from 2-1 to 2-5 and each level's second half has more than its first (unit test).

*Sources: P08-R03, D-110, D-164.*

#### WLD-2-12 — Desert ground under the concrete · MUST

The five levels share one ground: World 1's desert ground slowly covered by the stained concrete
of the industry. It is a dry olive earth by default, a warm fine sand as the sandy cover and on the
low ground, red-brown layered desert rock on the cliffs only (the mesas and canyon walls; the lee
sides of the dunes stay sand), and, as the paved cover, a grey industrial concrete stained with oil
and soot, sand blown into its cracks. Sand dunes stay in World 2 (World 1's desert lost its own,
D-200).

**Acceptance criteria**
- Given the World 2 looks, then they share one terrain whose paved cover is the industrial concrete, and every look has every part the scenery reads (unit test).
- Manual visual validation: the sand and the paved industrial ground read clearly, and the slow change from desert to factories shows.

*Sources: P08-R07, D-110.*

#### WLD-2-13 — Building groups · MUST

Each section picks its buildings from World 2's building groups, all drawn from the buildings of the
grid of tiles ([buildings.md](../../graphics/buildings.md)). No frozen prop (snow, ice, polar
buildings) and no tree stands in World 2.

| Group | Models | Weight |
|-------|--------|--------|
| `w2-desert-homes` | adobe homes and courtyard homes | 3 |
| `w2-outposts` | water towers, solar farms, radio masts, depots | 2 |
| `w2-mines` | the industrial models: mine headframes, ore silos, mine works, pumpjacks, oil tanks, flares, tanks, refineries, factories, warehouses, containers, cooling towers | 2 |
| `w2-worker-homes` | the homes of the future (homesteads) | 3 |
| `w2-oil` | the industrial models | 2 |
| `w2-refinery` | the industrial models | 2 |
| `w2-industrial` | the industrial models | 3 |
| `w2-heavy-industry` | foundries and plants | 1 |

**Acceptance criteria**
- Given the World 2 sections, then every group they name is one of the props table, each group has weighted models, and no section grows trees (unit test).

*Sources: P08-R07, D-110, D-160, D-163.*

#### WLD-2-14 — Roads and hamlets as in World 1 · MUST

The World 2 levels use World 1's roads (two main roads, paths, no road crossing another), its lone
buildings and its hamlets (WLD-1-15). The towns and works are street grids on tiles.

**Acceptance criteria**
- Given a World 2 level, then its road rules are World 1's (unit test).

*Sources: P08-R03, D-046.*

### Light

#### WLD-2-15 — A time of day per level · MUST

Each level has its own time of day, from the engine's presets ([sky-and-light.md](../../graphics/sky-and-light.md)):
three day levels, morning (2-1), midday (2-2) and afternoon (2-3), then dusk (2-4), then night
(2-5). The time of day does not change within a level. From 2-3 on, the smoke of the industry greys
the clouds a little more in each level (`storm`). The window, street and car lights are off in the
day levels and on at dusk and at night.

**Acceptance criteria**
- Given each World 2 level, then its look sets the time of day and the cloud cover of its level file, and no change within the level (unit test on the data).
- Given 2-1, 2-4 and 2-5 (e2e), then the ground lights are under 0.5 in 2-1, higher at dusk in 2-4, over 1 at night in 2-5, and the sun is weaker at night than in the morning.
- Manual visual validation: each time of day reads at once, and the ships, enemies, shots and bonuses stay easy to see at dusk and at night.

*Sources: P08-R04, P08-R06, D-110.*

#### WLD-2-16 — No weather · MUST

No World 2 level has weather: no snow, no rain, no falling ash and no aurora (snow and the aurora
belonged to the Frozen North World 2 was first drafted as).

**Acceptance criteria**
- Given each World 2 level, then its look has no weather and no aurora, and no weather particle is drawn (unit test on the data, e2e on 2-1 and 2-5).

*Sources: P08-R05, P08-R06, D-110.*

### Enemies and difficulty

#### WLD-2-17 — The kinds that lead the waves · MUST

World 2 uses the eleven basic enemy kinds. Each level puts its weight on some of them, and its waves,
fillers included, use only these kinds:

| Level | Enemy kinds |
|-------|-------------|
| 2-1 | Gnat, Hornet, Scout, Strafer, Weaver, over the dunes |
| 2-2 | the 2-1 kinds plus Splitter and Lancer, over the mines |
| 2-3 | every basic kind, with Carrier and Spinner groups over the oil fields |
| 2-4 | every basic kind, with Rocketeers and Bulwarks over the industrial belt |
| 2-5 | every basic kind, the heaviest mixes: Bulwarks and Carriers together |

**Acceptance criteria**
- Given each World 2 wave script, then it only uses the kinds listed for its level, and 2-3 to 2-5 use all eleven (unit test).

*Sources: P08-R08.*

#### WLD-2-18 — Basic kinds only · MUST

No veteran or elite enemy kind ever comes in World 2: they are for Worlds 3 and 4.

**Acceptance criteria**
- Given the World 2 wave scripts, then they use none of the veteran or elite kinds (unit test).

*Sources: P05-R24.*

#### WLD-2-19 — Waves composed from a plan · MUST

Each World 2 level's waves are composed from its plan, not written beat by beat: a cycle of phrases
(`[kind, groups, seconds between groups, side, position (0..1), spread]`), one beat every `gap`
seconds from `from` to `to`, each beat the next phrase of the cycle. The gap shrinks from its first
value at the start to its second at the end, so the level fills up as it goes, and the groups grow by
`growth` over the level (rounded half up), so the second half carries more enemy HP. The beats then
go through World 1's density and filler (WLD-1-19 to WLD-1-21) and the quiet stretch before each
boss ([level-flow.md](../../gameplay/level-flow.md)). The composition is deterministic. Each level's
plan and filler are in its level file.

**Acceptance criteria**
- Given a plan, then it composes beats that name known kinds and sides, in order of time, from `from` to `to` (unit test).
- Given the same plan composed twice, then the beats are the same (unit test).

*Sources: P08-R08, D-067.*

#### WLD-2-20 — Each level harder per minute · MUST

From 2-1 to 2-5, these go up strictly, level after level: the enemies spawned per minute of scroll,
their total HP per minute, and the highest number of enemies on screen at the same time, measured as
in World 1 (WLD-1-22: a play-through without shooting, Carrier launches counted).

**Acceptance criteria**
- Given the five levels played through without shooting, then enemies per minute, HP per minute and peak on screen go up strictly from 2-1 to 2-5 (unit test).
- Manual validation: the difficulty clearly goes up from 2-1 to 2-5.

*Sources: P08-R09, D-067.*

#### WLD-2-21 — Enemy bullet speed and fire rate · MUST

Each level sets an enemy bullet speed factor and an enemy fire rate factor (`bullet_speed_factor`,
`fire_rate_factor`). Neither ever goes down from 2-1 to 2-5.

**Acceptance criteria**
- Given the World 2 difficulty table, then each factor never goes down from 2-1 to 2-5 (unit test).

*Sources: P08-R09.*

#### WLD-2-22 — Harder second halves · MUST

In each World 2 level, the second half has more total enemy HP than the first half.

**Acceptance criteria**
- Given each World 2 level, then the HP of the enemies spawned in its second half is more than in its first half (unit test).

*Sources: P08-R09.*

#### WLD-2-23 — World 2 goes on from World 1 · MUST

World 2 continues where World 1 ended, with a short breather: 2-1 is at least as hard as 1-3, and
2-5 is harder than 1-5, on enemies per minute, HP per minute, the bullet speed factor and the fire
rate factor. 2-1 may be easier than 1-5.

**Acceptance criteria**
- Given the measures of WLD-1-22 and WLD-2-20, then 2-1 ≥ 1-3 and 2-5 > 1-5 on each of them (unit test).
- Manual validation: 2-1 feels close to the middle of World 1, a fresh start rather than a wall.

*Sources: P08-R09.*

### Bosses

#### WLD-2-24 — Ten bosses, two in each level · MUST

Each World 2 level has its own mini boss, at the middle of its length, and its own final boss, at
its end: ten different bosses, none used twice in the world, none used in World 1.

| Level | Mini boss | Final boss |
|-------|-----------|------------|
| 2-1 | [Floe Breaker](../../bosses/mini/2-1-floe-breaker.md) | [Narwhal](../../bosses/final/2-1-narwhal.md) |
| 2-2 | [Fjord Lynx](../../bosses/mini/2-2-fjord-lynx.md) | [Harbour Kraken](../../bosses/final/2-2-harbour-kraken.md) |
| 2-3 | [Snow Owl](../../bosses/mini/2-3-snow-owl.md) | [Aurora Station](../../bosses/final/2-3-aurora-station.md) |
| 2-4 | [Avalanche](../../bosses/mini/2-4-avalanche.md) | [Glacier Colossus](../../bosses/final/2-4-glacier-colossus.md) |
| 2-5 | [Ice Queen](../../bosses/mini/2-5-ice-queen.md) | [Boreal Citadel](../../bosses/final/2-5-boreal-citadel.md) |

Within World 2, at least one fight stops the ground (the Harbour Kraken) and at least one is a chase
(the Narwhal, the Avalanche).

**Acceptance criteria**
- Given each World 2 level, then it names one mini boss and one final boss of the game, two different bosses, and no boss is used in two levels (unit test).

*Sources: GD-41, P08-R10.*

#### WLD-2-25 — Boss health grows across the world · MUST

As in World 1 (WLD-1-27, full health counted the same way):
- the full health of the mini bosses goes up strictly from 2-1 to 2-5, and so does that of the final bosses;
- each final boss has more full health than its level's mini boss;
- each World 2 boss has more full health than the World 1 boss of the same level and rank (the 2-k mini boss more than the 1-k mini boss, the 2-k final boss more than the 1-k final boss).

**Acceptance criteria**
- Given the twenty bosses of Worlds 1 and 2, then the orders above hold (unit test).
- Manual validation: the World 2 bosses feel harder than the World 1 ones, and the 2-5 ones the hardest so far.

**Discrepancy:** with the hidden weapons of D-221 counted (as the health bar counts them), the mini
bosses go 3 760 / 3 840 / 5 590 / 5 240 / 5 540 (the Avalanche and the Ice Queen under the Snow
Owl), the final bosses 10 460 / 10 240 / 13 100 / 19 840 / 26 960 (the Harbour Kraken under the
Narwhal); the Fjord Lynx (3 840) is under the Breakwater (3 900) and the Aurora Station (13 100)
under the Mesa Fortress (15 000). Counting only the core and the parts there from the start, every
order holds (mini 2 720 / 2 880 / 3 550 / 3 800 / 4 200, final 6 500 / 7 000 / 8 600 / 13 000 /
17 500). No unit test checks these orders since the Python port.

*Sources: P08-R11, D-068.*

#### WLD-2-26 — Boss bullets follow the level · MUST

A boss's bullets use its level's enemy bullet speed and fire rate factors (WLD-2-21), like the
enemies'.

**Acceptance criteria**
- Given a level's difficulty factors, then the bosses fought in it get the same bullet speed and fire rate factors as its enemies (unit test).

*Sources: P08-R11.*

#### WLD-2-27 — Boss fight times · MUST

With the balanced ship, guns at level 3, always firing at the boss, each fight lasts within
`mini_fight_time` and `final_fight_time`, longer from 2-1 to 2-5.

**Acceptance criteria**
- Given a simulated fight of each World 2 boss (balanced ship, guns level 3, always on target), then it lasts within the ranges of **Tunable values** (unit test).

*Sources: P08-R11, D-068.*

### Music

#### WLD-2-28 — World 2's music · MUST

The World 2 levels play World 2's music style ([music.md](../../audio/music.md)): the dreamwave
flavour of darksynth, a heavy kick on a driving backbeat with a gated snare, a soft eighth-note
bass, dreamy pads, glassy arpeggios and a bell lead, in minor, harmonic minor or phrygian keys, at
`music_tempo`. Each level has its own track, generated from its id (`level-2-1` …); the World 2
bosses share one boss track (`boss-2`), faster and tenser, in the same instruments.

**Acceptance criteria**
- Given a World 2 level, then its track is its own and uses World 2's style; given a World 2 boss fight, then the track is `boss-2` (unit test).
- Manual validation by ear: the World 2 tracks sound alike and differ from the other worlds'.

*Sources: P12-R06, P12-R07, D-098, D-099, D-100.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| level_duration | 300 s ± 10 s (every level is exactly 300 s) | WLD-2-03; sections' `seconds` in `src/game/config/world_2/scenery.py` |
| ground_speed 2-1 / 2-2 / 2-3 / 2-4 / 2-5 | 70 / 65 / 60 / 55 / 60 units/s | WLD-2-04; `LEVEL_2_x.scrollSpeed` |
| section_transition | 900 units (about 15 s; World 1: 420) | WLD-2-08; `TRANSITION` |
| sea_share | 0 % in every level | WLD-2-06 |
| cover_share sand 2-1 … 2-5 | 0.89 / 0.67 / 0.39 / 0.17 / 0.05 | WLD-2-07; share of section time |
| cover_share paved 2-1 … 2-5 | 0.005 / 0.14 / 0.40 / 0.67 / 0.89 | WLD-2-07 |
| buildings 2-1 … 2-5 | 1 384 / 12 834 / 24 278 / 33 137 / 33 934 (halves 525 / 859 · 5 005 / 7 829 · 10 287 / 13 991 · 13 499 / 19 638 · 16 196 / 17 738) | WLD-2-11; placed with each level's seed, lots included, measured for this file |
| time_of_day 2-1 / 2-2 / 2-3 / 2-4 / 2-5 | morning / midday / afternoon / dusk / night | WLD-2-15; `src/game/config/world_2/looks.py` |
| storm (smog) 2-1 … 2-5 | 0 / 0 / 0.15 / 0.3 / 0.35 | WLD-2-15 |
| bullet_speed_factor 2-1 … 2-5 | 0.9 / 0.95 / 1.0 / 1.1 / 1.15 | WLD-2-21; `src/game/config/world_2/difficulty.py` `WORLD_2_DIFFICULTY` |
| fire_rate_factor 2-1 … 2-5 | 0.9 / 0.95 / 1.0 / 1.1 / 1.15 | WLD-2-21; same |
| plan growth | 0.6 (groups 60 % bigger at the end) | WLD-2-19; every plan of `src/game/config/world_2/waves.py` |
| enemies per minute 2-1 … 2-5 | 116.8 / 120.4 / 121.4 / 172.0 / 233.4 | WLD-2-20; D-067, play-through without shooting, seed 606 (World 1: 1-3 104.8, 1-5 130.3) |
| HP per minute 2-1 … 2-5 | 2 466 / 3 384 / 3 666 / 6 016 / 7 360 | WLD-2-20; D-067 (World 1: 1-3 2 235, 1-5 4 150) |
| peak_on_screen 2-1 … 2-5 | 22 / 23 / 36 / 37 / 51 measured (the old tunable 10 / 11 / 13 / 15 / 17, superseded as in World 1) | WLD-2-20; D-067 |
| enemy HP written, halves 2-1 … 2-5 | 5 140 / 7 190 · 6 520 / 10 400 · 6 620 / 9 910 · 10 980 / 16 900 · 13 000 / 19 000 | WLD-2-22; from the scripts, Carrier launches out |
| boss full health, mini 2-1 … 2-5 | 3 760 / 3 840 / 5 590 / 5 240 / 5 540 (core and original parts: 2 720 / 2 880 / 3 550 / 3 800 / 4 200) | WLD-2-25; `src/game/config/bosses/world_2/*.py` |
| boss full health, final 2-1 … 2-5 | 10 460 / 10 240 / 13 100 / 19 840 / 26 960 (core and original parts: 6 500 / 7 000 / 8 600 / 13 000 / 17 500) | WLD-2-25; same |
| mini_fight_time 2-1 → 2-5 | 30–40 s → 45–55 s | WLD-2-27; measured 32.8 / 40.3 / 41.1 / 45.4 / 51.3 s (D-068, before the hidden weapons) |
| final_fight_time 2-1 → 2-5 | 60–80 s → 100–130 s | WLD-2-27; measured 66.7 / 86.7 / 97.0 / 108.0 / 113.6 s (D-068, same) |
| music_tempo | 112–124 BPM; the boss track 20–30 BPM faster | WLD-2-28; `src/game/view/audio/music_styles.py` `WORLD_STYLES[2]` |
| world tone | 0.45 | the ground and props darkened for readability ([readability.md](../../graphics/readability.md)) |

## Notes

- History: World 2 was first drafted and built as the Frozen North (a cold sea with ice floes,
  fjords, a tundra, a glacier and a polar city at night, with snow, a blizzard and an aurora,
  2026-10-25). The reviewer reworked it into the Industrial Desert on 2026-10-27 (D-110), with no
  sea and rivers allowed. The bosses and their names were kept, so the frost-themed bosses (Floe
  Breaker, Narwhal, Harbour Kraken, Snow Owl, Glacier Colossus, Ice Queen, Boreal Citadel…) fly over
  the desert and the factories, and the music style chosen for the Frozen North (cold, glassy bells)
  was kept too. The frozen props were removed (D-163); the engine tools made for them (snow, the
  aurora, floating ice, lakes, crevasses) stay in the engine.
- Since the grid of tiles (phase 15, reviewer, 2026-10-28), the mines, the oil fields, the
  refineries and the industrial works draw from one group of industrial models, so the `w2-mines`,
  `w2-oil`, `w2-refinery` and `w2-industrial` groups differ only by weight: the slow change of
  WLD-2-08 shows through the ground cover, the streets and the homes more than through the works.
  The oil pumpjack of the old P08-R07 is now one of these tile models.
- 2-1's look is World 2's (sand dunes, D-200 kept them here), so the step from 1-5's red desert dirt
  to 2-1's sand is a change of ground between the two worlds.
- The progression checks of the old phase 8 (no sea, sand and paved shares, groups, props growth,
  continuity, kinds per level, the per-minute increases, the cross-world comparisons) and the boss
  orderings and fight times of P08-R11 have no unit test since the Python port; the counts above were
  measured from the configs for this file.
