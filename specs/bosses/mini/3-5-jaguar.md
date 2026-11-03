# Jaguar (3-5 mini boss)

> **Area:** bosses · **Prefix:** `MB-JAGUAR` · **Related:** [common boss rules](../common.md),
> [3-5 Garden villages](../../worlds/world-3/3-5-garden-villages.md),
> [World 3](../../worlds/world-3/world.md), [Verdant Crown](../final/3-5-verdant-crown.md),
> [readability](../../graphics/readability.md)

The Jaguar is the mini boss of level 3-5, met at the middle of the level. It is a sleek stealth
interceptor 3.5 L across with spotted armour: a cat's head on a long nose, claw guns reaching forward
from its wing roots, and a tail curling out to a cannon held high over its left wing. It was designed
for the old Jungle world's canopy city and, since World 3 became the factories-to-garden-villages
world (D-111), it keeps its name and look and flies over the garden villages. It transforms once: the
spotted pelt of both its wings bursts off, baring dark metal wing frames, and a laser lance unfolds on
each wing. Shared rules are in [bosses/common.md](../common.md); this file only gives what is the
Jaguar's own.

## Requirements

### Look

#### MB-JAGUAR-01 — Silhouette · MUST

Seen from above, the Jaguar is a stealth delta, nose down the screen: a long nose reaching about 61 px
ahead of its centre, wings swept back from the claw roots out to about 57 px either side with a
sawtooth trailing edge, a fuselage down the centre line, and a tail curling from the fuselage's end out
to a cannon pod over its left wing, 30 px left of and 42 px behind the centre. It is a 3.5 L boss
(radius 1.75 L).

**Acceptance criteria**
- Given the dev bosses viewer, then it reads as a swept stealth wing with a cat's head and a curled
  tail (manual).

*Sources: P09-R09.*

#### MB-JAGUAR-02 — Cyber-Organic body · MUST

Under its pelt it is a living cat: a bone spine, sinews and veins showing under its armour. Its head
is a cat's on the fuselage, with ears, angry neon eyes and twin fang guns under the nose (4.5 px either
side, 55 px ahead). The cockpit is dark. A lit eye on its back behind the cockpit is the core's spiral
emitter. Its reactors sit at the tail.

**Acceptance criteria**
- Given the model, then the cat's head, ears and eyes read from above (manual).

*Sources: P09-R09, P16-R05.*

#### MB-JAGUAR-03 — Spotted armour · MUST

Its armour is a warm ochre metal (a body shade, greyed by the enemy colour rule) painted with jaguar
rosettes: on each wing's pelt (MB-JAGUAR-11) seven rosettes of five dark blotches in a ring round a
darker heart, and spots on the claw pads and the tail pods. Its wings' leading edges are lit with
neon.

**Acceptance criteria**
- Given the model, then rosettes are visible on both wings (manual).

*Sources: P09-R09, D-231.*

#### MB-JAGUAR-04 — Parts on the model · MUST

- Each **claw gun** (a part) is an armoured pad on an arm reaching forward from the wing root, spotted
  on top with neon lights along its flank, and on it a turret: a low housing with twin barrels between
  three steel talons curving forward like a paw's claws.
- The **tail cannon** (a part) is a spotted pod at the tail's tip with a pylon and a lit ring, and on
  the pylon a turret: a spotted pod with a long barrel reaching forward over the wing, its lens glowing
  as its laser charges.

A destroyed part is hidden and leaves nothing in its place.

**Acceptance criteria**
- Given K destroys a claw gun, then its pad and turret disappear (manual).

*Sources: P09-R09, P16-R05, D-225, D-167.*

#### MB-JAGUAR-05 — Lights and colours · MUST

Its neon is its own amber (`jaguar`), shown bright yellow under the enemy colour rule: the eyes, the
wings' leading edges, the claw pads' lights and the tail mount's ring. White charge lights glow at the
fang guns, the claw barrels, the tail cannon's lens and the eye on its back. Its lasers are drawn in
its own neon, moved into the enemy shots' colours (see [common](../common.md)).

**Acceptance criteria**
- Given the model, then every neon light is bright yellow (unit: enemy colour family tests).

*Sources: P09-R09, D-231.*

### Behaviour

#### MB-JAGUAR-06 — Entry, place and ground speed · MUST

The Jaguar stops at 0.74 of the playfield's height, sways up to 60 px either side over 6 s and bobs
8 px over 3 s. While it is fought the ground runs at ×0.6.

**Acceptance criteria**
- Given the fight starts, then the ground slows to ×0.6 (design values; common rule tests).

*Sources: P09-R09.*

#### MB-JAGUAR-07 — Parts and health · MUST

The core (hit radius 20 px, 2 000 HP) has three original parts: two claw guns (15 px, 1 100 HP each),
which shield the core, and the tail cannon (14 px, 900 HP), which does not. Their hit circles are
large so that a ship's spread can reach them. Its full health is 5 100 HP with the original parts,
6 860 HP with its two hidden lances.

**Acceptance criteria**
- Given the design, then it has three original parts and two hidden ones, the claws shielding the core
  (unit: `test_jaguar.py`).

*Sources: P09-R09, P09-R10, D-081, D-221.*

#### MB-JAGUAR-08 — Part weapons · MUST

While they stand, in every stage:
- each claw gun turns on its pad and fires an aimed spread of 3 `orange` bullets (205 px/s, 11°
  apart) every 2.1 s, the two about 1 s apart;
- the tail cannon fires a laser (1.4 s) every 6 s from its lens; its turret turns to aim at the player
  during the warning line and holds still while the beam fires.

**Acceptance criteria**
- Given a claw gun fires, then its turret points at the player (unit: turret rules; design guns).

