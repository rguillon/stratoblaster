# Level 3-5 — Garden villages

> **Area:** worlds · **Prefix:** `LVL-3-5` · **Related:** [World 3](world.md), [3-4 Suburbs](3-4-suburbs.md), [4-1 Garden town](../world-4/4-1-garden-town.md), [Jaguar](../../bosses/mini/3-5-jaguar.md), [Verdant Crown](../../bosses/final/3-5-verdant-crown.md), [level flow](../../gameplay/level-flow.md), [sky and light](../../graphics/sky-and-light.md)

The last level of World 3. From the village edge 3-4 ended on, the player flies over a village green,
allotments and cottages to garden villages of small houses, which last to the end, on gently rolling
ground, on a rainy night whose clouds open on a moonlit sky before the final boss. Bulwarks escort
Carriers in the heaviest mixes of World 3, and the Phantom comes in. World 4 begins where 3-5 ends.
Its checkpoint is its mini boss (see [level flow](../../gameplay/level-flow.md)).

## Requirements

### LVL-3-5-01 — Identity and duration · MUST

Level `3-5`, named "Garden villages", is the last level of World 3. Its scenery is `world-3-5`, built
from seed 3501. Its ground scrolls at `ground_speed` for `level_length`: 300 s.

**Acceptance criteria**
- Given level `3-5`, then its scenery id is `world-3-5`, its seed 3501, its ground speed 60 and its length 18 000 units (300 s).

*Sources: P09-R02, P09-R03, D-111.*

### LVL-3-5-02 — Scenery sections · MUST

3-5's ground is these sections, in this order, blending over World 3's `section_transition`, all on
World 3's rolling ground:

| # | Section | Time | Length | Paved / grass | Buildings (groups) | Streets | Building density |
|---|---------|------|--------|---------------|--------------------|---------|------------------|
| 1 | Village edge | 0–40 s | 2 400 | 0.2 / 0.65 | residences, garden villages | suburb streets | 1 |
| 2 | Village green | 40–100 s | 3 600 | 0.16 / 0.72 | garden villages, residences | village streets | 1 |
| 3 | Allotments | 100–150 s | 3 000 | 0.12 / 0.78 | garden villages | village streets | 1 |
| 4 | Riverside cottages | 150–205 s | 3 300 | 0.12 / 0.78 | garden villages | village streets | 1 |
| 5 | Garden villages | 205–300 s | 5 700 | 0.1 / 0.82 | garden villages | lanes | 1 |

The first section is the one 3-4 ended on. The last, the garden villages (small houses only, on the
closest lanes), is where World 4 begins: 4-1's first section has its building group and lanes (see
[4-1](../world-4/4-1-garden-town.md)). No industry, no flats and no tower stand in 3-5. The river runs
on and ponds lie among the gardens (WLD-3-10).

**Acceptance criteria**
- Given 3-5's scenery, then its sections are these, in this order, with these lengths, covers, groups, streets and densities.
- Given 3-5's first section, then it is 3-4's last section, shortened to 40 s.
- Given 3-5's last section, then it holds the garden villages group only.

*Sources: P09-R03, D-111.*

### LVL-3-5-03 — Look · MUST

3-5 is a **night**: clouds at cover 0.6 (low) and 0.4 (high) and rain of strength `rain`, the windows
of the villages lit and glowing in the rain. Over 250–275 s the rain stops and the clouds open to
0.2 / 0.1 on a moonlit sky, before the final boss.

**Acceptance criteria**
- Given 3-5's look, then it starts at night with clouds 0.6 / 0.4 and rain 0.5, and changes over 250–275 s to night with clouds 0.2 / 0.1 and no rain.
- Given `?level=3-5&t=60`, then it rains (0.5) over the lit villages.
- Manual visual validation: the player ship, enemies, shots and bonuses stay clearly visible at night.

*Sources: P09-R04, P09-R05, D-111.*

### LVL-3-5-04 — Enemy waves · MUST

