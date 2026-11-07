# Prism

> **Area:** Enemies (tier 3, laser) · **Prefix:** `ENM-PRISM` · **Related:** [common rules](common.md),
> [Lancer](lancer.md), [Scissor](scissor.md)

The Prism is the laser kind of tier 3 (World 3, [common.md](common.md)): a crystalline laser
platform that stops in the upper third of the screen and fires two beams from the tips of its wings.
The beams start wide apart, turn together until they cross and cut the screen into an X, then turn
back, the crossing sliding down the screen. Unlike the [Scissor](scissor.md) (tier 4), its emitters
are fixed on the hull and cannot be shot off, and its beams cross rather than close.

## Requirements

### Look

#### ENM-PRISM-01 — A crystal on two wings · MUST

The Prism is a crystalline platform about `size` L across: an angular, faceted hull like a flattened
double-pointed crystal, with a wing swept forward on each side, each ending in a laser emitter.

*Sources: tier 3 rework (ENM-01).*

#### ENM-PRISM-02 — Metal facets and a glowing core · MUST

Its hull is metal ([common.md](common.md), Cyber-Organic): bevelled wing slabs and armour facets on
its back. A core crystal glows on its back, pulsing like a vein, with a neon strip along its length
and along the leading edge of each wing.

**Acceptance criteria**
- Unit test: the model has a metal hull, lit neon strips, and a lit (vein) core crystal.

*Sources: tier 3 rework.*

#### ENM-PRISM-03 — Triangle budget · MUST

The Prism's model (reactors included) stays within the tier 3 budget, `ENEMY_LOOK.budget.tier3`
(900, [common.md](common.md)).

**Acceptance criteria**
- Unit test: its triangle count is at most the tier 3 budget.

*Sources: tier 3 rework, ENM-03.*

#### ENM-PRISM-04 — Emitters that charge · MUST

Each wing ends in an emitter barrel whose mouth is a charge light: it brightens through the warning
and is at full brightness while the beams fire. The barrels' tips are the laser's muzzles (the model
and the simulation read the same `emitters`). It has three reactors: one at the tail and one at the
root of each wing.

**Acceptance criteria**
- Unit test: the model has two laser muzzles at the configured emitters, and charge lights.
- Given a Prism during the warning, then its `charge` rises from 0 to 1.

*Sources: tier 3 rework, ENM-23.*

### Behaviour

#### ENM-PRISM-05 — It stops in the upper third · MUST

The Prism comes in from above the top of the screen (X in `xRange` of the ship's reach, or the
wave's entry) fast, at `entrySpeed`, slows down over its last `brakeDistance` (never below `creep`),
and stops at `stopFraction` of the playfield height (above two thirds), nose down. It holds still (it
only turns, ENM-PRISM-07) while it aims and fires.

**Acceptance criteria**
- Given a Prism that reaches its stop height, then it stops and does not move until its last
  burst is over.

*Sources: tier 3 rework.*

#### ENM-PRISM-06 — Two warning lines, then two lasers · MUST

After it has aimed (ENM-PRISM-07), a thin warning line shows from each emitter, straight ahead, for
`warningSeconds`; then each emitter fires a laser `width` wide for `firingSeconds`.

**Acceptance criteria**
- Given a Prism starts its attack, then two lasers start at once, one per emitter, each with its
  warning line shown before the beam.

*Sources: tier 3 rework, ENM-19.*

#### ENM-PRISM-07 — It aims at the player, then fires straight ahead · MUST

Both beams always point straight ahead of the Prism, parallel, one per wing (a beam never turns
relative to the hull). It starts turning its nose to the player, easing in as it gets there,
while it is still slowing down on its way in, and fires its first burst the moment it stops. Before
each later burst it spends `aimSeconds` turning to the player again, stopped. It stops turning when the warning lines show and does not turn
again until the burst is over: the beams keep the direction it had then, whatever the player does.
It fires `bursts` bursts.

**Acceptance criteria**
- Given a Prism coming in, then it turns to the player while it slows down and no laser starts
  before it has stopped.
- Given the lasers have started, then both beams point along the Prism's heading and the heading
  does not change until the burst is over, even if the player moves.
- Given the first burst ends, then it aims again and fires a second burst.

*Sources: tier 3 rework, D-266.*

#### ENM-PRISM-08 — It leaves upward · MUST

Once its last burst is over, the Prism leaves upward at `exitSpeed`, its nose turning round to the way it flies, its `charge` back at 0.

*Sources: tier 3 rework.*

#### ENM-PRISM-09 — Fixed emitters · MUST

Its emitters are fixed on the hull: they do not move relative to the Prism and are not parts that
can be shot off. Only the Prism itself can be hit.

**Acceptance criteria**
- Given a Prism during its burst, then its emitters' positions do not change and its only hit
  target is the Prism.

*Sources: tier 3 rework.*

#### ENM-PRISM-10 — Tier 3 colours · MUST

The Prism is in tier 3: its lights and reactor flames are the chartreuse neon of the tier and its hull
is tinted indigo, applied by the model builder from the tier table (ENM-49).

**Acceptance criteria**
- Unit test: the Prism is a tier 3 kind and its neon is its tier's.

*Sources: tier 3 rework, ENM-49.*

#### ENM-PRISM-11 — Its timing does not follow the fire rate · MUST

The warning and firing times do not follow the level's fire-rate factor.

*Sources: tier 3 rework, ENM-22.*

#### ENM-PRISM-12 — Health and points · MUST

A Prism has `hp` health and scores `points`. Its hit circle is 0.8 of the usual one for its size.

*Sources: tier 3 rework, GD-21.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `size` | 1.5 L | `src/game/config/enemy_prism.py` `PRISM_CONFIG` |
| `hp` / `points` | 150 / 380 | `stats` |
| hit radius | `radius(1.5) * 0.8` | |
| `entrySpeed` / `brakeDistance` / `creep` | 150 px/s / 60 px / 20 px/s | `creep` is `CREEP` in `src/game/sim/enemies/prism.py` |
| `stopFraction` | 0.78 | of the playfield height |
| `warningSeconds` / `firingSeconds` | 1 s / 2 s | `laser`, style `lancer` |
| `width` | 9 px | `laser` |
| `bursts` | 50° to −35°, then −35° to 50° | `start` to `end`, positive outward |
| `gapSeconds` | 0.6 s | between the bursts |
| `emitters` | (∓21, −4, 2.5) | the wing tips |
| `exitSpeed` | 180 px/s | |
| `xRange` | 0.25–0.75 | of the ship's reach |
| triangle budget | 900 (tier 3) | `ENEMY_LOOK.budget.tier3` |
| `neon` | tier 3's | `ENEMY_LOOK.neon.prism` |

## Notes

**Appears in:** World 3 (`src/game/config/wave_plans.py`).

- Model: `src/game/view/enemies/tier3_prism_model.py`. Sim: `src/game/sim/enemies/prism.py`.
