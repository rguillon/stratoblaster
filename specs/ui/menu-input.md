# Menu input

> **Area:** UI · **Prefix:** `UI-INPUT` · **Related:** [screen-flow.md](screen-flow.md), [pause-menu.md](pause-menu.md), [settings.md](settings.md), [look-and-layout.md](look-and-layout.md), [../gameplay/controls.md](../gameplay/controls.md), [../01-engineering.md](../01-engineering.md)

Every menu (title, ship select, level select, settings, pause menu, end-of-level panels) can be used
with the keyboard, a gamepad, or a mouse or touch screen. The devices are turned into the same few
abstract menu actions, and the screens react only to those. This file covers the menu actions and
their bindings. Flying, shooting and bombing in a level are game controls, in
[gameplay/controls.md](../gameplay/controls.md).

## Requirements

### UI-INPUT-01 — One set of menu actions for every device · MUST

The input layer (`input/`) turns the keyboard, the gamepads and taps into the same abstract menu
commands:
- the actions `up`, `down`, `left`, `right`, `confirm`, `back`, `cancel`, `pause` and `resume`;
- `select(entry)`: a tap or click on an entry that is not the selected one;
- `set(slider, value)`: a tap or drag on a settings slider ([settings.md](settings.md)).

Menu screens react only to these commands, never to raw keys, buttons or pointer events.

**Acceptance criteria**
- Unit tests show that Enter, Space, gamepad A and a tap on the selected entry all produce `confirm`.
- Given a key that no binding names, then no menu command is produced.

*Sources: P01-R12, D-008, D-096.*

### UI-INPUT-02 — What each action means · MUST

| Action | On a menu screen | In a level | On the pause menu |
|--------|------------------|------------|-------------------|
| `up` / `down` / `left` / `right` | Move the selection | Nothing (the ship's moves are game controls) | Move the selection |
| `confirm` | Take the selected entry | Nothing | Take the selected entry |
| `back` | Back ([screen-flow.md](screen-flow.md)) | Nothing | Resume (or close the `Leave the level?` question) |
| `cancel` | Back | Pause | Resume (or close the question) |
| `pause` | Nothing | Pause | Resume (or close the question) |
| `resume` | Nothing | Nothing | Resume (used by the test API) |

On the "Level complete" and "Game over" panels, only the moves and `confirm` do something
([continue-and-game-over.md](continue-and-game-over.md)).

**Acceptance criteria**
- Given a level, when `cancel` or `pause` comes, then the level is paused; when `back` comes, then nothing happens.
- Given the pause menu, when `back`, `cancel` or `pause` comes, then the level resumes.
- Given the ship select screen, when `cancel` comes, then the screen is `title`.

*Sources: D-096, P12-R01, P12-R02.*

### UI-INPUT-03 — Bindings in config · MUST

The key, button and stick bindings, the stick dead zone and the repeat timings are config
(`src/config/menu_input.py`), not code, so they can be remapped later (ENG-112).

**Acceptance criteria**
- Changing a binding in `MENU_INPUT_CONFIG` changes the key without touching the input code (unit test with other bindings).

*Sources: P01-R12.*

### UI-INPUT-04 — Keyboard by key position · MUST

Keys are matched by their physical position (`KeyboardEvent.code`), so the same places work on
QWERTY and AZERTY keyboards:

| Action | Keys |
|--------|------|
| `up` / `down` / `left` / `right` | Arrow keys; `KeyW` / `KeyS` / `KeyA` / `KeyD` (Z / S / Q / D on AZERTY) |
| `confirm` | `Enter`, `NumpadEnter`, `Space` |
| `back` | `Backspace` |
| `cancel` | `Escape` |
| `pause` | `KeyP` |

**Acceptance criteria**
- On an AZERTY layout, the keys in the WASD positions (Z, Q, S, D) move the selection.
- `Escape` gives `cancel` and `KeyP` gives `pause` (unit test).

*Sources: P01-R09, P12-R01, D-096.*

### UI-INPUT-05 — Bound keys belong to the game · SHOULD

A bound key's browser default is cancelled (no page scroll on Space or the arrows, no history jump
on Backspace). The browser's own key auto-repeat is ignored: holding a key repeats only as
UI-INPUT-06 says. When the window loses the focus, every held key is let go, so a key-up missed
outside the window does not keep a direction repeating.

**Acceptance criteria**
- Given a held arrow key, when the window loses the focus, then the selection stops moving.

*Sources: P01-R09, D-008.*

### UI-INPUT-06 — Holding a direction repeats it · MUST

Holding a direction (a key, the D-pad or the stick) moves the selection once at once, then again
after `menu_repeat_delay`, then every `menu_repeat_interval` while it is held. A direction keeps
repeating while any key bound to it is still down. `confirm`, `back`, `cancel` and `pause` never
repeat: each press gives one action.

