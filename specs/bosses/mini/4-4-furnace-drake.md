# Furnace Drake (4-4 mini boss)

> **Area:** bosses · **Prefix:** `MB-FURNACE-DRAKE` · **Related:** [common boss rules](../common.md),
> [4-4 Business district](../../worlds/world-4/4-4-business-district.md),
> [World 4](../../worlds/world-4/world.md), [Foundry Ark](../final/4-4-foundry-ark.md),
> [readability](../../graphics/readability.md)

The Furnace Drake is the mini boss of level 4-4, met at the middle of the level. It is a
dragon-shaped gunship 3.5 L across: a heavy armoured torso with a furnace glowing through a grate in
its back, two beating wings with a gun pod under each, a horned head on a swaying neck that breathes
a short flame of dense bullets, and a long spiked tail lashing behind. It was designed for the
Volcanic Lands' forge belt; since World 4 became the Metropolis (D-112) it keeps its name and its
look and flies over the business district. It transforms once: its back plating bursts off and two
heavy cannons unfold. Everything shared by all bosses is in [bosses/common.md](../common.md); this
file only gives what is the Drake's own. Positions are px from the boss's centre, X right, Y up the
screen (its head at -Y); heights are above the playfield.

## Requirements

### Look

#### MB-FURNACE-DRAKE-01 — Silhouette · MUST

Seen from above, the Drake is a dragon about 3.5 L across (radius 1.75 L), head down the screen: two
broad scalloped wings spanning about 118 px, a heavy torso about 26 px wide between them, its head on
a neck reaching about 57 px ahead of the centre (its open maw), and a long tapering tail reaching
about 57 px behind it. Four short clawed legs are folded under the torso.

**Acceptance criteria**
- Given the dev bosses viewer, when the Drake is shown, then it reads as a dragon with beating wings,
  a horned head and a long tail (manual).

*Sources: P10-R11.*

#### MB-FURNACE-DRAKE-02 — Cyber-Organic body · MUST

It is a living dragon (Cyber-Organic): its flesh torso ribbed in bone, magma veins under its hide,
bone spines down its back and claws on its folded legs, soot-black plates with molten seams between
them, and a furnace heart grafted in its back, its grate (a lathe dome) glowing as its next spiral
charges. The tail is a tapering spiked whip, spikes down its back and a glowing blade at its tip.

**Acceptance criteria**
- Given the model, then it reads as one creature with a furnace in its back (manual).

*Sources: P10-R11, P16-R05.*

#### MB-FURNACE-DRAKE-03 — Wings · MUST

Each wing is a scalloped membrane of dark, heat-stained hide stretched over heavy bones (three thick
ones out from the shoulder, finer ones to each scallop), molten seams lit along the bones, and under
it a gun pod with the two barrels of its fans. Destroyed, a wing is hidden and leaves nothing in its
place.

**Acceptance criteria**
- Given the dev viewer, when K destroys a wing, then the wing and its pod disappear (manual;
  `test_boss_models.py` checks every part is drawn).

*Sources: P10-R11, P16-R05, D-225, D-167.*

#### MB-FURNACE-DRAKE-04 — Head and jaw · MUST

The jaw part is the drake's head on its neck: the neck and the skull, horns swept back, red eyes, an
open lower jaw with its teeth, the maw glowing as the flame charges and the flame nozzle in its
throat. Destroyed, the head is hidden and leaves nothing in its place.

**Acceptance criteria**
- Given the model, then the flame nozzle sits at its muzzle in the open maw (unit:
  `test_boss_models.py`; manual).

*Sources: P10-R11, P16-R05, D-225.*

#### MB-FURNACE-DRAKE-05 — Lights and colours · MUST

Its registered neon is red (`furnace-drake`) with orange molten seams and flame; like every boss's
warm lights they are drawn bright yellow (see [readability](../../graphics/readability.md)). The
molten seams of its plates and wings, its magma veins, the tail's blade, the eyes and the furnace
heart glow in that yellow family. White charge lights sit at the barrels' mouths, in the maw and in
the heart's grate.

**Acceptance criteria**
- Given the model, then every neon and glowing seam is bright yellow (unit: enemy colour family
  tests).

*Sources: P10-R11, D-231.*

#### MB-FURNACE-DRAKE-06 — Beating wings, swaying neck, lashing tail · MUST

The two wings are moving limbs on joints at their roots (12 px either side, 2 px ahead of the
centre): they beat together, mirrored, 13° either way once every 1.3 s, a wide stroke as a bird's.
The head sways on its neck joint (18 px ahead of the centre) 9° either way once every 3.4 s. The tail
is a limb of the body on its joint at the hips (20 px behind the centre), lashing 12° either way once
every 2.6 s, out of step with the neck. The wings' and the head's hit circles and muzzles move with
their joints.

