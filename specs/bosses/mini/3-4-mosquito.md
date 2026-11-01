# Mosquito (3-4 mini boss)

> **Area:** bosses · **Prefix:** `MB-MOSQUITO` · **Related:** [common boss rules](../common.md),
> [3-4 Suburbs](../../worlds/world-3/3-4-suburbs.md), [World 3](../../worlds/world-3/world.md),
> [Dam Breaker](../final/3-4-dam-breaker.md), [readability](../../graphics/readability.md)

The Mosquito is the mini boss of level 3-4, met at the middle of the level. It is a thin, fast
bio-drone 3 L across shaped like a mosquito: long buzzing wings with a fan pod under each, a big-eyed
head and a needle-like proboscis that turns to aim a laser. It darts from side to side. It was
designed for the old Jungle world's swamp and, since World 3 became the factories-to-garden-villages
world (D-111), it keeps its name and look and flies over the suburbs. It transforms once: its back
plating bursts off and two heavy cannons come out. Shared rules are in
[bosses/common.md](../common.md); this file only gives what is the Mosquito's own.

## Requirements

### Look

#### MB-MOSQUITO-01 — Silhouette · MUST

Seen from above, the Mosquito is a thin insect nose down the screen: a big-eyed head, a small thorax,
a long segmented abdomen behind, six thin legs hanging under the thorax, a long needle reaching about
53 px ahead of its centre, and two long, thin wings rooted either side of the thorax and reaching out
to about 52 px either side. It is a 3 L boss (radius 1.5 L).

**Acceptance criteria**
- Given the dev bosses viewer, then it reads as a mosquito: thin body, long wings, long needle
  (manual).

*Sources: P09-R09.*

#### MB-MOSQUITO-02 — Cyber-Organic body · MUST

It is a living insect: a dark flesh thorax, a swollen, blood-filled abdomen ringed by grafted metal
bands with a vein pulsing down its back, a blood sac swelling out of the abdomen's flesh on its back,
feathery antennae of sinew tipped with a lit gland, and six thin legs of sinew with a metal knee
joint grafted where they bend. Its head is a rounded capsule with big compound eyes (low neon domes)
and twin mandible guns under them.

**Acceptance criteria**
- Given the model, then the body reads as one living insect (manual).

*Sources: P16-R05.*

#### MB-MOSQUITO-03 — Parts on the model · MUST

- Each **wing** (a part) is a long, thin membrane with a dark, oily sheen on a bone spar, veined with
  neon from root to tip, and under it its fan pod: a grafted metal nacelle in a flesh sheath with two
  barrels on the wing's leading edge.
- The **proboscis** (a part) is a ringed socket under the head, a fleshy mouthpart sheath with metal
  blades grafted either side of it; in it turns the **needle** (a turret), a long, thin spike ringed
  in neon whose point glows as its laser charges.

A destroyed part is hidden and leaves nothing in its place: a destroyed wing is gone, membrane and
pod.

**Acceptance criteria**
- Given K destroys a wing, then the whole wing disappears (manual).

*Sources: P09-R09, P16-R05, D-225, D-167.*

#### MB-MOSQUITO-04 — Buzzing wings · MUST

The wings are moving limbs on joints at their roots (11 px either side of the centre line, 4 px
behind the centre): they buzz, swinging 7° five times a second (a 0.2 s period), the two beating
together as mirror images. The wings' hit circles and guns move with them.

**Acceptance criteria**
- Given the boss is in place, then the wings buzz fast and small, the pair together (manual, dev
  viewer).

*Sources: P09-R09, D-081, D-061.*

#### MB-MOSQUITO-05 — Swamp growth · MUST

Moss tufts grow on its back and a strand of vine trails from its side: the World 3 growth, in clear
greens.

**Acceptance criteria**
- Given the model, then moss and the vine are visible (manual).

*Sources: P09-R09, D-231.*

#### MB-MOSQUITO-06 — Lights and colours · MUST

Its neon is its own pink (`mosquito`), shown bright yellow under the enemy colour rule: the bands
between the abdomen's segments, the compound eyes, the wings' veins and the needle's rings. White
charge lights glow at the mandible guns, the wing barrels, the needle's point and the blood sac,
which lights up as its next ring charges. Its laser is drawn in its own neon, moved into the enemy
shots' colours (see [common](../common.md)).

**Acceptance criteria**
- Given the model, then every neon light is bright yellow (unit: enemy colour family tests).

*Sources: P09-R09, D-231.*

### Behaviour

#### MB-MOSQUITO-07 — Entry, place and ground speed · MUST

The Mosquito stops at 0.74 of the playfield's height and darts from side to side: it sways up to 72 px
either side over 5.6 s (the widest and fastest sway in World 3) and bobs 10 px over 2.6 s. While it is
fought the ground runs at ×0.6.

**Acceptance criteria**
- Given the fight, then it sways faster than the other World 3 mini bosses (design values).

*Sources: P09-R09.*

#### MB-MOSQUITO-08 — Parts and health · MUST

The core (hit radius 16 px, 1 750 HP) has three original parts: two wings (13 px, 1 000 HP each,
centred on their pods 35 px out) that shield the core and ride their joints, and the proboscis (10 px,
750 HP), which does not: it hangs in front of the core, so it can always be shot. Its full health is
4 500 HP with the original parts, 6 100 HP with its two hidden cannons.

