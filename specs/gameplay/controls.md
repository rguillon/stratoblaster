# In-game controls

> **Area:** Gameplay · **Prefix:** `GAME-CTRL` · **Related:** [player-ship.md](player-ship.md), [weapons.md](weapons.md), [bombs.md](bombs.md), [../ui/menu-input.md](../ui/menu-input.md), [../ui/pause-menu.md](../ui/pause-menu.md), [../ui/hud.md](../ui/hud.md), [../dev/debug-options.md](../dev/debug-options.md)

The controls of a level being played: moving the ship, shooting, switching the weapon, setting a
bomb off and pausing, on the keyboard, a gamepad and a touch screen, all at once. The menus have
their own input ([ui/menu-input.md](../ui/menu-input.md)); the debug keys of a level are in
[dev/debug-options.md](../dev/debug-options.md). How fast the ship answers a direction (its
acceleration) is the ship's handling, in [player-ship.md](player-ship.md).

## Requirements

### GAME-CTRL-01 — The bindings · MUST

In a level, the actions are bound as follows:

| Action | Keyboard | Gamepad (standard mapping) | Touch |
|--------|----------|----------------------------|-------|
| Move | arrows, or W A S D | left stick, or D-pad | drag anywhere on the playfield |
| Shoot (held) | Space | A (button 0) or right trigger (button 7) | on-screen fire button, held |
| Switch weapon (per press) | E | — | — |
| Bomb (per press) | R or Left Shift | X / Square (button 2) or left bumper (button 4) | on-screen `BOMB` button |
| Pause | Escape or P | Start (button 9) or Select / View (button 8) | on-screen `❚❚` button |

Keys are read by their position (`KeyboardEvent.code`), not by the letter they print, so the same
keys work on QWERTY and AZERTY keyboards. Backspace and gamepad B do nothing in a level. E was
first given to the bomb (GD §2); it switches the weapon instead, and the bomb has R and Left Shift.

**Acceptance criteria**
- Given a level, when each binding of the table is used, then its action happens (unit tests on
  the game controls, e2e by key).
- Given an AZERTY keyboard, when the keys at the W A S D positions are held, then the ship moves.
- Given E is pressed, then the weapon switches and no bomb goes off.

*Sources: GD controls table, P06-R02, D-039, D-043, D-091, D-095, P11-R06.*

### GAME-CTRL-02 — Every device at once · MUST

The keyboard, every connected gamepad and the touch screen work at the same time, merged. The
direction used is the strongest of the keys and the gamepads (a tie goes to the keys); a touch
drag, when there is one, takes over. Any device's fire input shoots. Touch fire, touch bomb and the
drag work together.

**Acceptance criteria**
- Given the keys held left and a gamepad stick half right, then the ship flies left (unit test).
- Given two gamepads, then the stronger stick steers and either fire button shoots (unit test).
- Given a touch screen, when the `BOMB` button is tapped while the fire button is held and a
  finger drags, then a bomb goes off and the ship still shoots and moves (e2e).

*Sources: D-039, P11-R06.*

### GAME-CTRL-03 — Keys and pad: direction · MUST

Held direction keys give a direction of length 1 (a diagonal is not faster). The gamepad's left
stick gives its own deflection, so a stick pushed halfway flies at half speed; deflections under
the dead zone (`stick_dead_zone`) are ignored, and longer ones are cut to length 1. The D-pad works
like the keys. Up on the stick is up on the screen.

**Acceptance criteria**
- Given Up and Right held, then the direction is (0.71, 0.71) (unit test).
- Given the stick pushed 0.15 to the right, then the ship does not move; pushed 0.5, it flies at
  half its top speed (unit test).

*Sources: GD controls table, D-039.*

### GAME-CTRL-04 — Touch: the ship follows the finger · MUST

