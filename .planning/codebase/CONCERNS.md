---
last_mapped_commit: f4b3594074f5b8d67c594e038113c45d65d18a7c
last_mapped_at: 2026-10-27
---

# Codebase Concerns

**Analysis Date:** 2026-10-27

## Tech Debt

**CI does not run the e2e suite (ENG-72 is a MUST):**

- Issue: The `e2e` job in `.github/workflows/ci.yml` is commented out. CI runs only `make lint typecheck coverage build`. Deploy (`.github/workflows/deploy.yml`) is gated on that CI run, so a regression that only the Playwright suite catches reaches GitHub Pages.
- Files: `.github/workflows/ci.yml`, `.github/workflows/deploy.yml`, `specs/01-engineering.md` (ENG-72, ENG-81)
- Impact: The full gate (`make check`, including `make e2e`) depends on the agent or a developer running it locally during `/validate-phase`. Nothing enforces it on `main`.
- Fix approach: Restore the `e2e` job as ENG-72 describes (`make install` then `make e2e`, Chromium cached, Playwright report uploaded on failure) and make the deploy job `needs` both jobs. If the job is disabled on purpose for runner cost, record it as a decision in `specs/DECISIONS.md` and amend ENG-72 by a human.

**Spec and decision drift:**

- Issue: Several specs and decisions disagree with the code and have not been reconciled:
  - ENG-07 says persistence uses `localStorage`; the code uses cookies (`src/platform/cookie-storage.ts`, D-010). The phase 1 report already asks to "update ENG-07 to say cookies".
  - ENG-12 names `eslint-plugin-import`; the code uses `eslint-plugin-import-x` (D-019).
  - D-002 still reads "Accepted" with ESLint `^9.39`; `package.json` pins ESLint `^10.13.0` and `@eslint/js` `^10.0.1` (D-019 supersedes it, but D-002 has no status change).
  - ENG-52 names `setSeed(n)` and `pause()` on `window.__GAME_TEST__`; `src/debug/test-api.ts` has `getState`, `sendAction` and the phase hooks only, and `src/main.ts` installs no `setSeed` or `pause`.
  - Every phase spec still has all acceptance boxes unticked (for example `specs/phases/phase-11-score-lives-bombs.md`), though the phases are marked validated in `specs/PROGRESS.md`. Only the agent may tick requirement traceability tables, so the checklists cannot be trusted as a record of what was verified.
- Files: `specs/01-engineering.md`, `specs/DECISIONS.md`, `specs/phases/*.md`, `src/platform/cookie-storage.ts`, `src/debug/test-api.ts`, `package.json`
- Impact: Future agents follow the wrong rule (for example, use `localStorage` because ENG-07 says so), and the validation record is unreliable.
- Fix approach: A human edits ENG-07, ENG-12 and ENG-52 (requirement sections are human-owned). The agent sets D-002 to "Superseded by D-019" and adds the missing `setSeed` / `pause` hooks when a phase needs them, or records their deferral in `specs/DECISIONS.md`.

**Stray build log committed at the repository root:**

- Issue: `vite.log` is tracked by git (it was committed in "Phase 08 (#18)"). It contains a Vite stack trace.
- Files: `vite.log`, `.gitignore`
- Impact: Noise in the repository and a risk of committing more logs. The root `.gitignore` covers `dist/`, `coverage/` and `test-results/` but not logs.
- Fix approach: `git rm vite.log`, add `*.log` to `.gitignore`.

**Debug viewer code ships in the player bundle:**

- Issue: `src/main.ts` imports all five debug viewer starters (`start-ship-viewer`, `start-shot-viewer`, `start-scenery-viewer`, `start-enemy-viewer`, `start-boss-viewer`) at the top of the entry, so their code is in the main chunk that every player downloads. The viewer pages are separate HTML entries (`player_ship/`, `bosses/`, and so on) and need only their own starter.
- Files: `src/main.ts`, `src/app/start-enemy-viewer.ts`, `src/app/start-boss-viewer.ts`, `src/app/start-shot-viewer.ts`, `src/app/start-scenery-viewer.ts`, `src/app/start-ship-viewer.ts`, `vite.config.ts`
- Impact: Larger first download. The phase 7 report already notes the main chunk is "a little over Vite's 1,500 kB warning size" (410 kB gzip). Current JS output in `dist/assets/` is about 0.83 MB gzip in total across chunks.
- Fix approach: Load the viewer starters with dynamic `import()` inside the branches of `boot()` in `src/main.ts`, or split each viewer into its own Vite entry chunk. Then check the main chunk size with `make build`.

