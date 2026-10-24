# Stratoblaster

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

### In game

| Action            | Keyboard                    | Gamepad           | Touch                     |
| ----------------- | --------------------------- | ----------------- | ------------------------- |
| Move              | Arrows / WASD (by position) | Left stick, D-pad | Drag anywhere             |
| Shoot (hold)      | Space                       | A, right trigger  | Hold the **Fire** button  |
| Back to the title | Esc, Backspace              | B                 | On-screen **Back** button |

Bombs and pause come in later phases.

Debug options (any build): `?level=1-3&t=120&ship=heavy` starts level 1-3 at 2:00 with the heavy
ship. With them, F fast-forwards ×4, ← / → jump 10 s, and an FPS / polygons tile shows.

The high score and the last chosen ship are kept in cookies (`stratoblaster_high_score`, `stratoblaster_last_ship`).

## Requirements

- Node.js 24 LTS (see `.nvmrc`) and npm
- GNU Make

## Getting started

```sh
make install   # npm ci + git hooks + Playwright Chromium
make dev       # http://localhost:5173 (player ship viewer: http://localhost:5173/player_ship/)
# Debug pages: /player_ship/ (ships), /player_shots/ (shots), /level_zero/ (generated level),
# /enemies/ (enemies)
```

## Make targets

| Target            | What it does                                         |
| ----------------- | ---------------------------------------------------- |
| `make help`       | List targets                                         |
| `make install`    | Install dependencies, git hooks, Playwright browser  |
| `make dev`        | Vite dev server with HMR (port 5173)                 |
| `make build`      | Production build into `dist/`                        |
| `make preview`    | Serve the production build                           |
| `make lint`       | ESLint + Prettier check                              |
| `make format`     | Prettier write + ESLint `--fix`                      |
| `make typecheck`  | `tsc --noEmit`                                       |
| `make test`       | Unit tests                                           |
| `make test-watch` | Unit tests in watch mode                             |
| `make coverage`   | Unit tests with coverage thresholds                  |
| `make e2e`        | e2e build + Playwright                               |
| `make e2e-ui`     | Playwright UI mode                                   |
| `make check-fast` | lint + typecheck + test (pre-push hook)              |
| `make check`      | Full gate: lint + typecheck + coverage + build + e2e |
| `make clean`      | Remove build outputs and reports                     |

## Project layout

See [`docs/architecture.md`](docs/architecture.md) and the specs in [`specs/`](specs/).
