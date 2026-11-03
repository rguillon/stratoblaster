# Harrier

> **Area:** enemies · **Prefix:** `ENM-HARRIER` · **Related:** [common.md](common.md),
> [rocketeer.md](rocketeer.md), [shots](../graphics/shots.md)

The Harrier is the missile launcher of **tier 2** (World 2, lime neon on a teal hull, over a
rust/concrete industrial desert). A fast, agile gunship: it comes in from the top, brakes, holds in
the upper third and launches one fast homing missile at the player every 2.5 s, strafing slowly
sideways, then leaves upward after its last missile. Its missiles are faster and turn tighter than
the [Rocketeer's](rocketeer.md): they must be shot down or out-turned.

## Requirements

### Look

#### ENM-HARRIER-01 — A sleek swept dart · MUST

The Harrier is a sleek, swept dart about `size` L long: a slim flesh fuselage with a metal spike on
its nose, two eyes, a neon vein along its back, and two swept metal wings each with a neon light
along its leading edge.

**Acceptance criteria**
- Unit test: the model has flesh, hull and neon geometry.

*Sources: tier 2 brief.*

#### ENM-HARRIER-02 — Twin missile rails under the wings · MUST

A missile rail hangs under each wing on a short sinew strut. The two rails' tips (`muzzles`) are
where the missiles leave from, and the model marks them as `missile` muzzles.

**Acceptance criteria**
- Unit test: the model has two `missile` muzzles, mirrored across its centre.

*Sources: tier 2 brief.*

#### ENM-HARRIER-03 — Charge lights on the rails · MUST

A charge light sits at each rail's tip: it brightens as the next missile is due (`Enemy.charge`,
ENM-23).

*Sources: tier 2 brief.*

#### ENM-HARRIER-04 — One reactor, lime · MUST

One reactor sits at the back of the fuselage, set in a flesh sac. Every light and the reactor flame
are tier 2's lime neon (ENM-48).

*Sources: tier 2 brief, ENM-48.*

### Behaviour

#### ENM-HARRIER-05 — It comes in, brakes and holds in the upper third · MUST

The Harrier comes in from above the top of the screen (X in `xRange` of the ship's reach, or the
wave's entry) at `entrySpeed`, slows down over its last `brakeDistance` (never below `creep`) and
holds at `stopFraction` of the playfield height, nose down.

*Sources: tier 2 brief.*

#### ENM-HARRIER-06 — It strafes slowly while it holds · MUST

While it holds, the Harrier slides sideways at `strafeSpeed`, first towards the middle of the
screen, and turns back `strafeMargin` from either side edge. It does not change height.

**Acceptance criteria**
- Given a holding Harrier, then it moves sideways at `strafeSpeed` and reverses at the margins.

*Sources: tier 2 brief.*

#### ENM-HARRIER-07 — One fast homing missile at a time · MUST

While it holds, the Harrier launches one missile every `fireInterval` (the first `firstShot` after
it holds), from its two rails in turn, straight down. The timer follows the level's fire-rate
factor. Each missile flies at `missile.speed` and turns towards the player at no more than
`missile.turnRateDeg` for `missile.homingSeconds`, then flies straight on: faster and tighter than
the Rocketeer's. A missile has `missile.health` health (the Rocketeer's): a level 1 bullet shoots
it down with a small explosion (ENM-18).

**Acceptance criteria**
- Given a holding Harrier, then a missile leaves a rail every `fireInterval`, alternately left and
  right.
- Given the Harrier's missile spec, then its speed and turn rate are above the Rocketeer's.

*Sources: tier 2 brief, ENM-18.*

#### ENM-HARRIER-08 — It leaves upward after its last missile · MUST

After `missiles` missiles the Harrier stops launching and flies away upward at `exitSpeed`.

*Sources: tier 2 brief.*

#### ENM-HARRIER-09 — Health and points · MUST

The Harrier has 60 health and scores 220 points. Its hit radius is about its size.

*Sources: tier 2 brief, GD-21.*

#### ENM-HARRIER-10 — Triangle budget · MUST

Its model stays within `ENEMY_LOOK.budget.tier2` (600 triangles, reactors counted as about 40).

*Sources: ENM-03.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `size` | 0.9 L | `src/game/config/enemy_harrier.py` `HARRIER_CONFIG` |
| `hp` / `points` | 60 / 220 | |
| hit radius | 13.0 px | `radius(0.9)` |
| `entrySpeed` | 260 px/s | |
| `brakeDistance` / `creep` | 90 px / 30 px/s | `creep` is `CREEP` in `src/game/sim/enemies/harrier.py` |
| `stopFraction` | 0.78 | of the playfield height |
| `strafeSpeed` / `strafeMargin` | 28 px/s / 40 px | |
| `fireInterval` / `firstShot` | 2.5 s / 0.8 s | |
| `missiles` | 4 | then it leaves |
| `exitSpeed` | 280 px/s | |
| `muzzles` | (±6.8, −9.6, −1.4) | the rails' tips |
| `missile.speed` | 240 px/s | Rocketeer: 150 |
| `missile.turnRateDeg` / `homingSeconds` | 150 °/s / 2.5 s | Rocketeer: 90 °/s / 3.5 s |
| `missile.radius` / `health` | 4 px / 10 | one level 1 bullet; style `rocketeer` |
| `xRange` | 0.2–0.8 | of the ship's reach |
| `neon` | tier 2's, `[0.25, 1, 0.1]` | `ENEMY_TIERS`, ENM-48 |

## Notes

**Tier:** 2 (missile). **Appears in:** World 2 (see `src/game/config/wave_plans.py`).