**Repetitive viewer bootstrap code:**

- Issue: `startShots`, `startScenery`, `startEnemies` and `startBosses` in `src/main.ts` repeat the same pattern (`fitCanvasStage`, the viewer start call, then `if (__E2E__) installXTestApi(...)`).
- Files: `src/main.ts`
- Impact: Each new viewer repeats about 25 lines, and a missed `renderLoop: !__E2E__` or `fitCanvasStage` call breaks only that page.
- Fix approach: One table of `{ start, installTestApi, testGlobal }` per viewer route, driven by `resolveRoute`.

**Listener lifecycle is not symmetric:**

- Issue: `src/` has 49 `addEventListener` calls and 21 `removeEventListener` calls. Most of the unbalanced ones are on DOM elements that are discarded with their screen (`src/ui/screens/game-screen.ts`, `src/ui/game-hud.ts`, `src/ui/screens/settings-screen.ts`), which is safe only while the owning element is removed on teardown. The HUD is created per level (`src/app/game-play-hud.ts`), so each restart adds listeners to new elements.
- Files: `src/ui/screens/game-screen.ts`, `src/ui/game-hud.ts`, `src/ui/screens/settings-screen.ts`, `src/app/game-play-hud.ts`, `src/app/game-session.ts`
- Impact: Possible leak of closures across many level restarts. Not measured.
- Fix approach: Track listeners in the screen or HUD object and remove them in its `dispose()`, or add a test that counts listeners after two level starts with a fake DOM.

**Level scenery built synchronously on the main thread:**

- Issue: Starting a level builds its scenery synchronously, and terrain chunks plus props are generated during scroll (`src/app/level-scene.ts`, `src/render/scenery/scenery-stage.ts`, `src/render/scenery/terrain-chunks.ts`). The phase 6 and phase 4 reports name this as a freeze after Confirm ("longer for 1-5's city") and a hitch while scrolling.
- Files: `src/app/level-scene.ts`, `src/render/scenery/scenery-stage.ts`, `src/render/scenery/terrain-chunks.ts`, `src/core/scenery/scenery-level.ts`
- Impact: Visible stutter at level start and on scroll, which matters for ENG-101.
- Fix approach: Spread chunk generation over frames (budget per frame), or move `src/core/scenery/` generation into a Web Worker (the core layer is already pure, so it is worker-safe).

## Known Bugs

No confirmed functional bugs were found in static review. The following are behaviours the phase reports record as open:

**Audio starts on the second key press when the first key is Escape:**

- Symptoms: Browsers only allow audio after a user activation; Escape is not treated as one, so the first Escape press leaves the music silent until the next key, tap or click.
- Files: `src/app/page-audio.ts`, `src/audio/audio-output.ts`
- Trigger: First interaction with the page is Escape.
- Workaround: Press any other key, tap or click.

**Invalid debug URL options do nothing silently:**

- Symptoms: `?level=1-1&ship=bogus` returns without starting a level (`MenuFlow.playDirect` returns `false`), so the player stays on the title screen with no message.
- Files: `src/app/menu-flow.ts` (`playDirect`), `src/app/start-app.ts` (`startDebugLevel`), `src/app/debug-options.ts`
- Trigger: A `level` or `ship` value that is not in the catalog.
- Workaround: Use a valid level id (see `src/game/config/levels.ts`).

**Stored weapon levels are trusted without an upper bound check:**

- Symptoms: `parseWeaponLevels` in `src/app/saved-weapons.ts` accepts any positive integer per weapon id. `ShotWorld.select` clamps the active level (`src/core/systems/shot-world.ts:80`), so no crash occurs, but a hand-edited cookie can restore the top level of every weapon. The same applies to the high score cookie (`src/app/saved-choices.ts`).
- Files: `src/app/saved-weapons.ts`, `src/app/saved-choices.ts`, `src/core/systems/run-arsenal.ts`
- Trigger: Editing the cookie in browser devtools.
- Workaround: None needed for a single-player offline game; treat as cheating only.

## Security Considerations

**Debug URL options and debug keys are live in production builds:**

