# Cloud Dreadnought

> **Area:** bosses · **Prefix:** `FB-CLOUD-DREADNOUGHT` · **Related:** [common](../common.md),
> [Bell Keep](L-12-bell-keep.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Cloud Dreadnought is the final boss of Lab level L-12: a long flying battleship. A sharp grey
hull carries a triple-gun main turret fore and aft, a two-tiered superstructure under its bridge,
two raked smokestacks and a lift-engine nacelle out on each flank. It comes in bow first, firing
its main guns down its length. Losing its lift engines, it swings its side armour belts out like
wings to stay aloft, a battery riding each; losing its main turrets, it turns broadside, its whole
length across the screen, bursts the plating of its after deck on a pair of missile racks and a
lance, and opens up with its starboard casemates: a wall of fire across the screen. Shared rules
are in [common](../common.md).

**Not a creature.** BOSS-47 asks for a Cyber-Organic creature; this Lab boss departs from it on the
user's requests (2026-11-06, "drop the animal looking theme", then "flying fortress theme"): it is
a warship of grey and dark metal plating with red light lines, no flesh, eyes or limbs.

## Requirements

### Look

#### FB-CLOUD-DREADNOUGHT-01 — Silhouette and size · MUST

Seen from above at rest it is a long, narrow ship 164 px (4.8 L) from its pointed bow to its flat
stern and 36 px across its deck, its lift engines' round ducts out on either flank behind its
middle. Once its belts are out it is a cross, 92 px across its belts; once broadside it lies across
the screen, its bow to the left.

**Acceptance criteria**
- Manual validation in the boss viewer: a battleship, unlike any other boss, then a cross, then
  broadside.

*Sources: Lab boss request (2026-11-06).*

#### FB-CLOUD-DREADNOUGHT-02 — Hull and superstructure · MUST

Its hull is lofted from a flat deck down to a narrow keel that rises towards the bow, its deck
planked, lit strips along its deck's edges and down its flanks, lit chevrons on its prow and a stem
post with a lamp. Its superstructure is two stepped tiers on the centre line before its middle, lit
window bands, searchlights at the lower tier's corners, the bridge's flak rotor seated on the upper
tier's back. Behind it a deckhouse carries the core's twin turret, then two raked smokestacks with
lit bands near their caps. Launches in their davits and cowl vents stand either side of the
smokestacks, an anchor in each hawse at the bow, lit portholes (its charge lights) along its
flanks, twin tail fins over its stern, the belts' hinge rails along its deck's edges.

**Acceptance criteria**
- Manual validation: one ship, its hull, superstructure and stacks readable from above.

*Sources: BOSS-49, user request (2026-11-06).*

#### FB-CLOUD-DREADNOUGHT-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Lift engines** (`engine-left`, `engine-right`): a ducted lift fan (its fan turning, its duct's
  rim lit) out on a pylon from the deck's edge behind the belts; a twin-barrelled AA turret at the
  pylon's root, on the deck (its bursts).
- **Main turrets** (`turret-fore`, `turret-aft`): a heavy armoured collar, lit, round the top of a
  barbette on the centre line; a turret of three heavy barrels (its aimed spreads of shells).
- **Bridge** (`bridge`): a conning tower on the superstructure, its windows lit, a rangefinder
  across its roof, a tripod mast with a yard and a lamp; its flak rotor of eight barrels stands on
  the upper tier behind it (its rings).
