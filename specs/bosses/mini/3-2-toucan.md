# Toucan (3-2 mini boss)

> **Area:** bosses · **Prefix:** `MB-TOUCAN` · **Related:** [common boss rules](../common.md),
> [3-2 Docklands](../../worlds/world-3/3-2-docklands.md), [World 3](../../worlds/world-3/world.md),
> [Canopy Spider](../final/3-2-canopy-spider.md), [readability](../../graphics/readability.md)

The Toucan is the mini boss of level 3-2, met at the middle of the level. It is a stubby gunship
3 L across shaped like a toucan: a round black body, short wings with a ducted fan pod at each end, a
fanned tail and a huge beak in front of its head, which is its laser cannon. It was designed for the
old Jungle world's rainforest and, since World 3 became the factories-to-garden-villages world
(D-111), it keeps its name and look and flies over the docklands. It transforms once: its back
plating bursts off and two missile racks come out. Shared rules are in
[bosses/common.md](../common.md); this file only gives what is the Toucan's own.

## Requirements

### Look

#### MB-TOUCAN-01 — Silhouette · MUST

Seen from above, the Toucan is a round-bodied bird nose down the screen: a short body, short straight
wings out to about 30 px either side of the centre line with a round fan pod at each end (38 px out),
a fan of tail feathers behind, and a huge, long beak reaching from its head to about 56 px ahead of
its centre, by far its most visible shape. It is a 3 L boss (radius 1.5 L).

**Acceptance criteria**
- Given the dev bosses viewer, then it reads as a toucan: round body, short wings with fan pods, a
  huge beak (manual).

*Sources: P09-R09.*

#### MB-TOUCAN-02 — Cyber-Organic body · MUST

Its body is a living bird's: a round body of dark flesh with a bone ribcage over its back and a vein
down its spine, the spine a ridge along its back between the two plates of its back plating
(MB-TOUCAN-12), a cream bib under its head, short heavy membrane wings on bone struts, a fan of bone
quills for a tail, and its two reactors in flesh sacs at the tail. Its heavy wings stay still (they do
not flutter). The beak is living horn with a metal band at its root.

**Acceptance criteria**
- Given the model, then the body is flesh with grafted plates, seams and vents, and its wings do not
  move (manual).

*Sources: P16-R05, P16-R07.*

#### MB-TOUCAN-03 — Head · MUST

Its head has a round neon eye on each side with a charge light at its centre (on the cheek of its
back plating, MB-TOUCAN-12), a cheek gun under each eye (11 px either side, 24 px ahead of the
centre) and a crest emitter on top of its head (17 px high) on a socket ringed with neon, on the
spine ridge.

**Acceptance criteria**
- Given the model, then the cheek guns and the crest stand at the design's muzzles (unit:
  `test_boss_models.py`).

*Sources: P09-R09.*

#### MB-TOUCAN-04 — Parts on the model · MUST

- The **beak** (a part) is a huge, faceted beak painted yellow along most of its length, orange
  towards its tip and dark at its root, with neon along its ridge and its cutting edges, nostrils at
  its root and, in its tip, the laser emitter: a dark barrel ringed with neon round a charge lens.
  Its paint is a body shade, so the enemy colour rule greys it to a pale, bright horn: the beak reads
  by its size and its neon edges.
- Each **wing pod** (a part) is a ducted fan at the wing's end: a grafted duct, its lip ringed with
  neon, growing out of a swollen flesh root fed by a vein, a spinning fan inside, a gun housing under
  its front with two barrels, moss on its back and a navigation lamp on its outer side.

A destroyed part is hidden and leaves nothing in its place.

**Acceptance criteria**
- Given K destroys the beak, then the whole beak disappears and the head stays (manual).

*Sources: P09-R09, P16-R05, D-225, D-167, D-231.*

#### MB-TOUCAN-05 — Rainforest growth · MUST

Moss lies on its back and its wings and pods, and vines hang from under its wings: the World 3 growth
over its dark metal and flesh, in clear greens.

