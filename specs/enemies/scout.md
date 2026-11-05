# Scout

> **Area:** Enemies (basic) · **Prefix:** `ENM-SCOUT` · **Related:** [common rules](common.md),
> [shots](../graphics/shots.md)

The Scout is the first enemy that shoots: a light winged flyer that comes slowly straight down the
screen, firing one bullet aimed at the player at a steady beat.

## Requirements

### Look

#### ENM-SCOUT-01 — A light winged scout · MUST

The Scout is a light fighter about `size` L long, one blended airframe that does not look like an
insect: a metal fighter fuselage, widest in the middle and closing to a point at the nose, with
fixed swept wings in metal with a neon leading edge (nothing flaps) and a small tailplane, the
wings' roots faired into the fuselage, and no fin. A flesh canopy sits on its back ahead of the
turret, with a neon visor across its front; it has no eyes.

*Sources: P05-R03, P16-R03, P16-R07, owner requests 2026-11-05 (D-272, D-277).*

#### ENM-SCOUT-02 — Twin reactors under the wings · MUST

A reactor sits at the trailing root of each wing, its nozzle opening in the end of an engine nacelle
faired into the fuselage's flank (part of the body, not hanging behind the tail on its own).

**Acceptance criteria**
- Unit test: the model has two reactors, no flapping wing and one gun.

*Sources: P05-R03, phase 5 review, owner request 2026-11-05.*

#### ENM-SCOUT-03 — A gun on a turret · MUST

A metal gun barrel stands on a turret ring on the fuselage's back, pointing ahead, a charge light at
its tip; its muzzle is where the Scout's bullets leave from (WPN-01 to WPN-03).

*Sources: P05-R03, D-057.*

#### ENM-SCOUT-04 — Green · MUST

The Scout's lights, its charge light and its reactor flames are bright green (was cyan).

*Sources: P05-R03, D-231.*

### Behaviour

#### ENM-SCOUT-05 — Straight down, slowly · MUST

The Scout comes in from above the top of the screen (X in `xRange` of the ship's reach, or the
wave's entry) and flies straight down at `speed`, nose down, until it leaves at the bottom.

*Sources: P05-R03.*

#### ENM-SCOUT-06 — One aimed bullet at a steady beat · MUST

While it is over the playfield, the Scout fires one bullet aimed at the player every
`fireInterval`, the first `firstShot` after it comes over the playfield, from its nose gun.

**Acceptance criteria**
- Given a Scout on screen, then each of its bullets moves along the line from its muzzle to the
  player at the moment it was fired.
- Given a Scout above the playfield, then it does not fire.

*Sources: P05-R03, GD-44.*

#### ENM-SCOUT-07 — Health and points · MUST

The Scout has `hp` health and scores `points`.

*Sources: P05-R03.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `size` | 0.8 L | `src/game/config/enemies.py` `ENEMY_CONFIG["scout"]` |
| `hp` / `points` | 30 / 100 | |
| hit radius | 11.6 px | `radius(0.8)` |
| `speed` | 75 px/s | |
| `fireInterval` / `firstShot` | 1.5 s / 0.6 s | |
| `bullet` | 210 px/s, radius 4, style `red` | |
| `muzzles` | (0, −13.3, 1.3) | the nose gun's tip |
| `xRange` | 0.15–0.85 | of the ship's reach |
| `neon` | [0.05, 0.9, 1], drawn bright green | `src/game/config/enemy_look.py` |

## Notes

**Appears in:** every level, 1-1 to 4-5.

The P05 Scout was a small delta wing with twin tail booms and a cyan neon strip along each boom.
Its first gun sat under its nose and was removed as only visible from below (phase 5 review); the
nose gun on top came with the muzzles (D-057).
