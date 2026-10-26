# 01 — Engineering requirements

> Applies to **every** phase. Each requirement has an ID (`ENG-xx`) and a priority:
> **MUST** (mandatory), **SHOULD** (expected unless justified in DECISIONS.md), **MAY** (optional).
> Values below are filled-in defaults: edit any of them freely.

---

## 0. Architecture summary

- **100 % client-side.** The game runs entirely in the browser. The server (GitHub Pages) only serves static files: no backend, no API, no server-side code.
- **Stack:** TypeScript (strict) + **Babylon.js** (3D engine) + Vite (build) + Vitest (unit) + Playwright (e2e).
- **Why Babylon.js** (see `DECISIONS.md` D-001): it is written in TypeScript and comes with everything this game needs:
  - PBR materials, shadow generators (PCF / cascaded), glow layer
  - a post-processing pipeline (bloom, tone mapping, FXAA)
  - CPU + GPU particle systems with ready-made fire / smoke / explosion presets
  - an audio engine, an in-browser inspector, a headless `NullEngine` for tests
  - WebGL2 with an optional WebGPU backend

  Three.js would need several third-party libraries to reach the same feature set.
- **Layers:** a pure, deterministic simulation (`core/`) runs at a fixed timestep. Presentation layers (`render/`, `fx/`, `audio/`, `ui/`) only *read* simulation state and react to simulation *events*.
- **Engine / game split** (§2.3): everything outside `src/game/` is a **game-agnostic engine** (abstract `Boss`, `Enemy`, `Weapon`, systems, rendering plumbing...). This game's actual content (the concrete bosses, enemies, weapons, levels, visuals, sounds and their tunables) lives in `src/game/`. Replacing `src/game/` is enough to build a different shoot 'em up on the same engine.

---

## 1. Tech stack

| ID | Priority | Requirement |
|----|----------|-------------|
| ENG-01 | MUST | Language: **TypeScript**, `strict: true`, plus `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitOverride`. No `.js` source files. |
| ENG-02 | MUST | 3D engine: **Babylon.js** (`@babylonjs/core`, ES modules, deep imports for tree-shaking). Extra packages allowed when needed: `@babylonjs/loaders` (glTF), `@babylonjs/materials`, `@babylonjs/inspector` (dev only). |
| ENG-03 | MUST | Bundler / dev server: **Vite**. |
| ENG-04 | MUST | Runtime / package manager: **Node.js 24 LTS** + **npm**, versions pinned via `.nvmrc` and `package.json#engines`. `package-lock.json` committed; installs use `npm ci`. |
| ENG-05 | MUST | Runtime dependencies kept to a minimum. Each new runtime dependency gets a `DECISIONS.md` entry (purpose, size, license). |
| ENG-06 | MUST | Supported browsers: last 2 versions of Chrome, Edge, Firefox and Safari on desktop, with WebGL2 required. Show a clear message when WebGL2 is unavailable. |
| ENG-07 | MUST | No backend: no server calls at runtime other than fetching static files from the same origin. Persistence (settings, high scores) uses `localStorage`. |
| ENG-08 | MAY | WebGPU backend used when available, with automatic fallback to WebGL2. |
| ENG-09 | MUST | Collision detection is custom and simple (sphere / AABB) inside `core/`. No physics engine unless a phase requires one. |

## 2. Project structure & code style

### 2.1 Directory layout (ENG-10 · MUST)

