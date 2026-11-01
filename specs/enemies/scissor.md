# Scissor

> **Area:** enemies · **Prefix:** `ENM-SCISSOR` · **Related:** [common.md](common.md), [lancer.md](lancer.md), [World 4](../worlds/world-4/world.md)

The Scissor is an elite kind ([common.md](common.md)) with moving parts: a long, narrow hull with
two laser arms hinged at its shoulders. It stops in the upper part of the screen, warns, then fires
both lasers while the arms close inward like scissors, and leaves. Its arms can be shot off; a
destroyed arm's laser stops.

## Requirements

### Look

#### ENM-SCISSOR-01 — Shape and size · MUST

The Scissor is a long, narrow hull 1.8 L long (about 1.15 L across its arms at rest), with two laser
arms hinged at its shoulders, pointing down and out on either side of its nose.

**Acceptance criteria**
- Given the Scissor's model at rest, then it is 1.8 L long (within the size tolerance of
  [common.md](common.md)), and both arms show from above.

*Sources: P05-R21, P16-R04.*

#### ENM-SCISSOR-02 — Cyber-Organic body · MUST

Its body is a long, narrow flesh body of five segments (slate) under a ridged shell (sinew and
slate). Metal is grafted on: a nose cap with a dark canopy painted on it, a riveted armour plate over
each shoulder hinge and swept fins either side of its tail. Its armour and limbs make it read as an
elite ([common.md](common.md)).

**Acceptance criteria**
- Given the Scissor's model, then its body and shell are flesh, and its nose cap, shoulder plates
  and fins are metal.

*Sources: P16-R04.*

#### ENM-SCISSOR-03 — Neon lights · MUST

A stripe runs down its back, two eyes glow at its front, a glowing vein runs along each side, a
neon ring circles each shoulder hinge and a strip runs along each arm, all in the Scissor's neon
colour. That colour is bright yellow: its configured crimson is on the yellow side of the two enemy
hues ([common.md](common.md)).

**Acceptance criteria**
- Given the Scissor's model, then its stripe, eyes, veins, hinge rings and arm strips are lit in
  bright yellow.

*Sources: P05-R21, P16-R04, D-231.*

#### ENM-SCISSOR-04 — Reactors · MUST

Two reactors sit at its tail, each set in a glowing organ: a flesh sac round the nozzle, a gland on
its back and a vein running forward from it.

**Acceptance criteria**
- Given the Scissor's model, then its body has two reactors, each in a flesh sac.

*Sources: P16-R04.*

#### ENM-SCISSOR-05 — Laser arms on their shoulders · MUST

Each arm is a flesh limb (sinew) with a bone blade along it, held by two metal cuffs, ending in an
emitter cone at its tip, where its laser leaves. It hangs on a metal shoulder hinge that turns with
it and cannot be shot off. The model's arms turn on their shoulders exactly as the Scissor's do in
the game ([common.md](common.md)). A destroyed arm disappears from the model; its hinge stays.

**Acceptance criteria**
- Given the Scissor's model, then it draws its two arms, each on its shoulder joint with one laser
  muzzle at its tip, at the place the game fires from.
- Given an arm is destroyed, then it is no longer drawn.

*Sources: P05-R21, P16-R04.*

#### ENM-SCISSOR-06 — Charge lights · SHOULD

Each arm's emitter cone is a charge light: it brightens through the warning and is at full
brightness when the beams start ([common.md](common.md)).

**Acceptance criteria**
- Given a Scissor halfway through its warning, then its charge is about one half.

*Sources: P05-R21, P16-R04.*

#### ENM-SCISSOR-07 — Triangle budget · MUST

The Scissor's model (body, hinges and arms, reactors included) stays within the elite triangle
budget (1200, [common.md](common.md)). It is about 1120 triangles before the edge trim.

**Acceptance criteria**
- Given the Scissor's model, then its triangle count is at most the elite budget.

*Sources: P16-R04, P16-R09.*

### Behaviour

#### ENM-SCISSOR-08 — Entry and stop · MUST

A Scissor comes in alone from just above the top edge, at the wave's entry position or at a random
X between 25 % and 75 % of the width. It flies down at 160 px/s, slowing over the last 60 px (never
below 20 px/s), and stops at 80 % of the playfield height (the upper part of the screen).

**Acceptance criteria**
- Given a Scissor comes in, then it stops at 80 % of the height.

*Sources: P05-R21.*

#### ENM-SCISSOR-09 — The arms at rest · MUST

The two arms are moving parts ([common.md](common.md)) hinged at its shoulders (6 px either side of
the centre, 2 px behind it), 30 px long, angled 25° out from straight down. They hold still while it
comes in and through the warning.

**Acceptance criteria**
- Given a Scissor coming in or warning, then its arms are still, 25° out from straight down.

*Sources: P05-R21.*

#### ENM-SCISSOR-10 — Warning lines · MUST

As soon as it stops, each living arm shows a warning line along its direction for 1 s, from its
emitter: the warning every laser has ([common.md](common.md)).

**Acceptance criteria**
- Given a Scissor starts its attack, then each living arm shows a warning line for 1 s before its
  laser appears on the same line.

