# Prism Gate

> **Area:** bosses · **Prefix:** `MB-PRISM-GATE` · **Related:** [common](../common.md),
> [Orbital Foundry](L-6-orbital-foundry.md)

The Prism Gate is the mini boss of the Lab's level L-6: a hollow equilateral triangle of heavy metal
girders, 3.6 L across, one point towards the player, a big faceted crystal emitter on each corner
and a crystal prism hung on cables in its middle. A geometry boss: each corner's crystal fires a
laser along a fixed line, so the three beams fence the playfield into lanes, while the prism's
turret sweeps its fans between them and adds a new pattern at every stage. All three crystals
shield its core. Once both back crystals are gone the housings on its back girder burst off and a
pair of missile racks unfolds. Shared rules are in [common](../common.md).

**Lab boss: in the dev viewer only.** It is listed after the World bosses in the dev viewer's
Bosses list; no level brings it in.

**A machine, not a creature.** On the user's request (2026-11-06: "make 10 more, drop the animal
looking theme"), the Lab's second set departs from BOSS-47's Cyber-Organic creature: the Prism Gate
is built from dark metal girders, plated hubs, glass and crystal, cables and neon light lines, with
no flesh, eyes or veins. Its parts still read as targets (BOSS-48) and its armour still lies over a
darker mechanism (BOSS-49).

## Requirements

### Look

#### MB-PRISM-GATE-01 — Silhouette and size · MUST

Seen from above, the Prism Gate is an open equilateral triangle, 3.6 L across, its nose corner
pointing down the screen: three girders between three heavy hubs, empty between them but for the
prism hung in the middle, which points the other way (its corner to the back). A tall crystal stands
on each hub.

**Acceptance criteria**
- Manual validation in the boss viewer: a hollow triangle of girders, a crystal on each corner and an
  upturned prism in its middle, unlike every other boss (no ring, no hull, no creature).

*Sources: Lab request (2026-11-06: "make 10 more, drop the animal looking theme").*

#### MB-PRISM-GATE-02 — Body · MUST

Each girder is a dark box web with two top chords, a zig-zag of braces between them, riveted plates
on its sides and an ice blue light line deep along its middle. Each hub is a heavy hexagonal node
ringed with light, two claws on its top round the crystal's socket. The prism is an upright crystal
of three faces, pointed at its foot, its edges and a band round its faces lit; a dark metal crown on
its top seats the core's guns, a light ring round it. Two cables run from each hub's top (a
tensioner block there) to the prism's two nearest corners, a light bead on each.

**Acceptance criteria**
- Manual validation: one machine, the prism visibly hung from its corners.

*Sources: Lab request.*

#### MB-PRISM-GATE-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts, the shared models of [common](../common.md) (BOSS-58):
- **Crystal emitters** (`crystal-left`, `crystal-right` at the back corners, `crystal-nose`): each a
  big six-faced crystal leaning a little outwards in its hub's socket, its tip glowing, a light band
  round its widest and two shards at its foot; in front of it, on the hub, a fixed **laser** emitter
  pointing along its beam's line: straight down the screen for the nose, 10° in towards the centre
  line for the back corners, so the three beams cross under the boss.
