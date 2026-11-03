# 1-2 Green coast

> **Area:** Worlds · **Prefix:** `LVL-1-2` · **Related:** [World 1](world.md), [1-1 Open sea](1-1-open-sea.md), [1-3 Green country](1-3-green-country.md), [Breakwater](../../bosses/mini/1-2-breakwater.md), [Gull Mothership](../../bosses/final/1-2-gull-mothership.md), [level flow](../../gameplay/level-flow.md), [terrain](../../graphics/terrain.md), [sky and light](../../graphics/sky-and-light.md)

The second level of World 1: early afternoon along the green coast where 1-1 ended, its beaches and
bays, then inland over green meadows, groves and farmland once the sea is gone. The Lancer
joins the 1-1 kinds. The Breakwater waits at the middle and the Gull Mothership at the end.

## Requirements

### Identity

#### LVL-1-2-01 — Identity · MUST

Level `1-2` is the second level of World 1. It is named "Green coast"; its scenery is `world-1-2`,
generated from the seed `seed`.

**Acceptance criteria**
- Given the game's levels, then the second is `1-2`, named "1-2 Green coast", with the scenery `world-1-2` and its seed (unit test).

*Sources: P06-R05, D-109.*

#### LVL-1-2-02 — Duration and ground speed · MUST

1-2 scrolls at `ground_speed` for `duration`: its sections' seconds add up to 240, so its length is
15 600 units. Its sections blend over 420 units.

**Acceptance criteria**
- Given 1-2, then its length ÷ its ground speed is 240 s (unit test, e2e).

*Sources: P06-R04, GD-01, D-109.*

#### LVL-1-2-03 — Early afternoon · MUST

1-2 is in the early afternoon, the whole level long:
- the sun a little lower than in 1-1 (`sun`) and a little warmer;
- a blue sky with a warmer horizon, a cool ambient light (`ambient`);
- two layers of scattered white clouds, a little thinner than 1-1's (`clouds`);
- the fog of the base look (`fog`), no ground lights, no weather.

**Acceptance criteria**
- Given the 1-2 look, then its sun is lower than 1-1's and higher than 1-3's (unit test, WLD-1-16).

*Sources: P06-R10, D-109.*

### Scenery

#### LVL-1-2-04 — Sections · MUST

1-2's ground is these sections, in this order (relief: height above the sea level 0, ± its
amplitude, features about that wide across; scarps: the hills with one rocky face of WLD-1-31,
their height / wavelength):

| # | Section | Seconds | Relief | Cover | Buildings (density) | What it shows |
|---|---------|---------|--------|-------|---------------------|---------------|
| 1 | coast road | 40 | 16 ± 10, 480, scarps 28 / 340 | grass 0.8, sand 0.2 | fishing, coast homes (0.5) | 1-1's green coast: the shore, beaches, a fishing village along the coast road. |
| 2 | bays | 40 | 22 ± 14, 460, scarps 28 / 340 | grass 0.8, sand 0.2 | coast homes, villages (0.55) | Deeper bays along a more winding shore. |
| 3 | coast farms | 30 | 24 ± 14, 460, scarps 36 / 340 | grass 0.9, sand 0.1 | coast homes, farms (0.5) | The last of the sea, the shore moving away to the left. |
| 4 | meadows | 45 | 24 ± 10, 600, scarps 36 / 340 | grass 1 | villages, farms (0.5) | Green meadows, wooded. |
| 5 | groves | 40 | 30 ± 16, 480, scarps 40 / 340 | grass 1 | farms (0.45) | Rolling land with groves and farms. |
| 6 | farmland | 45 | 26 ± 8, 620, scarps 24 / 360 | grass 1 | farms, villages (0.6) | Flat farmland, where 1-3 begins. |

**Acceptance criteria**
- Given 1-2, then its sections are these, in this order, with these seconds (unit test on the data).
- Given 1-1's last section and 1-2's first, then they have the same relief, cover, shore and groups (unit test, WLD-1-08).
- Manual visual validation: `?level=1-2&t=0` the coast, `&t=150` the meadows.

*Sources: P06-R05, D-109.*

#### LVL-1-2-05 — The sea goes · MUST

1-2 has a sea at level 0, only along its first three sections (its first 110 s): their shore winds
along the level, the sea on the left, each one further left than the one before (`shore`), so the
land takes more and more of the screen; after them the sea is gone. 1-2 is at most 50 % over the
sea (WLD-1-06).

**Acceptance criteria**
- Given 1-2, then only its first three sections have a shore, each further from the middle than the one before (unit test on the data).

*Sources: P06-R05, D-109.*

#### LVL-1-2-06 — Buildings and roads · MUST

1-2's habitations are coastal villages along the coast road, then villages and farms in the
meadows (the groups of the table above, WLD-1-13), with a few lone buildings and hamlets
(WLD-1-15). It has World 1's two main roads.

**Acceptance criteria**
- Given 1-2 placed with its seed, then it has more buildings than 1-1 and fewer than 1-3, and its second half more than its first (unit test, WLD-1-09).

*Sources: P06-R05, P06-R06, D-207, D-046.*

#### LVL-1-2-07 — Woods · MUST

Every 1-2 section grows living woods on its grass (tree density 1, the living trees, WLD-1-14):
full on the meadows, groves and farmland, less on the coast.

**Acceptance criteria**
- Manual visual validation: the green land is wooded, with clearings.

*Sources: D-212, D-214.*

### Waves

#### LVL-1-2-08 — Enemy kinds · MUST

1-2 adds the Lancer to the 1-1 kinds (Hornet, Scout and Lancer), in its beats and its fillers, and uses no other kind.

