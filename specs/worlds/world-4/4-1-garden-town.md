# Level 4-1 — Garden town

> **Area:** worlds · **Prefix:** `LVL-4-1` · **Related:** [World 4](world.md), [3-5 Garden villages](../world-3/3-5-garden-villages.md), [4-2 Inner town](4-2-inner-town.md), [Cinder Crab](../../bosses/mini/4-1-cinder-crab.md), [Steam Dreadnought](../../bosses/final/4-1-steam-dreadnought.md), [level flow](../../gameplay/level-flow.md), [sky and light](../../graphics/sky-and-light.md)

The first level of World 4. From the garden villages 3-5 ended on, the player flies over suburban
lanes, suburbs, terraced streets and flats to a town centre with the first mid-rise blocks, on the
flat, fully paved city ground, at a bright midday under a smoke haze. Splitters and Juggernauts lead the
waves, and the Scissor comes in with them.
Its checkpoint is its mini boss (see [level flow](../../gameplay/level-flow.md)).

## Requirements

### LVL-4-1-01 — Identity and duration · MUST

Level `4-1`, named "Garden town", is the first level of World 4. Its scenery is `world-4-1`, built
from seed 4101. Its ground scrolls at `ground_speed` for `level_length`: 300 s.

**Acceptance criteria**
- Given level `4-1`, then its scenery id is `world-4-1`, its seed 4101, its ground speed 70 and its length 21 000 units (300 s).

*Sources: P10-R02, P10-R03, D-112.*

### LVL-4-1-02 — Scenery sections · MUST

4-1's ground is these sections, in this order, blending over World 4's `section_transition`, every one
on the flat, fully paved city ground (WLD-4-08):

| # | Section | Time | Length | Buildings (groups) | Streets | Building density |
|---|---------|------|--------|--------------------|---------|------------------|
| 1 | Garden villages | 0–40 s | 2 800 | garden villages | lanes | 1 |
| 2 | Suburban lanes | 40–95 s | 3 850 | garden villages, residences | lanes | 1 |
| 3 | Suburbs | 95–150 s | 3 850 | residences | village streets | 1 |
| 4 | Terraced streets | 150–200 s | 3 500 | residences | village streets | 1 |
| 5 | Flats | 200–250 s | 3 500 | residences, workers' flats | streets | 1 |
| 6 | Town centre | 250–300 s | 3 500 | workers' flats, town centre | streets | 1 |

The first section is 3-5's last, the garden villages, with the very same building group and lanes, on
the city ground. The last, the town centre, where the first mid-rise blocks mix in, is where 4-2
begins. No city tower and no skyscraper stands in 4-1.

**Acceptance criteria**
- Given 4-1's scenery, then its sections are these, in this order, with these lengths, groups, streets and densities, all city-only.
- Given 4-1's first section, then it has 3-5's last section's building group and streets.

*Sources: P10-R03, D-112, D-126.*

### LVL-4-1-03 — Look · MUST

4-1 is World 4's bright **midday** (WLD-4-14) under a **smoke haze**: the haze ends at `smoke_haze_fog`
of its clear distance and turns `smoke_haze_white` of the way to a pale colour. Clouds at cover 0.4
(low) and 0.3 (high), white (their ash-pink tint does not show, the clouds being plain). No weather and
no glow from below, with no change along the level.

**Acceptance criteria**
- Given 4-1's look, then it is midday with clouds 0.4 / 0.3, the smoke haze on, no weather and no underglow, with World 4's daylight.

*Sources: P10-R04, D-126.*

### LVL-4-1-04 — Enemy waves · MUST

4-1 brings Splitter, Juggernaut and Scissor (a diver, a shooter and a laser) and no other kind. 4-1's waves follow its wave plan (WLD-4-18) from 4 s to 292 s, with a beat every `wave_gap` seconds (4.6 s to 3.3 s) and
groups growing by `wave_growth` (90 %) over the level (74 beats). The cycle of phrases, each a kind with its number of
groups at the start: Splitter 2, Juggernaut 1, Scissor 1, Splitter 2, Juggernaut 1, Splitter 2, Scissor 1, Juggernaut 1. The filler draws Splitters and Juggernauts, at most `filler_gap` apart.

