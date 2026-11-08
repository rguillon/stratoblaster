# 1-4 Dry lands

> **Area:** Worlds · **Prefix:** `LVL-1-4` · **Related:** [World 1](world.md), [1-3 Green country](1-3-green-country.md), [1-5 Deep desert](1-5-deep-desert.md), [Scorpion](../../bosses/mini/1-4-scorpion.md), [Refinery Titan](../../bosses/final/1-4-refinery-titan.md), [level flow](../../gameplay/level-flow.md), [terrain](../../graphics/terrain.md), [sky and light](../../graphics/sky-and-light.md)

The fourth level of World 1: sunset over the dry lands, from the dry grassland 1-3 ended on into an
American desert of red dirt and scrub, rock, a cracked dry lake, an oasis town, a canyon, mesas and a
desert town, to the desert outskirts. No sea, no sand dunes. Tier 1 brings 65 % of the
enemies, tier 2 35 %. The Scorpion waits at the middle and the Refinery Titan at the end.

## Requirements

### Identity

#### LVL-1-4-01 — Identity · MUST

Level `1-4` is the fourth level of World 1. It is named "Dry lands"; its scenery is `world-1-4`,
generated from the seed `seed`.

**Acceptance criteria**
- Given the game's levels, then the fourth is `1-4`, named "1-4 Dry lands", with the scenery `world-1-4` and its seed (unit test).

*Sources: P06-R05, D-109.*

#### LVL-1-4-02 — Duration and ground speed · MUST

1-4 scrolls at `ground_speed` for `duration`: its sections' seconds add up to 240, so its length is
14 400 units. Its sections blend over 420 units.

**Acceptance criteria**
- Given 1-4, then its length ÷ its ground speed is 240 s (unit test, e2e).

*Sources: P06-R04, GD-01, D-109.*

#### LVL-1-4-03 — Sunset · MUST

1-4 is at sunset, the whole level long:
- a low orange sun (`sun`), long shadows;
- a magenta haze, an orange horizon, a violet zenith; a warm violet ambient light (`ambient`), a
  little stronger than in the day levels;
- a farther fog than the base look's (`fog`);
- few clouds, tinted orange and pink (`clouds`);
- the window, street and car lights a little brighter (`ground_lights`); no weather.

**Acceptance criteria**
- Given the 1-4 look, then its sun is lower than 1-3's and higher than 1-5's (unit test, WLD-1-16).
- Manual visual validation: a sunset over red land, and the ships stay easy to see.

*Sources: P06-R10, D-109.*

### Scenery

#### LVL-1-4-04 — Sections · MUST

1-4's ground is these sections, in this order (relief: height ± its amplitude, features about that
wide across; scarps: the hills with one rocky face of WLD-1-31, their height / wavelength, on the
open land only); there is no sea. The cover is the sections' `sandy` cover, drawn as the red desert dirt
(WLD-1-10); where a section's covers add up to less than 1, the dried earth shows.

| # | Section | Seconds | Relief | Cover | Buildings (density) | What it shows |
|---|---------|---------|--------|-------|---------------------|---------------|
| 1 | dry grassland | 30 | 28 ± 10, 560, scarps 32 / 360 | grass 0.2 | villages, outposts (0.75) | 1-3's dry grassland. |
| 2 | scrubland villages | 40 | 30 ± 14, 520, scarps 28 / 360 | sandy 0.35 | desert homes, outposts (1) | Dried earth and red dirt, villages of desert homes. |
| 3 | rock and scrub | 20 | 20 ± 90 ridged, 520, cut at 120 | sandy 1 | outposts (0.6) | Rocky ridges. |
| 4 | dry lake | 20 | 3 ± 2, 700 | sandy 1 | outposts (0.4) | A flat, low dry lake bed: cracked hardpan. |
| 5 | oasis town | 45 | 28 ± 12, 520 | sandy 0.75, grass 0.25 | desert homes (1), streets | An oasis town on a street grid, a little grass. |
| 6 | canyon | 20 | 95 ± 22, 380, a canyon cut in it | sandy 1 | outposts (0.5) | A high plateau cut by a winding canyon. |
| 7 | mesas | 20 | 30 ± 150, 560, cut at 100 | sandy 1 | outposts (0.9) | Flat-topped mesas with red walls. |
| 8 | desert town | 25 | 30 ± 4, 600 | sandy 0.8, paved 0.15 | desert homes (1), streets | A desert town on a street grid. |
| 9 | desert outskirts | 20 | 30 ± 8, 560, scarps 24 / 360 | sandy 0.85 | desert homes, outposts (1) | The outskirts of the desert towns, where 1-5 begins. |

