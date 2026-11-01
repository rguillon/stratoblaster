# Orbiter

> **Area:** enemies · **Prefix:** `ENM-ORBITER` · **Related:** [common.md](common.md), [World 4](../worlds/world-4/world.md)

The Orbiter is an elite kind ([common.md](common.md)) with moving parts: a spherical core with
three armoured drones orbiting it. The core fires rings of bullets; the drones fire at the player
and catch shots aimed at the core. The drones can be shot down one by one.

## Requirements

### Look

#### ENM-ORBITER-01 — Shape and size · MUST

The Orbiter is a spherical core, squashed a little in height, with three small armoured drones
orbiting close around it: 1.1 L across, drones included. The core alone is 24 px across.

**Acceptance criteria**
- Given the Orbiter's model, then it is 1.1 L across with its drones (within the size tolerance of
  [common.md](common.md)), and the core and its three drones show from above.

*Sources: P05-R20, P16-R04.*

#### ENM-ORBITER-02 — Cyber-Organic core · MUST

The core is a flesh heart (graphite shade) held in two dark metal armour bands, one above and one
below its equator. It has no reactor. Its armour, organs and drones make it read as an elite
([common.md](common.md)).

**Acceptance criteria**
- Given the Orbiter's model, then its core is flesh in two metal bands, and it has no reactor.

*Sources: P05-R20, P16-R04.*

#### ENM-ORBITER-03 — Neon lights · MUST

A glowing ring circles the core's equator and four glowing veins run over its top, from the pole
down to the upper band; each drone has a neon eye slit and a pulsing gland at its back. All are in
the Orbiter's neon colour, a pale yellow: its configured white-gold is on the yellow side of the
two enemy hues ([common.md](common.md)), so it is drawn at the enemy yellow hue, keeping its own
brightness and paleness.

**Acceptance criteria**
- Given the Orbiter's model, then its equator ring, veins, eye slits and glands are lit in pale
  yellow (hue 60°).

*Sources: P05-R20, P16-R04, D-231.*

#### ENM-ORBITER-04 — Charge lights · SHOULD

A light on the core's pole brightens as the next ring of bullets comes and is at full brightness
when it leaves; the charge lights at the mouths of the drones' guns follow the same charge
([common.md](common.md)).

**Acceptance criteria**
- Given an Orbiter over the playfield, then its charge rises from 0 to 1 over each ring interval.

*Sources: P05-R20, P16-R04.*

#### ENM-ORBITER-05 — Drones on their orbit · MUST

Each drone is a flesh pod (slate) under a metal armour shell, its nose facing out from the core,
with a gun barrel on its nose. The model's drones turn round the core exactly as the Orbiter's
drones do in the game ([common.md](common.md)), and each drone's gun muzzle is where its shots
leave. The core has twelve ring muzzles round its equator. A destroyed drone disappears from the
model.

**Acceptance criteria**
- Given the Orbiter's model, then it draws one part per drone of its design, each with one gun
  muzzle, and the core has twelve ring muzzles.
- Given a drone is destroyed, then it is no longer drawn.

*Sources: P05-R20, P16-R04.*

#### ENM-ORBITER-06 — Triangle budget · MUST

The Orbiter's model (core and drones) stays within the elite triangle budget (1200,
[common.md](common.md)). It is about 760 triangles before the edge trim.

**Acceptance criteria**
- Given the Orbiter's model, then its triangle count is at most the elite budget.

*Sources: P16-R04, P16-R09.*

### Behaviour

#### ENM-ORBITER-07 — Entry, stay and exit · MUST

An Orbiter comes in alone from just above the top edge, at the wave's entry position or at a random
X between 25 % and 75 % of the width. It flies down at 120 px/s to a random height between 60 % and
78 % of the playfield (the upper half), stays there 8 s, then leaves upward at 140 px/s.

**Acceptance criteria**
- Given an Orbiter spawns, then it is one enemy that comes in to its stop height and stays there.
- Given it has stayed 8 s, then it moves up and off the screen.

*Sources: P05-R20.*

#### ENM-ORBITER-08 — Orbiting drones · MUST

The three drones are moving parts ([common.md](common.md)) evenly spaced on an orbit 15.5 px from
the centre, each facing out, turning clockwise at 100°/s all the time. They are close enough to
overlap the core's hit circle, so they catch shots aimed at the core: a shot that hits a drone
damages the drone, not the core.

**Acceptance criteria**
- Given an Orbiter, then its drones turn around the core, and the shots that hit a drone damage the
  drone, not the core.

*Sources: P05-R20.*

#### ENM-ORBITER-09 — Rings from the core · MUST

