# Mesa Fortress

> **Area:** bosses · **Prefix:** `FB-MESA-FORTRESS` · **Related:** [common](../common.md),
> [1-3 Green Country](../../worlds/world-1/1-3-green-country.md), [Dust Devil](../mini/1-3-dust-devil.md),
> [World 1](../../worlds/world-1/world.md)

The Mesa Fortress is the final boss of 1-3: a colossal canyon tortoise, 5 L across (first designed
as a flying fortress), its high stepped shell shaped like the mesas. A laser lance in each forelimb
and two spore silos on its back shield its core, a fan turret on its brow and a rotor behind its
keep. The ground stops while it
is fought. At its second transformation its shell splits open. Shared rules are in
[common](../common.md).

## Requirements

### Look

#### FB-MESA-FORTRESS-01 — Silhouette and size · MUST

Seen from above, the Mesa Fortress is a wide tortoise, 5 L across: a skirt of hide under a high,
stepped shell, its head at its front (down the screen) with a fan turret on its brow, a forelimb on
each side reaching forward to a laser lance, and two silos on the back of its shell.

**Acceptance criteria**
- Manual validation in the boss viewer: a tortoise with a stepped shell, a lance in each forelimb.

*Sources: P07-R05, P16-R06.*

#### FB-MESA-FORTRESS-02 — Body · MUST

Its body is a wide skirt of hide under a high stepped shell (slate and sinew shades) with ribs,
veins and grafted armour plates on it, its keep along the ridge of the shell standing on the lower
shell's flat top, its head at its front. Each forelimb is a scaly limb out to its lance's cradle, a bone claw at its front.

**Acceptance criteria**
- Manual validation: a living tortoise plated with grafted armour.

*Sources: P07-R05, P16-R06.*