**Acceptance criteria**
- Given the model, then moss and hanging vines are visible (manual).

*Sources: P09-R09, D-231.*

#### MB-TOUCAN-06 — Lights and colours · MUST

Its neon is its own yellow (`toucan`) with orange accents, both shown bright yellow under the enemy
colour rule: the eyes, the wings' leading edges and the pods' lips in its yellow, the flanks, the
tail, the spine vein, the beak's cutting edges and its emitter ring in the accent. The left pod's lamp
(drawn red) shows yellow and the right one's green. White charge lights glow in the eyes, the
cheek guns, the pod barrels, the crest and the beak's lens. Its laser is drawn in its own neon,
moved into the enemy shots' colours (see [common](../common.md)).

**Acceptance criteria**
- Given the model, then every neon light is bright yellow or bright green (unit: enemy colour family
  tests).

*Sources: P09-R09, D-231.*

### Behaviour

#### MB-TOUCAN-07 — Entry, place and ground speed · MUST

The Toucan stops at 0.73 of the playfield's height, sways up to 60 px either side over 7 s and bobs
8 px over 3.6 s. While it is fought the ground runs at ×0.6.

**Acceptance criteria**
- Given the fight starts, then the ground slows to ×0.6 (design values; common rule tests).

*Sources: P09-R09.*

#### MB-TOUCAN-08 — Parts and health · MUST

The core (hit radius 17 px, 1 640 HP) has three original parts: two wing pods (13 px, 780 HP each)
that shield the core, and the beak (12 px, 580 HP), which does not: it hangs in front of the core, so
it can always be shot. Its full health is 3 780 HP with the original parts, 5 020 HP with its two
hidden missile racks.

**Acceptance criteria**
- Given the design, then it has three original parts and two hidden ones, the pods shielding the core
  (unit: `test_toucan.py`).

*Sources: P09-R09, P09-R10, D-081, D-221.*

#### MB-TOUCAN-09 — Part weapons · MUST

While they stand, in every stage:
- each pod fires a fan of 3 `orange` bullets (195 px/s, 14° apart) every 2.4 s, leaning 10° towards
  the other side, so that the two fans cross under the gunship, 1.2 s apart;
- the beak fires a laser (1.4 s, after its warning line) every 6 s from its tip.

**Acceptance criteria**
- Given the beak stands, then its laser leaves from the beak's tip (unit: design guns).

*Sources: P09-R09.*

#### MB-TOUCAN-10 — Core patterns by stage · MUST

The core fires from its cheek guns, and from its crest once alone:
- stage 0: aimed bursts of 3 `red` bullets (205 px/s, 0.15 s apart) every 2.8 s;
- stage 1: bursts of 4 (0.13 s apart) every 2.5 s;
- stage 2: bursts of 4 (0.12 s apart) every 2.6 s, and 3 aimed `magenta` bullets (210 px/s, 12° apart)
  every 2.6 s;
- stage 3 (alone): a spiral from its crest (rings of 12 `purple` at 200 px/s every 1.3 s, turning
  11°) and bursts of 3 `red` every 2.4 s.

**Acceptance criteria**
- Given the design, then it has four stages and the last one's spiral is used by no earlier stage
  (unit: `test_toucan.py`).

*Sources: P09-R09, D-081.*

#### MB-TOUCAN-11 — Rage · MUST

It is angry after its transformation, when the two missile racks it revealed fire all out,
for `boss_rage_seconds`, `boss_rage_rate` times as often, instead of its stage's
pattern ([common](../common.md), BOSS-27). A lost part no longer angers it, and it has no
angry pattern of its own.

**Acceptance criteria**
- Given its transformation is over, then it is angry and fires only the two missile racks it
  revealed (unit: `test_boss_build.py` angry_pattern).
- Given a part is destroyed without a transformation, then it is not angry (unit test).

*Sources: D-081, D-063, D-256.*

#### MB-TOUCAN-12 — Transformation: back plating, two missile racks · MUST

