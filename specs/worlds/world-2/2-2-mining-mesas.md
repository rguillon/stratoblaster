# 2-2 Mining mesas

> **Area:** Worlds · **Prefix:** `LVL-2-2` · **Related:** [World 2](world.md), [2-1 Great erg](2-1-great-erg.md), [2-3 Oil fields](2-3-oil-fields.md), [Fjord Lynx](../../bosses/mini/2-2-fjord-lynx.md), [Harbour Kraken](../../bosses/final/2-2-harbour-kraken.md), [level flow](../../gameplay/level-flow.md), [terrain](../../graphics/terrain.md), [sky and light](../../graphics/sky-and-light.md)

The second level of World 2: a high, hard midday sun over the mining mesas, from the first mines 2-1
ended on, over mesas and along a canyon, through a mining town and open pits, to the first oil wells
among the last mines. Tier 2 brings 60 % of the enemies, tier 1 30 % and tier 3 its first 10 %. The Fjord Lynx waits at the middle
and the Harbour Kraken at the end.

## Requirements

### Identity

#### LVL-2-2-01 — Identity · MUST

Level `2-2` is the second level of World 2. It is named "Mining mesas"; its scenery is `world-2-2`,
generated from the seed `seed`.

**Acceptance criteria**
- Given the game's levels, then the seventh is `2-2`, named "2-2 Mining mesas", with the scenery `world-2-2` and its seed (unit test).

*Sources: P08-R03, D-110.*

#### LVL-2-2-02 — Duration and ground speed · MUST

2-2 scrolls at `ground_speed` for `duration`: its sections' seconds add up to 300, so its length is
19 500 units. Its sections blend over 900 units (WLD-2-08).

**Acceptance criteria**
- Given 2-2, then its length ÷ its ground speed is 300 s (unit test, e2e).

*Sources: P08-R02, GD-01, D-110.*

#### LVL-2-2-03 — Midday · MUST

2-2 is at midday, the whole level long: the engine's `midday` preset (a high, hard sun), two layers
of few clouds (`clouds`), no smog, the fog of World 2's looks (`fog`), the ground lights off, no
weather.

**Acceptance criteria**
- Given the 2-2 look, then it is `midday` with cloud cover 0.2 / 0.15, no storm, no weather and no change within the level (unit test on the data).

*Sources: P08-R04, P08-R06, D-110.*

### Scenery

#### LVL-2-2-04 — Sections · MUST

2-2's ground is these sections, in this order (relief: height ± its amplitude, features about that
wide across); there is no sea:

| # | Section | Seconds | Relief | Cover | Buildings (density) | What it shows |
|---|---------|---------|--------|-------|---------------------|---------------|
| 1 | prospect mines | 40 | 30 ± 10, 520 | sand 0.8, paved 0.05 | outposts, mines (1) | 2-1's first mines. |
| 2 | mesa mines | 50 | 30 ± 150, 560, cut at 100 | sand 0.75, paved 0.05 | mines, outposts (0.9) | Mines on and between flat-topped mesas. |
| 3 | canyon | 35 | 95 ± 22, 380, a canyon cut in it | sand 0.7, paved 0.05 | mines (0.8) | Mines along a winding canyon through a plateau. |
| 4 | mining town | 55 | 30 ± 4, 600 | sand 0.6, paved 0.2 | worker homes, mines (1), wide streets | A mining town on a street grid. |
| 5 | open pits | 45 | 26 ± 12, 480 | sand 0.65, paved 0.15 | mines, outposts (1) | Open pits and their outposts, the sand trodden around them. |
| 6 | first wells | 40 | 28 ± 6, 560 | sand 0.6, paved 0.2 | mines, oil (1) | The first oil wells among the mines. |
| 7 | oil edge | 35 | 28 ± 5, 600 | sand 0.55, paved 0.25 | oil, mines (1) | Oil wells taking over, where 2-3 begins. |