```
.
├── Makefile
├── index.html
├── public/                  # static files copied as-is
│   └── assets/
│       ├── models/          # .glb
│       ├── textures/        # .ktx2 / .webp, flipbooks for fire/smoke
│       ├── env/             # .env IBL environment maps
│       └── audio/           # .ogg / .mp3
├── src/
│   ├── main.ts              # bootstrap only: create engine, start app
│   ├── app/                 # game state machine (boot, title, play, pause, game over), wiring of layers
│   ├── core/                # PURE, GAME-AGNOSTIC simulation, no Babylon / DOM imports
│   │   ├── entities/        # abstract bases & interfaces: Entity, Player, Enemy, Boss, Bullet, Pickup, Weapon
│   │   ├── systems/         # movement, weapons, collision, spawning, scoring, damage
│   │   ├── events/          # typed event bus (EnemyDestroyed, PlayerHit, ...)
│   │   ├── math/            # vectors, seeded RNG, easing
│   │   ├── content/         # GameDefinition contract + registries that game/ fills
│   │   └── world.ts         # world state + fixed-step update(dt)
│   ├── render/              # Babylon scene, camera, lights, shadows, materials, post-processing, mesh sync
│   ├── fx/                  # particles, explosions, smoke, fire, trails, screen shake, hit flash
│   ├── audio/               # music & SFX, driven by core events
│   ├── input/               # keyboard / gamepad / touch → abstract actions
│   ├── ui/                  # HUD & menus (HTML/CSS overlay)
│   ├── assets/              # asset manifest, loaders, loading screen progress
│   ├── config/              # all tunables (gameplay values)
│   ├── platform/            # browser wrappers: storage, visibility, capabilities detection
│   ├── debug/               # inspector toggle, FPS/stats overlay, hitbox view (dev/e2e builds only)
│   └── game/                # THIS game's content, built on the engine above (§2.3)
│       ├── index.ts         # exports the single GameDefinition used by main.ts
│       ├── sim/             # PURE: concrete bosses, enemies, weapons, pickups, levels (extend core/)
│       ├── view/            # mesh / material / effect / sound definitions for the concrete content
│       └── config/          # game-specific tunables (enemy HP, boss patterns, scoring...)
├── tests/
│   ├── unit/                # mirrors src/ (tests/unit/core/systems/collision.test.ts)
│   ├── fixtures/            # minimal "sample game" used to test the engine without src/game/ (ENG-145)
│   ├── e2e/                 # Playwright specs
│   └── helpers/
├── docs/
│   └── architecture.md
└── .github/workflows/
```

### 2.2 Rules

| ID | Priority | Requirement |
|----|----------|-------------|
| ENG-11 | MUST | **Layering**, enforced by lint (`no-restricted-imports` / `import/no-restricted-paths`):<br>• `core/` imports only `core/` and `config/`. It never imports Babylon, the DOM, `window` or `performance`.<br>• `render/`, `fx/`, `audio/`, `ui/` may read `core/` state and subscribe to events. They never mutate core state.<br>• `input/` produces actions that `app/` passes to `core/`.<br>• Only `app/` and `main.ts` wire layers together. |
| ENG-12 | MUST | Linter: **ESLint** (flat config) with `typescript-eslint` `strict-type-checked` + `stylistic-type-checked`, plus `eslint-plugin-import`. **Zero warnings** (`--max-warnings 0`). |
| ENG-13 | MUST | Formatter: **Prettier**, config committed. ESLint must not conflict with it (`eslint-config-prettier`). |
| ENG-14 | MUST | Type checking: `tsc --noEmit` passes with zero errors. No `any` (lint error), no `@ts-ignore` (`@ts-expect-error` allowed only with a comment). |
| ENG-15 | MUST | Naming: files `kebab-case.ts`; classes/types `PascalCase`; functions/variables `camelCase`; constants `UPPER_SNAKE_CASE`. One main export per file. Named exports only (no `default`). |
| ENG-16 | SHOULD | Functions ≤ 50 lines, files ≤ 300 lines, cyclomatic complexity ≤ 10 (ESLint `max-lines-per-function`, `max-lines`, `complexity` as warnings → errors via `--max-warnings 0`). |
| ENG-17 | MUST | No magic numbers in gameplay code: engine tunables (timestep...) live in `src/config/`; game-specific tunables live in `src/game/config/` (ENG-143). |
| ENG-18 | MUST | Simulation determinism: `core/` uses a seeded RNG and receives `dt` from the loop. No `Math.random()` and no `Date.now()` in `core/` (lint rule). |
| ENG-19 | SHOULD | Hot paths (per-frame update of bullets, particles, enemies) use object pools and avoid allocations. |

### 2.3 Engine / game separation

Goal: the engine (everything outside `src/game/`) can be reused as a template for another game by replacing `src/game/` only.

