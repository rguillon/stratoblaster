# Boot and loading

> **Area:** UI · **Prefix:** `UI-LOAD` · **Related:** [screen-flow.md](screen-flow.md), [title-screen.md](title-screen.md), [look-and-layout.md](look-and-layout.md), [../performance.md](../performance.md), [../01-engineering.md](../01-engineering.md)

What the player sees from opening the page until the title screen, and while a level loads: the
WebGL2 check and its message, the loading screen with its real progress bar, the loading screen of
a level, and the message shown when the graphics context is lost. How fast the loading is, and how
the work is split into steps, is in [performance.md](../performance.md).

## Requirements

### UI-LOAD-01 — WebGL2 is checked first · MUST

Before anything else is built, the page checks that the browser can create a WebGL2 context
(ENG-06). Without WebGL2, the friendly message of UI-LOAD-02 is shown instead of the menu, nothing
else starts, and no error is thrown or logged.

**Acceptance criteria**
- Given a browser without WebGL2 (e2e: `getContext('webgl2')` returns null), when the page loads, then the message is visible, no menu screen exists, and the console shows no error.
- Given creating the test canvas throws, then the check reads as "no WebGL2" (unit test).

*Sources: P01-R03, ENG-06.*

### UI-LOAD-02 — A message a parent understands · MUST

The "not supported" message is short and plain, understandable by a kid's parent: the game cannot
run in this browser or on this device, and which browsers to try. It comes from the game's texts
(`unsupported`): "Sorry! This game cannot run in this browser or on this device. Please try a
recent version of Chrome, Edge, Firefox or Safari on a computer." It is centred on the whole page,
in large text (22 px) on the dark background.

**Acceptance criteria**
- Given no WebGL2, then the page shows a text containing "cannot run in this browser or on this device".

*Sources: P01-R03.*

### UI-LOAD-03 — A loading screen with real progress · MUST

While the menus' 3D scenes are prepared, a loading screen shows a progress bar that goes from 0 %
to 100 % with the real work (ENG-108). The work is a list of steps, and the bar moves after each
one: build the title backdrop, build the ship select stage, wait until each of the two scenes has
compiled its shaders, then draw each ship highlighted once (so the first highlight on the ship
select screen does not stall). The browser paints between two steps, so the bar visibly moves. It
never goes back.

**Acceptance criteria**
- Given a page load, then a progress bar going from 0 % to 100 % is visible before the title screen, with more than two values, in increasing order (e2e).

*Sources: P01-R02, ENG-108, D-008, D-118.*

### UI-LOAD-04 — The title follows by itself · MUST

When the last loading step is done, the title screen appears without any user action.

**Acceptance criteria**
- Given a page load, when loading completes, then the title screen shows with no key, click or tap.

*Sources: P01-R02.*

### UI-LOAD-05 — The loading screen's look · SHOULD

The loading screen shows, centred: the game's "Loading…" text (30 px, italic, uppercase, in a cyan
glow), a 320 × 24 px gauge with a cyan border filled by the blue-to-green neon line cut into
segments like a power gauge, and the percent under it in green monospace. Its background is a faint
cyan grid floor under a deep blue horizon glow. It does not fade in.

**Acceptance criteria**
- Manual check: the loading screen matches this description in the neon blue/green look ([look-and-layout.md](look-and-layout.md)).
- The gauge is a `progressbar` with its value from 0 to 100 (unit test).

*Sources: P01-R13, D-013, D-198.*

### UI-LOAD-06 — The loading screen of a level · MUST

When a confirmed level (or a Continue) needs loading, the game screen shows at once and the same
loading screen is drawn over it, with the real progress of the level's loading steps. It fades in
only after `loading_screen_after_ms`, so a quick load does not flash it. It is updated in place as
the steps run (it does not fade in again), and it is removed when the level's last step is done. A
level that was built ahead on the level select screen and starts at once shows no loading screen
([performance.md](../performance.md)).

**Acceptance criteria**
- Given a level that takes longer than `loading_screen_after_ms` to load, then the loading screen shows over the game screen and its bar moves with each step.
- Given a later progress value, then the same loading screen element is updated, not a new one (unit test).
- Given the level is ready, then the loading screen is gone.

*Sources: P13-R03, ENG-108, D-115.*

### UI-LOAD-07 — Graphics context lost · MUST

If the WebGL context is lost while the game runs, a message covers the whole page: "The graphics
context was lost. Please reload the page." (ENG-110).

**Acceptance criteria**
- Given a running game, when the WebGL context is lost, then the message shows over the game.

**Discrepancy:** ENG-110 asks to "show a message and offer a reload"; the message only asks the
player to reload the page: there is no reload button.

*Sources: ENG-110.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| Boot loading steps | 5 | `src/app/menu_scenes.py` `prepare_menu_scenes` (backdrop, ships, wait for each scene, highlight each ship) |
| `loading_screen_after_ms` | 300 ms | `index.html` `.level-loading` (animation delay 0.3 s, then a 0.15 s fade) |
| Loading gauge | 320 × 24 px | `index.html` `.loading-bar` |
| Loading text | "Loading…" | `src/game/config/menu_texts.py` `MENU_TEXTS["loading"]` |
| Unsupported text | see UI-LOAD-02 | `MENU_TEXTS["unsupported"]` |

## Notes

- The context-lost text is written in `src/main.py`, not in the game's texts: it is not specific
  to this game.
