# In-game HUD

> **Area:** UI · **Prefix:** `UI-HUD` · **Related:** [look-and-layout.md](look-and-layout.md), [pause-menu.md](pause-menu.md), [../gameplay/scoring.md](../gameplay/scoring.md), [../gameplay/lives-and-damage.md](../gameplay/lives-and-damage.md), [../gameplay/bombs.md](../gameplay/bombs.md), [../gameplay/weapons.md](../gameplay/weapons.md), [../gameplay/controls.md](../gameplay/controls.md), [../gameplay/player-ship.md](../gameplay/player-ship.md), [../bosses/common.md](../bosses/common.md)

While a level is played, the HUD shows the player's state in one bar along the bottom of the
playfield: the level's progress, the ship, its lives, bombs and health, the score and high score,
the weapon and the level played. During a boss fight, a slim gauge up the left edge shows the
boss's health. How the score, lives, bombs, health and weapons work is in
[gameplay/](../gameplay/scoring.md); this file is only what the HUD shows and where.

## Requirements

### UI-HUD-01 — One bar at the bottom · MUST

The HUD is one bar, `hud_bar_height` high, along the bottom of the playfield, on blue-black glass
with a thin cyan line along its top. It holds, left to right:
- **left:** the ship's name, its lives and its bombs, and under them its health bar (UI-HUD-03, UI-HUD-04);
- **middle:** the score and, under it, the high score (UI-HUD-05);
- **right:** the weapon and its level, and under it the level played (UI-HUD-06).

Nothing else of the HUD is over the playfield, except the boss gauge (UI-HUD-12), the pause button
([pause-menu.md](pause-menu.md)) and, on touch screens, the fire and bomb buttons (UI-HUD-10).

**Acceptance criteria**
- Given a level, then the bar is along the bottom of the playfield and shows the ship, lives, bombs, health, score, high score, weapon and level.

*Sources: D-155, D-041, P11-R02.*

### UI-HUD-02 — The level's progress · MUST

A thin line along the top edge of the bar fills from left to right with the share of the level
flown, in the blue-to-green neon line.

**Acceptance criteria**
- Given a level half flown, then the progress line is half filled (unit test on the value given to the HUD).

*Sources: D-041, D-155.*

### UI-HUD-03 — The ship, its lives and its bombs · MUST

The left of the bar shows the ship's name (cyan, uppercase), then its lives as `♥ N` (green), then
its bombs as a count, `● N` (orange), however many there are.

**Acceptance criteria**
- Given the balanced ship with 3 lives and 7 bombs, then the HUD shows `Balanced` (in capitals), `♥ 3` and `● 7`.

*Sources: D-041, D-050, D-154, D-155.*

### UI-HUD-04 — Health · MUST

Under the name, a health bar (at most `hud_health_bar_width` wide) is filled with the share of
health left, in deep blue to cyan; under `low_health` of the ship's full health it turns red. Next
to it, a text gives the health, rounded up, over the full health: `HP 73 / 100`.

**Acceptance criteria**
- Given the balanced ship at 72.4 health, then the text is `HP 73 / 100` and the bar is 72.4 % full.
- Given the ship under 30 % health, then the bar is red; at 30 % or more, it is not.

*Sources: D-041, D-050.*

### UI-HUD-05 — Score and high score · MUST

The middle of the bar shows the attempt's score, zero-padded to `score_digits` digits, in large
text, and under it, smaller, `HI` and the larger of the saved high score and the current score,
padded the same way. Both change on the frame the points are scored.

**Acceptance criteria**
- Given a level starts with a saved high score of 12 340, then the HUD shows `0000000` and `HI 0012340`.
- Given the score passes the saved high score, then the `HI` line shows the current score from then on.

*Sources: P11-R02, D-155.*

### UI-HUD-06 — The weapon and the level played · MUST

The right of the bar shows the weapon in use and its level, `<weapon> · Lv <level>/<levels>`
(e.g. `Bullet · Lv 1/5`), in cyan, and under it, small, the level played (`Level 1-2`).

**Acceptance criteria**
- Given the laser at level 3 in level 2-4, then the HUD shows `Laser · Lv 3/5` and `Level 2-4`.

*Sources: D-041, D-155.*

### UI-HUD-07 — The bar never hides the ship · MUST

The ship never flies lower than 30 px above the bar: its bottom margin keeps it there
([gameplay/player-ship.md](../gameplay/player-ship.md)).

**Acceptance criteria**
- Given the ship pushed against the bottom of the playfield, then its model is fully above the bar.

*Sources: D-155.*

### UI-HUD-08 — Readable, nothing overlapping · MUST

At 800 × 600 and 390 × 844 the HUD texts are fully visible and no HUD element overlaps another: the
score lines, the health, the weapon, the boss gauge and the pause button are apart.

**Acceptance criteria**
- Given the HUD at 800 × 600 and 390 × 844, then the score lines are fully visible and overlap no other HUD element (e2e).

*Sources: P11-R02.*

### UI-HUD-09 — What the HUD does not show · MUST

The HUD has no Back button over the playfield (the level is left through the pause menu), and it
does not count the enemies destroyed (the "Level complete" panel does).

**Acceptance criteria**
- Given a level, then no Back button and no "enemies destroyed" text are shown.

