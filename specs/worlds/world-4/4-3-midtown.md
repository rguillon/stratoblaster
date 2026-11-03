# Level 4-3 — Midtown

> **Area:** worlds · **Prefix:** `LVL-4-3` · **Related:** [World 4](world.md), [4-2 Inner town](4-2-inner-town.md), [4-4 Business district](4-4-business-district.md), [Magma Salamander](../../bosses/mini/4-3-magma-salamander.md), [Obsidian Golem](../../bosses/final/4-3-obsidian-golem.md), [level flow](../../gameplay/level-flow.md), [weather](../../graphics/weather.md)

The third level of World 4. From the mid-rise blocks 4-2 ended on, the player flies over offices among
mid-rise blocks, office blocks, the old river quays and plazas to the first city towers, at midday,
embers rising and the city's orange glow growing from below. Lancers and Rocketeers lead the waves and
the Hive comes in. Its checkpoint is its mini boss (see [level flow](../../gameplay/level-flow.md)).

## Requirements

### LVL-4-3-01 — Identity and duration · MUST

Level `4-3`, named "Midtown", is the third level of World 4. Its scenery is `world-4-3`, built from
seed 4301. Its ground scrolls at `ground_speed` for `level_length`: 300 s.

**Acceptance criteria**
- Given level `4-3`, then its scenery id is `world-4-3`, its seed 4301, its ground speed 60 and its length 18 000 units (300 s).

*Sources: P10-R02, P10-R03, D-112.*

### LVL-4-3-02 — Scenery sections · MUST

4-3's ground is these sections, in this order, blending over World 4's `section_transition`, every one
on the flat, fully paved city ground (WLD-4-08), with World 3's widest street blocks (`streets`):

| # | Section | Time | Length | Buildings (groups) | Building density |
|---|---------|------|--------|--------------------|------------------|
| 1 | Midrise edge | 0–40 s | 2 400 | mid-rise, offices | 1 |
| 2 | Midtown | 40–100 s | 3 600 | offices, mid-rise | 1 |
| 3 | Office blocks | 100–155 s | 3 300 | offices | 1 |
| 4 | River quays | 155–205 s | 3 000 | offices | 1 |
| 5 | Plazas | 205–250 s | 2 700 | offices, towers | 1 |
| 6 | Tower edge | 250–300 s | 3 000 | towers, offices | 1 |

The first section is the one 4-2 ended on; the last, where the city towers take over, is where 4-4
begins. The first city towers come in the plazas. No skyscraper stands in 4-3 (but see the discrepancy
under WLD-4-07).

**Acceptance criteria**
- Given 4-3's scenery, then its sections are these, in this order, with these lengths, groups and densities, all city-only.
- Given 4-3's first section, then it is 4-2's last section, shortened to 40 s.

*Sources: P10-R03, D-112, D-126.*

### LVL-4-3-03 — Look: the city's glow takes over · MUST

4-3 is World 4's bright **midday** (WLD-4-14), clouds at cover 0.5 (low) and 0.4 (high), white (their
storm grey does not show, the clouds being plain), with **embers** of strength `embers` rising all
along the level. The orange glow of the city lights the haze and the ground from below, growing from
`underglow` at the start to its end value over 60–280 s.

**Acceptance criteria**
- Given 4-3's look, then it starts at midday with clouds 0.5 / 0.4, embers 0.4 and an orange underglow of 0.25, and changes over 60–280 s to the same with an underglow of 0.8, with World 4's daylight.

*Sources: P10-R04, P10-R06, D-126.*

### LVL-4-3-04 — Enemy waves · MUST

