# Pewet

An old-school vertical shoot 'em up with modern 3D graphics, running entirely in the browser.

**Play:** _link added once GitHub Pages is enabled_

## Controls

| Action         | Keyboard      |
| -------------- | ------------- |
| Move           | Arrows / WASD |
| Shoot          | Space         |
| Special / bomb | E             |
| Pause          | Esc / P       |

## Requirements

- Node.js 24 LTS (see `.nvmrc`) and npm
- GNU Make

## Getting started

```sh
make install   # npm ci + git hooks + Playwright Chromium
make dev       # http://localhost:5173
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
