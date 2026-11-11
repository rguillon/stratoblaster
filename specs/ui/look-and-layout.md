# Look and layout

> **Area:** UI · **Prefix:** `UI-LOOK` · **Related:** [title-screen.md](title-screen.md), [hud.md](hud.md), [menu-input.md](menu-input.md), [boot-and-loading.md](boot-and-loading.md), [../gameplay/screen.md](../gameplay/screen.md), [../graphics/art-direction.md](../graphics/art-direction.md), [../graphics/readability.md](../graphics/readability.md)

The menus, the HUD and the panels are an HTML/CSS overlay over the 3D canvas, laid out at the
game's logical resolution and scaled to the window. They share one look: electric cyan and neon
green on blue-black glass, a cold chrome logo, soft neon glows. This file fixes the layout, the
palette, the fonts, the selection marks and the logo. The 3D look of the levels is in
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

The canvas and the overlay share one box, the largest box with the 16:9 logical aspect ratio that
fits the window, centred, with dark bars (letterbox) on the rest. The menus have the game's aspect
ratio (D-319): every menu screen, and the 3D scenes behind the menus (the backdrop, the ship select
stage), are laid in the playfield window (540 × 720, 3:4, [gameplay/screen.md](../gameplay/screen.md)),
between opaque blue-black side columns with a thin cyan line on the window's edges, as a level is.
Their cards, sliders and entry lists keep to a column (`menu_column`) inside it. The dev viewer's
3D views keep the whole box. The overlay is scaled to that box
with a CSS transform, so the 3D models and their HTML captions line up. The box follows window
resizes.

On a phone (the box scaled under `phone_scale`, such as 0.3 on a 390 × 844 portrait screen), the
menus, the pause menu, the settings and the end-of-level panels are instead laid out across the
whole window at their real size (one CSS pixel per logical pixel), over the 16:9 canvas, so they stay
readable and their touch targets keep their size (UI-INPUT-11). The HUD of a level being played
keeps to the 16:9 box, lined up with the playfield; under a panel it is hidden (D-286).

**Acceptance criteria**
- At window sizes 800 × 600 and 1920 × 1080, the menu is fully visible, not cropped, not stretched (16:9 within 0.5 %), and fills the window's width or height.
- Given the menu scenes of a game with a playfield window, then their cameras draw only in it (unit test); manual check: every menu screen sits in the 3:4 window, between the side columns.
- At 390 × 844 (portrait phone), the canvas is the 16:9 box and the menus fill the window at their real size (e2e: UI-INPUT-11, UI-SET-03); a level being played keeps its HUD on the box, a pause menu does not (unit tests).
- Given the window goes from 800 × 600 to 390 × 844, then the menu follows within 5 s (e2e).

*Sources: P01-R13, GD-02, GD-03, ENG-110, D-008, D-249, D-286, D-319.*

### UI-LOOK-03 — Neon blue/green palette · MUST

The overlay uses a neon blue/green scheme (reviewer, 2026-10-30):
- **neon**, electric cyan `#00e8ff`: the selected entries, the headings' glow, the loading bar, the scores;
- **accent**, neon green `#3dff9a`: panel borders, labels, the sliders, the Back button;
- **deep**, deep blue `#0a5cff`: glows and the start of the bars;
- blue-black glass panels (`rgba(2, 14, 22, 0.8)`) on a blue-black background (`#010a10`), near-white text (`#ecfdff`);
- a blue-to-green **neon line** gradient (deep blue → cyan → green → lime) for the lines and bar fills.

The magenta / violet / blood red darksynth look (D-103) and the acid yellow / cyan / red cyberpunk
look (D-013, D-014) are gone.

**Acceptance criteria**
- Manual check in screenshots of the title, ship select, level select, settings, pause menu and HUD: cyan, green and deep blue on blue-black, no magenta or violet.

*Sources: P01-R13, GD-60, D-198.*

### UI-LOOK-04 — Red for danger, orange for bombs · MUST

Red (`#ff2244`) is used only for danger: low health, the "Game over" panel, locked levels and the
"Locked!" status, and the boss gauge. The bombs are orange (`#ff8a1e`).

**Acceptance criteria**
- Given the HUD at full health, then nothing in it is red; under 30 % health, the health bar is red.

*Sources: D-198.*

### UI-LOOK-05 — The UI scheme leaves the gameplay colours alone · MUST

The UI palette changes no gameplay colour (enemies, enemy shots, player shots, pickups) and none of
the levels' 3D look ([graphics/readability.md](../graphics/readability.md)). Over the playfield, the
UI draws no neon frame or line; the HUD over it is light, outlined text and slim gauges in the
window's corners and edges ([hud.md](hud.md), D-317).

**Acceptance criteria**
- Given the game screen, then the menu screens' neon frame and bottom line are not drawn.

*Sources: D-198.*

### UI-LOOK-06 — Glass panels and a neon frame · SHOULD

Entries and panels are glass panels with a 2 px border and their top-left and bottom-right corners
cut off (14 px chamfer); the level cells are square, so the dashed outline of the selected cell
shows whole. Each menu screen has a thin neon frame 6 px inside its edge (cyan at the top, fading
to deep blue), and a 3 px neon line along its bottom, both softly glowing. Headings are uppercase
with a cyan and deep blue glow.

**Acceptance criteria**
- Manual check: the title, ship select, level select and settings screens show the frame and the bottom line; the level cells have square corners.

*Sources: P01-R13, D-013, D-014, D-103, D-198.*

### UI-LOOK-07 — No screen overlay · MUST

No CRT scanlines, vignette or other overlay is drawn over the stage: the levels show without any
layer over them.

**Acceptance criteria**
- Given the game screen, then no element with a scanline or vignette background covers the canvas.

*Sources: D-040.*

