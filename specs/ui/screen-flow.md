# Screen flow

> **Area:** UI · **Prefix:** `UI-FLOW` · **Related:** [menu-input.md](menu-input.md), [title-screen.md](title-screen.md), [ship-select.md](ship-select.md), [level-select.md](level-select.md), [pause-menu.md](pause-menu.md), [settings.md](settings.md), [continue-and-game-over.md](continue-and-game-over.md), [../gameplay/level-flow.md](../gameplay/level-flow.md), [../dev/dev-menu.md](../dev/dev-menu.md)

The game is a small set of screens joined by a state machine: Loading → Title → Ship select →
Level select → Game, with Back on each menu screen, a pause menu over the level, a settings screen
reached from the title and from the pause menu, and the end-of-level panels that lead back to the
level select. This file fixes which screens exist and how the player moves between them. What each
screen shows is in its own file. The dev menu's screens are described in
[dev/dev-menu.md](../dev/dev-menu.md).

## Requirements

### UI-FLOW-01 — The screens · MUST

The app has these screens:

| Screen | What it is |
|--------|------------|
| `loading` | The loading screen at start-up ([boot-and-loading.md](boot-and-loading.md)) |
| `title` | The title screen ([title-screen.md](title-screen.md)) |
| `ship-select` | The ship select screen ([ship-select.md](ship-select.md)) |
| `level-select` | The level select screen ([level-select.md](level-select.md)) |
| `game` | A level being played, with its "Level complete" / "Game over" panel at the end ([continue-and-game-over.md](continue-and-game-over.md)) |
| `pause` | The pause menu over the paused level ([pause-menu.md](pause-menu.md)) |
| `settings` | The settings screen ([settings.md](settings.md)) |
| `dev`, `dev-viewer` | The dev menu and its viewers, only with `?dev` ([dev/dev-menu.md](../dev/dev-menu.md)) |

The app starts on `loading`.

**Acceptance criteria**
- Given a page load, then the first screen is `loading`, and it ignores every menu command.

*Sources: P01-R01, GD game flow, D-096.*

### UI-FLOW-02 — Allowed screen changes · MUST

The flow allows exactly these changes:

```
loading ──done──▶ title ──Start──▶ ship-select ──confirm──▶ level-select ──confirm──▶ game
                  title ◀──back─── ship-select ◀───back──── level-select ◀──end panel── game
game ──pause──▶ pause ──resume──▶ game
game ──Continue (Game over panel)──▶ game (a new attempt)
title ──Settings──▶ settings ──back──▶ title
pause ──Settings──▶ settings ──back──▶ pause
pause ──Main menu, Yes──▶ title
```

| From | To | When |
|------|----|------|
| `loading` | `title` | Loading is done |
| `title` | `ship-select` | Start is confirmed |
| `title` | `settings` | Settings is confirmed |
| `title` | `dev` | Dev is confirmed (only with `?dev`) |
| `title` | `title` | Full screen is confirmed: the page's full screen is toggled ([title-screen.md](title-screen.md), UI-TITLE-11) |
| `ship-select` | `level-select` | A ship is confirmed |
| `ship-select` | `title` | Back |
| `level-select` | `game` | An unlocked level is confirmed |
| `level-select` | `ship-select` | Back |
| `game` | `pause` | A pause control, or an automatic pause ([pause-menu.md](pause-menu.md)) |
| `game` | `level-select` | Confirm on the "Level complete" or "Game over" panel, or its "Level select" choice |
| `game` | `game` | Continue on the "Game over" panel: the level starts again from its checkpoint, as a new attempt |
| `pause` | `game` | Resume: the same attempt goes on |
| `pause` | `settings` | Settings |
| `pause` | `title` | Main menu, then Yes |
| `settings` | `title` or `pause` | Back, to the screen it was opened from |
| `dev` | `title`, `dev-viewer` | See [dev/dev-menu.md](../dev/dev-menu.md) |
| `dev-viewer` | `dev` | See [dev/dev-menu.md](../dev/dev-menu.md) |

**Acceptance criteria**
- Given the `title` screen, when Start is confirmed, then the screen is `ship-select`.
- Given `ship-select`, when a ship is confirmed, then the screen is `level-select`.
- Given `level-select`, when `1-1` is confirmed, then the screen is `game`.
- Given `game`, when the level is paused, then the screen is `pause`; when it is resumed, then the screen is `game` with the same attempt.
- Given the pause menu, when Main menu then Yes is confirmed, then the screen is `title`.
- The ENG-54 smoke test goes loading → title → ship select → level select → game → pause → resume → leave → title.

*Sources: P01-R01, GD game flow, P12-R02, P12-R04, D-050, D-056, D-096.*

### UI-FLOW-03 — Other screen changes are refused · MUST

