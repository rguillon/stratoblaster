# Geyser Rig (4-2 final boss)

> **Area:** bosses · **Prefix:** `FB-GEYSER-RIG` · **Related:** [common boss rules](../common.md),
> [4-2 Inner town](../../worlds/world-4/4-2-inner-town.md), [World 4](../../worlds/world-4/world.md),
> [Ash Wraith](../mini/4-2-ash-wraith.md), [Hornet](../../enemies/hornet.md),
> [readability](../../graphics/readability.md)

The Geyser Rig is the final boss of level 4-2, met at the end of the level. It is a flying drilling
rig 5 L long: a heavy deck with a lattice derrick in its middle (the core), two drill heads on arms
reaching forward from its bow corners and swinging as if boring, two steam vents at its stern, a
drone hangar jutting from its bow and a squat cooling tower aft. It was designed for the Volcanic
Lands' ash plains; since World 4 became the Metropolis (D-112) it keeps its name and its look and
flies over the inner town. It transforms twice: its back plating bursts off for two missile racks,
then its wing armour for two ring emitters. Everything shared by all bosses is in
[bosses/common.md](../common.md); this file only gives what is the Rig's own. Positions are px from
the boss's centre, X right, Y up the screen (its bow at -Y); heights are above the playfield.

## Requirements

### Look

#### FB-GEYSER-RIG-01 — Silhouette · MUST

Seen from above, the Rig is a drilling platform about 5 L long (radius 2.5 L), bow down the screen:
a deck about 88 px wide and 108 px long, its stern corners cut, the derrick standing about 42 px
high in its middle, the drill arms reaching forward from the bow corners to the drill heads about
62 px ahead of the centre and 50 px either side, the hangar jutting from the bow between them, the
two steam vents at the stern corners and the cooling tower aft.

**Acceptance criteria**
- Given the dev bosses viewer, when the Rig is shown, then it reads as a flying drilling rig with a
  derrick, two drills in front and two vents behind (manual).

*Sources: P10-R11.*

#### FB-GEYSER-RIG-02 — Cyber-Organic body · MUST

It is a living rock-tick (Cyber-Organic): its back a scorched flesh shell veined molten, bone ribs
across it, glowing glands, a spire of bone braced by sinews standing as the derrick's four posts
over its core. Metal is grafted on as its drills, pipes and guns: worn deck plates a little proud of
the deck, hazard paint, a pipe rack along each side (two pipes on trestles and a valve wheel), the
drill floor's gun house at the derrick's foot with its twin fan guns pointing forward, the derrick's
crown block and the drill pipe glowing hot down its middle, and the cooling tower (a squat flared
stack, hot metal glowing in its mouth, ash on its rim). Ash drifts and soot lie on the deck.

**Acceptance criteria**
- Given the model, then it reads as one creature with a rig grafted on, not as parts stuck on a box
  (manual).

*Sources: P10-R11, P16-R06.*

**Discrepancy:** P16-R06 asks for the world's theme to stay recognisable ("a metropolis boss feels
like a city-sized organism"); the model keeps the volcanic industry theme of its design (D-112 left
the World 4 bosses unchanged) and nothing in it reads as a city.

#### FB-GEYSER-RIG-03 — Drill arms and drill heads · MUST

Each drill arm is a heavy metal boom on its shoulder joint, a ram along it and a neon line, carrying
the drill head at its end: a ribbed motor housing, a long fluted bit glowing hot at its root and
reaching about 28 px ahead of the head, and the gun on top of the housing beside the bit. The
booms belong to the body (they flash with the core). A destroyed drill head is hidden and leaves
nothing in its place; its boom stays, still swinging.

**Acceptance criteria**
- Given the dev viewer, when K destroys a drill head, then the head disappears and its boom stays
  (manual; `test_boss_models.py` checks every part is drawn).

*Sources: P10-R11, P16-R06, D-225, D-167.*

#### FB-GEYSER-RIG-04 — Steam vents · MUST

Each steam vent is a scorched stack rising from a valve block on the stern, its flared mouth ringed
with neon, hot metal glowing in it, ash settled round its foot. Destroyed, a vent is hidden and
leaves nothing in its place.

**Acceptance criteria**
- Given the model, then each vent's mouth sits at its muzzle, 24 px high (unit:
  `test_boss_models.py`; manual).

*Sources: P10-R11, P16-R06, D-225.*

#### FB-GEYSER-RIG-05 — Drone hangar · MUST

