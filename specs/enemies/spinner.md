# Spinner

> **Area:** Enemies (basic) · **Prefix:** `ENM-SPINNER` · **Related:** [common rules](common.md),
> [shots](../graphics/shots.md)

The Spinner is a spiral turret: it comes down to a point in the upper half of the screen, stops,
spins faster while it sprays a spiral of bullets from its four pods for a few seconds, then leaves
upward.

## Requirements

### Look

#### ENM-SPINNER-01 — Four curled arms round an organic core · MUST

The Spinner is about `size` L across: an organic core with a neon heart in its centre, spinning
four sinew arms curled the same way round (a spiral), a flesh pod at the end of each with a metal
muzzle collar. The arms and pods replace the old ring with four spokes and its pods.

*Sources: P05-R06, P16-R03.*

#### ENM-SPINNER-02 — Muzzle lights, no reactor · MUST

The muzzle of each pod is a charge light, lit while the Spinner fires. The Spinner has no reactor:
it spins on itself.

**Acceptance criteria**
- Unit test: the model has four guns and no reactor.

*Sources: P05-R06, phase 5 review.*

#### ENM-SPINNER-03 — Yellow · MUST

The Spinner's heart and muzzle lights are bright yellow (was orange).

*Sources: P05-R06, D-231.*

### Behaviour

#### ENM-SPINNER-04 — It stops in the upper half · MUST

The Spinner comes in from above the top of the screen (X in `xRange` of the ship's reach, or the
wave's entry) and descends at `entrySpeed` to a height picked at random in `stopRange` (the upper
half), where it stops. It turns slowly (`idleSpin`) on the way in.

*Sources: P05-R06.*

#### ENM-SPINNER-05 — A spiral from its four pods · MUST

Stopped, the Spinner spins at `firingSpin` and fires for `fireDuration`: every `fireInterval`, a
bullet leaves each of its four pods, outwards in the direction the pod points, so the bullets'
directions turn with the arms and draw a spiral.

**Acceptance criteria**
- Given a Spinner firing, then its bullets leave from its 4 pods in directions that turn with it.

*Sources: P05-R06, GD-44.*

#### ENM-SPINNER-06 — It leaves upward · MUST

Once `fireDuration` has passed, the Spinner stops firing and leaves upward at `exitSpeed`.

**Acceptance criteria**
- Given 3 s of firing have passed, then the Spinner stops firing and leaves upward.

*Sources: P05-R06.*

#### ENM-SPINNER-07 — Health and points · MUST

The Spinner has `hp` health and scores `points`.

*Sources: P05-R06.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `size` | 1 L | `src/game/config/enemies.py` `ENEMY_CONFIG["spinner"]` |
| `hp` / `points` | 60 / 200 | |
| hit radius | 14.5 px | `radius(1)` |
| `entrySpeed` | 130 px/s | |
| `stopRange` | 0.62–0.8 | of the playfield height, picked at random |
| `idleSpin` / `firingSpin` | 60 °/s / 110 °/s | |
| `fireDuration` | 3 s | |
| `fireInterval` | 0.16 s | a bullet from each pod; 4 pods |
| `podRadius` | 15.3 px | pods' distance from the centre |
| `muzzles` | 18.4 px out, on the 4 pods, height 0 | `SPINNER_MUZZLE` |
| `exitSpeed` | 150 px/s | |
| `bullet` | 160 px/s, radius 4, style `orange` | |
| `xRange` | 0.25–0.75 | of the ship's reach |
| `neon` | [1, 0.5, 0.05], drawn bright yellow | `src/game/config/enemy_look.py` |

## Notes

**Appears in:** 1-3, 1-4, 1-5, 2-3, 2-4, 2-5, 3-2 to 3-5, 4-1 to 4-5.

The P05 Spinner was a ring with four spokes, a pod at the end of each and an orange neon core.