- Risk: `?level=…&t=…&boss=…&look=…` and the keys F (×4 fast forward), ← / → (seek) and K (destroy the next boss part) work in every build, not only dev and e2e (D-039, P06-R09). The FPS / polygons tile is shown too (`src/app/game-play.ts`, `src/app/debug-options.ts`, `src/main.ts`).
- Files: `src/app/debug-options.ts`, `src/app/game-play.ts` (`debugKey`), `src/app/game-session.ts`, `src/main.ts`
- Current mitigation: Keys are ignored unless the URL has `level`, and the `__E2E__` test API is stripped from production (`make build` greps for it).
- Recommendations: This is a deliberate decision, so record the trade-off: ENG-111 (SHOULD) says the overlay is for dev and e2e builds only, which conflicts with P06-R09. Either gate the stats tile and the debug keys behind `__E2E__ || import.meta.env.DEV`, or amend ENG-111 in `specs/01-engineering.md` by a human.

**Cookie attributes:**

- Risk: The game's cookies are written without the `Secure` attribute (`src/platform/cookie-storage.ts`). They hold only a high score, the last ship, volumes and the weapon kept between levels, so the impact is low.
- Files: `src/platform/cookie-storage.ts`
- Current mitigation: `SameSite=Lax`, values are URL-encoded and parsed defensively (`src/app/saved-choices.ts`, `src/app/saved-settings.ts`).
- Recommendations: Add `Secure` when the page is served over HTTPS (`location.protocol === 'https:'`), which GitHub Pages always is.

**No Content Security Policy and no subresource integrity:**

- Risk: `index.html` (and the viewer pages) set no CSP `<meta>` header. There are no external scripts, fonts or stylesheets (the page uses system fonts only), and `innerHTML` is not used anywhere in `src/`, so the current XSS surface is small.
- Files: `index.html`, `player_ship/index.html`, `player_shots/index.html`, `level_zero/index.html`, `enemies/index.html`, `bosses/index.html`, `boss/index.html`
- Current mitigation: No third-party runtime resources; DOM is built with `createElement` / `setAttribute`.
- Recommendations: Add `<meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data: blob:; media-src 'self' blob:; style-src 'self' 'unsafe-inline'">` (Babylon may need `worker-src blob:` and `unsafe-eval` checks; verify in the e2e build before enabling). Keep it self-only.

**GitHub Actions pinned by tag, not by commit:**

- Risk: `actions/checkout@v7`, `actions/setup-node@v7`, `actions/upload-artifact@v7`, `actions/upload-pages-artifact@v5` and `actions/deploy-pages@v5` are referenced by major tag. The deploy job has `pages: write` and `id-token: write`.
- Files: `.github/workflows/ci.yml`, `.github/workflows/deploy.yml`
- Current mitigation: Dependabot is configured (`.github/dependabot.yml`); `permissions` on deploy are limited.
- Recommendations: Pin each action to a full commit SHA with the tag in a comment, and let Dependabot update SHAs.

**Viewport disables user zoom:**

- Risk: `index.html` uses `user-scalable=no` in the viewport meta tag, which blocks pinch zoom for low-vision players (accessibility, WCAG 1.4.4). This is not a data risk but conflicts with ENG-112 (accessibility, SHOULD).
- Files: `index.html`
- Current mitigation: None.
- Recommendations: Remove `user-scalable=no` from `index.html` and check that the game layout (`src/ui/stage-fit.ts`) still letterboxes correctly on mobile.

## Performance Bottlenecks

**60 FPS target (ENG-101, MUST) has never been measured:**

- Problem: Every phase report from 6 to 12 says the frame rate could only be checked under software WebGL (SwiftShader, about 10–27 FPS for every level), so the mid-range laptop target is unverified.
- Files: `specs/01-engineering.md` (ENG-101), `specs/phases/phase-06-world-1.md`, `specs/phases/phase-08-world-2.md`, `specs/phases/phase-10-world-4.md`, `playwright.config.ts`
- Cause: Scenes are heavy. The city centres draw about 0.8 M triangles (1-5, D-027) and about 0.95 M (polar city centre, phase 8). Each ship is 30–45 meshes, each boss 31–65 meshes, with a glow layer per scene.
- Improvement path: Add an F3-style frame-time and draw-call readout (ENG-111, SHOULD) to a manual check page, measure on a reference laptop, and record the numbers in `specs/PROGRESS.md`. Merge meshes by material per ship and boss (phase 2 and phase 7 suggestions).

