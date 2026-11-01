# Lancer

> **Area:** Enemies (basic) · **Prefix:** `ENM-LANCER` · **Related:** [common rules](common.md),
> [shots](../graphics/shots.md)

The Lancer is the laser enemy: it moves to a point near the top of the screen, stops, shows a
warning line straight down for one second, fires a laser along it, then backs away.

## Requirements

### Look

#### ENM-LANCER-01 — A long laser lance · MUST

The Lancer is a long, narrow enemy about `size` L long: a body of four swollen flesh segments with
two eyes, two neon stripes along its back, and a metal lance grafted on its head, ending in the
glowing laser emitter.

*Sources: P05-R07, P16-R03.*

#### ENM-LANCER-02 — Two fins and three reactors · MUST

Two flesh fins (membrane with sinew edges) sweep back from its tail. It has three reactors: a main
one at the tail and one at the back of each fin.

**Acceptance criteria**
- Unit test: the model has three reactors and one laser emitter.

*Sources: P05-R07, phase 5 review.*

#### ENM-LANCER-03 — The emitter charges · MUST

The emitter is a charge light: it brightens through the warning and is at full brightness while
the laser fires.

*Sources: P05-R07, D-032.*

#### ENM-LANCER-04 — Yellow · MUST

The Lancer's lights, emitter and reactor flames are bright yellow (was red).

*Sources: P05-R07, D-231.*

### Behaviour

#### ENM-LANCER-05 — It stops at a point near the top · MUST

The Lancer comes in from above the top of the screen (X in `xRange` of the ship's reach, or the
wave's entry) at `entrySpeed`, slows down over its last `brakeDistance` (never below `creep`), and
stops at `stopFraction` of the playfield height, nose down.

*Sources: P05-R07.*

#### ENM-LANCER-06 — A warning line, then the laser · MUST

As it stops, the Lancer shows a thin warning line straight down from its emitter for
`warningSeconds`, then fires a laser `width` wide along that line for `firingSeconds`. It does not
move while the warning line or the laser shows. Its laser's timing does not follow the level's
fire-rate factor.

**Acceptance criteria**
- Given a Lancer starts its attack, then a warning line shows for 1 s before the laser appears on
  the same line.
- Given the warning or the laser showing, then the Lancer holds still.

*Sources: P05-R07, GD-43, D-036.*

#### ENM-LANCER-07 — It backs away upward · MUST

Once its laser is over, the Lancer moves away upward at `exitSpeed`.

*Sources: P05-R07.*

#### ENM-LANCER-08 — Health and points · MUST

The Lancer has `hp` health and scores `points`. Its hit radius is smaller than its length (a
circle inside a long body).

*Sources: P05-R07, GD-21.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `size` | 1.3 L | length; `src/game/config/enemies.py` `ENEMY_CONFIG["lancer"]` |
| `hp` / `points` | 80 / 250 | |
| hit radius | 10.3 px | `radius(1.3) × 0.55` |
| `entrySpeed` | 170 px/s | |
| `brakeDistance` / `creep` | 60 px / 20 px/s | `creep` is `CREEP` in `src/game/sim/enemies/lancer.py` |
| `stopFraction` | 0.8 | of the playfield height |
| `warningSeconds` / `firingSeconds` | 1 s / 1.5 s | `laser` |
| `width` | 10 px | `laser`; style `lancer` |
| `emitterOffset` / `muzzle` | 21.1 px / (0, −22.9, 0) | the emitter at the nose, and the front of it |
| `exitSpeed` | 200 px/s | |
| `xRange` | 0.15–0.85 | of the ship's reach |
| `neon` | [1, 0.25, 0.35], drawn bright yellow | `src/game/config/enemy_look.py` |

## Notes

**Appears in:** 1-4, 1-5, 2-2 to 2-5, 3-2 to 3-5, 4-1 to 4-5.

The P05 Lancer was a long needle hull with a glowing emitter at its nose and two small side fins.
With the tilted camera, it stops close to the top edge of the screen.
