# Phase 13 — Perf

> Fill the **Human** sections. Set **Status** to `Ready` when the agent may implement it.
> The agent fills the **Agent** sections and never edits the requirement sections.
> Drafted by the agent at the reviewer's request (2026-10-27) from three reported problems: lag of up to 1 s after some button presses, slow level loading, and repeated 1 s freezes during play in Worlds 3 and 4. Numbers are agent defaults; the reviewer may change any of them before setting the status to `Ready`.

**Status:** Ready  <!-- Draft | Ready -->
**Depends on:** Phase 12

---

## 🧑 Goal
The game feels instant: every button press gets visible feedback straight away, a level starts within a couple of seconds of being chosen, and play in every level (Worlds 3 and 4 included) runs without freezes or hitches. Nothing about the look, the content or the rules changes.

## 🧑 Requirements

> ID format `P13-Rxx`. Every requirement is **MUST** (no SHOULD / MAY).
> Write each requirement so it is testable. Add acceptance criteria when "done" isn't obvious.
> "Reference machine" means the ENG-101 target (mid-range laptop, integrated GPU of the Intel Iris Xe / Apple M1 class, 1080p, Chrome stable). Timings are measured on a production build (`make build` + preview), not `make dev`. Numbers are listed in **Tunable values**.
> This phase is about speed only: the scenery, models, effects, music, waves and difficulty of every level stay as they are (same look in screenshots, same simulation results).

### P13-R01 — Measure first  · MUST

Before any optimisation, the agent measures and records where the time goes, so every fix is backed by numbers:
- for each reported problem (button lag, level loading, World 3 / 4 freezes), the cause is found with the browser profiler and Babylon's instrumentation (for example shader compilation, synchronous scenery or terrain generation, garbage collection, texture uploads, material or mesh creation during play);
- a **long frame** is a frame whose time is above `long_frame_ms`. The game counts long frames, the longest frame, and the level loading time, and shows them in the debug overlay (ENG-111, dev and e2e builds only);
- the same numbers are readable from the e2e test API.

The before / after numbers for every level (1-1 to 4-5) and for the menu buttons go in the implementation report.

**Acceptance criteria**
- [ ] The implementation report has a table with, for each of the 20 levels, the loading time, the number of long frames over a full run (or the first `measure_run_s` seconds) and the longest frame, before and after this phase, on the reference machine.
- [ ] The report names the cause of each of the three reported problems.
- [ ] Given the debug overlay (F3), then it shows the long-frame count, the longest frame and the last level loading time.

### P13-R02 — Instant button feedback  · MUST

Every button and menu action reacts visibly within `input_feedback_ms` of the press (keyboard, gamepad and touch): the selection moves, the button shows its pressed state, or the next screen (or a loading screen, P13-R03) appears. This covers the title screen, ship select, level select, settings, the pause menu and its `Leave the level?` question, and the "Level complete" and "Game over" panels.

No heavy work (scene building, asset generation, music generation, shader compilation) runs between the press and its feedback; if an action needs heavy work, the feedback is shown first and the work follows.

**Acceptance criteria**
- [ ] Given any menu on the reference machine, when a button is pressed, then the visible reaction comes within `input_feedback_ms` (checked with the browser performance panel; listed per screen in the report).
- [ ] Given the pause menu during a World 4 level, when Resume, Settings or Main menu is confirmed, then the reaction comes within `input_feedback_ms`.
- [ ] No frame longer than `long_frame_ms` happens in the menus, except during a loading screen.

### P13-R03 — Fast level loading  · MUST

From confirming a level in the level select (or Retry / Next level) to the first playable frame takes at most `level_load_max_s` on the reference machine, for every level.

If loading takes more than `loading_screen_after_ms`, a loading screen with real progress shows (ENG-108) and its progress bar keeps moving (the page never looks frozen). Work that can be done once (shader compilation, shared materials, models, music) is done once and reused, not repeated for every level start or Retry.

