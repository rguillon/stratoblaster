# Gnat

> **Area:** Enemies (basic) · **Prefix:** `ENM-GNAT` · **Related:** [common rules](common.md),
> [Carrier](carrier.md), [level flow](../gameplay/level-flow.md), [bosses](../bosses/common.md)

The Gnat is the smallest and weakest enemy: an unmanned swarm drone that comes in groups of five,
one behind the other on the same S-shaped path down the screen. It never shoots; one level 1
bullet kills it. Carriers and some bosses launch Gnats too.

## Requirements

### Look

#### ENM-GNAT-01 — A pointed insect drone · MUST

The Gnat is a small, unmanned insect drone about `size` L long: a pointed flesh body, swollen in
the middle and tapering to a point at its nose, with a small head at the front carrying two eyes,
a neon band around its middle, and a thin bone feeler curling up its back. It has no cockpit.

**Acceptance criteria**
- Given the dev enemies viewer, then the Gnat reads as a drone, not a manned ship (manual check).
- Given the Gnat's model, then its nose is the front-most point of its body.

*Sources: P05-R01, P16-R03; redesign (single fan, pointed front).*

#### ENM-GNAT-02 — One ducted fan at the centre · MUST

A single fan stands at the centre of the Gnat's back, on the spine: a metal duct around a
two-bladed rotor that spins around the vertical axis.

**Acceptance criteria**
- Unit test: the model has one rotor, centred across the body and above its spine.

*Sources: P05-R01, P16-R03; redesign (single fan).*

#### ENM-GNAT-03 — Green, one reactor · MUST

The Gnat's lights (its ring, its eyes) and its reactor flame are bright green (was cyan). It has
one reactor at the rear.

*Sources: phase 5 review, D-231.*

### Behaviour

#### ENM-GNAT-04 — A group of five on one S-shaped path · MUST

A Gnat group is `groupSize` Gnats. They come in from above the top of the screen one after the
other, `groupDelay` apart, and follow the same predefined S-shaped path (`path`) down to below the
bottom of the screen at `speed`, their noses along the path. The path is mirrored towards the
wave's entry, or at random without one. A Gnat is done once it reaches the end of the path.

**Acceptance criteria**
- Given a Gnat group spawns, then its Gnats follow the same path with a fixed delay between them.
- Given a Gnat at the end of its path, then it is gone.

*Sources: P05-R01.*

#### ENM-GNAT-05 — It does not shoot · MUST

The Gnat never fires.

*Sources: P05-R01.*

#### ENM-GNAT-06 — One bullet kills it · MUST

The Gnat has `hp` health: a single level 1 bullet destroys it. It scores `points`.

*Sources: P05-R01.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `size` | 0.5 L | `src/game/config/enemies.py` `ENEMY_CONFIG["gnat"]["size"]` |
| `hp` / `points` | 10 / 50 | `ENEMY_CONFIG["gnat"]["stats"]` |
| hit radius | 7.2 px | `radius(0.5)` |
| `groupSize` / `groupDelay` | 5 / 0.3 s | |
| `speed` | 190 px/s | |
| `path` | (0.75, 1.1) → (0.75, 0.85) → (0.25, 0.65) → (0.75, 0.4) → (0.25, 0.18) → (0.4, −0.15) | fractions of the playfield (x across the ship's reach, y up) |
| `neon` | [0.1, 0.95, 1], drawn bright green | `src/game/config/enemy_look.py` `ENEMY_LOOK["neon"]["gnat"]` |
| rotor | 1 fan, 2 blades, 30 rad/s, centred on the spine | `ENEMY_LOOK["rotor"]`; model `GNAT_BODY` in `small_enemy_models.py` |

## Notes

**Appears in:** every level, 1-1 to 4-5. Every [Carrier](carrier.md) launches Gnats, and the
hangars and bays of some bosses do too (Gull Mothership, Harbour Kraken, Canopy Spider; see their
files). Launched Gnats are ordinary Gnats on their own path out of the launcher (see
[carrier.md](carrier.md)).

The P05 Gnat was a flat disc with three short fins, then (phase 5 review) a tri-rotor drone with a
sensor turret under its nose; the turret and its lens were removed as only visible from below. The
redesign replaced the three ducted fans at 120° and the round head with one central fan and a
pointed front.
