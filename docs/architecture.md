# Architecture

The game is Python 3.12 (`src/`), compiled to JavaScript by Transcrypt and bundled by esbuild. The
3D engine is Babylon.js, reached only through `render/babylon.py` (ENG-113). The requirements are in
[`specs/`](../specs/); `specs/01-engineering.md` §2 holds the layout rules this page summarises.

## Layers

The engine and the game are separate (ENG-142). `make lint` checks the import direction with
import-linter (the contracts in `pyproject.toml`).

| Layer      | Path            | What it holds                                                                |
| ---------- | --------------- | ---------------------------------------------------------------------------- |
| `main.py`  | `src/main.py`   | Bootstrap: the WebGL check, the engine, the game page. Imports only `game/index.py`. |
| `app/`     | `src/app/`      | The flow of the game: menus, levels, loading steps, HUD. Wires the layers together. |
| `game/`    | `src/game/`     | This game's content (see below).                                             |
| `core/`    | `src/core/`     | The pure rules: entities, systems, scenery generation, the fixed-step clock. No DOM, no Babylon (ENG-11). |
| `render/`  | `src/render/`   | Babylon plumbing: meshes, materials, scenery, the scene's layers.            |
| `ui/`      | `src/ui/`       | DOM screens and the panels of the menus.                                     |
| `audio/`   | `src/audio/`    | The synthesised music and sound effects (Web Audio).                         |
| `input/`   | `src/input/`    | Keyboard, gamepad and touch, turned into actions (menu actions, `LevelControls`). |
| `config/`  | `src/config/`   | The engine's tunables (menus, controls, the game screen, audio).             |
| `host/`    | `src/host/`     | Browser storage, WebGL capability checks, the data sent to the worker.       |
| `assets/`  | `src/assets/`   | The loading tasks of the start-up.                                           |

`game/` has four parts:

- `game/config/` holds the game's tunables. It imports only `game/config/`.
- `game/sim/` holds the game's rules content (enemies, bosses, waves, levels), as data for `core/`.
  It imports only `core/`, `config/`, `game/sim/` and `game/config/`.
- `game/view/` holds the presentation bindings: meshes, sounds and renderers for the content above.
  It may import `render/`, `audio/`, `ui/`, `assets/`, `config/`, `core/`, `game/sim/` and
  `game/config/`.
- `game/index.py` builds the one `GameDefinition` (`GAME`), the only object the engine gets from
  the game.

The rules, as contracts:

- `core/` imports only `core/`, `config/` and the standard library. It may import the Transcrypt
  stub `org` only for `__pragma__`, in the modules listed in the contract of `pyproject.toml`.
- Nothing outside `game/` imports `game/`. `main.py` imports only `game/index.py` (import-linter
  cannot read `main.py`, a module rather than a package, so that rule is checked by review).

## Game loop

`app/game_play.py` runs a level at a fixed step (ENG-100). `FixedStepClock` (`core/loop/`) turns the
frame's time into a whole number of steps of `1 / step_hz` seconds, and an interpolation factor
`alpha` in [0, 1). The steps per frame are capped; time beyond the cap is dropped.

Each step reads the controls (`input/` actions, as `LevelControls`) and runs `LevelRun.step` in
`core/`. The step's results (blasts, impacts, hits, bonuses picked) are collected for the frame.
After the steps, the scroll is drawn at the position between the last two steps, by `alpha`, and
the view draws the frame with the frame's real `dt` (animation, banking).

## Data flow

input → core → per-step state → render / ui / audio

- `input/` reads the devices into actions; `app/` passes them to `core/`.
- `core/` advances the rules. It never reads the clock or `random`: `dt` comes from the loop, and
  randomness from the seeded RNG (ENG-18).
- After each step, `render/`, `ui/` and `audio/` read the core state, including its lists of what
  happened in that step. They never change it. There is no event bus (ENG-11).

## Worker

`worker_main.py` is the ground worker, bundled as `dist/js/ground_worker.js`. It generates each
level's terrain, roads and props off the main thread (`render/scenery/ground_worker.py`), started by
`render/scenery/background_loader.py`. Its messages carry plain data only (`host/worker_data.py`),
because a Transcrypt object cannot be cloned into a message.

## Build

```
src/*.py ──transcrypt──▶ build/game/, build/worker/ ──esbuild (node/)──▶ dist/js/
index.html, public/ ─────────────────────────────────────────────────▶ dist/
```

- `make build` compiles with Transcrypt only when a Python source changed (`build/.stamp`), bundles
  the game and the worker into `dist/js/`, and copies `index.html` and `public/` into `dist/`. The
  script URLs get the short commit as `?v=` (ENG-84). It fails if a compiler pragma, the test API or
  an audio file (AUD-ENGINE-01) reaches `dist/`.
- The `babylon` step downloads the pinned `babylon.js` into `public/vendor/` and checks its SHA-256
  (ENG-02).
- `make build-info` writes `src/build_info.py`: the version (latest tag) and the short commit shown
  on the title screen.
- `make e2e-build` makes the e2e game in `dist-e2e/`, with the test API.

## Tests

- `make lint` runs ruff and import-linter; `make typecheck` runs mypy `--strict`.
- `make tests` runs the unit tests (pytest, in CPython, over `src/`, `tests/unit/`) with branch
  coverage. The gates: `src/` 70 %, `src/core/` 90 %, `src/game/sim/` 90 % (ENG-43, ENG-146). One
  test file per source file, at the same path: `tests/unit/core/math/test_color.py` tests
  `src/core/math/color.py`. Shared helpers are in `tests/helpers/`.
- `make e2e` runs Playwright (Chromium) against the e2e build, in `tests/e2e/`. CI runs it in four
  shards.
- `make check` runs all of the above. CI runs the lint, unit and e2e jobs
  (`.github/workflows/ci.yml`).
- `node/tests/` is the read-only TypeScript suite the port came from. Nothing runs it (ENG-10).

## Making a new game from this template

The engine runs any game built this way; only `src/game/` is game-specific.

1. Replace `src/game/`. Keep the four parts above: `config/`, `sim/`, `view/` and `index.py`.
2. Write the tunables in `game/config/` (game settings in `game/config/game.py`, records as in
   `game/config/record.py`).
3. Write the content in `game/sim/`: the enemy and boss kinds, the waves, the levels. Build them
   into the `core/` types the way `game/sim/levels.py` and `game/sim/rules_build.py` do.
4. Write the presentation in `game/view/`: meshes, materials, sounds and renderers for each kind,
   gathered into bindings as `GameBindings` does in `game/index.py`. `render/game_view.py` and
   `app/` read these bindings through the `view` field.
5. Define `GAME = GameDefinition(...)` in `game/index.py` with every field of
   `core/content/game_definition.py` (its docstring lists them in order), and keep `main.py`
   importing only `GAME` from it.
6. Keep the engine unchanged: `core/`, `render/`, `ui/`, `audio/`, `app/`, `input/`, `config/`,
   `host/`, `assets/` and `main.py`. Run `make check`: the import contracts and the tests fail if the
   game's code leaks into the engine or a dependency points the wrong way.
