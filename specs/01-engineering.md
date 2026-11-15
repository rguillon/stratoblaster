# Engineering

> **Area:** engineering · **Prefix:** `ENG` · **Related:** [performance.md](performance.md),
> [dev/test-api.md](dev/test-api.md), [dev/perf-tools.md](dev/perf-tools.md),
> [dev/debug-options.md](dev/debug-options.md), [ui/boot-and-loading.md](ui/boot-and-loading.md),
> [ui/settings.md](ui/settings.md), [DECISIONS.md](DECISIONS.md), [TRACEABILITY.md](TRACEABILITY.md)

How the game is built, checked, tested and shipped: the stack, the source layout and its layering,
the split between the reusable engine and this game's content, the Makefile, the unit and end-to-end
tests, the git hooks, CI, deployment, the git workflow, the engineering rules of rendering, assets and
documentation, and the rules Python code must follow to compile with Transcrypt and to run the same
way in the browser and under CPython. It applies to all code. It does not set the game's frame rate,
loading times or freezes (see [performance.md](performance.md)), nor the dev menu, viewers and debug
keys (see [dev/](dev/)).

Each requirement has an ID (`ENG-xx`) and a priority: **MUST** (mandatory), **SHOULD** (expected
unless a decision says why not), **MAY** (optional). The IDs keep the numbers of the phase-based
`01-engineering.md`; a removed requirement keeps its row, marked *Removed* with the date and the
reason. Values are defaults the owner may change; the main ones are listed under
[Tunable values](#tunable-values).

## Requirements

### 0. Architecture summary

- **100 % client-side.** The game runs entirely in the browser. GitHub Pages only serves static
  files: `index.html`, the bundled game (`js/game.js`), the ground worker (`js/ground_worker.js`) and
  the vendored Babylon.js (`vendor/babylon.js`). No backend, no API, no server-side code.
- **Stack:** Python 3.12 (typed, `mypy --strict`) compiled to JavaScript by **Transcrypt** 3.9.5 and
  bundled by **esbuild** (Node, in `node/`, a build step only); **Babylon.js** 9 (its UMD build) for
  3D, called through JavaScript interop from `render/` only; **uv** for the environment and every
  Python command; **pytest** for the unit tests (run in CPython); **pytest-playwright** (Chromium)
  for the end-to-end tests.
- **Why Babylon.js** (D-001, kept by D-169): it comes with what the game draws with (PBR materials,
  shadow generators, glow layers, tone mapping, thin instances, material plugins) and more (a
  post-processing pipeline, particle systems, an inspector, a WebGPU backend). Three.js would need
  several third-party libraries to reach the same feature set.
- **Layers:** a pure, deterministic simulation (`core/`, and the game's `game/sim/`) runs at a fixed
  timestep. The presentation (`render/`, `ui/`, `audio/`, `game/view/`) only *reads* the simulation's
  state after each step, including the lists of what happened in that step.
- **Engine / game split** (§2.3): everything outside `src/game/` is a **game-agnostic engine**
  (abstract `Enemy`, `Boss`, weapons as data, systems, rendering plumbing). This game's content (the
  concrete enemies, bosses, weapons, levels, visuals, sounds and their tunables) lives in
  `src/game/`. Replacing `src/game/` is enough to build a different shoot 'em up on the same engine.
- **Two runtimes, one source:** the browser runs the Transcrypt output; the unit tests run the same
  modules in CPython (§14).

### 1. Tech stack

| ID | Priority | Requirement | Sources |
|----|----------|-------------|---------|
| ENG-01 | MUST | Language: **Python 3.12**, fully type-annotated, checked by `mypy --strict` (ENG-14). Transcrypt compiles it to JavaScript; the browser runs the output with no Python runtime. The rules Transcrypt needs are in §13 and §14. `src/` holds Python only: no `.ts` or `.js` source file. JavaScript appears only inside `__pragma__("js", ...)` blocks (ENG-158). The only tracked TypeScript is the read-only reference suite in `node/tests/` (ENG-10), which nothing builds, lints or runs. | ENG-01, P18-R07, D-169, D-187, D-188 |
| ENG-02 | MUST | 3D engine: **Babylon.js**, the pinned UMD build `babylon.js` of the `babylonjs` npm package (version and SHA-256 in the Makefile: `BABYLON_VERSION`, `BABYLON_SHA256`). The `babylon` step downloads it from jsDelivr into `public/vendor/` when it is missing or wrong and checks its SHA-256; on a mismatch it fails and leaves nothing behind. The file is git-ignored, never committed. `index.html` loads it as a classic script before the game module. Only `babylon.js` is vendored: the game uses no glTF loader, materials library or inspector build. Python reaches Babylon only through `render/` (ENG-113). | ENG-02, P18-R04, D-169, D-173, D-174 |
| ENG-03 | MUST | Compiler and bundler: **Transcrypt** (pinned, `transcrypt==3.9.5` in `pyproject.toml`) compiles the Python entries into ES modules under `build/`; **esbuild** (pinned exactly in `node/package.json`) bundles each entry into one minified file under `dist/js/` (ENG-23, ENG-150), so the page makes one request for the game instead of one per module. There is no dev server and no hot reload: `make serve` rebuilds and serves `dist/` (ENG-22). | ENG-03, P17-R02, D-169, D-171, D-176 |
| ENG-04 | MUST | Toolchain: **Python 3.12** (`.python-version`; `requires-python = ">=3.12,<3.13"`) and **uv**, which fetches Python and runs every Python command. `uv.lock` is committed; installs use `uv sync --locked`. Python 3.13 and later are not supported (ENG-154). **Node.js** (the major version in `node/.nvmrc`: 24) and npm are needed for the bundling step only; every Node file is under `node/` (`package.json`, `package-lock.json`, `.nvmrc`) and is installed with `npm ci --prefix node`. A clean clone reaches a working toolchain with one command (`make setup`, ENG-21). | ENG-04, P17-R01, P18-R07, D-169, D-176, D-187, D-189 |
| ENG-05 | MUST | Dependencies are kept to a minimum. The game has no Python run-time dependency (`dependencies = []`) and one JavaScript library, Babylon.js. Dev tools are in the uv `dev` group and, for Node, in `node/` (esbuild only). A small piece of own code is preferred to a new library (for example the own ear-clipping triangulation instead of `earcut`, a generated environment map instead of a downloaded `.env` file). Each new Python dependency and each vendored JavaScript library gets a decision entry (purpose, size, license).<br>**Discrepancy:** D-173 (Babylon.js) gives its purpose and size (8.7 MB) but not its license (Apache-2.0). | ENG-05, D-005, D-173 |
| ENG-06 | MUST | Supported browsers: the last 2 versions of Chrome, Edge, Firefox and Safari on desktop, with WebGL2 required. Without WebGL2 the page shows a clear message instead of the game (`host/webgl_support.py`, the game's `texts.unsupported` shown in `#fatal`). | ENG-06 |
| ENG-07 | MUST | No backend: at run time the page fetches only static files from its own origin (the bundle, the worker script, Babylon.js). Persistence (high score, volumes, saved supplies…) uses **cookies**, not `localStorage`: `host/cookie_storage.py`, behind the `KeyValueStorage` shape, writes `max-age` (`MENU_CONFIG.cookie_max_age_days`) and `SameSite=Lax`; keys are prefixed with the game's id (`stratoblaster_high_score`). Switching storage is one new `KeyValueStorage` class. | ENG-07, D-010, D-326 |
| ENG-08 | MAY | WebGPU backend used when available, with automatic fallback to WebGL2.<br>**Not implemented:** `render/babylon.py::new_engine` always creates a WebGL `BABYLON.Engine`. | ENG-08 |
| ENG-09 | MUST | Collision detection is custom and simple, inside `core/`: circles (every `ShotTarget` has a radius) and beam segments. No physics engine unless a requirement asks for one. | ENG-09, D-015 |

### 2. Project structure and code style

#### 2.1 Directory layout (ENG-10 · MUST)

```
.
├── Makefile                 # the single entry point (§3)
├── pyproject.toml           # project, dev group; ruff, mypy, import-linter, pytest, coverage config
├── uv.lock
├── .python-version          # 3.12
├── .pre-commit-config.yaml  # git hooks (§6)
├── .editorconfig
├── index.html               # page shell: loads vendor/babylon.js, then js/game.js, calls main()
├── public/                  # static files copied as-is into dist/
│   └── vendor/              # pinned Babylon.js build (the `babylon` step; git-ignored)
├── node/                    # Node tooling only: esbuild (package.json, package-lock.json, .nvmrc)
│   └── tests/               # read-only TypeScript reference tests (not built, linted or run)
├── src/
│   ├── main.py              # bootstrap of the game page: WebGL check, engine, app
│   ├── worker_main.py       # entry of the ground worker
│   ├── build_info.py        # version and commit, written by `make build-info` (git-ignored)
│   ├── app/                 # game flow and wiring: menus, levels, loading steps, HUD, pause, dev viewer
│   ├── core/                # PURE, GAME-AGNOSTIC simulation, no Babylon / DOM imports
│   │   ├── content/         # GameDefinition, GameLevel, level catalog, menu texts: the contract game/ fills
│   │   ├── entities/        # abstract bases: Enemy, Boss and its parts, weapons as data, ShotTarget, PlayerShip
│   │   ├── systems/         # LevelRun, ShotWorld, EnemyWorld, wave runner, flight, hits, bombs, bonuses
│   │   ├── scenery/         # generated levels: terrain, roads, streets, districts, props, sky
│   │   ├── menu/            # menu screens and grid cursor
│   │   ├── math/            # seeded RNG, 32-bit helpers, noise, colour, heap
│   │   └── loop/            # fixed-step clock
│   ├── render/              # Babylon plumbing: babylon.py, geometry/, environment/, scenery/, pools, layers
│   ├── ui/                  # DOM HUD, menus and screens
│   ├── audio/               # Web Audio engine: synth, sequencer, sample bank, music and SFX players, cues
│   ├── input/               # keyboard / gamepad / touch → menu actions and controls
│   ├── assets/              # the start-up loading tasks
│   ├── config/              # engine tunables (ENGINE_CONFIG, menus, controls, scenery stage, weather…)
│   ├── host/                # browser wrappers: cookie storage, WebGL check, worker data (not "platform")
│   ├── debug/               # the e2e test API (e2e builds only, ENG-52)
│   └── game/                # THIS game's content, built on the engine above (§2.3)
│       ├── index.py         # GAME: the single GameDefinition used by main.py
│       ├── sim/             # PURE: concrete enemies, bosses, levels, builders from the config
│       ├── view/            # models, materials, effects, sounds of the concrete content
│       └── config/          # game tunables (enemies, bosses, weapons, scoring, looks), world_1..world_4
├── tests/
│   ├── unit/                # mirrors src/ (tests/unit/core/math/test_color.py), ENG-49
│   ├── e2e/                 # pytest-playwright tests; conftest.py serves dist-e2e/
│   ├── fixtures/            # sample_game/: a minimal GameDefinition of its own (ENG-145)
│   └── helpers/             # fakes (Babylon, DOM, audio), sample levels, builders;
│                            # typings/: mypy stubs of the Transcrypt browser stub
├── docs/
│   └── architecture.md
├── README.md, CREDITS.md, LICENSE
└── .github/                 # workflows/ci.yml, workflows/deploy.yml, dependabot.yml
```

Generated, git-ignored: `build/` (Transcrypt output), `dist/`, `dist-e2e/`, `coverage/`,
`.coverage`, `test-results/`, `.make/` (install and compile stamps).

The browser wrappers package is `host/`, not `platform/`: with `src/` on the import path a package
named `platform` shadows the standard library module.

**Discrepancy:** the layout of the phase-based spec listed folders that were never built: `fx/`
(effects are drawn by `render/` and `game/view/`), `core/events/` (there is no event bus, ENG-11),
`core/world.py`, `public/assets/` (the only asset files are the sound samples in `public/sfx/`,
ENG-126), `src/assets/manifest.py` (ENG-123) and `tests/fixtures/` (ENG-145).

*Sources: ENG-10, D-172, D-176, D-187, D-188, D-189, D-190.*

#### 2.2 Rules

| ID | Priority | Requirement | Sources |
|----|----------|-------------|---------|
| ENG-11 | MUST | **Layering**:<br>• `core/` imports only `core/`, `config/` and the standard library (`math`; `typing` and `collections.abc` for annotations). It never imports Babylon, the DOM or the Transcrypt browser stub (`org`, `browser`), nor `random`, `time` or `datetime` (ENG-18). Its one use of the stub is `__pragma__`, a compile-time marker: each `core/` module that imports it is named in the `ignore_imports` of the import-linter contract, and any other import of `org` or `browser` from `core/` fails `make lint`.<br>• `render/`, `ui/` and `audio/` read the core state after each step, including its lists of what happened in that step (blasts, impacts, hits, bonuses picked), and never change it. There is no event bus.<br>• `input/` turns devices into actions (menu actions, `LevelControls`) that `app/` passes to `core/`.<br>• Only `app/` and `main.py` wire layers together; nothing else imports `app/`.<br>Each rule is an import-linter contract in `pyproject.toml`, checked by `make lint`.<br>**Discrepancy:** only the core purity contract exists ("core/ is pure: no browser or DOM"). The other rules, and those of ENG-142, hold in the code today (import scan of 2026-11-01), but no contract checks them. | ENG-11, P17-R04, P18-R05, D-003, D-171 |
| ENG-12 | MUST | Linter: **Ruff** (`ruff check src`; rule sets E, F, W, I, UP, B, SIM, N, PL, C90, TID; `PLR0913` off; `PLR2004` off in `tests/`) plus the import-linter contracts. **Zero findings** (non-zero exit on any finding). | ENG-12, D-169 |
| ENG-13 | MUST | Formatter: **ruff format** (line length 100), config committed in `pyproject.toml`. `make lint` only checks formatting (`ruff format --check`); `make format` and the pre-commit hook write it. | ENG-13 |
| ENG-14 | MUST | Type checking: `mypy --strict` over `src/` (stubs in `tests/helpers/typings/`) passes with zero errors. `Any` is used only for what mypy cannot type: JavaScript handles (Babylon objects, DOM elements, raw JavaScript values, ENG-113) and config records (`game/config/record.py`). Every `# type: ignore[code]` and every `# noqa: CODE` gives its reason in the same comment (the `# noqa: E402` after a `skip` block is explained once by the comment above the block).<br>**Discrepancy:** on 2026-11-01, `src/` has 19 `# type: ignore[...]` and about 270 other `# noqa` with no reason (170 of them `# noqa: E711`, ENG-161). | ENG-14, D-174, D-191 |
| ENG-15 | MUST | Naming: modules `snake_case.py`; classes `PascalCase`; functions and variables `snake_case`; constants `UPPER_SNAKE_CASE`. One main public name per module. No wildcard imports. Config record keys stay camelCase (`maxRadius`, `entrySpeed`): they are data the browser reads as object fields (`# noqa: N802` where a class declares one). | ENG-15, D-188 |
| ENG-16 | SHOULD | Functions ≤ 50 lines, modules ≤ 300 lines, cyclomatic complexity ≤ 10 (ruff `C90`, max-complexity 10), at most 6 arguments (`max-args`).<br>**Discrepancy:** only complexity, statements and arguments are checked; on 2026-11-01, 48 functions are over 50 lines and 61 of 628 modules over 300 lines (the longest: `game/view/bosses/boss_armour.py`, 840; `render/babylon.py`, 788). | ENG-16 |
| ENG-17 | MUST | No magic numbers in gameplay code: engine tunables live in `src/config/` (`ENGINE_CONFIG`, …), game tunables in `src/game/config/` (ENG-143). Ruff `PLR2004` flags them (off in tests, where a literal is the expected value). | ENG-17 |
| ENG-18 | MUST | Simulation determinism: `core/` and `game/sim/` use the seeded RNG (`core/math/rng.py`, mulberry32 on unsigned 32-bit integers) and receive `dt` from the loop. Ruff's `banned-api` forbids `random`, `time` and `datetime` in all of `src/`. | ENG-18, P17-R03 |
| ENG-19 | SHOULD | Hot paths (per-frame shots, particles, enemies, scenery chunks) reuse objects instead of allocating: node pools (`render/node_pool.py`), thin-instance buffers that grow by powers of two, pooled projectiles in `ShotWorld`. | ENG-19, D-015 |

#### 2.3 Engine / game separation

Goal: the engine (everything outside `src/game/`) can be reused as a template for another game by
replacing `src/game/` only.

| ID | Priority | Requirement | Sources |
|----|----------|-------------|---------|
| ENG-140 | MUST | **Engine is game-agnostic.** Code outside `src/game/` contains no content specific to this game: no concrete enemy, boss, weapon, bonus or level; no game-specific names, numbers or texts. It provides abstractions (`Enemy`, `Boss`, `ShotTarget`, weapon definitions, `GameLevel`, `GameDefinition`), generic systems and generic presentation plumbing. | ENG-140 |
| ENG-141 | MUST | **Content lives in `src/game/`.** Concrete classes (e.g. `class Hornet(Enemy)` in `game/sim/enemies/hornet.py`) and the levels, waves and bosses live in `game/sim/` and `game/config/`; their models, effects and sounds in `game/view/`. | ENG-141 |
| ENG-142 | MUST | **Dependency direction**, enforced by lint (the mechanism of ENG-11):<br>• No module outside `src/game/` imports `src/game/`, except `src/main.py`, which imports only `game/index.py`.<br>• `game/sim/` follows the purity rules of `core/` (ENG-11, ENG-18) and imports only `core/`, `config/`, `game/sim/` and `game/config/`.<br>• `game/config/` imports only `game/config/`.<br>• `game/view/` may import `render/`, `audio/`, `ui/`, `assets/`, `config/`, `core/`, `game/sim/` and `game/config/`.<br>**Discrepancy:** no import-linter contract checks these rules; they hold in the code today (see ENG-11). | ENG-142, P18-R05, D-003 |
| ENG-143 | MUST | Game-specific tunables live in `src/game/config/`. The game's file assets (the sound samples, ENG-126) are declared in a game manifest under `src/game/` (the sound designs) that the engine loads by name without knowing their contents (ENG-123). | ENG-143 |
| ENG-144 | MUST | **Single entry point.** `src/game/index.py` exports one `GameDefinition` (`GAME`; the type is in `core/content/game_definition.py`) that registers all the content: id and title, logical screen, player ships and weapons, the level catalog and the playable levels, enemy and boss kinds, the rules of boss fights, bonuses, bombs and hull, the menu texts, and the view bindings (ship models, shot renderers, title backdrop, scenery, enemy, bonus and bomb renderers, audio, outline). `main.py` passes it to `app/` (`start_app`). The engine finds content only through this object (registries and factories), never by importing `src/game/`. | ENG-144, D-015, D-036 |
| ENG-145 | MUST | **Engine tested on its own.** Engine unit tests (all of `tests/unit/` except `tests/unit/game/`) build their content by hand with the small helpers of `tests/helpers/` (a sample scenery level, a menu game, level builders, fakes), not from `src/game/`. A minimal sample game (a `GameDefinition` of its own) in `tests/fixtures/` proves the engine works with another game. Content in `src/game/` has its own tests in `tests/unit/game/`. | ENG-145 |
| ENG-146 | MUST | Coverage: `src/game/sim/**` has the same threshold as `src/core/**` (ENG-43): both are held to the 100 % of the whole of `src/`. | ENG-146 |
| ENG-147 | MUST | `docs/architecture.md` has a section "Making a new game from this template" that lists the steps (replace `src/game/`, implement `GameDefinition`, provide the view bindings and tunables) and is kept accurate.<br>**Discrepancy:** the section does not exist. | ENG-147 |
| ENG-148 | SHOULD | Abstract engine classes expose behaviour through overridable hooks and documented contracts (docstrings, ENG-132), so new content needs no engine change: `Enemy.update(ctx, dt)`, `on_destroyed(ctx)`, `expires`, `rammable`, `drop_chance` and the `_hit_targets` / `_shot_targets` hooks; `Boss.enter`, `move`, `update_pattern` and its stage and transformation hooks. `EnemyContext` gives an enemy what it may do: read the player's position, fire bullets, homing missiles and lasers, spawn enemies, explode, break a part. Everything the player's shots, beams, homing missiles and the ship's collisions can hit is a `ShotTarget`; an enemy made of several (a boss's parts and core) lists them in `hit_targets`, and those proxies decide whether damage counts (a core shielded by its parts, a boss not yet in place), so shots, collisions and views need no boss-specific code. When new content needs an engine change, the change stays generic. | ENG-148, D-032, D-053 |
| ENG-149 | SHOULD | Content is data wherever the engine can run it, so changing the numbers needs no code change: player weapons are definitions (projectile streams per level, or beam levels) run by the pure `ShotWorld` (`core/systems/shot_world.py`); a playable level is a `GameLevel` (a scenery level, a wave script, an enemy difficulty, its bosses) run by the pure `LevelRun` (`core/systems/level_run.py`), whose wave runner queues groups once the scroll distance passes them and knows enemy kinds only by id. Enemies and bosses with their own state machines are classes on the hooks of ENG-148. | D-015, D-032, D-036 |

### 3. Makefile

The Makefile is the single entry point for people, git hooks and CI. CI calls **only** `make` targets.

| ID | Priority | Requirement | Sources |
|----|----------|-------------|---------|
| ENG-20 | MUST | `make help`: the default target. Lists the public targets (ENG-37) with their descriptions (target names may contain digits: `e2e`). | ENG-20, D-219 |
| ENG-21 | MUST | `make setup`: checks the tools (ENG-38), then installs everything: `uv sync --locked`, `npm ci --prefix node`, Babylon.js (ENG-02), Chromium for Playwright (`SKIP_BROWSER=1` leaves it out; on CI, `--with-deps --only-shell`), and the git hooks (`pre-commit install` for the pre-commit and pre-push stages, ENG-60). It was called `make install`. | ENG-21, P17-R01, D-018, D-195, D-219 |
| ENG-22 | MUST | `make serve`: builds the production game (`make build`) and serves `dist/` on port **5173** (`SERVE_PORT`) with Python's `http.server`. Rebuild to see changes; no hot reload, no Babylon inspector (D-173). It was called `make dev`. | ENG-22, ENG-33, D-173 |
| ENG-23 | MUST | `build` step (`make build`): Transcrypt compiles `main.py` into `build/game/` and `worker_main.py` into `build/worker/` (ENG-150); esbuild bundles them, minified, into `dist/js/game.js` and `dist/js/ground_worker.js`; `index.html` and `public/` (with `vendor/babylon.js`) are copied into `dist/`. It fails if a compiler pragma call (`__pragma__(`) or the test API (`__GAME_TEST__`, ENG-52) is found in `dist/js/game.js`. | ENG-23, P17-R02, D-011, D-171, D-176, D-195 |
| ENG-24 | MUST | `lint` step: `ruff check src`, `ruff format --check src` and `lint-imports` (no auto-fix). | ENG-24 |
| ENG-25 | MUST | `format` step: `ruff format src` + `ruff check --fix src`. | ENG-25 |
| ENG-26 | MUST | `typecheck` step: `mypy` (strict, configured in `pyproject.toml`). | ENG-26 |
| ENG-27 | — | *Removed (2026-11-01): there is no unit-test target without coverage; `make tests` (ENG-29) runs the unit tests and the coverage gates together.* | ENG-27 |
| ENG-28 | — | *Removed (2026-11-01): no watch-mode target; the uv dev group has no watch plugin.* | ENG-28 |
| ENG-29 | MUST | `make tests`: the unit tests (pytest over `tests/unit/`, in CPython, on every core with pytest-xdist: `UNIT_WORKERS`, default `auto`) with coverage, branches included: a terminal report (the modules below 100 %, with their missed lines and branches) and `coverage/coverage.xml`. Fails on a failing test or below the threshold of ENG-43. It replaces `make test` and `make coverage`. | ENG-27, ENG-29, P18-R06, D-184, D-186, D-191, D-232 |
| ENG-30 | MUST | `make e2e`: makes the e2e build (`e2e-build`, ENG-51), installs Chromium if needed, and runs pytest-playwright over `tests/e2e/` on `E2E_WORKERS` workers (default 4). `E2E_ARGS` passes pytest options (`-k smoke`); `E2E_SHARD=K/N` runs one slice (ENG-59). Failures keep their traces, screenshots and videos (ENG-57). | ENG-30, D-195, D-219 |
| ENG-31 | MUST | `check-fast` step: `lint` + `typecheck`. Used by the pre-push hook. The unit tests are not part of it (they take minutes, against the hooks' budget of ENG-65); `make check` and CI run them. | ENG-31 |
| ENG-32 | MUST | `make check`: the **full gate**: `lint`, `typecheck`, `tests` (with the coverage gates), `build`, `e2e`. CI runs the same steps across its jobs (ENG-71, ENG-72); the agent runs it before validation. | ENG-32, D-195 |
| ENG-33 | — | *Removed (2026-11-01): `make serve` (ENG-22) serves the production build, so there is no separate preview target.* | ENG-33 |
| ENG-34 | SHOULD | `clean` step: removes `dist/`, `dist-e2e/`, `build/`, `coverage/`, `.coverage`, `test-results/`, `src/__target__/` and the tool caches (`.mypy_cache`, `.ruff_cache`, `.pytest_cache`). | ENG-34, D-094, D-186 |
| ENG-35 | — | *Removed (2026-11-01): Playwright's UI mode belongs to its Node runner; the Python suite takes pytest-playwright options through `E2E_ARGS` (e.g. `--headed`).* | ENG-35 |
| ENG-36 | MAY | `make size`: prints the bundle sizes and fails above budget (ENG-107).<br>**Not implemented.** | ENG-36 |
| ENG-37 | MUST | Public and step targets: the public targets are `setup`, `check`, `tests`, `e2e`, `serve` and `help`, the only ones `make help` lists and `README.md` documents. `lint`, `typecheck`, `format`, `check-fast`, `build`, `e2e-build`, `build-info`, `babylon`, `check-tools` and `clean` are steps: they work on their own and are called by the public targets, the git hooks and CI, but are not listed. | ENG-20, Makefile (owner, 2026-10-31) |
| ENG-38 | MUST | Every install and build step first checks the tools (`uv`, `node`, `npm`, `curl`, `git`, and `sha256sum` or `shasum`) and that Node's major version is the one in `node/.nvmrc`. A missing tool is named, with where to get it, before anything is installed. | ENG-04, Makefile (owner, 2026-10-31) |
| ENG-39 | SHOULD | The steps are incremental and safe under `make -j`: the install steps re-run only when their inputs change (stamps in `.make/`: `uv sync` after `pyproject.toml` or `uv.lock`, `npm ci` after `node/package*.json`, Playwright after `uv sync`); Transcrypt recompiles only when a Python source changed (`build/.stamp`, `build/.stamp-e2e`); Babylon.js is downloaded only when missing or wrong; `build-info` is an order-only prerequisite, so `src/build_info.py` is written before Transcrypt reads it. CI runs `make -j3 e2e`, which compiles the two Transcrypt builds side by side. | D-176, D-219 |

### 4. Unit testing and coverage

| ID | Priority | Requirement | Sources |
|----|----------|-------------|---------|
| ENG-40 | MUST | Framework: **pytest** with **coverage.py** (pytest-cov) and pytest-xdist. Tests run in CPython on the same `src/` modules as the browser (`pythonpath = ["src", "tests"]`); `tests/unit/conftest.py` puts Transcrypt's browser stubs (`org`) last on `sys.path`, so the standard library still wins. No browser is needed (ENG-160). | ENG-40, D-184, D-191 |
| ENG-41 | MUST | Test-driven: tests are written before or together with the implementation of each requirement. | ENG-41 |
| ENG-42 | MUST | Each requirement ID appears in at least one test name, lower case with underscores (`def test_enm_hornet_03_follows_the_s_path():`), as `README.md` says. | ENG-42 |
| ENG-43 | MUST | Coverage threshold: **100 %** of the whole of `src/` (with the ENG-45 exclusions), as the coverage.py total with branch coverage on (lines and branches counted together): `fail_under = 100` in `pyproject.toml`, so `make tests` fails on any line or branch no unit test runs. Code no test can reach is removed or restructured, never excluded: no `# pragma: no cover`, no `exclude_lines` (D-236). coverage.py has no function metric, so the old function and statement thresholds are gone. | ENG-43, P18-R06, D-184, D-191, D-236 |
| ENG-44 | MUST | Coverage never decreases from one change merged into `main` to the next; the agent reports the old and new numbers. | ENG-44 |
| ENG-45 | MUST | Excluded from coverage: only the entry points and the generated module, `src/main.py`, `src/worker_main.py` and `src/build_info.py` (`[tool.coverage.run] omit`). Every other module is measured, including the ones no test imports (`source = ["src"]`), `debug/` and the `*_visual.py` Babylon wiring (ENG-114). | ENG-45, D-003, D-191 |
| ENG-46 | MUST | Deterministic tests: seeded RNG, injected clock / `dt`. No real timers. | ENG-46 |
| ENG-47 | SHOULD | Code that touches Babylon, the DOM or Web Audio is tested under CPython against fakes: the `render.babylon` helpers replaced by recording `MagicMock`s (`tests/helpers/babylon_stub.py`, `render_fakes.py`), the DOM by `tests/helpers/dom.py`, audio by `tests/helpers/audio_fakes.py`. Babylon's `NullEngine` is not used: Babylon does not run under CPython. | ENG-47, D-009, D-174, D-191 |
| ENG-48 | SHOULD | Unit tests run in under 30 s in total on a developer machine, spread over every core (`UNIT_WORKERS=auto`). A suite that slows down is a defect to find in the code under test and fix there, with the same answers computed faster, not a budget to raise.<br>**Discrepancy:** about 29 s on 8 workers after D-232; on the CI runner, under coverage, the suite took about 3 minutes before D-227 and 20 after it, and no CI time is recorded since D-232. | ENG-48, D-232 |
| ENG-49 | SHOULD | One test file per source module, at the mirrored path (`tests/unit/core/math/test_color.py` tests `src/core/math/color.py`); a module's tests are not spread over several files, and a test file does not test several modules. Shared helpers live in `tests/helpers/`. pytest imports with `--import-mode=importlib`, because source modules share basenames. | D-190 |

### 5. End-to-end testing

| ID | Priority | Requirement | Sources |
|----|----------|-------------|---------|
| ENG-50 | MUST | Framework: **Playwright** through **pytest-playwright** (Python), Chromium (the headless shell on CI); WebGL through SwiftShader in headless runs. | ENG-50, D-195 |
| ENG-51 | MUST | E2E runs against the **built** e2e game, never a dev server: `make e2e-build` copies `dist/` into `dist-e2e/` and puts the e2e bundle in its `js/game.js`; `tests/e2e/conftest.py` serves `dist-e2e/` on a free local port for the session. | ENG-51, D-195 |
| ENG-52 | MUST | **Test API**: in e2e builds only, the game exposes `window.__GAME_TEST__` (`src/debug/test_api.py`: `getState()`, `sendAction(action)`, `step(frames, render)`, `advance(seconds)`, `readability(share)`; see [dev/test-api.md](dev/test-api.md)). `main.py` imports and installs it inside `__pragma__("ifdef", "e2e")` blocks, compiled in only with the Transcrypt symbol `e2e` (`E2E = True`). `make build` fails if `__GAME_TEST__` is in the production bundle; `make e2e-build` fails if it is missing from the e2e bundle. | ENG-52, D-011, D-075, D-093, D-175, D-195 |
| ENG-53 | MUST | Every e2e test fails on any browser console error, any uncaught exception, and any audio warning (autoplay, a context that could not start): the autouse `console_errors` fixture of `tests/e2e/conftest.py`. | ENG-53, D-195 |
| ENG-54 | MUST | Minimum smoke suite: page loads → loading completes → title screen visible → start a game (level select) → the player moves and shoots (asserted through the test API) → pause / resume, and a hidden page pauses → game over → back to the title. | ENG-54, P18-R03, D-095, D-326 |
| ENG-55 | SHOULD | Each user-visible requirement gets e2e tests, named with its ID (ENG-42). | ENG-55 |
| ENG-56 | MAY | Visual regression screenshots of fixed-seed paused frames, with a tolerance threshold; disabled by default, because GPU output differs between machines.<br>**Not implemented.** | ENG-56 |
| ENG-57 | MUST | On failure, Playwright traces, screenshots and videos are kept (`--tracing retain-on-failure --screenshot only-on-failure --video retain-on-failure --output test-results`) and uploaded as CI artefacts (`playwright-results-K`, one per CI job). | ENG-57, D-195, D-219 |
| ENG-58 | MUST | E2E tests never wait on real time. E2E builds start no render loop: nothing moves until a test steps the app by whole 1/60 s frames (`step`, `advance`), so every run sees the same frames in the same order. The helpers (`tests/e2e/menu_helpers.py`) step without drawing and draw only the frames a test looks at (`wait_for_load`, `step_until`, the readability probe). E2E builds also draw fewer pixels: half the resolution across and no multisampling (`ENGINE_CONFIG.e2e`), no shader precompilation, no level built ahead: the tests read the game's state, not its pixels. | D-075, D-093, D-195, D-219 |
| ENG-59 | SHOULD | The e2e tests share no state, so they run in parallel: `make e2e` spreads them over `E2E_WORKERS` pytest-xdist workers, each with its own browser, and `--shard K/N` (`tests/e2e/conftest.py`) keeps every N-th test from the K-th in collection order, so that the cases of one parametrised test land in different CI jobs. | D-018, D-195, D-219 |

### 6. Git hooks (pre-commit)

| ID | Priority | Requirement | Sources |
|----|----------|-------------|---------|
| ENG-60 | MUST | Hooks are managed by **pre-commit** (from the uv dev group, `.pre-commit-config.yaml`), installed by `make setup` for the pre-commit and pre-push stages. | ENG-60, D-169 |
| ENG-61 | MUST | `pre-commit`: `ruff format` and `ruff check --fix` on the staged Python files, then `make typecheck`. | ENG-61 |
| ENG-62 | — | *Removed (2026-10-22): no commit-msg hook. Commit messages still follow ENG-90, without automated enforcement.* | ENG-62 |
| ENG-63 | MUST | `pre-push`: `make check-fast`. | ENG-63 |
| ENG-64 | MUST | The agent never bypasses hooks (`--no-verify` is forbidden). If a hook fails, fix the cause. | ENG-64 |
| ENG-65 | SHOULD | Hooks finish in under 15 s on a typical commit. | ENG-65, D-094 |
| ENG-66 | SHOULD | Hooks and `check-fast` lean on the tools' own sound caches (ruff's `.ruff_cache`, mypy's incremental `.mypy_cache`); `make clean` removes them. The full gate (`make check`, and CI on a fresh runner) checks every file. | D-094 |
| ENG-67 | SHOULD | The hooks run the project's own locked tools (local hooks, `language: system`: `uv run ruff …`, `make typecheck`, `make check-fast`), so a hook and the gate always use the same versions and configuration. | ENG-60, ENG-61 |

### 7. CI (GitHub Actions)

| ID | Priority | Requirement | Sources |
|----|----------|-------------|---------|
| ENG-70 | MUST | Workflow `ci.yml` runs on push to `main` and on every pull request; a newer run on the same ref cancels the older one. | ENG-70 |
| ENG-71 | MUST | Two code jobs, neither compiling with Transcrypt nor installing a browser: `lint` ("code check": `make lint typecheck`) and `unit` (`make tests`, with the coverage gates). The game is built in each e2e job (`make e2e` runs `make build` and its checks, ENG-23). Each target installs what it needs (ENG-39): there is no separate install step. | ENG-71, D-018, D-186, D-219 |
| ENG-72 | MUST | E2E: a matrix of 4 jobs (`fail-fast` off), in parallel with the code jobs, each running `make -j3 e2e E2E_SHARD=K/4` (ENG-59), with the Playwright browser cache (`~/.cache/ms-playwright`, keyed on `uv.lock`) and the npm cache. | ENG-72, D-018, D-186, D-195, D-201, D-219 |
| ENG-73 | MUST | CI fails on any lint error, type error, failing unit or e2e test, coverage below a threshold, or failed build check. | ENG-73 |
| ENG-74 | MUST | Runner: `ubuntu-latest`. uv from `astral-sh/setup-uv`; uv itself fetches the Python version of `.python-version` / `requires-python`; uv cache enabled. Node from `actions/setup-node` with `node/.nvmrc` (the Makefile checks it, ENG-38). Tags are fetched, for the version on the title (ENG-83).<br>**Note:** `ci.yml` does not set the uv cache itself; it relies on the action's default. | ENG-74, D-186 |
| ENG-75 | MUST | Artefacts uploaded: the coverage report (`coverage/coverage.xml`, always) and the Playwright results of failed e2e tests (ENG-57). | ENG-75, D-186, D-219 |
| ENG-76 | SHOULD | The coverage summary (the report of the whole of `src/`) is written to the job summary (`$GITHUB_STEP_SUMMARY`). | ENG-76, D-186 |
| ENG-77 | SHOULD | Dependabot is enabled, weekly, for the Python dev tools (`uv`), npm in `node/` (esbuild) and GitHub Actions (grouped).<br>**Discrepancy:** `.github/dependabot.yml` watches npm (`/node`) and GitHub Actions only; there is no `uv` entry, so ruff, mypy, pytest and the other dev tools are not watched. | ENG-77, D-189 |
| ENG-78 | MAY | `pip-audit` on `uv.lock` (high severity and above).<br>**Not implemented.** | ENG-78 |
| ENG-79 | MAY | CI and deploy status badges in `README.md`.<br>**Not implemented.** | ENG-79 |

### 8. Deployment (GitHub Pages)

| ID | Priority | Requirement | Sources |
|----|----------|-------------|---------|
| ENG-80 | MUST | Workflow `deploy.yml` builds with `make build` and deploys `dist/` to GitHub Pages with the official `actions/upload-pages-artifact` + `actions/deploy-pages`; deployments do not overlap (`concurrency: pages`). | ENG-80, D-186 |
| ENG-81 | MUST | Trigger: a CI run on a push to `main` that **succeeded** (`workflow_run`); it deploys the commit CI checked (`head_sha`). A manual `workflow_dispatch` is also allowed. | ENG-81 |
| ENG-82 | MUST | Works under the sub-path `https://<user>.github.io/<repo>/`: every URL is relative (`vendor/babylon.js`, `./js/game.js`; the worker's is relative to its module), so no base path is configured. | ENG-82, D-003 |
| ENG-83 | MUST | The version and the short commit hash are shown on the title screen, written at build time: `make build-info` writes the git-ignored `src/build_info.py` (`APP_VERSION`: the latest release tag without its `v`, or `unknown` without one; `APP_COMMIT`: the short hash). | ENG-83, D-175 |
| ENG-84 | SHOULD | Cache busting: the build adds the short commit hash to the script URLs (`js/game.js?v=<hash>`), so a new deploy is never served stale from a cache.<br>**Discrepancy:** not done: `index.html` loads `vendor/babylon.js` and `./js/game.js` without a version query, and the worker URL has none either. | ENG-84 |
| ENG-85 | MAY | PR preview deployments: no (GitHub Pages doesn't support them natively). | ENG-85 |

### 9. Git workflow

| ID | Priority | Requirement | Sources |
|----|----------|-------------|---------|
| ENG-90 | MUST | Commit convention: **Conventional Commits** (`feat:`, `fix:`, `test:`, `refactor:`, `perf:`, `chore:`, `docs:`, `ci:`), scope = layer or area (`feat(core): …`, `fix(view): …`).<br>**Discrepancy:** the squash-merge commits on `main` take the pull request's title (`Feat/ship glow boss transform (#38)`), not the convention; the commits inside the branches follow it. | ENG-90 |
| ENG-91 | MUST | One branch per piece of work, created from up-to-date `main`: `phase-NN` for a phase, `<type>/<topic>` otherwise (`feat/forest-imposters`, `fix/title-commit-sha`, `perf/e2e-speed`, `docs/specs-by-function`). | ENG-91 |
| ENG-92 | MUST | The agent may commit on its branch and push it. It does **not** merge to `main` until the owner validates the work. | ENG-92 |
| ENG-93 | MUST | On validation: squash-merge the branch into `main` (through its pull request), push, and tag the release (`v0.NN.0` for phase NN). The title shows the latest tag (ENG-83).<br>**Discrepancy:** the latest tag, locally and on `origin`, is `v0.15.0`: the `v0.16.0` that `PROGRESS.md` records for phase 16 does not exist, so the current game shows version 0.15.0. | ENG-93, D-188 |
| ENG-94 | SHOULD | Small, focused commits (one per task or requirement), each passing the pre-commit hook. | ENG-94 |

### 10. Rendering and performance (engineering rules)

The frame rate, loading times and freezes players feel are in [performance.md](performance.md).

| ID | Priority | Requirement | Sources |
|----|----------|-------------|---------|
| ENG-100 | MUST | Fixed-timestep simulation at **60 Hz** (`ENGINE_CONFIG.simulation_hz`), rendering at display rate, with interpolation between simulation states (the scroll distance by the clock's `alpha`). At most 5 steps per rendered frame (`max_steps_per_frame`); after a stall the time beyond them is dropped (`core/loop/fixed_step_clock.py`). Logic is independent of the monitor's refresh rate. | ENG-100, D-003 |
| ENG-101 | MUST | Target **60 FPS** at 1080p on the reference machine: a mid-range laptop with an integrated GPU (Intel Iris Xe / Apple M1 class). How it is measured, and the budgets that follow from it (loading, long frames, the busiest districts), are in [performance.md](performance.md) (PERF-01, PERF-19, PERF-32). **Gap:** never measured on the reference machine (only software WebGL). | ENG-101 |
| ENG-102 | — | *Removed (2026-10-26, by the reviewer): quality presets Low / Medium / High (shadow map size, particle budget, post-processing, MSAA, render scale) are not part of the game.* | ENG-102, D-020, D-095 |
| ENG-103 | MUST | The game renders with the vendored Babylon build alone (no other rendering library): PBR and standard materials, image-based lighting from a generated cube map (no `.env` file), directional and hemispheric lights, a shadow generator, glow layers for emissive parts, ACES tone mapping, thin instances and material plugins. Effects (explosions, laser particles, weather) are the game's own seeded particles drawn as meshes, not Babylon particle systems, so they need no texture. Babylon's `DefaultRenderingPipeline`, cascaded shadows and GPU particles stay available but are not used. | ENG-103, D-005, D-015 |
| ENG-104 | MUST | Many identical objects (bullets, blast particles, trees, cars) use **thin instances** or instancing, not one mesh each. | ENG-104 |
| ENG-105 | MUST | Particle and effect nodes are pooled (`render/node_pool.py`, thin-instance buffers), and each effect caps its live particles (for example the per-layer `cap` of the blasts, `ENEMY_LOOK.blasts.cap` in `game/config/enemy_look.py`; the weather's particle counts in `config/weather.py`). There is no `fx/` layer: the renderers in `render/` and `game/view/` enforce their caps. | ENG-105 |
| ENG-106 | SHOULD | Draw-call budget: under 200 draw calls per frame in play, shown in the debug perf overlay.<br>**Discrepancy:** draw calls are counted nowhere: the perf overlay (F3) shows frame and load times, and the stats tile (F2) shows the FPS and the triangles drawn. | ENG-106 |
| ENG-107 | SHOULD | Bundle budget: the JavaScript loaded before the title screen is at most **1.5 MB gzip**; the total download before the title screen is at most **15 MB**; level content is generated later, not downloaded.<br>**Discrepancy:** measured on the build of 2026-11-01: `vendor/babylon.js` 8.7 MB (1.89 MB gzip) and `js/game.js` 1.14 MB (0.36 MB gzip) make about 2.2 MB gzip of JavaScript before the title, over budget; the total (about 10 MB) is within budget. Nothing checks it (ENG-36). | ENG-107, D-001, D-173 |
| ENG-108 | — | *Removed (2026-11-01): moved to [ui/boot-and-loading.md](ui/boot-and-loading.md) (the loading screen and its progress) and [performance.md](performance.md) (loading times).* | ENG-108 |
| ENG-109 | MUST | No errors or warnings in the browser console during normal play (ENG-53 checks the errors and the audio warnings in every e2e test). | ENG-109 |
| ENG-110 | MUST | Handles window resize (the stage is fitted to the window, `ui/stage_fit.py`), the device pixel ratio (capped at 2, `ENGINE_CONFIG.max_device_pixel_ratio`, and the canvas never drawn at more than `ENGINE_CONFIG.max_render_scale` pixels per logical pixel, 1920 × 1080 for the 1280 × 720 screen: a 4K panel is drawn at full HD and upscaled, D-250), tab visibility and window focus (the level pauses when the page is hidden or the window loses its focus, `app/page_audio.py::PageVisibility`) and WebGL context loss (a message in `#fatal` asks the player to reload). | ENG-110 |
| ENG-111 | SHOULD | Debug overlays never show unless asked for: the perf overlay (long frames, longest frame, last load, longest load step) toggles with **F3** in e2e (and dev) builds only; `DEV_BUILD` is off, as there is no separate dev build. The FPS / triangles tile shows with **F2** in any level, or with the URL's debug options. Details in [dev/perf-tools.md](dev/perf-tools.md). The Babylon inspector (the old F4) is not available: it is not vendored (D-173). | ENG-111, D-173, D-175, D-195, D-212 |
| ENG-112 | SHOULD | Accessibility: remappable keys, a "reduce flashes and screen shake" option, colour-blind-friendly bullet colours, master / music / SFX volume sliders (see [ui/settings.md](ui/settings.md)).<br>**Discrepancy:** only the music and SFX volume sliders exist. The key bindings are in config (`config/game_controls.py`, `config/menu_input.py`) but cannot be remapped in the game; there is no master volume and no reduce-flashes option; the bullet colours are checked for contrast (see [graphics/readability.md](graphics/readability.md)), not for colour blindness. | ENG-112, D-095 |
| ENG-113 | SHOULD | `render/babylon.py` is the only module that names the `BABYLON` global. Every Babylon object is made by one of its functions (`vector3`, `new_standard_material`, `create_torus`, …), constructors and builders with option objects in raw JavaScript there (ENG-158). Other modules hold Babylon objects as opaque handles (typed `Any`) and use their methods and properties by attribute; adding a Babylon call means adding one helper there.<br>**Discrepancy:** `render/scenery/imposter_bake_visual.py` builds a `BABYLON.RenderTargetTexture` itself. | D-169, D-174 |
| ENG-114 | SHOULD | Babylon wiring that needs a real WebGL context lives in small `*_visual.py` modules; the pure parts they use (geometry, gradients, layouts) are separate modules, unit-tested on their numbers. | D-003, D-005, D-174 |

### 11. Assets and licensing

| ID | Priority | Requirement | Sources |
|----|----------|-------------|---------|
| ENG-120 | MUST | Formats of file assets (ENG-126): sound effects **OGG (Vorbis)** with an **MP3** fallback, both shipped; if other assets are ever added: models **glTF binary (`.glb`)**; textures **KTX2 (Basis)** or WebP; environment maps Babylon `.env`. | ENG-120 |
| ENG-121 | MUST | Allowed sources: generated in code; CC0 packs (e.g. Kenney, Quaternius, Poly Haven); CC-BY only with attribution. No unclear licenses. | ENG-121 |
| ENG-122 | MUST | Every third-party asset is listed in `CREDITS.md` (name, author, source URL, license). Today the table lists the sound effect samples (29 sounds from two CC0 packs); the README repeats the packs and their authors. | ENG-122, D-261 |
| ENG-123 | MUST | File assets, if any, are referenced through a typed manifest (`src/assets/manifest.py`), never by string paths scattered in code. The only file assets are the sound samples: they are named once each by the sound designs of the game (`src/game/view/audio/sound_designs.py`, the game manifest of ENG-143), and the engine fetches them by name through one function (`fetch_sample` in `main.py`); there is no model or texture file, and `src/assets/` holds the start-up loading tasks. The other files the code fetches are named once each: `vendor/babylon.js` and `js/game.js` in `index.html`, `ground_worker.js` in `render/scenery/background_loader.py`. | ENG-123, D-261 |
| ENG-124 | SHOULD | Asset size budget: at most 2 MB per model and 1 MB per texture and 100 KB per sound effect sample (`public/sfx/` is about 630 KB today, no model or texture file). | ENG-124 |
| ENG-125 | MUST | Project license: **MIT** (`LICENSE`, `pyproject.toml` `license`). | ENG-125 |
| ENG-126 | SHOULD | The game ships no model, texture, environment-map or music file: models are built in code, textures and the lighting environment are generated at run time (a procedural cube map, atlases), and the music is synthesised with Web Audio. The sound effects are CC0 samples (AUD-ENGINE-01). `public/` holds the vendored Babylon.js and `sfx/`. | GD-60, D-005, D-097, D-261 |

### 12. Documentation

| ID | Priority | Requirement | Sources |
|----|----------|-------------|---------|
| ENG-130 | MUST | `README.md`: link to the live game, controls, requirements (Python 3.12 and uv, GNU Make, Node.js and npm for the bundling step) and the public `make` targets. | ENG-130 |
| ENG-131 | MUST | `docs/architecture.md`: the layers, the data flow (input → core → per-step state → render / ui / audio), the game loop, the worker, the build and the tests. Updated whenever a change alters the architecture or the tooling.<br>**Discrepancy:** it has the layers, the worker, the build and the tests, but no data flow and no game loop, and it is stale: it names `make vendor` and `make coverage` (now the `babylon` step and `make tests`), says there are no browser checks in CI (the e2e jobs run there), and points to `node/tests/` for tests still to port. | ENG-131, D-189 |
| ENG-132 | SHOULD | Public functions and classes in `core/` have docstrings that state their contract.<br>**Discrepancy:** 181 of the 719 public classes and functions of `core/` have none (count of 2026-11-01). | ENG-132 |
| ENG-133 | MUST | `CREDITS.md` is kept up to date (ENG-122). | ENG-133 |
| ENG-134 | SHOULD | Comments and docstrings describe the code as it is, in the present tense. They do not cite removed code (the TypeScript game, deleted pages) or tell the history of a port; what still explains the code stays.<br>**Discrepancy:** about 20 comments in `src/` still compare with the TypeScript (for example "as in the TS" in `render/babylon.py::new_engine`, the docstring of `game/config/record.py`). | D-188 |

### 13. Python for Transcrypt

Measured with Transcrypt 3.9.5 (D-170) and found since. Transcrypt compiles a Python subset, so these
rules apply to every module of `src/`. Where a lint rule would rewrite the workaround, the line
carries `# noqa: CODE (reason)`.

| ID | Priority | Requirement | Sources |
|----|----------|-------------|---------|
| ENG-150 | MUST | Transcrypt 3.9.5 (pinned) compiles, with `-b -n`, `src/main.py` and every module it imports, `src/worker_main.py` (the ground worker, which `main.py` does not import, so it needs its own entry) and, with the symbol `e2e`, `main.py` again for the e2e build, each into its own folder under `build/` (a second run in the same folder deletes the first). esbuild then bundles and minifies them (ENG-23). `index.html` imports `main` from `./js/game.js` and calls `main()`. | ENG-150, P17-R02, D-176, D-195 |
| ENG-151 | MUST | **No keyword arguments in calls.** Transcrypt 3.9.5 drops them silently: `add(4, scale=3)` returns the default-argument result. Pass arguments by position (constructors with many fields carry `# noqa: PLR0917 (positional: …)`). | ENG-151, D-170 |
| ENG-152 | MUST | **No `%` string formatting** (it compiles to `NaN`) and **no list repetition** (`[x] * n` compiles to the number `x * n`): build strings with `+` and `str()`, lists with comprehensions or loops. Unsigned 32-bit arithmetic (`>>>`, `^`, `Math.imul`) goes through the helpers of `core/math/bits.py`, which are raw JavaScript with a Python twin (ENG-160). | ENG-152, D-170, D-184 |
| ENG-153 | MUST | **Names that exist only for mypy** (`typing`, the `collections.abc` imports, `TypeVar`s, type aliases) are imported or defined inside `__pragma__("skip")` … `__pragma__("noskip")` blocks, because Transcrypt has no `typing` module at run time; the imports after such a block carry `# noqa: E402`. Browser globals come from `from org.transcrypt.stubs.browser import …` (`from browser import …` does not compile), typed by `tests/helpers/typings/org/transcrypt/stubs/browser.pyi`; in `core/` only `__pragma__` (ENG-11). | ENG-153, D-170, D-171, D-189 |
| ENG-154 | MUST | **Python 3.12 only** (ENG-04): Transcrypt 3.9.5 fails to compile its own runtime under later versions (measured with Python 3.14). | ENG-154, P17-R01, D-170 |
| ENG-155 | MUST | **Lists are joined with `extend` or a helper**, never with `+` (it compiles to JavaScript's `+`, which joins arrays as a string) nor with a `*` spread in a list literal (Transcrypt drops it): `compose_parts.concat`, `sound_recipes.flatten_layers` in `game/view/audio/`. | D-170 |
| ENG-156 | MUST | **Names Transcrypt renames** are never used as Python attribute names on JavaScript objects: a parameter or attribute `name` becomes `py_name`, and JavaScript members such as `name`, `update`, `from`, `length` and `items` are read, written or called through raw-JavaScript helpers (`render/babylon.py::node_name`, `update_raw_cube_texture`) or by subscript (`raw["name"]` in the `game/sim/*_build.py` mapping modules). | D-170, D-174 |
| ENG-157 | SHOULD | **Hot loops are plain loops.** In code that runs per frame or many times per level load (geometry tests, placement, scenery chunks, colour helpers), tests are written as `for` loops with early exits, not `any()` / `all()` over a generator (Transcrypt runs those through a slow Python iterator), comparisons replace the `min` and `max` builtins, and no closure or comprehension is created per item. Such lines carry `# noqa: SIM110` or `PLR1730` with the reason. | D-182, D-212, D-233 |
| ENG-158 | MUST | **Raw JavaScript** is limited to small helper functions: their body is a `__pragma__("js", "{}", …)` block and a placeholder Python return, their docstring gives the JavaScript they stand for (`` `new Engine(canvas, antialias, …)` ``), and they build JavaScript objects and option objects there (a Python dict is not a JavaScript object, and keyword arguments are dropped). Transcrypt cannot subclass a JavaScript class: such subclasses (a `MaterialPluginBase`) are made in raw JavaScript and call back into Python methods. | D-170, D-174 |
| ENG-159 | MUST | **Dicts, maps and sorting:** a Python dict is iterated with explicit `.keys()` or `.items()` (`for k in d` is broken under Transcrypt), the keys of a config record (a plain JavaScript object) are read with `keys_of` (`game/sim/config_access.py`), maps keyed by objects are JavaScript `WeakMap`s (`new_weak_map`) or lists compared by identity, and a dict never holds the key `__proto__`. Transcrypt's `sort` is unstable and takes no comparator, so order-sensitive code sorts with the stable helpers (`core/scenery/ordering.py::stable_sort_by`). | D-174 |

### 14. One source, two runtimes

The browser runs the Transcrypt output; the unit tests run the same modules in CPython (ENG-40).
These rules keep the two in step.

| ID | Priority | Requirement | Sources |
|----|----------|-------------|---------|
| ENG-160 | MUST | Every module of `src/` imports and runs under CPython. A raw-JavaScript helper (ENG-158) that a test reaches has a Python twin in a `skip` block with the browser's semantics (32-bit wrap, truncating `%`, own-key tests, `Object.keys` order). The game's config tables are records (`game/config/record.py`), read by attribute in both runtimes. | D-184, D-191, D-193 |
| ENG-161 | MUST | **An absent value is `undefined` in the browser** (a field a config record leaves out, an index past a list's end), not `None`. Code that may meet one tests it with `== None` / `!= None` (JavaScript's `== null`, true for both; `# noqa: E711 (reason)`), or reads it through `opt` / `maybe` (`game/sim/config_build.py`, `config_access.py`). The `game/sim/*_build.py` mapping modules turn config records into `core/` objects whose optional fields are `None`, so `core/` may test `is None`. | D-192, D-196 |
| ENG-162 | MUST | **Containers are tested by size**, never by truthiness: an empty list or dict is truthy in JavaScript, so emptiness is `len(x) == 0`, not `not x`. | D-195 |
| ENG-163 | SHOULD | A defect a test finds is fixed in the source, so that both runtimes agree, even when only CPython showed it (an infinity floored, `range` of a float). A known defect may be recorded for a while as a strict `xfail` with its reason; the suite has no expected failure when a change is validated, and no test is skipped or loosened to pass. | D-185, D-192, D-193 |
| ENG-164 | MUST | **Messages to and from the ground worker carry plain data only**: each side copies what it posts with `host/worker_data.py::to_plain` (objects and arrays, with their shared references, without functions or class markers), because a Transcrypt object cannot be structured-cloned (its own `__class__` is a function). | D-177 |

## Tunable values

| Name | Value | Where |
|------|-------|-------|
| Python | 3.12 (not 3.13+) | `.python-version`, `pyproject.toml` `requires-python` |
| Transcrypt | 3.9.5 | `pyproject.toml` `[dependency-groups] dev` |
| Babylon.js | 9.32.0, SHA-256 `58c486be…ab37a5` | `Makefile` `BABYLON_VERSION`, `BABYLON_SHA256` |
| Node.js / esbuild | 24 / 0.28.2 | `node/.nvmrc`, `node/package.json` |
| Ruff line length, complexity, arguments | 100, 10, 6 | `pyproject.toml` `[tool.ruff]`, `mccabe`, `pylint` |
| Coverage gate | `src/` 100 %, lines and branches | `pyproject.toml` `[tool.coverage.report] fail_under` |
| Unit test workers | `auto` (one per core) | `Makefile` `UNIT_WORKERS` |
| E2E workers / CI e2e jobs | 4 / 4 | `Makefile` `E2E_WORKERS`; `.github/workflows/ci.yml` matrix |
| Serve port | 5173 | `Makefile` `SERVE_PORT` |
| Simulation rate | 60 Hz | `src/config/engine.py` `ENGINE_CONFIG.simulation_hz` |
| Steps per frame, at most | 5 | `ENGINE_CONFIG.max_steps_per_frame` |
| Device pixel ratio cap | 2 | `ENGINE_CONFIG.max_device_pixel_ratio` |
| Render scale cap | 1.5 pixels per logical pixel (1920 × 1080) | `ENGINE_CONFIG.max_render_scale`, `ui/stage_fit.py` `render_ratio` (D-250) |
| E2E render scale / antialiasing | 0.5 / off | `ENGINE_CONFIG.e2e` |
| Perf overlay key / refresh | F3 / 0.25 s | `ENGINE_CONFIG.perf_overlay` |
| Stats tile key | F2 | `src/config/game_play.py` `GAME_PLAY_CONFIG` (`DebugStats`) |
| Cookie lifetime | 365 days | `src/config/menu.py` `MENU_CONFIG.cookie_max_age_days` |
| Hook time budget | 15 s | ENG-65 |
| Unit test time budget | 30 s | ENG-48 |
| Draw calls per frame | < 200 | ENG-106 |
| JavaScript before the title / total download | 1.5 MB gzip / 15 MB | ENG-107 |
| Model / texture size | 2 MB / 1 MB | ENG-124 |

## Notes

- **History.** The game was written in TypeScript with Vite, Vitest, ESLint, Prettier and Husky
  (D-001, D-002, D-019, D-094) up to `v0.15.0`, then ported to Python with Transcrypt and uv
  (phases 17 and 18, D-169 to D-176). The TypeScript sources are gone (D-188); `node/tests/` keeps
  their tests as a reference. The one-off port requirements (module-by-module port, parity scripts
  against the TypeScript output) are done and not carried over.
- **Requirement IDs in tests.** The tests still carry the phase-based IDs (`test_p06_r02_…`,
  `test_eng_54_…`); [TRACEABILITY.md](TRACEABILITY.md) maps them to the new IDs until they are
  renamed (ENG-42).
- **Smoke suite (ENG-54).** Its steps are spread over several files: `tests/e2e/test_smoke.py`
  (loading, title, start, pause and resume, hidden page, back to the title), `test_world_1.py` (the
  ship flies over 1-1 and shoots) and `test_score_bombs.py` (game over, continue).
- **Test API (ENG-52).** The `setSeed(n)` and `pause()` of the phase-based text were never built:
  pausing goes through `sendAction("pause")` (D-011, D-195).
