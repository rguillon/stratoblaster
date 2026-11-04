# 2-3 Oil fields

> **Area:** Worlds · **Prefix:** `LVL-2-3` · **Related:** [World 2](world.md), [2-2 Mining mesas](2-2-mining-mesas.md), [2-4 Industrial belt](2-4-industrial-belt.md), [Snow Owl](../../bosses/mini/2-3-snow-owl.md), [Aurora Station](../../bosses/final/2-3-aurora-station.md), [level flow](../../gameplay/level-flow.md), [terrain](../../graphics/terrain.md), [sky and light](../../graphics/sky-and-light.md)

The middle level of World 2: a golden afternoon over the oil fields, from the oil edge 2-2 ended on,
through pumpjacks and tanks, a company town, refineries and tank farms, to the first factories at the
end, the ground more and more paved. The first smoke greys the clouds. All five kinds of tier 2 come, the
Hatchery with them. The Snow Owl waits at the middle and the Aurora Station at the end.

## Requirements

### Identity

#### LVL-2-3-01 — Identity · MUST

Level `2-3` is the third level of World 2. It is named "Oil fields"; its scenery is `world-2-3`,
generated from the seed `seed`.

**Acceptance criteria**
- Given the game's levels, then the eighth is `2-3`, named "2-3 Oil fields", with the scenery `world-2-3` and its seed (unit test).

*Sources: P08-R03, D-110.*

#### LVL-2-3-02 — Duration and ground speed · MUST

2-3 scrolls at `ground_speed` for `duration`: its sections' seconds add up to 300, so its length is
18 000 units. Its sections blend over 900 units (WLD-2-08).

**Acceptance criteria**
- Given 2-3, then its length ÷ its ground speed is 300 s (unit test, e2e).

*Sources: P08-R02, GD-01, D-110.*

#### LVL-2-3-03 — Afternoon · MUST

2-3 is in the afternoon, the whole level long: the engine's `afternoon` preset (a golden light), two
layers of clouds a little thicker than 2-2's (`clouds`), greyed a little by the first smoke
(`storm`), the fog of World 2's looks (`fog`), the ground lights off, no weather.

**Acceptance criteria**
- Given the 2-3 look, then it is `afternoon` with cloud cover 0.25 / 0.2, storm 0.15, no weather and no change within the level (unit test on the data).

*Sources: P08-R04, P08-R06, D-110.*

### Scenery

#### LVL-2-3-04 — Sections · MUST

2-3's ground is these sections, in this order (relief: height ± its amplitude, features about that
wide across); there is no sea:

| # | Section | Seconds | Relief | Cover | Buildings (density) | What it shows |
|---|---------|---------|--------|-------|---------------------|---------------|
| 1 | oil edge | 40 | 28 ± 5, 600 | sand 0.55, paved 0.25 | oil, mines (1) | 2-2's oil edge. |
| 2 | oil fields | 60 | 26 ± 5, 620 | sand 0.5, paved 0.25 | oil (1) | Oil fields: pumpjacks and storage tanks. |
| 3 | company town | 50 | 30 ± 4, 600 | sand 0.4, paved 0.4 | worker homes, oil (1), wide streets | A company town on a street grid. |
| 4 | refineries | 55 | 30 ± 4, 600 | sand 0.35, paved 0.45 | refinery, oil (1) | Refineries among the last wells. |
| 5 | tank farms | 50 | 30 ± 4, 600 | sand 0.3, paved 0.5 | refinery (1), streets | Tank farms on a dense street grid. |
| 6 | industrial edge | 45 | 30 ± 4, 600 | sand 0.25, paved 0.55 | refinery, industrial (1), streets | Refineries giving way to the first factories, where 2-4 begins. |

**Acceptance criteria**
- Given 2-3, then its sections are these, in this order, with these seconds (unit test on the data).
- Given 2-2's last section and 2-3's first, then they have the same relief, cover and groups (unit test, WLD-2-10).
- Manual visual validation: `?level=2-3&t=70` the oil fields, `&t=180` the refineries, `&t=280` the first factories.

*Sources: P08-R03, D-110.*

#### LVL-2-3-05 — Flat, half paved · MUST

2-3 is flat ground (its reliefs within ± 5), more and more of it paved: about even between sand
(0.39) and pavement (0.40) over the level, sand ahead in its first half and pavement in its second
(WLD-2-07). The industrial group first comes in its last section, mixed with the refineries
(WLD-2-08).

**Acceptance criteria**
- Given 2-3's sections, then the sand share goes down from each section to the next and the paved share never goes down, and only the last lists the industrial group (unit test on the data).

*Sources: P08-R03, D-110.*

#### LVL-2-3-06 — Buildings and roads · MUST

2-3's habitations are the oil fields, a company town of worker homes, refineries and tank farms,
then the first factories (the groups of the table above, WLD-2-13), with a few lone buildings and
hamlets. It has World 1's roads (WLD-2-14). No tree grows.

**Acceptance criteria**
- Given 2-3 placed with its seed, then it has more buildings than 2-2 and fewer than 2-4, and its second half more than its first (unit test, WLD-2-11).

*Sources: P08-R03, P08-R07, D-110.*

### Waves

#### LVL-2-3-07 — Enemy kinds · MUST

2-3 brings in the last kind, the Hatchery, and so uses the five kinds of tier 2 (Wasp, Strafer, Sweeper, Harrier and Hatchery), in its beats and its fillers, and no other kind.

**Acceptance criteria**
- Given the 2-3 wave script, then it only uses Wasp, Strafer, Sweeper, Harrier and Hatchery, and it uses each of them (unit test).

