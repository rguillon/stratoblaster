# Level 3-4 — Suburbs

> **Area:** worlds · **Prefix:** `LVL-3-4` · **Related:** [World 3](world.md), [3-3 Workers' quarter](3-3-workers-quarter.md), [3-5 Garden villages](3-5-garden-villages.md), [Mosquito](../../bosses/mini/3-4-mosquito.md), [Dam Breaker](../../bosses/final/3-4-dam-breaker.md), [level flow](../../gameplay/level-flow.md), [sky and light](../../graphics/sky-and-light.md)

The fourth level of World 3. From the suburb edge 3-3 ended on, the player flies over garden suburbs,
houses along the river, a town park and leafy avenues to the first garden villages, on gently rolling
ground, at a rainy dusk with the windows and streets lit. No industry is left. Broodmothers and Prisms lead
the waves, all five kinds of tier 3 in the mix. Its checkpoint is its mini boss (see
[level flow](../../gameplay/level-flow.md)).

## Requirements

### LVL-3-4-01 — Identity and duration · MUST

Level `3-4`, named "Suburbs", is the fourth level of World 3. Its scenery is `world-3-4`, built from
seed 3401. Its ground scrolls at `ground_speed` for `level_length`: 300 s.

**Acceptance criteria**
- Given level `3-4`, then its scenery id is `world-3-4`, its seed 3401, its ground speed 60 and its length 18 000 units (300 s).

*Sources: P09-R02, P09-R03, D-111.*

### LVL-3-4-02 — Scenery sections · MUST

3-4's ground is these sections, in this order, blending over World 3's `section_transition`, all on
World 3's rolling ground:

| # | Section | Time | Length | Paved / grass | Buildings (groups) | Streets | Building density |
|---|---------|------|--------|---------------|--------------------|---------|------------------|
| 1 | Suburb edge | 0–40 s | 2 400 | 0.42 / 0.4 | residences | suburb streets | 1 |
| 2 | Garden suburbs | 40–100 s | 3 600 | 0.36 / 0.46 | residences | suburb streets | 1 |
| 3 | River suburbs | 100–155 s | 3 300 | 0.3 / 0.52 | residences | garden suburb streets | 1 |
| 4 | Town park | 155–200 s | 2 700 | 0.2 / 0.7 | residences | streets | 1 |
| 5 | Leafy avenues | 200–255 s | 3 300 | 0.26 / 0.58 | residences | avenue streets | 1 |
| 6 | Village edge | 255–300 s | 2 700 | 0.2 / 0.65 | residences, garden villages | suburb streets | 1 |

The first section is the one 3-3 ended on; the last, the village edge, where the first garden villages
mix in, is where 3-5 begins. No industrial, dock, workshop or flats group stands in 3-4. The river
suburbs and the leafy avenues have their own, closer blocks and the park's buildings fill every slot,
so the buildings keep growing in number (WLD-3-08). The river runs between grassy banks (WLD-3-10).

**Acceptance criteria**
- Given 3-4's scenery, then its sections are these, in this order, with these lengths, covers, groups, streets and densities.
- Given 3-4's first section, then it is 3-3's last section, shortened to 40 s.

*Sources: P09-R03, D-111, D-139, D-164.*

### LVL-3-4-03 — Look · MUST

3-4 is a **dusk**: clouds at cover 0.6 (low) and 0.4 (high), orange to purple, and a light rain of
strength `rain` all along the level. The ground lights are on: the windows of the homes and the
streets.

**Acceptance criteria**
- Given 3-4's look, then it is dusk with clouds 0.6 / 0.4 and rain 0.3, with no change along the level.
- Manual visual validation: a rainy dusk over lit homes.

*Sources: P09-R04, P09-R05, D-111.*

### LVL-3-4-04 — Enemy waves · MUST

3-4 uses all five kinds of tier 3, Phantom, Spinner, Prism, Mortar and Broodmother, and no other. 3-4's waves follow its wave plan (WLD-3-16) from 4 s to 292 s, with a beat every `wave_gap` seconds (4 s to 2.9 s) and
groups growing by `wave_growth` (95 %) over the level (85 beats). The cycle of phrases, each a kind with its number of
groups at the start: Phantom 1, Spinner 2, Prism 1, Phantom 1, Mortar 1, Spinner 2, Phantom 1, Broodmother 1, Prism 1, Spinner 2, Mortar 1. The filler draws Phantoms and Spinners, at most `filler_gap` apart.

**Acceptance criteria**
- Unit test: 3-4's waves use exactly Phantom, Spinner, Prism, Mortar and Broodmother, and each of them.
- Unit test: 3-4's waves are the same each time the level is built.

*Sources: P09-R07, P05-R24, D-080, D-090, ENM-50.*

### LVL-3-4-05 — Difficulty · MUST

3-4's enemy bullets fly at ×1.2 their speed and its enemies fire at ×1.2 their rate. Its second half
has more enemy HP than its first.

**Acceptance criteria**
- Given level `3-4`, then its enemy difficulty is bullet speed 1.2 and fire rate 1.2.
- Unit test: 3-4's second half has more enemy HP than its first.

*Sources: P09-R08, D-080, D-090.*

### LVL-3-4-06 — Mini boss · MUST

3-4's mini boss is the [Mosquito](../../bosses/mini/3-4-mosquito.md), at the middle of the level (150 s,
9 000 units), after a quiet stretch with no new wave. Its fight runs the ground at ×0.6.

