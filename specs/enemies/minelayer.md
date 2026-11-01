# Minelayer

> **Area:** enemies · **Prefix:** `ENM-MINELAYER` · **Related:** [common.md](common.md), [strafer.md](strafer.md), [mortar.md](mortar.md), [World 3](../worlds/world-3/world.md), [World 4](../worlds/world-4/world.md)

The Minelayer is a veteran kind ([common.md](common.md)): a long, flat hull that crosses the top
half of the screen sideways, like a [Strafer](strafer.md), dropping slow mines that burst into rings
of bullets behind it. It has no moving parts.

## Requirements

### Look

#### ENM-MINELAYER-01 — Shape and size · MUST

The Minelayer is a long, flat hull 1.3 L long (about 0.6 L wide), with a rack of mines along its
belly and fins at its tail.

**Acceptance criteria**
- Given the Minelayer's model, then it is 1.3 L long (within the size tolerance of
  [common.md](common.md)) and long and flat from above.

*Sources: P05-R18, P16-R04.*

#### ENM-MINELAYER-02 — Cyber-Organic body · MUST

The Minelayer reads as a long, flat, segmented grub ([common.md](common.md)): four swollen flesh
segments (graphite shade). Metal is grafted on: the mine rack along its belly, with three flesh
egg-mines (membrane shade) hanging from it, one under each hatch, and swept metal fins either side
of its tail. It has more grafts than the basic kinds, so it reads as a veteran.

**Acceptance criteria**
- Given the Minelayer's model, then its body and eggs are flesh, and its rack and tail fins are
  metal.

*Sources: P05-R18, P16-R04.*

#### ENM-MINELAYER-03 — Neon lights · MUST

Three running lights line each flank, a light sits on its nose, a glowing vein runs along its back
and a neon ring circles each egg-mine, all in the Minelayer's neon colour. That colour is bright
yellow: its configured red-orange is on the yellow side of the two enemy hues
([common.md](common.md)).

**Acceptance criteria**
- Given the Minelayer's model, then its running lights, nose light, vein and egg rings are lit in
  bright yellow.

*Sources: P05-R18, P16-R04, D-231.*

#### ENM-MINELAYER-04 — Charge lights · SHOULD

A pair of glands on its back over each hatch are charge lights: they brighten as the next drop
comes and are at full brightness when a mine leaves ([common.md](common.md)).

**Acceptance criteria**
- Given a Minelayer over the playfield, then its charge rises from 0 to 1 over each drop interval.

*Sources: P05-R18, P16-R04.*

#### ENM-MINELAYER-05 — Reactors · MUST

Two plain reactors (no flesh sac) sit at its tail. It has no wings.

**Acceptance criteria**
- Given the Minelayer's model, then it has two reactors and three muzzles, one at each egg-mine
  hatch.

*Sources: P05-R18, P16-R04.*

#### ENM-MINELAYER-06 — Triangle budget · MUST

The Minelayer's model, reactors included, stays within the veteran triangle budget (700,
[common.md](common.md)). It is about 510 triangles before the edge trim.

**Acceptance criteria**
- Given the Minelayer's model, then its triangle count is at most the veteran budget.

*Sources: P16-R04, P16-R09.*

### Behaviour

#### ENM-MINELAYER-07 — Side pass · MUST

A Minelayer comes in alone from just beyond the left or right edge (60 px out): the wave's side and
height when the wave gives one, otherwise a random side at 74 % of the playfield height. Its pass is
never lower than 55 % of the height, whatever the wave says, so it stays in the top half. It crosses
the screen horizontally at 110 px/s, its nose the way it flies, and leaves by the other side, like a
[Strafer](strafer.md).

**Acceptance criteria**
- Given a Minelayer spawns from the left, then it comes in beyond the left edge and moves right at
  110 px/s at a constant height.
- Given a wave entry lower than 55 % of the height, then the Minelayer still crosses at 55 %.

*Sources: P05-R18.*

#### ENM-MINELAYER-08 — Mines · MUST

