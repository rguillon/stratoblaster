# Level select

> **Area:** UI · **Prefix:** `UI-LEVEL` · **Related:** [screen-flow.md](screen-flow.md), [menu-input.md](menu-input.md), [title-screen.md](title-screen.md), [continue-and-game-over.md](continue-and-game-over.md), [../gameplay/level-flow.md](../gameplay/level-flow.md), [../performance.md](../performance.md), [../worlds/world-1/world.md](../worlds/world-1/world.md)

The screen where the player picks a level, straight after the title's Start: a grid of 4 worlds × 5 levels, one row per world. Every
level of the game can be played at any time, in any order. The worlds and their levels are in
[worlds/](../worlds/world-1/world.md).

## Requirements

### UI-LEVEL-01 — A grid of 4 worlds × 5 levels · MUST

The levels are shown as a grid with one row per world and one column per level: 4 rows of 5, the
20 cells labelled `1-1` … `4-5`, World 1 at the top. World 4 is the last row.

**Acceptance criteria**
- The grid shows 20 entries labelled `1-1` … `4-5`, in 4 rows of 5.
- Given `level-select`, then the World 1 row shows exactly `1-1` … `1-5`, the World 2 row `2-1` … `2-5`, the World 3 row `3-1` … `3-5`, and the World 4 row `4-1` … `4-5`.

*Sources: P01-R07, P06-R01, P08-R01, P09-R01, P10-R01, D-089.*

### UI-LEVEL-02 — The levels come from the game's data · MUST

How many worlds and levels per world there are, and which levels exist, come from the game's data
(`src/game/config/levels.py` and the game's list of levels), not from engine code. The engine only
provides a generic grid of levels (`core/content/level_catalog.py`).

**Acceptance criteria**
- Unit test: a grid built from other numbers of worlds and levels has those rows and columns.

*Sources: P01-R07, P06-R01, D-008.*

### UI-LEVEL-03 — No level is locked by progress · MUST

Every level that exists is unlocked from the first start: the player can pick any level at any
time, without finishing the levels before it (reviewer's choice). With the 20 levels built, no
level of this game is locked.

**Acceptance criteria**
- Given a fresh start (no cookie), then `1-5`, `2-5`, `3-5` and `4-5` can be confirmed straight away.
- Given `level-select`, then no cell is locked.

*Sources: P06-R01, P08-R01, P09-R01, P10-R01.*

### UI-LEVEL-04 — Locked levels, for games that have them · MUST

The engine still handles a level the data marks as locked: its cell is greyed out, hazard-striped,
with a padlock. It can be highlighted (its frame is then red), but Confirm does not start it: the
cell shakes (`locked_shake`) and the status line under the grid says "Locked". This game's data has
no locked level, so this is checked with sample grids in unit tests only.

**Acceptance criteria**
- Given a sample grid with a locked level, when it is highlighted and Confirm is pressed, then the screen stays `level-select` and the "locked" feedback is given (unit test).

*Sources: P01-R07, D-013, D-089.*

### UI-LEVEL-05 — Moving in the grid · MUST

The arrows move the highlight across the grid, one cell at a time; it stops at the edges (no
wrap). Holding a direction repeats ([menu-input.md](menu-input.md)). Tapping another cell
highlights it; tapping the highlighted cell confirms it.

**Acceptance criteria**
- Given `1-5` highlighted, when Right is pressed, then `1-5` stays highlighted; when Down is pressed, then `2-5` is highlighted.

*Sources: P01-R07, P01-R09, P01-R11.*

### UI-LEVEL-06 — The first level is highlighted on arrival · MUST

Coming from the title screen, the first unlocked level (`1-1`) is highlighted.

**Acceptance criteria**
- Given `level-select` is opened from the title screen, then `1-1` is highlighted.

*Sources: P01-R07, D-326.*

### UI-LEVEL-07 — After a level, the next one is highlighted · MUST

Coming back from a level's end panel ([continue-and-game-over.md](continue-and-game-over.md)):
- after "Level complete", the next level is highlighted, across worlds: after `1-5` it is `2-1`,
  after `2-5` `3-1`, after `3-5` `4-1`; after the last level, `4-5`, it stays `4-5`;
- after "Game over" (or the "Level select" choice of the Continue panel), the level just played is
  highlighted.

**Acceptance criteria**
- Given the "Level complete" panel after `1-2`, when Confirm is pressed, then `level-select` shows with `1-3` highlighted.
- Given `1-5`, `2-5` or `3-5` is completed, then `level-select` shows with `2-1`, `3-1` or `4-1` highlighted.
- Given `4-5` is completed, then `level-select` shows with `4-5` highlighted.
- Given a game over in `1-3`, then `level-select` shows with `1-3` highlighted.

*Sources: P06-R03, P08-R01, P09-R01, P10-R01, D-050, D-089.*

### UI-LEVEL-08 — Confirm starts the level · MUST

Confirming an unlocked level opens the game screen, which starts that level with the game's one
ship, the Balanced one ([gameplay/player-ship.md](../gameplay/player-ship.md)). Back opens the
title screen.

**Acceptance criteria**
- Given `1-1` is confirmed, then the game screen plays `1-1` with the Balanced ship.
- Given any level of any world is confirmed, then the game screen starts that level.
- Given `level-select`, when Back is pressed, then the screen is `title`.

*Sources: P01-R07, P06-R01, P08-R01, P09-R01, P10-R01, D-326.*

### UI-LEVEL-09 — The screen's look · SHOULD

The heading "Choose a level" is over the grid; the hint "Arrows to pick · Enter or tap to go"
and the status line are under it; the grid, the hint and the status line are centred together in
the height left under the heading; the Back button is at the top left. The cells are 68 × 68 px
glass squares with 8 px corners, 12 px apart, with a hairline border and the label in 24 px
monospace at weight 600. The
highlighted cell is the light cyan block of the menus with a white border and a dashed white
outline ([look-and-layout.md](look-and-layout.md)).

**Acceptance criteria**
- Manual check at 390 × 844 and 800 × 600: the whole grid, heading and hint are visible.

*Sources: P01-R07, P01-R13.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| Worlds × levels per world | 4 × 5 | `src/game/config/levels.py` `LEVELS_CONFIG` (`worlds`, `levelsPerWorld`) |
| Unlocked levels | every level of `GAME_LEVELS` | `src/game/sim/levels.py` `LEVELS` |
| Level cell | 68 × 68 px, 12 px gap | `index.html` `.level-cell`, `.level-grid` |
| `locked_shake` | 0.3 s, ±6 px | `index.html` `.shake`, `@keyframes menu-shake` |
| Locked text | "Locked" | `src/game/config/menu_texts.py` `MENU_TEXTS["locked"]` |

## Notes

- The grid was 5 × 5 until World 5 was dropped (reviewer, 2026-10-26, D-089).
- Once the highlight has rested on a level for a moment, that level is prepared and built ahead,
  so confirming it starts it at once ([performance.md](../performance.md)).
