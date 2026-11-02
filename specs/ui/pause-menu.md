# Pause menu

> **Area:** UI · **Prefix:** `UI-PAUSE` · **Related:** [screen-flow.md](screen-flow.md), [menu-input.md](menu-input.md), [settings.md](settings.md), [hud.md](hud.md), [../gameplay/controls.md](../gameplay/controls.md), [../gameplay/scoring.md](../gameplay/scoring.md), [../audio/engine.md](../audio/engine.md), [../01-engineering.md](../01-engineering.md)

During a level the player can pause: the level freezes, dimmed, under a small menu to resume, open
the settings or leave the level. The level also pauses by itself when the page is hidden or the
gamepad in use is lost. What the music and sounds do while paused is in
[audio/engine.md](../audio/engine.md).

## Requirements

### UI-PAUSE-01 — Pause controls · MUST

During a level, the game is paused by:
- the keyboard: `Escape` and `KeyP`, by key position (QWERTY and AZERTY);
- a gamepad (standard mapping): Start (button 9) and Select / View (button 8);
- the on-screen pause button `❚❚` (UI-PAUSE-02).

**Acceptance criteria**
- Given a level, when `Escape`, `KeyP`, gamepad Start or Select, or the pause button is pressed, then the game is paused and the pause menu shows (unit test on the controls, e2e by key, gamepad and tap).

*Sources: P12-R01, D-095, D-096.*

### UI-PAUSE-02 — The pause button · MUST

The pause button `❚❚` is in the top right corner of the playfield, `pause_button_size` square: a
glass panel with a green border and chamfered corners. It is at least 44 × 44 CSS px on every
screen, and never covers the score, the health, the weapon or the boss gauge. Pressing it does not
start a drag of the ship. It shows while the level is played, not on the pause menu or the end
panels.

**Acceptance criteria**
- Given the pause button on a 390 × 844 and an 800 × 600 screen, then it is fully visible, at least 44 × 44 CSS px, and overlaps no other HUD element (e2e).

*Sources: P12-R01, D-096, D-155.*

### UI-PAUSE-03 — Nothing moves while paused · MUST

While paused, nothing in the level advances: no scrolling, no spawns, no movement, no shots, no
timers (invincibility, bomb, laser warnings, checkpoint, level end). The level's own clock gets no
time at all. The last frame stays visible under the pause menu, dimmed by `pause_dim`. Resuming
goes on from exactly the same state: no time is skipped and the fixed-step clock does not catch up
the paused time.

**Acceptance criteria**
- Given a paused level for 10 s, when it is resumed, then the level's scroll position, the enemies, shots and timers are exactly as when it was paused (unit test over the simulation state; e2e with `P`).

*Sources: P12-R01, D-096.*

### UI-PAUSE-04 — No press carries over a pause · SHOULD

Pausing and resuming let go of every held game control, so a key or button pressed on the pause
menu (a bomb key, say) does nothing in the level after it resumes. The level's debug keys do
nothing while it is paused.

**Acceptance criteria**
- Given the fire key held when the level is paused, when it is resumed with the key up, then the ship does not fire.

*Sources: D-096.*

### UI-PAUSE-05 — Back does nothing in a level · MUST

In a level, `Backspace` and gamepad B do nothing: they neither leave the level nor pause it. Leaving
goes through the pause menu (UI-PAUSE-10).

**Acceptance criteria**
- Given the game screen, when `Backspace` or gamepad B is pressed, then the level does not leave and does not pause.

*Sources: P12-R01, P06-R02, D-095, D-096.*

### UI-PAUSE-06 — The end panels cannot be paused · MUST

The "Level complete" and "Game over" panels cannot be paused: the pause controls do nothing there.

**Acceptance criteria**
- Given the "Level complete" panel, when `Escape` or `P` is pressed, then the panel stays and no pause menu shows.

*Sources: P12-R01.*

### UI-PAUSE-07 — The pause menu · MUST

The pause menu is a panel in the middle of the dimmed playfield, in the menu look: the heading
"Paused", then three entries, navigated with the menu actions ([menu-input.md](menu-input.md)):
1. **Resume**, selected when the menu opens;
2. **Settings**;
3. **Main menu**.

Under them, the hint "Esc / P to resume". Up and Down move between the entries without wrapping;
Left and Right do nothing. Each entry is at least 56 px tall; the selected one has a `▶` before it.
The whole menu can be used with the keyboard only, the gamepad only and taps only.

