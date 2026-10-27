---
last_mapped_commit: f4b3594074f5b8d67c594e038113c45d65d18a7c
last_mapped_at: 2026-10-27
---

# External Integrations

**Analysis Date:** 2026-10-27

## APIs & External Services

**Game/backend APIs:**

- None. The game makes no network requests at runtime. There are no `fetch`, `XMLHttpRequest`, or `WebSocket` calls under `src/`. The only URL-like string in `src/` is the SVG namespace in `src/ui/screens/elements.ts`.

**Package registry:**

- npm registry (`https://registry.npmjs.org/`) - Source for all dependencies at install time. The resolved URLs are recorded in `package-lock.json`.

**Browser platform APIs (not external services, but integration points):**

- Web Audio API - All music and sound is synthesized in the browser: `src/audio/audio-output.ts`, `src/audio/synth.ts`, `src/audio/sfx-player.ts`, `src/audio/music-player.ts`, `src/app/page-audio.ts`. Audio starts on the first key press, tap, click, or gamepad button.
- WebGL2 - Required by Babylon.js. Support is probed in `src/platform/webgl-support.ts`.
- Gamepad API - `navigator.getGamepads()` in `src/input/gamepad-menu-input.ts` and the in-game gamepad source in `src/input/game-controls.ts`.
- Pointer and touch events - Menu and in-game controls, for example `src/input/menu-input.ts`.
- Page Visibility - The level pauses when the page is hidden (see `README.md`, "In game").

## Data Storage

**Databases:**

- None. No database client, ORM, or database library is in `package.json`.

**File Storage:**

- Local filesystem only for development. Asset folders `public/assets/audio/`, `public/assets/env/`, `public/assets/models/`, and `public/assets/textures/` contain only `.gitkeep` files. No assets are fetched at runtime. The build checks that no audio files are emitted (`Makefile` `build` target, P12-R05).

**Caching:**

- None at the server level. Browser cache is handled by GitHub Pages and the browser default.

**Client-side persistence:**

- Browser cookies, through `CookieStorage` in `src/platform/cookie-storage.ts`. It is wired in `src/main.ts` (`storage: new CookieStorage(document, MENU_CONFIG.cookieMaxAgeDays)`). Cookie names are defined in `src/config/menu.ts` and documented in `README.md`:
  - `stratoblaster_high_score`
  - `stratoblaster_last_ship`
  - `stratoblaster_music_volume`
  - `stratoblaster_sfx_volume`
- Cookies are set with `SameSite=Lax` and a `max-age` taken from `MENU_CONFIG.cookieMaxAgeDays`. The key-value interface is in `src/platform/key-value-storage.ts`. The saved-data modules `src/app/saved-choices.ts`, `src/app/saved-settings.ts`, and `src/app/saved-weapons.ts` use it.

## Authentication & Identity

**Auth Provider:**

- Not applicable. There are no user accounts, logins, or tokens.

## Monitoring & Observability

**Error Tracking:**

- None. No Sentry, Bugsnag, or similar SDK is present.

**Logs:**

- No logging library. Diagnostics go to the browser console only, and no log shipping exists.

**Performance tooling (dev/debug only):**

- An FPS and polygon-count tile is shown with the debug options (`src/app/debug-options.ts`, `src/ui/stats-tile.ts`). It is not sent anywhere.

**Test hooks (dev/e2e only):**

- `src/debug/test-api.ts`, `src/debug/viewer-test-api.ts`, and related files expose test globals (`__GAME_TEST__`, `__ENEMIES_TEST__`, `__BOSSES_TEST__`, `__SCENERY_TEST__`, `__SHOTS_TEST__`). The production build fails if any of these names appears in `dist/` (`Makefile` `build` target, ENG-52).

## CI/CD & Deployment

**Hosting:**

- GitHub Pages, project site `https://rguillon.github.io/stratoblaster/` (from `README.md`). The deploy workflow is `.github/workflows/deploy.yml`.

**CI Pipeline:**

- GitHub Actions
  - `.github/workflows/ci.yml` - Runs on pushes to `main` and on pull requests. Steps: `make install SKIP_BROWSER=1`, `make lint typecheck coverage build`, then a coverage summary to `$GITHUB_STEP_SUMMARY` and an artifact upload (`coverage-report`). The e2e job is commented out.
  - `.github/workflows/deploy.yml` - Triggered by a completed `CI` workflow run on `main` (`workflow_run`), or by `workflow_dispatch`. It runs `npm ci`, `make build`, then `actions/upload-pages-artifact@v5` and `actions/deploy-pages@v5`. Permissions are `contents: read`, `pages: write`, `id-token: write`. Concurrency group `pages`.
- Actions in use: `actions/checkout@v7`, `actions/setup-node@v7` (with `node-version-file: .nvmrc` and npm cache), `actions/upload-artifact@v7`, `actions/upload-pages-artifact@v5`, `actions/deploy-pages@v5`
- Dependabot - `.github/dependabot.yml`: weekly updates for npm and GitHub Actions, with grouped `lint` and `test` updates.
- Git hooks (local, not a service) - `.husky/pre-commit` runs `npx lint-staged` and `make typecheck`. `.husky/pre-push` runs `make check-fast`.

## Environment Configuration

**Required env vars:**

- None for the application. `CI` is optional and read by Playwright and the Makefile (`playwright.config.ts`, `Makefile`). `SKIP_BROWSER` is an optional Makefile variable. `E2E_ARGS` is an optional Makefile variable.

**Secrets location:**

- No secrets are used. No `.env` files are tracked. The CI workflows need only the default `GITHUB_TOKEN` and the GitHub Pages OIDC token (`id-token: write`). No repository secrets are referenced in `.github/workflows/`.

## Third-Party Assets & Credits

- `CREDITS.md` lists third-party assets (table is currently empty). Models and textures are generated in code, so no third-party 3D assets, fonts, or audio files are fetched or bundled.
- The `index.html` entry contains no external `<link>`, `<script src>`, or CDN references (checked for `http` and `<link>`).

## Webhooks & Callbacks

**Incoming:**

- None

**Outgoing:**

- None

---

_Integration audit: 2026-10-27_
