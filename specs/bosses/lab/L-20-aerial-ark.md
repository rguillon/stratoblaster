# Aerial Ark

> **Area:** bosses · **Prefix:** `FB-AERIAL-ARK` · **Related:** [common](../common.md),
> [Rocket Interceptor](L-20-rocket-interceptor.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Aerial Ark is the final boss of Lab level L-20, the climax of the gigantic airplanes: a
six-engine flying-wing mothership about 5.3 L across, a long command fuselage down its middle under
a raised bridge, a swept wing with a sawtooth trailing edge, six podded engines along it. Its wing
is built in three segments: the centre section round the fuselage and an outer segment each side,
plated in four tiles. It changes character at each phase: a flying wing whose engines fire crossing
fans, tracking lasers and homing missiles; then, its wing split at its joints and its outer
segments spread apart like a squadron breaking formation, orbs at the split joints filling the sky
with turning rings; then, its outer segments broken into their tiles, which swing round and close
into a halo round its centre section, gatling streams, a lance down its centre line and wide fans.
It is the hardest boss of the Lab set. Shared rules are in [common](../common.md).

**Departure from BOSS-47 (one Cyber-Organic creature):** on the user's requests (2026-11-06, "drop
the animal looking theme", then "10 more gigantic airplanes but be really creative on the
transformation") this Lab boss is an aircraft, not a creature: dark metal plating, glass, engines,
struts, cables and neon light lines, no flesh, eyes or veins.

## Requirements

### Look

#### FB-AERIAL-ARK-01 — Silhouette and size · MUST

Seen from above, its nose down the screen, at rest it is a wide flying wing: a fuselage from y -74
to 56, the wing's leading edge swept back from its root at y -38 to its tips at x ±90 (y 6), its
trailing edge parallel on the outer segments and sawtoothed on the centre section, six engines on
it, about 5.3 L across. After its first transformation its outer segments stand apart from the
centre section, out and back, a gap at each joint bridged by a strut and two cables (about 6.4 L
across). After its second its outer segments are gone from the sides: their eight tiles lie in a
ring of radius 50 round the centre section, a halo about 3.6 L across round the fuselage, its nose
and tail through it.

**Acceptance criteria**
- Manual validation in the boss viewer: a flying wing at rest; a wing split in three, its outer
  segments spread, after the first transformation; a fuselage and centre wing inside a halo after
  the second.

*Sources: Lab boss request (2026-11-06, "gigantic airplanes").*

#### FB-AERIAL-ARK-02 — Fuselage, wing and engines · MUST

Its fuselage is a long faceted hull of dark plating, a light down each shoulder, seams and a vent on
its back, the raised bridge on it (a band of smoked glass round it, a lit edge, the bridge gun's
seat on its roof), the tail rotor's seat, two canted fins at its tail with a lit cargo ramp between
them; its nose lies under the nose plating (armour). The centre section of the wing is a wide,
thick plate, lit along its leading edges, a dark trim along its sawtooth trailing edge, panel lines,
vents and lamps; a dark rib runs along each joint, and out of it the sleeve of the joint's strut.
The inner and middle engines are podded nacelles on it: a plated tube on a pylon, an intake lip lit
at its front, its nozzle burning at its back. Each outer segment is four tiles of dark plating side
by side across its span (the view rig's), a lit seam along each side of each tile, its leading edge
lit, a winglet and a lamp on the tip tile, the outer engine's nacelle on the third tile.

**Acceptance criteria**
- Manual validation: one aircraft of metal, glass and neon lines; no creature features.

*Sources: BOSS-49, BOSS-52; departure from BOSS-47 above.*

#### FB-AERIAL-ARK-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58). Each engine part is the armoured gun section
round its nacelle; destroyed, it is gone and its stump stands on the bare nacelle:
- **Outer engines** (left and right, on the outer segments): collars fore and aft round the nacelle,
  armour cheeks down its sides, a seat lit round its foot with a turret of two barrels on it (its
  crossing fans).
- **Inner engines** (left and right, by the fuselage): the same, a laser turret on the seat (its
  tracking lasers).
- **Middle engines** (left and right): an armoured saddle over the nacelle, lit along its edges,
  cheeks and a collar, a block of four missile ports on it (its homing pairs).
- **Bridge gun** (the core's, on the bridge's roof): three barrels side by side (its aimed shots,
  spreads, fans and bursts).
- **Tail rotor** (the core's): sixteen barrels round a hub on the fuselage's back (its last rings).
  Until its last stage it lies under an octagonal hatch with a lit seam; as the rotor comes into use
  the hatch bursts off (BOSS-58), leaving a lit collar, and the rotor rises out.

**Acceptance criteria**
- Given its model, then it draws all six engine parts and every gun mount.

*Sources: BOSS-48, BOSS-58.*

#### FB-AERIAL-ARK-04 — Lights · MUST

Its leading edges, the tiles' seams, the fuselage's shoulder lines, the bridge's edge, the fins'
tips, the cargo ramp, the engines' intake rings and seats, the saddles' edges, the joints' fairing
seams and bolts, the strut rods' caps, the cables, the tip lamps and the hatch's seam glow. Its neon
colour is set near-white pink (1, 0.95, 0.95); the viewer folds it into the enemy palette
(BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are in its neon colour.

*Sources: BOSS-50.*

#### FB-AERIAL-ARK-05 — Its wing's segments, struts and armour · MUST

The outer segments, their struts' rods and their cables are its view rig: they move only in the
model; the parts and weapons that the player can hit or that fire never move. Its armour regions:
- the **joint fairings** (mirrored): a long plated blister over each joint, x 37 to 51, its seam lit
  along the line the wing splits at, bolts either side of it; shed at the first transformation,
  leaving the joint's dark socket and a lit collar on the strut's sleeve;
- the **wing root plating** (mirrored): thick plated slabs on the centre section ahead of the inner
  engines, a lit slit; shed at the second transformation, leaving a frame;
- the **nose plating**: the armoured command deck over the nose, its windscreen of smoked glass,
  side windows and a light down its middle; shed at the second transformation, leaving a frame;
- the **rotor hatch** over the tail rotor (BOSS-58).

**Acceptance criteria**
- Given its model, then it draws each region, and it holds together at rest and after its first
  transformation (the rig's split pose included).

*Sources: BOSS-42, BOSS-44, BOSS-52.*

### Behaviour

#### FB-AERIAL-ARK-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then sways and bobs
slowly, the biggest thing in the sky. While it is fought the ground scrolls at ×0.3.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.3 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### FB-AERIAL-ARK-07 — Parts and core · MUST

It has six parts as it comes in, all shielding its core: `engine-outer-left`, `engine-outer-right`,
`engine-inner-left`, `engine-inner-right`, `engine-mid-left` and `engine-mid-right`. The core's
guns (the bridge gun and the tail rotor) fire the core's volleys and are the last the player
destroys.

**Acceptance criteria**
- Given its design, then its six parts all shield the core.

*Sources: BOSS-12, BOSS-14.*

#### FB-AERIAL-ARK-08 — Stage patterns: wing, squadron, halo · MUST

In every stage while they stand: each outer engine sweeps a fan of 5 red bullets 12° apart, turned
14° in towards the centre line, so the two fans cross under it; each inner engine fires a tracking
laser (its turret aims during the warning), in turn; each middle engine fires a pair of homing
missiles 24° apart, in turn. The core fires:
- stage 0: an aimed magenta bullet;
- stage 1: an aimed spread of 3, 10° apart;
- stage 2: a fan of 7 purple bullets 12° apart;
- stage 3: a fan of 5 and bursts of 4 magenta;
- stage 4: a fan of 9 and an aimed spread of 3, 12° apart;
- stage 5: a fan of 11, 10° apart, and bursts of 4 red;
- stage 6 and after: a ring of 16 from the tail rotor, one bullet a barrel, turning 8° at each
  volley (a spiral), and a fan of 7.

Its character: as a flying wing (stages 0 and 1), crossing fans, lasers and missiles; split
(stages 2 and 3), the orbs' turning rings with the bridge's fans between them; as a halo (stage 4
on), gatling streams, the lance's straight beam down the centre line, the bridge's wide fans and,
at the last, the tail rotor's spiral.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel (a fight in
  the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-58.*

#### FB-AERIAL-ARK-09 — Angry · MUST

After each transformation it is angry (BOSS-27): the weapons that transformation revealed fire all
out for `boss_rage_seconds` (the orbs' rings; then the gatlings' bursts and the lance as often as
its warning, beam and gap allow). It has no angry pattern of its own.

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only the weapons it revealed.

*Sources: BOSS-27.*

#### FB-AERIAL-ARK-10 — First transformation: the squadron breaks formation · MUST

It transforms the first time when both outer engines are destroyed (named; they retire at it, so
their stumps leave with their segments). As a staged event (2 s, the reveal timeline): the joints'
fairings strain and burst off (to 0.6); from 0.15 to 0.62, eased, each outer segment slides 22 px
out and 8 px back from its joint, swinging its tip 10° back, as one piece; the rod in the joint's
strut telescopes out of its sleeve under it (out to x 68) and the two cables pay out from the centre
section's corners to the segment's root; an **orb** at each split joint, standing on the strut's
sleeve, swings up and slides its rotor out (0.4 to 1.0). The orbs shield the core and fire turning
rings of 10. The fight changes character: no more crossing fans from the wingtips, but two spirals
either side of the fuselage that fill the sky, between the bridge's fans, the lasers and missiles.

**Acceptance criteria**
- Given both outer engines destroyed, then it transforms, its outer engines retire and its two orbs
  are revealed in its joints' fairings.
- Manual validation: the wing splits at its joints and its outer segments spread apart, held by the
  struts and cables.

*Sources: BOSS-35, BOSS-36, BOSS-42, BOSS-46.*

#### FB-AERIAL-ARK-11 — Second transformation: the halo · MUST

It transforms the second time when both inner engines are destroyed (named). As a staged event:
the wing roots' and the nose's plating strain and burst off (to 0.6); the cables reel in (0.12 to
0.32); then each outer segment breaks into its four tiles, which fly one after the other (the
inner one from 0.2 to 0.6, each next one 0.07 later), lifting up to 14 px on their way and turning
about the vertical, each to its place along a ring of radius 50 round the centre section (from the
front of the ring, its tiles 45° apart, their lit seams its two rims), 4 px higher than drawn;
the strut's rod draws back to x 53 (0.15 to 0.45), under the orb, which stands in the ring's gap at
its side. A **gatling** comes out of each wing root's plating and a **lance** out of the nose's,
on its centre line (0.4 to 1.0). They shield the core; the gatlings fire bursts at the player, the
lance a laser straight down the screen. The airplane has become a halo: its silhouette is round,
the fuselage through it, and its fire comes from its middle (streams and a beam) and its sides (the
orbs' rings, if they stand).

**Acceptance criteria**
- Given both inner engines destroyed, then it transforms and its gatlings and lance are revealed in
  their plating.
- Manual validation: the outer segments break into tiles that swing round into a ring round the
  centre section.

*Sources: BOSS-35, BOSS-36, BOSS-41, BOSS-42.*

#### FB-AERIAL-ARK-12 — Death, drops and points · MUST

Its parts drop a weapon bonus 60 % of the time, its hidden weapons 30 %, its core always (BOSS-57).
It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/aerial_ark.py` (`_AERIAL_ARK`, `AERIAL_ARK`) unless named; its
model in `src/game/view/bosses/lab/aerial_ark_model.py`, `aerial_ark_parts.py` and
`aerial_ark_rig.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 5.5 L (radius 93.5 px) | `stats.size` |
| fuselage | y -74 to 56, 24 px wide, back 15 px high; bridge y -30 to -10, 14 px wide, 20 px high | `NOSE`, `TAIL`, `FUSE_TOP`, `BRIDGE*`; loft `FUSELAGE` (model) |
| centre wing (right) | (11, -38) (44, -20) (44, 8) (30, 24) (24, 20) (11, 40); 3 to 8 px high | `CENTRE_WING`, `WING_Y` |
| outer segment | from the joint (x 44) to the tip (x 90), leading edge from y -20 (slope 0.565), chord 28; 4 tiles of 11.5 px; 3.5 to 7.5 px high | `JOINT_X`, `LEAD_*`, `CHORD`, `TIP_X`, `TILES`, `TILE_Y` |
| nacelles | radius 4.6, axis 12 px high, top 16.6; inner x ±20 (y 4–32), middle x ±32 (y -3–20), outer x ±72.75 (y 0–26) | `NACELLE_*`, `*_ENGINE` |
| strut sleeves | y -2, x 38 to 50, 9 px wide, top 9 | `STRUT_*` |
| split (rig) | 0.15–0.62: 22 px out, 8 px back, 10° about (44, -6) | `aerial_ark_rig.SPLIT*` |
| halo (rig) | radius 50 round (0, -2); tiles at -67.5°, -22.5°, 22.5°, 67.5° (and mirrored), 4 px up; each over 0.4 of the transformation from 0.2, 0.07 apart, lifting 14 px | `HALO_*` |
| strut rod (rig) | 22 px long; its outer end at x 44, 68 (split), 53 (halo) | `ROD_*` |
| core | health 5 400, radius 22 | |
| `engine-outer-left`, `engine-outer-right` | (∓72.75, 10), radius 10, health 1 500, shield, drop 0.6, retire at 1 | on the outer segments |
| outer turrets | (∓72.75, 6), 16.6 px high; 2 barrels 2.9 px apart, bore 1.1, 7.5 px long; dome radius 4.4 | `OUTER_GUN` |
| `engine-inner-left`, `engine-inner-right` | (∓20, 14), radius 10, health 1 700, shield, drop 0.6 | |
| inner lasers | (∓20, 10), 16.6 px high, on a turret; bore 1.9, 9 px long | `INNER_LASER` |
| `engine-mid-left`, `engine-mid-right` | (∓32, 4), radius 9, health 1 600, shield, drop 0.6 | |
| missile blocks | (∓32, 3), 4 ports, block top 19.6 | `missile_mount` |
| bridge gun (core) | (0, -20), 20 px high; 3 barrels 2.9 px apart, bore 1.1, 8.5 px long; dome radius 5.6 | `BRIDGE_GUN` |
| tail rotor (core) | (0, 36), 15 px high; 16 barrels, bore 0.7, 3.4 px long; hub radius 5.4 | `ROTOR` |
| rotor hatch | octagon of radius 6.4 round (0, 36) | `armour_region` `rotor-hatch` (`mount`) |
| joint fairings | (37, -11) to (51, 7), mirrored, 7.5 to 13 px high | `JOINT_FAIRING`, `FAIRING_Y` |
| root plating | (12, -28) (31, -22) (31, -6) (12, -6), mirrored, 7.5 to 11 px high | `ROOT_PLATING`, `PLATING_Y` |
| nose plating | (0, -66) (±7, -62) (±10, -50) (±10, -40), 10 to 15.5 px high | `NOSE_PLATING`, `NOSE_Y` |
| full health | 22 820 (core 5 400, parts 9 600, orbs 2 720, gatlings and lance 5 100) | BOSS-54; the 1-5 final boss (Overlord) has 22 760 |
| points | 16 500 | |
| ground speed | ×0.3 | |
| stop height | 0.72 | `stopFraction` |
| sway / bob | 22 px over 12 s / 5 px over 6 s | |
| outer fans | 5 red at 200 px/s, 12° apart, turned ±14° inwards, every 2.8 s (first 1 s / 2.4 s) | `volley.fan`, a sweep |
| inner lasers | 1.4 s every 7 s (first 3 s / 6.5 s) | `volley.laser` |
| middle missiles | 2 homing, 24° apart, every 6 s (first 2 s / 5 s) | `volley.missiles` |
| core stages 0–6 | see FB-AERIAL-ARK-08; magenta 180 px/s, purple 190 px/s, red 200 px/s | bridge gun; rotor |
| weighted fire rate | 7.58 as it comes in, 14.23 after the first transformation, 18.55 after the second | BOSS-39 |
| transformations | `engine-outer-*` destroyed; `engine-inner-*` destroyed | `transformParts` |
| orbs | (∓44, -2) on the strut sleeves, radius 7, health 1 360, pod from 9 to 12.5 px; first 1.2 s / 2.5 s | `orb` kind (rings of 10 turning 13° every 2.6 s) |
| gatlings | (∓21, -16) on the wing roots, radius 7, health 1 700, pod from 8 to 11.5 px; first 1.2 s / 2.2 s | `gatling` kind (bursts of 4 every 2.2 s) |
| lance | (0, -52) in the nose, radius 8, health 1 700, pod from 11 to 15 px; first 1.6 s | `lance` kind (a laser 1.4 s every 7.5 s, straight down) |
| neon | near-white pink (1, 0.95, 0.95) | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its full health is about that of the 1-5
  final boss (Overlord).
- **Not a creature** (see the departure from BOSS-47 above).
- **Only looks move.** Its outer segments are the view rig's, not moving regions (BOSS-45): a
  moving region moves once, at one transformation, and the segments move at both (split, then
  halo). So nothing the player can hit stands on them once they move: the outer engines are named
  for the first transformation and retire at it (their stumps go with them); the orbs stand on the
  strut sleeves of the centre section, the gatlings and the lance in its plating. It changes shape
  in the model only, so `is_moving` does not count it among the bosses that change shape.
- **Engine change wanted.** A moving region with a motion per transformation (e.g. `motions`
  indexed by form), or a rig whose `triangles` gets the form rather than "unfolded or not", would
  let the wholeness check (BOSS-52) see the halo: today it sees the rig's split pose after both
  transformations, so the halo pose is checked by eye only.
- **Silhouette.** The other flying wings (the Storm Petrel, the Arrow Lance) are deltas that keep
  their outline; the Crescent Halo (L-5) is a ring from the start. The Aerial Ark is a wide swept
  wing with a sawtooth trailing edge that splits into three and closes into a halo.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 2 130 shots and 22
  lasers, every shot from a barrel, along it; it dies at about 146 s.
