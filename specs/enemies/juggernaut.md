# Juggernaut

> **Area:** enemies · **Prefix:** `ENM-JUGGERNAUT` · **Related:** [common.md](common.md), [bosses/common.md](../bosses/common.md), [World 4](../worlds/world-4/world.md)

The Juggernaut is an elite kind ([common.md](common.md)) with moving parts: a massive armoured
brute that drifts from side to side in the upper third. Two swinging shoulder cannons fire bursts
along their barrels, a turret on its back fires wide aimed spreads, and two armour plates over its
front shield its core until both are shot off.

## Requirements

### Look

#### ENM-JUGGERNAUT-01 — Shape and size · MUST

The Juggernaut is a massive, wide hull 2 L across (about 1.4 L long), with two armour plates over
its front, a shoulder cannon on each side pointing forward, and a turret with a twin cannon on its
back.

**Acceptance criteria**
- Given the Juggernaut's model at rest, then it is 2 L across, cannons included (within the size
  tolerance of [common.md](common.md)), and its plates, cannons and turret show from above.

*Sources: P05-R22, P16-R04.*

#### ENM-JUGGERNAUT-02 — Cyber-Organic body · MUST

Its body is a swollen, wide flesh body (sinew) under a ridged shell (slate and sinew). Metal is
grafted on: a riveted plate bolted on its back under the turret, the turret and its twin cannon, the
shoulder mounts and the front plates. Heavily armoured, it reads as an elite
([common.md](common.md)).

**Acceptance criteria**
- Given the Juggernaut's model, then its body and shell are flesh, and its back plate, turret,
  mounts and front plates are metal.

*Sources: P16-R04.*

#### ENM-JUGGERNAUT-03 — Neon lights · MUST

Slanted eye slits glow at its front, two long strips run along its back, a glowing vein runs along
each side, a light runs along each front plate's edge and each cannon has a gland and a strip on
top, all in the Juggernaut's neon colour. That colour is a soft green: its configured steel blue is
on the green side of the two enemy hues ([common.md](common.md)), so it is drawn at the enemy green
hue, keeping its own brightness and paleness.

**Acceptance criteria**
- Given the Juggernaut's model, then its eye slits, back strips, veins, plate edges and cannon
  lights are lit in green (hue 125°).

*Sources: P05-R22, P16-R04, D-231.*

#### ENM-JUGGERNAUT-04 — Charge lights · SHOULD

Charge lights at the mouths of the twin cannon and of the shoulder cannons brighten as the next
spread comes and are at full brightness when it leaves ([common.md](common.md)).

**Acceptance criteria**
- Given a Juggernaut over the playfield, then its charge rises from 0 to 1 over each spread
  interval.

*Sources: P05-R22, P16-R04.*

#### ENM-JUGGERNAUT-05 — Reactors · MUST

Three reactors sit at its tail: two each set in a glowing organ (a flesh sac, a gland and a vein)
and a plain one between them.

**Acceptance criteria**
- Given the Juggernaut's model, then its body has three reactors and two gun muzzles, those of the
  twin cannon.

*Sources: P16-R04.*

#### ENM-JUGGERNAUT-06 — Cannons, plates and mounts · MUST

Each shoulder cannon is a flesh pod (slate) in a metal band with a long barrel forward, on a dark
metal shoulder mount that turns with it and cannot be shot off. Each front plate is a thick,
chamfered metal slab with rivets. The model's cannons turn on their shoulders exactly as the
Juggernaut's do in the game ([common.md](common.md)), and each barrel's tip is where its bursts
leave. A destroyed cannon or plate disappears from the model; the mounts stay.

**Acceptance criteria**
- Given the Juggernaut's model, then it draws the two cannons and two plates of its design, each
  cannon on its shoulder joint with one muzzle at its barrel's tip, at the place the game fires
  from.

*Sources: P05-R22, P16-R04.*

#### ENM-JUGGERNAUT-07 — Triangle budget · MUST