The hangar is a brood sac of flesh jutting from the bow, its open door framed in metal and neon,
where its Hornets leave from, glowing glands on its top, warning lamps either side, a vent and ash
on its roof. Destroyed, it is hidden and leaves nothing in its place.

**Acceptance criteria**
- Given the model, then the hangar's door faces down the screen at the bow (manual).

*Sources: P10-R11, P16-R06, D-225.*

#### FB-GEYSER-RIG-06 — Lights and colours · MUST

Its registered neon is yellow (`geyser-rig`), drawn bright yellow as every boss's warm lights (see
[readability](../../graphics/readability.md)). Neon runs along the deck's sides, the drill arms, the
vents' mouths, the hangar's door and the derrick's crown; its molten veins, the hot drill pipe and
bits and the glowing mouths are in the same yellow family. White charge lights sit at the barrels'
mouths and in the vents.

**Acceptance criteria**
- Given the model, then every neon and glowing vein is bright yellow (unit: enemy colour family
  tests).

*Sources: P10-R11, D-231.*

#### FB-GEYSER-RIG-07 — Boring arms · MUST

The two drill arms are moving limbs on shoulder joints on the deck, 30 px either side and 26 px
ahead of the centre (12 px high): each swings 13° either way once every 3.6 s, the two half a swing
out of step, as if boring. The drill heads' hit circles and guns move with their arms.

**Acceptance criteria**
- Given the boss is in place, then the drills swing in turn (manual, dev viewer); their muzzles move
  with the joints (unit: `test_boss_build.py` joints).

*Sources: P10-R11, D-061.*

### Behaviour

#### FB-GEYSER-RIG-08 — Entry, place and ground speed · MUST

The Rig comes in from above the top edge and stops at 0.74 of the playfield's height. In place it
sways up to 30 px either side over 11 s and bobs 5 px over 5.5 s. While it is fought the ground runs
at ×0.4 the level's speed.

**Acceptance criteria**
- Given the fight starts, then the ground slows to ×0.4 and the boss stops at 0.74 of the
  playfield height (unit: `test_world_boss.py` for the rule; design values in the config).

*Sources: P10-R11.*

#### FB-GEYSER-RIG-09 — Parts and health · MUST

The Rig has a core (hit radius 22 px, 3 900 HP) and five original parts: two drill heads (14 px,
1 300 HP each) and two steam vents (13 px, 1 150 HP each), the four shielding the core, and the
drone hangar (14 px, 900 HP) that does not; hanging in front of the core, the hangar can always be
shot. Its full health is 9 700 HP with the original parts, 14 380 HP with its four hidden weapons,
which count in the health bar from the start.

**Acceptance criteria**
- Given the design, then it has five original parts and four hidden ones, and the hangar is the only
  original part that does not shield the core (unit: `test_geyser_rig.py`).

*Sources: P10-R11, D-088, D-221.*

#### FB-GEYSER-RIG-10 — Drill bursts · MUST

While they stand, in every stage, each drill head fires a burst of 4 `red` bullets (210 px/s,
0.12 s apart) at the player every 3.2 s from the gun on its housing, the left one 1 s and the right
one 2.6 s into a stage.

**Acceptance criteria**
- Given a drill head stands, then its bursts leave its gun, wherever its arm has swung (unit: design
  guns, joints).

*Sources: P10-R11.*

#### FB-GEYSER-RIG-11 — Steam vent spirals · MUST

While they stand, in every stage, each vent fires a three-armed spiral from its stack's top (rings
of 3 `orange` bullets, 200 px/s, every 0.8 s), the two turning opposite ways (17° and -17° each
time), the left one 0.6 s and the right one 1 s into a stage.

**Acceptance criteria**
- Given both vents stand, then their spirals turn opposite ways (unit: design stages).

*Sources: P10-R11.*

#### FB-GEYSER-RIG-12 — Hornets from the hangar · MUST

While it stands, in every stage, the hangar launches 2 [Hornets](../../enemies/hornet.md) every
7 s, first 3.5 s into a stage.

**Acceptance criteria**
- Given the hangar stands, then two Hornets come out of it every 7 s; once it is destroyed, none
  (unit: launches in `world_boss.py`).

*Sources: P10-R11.*

#### FB-GEYSER-RIG-13 — Core fans by stage · MUST

The core fires fans from the twin guns at the derrick's foot, a new pattern at each stage (stage k:
k parts destroyed; from the fifth on, its last pattern):
- stage 0: a fan of 3 `purple` bullets (195 px/s, 16° apart) every 2.6 s;
- stage 1: a fan of 5 `purple` (14° apart) every 2.4 s;
- stage 2: two fans of 4 `magenta` (205 px/s, 12° apart) every 2.6 s, one leaning 18° left and one
  18° right, 1.3 s apart;