**Acceptance criteria**
- Given 3-4, then its mini boss is the Mosquito, at half the level's length.

*Sources: P09-R09.*

### LVL-3-4-07 — Final boss · MUST

3-4's final boss is the [Dam Breaker](../../bosses/final/3-4-dam-breaker.md), at the end of the level
(300 s, 18 000 units); its fight runs the ground at ×0.3. 3-4 is complete when it is destroyed.

**Acceptance criteria**
- Given 3-4, then its final boss is the Dam Breaker, at the level's end.

*Sources: P09-R09.*

### LVL-3-4-08 — Runout · MUST

`runout` seconds of ground like the last section (the village edge) are drawn past the level's end for
the two fights.

**Acceptance criteria**
- Given 3-4, then its runout is 100 s (6 000 units).

*Sources: P07-R03.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| ground_speed | 60 units/s | `LEVEL_3_4.scrollSpeed`, `src/game/config/world_3/scenery.py` |
| level_length | 18 000 units (300 s) | `SUBURBS` |
| seed | 3401 | `LEVEL_3_4.seed` |
| streets | suburb 40–70 × 50–95; garden suburb 36–62 × 46–88; streets 45–90 × 50–110; avenue 36–62 × 40–78 (rows × columns) | `SUBURB_STREETS`, `GARDEN_SUBURB_STREETS`, `STREETS`, `AVENUE_STREETS` |
| clouds | 0.6 / 0.4 | `LEVEL_3_4_LOOK`, `src/game/config/world_3/looks.py` |
| rain | 0.3 | same |
| wave_gap | 4 s → 2.9 s | `PLAN_3_4.gap`, `src/game/config/world_3/waves.py` |
| wave_growth | 0.95 | `PLAN_3_4.growth` |
| filler_gap | 2.9 s → 1.8 s | `WORLD_3_FILLERS["3-4"].maxGap` |
| bullet speed / fire rate factors | 1.2 / 1.2 | `WORLD_3_DIFFICULTY["3-4"]` |
| measured | 219.0 enemies/min, 7 744 HP/min, peak 50 | D-090 |
| runout | 100 s | `WORLD_3_BOSSES["3-4"].runout` |

## Notes

- The "river suburbs" are named after the river they no longer have (see WLD-3-10).
- Before the rework (D-111) 3-4 was the swamp works with a giant dam, which gave the Dam Breaker its name.
