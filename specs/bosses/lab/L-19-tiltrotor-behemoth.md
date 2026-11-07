# Tiltrotor Behemoth

> **Area:** bosses · **Prefix:** `FB-TILTROTOR-BEHEMOTH` · **Related:** [common](../common.md),
> [Canard Gunship](L-19-canard-gunship.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Tiltrotor Behemoth is the final boss of Lab level L-19: a gigantic tiltrotor hovering over the
battlefield. A boxy fuselage with a glazed nose and an upswept tail (an H tail over its rear ramp)
carries a wide high wing across its back, gun sponsons low on its flanks, and at each wingtip a
forked cradle holding a huge rotor nacelle standing up, its three-bladed rotor turning over it. It
changes character at each phase:
- **Gunship** (as it comes in): aimed pairs from its wing guns, bursts from its tail guns, fans swept
  down by its nose gun.
- **Turbine cannons** (its first transformation): each rotor nacelle **morphs into a turbine
  cannon**: its rotor spins down, its blades fold back along it, it tilts forward in its cradle,
  slides in along the wing's leading edge onto its sponson, and its spinner opens in petals as a
  heavy cannon turret rises out of it. Heavy, slow shells join the fight.
- **Gun tower** (its second): its outer **wing halves swing round and stow along the fuselage**
  like a carrier aircraft's, their leading-edge slats flipping up into walls, the ramp swinging
  shut: a compact flying gun tower. A **sweeper** laser rides out on each stowed half and the spine
  fairing bursts off a **mortar** on the centre line: sweeping lasers and flak.

Shared rules are in [common](../common.md).

**Not a creature.** BOSS-47 asks for a Cyber-Organic creature; this Lab boss departs from it on the
user's requests (2026-11-06, "drop the animal looking theme"; "10 more gigantic airplanes"): it is
a built aircraft of dark metal, plating, glass, rotors and neon light lines, with no flesh, eyes or
limbs.

## Requirements

### Look

#### FB-TILTROTOR-BEHEMOTH-01 — Silhouette and size · MUST

Seen from above it is a tiltrotor flying nose first down the screen: a fuselage 158 px long and 30
px wide, a straight wing 172 px across its back, a rotor 52 px across turning over each wingtip (about
208 px from rotor tip to rotor tip), an H tail at its stern: a tiltrotor, unlike any other boss. Its
silhouette changes at each transformation: the rotors go, cannons lie along its forward flanks,
then the wing halves fold in and it is a compact block 60 px across.

**Acceptance criteria**
- Manual validation in the boss viewer: a tiltrotor at rest; cannons by its nose after its first
  transformation; its wing stowed after its second.

*Sources: Lab boss request (2026-11-06, gigantic airplanes).*

#### FB-TILTROTOR-BEHEMOTH-02 — Fuselage, wing, tail and sponsons · MUST

The fuselage is a loft of a chamfered box, tapering to its nose and up into its tail; a smoked glass
cockpit over the nose framed in light, lit lines along its roof's edges, a row of lit ports down each
flank, roof plating, intake grilles behind the wing. The wing's centre section is a bevelled plate
on the roof lit along its leading edge, a fold knuckle at each end; each outer half is a thicker
plate on top of it, lit along its trailing edge, flap seams across it, its wingtip cradle two cheek
plates either side of the nacelle and a bridge behind it, lit on top. The H tail is a stabiliser over
the tail lit along its trailing edge, a fin at each end lit up its rudder. Each gun sponson is a
bevelled box low on the forward flank, lit along its edge, with two saddles and a pedestal on top
for its cannon.

**Acceptance criteria**
- Manual validation: one aircraft, its fuselage, wing, cradles, tail and sponsons readable from
  above.

*Sources: BOSS-49, user request (2026-11-06).*

#### FB-TILTROTOR-BEHEMOTH-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Wing guns** (`wing-left`, `wing-right`): a lit drum on each outer wing, round a twin-barrelled
  turret (its aimed pairs).
- **Tail guns** (`tail-left`, `tail-right`): a lit drum on each of the roof's aft corners, round a
  three-barrelled turret (its bursts).
- **Nose gun** (`nose-gun`): a lit drum on the nose, round a three-barrelled turret (its fans).
- **Dorsal turret** (the core's, on the roof ahead of the wing): three barrels side by side.
- **Spine rotor** (the core's, on the roof behind the wing): fourteen barrels round a hub (its last
  spiral). Until its last stage it lies under an octagonal hatch with a lit seam; as the rotor comes
  into use the hatch bursts off (BOSS-58), leaving a collar, and the rotor rises out.

A destroyed wing gun leaves its stump on its outer wing (it moves with it, BOSS-18); the tail guns'
on the roof; the nose gun's on the nose; a cannon's on its sponson's pedestal.

**Acceptance criteria**
- Given its model, then it draws its five parts and every gun mount.

*Sources: BOSS-18, BOSS-48, BOSS-58.*

#### FB-TILTROTOR-BEHEMOTH-04 — Lights · MUST

The cockpit's frame, the roof lines and ports, the wing's and tail's edges, the cradles' tops, the
sponsons' edges, the drums' rims, the nacelles' intake rings and vents' bands, the blades' tips and
stripes, the petals' stripes, the slats' edges and the ramp's edges glow in its neon colour, orchid
(0.9, 0.4, 1) (BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are its neon colour.

*Sources: BOSS-50.*

#### FB-TILTROTOR-BEHEMOTH-05 — Its rotors, slats and ramp (a view rig) · MUST

Its view rig (`tiltrotor_behemoth_rig.py`, the nacelles drawn in `tiltrotor_behemoth_nacelle.py`):
- **Rotor nacelles**: a cowling standing up in each wingtip cradle on a pivot shaft, a lit intake
  ring and vents, a hub ring at its top; three blades (lit tips and stripes) hinged on the hub ring,
  turning (7 rad/s, the left one the other way); a spinner of four petals closed into a pyramid
  over the hub.
- **Slats**: a lit strip along each outer wing's leading edge, riding the wing half.
- **Ramp**: under the tail, hanging open (level), lit along its edges.

Their moves at the transformations are FB-TILTROTOR-BEHEMOTH-10 and FB-TILTROTOR-BEHEMOTH-11. They
are drawn only: no part, no muzzle, nothing the player can hit or that fires; the cannon parts draw
the same nacelle, tilted and folded, so the rig's nacelle and the part read as one object.

**Acceptance criteria**
- Manual validation: the rotors turn; each morph reads as one machine changing shape.
- Given its model at rest and after each transformation, then it holds together (unit test).

*Sources: user request (2026-11-06, "pieces morphing into something else"), BOSS-52.*

### Behaviour

#### FB-TILTROTOR-BEHEMOTH-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then sways slowly
and bobs: a huge machine hovering. While it is fought the ground scrolls at ×0.6.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.6 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### FB-TILTROTOR-BEHEMOTH-07 — Parts and core · MUST

It has five parts as it comes in, all shielding its core: `wing-left`, `wing-right`, `tail-left`,
`tail-right` and `nose-gun`. The core's guns (the dorsal turret and the spine rotor) fire the core's
volleys and are the last the player destroys.

**Acceptance criteria**
- Given its design, then its five parts all shield the core.

*Sources: BOSS-12, BOSS-13, BOSS-14.*

#### FB-TILTROTOR-BEHEMOTH-08 — Stage patterns · MUST

In every stage while they stand, each wing gun sweeps an aimed pair of red bullets 6° apart, each
tail gun fires bursts of 3 orange bullets, and the nose gun sweeps a fan of 5 purple bullets 12°
apart straight down. The core fires:
- stage 0: an aimed orange bullet;
- stage 1: an aimed spread of 3, 8° apart;
- stage 2: bursts of 4 red bullets;
- stage 3: a fan of 5 purple bullets, 12° apart, and an aimed red bullet;
- stage 4: a fan of 7, 10° apart, and bursts of 3 red bullets;
- stage 5 (all five parts gone): a ring of 14 from the spine rotor, turning 9° at each volley (a
  spiral), and an aimed spread of 3.

Once out, each cannon (FB-TILTROTOR-BEHEMOTH-10) fires aimed spreads of 3 large, slow orange shells;
each sweeper (FB-TILTROTOR-BEHEMOTH-11) a laser sweeping after the player; the mortar flak shells
bursting into rings of 8.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel (a fight in
  the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-40, BOSS-58.*

#### FB-TILTROTOR-BEHEMOTH-09 — Angry · MUST

After each transformation it is angry (BOSS-27): the weapons it has just revealed fire all out for
`boss_rage_seconds`. It has no angry pattern of its own.

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only the weapons it revealed.

*Sources: BOSS-27.*

#### FB-TILTROTOR-BEHEMOTH-10 — First transformation: rotors into turbine cannons · MUST

It transforms when both wing guns are destroyed (named). Each rotor nacelle turns into a cannon, as
one staged event over the transformation's 2 s:
- the rotors spin down and stop (0 to 0.14), each with a blade straight down;
- the blades fold back about their hinges on the hub ring until they lie along the nacelle (0.1 to
  0.26);
- the nacelle tilts forward a quarter turn in its cradle about its pivot shaft, its nose to the
  front (0.22 to 0.4);
- the **cannon** (`cannon-left`, `cannon-right`, BOSS-40) takes over: drawn as the same tilted
  nacelle, its blades folded, it slides in straight from the wingtip along the wing's leading edge
  onto its sponson by the fuselage (0.4 to 0.75, `out_of`);
- its spinner's four petals open like a flower round its nose (0.45 to 0.7), and its heavy turret
  rises out of it (0.7 to 1).

The cradles stay on the wingtips, empty. The cannons shield the core. The fight changes character:
the light aimed pairs give way to heavy, slow shells from close to its nose, the player now weaving
between big bullets.

**Acceptance criteria**
- Given both wing guns destroyed, then it transforms and its two cannons are revealed by its nose,
  sliding in from its wingtips (unit tests on the design).
- Manual validation: the rotor stops, folds, tilts and becomes the cannon in one movement.

*Sources: BOSS-35, BOSS-36, BOSS-40, user request (2026-11-06).*

#### FB-TILTROTOR-BEHEMOTH-11 — Second transformation: the wing stows, a gun tower · MUST

It transforms again when both tail guns are destroyed (named), as one staged event:
- its outer **wing halves** (moving pieces, BOSS-45) strain, then each swings a quarter turn round
  its leading root, back along the fuselage, to lie on top of the wing's centre section and the
  roof (0.15 to 0.6), carrying their empty cradles and the wing guns' stumps;
- a **sweeper** (`sweeper-left`, `sweeper-right`) rides each stowed half and unfolds on it (0.4 to
  0.75);
- the **spine fairing** behind the wing (an armoured hump with a lit seam) bursts off (BOSS-42,
  `shell` frame left) on a **mortar** on the centre line, between the stowed halves;
- the **slats** flip up a quarter turn about the stowed halves' outer edges into walls (0.6 to 0.8),
  and the **ramp** swings up shut under the tail (0.72 to 0.95).

The sweepers and the mortar shield the core. The fight changes character again: from shells to
lasers sweeping after the player and flak bursting round them, from a compact block that fills less
of the screen.

**Acceptance criteria**
- Given both tail guns destroyed, then it transforms, its wing halves move to their stowed pose,
  its spine fairing bursts and its two sweepers and its mortar are revealed (unit tests on the
  design).
- Manual validation: the wing folds in, the slats rise and the ramp shuts as one movement.

*Sources: BOSS-35, BOSS-36, BOSS-42, BOSS-45.*

#### FB-TILTROTOR-BEHEMOTH-12 — Never easier · MUST

Its weighted fire rate (BOSS-39) goes up at each transformation.

**Acceptance criteria**
- Given its design, then its weighted fire rate goes up at each transformation (unit test).

*Sources: BOSS-39.*

#### FB-TILTROTOR-BEHEMOTH-13 — Death, drops and points · MUST

Its parts drop a weapon bonus 60 % of the time, its hidden weapons 30 %, its core always (BOSS-57).
It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/tiltrotor_behemoth.py` (`_TILTROTOR_BEHEMOTH`,
`TILTROTOR_BEHEMOTH`); its model in `src/game/view/bosses/lab/tiltrotor_behemoth_model.py`,
`tiltrotor_behemoth_nacelle.py` and `tiltrotor_behemoth_rig.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 6 L | `stats.size` |
| fuselage | y -84..58 (tail to 74), half width 15, belly 2, roof 20 px | `NOSE`, `TAIL`, `HALF`, `BELLY`, `ROOF` |
| wing | chord y -14..8; centre section x ±30, 20–24 px; outer halves to x ±72, 24.2–27.4 px | `CHORD`, `CENTRE_X`, `CENTRE_H`, `WING_TIP_X`, `OUTER_H` |
| cradles | x ±70..86, y -9..5, 16–29 px | `CRADLE`, `CRADLE_H` |
| nacelles | pivot (±78, -2), 22 px high; radius 6, 24 px long; rotor 26 px; spin 7 rad/s | `NACELLE_AT`, `NACELLE_H`, `NACELLE_RADIUS`, `NACELLE_LENGTH`, `ROTOR_RADIUS`; rig `SPIN` |
| rotor morph | stop 0–0.14, fold 0.1–0.26, tilt 0.22–0.4, petals 0.45–0.7 of the first transformation | rig `SPIN_DOWN`, `FOLD`, `TILT`, `PETALS` |
| wing stow | each outer half turns 90° about (±30, -14) (`up`) | `WING_SWING`; moving regions `wing-right`, `wing-left`, form 2 |
| slats / ramp | flip 0.6–0.8 / shut 0.72–0.95 of the second transformation | rig `SLATS`, `RAMP` |
| sponsons | x ±14..34, y -54..-18, 8–15.5 px | `SPONSON`, `SPONSON_H` |
| core | health 4 700, radius 20, drop 1 | |
| `wing-left`, `wing-right` | (∓44, -3) on the outer wings, radius 9, health 1 300, shield, drop 0.6 | |
| `tail-left`, `tail-right` | (∓9, 52) on the roof, radius 8, health 1 250, shield, drop 0.6 | |
| `nose-gun` | (0, -70) on the nose, radius 10, health 1 400, shield, drop 0.6 | |
| wing guns | 30 px high; 2 barrels 3 px apart, bore 1.1, 8 px long; dome radius 5 | `WING_GUN` |
| tail guns | 20.5 px high; 3 barrels, bore 1, 7 px long; dome radius 4.4 | `TAIL_GUN` |
| nose gun | 19.5 px high; 3 barrels, bore 1.2, 8.5 px long; dome radius 5.2 | `NOSE_GUN` |
| dorsal turret (core) | (0, -36), 20.5 px high; 3 barrels, bore 1.2, 8.5 px long | `DORSAL_GUN` |
| spine rotor (core) | (0, 38), 20.5 px high; 14 barrels, bore 0.75, 3.6 px long; hub radius 5 | `ROTOR` |
| rotor hatch | octagon of radius 6.4 round (0, 38) | `armour_region` `rotor-hatch` (`mount`) |
| cannons | (∓26, -50) on the sponsons, radius 10, health 1 600, pod 16–19.3 px, orange; slide in from (∓78, -29); first 1.2 s / 2.4 s | `cannon-left`, `cannon-right`; `CANNON_AT`, `CANNON_FROM`, `CANNON_POD` |
| sweepers | (∓19, 16) on the stowed halves, radius 8, health 1 400, pod 27.4–30.4 px, red; first 1.2 s / 4.5 s | `sweeper-left`, `sweeper-right`; `SWEEPER_AT`, `SWEEPER_POD` |
| mortar | (0, 18), radius 7, health 1 500, pod 20–22.5 px, purple; first 1.8 s | `mortar`; `MORTAR_AT`, `MORTAR_POD` |
| spine fairing (armour) | x ±7, y 10..29.5, 19.5–25 px; `shell` frame | `FAIRING`, `FAIRING_TOP`; form 2 |
| full health | 18 700 (core 4 700, parts 6 500, cannons 3 200, sweepers 2 800, mortar 1 500) | BOSS-54; the Refinery Titan (1-4) has 19 210 |
| points | 15 000 | |
| ground speed | ×0.6 | |
| stop height | 0.7 | `stopFraction` |
| sway / bob | 28 px over 11 s / 5 px over 4.6 s | |
| wing guns' pairs | aimed 2, 6° apart, red 190 px/s, every 2 s (first 0.8 s / 1.8 s) | sweeps |
| tail guns' bursts | 3, 0.12 s apart, orange 180 px/s, every 2.6 s (first 1.2 s / 2.4 s) | |
| nose gun's fans | 5, 12° apart, purple 175 px/s, every 3 s (first 1.5 s) | swept |
| core stage 0 | aimed 1, orange, every 2.8 s | dorsal turret |
| core stage 1 | aimed 3, 8° apart, every 2.6 s | dorsal turret |
| core stage 2 | bursts of 4, 0.13 s apart, red, every 2.4 s | dorsal turret |
| core stage 3 | fan of 5, 12° apart, purple, every 2.6 s; aimed 1, red, every 3 s | dorsal turret |
| core stage 4 | fan of 7, 10° apart, every 2.4 s; bursts of 3, red, every 2.8 s | dorsal turret |
| core stage 5 | ring of 14 turning 9°, purple, every 1.4 s; aimed 3, 8° apart, orange, every 2.8 s | rotor; dorsal turret |
| weighted fire rate | 6.3 as it comes in, 8.1 after its first transformation, 10.5 after its second | BOSS-39 |
| transformations | `wing-left` and `wing-right`; then `tail-left` and `tail-right` | `transformParts` |
| neon | orchid (0.9, 0.4, 1) | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its full health is in line with the 1-4
  final boss's (Refinery Titan, 19 210), as asked.
- **Not a creature** (see the top): BOSS-47's creature look does not apply; BOSS-48 to BOSS-53 do.
- **The morph is the view's.** The nacelles, their blades and petals, the slats and the ramp are the
  rig's: they follow the boss's `form`, `transforming_into` and `transform`, the reveal timeline
  (`BOSS_LOOK.reveal.swing`: the rig's nacelle hands over to the cannon part exactly as it starts
  sliding) and the wing halves' own progress (`region_motion.progress`). The cannons are hidden
  weapons sliding out of the wingtips (`out_of`), drawn by the model as the tilted nacelle; the
  wing halves are moving regions. No engine change was needed.
- **Why the cannons dock by the nose.** The wing halves move at the second transformation; a
  weapon revealed at the first cannot ride them (BOSS-45), so the nacelles leave the wingtips as
  they become cannons, and their stumps stand on fixed sponsons.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 1 135 shots and 17
  lasers, every one from a barrel or emitter, along it; it dies at about 134 s.
