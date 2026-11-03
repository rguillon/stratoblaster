# 2-1 Great erg

> **Area:** Worlds · **Prefix:** `LVL-2-1` · **Related:** [World 2](world.md), [1-5 Deep desert](../world-1/1-5-deep-desert.md), [2-2 Mining mesas](2-2-mining-mesas.md), [Floe Breaker](../../bosses/mini/2-1-floe-breaker.md), [Narwhal](../../bosses/final/2-1-narwhal.md), [level flow](../../gameplay/level-flow.md), [terrain](../../graphics/terrain.md), [sky and light](../../graphics/sky-and-light.md)

The first level of World 2: a clear desert morning over the great erg, from an oasis edge across
great dunes, caravan posts and a dune field to rocky desert and desert outposts, the first mines in
the last 30 seconds. Open sand to the end, no sea. Gnats, Hornets, Scouts, Strafers and Weavers lead
the waves. A breather after 1-5, about as hard as 1-3. The Floe Breaker waits at the middle and the
Narwhal at the end.

## Requirements

### Identity

#### LVL-2-1-01 — Identity · MUST

Level `2-1` is the first level of World 2. It is named "Great erg" (first named "Sand sea", renamed
so its name suggests no sea); its scenery is `world-2-1`, generated from the seed `seed`.

**Acceptance criteria**
- Given the game's levels, then the sixth is `2-1`, named "2-1 Great erg", with the scenery `world-2-1` and its seed (unit test).

*Sources: P08-R03, D-110.*

#### LVL-2-1-02 — Duration and ground speed · MUST

2-1 scrolls at `ground_speed`, World 2's fastest, for `duration`: its sections' seconds add up to
300, so its length is 21 000 units. Its sections blend over 900 units (WLD-2-08).

**Acceptance criteria**
- Given 2-1, then its length ÷ its ground speed is 300 s (unit test, e2e).

*Sources: P08-R02, GD-01, D-110.*

#### LVL-2-1-03 — Morning · MUST

2-1 is in the morning, the whole level long: the engine's `morning` preset (a warm, low light and
long shadows of the dunes), two layers of few clouds (`clouds`), no smog, the fog of World 2's
looks (`fog`), the ground lights off, no weather.

**Acceptance criteria**
- Given the 2-1 look, then it is `morning` with cloud cover 0.15 / 0.1, no storm, no weather and no change within the level (unit test on the data).
- Given 2-1 (e2e), then no weather particle and no aurora are drawn, and the ground lights are under 0.5.

*Sources: P08-R04, P08-R06, D-110.*

### Scenery

#### LVL-2-1-04 — Sections · MUST

2-1's ground is these sections, in this order (relief: height ± its amplitude, features about that
wide across); there is no sea:

| # | Section | Seconds | Relief | Cover | Buildings (density) | What it shows |
|---|---------|---------|--------|-------|---------------------|---------------|
| 1 | oasis edge | 40 | 30 ± 4, 600 | sand 0.85, grass 0.1 | desert homes, outposts (0.3) | The edge of an oasis, on flat sand. |
| 2 | great dunes | 50 | 28 ± 10, 520, great dunes | sand 1 | outposts (0.3) | Great dunes. |
| 3 | caravan posts | 45 | 28 ± 10, 520 | sand 1 | outposts, desert homes (0.6) | Caravan outposts on the sand. |
| 4 | dune field | 45 | 28 ± 10, 520, a dune field | sand 1 | outposts (0.45) | A field of smaller dunes. |
| 5 | rocky desert | 50 | 22 ± 80 ridged, 500, cut at 110 | sand 0.7 | outposts (0.8) | Rocky ridges between the sand. |
| 6 | desert outposts | 40 | 30 ± 8, 560 | sand 0.85 | outposts, desert homes (1) | Desert outposts: water towers, solar farms, radio masts. |
| 7 | prospect mines | 30 | 30 ± 10, 520 | sand 0.8, paved 0.05 | outposts, mines (1) | The first mines, where 2-2 begins. |

**Acceptance criteria**
- Given 2-1, then its sections are these, in this order, with these seconds (unit test on the data).
- Manual visual validation: `?level=2-1&t=60` the great dunes, `&t=280` the first mines; never any sea.

*Sources: P08-R03, D-110.*

#### LVL-2-1-05 — Dunes · MUST

2-1 is the sand of the erg: its two dune sections raise sand dunes on the relief, great dunes
(`great_dunes`) then a field of smaller ones at another angle (`dune_field`); the lee sides of the
dunes stay sand (only cliffs are bare rock, WLD-2-12). 2-1 has no sea, shore or water (WLD-2-06).

**Acceptance criteria**
- Given 2-1, then it has no sea and no shore section, and its great dunes and dune field have dunes (unit test on the data).

*Sources: P08-R03, D-110, D-200.*

#### LVL-2-1-06 — Buildings and roads · MUST

2-1's habitations are oasis and desert homes and outposts, then the first mines in its last
section (the groups of the table above, WLD-2-13), with a few lone buildings and hamlets; no
industrial or heavy-industry group (WLD-2-09). It has World 1's roads (WLD-2-14). No tree grows.

**Acceptance criteria**
- Given 2-1's sections, then none lists the industrial or heavy-industry group (unit test).
- Given 2-1 placed with its seed, then it has fewer buildings than 2-2 and its second half more than its first (unit test, WLD-2-11).

*Sources: P08-R03, P08-R07, D-110.*

### Waves

#### LVL-2-1-07 — Enemy kinds · MUST

2-1 brings Wasp, Strafer and Sweeper (a diver, a shooter and a laser), in its beats and its fillers, and no other kind.

**Acceptance criteria**
- Given the 2-1 wave script, then it only uses Wasp, Strafer and Sweeper, and it uses each of them (unit test).

