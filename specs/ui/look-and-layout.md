# Look and layout

> **Area:** UI · **Prefix:** `UI-LOOK` · **Related:** [title-screen.md](title-screen.md), [hud.md](hud.md), [menu-input.md](menu-input.md), [boot-and-loading.md](boot-and-loading.md), [../gameplay/screen.md](../gameplay/screen.md), [../graphics/art-direction.md](../graphics/art-direction.md), [../graphics/readability.md](../graphics/readability.md)

The menus, the HUD and the panels are an HTML/CSS overlay over the 3D canvas, laid out at the
game's logical resolution and scaled to the window. They share one look, a cyan neon night made
clear (D-324): a blue-black ramp, one electric cyan accent, a chrome logo with a hard extruded edge,
a cyan horizon line under the headings, and nothing that glows. This file fixes the layout, the
palette, the fonts, the selection marks and the logo.

The chrome is quiet so the scenes carry the colour: the chrome logo on the title, the 3D trench and
the ship behind the menus, the level in play. Panels, entries and texts frame them and never
compete (no glow, no hue gradient on a panel or a text). The 3D look of the levels is in
[graphics/](../graphics/art-direction.md); the title's 3D backdrop is in
[title-screen.md](title-screen.md).

## Requirements

### UI-LOOK-01 — An overlay laid out at the logical resolution · MUST

The menus, the HUD, the pause menu and the end-of-level panels are an HTML/CSS overlay (`ui/`) over
the canvas. It is laid out at the logical resolution, 1280 × 720 logical px (CSS px before
scaling; 480 × 640 until D-249), so every size in the UI specs is in logical px.

**Acceptance criteria**
- The overlay element is 1280 × 720 px before its scale (unit test of the stage fit).

*Sources: P01-R13, GD-02, D-008, D-041.*

### UI-LOOK-02 — Fitted to the window, never cropped or stretched · MUST

The canvas and the overlay share one box with the 16:9 logical aspect ratio, fitted so its
playfield window is as large as the window allows, centred (GAME-SCREEN-02, D-329): dark bars
(letterbox) on the rest, or, in a window narrower than 16:9, the side columns running past its
edges. The menus have the game's aspect
ratio (D-319): every menu screen, and the 3D backdrop behind the menus, are laid in the playfield
window (540 × 720, 3:4, [gameplay/screen.md](../gameplay/screen.md)), between opaque blue-black
side columns with a hairline on the window's edges, as a level is. Their sliders and entry lists
keep to a column (`menu_column`) inside it. The dev viewer's 3D views keep the whole box. The
overlay is scaled to that box with a CSS transform, so the 3D scene and the HTML over it line up.
The box follows window resizes.

On a phone (the whole box would be scaled under `phone_scale`, such as 0.3 on a 390 × 844
portrait screen), the
menus, the pause menu, the settings and the end-of-level panels are instead laid out across the
whole window at their real size (one CSS pixel per logical pixel), over the 16:9 canvas, so they stay
readable and their touch targets keep their size (UI-INPUT-11). The HUD of a level being played
keeps to the box, lined up with the playfield, which fills the phone's width (D-329); under a
panel it is hidden (D-286).

**Acceptance criteria**
- At window sizes 800 × 600 and 1920 × 1080, the menu is fully visible, not cropped, not stretched (16:9 within 0.5 %), and fills the window's width or height.
- Given the menu scenes of a game with a playfield window, then their cameras draw only in it (unit test); manual check: every menu screen sits in the 3:4 window, between the side columns.
- At 390 × 844 (portrait phone), the canvas is the 16:9 box and the menus fill the window at their real size (e2e: UI-INPUT-11, UI-SET-03); a level being played keeps its HUD on the box, a pause menu does not (unit tests).
- Given the window goes from 800 × 600 to 390 × 844, then the menu follows within 5 s (e2e).

