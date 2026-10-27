# Phase 13 — Perf

> Fill the **Human** sections. Set **Status** to `Ready` when the agent may implement it.
> The agent fills the **Agent** sections and never edits the requirement sections.
> Drafted by the agent at the reviewer's request (2026-10-27) from three reported problems: lag of up to 1 s after some button presses, slow level loading, and repeated 1 s freezes during play in Worlds 3 and 4. Numbers are agent defaults; the reviewer may change any of them before setting the status to `Ready`.

**Status:** Draft  <!-- Draft | Ready -->
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

- [ ] 

---

## 🤖 Implementation report
> Filled by the agent. Do not edit (comment in Review feedback instead).

### Questions / blockers
<!-- Ambiguities found before implementing. If non-empty, agent stops and waits. -->

### Plan
| Task | Requirement IDs |
|------|-----------------|
| | |

### Requirement traceability
| ID | Status (Done / Partial / Not done) | Code | Tests | Notes |
|----|-----------------------------------|------|-------|-------|
| P13-R01 | | | | |

### Gate results
```
make check output summary: lint ✔ / typecheck ✔ / tests N passed / coverage xx% / build ✔
```

### How to test manually
<!-- Steps, keys, debug toggles, URL. -->

### Deviations from spec
<!-- Anything done differently and why. Also logged in DECISIONS.md. -->

### Known limitations
-

### Suggestions for future phases
-
