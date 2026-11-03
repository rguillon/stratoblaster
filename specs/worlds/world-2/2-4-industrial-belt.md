# 2-4 Industrial belt

> **Area:** Worlds · **Prefix:** `LVL-2-4` · **Related:** [World 2](world.md), [2-3 Oil fields](2-3-oil-fields.md), [2-5 Factory district](2-5-factory-district.md), [Avalanche](../../bosses/mini/2-4-avalanche.md), [Glacier Colossus](../../bosses/final/2-4-glacier-colossus.md), [level flow](../../gameplay/level-flow.md), [terrain](../../graphics/terrain.md), [sky and light](../../graphics/sky-and-light.md)

The fourth level of World 2: dusk through the smog over the industrial belt, from the industrial
edge 2-3 ended on, through workers' suburbs, warehouses and yards, a power plant and factory yards,
to the factory district, the window, street and car lights coming on. Mostly paved ground. Every
basic kind comes, Rocketeers and Bulwarks leading. The Avalanche waits at the middle and the Glacier
Colossus at the end.

## Requirements

### Identity

#### LVL-2-4-01 — Identity · MUST

Level `2-4` is the fourth level of World 2. It is named "Industrial belt"; its scenery is
`world-2-4`, generated from the seed `seed`.

**Acceptance criteria**
- Given the game's levels, then the ninth is `2-4`, named "2-4 Industrial belt", with the scenery `world-2-4` and its seed (unit test).

*Sources: P08-R03, D-110.*

#### LVL-2-4-02 — Duration and ground speed · MUST

2-4 scrolls at `ground_speed`, World 2's slowest, for `duration`: its sections' seconds add up to
300, so its length is 16 500 units. Its sections blend over 900 units (WLD-2-08).

**Acceptance criteria**
- Given 2-4, then its length ÷ its ground speed is 300 s (unit test, e2e).

*Sources: P08-R02, GD-01, D-110.*

#### LVL-2-4-03 — Dusk through the smog · MUST

2-4 is at dusk, the whole level long: the engine's `dusk` preset (a low sun through the smog), two
layers of thicker clouds (`clouds`), greyed by the smog (`storm`), the fog of World 2's looks
(`fog`), the window, street and car lights on, no weather.

**Acceptance criteria**
- Given the 2-4 look, then it is `dusk` with cloud cover 0.35 / 0.25, storm 0.3, no weather and no change within the level (unit test on the data).
- Given `?level=2-4&t=60` (e2e), then its ground lights are brighter than 2-1's.
- Manual visual validation: the ships, shots and bonuses stay easy to see at dusk.

*Sources: P08-R04, P08-R06, D-110.*

### Scenery

#### LVL-2-4-04 — Sections · MUST

2-4's ground is these sections, in this order (relief: height ± its amplitude, features about that
wide across); there is no sea:

| # | Section | Seconds | Relief | Cover | Buildings (density) | What it shows |
|---|---------|---------|--------|-------|---------------------|---------------|
| 1 | industrial edge | 40 | 30 ± 4, 600 | sand 0.25, paved 0.55 | refinery, industrial (1), streets | 2-3's industrial edge. |
| 2 | workers' suburbs | 50 | 30 ± 4, 600 | sand 0.22, paved 0.6 | worker homes, industrial (0.6), wide streets | Workers' suburbs on a street grid. |
| 3 | warehouses | 55 | 30 ± 4, 600 | sand 0.18, paved 0.65 | industrial (0.7), streets | Warehouses and container yards. |
| 4 | power plant | 45 | 30 ± 4, 600 | sand 0.15, paved 0.68 | industrial, refinery (1), streets | A power plant: cooling towers and tanks. |
| 5 | factory yards | 55 | 30 ± 4, 600 | sand 0.12, paved 0.72 | industrial, heavy industry (1), streets | Factory yards, the first heavy industry. |
| 6 | factory district | 55 | 32 ± 3, 600 | sand 0.1, paved 0.78 | heavy industry, industrial (1), streets | The factory district, where 2-5 begins. |

