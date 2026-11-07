# Canard Gunship

> **Area:** bosses · **Prefix:** `MB-CANARD-GUNSHIP` · **Related:** [common](../common.md),
> [Tiltrotor Behemoth](L-19-tiltrotor-behemoth.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Canard Gunship is the mini boss of Lab level L-19: a gigantic canard-wing side-firing gunship.
A long boxy fuselage with a glazed nose carries small canards just behind the nose, its main wings
at the back (swept, a winglet standing on each tip) with an engine on each and a pusher propeller
turning behind it, and two cargo doors down its right flank. It comes in nose-on, firing aimed pairs
from the gun pods on its canard tips and bursts from its nose gun. At its transformation it **banks
round into a broadside** (BOSS-46, a quarter turn) while its right flank **opens up into a gun
gallery**: the cargo doors fold down outward into firing platforms, struts telescoping under them,
an ammunition rack swings out of each bay onto its platform, a gatling unfolds on each and a railing
rises along each platform's edge. From nose-on aimed fire it turns to a side-on gallery raking the
screen. Shared rules are in [common](../common.md).

**Not a creature.** BOSS-47 asks for a Cyber-Organic creature; this Lab boss departs from it on the
user's requests (2026-11-06, "drop the animal looking theme"; "10 more gigantic airplanes"): it is
a built aircraft of dark metal, plating, glass, propellers and neon light lines, with no flesh, eyes
or limbs.

## Requirements

### Look

#### MB-CANARD-GUNSHIP-01 — Silhouette and size · MUST

Seen from above it is a long, thin airplane flying nose first down the screen: a fuselage 128 px
long and 18 px wide, canards 62 px across just behind the nose, swept wings 124 px across at its
back with winglets on their tips: a canard pusher, unlike any other boss. Broadside, the same
airplane lies across the screen, its nose to the left and its gun gallery towards the player.

**Acceptance criteria**
- Manual validation in the boss viewer: a canard airplane at rest, broadside with its gallery out
  after its transformation.

*Sources: Lab boss request (2026-11-06, gigantic airplanes).*

#### MB-CANARD-GUNSHIP-02 — Fuselage, canards, wings and engines · MUST

The fuselage is a loft of a chamfered box, tapering to its nose and up into a tail cone with a lit
band; a smoked glass canopy framed in light over its nose, lit lines along its roof's edges, a row
of lit ports down its left flank, and on its right flank the two cargo doors' dark bays with lit
seams. The canards are bevelled plates lit along their leading edges. The main wings are swept
bevelled plates lit along their trailing edges, flap seams across them, a tall winglet on each tip
lit up its edge. Each engine is a cigar on its wing, a lit intake ring at its nose and a lit collar
at its tail.

**Acceptance criteria**
- Manual validation: one airplane, its fuselage, canards, wings, winglets and engines readable from
  above.

*Sources: BOSS-49, user request (2026-11-06).*

#### MB-CANARD-GUNSHIP-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Canard pods** (`canard-left`, `canard-right`): an armoured, lit drum on each canard's tip, a
  pointed fairing ahead of it, round a twin-barrelled turret (its aimed pairs).
- **Nose gun** (`nose-gun`): a lit drum on the nose, a lit chevron ahead of it, round a
  three-barrelled turret (its bursts).
- **Dorsal turret** (the core's, on the roof amidships): two barrels side by side (its aimed shots,
  spreads and bursts).
- **Spine rotor** (the core's, on the roof between the wings): ten barrels round a hub (its last
  rings). Until its last stage it lies under an octagonal hatch with a lit seam; as the rotor comes
  into use the hatch bursts off (BOSS-58), leaving a collar, and the rotor rises out.

A destroyed canard pod leaves its stump on its canard's tip; the nose gun's on the nose.

**Acceptance criteria**
- Given its model, then it draws its three parts and every gun mount.

*Sources: BOSS-18, BOSS-48, BOSS-58.*

#### MB-CANARD-GUNSHIP-04 — Lights · MUST

The canopy's frame, the roof lines, the ports, the doors' seams, the canards' and wings' edges, the
winglets' stripes, the engines' rings, the pods' and drum's rims, the propellers' blade tips, the
platforms' edges, the struts' sleeves, the racks' drums and the railings' bars glow in its neon
colour, lime (0.5, 1, 0.2) (BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are its neon colour.

*Sources: BOSS-50.*

#### MB-CANARD-GUNSHIP-05 — Its propellers and gallery (a view rig) · MUST

Its view rig (`canard_gunship_rig.py`) draws:
- **Pusher propellers**: four blades with lit tips round a spinner behind each engine, turning all
  the time (18 rad/s, the left one the other way).
- **Struts**: two under each cargo door, from the roof's edge to the door, a sleeve and a rod
  telescoping as the door folds down.
- **Ammunition racks**: one in each bay, lying along the bay's floor inside the hull; from 0.42 to
  0.66 of the transformation each swings a quarter turn out about its foot onto its open platform,
  beside the gatling: a frame of three lit drum magazines.
- **Railings**: once a door is down, a lit railing lying on its platform's outer edge rises (0.62
  to 0.86 of the transformation).

They are drawn only: no part, no muzzle, nothing the player can hit or that fires.

**Acceptance criteria**
- Manual validation: the propellers spin; the struts, racks and railings follow the doors as the
  gallery opens.
- Given its model at rest and after its transformation, then it holds together (unit test).

*Sources: user request (2026-11-06, "pieces morphing into something else"), BOSS-52.*

### Behaviour

#### MB-CANARD-GUNSHIP-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then sways in slow,
wide orbits and bobs: a heavy gunship. While it is fought the ground scrolls at ×1.1.

**Acceptance criteria**
- Given the fight, then the ground eases to ×1.1 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### MB-CANARD-GUNSHIP-07 — Parts and core · MUST

It has three parts as it comes in, all shielding its core: `canard-left`, `canard-right` and
`nose-gun`. The core's guns (the dorsal turret and the spine rotor) fire the core's volleys and are
the last the player destroys.

**Acceptance criteria**
- Given its design, then its three parts all shield the core.

*Sources: BOSS-12, BOSS-13, BOSS-14.*

#### MB-CANARD-GUNSHIP-08 — Stage patterns: nose-on, then a raking gallery · MUST

In every stage while they stand, each canard pod sweeps an aimed pair of red bullets 6° apart, and
the nose gun fires bursts of 3 orange bullets at the player. The core fires:
- stage 0: an aimed green bullet;
- stage 1: an aimed spread of 3, 8° apart;
- stage 2: bursts of 4 orange bullets;
- stage 3 (all three parts gone): a ring of 10 from the spine rotor, turning 9° at each volley (a
  spiral), and an aimed pair of red bullets.

Once out (MB-CANARD-GUNSHIP-10), each gatling fires its bursts of 4 at the player and **rakes**: a
fan of 9 orange bullets 9° apart, 90° off its nose (out of its right flank: once broadside,
straight down the screen), its turret sweeping across it one bullet at a time.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel (a fight in
  the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-58.*

#### MB-CANARD-GUNSHIP-09 — Angry · MUST

After its transformation it is angry (BOSS-27): its two gatlings fire all out for
`boss_rage_seconds`. It has no angry pattern of its own.

**Acceptance criteria**
- Given its transformation is over, then it is angry and fires only its gatlings.

*Sources: BOSS-27.*

#### MB-CANARD-GUNSHIP-10 — Transformation: the gun gallery · MUST

It transforms when both canard pods are destroyed (named). As one event over the transformation's
2 s, following the reveal timeline:
- it **banks round into a broadside** (BOSS-46): a quarter turn clockwise, easing, its nose ending
  to the screen's left and its right flank towards the player; its parts' places, hit circles and
  muzzles turn with it;
- its two **cargo doors** (moving pieces, BOSS-45) strain, then fold down outward about their
  hinges at the cargo floor, from standing closed up the flank to lying open: two firing platforms
  out from the flank (0.15 to 0.6), the struts telescoping under them;
- the **ammunition racks** swing out of the bays onto the platforms (0.42 to 0.66) and a
  **gatling** unfolds on each platform about a hinge by the flank (0.4 to 0.75), its barrels
  sliding out (0.7 to 1); they ride the doors and shield the core;
- the **railings** rise along the platforms' outer edges (0.62 to 0.86).

The fight changes character: from an airplane coming nose-on with aimed pairs and bursts to a
gunship circling broadside, its gallery raking the screen with sweeping fans the player has to
cross between bursts.

**Acceptance criteria**
- Given both canard pods destroyed, then it transforms, turning by pi/2, its doors move to their
  open pose and its two gatlings are revealed on them (unit tests on the design).
- Manual validation: the doors, struts, racks and railings read as the flank opening into a gun
  gallery.

*Sources: BOSS-35, BOSS-36, BOSS-45, BOSS-46.*

#### MB-CANARD-GUNSHIP-11 — Never easier · MUST

Its weighted fire rate (BOSS-39) goes up at its transformation.

**Acceptance criteria**
- Given its design, then its weighted fire rate is higher after its transformation than as it
  comes in (unit test).

*Sources: BOSS-39.*

#### MB-CANARD-GUNSHIP-12 — Death, drops and points · MUST

Its parts drop a weapon bonus 50 % of the time, its hidden weapons 30 % (BOSS-57). It scores the
points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/canard_gunship.py` (`_CANARD_GUNSHIP`, `CANARD_GUNSHIP`); its
model in `src/game/view/bosses/lab/canard_gunship_model.py` and `canard_gunship_rig.py` (the
propellers, struts, racks and railings).

| Name | Value | Notes |
|------|-------|-------|
| size | 3.8 L | `stats.size` |
| fuselage | y -74..54, half width 9, belly 2, floor 6, roof 20 px | `NOSE`, `TAIL`, `HALF`, `BELLY`, `FLOOR`, `ROOF` |
| canards | root y -60..-46, tip x ±31 at y -55..-48, 11–12.6 px high | `CANARD_ROOT`, `CANARD_TIP_X`, `CANARD_TIP`, `CANARD_H` |
| main wings | root y 12..38, tip x ±62 at y 30..42, 12–14.4 px; winglets 30 px high | `WING_ROOT`, `WING_TIP_X`, `WING_TIP`, `WING_H`, `WINGLET_TOP` |
| engines | x ±33, y 16..44, radius 5, axis 14 px high | `ENGINE_X`, `ENGINE_Y`, `ENGINE_RADIUS`, `ENGINE_H` |
| propellers | hub at y 47, 4 blades of 11 px; 18 rad/s | `PROP_Y`, `PROP_RADIUS`; rig `SPIN` |
| cargo doors | y -38..-18 and -14..6 on the right flank, hinged at (9, floor 6), 15 px out open, 1.2 px thick; -90° closed to 0° open | `DOORS`, `DOOR_REACH`, `DOOR_THICK`, `DOOR_SWING`; moving regions `door-fore`, `door-aft`, form 1 |
| racks / railings | swing 0.42–0.66 / rise 0.62–0.86 of the transformation | rig `RACK`, `RAIL` |
| core | health 1 400, radius 14 | |
| `canard-left`, `canard-right` | (∓25, -51) on the canard tips, radius 8, health 700, shield, drop 0.5 | |
| `nose-gun` | (0, -64) on the nose, radius 9, health 760, shield, drop 0.5 | |
| canard pods' guns | 16 px high; 2 barrels 2.8 px apart, bore 1, 7 px long; dome radius 4 | `CANARD_GUN` |
| nose gun | 16.5 px high; 3 barrels, bore 1.1, 8 px long; dome radius 4.6 | `NOSE_GUN` |
| dorsal turret (core) | (0, -6), 20.5 px high; 2 barrels 3 px apart, bore 1.1, 7.5 px long | `DORSAL_GUN` |
| spine rotor (core) | (0, 26), 20.5 px high; 10 barrels, bore 0.8, 3.4 px long; hub radius 4.4 | `ROTOR` |
| rotor hatch | octagon of radius 5.6 round (0, 26) | `armour_region` `rotor-hatch` (`mount`) |
| gatlings | (16.5, -29.5) and (16.5, -5.5) on the doors, radius 7, health 640, pod 6–9.5 px, red; hinge 6.5 px inboard, folded a quarter turn; first 1.0 s / 1.8 s | `gatling-fore`, `gatling-aft`; `GATLING_X`, `GATLING_POD`, `GATLING_HINGE` |
| gatlings' rakes | fan of 9, 9° apart, 90° off the nose, orange 180 px/s, every 3.4 s (first 2.2 s / 3.9 s) | `RAKE_HEADING`; swept by the turret |
| turn | pi/2 (clockwise) at its transformation | `turns` |
| full health | 4 840 (core 1 400, parts 2 160, gatlings 1 280) | BOSS-54 |
| points | 4 600 | |
| ground speed | ×1.1 | |
| stop height | 0.72 | `stopFraction` |
| sway / bob | 55 px over 8 s / 6 px over 3.4 s | |
| canard pods' pairs | aimed 2, 6° apart, red 190 px/s, every 2.2 s (first 0.8 s / 1.9 s) | sweeps |
| nose gun's bursts | 3, 0.12 s apart, orange 180 px/s, every 2.6 s (first 1.3 s) | |
| core stage 0 | aimed 1, green 175 px/s, every 2.8 s | dorsal turret |
| core stage 1 | aimed 3, 8° apart, every 2.4 s | dorsal turret |
| core stage 2 | bursts of 4, 0.12 s apart, orange, every 2.2 s | dorsal turret |
| core stage 3 | ring of 10 turning 9°, green, every 1.5 s; aimed 2, 6° apart, red, every 2.6 s | rotor; dorsal turret |
| weighted fire rate | 3.3 as it comes in, 11.9 after its transformation | BOSS-39 |
| transformation | `canard-left` and `canard-right` | `transformParts` |
| neon | lime (0.5, 1, 0.2) | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its full health is about the Lab's other
  level-4-ish mini bosses' (Windmill Ram 4 840, Scorpion 4 760).
- **Not a creature** (see the top): BOSS-47's creature look does not apply; BOSS-48 to BOSS-53 do.
- **The gallery's detail is the view's.** The doors are moving regions and the gatlings ride them
  (the sim knows them); the struts, racks and railings are the rig's and follow the boss's `form`,
  `transforming_into` and `transform` and the doors' own progress. No engine change was needed.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 632 shots, every one
  from a barrel, along it; it dies at about 74 s.
