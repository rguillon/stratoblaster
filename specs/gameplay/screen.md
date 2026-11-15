# Screen and playfield

> **Area:** Gameplay · **Prefix:** `GAME-SCREEN` · **Related:** [level-flow.md](level-flow.md), [player-ship.md](player-ship.md), [../graphics/camera.md](../graphics/camera.md), [../ui/look-and-layout.md](../ui/look-and-layout.md), [../ui/hud.md](../ui/hud.md), [../enemies/common.md](../enemies/common.md)

The game is a vertical shoot 'em up played on a fixed, landscape logical screen of 1280 × 720
pixels (16:9: a full HD screen at ×1.5), scaled to fit the window. The playfield is a 1000 × 720
window in the middle of that screen, between two empty side columns: a flat plane at flight
altitude over which the level's ground scrolls down, drawn nowhere else. This file fixes the
logical resolution, how it is fitted to the window, the coordinate conventions, what part of the
playfield the screen shows, where the ship may fly and what is removed off screen. The camera
itself (tilt, field of view) is in [graphics/camera.md](../graphics/camera.md); the HUD and menu
layout in [ui/](../ui/).

## Requirements

### GAME-SCREEN-01 — Logical resolution · MUST

The game is laid out on a logical screen of **1280 × 720** pixels (landscape, 16:9, a full HD
screen at ×1.5; it was 480 × 640, portrait, until D-249). The playfield is a **540 × 720** window
(3:4, the original ratio) in the middle of the screen, from x = 370 to 910 of it (D-252, D-263;
1000 × 720 between D-253 and D-263): the level is drawn and played there and nowhere else, the HUD laid over it; empty side columns fill the rest
([ui/hud.md](../ui/hud.md)). Every gameplay position, size, distance and speed is in logical
pixels (`px`) of the playfield: X to the right, Y up, the origin at the bottom-left corner of the
playfield window. Angles are in degrees from forward (+Y), positive to the right. The logical
resolution and the window are game data.

**Acceptance criteria**
- Given the game definition, then its screen is 1280 × 720 and its playfield window 540 × 720,
  in the middle (unit test).