**Draw-call budget (ENG-106, SHOULD) is not measured:**

- Problem: The phase 2 and phase 7 reports say each ship should be merged into one mesh per material to stay within 200 draw calls; this is not done.
- Files: `src/game/view/ship-parts.ts`, `src/game/view/balanced-ship.ts`, `src/game/view/light-ship.ts`, `src/game/view/heavy-ship.ts`, `src/game/view/bosses/boss-model.ts`
- Cause: One Babylon mesh per part for flashes and stumps.
- Improvement path: Merge static parts by material, keep only the animated parts separate.

**Bundle size near its limit:**

- Problem: `vite.config.ts` raises `chunkSizeWarningLimit` to 1500 kB (D-003) so the build does not warn about Babylon. The budget (ENG-107) is 1.5 MB gzip. The main chunk is already around 410 kB gzip (phase 7 report).
- Files: `vite.config.ts`, `src/main.ts`
- Cause: Babylon core plus all viewer code (see Tech Debt).
- Improvement path: Split viewer code (see Tech Debt), and import only needed Babylon modules (ENG-02, ENG-107 already require deep imports).

## Fragile Areas

**Stand-in `Enemy` objects typed with casts:**

- Files: `src/game/view/bosses/boss-model.ts` (lines 218 and 250: `as unknown as Enemy`), `src/game/view/enemies/enemy-mesh.ts` (line 143: `as unknown as Rgb`)
- Why fragile: The boss model drives its flashing parts and charge lights through a fake `Enemy` built from `{ charge: 0 }`. Any future read of another `Enemy` field in `core.model.sync` or `showTurret` returns `undefined` silently, and TypeScript cannot catch it.
- Safe modification: Give the view a small interface with only the fields it reads (`charge`, `health`, and so on) and type the sync functions against that interface, instead of casting.
- Test coverage: Covered by model tests, but a missing field would not fail them.

**Scattered game-specific tuning and config modules:**

- Files: `src/game/config/` (about 75 modules, including `src/game/config/bosses/world-2/*.ts`, `src/game/config/bosses/world-3/*.ts`, `src/game/config/bosses/world-4/*.ts`)
- Why fragile: Boss health values are marked as placeholders awaiting balance (for example `src/game/config/bosses/world-2/floe-breaker.ts`, `aurora-station.ts`, `snow-owl.ts`, `narwhal.ts`). Changing one number changes fight times that other specs document (phase 8 table: "mini_fight_time 2-1 → 2-5").
- Safe modification: Change a tunable in `src/game/config/`, then update the fight-time table in the phase spec and re-run `make typecheck` and the unit tests for the world (`tests/unit/game/sim/world-2.test.ts`).
- Test coverage: The sim tests check counts and ranges, not final balance.

**Large multi-responsibility modules at the edge of the lint limits:**

- Files: `src/core/scenery/scenery-level.ts` (440 lines), `src/core/scenery/road-network.ts` (399), `src/core/systems/boss-pattern.ts` (384), `src/app/menu-flow.ts` (375), `src/app/game-play.ts` (349), `src/app/start-boss-viewer.ts` (335), `src/app/start-app.ts` (331)
- Why fragile: The ESLint limits (`max-lines` 300 non-blank lines, `max-lines-per-function` 50, `complexity` 10, all warnings with `--max-warnings 0`) pass only because blank lines and comments are skipped. Changes to these modules touch many concerns at once.
- Safe modification: Split by concern when touching them (for example, `game-play.ts` into the run driver, the HUD wiring and the debug keys, which already have their own method).
- Test coverage: `src/app/` is 97.2% lines overall, but `src/app/level-scene.ts` is 67.6% (`coverage/coverage-summary.json`).

**Game screen and level lifecycle depend on call order:**

- Files: `src/app/game-session.ts` (`sync`, `#start`, `end`), `src/app/game-play.ts` (constructor, `dispose`), `src/app/page-audio.ts`
- Why fragile: `GameSession.sync` ends the level when the attempt number changes, records the score in `end()`, and disposes the scene, HUD and controls. Adding a new exit path that skips `end()` would leave the score unrecorded and the scene alive.
- Safe modification: Route every level exit through `GameSession.end()`; add a unit test per exit path in `tests/unit/app/game-session.test.ts`.
- Test coverage: Unit tests exist; the pause and checkpoint paths are covered only through e2e.