The Juggernaut's model (body, mounts, cannons and plates, reactors included) stays within the elite
triangle budget (1200, [common.md](common.md)). It is about 1190 triangles before the edge trim.

**Acceptance criteria**
- Given the Juggernaut's model, then its triangle count is at most the elite budget.

*Sources: P16-R04, P16-R09.*

### Behaviour

#### ENM-JUGGERNAUT-08 — Entry, drift and exit · MUST

A Juggernaut comes in alone from just above the top edge, at the wave's entry position or at a
random X between 30 % and 70 % of the width. It comes down slowly, at 55 px/s, to 74 % of the
playfield height (the upper third), then drifts left and right, up to 60 px either side of where it
came in, one drift every 5 s, for 10 s. Then it leaves downward at 80 px/s.

**Acceptance criteria**
- Given a Juggernaut comes in, then it stops at 74 % of the height and starts drifting sideways.
- Given it has drifted 10 s, then it moves down and off the screen.

*Sources: P05-R22.*

#### ENM-JUGGERNAUT-09 — Swinging shoulder cannons · MUST

The two shoulder cannons are moving parts ([common.md](common.md)) on joints at its shoulders
(22 px either side of the centre, 3 px behind it). Each swings to and fro by up to 20° every 2.4 s,
the left one half a swing behind the right, all the time.

**Acceptance criteria**
- Given a Juggernaut, then its cannons' headings swing by up to 20° either way of straight down,
  half a period apart.

*Sources: P05-R22.*

#### ENM-JUGGERNAUT-10 — Cannon bursts · MUST

While its centre is over the playfield, every 1.6 s (the first 0.8 s after it is over it) each
standing shoulder cannon fires a burst of 3 bullets (210 px/s), 0.12 s apart, along its barrel as
it is turned at that moment, from the barrel's tip. A destroyed cannon no longer fires.

**Acceptance criteria**
- Given a Juggernaut fires a burst, then each standing cannon's 3 bullets leave its barrel's tip
  along the barrel's current direction.
- Given a cannon is destroyed, then it no longer fires and the other does.

*Sources: P05-R22.*

#### ENM-JUGGERNAUT-11 — Aimed spread from the turret · MUST

While its centre is over the playfield, every 2.5 s (the first 1.2 s after it is over it) its back
turret fires a spread of 7 bullets (185 px/s) 9° apart, centred on the player. The turret is a
mantlet with seven parallel barrels that turns (240°/s): it sweeps across the spread, each barrel
firing in turn, 0.08 s after the one before, as the turret points that bullet's way; every bullet
leaves its barrel's tip along the turret (WPN-01, WPN-02). Between spreads the turret follows the
player (owner request 2026-11-05, D-273).

**Acceptance criteria**
- Given a Juggernaut over the playfield, then it fires its spread of 7 from the core's twin cannon,
  the middle bullet towards the player.

*Sources: P05-R22.*

#### ENM-JUGGERNAUT-12 — Front plates shield the core · MUST

The two front plates are parts ([common.md](common.md)) fixed on its front (10 px either side of the
centre, 17 px ahead of it), each with its own hit circle (9 px) and health (120 HP). While one of
them stands, the player's shots pass through the core and do it no damage, as a boss's shielded
core does ([bosses/common.md](../bosses/common.md)). Once both are destroyed, the core can be hit.

**Acceptance criteria**
- Given a Juggernaut with a plate left, then shots on the core do no damage; once both plates are
  destroyed, the core can be hit.

*Sources: P05-R22, D-090.*

#### ENM-JUGGERNAUT-13 — The cannons as parts · MUST

Each shoulder cannon has its own hit circle (7 px, centred 28 px out and 3 px ahead of the centre at
rest) and its own health (60 HP). Destroyed cannons and plates blow up as parts do
([common.md](common.md)): no points, no bonus.

**Acceptance criteria**
- Given a cannon reaches 0 HP, then only that cannon is destroyed and the Juggernaut goes on.

*Sources: P05-R22.*

