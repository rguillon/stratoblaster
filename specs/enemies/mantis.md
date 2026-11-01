# Mantis

> **Area:** enemies · **Prefix:** `ENM-MANTIS` · **Related:** [common.md](common.md), [World 3](../worlds/world-3/world.md), [World 4](../worlds/world-4/world.md)

The Mantis is a veteran kind ([common.md](common.md)) with moving parts: an insect with two long
scythe arms that swing out and in while it hovers in the upper half, each firing along its blade so
the shots sweep. Its head fires at the player. Its arms can be shot off one by one.

## Requirements

### Look

#### ENM-MANTIS-01 — Shape and size · MUST

The Mantis is an insect-like hull 1.4 L long: a long abdomen at the back, a plated thorax, a narrow
head at the front, and two long scythe arms folded forward either side of the head, turned a little
out (14°) at rest.

**Acceptance criteria**
- Given the Mantis's model at rest, then it is 1.4 L long, arms included (within the size
  tolerance of [common.md](common.md)), and both scythes show from above.

*Sources: P05-R16, P16-R04.*

#### ENM-MANTIS-02 — Cyber-Organic body · MUST

The Mantis is Cyber-Organic ([common.md](common.md)). Its abdomen is three swollen flesh segments
(teal shade), its thorax a ridged carapace (sinew and teal), its narrow head a teal flesh bulb on
its neck. Metal is grafted on: a plate on the head's brow and a short gun barrel on the head. With
its two limbs and grafts it reads as a veteran, more complex than the basic kinds.

**Acceptance criteria**
- Given the Mantis's model, then its body and head are flesh, and the brow plate and the head's gun
  are metal.

*Sources: P05-R16, P16-R04.*

#### ENM-MANTIS-03 — Neon lights · MUST

Three neon bands stripe the back of the abdomen, two eyes glow on the head, and a neon line runs
along the cutting edge of each blade, all in the Mantis's neon colour. That colour is bright
yellow: its configured lime is on the yellow side of the two enemy hues ([common.md](common.md)).

**Acceptance criteria**
- Given the Mantis's model, then its bands, eyes and blade edges are lit in bright yellow.

*Sources: P05-R16, P16-R04, D-231.*

#### ENM-MANTIS-04 — Charge lights · SHOULD

Charge lights at the tip of each blade, by its pair of muzzles, and at the mouth of the head's gun
brighten as the arms' next pair of shots comes, while the Mantis is stopped; they are dark while it
comes in and leaves ([common.md](common.md)).

**Acceptance criteria**
- Given a stopped Mantis, then its charge rises from 0 to 1 over each arm fire interval; given it
  leaves, then its charge is 0.

*Sources: P05-R16, P16-R04.*

#### ENM-MANTIS-05 — Scythe arms on their shoulders · MUST

Each arm is a flesh forearm (sinew) with a bone scythe grown out of it, hooking inwards, its
cutting edge on the inside. It hangs on a metal shoulder knuckle on its side of the thorax, which
turns with the arm and cannot be shot off. The model's arms swing on their shoulders exactly as the
Mantis's joints do in the game ([common.md](common.md)), and the pair of muzzles at each blade's
tip are where its shots leave. A destroyed arm disappears from the model; its knuckle stays.

**Acceptance criteria**
- Given the Mantis's model, then it draws both arm parts of its design, each on its shoulder joint,
  with two muzzles at the blade's tip, at the places the game fires from.
- Given an arm is destroyed, then its blade and forearm are no longer drawn.

*Sources: P05-R16, P16-R04.*

#### ENM-MANTIS-06 — Reactor · MUST

One plain reactor (no flesh sac) sits at the tip of its abdomen. It has no wings.

**Acceptance criteria**
- Given the Mantis's model, then its body has one reactor and one gun muzzle (the head's).

*Sources: P16-R04.*

#### ENM-MANTIS-07 — Triangle budget · MUST

The Mantis's model (body, shoulders and arms, reactor included) stays within the veteran triangle
budget (700, [common.md](common.md)). It is about 520 triangles before the edge trim.

**Acceptance criteria**
- Given the Mantis's model, then its triangle count is at most the veteran budget.

*Sources: P16-R04, P16-R09.*

### Behaviour

#### ENM-MANTIS-08 — Entry, stop and exit · MUST

A Mantis comes in alone from just above the top edge, at the wave's entry position or at a random X
between 25 % and 75 % of the width. It flies down at 120 px/s, slowing over the last 70 px (never
below 20 px/s), to stop at a random height between 62 % and 76 % of the playfield (the upper half).
It stays there 6 s, then leaves downward at 100 px/s.

**Acceptance criteria**
- Given a Mantis comes in, then it stops at its stop height and is still there halfway through its
  stay.
- Given it has stayed 6 s, then it moves down and off the screen.

*Sources: P05-R16.*

#### ENM-MANTIS-09 — Swinging arms · MUST

The two arms are moving parts ([common.md](common.md)) on shoulder joints either side of the thorax
(8 px out, 5 px ahead of the centre). Each swings out and in by up to 24° every 2.4 s, the right arm
a quarter of a swing behind the left (out of step), all the time.