**Sync-time scene work mixed with the render loop:**

- Files: `src/main.ts` (`boot`, `startGame`), `src/app/start-app.ts`
- Why fragile: `renderLoop: !__E2E__` switches the loop off in e2e builds and the tests step the app by hand (`app.step`). Any new per-frame work added to `src/app/start-app.ts` outside `withAudio` is not stepped in tests.
- Safe modification: Put per-frame logic inside the `Ticker` (`simulate` / `render`) so both the browser and the test API run it.

**Test API covers only part of ENG-52:**

- Files: `src/debug/test-api.ts`, `src/main.ts`
- Why fragile: Without `setSeed` and `pause`, e2e tests depend on `step` and on the level's fixed content; they cannot pick a different seed or pause the simulation directly.
- Safe modification: Add the missing hooks in `src/debug/test-api.ts` when a phase needs them, and add the install call for them in `src/main.ts`.

## Scaling Limits

**Playfield aspect and camera:**

- Current capacity: The playfield is 480 × 640 logical px (`src/game/config/game.ts`). With the 35° tilted camera, only about 293 of 480 px are visible across the bottom edge and about 493 across the top (`specs/DECISIONS.md`, D-020).
- Limit: Enemies that stop in the top third (Strafer, Lancer, Bulwark) sit close to the top edge of the screen (phase 5 known limitation).
- Scaling path: Project the 2D playfield onto the tilted plane or move the camera higher (phase 4 suggestion). Decide and record in `specs/DECISIONS.md`.

**Per-level content and memory:**

- Current capacity: One Babylon scene per level, rebuilt on every start (`src/app/game-play.ts` `dispose` disposes the scene). There are 25 levels in a 5 × 5 grid (`src/game/config/levels.ts`), each generated from a seed.
- Limit: Level start time grows with the city density (1-5 and polar city are the slowest; see Performance).
- Scaling path: Cache generated scenery per level id for the session, or generate it in a worker.

## Dependencies at Risk

**ESLint 10 and typescript-eslint:**

- Risk: `typescript-eslint` 8.x requires TypeScript below 6.1, so `typescript` is pinned to `~6.0.3` and Dependabot ignores later 6.x (`specs/DECISIONS.md`, D-019 and D-002).
- Impact: TypeScript security or bug fixes after 6.0 are blocked until typescript-eslint releases support.
- Migration plan: Track typescript-eslint releases; move TypeScript when support lands (D-019 consequence).

**`eslint-plugin-import-x` replaces `eslint-plugin-import`:**

- Risk: ENG-12 still names the old plugin; the code depends on the fork (`eslint.config.mjs`).
- Impact: A reader following the spec installs the wrong plugin.
- Migration plan: Human update to ENG-12 (see Tech Debt).

**`@babylonjs/core` on a caret range:**

- Risk: `package.json` pins `@babylonjs/core` to `^9.32.0`. Babylon's shader and material APIs change between minor releases and the code uses low-level APIs (`RawCubeTexture`, `ExtrudePolygon`-style builders, custom materials under `src/render/scenery/*.visual.ts`).
- Impact: A lockfile update can break the visual files, which are excluded from unit tests (see Test Coverage Gaps).
- Migration plan: Keep `package-lock.json` committed (it is), run `make e2e` on every Babylon bump, and check the `*.visual.ts` materials by hand.

**`happy-dom` as a dev dependency:**

- Risk: Used by the UI unit tests only (`// @vitest-environment happy-dom`, D-009). Its API differs from browsers in places, so a test can pass against it and fail in a browser.
- Impact: Limited to the UI tests.
- Migration plan: Cover UI behaviour that depends on real layout or events in e2e (`tests/e2e/menu-layout.spec.ts`, `tests/e2e/menu-pointer.spec.ts`).

## Missing Critical Features

**Player damage and collisions are not described as complete in the phase reports:**

- Problem: Phase 5 reports "player damage is out of scope". Phase 11 adds lives, health and bombs (`src/core/systems/player-hull.ts`, `src/core/systems/player-hits.ts`), but the phase reports do not state every collision case is covered. Confirm against P11-R05 before relying on it.
- Blocks: Balance tuning on the lives system (see Test Coverage Gaps).

