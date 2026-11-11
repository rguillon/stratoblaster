# Scoring

> **Area:** Gameplay · **Prefix:** `GAME-SCORE` · **Related:** [level-flow.md](level-flow.md), [lives-and-damage.md](lives-and-damage.md), [bonuses.md](bonuses.md), [../ui/hud.md](../ui/hud.md), [../ui/title-screen.md](../ui/title-screen.md), [../ui/continue-and-game-over.md](../ui/continue-and-game-over.md), [../enemies/common.md](../enemies/common.md), [../bosses/common.md](../bosses/common.md)

Each level attempt has a score: the player scores points for every enemy and boss part destroyed.
The best score ever reached is the high score, saved in a cookie and shown on the title screen.
This file gives what scores and how the high score is kept. Each enemy kind's points are in its
own file ([enemies/](../enemies/common.md)), each boss's in its own ([bosses/](../bosses/common.md));
the score lines of the HUD are in [ui/hud.md](../ui/hud.md).

## Requirements

### GAME-SCORE-01 — A score per level attempt · MUST

Each level attempt has its own score, which starts at 0 (or at the checkpoint's score after a
Continue, GAME-SCORE-06). The score is not carried from one level to the next: levels are played
one by one from the level select.

**Acceptance criteria**
- Given a level started from the level select, then its score is 0 (unit test).

*Sources: P11-R01, D-091.*

### GAME-SCORE-02 — Points for destroyed enemies · MUST

Every enemy destroyed adds the points of its kind, whatever destroyed it: a shot, a bomb, or the
ship ramming it. Enemies that leave the screen or are removed for age score nothing. Enemies that
other enemies spawn (Splitter pods, Carrier launches, …) score their own kind's points.

**Acceptance criteria**
- Given a Hornet destroyed by a shot, then the score rises by the Hornet's points (unit test).
- Given an enemy destroyed by ramming or by a bomb, then it scores its points too (unit test).
- Given an enemy that leaves the screen alive, then the score does not change (unit test).

*Sources: GD-50, P11-R01.*

### GAME-SCORE-03 — Points by difficulty · MUST

An enemy kind's points follow its difficulty: a kind with at least twice the health of another
never scores less than it.

**Acceptance criteria**
- Given every enemy kind of the game, then no kind scores less than a kind with half its health or
  less (unit test over the roster).

*Sources: GD-50, P11-R01.*

### GAME-SCORE-04 — Points for bosses · MUST

A destroyed boss part scores `boss_part_share` (10 %) of its boss's points, rounded to the nearest
10; a destroyed boss core scores the boss's points. Parts that go down in the boss's own death
blasts score nothing more.

**Acceptance criteria**
- Given a boss of 10 000 points, when one of its parts is destroyed, then the score rises by 1 000;
  when its core is destroyed, by 10 000 (unit test).
- Given a boss of 8 050 points, then a part scores 810 (unit test).

*Sources: P11-R01, D-091, D-092.*

### GAME-SCORE-05 — The high score · MUST

The high score is one number for the whole game: the best score of any level attempt. It is kept
in a cookie (`<game id>_high_score`, a plain whole number). When a level attempt ends — the level
is completed, the game is over, or the player leaves the level (from the pause menu, or by
continuing from a checkpoint) — its score is saved as the new high score if it is higher. The
title screen shows the high score ([ui/title-screen.md](../ui/title-screen.md)), also after a
reload; the end-of-level panels say when it was beaten
([ui/continue-and-game-over.md](../ui/continue-and-game-over.md)). A cookie that is not a plain
whole number reads as 0, and the next higher score overwrites it.

**Acceptance criteria**
- Given a saved high score of 1 000 and a level completed with 2 500 points, then the cookie holds
  `2500` and the panel shows `New high score` (unit test, e2e).
- Given a saved high score of 5 000 and a game over at 2 500 points, then the cookie still holds
  `5000`.
- Given the player leaves a level from the pause menu at 3 000 points over a saved 1 000, then the
  title shows 3 000, also after a reload (e2e).
- Given an unreadable cookie, then the high score reads as 0 (unit test).

*Sources: GD-51, P11-R03, D-091, D-092.*

### GAME-SCORE-06 — Score at the checkpoint · MUST

The checkpoint ([level-flow.md](level-flow.md)) keeps the score at the moment the mini boss is
destroyed, and a Continue starts again from that score, not 0. The game over's score is checked
against the high score before Continue is offered, so a Continue never loses a high score.

**Acceptance criteria**
- Given the mini boss destroyed at 8 000 points and the game over at 9 500, when Continue is
  chosen, then the level starts again from the checkpoint with a score of 8 000 (unit test).
- Given that game over beat the high score, then the cookie holds 9 500 before Continue is chosen
  (e2e).

*Sources: P11-R04, D-092.*

### GAME-SCORE-07 — Score in the HUD · MUST

The HUD shows the score and the high score (the larger of the saved high score and the current
score), and both change on the step the points are scored ([ui/hud.md](../ui/hud.md)).

*Sources: P11-R02, D-155.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| enemy points | per kind, from Hornet 100 to Juggernaut 1 000 | each kind's `stats.points`, `src/game/config/enemies.py`, `enemies_veteran.py`, `enemies_elite.py` (the new kinds' values are set with their files) |
| boss points | per boss | each boss's data, `src/game/config/bosses/` |
| boss_part_share | 10 %, rounded to 10 | `src/game/config/scoring.py` `SCORING["bossPartShare"]`, `["roundTo"]` |
| high score key | `<game id>_high_score` (cookie) | `src/app/saved_choices.py` |

## Notes

- There are no multipliers, combos, chains, level-end bonuses, per-level or per-ship high scores,
  or high score table (out of scope since phase 11).
