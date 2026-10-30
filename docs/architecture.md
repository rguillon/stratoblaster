# Architecture

The game is Python 3.12 (`src/`), compiled to JavaScript by Transcrypt and bundled by esbuild. The
3D engine is Babylon.js, called through the JavaScript interop of the Python modules. The
requirements are in [`specs/`](../specs/): `01-engineering.md` §2 is the layout rule this page
summarises.

## Layers

Dependencies point down the list: a layer imports only the layers below it.

| Layer      | Path            | What it holds                                                          |
| ---------- | --------------- | ---------------------------------------------------------------------- |
| `main.py`  | `src/main.py`   | Bootstrap: the WebGL check, the engine, the game page.                |
| `app/`     | `src/app/`      | The flow of the game: menus, levels, the loading steps, the HUD.      |
| `game/`    | `src/game/`     | This game's content: its bosses, enemies, weapons, levels, visuals.   |
| `render/`  | `src/render/`   | Babylon plumbing: meshes, materials, scenery, the scene's layers.     |
| `ui/`      | `src/ui/`       | DOM screens and the panels of the menus.                              |
| `audio/`   | `src/audio/`    | The synthesised music and sound effects.                              |
| `input/`   | `src/input/`    | Keyboard, gamepad and touch, read into the game's controls.           |
| `config/`  | `src/config/`   | The engine's tunables (menus, controls, the scenery stage, audio).    |
| `host/`    | `src/host/`     | Browser storage and WebGL capability checks.                          |
| `core/`    | `src/core/`     | The pure rules: entities, systems, scenery generation. No DOM, no Babylon. |
| `assets/`  | `src/assets/`   | The loading tasks of the start-up.                                    |

`core/` is checked by import-linter (`make lint`): it may not import `org` or `browser` (the
Transcrypt stubs), except the modules marked in `pyproject.toml`, which import `__pragma__` only.

The engine never imports `src/game/`. `main.py` hands the game (`game/index.py`, its
`GameDefinition`) to `app/`, which runs any game built that way.

## Worker

`worker_main.py` is the ground worker: it generates each level's terrain, roads and props off
the main thread (`render/scenery/ground_worker.py`). Its messages carry plain data only
(`host/worker_data.py`), because a Transcrypt object cannot be cloned into a message.

## Build

```
src/*.py ──transcrypt──▶ build/game/, build/worker/ ──esbuild (node/)──▶ dist/js/
index.html, public/ ─────────────────────────────────────────────────▶ dist/
```

`make build` compiles only when a Python source changed (`build/.stamp`), then bundles the game
and the worker into `dist/js/`. `make vendor` downloads the pinned Babylon.js into `public/vendor/`
(checked by SHA-256). The title screen shows the latest release tag and the short commit, written
to `src/build_info.py` by `make build-info`.

## Tests

- Unit tests: `tests/unit/` (pytest, run in CPython over `src/`). One test file per source file, at
  the same path: `tests/unit/core/math/test_color.py` tests `src/core/math/color.py`. Shared test
  helpers (fakes, sample levels) are in `tests/helpers/`. `make coverage` gates `core/` at 90 %
  lines and branches.
- Browser checks: none in CI yet. `node/tests/` holds the TypeScript suite of the game this port
  came from, as the reference for the tests still to port (see D-186 and D-188).