**Acceptance criteria**
- Given 1-4, then its sections are these, in this order, with these seconds (unit test on the data).
- Given 1-3's last section and 1-4's first, then they have the same relief, cover and groups (unit test, WLD-1-08).
- Manual visual validation: `?level=1-4&t=20` the dry grassland, `&t=96` the dry lake, `&t=182` the mesas.

*Sources: P06-R05, D-109, D-200.*

#### LVL-1-4-05 — Dry lake, canyon and mesas · MUST

The bare stretches of 1-4 are short, so the buildings keep growing in number (WLD-1-09):
- the dry lake lies all under the low-ground height, so its whole bed is the cracked hardpan;
- the canyon is a channel (`canyon`) winding along the level through a high plateau, its walls of
  red layered rock;
- the mesas are a high relief cut flat at a top height, red rock on their steep walls;
- no section has sand dunes (WLD-1-10).

**Acceptance criteria**
- Given the dry lake's relief, then its highest point is under the low-ground height (unit test).
- Given 1-4's sections, then none has dunes (unit test).
- Manual visual validation: a cracked dry lake, a canyon and mesas, nothing like sand dunes.

*Sources: D-200, P06-R05.*

#### LVL-1-4-06 — Buildings and roads · MUST

1-4's habitations are dry-land villages, desert homes and outposts, an oasis town and a desert town
on street grids (the groups of the table above, WLD-1-13), with a few lone buildings and hamlets
(WLD-1-15); no mine and no industry (WLD-1-11). It has World 1's two main roads.

**Acceptance criteria**
- Given 1-4 placed with its seed, then it has more buildings than 1-3 and fewer than 1-5, and its second half more than its first (unit test, WLD-1-09).

*Sources: P06-R05, P06-R06, D-109, D-207, D-046.*

#### LVL-1-4-07 — Dying woods and dead trees · MUST

The dry grassland grows dying woods (living and dead trees mixed); the desert sections grow sparse
patches of dead trees with a few standing alone (`desert_woods`); the dry lake only a lone dead tree
here and there (`lone_dead_trees`) (WLD-1-14).

**Acceptance criteria**
- Manual visual validation: pale dead trees in patches on the red ground, almost none in the towns.

*Sources: D-214, D-212.*

### Waves

#### LVL-1-4-08 — Enemy kinds · MUST

1-4 mixes two tiers: tier 1 (the main one) is 65 % of its enemy ships and tier 2 35 % (each within 5 points; a Wasp group counts as its 5 ships, and the filler is counted with the beats). It brings every kind of both tiers, each at least once: tier 1's Hornet, Scout, Rocketeer, Lancer and Carrier; tier 2's Wasp, Strafer, Harrier, Sweeper and Hatchery, and no other kind.

**Acceptance criteria**
- Given the 1-4 wave script, then it only uses the kinds of tiers 1 and 2, and it uses each of them (unit test).
- Given 1-4 assembled, then each tier's share of its enemy ships is within 5 points of its target (unit test).

*Sources: P06-R07, ENM-50, D-283.*

#### LVL-1-4-09 — Wave plan · MUST

1-4's waves are composed from this plan (WLD-1-19; the density of WLD-1-20 applies on top):

Beats from 4 s to 226 s, each wave followed by a breather of 2.8 s at the start down to 2 s at the end, groups growing by 75 % over the level. Each beat goes to the tier furthest below its share of the ships so far (the filler that follows a beat counted with it). A tier's beats first bring each of its five kinds once (shooter, laser, missile, carrier, then diver; one group each outside the main tier), then follow the role cycle (shooter, diver, laser, diver, missile, shooter, diver, carrier, laser, shooter, missile). A wave brings no more groups than its tier lacks, the main tier's never fewer than written.

No wave starts in the 10 s before each boss ([level-flow.md](../../gameplay/level-flow.md)): the beats are composed around these stretches, so none is dropped.

**Acceptance criteria**
- Given the 1-4 plan, then it composes beats that name its kinds and sides in order of time (unit test).

*Sources: P06-R07, D-067, ENM-50, D-283.*

#### LVL-1-4-10 — Filler · MUST

1-4's filler (WLD-1-21) brings the divers and shooters of the level's tiers, Hornet, Scout, Wasp and Strafer: after a wave of one of them, single groups of its kind in the lull, one every `max_gap`.

