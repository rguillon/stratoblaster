# 2-5 Factory district

> **Area:** Worlds · **Prefix:** `LVL-2-5` · **Related:** [World 2](world.md), [2-4 Industrial belt](2-4-industrial-belt.md), [3-1 Canal works](../world-3/3-1-canal-works.md), [Ice Queen](../../bosses/mini/2-5-ice-queen.md), [Boreal Citadel](../../bosses/final/2-5-boreal-citadel.md), [level flow](../../gameplay/level-flow.md), [terrain](../../graphics/terrain.md), [sky and light](../../graphics/sky-and-light.md)

The last and hardest level of World 2: night over the factory district, lit by the factories'
windows, neon, streets and cars, from the factory district 2-4 ended on, through foundries, rail
yards and heavy industry, to great works filling every block at the end. Paved to the end. Tier 2 brings
60 % of the enemies and tier 3 the other 40 %. The Ice Queen waits at the
middle and the Boreal Citadel at the end.

## Requirements

### Identity

#### LVL-2-5-01 — Identity · MUST

Level `2-5` is the fifth and last level of World 2. It is named "Factory district"; its scenery is
`world-2-5`, generated from the seed `seed`.

**Acceptance criteria**
- Given the game's levels, then the tenth is `2-5`, named "2-5 Factory district", with the scenery `world-2-5` and its seed (unit test).

*Sources: P08-R03, D-110.*

#### LVL-2-5-02 — Duration and ground speed · MUST

2-5 scrolls at `ground_speed` for `duration`: its sections' seconds add up to 300, so its length is
18 000 units. Its sections blend over 900 units (WLD-2-08).

**Acceptance criteria**
- Given 2-5, then its length ÷ its ground speed is 300 s (unit test, e2e).

*Sources: P08-R02, GD-01, D-110.*

#### LVL-2-5-03 — Night over the factories · MUST

2-5 is at night, the whole level long: the engine's `night` preset (a dim, cold moonlight that
shows the ground's shapes), the thickest clouds of World 2 (`clouds`), greyed by the smog
(`storm`), the fog of World 2's looks (`fog`), the window, neon, street and car lights on and
bright, no weather and no aurora. The ground is dark, but the player ship, the enemies, their shots
and the bonuses keep their shapes and colours.

**Acceptance criteria**
- Given the 2-5 look, then it is `night` with cloud cover 0.4 / 0.3, storm 0.35, no weather and no change within the level (unit test on the data).
- Given `?level=2-5&t=120` (e2e), then no weather particle and no aurora are drawn, the ground lights are over 1 and the sun is weaker than 2-1's.
- Manual visual validation: the night level stays readable; ship, enemies, shots and bonuses clearly visible.

*Sources: P08-R04, P08-R06, D-110.*

### Scenery

#### LVL-2-5-04 — Sections · MUST

2-5's ground is these sections, in this order (relief: height ± its amplitude, features about that
wide across); there is no sea:

| # | Section | Seconds | Relief | Cover | Buildings (density) | What it shows |
|---|---------|---------|--------|-------|---------------------|---------------|
| 1 | factory district | 40 | 32 ± 3, 600 | sand 0.1, paved 0.78 | heavy industry, industrial (1), streets | 2-4's factory district. |
| 2 | foundries | 60 | 32 ± 3, 600 | sand 0.08, paved 0.82 | heavy industry, industrial (0.8), streets | Foundries and factories along streets. |
| 3 | rail yards | 50 | 32 ± 2, 600 | sand 0.06, paved 0.86 | industrial (0.85), streets | Rail yards and works. |
| 4 | heavy industry | 70 | 32 ± 2, 600 | sand 0.04, paved 0.92 | heavy industry, industrial (1), streets | Dense heavy industry. |
| 5 | great works | 80 | 32 ± 2, 600 | paved 1 | heavy industry (1), streets, every block filled | Great works filling every block, where World 3 begins. |

**Acceptance criteria**
- Given 2-5, then its sections are these, in this order, with these seconds (unit test on the data).
- Given 2-4's last section and 2-5's first, then they have the same relief, cover and groups (unit test, WLD-2-10).
- Manual visual validation: `?level=2-5&t=70` the foundries, `&t=280` the great works.

*Sources: P08-R03, D-110.*

#### LVL-2-5-05 — The great works · MUST

2-5 ends on heavy industry only (WLD-2-09): its last section, the great works, is all paved, and
every part of every block of its street grid gets a plant or works, side by side
(`great_works_blocks`). World 3's first level begins on this section
([3-1](../world-3/3-1-canal-works.md)).

**Acceptance criteria**
- Given 2-5's last section, then it lists only the heavy-industry group, is all paved and fills its blocks (unit test on the data).

*Sources: P08-R03, D-110, D-111.*

#### LVL-2-5-06 — Buildings and roads · MUST

2-5's habitations are factories, foundries, rail yards and heavy industry, then the great works (the
groups of the table above, WLD-2-13), the fullest level of World 2. It has World 1's roads
(WLD-2-14). No tree grows.

**Acceptance criteria**
- Given 2-5 placed with its seed, then it has more buildings than 2-4, and its second half more than its first (unit test, WLD-2-11).

*Sources: P08-R03, P08-R07, D-110.*

### Waves

#### LVL-2-5-07 — Enemy kinds · MUST

2-5 mixes two tiers: tier 2 (the main one) is 60 % of its enemy ships and tier 3 40 % (each within 5 points; a Wasp group counts as its 5 ships, and the filler is counted with the beats). It brings every kind of both tiers, each at least once: tier 2's Wasp, Strafer, Harrier, Sweeper and Hatchery; tier 3's Phantom, Spinner, Mortar, Prism and Broodmother, and no other kind.

