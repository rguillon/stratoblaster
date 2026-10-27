---
last_mapped_commit: f4b3594074f5b8d67c594e038113c45d65d18a7c
last_mapped_at: 2026-10-27
---

# Coding Conventions

**Analysis Date:** 2026-10-27

## Naming Patterns

**Files:**

- `kebab-case.ts` everywhere under `src/` and `tests/` (ENG-15). Examples: `src/core/systems/shot-world.ts`, `src/app/game-session.ts`, `src/game/view/props/volcanic-foundry.ts`.
- Test files mirror the source tree with a `.test.ts` suffix: `src/core/systems/beam.ts` is tested by `tests/unit/core/systems/beam.test.ts`. E2E specs are `tests/e2e/<topic>.spec.ts`.
- Rendering code that touches the GPU but holds pure visual setup uses the `*.visual.ts` suffix, e.g. `src/render/scenery/aurora-material.visual.ts`. These files are excluded from coverage (see `vitest.config.ts`).
- Shared test helpers live in `tests/helpers/` (`tests/helpers/test-weapons.ts`, `tests/helpers/fake-dom.ts`); fixtures for the engine's sample game live in `tests/fixtures/` (`tests/fixtures/sample-game.ts`).
- Only one barrel file exists in `src/`: `src/game/index.ts`, which exports the single `GameDefinition` consumed by `src/main.ts`. Do not add new barrels.

**Functions:**

- `camelCase`. Factory and builder functions use `make`/`create`/`build`-style or noun names, e.g. `testGun()` in `tests/helpers/test-weapons.ts`, `sampleBonusRenderer()` in `tests/fixtures/sample-game.ts`.
- Top-level exported functions are the dominant form (about 326 `export function` declarations in `src/`). Arrow-function exports (`export const x = () =>`) are rare (about 12 files) and should be avoided in new code. Use `function` declarations for exported helpers.
- Predicate helpers read as questions: `isAlive()` in `src/core/entities/shot-target.ts`.
- Parsers and loaders use `parse*` / `load*` / `save*` pairs: `parseVolume`, `loadVolumes`, `saveVolumes` in `src/app/saved-settings.ts`.

**Variables:**

- `camelCase` for locals and parameters. Module-level constants are `UPPER_SNAKE_CASE` for true constants (`DEG` in `src/core/systems/shot-world.ts`, `ENGINE_LAYERS` in `eslint.config.mjs`, `CORE_THRESHOLDS` in `vitest.config.ts`, `LEVELS` in test files).
- Config objects are `UPPER_SNAKE_CASE` and exported as plain `const` data: `AUDIO_CONFIG` in `src/config/audio.ts`, `GAME_CONTROLS_CONFIG` in `src/config/game-controls.ts`.
- Regex constants are short `UPPER` names: `const STEP = /^\d{1,2}$/;` in `src/app/saved-settings.ts`.
- Use `readonly` on interface properties for data passed across layers. About 3,400 `readonly` occurrences exist in `src/`. Follow this for new interfaces.

**Types:**

- `PascalCase` for interfaces, type aliases and classes (ENG-15). Interfaces do not use an `I` prefix (no `I`-prefixed interfaces in `src/`).
- Options bags are named `<Thing>Options` (`ShotWorldOptions` in `src/core/systems/shot-world.ts`, `GameSessionOptions` in `src/app/game-session.ts`, `AppOptions` in `src/app/start-app.ts`).
- Definitions/contracts end in `Definition` (`WeaponDefinition`, `BeamWeaponDefinition` in `src/core/entities/weapon.ts`, `GameDefinition` in `src/core/content/game-definition.ts`).
- Frame and state snapshots end in `Frame` / `State` (`BombFrame`, `BonusFrame` in `src/render/game-view.ts`, `ControlState` in `src/input/game-controls.ts`).
- Use `import type { ... }` for type-only imports. About 440 files do so; `verbatimModuleSyntax` is enabled in `tsconfig.json`, so type imports must be marked.

## Code Style

**Formatting (Prettier, `.prettierrc.json`):**

- `printWidth: 100`
- `singleQuote: true`
- `trailingComma: "all"`
- `semi: true`
- 2-space indentation (`.editorconfig`: `indent_style = space`, `indent_size = 2`, LF line endings, final newline required, trailing whitespace trimmed). Makefile uses tabs.
- `.prettierignore` excludes `specs/`, `CLAUDE.md`, `.claude/`, `package-lock.json`, build output and `public/assets/`.
- Run `make format` to fix; `make lint` checks without writing. The pre-commit hook (lint-staged) runs Prettier and ESLint `--fix` on staged files.

**Linting (ESLint flat config, `eslint.config.mjs`):**