4-3 brings in the Hive, the last kind of tier 4, and so uses Splitter, Juggernaut, Scissor, Hydra and Hive, no other. 4-3's waves follow its wave plan (WLD-4-18) from 4 s to 292 s, with a beat every `wave_gap` seconds (3.8 s to 2.7 s) and
groups growing by `wave_growth` (100 %) over the level (89 beats). The cycle of phrases, each a kind with its number of
groups at the start: Splitter 2, Juggernaut 1, Scissor 1, Splitter 2, Hydra 1, Juggernaut 1, Splitter 2, Hive 1, Scissor 1, Juggernaut 1, Hydra 1. The filler draws Splitters and Juggernauts, at most `filler_gap` apart.

**Acceptance criteria**
- Unit test: 4-3's waves use exactly Splitter, Juggernaut, Scissor, Hydra and Hive, and each of them.
- Unit test: 4-3's waves are the same each time the level is built.

*Sources: P10-R09, P05-R24, D-087, D-090, ENM-50.*

### LVL-4-3-05 — Difficulty · MUST

4-3's enemy bullets fly at ×1.2 their speed and its enemies fire at ×1.2 their rate. Its second half
has more enemy HP than its first.

**Acceptance criteria**
- Given level `4-3`, then its enemy difficulty is bullet speed 1.2 and fire rate 1.2.
- Unit test: 4-3's second half has more enemy HP than its first.

*Sources: P10-R10, D-087, D-090.*

### LVL-4-3-06 — Mini boss · MUST

4-3's mini boss is the [Magma Salamander](../../bosses/mini/4-3-magma-salamander.md), at the middle of
the level (150 s, 9 000 units), after a quiet stretch with no new wave. Its fight runs the ground at
×0.6.

**Acceptance criteria**
- Given 4-3, then its mini boss is the Magma Salamander, at half the level's length.

*Sources: P10-R11.*

### LVL-4-3-07 — Final boss · MUST

4-3's final boss is the [Obsidian Golem](../../bosses/final/4-3-obsidian-golem.md), at the end of the
level (300 s, 18 000 units); its fight runs the ground at ×0.3. 4-3 is complete when it is destroyed.

**Acceptance criteria**
- Given 4-3, then its final boss is the Obsidian Golem, at the level's end.

*Sources: P10-R11.*

### LVL-4-3-08 — Runout · MUST

`runout` seconds of ground like the last section (the tower edge) are drawn past the level's end for
the two fights.

**Acceptance criteria**
- Given 4-3, then its runout is 100 s (6 000 units).

*Sources: P07-R03.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| ground_speed | 60 units/s | `LEVEL_4_3.scrollSpeed`, `src/game/config/world_4/scenery.py` |
| level_length | 18 000 units (300 s) | `MIDTOWN` |
| seed | 4301 | `LEVEL_4_3.seed` |
| streets | rows 45–90, columns 50–110 | `STREETS`, `src/game/config/world_3/scenery.py` |
| clouds | 0.5 / 0.4, storm 0.5 (not shown) | `LEVEL_4_3_LOOK`, `src/game/config/world_4/looks.py` |
| embers | 0.4 | same |
| underglow | colour 1, 0.42, 0.12; 0.25 → 0.8 over 60–280 s | `LAVA_GLOW`, `LEVEL_4_3_LOOK` |
| wave_gap | 3.8 s → 2.7 s | `PLAN_4_3.gap`, `src/game/config/world_4/waves.py` |
| wave_growth | 1 | `PLAN_4_3.growth` |
| filler_gap | 3 s → 2 s | `WORLD_4_FILLERS["4-3"].maxGap` |
| bullet speed / fire rate factors | 1.2 / 1.2 | `WORLD_4_DIFFICULTY["4-3"]` |
| measured | 211.2 enemies/min, 10 644 HP/min, peak 57 | D-090 |
| runout | 100 s | `WORLD_4_BOSSES["4-3"].runout` |

## Notes

- 4-3 was a dusk turning to night before D-126 (the sunset fading while the glow took over); it is
  now at midday, keeping its clouds, embers and growing glow.
- The "river quays" section is named after the quays it no longer has (WLD-4-09). The glow's colour is
  still called `LAVA_GLOW` in the code, from the volcanic World 4.