**Acceptance criteria**
- Given the boss is in place, then the wings beat, the head sways and the tail lashes (manual, dev
  viewer); the muzzles move with the joints (unit: joint rule).

*Sources: P10-R11, D-061.*

### Behaviour

#### MB-FURNACE-DRAKE-07 — Entry, place and ground speed · MUST

The Drake comes in from above the top edge and stops at 0.74 of the playfield's height. In place it
sways up to 60 px either side over 6.4 s and bobs 8 px over 2.9 s. While it is fought the ground runs
at ×0.5 the level's speed.

**Acceptance criteria**
- Given the fight starts, then the ground slows to ×0.5 and the boss stops at 0.74 of the playfield
  height (unit: `test_world_boss.py` for the rule; design values in the config).

*Sources: P10-R11.*

#### MB-FURNACE-DRAKE-08 — Parts and health · MUST

The Drake has a core (hit radius 16 px, 2 150 HP) and three original parts: two wings (14 px,
1 100 HP each, their centres at their gun pods) that shield the core, and the jaw (11 px, 800 HP)
that does not; hanging in front of the core, the head can always be shot. Its full health is
5 150 HP with the original parts, 6 910 HP with its two hidden cannons (880 HP each), which count in
the health bar from the start.

**Acceptance criteria**
- Given the design, then it has three original parts and two hidden ones, and only the wings and the
  cannons shield the core (unit: `test_furnace_drake.py`).

*Sources: P10-R11, D-088, D-221.*

#### MB-FURNACE-DRAKE-09 — Wing fans · MUST

While they stand, in every stage, each wing fires a fan of 3 `red` bullets (215 px/s, 14° apart)
every 2.4 s from its pod's two barrels, leaning outwards (the left one 12° to the left of straight
down, the right one 12° to the right), one after the other on the down strokes: the left one 0.9 s
and the right one 2.1 s into a stage.

**Acceptance criteria**
- Given both wings stand, then their fans lean away from each other (unit: design stages).

*Sources: P10-R11.*

#### MB-FURNACE-DRAKE-10 — Jaw flame · MUST

While it stands, in every stage, the jaw breathes a short flame at the player every 3.2 s from its
nozzle: a burst of 9 small, fast sparks (`orange`, 240 px/s, radius 3 px, 0.045 s apart) and, 0.2 s
later, an aimed spray of 4 slower ones round it (`red`, 215 px/s, radius 3 px, 9° apart); first 1.6 s
into a stage.

**Acceptance criteria**
- Given the jaw stands, then its flame is a dense stream of small bullets at the player and a spray
  round it (unit: design stages).

*Sources: P10-R11.*

#### MB-FURNACE-DRAKE-11 — Core spirals by stage · MUST

The core fires spirals from the furnace heart on its back, a new one at each stage (stage k: k parts
destroyed; from the third on, its last pattern):
- stage 0: a three-armed spiral (rings of 3 `orange`, 210 px/s, every 0.5 s, turning 17°);
- stage 1: a four-armed spiral the other way (rings of 4 `orange` every 0.48 s, turning -21°);
- stage 2: a five-armed spiral (rings of 5 `purple`, 205 px/s, every 0.46 s, turning 25°);
- stage 3: twin spirals turning opposite ways (rings of 5 `orange` turning 14° and rings of 6 `red`
  turning -16°, every 0.44 s), used by no earlier stage.

**Acceptance criteria**
- Given the design, then it has one stage per original part plus one, and the last stage's twin
  spirals are used by no earlier stage (unit: `test_furnace_drake.py`).

*Sources: P10-R11, D-088.*

#### MB-FURNACE-DRAKE-12 — Rage · MUST

After the pause that follows each destroyed part, the Drake is angry: it fires a flower (a dense,
slowly turning ring and small aimed fans) at heat 12.5, in `orange` and `red`: about 120 bullets a
second at 220 px/s.

**Acceptance criteria**
- Given a part is destroyed, when its pause is over, then the core fires the flower for the rage time
  (unit: `test_boss_rage.py`, `test_furnace_drake.py`).

*Sources: D-088, D-063.*

#### MB-FURNACE-DRAKE-13 — Transformation: back plating bursts off · MUST

The Drake transforms once, when 2 of its 3 original parts are destroyed. Its back plating bursts
off: one region across the centre line, 26 px either side, from 20 px ahead of the centre to 24 px
behind it, above 2 px high. Under it a dark metal `shell` frame (a lattice) shows. The boss stays one
object at rest and after its transformation.

