# Folding Citadel

> **Area:** bosses · **Prefix:** `FB-FOLDING-CITADEL` · **Related:** [common](../common.md),
> [Lattice Node](L-9-lattice-node.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Folding Citadel is the final boss of Lab level L-9: a flat, square fortress folded shut like an
origami box. Four great wall panels hinged on the edges of its square base lean in over its
courtyard round a stepped central keep, an octagonal tower at each corner. Closed, it is compact
(2.6 L across) and fires tight, aimed volleys; at its first transformation its panels swing open
outward like a flower unfolding (it changes shape, BOSS-45), and it sprawls 4.5 L across, firing
wide fans and missiles. Shared rules are in [common](../common.md).

**Not a creature.** BOSS-47 asks for a Cyber-Organic creature; this Lab boss departs from it on the
user's request (2026-11-06, "drop the animal looking theme"): it is architecture of dark metal
panels, plates, hinges and neon light lines, with no flesh, eyes or limbs.

## Requirements

### Look

#### FB-FOLDING-CITADEL-01 — Silhouette and size · MUST

Seen from above, at rest, it is a square box 88 px (2.6 L) across between its hinges, its four
trapezoid wall panels leaning in at 50° from the ground, their sides meeting along the box's
diagonals like the flaps of a folded paper box, the top of its keep showing through the square
opening their tips leave; an octagonal tower stands out at each corner. Once open, its panels lie
flat round the base like the petals of a flower, about 4.5 L across.

**Acceptance criteria**
- Manual validation in the boss viewer: a closed square box at rest, a flat cross-shaped flower
  once open, unlike any other boss.

*Sources: Lab boss request (2026-11-06).*

#### FB-FOLDING-CITADEL-02 — Base, keep and towers · MUST

Its base is a square deck, its edges the panels' hinges, with three hinge knuckles along each edge,
lit strips from the keep's foot out to each hinge's middle, grated bays at its back corners and
vents beside the keep (the courtyard, bared once the panels are open). The keep is two stepped
square blocks, a lit band and window slits round the lower one, a lit band round the upper one, a
pinnacle at each corner of its roof, the seat of its fan turret on its front and the rotor's well
under a hatch behind it. Each corner tower is an octagonal, tapering tower on a plinth, a lit ring
near its top, braced to the base's corner by a buttress.

**Acceptance criteria**
- Manual validation: one fortress, its keep and towers readable at rest and open.

*Sources: BOSS-49, user request (2026-11-06).*

#### FB-FOLDING-CITADEL-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Wall guns** (`wall-left`, `wall-right`): each on an octagonal sponson jutting from a side
  panel's outer face, braced to it by two struts: an armoured, lit cowl round a twin-barrelled
  turret (its aimed pairs).
- **Bastions** (`bastion-left`, `bastion-right`, on the front towers): an armoured octagonal
  cupola, lit, round a three-barrelled turret (its bursts).
- **Towers** (`tower-left`, `tower-right`, on the rear towers): the same cupola with four lit fins
  round a laser turret (its aimed lasers, BOSS-31).
- **Keep turret** (the core's, on the keep's front): five barrels side by side (its aimed shots,
  bursts and fans).
- **Keep rotor** (the core's, on the keep's roof): sixteen barrels round a hub (its last ring).
  Until its last stage it lies under an octagonal hatch with a lit seam; as the rotor comes into use
  the hatch bursts off (BOSS-58), leaving a collar, and the rotor rises out.

**Acceptance criteria**
- Given its model, then it draws its six parts and every gun mount.

*Sources: BOSS-48, BOSS-58.*

#### FB-FOLDING-CITADEL-04 — Lights · MUST

The fold lines on its panels' outer faces (from each hinge's ends and middle to the tip: the
origami creases), the creases and the tip lip of their inner faces, the strips and bands of its
base and keep, the rings of its towers and cupolas glow. Its neon colour, set orange, shows bright
yellow (BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright yellow.

*Sources: BOSS-50.*

#### FB-FOLDING-CITADEL-05 — Its panels change shape · MUST

Its four wall panels are moving pieces (BOSS-45), each drawn folded up as it rests: a thick plated
slab, three armour plates on its outer face, ribs, rails and dark bays on its inner face; the side
panels carry the wall guns' sponsons outside and the racks' beds inside. At its first
transformation each swings 130° about its hinge (the side ones about the boss's length, the front
and back ones across it) to lie flat open, its inner face up, and stays so. They leave no frame. The
front courtyard's plating and the keep's rotor hatch are shed regions (FB-FOLDING-CITADEL-11,
BOSS-58).

**Acceptance criteria**
- Given its design, then its first transformation moves its four panels, the side ones mirrored,
  and its racks ride the side panels (unit tests on the moving regions).
- Given its model, then it draws each panel, and it holds together at rest and once they have
  moved.

*Sources: BOSS-42, BOSS-45, BOSS-52.*

### Behaviour

#### FB-FOLDING-CITADEL-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then sways slowly
and bobs a little: a heavy, slow fortress. While it is fought the ground scrolls at ×0.3.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.3 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### FB-FOLDING-CITADEL-07 — Parts and core · MUST

It has six parts as it comes in, all shielding its core: `wall-left`, `wall-right`,
`bastion-left`, `bastion-right`, `tower-left` and `tower-right`. The core's guns (the keep turret
and rotor) fire the core's volleys and are the last the player destroys.