**Acceptance criteria**
- [ ] Given each of the 20 levels on the reference machine, when it is confirmed, then it is playable within `level_load_max_s` (report table, P13-R01).
- [ ] Given a level that is retried, then the second start is no slower than the first.
- [ ] Given a level that takes longer than `loading_screen_after_ms` to load, then a loading screen shows and its progress bar moves with no single frozen step longer than `loading_step_max_ms`.
- [ ] An e2e test starts one level of each world and checks, through the test API, that the loading time is recorded and below `level_load_max_s` × `e2e_slowdown` (software WebGL is slower than the reference machine).

### P13-R04 — No freezes during play  · MUST

During play, no level has freezes: on the reference machine, after the first second of a level, no frame is longer than `freeze_ms`, and long frames (above `long_frame_ms`) are rare (at most `max_long_frames_per_min` per minute). This holds in every level and especially in Worlds 3 and 4, where repeated freezes of about one second happen today.

Things created while the level scrolls (terrain chunks, props, enemies, bosses, effects, weather) must not stall a frame: they are prepared ahead of time, spread over several frames, pooled or reused (ENG-104, ENG-105), and shaders are compiled before they are first needed (for example during loading), not when a new kind of object first appears.

**Acceptance criteria**
- [ ] Given each level of Worlds 3 and 4, played to the end (or boss) on the reference machine, then no frame is longer than `freeze_ms` after the first second (report table, P13-R01).
- [ ] Given each level of Worlds 1 and 2, then the same holds.
- [ ] Given any level, then long frames stay at or below `max_long_frames_per_min` per minute.
- [ ] Given the first appearance of each enemy kind, boss and effect in a level, then it causes no frame longer than `freeze_ms`.

### P13-R05 — Nothing else changes  · MUST

The optimisations do not change the game: the same scenery, models, effects, music and sounds; the same waves, enemy counts, timing and difficulty; the same scores. Frame rate targets (ENG-101) and budgets (ENG-104..ENG-107) still hold.

**Acceptance criteria**
- [ ] Existing e2e screenshot checks still pass for every world.
- [ ] Given the same inputs and seed, then the simulation produces the same results before and after (existing unit tests unchanged and green).
- [ ] The initial JS bundle stays within ENG-107.

## 🧑 Tunable values
| Name | Value | Notes |
|------|-------|-------|
| long_frame_ms | 50 | A frame longer than this counts as a long frame (3 frames at 60 FPS) |
| freeze_ms | 100 | No frame may exceed this during play (after the first second) |
| max_long_frames_per_min | 3 | Per minute of play, per level |
| input_feedback_ms | 100 | Press to visible reaction |
| level_load_max_s | 2 | Confirm to first playable frame, reference machine |
| loading_screen_after_ms | 300 | Show the loading screen if loading takes longer |
| loading_step_max_ms | 200 | Longest single frozen step while the loading screen shows |
| measure_run_s | 120 | Run length measured per level when a full run is longer |
| e2e_slowdown | 10 | Factor applied to time limits in e2e (software WebGL) |

## 🧑 Out of scope for this phase
- Quality presets or graphics settings (ENG-102 was removed).
- Any change to the look, content, difficulty or rules of a level.
- New levels, enemies, bosses, music or sounds.
- Mobile-specific performance tuning beyond what the fixes give for free.

## 🧑 Engineering additions for this phase
- Long-frame counter, longest frame and level loading time in the debug overlay and the e2e test API (P13-R01).
- An e2e perf smoke test per world (P13-R03), with limits scaled by `e2e_slowdown`.
- Every non-trivial optimisation (precompilation, chunk generation spread over frames, pooling, caching) is logged in `DECISIONS.md`.