At 2 of its 3 original parts destroyed, the Toucan transforms once. Its back plating bursts off
([common](../common.md), BOSS-42): two plates drawn as pieces of their own, one either side of the
spine ridge, over the flattened body, from just under the body's top (4.3 px) up to its back (15 px
at its fullest), from the tail stub (26 px behind the centre) to the head (21 px ahead). Each plate
is the body's own skin there, from the ridge over the shoulder down to the flank, and carries the
eye on its cheek, the orange neon along its flank, the seam and vent on its back and its moss; the
spine ridge with the crest emitter, the ribcage's arches and the cheek guns stay on the body. The
region (`back`, the right plate's plan mirrored: from 2 to 17 px out, between the ridge and the
body's flank) bursts into plates cracked from the two outlines and leaves a dark metal `shell` frame
either side of the ridge. Two missile racks come out at 12 px either side of the centre line, 9 px
ahead of the centre (radius 10 px, pods 18 px high, 620 HP each, 30 % drop chance). They shield the
core and each fires 2 homing missiles every 6 s, 1.2 s and 2.0 s into a stage. The Toucan fires no
less after its transformation than before, and stays one object in every state.

**Acceptance criteria**
- Given 2 original parts are destroyed, then the back region bursts off and both racks come out and
  fire (unit: `test_boss_kinds.py`).
- Given its model, then it draws the back region's armour, and the boss holds together with and
  without it (unit: `test_boss_52_the_boss_holds_together_in_every_state`).

*Sources: D-221, D-224, D-229, D-227, D-254.*

#### MB-TOUCAN-13 — Points and drops · MUST

Destroying the Toucan scores 6 000 points, and each part destroyed 600. Its original parts drop a
bonus half of the time; its core drops one by the game's rule.

**Acceptance criteria**
- Given a pod is destroyed, then the score rises by 600 (unit: scoring rule, design values).

*Sources: P07-R07, P11-R01, D-055.*

## Tunable values

All in `src/game/config/bosses/world_3/toucan.py` (`TOUCAN`) unless noted. Px from the boss's centre,
X right, Y up the screen (its beak at -Y).

| Name | Value | Notes |
|------|-------|-------|
| size | 3 L (radius 51 px) | |
| core | radius 17 px, 1 640 HP | |
| wing pods | (±38, 2), radius 13, 780 HP, shield | |
| beak | (0, -38), radius 12, 580 HP, no shield; tip at (0, -55.6) | `TOUCAN_BEAK_TIP` |
| full health | 3 780 (5 020 with hidden weapons) | P09-R10 band 3 550–3 900 |
| stop / sway / bob | 0.73 / 60 px, 7 s / 8 px, 3.6 s | |
| ground speed | ×0.6 | |
| pod fans | 3 × 14°, every 2.4 s, lean ±10° | |
| beak laser | 1.4 s every 6 s | |
| angry | the revealed weapons, BOSS-27 | `boss_build.angry_pattern` |
| transformation | once, at 2 parts destroyed | `default_transforms` |
| back region | two plates either side of the ridge: right one x 2.1–10.6 at y -21, to 17 at y -6, 16 at y 10, 2.2–11 at y 26 (mirrored), `shell`; plates 4.0–15 px over the body (top 4.3) | `armour_region("back", …)`; `toucan_model.py` `KEEL`, `PLATES` |
| missile racks | (±12, -9), radius 10, pod 18, 620 HP, first 1.2 / 2.0 s | |
| points | 6 000 (600 a part) | |
| neon | [1, 0.7, 0.1]; accent [1, 0.36, 0.04] | `BOSS_LOOK.neon["toucan"]`; `src/game/view/bosses/world_3/toucan_parts.py` `TOUCAN_ORANGE` |
| beak paint | yellow [0.95, 0.66, 0.1], orange [0.95, 0.34, 0.05] | `toucan_parts.py` |

## Notes

- Phase 9 fight time with the D-055 bot: 44.4 s, before the hidden weapons were added (D-221).