**Acceptance criteria**
- Given its design, then its six parts all shield the core.

*Sources: BOSS-12, BOSS-13, BOSS-14.*

#### FB-FOLDING-CITADEL-08 — Stage patterns: closed and tight, then open and wide · MUST

In every stage while they stand, each wall gun sweeps an aimed pair of red bullets 5° apart, the
two in turn; each bastion fires bursts of 3 orange bullets at the player; each rear tower fires an
aimed laser (its turret following the player through its warning line), the two in turn. The core
fires, from tight to wide:
- stage 0: an aimed red bullet;
- stage 1: an aimed spread of 3, 6° apart;
- stage 2: a fan of 7 orange bullets, 12° apart, straight down;
- stage 3: a fan of 5, 12° apart, and an aimed red bullet;
- stage 4: a fan of 9, 12° apart, and a burst of 3;
- stage 5: a fan of 11 magenta bullets, 10° apart, and an aimed spread of 3, 12° apart;
- stage 6 (all six parts gone): a ring of 16 from the keep rotor, turning 9° at each volley (a
  spiral), and a fan of 7 red bullets.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel (a fight in
  the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-58.*

#### FB-FOLDING-CITADEL-09 — Angry · MUST

After each transformation it is angry (BOSS-27): after the first its two racks fire all out (three
times the missiles), after the second its batteries and gatling, for `boss_rage_seconds`. It has no
angry pattern of its own.

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only the weapons it revealed.

*Sources: BOSS-27.*

#### FB-FOLDING-CITADEL-10 — First transformation: it unfolds · MUST

It transforms the first time when both wall guns are destroyed (named, so that no part the player
can hit stands on a panel as it moves): its four panels swing open flat (FB-FOLDING-CITADEL-05) and
a missile **rack** rides in on each side panel's inner face, on the pod it unfolds on its bed,
firing pairs of homing missiles. They shield the core.

**Acceptance criteria**
- Given both wall guns destroyed, then it transforms, its panels swing open and its two racks are
  revealed on the side panels.

*Sources: BOSS-35, BOSS-36, BOSS-45.*

#### FB-FOLDING-CITADEL-11 — Second transformation · MUST

It transforms the second time when both bastions are destroyed (named): the heavy plating of its
front courtyard (four plates with lit seams, bared since its panels opened) bursts off (`shell`
frame), and a **battery** unfolds either side of the courtyard, sweeping wide fans of 7 straight
down, and a **gatling** on the centre line between them, firing bursts at the player. They shield
the core.

**Acceptance criteria**
- Given both bastions destroyed, then it transforms, its courtyard plating bursts and its two
  batteries and gatling are revealed.

*Sources: BOSS-35, BOSS-36, BOSS-41, BOSS-42.*

#### FB-FOLDING-CITADEL-12 — Never easier · MUST

Its weighted fire rate (BOSS-39) goes up at each transformation.

**Acceptance criteria**
- Given its design, then its weighted fire rate as it comes in, after its first and after its second
  transformation goes up (unit test).

*Sources: BOSS-39.*

#### FB-FOLDING-CITADEL-13 — Death, drops and points · MUST

Its parts drop a weapon bonus 60 % of the time, its hidden weapons 30 %, its core always (BOSS-57).
It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/folding_citadel.py` (`_FOLDING_CITADEL`, `FOLDING_CITADEL`);
its model in `src/game/view/bosses/lab/folding_citadel_model.py` and `folding_citadel_panels.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 4.5 L (radius 76.5 px) | `stats.size` |
| base | 88 px square (hinges at ±44), deck 0–4 px | `BASE`, `HINGE_H` |
| panels | 32 px long, 3 px thick; outer edge 46.9 px (half 23.4); folded 130° up at rest (tips 23.4 px from the centre, 28.5 px high) | `PANEL_LENGTH`, `PANEL_THICK`, `FOLD` |
| keep | 34 px square to 19 px, 27 px square to 30 px | `KEEP_HALF`, `KEEP_TOP` |
| towers | (±53, ±53), radius 9, 16 px high | `TOWER_AT`, `TOWER_RADIUS`, `TOWER_TOP` |
| core | health 4 000, radius 20 | |
| `wall-left`, `wall-right` | (∓39, 0) on the side panels' sponsons, radius 11, health 1 200, shield, drop 0.6 | |
| `bastion-left`, `bastion-right` | (∓53, -53), radius 11, health 1 400, shield, drop 0.6 | |
| `tower-left`, `tower-right` | (∓53, 53), radius 11, health 1 550, shield, drop 0.6 | |
| wall guns | 19 px high; 2 barrels 2.9 px apart, bore 1.1, 7.5 px long; dome radius 4.5 | `WALL_GUN` |
| bastion turrets | 20.5 px high; 3 barrels 2.9 px apart, bore 1.1, 7.5 px long; dome radius 5 | `BASTION_GUN` |
| tower lasers | 20.5 px high; turret, bore 2.2, 10 px long | `TOWER_LASER` |
| keep turret (core) | (0, -9), 30 px high; 5 barrels 2.6 px apart, bore 1, 8 px long; dome radius 6.8 (to cover its row) | `KEEP_GUN` |
| keep rotor (core) | (0, 7), 30 px high; 16 barrels, bore 0.7, 3.4 px long; hub radius 5.5 | `KEEP_ROTOR` |
| rotor hatch | octagon of radius 7 round (0, 7) | `armour_region` `rotor-hatch` (`mount`) |
| panels (moving regions) | outlines as drawn, folded up: the side panel x 23.4..44; swings 130° about their hinges (`along` at (±44, 0, 4), `across` at (0, ±44, 4)); no frame | `moving_region` `panel` (mirrored), `panel-front`, `panel-back` |
| racks | (∓62, 0) on the open side panels, radius 9, health 1 240, pod 4–7 px; first 1.2 s / 2.0 s | ride the side panels |
| court (armour) | x -40..40, y -41..-19, 4–7 px; `shell` frame | form 2 |
| batteries | (∓24, -31), radius 9, health 1 550, pod 4–8 px, red; first 1.2 s / 2.0 s | in the court |
| gatling | (0, -31), radius 8, health 1 550, pod 4–8 px, magenta; first 1.6 s | in the court, centre line |
| full health | 19 430 (core 4 000, parts 8 300, racks 2 480, batteries and gatling 4 650) | BOSS-54; the Refinery Titan's is 19 210 |
| points | 14 000 | |
| ground speed | ×0.3 | |
| stop height | 0.73 | `stopFraction` |
| sway / bob | 26 px over 11 s / 4 px over 5 s | |
| wall guns' pairs | aimed 2, 5° apart, red 190 px/s, every 1.9 s (first 0.8 s / 1.75 s) | sweeps |
| bastions' bursts | 3, 0.14 s apart, orange 180 px/s, every 2.6 s (first 1.2 s / 2.5 s) | |
| towers' lasers | 1.4 s every 7.5 s (first 2.5 s / 6.25 s) | turrets |
| core stage 0 | aimed 1, red, every 2.6 s | keep turret |
| core stage 1 | aimed 3, 6° apart, every 2.4 s | keep turret |
| core stage 2 | fan of 7, 12° apart, orange, every 2.4 s | keep turret |
| core stage 3 | fan of 5, 12° apart, every 2.2 s; aimed 1 every 2.8 s | keep turret |
| core stage 4 | fan of 9, 12° apart, every 2.6 s; burst of 3, 0.14 s apart, every 2.8 s | keep turret |
| core stage 5 | fan of 11, 10° apart, magenta 175 px/s, every 2.4 s; aimed 3, 12° apart, every 2.6 s | keep turret |
| core stage 6 | ring of 16 turning 9°, orange, every 1.3 s; fan of 7, 12° apart, red, every 2.6 s | rotor; keep turret |
| weighted fire rate | 6.9 as it comes in, 8.7 after its first transformation, 16.8 after its second | BOSS-39 |
| transformations | `wall-left` and `wall-right`; then `bastion-left` and `bastion-right` | `transformParts` |
| neon | orange (1, 0.6, 0.1), shown yellow | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its full health is that of the 1-4 final boss
  (Refinery Titan, 19 210).
- **Not a creature** (see the top): BOSS-47's creature look does not apply; BOSS-48 to BOSS-53 do.
- **Drawn folded.** The panels are drawn as they rest, folded up, and swing open: a panel drawn
  open flat would have its outer face pointing down in the drawing, and the models drop the faces
  the camera never sees from above before posing them.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 2 005 shots and 9
  lasers, every one from a barrel, along it; it dies at about 146 s.
