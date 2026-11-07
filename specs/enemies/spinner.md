# Spinner

> **Area:** Enemies (basic) · **Prefix:** `ENM-SPINNER` · **Related:** [common rules](common.md),
> [shots](../graphics/shots.md)

The Spinner is a spiral turret: a small ship inside a gun ring. It comes down to a point in the
upper half of the screen, stops, spins its ring faster while it sprays a spiral of bullets from its
four guns for a few seconds, then leaves upward.

## Requirements

### Look

#### ENM-SPINNER-01 — An inner body inside a spinning gun ring · MUST

The Spinner is about `size` L across, in two parts:

- **The inner body**, which does not spin: it always faces down the screen, towards the player. A
  flesh body with a dark cockpit canopy and a neon visor across its front, a metal plate on its
  back, and two engine pods at its tail. It is raised a little above the ring, so its reactors'
  flames pass over the ring, not through it.
- **The outer ring**, which spins round the body: a low metal ring, four spokes under the body to
  the hub it turns on, and four gun mounts on its outside, each with a collar its barrel comes out
  of. The ring, spokes, mounts and barrels turn together.

Nothing on it is curled or hooked (it must not read as a swastika). This replaces the four curled
sinew arms round an organic core.

**Acceptance criteria**
- Given a Spinner spinning, then its body keeps facing down the screen while its ring and guns
  turn.

*Sources: P05-R06, P16-R03, enemy redesign review.*

#### ENM-SPINNER-02 — Four recoiling guns, two reactors · MUST

The ring carries four guns, one on each mount, pointing straight out from the centre a quarter
turn apart. Each barrel recoils when it fires (WPN-03). The guns have no charge light and nothing
round them glows. The inner body has two reactors, one in each engine pod.

**Acceptance criteria**
- Unit test: the model has four guns and two reactors.

*Sources: P05-R06, phase 5 review, enemy redesign review.*

#### ENM-SPINNER-03 — Yellow · MUST

The Spinner's lights are bright yellow (was orange): the cockpit visor and a line along each
engine pod. The ring has no neon light: its edges glow with the hull's highlight (the edge trim,
GFX-TRIM-06). The spokes, the mounts and the guns have no light and no edge trim.

*Sources: P05-R06, D-231, enemy redesign review.*

### Behaviour

#### ENM-SPINNER-04 — It stops in the upper half · MUST

The Spinner comes in from above the top of the screen (X in `xRange` of the ship's reach, or the
wave's entry) and descends at `entrySpeed` to a height picked at random in `stopRange` (the upper
half), where it stops. Its ring turns slowly (`idleSpin`) on the way in.

*Sources: P05-R06.*

#### ENM-SPINNER-05 — A spiral from its four guns · MUST

Stopped, the Spinner spins its ring at `firingSpin` and fires for `fireDuration`: every
`fireInterval`, a bullet leaves each of its four guns, from the barrel's tip outwards along the
barrel, so the bullets' directions turn with the ring and draw a spiral.

**Acceptance criteria**
- Given a Spinner firing, then its bullets leave from its 4 guns in directions that turn with its
  ring, while its body keeps facing down the screen.

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
| `fireInterval` | 0.16 s | a bullet from each gun; 4 guns |
| `podRadius` | 15.3 px | the guns' distance from the centre |
| `muzzles` | 18.4 px out, on the 4 guns, height 0 | `SPINNER_MUZZLE` |
| `exitSpeed` | 150 px/s | |
| `bullet` | 160 px/s, radius 4, style `orange` | |
| `xRange` | 0.25–0.75 | of the ship's reach |
| `neon` | [1, 0.5, 0.05], drawn bright yellow | `src/game/config/enemy_look.py` |

## Notes

**Appears in:** 1-3, 1-4, 1-5, 2-3, 2-4, 2-5, 3-2 to 3-5, 4-1 to 4-5.

The P05 Spinner was a ring with four spokes, a pod at the end of each and an orange neon core.
P16 replaced it with four curled sinew arms round an organic core, which read as a swastika; the
enemy redesign review replaced that with the inner body inside a spinning gun ring.

In the simulation, the Spinner's heading stays pointing down the screen and the ring's rotation is
its turret's aim; the guns' barrels turn with that turret.
