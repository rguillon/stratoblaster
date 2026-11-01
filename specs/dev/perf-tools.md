# Perf tools

> **Area:** Dev · **Prefix:** `DEV-PERF` · **Related:** [../performance.md](../performance.md), [test-api.md](test-api.md), [debug-options.md](debug-options.md), [dev-menu.md](dev-menu.md), [../01-engineering.md](../01-engineering.md)

The tools that measure how fast the game runs: the perf monitor, which times every frame and every
level loading; the F3 perf overlay, which shows its numbers; the FPS / polygons tile of a level; and
the scripts and tests that measure the game. They serve [../performance.md](../performance.md):
they are developer tools, never part of what the player is meant to see (the tile is shown only on
request). The same numbers are readable through the e2e test API ([test-api.md](test-api.md)).

## Requirements

### DEV-PERF-01 — The perf monitor · MUST

The app times the work of each frame (its simulation and its drawing) with the page's clock
(`performance.now`), and keeps:
- the number of **long frames**, those longer than `long_frame_ms` (PERF-01);
- the **longest frame**;
- the number of **frames** counted;
- the **last level loading time**: from the frame the level was confirmed in to the level's first
  drawn frame;
- the **longest loading step**: the longest frame of that loading.

**Acceptance criteria**
- Given frames of 10, 60 and 30 ms, then 3 frames are counted, 1 long, and the longest is 60 ms.
- Given a level loaded, then its loading time and its longest step are recorded.

*Sources: P13-R01, D-113.*

### DEV-PERF-02 — What the monitor counts · MUST

While a level loads, its frames count as loading steps, not as frames. When the level's first frame
is drawn, the loading time is recorded and the frame counts start again, skipping the next second
of frames (`simulation_hz` frames), so the first second of a level is not counted (PERF-19). The
last loading time stays until the next level is loaded.

**Acceptance criteria**
- Given a level that has just loaded, when its first `simulation_hz` frames run, then none of them
  is counted.
- Given a reset of the counts, then the last loading time is kept.

*Sources: P13-R01, P13-R03, P13-R04.*

### DEV-PERF-03 — The F3 perf overlay · MUST

F3 shows or hides a perf overlay in the top-left corner of the window, with three lines:
`Long frames: <n>`, `Longest frame: <t> ms` and `Level load: <t> ms` (a dash before any level has
loaded). It is hidden when the page opens. Its text changes at most every `overlay_refresh`, so the
numbers stay readable. It exists in dev and e2e builds only, never in the production build. No
automated check needs it: the test API gives the same numbers (DEV-API-06).

There is no separate dev build since the Python port (`DEV_BUILD` is off in `main.py` until the
build is split, D-175), so today the overlay is in the e2e build only (`make e2e-build`, served from
`dist-e2e/`).

**Acceptance criteria**
- e2e: given the game page, then the overlay is hidden; when F3 is pressed, then it shows
  `Long frames:`, `Longest frame:` and `Level load:`; when F3 is pressed again, then it hides.
- Given a production build, then F3 shows nothing.

*Sources: P13-R01, P14-R08, D-113, D-175, ENG-111.*

### DEV-PERF-04 — The FPS / polygons tile · MUST

A small tile in the top-right corner of the window shows two lines: `FPS: <n>`, the frames per
second over the last `fps_window`, and `Polygons: <n>`, the triangles drawn in the last frame (thin
instances included), with thousands separators (`Polygons: 264,512`). Its text changes at most every
`tile_refresh`. It takes no input (clicks go through it). In e2e builds, which have no render loop,
its FPS is the frames per simulated second.

**Acceptance criteria**
- e2e: given `?level=1-3&t=120`, when 60 frames are stepped, then the tile reads `FPS: <n>` and
  `Polygons: <n>`, both above 0.

*Sources: P06-R09, D-212, D-093.*

### DEV-PERF-05 — When the tile shows · MUST

In a level, the tile shows in debug mode (the URL debug options,
[debug-options.md](debug-options.md)). F2 shows or hides it in any level, with or without debug
mode, in every build. The F2 choice holds from level to level for the rest of the session (until the
page is reloaded); until F2 is first pressed, the tile follows debug mode. The tile belongs to the
level: it is not shown in the menus or the dev viewers, nor while a level is being built ahead.
F2 does nothing while the game is paused.

**Acceptance criteria**
- Given a level started without debug options, then no tile shows; when F2 is pressed, then it shows,
  and the next level shows it too.
- Given a level started in debug mode, then the tile shows; when F2 is pressed, then it hides.

*Sources: P06-R09, D-039, D-212.*

### DEV-PERF-06 — A script measures the game · SHOULD

A script drives the e2e build in Chromium (with the machine's GPU when asked, so it can run on the
reference machine) and measures, for every level or the levels it is given:
- the menu presses (the press and the frame after it);
- each level's loading time and its longest step;
- the long frames and the longest frame over a full run, or its first `measure_run_s` seconds, the
  first second not counted.

It can measure another build from its URL, so the numbers before and after a change can be
compared (PERF-02).

**Gap:** not implemented. Phase 13's `scripts/measure-perf.mjs` was removed with the TypeScript
setup (D-187, D-189), and nothing replaces it.

*Sources: P13-R01, D-113.*

### DEV-PERF-07 — A perf smoke test for each world · MUST

An e2e test starts the first level of each world (1-1, 2-1, 3-1, 4-1) from the level select and
checks, through the test API, that its loading time and its longest step are recorded, and that the
loading time is under `level_load_max_s` × `e2e_slowdown` (PERF-08).

**Acceptance criteria**
- Given `make e2e`, then the test passes for the four worlds.

*Sources: P13-R03.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `long_frame_ms` | 50 | See [../performance.md](../performance.md). `src/config/engine.py` `ENGINE_CONFIG.long_frame_ms` |
| `simulation_hz` | 60 | Frames skipped after a level loads (its first second). `ENGINE_CONFIG.simulation_hz` |
| overlay key | F3 | `src/config/engine.py` `ENGINE_CONFIG.perf_overlay.key` |
| `overlay_refresh` | 0.25 s | `ENGINE_CONFIG.perf_overlay.refresh` |
| tile key | F2 | `src/config/game_play.py` `GAME_PLAY_CONFIG.stats.key` |
| `fps_window` | 0.5 s | `GAME_PLAY_CONFIG.stats.fps_window` |
| `tile_refresh` | 0.25 s | `GAME_PLAY_CONFIG.stats.refresh` |
| `measure_run_s` | 120 | Run length measured per level when a full run is longer (no script today) |
| `level_load_max_s`, `e2e_slowdown` | 2, 10 | See [../performance.md](../performance.md). `tests/e2e/test_perf.py` |

## Notes

- ENG-111 also asks the debug overlay for the frame time, the draw calls, the active entities and
  particles, and a Babylon inspector on F4; none of these exist today.
- Phase 13's before / after measurements (software WebGL) and the script's options (`--gpu`,
  `--seconds`, `--levels`, `--url`, `--render-every`, `--warm`) are recorded in
  `specs_old/phases/phase-13-perf.md`.
