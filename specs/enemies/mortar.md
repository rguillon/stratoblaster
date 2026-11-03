# Mortar

> **Area:** enemies · **Prefix:** `ENM-MORTAR` · **Related:** [common.md](common.md), [minelayer.md](minelayer.md), [World 3](../worlds/world-3/world.md), [World 4](../worlds/world-4/world.md)

The Mortar is a veteran kind ([common.md](common.md)) and **tier 3's missile launcher** (World 3's
enemies, `src/game/config/enemy_tiers.py`): a squat gunship that comes down slowly and lobs big,
slow homing missiles at the player. A missile can be shot down; if it is not, its fuse runs out and
it bursts into a ring of bullets. It has no moving parts.

## Requirements

### Look

#### ENM-MORTAR-01 — Shape and size · MUST

The Mortar is a squat gunship 1.2 L across, wider than it is long (about 0.8 L long). A short, wide
launcher tube stands on a raised mount in its middle, pointing forward, with a missile loaded in
it (its nose cone and a neon band show at the mouth), and a swollen sac bulges on each flank.

**Acceptance criteria**
- Given the Mortar's model, then it is 1.2 L across (within the size tolerance of
  [common.md](common.md)) and its launcher tube on its mount shows from above, with a missile in it.

*Sources: P05-R15, P16-R04.*

#### ENM-MORTAR-02 — Cyber-Organic body · MUST

The Mortar reads as a squat, armoured beetle ([common.md](common.md)). Its body is a ridged flesh
shell of three segments (sinew and slate shades), with a flesh sac swollen with shells on each
flank and two eyes at its front. Metal is grafted on: armour plates on its front shoulders, and the
whole mount, a squat drum with a cradle on it, then the barrel with a collar near its mouth. It has
more armour and grafts than the basic kinds, so it reads as a veteran.

**Acceptance criteria**
- Given the Mortar's model, then its shell and sacs are flesh, and its shoulder plates, mount and
  barrel are metal.

*Sources: P05-R15, P16-R04.*

#### ENM-MORTAR-03 — Neon lights · MUST

A neon ring runs round the mount's drum, a running light lies along each shell sac and its two eyes
glow, all in the Mortar's neon colour. That colour is yellow: its configured olive green is on the
yellow side of the two enemy hues ([common.md](common.md)), so it is drawn at the enemy yellow hue,
keeping its own brightness.

**Acceptance criteria**
- Given the Mortar's model, then its ring, sac lights and eyes are lit in yellow (hue 60°).

**Discrepancy:** keeping the configured brightness makes the Mortar's yellow darker
(`[0.7, 0.7, 0.12]`) than the other yellow kinds' (about `[1, 1, 0.1]`), where the reviewer asked
for bright shades of yellow or green (D-231).

*Sources: P05-R15, P16-R04, D-231.*

#### ENM-MORTAR-04 — Charge light · SHOULD

A charge ring at the tube's mouth brightens as the next missile charges and is at full brightness
when it leaves ([common.md](common.md)).

**Acceptance criteria**
- Given a Mortar over the playfield, then its charge rises from 0 to 1 over each fire interval.

*Sources: P05-R15, P16-R04.*

#### ENM-MORTAR-05 — Reactors · MUST

Two plain reactors (no flesh sac) sit at its back. It has no wings.

**Acceptance criteria**
- Given the Mortar's model, then it has two reactors and one gun muzzle, at the barrel's mouth.

*Sources: P16-R04.*

#### ENM-MORTAR-06 — Triangle budget · MUST

The Mortar's model, reactors included, stays within the veteran triangle budget (700,
[common.md](common.md)). It is about 500 triangles before the edge trim.

**Acceptance criteria**
- Given the Mortar's model, then its triangle count is at most the veteran budget.

*Sources: P16-R04, P16-R09.*

### Behaviour

#### ENM-MORTAR-07 — Entry and path · MUST

A Mortar comes in alone from just above the top edge, at the wave's entry position or at a random X
between 20 % and 80 % of the width. It flies straight down the screen at 40 px/s, nose down, and
leaves at the bottom.

**Acceptance criteria**
- Given a Mortar kind spawns, then one Mortar comes in just above the top edge and moves down at
  40 px/s.

*Sources: P05-R15.*

#### ENM-MORTAR-08 — Missiles · MUST

While its centre is over the playfield, every 3.5 s (the first 1 s after it is over it) the Mortar
launches one heavy, slow homing missile from its tube's mouth, first towards the player (radius 8,
90 px/s, turning at up to 55°/s towards the player for 2.2 s, then flying straight on). It is one
of the engine's enemy missiles ([rocketeer.md](rocketeer.md), ENM-18): the player's shots can hit it
(20 HP) and shoot it down, and it is drawn bigger than a Rocketeer's missile in proportion to its
radius.