*Sources: P05-R21.*

#### ENM-SCISSOR-11 — Closing twin lasers · MUST

After the warning, each living arm fires its laser (9 px wide, in the Lancer's laser style) along
the arm for 2 s, from its emitter, while both arms swing slowly 15° inward, so the two beams close
like scissors. The beams turn with their arms (a sweeping laser, unlike a beam that keeps its
heading). A destroyed arm's warning line or beam stops.

**Acceptance criteria**
- Given its lasers are firing, then the arms swing inward and the beams turn with their arms.
- Given an arm is destroyed while its laser fires, then that laser stops and the other goes on.

*Sources: P05-R21, D-090.*

#### ENM-SCISSOR-12 — Exit · MUST

Once the beams are over, the arms hold still again and the Scissor leaves upward at 190 px/s. It
attacks only once.

**Acceptance criteria**
- Given its beams end, then its arms stop swinging, its charge is 0, and it moves up and off the
  screen.

*Sources: P05-R21.*

#### ENM-SCISSOR-13 — The arms as parts · MUST

Each arm has its own hit circle (7 px, on the arm 16 px from its shoulder) and its own health
(70 HP); shots that hit an arm damage the arm, not the hull. A destroyed arm blows up as a part does
([common.md](common.md)): no points, no bonus.

**Acceptance criteria**
- Given an arm reaches 0 HP, then only that arm is destroyed and the Scissor goes on.

*Sources: P05-R21.*

#### ENM-SCISSOR-14 — Health, points and hit circle · MUST

The Scissor's hull has 240 HP and scores 800 points. Its hit circle is 14 px, at its centre.

**Acceptance criteria**
- Given a Scissor, then its hull takes 240 damage to destroy and scores 800 points, and the arms
  still on it blow up with it.

*Sources: P05-R21.*

#### ENM-SCISSOR-15 — Arms from its config, as engine specs · SHOULD

The Scissor's shoulders and arms are written in its config, and the game hands them to the engine
as the engine's own joint and part specs (`jointed_design`), as it does for the bosses. So the
engine reads the swing the config gives (amplitude, period, phase), in CPython and in the browser
alike.

**Acceptance criteria**
- Given a Scissor is made, then each arm is an engine part spec on its shoulder joint, and in 2 s
  of firing each arm turns 15° inward (no NaN angle).

*Sources: D-192.*

#### ENM-SCISSOR-16 — Elite kind, World 4 only · MUST

The Scissor is an elite kind: only World 4's waves use it. 4-2 brings it in, the third elite kind,
and every later level (4-2 to 4-5) uses it.

**Acceptance criteria**
- Given the wave scripts, then no level before 4-2 names the Scissor, and every level from 4-2 to
  4-5 does.

*Sources: P05-R24, D-090.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| size | 1.8 L | `src/game/config/enemies_elite.py` `ELITE_CONFIG.scissor.size` |
| health / points | 240 / 800 | `ELITE_CONFIG.scissor.stats` |
| hit radius | 14 px | `ELITE_CONFIG.scissor.stats.radius` |
| xRange | 25 % – 75 % of the width | when the wave gives no entry |
| entrySpeed / brakeDistance | 160 px/s / 60 px | slowest 20 px/s (`src/game/sim/enemies/scissor.py` `CREEP`) |
| stopFraction / exitSpeed | 0.8 / 190 px/s | exit upward |
| arm | 30 px long, 25° out, part 16 px from the shoulder, emitter 2 px up | `SCISSOR_ARM` |
| shoulders | `[±6, 2]` | `SCISSOR_ARMS` |
| arm health / radius | 70 / 7 px | `ELITE_CONFIG.scissor.design.parts` |
| laser | warning 1 s, beam 2 s, width 9, style `lancer`, sweeps | `ELITE_CONFIG.scissor.laser` |
| sweep | 15° inward | joint swing 15° over a period of 8 s, a quarter period (2 s) while the beams fire; phases 0 (right), 0.5 (left) |
| neon | `[0.95, 0.04, 0.22]`, drawn `[0.95, 0.95, 0.04]` | `src/game/config/enemy_look_elite.py` `ELITE_NEON.scissor` |
| triangle budget | 1200 (elite) | `src/game/config/enemy_look.py` `ENEMY_LOOK.budget.elite` |

## Notes

**Appears in** (`src/game/config/world_4/waves.py`): one Scissor in a phrase of its level's cycle
in each of [4-2](../worlds/world-4/4-2-inner-town.md), [4-3](../worlds/world-4/4-3-midtown.md),
[4-4](../worlds/world-4/4-4-business-district.md) and [4-5](../worlds/world-4/4-5-downtown.md); the
groups grow over each level. It is in no level's filler.

- The joints swing only while the beams fire (the enemy's `swinging` flag, D-090), so the inward
  swing starts with the beams; the beams follow their arms through `EnemyLaserSpec.sweeps`. The
  rule that a beam keeps its heading stays the default for other lasers.
- Known gaps: no unit test checks the model's size or its triangle count since the Python port
  (D-220).