## 🧑 Manual validation checklist
- [ ] Runs on GitHub Pages / `make dev` without console errors
- [ ] Menu buttons (title, ship select, level select, settings, pause menu) react straight away
- [ ] Each world's first and last level start in about 2 s or less, with a moving progress bar if there is a wait
- [ ] Levels 3-1 to 3-5 and 4-1 to 4-5 play to the boss without any visible freeze
- [ ] F3 overlay shows long frames, longest frame and loading time; the numbers match the report
- [ ] The levels look and play exactly as before

## 🧑 Notes, references, sketches
- Reported by the reviewer (2026-10-27): "<1 s lag when some buttons are clicked", "level loading time is so slow", "Worlds 3 and 4 have repeated 1 s lag during gameplay".
- Known leads (from `.planning/codebase/CONCERNS.md`, to be confirmed by P13-R01): level scenery is built synchronously on start, and terrain chunks and props are generated during scroll (`src/app/level-scene.ts`, `src/render/scenery/scenery-stage.ts`, `src/render/scenery/terrain-chunks.ts`); the phase 4 and 6 reports already note a freeze after Confirm and a hitch while scrolling.
- Frame rate has so far only been checked under software WebGL (about 10–27 FPS); this phase needs real-GPU measurements on the reference machine.

---

## 🧑 Review feedback
> After the agent reports, write corrections here, then say **"Fix phase 13"**.
> The agent ticks each item when fixed.

- [x] (2026-10-27, reviewer in chat) "there is still a lag when we select the second or third ship". Fixed: each ship has its own key light, so highlighting another ship only switches lights on and off and no shader is recompiled (D-116). First press 186 → 6 ms.
- [x] (2026-10-27, reviewer in chat) "the level loading is too long, is it not possible to start instantly and do the rest of the loading in background?" Fixed: the level highlighted on the level select is prepared in a worker while the player chooses (ground and textures). Enemy models are built during play, one per frame, instead of during loading (D-117). Load after the highlight rests on a level: 3.7–4 s → 0.44–0.51 s.
- [x] (2026-10-27, reviewer in chat, second time) "there is still a lag when we select the second or third ship" (a whole-screen freeze, on a local phase-13 build). Fixed as far as the agent can see: no work was found on the press in this build (no long task, and no shader, texture or buffer created on ← / →, checked on the dev and production builds), so the stall is taken to be the GPU driver finishing a shader the first time a ship is drawn highlighted. While the menus load, each ship is now drawn once highlighted, hidden by the loading screen (D-118). Needs the reviewer's check on the real GPU.
- [x] (2026-10-27, reviewer in chat, second time) "the level loading is too long, is it not possible to start instantly and do the rest of the loading in background? focus only on level 4-1." Fixed: the level the level select highlight rests on (0.6 s) is now fully built in the background, one step per frame: scene, shaders compiled, drawn once off screen. Confirm then starts it in the same frame, with no loading screen (D-119). 4-1 in the dev build: Confirm → playing in 1 ms (was about 0.5 s plus shader compilation). The cost moves to the level select screen: one step of about 0.7 s (dev build, CPU) about 0.6 s after the highlight stops, which the reviewer accepted.
- [x] (2026-10-27, reviewer in chat) "the music pauses while the level is loading, this is what makes it so noticeable". Fixed: the music was scheduled only 100 ms ahead from the page, so any longer loading step left a gap. Before each loading step (the first time it runs, also for a level built ahead), the music is now scheduled `stallCoverSeconds` (1.5 s) ahead. Notes already scheduled keep playing through a frozen frame; fades and pauses still act on them (D-120). The 100 ms lookahead of P12 is unchanged in normal play.
- [x] (2026-10-27, reviewer in chat) "the music pauses while the level is loading, this is what makes it so noticeable". First fix (music scheduled 1.5 s ahead before each loading step) was not enough: "still blocking, not long, under one second". The level track starts when the level starts, and the stalls of the first frames of play are not loading steps. Fixed: the music is always scheduled 1.5 s ahead (`AUDIO_CONFIG.lookaheadSeconds`, was 100 ms), so any frozen frame under 1.5 s, anywhere, leaves no gap. Fades, cross-fades, pause and volume still apply to the notes scheduled ahead (D-120). The per-step hook was removed.