- stage 3: a fan of 7 `purple` (12° apart) every 2.3 s;
- stage 4: a fan of 9 `magenta` (10° apart) every 2.4 s and a quick fan of 3 `red` (210 px/s, 6°
  apart) every 1.2 s;
- stage 5: five fans of 5 `magenta` (9° apart) at -30°, -15°, 0°, 15° and 30°, every 3 s, each 0.6 s
  after the one before, so they sweep across the screen, used by no earlier stage.

**Acceptance criteria**
- Given the design, then it has one stage per original part plus one, and the last stage's sweeping
  fans are used by no earlier stage (unit: `test_geyser_rig.py`).

*Sources: P10-R11, D-088.*

#### FB-GEYSER-RIG-14 — Rage · MUST

It is angry after each of its transformations, when the weapons that one revealed
fire all out: the two missile racks after the first, the two ring emitters after the second.
For `boss_rage_seconds` it fires only those, `boss_rage_rate` times as often, instead of its
stage's pattern ([common](../common.md), BOSS-27). A lost part no longer angers it, and it
has no angry pattern of its own.

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only the weapons it revealed
  (unit: `test_boss_build.py` angry_pattern).
- Given a part is destroyed without a transformation, then it is not angry (unit test).

*Sources: D-088, D-063, D-256.*

#### FB-GEYSER-RIG-15 — First transformation: back plating bursts off · MUST

The Rig transforms a first time when 2 of its 5 original parts are destroyed. Its back plating
bursts off: a piece of the model's own ([common](../common.md), BOSS-42), a plate of scorched hide
lying on the deck across the centre line, 27 px either side, from 26 px to 70 px behind the centre
(the deck's stern edge), 7 to 8.5 px high, clear of the steam vents' valve blocks; on it the
cooling tower, two bone ribs arching over it, two glands, two worn deck plates, ash drifts, soot
streaks and the molten veins' stern runs. It bursts into plates cracked from its outline at its own
height. Under it the flat deck and a dark metal `shell` frame (a lattice) show. The missile racks
lie folded under it. The boss stays one object after it.

**Acceptance criteria**
- Given two original parts are destroyed, then the boss transforms and its back region bursts off,
  leaving the shell frame (unit: `test_boss_kinds.py`, `test_boss_armour.py`).
- Given the boss after its first transformation, then nothing of it hangs in the air (unit:
  `test_d227_the_boss_holds_together_in_every_state`).

*Sources: D-221, D-224, D-227, D-254.*

#### FB-GEYSER-RIG-16 — First hidden weapons: two missile racks · MUST

The first transformation reveals two missile racks on the bared back, 13 px either side of the
centre line and 57 px behind the centre (radius 11 px, pods 12.4 px high, 1 040 HP each, 30 % drop
chance). They shield the core and fire homing missiles as every rack does (see
[common](../common.md)), the left one 1.2 s and the right one 2.0 s into a stage.

**Acceptance criteria**
- Given the first transformation is over, then both racks are live targets that fire (unit:
  `test_boss_kinds.py` weapon checks).

*Sources: D-221, D-229.*

#### FB-GEYSER-RIG-17 — Second transformation: wing armour bursts off · MUST

The Rig transforms a second time when 4 of its 5 original parts are destroyed. Its wing armour
bursts off: a plate of scorched hide either side, a piece of the model's own ([common](../common.md),
BOSS-42), lying on the deck from 14 px to 41 px out (inset from the deck's edge so the yellow
strip along it stays in sight), from 37 px ahead of the centre to 4 px behind it, its bow corner
cut as the deck's is (from (29, -37) to (41, -28)), 7 to 8.5 px high; on it the pipe rack (its
stern trestle standing on the deck behind the plate), the hazard paint, a molten seam, a worn deck
plate and an ash drift. It bursts into plates cracked from its outline at its own height. Under
each the flat deck and a dark metal `wing` frame (ribs across and two spars) show. The ring
emitters lie folded under them. The boss stays one object after it.

**Acceptance criteria**
- Given four original parts are destroyed, then the boss transforms a second time and its wing
  regions burst off (unit: `test_boss_kinds.py`, `test_boss_armour.py`).
- Given the boss after its second transformation, then nothing of it hangs in the air (unit:
  `test_d227_the_boss_holds_together_in_every_state`).

*Sources: D-221, D-224, D-227, D-254.*

