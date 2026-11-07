# Throne of Storms

> **Area:** bosses · **Prefix:** `FB-THRONE-OF-STORMS` · **Related:** [common](../common.md),
> [Kite Bulwark](L-15-kite-bulwark.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Throne of Storms is the final boss of Lab level L-15, the climax of the flying fortresses: a
round sky castle on a floating disc of rock. A curtain wall with a drum tower on each of its four
corners rings a ward round the central keep, on whose roof stands a throne under a tall lightning
spire; a storm generator stands on a rock spur at each side, a barbican on the rock's prow and a
rocket loft at its back. It changes character at each phase: a closed siege castle firing aimed
bursts, walls of bullets, lightning lasers and rockets; then, its towers slid out on their rails
(it changes shape, BOSS-45), an expanded fortress whose cannons and fans fill the sky; then, its
curtain wall burst off and the whole castle turned 45° to bring a corner to bear (BOSS-46), a
storm of crossing diagonal lances, gatling bursts and wide fans, its spire crackling with lightning.
It is the hardest boss of the Lab set. Shared rules are in [common](../common.md).

**Departure from BOSS-47 (one Cyber-Organic creature):** on the user's requests (2026-11-06, "drop
the animal looking theme", then "flying fortress theme") this Lab boss is architecture, not a
creature: stone on floating rock, dark metal, rails, coils and neon light lines, no flesh, eyes or
veins.

## Requirements

### Look

#### FB-THRONE-OF-STORMS-01 — Silhouette and size · MUST

Seen from above, at rest, it is a round castle on a round rock 120 px across: a ring of wall with a
drum tower on each diagonal, the round keep in the middle with the throne's tall back and its spire
rising at its rear, a generator tower on a spur at each side (about 4.8 L across all told), the
barbican jutting out on the prow and the loft on the stern. After its first transformation its
towers stand out on girders beyond the rock's rim, the castle's corners spread; after its second its
wall is gone, the bare ward shows round the keep and the whole castle stands turned 45°, a tower
pointing down the screen like a diamond.

**Acceptance criteria**
- Manual validation in the boss viewer: a round castle on a floating rock at rest, its corners
  spread once its towers have slid out, a turned, unwalled diamond after its second transformation.

*Sources: Lab boss request (2026-11-06, "flying fortress theme").*

#### FB-THRONE-OF-STORMS-02 — Rock, keep and throne · MUST

The rock is a jagged disc tapering to a point far below, boulders round its rim, lit crystal seams
down its flanks and four spurs (a prow, a stern and one at each side). Lit rails run out along each
diagonal from under each tower to an end stop on a girder past the rim. The keep is a round,
battered stone drum with lit bands, a parapet ring round its roof; on the roof stands the throne:
the throne gun's dais on its seat, two long armrests lit along their tops, a tall stepped back with
a lit panel on its face, and the lightning spire rising from its crown, a tapering mast with three
lit coils and a lit tip. The generators' bare masts stand on their platforms, and the barbican's and
the loft's foundations and gun pedestals on the prow and the stern (what stays once those parts are
gone).

**Acceptance criteria**
- Manual validation: one sky castle, its rock, keep, throne and spire readable at every phase.

*Sources: BOSS-49, BOSS-52.*

#### FB-THRONE-OF-STORMS-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Front towers** (`tower-left`, `tower-right`, on the front corner towers): each a battlemented
  crown on its tower's drum (a lit band, five merlons), a turret of two barrels side by side
  standing in it (its aimed bursts). The drum and its seat stay on the tower once the crown is
  destroyed.
- **Storm generators** (`generator-left`, `generator-right`, on the side spurs): a stone plinth and
  a coil tower round the mast, three lit coils stacked up it, a crown with four lit insulators, a
  laser turret on top (its lightning lasers, aimed at the player through their warning).
- **Barbican** (`barbican`, on the prow): a squat gatehouse between two round flanking turrets, a lit
  portcullis in its face; on its front the **wall gun**, five barrels side by side on a fixed base,
  all pointing straight down the screen.
- **Rocket loft** (`loft`, on the stern): a long hall with a ribbed roof and lit slits; a block of
  four rocket ports on its roof (its homing rockets).
- **Throne gun** (the core's, on the throne's seat): five barrels side by side on a turret (its
  aimed shots, spreads, fans and bursts).
