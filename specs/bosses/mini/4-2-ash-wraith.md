# Ash Wraith (4-2 mini boss)

> **Area:** bosses · **Prefix:** `MB-ASH-WRAITH` · **Related:** [common boss rules](../common.md),
> [4-2 Inner town](../../worlds/world-4/4-2-inner-town.md), [World 4](../../worlds/world-4/world.md),
> [Geyser Rig](../final/4-2-geyser-rig.md), [readability](../../graphics/readability.md),
> [shots](../../graphics/shots.md)

The Ash Wraith is the mini boss of level 4-2, met at the middle of the level, and World 4's first
chase: the ground speeds up under it. It is a ragged grey stealth gunship 3 L across, a thin flying
wing torn at its trailing edge, trailing ash, with two shroud pods on its wings and an eye cannon on
its nose. It was designed for the Volcanic Lands' ash plains; since World 4 became the Metropolis
(D-112) it keeps its name and its look and chases over the inner town. It transforms once: its back
plating bursts off and two laser lances unfold. It is the one World 4 boss whose lights are green.
Everything shared by all bosses is in [bosses/common.md](../common.md); this file only gives what is
the Wraith's own. Positions are px from the boss's centre, X right, Y up the screen (its nose at
-Y); heights are above the playfield.

## Requirements

### Look

#### MB-ASH-WRAITH-01 — Silhouette · MUST

Seen from above, the Wraith is a sharp delta flying wing about 3 L across (radius 1.5 L), nose down
the screen: about 102 px from tip to tip and 80 px from its nose to its trailing edge, which is torn
into ragged points as if it had flown through fire. A low faceted fuselage runs down its middle, a
shroud pod sits on each wing 36 px out, and the eye cannon hangs under its nose. It is thin: the
wing is about 3 px thick, the fuselage about 10 px high.

**Acceptance criteria**
- Given the dev bosses viewer, when the Wraith is shown, then it reads as a ragged stealth wing with
  two pods and an eye on its nose (manual).

*Sources: P10-R11.*

#### MB-ASH-WRAITH-02 — Cyber-Organic body · MUST

It is a living ash ray (Cyber-Organic): its wing a scorched membrane of dark flesh veined with glowing
veins, its fuselage flesh under bone ribs, a dark canopy over its spine; metal only on its grafts
(vents, scorched plates by the engines, the guns, the reactors set in flesh sacs). Ash lies on it:
drifts of pale grey ash on the wing, soot streaks across it, molten seams on its plates, and grey
flakes of ash drifting behind its trailing edge on either side (static, part of the model). The ash
vent on its back is a squat stack with a neon ring and a lit grate.

**Acceptance criteria**
- Given the model, then it reads as one ragged creature trailing ash (manual).

*Sources: P10-R11, P16-R05.*

#### MB-ASH-WRAITH-03 — Shroud pods · MUST

Each shroud pod is a ducted fan whose lip is ringed with neon, torn grey shroud strips trailing off
it towards the back and the outside, ash on its lip, and a gun housing under its front holding the
two barrels of its fans. Destroyed, a pod is hidden and leaves nothing in its place.

**Acceptance criteria**
- Given the model, then each pod's two barrels sit at its muzzles under the shroud's front lip (unit:
  `test_boss_models.py`; manual).

*Sources: P10-R11, P16-R05, D-225, D-167.*

#### MB-ASH-WRAITH-04 — Eye cannon · MUST

The eye cannon hangs under the nose, in front of the core: an armoured collar ringed with neon on
the nose, and on it, turning, the eye itself, a dark armoured ball under a heavy lid, its lens barrel
reaching forward, its pale iris and lens lit as the laser charges. Destroyed, the eye and its collar
are hidden and leave nothing in their place.

**Acceptance criteria**
- Given the eye stands, then it turns to aim at the player during its warning line (manual; unit:
  turret laser rule).

*Sources: P10-R11, P16-R05, D-225.*

#### MB-ASH-WRAITH-05 — Lights and colours · MUST

Its registered neon is pale cyan (`ash-wraith`); like every boss's lights it is drawn in the nearer
of the two enemy hues, here bright green (see [readability](../../graphics/readability.md)). Neon
lines the wing's leading edges and tips, the pods' lips, the eye's collar and the ash vent; its veins
are drawn in the same green, its molten seams (orange in the design) in bright yellow. Its hull and
ash stay grey. White charge lights sit in the eye's lens, in the vent's grate and at the barrels'
mouths.

**Acceptance criteria**
- Given the model, then its neon is bright green, its molten seams bright yellow (unit: enemy
  colour family tests).

*Sources: P10-R11, D-231.*

