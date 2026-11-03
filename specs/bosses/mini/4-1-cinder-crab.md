# Cinder Crab (4-1 mini boss)

> **Area:** bosses · **Prefix:** `MB-CINDER-CRAB` · **Related:** [common boss rules](../common.md),
> [4-1 Garden town](../../worlds/world-4/4-1-garden-town.md), [World 4](../../worlds/world-4/world.md),
> [Steam Dreadnought](../final/4-1-steam-dreadnought.md), [readability](../../graphics/readability.md),
> [shots](../../graphics/shots.md)

The Cinder Crab is the mini boss of level 4-1, met at the middle of the level. It is a wide, low
crab-ship 3 L across, its two claws opening and closing on swinging arms, a ring dome on its back and
a mortar behind it. It was designed for the Volcanic Lands' black-sand coast (soot, heat glow,
molten seams); since World 4 became the Metropolis (D-112) it keeps its name and its forge look and
flies over the garden town. It transforms once: its flank armour bursts off and two gatling turrets
come out. Everything shared by all bosses (parts and core, stages, rage, turrets, joints,
transformations, colours, death, checkpoint) is in [bosses/common.md](../common.md); this file only
gives what is the Crab's own. Positions are px from the boss's centre, X right, Y up the screen (it
faces down the screen, its front at -Y); heights are above the playfield.

## Requirements

### Look

#### MB-CINDER-CRAB-01 — Silhouette · MUST

Seen from above, the Crab is a wide, low crab about 3 L across (radius 1.5 L), facing down the
screen: a broad, flat carapace about 96 px wide and 56 px long, six short legs (three a side), two
eye stalks at its front, two arms reaching forward from under its front rim to the two claws (about
36 px ahead of its centre and 24 px either side), a ring dome on its back and a squat mortar behind
the dome. It is low: the carapace stands about 12 px high at most.

**Acceptance criteria**
- Given the dev bosses viewer, when the Crab is shown, then it reads as a wide, low crab with two
  claws in front, a dome and a mortar on its back (manual).

*Sources: P10-R11.*

#### MB-CINDER-CRAB-02 — Cyber-Organic body · MUST

Its body is a living crab's (Cyber-Organic): a scorched flesh shell banded in darker seams, bony
legs that bend up at the knee and down to a pointed foot, glowing glands as eyes on fleshy stalks,
bone ribs arching over its back, a molten vein across it and a glowing gland either side of its back.
Metal is grafted on as its belly plate, its brow plate, the arms' shoulder sockets, the ring dome
and the guns. Its back carries the World 4 forge dressing: molten seams between its plates, soot
stains, a row of bolts and a hot vent. Its two reactors sit in glowing flesh sacs at the back.

**Acceptance criteria**
- Given the model, then its body is drawn in flesh with metal grafts (belly plate, dome, sockets,
  guns), and it reads as one creature (manual).

*Sources: P10-R11, P16-R05.*

#### MB-CINDER-CRAB-03 — Claws and arms · MUST

Each claw is drawn on its arm where the design places it: a swollen flesh palm with a molten gland
and a molten seam across it, a fixed bone finger on its inner side with dark metal teeth, a moving
bone finger on its outer side with a hot glow along its inner edge, a neon line along the palm's
outer side and the palm gun between the fingers. Each arm is a flesh shoulder ball, an upper arm out
to a dark metal elbow and a forearm to the wrist, a neon line along the upper arm and a molten one
along the forearm. A destroyed claw takes its arm and its moving finger with it: they are hidden and
nothing is left in their place.

**Acceptance criteria**
- Given the dev viewer, when K destroys a claw, then the claw, its arm and its finger disappear
  (manual; `test_boss_models.py` checks every part is drawn).

*Sources: P10-R11, P16-R05, D-225, D-167.*

#### MB-CINDER-CRAB-04 — Back mortar · MUST

The mortar stands on the back of the carapace behind the dome: a squat metal turntable ringed with
neon, a fat barrel on trunnions leaning forward over the carapace, its mouth glowing as it loads.
Destroyed, it is hidden and leaves nothing in its place.

**Acceptance criteria**
- Given the model, then the mortar's mouth sits at its muzzle, over the carapace's back (unit:
  `test_boss_models.py`; manual).

*Sources: P10-R11, P16-R05, D-225.*

#### MB-CINDER-CRAB-05 — Lights and colours · MUST

Its registered neon is orange (`cinder-crab`); like every boss's lights it is drawn bright yellow
(see [readability](../../graphics/readability.md)). Neon runs along both flanks of the carapace, on
the knees of its legs, on the eye stalks' tips, round the dome and the mortar, and along the claws
and arms; its molten seams, veins and glands are drawn in the same yellow family. White charge
lights sit on the dome's top, on the brow, in the hot vent and at every barrel's mouth.

**Acceptance criteria**
- Given the model, then every neon and glowing vein is bright yellow (unit: enemy colour family
  tests).

*Sources: P10-R11, D-231.*

#### MB-CINDER-CRAB-06 — Arms and snapping fingers · MUST