- **Spire rotor** (the core's): sixteen barrels round a hub on the throne's seat, at the spire's
  foot (its last spiral). Until its last stage it lies under an octagonal hatch with a lit seam; as
  the rotor comes into use the hatch bursts off (BOSS-58), leaving a lit collar, and the rotor rises
  out.

**Acceptance criteria**
- Given its model, then it draws its six parts and every gun mount.

*Sources: BOSS-48, BOSS-58.*

#### FB-THRONE-OF-STORMS-04 — Lights · MUST

The rails, the crystal seams, the keep's bands, the armrests, the throne's panel, the spire's coils
and tip, the towers' bands and rail shoes, the wall's walk, the ward's seam, the generators' coils
and insulators, the portcullis, the loft's slits, the hatch's seam and the lightning glow. Its neon
colour is set magenta (1, 0.3, 0.8); the viewer folds it into the enemy palette (BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are in its neon colour.

*Sources: BOSS-50.*

#### FB-THRONE-OF-STORMS-05 — Its towers, ward and wall · MUST

Its four corner towers are moving pieces (BOSS-45), drawn at rest on the wall's corners: each a
round, battered stone drum with arrow slits, a lit band and two lit rail shoes at its foot; the
front ones end in their crowns' seats, the rear ones in a flat roof with a lit hatch ring. At its
first transformation each slides 16 px out along each axis on its rails, and stays there; they
leave no frame (the rails show where they stood). Its ward and curtain wall are three shed regions
(BOSS-42): the front quarter, the back quarter and the two side quarters (mirrored), each an
annular sector from the keep's foot to the wall's outer face, drawn as plated flagstones with a lit
seam and radial plate lines and, on their rim, a thick stone wall arc with a lit walk round its outer
face and merlons along its top. At its second transformation they burst off, leaving a dark lattice
frame. The hatch over the spire rotor is a shed region of its own (BOSS-58).

**Acceptance criteria**
- Given its design, then its first transformation slides the four towers out, each pair mirrored,
  its cannons riding the rear towers, and its second sheds the three ward regions with the lances
  and the gatling in them (unit tests on the regions).
- Given its model, then it holds together at rest and after each transformation.

*Sources: BOSS-42, BOSS-45, BOSS-52.*

### Behaviour

#### FB-THRONE-OF-STORMS-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then sways slowly
and bobs a little: a mountain in the sky. While it is fought the ground stops (×0).

**Acceptance criteria**
- Given the fight, then the ground eases to a stop and back after it.

*Sources: BOSS-03, BOSS-10.*

#### FB-THRONE-OF-STORMS-07 — Parts and core · MUST

It has six parts as it comes in, all shielding its core: `tower-left`, `tower-right`,
`generator-left`, `generator-right`, `barbican` and `loft`. The core's guns (the throne gun and the
spire rotor) fire the core's volleys and are the last the player destroys.

**Acceptance criteria**
- Given its design, then its six parts all shield the core.

*Sources: BOSS-12, BOSS-13, BOSS-14.*

#### FB-THRONE-OF-STORMS-08 — Stage patterns: siege, storm, tempest · MUST

In every stage while they stand: each front tower fires a burst of 3 red bullets at the player, the
two in turn; the barbican's wall gun drops a straight wall of 5 orange bullets side by side, all
straight down the screen; each generator fires a lightning laser (1.4 s), aimed through its warning,
the two in turn; the loft fires a pair of homing rockets. The core fires:
- stage 0: an aimed magenta bullet;
- stage 1: an aimed spread of 3, 10° apart;
- stage 2: a fan of 7 purple, 12° apart, straight down (swept);
- stage 3: a fan of 5 and a burst of 4 magenta at the player;
- stage 4: a fan of 9 and an aimed spread of 3, 12° apart;
- stage 5: a fan of 11, 10° apart, and a burst of 4 red;
- stage 6 and after: a spiral of 16 from the spire rotor, one bullet a barrel, turning 8° at each
  volley, and a fan of 7.

So the siege (closed) is aimed fire from many guns; the storm (expanded) adds the cannons' heavy
shell spreads to wide fans; the tempest (turned) crosses diagonal lance beams with gatling bursts,
wide fans and, last, the spiral.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel (a fight in
  the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-58.*

#### FB-THRONE-OF-STORMS-09 — Angry · MUST

After each transformation it is angry (BOSS-27): the weapons it has just revealed fire all out,
`boss_rage_rate` times as often (its lances as often as their warning, beam and gap allow), for
`boss_rage_seconds`. It has no angry pattern of its own.

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only the weapons it revealed.

*Sources: BOSS-27.*

#### FB-THRONE-OF-STORMS-10 — First transformation: the castle expands · MUST

It transforms the first time when both front towers are destroyed (named, so that no part the player
can hit stands on a tower as it moves). As an event: the towers strain, then slide out along their
lit rails onto the girders past the rock's rim, the front ones carrying their stumps; the wall's
corners stand open between the wall's ends and the towers. A **cannon** rides out on each rear
tower's roof, on the square pod it unfolds there: a big turret sweeping aimed spreads of three heavy
shells. The fight turns from aimed siege fire to a storm of heavy shells and wide fans.

**Acceptance criteria**
- Given both front towers destroyed, then it transforms, its towers slide out and its two cannons
  are revealed on the rear towers.

*Sources: BOSS-35, BOSS-36, BOSS-45.*

#### FB-THRONE-OF-STORMS-11 — Second transformation: wall down, turned to bear · MUST

It transforms the second time when both generators are destroyed (named). As an event: the curtain
wall and the ward's plating strain, shuddering, and burst off in pieces, baring a dark lattice frame
round the keep, while the whole castle turns 45° (clockwise on screen, BOSS-46), its front right
tower coming round to point straight down the screen; the spire's lightning breaks out (FB-...-12).
Two **lances** unfold in the side quarters and a **gatling** in the front quarter, on the centre
line. Turned with the castle, the lances point diagonally down the screen: two parallel beams cut
diagonal lanes as it sways, crossed by the gatling's bursts and the core's wide fans.

**Acceptance criteria**
- Given both generators destroyed, then it transforms, sheds its ward regions, turns by pi/4 and its
  lances and gatling are revealed.

*Sources: BOSS-35, BOSS-36, BOSS-41, BOSS-42, BOSS-46.*

#### FB-THRONE-OF-STORMS-12 — The spire's lightning · SHOULD

Its spire crackles (a rig of its own model, visual only: nothing in it fires or can be hit). From
the start three short sparks fork round the spire's tip, flickering between two shapes and off. As
its second transformation strains it, and from then on, forked lightning bolts leap from the tip
down to the tops of its four towers (out on their rails by then), each flickering between two
zigzag shapes and off on its own beat, so the storm crackles round the turned castle.

**Acceptance criteria**
- Manual validation in the boss viewer: sparks at the tip from the start, bolts to the four towers
  from its second transformation on.

*Sources: Lab boss request (2026-11-06: "its spire crackles").*

#### FB-THRONE-OF-STORMS-13 — Death, drops and points · MUST

Its parts drop a weapon bonus 60 % of the time, its hidden weapons 30 %, and its core always drops
one (BOSS-57). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/throne_of_storms.py` (`_THRONE_OF_STORMS`, `THRONE_OF_STORMS`)
unless named; its model in `src/game/view/bosses/lab/throne_of_storms_model.py`,
`throne_of_storms_parts.py` and `throne_of_storms_storm.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 5.5 L (radius 93.5 px) | `stats.size` |
| rock | radius 60, its top 4 px high; spurs out to x ±85, y ±72 | `ROCK_R`, `ROCK_TOP`; `SPUR_*` (model) |
| curtain wall | from 41 to 48 px out, 16 px high; the ward's plating 7 px high | `WALL_IN`, `WALL_OUT`, `WALL_TOP`, `WARD_TOP` |
| keep | radius 18, 24 px high; throne back to 44 px; spire at (0, 14) up to 72 px | `KEEP_R`, `KEEP_TOP`, `SPIRE_AT`, `SPIRE_TOP` |
| corner towers | radius 10 at (±32, ±32), 27 px high; slide 16 px out along each axis | `TOWER_AT`, `TOWER_R`, `TOWER_TOP`, `SLIDE_OUT` |
| core | health 5 000, radius 22 | |
| `tower-left`, `tower-right` | (∓32, -32), radius 11, health 1 400, shield, drop 0.6 | on the front towers |
| tower turrets | 27 px high; 2 barrels 3.1 px apart, bore 1.2, 7.5 px long; dome radius 4.8 | `TOWER_GUN` |
| `generator-left`, `generator-right` | (∓70, 2), radius 12, health 1 800, shield, drop 0.6 | |
| generator lasers | 30 px high, on a turret; bore 2.2, 10 px long | `GENERATOR_LASER` |
| `barbican` | (0, -57), radius 12, health 1 600, shield, drop 0.6 | |
| wall gun | (0, -61), 14 px high, fixed; 5 barrels 4.4 px apart, bore 1.1, 6 px long | `WALL_GUN` |
| `loft` | (0, 57), radius 11, health 1 500, shield, drop 0.6 | |
| rocket block | (0, 59), 12 px high, 4 ports | `missile_mount` |
| throne gun (core) | (0, -10), 24 px high; 5 barrels 2.6 px apart, bore 1, 8 px long; dome radius 6 | `THRONE_GUN` |
| spire rotor (core) | (0, 2), 24 px high; 16 barrels, bore 0.7, 3.4 px long; hub radius 5.5 | `ROTOR` |
| rotor hatch | octagon of radius 6.5 round (0, 2) | `armour_region` `rotor-hatch` (`mount`) |
| full health | 22 780 (core 5 000, parts 9 600, cannons 2 880, lances and gatling 5 400) | BOSS-54; the 1-5 final boss (Overlord) has 22 760 |
| points | 16 000 | |
| ground speed | ×0 | |
| stop height | 0.74 | `stopFraction` |
| sway / bob | 24 px over 12 s / 5 px over 6 s | |
| tower bursts | 3 red at 195 px/s, 0.14 s apart, every 2.6 s (first 0.8 s / 2.1 s) | |
| wall | 5 orange at 180 px/s, straight down, every 2.4 s (first 1.6 s) | `volley.fan`, spacing 0 (fixed barrels) |
| generator lasers | 1.4 s beam every 7 s (first 2.5 s / 6 s) | |
| rockets | 2 homing, 24° apart, every 6 s (first 3.5 s) | |
| core stage 0 | aimed 1 magenta at 175 px/s, every 2.6 s | throne gun |
| core stage 1 | aimed 3, 10° apart, every 2.4 s | |
| core stage 2 | fan of 7 purple at 185 px/s, 12° apart, every 2.4 s | a sweep |
| core stage 3 | fan of 5, 12° apart, every 2.2 s; burst of 4 magenta, 0.12 s apart, every 2.6 s | |
| core stage 4 | fan of 9, 12° apart, every 2.4 s; aimed 3, 12° apart, every 2.8 s | |
| core stage 5 | fan of 11, 10° apart, every 2.4 s; burst of 4 red, every 2.4 s | |
| core stage 6+ | spiral of 16 magenta turning 8°, every 1.2 s; fan of 7, every 2.4 s | rotor; throne gun |
| weighted fire rate | 7.7 as it comes in, 10.5 after its first transformation, 14.0 after its second | BOSS-39 |
| first transformation | `tower-left` and `tower-right` destroyed | `transformParts` |
| front towers (moving region) | x 20..44, y -44..-20 (mirrored); slide from (0, 0, 0) to (±16, -16, 0); no frame | `moving_region`, `slide`; `heights` from 4 |
| rear towers (moving region) | x 20..44, y 20..44 (mirrored); slide to (±16, 16, 0); no frame | |
| cannons | (∓48, 48) on the rear towers once slid out, radius 10, health 1 440, pod from 27 to 31 px, red; first 1.2 s / 2.0 s | ride the rear towers |
| second transformation | `generator-left` and `generator-right` destroyed; turns pi/4 | `transformParts`, `turns` [0, pi/4] |
| ward regions | front (bearings -135° to -45°), back (45° to 135°), sides (-45° to 45°, mirrored); 19 to 48 px out; shell frame | `armour_region` `ward-front`, `ward-back`, `ward-side` |
| lances | (∓31, -6), radius 8, health 1 800, pod from 5 to 9 px, magenta; first 1.2 s / 2.6 s | in the side quarters |
| gatling | (0, -31), radius 8, health 1 800, pod from 5 to 9 px, purple; first 1.6 s | in the front quarter, centre line |
| lightning | bolts of 6 legs, kinks 9 % of their length, radius 0.45; sparks 7 px; 13 shape changes a second | `throne_of_storms_storm` |
| neon | magenta (1, 0.3, 0.8) | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its full health is that of the 1-5 final
  boss (Overlord).
- **Not a creature** (see the departure from BOSS-47 above).
- **Lances after the turn.** A lance points down its boss's nose; turned 45° with the castle, its
  beams run diagonally down the screen. That is the intent (a turned castle brings new lines of fire
  to bear), not a fixed lance pointing down the screen as BOSS-40 words it.
- **Silhouette.** The Mesa Fortress (1-3) and the Folding Citadel (L-9) are square fortresses; the
  Throne of Storms is round, on a floating rock with spurs, a throne and a tall spire, and ends as a
  turned diamond.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 1 668 shots and 31
  lasers, every shot from a barrel, along it; it dies at about 146 s.
