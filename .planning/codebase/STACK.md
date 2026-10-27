---
last_mapped_commit: f4b3594074f5b8d67c594e038113c45d65d18a7c
last_mapped_at: 2026-10-27
---

# Technology Stack

**Analysis Date:** 2026-10-27

## Languages

**Primary:**

- TypeScript ~6.0.3 - All game code: `src/`, `tests/unit/`, `tests/e2e/`, `vite.config.ts`, `vitest.config.ts`, `playwright.config.ts`, `eslint.config.mjs`, `lint-staged.config.mjs`
- Strict mode is on in `tsconfig.json` (`strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `verbatimModuleSyntax`, `noUnusedLocals`, `noUnusedParameters`)

**Secondary:**

- HTML - Seven page entries at the repo root and in subfolders: `index.html`, `player_ship/index.html`, `player_shots/index.html`, `level_zero/index.html`, `enemies/index.html`, `bosses/index.html`, `boss/index.html`
- JavaScript (ESM) - Tooling config only (`eslint.config.mjs`, `lint-staged.config.mjs`); `package.json` sets `"type": "module"`
- YAML - CI and deploy workflows in `.github/workflows/ci.yml` and `.github/workflows/deploy.yml`, Dependabot in `.github/dependabot.yml`
- Shell - Git hooks in `.husky/pre-commit` and `.husky/pre-push`
- Make - Single entry point for all commands in `Makefile`

## Runtime

**Environment:**

- Node.js 24 LTS, pinned in `.nvmrc` (value `24`); `package.json` `engines` requires `>=24 <25`
- Browser runtime: the game runs entirely client-side. It needs WebGL2 (checked in `src/platform/webgl-support.ts`) and the Web Audio API (`src/audio/audio-output.ts`)
- Vitest unit tests run in the `node` environment (`vitest.config.ts`); `happy-dom` is a dev dependency for DOM-dependent tests

**Package Manager:**

- npm (version not pinned; `package-lock.json` is lockfileVersion-based and committed)
- Lockfile: present (`package-lock.json`)
- Install is `npm ci` (via `make install`, and in CI)

## Frameworks

**Core:**

- Babylon.js `@babylonjs/core` 9.32.0 - 3D rendering engine (scene, meshes, materials, cameras, lights, glow layer). Imported by subpath, e.g. `@babylonjs/core/scene`, `@babylonjs/core/Engines/nullEngine`. Used across `src/render/`, `src/fx/`, `src/game/view/`, `src/app/`. The `nullEngine` subpath is used by headless code and tests.
- No UI framework. The DOM UI is built by hand in `src/ui/` (for example `src/ui/screens/elements.ts`, `src/ui/menu-overlay.ts`).
- Web Audio API - Music and sound effects are generated in code (`src/audio/synth.ts`, `src/audio/sequencer.ts`, `src/audio/sfx-player.ts`, `src/audio/track-mixer.ts`). No audio files are shipped; `public/assets/audio/` holds only `.gitkeep`, and the build fails if an audio file reaches `dist/` (`Makefile` `build` target).
- Geometry is generated from code (`src/render/geometry/`, `src/game/view/`), per the credits note "All models are generated from code (GD-60)" in `CREDITS.md`.

**Testing:**

- Vitest 5.0.5 - Unit test runner. Config: `vitest.config.ts`. Tests in `tests/unit/**/*.test.ts`. Coverage via `@vitest/coverage-v8` 5.0.5 (provider `v8`).
- `happy-dom` 21.0.4 - DOM environment for tests that need one
- Playwright `@playwright/test` 1.64.1 - End-to-end tests. Config: `playwright.config.ts`. Tests in `tests/e2e/`. Runs Chromium only (`Desktop Chrome` device, with `--use-angle=swiftshader` and `--enable-unsafe-swiftshader` for software WebGL).

**Build/Dev:**

- Vite 8.3.5 - Dev server (port 5173), production build (`dist/`), e2e build (`dist-e2e/`, mode `e2e`), and preview server (port 4173). Config: `vite.config.ts`. Output uses `base: './'` for GitHub Pages sub-paths. The build bundles the seven HTML entries listed under Secondary.
- Rolldown is the bundler underneath Vite 8 (`build.rolldownOptions` in `vite.config.ts`).
- TypeScript 6.0.3 - Type checking only (`tsc --noEmit`, `make typecheck`). Vite does not emit types.
- ESLint 10.13.0 with `typescript-eslint` 8.72.0, `@eslint/js` 10.0.1, `eslint-plugin-import-x` 4.17.1, `eslint-import-resolver-typescript` 4.4.5, `eslint-config-prettier` 10.1.8. Config: `eslint.config.mjs`. Enforces the layer rules via `import/no-restricted-paths`.
- Prettier 3.9.10 - Formatting. Config: `.prettierrc.json`, ignores in `.prettierignore`.
- EditorConfig - `.editorconfig`
- Husky 9.1.7 - Git hooks (`prepare` script in `package.json`)
- lint-staged 17.6.0 - Pre-commit file linting, config `lint-staged.config.mjs`

## Key Dependencies

**Critical:**

- `@babylonjs/core` 9.32.0 - Only runtime dependency. Everything visual depends on it. It is the bulk of the production bundle, which the build budget tracks (`vite.config.ts` comment cites ENG-107, 1.5 MB gzip; `chunkSizeWarningLimit` is 1500).
- `vite` 8.3.5 - Build and dev server. Changing its major version changes the build output and the `base` handling.
- `typescript` ~6.0.3 - The tilde range is deliberate. Dependabot ignores `typescript >=6.1.0` because `typescript-eslint` 8.x only supports TypeScript `<6.1` (see `.github/dependabot.yml`).
- `vitest` 5.0.5 with `@vitest/coverage-v8` 5.0.5 - Must stay in lockstep (Dependabot groups them under `test`).

**Infrastructure:**

- `husky` 9.1.7 and `lint-staged` 17.6.0 - Enforce `make check-fast` on pre-push and lint-staged plus `make typecheck` on pre-commit
- `@types/node` ^26.6.5 - Node typings. Note `engines` pins Node 24, while the types are for Node 26; keep the two in mind when using Node APIs.
- `globals` ^17.13.0 - Global names for ESLint

## Configuration

**Environment:**

- No runtime environment variables are read by the application source (no `process.env` or `import.meta.env` usage under `src/`).
- Build-time constants are injected by Vite `define` in `vite.config.ts`: `__APP_VERSION__` (from `package.json` `version`), `__APP_COMMIT__` (from `git rev-parse --short HEAD`, falls back to `unknown`), and `__E2E__` (true in `e2e` mode). Declared types are in `src/**/*.d.ts` files.
- `vitest.config.ts` defines the same three constants with test values (`test`, `test`, `false`).
- Playwright reads `CI` for `forbidOnly`, `retries`, and reporter choice (`playwright.config.ts`). `Makefile` reads `CI` to add `--with-deps` to Playwright installs, and `SKIP_BROWSER` to skip the Chromium install.
- Persistent player settings use browser cookies, not env vars. See `src/platform/cookie-storage.ts` and `INTEGRATIONS.md`.
- No `.env` file is tracked in the repo, and `.gitignore` does not list `.env`. The app does not need one.

**Build:**

- `vite.config.ts` - Vite config, multi-page `rolldownOptions.input`, `base: './'`, sourcemaps only in `e2e` mode, outputs `dist/` (default) or `dist-e2e/` (e2e)
- `tsconfig.json` - Target `ES2023`, module `ESNext`, resolution `bundler`, types `vite/client` and `node`, includes `src`, `tests`, `*.config.ts`
- `eslint.config.mjs`, `.prettierrc.json`, `.prettierignore`, `.editorconfig`
- `vitest.config.ts` - Coverage thresholds: global lines 70; `src/core/**` and `src/game/sim/**` at lines 90, branches 85, functions 90, statements 90. These must not be lowered.
- `playwright.config.ts` - Base URL `http://localhost:4173`; the web server runs `npx vite preview --mode e2e --outDir dist-e2e`
- `Makefile` - Targets: `install`, `dev`, `build`, `lint`, `format`, `typecheck`, `test`, `test-watch`, `coverage`, `e2e`, `e2e-build`, `e2e-ui`, `check-fast`, `check`, `preview`, `clean`
- `.nvmrc` - Node version (24)

## Platform Requirements

**Development:**

- Node.js 24.x and npm (`.nvmrc`, `package.json` `engines`)
- GNU Make
- Chromium for Playwright e2e tests (`make install` installs it unless `SKIP_BROWSER=1`). On Linux CI, `PLAYWRIGHT_INSTALL_FLAGS=--with-deps` is applied when `CI` is set.
- A browser with WebGL2 and Web Audio for manual play. Gamepad support uses `navigator.getGamepads()` (`src/input/gamepad-menu-input.ts`), and touch controls are included.
- Dev server: `make dev` on `http://localhost:5173`

**Production:**

- Static hosting on GitHub Pages. `.github/workflows/deploy.yml` builds with `make build`, uploads `dist/` with `actions/upload-pages-artifact`, and deploys with `actions/deploy-pages`. The public URL is in `README.md`.
- No server-side runtime. The output is static HTML, JS and CSS with no audio or texture assets. Production builds are checked for e2e test API leakage and audio files (`Makefile` `build` target).

---

_Stack analysis: 2026-10-27_
