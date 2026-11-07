# Iron Lighthouse

> **Area:** bosses · **Prefix:** `MB-IRON-LIGHTHOUSE` · **Related:** [common](../common.md),
> [Skyport Hub](L-22-skyport-hub.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Iron Lighthouse is the mini boss of Lab level L-22: a gigantic flying lighthouse. A round
riveted iron platform, held up by a ring of four ducted propellers under its rim, carries a tall
striped lighthouse tower (its gallery rail, its lantern room and the revolving lens in it), two
whitewashed keeper's cottages on its front, a landing stage at its bow, an iron buttress either
side of the tower and a dynamo house at its back. Its lantern's beam is a fixed laser straight down
the screen; its buttresses' casemates fire fixed rows down and out. It comes in with three guns,
and more rise out of its cottages and its landing stage as its parts fall; once both buttresses are
gone the deck leaves they stood on drop open like trapdoors and an orb rises out of each well.
Shared rules are in [common](../common.md).

**Not a creature.** BOSS-47 asks for a Cyber-Organic creature; this Lab boss departs from it on the
user's requests (2026-11-06: "drop the animal looking theme", then "10 more gigantic flying
fortress, add non rotating guns too, don't add too many start guns, 3 max, then more appear when
they are destroyed"): it is a machine of riveted iron, painted bands and glass with lamp-yellow
light lines, no flesh, eyes or limbs.

## Requirements

### Look

#### MB-IRON-LIGHTHOUSE-01 — Silhouette and size · MUST

Seen from above it is a round iron platform 76 px across, the lips of four propeller ducts showing
round its rim (at 50°, 130°, 230° and 310°), a jetty jutting 8 px out of its bow, and in its middle,
a little behind its centre, the round lighthouse tower rising 31 px to its gallery and 41 px to
its dome's finial. Seen from the side, the platform's underside is a ribbed cone down to a keel hub
18 px under its deck.

**Acceptance criteria**
- Manual validation in the boss viewer: a lighthouse on a flying platform, unlike any other boss.

*Sources: Lab boss request (2026-11-06).*

#### MB-IRON-LIGHTHOUSE-02 — Platform, tower and cottages · MUST

Its deck is riveted iron plating (seams with rows of rivets, a ring of plates round the tower's
foot, a lit line round its rim and a dark band under it). The tower (its core) tapers from 9.5 px
round at its foot to 6 px at its neck in five painted bands, pale and dark in turn, a lit door and
windows climbing it; corbels flare to the gallery's floor, a rail round it with a lit top; the
lantern room above is dark glass between eight iron mullions, a lit sill, an iron roof plate, the
dome over it. The two keeper's cottages on its front are whitewashed, slate-roofed (gabled), with a
lit door, windows and a chimney; a paved walk runs from the tower's door between them to the bow.
The landing stage at the bow carries a davit (mast, jib and hook block) and its gun's hatch.

**Acceptance criteria**
- Manual validation: one machine, its platform, tower and cottages readable from above.

*Sources: BOSS-49, user request (2026-11-06).*

#### MB-IRON-LIGHTHOUSE-03 — Its parts · MUST

- **Buttresses** (`buttress-left`, `buttress-right`): a riveted iron casemate housing on each side
  leaf, its fixed gun on top, a flying arch of two girders up to the tower's flank, braced to the
  deck, a lit seam and a warning lamp. Each stands on a dark plinth on its leaf, which stays (with
  the gun's stump) once the buttress is destroyed.
- **Dynamo house** (`dynamo`, no gun): the engine that lights the lamp, at the platform's back: a
  riveted house, its big flywheel in a lit slot in its roof, two smoke stacks with lit bands, lit
  windows, a conduit to the tower's foot. Its loss brings out new guns (MB-IRON-LIGHTHOUSE-08).

**Acceptance criteria**
- Given its model, then it draws its three parts and every gun mount.

*Sources: BOSS-48, BOSS-58, lab-brief round 5 (gunless parts).*

#### MB-IRON-LIGHTHOUSE-04 — Lights and its lens · MUST

Its windows, door, seams, rim, rails, ridge lines and lamps glow. Its neon colour, lamp yellow
`[1, 0.95, 0.5]`, shows bright yellow (BOSS-50). In its lantern a revolving lens (prism slats and
two bull's-eye panels) turns, two flat flares of light sweeping round over its gallery rail like a
lighthouse's beams: slowly as it comes in, twice as fast once it has transformed. The lens is on a
rig of the model's own (D-228): it is not hit and fires nothing (the beam that hurts is the lamp,
MB-IRON-LIGHTHOUSE-07).

**Acceptance criteria**
- Given its model, then its lights are bright yellow.
- Manual validation: the lens's flares sweep round, faster after the transformation.

*Sources: BOSS-50, BOSS-51.*

#### MB-IRON-LIGHTHOUSE-05 — Its deck leaves · MUST

The platform's two side segments, outside `x = ±18` between `y = -12` and `y = 21` out to the rim,
are moving pieces (BOSS-45): riveted plating with seams, a lit rim line, the hinge's barrel and its
lit knuckles along their inner edge, ribs underneath. Each is drawn flat (the deck as it comes in)
and at its transformation drops 96° about its hinge (along the boss, at the deck's top) to hang
open under the platform, the left one the right one's mirror image. Each leaves its well's dark
floor (a `shell` frame).

**Acceptance criteria**
- Given its design, then its transformation moves its two leaves, mirrored (unit tests on the
  moving regions).
- Given its model, then it holds together at rest and once they have dropped.

*Sources: BOSS-42, BOSS-45, BOSS-52.*

### Behaviour

#### MB-IRON-LIGHTHOUSE-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then drifts: a slow
sway, a bob. While it is fought the ground scrolls at ×0.4. Its four propellers spin in their ducts
(the model's rig), harder as its leaves drop (straining to stay up), and stay faster after.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.4 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### MB-IRON-LIGHTHOUSE-07 — Gun mounts · MUST

Every shot leaves one of its gun mounts (BOSS-58). Fixed mounts (no turret) fire along their
barrels only:
- **Casemates** (on the buttresses, fixed): three barrels side by side on each, pointing 32° out
  from straight down (the left one to the screen's left).
- **Lamp** (the core's, fixed): a laser emitter in the lantern room, pointing straight down the
  screen.
- **Cottage turrets** (the core's, one on each cottage): two barrels side by side. Each lies under
  its cottage's slate roof, a hatch: the roof bursts off as the turret first comes into use.
- **Bow gun** (the core's, fixed, at the landing stage): four barrels side by side pointing straight
  down, under an armoured octagonal lid that bursts as it first comes into use.
- **Lantern rotor** (the core's): twelve barrels round a hub on the lantern's roof, under the dome,
  which bursts off (leaving an iron collar) as it first comes into use.

**Acceptance criteria**
- Given its model, then every mount is drawn from its config numbers; given a fight in the
  simulation, then every shot leaves a barrel along it.

*Sources: BOSS-29, BOSS-58, user request (2026-11-06: "add non rotating guns too").*

#### MB-IRON-LIGHTHOUSE-08 — Stage patterns: guns rise as parts fall · MUST

Parts' volleys, while they stand: each casemate fires a row of three orange bullets along its
barrels every 2.6 s; the dynamo fires nothing. The core fires, at every stage, the lamp's laser
(every 6.5 s, 1.6 s beam), and:
- stage 0: nothing more. **Guns out: 3** (the lamp and both casemates, all fixed).
- stage 1: the cottage turrets rise out of their roofs: an aimed magenta pair 8° apart (left), a
  burst of 3 at the player (right). Guns out: 4 (a buttress lost first) or 5 (the dynamo first).
- stage 2: the bow gun rises: a row of four red bullets straight down every 2.4 s. Guns out: 5 to 6
  (6 with the orbs, if both buttresses are gone).
- stage 3 (all three parts gone): the lantern rotor rises out of the dome: a ring of 12 turning 15°
  at each volley (a spiral), every 1.5 s. Guns out: 7 (with the orbs).

Every lost part brings at least one new gun out; every stage's pattern differs from the last.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys and its new mount rises; each shot
  leaves a barrel (a fight in the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-58, user request (2026-11-06: "then more appear when they are
destroyed").*

#### MB-IRON-LIGHTHOUSE-09 — Angry · MUST

After its transformation it is angry (BOSS-27): its two orbs fire all out for `boss_rage_seconds`.
It has no angry pattern of its own.

**Acceptance criteria**
- Given the transformation is over, then it is angry and fires only its orbs.

*Sources: BOSS-27.*

#### MB-IRON-LIGHTHOUSE-10 — Its transformation: the trapdoors drop · MUST

It transforms when both buttresses are destroyed (named, BOSS-36), whatever else is lost: its two
deck leaves strain, then drop open about their hinges (MB-IRON-LIGHTHOUSE-05), the buttresses'
stumps and plinths going down with them, its propellers spinning up; an **orb** unfolds out of
each open well (at `(±28, 3)`, on the well's floor): ten barrels round a hub, firing turning rings
of 10. They shield the core. The fight turns from fixed rows and a straight beam (lanes to hide
in) to rings filling the screen from its flanks.

**Acceptance criteria**
- Given both buttresses destroyed, then it transforms, its leaves drop and its two orbs are
  revealed in the wells.

*Sources: BOSS-35, BOSS-36, BOSS-45.*

#### MB-IRON-LIGHTHOUSE-11 — Never easier, death, drops and points · MUST

Its weighted fire rate (BOSS-39) goes up at its transformation (about 3.5 as it comes in, 12.4
after). Its parts drop a weapon bonus half the time, its orbs 30 % (BOSS-57). It scores the points
of Tunable values.

**Acceptance criteria**
- Given its design, then its fire rate after its transformation is above the one as it comes in,
  and its drop chances and points are those of Tunable values.

*Sources: BOSS-39, BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/iron_lighthouse.py` (`_IRON_LIGHTHOUSE`, `IRON_LIGHTHOUSE`);
its model in `src/game/view/bosses/lab/iron_lighthouse_model.py`, `iron_lighthouse_parts.py` and
`iron_lighthouse_rig.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 3.6 L (radius 61.2 px) | `stats.size` |
| platform | radius 38, deck 2 → 6 px | `PLATFORM_R`, `DECK_LOW`, `DECK` |
| tower | at (0, 6), radius 9.5 → 6, gallery 30 px, lantern roof 37 px | `TOWER_*`, `GALLERY`, `LANTERN_TOP` |
| deck leaves | `x ≥ 18`, `-12 ≤ y ≤ 21`, drop 96° | `LEAF_X`, `LEAF_Y`, `LEAF_DROP` |
| core health | 1500 | `coreHealth` |
| buttresses | (±27, 4), radius 10, health 650 each | casemates at (±30, -2), 10 px high, ±32° |
| dynamo | (0, 28), radius 10, health 750, no gun | |
| orbs | (±28, 3), radius 8, health 600, firsts 1.2 / 2.0 s | 0.8 of the sturdiest part |
| full health | 4750 | core + parts + orbs (BOSS-54) |
| points | 3800 | `points` |
| motion | stop 0.72, sway 46 px / 9 s, bob 5 px / 4.4 s, ground ×0.4 | |
| lamp | laser every 6.5 s, 1.6 s beam | `LAMP_BEAM` |
| casemates | rows of 3 orange (170 px/s), every 2.6 s | |
| cottages | aimed pair 8° (2.6 s), burst of 3 (2.8 s), magenta 180 px/s | `COTTAGES` |
| bow gun | row of 4 red (185 px/s), every 2.4 s | `BOW` |
| lantern rotor | ring of 12, 15° turn, every 1.5 s, orange 160 px/s | |
| propellers | 4 blades, 11 rad/s, 24 flat out | `iron_lighthouse_rig` |
| lens | 1.3 rad/s, 2.6 once transformed | `iron_lighthouse_rig` |

## Implementation report

- Config, model (core, parts and armour drawings, rig), registration at the `# LAB L-22` markers.
- Simulated fight (a part broken every 12 s): every shot leaves a barrel (0 off), it dies at about
  74 s.
- Guns out per stage checked in the simulation (both destruction orders): 3 → 4/5 → 5/6 → 7.