**Acceptance criteria**
- Given the design, then it has three original parts and two hidden ones, the wings shielding the
  core (unit: `test_mosquito.py`).

*Sources: P09-R09, P09-R10, D-081, D-221.*

#### MB-MOSQUITO-09 — Part weapons · MUST

While they stand, in every stage:
- each wing fires a fan of 3 `magenta` bullets (200 px/s, 14° apart) every 2.2 s from its pod,
  leaning 10° towards the other side so the two fans cross under the drone, 1.1 s apart;
- the proboscis fires a laser (1.4 s) every 5.5 s from the needle's tip; the needle turns to aim at
  the player during the warning line and holds still while the beam fires.

**Acceptance criteria**
- Given the proboscis's warning line shows, then the needle follows the player at the laser turret
  rate (unit: turret rules; design guns).

*Sources: P09-R09, D-073.*

#### MB-MOSQUITO-10 — Core patterns by stage · MUST

The core fires aimed bursts from its mandible guns that change at every stage, and a ring from its
blood sac once alone:
- stage 0: bursts of 3 `red` bullets (205 px/s, 0.14 s apart) every 2.6 s;
- stage 1: bursts of 4 (0.12 s apart) every 2.3 s;
- stage 2: bursts of 5 `purple` (210 px/s, 0.11 s apart) every 2.2 s, and 3 aimed `red` (12° apart)
  every 2.8 s;
- stage 3 (alone): a ring of 12 `blue` (195 px/s) every 1.4 s turning 8°, and bursts of 3 `red` every
  2.4 s.

**Acceptance criteria**
- Given the design, then it has four stages and the last one's ring is used by no earlier stage
  (unit: `test_mosquito.py`).

*Sources: P09-R09, D-081.*

#### MB-MOSQUITO-11 — Rage · MUST

After the pause that follows each destroyed part, it fires a vortex at heat 7.5, in `magenta` and
`purple`.

**Acceptance criteria**
- Given a part is destroyed, when its pause is over, then the core fires the vortex (unit: rage
  patterns).

*Sources: D-081, D-063.*

#### MB-MOSQUITO-12 — Transformation: back plating, two heavy cannons · MUST

At 2 of its 3 original parts destroyed, the Mosquito transforms once. Its back plating (one region
across the centre line, 30 px either side, from 29.4 px ahead of the centre to 19 px behind it, from
the playfield up) bursts off over a dark metal `shell` frame, and two heavy cannons come out at 12 px
either side, 11 px ahead of the centre (radius 10 px, pods 8.1 px high, 800 HP each, 30 % drop
chance). They shield the core and fire `magenta` aimed spreads of big shells, 1.2 s and 2.0 s into a
stage. The Mosquito fires no less after its transformation than before, and stays one object in every
state.

**Acceptance criteria**
- Given 2 original parts are destroyed, then the back region bursts off and both cannons come out and
  fire (unit: `test_boss_kinds.py`).
- Given each state, then nothing of it hangs in the air (unit:
  `test_d227_the_boss_holds_together_in_every_state`).

*Sources: D-221, D-224, D-229, D-227.*

#### MB-MOSQUITO-13 — Points and drops · MUST

Destroying the Mosquito scores 7 500 points, and each part destroyed 750. Its original parts drop a
bonus half of the time; its core drops one by the game's rule.

**Acceptance criteria**
- Given the proboscis is destroyed, then the score rises by 750 (unit: scoring rule, design values).

*Sources: P07-R07, P11-R01, D-055.*

## Tunable values

All in `src/game/config/bosses/world_3/mosquito.py` (`MOSQUITO`) unless noted. Px from the boss's
centre, X right, Y up the screen (its needle at -Y).

| Name | Value | Notes |
|------|-------|-------|
| size | 3 L (radius 51 px) | |
| core | radius 16 px, 1 750 HP | |
| wings | roots (±11, 4); pods (±35, 2), radius 13, 1 000 HP, shield | `MOSQUITO_WING` |
| proboscis | (0, -32), radius 10, 750 HP, no shield; needle tip (0, -53) | `MOSQUITO_PROBOSCIS`, `MOSQUITO_NEEDLE` |
| full health | 4 500 (6 100 with hidden weapons) | P09-R10 band |
| stop / sway / bob | 0.74 / 72 px, 5.6 s / 10 px, 2.6 s | |
| ground speed | ×0.6 | |
| buzz | ±7°, 0.2 s period | `BUZZ` |
| wing fans | 3 × 14°, every 2.2 s, lean ±10° | |
| proboscis laser | 1.4 s every 5.5 s | on a turret |
| rage | vortex, heat 7.5 | |
| transformation | once, at 2 parts destroyed | `default_transforms` |
| back region | x ±30, y -29.4..19, from 0 px, `shell` | |
| cannons | (±12, -11), radius 10, pod 8.1, 800 HP, `magenta`, first 1.2 / 2.0 s | |
| points | 7 500 (750 a part) | |
| neon | [1, 0.3, 0.7] | `BOSS_LOOK.neon["mosquito"]` |

## Notes

- Phase 9 fight time with the D-055 bot: 51.4 s, before the hidden weapons were added (D-221).
- With its hidden cannons counted, its full health (6 100) is below the previous level's mini boss's,
  the Stone Idol's (6 480); with the original parts only (4 500 against 4 200) the World 3 mini
  bosses still go up strictly (see [World 3](../../worlds/world-3/world.md)).