**Acceptance criteria**
- Given 2-2, then its sections are these, in this order, with these seconds (unit test on the data).
- Given 2-1's last section and 2-2's first, then they have the same relief, cover and groups (unit test, WLD-2-10).
- Manual visual validation: `?level=2-2&t=60` the mesas, `&t=150` the mining town, `&t=280` the oil edge.

*Sources: P08-R03, D-110.*

#### LVL-2-2-05 — Mesas and a dry canyon · MUST

The mesas are a high relief cut flat at a top height, red-brown rock on their cliffs (WLD-2-12). The
canyon is a channel (`canyon`) winding along the level through a high plateau; 2-2 has no sea level,
so the canyon holds no water and no shore comes with it (WLD-2-06).

**Acceptance criteria**
- Given 2-2, then it has no sea and no shore section; its canyon section has a channel (unit test on the data).

*Sources: P08-R03, D-110.*

#### LVL-2-2-06 — Buildings and roads · MUST

2-2's habitations are mines and their outposts, a mining town of worker homes, open pits, then the
first oil wells (the groups of the table above, WLD-2-13), with a few lone buildings and hamlets.
It has World 1's roads (WLD-2-14). No tree grows.

**Acceptance criteria**
- Given 2-2 placed with its seed, then it has more buildings than 2-1 and fewer than 2-3, and its second half more than its first (unit test, WLD-2-11).

*Sources: P08-R03, P08-R07, D-110.*

### Waves

#### LVL-2-2-07 — Enemy kinds · MUST

2-2 mixes three tiers: tier 2 (the main one) is 60 % of its enemy ships, tier 1 30 % and tier 3 10 % (each within 5 points; a Wasp group counts as its 5 ships, and the filler is counted with the beats). It brings every kind of its tiers, each at least once: tier 2's Wasp, Strafer, Harrier, Sweeper and Hatchery; tier 1's Hornet, Scout, Rocketeer, Lancer and Carrier; tier 3's Phantom, Spinner, Mortar, Prism and Broodmother, and no other kind.

**Acceptance criteria**
- Given the 2-2 wave script, then it only uses the kinds of tiers 2, 1 and 3, and it uses each of them (unit test).
- Given 2-2 assembled, then each tier's share of its enemy ships is within 5 points of its target (unit test).

*Sources: P06-R07, ENM-50, D-283.*

#### LVL-2-2-08 — Wave plan · MUST

2-2's waves are composed from this plan (WLD-2-19; World 1's density and filler apply on top):

Beats from 4 s to 292 s, each wave followed by a breather of 2.9 s at the start down to 2 s at the end, groups growing by 75 % over the level. Each beat goes to the tier furthest below its share of the ships so far (the filler that follows a beat counted with it). A tier's beats first bring each of its five kinds once (shooter, laser, missile, carrier, then diver; one group each outside the main tier), then follow the role cycle (shooter, diver, laser, diver, missile, shooter, diver, carrier, laser, shooter, missile). A wave brings no more groups than its tier lacks, the main tier's never fewer than written.

No wave starts in the 10 s before each boss ([level-flow.md](../../gameplay/level-flow.md)): the beats are composed around these stretches, so none is dropped.

**Acceptance criteria**
- Given the 2-2 plan, then it composes beats that name its kinds and sides in order of time (unit test).

*Sources: P06-R07, D-067, ENM-50, D-283.*

#### LVL-2-2-09 — Filler · MUST

2-2's filler (WLD-1-21) brings the divers and shooters of the level's tiers, Wasp, Strafer, Hornet, Scout, Phantom and Spinner: after a wave of one of them, single groups of its kind in the lull, one every `max_gap`.

**Acceptance criteria**
- Given the 2-2 filler, then its kinds are the Wasp, the Strafer, the Hornet, the Scout, the Phantom and the Spinner only and its gap shrinks (unit test).

*Sources: D-051, ENM-50, D-283.*

### Difficulty

#### LVL-2-2-10 — Difficulty · MUST

