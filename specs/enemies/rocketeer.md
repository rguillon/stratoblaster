# Rocketeer

> **Area:** Enemies (basic) · **Prefix:** `ENM-ROCKETEER` · **Related:** [common rules](common.md),
> [shots](../graphics/shots.md), [effects](../graphics/effects.md)

The Rocketeer is the missile carrier: a bulky enemy that descends slowly and launches a pair of
homing missiles at a steady beat. Its missiles can be shot down.

## Requirements

### Look

#### ENM-ROCKETEER-01 — A bulky armoured body · MUST

The Rocketeer is a bulky enemy about `size` L wide: a body of three swollen flesh segments with a
metal armour plate grafted on its back, two slanted neon eye slits on the plate.

*Sources: P05-R08, P16-R03.*

#### ENM-ROCKETEER-02 — A missile sac on each side · MUST

On each side lies a long egg sac (its missile pod) ending in a hexagonal launcher port (WPN-07). One
swept metal wing on each side joins the body to the pod, runs through it and comes out past its
outer side, a neon light along its leading edge there. The sac's lights are two glowing veins along
its flanks, not along the top of the launcher. The port's rim is the charge light: it glows brighter
as the missiles reload, fully when they are loaded (owner request 2026-11-05, D-278).

**Acceptance criteria**
- Unit test: the model has two missile mouths and two reactors.

*Sources: P05-R08, P16-R03, owner request 2026-11-05.*

#### ENM-ROCKETEER-03 — Two reactors · MUST

Two reactors sit at the back of its body.

*Sources: P05-R08, phase 5 review.*

#### ENM-ROCKETEER-04 — Yellow · MUST

The Rocketeer's lights, missile tips and reactor flames are bright yellow (the tips were red).

*Sources: P05-R08, D-231.*

### Behaviour

#### ENM-ROCKETEER-05 — It descends slowly · MUST

The Rocketeer comes in from above the top of the screen (X in `xRange` of the ship's reach, or the
wave's entry) and descends straight down at `speed`, nose down, until it leaves at the bottom.

*Sources: P05-R08.*

#### ENM-ROCKETEER-06 — A missile from each pod · MUST

While it is over the playfield, the Rocketeer launches one missile from the tip of each pod every
`fireInterval`, the first `firstShot` after it comes over the playfield. The missiles leave
straight down.

**Acceptance criteria**
- Given a Rocketeer launches, then two missiles leave, one from each pod's tip.

*Sources: P05-R08.*

#### ENM-ROCKETEER-07 — Homing missiles · MUST

Each missile flies at `missile.speed` and turns towards the player at no more than
`missile.turnRateDeg` for `missile.homingSeconds`, then flies straight on.

**Acceptance criteria**
- Given a Rocketeer missile in flight, then it turns towards the player no faster than its turn
  rate.

*Sources: P05-R08, D-032.*

#### ENM-ROCKETEER-08 — Missiles can be shot down · MUST

A missile has `missile.health` health: a single level 1 bullet shoots it down. A missile shot
down is destroyed with a small explosion.

**Acceptance criteria**
- Given a player shot hits a missile, then the missile is destroyed with a small explosion.

*Sources: P05-R08, GD-43.*

#### ENM-ROCKETEER-09 — Health and points · MUST

The Rocketeer has `hp` health and scores `points`. Its hit radius is a little smaller than its
width.

*Sources: P05-R08, GD-21.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `size` | 1.3 L | `src/game/config/enemies.py` `ENEMY_CONFIG["rocketeer"]` |
| `hp` / `points` | 100 / 300 | |
| hit radius | 15.0 px | `radius(1.3) × 0.8` |
| `speed` | 45 px/s | |
| `fireInterval` / `firstShot` | 3 s / 1 s | |
| `podOffset` | 16.3 px | each pod's distance from the centre |
| `muzzles` | (±16.3, −14.5, 0) | the pods' missile tips |
| `missile.speed` | 150 px/s | |
| `missile.turnRateDeg` / `homingSeconds` | 90 °/s / 3.5 s | |
| `missile.radius` / `health` | 5 px / 10 | one level 1 bullet |
| `missile.style` | `rocketeer` | look in [shots](../graphics/shots.md) |
| `xRange` | 0.2–0.8 | of the ship's reach |
| `neon` | [1, 0.12, 0.08], drawn bright yellow | `src/game/config/enemy_look.py` |

## Notes

**Appears in:** 1-4, 1-5, 2-3, 2-4, 2-5, 3-2 to 3-5, 4-1 to 4-5.

The P05 Rocketeer was a bulky hull with a missile pod on each side, the missile tips glowing red
when loaded.