A screen change that is not in the table of UI-FLOW-02 is refused: the flow stays on its screen and
nothing changes. The one exception is the debug start of a level from the URL, which skips the
menus ([dev/debug-options.md](../dev/debug-options.md)).

**Acceptance criteria**
- Given the `title` screen, when the flow is asked to go to `game`, then it refuses and the screen stays `title`.
- Given the `game` screen, when the flow is asked to go to `title`, then it refuses.

*Sources: P01-R01.*

### UI-FLOW-04 — A pure state machine · MUST

The flow is a pure state machine: no Babylon, no DOM, no clock of its own (time comes in through its
`update`). It holds the screen, the selection on each screen, the chosen ship and level, the level's
result panel, the pause menu, the settings and the attempt count. The screen names and the table of
allowed changes live in `core/menu/`, so the render layer can read them; the flow itself, the pause
menu and the settings menu live in `app/`. The views and the 3D scenes only follow the flow's state.
The flow is fully unit tested.

**Acceptance criteria**
- The flow modules import neither Babylon nor the DOM (checked by the layering rules of [01-engineering.md](../01-engineering.md)).
- Unit tests drive the whole flow (every screen change of UI-FLOW-02) without a browser.

*Sources: P01-R01, D-008, D-096.*

### UI-FLOW-05 — Back on each menu screen · MUST

Back goes one step back:
- `ship-select` → `title`;
- `level-select` → `ship-select`, with the ship chosen before still highlighted;
- `settings` → the screen it was opened from (`title` or `pause`);
- on `title`, Back does nothing.

What Back does in a level, on the pause menu and on the end-of-level panels is in
[pause-menu.md](pause-menu.md) and [continue-and-game-over.md](continue-and-game-over.md).

**Acceptance criteria**
- Given `ship-select`, when Back is pressed, then the screen is `title`.
- Given `level-select`, when Back is pressed, then the screen is `ship-select` with the previously chosen ship still highlighted.
- Given `title`, when Back is pressed, then nothing changes.

*Sources: P01-R01, P12-R04.*

### UI-FLOW-06 — A level is left only through the pause menu or its end panel · MUST

There is no direct change from `game` to `title`. A level is left in one of two ways only: the pause
menu's Main menu entry, confirmed with Yes ([pause-menu.md](pause-menu.md)), or the end-of-level
panel ([continue-and-game-over.md](continue-and-game-over.md)). In a level, Back does nothing
(P01-R01's "Back from `game` goes to `title`" no longer holds).

**Acceptance criteria**
- Given a level being played, when Backspace or gamepad B is pressed, then the screen stays `game` and the level is not paused.

*Sources: P01-R01, P06-R02, P12-R01, D-041, D-095, D-096.*

### UI-FLOW-07 — The end of a level leads to the level select · MUST

From the "Level complete" and "Game over" panels, the flow goes to `level-select` (not to the title,
as the first game-flow sketch had it). On a "Game over" panel with a checkpoint, Continue keeps the
`game` screen and starts a new attempt from the checkpoint. Which level is highlighted on arrival is
in [level-select.md](level-select.md).

**Acceptance criteria**
- Given the "Game over" panel without a checkpoint, when Confirm is pressed, then the screen is `level-select`.
- Given the "Game over" panel with a checkpoint, when Continue is confirmed, then the screen stays `game` and the attempt count goes up by one.

*Sources: GD game flow, P06-R03, P07-R08, D-050, D-056.*

### UI-FLOW-08 — Short screen transitions · MAY

A new screen fades in over `menu_transition_duration` (at most 300 ms): from transparent and 8 px
below, to its place (no brightness flash, D-323). Input is ignored during a transition, so one press cannot
skip two screens. The timer is in the flow, so commands from the test API obey it too. Resuming a
level and a Continue also start a transition. The boot loading screen does not fade in.

**Acceptance criteria**
- Given a screen change, when a command comes within `menu_transition_duration`, then it is ignored.
- Given a held Confirm key on the title, then it starts the ship select screen and nothing more.

*Sources: P01-R15, D-008.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `menu_transition_duration` | 250 ms | `src/config/menu.py` `MENU_CONFIG.transition_seconds` (0.25); fade-in and input lock (UI-FLOW-08) |
| Screens and allowed changes | see UI-FLOW-02 | `src/core/menu/menu_screen.py` `MENU_TRANSITIONS` |

## Notes

- The first game-flow sketch (`02-game-design.md` §7) had "Game over → any key → Title". The
  reviewer chose a "Game over" panel leading back to the level select instead (D-050), and the
  pause menu, the settings screen and the Continue choice came later (D-056, D-096).
- The phase 1 placeholder game screen ("Gameplay coming soon") is gone: the `game` screen plays the
  chosen level since phase 6.