2-2's enemies fire at `fire_rate_factor` of their rate and their bullets fly at
`bullet_speed_factor` of their speed. Per minute of scroll it has more enemies and more enemy HP than
2-1 and fewer than 2-3, and a higher peak on screen than 2-1 (WLD-2-20); its second half more HP
than its first.

**Acceptance criteria**
- Given the 2-2 difficulty, then both factors are 0.95 (unit test).

*Sources: P08-R09, D-067.*

### Bosses

#### LVL-2-2-11 — Mini boss: Fjord Lynx · MUST

The [Fjord Lynx](../../bosses/mini/2-2-fjord-lynx.md) comes at the middle of 2-2's length
(9 750 units, 2:30), over the mining town. Destroying it saves the level's checkpoint
([level-flow.md](../../gameplay/level-flow.md)).

**Acceptance criteria**
- Given 2-2, then its mini boss is the Fjord Lynx, at half its length (unit test).

*Sources: GD-41, GD-42, P08-R10.*

#### LVL-2-2-12 — Final boss: Harbour Kraken · MUST

The [Harbour Kraken](../../bosses/final/2-2-harbour-kraken.md) comes at the end of 2-2's length
(19 500 units, 5:00), over the oil edge, the ground stopped under it (World 2's fight that stops the
ground, WLD-2-24); destroying it completes the level.

**Acceptance criteria**
- Given 2-2, then its final boss is the Harbour Kraken, at its length (unit test).

*Sources: GD-41, P08-R10, D-068.*

#### LVL-2-2-13 — Runout · MUST

`runout` seconds of the last section's ground (the oil edge) are drawn past the level's end, the
shortest of World 2: its final fight stops the ground.

**Acceptance criteria**
- Given 2-2, then its runout is 50 s (unit test on the data).

*Sources: D-054.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| seed | 2201 | `src/game/config/world_2/scenery.py` `LEVEL_2_2` |
| ground_speed | 65 units/s | `LEVEL_2_2.scrollSpeed` |
| duration | 300 s (19 500 units) | sum of the sections' `seconds` |
| look | `midday`, clouds 0.2 / 0.15, no storm, no weather | `src/game/config/world_2/looks.py` `LEVEL_2_2_LOOK` |
| fog / glow | 1 100 → 2 800 / 0.4 | World 2's looks |
| mesas | base 30, amplitude 150, 1/560, 5 octaves, cut at 100 | `MINING_MESAS` |
| canyon | channel x 0 ± 140 every 1 900 units, half width 40, walls 110, floor 10 | same |
| suburb_streets | rows 60–110, columns 70–130, links 0.55 | `SUBURB_STREETS` (also 2-3's company town and 2-4's suburbs) |
| max_gap | 3.2 s → 2.1 s | `src/game/config/world_2/waves.py` `WORLD_2_FILLERS["2-2"]` |
| bullet_speed_factor / fire_rate_factor | 0.95 / 0.95 | `src/game/config/world_2/difficulty.py` |
| written | beats composed from the plan and its tier mix (D-283); waves, groups, enemies and HP after fill and density: to be measured again | `src/game/config/wave_plans.py` `level_plan(2, 2)`, `tier_mix(2, 2)`; density 2 (D-249) |
| buildings | 12 834 (halves 5 005 / 7 829) | each level's seed, measured for this file |
| mini boss / final boss | `fjord-lynx` / `harbour-kraken` | `src/game/config/world_2/bosses.py` |
| runout | 50 s | same |

## Notes

- Before the 2026-10-27 rework (D-110), 2-2 was morning fjords with a harbour at its start; the
  Harbour Kraken's "the ground stops over the harbour" was already over 2-2's inland end (D-068), as
  2-2 has to end where 2-3 begins. Its bosses keep their fjord and harbour names over the mines.
- Since the grid of tiles, the mines and the oil wells draw from the same industrial models
  (WLD-2-13 and its note).