**Acceptance criteria**
- Given 2-4, then its sections are these, in this order, with these seconds (unit test on the data).
- Given 2-3's last section and 2-4's first, then they have the same relief, cover and groups (unit test, WLD-2-10).
- Manual visual validation: `?level=2-4&t=60` the suburbs, `&t=150` the power plant, `&t=280` the factory district.

*Sources: P08-R03, D-110, D-164.*

#### LVL-2-4-05 — Paved, a little sand between the plots · MUST

2-4 is mostly paved (0.67 of the ground over the level), a little sand left between the plots
(0.17), every section a street grid. The suburbs and the warehouses are built a little looser than
the rest (`building_density`), so the props still grow from section to section and level to level
on the grid of tiles (WLD-2-11). Heavy industry first comes in the factory yards, mixed with the
industrial works (WLD-2-08).

**Acceptance criteria**
- Given 2-4's sections, then each has streets, the sand share goes down and the paved share up from each section to the next (unit test on the data).

*Sources: P08-R03, D-110, D-164.*

#### LVL-2-4-06 — Buildings and roads · MUST

2-4's habitations are the workers' suburbs, warehouses and yards, the power plant, factory yards
and the factory district (the groups of the table above, WLD-2-13). It has World 1's roads
(WLD-2-14). No tree grows.

**Acceptance criteria**
- Given 2-4 placed with its seed, then it has more buildings than 2-3 and fewer than 2-5, and its second half more than its first (unit test, WLD-2-11).

*Sources: P08-R03, P08-R07, D-110, D-164.*

### Waves

#### LVL-2-4-07 — Enemy kinds · MUST

2-4 uses all eleven basic kinds, with Rocketeers and Bulwarks leading its waves over the industrial
belt, in its beats and its fillers.

**Acceptance criteria**
- Given the 2-4 wave script, then it uses all eleven basic kinds and no other (unit test).

*Sources: P08-R08.*

#### LVL-2-4-08 — Wave plan · MUST

2-4's waves are composed from this plan (WLD-2-19; World 1's density and filler apply on top):

Beats from 4 s to 292 s, one every 4.8 s at the start down to 3.4 s at the end, groups growing by 60 % over the level (71 beats, the last at 289.4 s). The phrases, in their cycle:

| # | Kind | Groups | Between groups (s) | Side | Position | Spread |
|---|------|--------|--------------------|------|----------|--------|
| 1 | Rocketeer | 2 | 2.5 | top | 0.3 | 0.4 |
| 2 | Scout | 4 | 1 | top | 0.15 | 0.23 |
| 3 | Bulwark | 1 | 0 | top | 0.5 | — |
| 4 | Weaver | 3 | 1.2 | top | 0.3 | 0.2 |
| 5 | Rocketeer | 2 | 2 | top | 0.7 | -0.4 |
| 6 | Spinner | 2 | 2.5 | top | 0.3 | 0.4 |
| 7 | Bulwark | 1 | 0 | top | 0.35 | — |
| 8 | Lancer | 2 | 2 | top | 0.25 | 0.5 |
| 9 | Splitter | 2 | 2 | top | 0.3 | 0.4 |
| 10 | Carrier | 1 | 0 | top | 0.5 | — |
| 11 | Strafer | 3 | 1.5 | right | 0.8 | — |
| 12 | Hornet | 5 | 0.7 | top | 0.1 | 0.2 |
| 13 | Gnat | 2 | 2 | top | 0.3 | 0.4 |

**Acceptance criteria**
- Given the 2-4 plan, then it composes beats that name its kinds and sides in order of time (unit test).

*Sources: P08-R08, D-067.*

#### LVL-2-4-09 — Filler · MUST

2-4's filler (WLD-1-21) brings Gnat, Weaver, Hornet, Scout, Splitter, Spinner, in turn, one group
every `max_gap`.

**Acceptance criteria**
- Given the 2-4 filler, then its kinds are those six and its gap shrinks (unit test).