- Given the ship at x = 500, then it is in the middle of the playfield across.
- Given a level, then nothing of it is drawn outside the playfield window (the camera draws only
  into the window's viewport, unit test).

*Sources: GD-02, D-015, D-249, D-252, D-253.*

### GAME-SCREEN-02 — Fitted to the window · MUST

The stage (the 3D canvas and the HTML overlay of the menus and the HUD) keeps its 16:9 logical
ratio, never stretched, centred. What must fit the window is the playfield window (GAME-SCREEN-04),
where everything is drawn, played and laid out (D-252, D-317, D-319): it is the largest it can be
in the window, never cropped, and the stage's side columns round it may run past the window's
edges rather than shrink it (owner, 2026-11-11, D-329: "the display area get small for no good
reason when I play with the browser size"). A window wide enough for the whole stage shows it
whole, letterboxed as before. A game without a playfield window fits the whole stage. The overlay
is laid out at 1280 × 720 CSS pixels and scaled with the stage, so the canvas and the overlay
always line up. The stage is fitted again when the window is resized (ENG-110).

**Acceptance criteria**
- Given windows of 800 × 600, 1000 × 900, 1920 × 1080 and 390 × 844, then the stage keeps its
  16:9 ratio and its playfield window is wholly visible, centred, filling the window's width or
  height (unit test on the fit, e2e); at 1920 × 1080 the whole stage fills the window.
- Given the window is resized, then the stage is fitted to the new size.
- Given a window with no room, then the scale is 0 and nothing throws (unit test).

*Sources: GD-02, GD-03, D-008, D-249.*

### GAME-SCREEN-03 — Vertical scrolling · MUST

The game scrolls vertically: the level's ground (terrain, props, clouds) moves down the screen
under the playfield as the level goes on, at the level's ground speed
([level-flow.md](level-flow.md)). The player ship, the enemies, the shots and the bonuses move in
the playfield's coordinates, not with the ground. Between two simulation steps, the drawn ground
position is interpolated, so the scroll is smooth at any frame rate.

**Acceptance criteria**
- Given a level scrolling at 60 px/s, when 1 s of play passes, then the ground has moved 60 px down
  the screen and the ship has not moved with it (unit test on the scroll track).

*Sources: GD-01, P06-R02, D-036, D-054.*

### GAME-SCREEN-04 — What the screen shows of the playfield · MUST

The playfield is seen through the tilted scenery camera ([graphics/camera.md](../graphics/camera.md)):
the bottom and top edges of the screen pass through the bottom and top edges of the playfield, and
the screen shows less of the playfield's width at the bottom than at the top (`seen_half_width`).
A point of the playfield is **on screen** when 0 ≤ y ≤ 720 and its distance across from the middle
(x = 500) is at most the half width seen at its height. Gameplay rules that say "on screen" use
this test (which targets the player can hit, what a bomb reaches).

**Acceptance criteria**
- Given a point at the bottom edge 320 px from the middle, then it is not on screen; the same point
  at the top edge is (unit test on the framing).

*Sources: D-042, D-048.*

### GAME-SCREEN-05 — Where the ship may fly · MUST

The player ship flies only inside what the playfield window shows, within these margins
(`ship_margin`): at least 18 px inside the width seen at its height (the side columns are
outside the window, [ui/hud.md](../ui/hud.md)), no lower than y = 20 (half its length: its model
stays on screen; it was y = 78 while the HUD had a bar along the bottom, D-155 to D-251), and no
higher than 200 px below the top edge (y = 520). Pushed against an edge, the ship stops there: its
speed towards that edge drops to 0, and it can slide along it.

**Acceptance criteria**
- Given the ship pushed against any edge, then it stays on screen and inside the margins (unit
  test).
- Given the ship flying diagonally into a side edge, then it keeps its vertical speed (unit test).

*Sources: P06-R02, D-155.*

### GAME-SCREEN-06 — The ship's reach · MUST

The ship's reach is the X range the ship can get to at the bottom of its flight area: the middle
± the flight area's half width at y = 20 (about x 207 to 793). Enemies that come in from the top
keep to it ([enemies/common.md](../enemies/common.md)), and bonuses drop inside it
([bonuses.md](bonuses.md)), so the player can always fly under them.

**Acceptance criteria**
- Given a bonus dropped by an enemy destroyed at x = 20, then it falls at the left end of the reach
  (unit test).

*Sources: D-048, D-049.*

### GAME-SCREEN-07 — What leaves the playfield is removed · MUST

Player shots, enemy shots and bonuses more than `cull_margin` (80 px) outside the playfield are
removed. An enemy is removed once it has been on the playfield and is then more than
`cull_margin` outside it (the enemy rules are in [enemies/common.md](../enemies/common.md)).
Nothing scores or drops anything by being removed this way.

**Acceptance criteria**
- Given a player bullet 81 px above the top edge, then it is gone (unit test).
- Given a bonus 81 px under the bottom edge, then it is gone (unit test).

*Sources: D-015, D-036.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| logical screen | 1280 × 720 px | `src/game/config/game.py` `GAME_CONFIG["screen"]` (GAME-SCREEN-01, D-249) |
| playfield window | 540 × 720 px, left 370 (viewport 0.289, 0, 0.422, 1 of the canvas) | `GAME_CONFIG["playfield"]`, `src/game/index.py` `PLAYFIELD`, `GameDefinition.playfield` (D-252, D-263) |
| seen_half_width | about ±165 px at y = 0 and ±278 at y = 720 (D-252) | From the camera (tilt 35°, field of view 40°, `src/game/config/scenery_look.py`) and the window's 3:4 aspect, `src/render/scenery/playfield_framing.py` `visible_half_width` |
| ship_margin | side 18 px, bottom 20 px, top 200 px | `src/config/game_play.py` `GAME_PLAY_CONFIG.ship_margin` (GAME-SCREEN-05, D-251) |
| ship reach | x ≈ 207 … 793 px | Computed from `ship_margin` and `seen_half_width` at y = 20, GAME-SCREEN-06 |
| cull_margin | 80 px | `src/config/game_play.py` `GAME_PLAY_CONFIG.cull_margin` (GAME-SCREEN-07) |

## Notes

- D-048 measured the reach as x 107–373 when the bottom margin was 30 px; with the HUD bar at the
  bottom (D-155, bottom margin 78 px) it is about x 99–381.
- GD-03 only said "responsive"; the letterboxed 3:4 fit is the reading settled in phase 1 (D-008).
- D-249 (owner, 2026-11-02): the screen went from 480 × 640 (3:4) to 1280 × 720 (16:9), so the
  game takes a whole 1920 × 1080 screen. The logical pixel, and so every speed, size and margin,
  is unchanged; the playfield is 80 px taller and 800 px wider, the ship's reach about 2.8 times
  as wide (804 px instead of 282). On a portrait phone the stage is fitted by width (390 × 219
  at 390 × 844): the mobile layout is still to come.
- D-252 (owner, 2026-11-02): the level is drawn and played in a 540 × 720 window in the middle
  of the 16:9 screen, the HUD's columns on both sides; the gameplay is back to the 3:4 playfield
  (×1.125 the old 480 × 640), the wave density and the ground extents of D-249 with it.
- D-253 (owner, 2026-11-02): the columns were far too wide; the window is 1000 × 720, the
  columns 140 px. The ship's reach is 586 px wide (300 in the 540 px window), the ground in view
  ±390 units at the sea level; the wave density is 2 again, as on the whole screen (D-249).
- D-263 (owner, 2026-11-04): back to the original 3:4 ratio: the window is 540 × 720 again and the
  HUD's columns 370 px, outside the playing area (D-252's layout). The ship's reach is about
  x 120 … 420, the wave density 1.5 and the ground extents of D-252 are back.