*Sources: P01-R13, GD-02, GD-03, ENG-110, D-008, D-249, D-286, D-319, D-326.*

### UI-LOOK-03 — Cyan on blue-black · MUST

The overlay uses one blue-black neutral ramp and one accent (owner, 2026-11-11, D-324: "put back the
cyan theme"; synthwave pink D-323 and neon blue/green D-198 before):
- **surfaces**: blue-black background `#010a10`, glass panels `rgba(4, 18, 28, 0.86)`;
- **hairlines**: the primary text colour at 12 % opacity for borders, 24 % on hover;
- **text**, three roles: primary `#ecfdff`, secondary `#9fbcc4`, muted `#5f7f89`;
- **accent**, electric cyan `#00e8ff`, used rarely: the selected entry, the horizon line, the
  sliders' filled cells, the loading and progress fills, the player's gauges in the HUD, the ship
  select ring;
- **green** `#3dff9a`: good things only (the lives, a new high score);
- **chrome** (white, pale cyan, a navy horizon line, cyan): only inside the logo's letters
  (UI-LOOK-12).

Every other fill is a solid colour: no hue gradient on a panel, a bar or a text.

**Acceptance criteria**
- Manual check in screenshots of the title, level select, settings, pause menu and HUD: cyan on blue-black, green only on the lives and the new high score, no magenta, pink or violet.

*Sources: P01-R13, GD-60, D-198.*

### UI-LOOK-04 — Red for danger, orange for bombs · MUST

Red (`#ff3b47`) is used only for danger: low health, the "Game over" panel, locked levels and the
"Locked!" status, and the boss gauge. The bombs are orange (`#ff9a2e`).

**Acceptance criteria**
- Given the HUD at full health, then nothing in it is red; under 30 % health, the health bar is red.

*Sources: D-198.*

### UI-LOOK-05 — The UI scheme leaves the gameplay colours alone · MUST

The UI palette changes no gameplay colour (enemies, enemy shots, player shots, pickups) and none of
the levels' 3D look ([graphics/readability.md](../graphics/readability.md)). Over the playfield, the
UI draws no frame or line; the HUD over it is light, outlined text and slim gauges in the
window's corners and edges ([hud.md](hud.md), D-317).

**Acceptance criteria**
- Given the game screen, then no frame or line is drawn over the playfield.

*Sources: D-198.*

### UI-LOOK-06 — Rounded glass panels and the horizon line · SHOULD

Entries are glass panels with a 1 px hairline border and 8 px rounded corners; the panels (pause,
end of level) have 16 px corners. Menu screens have no frame of their own: the hairline on the
playfield window's edges (UI-LOOK-02) is their only edge. Each heading sits over the **horizon
line**, the UI's one signature: a 2 px cyan rule, 48 px wide, under the heading, centred, the
same line as the one under the logo. Headings are in sentence case, without a glow; only a soft dark
shadow keeps them readable over the 3D scene. No text, panel or gauge of the overlay glows (no
coloured `box-shadow`, `text-shadow` or `drop-shadow`).

**Acceptance criteria**
- Manual check: the title, level select and settings screens have no frame and nothing glowing; each heading has its horizon line.

*Sources: P01-R13, D-013, D-014, D-103, D-198.*

### UI-LOOK-07 — No screen overlay · MUST

No CRT scanlines, vignette or other overlay is drawn over the stage: the levels show without any
layer over them.

**Acceptance criteria**
- Given the game screen, then no element with a scanline or vignette background covers the canvas.

*Sources: D-040.*

### UI-LOOK-08 — The selection shows without colour · MUST

The selected entry is a solid cyan block with dark text (much lighter than the dark panels),
without a glow, plus a mark that does not rely on colour:
- title entries and the pause menu's entries: a `▶` before (and on the title a `◀` after), always
  one space from the word;
- level cells: a 3 px dashed white outline.

**Acceptance criteria**
- The selected entry stays identifiable in a greyscale screenshot.
- e2e: the selected title entry has its `▶`, the selected level cell a dashed outline.

*Sources: P01-R13, D-013, D-014, D-103, D-198, D-326.*

### UI-LOOK-09 — Readable by kids · MUST

The menus are easy to read for a child: large text for entries (20 to 32 px, level cells 24 px,
headings 32 px, hints 16 px; only the HUD readouts and the version are smaller, and no text is under
12 px but the version, 11 px), short words, few words per screen. Hints use plain words ("Press Space / Enter or tap to start"). Texts are in
sentence case, at weight 500, 600 for the headings, the entries and the score; letter spacing is at
most 0.04 em; no italic and no weight over 600 but the logo. Interface texts end without an exclamation mark. Sizes and
spacing are multiples of 4 px.

**Acceptance criteria**
- Manual check at 390 × 844: every menu text can be read without zooming.
- Unit test of the game texts: no text ends with `!`.

*Sources: P01-R13, D-326.*

### UI-LOOK-10 — Every text comes from the game · MUST

Every menu, HUD and panel text (titles, entries, hints, labels, number formats) comes from the
game's texts (`src/game/config/menu_texts.py`, given to the engine by the game definition), not
from engine code (ENG-140, ENG-144).

**Acceptance criteria**
- Unit test: the menu views are built from the `texts` of the game definition given to them.

*Sources: P01-R04, P01-R07, D-008, D-041.*

### UI-LOOK-11 — System fonts, nothing from another server · MUST

The overlay uses system fonts only: a condensed sans-serif stack (Bahnschrift, DIN Alternate,
Roboto Condensed, Arial Narrow, Segoe UI, then the system UI font) for names and entries, and a
monospace stack (Consolas, Menlo, DejaVu Sans Mono, Liberation Mono) for readouts: scores, percent,
level numbers, the version, the HUD. No font or other file is loaded from a third-party server, so
the game works offline once loaded.

**Acceptance criteria**
- e2e: every request made by the page goes to its own origin.

*Sources: P01-R13, D-013, D-014.*

### UI-LOOK-12 — The chrome logo · MUST

The logo is the title's one rich moment (D-324): the game's name in black (900), italic, uppercase
condensed letters at `title_logo_size`, filled with a cold 80s chrome (white at the top, pale cyan,
a hard navy horizon line across the middle, cyan, pale cyan at the foot), with a thin pale outline
and a solid deep teal extruded edge `title_logo_depth` down and to the right (hard, unblurred
layers, like a cast metal badge). Under it, the horizon line: a 4 px cyan bar, a little narrower
than the name. Nothing behind it (no sun or emblem); it does not glow or move.

**Acceptance criteria**
- Manual check: the title logo is chrome letters with a hard teal edge over a cyan bar, nothing behind them, nothing glowing or moving.

*Sources: P01-R13, D-103, D-104, D-198.*

### UI-LOOK-13 — The logo fits the screen · MUST

The logo is sized (`title_logo_size`) so the 13-letter name fits the screen's width (1280 px; it
was sized for 480) with a condensed font. Where the system has no condensed font, its font size
goes down 1 px at a time, after each screen is shown, until it fits its parent's width. Its letters are never clipped.

