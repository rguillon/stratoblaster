# Level 4-5 — Downtown

> **Area:** worlds · **Prefix:** `LVL-4-5` · **Related:** [World 4](world.md), [4-4 Business district](4-4-business-district.md), [Ember Herald](../../bosses/mini/4-5-ember-herald.md), [Caldera Throne](../../bosses/final/4-5-caldera-throne.md), [level flow](../../gameplay/level-flow.md), [weather](../../graphics/weather.md)

The last level of World 4 and of the game. From the skyline 4-4 ended on, the player flies over
skyscrapers, a central park, and downtown blocks filled with skyscrapers side by side to the city's
heart, at midday while a volcano erupts somewhere beyond downtown: the glow from below turns deep red
and the embers grow to their strongest by the final boss. Its waves are the heaviest of the game, and
its final boss, the Caldera Throne, is the game's last and hardest. Its checkpoint is its mini boss
(see [level flow](../../gameplay/level-flow.md)).

## Requirements

### LVL-4-5-01 — Identity and duration · MUST

Level `4-5`, named "Downtown", is the last level of World 4 and of the game. Its scenery is
`world-4-5`, built from seed 4501. Its ground scrolls at `ground_speed` for `level_length`: 300 s.

**Acceptance criteria**
- Given level `4-5`, then its scenery id is `world-4-5`, its seed 4501, its ground speed 55 and its length 16 500 units (300 s).

*Sources: P10-R02, P10-R03, D-112.*

### LVL-4-5-02 — Scenery sections · MUST

4-5's ground is these sections, in this order, blending over World 4's `section_transition`, every one
on the flat, fully paved city ground (WLD-4-08), with World 3's widest street blocks (`streets`):

| # | Section | Time | Length | Buildings (groups) | Building density | Blocks |
|---|---------|------|--------|--------------------|------------------|--------|
| 1 | Skyline edge | 0–40 s | 2 200 | skyscrapers | 1 | |
| 2 | Skyscrapers | 40–100 s | 3 300 | skyscrapers | 1 | |
| 3 | Central park | 100–140 s | 2 200 | skyscrapers | 0.7 | |
| 4 | Downtown | 140–210 s | 3 850 | skyscrapers, downtown | 0.7 | filled side by side |
| 5 | City heart | 210–300 s | 4 950 | downtown | 0.7 | filled side by side |

The first section is the one 4-4 ended on. Downtown and the city heart fill every block with
buildings side by side; their density is 0.7 so fewer low lots stand among the skyscrapers and the
buildings keep growing taller on the grid of tiles (WLD-4-06). The last section holds skyscrapers only.

**Acceptance criteria**
- Given 4-5's scenery, then its sections are these, in this order, with these lengths, groups, densities and blocks, all city-only.
- Given 4-5's first section, then it is 4-4's last section, shortened to 40 s.
- Given 4-5's last section, then it holds the downtown group (skyscrapers) only.

*Sources: P10-R03, D-112, D-126, D-164.*

### LVL-4-5-03 — Look: the eruption · MUST

4-5 is World 4's bright **midday** (WLD-4-14), clouds at cover 0.7 (low) and 0.6 (high), white (the
clouds being plain). A volcano erupts beyond downtown: the haze and the ground are lit from below by a
deep red glow (`underglow`) and **embers** rise (`embers`), and over 180–300 s the glow and the embers
grow to their strongest, which they keep for the final boss.

**Acceptance criteria**
- Given 4-5's look, then it starts at midday with clouds 0.7 / 0.6, a red underglow of 0.6 and embers 0.6, and changes over 180–300 s to an underglow of 1 and embers 1, with World 4's daylight.
- Given `?level=4-5&boss=final`, then 4-5 starts at the Caldera Throne's arrival, with embers at full strength, no lava, and the ground lights above 1.
- Manual validation: the embers are never confused with enemy bullets in the eruption.

*Sources: P10-R04, P10-R06, D-126.*

### LVL-4-5-04 — Enemy waves · MUST