*Sources: D-051, D-067.*

### Difficulty

#### LVL-2-4-10 — Difficulty · MUST

2-4's enemies fire at `fire_rate_factor` of their rate and their bullets fly at
`bullet_speed_factor` of their speed. Per minute of scroll it has more enemies and more enemy HP than
2-3 and fewer than 2-5, and a higher peak on screen than 2-3 (WLD-2-20); its second half more HP than
its first.

**Acceptance criteria**
- Given the 2-4 difficulty, then both factors are 1.1 (unit test).

*Sources: P08-R09, D-067.*

### Bosses

#### LVL-2-4-11 — Mini boss: Avalanche · MUST

The [Avalanche](../../bosses/mini/2-4-avalanche.md) comes at the middle of 2-4's length
(8 250 units, 2:30), over the power plant, in a chase. Destroying it saves the level's checkpoint
([level-flow.md](../../gameplay/level-flow.md)).

**Acceptance criteria**
- Given 2-4, then its mini boss is the Avalanche, at half its length (unit test).
- Given `?level=2-4&t=150` (e2e), then 2-4 starts at 2:30, where its mini boss comes.

*Sources: GD-41, GD-42, P08-R10.*

#### LVL-2-4-12 — Final boss: Glacier Colossus · MUST

The [Glacier Colossus](../../bosses/final/2-4-glacier-colossus.md) comes at the end of 2-4's length
(16 500 units, 5:00), over the factory district; destroying it completes the level.

**Acceptance criteria**
- Given 2-4, then its final boss is the Glacier Colossus, at its length (unit test).

*Sources: GD-41, P08-R10.*

#### LVL-2-4-13 — Runout · MUST

`runout` seconds of the last section's ground (the factory district) are drawn past the level's
end: the ground gets ahead of the level during the fights, the most in the Avalanche's chase.

**Acceptance criteria**
- Given 2-4, then its runout is 120 s (unit test on the data).

*Sources: D-054.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| seed | 2401 | `src/game/config/world_2/scenery.py` `LEVEL_2_4` |
| ground_speed | 55 units/s | `LEVEL_2_4.scrollSpeed` |
| duration | 300 s (16 500 units) | sum of the sections' `seconds` |
| look | `dusk`, clouds 0.35 / 0.25, storm 0.3, no weather | `src/game/config/world_2/looks.py` `LEVEL_2_4_LOOK` |
| fog / glow | 1 100 → 2 800 / 0.4 | World 2's looks |
| building_density | workers' suburbs 0.6, warehouses 0.7 (was 1, D-164), the others 1 | `INDUSTRIAL_BELT` |
| streets | rows 45–90, columns 50–110, links 0.6 (the suburbs: `suburb_streets`, 2-2) | `STREETS` |
| max_gap | 2.9 s → 1.8 s | `src/game/config/world_2/waves.py` `WORLD_2_FILLERS["2-4"]` |
| bullet_speed_factor / fire_rate_factor | 1.1 / 1.1 | `src/game/config/world_2/difficulty.py` |
| written | 71 beats; 136 waves and 552 groups after fill and density; 744 enemies, 32 380 HP (halves 12 600 / 19 780), Carrier launches not counted; 148.8 enemies and 6 476 HP a minute without them | measured from the configs; D-067, density 2 (D-249) |
| buildings | 33 137 (halves 13 499 / 19 638) | each level's seed, measured for this file |
| mini boss / final boss | `avalanche` / `glacier-colossus` | `src/game/config/world_2/bosses.py` |
| runout | 120 s | same |

## Notes

- Before the 2026-10-27 rework (D-110), 2-4 was an afternoon glacier with mining outposts and a
  blizzard from 2:30; the Avalanche and the Glacier Colossus were made for it. The `?level=2-4&t=150`
  check, first "in the blizzard", now lands on the mini boss over the power plant.
- The warehouses were built looser (density 1 → 0.7) when the grid of tiles made the props-growth
  check fail (D-164).
