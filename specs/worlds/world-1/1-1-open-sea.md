# 1-1 Open sea

> **Area:** Worlds · **Prefix:** `LVL-1-1` · **Related:** [World 1](world.md), [1-2 Green coast](1-2-green-coast.md), [Reef Warden](../../bosses/mini/1-1-reef-warden.md), [Storm Petrel](../../bosses/final/1-1-storm-petrel.md), [level flow](../../gameplay/level-flow.md), [terrain](../../graphics/terrain.md), [water](../../graphics/water.md), [sky and light](../../graphics/sky-and-light.md)

The first level of the game, and the easiest: midday over a clear turquoise sea, with small wooded
islands and reefs, and the first green coast in the last 30 seconds. Hornets and
Scouts come a few at a time; the Reef Warden waits at the middle and the Storm Petrel at the end.
It is meant to be easy, even for a kid.

## Requirements

### Identity

#### LVL-1-1-01 — Identity · MUST

Level `1-1` is the first level of World 1 and of the game. It is named "Open sea"; its scenery is
`world-1-1`, generated from the seed `seed`.

**Acceptance criteria**
- Given the game's levels, then the first is `1-1`, named "1-1 Open sea", with the scenery `world-1-1` and its seed (unit test).

*Sources: P06-R05, D-109.*

#### LVL-1-1-02 — Duration and ground speed · MUST

1-1 scrolls at `ground_speed`, World 1's fastest, for `duration`: its sections' seconds add up to
240, so its length is 16 800 units. Its sections blend over 420 units.

**Acceptance criteria**
- Given 1-1, then its length ÷ its ground speed is 240 s (unit test, e2e).

*Sources: P06-R04, GD-01, D-109.*

#### LVL-1-1-03 — Midday · MUST

1-1 is at midday, the whole level long:
- the sun is high (`sun`) and nearly white;
- a clear blue sky, a pale blue haze, a cool ambient light (`ambient`);
- two layers of scattered white clouds (`clouds`);
- the fog of the base look (`fog`), no ground lights, no weather.

**Acceptance criteria**
- Given the 1-1 look, then its sun's elevation is the highest of World 1 (unit test, WLD-1-16).
- Manual visual validation: a bright midday over a turquoise sea, short shadows.

*Sources: P06-R10, D-109.*

### Scenery

#### LVL-1-1-04 — Sections · MUST

1-1's ground is these sections, in this order (relief: height above the sea level 0, ± its
amplitude, features about that wide across):

| # | Section | Seconds | Relief | What it shows |
|---|---------|---------|--------|---------------|
| 1 | open sea | 35 | −70 ± 30, 520 | Deep open water: nothing rises above the sea. |
| 2 | reefs | 40 | −24 ± 48, 520 | Shallow reefs, a few breaking the surface as small islands. |
| 3 | islands | 45 | −12 ± 50, 520 | Small green islands, wooded, with beaches. |
| 4 | deep water | 30 | −70 ± 30, 520 | Deep open water again. |
| 5 | archipelago | 60 | −10 ± 50, 520 | Many small green islands close together, wooded. |
| 6 | green coast | 30 | 16 ± 10, 480 | The first coast: a winding shore, then green land with a fishing village and coast homes. |

**Acceptance criteria**
- Given 1-1, then its sections are these, in this order, with these seconds (unit test on the data).
- Manual visual validation: `?level=1-1&t=0` open sea, `&t=90` islands, `&t=215` the first coast.

*Sources: P06-R05, D-109.*

#### LVL-1-1-05 — Sea and islands · MUST

1-1 has a sea at level 0, so it is almost all water (WLD-1-06: at least 80 % of the level over the
sea). The islands' land is grass (cover 0.7); the water is turquoise in the shallows and deep blue away
from the land. The green coast's shore runs along the level on a winding line (sea on the left, land
on the right), with a beach 240 units wide and a sea bed of −55 off it; its land is grass (0.8)
with some sand (0.2). 1-2 begins on this green coast (WLD-1-08).

**Acceptance criteria**
- Given 1-1, then it has a sea level and only its last section has a shore (unit test on the data).

*Sources: P06-R05, D-109.*

#### LVL-1-1-06 — Buildings and roads · MUST