### UI-LOOK-08 — The selection shows without colour · MUST

The selected entry is a light cyan block with black text (much lighter than the dark panels), with
a glow, plus a mark that does not rely on colour:
- title entries and the pause menu's entries: a `▶` before (and on the title a `◀` after);
- ship cards: a `▲` above the selected card;
- level cells: a 3 px dashed white outline.

**Acceptance criteria**
- The selected entry stays identifiable in a greyscale screenshot.
- e2e: the selected title entry has its `▶`, the selected ship card its visible `▲` (hidden on the others), the selected level cell a dashed outline.

*Sources: P01-R13, D-013, D-014, D-103, D-198.*

### UI-LOOK-09 — Readable by kids · MUST

The menus are easy to read for a child: large text for entries and names (entries and ship names
18 to 34 px, level cells 22 px, headings 32 px, hints 15 px; only the ship stats, the HUD readouts
and the version are smaller), short words, few words per screen. Hints use plain words ("Press
Space / Enter or tap to start").

**Acceptance criteria**
- Manual check at 390 × 844: every menu text can be read without zooming.

*Sources: P01-R13.*

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

### UI-LOOK-12 — The logo · MUST

The logo is the game's name in heavy, italic, uppercase letters filled with a cold chrome gradient
(white, pale cyan, a navy horizon line across the middle, cyan, pale green), in a slow neon glow
that pulses between cyan and green (`title_glow_period`). There is no sun or other emblem behind it.

**Acceptance criteria**
- Manual check: the title logo is chrome letters in a cyan / green glow, with nothing behind them.

*Sources: P01-R13, D-103, D-104, D-198.*

### UI-LOOK-13 — The logo fits the screen · MUST

The logo is sized (`title_logo_size`) so the 13-letter name fits the screen's width (1280 px; it
was sized for 480) with a condensed font. Where the system has no condensed font, its font size
goes down 1 px at a time, after each screen is shown, until it fits its parent's width. Its letters are never clipped.

**Acceptance criteria**
- e2e (also on a CI runner without condensed fonts): the logo is not wider than the screen.

*Sources: D-016, D-017.*

### UI-LOOK-14 — Gentle motion · SHOULD

Hints pulse slowly (`hint_pulse_period`), the logo glows (UI-LOOK-12), a new screen fades in
([screen-flow.md](screen-flow.md)) and a locked level shakes ([level-select.md](level-select.md)).
Under the system's "reduce motion" setting, the logo's glow and the hints' pulse stop.

**Acceptance criteria**
- Given `prefers-reduced-motion: reduce`, then the logo and the hints are not animated.

*Sources: D-013, D-103.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| Logical resolution | 1280 × 720 | `src/game/config/game.py` `GAME_CONFIG.screen` (GD-02, D-249) |
| `menu_column` | 560 px, within the 540 px window since D-319 | `index.html` `--menu-column` (UI-LOOK-02, D-249) |
| Menu window | the playfield window, 540 × 720 at x = 370 | `index.html` `#menu:not(.phone)::before`, `.menu-screen`; `src/app/menu_scenes.py` `window_camera` (D-319) |
| `phone_scale` | 0.5 CSS px per logical px | `src/ui/stage_fit.py` `PHONE_SCALE`; `index.html` `#menu.phone` (UI-LOOK-02, D-286) |
| `--neon` | `#00e8ff` | `index.html` `:root` |
| `--accent` | `#3dff9a` | `index.html` `:root` |
| `--deep` | `#0a5cff` | `index.html` `:root` |
| `--red` | `#ff2244` | `index.html` `:root`, danger only |
| Bombs orange | `#ff8a1e` | `index.html` (`.hud-bombs`, `.hud-bomb-button`) |
| `--glass` | `rgba(2, 14, 22, 0.8)` | `index.html` `:root` |
| `--black` / `--letterbox` | `#010a10` / `#000407` | `index.html` `:root` |
| `--neon-line` | `#0a5cff → #00b4ff → #00e8ff → #3dff9a → #b4ff4a` | `index.html` `:root` |
| `--chrome` | `#ffffff → #d4fbff → #0b3a5a (50 %) → #4ff0ff → #e4fff4` | `index.html` `:root`, the logo |
| `--cut` | 14 px | `index.html`, panel chamfer |
| `title_logo_size` | 46 px | `index.html` `.title-name`; lowered by `src/ui/shrink_to_fit.py` down to 12 px at most |
| `title_glow_period` | 3.5 s | `index.html` `@keyframes title-glow` |
| `hint_pulse_period` | 2.4 s | `index.html` `@keyframes hint-pulse` |

## Notes

- History of the look: a synthwave sun and grid with a dark background (D-012), then a cyberpunk
  HUD in acid yellow, cyan and red with corner brackets, scanlines and glitches over a night city
  (D-013, D-014), then the scanlines removed (D-040), then darksynth magenta, violet and blood red
  with a chrome logo over a striped sun (D-103), then the sun removed (D-104), and now neon
  blue/green (D-198). `02-game-design.md` GD-60 still said "darksynth" for the menus and the HUD
  when D-198 was made at the reviewer's request; the 3D art direction is in
  [graphics/art-direction.md](../graphics/art-direction.md).
- From the cyberpunk and darksynth looks, these stay: the chamfered glass panels, the monospace
  readouts, the segmented loading bar, the hazard-striped locked cells, the chrome logo, the neon
  frame and bottom line, the pulsing hints and the light selected block with black text.
- D-249 (2026-11-02): the screen is 16:9. The menus were laid out for the 3:4 screen and only
  got a centre column; on a 390 × 844 phone the stage is now 390 × 219 CSS px. The phone layout
  (D-286) lays the menus out across the window there, so the UI-INPUT-11 touch targets hold.