**Acceptance criteria**
- Unit test: 4-1's waves use exactly Splitter, Juggernaut and Scissor, and each of them.
- Unit test: 4-1's waves are the same each time the level is built.

*Sources: P10-R09, P05-R24, D-087, D-090, ENM-50.*

### LVL-4-1-05 — Difficulty · MUST

4-1's enemy bullets fly at ×1.1 their speed and its enemies fire at ×1.1 their rate, as in 3-3: a
fresh start after 3-5. Its second half has more enemy HP than its first.

**Acceptance criteria**
- Given level `4-1`, then its enemy difficulty is bullet speed 1.1 and fire rate 1.1.
- Unit test: 4-1's second half has more enemy HP than its first.

*Sources: P10-R10, D-087, D-090.*

### LVL-4-1-06 — Mini boss · MUST

4-1's mini boss is the [Cinder Crab](../../bosses/mini/4-1-cinder-crab.md), at the middle of the level
(150 s, 10 500 units), after a quiet stretch with no new wave. Its fight runs the ground at ×0.5.

**Acceptance criteria**
- Given 4-1, then its mini boss is the Cinder Crab, at half the level's length.

*Sources: P10-R11.*

### LVL-4-1-07 — Final boss · MUST

4-1's final boss is the [Steam Dreadnought](../../bosses/final/4-1-steam-dreadnought.md), at the end of
the level (300 s, 21 000 units); its fight runs the ground at ×0.6. 4-1 is complete when it is
destroyed.

**Acceptance criteria**
- Given 4-1, then its final boss is the Steam Dreadnought, at the level's end.
- Given `?level=4-1&boss=final`, when K destroys the boss, then "Level complete" shows `4-1` and confirming it highlights `4-2`.

*Sources: P10-R11.*

### LVL-4-1-08 — Runout · MUST

`runout` seconds of ground like the last section (the town centre) are drawn past the level's end for
the two fights.

**Acceptance criteria**
- Given 4-1, then its runout is 120 s (8 400 units).

*Sources: P07-R03.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| ground_speed | 70 units/s | `LEVEL_4_1.scrollSpeed`, `src/game/config/world_4/scenery.py` |
| level_length | 21 000 units (300 s) | `GARDEN_TOWN` |
| seed | 4101 | `LEVEL_4_1.seed` |
| streets | lanes 35–60 × 40–80; village 40–70 × 45–90; streets 45–90 × 50–110 (rows × columns) | `LANES`, `VILLAGE_STREETS`, `STREETS`, `src/game/config/world_3/scenery.py` |
| smoke_haze_fog / smoke_haze_white | 0.75 / 0.2 | `SMOKE_HAZE`, `src/game/config/world_4/looks.py` |
| clouds | 0.4 / 0.3 (tint 0.95, 0.84, 0.86, not shown) | `LEVEL_4_1_LOOK` |
| wave_gap | 4.6 s → 3.3 s | `PLAN_4_1.gap`, `src/game/config/world_4/waves.py` |
| wave_growth | 0.9 | `PLAN_4_1.growth` |
| filler_gap | 3.4 s → 2.3 s | `WORLD_4_FILLERS["4-1"].maxGap` |
| bullet speed / fire rate factors | 1.1 / 1.1 | `WORLD_4_DIFFICULTY["4-1"]` |
| measured | 195.2 enemies/min, 7 496 HP/min, peak 53 | D-090 (3-3: 190.0, 6 452, 45) |
| runout | 120 s | `WORLD_4_BOSSES["4-1"].runout`, `src/game/config/world_4/bosses.py` |

## Notes

- 4-1 was a red dawn before D-126; it is now at midday, keeping its smoke haze and cloud cover.
- The sections' data still give World 3's river and ponds and a grass cover; `city_only` drops them
  (WLD-4-08, WLD-4-09).
