# Weaver

> **Area:** Enemies (basic) · **Prefix:** `ENM-WEAVER` · **Related:** [common rules](common.md),
> [shots](../graphics/shots.md)

The Weaver sways left and right along a sine wave on its way down the screen, firing a pair of
bullets aimed at the player, one from each of its twin bodies.

## Requirements

### Look

#### ENM-WEAVER-01 — Two serpents joined by a glowing bar · MUST

The Weaver is about `size` L long: two serpents side by side, each a swollen flesh head with two
eyes and a wavy sinew tail, joined by a web of membrane flesh under a glowing neon bar (the old
twin hulls and their neon bar). It has no wings.

*Sources: P05-R05, P16-R03.*

#### ENM-WEAVER-02 — A gun on each snout, a reactor at each tail · MUST

A metal gun barrel runs along each serpent's snout, a charge light at its tip, and a reactor sits
at the end of each tail.

**Acceptance criteria**
- Unit test: the model has two reactors, two guns and no wings.

*Sources: P05-R05, phase 5 review, D-057.*

#### ENM-WEAVER-03 — Green · MUST

The Weaver's lights, charge lights and reactor flames are bright green.

*Sources: P05-R05, D-231.*

### Behaviour

#### ENM-WEAVER-04 — A sine sway on the way down · MUST

The Weaver comes in from above the top of the screen (its centre X in `xRange` of the ship's reach,
or the wave's entry) and moves down at `speed`, its X swaying either side of that centre:
X = centre + `amplitude` × sin(2π × distance come down / `wavelength`). Its nose follows its way.

**Acceptance criteria**
- Given a Weaver moving, then its horizontal position is a sine of how far it has come down.

*Sources: P05-R05.*

#### ENM-WEAVER-05 — A pair of aimed bullets · MUST

While it is over the playfield, the Weaver fires a pair of bullets every `fireInterval` (the first
half an interval after it comes over the playfield): one from each snout gun, each aimed at the
player from where it leaves.

**Acceptance criteria**
- Given a Weaver fires, then two bullets leave, one from each gun, both aimed at the player.

*Sources: P05-R05, GD-44.*

#### ENM-WEAVER-06 — Health and points · MUST

The Weaver has `hp` health and scores `points`.

*Sources: P05-R05.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `size` | 0.9 L | `src/game/config/enemies.py` `ENEMY_CONFIG["weaver"]` |
| `hp` / `points` | 30 / 120 | |
| hit radius | 13.0 px | `radius(0.9)` |
| `speed` | 85 px/s | |
| `amplitude` / `wavelength` | 90 px / 280 px | |
| `fireInterval` | 2 s | first shot after 1 s |
| `bullet` | 200 px/s, radius 4, style `green` | |
| `muzzles` | (±10, −15.8, 1.9) | the snout guns' tips |
| `xRange` | 0.3–0.7 | of the ship's reach |
| `neon` | [0.2, 1, 0.3], drawn bright green | `src/game/config/enemy_look.py` |

## Notes

**Appears in:** every level but 1-1 (1-2 to 4-5).

The P05 Weaver was a twin-hull catamaran with its two hulls joined by a glowing green neon bar. Its
sway can take it a little past the ship's reach (D-048).