### Behaviour

#### MB-ASH-WRAITH-06 — Entry, place and chase · MUST

The Wraith comes in from above the top edge and stops at 0.73 of the playfield's height. In place it
sways up to 60 px either side over 6.5 s and bobs 8 px over 3.4 s. While it is fought the ground
runs at ×1.5 the level's speed: a chase, the faster of World 4's two.

**Acceptance criteria**
- Given the fight starts, then the ground speeds up to ×1.5 and the boss stops at 0.73 of the
  playfield height (unit: `test_world_boss.py` for the rule; design values in the config).

*Sources: P10-R11.*

#### MB-ASH-WRAITH-07 — Parts and health · MUST

The Wraith has a core (hit radius 17 px, 1 860 HP) and three original parts: two shroud pods (13 px,
820 HP each) that shield the core, and the eye cannon (12 px, 680 HP) that does not; hanging in front
of the core, the eye can always be shot. Its full health is 4 180 HP with the original parts,
5 500 HP with its two hidden lances (660 HP each), which count in the health bar from the start.

**Acceptance criteria**
- Given the design, then it has three original parts and two hidden ones, and only the pods and the
  lances shield the core (unit: `test_ash_wraith.py`).

*Sources: P10-R11, D-088, D-221.*

#### MB-ASH-WRAITH-08 — Pod fans · MUST

While they stand, in every stage, each pod fires a fan of 3 `blue` bullets (205 px/s, 14° apart)
every 2.4 s from its two barrels, leaning outwards (the left one 8° to the left of straight down,
the right one 8° to the right), sweeping the ground either side of the ship; the left one 0.9 s and
the right one 2.1 s into a stage.

**Acceptance criteria**
- Given the pods stand, then their fans lean away from each other (unit: design stages).

*Sources: P10-R11.*

#### MB-ASH-WRAITH-09 — Eye laser · MUST

