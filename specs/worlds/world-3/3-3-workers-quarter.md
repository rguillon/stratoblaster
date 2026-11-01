# Level 3-3 — Workers' quarter

> **Area:** worlds · **Prefix:** `LVL-3-3` · **Related:** [World 3](world.md), [3-2 Docklands](3-2-docklands.md), [3-4 Suburbs](3-4-suburbs.md), [Stone Idol](../../bosses/mini/3-3-stone-idol.md), [Sky Temple](../../bosses/final/3-3-sky-temple.md), [level flow](../../gameplay/level-flow.md), [weather](../../graphics/weather.md)

The third level of World 3. From the first flats 3-2 ended on, the player flies over blocks of
workers' flats, terraced streets, a park and brick terraces to the first houses, while an afternoon
thunderstorm builds over the first quarter and then rages, with lightning. Spinners and Rocketeers
lead the waves and the Minelayer comes in. Its mini boss stops the ground. Its checkpoint is its
mini boss (see [level flow](../../gameplay/level-flow.md)).

## Requirements

### LVL-3-3-01 — Identity and duration · MUST

Level `3-3`, named "Workers' quarter", is the third level of World 3. Its scenery is `world-3-3`,
built from seed 3301. Its ground scrolls at `ground_speed`, the slowest of World 3 (the storm), for
`level_length`: 300 s.

**Acceptance criteria**
- Given level `3-3`, then its scenery id is `world-3-3`, its seed 3301, its ground speed 55 and its length 16 500 units (300 s).

*Sources: P09-R02, P09-R03, D-111.*

### LVL-3-3-02 — Scenery sections · MUST

3-3's ground is these sections, in this order, blending over World 3's `section_transition`. The
first five lie on World 3's flat ground, the last on its rolling ground.

| # | Section | Time | Length | Paved / grass | Buildings (groups) | Streets | Building density |
|---|---------|------|--------|---------------|--------------------|---------|------------------|
| 1 | First flats | 0–40 s | 2 200 | 0.68 / 0.12 | workers' flats, workshops | streets | 1 |
| 2 | Workers' flats | 40–100 s | 3 300 | 0.64 / 0.15 | workers' flats | streets | 1 |
| 3 | Terraced streets | 100–155 s | 3 025 | 0.6 / 0.18 | residences, workers' flats | terraced streets | 1 |
| 4 | Canal park | 155–200 s | 2 475 | 0.4 / 0.45 | residences | streets | 1 |
| 5 | Brick terraces | 200–255 s | 3 025 | 0.5 / 0.3 | residences | terraced streets | 1 |
| 6 | Suburb edge | 255–300 s | 2 475 | 0.42 / 0.4 | residences | suburb streets | 1 |

The first section is the one 3-2 ended on; the last, the suburb edge, is where 3-4 begins. The park's
buildings fill every slot (density 1) so the buildings keep growing in number on the grid of tiles
(WLD-3-08). The canal runs along the park and becomes a river among the brick terraces (WLD-3-10).

**Acceptance criteria**
- Given 3-3's scenery, then its sections are these, in this order, with these lengths, covers, groups, streets and densities.
- Given 3-3's first section, then it is 3-2's last section, shortened to 40 s.

*Sources: P09-R03, D-111, D-139, D-164.*

### LVL-3-3-03 — Look: a thunderstorm · MUST

3-3 is an **afternoon**. It starts half covered (clouds 0.5 / 0.5, storm 0.3) without rain, and the
storm builds over the first 75 s (the first quarter) into a **thunderstorm**: dark blue-grey clouds at
cover 0.9 / 0.9 (storm 1), rain of strength `rain`, and **lightning** (strength 1) lighting the ground
in flashes. The storm then lasts to the end, the boss fights included. It is World 3's only level with
lightning (the flash limits are in [weather](../../graphics/weather.md)).

**Acceptance criteria**
- Given 3-3's look, then it starts at afternoon with clouds 0.5 / 0.5, storm 0.3 and no weather, and changes over 0–75 s to clouds 0.9 / 0.9, storm 1, rain 0.8 and lightning 1.
- Given `?level=3-3&t=120`, then 3-3 starts at 2:00 in its thunderstorm: rain 0.8 and lightning.
- Manual visual validation: dark, with lightning lighting the ground; shots and bonuses stay visible through the storm.

*Sources: P09-R04, P09-R05, D-111.*

### LVL-3-3-04 — Enemy waves · MUST

