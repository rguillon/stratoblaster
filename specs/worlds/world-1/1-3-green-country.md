# 1-3 Green country

> **Area:** Worlds · **Prefix:** `LVL-1-3` · **Related:** [World 1](world.md), [1-2 Green coast](1-2-green-coast.md), [1-4 Dry lands](1-4-dry-lands.md), [Dust Devil](../../bosses/mini/1-3-dust-devil.md), [Mesa Fortress](../../bosses/final/1-3-mesa-fortress.md), [level flow](../../gameplay/level-flow.md), [terrain](../../graphics/terrain.md), [sky and light](../../graphics/sky-and-light.md)

The third level of World 1: a golden late afternoon over the green country, from the farmland 1-2
ended on, through woods, green hills and a market town, to where the grass turns yellow and dry.
No sea. The Rocketeer joins the 1-2 kinds. The Dust Devil waits at the middle and the Mesa
Fortress at the end.

## Requirements

### Identity

#### LVL-1-3-01 — Identity · MUST

Level `1-3` is the third level of World 1. It is named "Green country"; its scenery is `world-1-3`,
generated from the seed `seed`.

**Acceptance criteria**
- Given the game's levels, then the third is `1-3`, named "1-3 Green country", with the scenery `world-1-3` and its seed (unit test).

*Sources: P06-R05, D-109.*

#### LVL-1-3-02 — Duration and ground speed · MUST

1-3 scrolls at `ground_speed` for `duration`: its sections' seconds add up to 240, so its length is
14 400 units. Its sections blend over 420 units.

**Acceptance criteria**
- Given 1-3, then its length ÷ its ground speed is 240 s (unit test, e2e).

*Sources: P06-R04, GD-01, D-109.*

#### LVL-1-3-03 — Late afternoon · MUST

1-3 is in the late afternoon, the whole level long:
- a golden sun, lower than 1-2's (`sun`), with longer shadows;
- a warm haze and horizon under a blue zenith, a warmer ambient light (`ambient`);
- two layers of thin clouds tinted warm (`clouds`);
- the fog of the base look (`fog`), no ground lights, no weather.

**Acceptance criteria**
- Given the 1-3 look, then its sun is lower than 1-2's and higher than 1-4's (unit test, WLD-1-16).
- Manual visual validation: golden light and long shadows over the green land.

*Sources: P06-R10, D-109.*

### Scenery

#### LVL-1-3-04 — Sections · MUST

1-3's ground is these sections, in this order (relief: height ± its amplitude, features about that
wide across; scarps: the hills with one rocky face of WLD-1-31, their height / wavelength); there is
no sea:

| # | Section | Seconds | Relief | Cover | Buildings (density) | What it shows |
|---|---------|---------|--------|-------|---------------------|---------------|
| 1 | farmland | 30 | 26 ± 8, 620, scarps 24 / 360 | grass 1 | farms, villages (0.6) | 1-2's farmland. |
| 2 | woods | 35 | 34 ± 18, 460, scarps 38 / 330 | grass 1 | farms (0.4) | Rolling wooded land, a few farms. |
| 3 | green hills | 35 | 46 ± 36, 420, scarps 40 / 320 | grass 1 | villages (0.5) | Green hills, the highest relief of the level. |
| 4 | farmland | 50 | 26 ± 8, 620, scarps 24 / 360 | grass 1 | farms, villages (0.75) | Farmland again, more built. |
| 5 | market town | 30 | 28 ± 4, 600, no scarps | grass 0.65, paved 0.3 | villages (1), streets | A market town on a street grid. |
| 6 | yellowing grass | 30 | 28 ± 10, 560, scarps 32 / 360 | grass 0.5 | villages, farms (0.7) | The grass turns yellow; dying woods. |
| 7 | dry grassland | 30 | 28 ± 10, 560, scarps 32 / 360 | grass 0.2 | villages, outposts (0.75) | A little grass left on the dry earth, where 1-4 begins. |