- `js.configs.recommended`, `typescript-eslint` `strictTypeChecked` and `stylisticTypeChecked`, `eslint-plugin-import-x` recommended and TypeScript presets, and `eslint-config-prettier` last (disables conflicting style rules).
- `make lint` runs with `--max-warnings 0`: warnings fail the gate. Treat every warning as an error.
- Explicit rules:
  - `@typescript-eslint/no-explicit-any`: error. Do not use `any`.
  - `@typescript-eslint/ban-ts-comment`: `@ts-ignore` banned; `@ts-expect-error` only with a description (`// @ts-expect-error: reason`). Current code has no suppressions.
  - `import-x/no-default-export`: error. Named exports only (ENG-15).
  - `max-lines-per-function`: warn at 50 lines (blank lines and comments skipped). Off in `tests/**`.
  - `max-lines`: warn at 300 lines per file (blank lines and comments skipped).
  - `complexity`: warn at 10.
  - `import-x/no-restricted-paths`: enforces the layer map (see Module Design).
- Pure modules (`src/core/**`, `src/game/sim/**`) additionally forbid: `@babylonjs/*` imports, browser globals (`window`, `document`, `performance`, `navigator`, `localStorage`, `requestAnimationFrame`), `Math.random`, `Date.now`, and `performance.now` (`PURE_RULES` in `eslint.config.mjs`). Use the seeded RNG in `src/core/math/rng.ts` and the injected `dt`.

**TypeScript (`tsconfig.json`):**

- `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitOverride`, `noUnusedLocals`, `noUnusedParameters`, `verbatimModuleSyntax`, `isolatedModules`.
- Indexed access returns `T | undefined`: guard reads (`if (!factory) throw ...`) rather than using `!`.
- With `exactOptionalPropertyTypes`, optional properties cannot be assigned `undefined`. Use conditional spreads, as in `src/app/game-session.ts`:
  ```ts
  ...(debug.weather === false ? { weather: false } : {}),
  ```
- Use `override` on overridden members (`noImplicitOverride`).
- Target ES2023; modules use `"moduleResolution": "bundler"`, so relative imports carry no file extension: `import { GameControls } from '../input/game-controls';`.
- `import` paths are relative. There are no path aliases.

**Babylon.js imports:**

- Always import from deep subpaths, never the root package: `import type { Scene } from '@babylonjs/core/scene';`, `import { Vector3 } from '@babylonjs/core/Maths/math.vector';`. Only `src/render/`, `src/fx/`, `src/game/view/`, and `src/app/` may import Babylon (ENG-11).

## Import Organization

**Order (observed convention, not enforced by a sort rule):**

1. Type-only and external packages first (`import type { ... } from '@babylonjs/...'`, `vitest`, `@playwright/test`).
2. Relative imports from the engine layers (`../core/...`, `../input/...`).
3. Relative imports from sibling modules in the same folder (`./beam`, `./projectile-motion`).

Examples: `src/app/game-session.ts` and `src/core/systems/shot-world.ts`.

**Path Aliases:**

- None. Use relative paths. Test files reach `src/` via `../../../../src/...` (see `tests/unit/core/systems/beam.test.ts`).

**Import-cycle and layering enforcement:**

- The layers are checked by `import-x/no-restricted-paths` (see Module Design). Import from the layer you are allowed to depend on; do not work around it by moving code.

## Error Handling

**Programmer errors and missing content (throw):**

- Use `throw new Error(...)` with a human-readable message that names the missing thing, including its id where useful. Examples:
  - `if (!level) throw new Error(\`Level "${id}" cannot be played\`);`in`src/app/game-play.ts`
  - `if (!factory) throw new Error(\`No model for player ship "${id}"\`);`in`src/app/menu-scenes.ts`
  - `if (game.bossKinds.length === 0) throw new Error('The game has no boss');` in `src/app/start-boss-viewer.ts`
  - `if (options.shipIds.length === 0) throw new Error('The menu needs at least one ship');` in `src/app/menu-flow.ts`
- Validate required content up front when constructing an object (guard clauses at the top of the factory), not deep in the render loop.
- No custom error classes exist. Use plain `Error`.

**Recoverable input (return a fallback):**

- Untrusted input from storage or URLs falls back to a default instead of throwing. `parseVolume` in `src/app/saved-settings.ts` returns `fallback` for anything that is not a whole number in range. `src/app/saved-weapons.ts` uses an empty `catch` (`} catch {`) around storage parsing and returns defaults.
- Optional-chaining and nullish coalescing are the standard way to read possibly-absent state: `storage.get(keys.music)` returns `string | null`, handled by `raw?.trim() ?? ''`.

**Browser/audio failures (swallow, do not crash):**

- Audio code tolerates failures: `src/audio/audio-output.ts` and `src/audio/synth.ts` use bare `catch {}` blocks and `promise.catch(() => undefined)` for fire-and-forget audio calls. Use this only where the failure is genuinely non-fatal; add a comment saying why.
- E2E tests fail on any browser console error, uncaught exception, or audio warning (`tests/e2e/fixtures.ts`, ENG-53, P12-R05). Do not add `console.error` in production code paths that the e2e suite exercises.

**Lint suppression:**

- No `eslint-disable` comments exist in `src/` or `tests/`. Do not add them; fix the code or, for tests only, adjust the scope of the rule in `eslint.config.mjs` with a documented reason.

## Logging

**Framework:** None. `console.*` is not used in `src/`. Diagnostics go through the in-browser inspector and the debug test API in `src/debug/` (dev and e2e builds only, ENG-52).

**Patterns:**

