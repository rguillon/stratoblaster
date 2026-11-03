# Hive

> **Area:** enemies · **Prefix:** `ENM-HIVE` · **Related:** [common.md](common.md), [splitter.md](splitter.md), [carrier.md](carrier.md), [World 4](../worlds/world-4/world.md)

The Hive is tier 4's **carrier** (World 4) and an elite kind ([common.md](common.md)): a huge, rounded hive-ship that flies slowly
straight down the screen, launching [Splitters](splitter.md) from a turning ring on its back and firing
rings of bullets from its rim, until it gets too close to the player. It has no destroyable parts;
only its ring moves.

## Requirements

### Look

#### ENM-HIVE-01 — Shape and size · MUST

The Hive is a huge, rounded hive-ship 2 L across: a swollen dome, round seen from above, with a
launch ring turning on its back.

**Acceptance criteria**
- Given the Hive's model, then it is 2 L across (within the size tolerance of
  [common.md](common.md)), round from above, its ring on its back.

*Sources: P05-R23, P16-R04.*

#### ENM-HIVE-02 — Cyber-Organic body · MUST

The Hive is a living hive ([common.md](common.md)): its dome is swollen flesh (sinew shade), with
metal only where it is grafted on: three armour plates on its back between the cells and the ring,
twelve vents round its rim, the launch ring and the reactor nozzles. Its organs and grafts make it
read as an elite.

**Acceptance criteria**
- Given the Hive's model, then its dome is flesh, and its plates, vents and ring are metal.

*Sources: P05-R23, P16-R04.*

#### ENM-HIVE-03 — Brood cells and lights · MUST

Ten hexagonal brood cells glow on the shoulder of the dome, tilted with it, pulsing like veins, and
six lights stand on the launch ring, all in the Hive's neon colour. That colour is bright yellow: its
configured honey-amber is on the yellow side of the two enemy hues ([common.md](common.md)).

**Acceptance criteria**
- Given the Hive's model, then its ten cells and ring lights are lit in bright yellow.

*Sources: P05-R23, P16-R04, D-231.*

#### ENM-HIVE-04 — Launch ring and vents · MUST

The launch ring is a metal ring on its back with a launch hatch on it. It turns with the Hive's
spin, so the hatch goes round, and the hatch is where the Splitters come out. The twelve vents round its
rim point outwards; each is where one bullet of a ring leaves.

**Acceptance criteria**
- Given the Hive's model, then its ring is drawn apart from its body with one launch muzzle on it,
  and its body has twelve ring muzzles round its rim.
- Given the Hive's spin turns, then the ring and its hatch turn by as much.

*Sources: P05-R23, P16-R04.*

#### ENM-HIVE-05 — Charge lights · SHOULD

The hatch is a charge light that glows as the next Splitter comes and is at full brightness when it
comes out; the charge lights at the vents' mouths follow the same charge. Below the lowest height it
launches from, they are dark ([common.md](common.md)).

**Acceptance criteria**
- Given a Hive over the playfield, then its charge rises from 0 to 1 over each launch interval;
  given it is below 30 % of the height, then its charge is 0.

*Sources: P05-R23, P16-R04.*

#### ENM-HIVE-06 — Reactors · MUST

Two reactors sit at its tail, each set in a glowing organ: a flesh sac round the nozzle, a gland on
its back and a vein running forward from it.

**Acceptance criteria**
- Given the Hive's model, then its body has two reactors, each in a flesh sac.

*Sources: P16-R04.*

#### ENM-HIVE-07 — Triangle budget · MUST

The Hive's model (body and ring, reactors included) stays within the elite triangle budget (1200,
[common.md](common.md)). It is about 1190 triangles before the edge trim.

**Acceptance criteria**
- Given the Hive's model, then its triangle count is at most the elite budget.

*Sources: P16-R04, P16-R09.*

### Behaviour

#### ENM-HIVE-08 — Path · MUST

A Hive comes in alone from just above the top edge, at the wave's entry position or at a random X
between 30 % and 70 % of the width. It flies slowly straight down the screen at 28 px/s and leaves
at the bottom. Its launch ring turns at 45°/s all the time.

**Acceptance criteria**
- Given a Hive kind spawns, then one Hive comes in just above the top edge and moves down at
  28 px/s.

*Sources: P05-R23.*

#### ENM-HIVE-09 — Launching Splitters · MUST

While its centre is over the playfield and above 30 % of its height, every 6 s (the first 2 s after
it is over it) the Hive launches a [Splitter](splitter.md) from the hatch, where the ring has turned
it. The Splitter is built mid-screen at the hatch, `Splitter(x, y, stop_y)`, and flies down 55 px
from the hatch, pauses turning to the player, then dives at where the player was, and breaks into its
pods if destroyed (ENM-SPLITTER-05 to -08). The launch timer is the same in every level (the level's
fire rate factor does not speed it up).