#### FB-GEYSER-RIG-18 — Second hidden weapons: two ring emitters · MUST

The second transformation reveals two ring emitters (orbs) on the bared wings, 33 px either side of
the centre and 29 px ahead of it (radius 11 px, pods 12.4 px high, 1 300 HP each, 30 % drop chance).
They shield the core and fire `red` rings as every orb does (see [common](../common.md)), the left
one 1.2 s and the right one 2.0 s into a stage. Its fire goes up at each transformation (about 11.7,
then 12.5, then 15.9 weighted shots a second). Unlike the other World 4 final bosses it reveals no
third, centre weapon (D-221 adds one only where there is room).

**Acceptance criteria**
- Given the second transformation is over, then both orbs are live targets that fire, of a kind not
  revealed at the first (unit: `test_boss_kinds.py`).

*Sources: D-221, D-229.*

#### FB-GEYSER-RIG-19 — Points and drops · MUST

Destroying the Rig scores 16 000 points, and each part destroyed 1 600. Its original parts drop a
bonus 60 % of the time, its hidden weapons 30 %, and its core always drops one.

**Acceptance criteria**
- Given a vent is destroyed, then the score rises by 1 600 (unit: scoring rule, design values).

*Sources: P07-R07, P11-R01, D-088.*

## Tunable values

All in `src/game/config/bosses/world_4/geyser_rig.py` (`GEYSER_RIG`) unless noted.

| Name | Value | Notes |
|------|-------|-------|
| level | 4-2, final | `src/game/config/world_4/bosses.py` `WORLD_4_BOSSES` |
| size | 5 L (radius 85 px) | `stats.size` |
| core | radius 22 px, 3 900 HP | `coreRadius`, `coreHealth` |
| drill heads | (±50, -62), radius 14, 1 300 HP, shield, on their arms | `RIG_DRILL` |
| steam vents | (±35, 30), radius 13, 1 150 HP, shield | `RIG_VENT` |
| hangar | (0, -50), radius 14, 900 HP, no shield | `RIG_HANGAR` |
| full health | 9 700 (14 380 with hidden weapons) | D-088 |
| stop / sway / bob | 0.74 / 30 px, 11 s / 5 px, 5.5 s | `stopFraction`, `sway`, `bob` |
| ground speed | ×0.4 | `groundSpeed` |
| arms | shoulders (±30, -26), 12 high; ±13°, 3.6 s, phases 0 / 0.5 | `RIG_SHOULDER`, `BORE`, `DRILL_HEIGHT` |
| muzzles | drill guns (±50, -76, 14), vent tops (±35, 30, 24), core guns (±10, -24, 10) | `RIG_*` |
| drill bursts | 4, 0.12 s apart, every 3.2 s, first 1 / 2.6 s | stage volleys |
| vent spirals | rings of 3, every 0.8 s, turn ±17°, first 0.6 / 1 s | stage volleys |
| hangar | 2 Hornets every 7 s, first 3.5 s | `launches` |
| bullets | `red` 210, `orange` 200, `magenta` 205, `purple` 195 px/s | radius 4 |
| angry | the revealed weapons, BOSS-27 | `boss_build.angry_pattern` |
| transformations | at 2, then 4 original parts destroyed | `src/game/sim/boss_build.py` `default_transforms` |
| back region | x -27..27, y 26..70, `shell`, not mirrored; plating 7–8.5 px, the cooling tower on it | form 1, `geyser_rig_armour.py` |
| wing regions | (14, -37), (29, -37), (41, -28), (41, 4), (14, 4) (mirrored), `wing`; plating 7–8.5 px, the pipe racks on it | form 2 |
| racks | (±13, 57), radius 11, pod 12.4, 1 040 HP, first 1.2 / 2.0 s | form 1 |
| orbs | (±33, -29), radius 11, pod 12.4, 1 300 HP, `red`, first 1.2 / 2.0 s | form 2 |
| drops | parts 0.6, hidden weapons 0.3, core 1 | `fpart`, `coreDrop` |
| points | 16 000 (1 600 a part) | `points`, `boss_part_points` |
| neon | [1, 0.88, 0.1], drawn [1, 1, 0.1] | `src/game/config/boss_look.py` `BOSS_LOOK.neon["geyser-rig"]` |

## Notes

- Phase 10 fight time with the D-055 bot: 100.7 s, before the hidden weapons (D-221). The vents were
  placed at ±35 px for the bot's spread (as D-081).
- Its full health takes its place in World 4's boss ordering (P10-R12, see
  [World 4](../../worlds/world-4/world.md)).