*Sources: P09-R09, D-060, D-073.*

#### MB-JAGUAR-09 — Core patterns by stage · MUST

The core fires spirals from the lit eye on its back, a new one at each stage:
- stage 0: rings of 3 `red` bullets (200 px/s) every 0.55 s, turning 17°;
- stage 1: rings of 4 every 0.5 s, turning -21°;
- stage 2: rings of 5 `purple` (195 px/s) every 0.5 s, turning 25°;
- stage 3 (alone): twin spirals of 5 every 0.45 s turning opposite ways (`red` 13°, `purple` -15°).

**Acceptance criteria**
- Given the design, then it has four stages and the last one's twin spirals are used by no earlier
  stage (unit: `test_jaguar.py`).

*Sources: P09-R09, D-081.*

#### MB-JAGUAR-10 — Rage · MUST

After the pause that follows each destroyed part, it fires a curtain at heat 8.5, in `orange` and
`red`: the hottest mini boss rage of World 3.

**Acceptance criteria**
- Given a part is destroyed, when its pause is over, then the core fires the curtain (unit: rage
  patterns).

*Sources: D-081, D-063.*

#### MB-JAGUAR-11 — Transformation: the wings' pelt pops off · MUST

At 2 of its 3 original parts destroyed, the Jaguar transforms once. The spotted pelt of each whole
wing, from the fuselage's side out to the wing tip (its outline drawn by hand, mirrored for the left
wing), bursts off ([common](../common.md), BOSS-42): the pelt is drawn as a piece of its own, a plate
of ochre armour lying on the wing's top face (inset 2 px from the outline, as the wing's bevel runs),
from just under the wing's top (3 px) up to 4.5 px, carrying the wing's seven rosettes, its vent and
the vein across it; the wing itself (its lower skin, up to 3 px), its lit leading edge, the sinews
and the canted fins stay. It bursts into plates cracked from the outline and bares a dark metal
`wing` frame on the wing: dark ribs across it and two spars, one rib in three with a thin neon seam.
The boss stays one object at rest and after its transformation.

**Acceptance criteria**
- Given 2 original parts are destroyed, then both wings' pelt bursts off and the wing frames show
  (unit: `test_boss_kinds.py`, `test_boss_armour.py`; manual: the wings read as bared dark metal).
- Given its model, then it draws the wings' pelt, and the boss holds together with and without it
  (unit: `test_boss_52_the_boss_holds_together_in_every_state`).

*Sources: D-224, D-221, D-227, D-254.*

#### MB-JAGUAR-12 — Hidden weapons: a laser lance on each wing · MUST

A laser lance unfolds on each wing, 38 px either side of the centre line and 4 px ahead of the centre
(radius 10 px, pods 5 px high, 880 HP each, 30 % drop chance), swinging up from folded flat and
sliding out. They shield the core and each fires a laser as every lance does (see
[common](../common.md)), 1.2 s and 4.9 s into a stage, so the two take turns. The Jaguar fires no less
after its transformation than before.

**Acceptance criteria**
- Given the transformation is over, then both lances are live targets that fire their lasers in turn
  (unit: `test_boss_kinds.py`).

*Sources: D-224, D-221, D-229.*

#### MB-JAGUAR-13 — Points and drops · MUST

Destroying the Jaguar scores 8 000 points, and each part destroyed 800. Its original parts drop a
bonus half of the time; its core drops one by the game's rule.

**Acceptance criteria**
- Given the tail cannon is destroyed, then the score rises by 800 (unit: scoring rule, design values).

*Sources: P07-R07, P11-R01, D-055.*

## Tunable values

All in `src/game/config/bosses/world_3/jaguar.py` (`JAGUAR`) unless noted. Px from the boss's centre,
X right, Y up the screen (its nose at -Y).

| Name | Value | Notes |
|------|-------|-------|
| size | 3.5 L (radius 59.5 px) | |
| core | radius 20 px, 2 000 HP | |
| claw guns | (±34, -22), radius 15, 1 100 HP, shield; barrels at (±34 ± 2.6, -42), 6 px high | `JAGUAR_PARTS.claw`, `JAGUAR_CLAW` |
| tail cannon | (-30, 42), radius 14, 900 HP, no shield; lens (-30, 18), 17 px high | `JAGUAR_PARTS.tail`, `JAGUAR_TAIL` |
| full health | 5 100 (6 860 with hidden weapons) | P09-R10 band |
| stop / sway / bob | 0.74 / 60 px, 6 s / 8 px, 3 s | |
| ground speed | ×0.6 | |
| claw spreads | 3 × 11°, every 2.1 s | on turrets |
| tail laser | 1.4 s every 6 s | on a turret |
| rage | curtain, heat 8.5 | |
| transformation | once, at 2 parts destroyed | `default_transforms` |
| wing pelt | `JAGUAR_WING` outline (mirrored), `wing` frame; the pelt a plate 2.7–4.5 px high on the wing's top face (3 px), inset 2 px | `armour_region("wings", …)`; `src/game/view/bosses/world_3/jaguar_pelt.py` |
| lances | (±38, 4), radius 10, pod 5, 880 HP, first 1.2 / 4.9 s | |
| points | 8 000 (800 a part) | |
| coat | [0.2, 0.135, 0.06] | `src/game/view/bosses/world_3/jaguar_parts.py` `COAT` |
| neon | [1, 0.6, 0.05] | `BOSS_LOOK.neon["jaguar"]` |

## Notes

- Phase 9 fight time with the D-055 bot: 54.7 s, before the hidden weapons were added (D-221).
- The Jaguar's wing pelt and lances are the reviewer's own example for armour shedding (D-224): it had
  a pair of missile racks first; lances fire more, so it still escalates.