No building stands on the islands (their building density is 0): the only habitations of 1-1 are
the fishing village (the `fishing` group: docks) and the coast homes of its final coast, at building
density 0.5. 1-1 has one main road (World 1's others otherwise, WLD-1-15), laid on land only.

**Acceptance criteria**
- Given 1-1 placed with its seed, then every building stands in its last section or the blend into it (unit test).

*Sources: P06-R05, P06-R06, D-207.*

#### LVL-1-1-07 — Wooded islands · MUST

The islands and the coast grow living woods on their grass (tree density 1, the living trees,
WLD-1-14).

**Acceptance criteria**
- Manual visual validation: the islands and the coast are wooded.

*Sources: D-212, D-214.*

### Waves

#### LVL-1-1-08 — Enemy kinds · MUST

1-1 brings only Hornets and Scouts (a diver and a shooter), in its beats and its fillers.

**Acceptance criteria**
- Given the 1-1 wave script, then it only uses Hornet and Scout, and it uses each of them (unit test).

*Sources: P06-R07, ENM-50.*

#### LVL-1-1-09 — Wave plan · MUST

1-1's waves are composed from this plan (WLD-1-19; the density of WLD-1-20 applies on top):

Beats from 4 s to 226 s, one every 6.4 s at the start down to 4.6 s at the end, groups growing by 60 % over the level (41 beats, the last at 223.5 s). The phrases, in their cycle:

| # | Kind | Groups | Between groups (s) | Side | Position | Spread |
|---|------|--------|--------------------|------|----------|--------|
| 1 | Hornet | 4 | 0.8 | top | 0.15 | 0.23 |
| 2 | Scout | 3 | 1.2 | top | 0.25 | 0.25 |
| 3 | Hornet | 4 | 0.8 | top | 0.85 | -0.23 |
| 4 | Scout | 3 | 1.2 | top | 0.75 | -0.25 |
| 5 | Hornet | 4 | 0.8 | top | 0.15 | 0.23 |
| 6 | Scout | 3 | 1.2 | top | 0.25 | 0.25 |

No wave starts in the 10 s before each boss ([level-flow.md](../../gameplay/level-flow.md)).

**Acceptance criteria**
- Given the 1-1 plan, then it composes beats that name its kinds and sides in order of time (unit test).

*Sources: P06-R07, D-067, ENM-50.*

#### LVL-1-1-10 — Filler · MUST

1-1's filler (WLD-1-21) brings only the Hornet, which does not shoot, one group every `max_gap`, the gentlest filler of the game.

**Acceptance criteria**
- Given the 1-1 filler, then its kind is the Hornet only and its gap shrinks (unit test).

*Sources: D-051, ENM-50.*

### Difficulty

#### LVL-1-1-11 — The easiest level · MUST

1-1's enemies fire at `fire_rate_factor` of their rate and their bullets fly at
`bullet_speed_factor` of their speed, the lowest of the game. It has the fewest enemies and the
least enemy HP of World 1 (WLD-1-22), its second half more than its first.

**Acceptance criteria**
- Given the 1-1 difficulty, then both factors are 0.8 (unit test).
- Manual validation: 1-1 feels easy, even for a kid.

*Sources: P06-R08, D-038.*

### Bosses

#### LVL-1-1-12 — Mini boss: Reef Warden · MUST

The [Reef Warden](../../bosses/mini/1-1-reef-warden.md) comes at the middle of 1-1's length
(8 400 units, 2:00). Destroying it saves the level's checkpoint
([level-flow.md](../../gameplay/level-flow.md)).

**Acceptance criteria**
- Given 1-1, then its mini boss is the Reef Warden, at half its length (unit test).

*Sources: GD-41, GD-42, P07-R05, P07-R06.*

#### LVL-1-1-13 — Final boss: Storm Petrel · MUST

The [Storm Petrel](../../bosses/final/1-1-storm-petrel.md) comes at the end of 1-1's length
(16 800 units, 4:00), in a chase over the sea; destroying it completes the level.

**Acceptance criteria**
- Given 1-1, then its final boss is the Storm Petrel, at its length (unit test).
- Given `?level=1-1&boss=final`, when the boss is destroyed, then "Level complete" shows `1-1` (e2e).

*Sources: GD-41, P07-R05, P07-R06.*

#### LVL-1-1-14 — Runout · MUST

`runout` seconds of the last section's ground (the green coast) are drawn past the level's end, the
longest of World 1: during the fights the ground gets ahead of the level, the most in the Storm
Petrel's chase.

**Acceptance criteria**
- Given 1-1, then its runout is 150 s (unit test on the data).

*Sources: D-054.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| seed | 1101 | `src/game/config/world_1/scenery_coast.py` `LEVEL_1_1` |
| ground_speed | 70 units/s | `LEVEL_1_1.scrollSpeed` |
| duration | 240 s (16 800 units) | sum of the sections' `seconds` |
| sun | elevation 72°, azimuth 20°, colour (1, 0.97, 0.92), intensity 1.7 | `src/game/config/world_1/looks.py` `LEVEL_1_1_LOOK` |
| sky | haze (0.7, 0.8, 0.9), horizon (0.86, 0.9, 0.95), zenith (0.22, 0.45, 0.82), environment 0.7 | same |
| ambient | sky (0.66, 0.76, 0.9), ground (0.32, 0.36, 0.3), intensity 0.65 | same |
| clouds | low 0.35, high 0.2, white | same |
| fog | 1 000 → 2 600 | the base look's |
| sea | level 0; colour (0.02, 0.2, 0.32); shallows (0.1, 0.62, 0.6) | `LEVEL_1_1.sea`, `TERRAIN.shore` |
| shore | x −40 ± 90, every 1 800 units; beach 240; sea bed −55 | `GREEN_COAST` |
| max_gap | 4.5 s → 3 s | `src/game/config/world_1/waves.py` `WORLD_1_FILLERS["1-1"]` |
| bullet_speed_factor / fire_rate_factor | 0.8 / 0.8 | `src/game/config/world_1/difficulty.py` |
| written | 41 beats from the plan; waves, groups, enemies and HP after fill and density: to be measured again with the new kinds | `src/game/config/wave_plans.py` `level_plan(1, 1)`; density 2 (D-249) |
| mini boss / final boss | `reef-warden` / `storm-petrel` | `src/game/config/world_1/bosses.py` `WORLD_1_BOSSES` |
| runout | 150 s | same |

## Notes

- Before D-207 a few lone huts and masts stood on the islands, scattered like plants; they went with
  the World 1 props.
