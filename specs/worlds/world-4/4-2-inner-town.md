# Level 4-2 — Inner town

> **Area:** worlds · **Prefix:** `LVL-4-2` · **Related:** [World 4](world.md), [4-1 Garden town](4-1-garden-town.md), [4-3 Midtown](4-3-midtown.md), [Ash Wraith](../../bosses/mini/4-2-ash-wraith.md), [Geyser Rig](../../bosses/final/4-2-geyser-rig.md), [level flow](../../gameplay/level-flow.md), [weather](../../graphics/weather.md)

The second level of World 4. From the town centre 4-1 ended on, the player flies over town streets,
the ring road, mid-rise flats and a city park to mid-rise blocks among the first offices, at midday
under an ash cloud with ash falling. Splitters and Spinners lead the waves and the Scissor comes in.
Its mini boss is a chase. Its checkpoint is its mini boss (see [level flow](../../gameplay/level-flow.md)).

## Requirements

### LVL-4-2-01 — Identity and duration · MUST

Level `4-2`, named "Inner town", is the second level of World 4. Its scenery is `world-4-2`, built from
seed 4201. Its ground scrolls at `ground_speed` for `level_length`: 300 s.

**Acceptance criteria**
- Given level `4-2`, then its scenery id is `world-4-2`, its seed 4201, its ground speed 65 and its length 19 500 units (300 s).

*Sources: P10-R02, P10-R03, D-112.*

### LVL-4-2-02 — Scenery sections · MUST

4-2's ground is these sections, in this order, blending over World 4's `section_transition`, every one
on the flat, fully paved city ground (WLD-4-08):

| # | Section | Time | Length | Buildings (groups) | Streets | Building density |
|---|---------|------|--------|--------------------|---------|------------------|
| 1 | Town centre | 0–40 s | 2 600 | workers' flats, town centre | streets | 1 |
| 2 | Town streets | 40–100 s | 3 900 | town centre | streets | 1 |
| 3 | Ring road | 100–150 s | 3 250 | town centre, mid-rise | streets | 1 |
| 4 | Mid-rise flats | 150–205 s | 3 575 | mid-rise | streets | 1 |
| 5 | City park | 205–250 s | 2 925 | mid-rise | suburb streets | 0.8 |
| 6 | Midrise edge | 250–300 s | 3 250 | mid-rise, offices | streets | 1 |

The first section is the one 4-1 ended on; the last, where the first offices mix in, is where 4-3
begins. No city tower and no skyscraper stands in 4-2 (but see the discrepancy under WLD-4-07).

**Acceptance criteria**
- Given 4-2's scenery, then its sections are these, in this order, with these lengths, groups, streets and densities, all city-only.
- Given 4-2's first section, then it is 4-1's last section, shortened to 40 s.

*Sources: P10-R03, D-112, D-126.*

### LVL-4-2-03 — Look: under an ash cloud · MUST

4-2 is World 4's bright **midday** (WLD-4-14) under an **ash cloud**: clouds at cover 0.9 / 0.9 (white;
their brown-grey tint does not show, the clouds being plain), a dim, flat, yellowish ambient light
(`ash_light`), and **falling ash** of strength `ash` all along the level. No glow from below.

**Acceptance criteria**
- Given 4-2's look, then it is midday with clouds 0.9 / 0.9, the yellowish ambient tint and falling ash 0.5, with World 4's daylight.
- Given `?level=4-2&t=60`, then ash falls (0.5) and there is no lava; with `&weather=0`, no ash.

*Sources: P10-R04, P10-R06, D-126.*

### LVL-4-2-04 — Enemy waves · MUST

