# Phase 11 — Score, Lives and Bombs

> Fill the **Human** sections. Set **Status** to `Ready` when the agent may implement it.
> The agent fills the **Agent** sections and never edits the requirement sections.
> Drafted by the agent at the reviewer's request (2026-10-26) from GD-20, GD-32, GD-50, GD-51 and the roadmap proposal. Unspecified choices use agent defaults (D-091); the reviewer may change any of them before setting the status to `Ready`.

**Status:** Ready  <!-- Draft | Ready -->
**Depends on:** Phase 10

---

## 🧑 Goal
The player scores points for every enemy and boss part they destroy, sees the score and the high score in the HUD, and beats a high score that is saved and shown on the title screen. Bonuses can now also give an extra life or an extra bomb, and the player can fire a bomb that clears the enemy bullets and damages every enemy on screen. This completes the core loop of the vision.

## 🧑 Requirements

> ID format `P11-Rxx`. Every requirement is **MUST** (no SHOULD / MAY).
> Write each requirement so it is testable. Add acceptance criteria when "done" isn't obvious.
> Builds on the phase 6 lives and health model (GD-20..GD-22, D-050), the weapon bonuses (D-049, P07-R07), the checkpoint (P07-R08) and the high score cookie read by the title screen (P01-R04). Numbers are listed in **Tunable values**.
> Score, bombs and bonus kinds are game-agnostic engine features (`src/core/`); the points, drop chances, key bindings and texts are game data in `src/game/` (`01-engineering.md` §2.3).

### P11-R01 — Points for destroyed enemies and boss parts  · MUST

Each level attempt has a score that starts at 0. Every enemy the player destroys adds its points (the `points` of its kind, GD-50), whatever destroyed it: a shot, a bomb (P11-R05) or ramming it (D-050). Enemies that leave the screen or are removed for age score nothing. A destroyed boss part scores `boss_part_points_share` of its boss's points, and a destroyed boss core scores its boss's points. Splitter pods and other spawned parts score their own kind's points.

**Acceptance criteria**
- [ ] Given a Gnat is destroyed by a shot, then the score rises by the Gnat's points (unit test).
- [ ] Given an enemy is destroyed by ramming or by a bomb, then it scores its points too (unit test).
- [ ] Given an enemy leaves the screen alive, then the score does not change (unit test).
- [ ] Given a boss of 10 000 points, when one of its parts is destroyed, then the score rises by 1 000; when its core is destroyed, by 10 000 (unit test).
- [ ] Given every enemy kind of the game, then a kind with more health never scores less than a kind with half its health (GD-50, unit test over the roster).

### P11-R02 — Score and high score in the HUD  · MUST

The HUD shows the score, zero-padded to `score_digits` digits, at the top centre of the playfield, and the high score (`HI` and the larger of the saved high score and the current score) under it, smaller. Both change on the frame the points are scored. The texts are readable at 800×600 and 390×844 and do not cover the health bar, weapon or boss bar.

**Acceptance criteria**
- [ ] Given a level starts with a saved high score of 12 340, then the HUD shows `0000000` and `HI 0012340`.
- [ ] Given the score passes the saved high score, then the `HI` line shows the current score from then on.
- [ ] Given the HUD at 800×600 and 390×844, then the score lines are fully visible and overlap no other HUD element (e2e screenshot check).

### P11-R03 — High score saved in a cookie  · MUST

