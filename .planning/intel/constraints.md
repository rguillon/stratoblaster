# Constraints intel

Sources: `specs/01-engineering.md` (SPEC, ENG-xx), `specs/02-game-design.md` (SPEC; GD-xx behaviour is in requirements.md, here only the controls/tunable contract) and the technical contracts (test API, debug endpoints, storage keys, tunables) of `specs/phases/phase-NN-*.md`. IDs verbatim. Priorities: MUST / SHOULD / MAY as in the source. ENG-62 is marked removed in the source (2026-10-22, no commit-msg hook). No ENG-102 exists (quality presets were removed by the reviewer, 2026-10-26 per D-095); ENG-103/ENG-106 still mention presets (High/Medium).
Where a decision overrides a constraint, see `/home/renaud/pewet/.planning/INGEST-CONFLICTS.md` (ENG-07 vs D-010, ENG-12 vs D-019, ENG-82 vs D-003, ENG-120 vs P12-R05).

## Tech stack (ENG-01..ENG-09)

- source: specs/01-engineering.md
- type: nfr
- content:
  - ENG-01 MUST: TypeScript strict + noUncheckedIndexedAccess, exactOptionalPropertyTypes, noImplicitOverride; no .js source.
  - ENG-02 MUST: Babylon.js (@babylonjs/core ES modules, deep imports); loaders, materials, inspector (dev only) allowed.
  - ENG-03 MUST: Vite bundler/dev server.
  - ENG-04 MUST: Node.js 24 LTS + npm, pinned via .nvmrc and package.json engines; lockfile committed; `npm ci`.
  - ENG-05 MUST: minimal runtime dependencies; each new one gets a DECISIONS.md entry.
  - ENG-06 MUST: last 2 versions of Chrome, Edge, Firefox, Safari desktop; WebGL2 required with clear message when missing.
  - ENG-07 MUST: no backend, only same-origin static fetches; persistence (settings, high scores) uses localStorage (overridden by D-010: cookies).
  - ENG-08 MAY: WebGPU backend with WebGL2 fallback.
  - ENG-09 MUST: custom simple collision (sphere/AABB) in core/, no physics engine.

## Project structure and layering (ENG-10, ENG-11)

- source: specs/01-engineering.md
- type: protocol
- content:
  - ENG-10 MUST: directory layout: Makefile, index.html, public/assets/{models,textures,env,audio}, src/{main.ts, app, core/{entities,systems,events,math,content,world.ts}, render, fx, audio, input, ui, assets, config, platform, debug, game/{index.ts,sim,view,config}}, tests/{unit,fixtures,e2e,helpers}, docs/architecture.md, .github/workflows.
  - ENG-11 MUST: layering enforced by lint: core/ imports only core/ and config/ and never Babylon, DOM, window, performance; render/fx/audio/ui read core state and subscribe to events but never mutate; input/ produces actions that app/ passes to core/; only app/ and main.ts wire layers.

## Code style and tooling (ENG-12..ENG-19)

- source: specs/01-engineering.md
- type: nfr
- content:
  - ENG-12 MUST: ESLint flat config with typescript-eslint strict-type-checked + stylistic-type-checked plus eslint-plugin-import (overridden by D-019: eslint-plugin-import-x), zero warnings.
  - ENG-13 MUST: Prettier with committed config; eslint-config-prettier.
  - ENG-14 MUST: tsc --noEmit with zero errors; no any, no @ts-ignore.
  - ENG-15 MUST: kebab-case files, PascalCase types, camelCase functions/variables, UPPER_SNAKE_CASE constants; one main export per file; named exports only.
  - ENG-16 SHOULD: functions <= 50 lines, files <= 300 lines, cyclomatic complexity <= 10.
  - ENG-17 MUST: no magic numbers in gameplay code; engine tunables in src/config/, game tunables in src/game/config/.
  - ENG-18 MUST: deterministic simulation: seeded RNG, dt from loop, no Math.random or Date.now in core/.
  - ENG-19 SHOULD: object pools in hot paths.

## Engine / game separation (ENG-140..ENG-148)