On a touch screen, dragging a finger anywhere over the playfield moves the ship by the distance
dragged (in logical pixels, whatever the stage's scale). The ship covers it at most at its top
speed: what it could not cover in a step waits for the next steps. The fire button and the bomb
button are drawn only on coarse pointers (touch screens); the touch bomb button shows the bombs
left and is dimmed with none ([ui/hud.md](../ui/hud.md)).

**Acceptance criteria**
- Given a drag of 100 px in one step and a ship whose top speed covers 4 px a step, then the ship
  moves 4 px that step and the rest over the next steps (unit test).
- Given a mouse (fine pointer), then the fire and bomb buttons are not shown.

*Sources: GD controls table, D-039, P11-R06.*

### GAME-CTRL-05 — Shooting is held · MUST

The ship shoots for as long as a fire input is held, and stops when every fire input is let go.

**Acceptance criteria**
- Given Space held, then the ship shoots; released, it stops (unit test).

*Sources: GD controls table, P06-R02.*

### GAME-CTRL-06 — Presses, not holds · MUST

Weapon switch and bomb inputs count presses: one action per press, however long it is held (key
repeats do not count; a gamepad button counts when it goes down). Each tap on the touch `BOMB`
button is one press.

**Acceptance criteria**
- Given E held for 3 s, then the weapon switches once (unit test).
- Given the bomb key held for 3 s, then one bomb goes off (unit test).
- Given the gamepad's bomb button held, then one bomb goes off until it is let go and pressed again
  (unit test).

*Sources: D-043, P11-R05, P11-R06.*

### GAME-CTRL-07 — Nothing carries into a level · MUST

Presses made outside a level (on a menu, or while the level loads) do not carry into it: the
controls are cleared when a level is built and again when it starts. When the window loses the
focus, every held key and the touch inputs are let go, so the ship does not keep flying or
shooting on its own.

**Acceptance criteria**
- Given R pressed on the level select, when the level starts, then no bomb goes off (unit test).
- Given the window loses the focus while a key is held, then the ship stops (unit test).

*Sources: D-092.*

### GAME-CTRL-08 — Pause from the game · MUST

Each pause binding of GAME-CTRL-01 pauses the level and opens the pause menu
([ui/pause-menu.md](../ui/pause-menu.md)). The level also pauses by itself when the page is hidden
or the gamepad in use is disconnected, and never resumes by itself.

**Acceptance criteria**
- Given a level, when Escape, P, gamepad Start or Select, or the `❚❚` button is pressed, then the
  level is paused (unit test, e2e).
- Given the gamepad last used to play is unplugged, then the level pauses, once (unit test).

*Sources: GD controls table, D-095.*

### GAME-CTRL-09 — Bindings in config · SHOULD

The keys and buttons of every action are in one config next to each other (fire, switch, bomb in
the game controls config; pause in the menu input config), so they can be remapped later
(ENG-112). There is no remapping screen.

*Sources: P11-R06, D-039.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| fire keys / buttons | `Space`; gamepad 0, 7 | `src/config/game_controls.py` `GAME_CONTROLS_CONFIG` |
| switch keys | `KeyE` | same |
| bomb keys / buttons | `KeyR`, `ShiftLeft`; gamepad 2, 4 | same |
| move keys | arrows, `KeyW` `KeyA` `KeyS` `KeyD` | `src/input/held_directions.py` `DIRECTION_KEYS` |
| D-pad | buttons 12, 13, 14, 15 (up, down, left, right) | `src/config/game_controls.py` |
| stick | axes 0 (X), 1 (Y, down positive); `stick_dead_zone` 0.2 | same |
| pause keys / buttons | `Escape`, `KeyP`; gamepad 9, 8 | `src/config/menu_input.py` `MENU_INPUT_CONFIG` |

## Notes

- The weapon switch has no gamepad or touch binding (D-043 left it for later; still open).
- In a level started with the debug URL options, ← and → are the playback keys and do not move
  the ship (A / D still do): see [dev/debug-options.md](../dev/debug-options.md) (D-039).
- Before the pause menu (phase 12), Escape left the level for the title (P06-R02, D-041); it now
  pauses, and a level is left from the pause menu (D-095).
