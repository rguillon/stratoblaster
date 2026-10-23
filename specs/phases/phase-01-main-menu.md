# Phase 01 — Main Menu

> Copy this file to `phase-NN-short-name.md` (e.g. `phase-03-enemies.md`).
> Fill the **Human** sections. Set **Status** to `Ready` when the agent may implement it.
> The agent fills the **Agent** sections and never edits the requirement sections.

**Status:** Ready  <!-- Draft | Ready -->
**Depends on:** Phase 2 (the ship select screen shows the player ships)

---

## 🧑 Goal

When the player opens the game, they see a loading screen, then a cyberpunk title screen. From there they go through the menu flow of `02-game-design.md` §7: **Title → Select Ship → Select Level → Game**, and can go back at each step.

All the menus can be used with the keyboard, a gamepad, or touch/mouse. Gameplay does not exist yet: confirming a level opens a placeholder game screen that shows what was chosen.

## 🧑 Requirements

> ID format `P01-Rxx`. Priority: **MUST** / **SHOULD** / **MAY**.
> Write each requirement so it is testable. Add acceptance criteria when "done" isn't obvious.

### P01-R01 — Screen state machine  · MUST
The app has a screen state machine in `app/` with these screens: `loading`, `title`, `ship-select`, `level-select`, `game` (placeholder). Transitions follow `02-game-design.md` §7, plus a **Back** action on each menu screen:

```
loading ──done──▶ title ──start──▶ ship-select ──confirm──▶ level-select ──confirm──▶ game
                    ▲                  │                        │                       │
                    └──────back────────┘ ◀────────back──────────┘                       │
                    ▲                                                                   │
                    └─────────────────────────────back──────────────────────────────────┘
```

The state machine logic is pure (no Babylon, no DOM) and fully unit-tested. Pause and Game Over are not part of this phase.

**Acceptance criteria**
- [ ] Given the `title` screen, when Start is confirmed, then the screen is `ship-select`.
- [ ] Given `ship-select`, when Back is pressed, then the screen is `title`.
- [ ] Given `level-select`, when Back is pressed, then the screen is `ship-select` with the previously chosen ship still selected.
- [ ] Given `game`, when Back (Esc) is pressed, then the screen is `title`.
- [ ] Invalid transitions (e.g. `title` → `game`) are rejected and leave the state unchanged.

### P01-R02 — Loading screen  · MUST
A loading screen with a real progress bar is shown while the title screen's assets and procedural content are prepared (ENG-108). It switches to the title screen automatically when loading completes.

**Acceptance criteria**
- [ ] Given a page load, then a progress bar going from 0 % to 100 % is visible before the title screen.
- [ ] When loading completes, the title screen appears without any user action.