**Acceptance criteria**
- Holding Right in `ship-select` moves the selection once, then repeats after the repeat delay.
- Holding Enter on the title gives one `confirm`.

*Sources: P01-R09, P01-R10.*

### UI-INPUT-07 — Gamepad buttons · MUST

Menus can be used with a standard gamepad (Gamepad API, standard mapping), polled once per frame.
All connected gamepads are merged. A button acts once, when it goes down.

| Action | Button (standard mapping) |
|--------|---------------------------|
| `confirm` | A, bottom (0) |
| `back` | B, right (1) |
| `pause` | Select / View (8), Start (9) |
| `up` / `down` / `left` / `right` | D-pad (12 / 13 / 14 / 15), or the left stick (UI-INPUT-08) |

**Acceptance criteria**
- With a gamepad connected, the whole flow Title → Ship select → Level select → Game → pause → Main menu → Title can be done with the gamepad only (e2e with a fake `navigator.getGamepads()`).
- Given a level, when Start is pressed, then the level is paused (unit test).

*Sources: P01-R10, P12-R01.*

### UI-INPUT-08 — Gamepad stick with a dead zone · MUST

The left stick (axes 0 and 1) moves the selection in the direction of its larger axis. A tilt
shorter than `gamepad_dead_zone` is ignored.

**Acceptance criteria**
- A stick tilt inside the dead zone does not move the selection.
- A tilt of (0.8, 0.3) gives `right`; a tilt of (0.2, −0.9) gives `up`.

*Sources: P01-R10.*

### UI-INPUT-09 — Tap or click an entry · MUST

Every menu entry can be tapped or clicked. Tapping an entry that is not selected selects it;
tapping the selected entry confirms it. The same holds for the choices of the pause menu's question
and of the "Game over" panel; the "Level complete" panel without choices is one entry that a tap
confirms.

**Acceptance criteria**
- Given the ship select screen with Balanced highlighted, when the Heavy card is tapped, then Heavy is highlighted; when it is tapped again, then the screen is `level-select`.

*Sources: P01-R11, D-008.*

### UI-INPUT-10 — An on-screen Back button · MUST

Every menu screen but the title (ship select, level select, settings, the dev menu) shows a
**◀ Back** button at its top left. Tapping it is `back`. The pause menu has none: its Resume entry
plays that part.

**Acceptance criteria**
- Given each of the ship select, level select and settings screens, then a Back button is visible and tapping it goes back.

*Sources: P01-R11.*

### UI-INPUT-11 — Large touch targets · MUST

Every tappable target (menu entries, level cells, sliders, the Back button, the panels'
choices) is at least 44 × 44 CSS px, also on a 390 px wide phone, where the logical screen is
scaled down to about 0.81.

**Acceptance criteria**
- At 390 × 844, every `.menu-entry` and `.menu-back` of the title, ship select and level select screens is at least 44 × 44 CSS px (e2e).

*Sources: P01-R11.*

### UI-INPUT-12 — Every device on its own · MUST

The whole menu flow, the pause menu and the settings screen can each be used with the keyboard only,
the gamepad only, the mouse only, and taps only.

**Acceptance criteria**
- e2e: Title → Ship select → Level select → Game → pause → Main menu → Yes → Title with the keyboard only, the gamepad only, the mouse only, and taps only (touch emulation).

*Sources: P01-R09, P01-R10, P01-R11, P12-R02, P12-R04.*

### UI-INPUT-13 — No second confirm from the browser · SHOULD

Menu entries are not native buttons that can take the focus, so the browser never turns a Space or
Enter press into a second click on a focused entry: the keyboard reaches the menus only through the
menu input.

**Acceptance criteria**
- Given the mouse clicked Start, when Space is pressed on the ship select screen, then exactly one `confirm` happens.

*Sources: D-008.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `menu_repeat_delay` | 350 ms | `src/config/menu_input.py` `MENU_INPUT_CONFIG.repeat_delay_seconds` |
| `menu_repeat_interval` | 120 ms | `MENU_INPUT_CONFIG.repeat_interval_seconds` |
| `gamepad_dead_zone` | 0.35 | `MENU_INPUT_CONFIG.gamepad_dead_zone` (stick length) |
| Keyboard bindings | see UI-INPUT-04 | `MENU_INPUT_CONFIG.keyboard` |
| Gamepad bindings | see UI-INPUT-07 | `MENU_INPUT_CONFIG.gamepad_buttons`, `gamepad_stick` (axes 0, 1) |
| Minimum touch target | 44 × 44 CSS px | `index.html` (`.menu-entry` min 44 px, `.menu-back` 96 × 56 logical px) |

## Notes

- `Escape` was plain Back in phase 1. Since the pause menu (D-096) it is its own action, `cancel`:
  Back in the menus, pause in a level, so that Escape follows the "Pause: Esc / P" row of the
  controls table while `P` and gamepad Start never go back on a menu screen.