**Acceptance criteria**
- Given the 1-4 filler, then its kinds are the Hornet, the Scout, the Wasp and the Strafer only and its gap shrinks (unit test).

*Sources: D-051, ENM-50, D-283.*

### Difficulty

#### LVL-1-4-11 — Difficulty · MUST

1-4's enemies fire at `fire_rate_factor` of their rate and their bullets fly at
`bullet_speed_factor` of their speed: the kinds' own values. It has more enemies, more enemy
HP and a higher peak on screen than 1-3, fewer than 1-5 (WLD-1-22), its second half more than its
first.

**Acceptance criteria**
- Given the 1-4 difficulty, then both factors are 1 (unit test).

*Sources: P06-R08, D-038.*

### Bosses

#### LVL-1-4-12 — Mini boss: Scorpion · MUST

The [Scorpion](../../bosses/mini/1-4-scorpion.md) comes at the middle of 1-4's length
(7 200 units, 2:00), over the oasis town. Destroying it saves the level's checkpoint
([level-flow.md](../../gameplay/level-flow.md)).

**Acceptance criteria**
- Given 1-4, then its mini boss is the Scorpion, at half its length (unit test).

*Sources: GD-41, GD-42, P07-R05, P07-R06.*

#### LVL-1-4-13 — Final boss: Refinery Titan · MUST

The [Refinery Titan](../../bosses/final/1-4-refinery-titan.md) comes at the end of 1-4's length
(14 400 units, 4:00), over the desert outskirts; destroying it completes the level.

**Acceptance criteria**
- Given 1-4, then its final boss is the Refinery Titan, at its length (unit test).

*Sources: GD-41, P07-R05, P07-R06.*

#### LVL-1-4-14 — Runout · MUST

`runout` seconds of the last section's ground (the desert outskirts) are drawn past the level's
end, for the ground that gets ahead of the level during the fights.

**Acceptance criteria**
- Given 1-4, then its runout is 70 s (unit test on the data).

*Sources: D-054.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| seed | 1401 | `src/game/config/world_1/scenery_desert.py` `LEVEL_1_4` |
| ground_speed | 60 units/s | `LEVEL_1_4.scrollSpeed` |
| duration | 240 s (14 400 units) | sum of the sections' `seconds` |
| sun | elevation 14°, azimuth 40°, colour (1, 0.64, 0.38), intensity 1.6 | `src/game/config/world_1/looks.py` `LEVEL_1_4_LOOK` |
| sky | haze (0.86, 0.56, 0.52), horizon (1, 0.62, 0.36), zenith (0.26, 0.24, 0.52), environment 0.6 | same |
| ambient | sky (0.66, 0.56, 0.72), ground (0.46, 0.32, 0.24), intensity 0.7 | same |
| fog | 1 100 → 2 800 | same |
| clouds | low 0.14, high 0.1, colour (1, 0.72, 0.56), shade (0.62, 0.4, 0.5) | same |
| ground_lights | prop light intensity 1.15 | same (`props.lightIntensity`) |
| ground | `DRY_TERRAIN`: dried earth, desert dirt, hardpan under the low height 7, mesa rock from slope 0.2 | `looks.py` (D-200, D-240) |
| canyon | channel x 0 ± 140 every 1 900 units, half width 40, walls 110, floor 10 | `DRY_LANDS` |
| desert_woods / lone_dead_trees | cover 0.55, keep 0.15, scatter 0.01 / cover 0, keep 0, scatter 0.004 | `src/game/config/trees.py` |
| max_gap | 3.2 s → 2 s | `src/game/config/world_1/waves.py` `WORLD_1_FILLERS["1-4"]` |
| bullet_speed_factor / fire_rate_factor | 1 / 1 | `src/game/config/world_1/difficulty.py` |
| written | beats composed from the plan and its tier mix (D-283); waves, groups, enemies and HP after fill and density: to be measured again | `src/game/config/wave_plans.py` `level_plan(1, 4)`, `tier_mix(1, 4)`; density 2 (D-249) |
| buildings | 14 909 (halves 2 290 / 12 619) | each level's seed, measured for this file |
| mini boss / final boss | `scorpion` / `refinery-titan` | `src/game/config/world_1/bosses.py` |
| runout | 70 s | same |

## Notes

- Before D-200 (2026-10-30), 1-4's desert was sand with dunes; the "dunes" section became the dry
  lake and "sand and rock" became "rock and scrub". Before the 2026-10-27 amendment of D-109 its
  mesas had mines and it ended on mining outskirts.
- The Refinery Titan was named before World 1 lost its industry; it flies over desert outskirts.