While it stands, in every stage, the eye fires a laser every 6 s (1.4 s long, after its 1 s warning
line), first 3 s into a stage. The laser is on the eye's turret: the eye follows the player slowly
during the warning line and holds still while the beam fires. Its lasers (the eye's and the hidden
lances') are drawn in its own colour: its pale cyan neon moved into the enemy shots' family, a pale
orange (about [1, 0.79, 0.55]) round a white-hot core.

**Acceptance criteria**
- Given the eye stands, then its beam leaves its lens, pale orange (unit: design guns;
  `enemy_lasers.color_of`).

*Sources: P10-R11, D-072, D-073.*

#### MB-ASH-WRAITH-10 — Core spirals by stage · MUST

The core fires spirals from the ash vent on its back, a new one at each stage (stage k: k parts
destroyed; from the third on, its last pattern):
- stage 0: a three-armed spiral (rings of 3 `purple`, 200 px/s, every 0.6 s, turning 19°);
- stage 1: a four-armed spiral the other way (rings of 4 `purple` every 0.55 s, turning -23°);
- stage 2: a slow six-armed spiral (rings of 6 `magenta`, 210 px/s, every 0.8 s, turning 11°);
- stage 3: twin spirals turning opposite ways (rings of 5 every 0.45 s, `purple` turning 14° and
  `blue` turning -17°), used by no earlier stage.

**Acceptance criteria**
- Given the design, then it has one stage per original part plus one, and the last stage's twin
  spirals are used by no earlier stage (unit: `test_ash_wraith.py`).

*Sources: P10-R11, D-088.*

#### MB-ASH-WRAITH-11 — Rage · MUST

It is angry after its transformation, when the two laser lances it revealed fire all out,
for `boss_rage_seconds`, `boss_rage_rate` times as often, instead of its stage's
pattern ([common](../common.md), BOSS-27). A lost part no longer angers it, and it has no
angry pattern of its own.

**Acceptance criteria**
- Given its transformation is over, then it is angry and fires only the two laser lances it
  revealed (unit: `test_boss_build.py` angry_pattern).
- Given a part is destroyed without a transformation, then it is not angry (unit test).

*Sources: D-088, D-063, D-256.*

#### MB-ASH-WRAITH-12 — Transformation: back plating bursts off · MUST

The Wraith transforms once, when 2 of its 3 original parts are destroyed. Its back plating bursts
off ([common](../common.md), BOSS-42): a faceted dome drawn as a piece of its own over the
fuselage, which is flattened to a deck 3.3 px high under it, from 2.8 px (its foot sunk into the
wing's top) up to 10 px, as wide as the fuselage was (13.5 px either side at the middle); the dark
canopy is painted on its back and it carries the glands, the ridge light, the vents and the scorched
flank strips. Its region (`back`, not mirrored) is the dome's footprint, a lozenge from 25 px ahead
of the centre to 30 px behind it; it bursts into plates cracked from that outline and leaves a
`shell` lattice frame on the deck, where the body's ribs arch and the ash vent's stack rises. The
lances lie folded under it.

**Acceptance criteria**
- Given two original parts are destroyed, then the boss transforms once and its back region bursts
  off, leaving the shell frame (unit: `test_boss_kinds.py`, `test_boss_armour.py`).
- Given its model, then it draws the back region's armour, and it holds together with and without
  it (unit: `test_boss_armour.py`, `test_boss_model.py`).

*Sources: D-221, D-224, D-227, D-254.*

#### MB-ASH-WRAITH-13 — Hidden weapons: two laser lances · MUST

The transformation reveals two laser lances on the bared back, 12 px either side of the centre line
and 7 px ahead of the centre (radius 10 px, pods 9 px high, 660 HP each, 30 % drop chance). They
shield the core and fire their lasers straight down the screen as every lance does (see
[common](../common.md)), the left one 1.2 s and the right one 2.0 s into a stage. The Wraith fires
more once it has transformed (about 8.8 weighted shots a second before, 11 after).

**Acceptance criteria**
- Given the transformation is over, then both lances are live targets that fire, and the boss's
  fire rate has gone up (unit: `test_boss_kinds.py` escalation and weapon checks).

*Sources: D-221, D-229.*

#### MB-ASH-WRAITH-14 — Points and drops · MUST

Destroying the Wraith scores 7 000 points, and each part destroyed 700. Its original parts drop a
bonus half of the time, its hidden weapons 30 % of the time; its core drops one by the game's rule.

**Acceptance criteria**
- Given a pod is destroyed, then the score rises by 700 (unit: scoring rule, design values).

*Sources: P07-R07, P11-R01, D-088.*

## Tunable values

All in `src/game/config/bosses/world_4/ash_wraith.py` (`ASH_WRAITH`) unless noted.

| Name | Value | Notes |
|------|-------|-------|
| level | 4-2, mini | `src/game/config/world_4/bosses.py` `WORLD_4_BOSSES` |
| size | 3 L (radius 51 px) | `stats.size` |
| core | radius 17 px, 1 860 HP | `coreRadius`, `coreHealth` |
| pods | (±36, 6), radius 13, 820 HP, shield | `WRAITH_POD` |
| eye | (0, -32), radius 12, 680 HP, no shield, on a turret | `WRAITH_EYE` |
| full health | 4 180 (5 500 with hidden weapons) | D-088 |
| stop / sway / bob | 0.73 / 60 px, 6.5 s / 8 px, 3.4 s | `stopFraction`, `sway`, `bob` |
| ground speed | ×1.5 | `groundSpeed` |
| muzzles | pod barrels (±36 ∓ 2.6, -8.2, 2), eye lens (0, -47.4, 5), vent (0, 8, 14) | `WRAITH_*` |
| pod fans | 3 × 14°, every 2.4 s, lean ±8°, first 0.9 / 2.1 s | stage volleys |
| eye laser | every 6 s, 1.4 s, first 3 s, on its turret | `volley.laser("eye", …)` |
| bullets | `blue` 205, `purple` 200, `magenta` 210 px/s | radius 4 |
| angry | the revealed weapons, BOSS-27 | `boss_build.angry_pattern` |
| transformation | once, at 2 original parts destroyed | `src/game/sim/boss_build.py` `default_transforms` |
| back region | the dome's footprint, not mirrored: a lozenge y -25..30, x ±13.5 at y -8..2, ±10.5 at y 14, ±5.5 at y 26, `shell`; dome 2.8–10 px over a 3.3 px deck | `armour_region("back", …)`; `src/game/view/bosses/world_4/ash_wraith_armour.py` |
| lances | (±12, -7), radius 10, pod 9, 660 HP, first 1.2 / 2.0 s | `hidden_weapon`; volleys in `src/game/config/bosses/weapon_kinds.py` |
| drops | parts 0.5, hidden weapons 0.3 | `part`, `hidden_weapon` defaults |
| points | 7 000 (700 a part) | `points`, `boss_part_points` |
| neon | [0.55, 0.95, 1], drawn [0.55, 1, 0.59]; laser [1, 0.79, 0.55] | `src/game/config/boss_look.py` `BOSS_LOOK.neon["ash-wraith"]` |

## Notes

- Phase 10 fight time with the D-055 bot: 48.0 s, before the hidden weapons (D-221).
- Its full health takes its place in World 4's boss ordering (P10-R12, see
  [World 4](../../worlds/world-4/world.md)).
