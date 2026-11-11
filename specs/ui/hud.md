# In-game HUD

> **Area:** UI · **Prefix:** `UI-HUD` · **Related:** [look-and-layout.md](look-and-layout.md), [pause-menu.md](pause-menu.md), [../gameplay/scoring.md](../gameplay/scoring.md), [../gameplay/lives-and-damage.md](../gameplay/lives-and-damage.md), [../gameplay/bombs.md](../gameplay/bombs.md), [../gameplay/weapons.md](../gameplay/weapons.md), [../gameplay/controls.md](../gameplay/controls.md), [../gameplay/player-ship.md](../gameplay/player-ship.md), [../bosses/common.md](../bosses/common.md)

While a level is played, the HUD shows the player's state over the playfield window, light: no
panels, only outlined text and slim gauges in its corners and along its edges. The score, high
score and level played at the top left; the lives and bombs at the top right; the level's progress
up the right edge; the ship's health at the bottom left; the weapon at the bottom right. During a
boss fight, a slim gauge across the top shows the boss's health. The side columns round the window
are empty. How the score, lives, bombs, health and weapons work is in
[gameplay/](../gameplay/scoring.md); this file is only what the HUD shows and where.

## Requirements

### UI-HUD-01 — Light readouts over the playfield window · MUST

The HUD is laid over the playfield window (540 × 720, [gameplay/screen.md](../gameplay/screen.md)).
It has no panels and no backgrounds: its texts are outlined in black and its gauges are slim, so the
level shows through everywhere (D-317). It holds:
- at the top left, the score, the high score under it and the level played under that (UI-HUD-05,
  UI-HUD-06);
- at the top right, the lives over the bombs (UI-HUD-03);
- at the top centre, the boss gauge while a boss is fought (UI-HUD-12);
- up the right edge, the level's progress rail (UI-HUD-02);
- at the bottom left, the ship's callsign and its health (UI-HUD-04);
- at the bottom right, the weapon and its level (UI-HUD-06).

The side columns, `hud_side_width` wide, down the left and right of the screen are opaque
blue-black and empty, with a thin cyan line along the window's edges; nothing of the level is drawn
there (D-252, D-263). The right one holds the touch fire and bomb buttons on touch screens
(UI-HUD-10). There is no pause button (D-251; the keyboard and the gamepad pause,
[pause-menu.md](pause-menu.md)).

