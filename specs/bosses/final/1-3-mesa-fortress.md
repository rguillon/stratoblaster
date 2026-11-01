# Mesa Fortress

> **Area:** bosses · **Prefix:** `FB-MESA-FORTRESS` · **Related:** [common](../common.md),
> [1-3 Green Country](../../worlds/world-1/1-3-green-country.md), [Dust Devil](../mini/1-3-dust-devil.md),
> [World 1](../../worlds/world-1/world.md)

The Mesa Fortress is the final boss of 1-3: a colossal canyon tortoise, 5 L across (first designed
as a flying fortress), its high stepped shell shaped like the mesas. A laser lance in each forelimb
and two spore silos on its back shield its core, a fan cannon on its brow. The ground stops while it
is fought. At its second transformation its shell splits open. Shared rules are in
[common](../common.md).

## Requirements

### Look

#### FB-MESA-FORTRESS-01 — Silhouette and size · MUST

Seen from above, the Mesa Fortress is a wide tortoise, 5 L across: a skirt of hide under a high,
stepped shell, its head at its front (down the screen) with a fan cannon on its brow, a forelimb on
each side reaching forward to a laser lance, and two silos on the back of its shell.

**Acceptance criteria**
- Manual validation in the boss viewer: a tortoise with a stepped shell, a lance in each forelimb.

*Sources: P07-R05, P16-R06.*

#### FB-MESA-FORTRESS-02 — Body · MUST

Its body is a wide skirt of hide under a high stepped shell (slate and sinew shades) with ribs,
veins and grafted armour plates on it, its keep's roof along the ridge of the shell, its head at its
front. Each forelimb is a scaly limb out to its lance's cradle, a bone claw at its front.

**Acceptance criteria**
- Manual validation: a living tortoise plated with grafted armour.

*Sources: P07-R05, P16-R06.*

#### FB-MESA-FORTRESS-03 — Its parts · MUST