While its centre is over the playfield, every 0.8 s (the first 0.4 s after it is over it) the
Minelayer drops a mine straight down from one of the three hatches of its rack, the hatches taking
turns. A mine is a slow, big bullet (radius 6, 45 px/s) drifting down.

**Acceptance criteria**
- Given a Minelayer crosses, then it drops a mine every drop interval, from its hatches in turn,
  heading straight down.

*Sources: P05-R18.*

#### ENM-MINELAYER-09 — Mine burst · MUST

1.5 s after it was dropped, a mine bursts where it is into a ring of 6 bullets (140 px/s), evenly
all around; the mine is gone.

**Acceptance criteria**
- Given a mine, when 1.5 s have passed, then it is replaced by 6 bullets 60° apart, leaving from
  where it was.

*Sources: P05-R18.*

#### ENM-MINELAYER-10 — Health, points and hit circle · MUST

A Minelayer has 120 HP and scores 400 points. Its hit circle, at its centre, is 0.6 of the usual one
for its size ([common.md](common.md)): 11.3 px.

**Acceptance criteria**
- Given a Minelayer, then it takes 120 damage to destroy and scores 400 points.

*Sources: P05-R18.*

#### ENM-MINELAYER-11 — Veteran kind, from World 3 · MUST

The Minelayer is a veteran kind. No wave of World 1 or World 2 uses it. World 3 brings it in at
3-3, the third veteran kind, and the waves of every later level (3-3 to 4-5) use it.

**Acceptance criteria**
- Given the wave scripts, then no level before 3-3 names the Minelayer, and every level from 3-3
  to 4-5 does.

*Sources: P05-R24, D-090.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| size | 1.3 L | `src/game/config/enemies_veteran.py` `VETERAN_CONFIG.minelayer.size` |
| health / points | 120 / 400 | `VETERAN_CONFIG.minelayer.stats` |
| hit radius | 11.3 px | `radius(1.3) * 0.6` |
| speed | 110 px/s | sideways |
| heightFraction / lowestFraction | 0.74 / 0.55 | of the playfield height |
| spawn margin | 60 px | beyond the side edge; `src/game/config/enemies.py` `ENEMY_SPAWN_MARGIN` |
| dropInterval / firstDrop | 0.8 s / 0.4 s | times the level's fire rate factor ([common.md](common.md)) |
| mine | style `red`, 45 px/s, radius 6 | `VETERAN_CONFIG.minelayer.mine` |
| mine burst | after 1.5 s, 6 bullets, style `red`, 140 px/s, radius 4 | `mine.burst` |
| muzzles | `[0, -8, -3]`, `[0, 0, -3]`, `[0, 8, -3]` | the rack's hatches, used in turn |
| neon | `[1, 0.3, 0.05]`, drawn `[1, 1, 0.05]` | `VETERAN_NEON.minelayer` |
| triangle budget | 700 (veteran) | `src/game/config/enemy_look.py` `ENEMY_LOOK.budget.veteran` |

## Notes

**Appears in** (`src/game/config/world_3/waves.py`, `world_4/waves.py`): one Minelayer in a phrase
of its level's cycle in each of [3-3](../worlds/world-3/3-3-workers-quarter.md) (from the right),
[3-4](../worlds/world-3/3-4-suburbs.md) (left), [3-5](../worlds/world-3/3-5-garden-villages.md)
(right), [4-1](../worlds/world-4/4-1-garden-town.md) (left),
[4-2](../worlds/world-4/4-2-inner-town.md) (right), [4-3](../worlds/world-4/4-3-midtown.md) (left)
and [4-4](../worlds/world-4/4-4-business-district.md) (right), and two phrases in
[4-5](../worlds/world-4/4-5-downtown.md) (one from each side), each at 72 % to 74 % of the height;
the groups grow over each level. It is in no level's filler.

- The rack and its egg-mines hang under the body, as P05-R18 asks ("a mine rack along its
  belly"), so from above they barely show, against the rule that nothing is only seen from below
  ([common.md](common.md)); what the player sees of the drops is the glands on its back over each
  hatch (ENM-MINELAYER-04). The reviewer may want the rack moved or dropped.
- Known gaps: no unit test checks the model's size or its triangle count since the Python port
  (D-220).