#### ENM-JUGGERNAUT-14 — Health, points and hit circle · MUST

The Juggernaut's core has 320 HP and scores 1 000 points, the most of any enemy kind. Its hit
circle is 20 px, at its centre.

**Acceptance criteria**
- Given a Juggernaut with no plate left, then its core takes 320 damage to destroy and scores
  1 000 points, and the parts still on it blow up with it.

*Sources: P05-R22.*

#### ENM-JUGGERNAUT-15 — Cannons and plates from its config, as engine specs · SHOULD

The Juggernaut's shoulders, cannons and plates are written in its config, and the game hands them
to the engine as the engine's own joint and part specs (`jointed_design`), as it does for the
bosses. So the engine reads the swing the config gives (amplitude, period, phase) and which parts
shield, in CPython and in the browser alike.

**Acceptance criteria**
- Given a Juggernaut is made, then its cannons are engine part specs on their shoulder joints
  swinging 20° every 2.4 s (no NaN angle), and its plates are engine part specs that shield.

*Sources: D-192.*

#### ENM-JUGGERNAUT-16 — Elite kind, World 4 only · MUST

The Juggernaut is an elite kind: only World 4's waves use it. 4-4 brings it in, the last elite
kind, and 4-5 uses it too.

**Acceptance criteria**
- Given the wave scripts, then no level before 4-4 names the Juggernaut, and 4-4 and 4-5 do.

*Sources: P05-R24, D-090.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| size | 2 L | `src/game/config/enemies_elite.py` `ELITE_CONFIG.juggernaut.size` |
| health / points | 320 / 1 000 | `ELITE_CONFIG.juggernaut.stats` |
| hit radius | 20 px | `ELITE_CONFIG.juggernaut.stats.radius` |
| xRange | 30 % – 70 % of the width | when the wave gives no entry |
| entrySpeed / stopFraction | 55 px/s / 0.74 | |
| drift / driftPeriod / stay | ±60 px / 5 s / 10 s | |
| exitSpeed | 80 px/s | downward |
| spread | 7 × 9° every 2.5 s, first after 1.2 s | `fireInterval`, `firstShot`, `spreadCount`, `spreadSpacing`; style `blue`, 185 px/s |
| twin cannon muzzles | `[-3, -9, 7]`, `[3, -9, 7]` | on the back turret |
| cannons | pivots `[±22, 3]`, centres `[±28, -3]`, muzzles `[±28, -16, 3]` | `JUGGERNAUT_CANNONS` |
| cannon swing | ±20° every 2.4 s, phases 0 (right), 0.5 (left) | `ELITE_CONFIG.juggernaut.design.joints` |
| cannon health / radius | 60 / 7 px | |
| cannon bursts | 3 bullets 0.12 s apart every 1.6 s, first after 0.8 s | `cannonInterval`, `firstBurst`, `burstCount`, `burstGap`; style `blue`, 210 px/s |
| plates | at `[±10, -17]`, health 120, radius 9 px, shield | `JUGGERNAUT_PLATES`, `design.parts` |
| fire rate | spreads and bursts times the level's fire rate factor | [common.md](common.md) |
| neon | `[0.42, 0.62, 0.95]`, drawn `[0.42, 0.95, 0.46]` | `src/game/config/enemy_look_elite.py` `ELITE_NEON.juggernaut` |
| triangle budget | 1200 (elite) | `src/game/config/enemy_look.py` `ENEMY_LOOK.budget.elite` |

## Notes

**Appears in** (`src/game/config/world_4/waves.py`): one Juggernaut in a phrase of its level's
cycle in each of [4-4](../worlds/world-4/4-4-business-district.md) and
[4-5](../worlds/world-4/4-5-downtown.md); the groups grow over each level. It is in no level's
filler.

- Known gaps: no unit test checks the model's size or its triangle count since the Python port
  (D-220); at about 1190 triangles before the trim, it is the elite closest to its budget, and
  whether the budget counts the trim is open (D-220).