- Do not add `console.log` to committed code.
- Expose state for debugging through `src/debug/test-api.ts` (`window.__GAME_TEST__`, only in `e2e` mode) instead.

## Comments

**When to Comment:**

- Every exported type, function and class has a `/** ... */` doc comment that states purpose and, where relevant, the requirement it implements. Examples:
  - `/** Player shots of one ship (P03-R01..R03): ... */` on `ShotWorld` in `src/core/systems/shot-world.ts`
  - `/** Storage keys of the volume settings (P12-R04, D-010), prefixed with the game's id. */` in `src/app/saved-settings.ts`
- Requirement IDs (`P03-R02`, `ENG-43`, `D-094`) are cited in comments to tie code to the specs. Keep this convention: cite the ID that the code implements.
- Inline `//` comments explain non-obvious decisions, e.g. why a `div` with `role="button"` is used instead of `<button>` in `src/ui/screens/elements.ts`.
- Do not comment what the code obviously does.

**JSDoc/TSDoc:**

- Use `/** */` for exported symbols. Use `@param`/`@returns` only when the name is not self-explanatory; the codebase prefers prose.
- Doc comments on object fields are common and encouraged for tunables: `/** Shots this far outside the playfield are removed. */`.

## Function Design

**Size:**

- Target 50 lines or fewer (warning at 50, ENG-16). Files target 300 lines or fewer (warning at 300). Split by responsibility into sibling modules rather than growing one file. Many large files already exist in `src/game/view/props/` and `src/game/config/`; those are data-heavy and acceptable, but new logic should stay under the limits.
- Cyclomatic complexity: keep at or below 10. Extract helper functions when a branch cascade grows.

**Parameters:**

- Prefer one options object for more than three parameters (`ShotWorldOptions`, `GameSessionOptions`).
- Optional options use `?` with `exactOptionalPropertyTypes` in mind.
- Positional parameters are fine for 1–3 required values (e.g. `traceBeam(levels, level, x, y0, y1, targets)`; see `src/core/systems/beam.ts`).
- Pure simulation functions take `dt` and an RNG as arguments; they never read the clock.

**Return Values:**

- Return plain data objects (`interface` types, `readonly` fields) from `core/` functions: `BeamTrace` with `segments` and `hits`.
- Return `void` for mutators. Mutators on classes are methods on `#private` state (see Classes).
- Return `undefined`, not `null`, for "no value" in new code, unless the type is explicitly `| null` (the codebase mixes both; `storage.get` uses `null` because the storage API does).

**Classes:**

- Classes are common (about 109 files) for stateful engine objects: `ShotWorld`, `GameSession`, `GamePlay`, `MenuFlow`.
- Private state uses ECMAScript `#private` fields (about 78 files), not `private` keyword or `_` prefixes. Example: `#weapon`, `#level`, `#cooldown` in `src/core/systems/shot-world.ts`.
- Public state fields are declared with `readonly` where they are not reassigned: `readonly projectiles: Projectile[] = [];`, constructor parameter properties like `readonly options: ShotWorldOptions`.
- Accessors (`get weapon()`) expose read-only views of private state.

## Module Design

**Exports:**

- Named exports only. Default exports are banned (`import-x/no-default-export`). Configs (`*.config.ts`, `*.config.mjs`, `eslint.config.mjs`) are the only exception, and they use `export default`.
- One main export per file (ENG-15). Helper types may accompany it.

**Barrel Files:**

- Not used, except `src/game/index.ts`, which exposes the single `GameDefinition` to `src/main.ts`. Import from the concrete module path.

**Layer map (enforced by lint, ENG-11, ENG-142):**

- `src/core/`: imports only `core/` and `config/`. No Babylon, no DOM.
- `src/game/sim/`: imports only `core/`, `config/`, `game/sim/`, `game/config/`. Same purity rules as `core/`.
- `src/game/view/`: may not import `app/`, `input/`, `platform/`, `debug/`, `config/`, or `main.ts`.
- `src/game/config/`: plain data; imports only `game/config/` and `core/`.
- Engine layers (`app`, `core`, `render`, `fx`, `audio`, `input`, `ui`, `assets`, `config`, `platform`, `debug`): never import from `src/game/` (except `src/main.ts`, which may import `src/game/index.ts` only).
- Only `src/app/` and `src/main.ts` may import `src/app/`.

**Engine versus game (ENG-145, §2.3):**

- Code outside `src/game/` stays game-agnostic and is tested with `tests/fixtures/sample-game.ts`. Concrete bosses, enemies, levels and tunables belong in `src/game/`.

## Commit Conventions

- Conventional Commits (ENG-90): `feat:`, `fix:`, `test:`, `refactor:`, `chore:`, `docs:`, `ci:`.
- Scope is a layer or phase: `feat(core): ...`, `test(p03): ...`, `docs(p12): ...`. Recent history uses `Phase 12 (#23)`, `Feat/world 1 rework (#24)` style for merged PRs.
- Branch per phase: `phase-NN` (ENG-91). Commits pass the pre-commit hook; do not bypass with `--no-verify`.

---

_Convention analysis: 2026-10-27_
