# Level 3-2 — Docklands

> **Area:** worlds · **Prefix:** `LVL-3-2` · **Related:** [World 3](world.md), [3-1 Canal works](3-1-canal-works.md), [3-3 Workers' quarter](3-3-workers-quarter.md), [Toucan](../../bosses/mini/3-2-toucan.md), [Canopy Spider](../../bosses/final/3-2-canopy-spider.md), [level flow](../../gameplay/level-flow.md), [weather](../../graphics/weather.md)

The second level of World 3. From the canal workshops 3-1 ended on, the player flies over warehouses
on the docks, workshop streets and old mills to the first workers' flats, under a bright midday sky
with a rain shower over the middle third. Phantoms, Spinners and Prisms lead its waves, and the
Mortar comes in. Its checkpoint is its mini boss (see
[level flow](../../gameplay/level-flow.md)).

## Requirements

### LVL-3-2-01 — Identity and duration · MUST

Level `3-2`, named "Docklands", is the second level of World 3. Its scenery is `world-3-2`, built from
seed 3201. Its ground scrolls at `ground_speed` for `level_length`: 300 s.

**Acceptance criteria**
- Given level `3-2`, then its scenery id is `world-3-2`, its seed 3201, its ground speed 60 and its length 18 000 units (300 s).

*Sources: P09-R02, P09-R03, D-111.*

### LVL-3-2-02 — Scenery sections · MUST

3-2's ground is these sections, in this order, blending over World 3's `section_transition`, all on
World 3's flat ground and widest street blocks (`streets`):

| # | Section | Time | Length | Paved / grass | Buildings (groups) | Building density |
|---|---------|------|--------|---------------|--------------------|------------------|
| 1 | Canal workshops | 0–40 s | 2 400 | 0.85 / 0.04 | workshops, industrial | 1 |
| 2 | Warehouse docks | 40–95 s | 3 300 | 0.84 / 0.04 | docks, workshops | 0.85 |
| 3 | Workshop streets | 95–150 s | 3 300 | 0.8 / 0.06 | workshops | 1 |
| 4 | Old mills | 150–200 s | 3 000 | 0.76 / 0.08 | workshops, industrial | 1 |
| 5 | Workers' blocks | 200–250 s | 3 000 | 0.72 / 0.1 | workshops, workers' flats | 1 |
| 6 | First flats | 250–300 s | 3 000 | 0.68 / 0.12 | workers' flats, workshops | 1 |

The first section is the one 3-1 ended on; the last, the first flats, is where 3-3 begins. The
warehouse docks are a little less dense (0.85) so the buildings keep growing in number from 3-1 to 3-5
on the grid of tiles (WLD-3-08). The canal runs on, wider at the docks (WLD-3-10).

**Acceptance criteria**
- Given 3-2's scenery, then its sections are these, in this order, with these lengths, covers, groups and densities.
- Given 3-2's first section, then it is 3-1's last section, shortened to 40 s.

*Sources: P09-R03, D-111, D-164.*

### LVL-3-2-03 — Look · MUST

3-2 is **midday**: bright, humid light under tall white cumulus, clouds at cover 0.5 (low) and 0.3
(high). A **rain shower** of strength `rain` covers the middle third: it comes in over 92–108 s and
clears over 192–208 s. No lightning.

**Acceptance criteria**
- Given 3-2's look, then it starts at midday with clouds 0.5 / 0.3 and no weather, changes over 92–108 s to the same with rain 0.4, and over 192–208 s back to no rain.
- Manual visual validation: a light, fast shower from 1:40 to 3:20.

*Sources: P09-R04, P09-R05, D-111.*

### LVL-3-2-04 — Enemy waves · MUST

3-2 adds the Mortar to the kinds of 3-1 and uses Phantom, Spinner, Prism and Mortar, no other. 3-2's waves follow its wave plan (WLD-3-16) from 4 s to 292 s, with a beat every `wave_gap` seconds (4.8 s to 3.5 s) and
groups growing by `wave_growth` (85 %) over the level (71 beats). The cycle of phrases, each a kind with its number of
groups at the start: Phantom 1, Spinner 2, Prism 1, Phantom 1, Mortar 1, Spinner 2, Phantom 1, Prism 1, Spinner 2, Mortar 1. The filler draws Phantoms and Spinners, at most `filler_gap` apart.

**Acceptance criteria**
- Unit test: 3-2's waves use exactly Phantom, Spinner, Prism and Mortar, and each of them.
- Unit test: 3-2's waves are the same each time the level is built.

*Sources: P09-R07, P05-R24, D-080, D-090, ENM-50.*

### LVL-3-2-05 — Difficulty · MUST

3-2's enemy bullets fly at ×1.05 their speed and its enemies fire at ×1.05 their rate. Its second half
has more enemy HP than its first.

**Acceptance criteria**
- Given level `3-2`, then its enemy difficulty is bullet speed 1.05 and fire rate 1.05.
- Unit test: 3-2's second half has more enemy HP than its first.

*Sources: P09-R08, D-080, D-090.*

### LVL-3-2-06 — Mini boss · MUST

3-2's mini boss is the [Toucan](../../bosses/mini/3-2-toucan.md), at the middle of the level (150 s,
9 000 units), after a quiet stretch with no new wave. Its fight runs the ground at ×0.6.

**Acceptance criteria**
- Given 3-2, then its mini boss is the Toucan, at half the level's length.

*Sources: P09-R09.*

### LVL-3-2-07 — Final boss · MUST

3-2's final boss is the [Canopy Spider](../../bosses/final/3-2-canopy-spider.md), at the end of the level
(300 s, 18 000 units); its fight runs the ground at ×0.4. 3-2 is complete when it is destroyed.

**Acceptance criteria**
- Given 3-2, then its final boss is the Canopy Spider, at the level's end.

*Sources: P09-R09.*

### LVL-3-2-08 — Runout · MUST

`runout` seconds of ground like the last section (the first flats) are drawn past the level's end for
the two fights.

**Acceptance criteria**
- Given 3-2, then its runout is 100 s (6 000 units).

*Sources: P07-R03.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| ground_speed | 60 units/s | `LEVEL_3_2.scrollSpeed`, `src/game/config/world_3/scenery.py` |
| level_length | 18 000 units (300 s) | `DOCKLANDS` |
| seed | 3201 | `LEVEL_3_2.seed` |
| streets | rows 45–90, columns 50–110 | `STREETS` |
| clouds | 0.5 / 0.3 | `MIDDAY`, `src/game/config/world_3/looks.py` |
| rain | 0.4, in over 92–108 s, out over 192–208 s | `LEVEL_3_2_LOOK` |
| wave_gap | 4.8 s → 3.5 s | `PLAN_3_2.gap`, `src/game/config/world_3/waves.py` |
| wave_growth | 0.85 | `PLAN_3_2.growth` |
| filler_gap | 3.2 s → 2.1 s | `WORLD_3_FILLERS["3-2"].maxGap` |
| bullet speed / fire rate factors | 1.05 / 1.05 | `WORLD_3_DIFFICULTY["3-2"]` |
| measured | 184.0 enemies/min, 5 494 HP/min, peak 38 | D-090 |
| runout | 100 s | `WORLD_3_BOSSES["3-2"].runout` |

## Notes

- Before the rework (D-111) 3-2 was the rainforest, under a green canopy tint, which the rework dropped.