| ID | Priority | Requirement |
|----|----------|-------------|
| ENG-140 | MUST | **Engine is game-agnostic.** Code outside `src/game/` contains no content specific to this game: no concrete boss, enemy, weapon, pickup or level; no game-specific names, assets, numbers or texts. It provides abstractions (abstract classes / interfaces such as `Entity`, `Enemy`, `Boss`, `Weapon`, `Pickup`, `Level`), generic systems, and generic presentation plumbing. |
| ENG-141 | MUST | **Content lives in `src/game/`.** Concrete classes (e.g. `class SerpentBoss extends Boss`) and level/wave definitions live in `src/game/sim/`; their visuals and sounds in `src/game/view/`. |
| ENG-142 | MUST | **Dependency direction**, enforced by lint (same mechanism as ENG-11):<br>• No file outside `src/game/` imports from `src/game/`, except `src/main.ts`, which imports only `src/game/index.ts`.<br>• `src/game/sim/` follows the same purity rules as `core/` (ENG-11, ENG-18) and imports only `core/`, `config/` and `game/sim/`, `game/config/`.<br>• `src/game/view/` may import `render/`, `fx/`, `audio/`, `ui/`, `assets/`, `core/` and `game/sim/`, `game/config/`. |
| ENG-143 | MUST | Game-specific tunables live in `src/game/config/`; game-specific assets are declared in a game manifest under `src/game/` that the engine's typed manifest (ENG-123) loads without knowing its contents. |
| ENG-144 | MUST | **Single entry point.** `src/game/index.ts` exports one `GameDefinition` object (type defined in `core/content/`) that registers all concrete content: entity factories, levels, view bindings, asset manifest, title and texts. `main.ts` passes it to `app/`. The engine discovers content only through this object (registries / factories), never by hard-coded imports. |
| ENG-145 | MUST | **Engine tested on its own.** Engine unit tests use a minimal sample game in `tests/fixtures/` (not `src/game/`), which proves the engine works with another game. Concrete content in `src/game/` has its own tests in `tests/unit/game/`. |
| ENG-146 | MUST | Coverage: `src/game/sim/**` uses the same thresholds as `src/core/**` (ENG-43). |
| ENG-147 | MUST | `docs/architecture.md` has a section "Making a new game from this template" that lists the steps (replace `src/game/`, implement `GameDefinition`, add assets) and is kept accurate. |
| ENG-148 | SHOULD | Abstract engine classes expose behaviour through overridable hooks (e.g. `Boss.onPhaseChange()`, `Boss.updatePattern(dt)`) and documented contracts (TSDoc, ENG-132), so new content needs no engine changes. When a phase needs an engine change to support new content, the change stays generic. |

## 3. Makefile

The Makefile is the single entry point for humans, git hooks and CI. CI calls **only** `make` targets.

| ID | Priority | Target | Behaviour |
|----|----------|--------|-----------|
| ENG-20 | MUST | `make help` | Default target. Lists targets with descriptions. |
| ENG-21 | MUST | `make install` | `npm ci` + installs git hooks + Playwright browsers (Chromium). |
| ENG-22 | MUST | `make dev` | Vite dev server with HMR on port **5173**, Babylon inspector available. |
| ENG-23 | MUST | `make build` | Production build into `dist/`. |
| ENG-24 | MUST | `make lint` | ESLint + Prettier check (no auto-fix). |
| ENG-25 | MUST | `make format` | Prettier write + ESLint `--fix`. |
| ENG-26 | MUST | `make typecheck` | `tsc --noEmit`. |
| ENG-27 | MUST | `make test` | Unit tests (Vitest), single run. |
| ENG-28 | MUST | `make test-watch` | Unit tests in watch mode. |
| ENG-29 | MUST | `make coverage` | Unit tests with coverage report; fails below thresholds (ENG-43). |
| ENG-30 | MUST | `make e2e` | Builds in `e2e` mode, serves it, runs Playwright. |
| ENG-31 | MUST | `make check-fast` | `lint` + `typecheck` + `test`. Used by the pre-push hook. |
| ENG-32 | MUST | `make check` | **Full gate**: `lint` + `typecheck` + `coverage` + `build` + `e2e`. Used by CI and by the agent before every report. |
| ENG-33 | SHOULD | `make preview` | Serves the production build locally. |
| ENG-34 | SHOULD | `make clean` | Removes `dist/`, `coverage/`, test reports and caches. |
| ENG-35 | MAY | `make e2e-ui` | Playwright UI mode for debugging. |
| ENG-36 | MAY | `make size` | Prints bundle size and fails above budget (ENG-82). |

## 4. Unit testing & coverage

| ID | Priority | Requirement |
|----|----------|-------------|
| ENG-40 | MUST | Framework: **Vitest** + `@vitest/coverage-v8`. |
| ENG-41 | MUST | Test-driven: tests are written before or together with the implementation of each requirement. |
| ENG-42 | MUST | Each phase requirement ID appears in at least one test name, e.g. `it("P03-R02: enemy dies after 3 hits")`. |
| ENG-43 | MUST | Coverage thresholds:<br>• `src/core/**`: **90 %** lines / **85 %** branches / **90 %** functions / **90 %** statements<br>• whole `src/` (with ENG-45 exclusions): **70 %** lines. |
| ENG-44 | MUST | Coverage never decreases between phases (the agent reports old vs. new numbers). |
| ENG-45 | MUST | Excluded from coverage: `src/main.ts`, `src/debug/**`, and pure GPU/visual configuration in `src/render/**` and `src/fx/**` (shaders, post-process setup). Logic inside those folders (pooling, mapping events to effects) stays covered. |
| ENG-46 | MUST | Deterministic tests: seeded RNG, injected clock / `dt`. No real timers (`vi.useFakeTimers()` when needed). |
| ENG-47 | SHOULD | Scene-level code in `render/` and `fx/` is tested with Babylon's **`NullEngine`** (headless) where it makes sense (e.g. "an explosion is spawned when `EnemyDestroyed` fires"). |
| ENG-48 | SHOULD | Unit tests run in < 30 s total. |

