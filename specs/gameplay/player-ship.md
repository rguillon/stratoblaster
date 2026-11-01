# Player ships: stats and handling

> **Area:** Gameplay · **Prefix:** `GAME-SHIP` · **Related:** [controls.md](controls.md), [screen.md](screen.md), [weapons.md](weapons.md), [lives-and-damage.md](lives-and-damage.md), [../graphics/player-ships.md](../graphics/player-ships.md), [../ui/ship-select.md](../ui/ship-select.md)

The player picks one of three ships before a level: Balanced, Heavy and Light. They trade speed
for health; every one of them fires every weapon. This file gives their stats and how they handle
in flight: top speed, acceleration, banking and hitbox. What they look like is in
[graphics/player-ships.md](../graphics/player-ships.md); how they are picked in
[ui/ship-select.md](../ui/ship-select.md).

## Requirements

### GAME-SHIP-01 — Three ships · MUST

The player can fly three ships, in this order: **Balanced**, **Heavy** and **Light** (ids
`balanced`, `heavy`, `light`). Every ship fires all three weapons ([weapons.md](weapons.md)) and
has the same bombs, lives and hitbox; they differ only by their top speed and health.

**Acceptance criteria**
- Given the game data, then there are three ships with distinct ids, in that order (unit test).

*Sources: P02-R01, P02-R02, P02-R03, GD-30, D-015.*

### GAME-SHIP-02 — Top speed · MUST

A ship's top speed is its speed factor times the base speed `base_speed` (225 px/s): Balanced ×1
(225 px/s), Heavy ×0.8 (180 px/s), Light ×1.4 (315 px/s). The speeds are stored as factors of the
base speed, so the base speed tunes every ship at once.

**Acceptance criteria**
- Given the Light ship, then its top speed is 315 px/s (unit test).
- Given the three ships, then Light is faster than Balanced, which is faster than Heavy (unit test).

*Sources: P02-R01, P02-R02, P02-R03, D-004, D-044, D-047.*

### GAME-SHIP-03 — Health · MUST

A ship's health points are its health bar ([lives-and-damage.md](lives-and-damage.md)): Balanced
100, Heavy 140, Light 80. The slower ship has more health: Heavy > Balanced > Light.

**Acceptance criteria**
- Given the three ships, then their health is 100, 140 and 80, and the order is Heavy > Balanced >
  Light (unit test).

*Sources: P02-R01, P02-R02, P02-R03, D-050.*

### GAME-SHIP-04 — Little acceleration, top speed quickly · MUST

The ship has a little acceleration but reaches its top speed quickly: its velocity eases towards
the direction asked ([controls.md](controls.md)) at a constant rate, so it goes from rest to top
speed, and from top speed to rest, in `acceleration_time` (0.18 s, the same for every ship). Starts
and stops are felt, and the ship never drifts on: let go, it stops within that time.

**Acceptance criteria**
- Given a ship at rest, when full right is held, then it is at top speed after 0.18 s and not
  before (unit test).
- Given a ship at top speed, when the input is let go, then it is at rest 0.18 s later (unit test).

*Sources: GD-10, D-045, D-047.*

### GAME-SHIP-05 — Banking · MUST

The ship banks (rolls around its nose) as it moves sideways: the wing on the side it flies to
dips, up to `roll_max` (35°) at its full sideways speed, in proportion to its sideways speed as a
share of its own top speed (so every ship banks fully at its own top speed). The bank eases towards
that target at `roll_ease` (8 per second), so it rolls in and levels out smoothly. Banking is
visual only: it changes neither the flight nor the hitbox.

**Acceptance criteria**
- Given a ship flying right at its top speed for 1 s, then it is banked about 35° to the right.
- Given it then stops, then it levels out smoothly within about half a second.
- Given a banked ship, then its hitbox and its position are unchanged.

*Sources: D-045, D-047.*

### GAME-SHIP-06 — Small hitbox · MUST

The ship can only be hurt through a small hitbox: a circle of `hit_radius` (5 px) around the ship's
centre, the same for every ship, much smaller than its model (about 30 px across). Shots, beams and
enemies that touch the model but not the hitbox do nothing. The hitbox is not drawn on the ship
([graphics/player-ships.md](../graphics/player-ships.md)).

**Acceptance criteria**
- Given an enemy bullet passing 10 px from the ship's centre (with a 4 px bullet radius), then the
  ship takes no damage (unit test).

*Sources: GD-21, D-050, D-194.*

### GAME-SHIP-07 — Start position · MUST

The ship starts each level at the middle of the playfield across, `ship_start_y` (90 px) from the
bottom, after it has risen in from below the screen ([level-flow.md](level-flow.md)).

*Sources: P06-R02.*

### GAME-SHIP-08 — Ship data is validated · SHOULD

The ships are data: an id, a name, a speed factor and a health. The engine refuses a roster with no
ship, a duplicate id, a base speed or speed factor that is not positive, or a health that is not a
positive whole number.

**Acceptance criteria**
- Given a roster with two ships of the same id, then it is refused with a message naming the id
  (unit test).
- Given the game's own ships, then they pass the check.

**Discrepancy:** the check (`validate_player_ship_roster`) exists and is unit tested, but nothing
runs it on the game's data.

*Sources: D-004.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| base_speed | 225 px/s | `src/game/config/player_ships.py` `PLAYER_SHIPS["baseSpeedPxPerSec"]`; was 100 (P02), then 150 (D-044) |
| speed factors | Balanced 1, Heavy 0.8, Light 1.4 | `PLAYER_SHIPS["ships"][i]["maxSpeedFactor"]` |
| health | Balanced 100, Heavy 140, Light 80 | `PLAYER_SHIPS["ships"][i]["maxHealth"]` |
| acceleration_time | 0.18 s, rest to top speed | `src/config/game_controls.py` `GAME_CONTROLS_CONFIG.acceleration_seconds`; was 0.08 s (D-045) |
| roll_max | 35° | `src/config/game_play.py` `GAME_PLAY_CONFIG.roll.max_deg` |
| roll_ease | 8 per second (share of the gap closed) | `GAME_PLAY_CONFIG.roll.ease_per_sec` |
| hit_radius | 5 px | `src/game/config/hull.py` `HULL_RULES["hitRadius"]` |
| ship_start_y | 90 px | `src/config/game_play.py` `GAME_PLAY_CONFIG.ship_start_y` |

## Notes

- The light ship crosses the playfield in about 1.5 s (D-047).
- The 225 px/s base speed comes from two reviewer requests of +50 % each in phase 6 (D-044,
  D-047); the phase 2 text said 100 px/s.
