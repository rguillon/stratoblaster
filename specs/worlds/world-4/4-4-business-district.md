# Level 4-4 — Business district

> **Area:** worlds · **Prefix:** `LVL-4-4` · **Related:** [World 4](world.md), [4-3 Midtown](4-3-midtown.md), [4-5 Downtown](4-5-downtown.md), [Furnace Drake](../../bosses/mini/4-4-furnace-drake.md), [Foundry Ark](../../bosses/final/4-4-foundry-ark.md), [level flow](../../gameplay/level-flow.md), [weather](../../graphics/weather.md)

The fourth level of World 4. From the tower edge 4-3 ended on, the player flies among city towers, over
a tower park and the financial district, where the first skyscrapers rise, and high rise, to the first
skyline, at midday under an orange glow, ash falling and embers rising together. Hives and Hydras
lead the waves, all five kinds of tier 4 in the mix. Its checkpoint is its mini boss (see
[level flow](../../gameplay/level-flow.md)).

## Requirements

### LVL-4-4-01 — Identity and duration · MUST

Level `4-4`, named "Business district", is the fourth level of World 4. Its scenery is `world-4-4`,
built from seed 4401. Its ground scrolls at `ground_speed` for `level_length`: 300 s.

**Acceptance criteria**
- Given level `4-4`, then its scenery id is `world-4-4`, its seed 4401, its ground speed 55 and its length 16 500 units (300 s).

*Sources: P10-R02, P10-R03, D-112.*

### LVL-4-4-02 — Scenery sections · MUST

4-4's ground is these sections, in this order, blending over World 4's `section_transition`, every one
on the flat, fully paved city ground (WLD-4-08), with World 3's widest street blocks (`streets`):

| # | Section | Time | Length | Buildings (groups) | Building density |
|---|---------|------|--------|--------------------|------------------|
| 1 | Tower edge | 0–40 s | 2 200 | towers, offices | 1 |
| 2 | Business district | 40–100 s | 3 300 | towers | 1 |
| 3 | Tower park | 100–145 s | 2 475 | towers | 0.8 |
| 4 | Financial district | 145–200 s | 3 025 | towers, skyscrapers | 1 |
| 5 | High rise | 200–250 s | 2 750 | skyscrapers, towers | 1 |
| 6 | Skyline edge | 250–300 s | 2 750 | skyscrapers | 1 |

The first section is the one 4-3 ended on; the last, the first skyline, is where 4-5 begins. The first
skyscrapers come in the financial district.

**Acceptance criteria**
- Given 4-4's scenery, then its sections are these, in this order, with these lengths, groups and densities, all city-only.
- Given 4-4's first section, then it is 4-3's last section, shortened to 40 s.

*Sources: P10-R03, D-112, D-126.*

### LVL-4-4-03 — Look · MUST

