# 1-5 Deep desert

> **Area:** Worlds · **Prefix:** `LVL-1-5` · **Related:** [World 1](world.md), [1-4 Dry lands](1-4-dry-lands.md), [2-1 Great erg](../world-2/2-1-great-erg.md), [Sentinel](../../bosses/mini/1-5-sentinel.md), [Overlord](../../bosses/final/1-5-overlord.md), [level flow](../../gameplay/level-flow.md), [terrain](../../graphics/terrain.md), [sky and light](../../graphics/sky-and-light.md)

The last and hardest level of World 1: dusk over the deep desert, from the desert outskirts 1-4
ended on, past buttes, oasis villages and a rocky pass, into desert towns ever bigger and denser, to
a great oasis town on the red land at the end, its lights on. No sea, no factory, no city. Every
basic kind comes, Bulwarks included. The Sentinel waits at the middle and the Overlord at the end.

## Requirements

### Identity

#### LVL-1-5-01 — Identity · MUST

Level `1-5` is the fifth and last level of World 1. It is named "Deep desert"; its scenery is
`world-1-5`, generated from the seed `seed`.

**Acceptance criteria**
- Given the game's levels, then the fifth is `1-5`, named "1-5 Deep desert", with the scenery `world-1-5` and its seed (unit test).

*Sources: P06-R05, D-109.*

#### LVL-1-5-02 — Duration and ground speed · MUST

1-5 scrolls at `ground_speed` for `duration`: its sections' seconds add up to 240, so its length is
14 400 units. Its sections blend over 420 units.

**Acceptance criteria**
- Given 1-5, then its length ÷ its ground speed is 240 s (unit test, e2e).

*Sources: P06-R04, GD-01, D-109.*

#### LVL-1-5-03 — Dusk, the town lights on · MUST

1-5 is at dusk, the whole level long:
- the sun on the horizon (`sun`), red-orange, low but still lighting the ground (in a darker dusk the
  ship was lost over the towns);
- a violet sky over a red horizon, a strong violet ambient light (`ambient`);
- few clouds, tinted pink and violet (`clouds`);
- the window, street and car lights on and bright (`ground_lights`), with a stronger glow (`glow`);
  no weather.

**Acceptance criteria**
- Given the 1-5 look, then its sun is the lowest of World 1 (unit test, WLD-1-16).
- Manual visual validation: dusk over the desert towns, their lights on, and the ships, enemies, shots and bonuses stay easy to see over them.

*Sources: P06-R10, D-109.*

### Scenery

#### LVL-1-5-04 — Sections · MUST

1-5's ground is these sections, in this order (relief: height ± its amplitude, features about that
wide across; scarps: the hills with one rocky face of WLD-1-31, their height / wavelength, on the
open land only); there is no sea. The cover is the sections' `sandy` cover, drawn as the red desert dirt
(WLD-1-10); where a section's covers add up to less than 1, the dried earth shows.

| # | Section | Seconds | Relief | Cover | Buildings (density) | What it shows |
|---|---------|---------|--------|-------|---------------------|---------------|
| 1 | desert outskirts | 30 | 30 ± 8, 560, scarps 24 / 360 | sandy 0.85 | desert homes, outposts (1) | 1-4's desert outskirts. |
| 2 | buttes | 25 | 35 ± 160, 450, cut at 70 | sandy 1 | outposts (0.45) | Buttes and mesas standing out of a cracked dry floor. |
| 3 | oasis villages | 40 | 28 ± 12, 520 | sandy 0.7, grass 0.3 | desert homes, outposts (1), streets | Oasis villages on street grids, a little grass. |
| 4 | rocky pass | 20 | 60 ± 30, 420, scarps 40 / 320 | sandy 1 | outposts (0.7) | A rocky pass through higher ground. |
| 5 | desert towns | 55 | 28 ± 6, 560 | sandy 0.85, paved 0.1 | desert homes, outposts (1), streets | Desert towns on street grids. |
| 6 | great oasis town | 70 | 30 ± 4, 600 | sandy 0.8, grass 0.1, paved 0.1 | desert homes (1), dense streets | A great oasis town on dense streets to the end. |

**Acceptance criteria**
- Given 1-5, then its sections are these, in this order, with these seconds (unit test on the data).
- Given 1-4's last section and 1-5's first, then they have the same relief, cover and groups (unit test, WLD-1-08).
- Manual visual validation: `?level=1-5&t=38` the buttes, `&t=200` the great oasis town.

*Sources: P06-R05, D-109, D-200.*

#### LVL-1-5-05 — Buttes and the great oasis town · MUST

- The buttes are a steep, high relief squashed flat under a top height: about a fifth of the ground
  is flat tops, about a fifth the cracked hardpan of the floor, with steep red walls between; no snow
  on their tops and no sand dunes anywhere (WLD-1-10).
- The great oasis town keeps 1-5 the fullest level of World 1: its streets are denser than the other
  towns' (`great_town_streets`), every block filled with desert homes.
- 1-5 ends in the desert: no factory, no industry, no city (WLD-1-11).