*Sources: P06-R07, ENM-50.*

#### LVL-2-1-08 — Wave plan · MUST

2-1's waves are composed from this plan (WLD-2-19; World 1's density and filler apply on top):

Beats from 4 s to 292 s, one every 5.8 s at the start down to 4.2 s at the end, groups growing by 70 % over the level (59 beats, the last at 291.6 s). The phrases, in their cycle:

| # | Kind | Groups | Between groups (s) | Side | Position | Spread |
|---|------|--------|--------------------|------|----------|--------|
| 1 | Wasp | 2 | 1.6 | top | 0.4 | 0.3 |
| 2 | Strafer | 2 | 1.5 | left | 0.8 | — |
| 3 | Sweeper | 1 | 0 | top | 0.5 | — |
| 4 | Wasp | 2 | 1.6 | top | 0.6 | -0.3 |
| 5 | Strafer | 2 | 1.5 | right | 0.2 | — |
| 6 | Wasp | 2 | 1.6 | top | 0.4 | 0.3 |
| 7 | Sweeper | 1 | 0 | top | 0.5 | — |
| 8 | Strafer | 2 | 1.5 | left | 0.8 | — |

No wave starts in the 10 s before each boss ([level-flow.md](../../gameplay/level-flow.md)).

**Acceptance criteria**
- Given the 2-1 plan, then it composes beats that name its kinds and sides in order of time (unit test).

*Sources: P06-R07, D-067, ENM-50.*

#### LVL-2-1-09 — Filler · MUST

2-1's filler (WLD-1-21) brings the level's divers and shooters, Wasp, Strafer, Wasp, Strafer, in turn, one group every `max_gap`.

**Acceptance criteria**
- Given the 2-1 filler, then its kinds are the Wasp and the Strafer only and its gap shrinks (unit test).

*Sources: D-051, ENM-50.*

### Difficulty

#### LVL-2-1-10 — A breather · MUST

2-1's enemies fire at `fire_rate_factor` of their rate and their bullets fly at
`bullet_speed_factor` of their speed, as in 1-3. Per minute of scroll it has at least as many
enemies and as much enemy HP as 1-3 and may have fewer than 1-5 (WLD-2-23), and less than 2-2
(WLD-2-20); its second half more HP than its first.

**Acceptance criteria**
- Given the 2-1 difficulty, then both factors are 0.9 (unit test).
- Manual validation: 2-1 feels close to the middle of World 1.

*Sources: P08-R09, D-067.*

### Bosses

#### LVL-2-1-11 — Mini boss: Floe Breaker · MUST

The [Floe Breaker](../../bosses/mini/2-1-floe-breaker.md) comes at the middle of 2-1's length
(10 500 units, 2:30). Destroying it saves the level's checkpoint
([level-flow.md](../../gameplay/level-flow.md)).

**Acceptance criteria**
- Given 2-1, then its mini boss is the Floe Breaker, at half its length (unit test).

*Sources: GD-41, GD-42, P08-R10.*

#### LVL-2-1-12 — Final boss: Narwhal · MUST

The [Narwhal](../../bosses/final/2-1-narwhal.md) comes at the end of 2-1's length (21 000 units,
5:00), in a chase over the first mines; destroying it completes the level.

**Acceptance criteria**
- Given 2-1, then its final boss is the Narwhal, at its length (unit test).
- Given `?level=2-1&boss=final`, when the Narwhal is destroyed, then "Level complete" shows `2-1`, and Confirm leads to `level-select` on `2-2` (e2e).

*Sources: GD-41, P08-R10.*

#### LVL-2-1-13 — Runout · MUST

`runout` seconds of the last section's ground (the prospect mines) are drawn past the level's end,
the longest of World 2: the ground gets ahead of the level during the fights, the most in the
Narwhal's chase.

**Acceptance criteria**
- Given 2-1, then its runout is 160 s (unit test on the data).

*Sources: D-054.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| seed | 2101 | `src/game/config/world_2/scenery.py` `LEVEL_2_1` |
| ground_speed | 70 units/s | `LEVEL_2_1.scrollSpeed` |
| duration | 300 s (21 000 units) | sum of the sections' `seconds` |
| look | `morning`, clouds 0.15 / 0.1, no storm, no weather | `src/game/config/world_2/looks.py` `LEVEL_2_1_LOOK` |
| fog / glow | 1 100 → 2 800 / 0.4 | World 2's looks (`industrial`) |
| great_dunes | crests 60 high every 300 units, at 60°, warp 0.6 | `dunes(60, 300)` |
| dune_field | crests 45 high every 240 units, at 70°, warp 0.6 | `dunes(45, 240, 70)` |
| max_gap | 3.4 s → 2.3 s | `src/game/config/world_2/waves.py` `WORLD_2_FILLERS["2-1"]` |
| bullet_speed_factor / fire_rate_factor | 0.9 / 0.9 | `src/game/config/world_2/difficulty.py` |
| written | 59 beats from the plan; waves, groups, enemies and HP after fill and density: to be measured again with the new kinds | `src/game/config/wave_plans.py` `level_plan(2, 1)`; density 2 (D-249) |
| buildings | 1 384 (halves 525 / 859) | each level's seed, measured for this file |
| mini boss / final boss | `floe-breaker` / `narwhal` | `src/game/config/world_2/bosses.py` `WORLD_2_BOSSES` |
| runout | 160 s | same |

## Notes

- Before the 2026-10-27 rework (D-110), 2-1 was a dawn over a dark sea with ice floes and icebergs;
  the Floe Breaker and the Narwhal were made for it and now fly over the sand.
- 1-5 ends on red desert dirt (D-200) and 2-1 begins on World 2's sand: the two worlds' grounds
  differ at the step between them.