#### FB-MESA-FORTRESS-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts, the shared models of [common](../common.md) (BOSS-58):
- **Laser lances** (one in each forelimb's cradle): a swollen gland, a long fixed laser mount on the
  cradle before it pointing down the screen, sinews binding it.
- **Missile silos** (two, on the rear of its shell): a swollen spore pod, a grafted collar round its
  mouth, a missile block of four ports standing in it like seeds, a vein ring at its foot.
- **Fan turret** (the core's, on its brow): a gun turret with seven barrels side by side (its fans
  and aimed shots).
- **Back rotor** (the core's, on its back behind the keep): a rotor with fourteen barrels (its
  rings).

**Acceptance criteria**
- Given its model, then it draws its lances, its silos and every gun mount (unit test).

*Sources: P07-R05, P16-R06, D-060, D-280.*

#### FB-MESA-FORTRESS-04 — Lights · MUST

Veins run along its shell and round its silos' feet. Its neon colour, set
red, shows bright yellow ([common](../common.md), BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright yellow.

*Sources: P07-R05, P16-R06, D-231.*

#### FB-MESA-FORTRESS-05 — What it sheds and moves · MUST

Its skirt is drawn in two layers: a lower slab of hide the whole skirt wide (-6 to 5 px) and an
upper one (5 to 7 px) whose flanks are its armour, drawn as pieces of their own out to the skirt's
rim ([common](../common.md), BOSS-42, BOSS-45); the upper layer runs on along the middle. Its keep,
the upper shell, stands on the flat top of the lower shell (17 px) and is drawn as two halves cut
along its ridge.

- The **front flanks** (`wings`, mirrored), either side of the head, are shed at its first
  transformation, the rim's neon along each on them. Shed, they burst into plates cracked from their
  outline and leave `wing` frames on the lower layer, out of which the batteries rise.
- The **roof halves** (`roof`, a mirrored pair), the keep from 17 px up to its ridge at 30 px, each
  with a vein along the ridge, a gland on its flank and two grafted plates sunk in it, are the
  pieces that move apart at its second transformation, leaving a `shell` lattice floor on the lower
  shell's top between them, out of which the cannon rises.
- The **rear flanks** (`flanks`, mirrored), along the skirt behind the front flanks and over the
  forelimbs, are shed at its second: they carry each forelimb's scaly sinew (5 to 13 px) and its
  grafted plate, lying on the limb. Shed, they leave `wing` frames on the skirt and the limbs, out of
  which the sweepers rise.

**Acceptance criteria**
- Given its design, then its first transformation sheds its wing fronts, its second moves its roof
  halves and sheds its flanks (unit test).
- Given its model, then it draws each region's piece, and it holds together at rest and after each
  transformation (unit tests).

*Sources: D-224, D-230, D-254.*

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
each silo fires one homing missile from its ports, in turn. The core's guns (the fan turret and the
back rotor) fire the core's volleys, and are the last the player destroys; the turret turns the way
it fires.

**Acceptance criteria**
- Given its design, then its four parts shield the core.

*Sources: P07-R01, P07-R05, D-060.*

#### FB-MESA-FORTRESS-08 — Stage patterns · MUST

The lances' lasers and the silos' missiles go on in every stage while they stand. The core fires:
- stage 0: a fan of 3 red straight down, swept from the fan turret one bullet at a time as it turns
  across the fan (BOSS-58);
- stage 1: a fan of 5, swept the same way;
- stage 2: a fan of 5 and one orange bullet at the player, both from the fan turret;
- stage 3: a fan of 7, swept the same way;
- stage 4 (all four parts gone): a ring of 14 orange from the back rotor, one bullet a barrel,
  turning at each volley, and a fan of 5 red from the fan turret.

Its fans are all 12° apart.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys and the parts left fire theirs
  (unit test on its design).

*Sources: P07-R04, D-055.*

#### FB-MESA-FORTRESS-09 — Angry · MUST

It is angry after each of its transformations, when the weapons that one revealed
fire all out: the two batteries after the first, the heavy cannon and two sweepers after the second.
For `boss_rage_seconds` it fires only those, `boss_rage_rate` times as often, instead of its
stage's pattern ([common](../common.md), BOSS-27). A lost part no longer angers it, and it
has no angry pattern of its own.

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only the weapons it revealed
  (unit: `test_boss_build.py` angry_pattern).
- Given a part is destroyed without a transformation, then it is not angry (unit test).

*Sources: D-063, D-256.*

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
| core | health 3 000, radius 22, drop 1 | `coreHealth`, `coreRadius`, `coreDrop` |
| `lance-left`, `lance-right` | (∓58, -12), radius 15, health 1 050, shield, drop 0.6 | |
| `silo-left`, `silo-right` | (∓28, 32), radius 13, health 1 500, shield, drop 0.6 | |
| lance lasers | (∓58, -16), 5 px high, fixed; barrel 30 px long, bore 3.5; base radius 7 | `MESA_LANCE`, `mounts` |
| silos' missile blocks | (∓28, 32), 12.4 px high; 4 ports each | `mounts` |
| fan turret (core) | (0, -25), 14 px high; 7 barrels 2.9 px apart, bore 1.1, 9 px long; dome radius 10.3 | `mounts` `brow` |
| back rotor (core) | (0, 48), 13.5 px high; 14 barrels, bore 0.7, 3.2 px long; hub radius 5 | `mounts` `back-rotor` |
| full health | 15 000 (8 100 without the hidden weapons) | BOSS-54 |
| points | 10 000; 1 000 a part | |
| ground speed | ×0 | |
| stop height | 0.74 | |
| sway / bob | 35 px over 10 s / 6 px over 5 s | |
| lance lasers | 1.4 s every 6 s (first 2 s / 5 s) | |
| silo missiles | 1 every 5 s (first 3.5 s / 6 s) | |
| core stage 0 | fan of 3, 12° apart, red 190 px/s, every 3 s | fan turret, a sweep |
| core stage 1 | fan of 5, 12° apart, every 2.6 s | fan turret, a sweep |
| core stage 2 | fan of 5, 12° apart, every 2.6 s; 1 aimed orange bullet, 175 px/s, every 2.2 s | fan turret |
| core stage 3 | fan of 7, 12° apart, every 2.2 s | fan turret, a sweep |
| core stage 4 | ring of 14 turning 12°, orange, every 1.5 s; fan of 5, 12° apart, red every 2.6 s | back rotor; fan turret |
| angry | the revealed weapons, BOSS-27 | `boss_build.angry_pattern` |
| transformation 1 | `lance-left` and `lance-right` destroyed | `transformParts` |
| wing-front region (shed) | the skirt's front flank out to the rim: x 16..46 at y -3.5..-28, then along the rim to (38, -38), (22, -46) and (16, -46.5), `wing`, mirrored; the plate 5-7 px | |
| batteries | (∓44, -26), radius 10, health 1 200, pod 14 px, red; first 1.2 s / 2.2 s | |
| transformation 2 | `silo-left` and `silo-right` destroyed | |
| roof halves (moving region) | the keep's own footprint, cut along the ridge: x 0..22, y -18..36, mirrored; the keep 17-30 px; slide 16 px apart; `shell` frame on the lower shell's top | `moving_region`, `slide`; `heights` 16 px |
| flank region (shed) | the skirt's rear flank, x 34..46 at y -3.5..36 then to (34, 50), and the forelimb from (46, 6) to (72, 6), (80, 23) and (46, 24), `wing`, mirrored; the plate 5-7 px, the limb's sinew to 13 px | |
| `cannon` | (0, 14), radius 14, health 1 500, pod 22 px, orange; first 1.4 s | rises between the roof halves |
| sweepers | (∓60, 22), radius 8, health 1 500, pod 14 px; first 2.4 s / 6.4 s | |
| neon | red (1, 0.1, 0.12), shown yellow | `BOSS_LOOK.neon` |

## Notes

- Its silos went from 890 to 1 500 health and its core from 2 420 to 3 000 when shots started going
  through a shielded core (D-062): the silos behind the core became easier to reach.