**Acceptance criteria**
- Given 1-3, then its sections are these, in this order, with these seconds (unit test on the data).
- Given 1-2's last section and 1-3's first, then they have the same relief, cover and groups (unit test, WLD-1-08).
- Manual visual validation: `?level=1-3&t=60` woods and hills, `&t=165` the market town, `&t=225` the dry grassland.

*Sources: P06-R05, D-109.*

#### LVL-1-3-05 — The market town and the drying grass · MUST

The market town has streets on a grid of tiles with wide blocks (`town_streets`), its ground part
paved. After it the grass share falls, 0.5 then 0.2, so the dry olive earth of World 1's ground
shows through: the green country ends dry and yellow.

**Acceptance criteria**
- Given 1-3's sections, then only the market town has streets, and the grass share of its last two sections is 0.5 then 0.2 (unit test on the data).
- Manual visual validation: the grass yellows, then dries, at the end of the level.

*Sources: P06-R05, D-109.*

#### LVL-1-3-06 — Buildings and roads · MUST

1-3's habitations are farms, villages and the market town (the groups of the table above,
WLD-1-13), with a few lone buildings and hamlets (WLD-1-15), more than in 1-2. It has World 1's two
main roads.

**Acceptance criteria**
- Given 1-3 placed with its seed, then it has more buildings than 1-2 and fewer than 1-4, and its second half more than its first (unit test, WLD-1-09).

*Sources: P06-R05, P06-R06, D-207, D-046.*

#### LVL-1-3-07 — Woods, then dying woods · MUST

The first five sections grow living woods on their grass (tree density 1, the living trees); the
yellowing grass and the dry grassland grow dying woods, living and dead trees mixed (WLD-1-14).

**Acceptance criteria**
- Manual visual validation: green woods, then dying woods where the grass dries.

*Sources: D-212, D-214.*

### Waves

#### LVL-1-3-08 — Enemy kinds · MUST

1-3 adds the Rocketeer to the 1-2 kinds (Hornet, Scout, Lancer and Rocketeer), in its beats and its fillers, and uses no other kind.

**Acceptance criteria**
- Given the 1-3 wave script, then it only uses Hornet, Scout, Lancer and Rocketeer, and it uses each of them (unit test).

*Sources: P06-R07, ENM-50.*

#### LVL-1-3-09 — Wave plan · MUST

1-3's waves are composed from this plan (WLD-1-19; the density of WLD-1-20 applies on top):

Beats from 4 s to 226 s, one every 5.6 s at the start down to 4 s at the end, groups growing by 70 % over the level (47 beats, the last at 224.6 s). The phrases, in their cycle:

| # | Kind | Groups | Between groups (s) | Side | Position | Spread |
|---|------|--------|--------------------|------|----------|--------|
| 1 | Hornet | 4 | 0.8 | top | 0.15 | 0.23 |
| 2 | Scout | 3 | 1.2 | top | 0.25 | 0.25 |
| 3 | Lancer | 2 | 2.5 | top | 0.25 | 0.5 |
| 4 | Hornet | 4 | 0.8 | top | 0.85 | -0.23 |
| 5 | Rocketeer | 1 | 0 | top | 0.5 | — |
| 6 | Scout | 3 | 1.2 | top | 0.75 | -0.25 |
| 7 | Hornet | 4 | 0.8 | top | 0.15 | 0.23 |
| 8 | Lancer | 2 | 2.5 | top | 0.75 | -0.5 |
| 9 | Scout | 3 | 1.2 | top | 0.25 | 0.25 |
| 10 | Rocketeer | 1 | 0 | top | 0.5 | — |

No wave starts in the 10 s before each boss ([level-flow.md](../../gameplay/level-flow.md)).

**Acceptance criteria**
- Given the 1-3 plan, then it composes beats that name its kinds and sides in order of time (unit test).

*Sources: P06-R07, D-067, ENM-50.*

#### LVL-1-3-10 — Filler · MUST

1-3's filler (WLD-1-21) brings the level's divers and shooters, Hornet, Scout, Hornet, Scout, in turn, one group every `max_gap`.

**Acceptance criteria**
- Given the 1-3 filler, then its kinds are the Hornet and the Scout only and its gap shrinks (unit test).

*Sources: D-051, ENM-50.*

### Difficulty