**Acceptance criteria**
- e2e (also on a CI runner without condensed fonts): the logo is not wider than the screen.

*Sources: D-016, D-017.*

### UI-LOOK-14 — Motion that explains · SHOULD

Only motion that tells something: a new screen fades in ([screen-flow.md](screen-flow.md)), a
locked level shakes ([level-select.md](level-select.md)), the low-health alarm pulses in the HUD
([hud.md](hud.md)), a hovered entry changes colour (`menu_hover_duration`). Nothing in the menus
loops: the hints and the logo are still. Under the system's "reduce motion" setting, the screen
fade does not move and the alarm does not pulse.

**Acceptance criteria**
- Given the title screen, then no element of the overlay has a running infinite animation.
- Given `prefers-reduced-motion: reduce`, then the low-health alarm is not animated.

*Sources: D-013, D-103.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| Logical resolution | 1280 × 720 | `src/game/config/game.py` `GAME_CONFIG.screen` (GD-02, D-249) |
| `menu_column` | 560 px, within the 540 px window since D-319 | `index.html` `--menu-column` (UI-LOOK-02, D-249) |
| Menu window | the playfield window, 540 × 720 at x = 370 | `index.html` `#menu:not(.phone)::before`, `.menu-screen`; `src/app/menu_scenes.py` `window_camera` (D-319) |
| `phone_scale` | 0.5 CSS px per logical px | `src/ui/stage_fit.py` `PHONE_SCALE`; `index.html` `#menu.phone` (UI-LOOK-02, D-286) |
| `--cyan` | `#00e8ff`, the one accent | `index.html` `:root` |
| `--green` | `#3dff9a`, lives and new high score only | `index.html` `:root` |
| `--text` / `--text-2` / `--text-3` | `#ecfdff` / `#9fbcc4` / `#5f7f89` | `index.html` `:root` |
| `--line` / `--line-2` | primary text at 12 % / 24 % | `index.html` `:root`, hairlines |
| `--red` | `#ff3b47` | `index.html` `:root`, danger only |
| `--orange` | `#ff9a2e` | `index.html` `:root`, bombs |
| `--glass` | `rgba(4, 18, 28, 0.86)` | `index.html` `:root` |
| `--night` / `--letterbox` | `#010a10` / `#000407` | `index.html` `:root` |
| Chrome | `#ffffff → #d4fbff → #0b3a5a (50 %) → #00e8ff → #c8fbff` | `index.html` `.title-name`, the logo only |
| Radii | 8 px entries, 16 px panels | `index.html` `--r-control`, `--r-panel` |
| Horizon line | 2 × 48 px, `--cyan` | `index.html` `.menu-heading::after` |
| `title_logo_depth` | 6 px, `#05607a` to `#022a38` | `index.html` `.title-name` `filter` |
| `title_logo_size` | 60 px | `index.html` `.title-name`; lowered by `src/ui/shrink_to_fit.py` down to 12 px at most |
| `menu_hover_duration` | 120 ms, `cubic-bezier(0.2, 0, 0, 1)` | `index.html` `.menu-entry` |