3-5 uses all five kinds of tier 3, Phantom, Spinner, Prism, Mortar and Broodmother, and no other. 3-5's waves follow its wave plan (WLD-3-16) from 4 s to 292 s, with a beat every `wave_gap` seconds (3.6 s to 2.6 s) and
groups growing by `wave_growth` (100 %) over the level (94 beats). The cycle of phrases, each a kind with its number of
groups at the start: Phantom 1, Spinner 2, Prism 1, Phantom 1, Mortar 1, Spinner 2, Phantom 1, Broodmother 1, Prism 1, Spinner 2, Mortar 1. The filler draws Phantoms and Spinners, at most `filler_gap` apart.

**Acceptance criteria**
- Unit test: 3-5's waves use exactly Phantom, Spinner, Prism, Mortar and Broodmother, and each of them.
- Unit test: 3-5's waves are the same each time the level is built.

*Sources: P09-R07, P05-R24, D-080, D-090, ENM-50.*

### LVL-3-5-05 — Difficulty · MUST

3-5's enemy bullets fly at ×1.25 their speed and its enemies fire at ×1.25 their rate, the most of
World 3, above 2-5's. Its second half has more enemy HP than its first.

**Acceptance criteria**
- Given level `3-5`, then its enemy difficulty is bullet speed 1.25 and fire rate 1.25.
- Unit test: 3-5's second half has more enemy HP than its first.

*Sources: P09-R08, D-080, D-090.*

### LVL-3-5-06 — Mini boss · MUST

3-5's mini boss is the [Jaguar](../../bosses/mini/3-5-jaguar.md), at the middle of the level (150 s,
9 000 units), after a quiet stretch with no new wave. Its fight runs the ground at ×0.6.

**Acceptance criteria**
- Given 3-5, then its mini boss is the Jaguar, at half the level's length.

*Sources: P09-R09.*

### LVL-3-5-07 — Final boss · MUST

3-5's final boss is the [Verdant Crown](../../bosses/final/3-5-verdant-crown.md), World 3's last boss,
at the end of the level (300 s, 18 000 units); its fight runs the ground at ×0.25. 3-5 is complete
when it is destroyed, and the level select then highlights `4-1`.

**Acceptance criteria**
- Given 3-5, then its final boss is the Verdant Crown, at the level's end.
- Given `?level=3-5&boss=final`, when K destroys the boss and the "Level complete" is confirmed, then `level-select` shows with `4-1` highlighted.

*Sources: P09-R09, P10-R01.*

### LVL-3-5-08 — Runout · MUST

`runout` seconds of ground like the last section (the garden villages) are drawn past the level's end
for the two fights.

**Acceptance criteria**
- Given 3-5, then its runout is 100 s (6 000 units).

*Sources: P07-R03.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| ground_speed | 60 units/s | `LEVEL_3_5.scrollSpeed`, `src/game/config/world_3/scenery.py` |
| level_length | 18 000 units (300 s) | `GARDEN_VILLAGES` |
| seed | 3501 | `LEVEL_3_5.seed` |
| streets | suburb 40–70 × 50–95; village 40–70 × 45–90; lanes 35–60 × 40–80 (rows × columns) | `SUBURB_STREETS`, `VILLAGE_STREETS`, `LANES` |
| clouds | 0.6 / 0.4, opening to 0.2 / 0.1 over 250–275 s | `LEVEL_3_5_LOOK`, `src/game/config/world_3/looks.py` |
| rain | 0.5, stopping over 250–275 s | same |
| wave_gap | 3.6 s → 2.6 s | `PLAN_3_5.gap`, `src/game/config/world_3/waves.py` |
| wave_growth | 1 | `PLAN_3_5.growth` |
| filler_gap | 2.8 s → 1.6 s | `WORLD_3_FILLERS["3-5"].maxGap` |
| bullet speed / fire rate factors | 1.25 / 1.25 | `WORLD_3_DIFFICULTY["3-5"]` |
| measured | 247.8 enemies/min, 8 952 HP/min, peak 53 | D-090 (2-5: 233.4, 7 360, 51) |
| runout | 100 s | `WORLD_3_BOSSES["3-5"].runout` |

## Notes

- The "riverside cottages" are named after the river they no longer have, and the ponds are not drawn
  (see WLD-3-10).
- The garden villages are small homes of the future on paved plots (D-160, D-207), not the farmhouses
  and greenhouses of World 1 the rework first used.
- Before the rework (D-111) 3-5 was a canopy city with towers.
