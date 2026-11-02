# Stratoblaster

<!-- ENG-130: the live game, the controls, the requirements and the make targets. -->

An old-school vertical shoot 'em up with modern 3D graphics, running entirely in the browser.

**Play:** <https://rguillon.github.io/stratoblaster/>

**Source:** <https://github.com/rguillon/stratoblaster>

## Controls

### Menus

| Action         | Keyboard                       | Gamepad           | Touch / mouse             |
| -------------- | ------------------------------ | ----------------- | ------------------------- |
| Move selection | Arrows / WASD (Z Q S D AZERTY) | Left stick, D-pad | Tap an entry              |
| Confirm        | Enter, Space                   | A                 | Tap the selected entry    |
| Back           | Esc, Backspace                 | B                 | On-screen **Back** button |
| Change a value | ◀ / ▶ on a slider (Settings)   | Left stick, D-pad | Tap or drag the slider    |

### In game

| Action         | Keyboard                    | Gamepad           | Touch                    |
| -------------- | --------------------------- | ----------------- | ------------------------ |
| Move           | Arrows / WASD (by position) | Left stick, D-pad | Drag anywhere            |
| Shoot (hold)   | Space                       | A, right trigger  | Hold the **Fire** button |
| Switch weapon  | E (same key on AZERTY)      |                   |                          |
| Bomb           | R, Left Shift (by position) | X / Square, LB    | Tap the **Bomb** button  |
| Pause / resume | Esc, P (by position)        | Start, Select     | On-screen **❚❚** button  |

The level pauses by itself when the page is hidden or the gamepad in use is disconnected. The
pause menu has **Resume**, **Settings** and **Main menu** (which asks before leaving the level).
**Settings** (also on the title screen) sets the music and sound effect volumes.

All the music and sounds are generated in the browser (Web Audio); they start with the first key
press, tap, click or gamepad button.

Debug options (any build): `?level=1-3&t=120&ship=heavy` starts level 1-3 at 2:00 with the heavy
ship. With them, F fast-forwards ×4, ← / → jump 10 s, and an FPS / polygons tile shows.

The high score, the last chosen ship and the volumes are kept in cookies (`stratoblaster_high_score`, `stratoblaster_last_ship`, `stratoblaster_music_volume`, `stratoblaster_sfx_volume`).

## Requirements

- Python 3.12 and [uv](https://docs.astral.sh/uv/) (it fetches the Python version and the tools)
- GNU Make
- Node.js 24 LTS and npm (`node/.nvmrc`), only for the build's bundling step (esbuild)

## Getting started

```sh
make setup     # installs the git hooks (pre-commit, pre-push)
make serve     # builds the game into dist/ and serves it on http://localhost:5173
```

Then open http://localhost:5173. `SERVE_PORT=8000 make serve` picks another port.

## Make targets

<!-- ENG-37: the public targets, the only ones `make help` lists. -->

| Target       | What it does                                                                 |
| ------------ | ---------------------------------------------------------------------------- |
| `make setup` | Installs the git hooks (pre-commit, pre-push)                                |
| `make check` | Every code check: ruff (lint and format), import-linter, mypy                |
| `make tests` | Unit tests (pytest, CPython over `src/`) with coverage (HTML in `coverage/`) |
| `make build` | Fetches Babylon.js if needed, builds the game into `dist/`                   |
| `make e2e`   | Builds the e2e game, then runs the end-to-end tests (Playwright, Chromium)  |
| `make serve` | Builds the game, then serves `dist/` on http://localhost:5173 (`SERVE_PORT`) |

[`node/tests/`](node/tests/) keeps the TypeScript test suite of the game this port came from. Nothing
runs it: it is the reference for the tests still to port.

## Project layout

See [`docs/architecture.md`](docs/architecture.md) and the specs in [`specs/`](specs/).