- **Core turret** (on the deckhouse): two barrels side by side (its aimed shots, bursts and fans).
- **Stern rotor** (the core's): sixteen barrels round a hub (its last spiral), under an armoured
  cupola (a hatch, BOSS-58) on the stern deck until its last stage; the cupola bursts off, leaving a
  collar, and the rotor rises out.
- **Starboard casemates** (the core's, four): fixed guns of three barrels side by side on sponsons
  out of its right flank, two fore, two aft, pointing out to its right (FB-CLOUD-DREADNOUGHT-11).

The barbettes and the superstructure's tiers are the hull's: a destroyed turret or bridge leaves its
stumps on them.

**Acceptance criteria**
- Given its model, then it draws its five parts and every gun mount.

*Sources: BOSS-48, BOSS-58.*

#### FB-CLOUD-DREADNOUGHT-04 — Lights · MUST

Its deck's edges, flanks, prow, window bands, stacks' bands, ducts' rims, belts' seams and edges and
the lamps glow. Its neon colour, set red, shows bright yellow (BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright yellow.

*Sources: BOSS-50.*

#### FB-CLOUD-DREADNOUGHT-05 — Its armour belts change shape · MUST

Its two armour belts are moving pieces (BOSS-45): heavy grey plates with lit seams and a lit outer
edge, the batteries' dark beds lit at their corners, hinge knuckles along their roots, ribbed
underneath. Each is drawn swung out flat like a wing at deck height (a swept trapezoid from the
deck's edge out to 46 px) and rests hanging straight down the hull's flank, swung 90° about its
hinge along the deck's edge (about the boss's length); the left one is the right one's mirror
image. At its first transformation both swing up and out to lie flat and stay so; they leave no
frame.

**Acceptance criteria**
- Given its design, then its first transformation moves its two belts, mirrored, and its batteries
  ride them (unit tests on the moving regions).
- Given its model, then it draws each belt, and it holds together at rest and once they are out.

*Sources: BOSS-42, BOSS-45, BOSS-52.*

### Behaviour

#### FB-CLOUD-DREADNOUGHT-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then drifts slowly
across and bobs a little: a heavy ship. While it is fought the ground scrolls at ×0.8.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.8 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### FB-CLOUD-DREADNOUGHT-07 — Parts and core · MUST

It has five parts as it comes in, all shielding its core: `engine-left`, `engine-right`,
`turret-fore`, `turret-aft` and `bridge`. The core's guns (its twin turret, its casemates and its
stern rotor) fire the core's volleys and are the last the player destroys.

**Acceptance criteria**
- Given its design, then its five parts all shield the core.

*Sources: BOSS-12, BOSS-13, BOSS-14.*

#### FB-CLOUD-DREADNOUGHT-08 — Stage patterns · MUST

In every stage while they stand: each lift engine's turret fires bursts of 3 red bullets at the
player; each main turret sweeps an aimed spread of 3 heavy orange shells 8° apart, fore and aft in
turn; the bridge's flak rotor fires a ring of 8 slow, heavy bullets, turned 22.5° at each volley.
The core fires:
- stage 0: an aimed magenta bullet;
- stage 1: a burst of 3;
- stage 2: an aimed pair, 6° apart;
- stage 3: a burst of 4 and an aimed red bullet;
- stage 4: a fan of 7, 8° apart, 45° off straight down (towards the screen's right as it comes in,
  its left once broadside: it turns with it), and its broadside (FB-CLOUD-DREADNOUGHT-11);
- stage 5 and on: the stern rotor's ring of 16 turning 11.25° at each volley (a spiral), a fan of
  5, 10° apart, 45° off straight down, and its broadside.

From stage 4 on the core aims nothing (FB-CLOUD-DREADNOUGHT-11, Notes).

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel (a fight in
  the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-58.*

#### FB-CLOUD-DREADNOUGHT-09 — Angry · MUST

After each transformation it is angry (BOSS-27): after the first its two batteries fire all out,
after the second its racks (three times the missiles) and its lance, for `boss_rage_seconds`. It
has no angry pattern of its own.

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only the weapons it revealed.

*Sources: BOSS-27.*

#### FB-CLOUD-DREADNOUGHT-10 — First transformation: the belts swing out like wings · MUST

It transforms the first time when both lift engines are destroyed (named, BOSS-36): its belts swing
up and out from its flanks to lie flat like wings (FB-CLOUD-DREADNOUGHT-05), and a **battery**
rides out on each, on its bed: five barrels side by side sweeping wide fans of 7 red bullets, 9°
apart. Their fans go 45° off straight down, towards the screen's right as they come out (both
batteries), and towards its left once it is broadside: the batteries turn with it. They shield the
core. Its fire turns from aimed shots down its length to sheets of fans raking the screen.

**Acceptance criteria**
- Given both lift engines destroyed, then it transforms, its belts swing out and its two batteries
  are revealed on them.

*Sources: BOSS-35, BOSS-36, BOSS-45.*

#### FB-CLOUD-DREADNOUGHT-11 — Second transformation: it turns broadside · MUST

It transforms the second time when both main turrets are destroyed (named): over the
transformation it turns a quarter round clockwise (BOSS-46), its bow to the screen's left and its
whole length across the screen, its right flank to the player, its belts now standing above and
below it; the plating of its after deck (three heavy plates with lit seams) bursts off (`shell`
frame) on a missile **rack** either side of the centre line, firing pairs of homing missiles, and a
**lance** on the centre line, its laser pointing out of its right flank, so straight down at the
player once broadside. They shield the core. While the lance stands, its four starboard casemates
fire their three barrels at once, one after the other from bow to stern (0.2 s apart), every 2.4 s:
a wall of parallel bullets across the screen, the lance's beam down its middle. The fight becomes
a broadside: find the gaps in the wall, or destroy the lance to silence it.

**Acceptance criteria**
- Given both main turrets destroyed, then it transforms, turns broadside, its plating bursts and
  its two racks and lance are revealed.
- Given it is broadside and its lance stands, then its casemates' bullets and its lance's beam go
  straight down the screen (a fight in the simulation).

*Sources: BOSS-35, BOSS-36, BOSS-41, BOSS-42, BOSS-46.*

#### FB-CLOUD-DREADNOUGHT-12 — Never easier · MUST

Its weighted fire rate (BOSS-39) goes up at each transformation.

**Acceptance criteria**
- Given its design, then its weighted fire rate as it comes in, after its first and after its second
  transformation goes up (unit test).

*Sources: BOSS-39.*

#### FB-CLOUD-DREADNOUGHT-13 — Death, drops and points · MUST

Its parts drop a weapon bonus 60 % of the time, its hidden weapons 30 %, its core always (BOSS-57).
It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/cloud_dreadnought.py` (`_CLOUD_DREADNOUGHT`,
`CLOUD_DREADNOUGHT`); its model in `src/game/view/bosses/lab/cloud_dreadnought_model.py` and
`cloud_dreadnought_parts.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 5 L (radius 85 px) | `stats.size` |
| hull | bow at y -88, stern at 76; half width 18 amidships (stations in `HULL`); deck 8 px, keel -7 px | `HULL`, `DECK`, `KEEL` |
| barbettes | (0, -50) and (0, 52), radius 8.5, to 12 px | `FORE_AT`, `AFT_AT`, `BARBETTE_*` |
| superstructure | tiers ±11 × y -40..-15 to 15 px, ±8 × y -37..-17 to 21 px; conning tower ±5.5 × y -37..-29 to 27 px | `SUPERSTRUCTURE`, `CONNING` |
| smokestacks | (0, 0.5) and (0, 9), radius 3.8, to 22 px, raked 0.18 rad | `FUNNELS`, `FUNNEL_*` |
| core | health 1 600, radius 16 | |
| `engine-left`, `engine-right` | (∓29, 32), radius 11, health 700, shield, drop 0.6; ducts radius 8.5 | `ENGINE_AT`, `ENGINE_RADIUS` |
| `turret-fore`, `turret-aft` | (0, -50), (0, 52), radius 11, health 900, shield, drop 0.6 | |
| `bridge` | (0, -28), radius 11, health 850, shield, drop 0.6 | |
| AA turrets | (∓14, 27), on the deck (8 px); 2 barrels 2.3 px apart, bore 0.9, 6 px long; dome radius 4 | `ENGINE_GUN` |
| main turrets | 12 px high; 3 barrels 3.4 px apart, bore 1.3, 10 px long; dome radius 6.5 | `MAIN_GUN` |
| flak rotor | (0, -21.5), 21 px high; 8 barrels, bore 0.9, 3.2 px long; hub radius 4.2 | `BRIDGE_ROTOR` |
| core turret | (0, -9), 13 px high; 2 barrels 2.6 px apart, bore 1, 7 px long; dome radius 4.4 | `CORE_GUN` |
| stern rotor (core) | (0, 65), 8 px high; 16 barrels, bore 0.7, 3.2 px long; hub radius 4.4 | `CORE_ROTOR` |
| stern hatch | octagon of radius 5.5 round (0, 65) | `armour_region` `rotor-hatch` (`mount`) |
| casemates (core) | (14.4, -42), (15.7, -34), (15.3, 40), (14.4, 46), 8.4 px high; fixed, 3 barrels 2.6 px apart, bore 0.9, 5 px long, pointing -90° (to its right) | `CASEMATE`, `CASEMATE_YS` |
| belts (moving regions) | outline (18, -24), (42, -12), (46, -5), (46, 10), (42, 15), (18, 20) (mirrored), 2.5 px thick; swing `along` about (±18, 0, 8) from 90° (hanging) to 0 (out, as drawn); no frame | `moving_region` `belt` |
| batteries | (∓32, -1) on the belts, radius 9, health 720 (0.8 of the main turrets'), pod 8–11 px, red; first 1.2 s / 2.0 s; fans 45° off straight down | ride the belts; `BATTERY_HEADING` |
| plating (armour) | x -12.5..12.5, y 14..38, 8–10.5 px; `shell` frame | form 2 |
| racks | (∓7, 21), radius 7, health 900, pod 8–11 px; first 1.2 s / 2.0 s | in the plating |
| lance | (0, 31.5), radius 7, health 900, pod 8–11 px; pointing -90° (out of its right flank); first 1.6 s | in the plating, centre line |
| turn | none at its first transformation; π/2 (clockwise) at its second | `turns` |
| full health | 9 790 (core 1 600, parts 4 050, batteries 1 440, racks and lance 2 700) | BOSS-54; the Gull Mothership's (1-2 final) is 9 740 |
| points | 10 000 | |
| ground speed | ×0.8 | |
| stop height | 0.72 | `stopFraction` |
| sway / bob | 40 px over 10 s / 4 px over 4.6 s | |
| AA bursts | 3, 0.13 s apart, red 185 px/s, every 2.6 s (first 1 s / 2.3 s) | |
| main turrets' spreads | aimed 3, 8° apart, orange 160 px/s radius 5, every 2.8 s (first 1.6 s / 3 s) | sweeps |
| flak rotor's rings | 8 turning 22.5°, orange 130 px/s radius 5, every 3.2 s (first 2 s) | |
| core stage 0 | aimed 1, magenta 175 px/s, every 2.8 s | core turret |
| core stage 1 | burst of 3, 0.14 s apart, every 2.6 s | core turret |
| core stage 2 | aimed 2, 6° apart, every 2.2 s | core turret |
| core stage 3 | burst of 4, 0.12 s apart, every 2.4 s; aimed 1, red, every 3 s | core turret |
| core stage 4 | fan of 7, 8° apart, 45° off down, every 2.2 s; broadside | core turret; casemates |
| core stage 5 | ring of 16 turning 11.25°, orange 130 px/s, every 1.4 s; fan of 5, 10° apart, 45° off down, red, every 2.6 s; broadside | rotor; turret; casemates |
| broadside | each casemate 3 bullets at once, red 170 px/s, every 2.4 s, first 0.5 / 0.7 / 0.9 / 1.1 s; only while the lance stands | `BROADSIDE` (`needs: lance`) |
| weighted fire rate | 7.3 as it comes in, 12.6 after its first transformation, 20.1 after its second | BOSS-39 |
| transformations | `engine-left` and `engine-right`; then `turret-fore` and `turret-aft` | `transformParts` |
| neon | red (1, 0.1, 0.2), shown yellow | `BOSS_LOOK.neon` |
| triangles | about 3 870 drawn (core, parts, armour), within 10 000 | BOSS-53 (scratch count) |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its full health is in line with the 1-2
  final boss's (Gull Mothership, 9 740).
- **Not a creature** (see the top): BOSS-47's creature look does not apply; BOSS-48 to BOSS-53 do.
- **Aiming once turned.** A turret's aim at the player (`boss_pattern._aim_at_player`) does not
  allow for its boss's heading: on a boss turned a quarter round, aimed shots and bursts from a
  turret leave a quarter turn off the player. So nothing it fires once it may be broadside (its
  core from stage 4, its revealed weapons) is aimed: preset fans (which turn with it), rings, the
  fixed casemates and lance, homing missiles. An engine fix (subtract the piece's heading from the
  turret's aim) would let its core aim again in its broadside.
- **Fans that turn with it.** Its batteries' and its core's late fans go 45° off straight down, a
  preset heading on the boss, not on the screen: they rake one way as it comes in and the other way
  once broadside, and never go up the screen (a battery's kind fires straight down, BOSS-40: these
  two are tilted so).
- **The casemates.** They rise when its core's stage 4 first uses them (its broadside's volleys,
  BOSS-58), and fire only while the lance stands; destroyed with the core.
- **Drawn out.** The belts are drawn as they end up, swung out flat, so that the batteries' pods lie
  on them (BOSS-45); the models drop the faces turned down, so their undersides are ribbed (each face
  40° off flat) to still show as they swing and once they hang.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 1 845 shots and 14
  lasers, every one from a barrel, along it; once broadside its casemates' bullets and its lance's
  beam go straight down, its batteries' fans 20°–71° to the left; it dies at about 134 s.