#### LVL-1-3-11 — Difficulty · MUST

1-3's enemies fire at `fire_rate_factor` of their rate and their bullets fly at
`bullet_speed_factor` of their speed. It has more enemies, more enemy HP and a higher peak on
screen than 1-2, fewer than 1-4 (WLD-1-22), its second half more than its first. It sets the bar
World 2 starts from (WLD-2-23).

**Acceptance criteria**
- Given the 1-3 difficulty, then both factors are 0.9 (unit test).

*Sources: P06-R08, P08-R09, D-038.*

### Bosses

#### LVL-1-3-12 — Mini boss: Dust Devil · MUST

The [Dust Devil](../../bosses/mini/1-3-dust-devil.md) comes at the middle of 1-3's length
(7 200 units, 2:00). Destroying it saves the level's checkpoint
([level-flow.md](../../gameplay/level-flow.md)).

**Acceptance criteria**
- Given 1-3, then its mini boss is the Dust Devil, at half its length (unit test).

*Sources: GD-41, GD-42, P07-R05, P07-R06.*

#### LVL-1-3-13 — Final boss: Mesa Fortress · MUST

The [Mesa Fortress](../../bosses/final/1-3-mesa-fortress.md) comes at the end of 1-3's length
(14 400 units, 4:00), over the dry grassland, the ground stopped under it; destroying it completes
the level.

**Acceptance criteria**
- Given 1-3, then its final boss is the Mesa Fortress, at its length (unit test).

*Sources: GD-41, P07-R05, P07-R06.*

#### LVL-1-3-14 — Runout · MUST

`runout` seconds of the last section's ground (the dry grassland) are drawn past the level's end,
the shortest of World 1: its final fight stops the ground.

**Acceptance criteria**
- Given 1-3, then its runout is 30 s (unit test on the data).

*Sources: D-054.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| seed | 1301 | `src/game/config/world_1/scenery_country.py` `LEVEL_1_3` |
| ground_speed | 60 units/s | `LEVEL_1_3.scrollSpeed` |
| duration | 240 s (14 400 units) | sum of the sections' `seconds` |
| sun | elevation 35°, azimuth 45°, colour (1, 0.85, 0.64), intensity 1.65 | `src/game/config/world_1/looks.py` `LEVEL_1_3_LOOK` |
| sky | haze (0.84, 0.76, 0.64), horizon (0.96, 0.82, 0.6), zenith (0.3, 0.44, 0.74), environment 0.65 | same |
| ambient | sky (0.68, 0.68, 0.76), ground (0.4, 0.34, 0.24), intensity 0.6 | same |
| clouds | low 0.22, high 0.14, colour (1, 0.94, 0.84), shade (0.76, 0.68, 0.68) | same |
| fog | 1 000 → 2 600 | the base look's |
| town_streets | rows 60–110, columns 70–130, links 0.55 | `TOWN_STREETS` (also 1-4's towns and 1-5's oasis villages and towns) |
| max_gap | 3.3 s → 2.2 s | `src/game/config/world_1/waves.py` `WORLD_1_FILLERS["1-3"]` |
| bullet_speed_factor / fire_rate_factor | 0.9 / 0.9 | `src/game/config/world_1/difficulty.py` |
| written | 47 beats from the plan; waves, groups, enemies and HP after fill and density: to be measured again with the new kinds | `src/game/config/wave_plans.py` `level_plan(1, 3)`; density 2 (D-249) |
| buildings | 8 034 (halves 598 / 7 436) | each level's seed, measured for this file |
| mini boss / final boss | `dust-devil` / `mesa-fortress` | `src/game/config/world_1/bosses.py` |
| runout | 30 s | same |

## Notes

- Before D-109 (2026-10-26), 1-3 was the desert (dunes, a canyon); the Dust Devil and the Mesa
  Fortress were named for it and now fly over green land, and the Mesa Fortress's stopped ground,
  first "over the canyon", is now over the dry grassland (the canyon moved to 1-4).
- Since D-212, the woods of 1-3's first half outnumber its buildings, so its props are fewer in its
  second half (WLD-1-09's discrepancy).