**Acceptance criteria**
- Given the pause menu opens, then Resume is selected.
- e2e: the pause menu can be used with the keyboard only, the gamepad only and taps only.

*Sources: P12-R02.*

### UI-PAUSE-08 — Resuming · MUST

Confirming Resume closes the menu and resumes the level. On the pause menu, `back` (`Escape`,
`Backspace`, gamepad B) and the pause controls (`KeyP`, gamepad Start and Select) resume it too, so
pressing `Escape` twice pauses and resumes.

**Acceptance criteria**
- Given the pause menu, when Resume is confirmed, then the level resumes (unit test and e2e).
- Given the pause menu, when `Escape` or gamepad B is pressed, then the level resumes.

*Sources: P12-R02.*

### UI-PAUSE-09 — Settings from the pause menu · MUST

Settings opens the settings screen over the still paused level ([settings.md](settings.md)). Back
from it returns to the pause menu, with the level still paused.

**Acceptance criteria**
- Given the pause menu, when Settings is opened and closed, then the pause menu shows again with the level still paused (e2e).

*Sources: P12-R02, P12-R04.*

### UI-PAUSE-10 — Leaving the level · MUST

Main menu asks `Leave the level?`, with **No** (selected first) and **Yes** side by side, in place
of the entries. Any direction picks: Left or Up for No, Right or Down for Yes; a tap selects a
choice and a second tap confirms it. Yes ends the attempt: its score is checked against the high
score and saved if higher ([gameplay/scoring.md](../gameplay/scoring.md)), and the title screen
shows. No, or `back`, returns to the pause menu, with the level still paused.

**Acceptance criteria**
- Given the pause menu, when Main menu then Yes is confirmed with a score of 3 000 and a saved high score of 1 000, then the title screen shows and the high score is 3 000 (e2e).
- Given the `Leave the level?` question, when No or `back` is chosen, then the pause menu shows again and the level is still paused.

*Sources: P12-R02, P11-R03, D-095.*

### UI-PAUSE-11 — Automatic pause · MUST

The level pauses by itself, with the pause menu showing, when:
- the page becomes hidden (`visibilitychange` to `hidden`: tab switched, window minimised, phone locked) (ENG-110);
- the window loses its focus (`blur` on the window: another window or app clicked, the browser's own UI opened) while the page stays visible; the audio plays on (D-242);
- the gamepad last used to play is disconnected.

It never resumes by itself: the player resumes from the pause menu. In the menus, a hidden page
changes no screen (only the audio goes quiet, [audio/engine.md](../audio/engine.md)).

**Acceptance criteria**
- Given a level, when the page becomes hidden, then the level is paused and, when the page is visible again, the pause menu shows (e2e with a faked `visibilitychange`).
- Given a level, when the window loses its focus, then the level is paused with the pause menu showing (e2e with a faked `blur`; unit test: the audio is not silenced).
- Given a level played with a gamepad, when the gamepad is disconnected, then the level is paused (unit test with a fake gamepad); a gamepad never used to play does not pause it.
- Given a paused level, when the page is hidden and shown again, then it is still paused.

*Sources: P12-R03, ENG-110, D-095, D-096, D-242.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| Pause keys / buttons | `Escape`, `KeyP`; gamepad 9, 8; the `❚❚` button | `src/config/menu_input.py` `MENU_INPUT_CONFIG` |
| `pause_dim` | 50 % black over the playfield | `index.html` `.pause-dim` |
| `pause_button_size` | 56 × 56 px, 14 px from the top, 18 px from the right | `index.html` `.game-pause` |
| Pause panel | at least 280 px wide, entries 56 px tall, 24 px text | `index.html` `.pause-panel`, `.pause-entry` |
| Texts | "Paused", "Resume", "Settings", "Main menu", "Esc / P to resume", "Leave the level?", "No", "Yes" | `src/game/config/menu_texts.py` `MENU_TEXTS` |

## Notes

- Before the pause menu (phase 12), `Escape`, `Backspace` and gamepad B left the level straight
  away (P01-R09, P06-R02, D-041). They no longer do in a level: a single key that quits a level is
  too easy to hit by accident (D-095).
- The pause button sat under the weapon readout at the top right while the HUD was at the top
  (D-096); since the HUD moved to the bottom bar it is in the corner itself (D-155).