*Sources: P06-R07, ENM-50.*

#### LVL-2-3-08 — Wave plan · MUST

2-3's waves are composed from this plan (WLD-2-19; World 1's density and filler apply on top):

Beats from 4 s to 292 s, one every 5 s at the start down to 3.6 s at the end, groups growing by 80 % over the level (68 beats, the last at 290.5 s). The phrases, in their cycle:

| # | Kind | Groups | Between groups (s) | Side | Position | Spread |
|---|------|--------|--------------------|------|----------|--------|
| 1 | Wasp | 2 | 1.6 | top | 0.4 | 0.3 |
| 2 | Strafer | 2 | 1.5 | left | 0.8 | — |
| 3 | Sweeper | 1 | 0 | top | 0.5 | — |
| 4 | Wasp | 2 | 1.6 | top | 0.6 | -0.3 |
| 5 | Harrier | 2 | 2 | top | 0.3 | 0.4 |
| 6 | Strafer | 2 | 1.5 | right | 0.2 | — |
| 7 | Wasp | 2 | 1.6 | top | 0.4 | 0.3 |
| 8 | Hatchery | 1 | 0 | top | 0.5 | — |
| 9 | Sweeper | 1 | 0 | top | 0.5 | — |
| 10 | Strafer | 2 | 1.5 | left | 0.8 | — |
| 11 | Harrier | 2 | 2 | top | 0.7 | -0.4 |

No wave starts in the 10 s before each boss ([level-flow.md](../../gameplay/level-flow.md)).

**Acceptance criteria**
- Given the 2-3 plan, then it composes beats that name its kinds and sides in order of time (unit test).

*Sources: P06-R07, D-067, ENM-50.*

#### LVL-2-3-09 — Filler · MUST

2-3's filler (WLD-1-21) brings the level's divers and shooters, Wasp, Strafer, Wasp, Strafer, in turn, one group every `max_gap`.

**Acceptance criteria**
- Given the 2-3 filler, then its kinds are the Wasp and the Strafer only and its gap shrinks (unit test).

*Sources: D-051, ENM-50.*

### Difficulty

#### LVL-2-3-10 — Difficulty · MUST

2-3's enemies fire at `fire_rate_factor` of their rate and their bullets fly at
`bullet_speed_factor` of their speed: the kinds' own values. Per minute of scroll it has more
enemies and more enemy HP than 2-2 and fewer than 2-4, and a higher peak on screen than 2-2 (the
Hatcheries' Wasps raise it, WLD-2-20); its second half more HP than its first.

**Acceptance criteria**
- Given the 2-3 difficulty, then both factors are 1 (unit test).

*Sources: P08-R09, D-067.*

### Bosses

#### LVL-2-3-11 — Mini boss: Snow Owl · MUST

The [Snow Owl](../../bosses/mini/2-3-snow-owl.md) comes at the middle of 2-3's length
(9 000 units, 2:30), over the refineries. Destroying it saves the level's checkpoint
([level-flow.md](../../gameplay/level-flow.md)).

**Acceptance criteria**
- Given 2-3, then its mini boss is the Snow Owl, at half its length (unit test).

*Sources: GD-41, GD-42, P08-R10.*

#### LVL-2-3-12 — Final boss: Aurora Station · MUST

The [Aurora Station](../../bosses/final/2-3-aurora-station.md) comes at the end of 2-3's length
(18 000 units, 5:00), over the industrial edge; destroying it completes the level.

**Acceptance criteria**
- Given 2-3, then its final boss is the Aurora Station, at its length (unit test).

*Sources: GD-41, P08-R10.*

#### LVL-2-3-13 — Runout · MUST

`runout` seconds of the last section's ground (the industrial edge) are drawn past the level's end,
for the ground that gets ahead of the level during the fights.

**Acceptance criteria**
- Given 2-3, then its runout is 80 s (unit test on the data).

*Sources: D-054.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| seed | 2301 | `src/game/config/world_2/scenery.py` `LEVEL_2_3` |
| ground_speed | 60 units/s | `LEVEL_2_3.scrollSpeed` |
| duration | 300 s (18 000 units) | sum of the sections' `seconds` |
| look | `afternoon`, clouds 0.25 / 0.2, storm 0.15, no weather | `src/game/config/world_2/looks.py` `LEVEL_2_3_LOOK` |
| fog / glow | 1 100 → 2 800 / 0.4 | World 2's looks |
| streets | rows 45–90, columns 50–110, links 0.6 (the company town: `suburb_streets`, 2-2) | `STREETS` |
| max_gap | 3 s → 2 s | `src/game/config/world_2/waves.py` `WORLD_2_FILLERS["2-3"]` |
| bullet_speed_factor / fire_rate_factor | 1 / 1 | `src/game/config/world_2/difficulty.py` |
| written | 68 beats from the plan; waves, groups, enemies and HP after fill and density: to be measured again with the new kinds | `src/game/config/wave_plans.py` `level_plan(2, 3)`; density 2 (D-249) |
| buildings | 24 278 (halves 10 287 / 13 991) | each level's seed, measured for this file |
| mini boss / final boss | `snow-owl` / `aurora-station` | `src/game/config/world_2/bosses.py` |
| runout | 80 s | same |

## Notes

- Before the 2026-10-27 rework (D-110), 2-3 was an overcast tundra with falling snow, frozen lakes
  and a pipeline on stilts; the Snow Owl and the Aurora Station were made for it.
- The pumpjacks of the old P08-R07 are tile models of the industrial group, shared with the mines,
  refineries and factories (WLD-2-13 and its note).