**Acceptance criteria**
- Given the 1-2 wave script, then it only uses Hornet, Scout and Lancer, and it uses each of them (unit test).

*Sources: P06-R07, ENM-50.*

#### LVL-1-2-09 — Wave plan · MUST

1-2's waves are composed from this plan (WLD-1-19; the density of WLD-1-20 applies on top):

Beats from 4 s to 226 s, one every 6 s at the start down to 4.3 s at the end, groups growing by 65 % over the level (44 beats, the last at 224.9 s). The phrases, in their cycle:

| # | Kind | Groups | Between groups (s) | Side | Position | Spread |
|---|------|--------|--------------------|------|----------|--------|
| 1 | Hornet | 4 | 0.8 | top | 0.15 | 0.23 |
| 2 | Scout | 3 | 1.2 | top | 0.25 | 0.25 |
| 3 | Lancer | 2 | 2.5 | top | 0.25 | 0.5 |
| 4 | Hornet | 4 | 0.8 | top | 0.85 | -0.23 |
| 5 | Scout | 3 | 1.2 | top | 0.75 | -0.25 |
| 6 | Hornet | 4 | 0.8 | top | 0.15 | 0.23 |
| 7 | Lancer | 2 | 2.5 | top | 0.75 | -0.5 |
| 8 | Scout | 3 | 1.2 | top | 0.25 | 0.25 |

No wave starts in the 10 s before each boss ([level-flow.md](../../gameplay/level-flow.md)).

**Acceptance criteria**
- Given the 1-2 plan, then it composes beats that name its kinds and sides in order of time (unit test).

*Sources: P06-R07, D-067, ENM-50.*

#### LVL-1-2-10 — Filler · MUST

1-2's filler (WLD-1-21) brings the level's divers and shooters, Hornet, Scout, Hornet, Scout, in turn, one group every `max_gap`.

**Acceptance criteria**
- Given the 1-2 filler, then its kinds are the Hornet and the Scout only and its gap shrinks (unit test).

*Sources: D-051, ENM-50.*

### Difficulty

#### LVL-1-2-11 — Difficulty · MUST

1-2's enemies fire at `fire_rate_factor` of their rate and their bullets fly at
`bullet_speed_factor` of their speed. It has more enemies, more enemy HP and a higher peak on
screen than 1-1, fewer than 1-3 (WLD-1-22), its second half more than its first.

**Acceptance criteria**
- Given the 1-2 difficulty, then both factors are 0.85 (unit test).

*Sources: P06-R08, D-038.*

### Bosses

#### LVL-1-2-12 — Mini boss: Breakwater · MUST

The [Breakwater](../../bosses/mini/1-2-breakwater.md) comes at the middle of 1-2's length
(7 800 units, 2:00). Destroying it saves the level's checkpoint
([level-flow.md](../../gameplay/level-flow.md)).

**Acceptance criteria**
- Given 1-2, then its mini boss is the Breakwater, at half its length (unit test).

*Sources: GD-41, GD-42, P07-R05, P07-R06.*

#### LVL-1-2-13 — Final boss: Gull Mothership · MUST

The [Gull Mothership](../../bosses/final/1-2-gull-mothership.md) comes at the end of 1-2's length
(15 600 units, 4:00); destroying it completes the level.

**Acceptance criteria**
- Given 1-2, then its final boss is the Gull Mothership, at its length (unit test).

*Sources: GD-41, P07-R05, P07-R06.*

#### LVL-1-2-14 — Runout · MUST

`runout` seconds of the last section's ground (the farmland) are drawn past the level's end, for
the ground that gets ahead of the level during the fights.

**Acceptance criteria**
- Given 1-2, then its runout is 80 s (unit test on the data).

*Sources: D-054.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| seed | 1201 | `src/game/config/world_1/scenery_coast.py` `LEVEL_1_2` |
| ground_speed | 65 units/s | `LEVEL_1_2.scrollSpeed` |
| duration | 240 s (15 600 units) | sum of the sections' `seconds` |
| sun | elevation 55°, azimuth 35°, colour (1, 0.93, 0.82), intensity 1.65 | `src/game/config/world_1/looks.py` `LEVEL_1_2_LOOK` |
| sky | haze (0.74, 0.8, 0.86), horizon (0.9, 0.88, 0.84), zenith (0.26, 0.46, 0.78), environment 0.7 | same |
| ambient | sky (0.66, 0.74, 0.86), ground (0.34, 0.36, 0.28), intensity 0.62 | same |
| clouds | low 0.3, high 0.18, white | same |
| fog | 1 000 → 2 600 | the base look's |
| shore | coast road x −40 ± 90 every 1 800; bays x −90 ± 170 every 1 500; coast farms x −230 ± 110 every 1 700 (beach 240, sea bed −55) | `GREEN_COAST`, `GREEN_COAST_LEVEL` |
| max_gap | 3.5 s → 2.4 s | `src/game/config/world_1/waves.py` `WORLD_1_FILLERS["1-2"]` |
| bullet_speed_factor / fire_rate_factor | 0.85 / 0.85 | `src/game/config/world_1/difficulty.py` |
| written | 44 beats from the plan; waves, groups, enemies and HP after fill and density: to be measured again with the new kinds | `src/game/config/wave_plans.py` `level_plan(1, 2)`; density 2 (D-249) |
| buildings | 1 466 (halves 681 / 785) | each level's seed, measured for this file |
| mini boss / final boss | `breakwater` / `gull-mothership` | `src/game/config/world_1/bosses.py` |
| runout | 80 s | same |

## Notes

- Before D-109 (2026-10-26), 1-2 was a dry coast giving way to sand and rock.