- source: specs/01-engineering.md
- type: protocol
- content:
  - ENG-140 MUST: engine outside src/game/ is game-agnostic (abstractions only).
  - ENG-141 MUST: concrete content (bosses, enemies, weapons, levels) in src/game/sim/, visuals and sounds in src/game/view/.
  - ENG-142 MUST: dependency direction enforced by lint: nothing outside src/game/ imports it except src/main.ts importing only src/game/index.ts; game/sim follows core purity rules; game/view may import render, fx, audio, ui, assets, core and game/sim, game/config.
  - ENG-143 MUST: game tunables in src/game/config/; game assets declared in a game manifest the engine's typed manifest (ENG-123) loads.
  - ENG-144 MUST: single entry point: src/game/index.ts exports one GameDefinition (type in core/content/); engine discovers content only through it.
  - ENG-145 MUST: engine unit tests use a minimal sample game in tests/fixtures/; game content tests in tests/unit/game/.
  - ENG-146 MUST: coverage for src/game/sim/** same thresholds as src/core/** (ENG-43).
  - ENG-147 MUST: docs/architecture.md has a section "Making a new game from this template", kept accurate (file outside this ingest set).
  - ENG-148 SHOULD: abstract engine classes expose overridable hooks and TSDoc contracts; engine changes for new content stay generic.

## Makefile targets (ENG-20..ENG-36)

- source: specs/01-engineering.md
- type: api-contract
- content:
  - ENG-20 MUST make help (default); ENG-21 MUST make install (npm ci, hooks, Playwright Chromium); ENG-22 MUST make dev (Vite, port 5173, inspector); ENG-23 MUST make build (dist/); ENG-24 MUST make lint (ESLint + Prettier check); ENG-25 MUST make format; ENG-26 MUST make typecheck; ENG-27 MUST make test; ENG-28 MUST make test-watch; ENG-29 MUST make coverage (fails below thresholds); ENG-30 MUST make e2e (builds in e2e mode, serves, Playwright); ENG-31 MUST make check-fast (lint + typecheck + test; pre-push); ENG-32 MUST make check (full gate: lint + typecheck + coverage + build + e2e; CI and agent).
  - ENG-33 SHOULD make preview; ENG-34 SHOULD make clean; ENG-35 MAY make e2e-ui; ENG-36 MAY make size (bundle budget).
  - The Makefile is the single entry point for humans, hooks and CI; CI calls only make targets.

## Unit testing and coverage (ENG-40..ENG-48)

- source: specs/01-engineering.md
- type: nfr
- content:
  - ENG-40 MUST Vitest + @vitest/coverage-v8; ENG-41 MUST test-driven; ENG-42 MUST each phase requirement ID appears in at least one test name.
  - ENG-43 MUST thresholds: src/core/** 90 % lines / 85 % branches / 90 % functions / 90 % statements; whole src/ 70 % lines.
  - ENG-44 MUST coverage never decreases between phases; ENG-45 MUST exclusions: src/main.ts, src/debug/**, pure GPU/visual config in render/ and fx/; ENG-46 MUST deterministic tests (seeded RNG, injected clock, fake timers).
  - ENG-47 SHOULD NullEngine tests for render/fx; ENG-48 SHOULD unit tests under 30 s.

## End-to-end testing and test API (ENG-50..ENG-57)

- source: specs/01-engineering.md
- type: protocol
- content:
  - ENG-50 MUST Playwright Chromium project; ENG-51 MUST e2e runs against the built app (vite build --mode e2e + static preview), never the dev server.
  - ENG-52 MUST test API in e2e mode only: window.**GAME_TEST** with getState(), setSeed(n), step(frames), pause(), sendAction(action); absent from production bundle (checked by e2e or build test).
  - ENG-53 MUST every e2e test fails on console error or uncaught exception.
  - ENG-54 MUST smoke suite: page loads, loading completes, title visible, start game, player moves and shoots, pause/resume, game over, back to title.
  - ENG-55 SHOULD each phase adds e2e tests named with requirement IDs; ENG-56 MAY visual regression screenshots (off by default); ENG-57 MUST traces, screenshots, video kept as CI artefacts on failure.

## Git hooks (ENG-60..ENG-65)

- source: specs/01-engineering.md
- type: protocol
- content:
  - ENG-60 MUST Husky hooks installed by make install; ENG-61 MUST pre-commit: lint-staged (Prettier + ESLint --fix) then make typecheck.
  - ENG-62 removed (2026-10-22): no commit-msg hook; messages still follow ENG-90.
  - ENG-63 MUST pre-push: make check-fast; ENG-64 MUST never bypass hooks (--no-verify forbidden); ENG-65 SHOULD hooks under 15 s.

## CI (GitHub Actions) (ENG-70..ENG-79)

- source: specs/01-engineering.md
- type: protocol
- content:
  - ENG-70 MUST ci.yml on push to main and every PR; ENG-71 MUST job check: make install then make lint typecheck coverage build; ENG-72 MUST job e2e parallel to check (make e2e, browsers cached).
  - ENG-73 MUST CI fails on lint, type, test or coverage failure; ENG-74 MUST ubuntu-latest, Node from .nvmrc, npm cache; ENG-75 MUST artefacts: coverage HTML, Playwright report on failure.
  - ENG-76 SHOULD coverage summary in job summary; ENG-77 SHOULD Dependabot weekly for npm and Actions; ENG-78 MAY npm audit; ENG-79 MAY status badges in README.

## Deployment (GitHub Pages) (ENG-80..ENG-85)

- source: specs/01-engineering.md
- type: protocol
- content:
  - ENG-80 MUST deploy.yml with actions/upload-pages-artifact + actions/deploy-pages; ENG-81 MUST trigger on push to main after CI succeeds, also workflow_dispatch.
  - ENG-82 MUST works under sub-path https://<user>.github.io/<repo>/: Vite base set from repo name and asset URLs relative to import.meta.env.BASE_URL (D-003 uses base './' instead).
  - ENG-83 MUST version + short commit hash on the title screen; ENG-84 SHOULD hashed filenames; ENG-85 MAY PR previews: no.

## Git workflow (ENG-90..ENG-94)

- source: specs/01-engineering.md
- type: protocol
- content:
  - ENG-90 MUST Conventional Commits with scope = layer or phase; ENG-91 MUST one branch per phase `phase-NN` from up-to-date main; ENG-92 MUST agent may commit and push the phase branch but not merge to main until /validate-phase N; ENG-93 MUST on validation squash-merge phase-NN into main, push, tag v0.NN.0; ENG-94 SHOULD small focused commits.

## Rendering, graphics and performance (ENG-100..ENG-112)

- source: specs/01-engineering.md
- type: nfr
- content:
  - ENG-100 MUST fixed-timestep simulation at 60 Hz with interpolation; ENG-101 MUST 60 FPS at 1080p on a mid-range integrated-GPU laptop (Intel Iris Xe / Apple M1 class).
  - ENG-103 MUST graphics feature set: PBR, IBL (.env), directional and point lights, PCF/cascaded shadows, glow layer, DefaultRenderingPipeline (bloom, ACES, FXAA), GPU particles with CPU fallback and flipbooks.
  - ENG-104 MUST thin instances for many identical objects; ENG-105 MUST pooled particles with per-preset budgets in fx/; ENG-106 SHOULD < 200 draw calls per frame on Medium; ENG-107 SHOULD initial JS <= 1.5 MB gzip, pre-title download <= 15 MB.
  - ENG-108 MUST loading screen with real progress; ENG-109 MUST no console errors or warnings in normal play; ENG-110 MUST resize, DPR capped at 2, auto-pause when hidden, WebGL context loss message with reload.
  - ENG-111 SHOULD debug overlay F3 (FPS, frame time, draw calls, entities, particles, hitboxes) and inspector F4, dev and e2e builds only; ENG-112 SHOULD accessibility: remappable keys, reduce flashes/shake option, colour-blind-friendly bullets, master/music/SFX sliders (only music and SFX sliders were scheduled, D-095).

## Assets and licensing (ENG-120..ENG-125)

- source: specs/01-engineering.md
- type: nfr
- content:
  - ENG-120 MUST formats: .glb models, KTX2 or WebP textures, Babylon .env, OGG with MP3 fallback audio (audio part does not apply to generated audio, P12-R05).
  - ENG-121 MUST allowed sources: procedural, CC0, CC-BY with attribution; ENG-122 MUST third-party assets listed in CREDITS.md; ENG-123 MUST typed asset manifest src/assets/manifest.ts; ENG-124 SHOULD model <= 2 MB, texture <= 1 MB; ENG-125 MUST MIT license.

## Documentation (ENG-130..ENG-133)

- source: specs/01-engineering.md
- type: nfr
- content:
  - ENG-130 MUST README.md with live game link, controls, Node version, make targets; ENG-131 MUST docs/architecture.md (layers, data flow, game loop; file outside this ingest set); ENG-132 SHOULD TSDoc on public core/ functions and types; ENG-133 MUST CREDITS.md kept up to date.

## Controls and input contract (GD section 2, P01-R09..R12, P11-R06, P12-R01)

- source: specs/02-game-design.md; specs/phases/phase-01-main-menu.md; specs/phases/phase-11-score-lives-bombs.md; specs/phases/phase-12-pause-music-settings.md
- type: protocol
- content:
  - Keys by physical position (KeyboardEvent.code), so AZERTY and QWERTY work. Move: arrows/WASD, left stick, touch drag. Shoot: Space, gamepad button, touch button.
  - Menu actions: up, down, left, right, confirm, back; Enter/Space confirm; Esc/Backspace back; gamepad A confirm, B back; menu_repeat_delay 350 ms, menu_repeat_interval 120 ms, gamepad_dead_zone 0.35.
  - Weapon switch: KeyE (D-043). Bomb: KeyR, ShiftLeft, gamepad button 2 (X) and 4 (LB), touch BOMB button (P11-R06). Pause: Escape, KeyP, gamepad Start (9) and Select (8), touch pause button (P12-R01).

## Persistence contract (cookies)

- source: specs/phases/phase-01-main-menu.md; specs/phases/phase-11-score-lives-bombs.md; specs/phases/phase-12-pause-music-settings.md; specs/DECISIONS.md
- type: schema
- content:
  - Cookie max age 365 days (cookie_max_age). Keys prefixed with game id (stratoblaster): `<gameId>_high_score`, `<gameId>_last_ship`, `<gameId>_music_volume`, `<gameId>_sfx_volume`, `<gameId>_weapons` (D-071). Missing or invalid values read as default (0 / none).
  - Volumes: 10 steps (0-10), defaults Music 6 and SFX 8 (D-095; names music_volume_default, sfx_volume_default).

## Test API and debug endpoints contract

- source: specs/phases/phase-01-main-menu.md; specs/phases/phase-03-player-shots.md; specs/phases/phase-05-first-enemies.md; specs/phases/phase-07-bosses.md; specs/phases/phase-11-score-lives-bombs.md; specs/phases/phase-12-pause-music-settings.md; specs/phases/phase-06-world-1.md; specs/phases/phase-08-world-2.md
- type: api-contract
- content:
  - window.**GAME_TEST** (e2e builds only): getState() returns screen, selected entry, chosen ship and level (P01), then score, highScore, bombs, bonuses with kind (P11-R08), then paused, volumes, music track id, last sound effects (P12-R12); sendAction accepts menu actions, bomb, pause, resume. Later additions per decisions: step(frames, render?) and advance(seconds) (D-093, D-075); **SCENERY_TEST** and **SHOTS_TEST** for viewer pages.
  - Debug pages (production build includes them): player_ship/ (P02), player_shots/ (P03-R10), level_zero/ (D-020), enemies/ (P05-R11), bosses/ and boss/ (P07-R09).
  - Debug URL options on the game screen: ?level=N-M, t=<seconds>, ship=, boss=mini|final, weather=0, look=<time of day>; keys F (x4), left/right (10 s jumps), K (destroy next boss part). Ignored without debug options.

## Phase tunable values (selected)

- source: specs/phases/phase-01-main-menu.md; specs/phases/phase-05-first-enemies.md; specs/phases/phase-06-world-1.md; specs/phases/phase-07-bosses.md; specs/phases/phase-08-world-2.md; specs/phases/phase-10-world-4.md; specs/phases/phase-11-score-lives-bombs.md
- type: nfr
- content:
  - Menu: menu_transition_duration 250 ms; title_ship_rotation_speed 0.3 rad/s; title_city_scroll_speed 8 units/s; ship_select_rotation_speed 0.5 rad/s; level grid in P01 table still reads 5 x 5 (stale, see conflicts).
  - Player ships: speed factors 1 / 0.8 / 1.4, HP 100 / 140 / 80 (P02); base speed 100 px/s in P02 text, now 225 px/s (D-047). Weapons: bullet 10 damage, 8 shots/s; laser 80/140/200/260/320 dps; missile 14 damage, 4/s per stream.
  - Enemies (P05 table): Gnat 10 HP / 50 pts, Hornet 20/100, Scout 30/100, Strafer 40/150, Weaver 30/120, Spinner 60/200, Lancer 80/250, Rocketeer 100/300, Bulwark 200/500, Splitter 50/200 (pod 10/50), Carrier 300/600, Wasp 30/150, Mortar 140/400, Mantis 160/500, Phantom 90/450, Minelayer 120/400, Hydra 220/700, Orbiter 160/650, Scissor 240/800, Juggernaut 320/1 000; further columns listed in source.
  - World levels: World 1 240 s +/- 10 s, ground speed 70/65/60/60/60 px/s; Worlds 2-4 300 s +/- 10 s, ground speeds W2 70/65/60/55/60, W4 70/65/60/55/55. P06 enemy counts ~60..~140 and peaks 6..15 (overridden by D-044/D-051 measurements); bullet speed and fire-rate factors W1 0.8/0.85/0.9/1.0/1.1, W2 0.9/0.95/1.0/1.1/1.15, W4 1.1/1.15/1.2/1.3/1.35.
  - Bosses: mini 2-3 parts, final 4-6; speed ease 2 s; stage_change_pause 1 s; mini boss at 50 % of level; quiet_before_boss 10 s; boss_triangles <= 6 000; part drop chance 50 % mini / 60 % final; final core drop 100 %.
  - Score and bombs (P11): score_digits 7; boss_part_points_share 10 %; bombs_start 3, bombs_max 5; bomb_damage 100; bomb_duration 1 s; lives_start 3, lives_max 5; life_drop_chance 1 %; bomb_drop_chance 3 %; life_bonus_points 5 000; bomb_bonus_points 2 000.
  - Audio (P12): sfx_voices_max 16; music tempo ranges W1 128-140, W2 112-124, W3 120-132, W4 104-116 BPM; menu theme 100 BPM; boss tracks 20-30 BPM faster; weather limits: snow 1 500 flakes max, at most 3 lightning flashes in any 1 s.