---

## 🤖 Implementation report
> Filled by the agent. Do not edit (comment in Review feedback instead).

### Questions / blockers
None. The reference machine (P13-R01) was not available to the agent: this WSL machine has no hardware GPU (Chromium falls back to SwiftShader or llvmpipe). All numbers below are measured on software WebGL; see Deviations.

### Plan
| Task | Requirement IDs |
|------|-----------------|
| Perf monitor (long frames, longest frame, loading time, longest loading step), F3 overlay, e2e test API field, `scripts/measure-perf.mjs` | P13-R01 |
| Profile the three reported problems (CDP profiler, unminified e2e build), before numbers on `main` | P13-R01 |
| Road ribbons: street line index, per-list caches, skip roads away from the chunk | P13-R03, R04 |
| Props: upload only the kinds that changed | P13-R04 |
| Noise tables, kept textures, kept level ground (Retry) | P13-R03 |
| Level loading in steps behind a loading screen; precompile shaders, prebuild enemy models | P13-R02, R03, R04 |
| Ship select: compile each ship's spot-lit shaders while the menus load | P13-R02 |
| Unit tests (results unchanged), e2e perf smoke test per world | P13-R05, R03 |

### Requirement traceability
| ID | Status (Done / Partial / Not done) | Code | Tests | Notes |
|----|-----------------------------------|------|-------|-------|
| P13-R01 | Partial | `src/app/perf-monitor.ts`, `src/ui/perf-overlay.ts`, `src/app/start-app.ts` (`perf`, `perfOverlay`), `src/debug/test-api.ts` (`perf`), `scripts/measure-perf.mjs` | `perf-monitor.test.ts`, `perf-overlay.test.ts`, `test-api.test.ts`, e2e `perf.spec.ts` (F3) | Causes found and named (D-113). Before / after table measured on software WebGL, not on the reference machine |
| P13-R02 | Done (software WebGL) | `game-session.ts` (stepped loading), `menu-scenes.ts` (ship highlight warm-up) | `game-session.test.ts` (stepped), `menu-scenes.test.ts`, `start-app.test.ts` | Level confirm 2368 → 5 ms; ship select ← / → 186 → 6 ms (review fix: one key light per ship) |
| P13-R03 | Partial | `game-session.ts`, `ui/level-loading.ts`, `scenery-stage.ts` (`prepareLevelRoads`, `prepareLevelGround`, kept ground), `procedural-textures.ts` (kept textures), `noise.ts`, road files | `game-session.test.ts` (steps, Retry), `procedural-textures.test.ts`, `noise.test.ts`, e2e `perf.spec.ts` (one level per world) | Real progress, moving bar, Retry reuses the ground. On software WebGL the loads are 1.5–4.3 s and the longest step (shader compilation) 0.6–3.4 s: over `level_load_max_s` and `loading_step_max_ms` there; needs the reference machine |
| P13-R04 | Done for the game's own work; see limitations | road files, `prop-field.ts`, `enemy-layer.ts` (`prepare`), `game-play.ts` (`prepare`) | `road-traffic.test.ts`, `prop-field.test.ts` | Long simulation frames per 2 min of play: 19–25 → 0–3 in Worlds 2–4. Rare multi-second stalls remain, inside WebGL calls waiting on SwiftShader (before and after) |
| P13-R05 | Done | (no change of results) | `noise.test.ts` (same values as the old formula), `road-traffic.test.ts` (index = full check), existing unit and screenshot e2e tests | Bundle 561 → 563 KB gzip (ENG-107) |

