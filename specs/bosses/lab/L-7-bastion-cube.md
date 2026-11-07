# Bastion Cube

> **Area:** bosses · **Prefix:** `MB-BASTION-CUBE` · **Related:** [common](../common.md),
> [Twin Pylon](L-7-twin-pylon.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Bastion Cube is the mini boss of Lab level L-7: a square, stepped block fortress 3.6 L across,
seen from above. Its gatehouse drops straight walls of bullets, its two front towers fire aimed
bursts in turn, and its keep adds an orderly pattern of its own: a geometric, grid-like fight. Once
both front towers are gone its four corner blocks slide out on their rails, opening the cube (it
changes shape, BOSS-45), and a gatling rides out on each rear tower. Shared rules are in
[common](../common.md).

**Departure from BOSS-47 (one Cyber-Organic creature):** on the user's request (2026-11-06, "drop
the animal looking theme") this Lab boss is a machine, not a creature: dark metal, plating,
battlements and neon light lines, no flesh, eyes or veins.

## Requirements

### Look

#### MB-BASTION-CUBE-01 — Silhouette and size · MUST

Seen from above, the Bastion Cube is a square fortress, its gatehouse down the screen: a
cross-shaped plinth with a square bastion block filling each of its four corner notches, a drum
tower standing on each block, a ziggurat of three square steel tiers stepping up to the keep on its
summit, and a gatehouse jutting out of the middle of its front wall. It is 92 px square (3.6 L
across with its gatehouse); once its blocks have slid out it is about 4.3 L across, its corners
standing apart from the core.

**Acceptance criteria**
- Manual validation in the boss viewer: a square stepped fortress with four corner towers and a
  gatehouse at rest, its corners slid apart once it has transformed.

*Sources: Lab boss request (2026-11-06).*

#### MB-BASTION-CUBE-02 — Body · MUST

Its plinth is dark plated steel with crenellated curtain walls (merlons along its outer walls, a lit
line under them) and a sealed rear gate; its three tiers are chamfered square slabs in alternating
shades, each with a lit line round its top edge, plates on the first tier's faces, a vent grille at
the back of the second, lit studs on its corners; the keep on the summit has four lit corner posts,
its turret's seat and the collar of its crown rotor. Each corner notch, under its block at rest,
holds a dark floor with two lit rails running out diagonally, a lit slot in each inner wall and a
ribbed conduit along their foot: the machinery the blocks bare as they slide out.

**Acceptance criteria**
- Manual validation: one machine of dark metal and neon lines; no creature features.

*Sources: BOSS-49, BOSS-52; departure from BOSS-47 above.*

#### MB-BASTION-CUBE-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Front towers** (left and right, on the front corner blocks): each the battlemented crown on its
  block's drum tower (a lit band, four merlons), a turret of two barrels side by side standing in it
  (its aimed bursts). The drum stays on the block once the crown is destroyed.
- **Gatehouse** (front, over the front wall's middle): a squat gate tower between two small lit
  bastions, a lit portcullis in its face and battlements on its roof; on its front the **wall gun**,
  five barrels side by side on a fixed base, all pointing straight down the screen. Its foot stays
  on the wall once it is destroyed.
- **Keep turret** (the core's, on the summit's front): three barrels side by side (its aimed shots,
  fans and bursts).
- **Crown rotor** (the core's): eight barrels round a hub on the summit, behind the keep turret (its
  last rings). Until its last stage it lies under an octagonal steel hatch with a lit seam; as the
  rotor comes into use the hatch bursts off (BOSS-58), leaving a lit collar, and the rotor rises
  out.

**Acceptance criteria**
- Given its model, then it draws both front towers, the gatehouse and every gun mount.

*Sources: BOSS-48, BOSS-58.*

#### MB-BASTION-CUBE-04 — Lights · MUST

Its tier edges, wall lines, rails, notch slots, tower bands, portcullis and the seams round its
hatches glow. Its neon colour is set coral (1, 0.35, 0.35); the viewer folds it into the enemy
palette (BOSS-50), where it shows as a warm yellow-white.

**Acceptance criteria**
- Given its model, then its lights are in its neon colour.

*Sources: BOSS-50.*

#### MB-BASTION-CUBE-05 — Its corner blocks slide out · MUST

Its four corner blocks (each with its drum tower) are moving pieces (BOSS-45), drawn at rest: at its
transformation each slides 13 px out diagonally, away from the centre on both axes (the two front
ones forward and out, the two rear ones back and out), and stays there. They leave no frame: the
lit floors, rails and slots of the notches show in the gaps. The summit hatch is a shed region of
its own (BOSS-58).

**Acceptance criteria**
- Given its design, then its transformation moves the front and rear blocks, each pair mirrored,
  and its gatlings ride the rear blocks (unit tests on the moving regions).
- Given its model, then it draws each block, and it holds together at rest and once they have moved.

*Sources: BOSS-42, BOSS-45, BOSS-52.*

### Behaviour

#### MB-BASTION-CUBE-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then sways slowly
and bobs a little: heavy and square. While it is fought the ground scrolls at ×0.6.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.6 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### MB-BASTION-CUBE-07 — Parts and core · MUST

It has three parts as it comes in, all shielding its core: `tower-left`, `tower-right` and
`gatehouse`. The core's guns (the keep turret and the crown rotor) fire the core's volleys and are
the last the player destroys.

**Acceptance criteria**
- Given its design, then its three parts all shield the core.

*Sources: BOSS-12, BOSS-14.*

#### MB-BASTION-CUBE-08 — Stage patterns · MUST

In every stage while they stand, the gatehouse's wall gun drops a straight wall of 5 orange
bullets, side by side, 4.4 px apart, all straight down the screen; the front towers each fire a
burst of 3 red bullets at the player, the two in turn. The core fires:
- stage 0: an aimed magenta bullet;
- stage 1: a fan of 5 straight down the screen, 12° apart, swept;
- stage 2: a burst of 4 at the player;
- stage 3 and after: a ring of 8 from the crown rotor, one bullet a barrel, turning 22.5° at each
  volley (a square grid, then the same turned half a step), and an aimed spread of 3 magenta
  bullets 12° apart.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel (a fight in
  the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-58.*

#### MB-BASTION-CUBE-09 — Angry · MUST

After its transformation it is angry (BOSS-27): its two gatlings fire all out, `boss_rage_rate`
times as often, for `boss_rage_seconds`. It has no angry pattern of its own.

**Acceptance criteria**
- Given its transformation is over, then it is angry and fires only its two gatlings.

*Sources: BOSS-27.*

#### MB-BASTION-CUBE-10 — Transformation · MUST

It transforms once, when both front towers are destroyed (named, so that no part the player can hit
stands on a block as it moves): its four corner blocks slide out and a **gatling** rides out on each
rear tower's roof, on the pod it unfolds there. They shield the core and fire their bursts at the
player, in turn.

**Acceptance criteria**
- Given both front towers destroyed, then it transforms, its blocks slide out and its two gatlings
  are revealed on the rear blocks.

*Sources: BOSS-35, BOSS-36, BOSS-45.*

#### MB-BASTION-CUBE-11 — Death, drops and points · MUST

Its parts drop a weapon bonus half of the time, its gatlings 30 %; it drops a life bonus as a mini
boss (BOSS-57). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/bastion_cube.py` (`_BASTION_CUBE`, `BASTION_CUBE`) unless named;
its model in `src/game/view/bosses/lab/bastion_cube_model.py` and `bastion_cube_blocks.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 3.6 L (radius 61 px) | `stats.size` |
| plinth | 92 px square (`HALF` 46), 10 px high; corner notches from 25 px out | `HALF`, `NOTCH`, `PLINTH_TOP` |
| tiers | 66, 48, 28 px square, tops at 15, 20, 24 px | `TIERS` |
| corner blocks | 21 px square, 14 px high; drum towers radius 7.5 at (±35.5, ±35.5), 23 px high | `CORNER`, `TOWER_AT`, `TOWER_TOP` |
| gatehouse | 24 px wide, out to y -55, 16 px high | `GATE_HALF`, `GATE_FRONT`, `GATE_TOP` |
| core | health 1 000, radius 17 | |
| `tower-left`, `tower-right` | (∓35.5, -35.5), radius 11, health 620, shield, drop 0.5 | on the front blocks |
| tower turrets | 23 px high; 2 barrels 2.9 px apart, bore 1.1, 7 px long; dome radius 4.6 | `TOWER_GUN` |
| `gatehouse` | (0, -43), radius 12, health 720, shield, drop 0.5 | |
| wall gun | (0, -45), 16 px high, fixed; 5 barrels 4.4 px apart, bore 1.1, 6 px long; base radius 10.6 | `WALL_GUN` |
| keep turret (core) | (0, -6), 24 px high; 3 barrels 2.9 px apart, bore 1.1, 7 px long; dome radius 4.8 | `KEEP_GUN` |
| crown rotor (core) | (0, 6), 24 px high; 8 barrels, bore 0.9, 3.4 px long; hub radius 4.4 | `ROTOR` |
| rotor hatch | octagon of radius 6 round (0, 6), the cap 23.6–25.4 px | `armour_region` `rotor-hatch` (`mount`) |
| full health | 4 040 (core 1 000, parts 1 960, gatlings 1 080) | BOSS-54; the L-2 mini boss (Twin Hammerhead) has 4 010 |
| points | 3 500 | |
| ground speed | ×0.6 | |
| stop height | 0.72 | `stopFraction` |
| sway / bob | 60 px over 8 s / 5 px over 4 s | |
| wall | 5 orange at 175 px/s, straight down, every 2.4 s (first 1.6 s) | `volley.fan`, spacing 0 (fixed barrels) |
| tower bursts | 3 red at 185 px/s, 0.12 s apart, every 2.6 s (first 1 s / 2.3 s) | |
| core stage 0 | aimed 1, magenta 190 px/s, every 3 s | keep turret |
| core stage 1 | fan of 5, 12° apart, straight down, every 2.8 s | keep turret, a sweep |
| core stage 2 | burst of 4, 0.13 s apart, every 2.2 s | keep turret |
| core stage 3+ | ring of 8 orange turning 22.5°, every 1.5 s; aimed 3, 12° apart, every 2.4 s | rotor; keep turret |
| weighted fire rate | 4.7 as it comes in, 7.5 after its transformation | BOSS-39 |
| transformation | `tower-left` and `tower-right` destroyed | `transformParts` |
| front blocks (moving region) | x 25..46, y -46..-25 (mirrored); slide from (0, 0, 0) to (±13, -13, 0); no frame | `moving_region`, `slide`; `heights` from 0 |
| rear blocks (moving region) | x 25..46, y 25..46 (mirrored); slide from (0, 0, 0) to (±13, 13, 0); no frame | |
| gatlings | (∓48.5, 48.5) on the rear towers once slid out, radius 8, health 540, pod from 24 to 27.5 px, red; first 1.2 s / 2.0 s | ride the rear blocks |
| neon | coral (1, 0.35, 0.35) | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its full health is about that of the L-2
  mini boss.
- **Not a creature** (see the departure from BOSS-47 above).
- **Silhouette.** The Sky Temple (3-3) also slides corner wedges of a stepped plan out
  diagonally; the Bastion Cube differs as a hard-edged metal cube with four drum towers, curtain
  walls and a gatehouse, and no stair or beast under it.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 530 shots, every one
  from a barrel, along it; it dies at about 74 s.
