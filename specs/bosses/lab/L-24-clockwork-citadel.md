# Clockwork Citadel

> **Area:** bosses · **Prefix:** `FB-CLOCKWORK-CITADEL` · **Related:** [common](../common.md),
> [Bunker Saucer](L-24-bunker-saucer.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Clockwork Citadel is the final boss of Lab level L-24: a gigantic flying clock-tower fortress.
A square stone citadel on a stepped plinth, a round bell tower at each corner, a gatehouse at its
front, and on its roof a huge clock face whose minute hand sweeps round; gear trains turn on steel
shelves on its flanks, great wheels mesh into them, and a great pendulum swings out of its back
wall. It comes in with only three guns (the front belfries' turrets and the gatehouse's fixed noon
gun): its gear trains, pendulum and minute hand carry none, but each of its parts that falls brings
a new gun out of the citadel. Once both gear trains are gone its great wheels unmesh and slide out
of its flanks, an orb on each; once the pendulum and the hand are gone its clock face splits down
the middle, its halves slide apart with a mortar on each, and a lance rises out of the movement.
Shared rules are in [common](../common.md).

**Not a creature.** BOSS-47 asks for a Cyber-Organic creature; this Lab boss departs from it on the
user's requests (2026-11-06: "drop the animal looking theme", "flying fortress theme", then "10
more gigantic flying fortress, add non rotating guns too, don't add too many start guns, 3 max,
then more appear when they are destroyed"): it is architecture and clockwork of stone, steel and
brass with warm light lines, no flesh, eyes or limbs.

## Requirements

### Look

#### FB-CLOCKWORK-CITADEL-01 — Silhouette and size · MUST

Seen from above it is a square citadel 96 px across its walls (106 across its plinth), a round
tower 22 px across at each corner, a gatehouse jutting 13 px out of its front, gear-train shelves
and wheel rails jutting out of its flanks and the pendulum swinging 28 px out behind it: about 170
px across (5 L). Its walls are dressed stone with lit slits (its charge lights) and a lit band,
crenellated parapets along their tops; a lit band runs round its plinth, an inverted step under it.

**Acceptance criteria**
- Manual validation in the boss viewer: a square clock-tower fortress, unlike any other boss.

*Sources: Lab boss request (2026-11-06).*

#### FB-CLOCKWORK-CITADEL-02 — The clock · MUST

The clock face (68 px across) lies on its roof in two halves (moving pieces, FB-CLOCKWORK-CITADEL-11):
dark enamel in a brass bezel, a brass chapter ring, lit hour bars (doubled at twelve, three, six
and nine), brass dots between them and latch bars along their cut edge. Under it is the movement in
a round pit: a dark floor, a lit ring round its wall, brass wheels meshing, the brass centre boss
the hands turn on and the steel arbor over it. The hour hand (the model's rig, not hit) turns on
the arbor's top a twelfth as fast as the minute hand; two gear trains on the roof's flanks and two
on its back turn with the clock (the rig), the flank ones stopping once the great wheels unmesh.

**Acceptance criteria**
- Manual validation: a clock face with its hands turning; the movement shows once it splits.

*Sources: user request (2026-11-06).*

#### FB-CLOCKWORK-CITADEL-03 — Its parts · MUST

Every shot leaves one of its gun mounts (BOSS-58); four of its six parts carry none:
- **Gear trains** (`gear-left`, `gear-right`): a great brass wheel and two pinions meshing round it
  on a steel shelf off each flank, their arbors in a lit steel bridge. No gun.
- **Pendulum** (`pendulum`): its bob, a brass lens with a lit rim and rosette, at the end of a steel
  rod swinging 16° either way out of its back wall (a joint, BOSS-33); the rod goes with the bob.
  No gun.
- **Minute hand** (`hand`): an ornate blued-steel hand 31 px long with a counterweight tail and a
  lit line, round the centre boss; it sweeps round the dial clockwise (it orbits, BOSS-34, 0.3 rad/s).
  No gun: a gun on a turning ring would not turn its shots with it (the engine turns an orbiting
  part's muzzles, not their headings, see Notes).
- **Front belfries** (`bell-left`, `bell-right`): a brass crown on each front tower's drum, four
  bell lanterns round it (posts, a domed cap with a lit finial, the bell inside), a twin-barrelled
  turret in the middle (its aimed pairs). Destroyed, they leave their stumps on the drums.

**Acceptance criteria**
- Given its model, then it draws its six parts and every gun mount.

*Sources: BOSS-48, BOSS-58, user request (2026-11-06: "don't add too many start guns").*

#### FB-CLOCKWORK-CITADEL-04 — Lights · MUST

Its slits, bands, hour bars, hands' lines, rosette, finials, lanterns and the gears' hubs glow. Its
neon colour, set brass, shows bright yellow (BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright yellow.

*Sources: BOSS-50.*

#### FB-CLOCKWORK-CITADEL-05 — Its core's guns · MUST

All on the core, each out from the first stage that uses it (BOSS-58):
- **Noon gun**: a fixed gun of three barrels side by side on the gatehouse, pointing straight down
  (out from the start).
- **Front casemates**: a fixed twin gun on a sponson either side of the gatehouse, angled 35° out
  and down. Their guns rise out of the open sponsons.
- **Back towers' turrets**: a twin turret on each back tower's drum, under its slate cone roof (a
  hatch that bursts, leaving a steel collar, as its turret first comes into use).
- **Broadsides**: a fixed gun of three barrels on a sponson on each flank, pointing straight out
  sideways.
- **Cuckoo gun**: a three-barrelled turret under the cuckoo house over the gate on the roof's front
  edge (a gabled house with a round, lit door: a hatch).
- **Rotor**: sixteen barrels round a hub under a domed brass hatch on the roof's back (its last
  spiral).

Five of them (noon gun, casemates, broadsides) are fixed: they never turn and fire along their
barrels.

**Acceptance criteria**
- Given its design, then it has these mounts, the fixed ones not on turrets.

*Sources: BOSS-58, user request (2026-11-06: "add non rotating guns too").*

#### FB-CLOCKWORK-CITADEL-06 — The flanks' steelwork · MUST

Each flank carries a steel shelf on brackets under its gear train, and two steel rails, stops at
their ends, along which its great wheel (a brass gear wheel lying half in the flank, its armour,
FB-CLOCKWORK-CITADEL-10) slides out. Once a gear train is destroyed its shelf stays.

**Acceptance criteria**
- Manual validation: the trains stand on their shelves, the wheels on their rails, at rest and once
  they have slid out.

*Sources: BOSS-52.*

#### FB-CLOCKWORK-CITADEL-07 — The pendulum's bracket · MUST

The pendulum hangs from a steel bracket with a brass axle on the back wall, its rod 11 px over the
playfield. Once the pendulum is destroyed (rod and bob), the bracket stays.

**Acceptance criteria**
- Manual validation: the pendulum swings from its bracket.

*Sources: BOSS-33, BOSS-52.*

### Behaviour

#### FB-CLOCKWORK-CITADEL-08 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then drifts
heavily: a slow, narrow sway, a shallow bob. While it is fought the ground scrolls at ×0.6.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.6 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### FB-CLOCKWORK-CITADEL-09 — Stage patterns: a new gun at every stage · MUST

It has six parts as it comes in, all shielding its core. While they stand the front belfries sweep
aimed pairs of magenta bullets 8° apart every 2.6 s, in turn. Fixed guns fire all their barrels at
once (parallel red bullets along them), a pair's right and left half a period apart. The core
fires (guns out counted in the debug key's order, gear trains first, then the pendulum, the hand,
the belfries; hidden weapons apart):
- stage 0: the noon gun every 2.2 s. **Guns out: 3** (1 fixed: the noon gun; 2 turrets);
- stage 1: the noon gun every 2.6 s, the front casemates every 2.2 s (they come out). **Guns out: 5**
  (3 fixed);
- stage 2: the back-left tower's burst of 3 (its roof bursts) every 2.6 s, the casemates every 2.6
  s. **Guns out: 6** (3 fixed), and its 2 orbs after the first transformation;
- stage 3: the noon gun, the back-left tower's aimed pairs, the back-right tower's burst of 3 (its
  roof bursts). **Guns out: 7** (3 fixed) and the orbs;
- stage 4: the noon gun, the back-right tower's aimed pairs, the broadsides every 2 s (they come
  out). **Guns out: 9** (5 fixed), the orbs, and its mortars and lance after the second
  transformation;
- stage 5: the cuckoo gun's aimed spreads of 3, 9° apart, every 2.4 s (the cuckoo house bursts), the
  back-left tower's bursts, the broadsides. **Guns out: 9** (5 fixed; a belfry is gone) and the
  hidden weapons left;
- stage 6 (all six parts gone): the rotor's ring of 16 turning half a step a volley (a spiral) every
  1.3 s (its hatch bursts), the noon gun and the broadsides. **Guns out: 9** (5 fixed; both belfries
  gone) and the hidden weapons left.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel along it (a
  fight in the simulation).
- Given stage 0, then no more than three mounts are out; given each later stage, then a mount comes
  out that no earlier stage used.

*Sources: BOSS-21, BOSS-23, BOSS-58, user request (2026-11-06: "3 max, then more appear").*

#### FB-CLOCKWORK-CITADEL-10 — First transformation: the great wheels unmesh · MUST

It transforms the first time once both gear trains are destroyed (named, BOSS-36). Its two great
wheels (brass gear wheels lying half in its flanks behind the trains, moving pieces, BOSS-45) slide
14 px straight out along their rails, unmeshing; the roof pinions that drove them stop. An **orb**
unfolds on each wheel's hub: a rotor of ten barrels firing turning rings of orange bullets. The
fight turns from aimed shots and straight streams to rings rolling off its flanks.

**Acceptance criteria**
- Given both gear trains destroyed, then it transforms, its wheels slide out and its two orbs are
  revealed on them.

*Sources: BOSS-35, BOSS-36, BOSS-45.*

#### FB-CLOCKWORK-CITADEL-11 — Second transformation: the face splits · MUST

It transforms the second time once the pendulum and the minute hand are destroyed (named,
BOSS-36). The clock face splits down its middle: its two halves slide 14 px apart across the roof
(moving pieces, BOSS-45), opening the movement's pit between them; a **mortar** unfolds on each
half (flak shells bursting into rings of 8), and a **lance** on the centre line (a laser pointing
straight down) rises out of the movement in front of the centre boss. The hour hand keeps turning
over the open pit. The fight turns to bombardment: flak bursting round the player and a beam down
the middle to keep away from.

**Acceptance criteria**
- Given the pendulum and the hand destroyed, then it transforms, its face's halves slide apart, its
  two mortars are revealed on them and the lance between them.

*Sources: BOSS-35, BOSS-36, BOSS-41, BOSS-45.*

#### FB-CLOCKWORK-CITADEL-12 — Angry and never easier · MUST

After each transformation it is angry (BOSS-27): the weapons it revealed fire all out for
`boss_rage_seconds`. Its weighted fire rate (BOSS-39) goes up at each transformation (2.9 as it
comes in, 11.9 after the first, 15.6 after the second).

**Acceptance criteria**
- Given its design, then its weighted fire rate never goes down from one transformation to the
  next, and ends higher (unit test).

*Sources: BOSS-27, BOSS-39.*

#### FB-CLOCKWORK-CITADEL-13 — Death, drops and points · MUST

Its parts drop a weapon bonus 60 % of the time, its hidden weapons 30 %, its core always (BOSS-57).
It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/clockwork_citadel.py` (`_CLOCKWORK_CITADEL`,
`CLOCKWORK_CITADEL`); its model in `src/game/view/bosses/lab/clockwork_citadel_model.py`,
`clockwork_citadel_parts.py` and `clockwork_citadel_rig.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 5 L (radius 85 px) | `stats.size` |
| plinth, block, roof | half widths 53 and 48; plinth top 6, roof 16, parapet 3 wide to 19 | `PLINTH`, `BLOCK`, `ROOF`, `PARAPET` |
| clock | face radius 34, top 17.6; pit floor 12.5; centre boss radius 9 (top 19.4); arbor to 23 | `FACE_RADIUS`, `FACE_TOP`, `MOVEMENT`, `CENTRE`, `ARBOR` |
| core | radius 22, health 4 300 | `coreRadius`, `coreHealth` |
| gear trains | (±60, -22), radius 12, health 1 300 each, no gun | `GEARS_AT` |
| pendulum | pivot (0, 51), bob (0, 76) radius 11, health 1 500, swings 16° over 3.2 s, no gun | `PENDULUM_PIVOT`, `BOB_AT`, `PENDULUM_SWING` |
| minute hand | (0, -17) radius 9, health 1 200, 31 px long, orbits at -0.3 rad/s, no gun | `HAND_AT`, `HAND_LENGTH`, `SPIN` |
| belfries | (±48, -48), radius 11, health 1 400 each; twin turrets 4.4 px on drums 28 px high | `TOWER_AT`, `TOWER_GUN` |
| noon gun | (0, -55) on the gatehouse (top 13), 3 fixed barrels straight down | `NOON_AT`, `NOON_GUN` |
| casemates | (±28, -51), top 10, 2 fixed barrels 35° out | `CASEMATE_AT`, `CASEMATE_DEG`, `CASEMATE_GUN` |
| broadsides | (±51, -2), top 10, 3 fixed barrels straight out | `BROADSIDE_AT`, `BROADSIDE_GUN` |
| back towers | (±48, 48), twin turrets under cone roofs 9.5 px round | `TOWER_GUN`, `ROOF_RADIUS` |
| cuckoo gun | (0, -42) on the roof, 3 barrels on a turret, under a 12 × 10 px house | `CUCKOO_AT`, `CUCKOO_HOUSE`, `CUCKOO_GUN` |
| rotor | (0, 41), 16 barrels, under a hatch 5.6 px round | `ROTOR_AT`, `CORE_ROTOR` |
| great wheels | (±56, 18) radius 12, slide 14 px out | `WHEEL_AT`, `WHEEL_RADIUS`, `WHEEL_SLIDE` |
| orbs | (±70, 18) once out, radius 9, health 1 200 each | `ORB_AT` |
| face halves | slide 14 px apart | `FACE_SLIDE` |
| mortars | (±32, 8) once out, radius 8, health 1 500 each | `MORTAR_AT` |
| lance | (0, -18), radius 7, health 1 500 | `LANCE_AT` |
| bullets | red 180 px/s; belfries magenta 170; spiral orange 160 | `RED`, `BELL_SHOT`, `SPIRAL` |
| full health | 19 300 | core, parts and hidden weapons (BOSS-54), in line with the Refinery Titan's 19 210 |
| points | 12 000 | `stats.points` |
| ground speed | ×0.6 | `stats.groundSpeed` |
| stop, sway, bob | 0.7; 34 px over 11 s; 4 px over 5 s | `stopFraction`, `sway`, `bob` |
| drawn triangles | about 7 900 (body, parts, weapons) and 1 300 (rig), budget 10 000 | BOSS-53 |

## Notes

- **A gun on the minute hand.** The hand was meant to carry a fixed laser along it, turning with it
  (BOSS-34). In the engine an orbiting part's (and a jointed part's) muzzles move with it but their
  headings do not turn (`BossPart.heading` is its boss's), so the beam would leave the lens at a
  heading other than the barrel's. The hand carries no gun; an engine change turning an orbiting
  part's headings by the boss's spin (and a jointed one's by its joint's angle) would allow it.