## Notes

- History of the look: a synthwave sun and grid with a dark background (D-012), then a cyberpunk
  HUD in acid yellow, cyan and red with corner brackets, scanlines and glitches over a night city
  (D-013, D-014), then the scanlines removed (D-040), then darksynth magenta, violet and blood red
  with a chrome logo over a striped sun (D-103), then the sun removed (D-104), and now neon
  blue/green (D-198), then retro synthwave made clear (D-323, 2026-11-11): a night violet ramp, one
  pink accent, a striped sun behind the logo, no glows or gradients in the chrome; then the same
  day back to cyan on blue-black with a chrome logo and no sun (D-324, owner: "remove the ugly
  sun [...] put back a kick ass game name logo, and put back the cyan theme").
  `02-game-design.md` GD-60 still said "darksynth" for the menus and the HUD
  when D-198 was made at the reviewer's request; the 3D art direction is in
  [graphics/art-direction.md](../graphics/art-direction.md).
- What stays across the looks: the glass panels (rounded since D-323), the monospace readouts, the
  hazard-striped locked cells, the italic capital logo and the light selected block with dark text.
  The chamfers, the chrome gradient, the neon frame and bottom line, the glows and the pulsing hints
  went in D-323.
- D-249 (2026-11-02): the screen is 16:9. The menus were laid out for the 3:4 screen and only
  got a centre column; on a 390 × 844 phone the stage is now 390 × 219 CSS px. The phone layout
  (D-286) lays the menus out across the window there, so the UI-INPUT-11 touch targets hold.