**Accessibility options (ENG-112, SHOULD) are partially done:**

- Problem: Volume sliders exist (`src/app/saved-settings.ts`, `src/ui/screens/settings-screen.ts`). Remappable keys, a "reduce flashes and screen shake" option and colour-blind-friendly bullet colours are not implemented (phase 12 suggestion).
- Blocks: Players who cannot use the default keys or who are sensitive to flashing. The lightning in World 3 is limited to three flashes per second by design (phase 9), but there is no user-facing switch.

**Hidden-tab and context-loss recovery:**

- Problem: On a WebGL context loss the app shows a fatal message and asks for a reload (`src/main.ts`, `engine.onContextLostObservable`). Hidden-tab pause is implemented later (phase 12, `src/app/page-audio.ts`).
- Blocks: Recovery without a reload (ENG-110 covers only the pause).

## Test Coverage Gaps

**Visual GPU setup excluded from coverage:**

- What's not tested: Shader and material setup, the environment and post-processing (9 files, 1,189 lines): `src/render/environment/showcase-environment.visual.ts`, `src/render/scenery/*-material.visual.ts`, `src/render/scenery/terrain-blend-plugin.visual.ts`, `src/render/scenery/scenery-kit.visual.ts`, `src/fx/**/*.visual.ts` (none in `src/fx/` yet).
- Files: `vitest.config.ts` (coverage `exclude`), the files above
- Risk: A Babylon upgrade or a shader edit can break the look without a unit test failing. Only e2e screenshots and manual checks catch it, and e2e is not run in CI (see Tech Debt).
- Priority: High for the scenery materials, since every level uses them.

**Excluded debug API and pages:**

- What's not tested: `src/debug/**` (excluded from coverage per ENG-45), and `src/main.ts`, which wires every route and the test API.
- Files: `src/debug/test-api.ts`, `src/debug/enemy-viewer-test-api.ts`, `src/debug/boss-viewer-test-api.ts`, `src/debug/viewer-test-api.ts`, `src/main.ts`
- Risk: A wiring mistake in `boot()` (for example, a route that starts the wrong viewer) reaches production. Only the build check and e2e smoke tests cover it.
- Priority: Medium.

**Level scene and app coverage:**

- What's not tested: `src/app/level-scene.ts` is at 67.6% lines (`coverage/coverage-summary.json`, last local run); branch coverage overall is 87.9% and has no enforced threshold for `src/app/` or `src/render/`.
- Files: `src/app/level-scene.ts`, `vitest.config.ts`
- Risk: Scenery placement errors in the level start path are caught only by e2e.
- Priority: Medium. Raise the `src/app/**` threshold once the file is covered, and do not lower any threshold (ENG-43, ENG-44).

**Lint and test results are not run on phase implementation:**

- What's not tested: By design (CLAUDE.md, "Implement phase N"), phases run only `make typecheck build e2e` during implementation. The phase 8, 9 and 10 reports say "Lint, unit tests and coverage have not been run (deferred to `/validate-phase`)".
- Files: `CLAUDE.md`, `specs/phases/phase-08-world-2.md`, `specs/phases/phase-09-world-3.md`, `specs/phases/phase-10-world-4.md`
- Risk: Unit-test regressions are found late, at validation, and CI is the only other check. Combined with the missing e2e job, a phase can reach `main` with unit-test or e2e failures unseen.
- Priority: High. Restore the CI e2e job (see Tech Debt) so the gate runs on every push.

**Timing-sensitive e2e tests under software rendering:**

- What's not tested reliably: Under SwiftShader the page runs at about 10–13 FPS. The phase 4 report records a gamepad test that exceeded its 30 s timeout under load; the phase 5 report records a model-view flake that passed on rerun. `tests/e2e/menu-gamepad.spec.ts` now uses a 90 s timeout.
- Files: `playwright.config.ts` (`retries` only on CI), `tests/e2e/menu-gamepad.spec.ts`, `tests/e2e/enemies.spec.ts`, `tests/e2e/level-zero.spec.ts`
- Risk: Flaky failures, with retries hiding them on CI and failing locally.
- Priority: Medium. Prefer `step` / test-API stepping over waiting on wall-clock time.

---

_Concerns audit: 2026-10-27_