**Acceptance criteria**
- Given a Mantis, then its two arm parts' headings swing by up to 24° either way of their rest
  heading, a quarter period apart.

*Sources: P05-R16.*

#### ENM-MANTIS-10 — Shots along the blades · MUST

While it is stopped, every 1.2 s (the first 0.6 s after it stops) each standing arm fires a pair of
bullets (210 px/s) straight along its blade, from either side of the blade's tip, where the arm is
now. As the arm swings, its shots sweep. A destroyed arm no longer fires.

**Acceptance criteria**
- Given a Mantis is stopped, then each living arm's shots leave from its blade's tip along the
  arm's current direction.
- Given an arm is destroyed, then that arm no longer fires.

*Sources: P05-R16.*

#### ENM-MANTIS-11 — Aimed head shot · MUST

Every 2 s (the first 1 s after it is over the playfield), its head fires one bullet (200 px/s)
aimed at the player, from the gun on its head, whenever its centre is over the playfield, with or
without its arms.

**Acceptance criteria**
- Given both arms are destroyed, then the head keeps firing at the player.

*Sources: P05-R16.*

#### ENM-MANTIS-12 — The arms as parts · MUST

Each arm has its own hit circle (6 px, on the middle of its blade, 13 px from its shoulder) and its
own health (50 HP); shots that hit an arm damage the arm, not the hull. A destroyed arm blows up as
a part does ([common.md](common.md)): no points, no bonus.

**Acceptance criteria**
- Given a shot hits an arm, then the arm loses health and the hull does not.
- Given an arm reaches 0 HP, then only that arm is destroyed and the Mantis flies on.

*Sources: P05-R16.*

#### ENM-MANTIS-13 — Health, points and hit circle · MUST

The Mantis's hull has 160 HP and scores 500 points. Its hit circle, at its centre, is half the
usual one for its size ([common.md](common.md)): 10.1 px. The arms have their own
(ENM-MANTIS-12).

**Acceptance criteria**
- Given a Mantis, then its hull takes 160 damage to destroy and scores 500 points, and the arms
  still on it blow up with it.

*Sources: P05-R16.*

#### ENM-MANTIS-14 — Veteran kind, from World 3 · MUST

The Mantis is a veteran kind. No wave of World 1 or World 2 uses it. World 3 brings it in at 3-4,
the fourth veteran kind, and the waves of every later level (3-4 to 4-5) use it.

**Acceptance criteria**
- Given the wave scripts, then no level before 3-4 names the Mantis, and every level from 3-4 to
  4-5 does.

*Sources: P05-R24, D-090.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| size | 1.4 L | `src/game/config/enemies_veteran.py` `VETERAN_CONFIG.mantis.size` |
| health / points | 160 / 500 | `VETERAN_CONFIG.mantis.stats` |
| hit radius | 10.1 px | `radius(1.4) * 0.5` |
| xRange | 25 % – 75 % of the width | when the wave gives no entry |
| entrySpeed / brakeDistance | 120 px/s / 70 px | slowest 20 px/s (`src/game/sim/enemies/mantis.py` `CREEP`) |
| stopRange | 62 % – 76 % of the height | |
| stay / exitSpeed | 6 s / 100 px/s | |
| shoulder | `[8, -5]` (each side) | `MANTIS_SHOULDER` |
| arm length / out at rest | 22 px / 14° | `MANTIS_ARM`, shoulder to blade tip |
| arm health / radius / centre | 50 / 6 px / 13 px from the shoulder | `VETERAN_CONFIG.mantis.arm` |
| arm swing | ±24° every 2.4 s, right arm a quarter period behind | `arm.swing`; phase in `mantis.py` |
| arm fireInterval | 1.2 s, first after 0.6 s | a pair, style `green`, 210 px/s |
| arm muzzles | 1.6 px either side of each blade's tip | `mantis_muzzles` |
| head fireInterval / firstShot | 2 s / 1 s | style `green`, 200 px/s; muzzle `[0, -14.6, 1.4]` |
| neon | `[0.6, 1, 0.1]`, drawn `[1, 1, 0.1]` | `VETERAN_NEON.mantis` |
| triangle budget | 700 (veteran) | `src/game/config/enemy_look.py` `ENEMY_LOOK.budget.veteran` |

## Notes

**Appears in** (`src/game/config/world_3/waves.py`, `world_4/waves.py`): one Mantis in a phrase of
its level's cycle in each of [3-4](../worlds/world-3/3-4-suburbs.md),
[3-5](../worlds/world-3/3-5-garden-villages.md), [4-1](../worlds/world-4/4-1-garden-town.md),
[4-2](../worlds/world-4/4-2-inner-town.md), [4-3](../worlds/world-4/4-3-midtown.md),
[4-4](../worlds/world-4/4-4-business-district.md) and [4-5](../worlds/world-4/4-5-downtown.md); the
groups grow over each level. It is in no level's filler.

- Its design (shoulder joints and arm parts) is built in its sim module (`MANTIS_DESIGN`) from the
  engine's specs, and the model draws from the same design.
- Known gaps: no unit test checks the model's size or its triangle count since the Python port
  (D-220).