- **Prism turret** (the core's): a gun turret with three barrels side by side on the front of the
  crown (its fans, aimed spreads and bursts).
- **Prism rotor** (the core's): a rotor with twelve barrels on the back of the crown (its last
  stage's ring). Until then it lies under a hatch, an armoured octagonal cap with a seam of light;
  the hatch bursts off as the rotor comes into use (BOSS-58), leaving a collar, and the rotor rises
  out.

A destroyed crystal leaves its laser's stump on its hub, between the hub's claws.

**Acceptance criteria**
- Given its model, then it draws the three crystals and every gun mount (unit test).

*Sources: Lab request.*

#### MB-PRISM-GATE-04 — Lights · MUST

The girders' light lines, the hubs' rings, the crystals' tips and bands, the prism's edges and band,
the crown's ring and the cables' beads glow. Its neon colour, set ice blue, shows bright green
([common](../common.md), BOSS-50); its crystal glass keeps an ice blue shade (inside BOSS-50's
window).

**Acceptance criteria**
- Given its model, then its lights are bright green.

*Sources: Lab request.*

#### MB-PRISM-GATE-05 — The back housings · MUST

Two armoured housings clad the back girder either side of its middle: bevelled boxes enclosing the
girder, vent slats and a light stripe on top. They are the armour it sheds at its transformation
(BOSS-42): its region, `housings`, is the right housing's outline and its mirror image; it bursts
into plates cracked from that outline and leaves a `shell` frame on the girder. The pair of racks
lies folded inside them, on the girder.

**Acceptance criteria**
- Given its design, then its one transformation sheds the housings and both racks lie in them (unit
  test).
- Given its model, then it draws the housings, and it holds together with and without them (unit
  tests).

*Sources: Lab request, D-254.*

### Behaviour

#### MB-PRISM-GATE-06 — Coming in and moving · MUST

It comes in from the top ([common](../common.md), BOSS-08) to `stopFraction` of the playfield's
height, then drifts slowly from side to side and bobs. While it is fought the ground scrolls at
×0.6.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.6 of the level's speed and back after it.

*Sources: Lab request.*

#### MB-PRISM-GATE-07 — Parts and core · MUST

It has three parts as it comes in, all shielding its core: `crystal-left`, `crystal-right` and
`crystal-nose`. The core's guns (the prism turret and the prism rotor) fire the core's volleys and
are the last the player destroys.

**Acceptance criteria**
- Given its design, then its three parts all shield the core (unit test on its design).

*Sources: Lab request.*

#### MB-PRISM-GATE-08 — Stage patterns · MUST

The crystals fire their lasers in every stage while they stand: the two back ones together (a V
closing under the boss), the nose's between them (splitting the V), each beam along its fixed line.
The core fires, from the prism turret unless named:
- stage 0: fans of 5 blue bullets 12° apart, one turned 20° to the boss's left, the next 20° to its
  right, each along a lane the beams leave;
- stage 1: an aimed spread of 3 magenta bullets 10° apart and a fan of 7 straight down;
- stage 2: a burst of 4 at the player, and fans of 5 turned 30° either way in turn;
- stage 3 (all three crystals gone): a ring of 12 green bullets from the prism rotor turning 11° a
  volley (a spiral, its first ring), and a single aimed shot.

Its turret sweeps its fans and spreads one bullet at a time (BOSS-58).

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys (BOSS-21 unit tests).

*Sources: Lab request.*

#### MB-PRISM-GATE-09 — Angry · MUST

It is angry after its transformation: the two racks it revealed fire all out for
`boss_rage_seconds`, `boss_rage_rate` times as often and `boss_rage_missiles` times as many missiles,
instead of its stage's pattern ([common](../common.md), BOSS-27).

**Acceptance criteria**
- Given its transformation is over, then it is angry and fires only its two racks (unit test).

*Sources: Lab request, D-256.*

#### MB-PRISM-GATE-10 — Transformation · MUST

It transforms once, when both back crystals (`crystal-left` and `crystal-right`) are destroyed: the
housings on its back girder burst off, baring the girder under a dark metal frame, and two missile
**racks** unfold on the girder either side of its middle. They shield the core and fire pairs of
homing missiles, in turn.

**Acceptance criteria**
- Given both back crystals destroyed, then it transforms and its two racks are revealed (unit test on
  its thresholds).

*Sources: Lab request, D-221, D-229.*

#### MB-PRISM-GATE-11 — Death, drops and points · MUST

Its crystals drop a weapon bonus half of the time, its racks 30 %; it drops a life bonus as a mini
boss ([common](../common.md), BOSS-57). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: Lab request.*

## Tunable values

All in `src/game/config/bosses/lab/prism_gate.py` (`_PRISM_GATE`, `PRISM_GATE`); its model in
`src/game/view/bosses/lab/prism_gate_model.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 3.6 L (radius 61.2 px) | `stats.size` |
| gate | hubs 48 px from the centre: nose (0, -48), back (∓41.6, 24); hub radius 10, top 11 px; girders 9 px across, 2 to 9 px high | `GATE_RADIUS`, `HUB_TOP`, `GIRDER_*` |
| prism | three faces, corners 18 px out (one at the back), 11 to 23 px high, pointed down to 6 px; crown radius 10.5, top 25.5 px | `PRISM_*`, `CROWN_*` |
| core | health 900, radius 13 | `coreHealth`, `coreRadius` |
| `crystal-left`, `crystal-right` | the back corners, radius 13, health 520, shield, drop 0.5 | `LEFT_AT`, `RIGHT_AT` |
| `crystal-nose` | the nose corner, radius 13, health 600, shield, drop 0.5 | `NOSE_AT` |
| crystal lasers | fixed emitters on the hubs, 11 px high, 8 px out along their beams; bore 2, 8 px long, base 4; nose 0°, back corners ±10° in | `CORNER_LASER`, `LASER_OUT`, `FLANK_TILT` |
| prism turret (core) | (0, -5), 25.5 px high; 3 barrels 2.6 px apart, bore 1, 6.5 px long; dome 4.5 | `PRISM_GUN`, `TURRET_AT` |
| prism rotor (core) | (0, 5), 25.5 px high; 12 barrels, bore 0.7, 2.6 px long; hub 3.6 | `PRISM_ROTOR`, `ROTOR_AT` |
| rotor hatch | octagon of radius 5.5 round (0, 5) on the crown; bursts as the rotor comes into use | `armour_region` `rotor-hatch` (`mount`) |
| full health | 3 500 (900 + 2 × 520 + 600 + 2 × 480) | BOSS-54; the Reef Warden's (1-1) is 3 200 |
| points | 3 500; 350 a part | |
| ground speed | ×0.6 | |
| stop height | 0.72 | `stopFraction` |
| sway / bob | 45 px over 10 s / 5 px over 4.5 s | |
| back lasers | 1.6 s every 7 s, together (first 1.5 s) | |
| nose laser | 1.4 s every 6 s (first 4.5 s) | |
| core stage 0 | fans of 5, 12° apart, blue 175 px/s, turned -20° and +20°, every 3.2 s each (first 1 s / 2.6 s) | sweeps |
| core stage 1 | aimed 3, 10° apart, magenta 185 px/s, every 2.2 s; fan of 7, 12° apart, every 3 s | |
| core stage 2 | burst of 4, 0.13 s apart, every 2 s; fans of 5 turned -30° and +30°, every 2.8 s each | |
| core stage 3 | ring of 12 green 165 px/s, turning 11°, every 1.4 s; aimed 1 every 2.4 s | prism rotor; turret |
| weighted fire rate | 6.7 as it comes in, 8.2 after its transformation | BOSS-39 |
| angry | the revealed racks, BOSS-27 | `boss_build.angry_pattern` |
| transformation | `crystal-left` and `crystal-right` destroyed | `transformParts` |
| housings (shed) | from (7, 17) to (31, 31) and its mirror image, `shell`; 9–13.5 px (the housing drawn down to 1.5 px round the girder) | `HOUSING`, `HOUSING_HEIGHTS` |
| racks | (∓19, 24), radius 7, health 480, pod on the girder from 9 px to 12 px, blue; first 1.2 s / 2.0 s; 2 homing missiles 30° apart every 6 s | `hidden_weapon`, `RACK_AT` |
| neon | ice blue (0.4, 0.85, 1), shown green | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** It is registered among the game's boss kinds and models only so that the dev viewer
  lists it; no world's boss table names it.
- **Fixed lasers as fences.** Its lasers never aim: the two back beams converge 10° each and cross
  the nose's beam about 235 px under the boss's back corners, so the player reads three fixed lines
  and picks a lane between them; the back pair and the nose fire at different times.
- **Health.** Its full health is in line with the 1-1 mini boss's (the Reef Warden, 3 200), for a
  first boss of the Lab's second set.
- **Check (2026-11-06).** A simulated fight breaking a part every 12 s: 466 shots (and 9 lasers),
  every one leaving a barrel's tip along it, dead at 74 s. Its model holds together at rest and after
  its transformation, about 3 100 triangles with its gun mounts (BOSS-53: 4 000).