While its centre is over the playfield, every 3 s (the first 0.8 s after it is over it) the core
fires a ring of 12 bullets (150 px/s) evenly all around, the first straight down, each from the
point of the equator facing its way.

**Acceptance criteria**
- Given an Orbiter fires a ring, then 12 bullets leave its equator 30° apart.

*Sources: P05-R20.*

#### ENM-ORBITER-10 — Aimed drone shots · MUST

While the Orbiter is over the playfield, each standing drone fires one bullet (200 px/s) aimed at
the player every 2 s, from its gun, where the drone is now. The drones fire in turn, not at once
(their first shots after 1 s, 1.67 s and 2.33 s). A destroyed drone stops firing.

**Acceptance criteria**
- Given an Orbiter stays, then it fires its rings and its drones' aimed bullets.
- Given a drone is destroyed, then it no longer fires and the others do.

*Sources: P05-R20.*

#### ENM-ORBITER-11 — The drones as parts · MUST

Each drone has its own hit circle (5.5 px) and its own health (40 HP). A destroyed drone blows up as
a part does ([common.md](common.md)): no points, no bonus.

**Acceptance criteria**
- Given a drone reaches 0 HP, then only that drone is destroyed and the core flies on.

*Sources: P05-R20.*

#### ENM-ORBITER-12 — Health, points and hit circle · MUST

The Orbiter's core has 160 HP and scores 650 points. Its hit circle is the core: 12 px, at its
centre.

**Acceptance criteria**
- Given an Orbiter, then its core takes 160 damage to destroy and scores 650 points, and the drones
  still on it blow up with it.

*Sources: P05-R20.*

#### ENM-ORBITER-13 — Drones from its config, as engine specs · SHOULD

The Orbiter's drones are written in its config, and the game hands them to the engine as the
engine's own part specs (`jointed_design`): each drone orbits and hangs on no joint. So an Orbiter
spawns without error in the browser too, where a raw config record would leave the drone's joint
undefined rather than empty.

**Acceptance criteria**
- Given an Orbiter is made, then it has three parts, each an engine part spec that orbits and has
  no joint.

*Sources: D-196, D-192.*

#### ENM-ORBITER-14 — Elite kind, World 4 only · MUST

The Orbiter is an elite kind: only World 4's waves use it. 4-1 brings it in with the Hydra, the
first two elite kinds, and every level of World 4 (4-1 to 4-5) uses it.

**Acceptance criteria**
- Given the wave scripts, then no level of Worlds 1 to 3 names the Orbiter, and every level of
  World 4 does.

*Sources: P05-R24, D-090.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| size | 1.1 L | `src/game/config/enemies_elite.py` `ELITE_CONFIG.orbiter.size` |
| health / points | 160 / 650 | `ELITE_CONFIG.orbiter.stats` |
| hit radius / coreRadius | 12 px / 12 px | the core |
| xRange | 25 % – 75 % of the width | when the wave gives no entry |
| entrySpeed / stopRange | 120 px/s / 60 % – 78 % of the height | |
| stay / exitSpeed | 8 s / 140 px/s | upward |
| spin | 100°/s, clockwise | the drones' orbit |
| drone orbit / radius / health | 15.5 px / 5.5 px / 40 | `ORBITER_DRONE` |
| drone muzzle | 4.5 px out of its centre, 2 px up | `ORBITER_DRONE.muzzleOut`, `height` |
| ringInterval / firstRing / ringCount | 3 s / 0.8 s / 12 | style `orange`, 150 px/s; muzzles 12.5 px out on the equator |
| droneFireInterval | 2 s, first after 1, 1.67, 2.33 s | style `orange`, 200 px/s |
| fire rate | rings and drone shots times the level's fire rate factor | [common.md](common.md) |
| neon | `[1, 0.86, 0.5]`, drawn `[1, 1, 0.5]` | `src/game/config/enemy_look_elite.py` `ELITE_NEON.orbiter` |
| triangle budget | 1200 (elite) | `src/game/config/enemy_look.py` `ENEMY_LOOK.budget.elite` |

## Notes

**Appears in** (`src/game/config/world_4/waves.py`): one Orbiter in a phrase of its level's cycle
in each of [4-1](../worlds/world-4/4-1-garden-town.md), [4-2](../worlds/world-4/4-2-inner-town.md),
[4-3](../worlds/world-4/4-3-midtown.md), [4-4](../worlds/world-4/4-4-business-district.md) and
[4-5](../worlds/world-4/4-5-downtown.md); the groups grow over each level. It is in no level's
filler.

- Before D-196 the Orbiter raised "Part hangs on no joint" when it spawned in World 4 (browser
  only).
- Known gaps: no unit test checks the model's size or its triangle count since the Python port
  (D-220).
