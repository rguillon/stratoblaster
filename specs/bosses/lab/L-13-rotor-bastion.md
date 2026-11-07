# Rotor Bastion

> **Area:** bosses · **Prefix:** `MB-ROTOR-BASTION` · **Related:** [common](../common.md),
> [Zeppelin Citadel](L-13-zeppelin-citadel.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Rotor Bastion is the mini boss of Lab level L-13: a flying tower held up by four huge ducted
rotors on outrigger arms, a quad-rotor fortress 3.8 L across. Its two front rotors carry gun pods
on their hubs, far out on its flanks, that fire a crossfire of aimed spreads, while the crown turret
on its roof fans bullets straight down. Once both front gun pods are gone its front arms fold back
against the tower, its rotors stopping as they go, its rear rotors tilt forward and spin up, and the
armoured prow bursts open on a pair of orbs: from a spread-out crossfire to a compact, spinning
storm of rings. Shared rules are in [common](../common.md).

**Departure from BOSS-47 (one Cyber-Organic creature):** on the user's requests (2026-11-06, "drop
the animal looking theme", then "flying fortress theme") this Lab boss is a machine that flies, not
a creature: dark metal, plating, rotors, battlements and neon light lines; no flesh, eyes or veins.

## Requirements

### Look

#### MB-ROTOR-BASTION-01 — Silhouette and size · MUST

Seen from above, the Rotor Bastion is an X of four arms round a square tower, its prow down the
screen: a square armoured tower in the middle, a wedge-shaped armoured prow on its front, a gun
balcony on its back, and on each arm, from a corner of the tower, a round rotor duct. It is about
3.8 L across (the rear ducts' outer edges 108 px apart, the front ducts' centres 31 px ahead of the
centre, the rear ones' 36 px behind it). Once it has transformed its front ducts lie beside the
tower's flanks: it is a compact block about 3 L across with two ducts still far out at its back.

**Acceptance criteria**
- Manual validation in the boss viewer: a tower on four ducted rotors at rest, its front arms
  folded back and its prow open once it has transformed.

*Sources: Lab boss request (2026-11-06, "flying fortress theme").*

#### MB-ROTOR-BASTION-02 — Body · MUST

Its tower is plated steel on a flared, chamfered skirt (a lit line round it), with lit window slits
in its walls and a dark roof deck sunk in a crenellated parapet (merlons all round, a lit line round
its edge), plates on its roof's flanks, a vent grille, the crown's seat and the collar of its roof
rotor. A pylon stands at each corner of the tower, a lit cap on it, where an arm hangs. Its gun
balcony juts out of its back on two struts, a lit line along its rear edge. A dark keel runs under
its prow and stays once the prow's armour is gone.

**Acceptance criteria**
- Manual validation: one flying machine of dark metal and neon lines; no creature features.

*Sources: BOSS-49, BOSS-52; departure from BOSS-47 above.*

#### MB-ROTOR-BASTION-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Front rotor gun pods** (left and right, on the front ducts' hubs): an armoured cowl over the hub
  nacelle, a lit band round it and two side cheeks, a turret of two barrels side by side on it (its
  aimed spreads). The nacelle stays under its stump once it is destroyed.
- **Crown** (on the roof's front): a battlemented cupola, a lit band round it and four merlons, a
  turret of three barrels side by side on it (its fans).
- **Balcony turret** (the core's, on the gun balcony behind the tower): three barrels side by side
  (its aimed shots, bursts and spreads).
- **Roof rotor** (the core's): twelve barrels round a hub on the roof's back (its last rings). Until
  its last stage it lies under an octagonal steel hatch with a lit seam; as the rotor comes into
  use the hatch bursts off (BOSS-58), leaving a lit collar, and the rotor rises out.

**Acceptance criteria**
- Given its model, then it draws both rotor gun pods, the crown and every gun mount.

*Sources: BOSS-48, BOSS-58.*

#### MB-ROTOR-BASTION-04 — Lights · MUST

Its skirt and roof lines, window slits, pylon caps, arm lines, duct lips, blade tips, prow chevrons
and the seams round its hatches glow. Its neon colour is set mint (0.3, 1, 0.6); the viewer folds it
into the enemy palette (BOSS-50), where it shows green.

**Acceptance criteria**
- Given its model, then its lights are in its neon colour.

*Sources: BOSS-50.*

#### MB-ROTOR-BASTION-05 — Arms, ducts and rotors · MUST

Each arm is a plated box beam from a corner pylon out to its duct, a lit line along its top, two
armour bands round it and a brace where it meets the duct. Each duct is a ring of dark armour (a lit
band on its lip, six plates round its outside) round a hub nacelle on three spokes. Its blades are a
rig of the model's own (BOSS-46, `drawing.rig`, view only): three blades in each duct, lit at their
tips, spinning. The two front arms, each with its duct, are moving pieces (BOSS-45), hinged on a lit
drum at the tower's front corner: as it transforms each swings 84° back about its hinge (the right
one counter-clockwise seen from above, the left one mirrored), its duct ending beside the tower's
flank, and stays there; they leave no frame. Their blades wind down and stop as they fold; the rear
rotors' blades tilt forward 0.32 rad and spin up from 13 to 21 rad/s (the bastion leaning into its
attack). The blades are not in the simulation: nothing fires from them and they are not hit.

**Acceptance criteria**
- Given its design, then its transformation swings both front arms, mirrored, and no part the
  player can hit stands on them as they move (unit tests on the moving regions).
- Given its model, then it draws each arm, and it holds together at rest and once they have moved.
- Manual validation: the blades spin; the front ones stop as their arms fold, the rear ones tilt
  forward.

*Sources: BOSS-42, BOSS-45, BOSS-46, BOSS-52.*

### Behaviour

#### MB-ROTOR-BASTION-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then sways and bobs
quickly: a hovering craft. While it is fought the ground scrolls at ×0.8.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.8 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### MB-ROTOR-BASTION-07 — Parts and core · MUST

It has three parts as it comes in, all shielding its core: `rotor-left`, `rotor-right` and `crown`.
The core's guns (the balcony turret and the roof rotor) fire the core's volleys and are the last the
player destroys.

**Acceptance criteria**
- Given its design, then its three parts all shield the core.

*Sources: BOSS-12, BOSS-14.*

#### MB-ROTOR-BASTION-08 — Stage patterns: a crossfire, then a ring storm · MUST

In every stage while they stand, each front gun pod fires an aimed spread of 3 red bullets 8° apart
from far out on its side, the two in turn, so their bullets cross on the player (a crossfire); the
crown sweeps a fan of 5 orange bullets 14° apart straight down. The core fires:
- stage 0: an aimed magenta bullet;
- stage 1: a burst of 3 at the player;
- stage 2: an aimed spread of 4, 10° apart;
- stage 3 and after: a ring of 12 from the roof rotor, one bullet a barrel, turning 15° at each
  volley, and a burst of 3 at the player.

Once it has transformed, its two orbs add their turning rings of 10 from the middle of its body:
the fight goes from bullets converging from its flanks to rings spreading from its centre.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel (a fight in
  the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-58.*

#### MB-ROTOR-BASTION-09 — Angry · MUST

After its transformation it is angry (BOSS-27): its two orbs fire all out, `boss_rage_rate` times
as often, for `boss_rage_seconds`: a storm of turning rings. It has no angry pattern of its own.

**Acceptance criteria**
- Given its transformation is over, then it is angry and fires only its two orbs.

*Sources: BOSS-27.*

#### MB-ROTOR-BASTION-10 — Transformation: it folds and opens · MUST

It transforms once, when both front gun pods are destroyed (named, so that no part the player can
hit stands on an arm as it moves). As one event: its prow's armour strains and bursts off in pieces
(BOSS-43, a `shell` frame left over its keel), its front arms swing back against the tower's flanks
(MB-ROTOR-BASTION-05), their blades stopping, the rear rotors tilt forward and spin up, and an
**orb** unfolds on each side of the prow's bared frame. They shield the core and fire their turning
rings.

**Acceptance criteria**
- Given both front gun pods destroyed, then it transforms: its front arms fold back and its two
  orbs are revealed in the prow.

*Sources: BOSS-35, BOSS-36, BOSS-42, BOSS-45.*

#### MB-ROTOR-BASTION-11 — Death, drops and points · MUST

Its parts drop a weapon bonus half of the time, its orbs 30 %; it drops a life bonus as a mini boss
(BOSS-57). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/rotor_bastion.py` (`_ROTOR_BASTION`, `ROTOR_BASTION`) unless
named; its model in `src/game/view/bosses/lab/rotor_bastion_model.py` and
`rotor_bastion_rotors.py` (arms, ducts and the blade rig).

| Name | Value | Notes |
|------|-------|-------|
| size | 3.8 L (radius 64.6 px) | `stats.size` |
| tower | 30 px square (`TOWER_HALF` 15), walls to 20 px, merlons to 22 px; skirt 35 px square to 6.2 px | `TOWER_HALF`, `TOWER_WALL`, `TOWER_ROOF` |
| prow (armour) | from the tower's front to y -33 (6 px wide nose), 2–14 px; `shell` frame | `PROW`, `PROW_TOP`; `armour_region` `prow` |
| balcony | 18 px wide, from the tower's back to y 25, 11 px high | `BALCONY_BACK`, `BALCONY_TOP` |
| ducts | outer radius 13, inner 10.6, 4–10 px high; hubs radius 4.2, the front ones to 14.4 px | `DUCT_OUT`, `DUCT_IN`, `DUCT_LOW`, `DUCT_HIGH`, `HUB_RADIUS`, `HUB_TOP` |
| front ducts | centres (±40, -31) at rest, about (±33.5, 8.2) folded | `FRONT_DUCT` |
| rear ducts | centres (±41, 36) | `REAR_DUCT` |
| arms | box beams 5 px wide, 5.5–9.5 px high | `ARM_LOW`, `ARM_HIGH` |
| front arms (moving regions) | outline round the beam and duct, from (±15, -15) out; swing 0° → 84° about `up` through (±15, -15, 0), mirrored; no frame | `moving_region` `front-arm`, `ARM_SWING`, `FOLD` |
| blades (rig) | 3 a rotor, 9.8 px long; spin 13 rad/s; the front ones stop as they fold (over the first 0.8 of the transformation), the rear ones tilt 0.32 rad forward and spin up to 21 rad/s | `rotor_bastion_rotors` `SPIN`, `SPIN_FAST`, `TILT` |
| core | health 1 050, radius 16 | |
| `rotor-left`, `rotor-right` | (∓40, -31), radius 11, health 640, shield, drop 0.5 | on the front arms |
| pod turrets | 15 px high; 2 barrels 2.9 px apart, bore 1.1, 7 px long; dome radius 4.4 | `POD_GUN` |
| `crown` | (0, -4), radius 9, health 700, shield, drop 0.5 | |
| crown turret | 25 px high; 3 barrels 2.9 px apart, bore 1.1, 7.5 px long; dome radius 5 | `CROWN_GUN` |
| balcony turret (core) | (0, 20), 11 px high; 3 barrels 2.9 px apart, bore 1.1, 7 px long; dome radius 4.6 | `BALCONY_GUN` |
| roof rotor (core) | (0, 9), 22 px high; 12 barrels, bore 0.7, 3.2 px long; hub radius 4.4 | `ROTOR` |
| roof hatch | octagon of radius 5.6 round (0, 9) | `armour_region` `roof-hatch` (`mount`) |
| orbs | (∓6.5, -23) in the prow, radius 6.5, health 560, pod 3–6.5 px, orange; first 1.2 s / 2.0 s | rings of 10 turning 13°, every 2.6 s |
| full health | 4 150 (core 1 050, parts 1 980, orbs 1 120) | BOSS-54; the Bastion Cube (L-7) has 4 040 |
| points | 3 600 | |
| ground speed | ×0.8 | |
| stop height | 0.72 | `stopFraction` |
| sway / bob | 50 px over 7 s / 7 px over 3.2 s | |
| pods' spreads | aimed 3, 8° apart, red 185 px/s, every 2.4 s (first 1 s / 2.2 s) | sweeps |
| crown's fans | 5, 14° apart, straight down, orange 175 px/s, every 2.8 s (first 1.6 s) | a sweep |
| core stage 0 | aimed 1, magenta 190 px/s, every 2.6 s | balcony turret |
| core stage 1 | burst of 3, 0.14 s apart, every 2.4 s | balcony turret |
| core stage 2 | aimed 4, 10° apart, every 2.6 s | balcony turret |
| core stage 3+ | ring of 12 orange turning 15°, every 1.6 s; burst of 3, 0.13 s apart, every 2.6 s | roof rotor; balcony turret |
| weighted fire rate | 4.7 as it comes in, 11.0 after its transformation | BOSS-39 |
| transformation | `rotor-left` and `rotor-right` destroyed | `transformParts` |
| neon | mint (0.3, 1, 0.6), shown green | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its full health is about that of the L-7
  mini boss (Bastion Cube).
- **Not a creature** (see the departure from BOSS-47 above).
- **Silhouette.** The Toucan (3-2) and the Ash Wraith (4-2) have ducted fans at their wing tips; the
  Rotor Bastion differs as a square tower on four rotors in an X, with no wings or body of a beast.
- **Its tilt.** The suggested "tower tilting into attack posture" is drawn on the rear rotors only
  (their blades tilt forward): tilting the tower itself would move its muzzles and hit circles away
  from the simulation's, and the engine has no pitch for a whole boss.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 795 shots, every one
  from a barrel, along it; it dies at about 74 s.