The two arms are moving limbs on shoulder joints at 16 px either side, 14 px ahead of the centre:
each swings 9° either way once every 4.2 s, the two out of step (phases 0.2 and 0.7). Each claw's
outer finger hangs on its own joint at the wrist (24 px out, 40 px ahead), carried by its arm, and
snaps from shut to wide open, 13° either way, once every 1.5 s, the two out of step. The claws' hit
circles and palm guns move with their arms.

**Acceptance criteria**
- Given the boss is in place, then the arms swing slowly and the fingers snap faster (manual, dev
  viewer); the claws' muzzles move with the joints (unit: `test_boss_limbs.py` for the rule).

*Sources: P10-R11, D-061.*

### Behaviour

#### MB-CINDER-CRAB-07 — Entry, place and ground speed · MUST

The Crab comes in from above the top edge and stops at 0.72 of the playfield's height. In place it
sways up to 65 px either side over 7.5 s and bobs 7 px over 3.6 s. While it is fought the ground
runs at ×0.5 the level's speed.

**Acceptance criteria**
- Given the fight starts, then the ground slows to ×0.5 and the boss stops at 0.72 of the
  playfield height (unit: `test_world_boss.py` for the rule; design values in the config).

*Sources: P10-R11.*

#### MB-CINDER-CRAB-08 — Parts and health · MUST

The Crab has a core (hit radius 13 px, 2 300 HP) and three original parts: two claws (10 px, 500 HP
each) that shield the core, and the back mortar (12 px, 350 HP) that does not, so it can be shot
past the core. Its full health is 3 650 HP with the original parts, 4 450 HP with its two hidden
gatlings (400 HP each), which count in the health bar from the start.

**Acceptance criteria**
- Given the design, then it has three original parts and two hidden ones, and only the claws and
  the gatlings shield the core (unit: `test_cinder_crab.py`).

*Sources: P10-R11, D-088, D-221.*

#### MB-CINDER-CRAB-09 — Claw spreads · MUST

While they stand, in every stage, each claw fires an aimed spread of 3 `red` bullets (200 px/s, 13°
apart, the middle one at the player) every 2.6 s from its palm gun, the left one 0.8 s and the
right one 2.1 s into a stage.

**Acceptance criteria**
- Given a claw stands, then its spreads leave its palm gun, wherever its arm has swung (unit:
  design guns, joints).

*Sources: P10-R11.*

#### MB-CINDER-CRAB-10 — Mortar slag · MUST

While it stands, in every stage, the mortar lobs one slow, big ball of slag at the player every
3.2 s (`orange`, 120 px/s, radius 7 px), first 1.6 s into a stage.

**Acceptance criteria**
- Given the mortar stands, then it fires one large, slow bullet at the player every 3.2 s (unit:
  design stages).

*Sources: P10-R11.*

#### MB-CINDER-CRAB-11 — Core patterns by stage · MUST

The core fires rings from the dome on its back, a new pattern at each stage (stage k: k parts
destroyed; from the third on, its last pattern):
- stage 0: a ring of 10 `orange` bullets (205 px/s) every 3 s, turning 18° each time;
- stage 1: a ring of 12 `orange` every 2.4 s, turning 15°;
- stage 2: two alternating rings of 10 every 2.4 s, a `purple` one (195 px/s) that does not turn and
  an `orange` one turning 18°, 1.2 s apart;
- stage 3: a dense, slow-turning ring of 16 `magenta` (210 px/s) every 2.2 s, turning 6°, and a
  three-armed spiral turning the other way (rings of 3 `red` every 0.4 s, turning -27°).

**Acceptance criteria**
- Given the design, then it has one stage per original part plus one, and the last stage's spiral
  is used by no earlier stage (unit: `test_cinder_crab.py`).

*Sources: P10-R11, D-088.*

#### MB-CINDER-CRAB-12 — Rage · MUST

After the pause that follows each destroyed part, the Crab is angry: it fires a curtain (fans
sweeping across the screen and back over a ring) at heat 9.5, in `orange` and `red`: about 96
bullets a second at 196 px/s, World 4's coolest rage, going on from World 3's hottest (9).

**Acceptance criteria**
- Given a part is destroyed, when its pause is over, then the core fires the curtain for the rage
  time (unit: `test_boss_rage.py`, `test_cinder_crab.py`).

*Sources: D-088, D-063.*

#### MB-CINDER-CRAB-13 — Transformation: flank armour bursts off · MUST

The Crab transforms once, when 2 of its 3 original parts are destroyed. Its flank plating bursts
off ([common](../common.md), BOSS-42): a wedge of banded shell drawn as a piece of its own either
side of the carapace, from the chine (2.2–3.6 px high) up the carapace's slope to the edge of its
flat top (4–12 px, the top's edge at 0.6 of the carapace's half width), resting on a low skirt of
the body, with the orange neon stripe along its slope. Its region (`flanks`, mirrored) follows the
carapace's stations, from the edge of the top out to the chine, tail to front; the plating bursts
into its six bands a side and leaves a `wing` frame (ribs across and two spars) on the skirt. The
gatlings lie folded under it; the legs stay on the body's skirt.