**Acceptance criteria**
- Given the 2-5 wave script, then it only uses the kinds of tiers 2 and 3, and it uses each of them (unit test).
- Given 2-5 assembled, then each tier's share of its enemy ships is within 5 points of its target (unit test).

*Sources: P06-R07, ENM-50, D-283.*

#### LVL-2-5-08 — Wave plan · MUST

2-5's waves are composed from this plan (WLD-2-19; World 1's density and filler apply on top):

Beats from 4 s to 292 s, each wave followed by a breather of 2.3 s at the start down to 1.6 s at the end, groups growing by 90 % over the level. Each beat goes to the tier furthest below its share of the ships so far (the filler that follows a beat counted with it). A tier's beats first bring each of its five kinds once (shooter, laser, missile, carrier, then diver; one group each outside the main tier), then follow the role cycle (shooter, diver, laser, diver, missile, shooter, diver, carrier, laser, shooter, missile). A wave brings no more groups than its tier lacks, the main tier's never fewer than written.

No wave starts in the 10 s before each boss ([level-flow.md](../../gameplay/level-flow.md)): the beats are composed around these stretches, so none is dropped.

**Acceptance criteria**
- Given the 2-5 plan, then it composes beats that name its kinds and sides in order of time (unit test).

*Sources: P06-R07, D-067, ENM-50, D-283.*

#### LVL-2-5-09 — Filler · MUST

2-5's filler (WLD-1-21) brings the divers and shooters of the level's tiers, Wasp, Strafer, Phantom and Spinner: after a wave of one of them, single groups of its kind in the lull, one every `max_gap`.

**Acceptance criteria**
- Given the 2-5 filler, then its kinds are the Wasp, the Strafer, the Phantom and the Spinner only and its gap shrinks (unit test).

*Sources: D-051, ENM-50, D-283.*

### Difficulty

#### LVL-2-5-10 — The hardest level so far · MUST

2-5's enemies fire at `fire_rate_factor` of their rate and their bullets fly at
`bullet_speed_factor` of their speed, the highest of Worlds 1 and 2. Per minute of scroll it has the
most enemies, the most enemy HP and the highest peak on screen of World 2, and more than 1-5
(WLD-2-20, WLD-2-23); its second half more HP than its first.

**Acceptance criteria**
- Given the 2-5 difficulty, then both factors are 1.15 (unit test).
- Manual validation: 2-5 feels clearly harder than 1-5.

*Sources: P08-R09, D-067.*

### Bosses

#### LVL-2-5-11 — Mini boss: Ice Queen · MUST

The [Ice Queen](../../bosses/mini/2-5-ice-queen.md) comes at the middle of 2-5's length
(9 000 units, 2:30), over the heavy industry. Destroying it saves the level's checkpoint
([level-flow.md](../../gameplay/level-flow.md)).

**Acceptance criteria**
- Given 2-5, then its mini boss is the Ice Queen, at half its length (unit test).

*Sources: GD-41, GD-42, P08-R10.*

#### LVL-2-5-12 — Final boss: Boreal Citadel · MUST

The [Boreal Citadel](../../bosses/final/2-5-boreal-citadel.md) comes at the end of 2-5's length
(18 000 units, 5:00), at night over the great works; destroying it completes the level and World 2,
and the level select then highlights `3-1` (WLD-2-02).

**Acceptance criteria**
- Given 2-5, then its final boss is the Boreal Citadel, at its length (unit test).

*Sources: GD-41, P08-R10.*

#### LVL-2-5-13 — Runout · MUST

`runout` seconds of the last section's ground (the great works) are drawn past the level's end, for
the ground that gets ahead of the level during the fights.

**Acceptance criteria**
- Given 2-5, then its runout is 80 s (unit test on the data).

*Sources: D-054.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| seed | 2501 | `src/game/config/world_2/scenery.py` `LEVEL_2_5` |
| ground_speed | 60 units/s | `LEVEL_2_5.scrollSpeed` |
| duration | 300 s (18 000 units) | sum of the sections' `seconds` |
| look | `night`, clouds 0.4 / 0.3, storm 0.35, no weather | `src/game/config/world_2/looks.py` `LEVEL_2_5_LOOK` |
| fog / glow | 1 100 → 2 800 / 0.4 | World 2's looks |
| great_works_blocks | no podium, 16 works per block | `GREAT_WORKS.blocks` |
| streets | rows 45–90, columns 50–110, links 0.6 | `STREETS` |
| max_gap | 2.8 s → 1.6 s | `src/game/config/world_2/waves.py` `WORLD_2_FILLERS["2-5"]` |
| bullet_speed_factor / fire_rate_factor | 1.15 / 1.15 | `src/game/config/world_2/difficulty.py` |
| written | beats composed from the plan and its tier mix (D-283); waves, groups, enemies and HP after fill and density: to be measured again | `src/game/config/wave_plans.py` `level_plan(2, 5)`, `tier_mix(2, 5)`; density 2 (D-249) |
| buildings | 33 934 (halves 16 196 / 17 738) | each level's seed, measured for this file |
| mini boss / final boss | `ice-queen` / `boreal-citadel` | `src/game/config/world_2/bosses.py` |
| runout | 80 s | same |

## Notes

- Before the 2026-10-27 rework (D-110), 2-5 was a polar city at dusk turning to night under an
  aurora; the Ice Queen and the Boreal Citadel were made for it.
- The busiest moments of World 2 for the frame rate are 2-5's end and its final fight at night over
  the factories ([performance.md](../../performance.md)).