## 5. End-to-end testing

| ID | Priority | Requirement |
|----|----------|-------------|
| ENG-50 | MUST | Framework: **Playwright**, Chromium project (WebGL through SwiftShader/ANGLE in headless CI). |
| ENG-51 | MUST | E2E runs against the **built** app (`vite build --mode e2e` + static preview server), never against the dev server. |
| ENG-52 | MUST | **Test API**: in `e2e` mode only, the game exposes `window.__GAME_TEST__` with `getState()`, `setSeed(n)`, `step(frames)`, `pause()`, `sendAction(action)`. It is absent from the production bundle (checked by an e2e or build test). |
| ENG-53 | MUST | Every e2e test fails on any browser console error or uncaught exception. |
| ENG-54 | MUST | Minimum smoke suite: page loads → loading completes → title screen visible → start game → player moves and shoots (asserted through the test API) → pause/resume → game over → back to title. |
| ENG-55 | SHOULD | Each phase adds e2e tests for its user-visible requirements (also named with their ID). |
| ENG-56 | MAY | Visual regression screenshots of fixed-seed paused frames, with a tolerance threshold. Disabled by default because GPU output differs between machines. |
| ENG-57 | MUST | On failure, Playwright traces, screenshots and video are kept as CI artefacts. |

## 6. Git hooks (pre-commit)

| ID | Priority | Requirement |
|----|----------|-------------|
| ENG-60 | MUST | Hooks managed by **Husky**, installed automatically by `make install` (`prepare` script). |
| ENG-61 | MUST | `pre-commit`: **lint-staged** → Prettier + ESLint `--fix` on staged files, then `make typecheck`. |
| ENG-62 | — | *Removed (2026-10-22): no commit-msg hook. Commit messages still follow ENG-90, without automated enforcement.* |
| ENG-63 | MUST | `pre-push`: `make check-fast`. |
| ENG-64 | MUST | The agent never bypasses hooks (`--no-verify` is forbidden). If a hook fails, fix the cause. |
| ENG-65 | SHOULD | Hooks finish in under 15 s on a typical commit. |

## 7. CI (GitHub Actions)

| ID | Priority | Requirement |
|----|----------|-------------|
| ENG-70 | MUST | Workflow `ci.yml` runs on push to `main` and on every pull request. |
| ENG-71 | MUST | Job `check`: `make install` → `make lint typecheck coverage build`. |
| ENG-72 | MUST | Job `e2e` (parallel to `check`): `make install` → `make e2e`. Playwright browsers cached. |
| ENG-73 | MUST | CI fails on any lint error, type error, failing test or coverage below threshold. |
| ENG-74 | MUST | Runner: `ubuntu-latest`, Node version from `.nvmrc`; npm cache enabled. |
| ENG-75 | MUST | Artefacts uploaded: coverage report (HTML), Playwright report (on failure). |
| ENG-76 | SHOULD | Coverage summary written to the job summary (`$GITHUB_STEP_SUMMARY`). |
| ENG-77 | SHOULD | Dependabot enabled for npm and GitHub Actions (weekly). |
| ENG-78 | MAY | `npm audit --audit-level=high` step. |
| ENG-79 | MAY | CI and deploy status badges in README. |

## 8. Deployment (GitHub Pages)