**Acceptance criteria**
- Given the buttes' relief, then it is smooth and its top height is under its base plus its amplitude (unit test).
- Given 1-5's sections, then none has dunes and none lists the industrial or heavy-industry group (unit test).

*Sources: D-200, D-109, P06-R05.*

#### LVL-1-5-06 — Buildings and roads · MUST

1-5's habitations are desert homes and outposts, oasis villages, desert towns and the great oasis
town (the groups of the table above, WLD-1-13), with a few lone buildings and hamlets (WLD-1-15),
more than in any other World 1 level. It has World 1's two main roads.

**Acceptance criteria**
- Given 1-5 placed with its seed, then it has more buildings than 1-4, and its second half more than its first (unit test, WLD-1-09).

*Sources: P06-R05, P06-R06, D-109, D-207, D-046.*

#### LVL-1-5-07 — Dead trees · MUST

The desert sections grow sparse patches of dead trees with a few standing alone (`desert_woods`,
WLD-1-14); almost none in the towns, whose buildings take the ground. 1-5 grows no living tree.

**Acceptance criteria**
- Manual visual validation: pale dead trees in patches between the towns.

*Sources: D-214.*

### Waves

#### LVL-1-5-08 — Enemy kinds · MUST

1-5 brings every basic kind, the Bulwark for the first time: Gnat, Hornet, Scout, Strafer, Weaver,
Splitter, Carrier, Spinner, Lancer, Rocketeer, Bulwark, in its beats and its fillers.

**Acceptance criteria**
- Given the 1-5 wave script, then it uses all eleven basic kinds and no other (unit test).

*Sources: P06-R07.*

#### LVL-1-5-09 — Written beats · MUST

1-5's waves are these beats, as written (WLD-1-19; the density of WLD-1-20 applies on top). They
leave the stretch from 104 s to 130 s to the fillers, around the mini boss at 120 s, and no wave
starts in the 10 s before each boss ([level-flow.md](../../gameplay/level-flow.md)).

| s | Kind | Groups | Between groups (s) | Side | Position | Spread |
|---|------|--------|--------------------|------|----------|--------|
| 4 | Scout | 4 | 1 | top | 0.15 | 0.23 |
| 10 | Gnat | 2 | 2 | top | 0.3 | 0.4 |
| 16 | Bulwark | 1 | 0 | top | 0.5 | — |
| 24 | Hornet | 5 | 0.7 | top | 0.1 | 0.2 |
| 30 | Weaver | 3 | 1.2 | top | 0.3 | 0.2 |
| 36 | Lancer | 2 | 2 | top | 0.25 | 0.5 |
| 44 | Rocketeer | 2 | 2.5 | top | 0.3 | 0.4 |
| 50 | Strafer | 3 | 1.5 | left | 0.8 | — |
| 56 | Splitter | 3 | 2 | top | 0.2 | 0.3 |
| 64 | Spinner | 2 | 2.5 | top | 0.3 | 0.4 |
| 70 | Carrier | 1 | 0 | top | 0.5 | — |
| 78 | Bulwark | 1 | 0 | top | 0.35 | — |
| 84 | Scout | 4 | 0.8 | top | 0.15 | 0.23 |
| 92 | Lancer | 3 | 1.5 | top | 0.2 | 0.3 |
| 98 | Gnat | 3 | 1.5 | top | 0.2 | 0.3 |
| 104 | Rocketeer | 2 | 2 | top | 0.3 | 0.4 |
| 130 | Bulwark | 2 | 4 | top | 0.3 | 0.4 |
| 134 | Hornet | 5 | 0.6 | top | 0.1 | 0.2 |
| 140 | Spinner | 2 | 2.5 | top | 0.7 | -0.4 |
| 146 | Carrier | 1 | 0 | top | 0.4 | — |
| 152 | Weaver | 4 | 1 | top | 0.2 | 0.2 |
| 158 | Strafer | 3 | 1.5 | right | 0.8 | — |
| 164 | Lancer | 3 | 1.5 | top | 0.2 | 0.3 |
| 170 | Rocketeer | 3 | 2 | top | 0.2 | 0.3 |
| 176 | Splitter | 3 | 1.5 | top | 0.2 | 0.3 |
| 182 | Bulwark | 2 | 3 | top | 0.3 | 0.4 |
| 188 | Gnat | 3 | 1.5 | top | 0.2 | 0.3 |
| 194 | Carrier | 1 | 0 | top | 0.6 | — |
| 200 | Scout | 5 | 0.6 | top | 0.1 | 0.2 |
| 206 | Spinner | 3 | 2 | top | 0.2 | 0.3 |
| 212 | Hornet | 5 | 0.5 | top | 0.1 | 0.2 |
| 218 | Lancer | 3 | 1.2 | top | 0.2 | 0.3 |
| 222 | Rocketeer | 2 | 1.5 | top | 0.3 | 0.4 |
| 226 | Bulwark | 1 | 0 | top | 0.5 | — |

**Acceptance criteria**
- Given the 1-5 beats, then each names a kind and a side, in order of time (unit test).

