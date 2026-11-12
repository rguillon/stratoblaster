# Level complete, game over and Continue

> **Area:** UI · **Prefix:** `UI-OVER` · **Related:** [screen-flow.md](screen-flow.md), [level-select.md](level-select.md), [hud.md](hud.md), [../gameplay/level-flow.md](../gameplay/level-flow.md), [../gameplay/lives-and-damage.md](../gameplay/lives-and-damage.md), [../gameplay/scoring.md](../gameplay/scoring.md), [../audio/music.md](../audio/music.md)

When a level ends, a panel shows over the playfield: "Level complete" when it is won, "Game over"
when every life is lost. After the level's checkpoint (its mini boss destroyed), the "Game over"
panel offers to Continue from there. When a level is won or lost, what the checkpoint keeps and
what a Continue restores are in [gameplay/level-flow.md](../gameplay/level-flow.md); this file is
what the panels show and what their choices do.

## Requirements

### UI-OVER-01 — The "Level complete" panel · MUST

When a level is complete ([gameplay/level-flow.md](../gameplay/level-flow.md)), a panel shows in the
middle of the playfield, over the still running level, with:
- the heading "Level complete";
- the level's label (e.g. `1-2`);
- how many enemies were destroyed out of how many came: `Enemies destroyed: 41 / 57`;
- the attempt's score: `Score: 12500`;
- `New high score` when the score beat the saved high score (UI-OVER-02);
- the hint "Press Space / Enter or tap to go on".

The HUD stays visible; the touch fire button is gone.

**Acceptance criteria**
- Given the panel is shown after level `1-2`, then it shows `1-2`, the destroyed / spawned counts and the score.

*Sources: P06-R03, P11-R03.*

### UI-OVER-02 — "New high score" · MUST

When an attempt ends with a score above the saved high score, the high score is saved before the
panel shows, and the panel says `New high score`. On a "Game over" panel this happens before
Continue is offered, so a Continue never loses a high score.

**Acceptance criteria**
- Given a saved high score of 1 000 and a level completed with 2 500 points, then the cookie holds `2500` and the panel shows the score and `New high score` (unit test and e2e).
- Given a saved high score of 5 000 and a game over at 2 500 points, then the panel does not show `New high score`.
- Given a game over at 9 500 that beat the high score, then the cookie holds 9 500 before Continue is chosen.

*Sources: P11-R03, P11-R04.*

### UI-OVER-03 — Going on from "Level complete" · MUST

Confirm, or a tap anywhere on the panel, goes to the level select screen, with the next level
highlighted ([level-select.md](level-select.md)).

**Acceptance criteria**
- Given the panel after `1-2`, when Confirm is pressed, then the screen is `level-select` with `1-3` highlighted.

*Sources: P06-R03, P08-R01.*

### UI-OVER-04 — The panels wait a moment, and only take Confirm · MUST

For `panel_input_delay` after a panel shows, input is ignored, so a held fire key does not skip it.
On the panels, Back does nothing and the pause controls do nothing (the level is already over).

**Acceptance criteria**
- Given a panel just shown, when Confirm comes within `panel_input_delay`, then it is ignored.
- Given a panel, when Back or `P` is pressed, then the panel stays.

*Sources: P06-R03, P12-R01, D-096.*

### UI-OVER-05 — The "Game over" panel · MUST

When the last life is lost, the "Game over" panel shows `game_over_delay` later. It is the "Level
complete" panel with the heading "Game over" in red and a red border. Confirm (or a tap) goes to the
level select screen with the level just played highlighted, not the next one.

**Acceptance criteria**
- Given the last life is lost, then the "Game over" panel shows 2 s later, with a red heading.
- Given the "Game over" panel without a checkpoint, when Confirm is pressed, then the screen is `level-select` with the level played highlighted.

*Sources: D-050, GD game flow.*

### UI-OVER-06 — The Continue choice · MUST

If the game is over after the level's checkpoint, the "Game over" panel offers two choices in place
of its hint: **Continue** (selected first) and **Level select**, side by side. Any direction picks:
Left or Up for Continue, Right or Down for Level select. Confirm takes the selected choice; a tap
selects a choice and a second tap takes it. The selected choice is the light cyan block of the
menus.

**Acceptance criteria**
- Given the mini boss of 1-2 was destroyed, when the game is over, then the panel offers Continue (selected) and Level select.
- Given the choices, when Right is pressed, then Level select is selected; when Up is pressed, then Continue is selected.

*Sources: P07-R08, D-056.*

### UI-OVER-07 — What the choices do · MUST

**Continue** starts the level again, on the game screen, from its checkpoint, as a new attempt: the
level is rebuilt (behind the loading screen if it takes a moment, [boot-and-loading.md](boot-and-loading.md)),
and what it restores (distance, weapons, score, lives and bombs) is in
[gameplay/level-flow.md](../gameplay/level-flow.md). **Level select** goes to the level select
screen with the level played highlighted, and the checkpoint is forgotten.

**Acceptance criteria**
- Given Continue is confirmed, then the game screen starts the level again just after its mini boss (unit test on the attempt and its checkpoint).
- Given Level select is confirmed, then the screen is `level-select`; a new start of the level from there has no checkpoint.

*Sources: P07-R08, D-056, P11-R04.*

### UI-OVER-08 — No checkpoint, no choice · MUST

If the game is over before the checkpoint, the "Game over" panel is the plain one of UI-OVER-05.

**Acceptance criteria**
- Given the game is over before the mini boss was destroyed, then the panel has no Continue choice.

*Sources: P07-R08.*

### UI-OVER-09 — The panels' look · SHOULD

The panels are glass panels with 16 px corners and a hairline border (red for "Game over"): the
heading in 32 px primary text at weight 600 over the horizon line (red for "Game over"), the level's
label in 40 px monospace, the enemy count in 20 px secondary text, the score in monospace, and
`New high score` in green.

**Acceptance criteria**
- Manual check: the panels read well over every level's ground.

*Sources: P06-R03, D-050, D-198.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `panel_input_delay` | 1 s | `src/config/game_play.py` `GAME_PLAY_CONFIG.complete_delay` |
| `game_over_delay` | 2 s | `src/config/game_play.py` `GAME_PLAY_CONFIG.damage.game_over_delay` |
| Texts | "Level complete", "Game over", "Enemies destroyed: N / M", "Score: N", "New high score", "Press Space / Enter or tap to go on", "Continue", "Level select" | `src/game/config/menu_texts.py` `MENU_TEXTS` |

## Notes

- There is no "Retry" or "Next level" button: the panels lead to the level select screen, where
  the next (or the same) level is already highlighted.