**Acceptance criteria**
- Given a Hive is over the playfield, when its launch timer runs out, then a Splitter appears at its
  ring's hatch and goes into its dive sequence.
- Given a launched Splitter, then it pauses 55 px below where it came out.

*Sources: P05-R23, tier 4 redesign (launched Wasps).*

#### ENM-HIVE-10 — Rings of bullets · MUST

While its centre is over the playfield and above 30 % of its height, every 3 s (the first 1 s after
it is over it) the Hive fires a ring of 12 bullets (150 px/s) evenly all around, the first straight
down, each from the rim vent facing its way.

**Acceptance criteria**
- Given a Hive fires a ring, then 12 bullets leave its rim 30° apart.

*Sources: P05-R23.*

#### ENM-HIVE-11 — Quiet in the lower part · MUST

Below 30 % of the playfield height, too close to the player, the Hive stops launching and firing;
it flies on down and off the screen.

**Acceptance criteria**
- Given a Hive below 30 % of the height, then it launches no Splitter and fires no ring.

*Sources: P05-R23.*

#### ENM-HIVE-12 — Health, points and hit circle · MUST

A Hive has 420 HP and scores 900 points. Its hit circle, at its centre, is 0.8 of the usual one for
its size ([common.md](common.md)): 23.1 px. It has no destroyable part. The Splitters it launched are
enemies of their own: they stay, with their own health and points, when it is destroyed.

**Acceptance criteria**
- Given a Hive, then it takes 420 damage to destroy and scores 900 points; its Splitters still on the
  screen fly on.

*Sources: P05-R23.*

#### ENM-HIVE-13 — Built from engine specs · SHOULD

The Hive is an enemy with a turning ring (an enemy with moving parts, with no part), and the game
builds it from its config through `jointed_design`, as the other elite kinds, never from the raw
config record, so it spawns the same in CPython and in the browser.

**Acceptance criteria**
- Given a Hive is made, then it has no part and no joint, and it spawns without error.

*Sources: D-196.*

#### ENM-HIVE-14 — Elite kind, World 4 only · MUST

The Hive is an elite kind: only World 4's waves use it. 4-3 brings it in, the fourth elite kind, and
4-4 and 4-5 use it too.

**Acceptance criteria**
- Given the wave scripts, then no level before 4-3 names the Hive, and 4-3, 4-4 and 4-5 do.

*Sources: P05-R24, D-090.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| size | 2 L | `src/game/config/enemies_elite.py` `ELITE_CONFIG.hive.size` |
| health / points | 420 / 900 | `ELITE_CONFIG.hive.stats` |
| hit radius | 23.1 px | `radius(2) * 0.8` |
| xRange | 30 % – 70 % of the width | when the wave gives no entry |
| speed | 28 px/s | straight down |
| ringSpin | 45°/s | the launch ring |
| launchInterval / firstLaunch | 6 s / 2 s | not scaled by the level's fire rate |
| port | `[0, 14, 9]` | the hatch on the ring, turned with it |
| launchDrop | 55 px | a launched Splitter's pause, below the hatch |
| ringInterval / firstRing / ringCount | 3 s / 1 s / 12 | style `orange`, 150 px/s; times the level's fire rate factor |
| ringMuzzles | 12 vents, 32 px out, 1 px up | `around(12, 32, 1)` |
| lastFraction | 0.3 | no launch nor ring below it |
| neon | `[1, 0.62, 0.12]`, drawn `[1, 1, 0.12]` | `src/game/config/enemy_look_elite.py` `ELITE_NEON.hive` |
| triangle budget | 1200 (elite) | `src/game/config/enemy_look.py` `ENEMY_LOOK.budget.elite` |

## Notes

**Appears in** (`src/game/config/world_4/waves.py`): one Hive in a phrase of its level's cycle in
each of [4-3](../worlds/world-4/4-3-midtown.md), [4-4](../worlds/world-4/4-4-business-district.md)
and [4-5](../worlds/world-4/4-5-downtown.md); the groups grow over each level. It is in no level's
filler.

- The Splitter's model is one of the child models built with every level's own models
  (`CHILD_MODELS` in `src/game/view/enemies/enemy_bindings.py`), so no model is built in play when
  a Hive launches ([performance.md](../performance.md)).
- It launches like the [Carrier](carrier.md) launches Gnats, one Splitter at a time.
- Known gaps: no unit test checks the model's size or its triangle count since the Python port
  (D-220).