### Measurements (P13-R01)
Software WebGL (SwiftShader), e2e build at half resolution, this machine, `node scripts/measure-perf.mjs --seconds 120 --render-every 12` (before: `main` at b920575; after: this branch, without the ship-select warm-up, added after). Each level is played from the menu with no input for 120 s (`measure_run_s`), the first second not counted; "sim" frames are simulation-only steps (the game's own CPU work), "drawn" frames also render (every 12th). Cells: count of frames over `long_frame_ms` (50 ms) / longest frame.

| Level | Load before | Load after | Longest load step before | after | Sim long / max before | after | Drawn long / max before | after |
|---|---|---|---|---|---|---|---|---|
| 1-1 | 1.0 s | 3.9 s | 923 ms | 3220 ms | 0 / 21 ms | 0 / 12 ms | 2 / 985 ms | 0 / 48 ms |
| 1-2 | 1.1 s | 3.6 s | 980 ms | 2765 ms | 0 / 16 ms | 0 / 14 ms | 2 / 1382 ms | 0 / 29 ms |
| 1-3 | 1.2 s | 4.3 s | 1111 ms | 3354 ms | 0 / 17 ms | 0 / 12 ms | 2 / 1350 ms | 0 / 33 ms |
| 1-4 | 1.3 s | 3.6 s | 1170 ms | 2471 ms | 3 / 58 ms | 2 / 281 ms | 3 / 1661 ms | 1 / 65 ms |
| 1-5 | 2.0 s | 2.4 s | 1887 ms | 1212 ms | 23 / 328 ms | 1 / 3165 ms | 1 / 871 ms | 0 / 48 ms |
| 2-1 | 1.3 s | 4.1 s | 1213 ms | 2856 ms | 0 / 18 ms | 0 / 15 ms | 1 / 1478 ms | 0 / 40 ms |
| 2-2 | 1.3 s | 1.5 s | 1175 ms | 642 ms | 2 / 70 ms | 0 / 19 ms | 0 / 27 ms | 0 / 35 ms |
| 2-3 | 2.1 s | 3.4 s | 1950 ms | 2298 ms | 23 / 338 ms | 2 / 16783 ms | 3 / 7424 ms | 0 / 29 ms |
| 2-4 | 4.7 s | 3.8 s | 4610 ms | 2237 ms | 19 / 920 ms | 1 / 52 ms | 2 / 666 ms | 0 / 44 ms |
| 2-5 | 5.2 s | 3.7 s | 5076 ms | 2386 ms | 25 / 26529 ms | 3 / 22082 ms | 1 / 67 ms | 2 / 6369 ms |
| 3-1 | 6.4 s | 3.7 s | 6248 ms | 2005 ms | 23 / 1203 ms | 0 / 22 ms | 5 / 28851 ms | 0 / 32 ms |
| 3-2 | 4.7 s | 3.8 s | 4554 ms | 2202 ms | 24 / 23129 ms | 1 / 6962 ms | 0 / 46 ms | 0 / 39 ms |
| 3-3 | 4.7 s | 3.8 s | 4510 ms | 2287 ms | 21 / 25708 ms | 1 / 22926 ms | 3 / 719 ms | 1 / 7851 ms |
| 3-4 | 5.3 s | 4.1 s | 5118 ms | 2325 ms | 24 / 26046 ms | 0 / 41 ms | 1 / 54 ms | 1 / 57 ms |
| 3-5 | 7.2 s | 2.7 s | 7074 ms | 801 ms | 24 / 19797 ms | 1 / 54 ms | 0 / 44 ms | 0 / 42 ms |
| 4-1 | 7.3 s | 3.7 s | 7185 ms | 1751 ms | 23 / 16728 ms | 1 / 104 ms | 4 / 1217 ms | 1 / 31062 ms |
| 4-2 | 6.2 s | 4.2 s | 6058 ms | 2246 ms | 21 / 1067 ms | 0 / 40 ms | 7 / 29042 ms | 1 / 39188 ms |
| 4-3 | 5.0 s | 3.8 s | 4866 ms | 2213 ms | 23 / 735 ms | 0 / 36 ms | 0 / 31 ms | 1 / 66 ms |
| 4-4 | 5.0 s | 3.8 s | 4828 ms | 2319 ms | 21 / 25846 ms | 1 / 71 ms | 3 / 618 ms | 2 / 40835 ms |
| 4-5 | 4.3 s | 3.8 s | 4146 ms | 2482 ms | 19 / 705 ms | 1 / 53 ms | 2 / 635 ms | 1 / 36373 ms |

Before, the load was one frozen step (the key press itself), and the first appearance of new objects froze 0.5–1.7 s at about 5 s in (drawn column). After, the press returns at once and the shader work is in the load (the `[roads, ground, scene, prepare, render]` steps measured for 4-5: 343, 212, 602, 2482, 119 ms; the 2.5 s "prepare" is SwiftShader compiling every shader in software). The few remaining multi-second "after" frames (2-3, 2-5, 3-2, 3-3, 4-1, 4-2, 4-4, 4-5) are stalls inside WebGL calls (`bindVertexArray`, `uniformMatrix4fv`, `bindBuffer`: 38 s of a 6 s profile window) waiting on SwiftShader's GPU process. They happen at different times from run to run, also before, and also on frames that draw nothing.

Menu presses (press + the frame after it):

| Press | Before | After |
|---|---|---|
| title: down | 14 ms | 19 ms |
| title: up | 5 ms | 6 ms |
| title: confirm (ship select) | 14 ms | 21 ms |
| ship select: right | 186 ms | 158 ms |
| ship select: confirm (level select) | 4 ms | 4 ms |
| level select: right | 2 ms | 2 ms |
| level select: left | 2 ms | 2 ms |
| level select: confirm (1-1) | 2368 ms | 48 ms |
| game: pause | 40 ms | 4 ms |
| pause: down | 3 ms | 6 ms |
| pause: up | 5 ms | 3 ms |
| pause: resume | 4 ms | 4 ms |

Re-measured with the ship-select warm-up (e2e build): ship select → 222 ms, level select confirm 42 ms, pause ↓ 1352 ms. In the e2e build the level's shaders are not precompiled (see Deviations), so that pause frame is the level's first draw catching up on SwiftShader. A CDP profile of the first ship-select press (186 ms) puts nearly all of it inside WebGL calls (`uniformMatrix4fv` 2.8 s, `uniform4f` 1.4 s over the profile), not in game code; the next presses take 14 and 5 ms.

### Causes of the three reported problems
1. **Freezes of about 1 s in Worlds 3 and 4.** Each new terrain chunk (about every 4–5 s) built its road ribbons by checking every point of every road in the level against every street (`meetingWidth`, `inCrossing`), so the cost grew with the square of the roads. That came to 0.8–0.9 s per chunk in the street mazes of Worlds 3 and 4 (Worlds 2 and 1-5 too). Moving the prop window also re-uploaded every prop kind's instances.
2. **Slow level loading.** The same road scan for the first chunks (4 s of the 6.1 s it took to load 3-1). Generating the level's roads and props took 1.1 s, regenerating the ground textures took 0.6 s, and the noise worked out a cosine and a sine on every call (0.7 s across all of these).
3. **Lag of up to 1 s after a button press.** Confirming a level (also Retry, Next level, Continue) built the whole level inside the key press, so the screen didn't change until it was built. Moving the highlight on the ship select screen compiled shaders the first time each ship was lit (186 ms).

### Review fixes (2026-10-27)
- **Ship select lag:** changing the one key light's `includedOnlyMeshes` dirtied the ship materials and recompiled their shaders the first time each ship was lit. Now there is one key light per ship (`ShipSelectStage`), and highlighting only changes intensities. The menu loading warm-up task added earlier was removed. Measured on software WebGL: ship select → 6 ms (was 186–222 ms).
- **Background loading:** `BackgroundLoader` (`src/render/scenery/background-loader.ts`) runs a worker (`ground-worker.ts`) that generates a level's ground (`groundSnapshot`: roads and placed buildings as plain data) and its scenery textures (`sceneryTextureJobs`). The main thread rebuilds the road network and placer from that data (`RoadNetwork`/`PropPlacer` take a snapshot: same roads, same buildings, same indexes, checked by a unit test on 3-3). `LevelPrefetcher` asks for the highlighted level once the highlight has rested on it for 0.25 s, so passing over levels doesn't queue them all. The loading step for the ground waits for the worker; without a worker (unit tests) it generates at once, and after a worker error it falls back to generating on the main thread. Enemy models: `EnemyLayer.prepareNext` builds one model per frame during play (shaders compiled as they're built, outside e2e).
- Measured (software WebGL, `--warm`: highlight rests 3 s): 1-1 0.44 s, 3-1 0.51 s, 4-5 0.47 s to the first playable frame (were 3.6–4.3 s). Steps: scene 287–349 ms, first draw 101–131 ms, others ≤ 11 ms. No frame over 50 ms in 20 s of play. Confirming at once (cold) takes ~4 s while the worker generates, but the frames stay at 1–3 ms and the bar keeps moving.

### Review fixes, second round (2026-10-27, focus on 4-1)
- **Diagnosis** (dev and production builds, real render loop, keyboard presses through Playwright): on ship select, ← / → creates no WebGL resource (counted on `compileShader`, `linkProgram`, `texImage2D`, `bufferData`, …) and causes no long task, so nothing in the game runs on the press. On 4-1 the earlier loading took 0.5 s to build the scene, 0.2 s to prepare it, then linked 20 shader programs and uploaded 36 textures and about 6000 buffers. On software WebGL the long frames after a 4-1 start (300 ms–2.8 s) are SwiftShader drawing the full-size scene: they are the same with no audio and with no enemy prebuild, and appear the moment the loading screen goes away.
- **Ship select** (D-118): a menu loading step draws each ship once highlighted, so that any driver-side shader work is done behind the loading screen.
- **4-1 instant start** (D-119): `GameSession` builds the level the highlight rests on (`prebuildLevels`, not in e2e builds) with the same steps as a load, short of starting it. `GamePlay.attach()` adds its HUD only when it starts. Confirming that level with the same ship starts it at once. A level built for another level or ship is dropped, and so is the one built when the level select is left. Dev build log for 4-1: build steps of 724 / 200 / 101 ms on the level select, Confirm → started in 1 ms.

### Review fix: music through loading (2026-10-27)
- `MusicPlayer.update(ahead)` and `GameAudio.coverStall()`; `GameSession` calls `SessionAudio.beforeLoadStep` before the first run of each loading step. Tests: `music-player.test.ts` (notes scheduled through a 2.5 s stall), `game-session.test.ts` (called before each step). Light verification green: typecheck, build, 122 e2e. Unit suite 1618 passed (run as a check). Calling it on every retry of a waiting step slowed the audio e2e tests by about 10 s, so it runs once per step.

### Review fix: music through loading (2026-10-27)
- `AUDIO_CONFIG.lookaheadSeconds` 0.1 → 1.5 s (deviation from the P12 tunable `scheduler lookahead`, at the reviewer's request; the music itself is unchanged, P13-R05). Test: `music-player.test.ts`, "with the game lookahead, a frozen frame of 1 s leaves no gap". Unit suite 1617 passed (run as a check). Light verification: typecheck, build green; e2e 121 passed + the World 2 dusk-lights timeout seen before (passed alone, 24.1 s).

### Gate results
```
Full gate (validation, 2026-10-27): make check ✔ — lint ✔, typecheck ✔, 1617 unit tests (180 files) ✔, coverage 99.28 % lines / 87.83 % branches / 98.57 % functions / 98.46 % statements ✔, build ✔, 122 e2e ✔ (6.8 min).
Light verification (implementation): make typecheck ✔ / make build ✔ / make e2e ✔ 122 passed (5.8 min, after the review fixes).
Light verification (second review round): make typecheck ✔ / make build ✔ / make e2e ✔ 122 passed (6.8 min). A first run had one timeout (world-2 "lights come on at dusk and night", 24.3 s alone against the 30 s limit).
The unit tests in tests/unit/app were run as a check: 229 passed, 1 failed. That failure, `level-prepare.test.ts` "prefetches the highlighted level once the highlight rests on it", failed the same way on c7f6af1. It is now fixed: levels a and c of the test game share one scenery, so starting a found c's ground already requested; the test gives a its own seed. Full unit suite: 1616 passed.
Lint, unit tests and coverage: not run (deferred to /validate-phase, per CLAUDE.md).
```

### How to test manually
- `make build && make preview` (or `make dev`), open the game, press **F3** (dev build): the overlay in the top left shows the long frames, the longest frame and the last level load. In a production build there is no overlay; use the browser performance panel.
- Confirm a level: the level select goes at once. If loading takes longer than 300 ms, a loading screen with a moving bar fades in.
- Play 3-1 to 3-5 and 4-1 to 4-5 (or `?level=3-3`): check for visible freezes; F3 shows the count.
- Retry a level from the Game over panel: it starts at least as fast as the first time.
- Measure on the reference machine: `make e2e-build && npx vite preview --mode e2e --outDir dist-e2e`, then `node scripts/measure-perf.mjs --gpu --seconds 120` (all levels and the menus; `--levels 3-1,4-5` for some).

### Deviations from spec
- P12 tunable `scheduler lookahead` (100 ms) is now 1.5 s (D-120, review fix): the music plays on through frozen frames.
- P13-R01: the before / after numbers were measured on software WebGL. No reference machine (real GPU) was available, so GPU-side costs (shader compilation, drawing) are far worse than real ones and the CPU-side costs are this machine's. The reviewer can run `scripts/measure-perf.mjs --gpu` on the reference machine to fill in the reference column.
- Only in unit tests (no `steppedLoading`) does a level still load all at once inside `sync`, which keeps the existing tests as they were. The browser game always loads in steps.
- e2e builds don't precompile a level's shaders while it loads (`precompileShaders: !__E2E__`). On SwiftShader, compiling them takes 2–4 s per load, and pushed tests that load several levels past their 30 s timeout under the parallel run (4 timeouts in one run). The e2e tests check state, not frame times (ENG-52). The browser game precompiles. Enemy models are prebuilt in both.

### Known limitations
- A level confirmed before the worker has prepared it (less than ~3 s after it was highlighted) still waits for the worker, about 4 s on this machine, behind the loading screen.
- On software WebGL, loading still takes longer than `level_load_max_s` (1.5–4.3 s), and the longest step is longer than `loading_step_max_ms`. The steps over 200 ms are the roads and props generation (~350–600 ms, CPU) and shader compilation (SwiftShader). Shader compilation should be much shorter on a real GPU, which also compiles in parallel (the loader waits for that). The generation steps would need resumable generators in `core/scenery` if the reference machine shows them over 200 ms (Suggestions).
- Rare multi-second stalls inside WebGL calls happen on SwiftShader, both before and after this phase. They need checking on the reference machine.
- The F3 overlay only exists in dev and e2e builds (ENG-111).
- Building a level ahead freezes the level select for one step (the scene, ~0.7 s dev build on this CPU) about 0.6 s after the highlight stops on a level. Splitting the scene build over frames is listed in Suggestions.
- The ship-select freeze could not be reproduced on software WebGL; the fix rests on the driver hypothesis (D-118).

### Suggestions for future phases
- Split road and prop generation over frames (resumable generators), or prepare the highlighted level's ground in idle time on the level select screen.
- Run the measurement script in CI on a machine with a GPU to catch regressions.