4-4 is World 4's bright **midday** (WLD-4-14), clouds at cover 0.6 (low) and 0.5 (high), white (their
storm grey does not show, the clouds being plain), the haze and the ground lit from below by the
business district's orange glow (`underglow`), with **falling ash** and **rising embers** together, all
along the level. The windows and the cars are lit (World 4's ground lights).

**Acceptance criteria**
- Given 4-4's look, then it is midday with clouds 0.6 / 0.5, an orange underglow of 0.7, falling ash 0.3 and embers 0.3 as a second weather, with World 4's daylight.
- Given `?level=4-4&t=60`, then ash and embers fall and rise together, there is no lava, and the ground lights are above 1.

*Sources: P10-R04, P10-R06, D-126.*

### LVL-4-4-04 — Enemy waves · MUST

4-4 uses all five kinds of tier 4, Splitter, Juggernaut, Scissor, Hydra and Hive, and no other. 4-4's waves follow its wave plan (WLD-4-18) from 4 s to 292 s, with a beat every `wave_gap` seconds (3.4 s to 2.4 s) and
groups growing by `wave_growth` (105 %) over the level (100 beats). The cycle of phrases, each a kind with its number of
groups at the start: Splitter 2, Juggernaut 1, Scissor 1, Splitter 2, Hydra 1, Juggernaut 1, Splitter 2, Hive 1, Scissor 1, Juggernaut 1, Hydra 1. The filler draws Splitters and Juggernauts, at most `filler_gap` apart.

**Acceptance criteria**
- Unit test: 4-4's waves use exactly Splitter, Juggernaut, Scissor, Hydra and Hive, and each of them.
- Unit test: 4-4's waves are the same each time the level is built.

*Sources: P10-R09, P05-R24, D-087, D-090, ENM-50.*

### LVL-4-4-05 — Difficulty · MUST

4-4's enemy bullets fly at ×1.3 their speed and its enemies fire at ×1.3 their rate. Its second half
has more enemy HP than its first.

**Acceptance criteria**
- Given level `4-4`, then its enemy difficulty is bullet speed 1.3 and fire rate 1.3.
- Unit test: 4-4's second half has more enemy HP than its first.

*Sources: P10-R10, D-087, D-090.*

### LVL-4-4-06 — Mini boss · MUST

4-4's mini boss is the [Furnace Drake](../../bosses/mini/4-4-furnace-drake.md), at the middle of the
level (150 s, 8 250 units), after a quiet stretch with no new wave. Its fight runs the ground at ×0.5.

**Acceptance criteria**
- Given 4-4, then its mini boss is the Furnace Drake, at half the level's length.

*Sources: P10-R11.*

### LVL-4-4-07 — Final boss · MUST

4-4's final boss is the [Foundry Ark](../../bosses/final/4-4-foundry-ark.md), at the end of the level
(300 s, 16 500 units); its fight runs the ground at ×0.3. 4-4 is complete when it is destroyed.

**Acceptance criteria**
- Given 4-4, then its final boss is the Foundry Ark, at the level's end.

*Sources: P10-R11.*

### LVL-4-4-08 — Runout · MUST

`runout` seconds of ground like the last section (the skyline edge) are drawn past the level's end for
the two fights.

**Acceptance criteria**
- Given 4-4, then its runout is 100 s (5 500 units).

*Sources: P07-R03.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| ground_speed | 55 units/s | `LEVEL_4_4.scrollSpeed`, `src/game/config/world_4/scenery.py` |
| level_length | 16 500 units (300 s) | `BUSINESS_DISTRICT` |
| seed | 4401 | `LEVEL_4_4.seed` |
| streets | rows 45–90, columns 50–110 | `STREETS`, `src/game/config/world_3/scenery.py` |
| clouds | 0.6 / 0.5, storm 0.6 (not shown) | `LEVEL_4_4_LOOK`, `src/game/config/world_4/looks.py` |
| underglow | colour 1, 0.5, 0.15; 0.7 | `FURNACE_GLOW`, `LEVEL_4_4_LOOK` |
| ash / embers | 0.3 / 0.3 | `LEVEL_4_4_LOOK.start.weather`, `.secondWeather` |
| wave_gap | 3.4 s → 2.4 s | `PLAN_4_4.gap`, `src/game/config/world_4/waves.py` |
| wave_growth | 1.05 | `PLAN_4_4.growth` |
| filler_gap | 2.9 s → 1.8 s | `WORLD_4_FILLERS["4-4"].maxGap` |
| bullet speed / fire rate factors | 1.3 / 1.3 | `WORLD_4_DIFFICULTY["4-4"]` |
| measured | 225.0 enemies/min, 11 238 HP/min, peak 62 | D-090 |
| runout | 100 s | `WORLD_4_BOSSES["4-4"].runout` |

## Notes

- 4-4 was a night lit by the towers before D-126; it is now at midday, its windows and cars still lit
  as at night (WLD-4-14).
- Before the rework (D-112) 4-4 was the forge belt, which gave the Furnace Drake and the Foundry Ark
  their names.
