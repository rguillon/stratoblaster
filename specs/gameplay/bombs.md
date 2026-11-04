# Bombs

> **Area:** Gameplay · **Prefix:** `GAME-BOMB` · **Related:** [controls.md](controls.md), [lives-and-damage.md](lives-and-damage.md), [bonuses.md](bonuses.md), [scoring.md](scoring.md), [weapons.md](weapons.md), [../graphics/effects.md](../graphics/effects.md), [../ui/hud.md](../ui/hud.md), [../audio/sfx.md](../audio/sfx.md), [../bosses/common.md](../bosses/common.md)

The bomb is the player's secondary weapon: one press sets one off, it damages every enemy on screen
at once, clears the enemy shots and keeps the ship safe for a second. The player has a few, gets
more from bomb bonuses and after a lost life, and keeps them from one level to the next. This file
gives its rules. Its controls are in [controls.md](controls.md); its shockwave and flash in
[graphics/effects.md](../graphics/effects.md); its count in the HUD in [ui/hud.md](../ui/hud.md).

## Requirements

### GAME-BOMB-01 — Bombs held · MUST

The player starts with `bombs_start` (3) bombs: in the first level played, and after a Continue.
Other levels start with the bombs kept from the level completed before
([lives-and-damage.md](lives-and-damage.md) GAME-LIFE-12). Each bomb bonus adds one
([bonuses.md](bonuses.md)). There is no maximum.

**Acceptance criteria**
- Given a fresh start, then a level starts with 3 bombs (unit test).
- Given 9 bombs, when a bomb bonus is picked up, then the player has 10 (unit test).

*Sources: GD-32, P11-R05, D-091, D-154.*

### GAME-BOMB-02 — Topped up after a lost life · MUST

When the player loses a life, the bomb count goes back up to `bombs_start` if it was lower; a
higher count is kept.

**Acceptance criteria**
- Given 1 bomb left, when a life is lost, then the player has 3; given 4 bombs, it stays 4 (unit
  test).

*Sources: P11-R05.*

### GAME-BOMB-03 — Setting a bomb off · MUST

Each press of the bomb control ([controls.md](controls.md)) sets one bomb off, if a bomb is left
and no bomb is going off; it uses one up. A press with no bomb left, or while a bomb is going off,
does nothing. A bomb can only be set off while the player flies the ship: not while it rises in or
flies off, nor once the game is over. A bomb lasts `bomb_duration` (1 s).

**Acceptance criteria**
- Given 3 bombs, when the bomb key is pressed, then a bomb goes off and 2 are left (unit test).
- Given a bomb going off, when the key is pressed again, then nothing more happens (unit test).
- Given no bomb left, when the key is pressed, then nothing happens (unit test).
- Given the ship rising in, when the key is pressed, then no bomb goes off (unit test).

*Sources: P11-R05.*

### GAME-BOMB-04 — Damage to everything on screen · MUST

When a bomb goes off, every target on screen at that moment ([screen.md](screen.md)
GAME-SCREEN-04) takes `bomb_damage` (100) once: every enemy, every boss part, and the boss core
unless a part shields it ([bosses/common.md](../bosses/common.md)). That is enough to destroy most
low-level enemies: every World 1 kind up to the Rocketeer (100 health); a Carrier (300 health) is
only hurt. Enemies destroyed by a bomb score and drop bonuses as usual.

**Acceptance criteria**
- Given 5 Hornets and 1 Carrier on screen, when a bomb goes off, then every Hornet is destroyed and
  the Carrier loses 100 health (unit test).
- Given a boss whose core is shielded by a part, when a bomb goes off, then the part takes the
  damage and the core does not (unit test).
- Given an enemy above the top edge, then the bomb does not hurt it.

*Sources: GD-32, P11-R05, D-092.*

### GAME-BOMB-05 — Clearing the enemy shots · MUST

For the whole time a bomb goes off, every enemy shot is removed on every step: the enemy bullets
and missiles, and the enemy lasers (their warning lines included). Shots fired during the bomb are
removed too, so none hits the ship right after it.

**Acceptance criteria**
- Given enemy bullets, missiles and a laser on screen, when a bomb goes off, then they are all gone
  (unit test).
- Given an enemy firing during the bomb, then its shots are gone on the next step (unit test).

*Sources: P11-R05, D-092.*

### GAME-BOMB-06 — The ship is safe · MUST

While a bomb goes off, the ship cannot be hurt by anything. This is not the invincibility after a
hit: the ship does not blink.

**Acceptance criteria**
- Given a bomb going off, when an enemy shot or an enemy reaches the ship, then the ship loses no
  health (unit test).

*Sources: P11-R05, D-092.*

### GAME-BOMB-07 — Feedback · MUST

A bomb going off is shown by a shockwave ring growing from where the ship was over the whole
playfield, with a short flash kept below 3 flashes a second
([graphics/effects.md](../graphics/effects.md)), and plays the bomb sound
([audio/sfx.md](../audio/sfx.md)). The HUD shows the bombs left ([ui/hud.md](../ui/hud.md)).

*Sources: P11-R05, D-154.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| bombs_start | 3 | `src/game/config/bombs.py` `BOMB_RULES["start"]`; also after a Continue, and the floor after a lost life |
| bomb_damage | 100 | `BOMB_RULES["damage"]` |
| bomb_duration | 1 s | `BOMB_RULES["seconds"]` |
| bombs maximum | none | `BOMB_RULES` sets no `max` (D-154; was 5, P11-R07) |

## Notes

- The P11-R05 text cleared only the shots on screen when the bomb goes off; clearing every enemy
  shot for the whole second is D-092's choice, so shots fired during the bomb do not hit right
  after it.
