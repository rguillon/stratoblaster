# Sweeper

> **Area:** enemies · **Prefix:** `ENM-SWEEPER` · **Related:** [common.md](common.md),
> [lancer.md](lancer.md), [scissor.md](scissor.md), [shots](../graphics/shots.md)

The Sweeper is the laser enemy of **tier 2** (World 2, lime neon on a teal hull, over a
rust/concrete industrial desert): a hovering laser platform that stops in the upper third, shows a
warning line, then fires a laser that sweeps across a 70° arc, so the player has to move through the
gap or escape past its edge. Then it retreats upward.

## Requirements

### Look

#### ENM-SWEEPER-01 — A flat disc with a long barrel · MUST

The Sweeper is a hovering platform about `size` L across: a flat armoured disc over a flesh belly,
a turret hub on top and a long emitter barrel pointing along its nose. A lime neon ring runs round
the disc's rim and four glowing flesh beads sit on it.

*Sources: tier 2 brief.*

#### ENM-SWEEPER-02 — The barrel swings with the beam · MUST

The whole model turns with the Sweeper's heading, so the barrel visibly swings with the laser. The
laser leaves from the barrel's front (`muzzle`), which the model marks as a `laser` muzzle.

**Acceptance criteria**
- Unit test: the model has one `laser` muzzle.

*Sources: tier 2 brief.*

#### ENM-SWEEPER-03 — The emitter charges · MUST

A charge light at the barrel's tip brightens through the warning (`Enemy.charge`, ENM-23) and is at
full brightness while the laser fires.

*Sources: tier 2 brief.*

#### ENM-SWEEPER-04 — Three reactors, lime · MUST

Three reactors sit at the disc's rear (one in a flesh sac). Every light and the reactor flames are
tier 2's lime neon (ENM-48).

*Sources: tier 2 brief, ENM-48.*

### Behaviour

#### ENM-SWEEPER-05 — It stops in the upper third · MUST

The Sweeper comes in from above the top of the screen (X in `xRange` of the ship's reach, or the
wave's entry) at `entrySpeed`, slows down over its last `brakeDistance` (never below `creep`) and
stops at `stopFraction` of the playfield height. It does not move while its warning line or laser
shows.

*Sources: tier 2 brief.*

#### ENM-SWEEPER-06 — A warning line first · MUST

While it brakes, the Sweeper turns its barrel smoothly (eased in and out over its
`brakeDistance`) to the first edge of the arc: the one away from the player's side as it starts
braking (the beam will sweep towards the player and past). It reaches that edge as it stops (D-322;
it used to turn there at once on stopping). A warning line shows along it for
`laser.warningSeconds` while the charge light fills, without moving.

**Acceptance criteria**
- Given a Sweeper that stops, then its heading stays put for the warning and the charge goes 0 to 1.
- Given a Sweeper coming in, then its heading goes from straight down to the first edge while it
  brakes, by less than 3° a frame at 60 fps (unit test).

*Sources: tier 2 brief, ENM-19, D-322.*

#### ENM-SWEEPER-07 — The beam sweeps across a 70° arc · MUST

Then it fires a laser `laser.width` wide for `laser.firingSeconds`, while the whole platform turns
at a steady rate through `arcDeg` degrees, to the other edge of the arc. The beam sweeps with it
(`EnemyLaserSpec.sweeps`, ENM-32). Its laser's timing does not follow the level's fire-rate factor.

**Acceptance criteria**
- Given the Sweeper's laser firing, then its heading changes by `arcDeg` over `firingSeconds`.

*Sources: tier 2 brief, ENM-32.*

#### ENM-SWEEPER-08 — It retreats upward · MUST

Once its laser is over, the Sweeper moves away upward at `exitSpeed`.

*Sources: tier 2 brief.*

#### ENM-SWEEPER-09 — Health and points · MUST

The Sweeper has 90 health and scores 300 points. Its hit radius is a little smaller than its size.

*Sources: tier 2 brief, GD-21.*

#### ENM-SWEEPER-10 — Triangle budget · MUST

Its model stays within `ENEMY_LOOK.budget.tier2` (600 triangles, reactors counted as about 40).

*Sources: ENM-03.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `size` | 1.3 L | `src/game/config/enemy_sweeper.py` `SWEEPER_CONFIG` |
| `hp` / `points` | 90 / 300 | |
| hit radius | 15.0 px | `radius(1.3) × 0.8` |
| `entrySpeed` | 150 px/s | |
| `brakeDistance` / `creep` | 60 px / 20 px/s | `creep` is `CREEP` in `src/game/sim/enemies/sweeper.py` |
| `stopFraction` | 0.78 | of the playfield height |
| `laser.warningSeconds` / `firingSeconds` | 1 s / 2.2 s | |
| `laser.width` | 9 px | style `lancer` |
| `arcDeg` | 70° | the beam's travel, edge to edge |
| `barrelOffset` / `muzzle` | 21.1 px / (0, −22.9, 7) | the barrel's tip, and its front |
| `exitSpeed` | 200 px/s | |
| `xRange` | 0.25–0.75 | of the ship's reach |
| `neon` | tier 2's, `[0.25, 1, 0.1]` | `ENEMY_TIERS`, ENM-48 |

## Notes

**Tier:** 2 (laser). **Appears in:** World 2 (see `src/game/config/wave_plans.py`).

No engine change: the sweeping beam is the existing laser owner abstraction with `sweeps: true`, as
the [Scissor's](scissor.md) arms; here the owner's heading turns on its own.