*Sources: P06-R07, D-044.*

#### LVL-1-5-10 — Filler · MUST

1-5's filler (WLD-1-21) brings Gnat, Weaver, Hornet, Scout, Splitter, Spinner, in turn, one group
every `max_gap`, the tightest of World 1.

**Acceptance criteria**
- Given the 1-5 filler, then its kinds are those six and its gap shrinks (unit test).

*Sources: D-051.*

### Difficulty

#### LVL-1-5-11 — The hardest level of World 1 · MUST

1-5's enemies fire at `fire_rate_factor` of their rate and their bullets fly at
`bullet_speed_factor` of their speed, the highest of World 1. It has the most enemies, the most
enemy HP and the highest peak on screen of World 1 (WLD-1-22), its second half more than its first.
World 2 ends harder than it (WLD-2-23).

**Acceptance criteria**
- Given the 1-5 difficulty, then both factors are 1.1 (unit test).
- Manual validation: 1-5 feels clearly harder than 1-1.

*Sources: P06-R08, P08-R09, D-038.*

### Bosses

#### LVL-1-5-12 — Mini boss: Sentinel · MUST

The [Sentinel](../../bosses/mini/1-5-sentinel.md) comes at the middle of 1-5's length
(7 200 units, 2:00), over the desert towns. Destroying it saves the level's checkpoint
([level-flow.md](../../gameplay/level-flow.md)).

**Acceptance criteria**
- Given 1-5, then its mini boss is the Sentinel, at half its length (unit test).

*Sources: GD-41, GD-42, P07-R05, P07-R06.*

#### LVL-1-5-13 — Final boss: Overlord · MUST

The [Overlord](../../bosses/final/1-5-overlord.md) comes at the end of 1-5's length (14 400 units,
4:00), over the great oasis town; destroying it completes the level and World 1, and the level
select then highlights `2-1` (WLD-1-02).

**Acceptance criteria**
- Given 1-5, then its final boss is the Overlord, at its length (unit test).
- Given `?level=1-5&boss=final`, when the Overlord is destroyed and Confirm pressed, then `level-select` shows with `2-1` highlighted (e2e).

*Sources: GD-41, P07-R05, P07-R06, P08-R01.*

#### LVL-1-5-14 — Runout · MUST

`runout` seconds of the last section's ground (the great oasis town) are drawn past the level's
end, for the ground that gets ahead of the level during the fights.

**Acceptance criteria**
- Given 1-5, then its runout is 75 s (unit test on the data).

*Sources: D-054.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| seed | 1501 | `src/game/config/world_1/scenery_desert.py` `LEVEL_1_5` |
| ground_speed | 60 units/s | `LEVEL_1_5.scrollSpeed` |
| duration | 240 s (14 400 units) | sum of the sections' `seconds` |
| sun | elevation 8°, azimuth 30°, colour (1, 0.56, 0.4), intensity 1.6 | `src/game/config/world_1/looks.py` `LEVEL_1_5_LOOK` |
| sky | haze (0.7, 0.48, 0.6), horizon (0.96, 0.5, 0.42), zenith (0.2, 0.16, 0.4), environment 0.6 | same |
| ambient | sky (0.66, 0.58, 0.82), ground (0.44, 0.34, 0.34), intensity 1 | same |
| fog | 1 000 → 2 600 | same |
| clouds | low 0.15, high 0.1, colour (0.9, 0.56, 0.6), shade (0.46, 0.3, 0.46) | same |
| ground_lights / glow | prop light intensity 1.3 / glow 0.4 | same |
| ground | `DRY_TERRAIN` (as 1-4) | `looks.py` (D-200) |
| buttes | base 35, amplitude 160, 1/450, 4 octaves, cut at 70 | `buttes(70)` |
| great_town_streets | rows 45–90, columns 50–110, links 0.6 | `DEEP_DESERT`; the other towns use 1-3's `town_streets` |
| desert_woods | cover 0.55, keep 0.15, scatter 0.01 | `src/game/config/trees.py` |
| max_gap | 3 s → 1.6 s | `src/game/config/world_1/waves.py` `WORLD_1_FILLERS["1-5"]` |
| bullet_speed_factor / fire_rate_factor | 1.1 / 1.1 | `src/game/config/world_1/difficulty.py` |
| written | 34 beats; 94 waves and 304 groups after fill and density; 448 enemies, 17 420 HP (halves 6 940 / 10 480), Carrier launches not counted | measured from the configs (density 2, D-249) |
| buildings | 35 919 (halves 8 618 / 27 301) | each level's seed, measured for this file |
| mini boss / final boss | `sentinel` / `overlord` | `src/game/config/world_1/bosses.py` |
| runout | 75 s | same |

## Notes

- Before the 2026-10-27 amendment of D-109, 1-5 was a desert city with factories at its end; then
  "Deep desert" with great dunes, which became the buttes in D-200 (2026-10-30).
- The busiest moment of World 1 for the frame rate is 1-5's end: the most enemies on screen over the
  great oasis town ([performance.md](../../performance.md)).