**Acceptance criteria**
- Given a Mortar fires, then its missile leaves the tube's mouth, heading towards the player, with
  the speed, turn rate, radius and health above.
- Given a Mortar outside the playfield, then it fires nothing.

*Sources: P05-R15.*

#### ENM-MORTAR-09 — Missile burst · MUST

2.5 s after it was launched (its fuse), a missile still in flight bursts where it is into a ring of
10 bullets (130 px/s), evenly all around, the first along the missile's heading; the missile is
gone. A missile shot down before its fuse is out does not burst, and neither does one that has left
the playfield. The engine's missile spec carries the burst (`EnemyMissileSpec.burst`), as a
bullet's does (`EnemyBulletSpec.burst`); its bullets are as fast as the level makes bullets
(ENM-22).

**Acceptance criteria**
- Given a Mortar missile, when 2.5 s have passed, then it is replaced by 10 bullets 36° apart,
  leaving from where it was.
- Given a Mortar missile shot down at 1 s, then it leaves no bullets.

*Sources: P05-R15.*

#### ENM-MORTAR-10 — Health, points and hit circle · MUST

A Mortar has 120 HP and scores 350 points. Its hit circle, at its centre, is 0.8 of the usual one
for its size ([common.md](common.md)): 13.9 px.

**Acceptance criteria**
- Given a Mortar, then it takes 120 damage to destroy and scores 350 points.

*Sources: P05-R15.*

#### ENM-MORTAR-11 — Veteran kind, from World 3 · MUST

The Mortar is a veteran kind. No wave of World 1 or World 2 uses it. World 3 brings it in at 3-2,
the second veteran kind after the Wasp, and the waves of every later level (3-2 to 4-5) use it.

**Acceptance criteria**
- Given the wave scripts, then no level before 3-2 names the Mortar, and every level from 3-2 to
  4-5 does.

*Sources: P05-R24, D-090.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| size | 1.2 L | `src/game/config/enemies_veteran.py` `VETERAN_CONFIG.mortar.size` |
| health / points | 120 / 350 | `VETERAN_CONFIG.mortar.stats` |
| hit radius | 13.9 px | `radius(1.2) * 0.8` |
| xRange | 20 % – 80 % of the width | when the wave gives no entry |
| speed | 40 px/s | straight down |
| fireInterval / firstShot | 3.5 s / 1 s | times the level's fire rate factor ([common.md](common.md)) |
| missile | style `mortar`, 90 px/s, radius 8, 20 HP, turn 55°/s for 2.2 s | `VETERAN_CONFIG.mortar.missile` |
| missile burst | after 2.5 s, 10 bullets, style `green`, 130 px/s, radius 4 | `missile.burst` |
| muzzles | `[0, -12.5, 7]` | the tube's mouth, on its raised mount |
| missile model scale | radius / 5 | `ENEMY_LOOK.missile.baseRadius` |
| neon | `[0.55, 0.7, 0.12]`, drawn `[0.7, 0.7, 0.12]` | `VETERAN_NEON.mortar` |
| triangle budget | 700 (veteran) | `src/game/config/enemy_look.py` `ENEMY_LOOK.budget.veteran` |

## Notes

**Appears in** (`src/game/config/world_3/waves.py`, `world_4/waves.py`): one phrase of its level's
cycle in each of [3-2](../worlds/world-3/3-2-docklands.md),
[3-3](../worlds/world-3/3-3-workers-quarter.md), [3-4](../worlds/world-3/3-4-suburbs.md),
[3-5](../worlds/world-3/3-5-garden-villages.md), [4-1](../worlds/world-4/4-1-garden-town.md),
[4-2](../worlds/world-4/4-2-inner-town.md), [4-3](../worlds/world-4/4-3-midtown.md) and
[4-4](../worlds/world-4/4-4-business-district.md) (1 Mortar), and in
[4-5](../worlds/world-4/4-5-downtown.md) (2, 2 s apart); the groups grow over each level. It is in
no level's filler.

- The bosses' "mortar" hidden weapons (D-221) are a boss weapon kind, not this enemy.
- The Mortar used to lob shells that burst into a ring after 1.2 s (140 HP, 400 points); tier 3
  made it the missile launcher. The burst bullets' style name (`green`) is kept from phase 5; every enemy bullet style is now drawn
  orange to amber ([graphics/shots.md](../graphics/shots.md)).
- Known gaps: no unit test checks the model's size or its triangle count since the Python port
  (D-220).