4-5 uses all five kinds of tier 4, Splitter, Juggernaut, Scissor, Hydra and Hive, and no other. 4-5's waves follow its wave plan (WLD-4-18) from 4 s to 292 s, with a beat every `wave_gap` seconds (3 s to 2.2 s) and
groups growing by `wave_growth` (110 %) over the level (113 beats). The cycle of phrases, each a kind with its number of
groups at the start: Splitter 2, Juggernaut 1, Scissor 1, Splitter 2, Hydra 1, Juggernaut 1, Splitter 2, Hive 1, Scissor 1, Juggernaut 1, Hydra 1. The filler draws Splitters and Juggernauts, at most `filler_gap` apart.

**Acceptance criteria**
- Unit test: 4-5's waves use exactly Splitter, Juggernaut, Scissor, Hydra and Hive, and each of them.
- Unit test: 4-5's waves are the same each time the level is built.

*Sources: P10-R09, P05-R24, D-087, D-090, ENM-50.*

### LVL-4-5-05 — Difficulty · MUST

4-5's enemy bullets fly at ×1.35 their speed and its enemies fire at ×1.35 their rate, the most of the
game. Its second half has more enemy HP than its first. It is the hardest level of the game and still
beatable (WLD-4-20).

**Acceptance criteria**
- Given level `4-5`, then its enemy difficulty is bullet speed 1.35 and fire rate 1.35.
- Unit test: 4-5's second half has more enemy HP than its first.

*Sources: P10-R10, D-087, D-090.*

### LVL-4-5-06 — Mini boss · MUST

4-5's mini boss is the [Ember Herald](../../bosses/mini/4-5-ember-herald.md), at the middle of the
level (150 s, 8 250 units), after a quiet stretch with no new wave. Its fight is a chase: the ground
runs at ×1.4.

**Acceptance criteria**
- Given 4-5, then its mini boss is the Ember Herald, at half the level's length, and its fight's ground speed factor is above 1.

*Sources: P10-R11.*

### LVL-4-5-07 — Final boss · MUST

4-5's final boss is the [Caldera Throne](../../bosses/final/4-5-caldera-throne.md), the game's last
boss, at the end of the level (300 s, 16 500 units). Its fight stops the ground (×0) over downtown.
4-5 is complete when it is destroyed, and the level select then keeps `4-5` highlighted.

**Acceptance criteria**
- Given 4-5, then its final boss is the Caldera Throne, at the level's end, and its fight's ground speed factor is 0.
- Given `?level=4-5&boss=final`, when K destroys the boss and the "Level complete" is confirmed, then `level-select` shows with `4-5` highlighted.

*Sources: P10-R11, P10-R01.*

### LVL-4-5-08 — Runout · MUST

`runout` seconds of ground like the last section (the city heart) are drawn past the level's end for
the two fights: the mini boss's chase runs the ground ahead.

**Acceptance criteria**
- Given 4-5, then its runout is 130 s (7 150 units).

*Sources: P07-R03.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| ground_speed | 55 units/s | `LEVEL_4_5.scrollSpeed`, `src/game/config/world_4/scenery.py` |
| level_length | 16 500 units (300 s) | `DOWNTOWN` |
| seed | 4501 | `LEVEL_4_5.seed` |
| streets | rows 45–90, columns 50–110 | `STREETS`, `src/game/config/world_3/scenery.py` |
| filled blocks | no podium, towers 16 | `FILLED_BLOCKS` |
| clouds | 0.7 / 0.6 | `LEVEL_4_5_LOOK`, `src/game/config/world_4/looks.py` |
| underglow | colour 1, 0.16, 0.08; 0.6 → 1 over 180–300 s | `ERUPTION_RED`, `LEVEL_4_5_LOOK` |
| embers | 0.6 → 1 over 180–300 s | same |
| wave_gap | 3 s → 2.2 s | `PLAN_4_5.gap`, `src/game/config/world_4/waves.py` |
| wave_growth | 1.1 | `PLAN_4_5.growth` |
| filler_gap | 2.8 s → 1.6 s | `WORLD_4_FILLERS["4-5"].maxGap` |
| bullet speed / fire rate factors | 1.35 / 1.35 | `WORLD_4_DIFFICULTY["4-5"]` |
| measured | 302.0 enemies/min, 13 752 HP/min, peak 64 | D-090 (3-5: 247.8, 8 952, 53) |
| runout | 130 s | `WORLD_4_BOSSES["4-5"].runout` |

## Notes

- 4-5 was a night eruption over a magma lake before the rework (D-112) and D-126; the Caldera Throne,
  which rose from the lake and stopped the ground over it, now stops over downtown.
