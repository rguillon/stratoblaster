# Stone Idol (3-3 mini boss)

> **Area:** bosses · **Prefix:** `MB-STONE-IDOL` · **Related:** [common boss rules](../common.md),
> [3-3 Workers' quarter](../../worlds/world-3/3-3-workers-quarter.md),
> [World 3](../../worlds/world-3/world.md), [Sky Temple](../final/3-3-sky-temple.md),
> [readability](../../graphics/readability.md)

The Stone Idol is the mini boss of level 3-3, met at the middle of the level. It is a flying carved
stone head 3 L across, flying face up so the player sees its face: two eyes that turn to aim lasers,
a mouth that spits rings of slow boulders, neon light glowing through cracks in the stone. It was
designed for the old Jungle world's lost temples and, since World 3 became the
factories-to-garden-villages world (D-111), it keeps its name and look; the ground still stops while
it is fought, now over the workers' quarter. It transforms once by changing shape: the back of its
head flips up like a lid over a hidden eye and two mortars. Shared rules are in
[bosses/common.md](../common.md); this file only gives what is the Idol's own.

## Requirements

### Look

#### MB-STONE-IDOL-01 — Silhouette · MUST

Seen from above, the Idol is a carved head lying face up, chin down the screen: a broad face, a flat
crown and a heavy chin, an Olmec helmet over its forehead, heavy brows over two round eyes either
side of a nose ridge running from between the brows to its tip over an open mouth, and an ear spool
on each side. It is a 3 L boss (radius 1.5 L).

**Acceptance criteria**
- Given the dev bosses viewer, then it reads as a carved stone face looking up at the camera
  (manual).

*Sources: P09-R09.*

#### MB-STONE-IDOL-02 — Cyber-Organic head · MUST

It is a living head of grey-green flesh with the carved stone grown over it as armour (its helmet,
brows, nose and ear spools), roots of sinew trailing from its chin with veins and glands on them, and
its thrusters in flesh sacs at the back of its head. The brow ridge is broken on the left. The back
of the head over the skull cut, with the helmet and brows, is the lid of its crown (MB-STONE-IDOL-11).

**Acceptance criteria**
- Given the model, then flesh shows between the stone pieces and roots trail from the chin
  (manual).

*Sources: P16-R05.*

#### MB-STONE-IDOL-03 — Parts on the model · MUST

- Each **eye** (a part) is a deep, round socket in the face, its rim cracked and lit, a raw flesh
  eyelid ringed by a stone growth, veins spreading from its corner and moss on its lower lid; in it
  an **eyeball** turns (a turret): a wet, bone-white ball, its neon iris a pulsing gland looking up
  and forward, and the charge-lit lens its laser leaves from.
- The **mouth** (a part) is a living maw under the nose: swollen flesh lips with the carved stone
  grown over them, square stone teeth under the upper lip and worn ones on the lower, a red throat
  with a neon lining where its boulders leave from, and a vine hanging from the lower lip over the
  chin.

A destroyed part is hidden; a dark empty socket in the face is left where each eye and the mouth
were.

**Acceptance criteria**
- Given K destroys an eye, then its socket and eyeball disappear and an empty socket shows in the
  face (manual).

*Sources: P09-R09, P16-R05, D-225, D-167.*

#### MB-STONE-IDOL-04 — Temple growth and neon cracks · MUST

Neon cracks run across the face, lit from inside the stone. Moss fills the hollows, vines hang over
its crown, and a jewel is set in its forehead. The stone is weathered on its top faces and darker in
its recesses, the moss a clear green.

**Acceptance criteria**
- Given the model, then the cracks glow and moss and vines are visible (manual).

*Sources: P09-R09, D-231.*

#### MB-STONE-IDOL-05 — Lights and colours · MUST

Its neon is its own magenta (`stone-idol`), shown bright yellow under the enemy colour rule: the
cracks, the glow under the helmet's rim, the irises, the mouth's lining and the ear spools' bores.
White charge lights glow at the eyes' lenses, the nostrils and the forehead jewel. Its lasers are
drawn in its own neon, moved into the enemy shots' colours (see [common](../common.md)).

**Acceptance criteria**
- Given the model, then every neon light is bright yellow (unit: enemy colour family tests).

*Sources: P09-R09, D-231.*

### Behaviour

#### MB-STONE-IDOL-06 — Entry, place and a stopped ground · MUST

The Idol stops at 0.72 of the playfield's height, sways up to 60 px either side over 7.5 s and bobs
8 px over 3.6 s. While it is fought the ground stops (×0): the only World 3 fight that does.

**Acceptance criteria**
- Given the fight starts, then the ground eases to a stop and starts again once the Idol is
  destroyed (design value; common ground-speed rule tests).

*Sources: P09-R09, D-111.*

#### MB-STONE-IDOL-07 — Parts and health · MUST

The core (hit radius 22 px, 1 550 HP) has three original parts: two eyes (13 px, 950 HP each) 64 px
apart, which shield the core, and the mouth (13 px, 750 HP), which does not. The eyes are that far
apart so that a ship's spread can reach them. Its full health is 4 200 HP with the original parts,
6 480 HP with its three hidden weapons.

**Acceptance criteria**
- Given the design, then it has three original parts and three hidden ones, the eyes shielding the
  core (unit: `test_stone_idol.py`).

*Sources: P09-R09, P09-R10, D-081, D-221.*

#### MB-STONE-IDOL-08 — Part weapons · MUST

While they stand, in every stage:
- each eye fires a laser (1.5 s) every 6.5 s from its lens, the two taking turns (3.25 s apart); its
  eyeball turns to aim at the player during the warning line and holds still while the beam fires;
- the mouth spits a ring of 9 slow, big boulders (`purple`, 115 px/s, radius 9 px) every 3 s from its
  throat, turning 20° each time.

**Acceptance criteria**
- Given an eye's warning line shows, then its eyeball follows the player at the laser turret rate
  and holds still once the beam fires (unit: turret rules; design guns).

*Sources: P09-R09, D-073.*

#### MB-STONE-IDOL-09 — Core patterns by stage · MUST

The core fires from its nostrils, and from its forehead jewel once alone:
- stage 0: a fan of 3 `magenta` bullets (205 px/s, 16° apart) every 2.6 s;
- stage 1: a fan of 5 (13° apart) every 2.4 s;
- stage 2: two fans of 5 `orange` (210 px/s, 12° apart) every 2.6 s, leaning 18° to either side, 1.3 s
  apart;
- stage 3 (alone): a spiral from its jewel (rings of 5 `purple` at 200 px/s every 0.45 s, turning
  17°) and a fan of 7 `magenta` (11° apart) every 2.2 s.

**Acceptance criteria**
- Given the design, then it has four stages and the last one's spiral is used by no earlier stage
  (unit: `test_stone_idol.py`).

*Sources: P09-R09, D-081.*

#### MB-STONE-IDOL-10 — Rage · MUST

It is angry after its transformation, when the third eye and two mortars it revealed fire all out,
for `boss_rage_seconds`, `boss_rage_rate` times as often, instead of its stage's
pattern ([common](../common.md), BOSS-27). A lost part no longer angers it, and it has no
angry pattern of its own.

**Acceptance criteria**
- Given its transformation is over, then it is angry and fires only the third eye and two mortars it
  revealed (unit: `test_boss_build.py` angry_pattern).
- Given a part is destroyed without a transformation, then it is not angry (unit test).

*Sources: D-081, D-063, D-256.*

#### MB-STONE-IDOL-11 — Transformation: the back of its head flips up · MUST

At 2 of its 3 original parts destroyed (whichever they are), the Idol transforms once by changing
shape. The back of its head is the lid of its crown, drawn as a piece of its own ([common](../common.md),
BOSS-45): the head is cut flat at 7 px (the skull cut) behind the brows, 4 px behind the centre, and
the lid is the head's slice from just under the cut up to the face (12 px) over that back half, the
Olmec helmet (up to 17 px), the brows, the forehead jewel and the crown's cracks, moss, vines and
glands on it, a stone strap at its rear round the hinge's pin, which runs across the back of the
crown on the head. It stays on and flips up and back like a lid, 75° about the hinge (50 px behind
the centre, 7 px high): it strains, then swings open. Its region is the lid's own plan (the head's
section at the skull cut behind the brows: 44.5 px either side at the brows, tapering to the back of
the crown 47.5 px behind the centre). Where it lay, a dark metal `ring` frame (spokes and a hoop)
shows on the skull cut round the hidden weapons; the core's last-stage spiral still leaves from
where the jewel was set. No part the player can hit stands on the lid. The boss stays one object at
rest and after its transformation.