*Sources: D-041, D-155, P06-R02.*

### UI-HUD-10 — Touch buttons above the bar · MUST

On touch screens only (coarse pointer), the fire button sits at the bottom right just above the
bar, and the bomb button above it, the same size. The bomb button shows the bombs left
(`Bomb N`) and is dimmed when none is left. What they do is in
[gameplay/controls.md](../gameplay/controls.md).

**Acceptance criteria**
- Given a touch screen, then the fire and bomb buttons show above the bar and cover none of it; given a mouse, then they are hidden.

*Sources: D-155, P11-R06.*

### UI-HUD-11 — The HUD takes no input and stays cheap · MUST

The HUD is drawn in the overlay at the logical resolution. It never takes clicks or taps, except on
the touch bomb button, so a drag over it still flies the ship. It is updated every frame but
touches the page only when a value it shows has changed. Its texts come from the game's texts.

**Acceptance criteria**
- Given two frames with the same values, then the second changes nothing in the page (unit test).

*Sources: D-041, D-092.*

### UI-HUD-12 — The boss gauge's place · MUST

While a boss fight lasts, the boss's health is shown as a slim vertical gauge up the left edge of
the playfield, from the top: `boss_gauge_height` tall, `boss_gauge_width` wide, with no panel. It
never hides the boss, which fights in the upper part of the screen, nor the HUD bar, the pause
button (top right) or the touch buttons (bottom right).

**Acceptance criteria**
- Given a boss fight, then the gauge is along the left edge, from the top, and overlaps neither the HUD bar nor the pause button.
- Manual check: the gauge is readable over every level's ground.

*Sources: P07-R02, D-105, D-155.*

### UI-HUD-13 — What the boss gauge measures · MUST

The gauge fills from the bottom with the boss's remaining health, its core and all its parts
together, against its full health. It goes down as any part or the core is damaged.

**Acceptance criteria**
- Given a part loses 50 HP, then the gauge goes down by 50 ÷ the boss's full HP (unit test on the value given to the HUD).

*Sources: P07-R02.*

### UI-HUD-14 — The boss gauge comes and goes · MUST

The gauge appears when the boss fight starts and fills up over `boss_gauge_fill` while the boss
arrives. It is removed when the boss is destroyed.

**Acceptance criteria**
- Given a boss fight starts, then the gauge appears with the boss's name and is full once the boss is in place.
- Given the boss is destroyed, then the gauge is gone.

*Sources: P07-R02.*

### UI-HUD-15 — Part notches · MUST

A small tick across the gauge marks the end of each destroyable part's share of the boss's full
health, so the player can see how much a part is worth.

**Acceptance criteria**
- Given a boss with parts of 200 and 300 HP and a 500 HP core, then the ticks are at 20 % and 50 % of the gauge (unit test).

*Sources: P07-R02, D-105.*

### UI-HUD-16 — The boss's kind and name · MUST

The boss's kind (`MINI BOSS` or `BOSS`, small, red) and its name (cyan) are written along the
gauge, from bottom to top.

**Acceptance criteria**
- Given the 1-1 mini boss fight, then `MINI BOSS` and the boss's name are written along the gauge.

*Sources: P07-R02, D-105.*

### UI-HUD-17 — The boss gauge's colours · MUST

The gauge has a red border; its fill goes from dark red at the bottom through red to orange-red,
with a red glow; the notches are white. Red marks the danger ([look-and-layout.md](look-and-layout.md)).

**Acceptance criteria**
- Manual check: the gauge is red, with white notches, in every level.

*Sources: P07-R02, D-198.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `hud_bar_height` | 48 px | `index.html` `.hud-panel` |
| Ship bottom margin | 78 px (30 px above the bar) | `src/config/game_play.py` `GAME_PLAY_CONFIG.ship_margin.bottom` |
| `low_health` | 30 % | `src/ui/game_hud.py` `LOW_HEALTH` |
| `hud_health_bar_width` | 110 px × 7 px | `index.html` `.hud-bar` |
| `score_digits` | 7 | `src/game/config/menu_texts.py` `SCORE_DIGITS` |
| HUD texts | `HP`, `♥ N`, `● N`, `<weapon> · Lv L/N`, `HI …`, `Bomb N`, `Mini boss`, `Boss`, `Level …` | `src/game/config/menu_texts.py` `MENU_TEXTS` (`hud*`, `gameLevel`) |
| Boss gauge place | 14 px from the top and left | `index.html` `.boss-bar` |
| `boss_gauge_height` × `boss_gauge_width` | 300 × 8 px | `index.html` `.boss-bar`, `.boss-track` |
| `boss_gauge_fill` | 1 s | `src/game/config/boss_fights.py` `BOSS_FIGHT_RULES["barFillSeconds"]` |
| Boss gauge fill colours | `#7a0016 → #ff2244 → #ff5a3c` | `index.html` `.boss-fill` |
| Touch fire / bomb buttons | 92 px round, right 22 px, bottom 74 / 180 px | `index.html` `.game-fire`, `.hud-bomb-button` |

## Notes

- The HUD was a set of panels at the top of the playfield (phase 6), with the score at the top
  centre (P11-R02) and the boss bar first across the top, then on the left under the health panel
  (D-105). The reviewer had it all put in one bar at the bottom (D-155).