3-3's waves follow its wave plan (WLD-3-16) from 4 s to 292 s, with a beat every `wave_gap` seconds and
groups growing by `wave_growth`. The cycle: Spinner 3, Rocketeer 2, Scout 4, Spinner 2, Lancer 2,
Rocketeer 2, Weaver 4, Bulwark 1, Splitter 2, Carrier 1, Strafer 3 (from the right), Hornet 5, Gnat 3,
Wasp 2, Mortar 1, Minelayer 1 (from the right). Groups of Spinners and Rocketeers (twice each a cycle)
lead the waves over the workers' quarter. The filler draws Gnats, Weavers, Hornets, Scouts, Splitters
and Spinners, at most `filler_gap` apart. 3-3 uses every basic kind, the Wasp, the Mortar and the
Minelayer.

**Acceptance criteria**
- Unit test: 3-3's waves use the eleven basic kinds, the Wasp, the Mortar and the Minelayer, and no other kind.
- Unit test: 3-3's waves are the same each time the level is built.

*Sources: P09-R07, P05-R24, D-080, D-090.*

### LVL-3-3-05 — Difficulty · MUST

3-3's enemy bullets fly at ×1.1 their speed and its enemies fire at ×1.1 their rate. Its second half
has more enemy HP than its first.

**Acceptance criteria**
- Given level `3-3`, then its enemy difficulty is bullet speed 1.1 and fire rate 1.1.
- Unit test: 3-3's second half has more enemy HP than its first.

*Sources: P09-R08, D-080, D-090.*

### LVL-3-3-06 — Mini boss · MUST

3-3's mini boss is the [Stone Idol](../../bosses/mini/3-3-stone-idol.md), at the middle of the level
(150 s, 8 250 units), after a quiet stretch with no new wave. Its fight stops the ground (×0): World
3's fight over still ground (WLD-3-19).

**Acceptance criteria**
- Given 3-3, then its mini boss is the Stone Idol, at half the level's length, and its fight's ground speed factor is 0.

*Sources: P09-R09.*

### LVL-3-3-07 — Final boss · MUST

3-3's final boss is the [Sky Temple](../../bosses/final/3-3-sky-temple.md), at the end of the level
(300 s, 16 500 units); its fight runs the ground at ×0.3. 3-3 is complete when it is destroyed.

**Acceptance criteria**
- Given 3-3, then its final boss is the Sky Temple, at the level's end.

*Sources: P09-R09.*

### LVL-3-3-08 — Runout · MUST

`runout` seconds of ground like the last section (the suburb edge) are drawn past the level's end for
the two fights.

**Acceptance criteria**
- Given 3-3, then its runout is 70 s (3 850 units).

*Sources: P07-R03.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| ground_speed | 55 units/s | `LEVEL_3_3.scrollSpeed`, `src/game/config/world_3/scenery.py` |
| level_length | 16 500 units (300 s) | `WORKERS_QUARTER` |
| seed | 3301 | `LEVEL_3_3.seed` |
| streets / terraced streets / suburb streets | rows 45–90 × columns 50–110 / 33–56 × 38–76 / 40–70 × 50–95 | `STREETS`, `TERRACE_STREETS`, `SUBURB_STREETS` |
| storm start | clouds 0.5 / 0.5, storm 0.3 | `LEVEL_3_3_LOOK`, `src/game/config/world_3/looks.py` |
| thunderstorm | clouds 0.9 / 0.9, storm 1, lightning 1, built over 0–75 s | `THUNDERSTORM` |
| rain | 0.8 | `THUNDERSTORM.weather` |
| wave_gap | 4.6 s → 3.1 s | `PLAN_3_3.gap`, `src/game/config/world_3/waves.py` |
| wave_growth | 0.6 | `PLAN_3_3.growth` |
| filler_gap | 2.8 s → 1.8 s | `WORLD_3_FILLERS["3-3"].maxGap` |
| bullet speed / fire rate factors | 1.1 / 1.1 | `WORLD_3_DIFFICULTY["3-3"]` |
| measured | 190.0 enemies/min, 6 452 HP/min, peak 45 | D-090 |
| runout | 70 s | `WORLD_3_BOSSES["3-3"].runout` |

## Notes

- The "canal park" is named after the canal it no longer has (see WLD-3-10).
- Before the rework (D-111) 3-3 was the lost temples, whose Stone Idol stopped the ground over a
  temple; it now stops over the workers' quarter.