**Acceptance criteria**
- Given 2 original parts are destroyed, then the lid swings 75° open and stays open (unit:
  `test_boss_kinds.py`, `test_region_motion.py`).
- Given its model, then it draws the lid, and the boss holds together with the lid shut and open
  (unit: `test_boss_52_the_boss_holds_together_in_every_state`).

*Sources: D-230, D-224, D-227, D-254.*

#### MB-STONE-IDOL-12 — Hidden weapons: a third eye and two mortars · MUST

Under the lid are a great sweeper eye on the centre line, 24 px behind the centre (radius 13 px, pod
12 px high, 760 HP), firing a laser that sweeps after the player, and two mortars 30 px either side,
30 px behind (radius 8 px, pods 13 px high, 760 HP each), lobbing `purple` flak shells that burst into
rings. They shield the core and fire 1.6 s (eye), 1.2 s and 2.6 s (mortars) into a stage. The Idol
fires no less after its transformation than before.

**Acceptance criteria**
- Given the transformation is over, then the third eye and both mortars are live targets that fire
  (unit: `test_boss_kinds.py`).

*Sources: D-230, D-221, D-229.*

#### MB-STONE-IDOL-13 — Points and drops · MUST

Destroying the Idol scores 7 500 points, and each part destroyed 750. Its original parts drop a bonus
half of the time, its hidden weapons 30 %; its core drops one by the game's rule.