4-2's waves follow its wave plan (WLD-4-18) from 4 s to 292 s, with a beat every `wave_gap` seconds and
groups growing by `wave_growth`. The cycle: Splitter 3, Spinner 3, Scout 4, Splitter 3, Lancer 2,
Spinner 2, Weaver 4, Rocketeer 2, Splitter 3, Bulwark 1, Strafer 3 (from the right), Spinner 3,
Carrier 1, Hornet 5, Gnat 3, Splitter 3, Spinner 2, Wasp 2, Mortar 1, Minelayer 1 (from the right),
Mantis 1, Phantom 1, Hydra 1, Orbiter 1, Scissor 1. Splitters and Spinners (four phrases each a cycle)
lead the waves over the inner town. The filler draws Splitters, Gnats, Weavers, Hornets, Scouts and
Spinners, at most `filler_gap` apart. 4-2 uses every basic and veteran kind, the Hydra, the Orbiter
and the Scissor.

**Acceptance criteria**
- Unit test: 4-2's waves use the eleven basic kinds, the five veteran kinds, the Hydra, the Orbiter and the Scissor, and no other elite kind.
- Unit test: 4-2's waves are the same each time the level is built.

*Sources: P10-R09, P05-R24, D-087, D-090.*

### LVL-4-2-05 — Difficulty · MUST

4-2's enemy bullets fly at ×1.15 their speed and its enemies fire at ×1.15 their rate. Its second half
has more enemy HP than its first.

**Acceptance criteria**
- Given level `4-2`, then its enemy difficulty is bullet speed 1.15 and fire rate 1.15.
- Unit test: 4-2's second half has more enemy HP than its first.

*Sources: P10-R10, D-087, D-090.*

### LVL-4-2-06 — Mini boss · MUST

4-2's mini boss is the [Ash Wraith](../../bosses/mini/4-2-ash-wraith.md), at the middle of the level
(150 s, 9 750 units), after a quiet stretch with no new wave. Its fight is a chase: the ground runs at
×1.5.

**Acceptance criteria**
- Given 4-2, then its mini boss is the Ash Wraith, at half the level's length, and its fight's ground speed factor is above 1.

*Sources: P10-R11.*

### LVL-4-2-07 — Final boss · MUST

4-2's final boss is the [Geyser Rig](../../bosses/final/4-2-geyser-rig.md), at the end of the level
(300 s, 19 500 units); its fight runs the ground at ×0.4. 4-2 is complete when it is destroyed.

**Acceptance criteria**
- Given 4-2, then its final boss is the Geyser Rig, at the level's end.

*Sources: P10-R11.*

### LVL-4-2-08 — Runout · MUST

`runout` seconds of ground like the last section (the midrise edge) are drawn past the level's end for
the two fights, the longest runout of World 4, as the chase runs the ground ahead.

**Acceptance criteria**
- Given 4-2, then its runout is 150 s (9 750 units).

*Sources: P07-R03.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| ground_speed | 65 units/s | `LEVEL_4_2.scrollSpeed`, `src/game/config/world_4/scenery.py` |
| level_length | 19 500 units (300 s) | `INNER_TOWN` |
| seed | 4201 | `LEVEL_4_2.seed` |
| streets | streets 45–90 × 50–110; suburb 40–70 × 50–95 (rows × columns) | `STREETS`, `SUBURB_STREETS`, `src/game/config/world_3/scenery.py` |
| clouds | 0.9 / 0.9 (tint 0.8, 0.72, 0.62, not shown) | `LEVEL_4_2_LOOK`, `src/game/config/world_4/looks.py` |
| ash_light | ambient × 1.04, 0.96, 0.74 | `ASH_LIGHT` |
| ash | 0.5 | `LEVEL_4_2_LOOK.start.weather` |
| wave_gap | 3 s → 2.1 s | `PLAN_4_2.gap`, `src/game/config/world_4/waves.py` |
| wave_growth | 1.1 | `PLAN_4_2.growth` |
| filler_gap | 2.6 s → 1.7 s | `WORLD_4_FILLERS["4-2"].maxGap` |
| bullet speed / fire rate factors | 1.15 / 1.15 | `WORLD_4_DIFFICULTY["4-2"]` |
| measured | 204.4 enemies/min, 9 216 HP/min, peak 55 | D-090 |
| runout | 150 s | `WORLD_4_BOSSES["4-2"].runout` |

## Notes

- The city park was a park with grass and a wider stretch of the river before D-126; it is now a
  stretch of fewer mid-rise blocks.