When a level attempt ends (level complete, game over, or leaving the level with Esc or the gamepad's B), if its score is higher than the saved high score, the score is saved as the new high score in the existing high score cookie (GD-51, P01-R04, `<gameId>_high_score`). The title screen shows it from then on, also after a reload. The "Level complete" and "Game over" panels show the score of the attempt, and `New high score!` when it beat the saved one.

**Acceptance criteria**
- [ ] Given a saved high score of 1 000 and a level completed with 2 500 points, then the cookie holds `2500` and the panel shows the score and `New high score!` (unit test and e2e).
- [ ] Given a saved high score of 5 000 and a game over at 2 500 points, then the cookie still holds `5000` and the panel does not show `New high score!`.
- [ ] Given the player leaves a level with Esc at 3 000 points and a saved high score of 1 000, then the title screen shows 3 000, also after a reload (e2e).
- [ ] Given an unreadable cookie, then the high score reads as 0 and a new score overwrites it (unit test).

### P11-R04 — Score at the checkpoint  · MUST

The checkpoint (P07-R08) also saves the score at the moment the mini boss is destroyed. **Continue** restarts from the checkpoint with that score, not 0, and with the bombs of P11-R05's starting count. The high score is checked (P11-R03) when the game is over, before Continue is offered, so a Continue never loses a high score.

**Acceptance criteria**
- [ ] Given the mini boss is destroyed at 8 000 points and the game is over at 9 500, when Continue is confirmed, then the level restarts from the checkpoint with a score of 8 000 (unit test).
- [ ] Given that game over beat the high score, then the cookie holds 9 500 before Continue is chosen.

### P11-R05 — Bombs  · MUST

The player has bombs (GD-32). Each level attempt starts with `bombs_start` bombs, and a Continue (P11-R04) too. When the player loses a life, the bomb count goes back up to `bombs_start` if it was lower. The bombs left show in the HUD next to the lives, as one icon per bomb.

Pressing the bomb control (P11-R06) fires one bomb, once per press (holding it does not fire more), if a bomb is left and no bomb is active. A bomb lasts `bomb_duration`:
- a shockwave ring grows from the ship to cover the whole playfield, with a short bright flash (kept below 3 flashes a second);
- every enemy whose centre is on screen when the bomb is fired takes `bomb_damage` once (enough to kill every World 1 kind up to the Rocketeer, GD-32);
- every boss part on screen takes `bomb_damage` once, and the boss core too unless a part shields it (P07);
- every enemy bullet and enemy missile on screen is removed, and every enemy laser on screen (and its warning line) is cut;
- the player cannot be hurt while the bomb is active.

Enemies destroyed by a bomb score and drop bonuses as usual. Firing with no bomb left does nothing.

**Acceptance criteria**
- [ ] Given a level starts, then the player has `bombs_start` bombs and the HUD shows that many bomb icons.
- [ ] Given 5 Gnats and 1 Bulwark on screen, when a bomb is fired, then every Gnat is destroyed, the Bulwark loses `bomb_damage` health, and the bomb count goes down by 1 (unit test).
- [ ] Given enemy bullets, missiles and a laser on screen, when a bomb is fired, then they are all gone (unit test).
- [ ] Given a bomb is active, when an enemy shot or an enemy reaches the ship, then the ship loses no health (unit test).
- [ ] Given the bomb key is held for 3 s, then only one bomb is fired (unit test).
- [ ] Given no bomb is left, when the bomb key is pressed, then nothing happens (unit test).
- [ ] Given 1 bomb left, when a life is lost, then the count goes back to `bombs_start`; given 4 bombs, it stays 4 (unit test).
- [ ] Given a boss whose core is shielded by a part, when a bomb is fired, then the part takes damage and the core does not (unit test).

### P11-R06 — Bomb controls  · MUST

The bomb is fired with:
- keyboard: `R` and `Left Shift`, by key position (`KeyR`, `ShiftLeft`, so the same keys on QWERTY and AZERTY). E keeps switching the weapon (D-043); the GD §2 binding of E to the bomb is superseded by D-043.
- gamepad (standard mapping): X / Square (button 2) and the left bumper (button 4);
- touch: an on-screen `BOMB` button, above the fire button, the same size, showing the bombs left; it is dimmed when no bomb is left.

The keys and buttons are in the game controls config next to the fire and switch keys (ENG-112).

**Acceptance criteria**
- [ ] Given a level, when `KeyR` or `ShiftLeft` is pressed, then a bomb is fired (unit test on `GameControls`, e2e by key).
- [ ] Given a gamepad, when button 2 or 4 is pressed, then a bomb is fired (unit test).
- [ ] Given a touch screen, when the `BOMB` button is tapped, then a bomb is fired; the fire button and the drag still work at the same time (e2e with touch).
- [ ] Given `E` is pressed, then the weapon switches and no bomb is fired.

### P11-R07 — Extra life and bomb bonuses  · MUST

Two new bonus kinds join the weapon bonus (D-049): a **life** bonus and a **bomb** bonus. They fall and are picked up like weapon bonuses. Each looks different from the others by shape, not only colour: the life bonus is a pink heart, the bomb bonus an orange sphere marked `B`, the weapon bonus unchanged.

- A destroyed enemy drops at most one bonus. Its kind is drawn in this order from the level's seed: life with `life_drop_chance`, else bomb with `bomb_drop_chance`, else the weapon bonus's chance as before (D-049).
- A mini boss's core always drops a life bonus. Boss parts and final boss cores keep dropping weapon bonuses only (P07-R07).
- Picking up a life bonus adds a life, up to `lives_max`; at the maximum it scores `life_bonus_points` instead. Picking up a bomb bonus adds a bomb, up to `bombs_max`; at the maximum it scores `bomb_bonus_points` instead.
- The lives in the HUD (`♥ N`) and the bomb icons change on pick-up.

**Acceptance criteria**
- [ ] Given a life bonus is picked up with 2 lives, then the player has 3 lives and the HUD shows `♥ 3` (unit test).
- [ ] Given a life bonus is picked up with `lives_max` lives, then the lives stay at `lives_max` and the score rises by `life_bonus_points` (unit test).
- [ ] Given a bomb bonus is picked up with `bombs_max` bombs, then the bombs stay at `bombs_max` and the score rises by `bomb_bonus_points` (unit test).
- [ ] Given a mini boss is destroyed, then a life bonus drops where its core was (unit test).
- [ ] Given the same level played twice with the same enemies destroyed in the same order, then the same bonuses of the same kinds drop (unit test).
- [ ] Given a play-through of World 1 shooting most enemies, then weapon bonuses per level stay within 10 % of the D-049 counts (measured, recorded in the report).

### P11-R08 — Test API  · MUST

In e2e builds, `getState()` also gives the score, the high score, the bombs left and the bonuses on screen with their kind; `sendAction` accepts `bomb`. None of it ships in the production bundle (as the rest of the test API).

**Acceptance criteria**
- [ ] Given an e2e build, when a level is played, then `getState()` returns `score`, `highScore`, `bombs` and each bonus's `kind`.
- [ ] Given `sendAction('bomb')`, then a bomb is fired as with the key.

## 🧑 Tunable values
| Name | Value | Notes |
|------|-------|-------|
| enemy points | per kind, as in the roster (Gnat 50 … Juggernaut 1 000) | P11-R01; already in the enemy data (GD-50) |
| boss_part_points_share | 10 % of the boss's points, rounded to 10 | P11-R01 |
| score_digits | 7 | P11-R02 |
| bombs_start | 3 | P11-R05; also after a Continue, and the floor after a lost life |
| bombs_max | 5 | P11-R07 |
| bomb_damage | 100 | P11-R05; kills every World 1 kind up to the Rocketeer (100 HP) |
| bomb_duration | 1 s | P11-R05; the player is invincible meanwhile |
| bomb keys / buttons | `KeyR`, `ShiftLeft`; gamepad 2, 4; touch `BOMB` | P11-R06 |
| lives_start | 3 | GD-20, unchanged (`HULL_RULES.lives`) |
| lives_max | 5 | P11-R07 |
| life_drop_chance | 1 % per destroyed enemy | P11-R07; about 1 extra life per level in World 1 shooting most enemies |
| bomb_drop_chance | 3 % per destroyed enemy | P11-R07 |
| life_bonus_points | 5 000 | P11-R07, at `lives_max` |
| bomb_bonus_points | 2 000 | P11-R07, at `bombs_max` |

## 🧑 Out of scope for this phase
- Pause, the pause overlay and the hidden-tab pause (Phase 12). Esc still leaves the level (D-041), and now saves the high score first (P11-R03).
- Sounds for bombs, pick-ups and extra lives (Phase 13).
- Remapping the bomb keys and a settings screen (Phase 14).
- Score multipliers, combos, chains, a level-complete or no-death bonus, and extra lives from score thresholds.
- A high score table, name entry, per-level or per-ship high scores, online leaderboards.
- A score kept across levels: every level attempt scores on its own (levels are picked one by one in the level select, P06-R01).
- Rebalancing enemies or bosses for bombs, beyond the P11-R07 weapon bonus check.

## 🧑 Engineering additions for this phase
- Unit tests for scoring, bombs, bonus kinds and the high score save, with the requirement IDs in the test names.
- e2e: score rises after a kill; a bomb clears the bullets on screen (key and touch); a high score is saved, then shown on the title after a reload; a Continue keeps the checkpoint score.
- The bomb's flash respects the flash limit (below 3 flashes a second), checked by a unit test on its timing.

## 🧑 Manual validation checklist
- [ ] Runs on GitHub Pages / `make dev` without console errors
- [ ] The score rises when enemies and boss parts are destroyed, and the `HI` line follows once it is beaten
- [ ] `R`, `Left Shift`, gamepad X / LB and the touch `BOMB` button each fire one bomb; the shockwave and flash look good and are not painful to look at
- [ ] A bomb clears the bullets, kills the small enemies and makes the ship safe for its duration
- [ ] Life and bomb bonuses are easy to tell from weapon bonuses (also in greyscale)
- [ ] A new high score shows on the panel and on the title screen after a reload
- [ ] A Continue after the mini boss keeps the score earned up to the checkpoint
- [ ] The HUD stays readable at 800×600 and on a phone

## 🧑 Notes, references, sketches
- GD §2 gives E to "Special / bomb", but D-043 gave E to the weapon switch; this phase uses `R` / `Left Shift` instead. The reviewer may update the GD §2 table.
- HUD layout sketch (480×640 logical):
```
 [ship ♥ 3  ● ● ●]      0012450       [Bullet · Lv 2/5]
 [HP ████████░░]       HI 0048200
                     [boss bar while fighting]
 ...
                                              [BOMB 3]
                                              [ FIRE ]
```

---

## 🧑 Review feedback
> After the agent reports, write corrections here, then say **"Fix phase 11"**.
> The agent ticks each item when fixed.

- [ ] 

---

## 🤖 Implementation report
> Filled by the agent. Do not edit (comment in Review feedback instead).

### Questions / blockers
None. The spec was drafted by the agent at the reviewer's request (D-091) and approved by the reviewer before implementation (2026-10-26). The technical choices it left open are in D-092.

### Plan
| Task | Requirement IDs |
|------|-----------------|
| Score: boss part points (`BossStats.partPoints`, `DropSource.points`, `EnemyWorld` breakPart), `LevelRun.score`, `LevelResult.score`, game scoring config (`game/config/scoring.ts`, `boss-kit.ts`) | P11-R01 |
| HUD score and high score lines (`ui/game-hud.ts`, `app/game-play-hud.ts`, texts, CSS) | P11-R02 |
| High score save (`saveHighScore`, `MenuController.recordScore` / `completeLevel`, `GameSession.end` with `SessionScores`, `start-app.ts`), score and "New high score!" on the panel | P11-R03 |
| Checkpoint score (`LevelCheckpoint.score`, restored on Continue) | P11-R04 |
| Bombs: `core/systems/player-bombs.ts`, `LevelRun` bomb step (damage, shot clearing, no hits, refill on a lost life), `GameDefinition.bombs`, `game/config/bombs.ts`, bomb renderer (`game/view/bombs/`, `config/bomb-look.ts`), HUD bomb icons | P11-R05 |
| Bomb controls: `GameControls` presses (keys, gamepad buttons, touch), config, HUD touch button | P11-R06 |
| Bonus kinds (`BonusKind`, `BonusRules.special` / `overflowPoints`, own random source, `place`), mini boss life drop, `HullRules.maxLives` / `addLife`, per-kind bonus looks (`bonus-geometry.ts`, `bonus-renderer.ts`, `bonus-look.ts`), measurement | P11-R07 |
| Test API: `score`, `bombs`, `enemyShots`, `bonusKinds`, `highScore`, `sendAction('bomb')` | P11-R08 |
| Unit and e2e tests, README controls, `docs/architecture.md`, decisions | all |

### Requirement traceability
| ID | Status (Done / Partial / Not done) | Code | Tests | Notes |
|----|-----------------------------------|------|-------|-------|
| P11-R01 | Done | `core/systems/enemy-world.ts`, `level-run.ts`, `core/entities/boss-pieces.ts`, `boss.ts`, `enemy.ts`, `game/config/scoring.ts`, `bosses/boss-kit.ts` | `level-run-score.test.ts`, `game/config/scoring.test.ts`, e2e `score-bombs.spec.ts` | Shots, rams and bombs all score (anything that takes an enemy's health). A boss part scores 10 % of its boss, rounded to 10. Parts lost in the boss's death score nothing. |
| P11-R02 | Done | `ui/game-hud.ts`, `app/game-play-hud.ts`, `game/config/menu-texts.ts`, `index.html` | `game-hud.test.ts`, `game-play.test.ts`, `scoring.test.ts`, e2e `score-bombs.spec.ts` (800×600, 390×844, overlap check) | Top centre, above the progress bar; `HI` shows the best of the saved score and the current one. |
| P11-R03 | Done | `app/saved-choices.ts`, `menu-controller.ts`, `game-session.ts`, `start-app.ts`, `menu-view-builder.ts`, `ui/screens/game-screen.ts` | `menu-controller.test.ts`, `saved-choices.test.ts`, `game-session.test.ts`, `menu-view-builder.test.ts`, `menu-overlay.test.ts`, e2e (complete → reload; Esc → reload) | Saved on level complete, game over, Esc, and before a Continue. |
| P11-R04 | Done | `level-run-types.ts` (`LevelCheckpoint.score`), `level-run.ts` | `level-run-score.test.ts`, e2e Continue test | The game over is recorded (P11-R03) before Continue is offered. |
| P11-R05 | Done | `core/systems/player-bombs.ts`, `level-run.ts`, `game/config/bombs.ts`, `game/view/bombs/bomb-renderer.ts`, `game/config/bomb-look.ts`, `ui/game-hud.ts` | `player-bombs.test.ts`, `level-run-score.test.ts`, `bomb-renderer.test.ts`, `game-play.test.ts`, e2e | The shots are cleared on every step while the bomb lasts (D-092). The flash fades in 0.3 s, one per bomb (≤ 1 a second). |
| P11-R06 | Done | `input/game-controls.ts`, `config/game-controls.ts`, `ui/game-hud.ts` (touch button), `app/game-play.ts`, `game-session.ts` | `game-controls.test.ts`, `game-hud.test.ts`, `game-play.test.ts`, `game-session.test.ts`, e2e (R, E, touch tap with fire button shown) | The gamepad press is detected by edge; presses made before a level are cleared. |
| P11-R07 | Done | `core/systems/bonus-world.ts`, `player-hull.ts`, `level-run.ts`, `game/config/bonuses.ts`, `hull.ts`, `game/view/bonuses/*`, `game/config/bonus-look.ts` | `bonus-world.test.ts`, `player-hull.test.ts`, `level-run-score.test.ts`, `bonus-renderer.test.ts`, `scoring.test.ts` | Weapon bonuses measured within 0 to −6 % of the same simulation with the D-049 rules (D-092). |
| P11-R08 | Done | `debug/test-api.ts`, `app/game-play-state.ts`, `main.ts` | `test-api.test.ts`, e2e `score-bombs.spec.ts` | Also `enemyShots` (to check the bomb). |

### Gate results
```
Light verification (implementation): make typecheck ✔ / make build ✔ / make e2e ✔ 95 passed (7.8 min), of which 7 new in `score-bombs.spec.ts`
Full gate (validation, make check): lint ✔ / typecheck ✔ / tests 1432 passed (156 files) / coverage 99.42 % lines, 87.18 % branches, 98.73 % functions, 98.68 % statements (Phase 10: 99.42 % lines) / build ✔ / e2e 95 passed (7.3 min)
The first run failed 2 earlier tests that did not expect Phase 11's changes: `LevelResult.score` (start-app), and the mini boss's life bonus (level-run-bosses P07-R07). Both expectations were updated (e777e12).
```

### How to test manually
1. `make dev`, play any level. The score shows at the top centre (`0000000`) with `HI` under it. Destroy enemies: the score rises.
2. `R` or `Left Shift` (gamepad X / LB) sets a bomb off: a cyan ring sweeps the screen, the enemy bullets vanish, the small enemies blow up. The bomb icons under the health bar go down by one. Holding the key sets off only one bomb. `E` still switches the weapon.
3. On a phone (or DevTools touch emulation), a round orange `BOMB 3` button sits above the Fire button. Tapping it sets a bomb off; it dims at 0.
4. Life bonuses are pink hearts, bomb bonuses orange balls marked B, weapon bonuses the yellow hexagons. Check them in greyscale too. The mini boss always drops a heart.
5. `?level=1-1&boss=final`, then press `K` five times: each part gives 800 points, and the panel shows the score and `New high score!`. Back to the title: the high score is there, also after a reload.
6. `?level=1-1&boss=mini`, press `K` until the mini boss is gone, then let the ship be destroyed. Choose Continue: the score starts again from the checkpoint's.
7. Check the HUD at 800×600 and on a phone.

### Deviations from spec
- P11-R05: the enemy shots are cleared during the whole bomb (1 s), not only when it goes off. The spec's "on screen" shots are a subset, and shots fired during the bomb would otherwise hit right after it (D-092).
- P11-R07: the D-049 counts (8 to 23) came from a simulator that was not kept. The check compares the same new simulator with the D-049 rules and with P11's: 0 to −6 % (D-092).
- The tunable note "about 1 extra life per level in World 1" does not hold for a player shooting most enemies: 1 to 8 life bonuses from enemies per level, plus the mini boss's (D-092). The chance is a tunable.

### Known limitations
- A player shooting most enemies gets 8 to 12 bomb bonuses per level, so the bombs often sit at 5 and the bonuses score points instead.
- The bomb's look (ring, flash) was only checked in software rendering; it needs a look in the browser.
- The high score is one number for the whole game (no table, no per-level score), as the spec asks.

### Suggestions for future phases
- Lower `special.life` (e.g. 0.3 %) and `special.bomb` (e.g. 1 %) if lives and bombs come too often.
- Sounds for the bomb, the pick-ups and an extra life (Phase 13); remapping the bomb keys (Phase 14).