### P01-R03 — WebGL2 check  · MUST
If WebGL2 is not available, the game shows a clear, friendly message (understandable by a kid's parent) instead of the menu, and does not throw errors (ENG-06).

**Acceptance criteria**
- [ ] Given a browser without WebGL2, when the page loads, then a message explains that the browser or device is not supported and no console error is thrown.

### P01-R04 — Title screen  · MUST
The title screen shows:
- the game title (text defined in `src/game/`, ENG-144),
- a **Start** entry, selected by default,
- the **high score** read from the cookie (GD-51); `0` when there is no cookie yet,
- the version and short commit hash, small, in a corner (ENG-83),
- a short controls hint (e.g. "Press Space / Enter or tap to start").

**Acceptance criteria**
- [ ] Given no high-score cookie, then the title screen shows a high score of `0`.
- [ ] Given a high-score cookie with value `12345`, then the title screen shows `12345`.
- [ ] Given a corrupted cookie value, then the title screen shows `0` and no error is thrown.
- [ ] The version string matches `package.json` and the commit hash is injected at build time.

### P01-R05 — Title screen 3D background  · SHOULD
Behind the menu, a 3D scene generated in code in a dark cyberpunk style (GD-60), not synthwave: for example a night city with lit windows, neon signs and haze scrolling by, and the balanced player ship (phase 2) flying slowly. It loops forever and keeps 60 FPS (ENG-101).

**Acceptance criteria**
- [ ] The background is animated and generated in code (no downloaded model or texture).
- [ ] The title screen keeps 60 FPS on the reference hardware (checked with the F3 overlay when it exists, or the browser performance tools).

### P01-R06 — Ship select screen  · MUST
Shows the 3 player ships from phase 2, rotating, with their name, speed and health (reusing `ModelShowcase` and the ship captions where it makes sense). One ship is highlighted; the player changes the selection with Left/Right and confirms it. The balanced ship is selected by default.

**Acceptance criteria**
- [ ] Given `ship-select` is opened for the first time, then the balanced ship is highlighted.
- [ ] Given the balanced ship is highlighted, when Right is pressed, then the next ship is highlighted (selection wraps around at the ends).
- [ ] When Confirm is pressed, then the highlighted ship is stored as the chosen ship and the screen is `level-select`.
- [ ] The highlighted ship is clearly visible (e.g. scaled up, glowing frame or spotlight) and the others are dimmed.

### P01-R07 — Level select screen  · MUST
Shows the levels as a grid of **5 worlds × 5 levels** (vision: first release). Only **World 1 – Level 1** is unlocked in this phase; the other levels are shown locked (padlock icon, greyed out) and cannot be confirmed. The player moves the selection with the arrows and confirms an unlocked level.

**Acceptance criteria**
- [ ] The grid shows 25 entries labelled `1-1` … `5-5`.
- [ ] Given `level-select` is opened, then `1-1` is highlighted.
- [ ] When the selection is moved to a locked level and Confirm is pressed, then nothing happens except a "locked" feedback (e.g. a short shake).
- [ ] When `1-1` is confirmed, then the screen is `game`.
- [ ] Which levels exist and which are unlocked come from `src/game/` data, not from engine code (ENG-142/144).

### P01-R08 — Placeholder game screen  · MUST
The `game` screen is a placeholder until gameplay phases exist: it shows the chosen ship and level (e.g. "Balanced ship — Level 1-1 — Gameplay coming soon") and how to go back to the title screen.

**Acceptance criteria**
- [ ] Given the player chose the heavy ship and level `1-1`, then the placeholder shows both.
- [ ] When Back is pressed, then the screen is `title`.

### P01-R09 — Menu navigation with keyboard  · MUST
Menus are navigated with the keyboard, using physical key positions so it works on QWERTY and AZERTY (`KeyboardEvent.code`, as in the controls table of `02-game-design.md` §2):

| Menu action | Keys |
|-------------|------|
| Move selection | Arrows / WASD (positions) |
| Confirm | Enter, Space |
| Back | Esc, Backspace |

Holding a direction repeats the move after a short delay (see Tunable values).

**Acceptance criteria**
- [ ] On an AZERTY layout, the keys in the WASD positions (Z, Q, S, D) move the selection.
- [ ] Holding Right in `ship-select` moves the selection once, then repeats after the repeat delay.

### P01-R10 — Menu navigation with a gamepad  · MUST
Menus can be navigated with a standard gamepad (Gamepad API, standard mapping): left stick or D-pad to move, **A** (bottom button) to confirm, **B** (right button) to go back. The stick uses a dead zone.

**Acceptance criteria**
- [ ] With a gamepad connected, the whole flow Title → Ship select → Level select → Game → Title can be done with the gamepad only.
- [ ] A stick tilt inside the dead zone does not move the selection.

### P01-R11 — Menu navigation with touch / mouse  · MUST
Every menu entry can be tapped or clicked. Tapping a non-selected entry selects it; tapping the selected entry confirms it. Each menu screen (except the title) has a visible on-screen **Back** button. Touch targets are at least 44×44 CSS px (mobile port, vision).

**Acceptance criteria**
- [ ] The whole flow can be done with the mouse only.
- [ ] On a touch screen (or Playwright touch emulation), the whole flow can be done with taps only.

### P01-R12 — Unified menu input  · MUST
Keyboard, gamepad and touch are translated by `input/` into the same abstract menu actions (`up`, `down`, `left`, `right`, `confirm`, `back`). Menu screens only react to these actions, never to raw keys or buttons. The mapping lives in config so it can be remapped later (ENG-112).

**Acceptance criteria**
- [ ] Unit tests show that Enter, Space, gamepad A and a tap on the selected entry all produce `confirm`.

### P01-R13 — Layout, scaling and look  · MUST
- Menus are an HTML/CSS overlay (`ui/`) laid out on the **480×640 logical resolution**, scaled to fit the window while keeping its aspect ratio (GD-02, GD-03), and they follow window resizes (ENG-110).
- Cyberpunk look (GD-60), not synthwave: a dark techno HUD with neon accents and a glow on the selected entry.
- Accessible to kids (vision): large readable font, short words, the selected entry is obvious without relying on colour alone (e.g. arrow marker or frame plus colour).
- Fonts are system fonts or a font bundled with the build (no font loaded from a third-party server at runtime, so the game works offline once loaded).

**Acceptance criteria**
- [ ] At window sizes 800×600, 1920×1080 and 390×844 (portrait phone), the menu is fully visible, not cropped, not stretched.
- [ ] The selected entry stays identifiable in a greyscale screenshot.

### P01-R14 — Remember the last ship  · MAY
The last chosen ship is saved in a cookie and pre-selected the next time `ship-select` opens.

**Acceptance criteria**
- [ ] Given the player chose the light ship and reloads the page, when `ship-select` opens, then the light ship is highlighted.

### P01-R15 — Screen transitions  · MAY
Short transitions between screens (fade or slide, ≤ 300 ms). Input is ignored during a transition so a key press cannot skip two screens.

## 🧑 Tunable values
<!-- Numbers you want to be able to tweak later. The agent puts them in config. -->
| Name | Value | Notes |
|------|-------|-------|
| `menu_repeat_delay` | 350 ms | Hold time before a held direction starts repeating |
| `menu_repeat_interval` | 120 ms | Time between repeats while held |
| `gamepad_dead_zone` | 0.35 | Stick magnitude below which input is ignored |
| `menu_transition_duration` | 250 ms | P01-R15 |
| `title_ship_rotation_speed` | 0.3 rad/s | Title background ship (P01-R05) |
| `title_city_scroll_speed` | 8 units/s | Night city scrolling by (P01-R05) |
| `ship_select_rotation_speed` | 0.5 rad/s | Rotating ships on the ship select screen |
| `cookie_max_age` | 365 days | High score and last ship cookies |
| `worlds` × `levels_per_world` | 5 × 5 | Level select grid (game data, `src/game/`) |

## 🧑 Out of scope for this phase
<!-- Things that might seem related but must NOT be done now. -->
- Gameplay: ship movement, shooting, enemies, scrolling level. The `game` screen is a placeholder.
- Pause overlay, Game Over screen and saving a new high score (only *reading* the cookie is in scope).
- Level unlocking and progress saving (only `1-1` is unlocked, hard-coded in game data).
- Options / settings screen: quality presets (ENG-102), volume sliders and accessibility options (ENG-112).
- Music and sound effects (GD-70, GD-71), including menu sounds.
- Weapon selection.

## 🧑 Engineering additions for this phase
<!-- Optional: phase-specific technical requirements beyond 01-engineering.md (e.g. "add e2e smoke test", "raise coverage to 85%"). -->
- Implement the test API `window.__GAME_TEST__` (ENG-52) in `e2e` mode, at least with `getState()` returning the current screen, the selected entry, the chosen ship and the chosen level, and `sendAction(action)` accepting the menu actions of P01-R12.
- Implement the first part of the ENG-54 smoke suite: page loads → loading completes → title screen visible → start → ship select → level select → placeholder game screen → back to title.
- e2e tests for the navigation by keyboard (including an AZERTY-position check), mouse and touch emulation, named with their requirement IDs (ENG-55). Gamepad navigation can be unit-tested with a fake `navigator.getGamepads()`.
- An e2e or build test checks that `__GAME_TEST__` is absent from the production bundle (ENG-52).
- The cookie code goes in `platform/` (or another engine layer) behind a small storage interface, so `core/` stays pure and tests can use an in-memory fake.
- The `player_ship/` viewer page from phase 2 keeps working.

## 🧑 Manual validation checklist
<!-- What YOU will check in the browser before validating. The agent should make these easy to check. -->
- [ ] Runs on GitHub Pages / `make dev` without console errors
- [ ] A loading bar is visible, then the title screen appears by itself
- [ ] The title screen shows the title, Start, high score `0`, version + commit hash, and an animated cyberpunk background
- [ ] Set a cookie by hand (browser dev tools) and check that the high score on the title screen shows it
- [ ] Keyboard: go through Title → Ship select → Level select → placeholder → Title with arrows, Enter/Space and Esc
- [ ] Keyboard on AZERTY: Z/Q/S/D move the selection
- [ ] Gamepad: same flow with the stick / D-pad, A and B
- [ ] Mouse / touch (or phone emulation in dev tools): same flow with clicks / taps and the Back button
- [ ] Ship select: the 3 ships rotate, the highlighted one is obvious, stats are shown
- [ ] Level select: 25 levels, only 1-1 can be chosen, locked levels give feedback
- [ ] Resize the window (and try a portrait phone size): the menu stays fully visible and keeps its proportions
- [ ] `player_ship/` still works

## 🧑 Notes, references, sketches
<!-- Links, images, pseudo-code, example level layouts... -->
- Flow source: `02-game-design.md` §7. Controls source: `02-game-design.md` §2.
- Style references: cyberpunk game HUDs and neon night cities (lit skyscrapers, neon signs, haze), kept readable for kids.
- Rough title layout (480×640 logical):

```
┌──────────────────────────┐
│        HIGH SCORE        │
│          012345          │
│                          │
│      ╔═════════════╗     │
│      ║  GAME TITLE ║     │
│      ╚═════════════╝     │
│                          │
│        ▶  START  ◀       │
│                          │
│    ~ ship flying over ~  │
│    ~~ neon grid floor ~~ │
│  Space / Enter / tap     │
│                  v0.1.0  │
│                  abc1234 │
└──────────────────────────┘
```

---

## 🧑 Review feedback
> After the agent reports, write corrections here, then say **"Fix phase 01"**.
> The agent ticks each item when fixed.

- [x] Make the background dark (all menu screens). *Fixed: dark night palette for the sky, horizon/fog, floor, page and loading screen; sun and neon grid kept bright (D-012).*
- [x] Make the UI look more technological / cyberpunk. *Fixed: CSS-only HUD restyle in `index.html` (corner brackets, screen frame, scanlines, monospace readouts, glitched title, segmented loading bar, hazard-striped locked levels); selection markers unchanged (D-013).*
- [x] Remove the pastel background requirement; make the UI look cyberpunk, not synthwave. *Fixed: pastel removed from GD-61, P01-R05, P01-R13 and the notes (at the reviewer's request). Backdrop rebuilt as a generated night city (street of dark towers with lit windows, neon blade signs and roof trims, distant skyline, haze, rain) in place of the sun and grid; overlay restyled in acid yellow / cyan / red with chamfered panels and a solid yellow selected entry; yellow selection ring (D-014).*

---

## 🤖 Implementation report
> Filled by the agent. Do not edit (comment in Review feedback instead).

### Questions / blockers
None blocking. One conflict was settled by the specs themselves: ENG-07 says `localStorage`, while the vision, GD-51 and P01-R04/R14 say cookies. Cookies are used (D-010).

### Plan
| Task | Requirement IDs |
|------|-----------------|
| Pure screen state machine `MenuFlow` (`app/`), transition table and grid cursor (`core/menu/`) | P01-R01, R06, R07, R15 |
| `input/`: `MenuAction`, keyboard by `code` with hold-repeat, gamepad polling with dead zone, tap → command; bindings in `config/menu-input.ts` | P01-R09, R10, R11, R12 |
| `platform/` cookie storage behind `KeyValueStorage`; high score / last ship read & write (`app/saved-choices.ts`) | P01-R04, R14 |
| `GameDefinition` gets `screen`, `levels`, `texts`, `view.menuBackdrop`; game data in `src/game/` | P01-R04, R07, ENG-144 |
| Loading tasks with real progress; 2 menu scenes built and compiled behind the loading screen | P01-R02 |
| WebGL2 check with a friendly message from the game texts | P01-R03 |
| HTML/CSS overlay (`ui/`): loading, title, ship select, level select, placeholder; 480×640 stage fitted to the window | P01-R04, R06, R07, R08, R11, R13, R15 |
| Cyberpunk city backdrop (`src/game/view/title-backdrop.ts`, `city-geometry.ts`) and ship select stage (`render/ship-select-stage.ts`) | P01-R05, R06 |
| Test API `__GAME_TEST__` (e2e builds), `make build` leak check, e2e suites per device | ENG-52, ENG-54, ENG-55 |

### Requirement traceability
| ID | Status (Done / Partial / Not done) | Code | Tests | Notes |
|----|-----------------------------------|------|-------|-------|
| P01-R01 | Done | `src/app/menu-flow.ts`, `src/core/menu/menu-screen.ts` | `tests/unit/app/menu-flow.test.ts`, `tests/unit/core/menu/menu-screen.test.ts`, e2e `smoke.spec.ts` | Pure: no Babylon/DOM imports |
| P01-R02 | Done | `src/assets/loading-tasks.ts`, `src/app/menu-scenes.ts`, `src/ui/screens/loading-screen.ts` | `loading-tasks.test.ts`, `start-app.test.ts`, `menu-overlay.test.ts`, e2e `smoke.spec.ts` | 4 real steps: backdrop, ships, compile each scene's shaders |
| P01-R03 | Done | `src/main.ts`, `src/platform/webgl-support.ts`, `MENU_TEXTS.unsupported` | e2e `smoke.spec.ts` (WebGL2 disabled by an init script) | |
| P01-R04 | Done | `src/ui/screens/title-screen.ts`, `src/app/saved-choices.ts`, `src/platform/cookie-storage.ts` | `saved-choices.test.ts`, `cookie-storage.test.ts`, `menu-overlay.test.ts`, e2e `smoke.spec.ts` (0, 12345, corrupted, version) | Cookie `pewet_high_score` |
| P01-R05 | Done | `src/game/view/title-backdrop.ts`, `src/game/view/city-geometry.ts`, `src/game/config/title-look.ts`, `src/core/math/rng.ts`, `src/render/geometry/gradient-shapes.ts` | `title-backdrop.test.ts`, `city-geometry.test.ts`, `rng.test.ts`, `gradient-shapes.test.ts` | 60 FPS to be checked manually (no F3 overlay yet). Cyberpunk night city after review (D-012, D-014) |
| P01-R06 | Done | `src/render/ship-select-stage.ts`, `src/ui/screens/ship-select-screen.ts` | `ship-select-stage.test.ts`, `menu-flow.test.ts`, `menu-overlay.test.ts`, e2e | Reuses `ModelShowcase` and `shipCaption` |
| P01-R07 | Done | `src/core/content/level-catalog.ts`, `src/game/sim/levels.ts`, `src/game/config/levels.ts`, `src/ui/screens/level-select-screen.ts` | `level-catalog.test.ts`, `levels.test.ts`, `menu-flow.test.ts`, `menu-controller.test.ts`, e2e `menu-pointer.spec.ts` | Locked feedback: shake + "Locked!" |
| P01-R08 | Done | `src/ui/screens/game-placeholder-screen.ts`, `src/app/menu-view-builder.ts` | `menu-view-builder.test.ts`, `menu-flow.test.ts`, e2e | |
| P01-R09 | Done | `src/input/keyboard-menu-input.ts`, `src/input/hold-repeater.ts`, `src/config/menu-input.ts` | `keyboard-menu-input.test.ts`, `hold-repeater.test.ts`, e2e `menu-keyboard.spec.ts` (incl. AZERTY positions, hold) | |
| P01-R10 | Done | `src/input/gamepad-menu-input.ts` | `gamepad-menu-input.test.ts`, e2e `menu-gamepad.spec.ts` (fake `navigator.getGamepads()`) | |
| P01-R11 | Done | `src/ui/screens/elements.ts`, `src/input/pointer-menu-input.ts` | `menu-overlay.test.ts`, e2e `menu-pointer.spec.ts` (mouse, touch), `menu-layout.spec.ts` (≥ 44 px) | |
| P01-R12 | Done | `src/input/menu-action.ts`, `menu-input.ts`, `src/config/menu-input.ts` | `menu-input.test.ts` (Enter, Space, A, tap → confirm) | |
| P01-R13 | Done | `src/ui/stage-fit.ts`, `index.html` styles (cyberpunk HUD after review, D-013) | `stage-fit.test.ts`, e2e `menu-layout.spec.ts` (3 sizes, resize, markers), `smoke.spec.ts` (same-origin only) | Greyscale: ▶ ◀ / ▲ markers, white frame, dashed outline |
| P01-R14 | Done (MAY) | `src/app/saved-choices.ts`, `src/app/menu-controller.ts` | `saved-choices.test.ts`, `menu-controller.test.ts`, `menu-flow.test.ts`, e2e `menu-pointer.spec.ts` | Cookie `pewet_last_ship` |
| P01-R15 | Done (MAY) | `MenuFlow` transition timer, `.menu-enter` fade in `ui/menu-overlay.ts` | `menu-flow.test.ts`, `menu-overlay.test.ts` | 250 ms fade-in |
| ENG-52 | Partial | `src/debug/test-api.ts`, `src/main.ts`, `Makefile` (`build`) | `test-api.test.ts`; leak check in `make build` | `getState`, `sendAction` only (as asked); `setSeed/step/pause` come with gameplay |
| ENG-54 | Partial | — | e2e `smoke.spec.ts` | Loading → title → ship → level → game → title; gameplay part comes later |

### Gate results
```
Light verification (2026-10-23): make typecheck ✔ / make build ✔ (ENG-52 leak check ✔) / make e2e ✔ 23 passed
After review fix "dark background" (2026-10-23): make typecheck ✔ / make build ✔ / make e2e ✔ 23 passed
After review fix "cyberpunk UI" (2026-10-23): make typecheck ✔ / make build ✔ / make e2e ✔ 23 passed
After review fix "cyberpunk, not synthwave" (2026-10-23): make typecheck ✔ / make build ✔ / make e2e ✔ 23 passed

Full gate, /validate-phase 1 (2026-10-23): make check ✔
  lint ✔ (after `prettier --write src/app/start-app.ts`)
  typecheck ✔
  unit tests ✔ 228 passed in 43 files (after fixing a wrong expected value in stage-fit.test.ts: top 97 → 162 = (844 − 520) / 2)
  coverage ✔ 99.21% statements / 96.53% branches / 98.97% functions / 99.61% lines
  build ✔ (ENG-52 leak check ✔)
  e2e ✔ 23 passed
Deferred to /validate-phase: lint, unit tests, coverage (not run during implementation)
```

### How to test manually
1. `make dev` and open http://localhost:5173/ (or `make preview` for the production build).
2. A loading bar fills up, then the title screen appears by itself: title, **▶ START ◀**, high score `0`, the hint, and `v0.0.0` + commit hash bottom right, over a cyberpunk night city (dark towers with lit windows and neon signs scrolling by, haze, rain, the balanced ship floating and turning). The logo is black on a yellow plate; the selected entry is a solid yellow block.
3. High score cookie: in dev tools (Application → Cookies), add `pewet_high_score` = `12345` and reload; try `abc` too (shows `0`).
4. Keyboard: Enter/Space to confirm, arrows or WASD to move, Esc/Backspace to go back. On AZERTY, Z/Q/S/D move. Hold an arrow on the level grid to see the repeat.
5. Gamepad: A confirm, B back, left stick or D-pad to move. A slight stick tilt does nothing.
6. Mouse/touch (or dev tools phone emulation): tap an entry to select it, tap it again to confirm; **◀ Back** at the top left.
7. Ship select: the 3 ships rotate; the selected one is bigger, lit, on a pink ring, and its card has a white frame and a ▲ marker. Choose Light, reload, go to ship select: Light is pre-selected (cookie `pewet_last_ship`).
8. Level select: 25 levels, only 1-1 can be played; a locked level shakes and shows "Locked!".
9. Resize the window or try a portrait phone size: the 3:4 stage stays fully visible, letterboxed.
10. http://localhost:5173/player_ship/ still shows the phase 2 viewer.
11. FPS (P01-R05): no F3 overlay yet; use the browser performance tools on the title screen.

### Deviations from spec
- ENG-07 (`localStorage`) vs cookies: cookies, as the vision, GD-51 and this phase ask (D-010).
- Tapping a non-selected entry produces a `{ select: index }` command in addition to the six actions of P01-R12, since none of them means "select this entry" (D-008).
- The default ship is the first ship of the roster, not a separate setting (D-008).

### Known limitations
- The cyberpunk look is checked by eye only (screenshots at 700×900, 800×900 and 390×844); e2e still checks the markers, outline and touch target sizes.
- 60 FPS (P01-R05) is not measured automatically; on ship select, two scenes with a glow layer each are drawn.
- No auto-pause on hidden tab and no WebGL context-loss recovery beyond the existing message (ENG-110, not asked by this phase).
- The test API has `getState` and `sendAction` only (ENG-52 `setSeed`, `step`, `pause` need gameplay).
- Ship stats on the cards show `Speed ×1 (100 px/s)` from the phase 2 caption; a bar or star display could be friendlier for kids.

### Suggestions for future phases
- Add the F3 debug overlay (ENG-111) to check P01-R05's 60 FPS.
- Menu sounds (GD-71) via the same `MenuFeedback` values (`moved`, `screen`, `locked`).
- Update ENG-07 to say cookies.