**Acceptance criteria**
- Given two original parts are destroyed, then the boss transforms once and its back region bursts
  off, leaving the shell frame (unit: `test_boss_kinds.py`, `test_boss_armour.py`).
- Given the boss at rest and after its transformation, then nothing of it hangs in the air (unit:
  `test_d227_the_boss_holds_together_in_every_state`).

*Sources: D-221, D-224, D-227.*

#### MB-FURNACE-DRAKE-14 — Hidden weapons: two heavy cannons · MUST

The transformation reveals two heavy cannons on the bared back, 11 px either side of the centre line
and 7 px behind the centre (radius 7 px, pods 13.2 px high, 880 HP each, 30 % drop chance). They
shield the core and fire `red` spreads of large, slow shells at the player as every cannon does (see
[common](../common.md)), turning to aim; the left one 1.2 s and the right one 2.0 s into a stage. The
Drake fires more once it has transformed (about 12.6 weighted shots a second before, 17.4 after).

**Acceptance criteria**
- Given the transformation is over, then both cannons are live targets that fire, and the boss's
  fire rate has gone up (unit: `test_boss_kinds.py` escalation and weapon checks).

*Sources: D-221, D-229.*

#### MB-FURNACE-DRAKE-15 — Points and drops · MUST

Destroying the Drake scores 8 500 points, and each part destroyed 850. Its original parts drop a
bonus half of the time, its hidden weapons 30 % of the time; its core drops one by the game's rule.

**Acceptance criteria**
- Given a wing is destroyed, then the score rises by 850 (unit: scoring rule, design values).

*Sources: P07-R07, P11-R01, D-088.*

## Tunable values

All in `src/game/config/bosses/world_4/furnace_drake.py` (`FURNACE_DRAKE`) unless noted.

| Name | Value | Notes |
|------|-------|-------|
| level | 4-4, mini | `src/game/config/world_4/bosses.py` `WORLD_4_BOSSES` |
| size | 3.5 L (radius 59.5 px) | `stats.size` |
| core | radius 16 px, 2 150 HP | `coreRadius`, `coreHealth` |
| wings | (±40, 2), radius 14, 1 100 HP, shield, on their joints | `DRAKE_WING.pod` |
| jaw | (0, -38), radius 11, 800 HP, no shield, on the neck | `DRAKE_JAW` |
| full health | 5 150 (6 910 with hidden weapons) | D-088 |
| stop / sway / bob | 0.74 / 60 px, 6.4 s / 8 px, 2.9 s | `stopFraction`, `sway`, `bob` |
| ground speed | ×0.5 | `groundSpeed` |
| wing beat | roots (±12, 2); ±13°, 1.3 s, together | `DRAKE_WING.root`, `BEAT` |
| neck sway | (0, -18); ±9°, 3.4 s, phase 0.1 | `DRAKE_NECK`, `SWAY` |
| tail lash | (0, 20); ±12°, 2.6 s, phase 0.6 | `DRAKE_TAIL`, `LASH` |
| muzzles | wing barrels (±40 ∓ 2.6, -13, 2), maw (0, -57, 4), heart (0, 4, 14) | `DRAKE_*` |
| wing fans | 3 × 14°, every 2.4 s, lean ±12° outwards, first 0.9 / 2.1 s | stage volleys |
| flame | burst 9 × 0.045 s (240 px/s) + spray 4 × 9° (215 px/s), radius 3, every 3.2 s, first 1.6 s | `flame`, `FLAME`, `FLAME_EDGE` |
| bullets | `red` 215, `orange` 210, `purple` 205 px/s | radius 4 |
| rage | flower, heat 12.5 (`orange`, `red`) | `rage.flower` |
| transformation | once, at 2 original parts destroyed | `src/game/sim/boss_build.py` `default_transforms` |
| back region | x -26..26, y -20..24, above 2.0 px, `shell` | `armour_region("back", …)` |
| cannons | (±11, 7), radius 7, pod 13.2, 880 HP, `red`, first 1.2 / 2.0 s | `hidden_weapon`; volleys in `src/game/config/bosses/weapon_kinds.py` |
| drops | parts 0.5, hidden weapons 0.3 | `part`, `hidden_weapon` defaults |
| points | 8 500 (850 a part) | `points`, `boss_part_points` |
| neon | [1, 0.22, 0.05], drawn [1, 1, 0.05] | `src/game/config/boss_look.py` `BOSS_LOOK.neon["furnace-drake"]` |

## Notes

- Phase 10 fight time with the D-055 bot: 56.3 s, before the hidden weapons (D-221).
- The flame is a burst plus a spray: the engine has no stream shape (phase 10 report).
- Its full health takes its place in World 4's boss ordering (P10-R12, see
  [World 4](../../worlds/world-4/world.md)).
