# Phase 13: Perf — Context

**Gathered:** 2026-10-27
**Status:** Ready for planning (spec `specs/phases/phase-13-perf.md` is still `Draft`; implementation waits for `Ready`)

<domain>
## Phase Boundary

Responsiveness only: instant button feedback (P13-R02), every level playable within 2 s of Confirm (P13-R03), no freezes during play in any level, Worlds 3 and 4 especially (P13-R04), measured before and after (P13-R01), with no change to look, content, rules or simulation results (P13-R05). Requirements and numbers are owned by the spec; this file records HOW.
</domain>

<decisions>
## Implementation Decisions

### Loading strategy

- **D-01:** Heavy level work happens **per level, on Confirm**, behind a loading screen whose progress bar keeps moving: split the level build into steps and yield to the browser between them (extend the `runLoadingTasks` / `yieldToBrowser` pattern in `src/assets/loading-tasks.ts`), no single step longer than `loading_step_max_ms`.
- **D-02:** Boot time stays as it is: nothing per-level moves to the initial loading screen.
- **D-03:** Work that can be shared (compiled shaders, shared materials, models, generated music) is **cached after first use** and reused on later starts and on Retry, so a second start is never slower than the first.

### In-play freezes

- **D-04:** Terrain chunks and props keep **streaming ahead of the camera**, but generation is **time-sliced**: work is split into small units run under a per-frame millisecond budget, started far enough ahead that a chunk is always ready before it scrolls into view. Same look, low memory. No Web Worker unless profiling proves time-slicing cannot meet P13-R04 (log in DECISIONS.md if so).
- **D-05:** The initial chunks visible at level start are built during the level's loading steps (D-01), not on the first frames of play.

### Shader warm-up

- **D-06:** During each level's loading screen, **force-compile every material and effect the level can show** (terrain, props, weather, every enemy kind and boss of that level, shots, bombs, explosions, HUD effects), so first appearances never stall. Use Babylon's material compilation APIs (e.g. `forceCompilationAsync` / `scene.whenReadyAsync`); verify via P13-R01 measurements.

### Claude's Discretion

- **Measurement:** the agent measures relatively (before/after, same machine) under its software WebGL and builds the instrumentation (long-frame counter, longest frame, loading time in the F3 overlay and test API). The absolute numbers on the ENG-101 reference machine are taken by the reviewer during manual validation using the F3 overlay; the report states which numbers came from where.
- **Button lag:** default approach is "feedback first, work after": on a press, render the next screen (or the loading screen) on the next frame, then start heavy work. Pre-build only if profiling shows a screen itself is slow to build.
- Exact per-frame generation budget and look-ahead distance (tune from P13-R01 numbers; put in config as tunables).
</decisions>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

- `specs/phases/phase-13-perf.md` — requirements P13-R01..R05, tunable values, out of scope, manual checklist (source of truth)
- `specs/01-engineering.md` — ENG-100..ENG-111 (fixed timestep, 60 FPS target and reference machine, instancing, pooling, budgets, loading screen with real progress, debug overlay), §2 layering and §2.3 engine/game split
- `specs/02-game-design.md` — game-wide rules that must not change
- `specs/DECISIONS.md` — prior decisions (D-044/D-051 enemy density, D-109..D-112 world reworks)
- `.planning/codebase/CONCERNS.md` — known lead: synchronous scenery build on level start and chunk/prop generation during scroll
- `CLAUDE.md` — spec-driven workflow, light verification during implementation
  </canonical_refs>

<code_context>

## Existing Code Insights

### Reusable assets

- `src/assets/loading-tasks.ts` — `runLoadingTasks` with `yieldToBrowser()` between tasks: the pattern to extend for per-level stepped loading.
- `RateMeter` + FPS/polygons stats tile (`src/app/start-boss-viewer.ts`, `src/app/start-scenery-viewer.ts`) — basis for the long-frame counter in the overlay.

### Hot spots (to confirm by profiling, P13-R01)

- `src/app/level-scene.ts` — builds the level synchronously on start.
- `src/render/scenery/scenery-stage.ts`, `src/render/scenery/terrain-chunks.ts` — chunk and prop generation during scroll; no time-slicing today.
- No shader precompilation anywhere in `src/`.

### Integration points

- Level start path from level select / Retry / Next level; loading screen `src/ui/screens/loading-screen.ts`.
- Engine vs game split: stepped loading, time-slicer and warm-up are engine features (outside `src/game/`); per-level budgets/tunables go in `src/game/` config.
  </code_context>

<specifics>
## Specific Ideas

- Reviewer report (2026-10-27): "<1 s lag when some buttons are clicked", "level loading time is so slow", "Worlds 3 and 4 have repeated 1 s lag during gameplay".
</specifics>

<deferred>
## Deferred Ideas

- Web Worker geometry generation — only if time-slicing cannot meet P13-R04.
- Pre-building all worlds at boot — rejected for now (longer first load).
</deferred>

---

_Phase: 13-perf_
_Context gathered: 2026-10-27_