**Acceptance criteria**
- Given a level, then the HUD holds, in this order, the score, the lives and bombs, the progress,
  the health, the weapon and the boss gauge, and no panel (unit test on the HUD's elements).

*Sources: D-155, D-041, P11-R02, D-251, D-252, D-253, D-317.*

### UI-HUD-02 — The level's progress · MUST

A 2 px rail up the right edge of the window fills from the bottom with the share of the level flown,
in the blue-to-green neon line, a bright bead where the fill ends.

**Acceptance criteria**
- Given a level half flown, then the progress rail is half filled (unit test on the value given to the HUD).

*Sources: D-041, D-155, D-317.*

### UI-HUD-03 — The lives and the bombs · MUST

The top right corner of the window shows the ship's lives as `♥ N` (green), and under them its
bombs as a count, `● N` (orange), however many there are.

**Acceptance criteria**
- Given the balanced ship with 3 lives and 7 bombs, then the HUD shows `♥ 3` and `● 7`.

*Sources: D-041, D-050, D-154, D-155, D-317.*

### UI-HUD-04 — Health · MUST

The bottom left corner shows the ship's name (small, cyan, uppercase) and the health, rounded up,
over the full health, `HP 73 / 100`; under them a health bar `hud_health_bar_width` wide, cut into
ten cells, filled with the share of health left, in deep blue to cyan. Under `low_health` of the
ship's full health the bar and the text turn red and the window's edges glow red, pulsing.

**Acceptance criteria**
- Given the balanced ship at 72.4 health, then the text is `HP 73 / 100` and the bar is 72.4 % full.
- Given the ship under 30 % health, then the bar is red and the HUD is marked low; at 30 % or more,
  it is not.

*Sources: D-041, D-050, D-317.*

### UI-HUD-05 — Score and high score · MUST

The top left corner shows the attempt's score, zero-padded to `score_digits` digits, in large text,
its padding zeros dim; under it, smaller, `HI` and the larger of the saved high score and the
current score, padded the same way. Both change on the frame the points are scored.

**Acceptance criteria**
- Given a level starts with a saved high score of 12 340, then the HUD shows `0000000` and `HI 0012340`.
- Given the score passes the saved high score, then the `HI` line shows the current score from then on.
- Given a score of 12 340, then `00` is drawn dim and `12340` bright (unit test).

*Sources: P11-R02, D-155, D-317.*

### UI-HUD-06 — The weapon and the level played · MUST

The bottom right corner shows the name of the weapon in use (cyan, uppercase) and under it one
diamond pip per level of the weapon, lit up to its level. Under the high score, small and dim, the
level played (`Level 1-2`).

**Acceptance criteria**
- Given the laser at level 3 of 5 in level 2-4, then the HUD shows `Laser` with 3 of its 5 pips lit,
  and `Level 2-4`.

*Sources: D-041, D-155, D-317.*

### UI-HUD-07 — The HUD never stops the ship · MUST

The ship flies only inside what the playfield window shows
([gameplay/screen.md](../gameplay/screen.md) GAME-SCREEN-05); the HUD over the window does not
narrow it. It may fly down to the bottom edge of the window, under the bottom readouts, its model
kept on screen by a bottom margin of half its length.

**Acceptance criteria**
- Given the ship pushed against a side of the playfield, then its model is fully inside the window; pushed against the bottom, then its model is fully on screen (unit test on the bounds).

*Sources: D-155, D-251, D-252, D-317.*

### UI-HUD-08 — Readable, nothing overlapping · MUST

At 800 × 600 and 390 × 844 the HUD texts are fully visible and no HUD element overlaps another: the
score lines, the health, the weapon, the progress rail and the boss gauge are apart.

**Acceptance criteria**
- Given the HUD at 800 × 600 and 390 × 844, then the score lines are fully visible and overlap no other HUD element (e2e).

*Sources: P11-R02.*

### UI-HUD-09 — What the HUD does not show · MUST

The HUD has no Back button over the playfield (the level is left through the pause menu), and it
does not count the enemies destroyed (the "Level complete" panel does).

**Acceptance criteria**
- Given a level, then no Back button and no "enemies destroyed" text are shown.

*Sources: D-041, D-155, P06-R02.*

### UI-HUD-10 — Touch buttons in the right column · MUST

On touch screens only (coarse pointer), the fire button sits at the foot of the right side column,
outside the playfield window, and the bomb button above it, the same size. The bomb button shows the bombs left
(`Bomb N`) and is dimmed when none is left. What they do is in
[gameplay/controls.md](../gameplay/controls.md).

**Acceptance criteria**
- Given a touch screen, then the fire and bomb buttons show in the right side column and cover none of the playfield window; given a mouse, then they are hidden.

*Sources: D-155, P11-R06.*

### UI-HUD-11 — The HUD takes no input and stays cheap · MUST

The HUD is drawn in the overlay at the logical resolution. It never takes clicks or taps, except on
the touch bomb button, so a drag over it still flies the ship. It is updated every frame but
touches the page only when a value it shows has changed. Its texts come from the game's texts.

**Acceptance criteria**
- Given two frames with the same values, then the second changes nothing in the page (unit test).

*Sources: D-041, D-092.*

### UI-HUD-12 — The boss gauge's place · MUST

While a boss fight lasts, the boss's health is shown as a slim horizontal gauge across the top of
the window, between the score and the lives: `boss_gauge_width` wide, `boss_gauge_height` tall. It
hides next to nothing of the boss, which fights over the playfield, and none of the readouts.

**Acceptance criteria**
- Given a boss fight, then the gauge is at the top of the window and overlaps none of the readouts (e2e).
- Manual check: the gauge is readable over every level's ground.

*Sources: P07-R02, D-105, D-155, D-317.*

### UI-HUD-13 — What the boss gauge measures · MUST

The gauge fills from the left with the boss's remaining health, its core and all its parts
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

The boss's kind (`MINI BOSS` or `BOSS`, small, red) and its name (cyan) are written above the
gauge, centred.

**Acceptance criteria**
- Given the 1-1 mini boss fight, then `MINI BOSS` and the boss's name are written above the gauge.

*Sources: P07-R02, D-105.*

### UI-HUD-17 — The boss gauge's colours · MUST

The gauge has a red border; its fill goes from dark red at the left through red to orange-red,
with a red glow; the notches are white. Red marks the danger ([look-and-layout.md](look-and-layout.md)).

**Acceptance criteria**
- Manual check: the gauge is red, with white notches, in every level.

*Sources: P07-R02, D-198.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `hud_side_width` | 370 px (the whole height; 200 px between D-251 and D-252, 140 px between D-253 and D-263); empty since D-317 | `index.html` `--hud-side`, `.game-screen::before`; the playfield window's `left`, `src/game/config/game.py` (D-252, D-263) |
| Ship bottom margin | 20 px (half the ship's length; 78 px while the bar was at the bottom) | `src/config/game_play.py` `GAME_PLAY_CONFIG.ship_margin.bottom` |
| `low_health` | 30 % | `src/ui/game_hud.py` `LOW_HEALTH` |
| `hud_health_bar_width` | 130 px × 6 px, ten cells of 11 px with 2 px gaps (116 × 9 px in the left column, D-253 to D-317) | `index.html` `.hud-bar` |
| `score_digits` | 7 | `src/game/config/menu_texts.py` `SCORE_DIGITS` |
| HUD texts | `HP`, `♥ N`, `● N`, `HI …`, `Bomb N`, `Mini boss`, `Boss`, `Level …` | `src/game/config/menu_texts.py` `MENU_TEXTS` (`hud*`, `gameLevel`) |
| Readout places | 12 px in from the window's corners (14 px on the right) | `index.html` `.hud-score`, `.hud-stock`, `.hud-health`, `.hud-weapon`, `.game-level` |
| Progress rail | 2 px wide, 104 px in from the window's top and bottom, 5 px from its right edge | `index.html` `.hud-progress` |
| Boss gauge place | 12 px from the top of the window, centred | `index.html` `.boss-bar` |
| `boss_gauge_width` × `boss_gauge_height` | 200 × 4 px (300 × 8 px, vertical, until D-317) | `index.html` `.boss-bar`, `.boss-track` |
| `boss_gauge_fill` | 1 s | `src/game/config/boss_fights.py` `BOSS_FIGHT_RULES["barFillSeconds"]` |
| Boss gauge fill colours | `#7a0016 → #ff2244 → #ff5a3c` | `index.html` `.boss-fill` |
| Touch fire / bomb buttons | 92 px round, in the right side column: right 24 px, bottom 40 / 160 px | `index.html` `.game-fire`, `.hud-bomb-button` |

## Notes

- The HUD was a set of panels at the top of the playfield (phase 6), with the score at the top
  centre (P11-R02) and the boss bar first across the top, then on the left under the health panel
  (D-105). The reviewer had it all put in one bar at the bottom (D-155). The owner then had it
  moved to a column on the left with a matching empty column on the right, the pause button
  removed and the ship free to reach the bottom edge (D-251, 2026-11-02), then the columns
  widened to 370 px and made opaque, the level drawn only in the 540 × 720 playfield window
  between them (D-252, the same day), then narrowed to 140 px, the window 1000 × 720: the
  owner found the columns far too wide (D-253, the same day), then back to 540 × 720 with 370 px
  columns (D-263). The owner then had the HUD put back over the playfield, light, and designed
  afresh (D-317, 2026-11-11): readouts in the window's corners with no panels, the progress as a
  rail up the right edge, the boss gauge across the top, the columns left empty.
