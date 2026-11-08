# 2-3 Oil fields

> **Area:** Worlds · **Prefix:** `LVL-2-3` · **Related:** [World 2](world.md), [2-2 Mining mesas](2-2-mining-mesas.md), [2-4 Industrial belt](2-4-industrial-belt.md), [Snow Owl](../../bosses/mini/2-3-snow-owl.md), [Aurora Station](../../bosses/final/2-3-aurora-station.md), [level flow](../../gameplay/level-flow.md), [terrain](../../graphics/terrain.md), [sky and light](../../graphics/sky-and-light.md)

The middle level of World 2: a golden afternoon over the oil fields, from the oil edge 2-2 ended on,
through pumpjacks and tanks, a company town, refineries and tank farms, to the first factories at the
end, the ground more and more paved. The first smoke greys the clouds. Tier 2 brings 60 % of the
enemies, tiers 1 and 3 20 % each. The Snow Owl waits at the middle and the Aurora Station at the end.

## Requirements

### Identity

#### LVL-2-3-01 — Identity · MUST

Level `2-3` is the third level of World 2. It is named "Oil fields"; its scenery is `world-2-3`,
generated from the seed `seed`.

**Acceptance criteria**
- Given the game's levels, then the eighth is `2-3`, named "2-3 Oil fields", with the scenery `world-2-3` and its seed (unit test).

*Sources: P08-R03, D-110.*

#### LVL-2-3-02 — Duration and ground speed · MUST

2-3 scrolls at `ground_speed` for `duration`: its sections' seconds add up to 300, so its length is
18 000 units. Its sections blend over 900 units (WLD-2-08).

**Acceptance criteria**
- Given 2-3, then its length ÷ its ground speed is 300 s (unit test, e2e).

*Sources: P08-R02, GD-01, D-110.*

#### LVL-2-3-03 — Afternoon · MUST

2-3 is in the afternoon, the whole level long: the engine's `afternoon` preset (a golden light), two
layers of clouds a little thicker than 2-2's (`clouds`), greyed a little by the first smoke
(`storm`), the fog of World 2's looks (`fog`), the ground lights off, no weather.

**Acceptance criteria**
- Given the 2-3 look, then it is `afternoon` with cloud cover 0.25 / 0.2, storm 0.15, no weather and no change within the level (unit test on the data).

*Sources: P08-R04, P08-R06, D-110.*

### Scenery

#### LVL-2-3-04 — Sections · MUST

2-3's ground is these sections, in this order (relief: height ± its amplitude, features about that
wide across); there is no sea:

| # | Section | Seconds | Relief | Cover | Buildings (density) | What it shows |
|---|---------|---------|--------|-------|---------------------|---------------|
| 1 | oil edge | 40 | 28 ± 5, 600 | sand 0.55, paved 0.25 | oil, mines (1) | 2-2's oil edge. |
| 2 | oil fields | 60 | 26 ± 5, 620 | sand 0.5, paved 0.25 | oil (1) | Oil fields: pumpjacks and storage tanks. |
| 3 | company town | 50 | 30 ± 4, 600 | sand 0.4, paved 0.4 | worker homes, oil (1), wide streets | A company town on a street grid. |
| 4 | refineries | 55 | 30 ± 4, 600 | sand 0.35, paved 0.45 | refinery, oil (1) | Refineries among the last wells. |
| 5 | tank farms | 50 | 30 ± 4, 600 | sand 0.3, paved 0.5 | refinery (1), streets | Tank farms on a dense street grid. |
| 6 | industrial edge | 45 | 30 ± 4, 600 | sand 0.25, paved 0.55 | refinery, industrial (1), streets | Refineries giving way to the first factories, where 2-4 begins. |

**Acceptance criteria**
- Given 2-3, then its sections are these, in this order, with these seconds (unit test on the data).
- Given 2-2's last section and 2-3's first, then they have the same relief, cover and groups (unit test, WLD-2-10).
- Manual visual validation: `?level=2-3&t=70` the oil fields, `&t=180` the refineries, `&t=280` the first factories.

*Sources: P08-R03, D-110.*

#### LVL-2-3-05 — Flat, half paved · MUST

2-3 is flat ground (its reliefs within ± 5), more and more of it paved: about even between sand
(0.39) and pavement (0.40) over the level, sand ahead in its first half and pavement in its second
(WLD-2-07). The industrial group first comes in its last section, mixed with the refineries
(WLD-2-08).

**Acceptance criteria**
- Given 2-3's sections, then the sand share goes down from each section to the next and the paved share never goes down, and only the last lists the industrial group (unit test on the data).

*Sources: P08-R03, D-110.*

#### LVL-2-3-06 — Buildings and roads · MUST

2-3's habitations are the oil fields, a company town of worker homes, refineries and tank farms,
then the first factories (the groups of the table above, WLD-2-13), with a few lone buildings and
hamlets. It has World 1's roads (WLD-2-14). No tree grows.

**Acceptance criteria**
- Given 2-3 placed with its seed, then it has more buildings than 2-2 and fewer than 2-4, and its second half more than its first (unit test, WLD-2-11).

*Sources: P08-R03, P08-R07, D-110.*

### Waves

#### LVL-2-3-07 — Enemy kinds · MUST

2-3 mixes three tiers: tier 2 (the main one) is 60 % of its enemy ships, tier 1 20 % and tier 3 20 % (each within 5 points; a Wasp group counts as its 5 ships, and the filler is counted with the beats). It brings every kind of its tiers, each at least once: tier 2's Wasp, Strafer, Harrier, Sweeper and Hatchery; tier 1's Hornet, Scout, Rocketeer, Lancer and Carrier; tier 3's Phantom, Spinner, Mortar, Prism and Broodmother, and no other kind.