- **Laser lances** (one in each forelimb's cradle): a swollen gland, a long grafted barrel out of it
  ringed with neon, sinews binding it, its lens glowing as it charges.
- **Missile silos** (two, on the rear of its shell): a swollen spore pod, a grafted collar round its
  mouth, four missile tips standing in it like seeds, a vein ring at its foot.
- **Fan cannon** (the core's gun, on its brow): a grafted housing and five barrels fanned out
  forward, turning about the hub of its barrels.

**Acceptance criteria**
- Given its model, then it draws its lances, its silos and the fan cannon's turret (unit test).

*Sources: P07-R05, P16-R06, D-060.*

#### FB-MESA-FORTRESS-04 — Lights · MUST

Veins run along its shell and round its silos' feet; neon rings its lances. Its neon colour, set
red, shows bright yellow ([common](../common.md), BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright yellow.

*Sources: P07-R05, P16-R06, D-231.*

#### FB-MESA-FORTRESS-05 — What it sheds and moves · MUST

The armour at the front of its wings is shed at its first transformation (`wing` frame beneath).
At its second, the two halves of its keep's roof are the pieces that move apart (a `shell` lattice
shows between them) and its flank armour is shed (`wing` frame beneath).

**Acceptance criteria**
- Given its design, then its first transformation sheds its wing fronts, its second moves its roof
  halves and sheds its flanks (unit test).

*Sources: D-224, D-230.*

### Behaviour

#### FB-MESA-FORTRESS-06 — Coming in and moving · MUST

It comes in from the top ([common](../common.md), BOSS-08) to `stopFraction` of the playfield's
height, then sways and bobs. While it is fought the ground stops (×0), over the canyon, and starts
again once it is destroyed.

**Acceptance criteria**
- Given the fight, then the ground eases to a stop and stays stopped until it is destroyed.

*Sources: P07-R03, P07-R05.*

#### FB-MESA-FORTRESS-07 — Parts and core · MUST

It has four parts as it comes in, all shielding its core: `lance-left`, `lance-right`, `silo-left`
and `silo-right`. Each lance fires a laser straight down, the two in turn, locked once it fires;
each silo fires one homing missile, in turn. The fan cannon on its turret fires the core's volleys
and turns the way it fires.

**Acceptance criteria**
- Given its design, then its four parts shield the core.

*Sources: P07-R01, P07-R05, D-060.*

#### FB-MESA-FORTRESS-08 — Stage patterns · MUST

The lances' lasers and the silos' missiles go on in every stage while they stand. The core fires:
- stage 0: a fan of 3 red;
- stage 1: a fan of 5;
- stage 2: a fan of 5 and one orange bullet at the player;
- stage 3: a fan of 7;
- stage 4 (all four parts gone): a ring of 14 orange turning at each volley, and a fan of 5 red.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys and the parts left fire theirs
  (unit test on its design).

*Sources: P07-R04, D-055.*

#### FB-MESA-FORTRESS-09 — Angry · MUST

Its angry pattern is a **curtain** at heat 2.5 (red fans sweeping across and back, an orange ring
under them).

**Acceptance criteria**
- Given its design, then its rage is that pattern at that heat, fired from its core.

*Sources: D-063.*

#### FB-MESA-FORTRESS-10 — First transformation: batteries · MUST

Once both lances are destroyed, the armour at the front of its wings bursts off, baring a dark
metal frame, and two **batteries** unfold there, either side of its head. They shield the core and
fire red fans of 7 straight down, in turn.

**Acceptance criteria**
- Given both lances destroyed, then it transforms and its two batteries are revealed.

*Sources: D-224, D-229, D-230.*

#### FB-MESA-FORTRESS-11 — Second transformation: its keep splits open · MUST

Once both silos are destroyed, its keep splits along its ridge: the two halves of its roof slide
16 px apart over a dark metal lattice, and a heavy **cannon** rises between them on its centre line,
firing aimed spreads of 3 big orange shells. Its flank armour bursts off for a pair of **sweepers**
at its rear corners, firing lasers that sweep after the player.

**Acceptance criteria**
- Given both silos destroyed, then it transforms a second time, its roof halves end 16 px apart and
  its cannon and two sweepers are revealed.
- Manual validation: the roof visibly splits and slides apart.

*Sources: D-224, D-229, D-230.*

#### FB-MESA-FORTRESS-12 — Laser colour · MUST

Its lasers (the lances' and the sweepers') are drawn in its neon folded into the enemy shots'
family: an amber beam round a white-hot core ([common](../common.md), BOSS-32).

**Acceptance criteria**
- Given its lasers, then their colour is its neon folded into the enemy shots' family (unit
  test).

*Sources: D-072, D-231.*

#### FB-MESA-FORTRESS-13 — Death, drops and points · MUST

Its parts drop a weapon bonus 60 % of the time, its hidden weapons 30 %, and its core always drops
one ([common](../common.md), BOSS-57). Destroying it ends 1-3
([level flow](../../gameplay/level-flow.md)). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: P07-R07.*

## Tunable values

All in `src/game/config/bosses/final_bosses.py` (`_MESA_FORTRESS`, `MESA_FORTRESS`) unless named.

| Name | Value | Notes |
|------|-------|-------|
| size | 5 L (radius 85 px) | |
| core | health 3 000, radius 22, drop 1 | fan cannon pivot (0, -30), 5 barrels |
| `lance-left`, `lance-right` | (∓58, -12), radius 15, health 1 050, shield, drop 0.6 | |
| `silo-left`, `silo-right` | (∓28, 32), radius 13, health 1 500, shield, drop 0.6 | 4 cells each |
| full health | 15 000 (8 100 without the hidden weapons) | BOSS-54 |
| points | 10 000; 1 000 a part | |
| ground speed | ×0 | |
| stop height | 0.74 | |
| sway / bob | 35 px over 10 s / 6 px over 5 s | |
| lance lasers | 1.4 s every 6 s (first 2 s / 5 s) | |
| silo missiles | 1 every 5 s (first 3.5 s / 6 s) | |
| core stage 0 | fan of 3, 16° apart, red 190 px/s, every 3 s | |
| core stage 1 | fan of 5, 14° apart, every 2.6 s | |
| core stage 2 | fan of 5 every 2.6 s; 1 aimed orange bullet, 175 px/s, every 2.2 s | |
| core stage 3 | fan of 7, 12° apart, every 2.2 s | |
| core stage 4 | ring of 14 turning 12°, orange, every 1.5 s; fan of 5 red every 2.6 s | |
| angry | curtain, heat 2.5 (40 bullets a second, 140 px/s), red and orange | |
| transformation 1 | `lance-left` and `lance-right` destroyed | `transformParts` |
| wing-front region | x 16..88, y -51..-3.5, above 4.3 px, `wing`, mirrored | |
| batteries | (∓44, -26), radius 10, health 1 200, pod 14 px, red; first 1.2 s / 2.2 s | |
| transformation 2 | `silo-left` and `silo-right` destroyed | |
| roof halves | x 0..23, y -6..46, above 16 px, mirrored; slide 16 px apart; `shell` frame | `moving_region`, `slide` |
| flank region | x 34..88, y -3.5..50, above 2.2 px, `wing`, mirrored | |
| `cannon` | (0, 14), radius 14, health 1 500, pod 22 px, orange; first 1.4 s | rises between the roof halves |
| sweepers | (∓60, 22), radius 8, health 1 500, pod 14 px; first 2.4 s / 6.4 s | |
| neon | red (1, 0.1, 0.12), shown yellow | `BOSS_LOOK.neon` |

## Notes

- Its silos went from 890 to 1 500 health and its core from 2 420 to 3 000 when shots started going
  through a shielded core (D-062): the silos behind the core became easier to reach.