**Acceptance criteria**
- Given the mouth is destroyed, then the score rises by 750 (unit: scoring rule, design values).

*Sources: P07-R07, P11-R01, D-055.*

## Tunable values

All in `src/game/config/bosses/world_3/stone_idol.py` (`STONE_IDOL`) unless noted. Px from the
boss's centre, X right, Y up the screen (its chin at -Y).

| Name | Value | Notes |
|------|-------|-------|
| size | 3 L (radius 51 px) | |
| core | radius 22 px, 1 550 HP | |
| eyes | (±32, -4), radius 13, 950 HP, shield; lenses at (±32, -11.5), 12 px high | `IDOL_PARTS.eye`, `IDOL_EYE` |
| mouth | (0, -34), radius 13, 750 HP, no shield | `IDOL_PARTS.mouth` |
| full health | 4 200 (6 480 with hidden weapons) | P09-R10 band |
| stop / sway / bob | 0.72 / 60 px, 7.5 s / 8 px, 3.6 s | |
| ground speed | ×0 | |
| eye lasers | 1.5 s every 6.5 s, first 2 / 5.25 s | on turrets |
| boulders | ring of 9, `purple` 115 px/s, radius 9, every 3 s, turn 20° | `BOULDER` |
| angry | the revealed weapons, BOSS-27 | `boss_build.angry_pattern` |
| transformation | once, at 2 parts destroyed | `default_transforms` |
| crown lid | the head's section at the skull cut behind the brows: x ±44.5 at y 4–11.8, ±41.6 at y 29.1, ±34.3 at y 40, ±21.4 at y 45.6, to y 47.5 on the centre line; from 7 px; swing `across` about (0, 50, 7), 0 → -75°; `ring` frame; lid 6.7–19 px | `moving_region("crown", …)`; `stone_idol_lid.py` |
| third eye | sweeper (0, 24), radius 13, pod 12, 760 HP, first 1.6 s | |
| mortars | (±30, 30), radius 8, pod 13, 760 HP, `purple`, first 1.2 / 2.6 s | |
| points | 7 500 (750 a part) | |
| neon | [0.95, 0.2, 1] | `BOSS_LOOK.neon["stone-idol"]` |

## Notes

- Phase 9 fight time with the D-055 bot: 47.3 s, before the hidden weapons were added (D-221).
- With its hidden weapons counted, its full health (6 480) is above the next level's mini boss's,
  the Mosquito's (6 100); with the original parts only, the World 3 mini bosses still go up strictly
  (see [World 3](../../worlds/world-3/world.md)).