**Acceptance criteria**
- Given two original parts are destroyed, then the boss transforms once and its flank regions burst
  off, leaving the wing frames (unit: `test_boss_kinds.py`, `test_boss_armour.py`).
- Given its model, then it draws the flank region's armour and its twelve pieces, and it holds
  together with and without it (unit: `test_boss_armour.py`, `test_boss_model.py`).

*Sources: D-221, D-224, D-227, D-254.*

#### MB-CINDER-CRAB-14 — Hidden weapons: two gatlings · MUST

The transformation reveals two gatling turrets on the bared flanks, 28 px either side of the centre
and 21 px behind it (radius 8 px, pods 11.7 px high, 400 HP each, 30 % drop chance). They shield the
core and fire `red` bursts as every gatling does (see [common](../common.md)), following the player,
the left one 1.2 s and the right one 2.0 s into a stage. The Crab fires more once it has transformed
(about 6 weighted shots a second before, 12 after).

**Acceptance criteria**
- Given the transformation is over, then both gatlings are live targets that fire, and the boss's
  fire rate has gone up (unit: `test_boss_kinds.py` escalation and weapon checks).

*Sources: D-221, D-229.*

#### MB-CINDER-CRAB-15 — Points and drops · MUST

Destroying the Crab scores 8 000 points, and each part destroyed 800. Its original parts drop a
bonus half of the time, its hidden weapons 30 % of the time; its core drops one by the game's rule.

**Acceptance criteria**
- Given a claw is destroyed, then the score rises by 800 (unit: scoring rule, design values).

*Sources: P07-R07, P11-R01, D-088.*

## Tunable values

All in `src/game/config/bosses/world_4/cinder_crab.py` (`CINDER_CRAB`) unless noted.

| Name | Value | Notes |
|------|-------|-------|
| level | 4-1, mini | `src/game/config/world_4/bosses.py` `WORLD_4_BOSSES` |
| size | 3 L (radius 51 px) | `stats.size` |
| core | radius 13 px, 2 300 HP | `coreRadius`, `coreHealth` |
| claws | (±24, -36), radius 10, 500 HP, shield | `CRAB_ARM.claw` |
| mortar | (0, 24), radius 12, 350 HP, no shield | `CRAB_MORTAR_AT` |
| full health | 3 650 (4 450 with hidden weapons) | D-088 |
| stop / sway / bob | 0.72 / 65 px, 7.5 s / 7 px, 3.6 s | `stopFraction`, `sway`, `bob` |
| ground speed | ×0.5 | `groundSpeed` |
| arms | shoulders (±16, -14); ±9°, 4.2 s, phases 0.2 / 0.7 | `CRAB_ARM`, `CRAB_SWING` |
| fingers | wrists (±24, -40); ±13°, 1.5 s, phases 0 / 0.5 | `CRAB_SWING` |
| muzzles | palm guns (±24, -52, 4.5), mortar (0, 15, 17), dome (0, -2, 15.5) | `CRAB_PALM_GUN`, `CRAB_MORTAR`, `CRAB_DOME` |
| claw spreads | 3 × 13°, every 2.6 s, first 0.8 / 2.1 s | stage volleys |
| mortar slag | 1, every 3.2 s, first 1.6 s; 120 px/s, radius 7 | `SLAG` |
| bullets | `orange` 205, `red` 200, `purple` 195, `magenta` 210 px/s | radius 4 |
| rage | curtain, heat 9.5 (`orange`, `red`) | `rage.curtain`; `src/game/config/bosses/boss_rage.py` |
| transformation | once, at 2 original parts destroyed | `src/game/sim/boss_build.py` `default_transforms` |
| flank regions | the carapace's flanks (mirrored) from 0.6 of its half width to its chine, station by station (x 7.2..12 at y -24, 28.8..48 at y -2, 8.4..14 at y 32), `wing`; plating from the chine (2.2–3.6 px) to the top (4–12 px) | `armour_region("flanks", …)`; `src/game/view/bosses/world_4/cinder_crab_armour.py` |
| gatlings | (±28, 21), radius 8, pod 11.7, 400 HP, `red`, first 1.2 / 2.0 s | `hidden_weapon`; volleys in `src/game/config/bosses/weapon_kinds.py` |
| drops | parts 0.5, hidden weapons 0.3 | `part`, `hidden_weapon` defaults |
| points | 8 000 (800 a part) | `points`, `src/game/config/scoring.py` `boss_part_points` |
| neon | [1, 0.45, 0.05], drawn [1, 1, 0.05] | `src/game/config/boss_look.py` `BOSS_LOOK.neon["cinder-crab"]` |

## Notes

- Phase 10 fight time with the D-055 bot (guns level 3, always on target): 44.4 s, before the hidden
  weapons were added (D-221). The claws were placed at ±24 px so that the bot's spread reaches them
  within the health band (as D-081). The bot seldom destroys the mortar, behind the core (D-088); a
  player can still shoot it.
- Its full health takes its place in World 4's boss ordering (P10-R12, see
  [World 4](../../worlds/world-4/world.md)).