**Acceptance criteria**
- Given the 2-3 wave script, then it only uses the kinds of tiers 2, 1 and 3, and it uses each of them (unit test).
- Given 2-3 assembled, then each tier's share of its enemy ships is within 5 points of its target (unit test).

*Sources: P06-R07, ENM-50, D-283.*

#### LVL-2-3-08 — Wave plan · MUST

2-3's waves are composed from this plan (WLD-2-19; World 1's density and filler apply on top):

Beats from 4 s to 292 s, each wave followed by a breather of 2.7 s at the start down to 1.9 s at the end, groups growing by 80 % over the level. Each beat goes to the tier furthest below its share of the ships so far (the filler that follows a beat counted with it). A tier's beats first bring each of its five kinds once (shooter, laser, missile, carrier, then diver; one group each outside the main tier), then follow the role cycle (shooter, diver, laser, diver, missile, shooter, diver, carrier, laser, shooter, missile). A wave brings no more groups than its tier lacks, the main tier's never fewer than written.

No wave starts in the 10 s before each boss ([level-flow.md](../../gameplay/level-flow.md)): the beats are composed around these stretches, so none is dropped.

**Acceptance criteria**
- Given the 2-3 plan, then it composes beats that name its kinds and sides in order of time (unit test).

*Sources: P06-R07, D-067, ENM-50, D-283.*

#### LVL-2-3-09 — Filler · MUST

2-3's filler (WLD-1-21) brings the divers and shooters of the level's tiers, Wasp, Strafer, Hornet, Scout, Phantom and Spinner: after a wave of one of them, single groups of its kind in the lull, one every `max_gap`.

**Acceptance criteria**
- Given the 2-3 filler, then its kinds are the Wasp, the Strafer, the Hornet, the Scout, the Phantom and the Spinner only and its gap shrinks (unit test).

*Sources: D-051, ENM-50, D-283.*

### Difficulty

#### LVL-2-3-10 — Difficulty · MUST

2-3's enemies fire at `fire_rate_factor` of their rate and their bullets fly at
`bullet_speed_factor` of their speed: the kinds' own values. Per minute of scroll it has more
enemies and more enemy HP than 2-2 and fewer than 2-4, and a higher peak on screen than 2-2 (the
Hatcheries' Wasps raise it, WLD-2-20); its second half more HP than its first.

**Acceptance criteria**
- Given the 2-3 difficulty, then both factors are 1 (unit test).

*Sources: P08-R09, D-067.*

### Bosses

#### LVL-2-3-11 — Mini boss: Snow Owl · MUST

The [Snow Owl](../../bosses/mini/2-3-snow-owl.md) comes at the middle of 2-3's length
(9 000 units, 2:30), over the refineries. Destroying it saves the level's checkpoint
([level-flow.md](../../gameplay/level-flow.md)).

**Acceptance criteria**
- Given 2-3, then its mini boss is the Snow Owl, at half its length (unit test).

*Sources: GD-41, GD-42, P08-R10.*

#### LVL-2-3-12 — Final boss: Aurora Station · MUST

The [Aurora Station](../../bosses/final/2-3-aurora-station.md) comes at the end of 2-3's length
(18 000 units, 5:00), over the industrial edge; destroying it completes the level.

**Acceptance criteria**
- Given 2-3, then its final boss is the Aurora Station, at its length (unit test).

*Sources: GD-41, P08-R10.*

#### LVL-2-3-13 — Runout · MUST

`runout` seconds of the last section's ground (the industrial edge) are drawn past the level's end,
for the ground that gets ahead of the level during the fights.

**Acceptance criteria**
- Given 2-3, then its runout is 80 s (unit test on the data).

*Sources: D-054.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| seed | 2301 | `src/game/config/world_2/scenery.py` `LEVEL_2_3` |
| ground_speed | 60 units/s | `LEVEL_2_3.scrollSpeed` |
| duration | 300 s (18 000 units) | sum of the sections' `seconds` |
| look | `afternoon`, clouds 0.25 / 0.2, storm 0.15, no weather | `src/game/config/world_2/looks.py` `LEVEL_2_3_LOOK` |
| fog / glow | 1 100 → 2 800 / 0.4 | World 2's looks |
| streets | rows 45–90, columns 50–110, links 0.6 (the company town: `suburb_streets`, 2-2) | `STREETS` |
| max_gap | 3 s → 2 s | `src/game/config/world_2/waves.py` `WORLD_2_FILLERS["2-3"]` |
| bullet_speed_factor / fire_rate_factor | 1 / 1 | `src/game/config/world_2/difficulty.py` |
| written | beats composed from the plan and its tier mix (D-283); waves, groups, enemies and HP after fill and density: to be measured again | `src/game/config/wave_plans.py` `level_plan(2, 3)`, `tier_mix(2, 3)`; density 2 (D-249) |
| buildings | 24 278 (halves 10 287 / 13 991) | each level's seed, measured for this file |
| mini boss / final boss | `snow-owl` / `aurora-station` | `src/game/config/world_2/bosses.py` |
| runout | 80 s | same |

## Notes

- Before the 2026-10-27 rework (D-110), 2-3 was an overcast tundra with falling snow, frozen lakes
  and a pipeline on stilts; the Snow Owl and the Aurora Station were made for it.
- The pumpjacks of the old P08-R07 are tile models of the industrial group, shared with the mines,
  refineries and factories (WLD-2-13 and its note).