| ID | Priority | Requirement |
|----|----------|-------------|
| ENG-80 | MUST | Workflow `deploy.yml` deploys to GitHub Pages with the official `actions/upload-pages-artifact` + `actions/deploy-pages`. |
| ENG-81 | MUST | Trigger: push to `main`, **after** CI succeeds (`workflow_run` or a `needs:` dependency). Also allows a manual `workflow_dispatch`. |
| ENG-82 | MUST | Works under the sub-path `https://<user>.github.io/<repo>/`: Vite `base` is set from the repo name, and all asset URLs are relative to `import.meta.env.BASE_URL`. |
| ENG-83 | MUST | Version + short commit hash shown on the title screen (injected at build time). |
| ENG-84 | SHOULD | Hashed filenames for JS/CSS (Vite default), so new deploys are never served stale from cache. |
| ENG-85 | MAY | PR preview deployments: no (GitHub Pages doesn't support them natively). |

## 9. Git workflow

| ID | Priority | Requirement |
|----|----------|-------------|
| ENG-90 | MUST | Commit convention: **Conventional Commits** (`feat:`, `fix:`, `test:`, `refactor:`, `chore:`, `docs:`, `ci:`), scope = layer or phase (`feat(core): ...`, `test(p03): ...`). |
| ENG-91 | MUST | One branch per phase: `phase-NN`, created from up-to-date `main`. |
| ENG-92 | MUST | The agent may commit on the phase branch and push it. It does **not** merge to `main` until `/validate-phase N`. |
| ENG-93 | MUST | On validation: squash-merge `phase-NN` into `main`, push, tag `v0.NN.0`. |
| ENG-94 | SHOULD | Small, focused commits during a phase (one per task or requirement), each passing the pre-commit hook. |

## 10. Rendering, graphics & performance

| ID | Priority | Requirement |
|----|----------|-------------|
| ENG-100 | MUST | Fixed-timestep simulation at **60 Hz**, with rendering at display rate and interpolation between simulation states. Logic is independent of the monitor's refresh rate. |
| ENG-101 | MUST | Target **60 FPS** at 1080p on a mid-range laptop with an integrated GPU (Intel Iris Xe / Apple M1 class). |
| ENG-103 | MUST | Graphics feature set available to phases:<br>• PBR materials, image-based lighting (`.env`), directional and point lights<br>• shadow generator (PCF, or cascaded on High)<br>• glow layer for emissive parts (engines, bullets)<br>• `DefaultRenderingPipeline` (bloom, ACES tone mapping, FXAA, optional chromatic aberration and grain)<br>• particle systems: GPU particles with CPU fallback, flipbook textures for fire, smoke and explosions. |
| ENG-104 | MUST | Many identical objects (bullets, debris) use **thin instances** or instancing, not one mesh each. |
| ENG-105 | MUST | Particle and effect instances are pooled; the active-particle budget per preset is enforced by `fx/`. |
| ENG-106 | SHOULD | Draw-call budget: < 200 draw calls per frame on Medium. Shown in the debug overlay. |
| ENG-107 | SHOULD | Bundle budget: initial JS ≤ **1.5 MB gzip**. Total download before the title screen ≤ **15 MB**; level assets load later. |
| ENG-108 | MUST | Loading screen with real progress while assets load. |
| ENG-109 | MUST | No errors or warnings in the browser console during normal play. |
| ENG-110 | MUST | Handles window resize, device pixel ratio (capped at 2), tab visibility (auto-pause when hidden) and WebGL context loss (show a message and offer a reload). |
| ENG-111 | SHOULD | Debug overlay (FPS, frame time, draw calls, active entities and particles, hitboxes) toggled with **F3**. Babylon inspector on **F4**. Both only in dev and e2e builds. |
| ENG-112 | SHOULD | Accessibility: remappable keys, a "reduce flashes & screen shake" option, colour-blind-friendly bullet colours, master/music/SFX volume sliders. |

## 11. Assets & licensing

| ID | Priority | Requirement |
|----|----------|-------------|
| ENG-120 | MUST | Formats: models **glTF binary (`.glb`)**; textures **KTX2 (Basis)** or WebP; environment maps Babylon `.env`; audio **OGG** with MP3 fallback. |
| ENG-121 | MUST | Allowed sources: procedurally generated (in code); CC0 packs (e.g. Kenney, Quaternius, Poly Haven); CC-BY only with attribution. No unclear licenses. |
| ENG-122 | MUST | Every third-party asset listed in `CREDITS.md` (name, author, source URL, license). |
| ENG-123 | MUST | Assets are referenced through a typed manifest (`src/assets/manifest.ts`). No string paths scattered in code. |
| ENG-124 | SHOULD | Asset size budget per model ≤ 2 MB, per texture ≤ 1 MB. |
| ENG-125 | MUST | Project license: **MIT** (`LICENSE` file). |

## 12. Documentation

| ID | Priority | Requirement |
|----|----------|-------------|
| ENG-130 | MUST | `README.md`: link to the live game, controls, requirements (Node version), and the `make` targets. |
| ENG-131 | MUST | `docs/architecture.md`: layers, data flow (input → core → events → render/fx/audio/ui) and the game loop. Updated whenever a phase changes the architecture. |
| ENG-132 | SHOULD | Public functions and types in `core/` have TSDoc comments. |
| ENG-133 | MUST | `CREDITS.md` kept up to date (ENG-122). |

## Free-form notes
<!-- Anything else about code that doesn't fit above. -->
