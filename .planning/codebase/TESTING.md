---
last_mapped_commit: f4b3594074f5b8d67c594e038113c45d65d18a7c
last_mapped_at: 2026-10-27
---

# Testing Patterns

**Analysis Date:** 2026-10-27

## Test Framework

**Runner:**

- Vitest 5 (`package.json` devDependency `vitest ^5.0.5`), config: `vitest.config.ts`
- Unit tests run in the Node environment by default. DOM-touching tests opt into happy-dom with a per-file pragma.
- E2E: Playwright (`@playwright/test ^1.64.1`), config: `playwright.config.ts`, single Chromium project.

**Assertion Library:**

- Vitest's built-in `expect` (Jest-compatible matchers: `toEqual`, `toBe`, `toBeCloseTo`, `toThrow`). Playwright's `expect` for e2e, including `expect.poll` for async state.

**Coverage:**

- `@vitest/coverage-v8` (`provider: 'v8'`), config in `vitest.config.ts`.

**Run Commands:**

```bash
make test            # Unit tests, single run (npx vitest run)
make test-watch      # Unit tests in watch mode (npx vitest)
make coverage        # Unit tests with coverage; fails below thresholds (npx vitest run --coverage)
make e2e             # Build in e2e mode, serve on :4173, run Playwright (npx playwright test)
make e2e E2E_ARGS=--grep=P09   # Run a subset of e2e tests
make e2e-ui          # Playwright UI mode
make check-fast      # lint + typecheck + unit tests (pre-push)
make check           # Full gate: lint + typecheck + coverage + build + e2e (CI and /validate-phase)
```

**Phase-time verification (CLAUDE.md):** during `/implement-phase` and `/fix-phase`, only `make typecheck build e2e` runs. Unit tests (`make test`) and coverage (`make coverage`) run once, in the full gate of `/validate-phase` via `make check`. Write unit tests as you implement, but do not run them mid-phase.

## Test File Organization

**Location:**

- Unit tests live in `tests/unit/`, a mirror of `src/` (ENG-10 layout). Example: `src/core/systems/shot-world.ts` is tested by `tests/unit/core/systems/shot-world.test.ts`.
- Shared helpers: `tests/helpers/` (builders and fakes used by many tests).
- Engine fixtures (a minimal "sample game" that proves the engine works without `src/game/`, ENG-145): `tests/fixtures/`.
- E2E specs: `tests/e2e/*.spec.ts` plus `tests/e2e/fixtures.ts` (extended `test` with the console-error guard) and `tests/e2e/menu-helpers.ts`.

**Naming:**

- Unit: `<source-name>.test.ts`, kebab-case, matching the source module. Some modules have several files for different aspects, e.g. `tests/unit/core/systems/level-run-bosses.test.ts`, `tests/unit/core/systems/level-run-bombs.test.ts`, `tests/unit/core/scenery/road-network-crossings.test.ts`.
- E2E: `<topic>.spec.ts`, e.g. `tests/e2e/world-1.spec.ts`, `tests/e2e/menu-gamepad.spec.ts`, `tests/e2e/player-shots.spec.ts`.

**Structure:**

```
tests/
├── unit/                # mirrors src/ (App, core, game, render, ui, audio, input, ...)
├── fixtures/            # sample-game.ts, sample-enemies.ts, sample-boss.ts, sample-scenery.ts
├── helpers/             # at.ts, fake-audio.ts, fake-dom.ts, test-weapons.ts, boss-bot.ts, ...
└── e2e/                 # Playwright specs + fixtures.ts + menu-helpers.ts
```

**Test ID convention (ENG-42):**

- Every phase requirement ID appears in at least one test name: `it("P03-R02: ...")`, `it("ENG-145: ...")`. About 740 test names carry an ID.
- Not every unit test file carries an ID. Pure helper tests (e.g. `tests/unit/core/math/rng.test.ts`, `tests/unit/core/entities/weapon.test.ts`) describe behavior without one. Add an ID whenever the test verifies a numbered requirement.
- Multiple IDs may be listed in one name: `it('P01-R05, P01-R06: ...')`, `test('ENG-54, P12-R12: ...')`.

## Test Structure

**Suite Organization:**

```typescript
import { describe, expect, it } from 'vitest';
import { traceBeam } from '../../../../src/core/systems/beam';
import type { ShotTarget } from '../../../../src/core/entities/shot-target';
import { testBeam } from '../../../helpers/test-weapons';

const LEVELS = testBeam().levels;

function target(id: number, x: number, y: number, health = 10): ShotTarget {
  return { id, x, y, radius: 5, health, maxHealth: 10 };
}

describe('traceBeam', () => {
  it('P03-R02: runs to the top when nothing is in the way', () => {
    const trace = traceBeam(LEVELS, 2, 50, 10, 200, [target(1, 90, 100)]);
    expect(trace.segments).toEqual([{ x: 50, y0: 10, y1: 200, level: 2, width: 4, hit: false }]);
    expect(trace.hits).toEqual([]);
  });
});
```

**Patterns:**

- One `describe` per exported unit (function or class), named exactly after it (`describe('traceBeam', ...)`). For classes, `describe('ShotWorld', ...)`.
- Each `it` is one behavior, phrased as a sentence in lowercase after the ID: `'P03-R02: at level 1, stops at the first target'`.
- Module-level helper builders (`function target(...)`, `const LEVELS = testBeam().levels`) sit above the `describe`.
- Use `describe.each`/`it.each` for tables of inputs (13 files do, e.g. `tests/unit/core/entities/player-ship.test.ts`, `tests/unit/render/geometry/lathe-z.test.ts`, `tests/unit/ui/stage-fit.test.ts`).
- Assertions compare whole structures with `toEqual` on mapped tuples to keep failure output readable:
  ```typescript
  expect(trace.segments.map((s) => [s.y0, s.y1, s.level, s.hit])).toEqual([
    [10, 95, 2, true],
    [95, 145, 1, true],
  ]);
  ```
- Environment pragma for DOM tests, first line of the file:
  ```typescript
  // @vitest-environment happy-dom
  ```
  Used in `tests/unit/app/start-app.test.ts`, `tests/unit/ui/stats-tile.test.ts`, `tests/unit/ui/boss-bar.test.ts`, `tests/unit/ui/shot-viewer-panel.test.ts`.

**Setup/Teardown:**

- Use `beforeEach`/`afterEach` for resource disposal. Pattern from `tests/unit/app/start-app.test.ts`:
  ```typescript
  describe('startApp', () => {
    let app: RunningApp | undefined;
    afterEach(() => {
      app?.dispose();
      app = undefined;
    });
  });
  ```
- Engines in tests are Babylon's headless `NullEngine` (`@babylonjs/core/Engines/nullEngine`), never a real WebGL context (ENG-47).
- Config overrides in `vitest.config.ts` set `__APP_VERSION__`, `__APP_COMMIT__`, `__E2E__` globals.

**Timeouts:**

- Global `testTimeout` and `hookTimeout` are 30 s (level generation takes about 2 s locally and more on shared CI runners).

## Mocking

**Framework:** Hand-written fakes and stubs. The project does not use `vi.mock`, `vi.fn`-heavy mocking, `vi.useFakeTimers`, or `vi.stubGlobal` (none found in `tests/`). `vi.fn` appears only for simple call tracking inside a test.

**Patterns:**

Fake collaborators are plain objects that record what they receive. From `tests/fixtures/sample-game.ts`:

```typescript
/** The frames the sample bonus renderer was given, most recent last. */
export const bonusFrames: BonusFrame[] = [];

/** A bonus renderer that records its frames. */
function sampleBonusRenderer(): BonusRenderer {
  return {
    sync: (frame) => {
      bonusFrames.push(frame);
    },
    dispose: () => undefined,
  };
}
```

Fake DOM: `tests/helpers/fake-dom.ts` provides `FakeElement` and `FAKE_DOCUMENT` for `ui/` code run under Node. Prefer `happy-dom` pragma for code that uses real DOM APIs (`querySelector`, `dataset`).

Fake audio: `tests/helpers/fake-audio.ts` is a fake Web Audio context: nodes record connections, parameters record scheduled values, and the test sets the clock.

Spies: `vi.spyOn` appears in a single file. Prefer recording fakes over spies.

**What to Mock:**

- Rendering: use Babylon's `NullEngine` and real scene objects instead of mocking Babylon.
- Browser DOM: use `happy-dom` pragma, or `FakeElement` for tiny tree checks.
- Audio: `tests/helpers/fake-audio.ts`.
- Storage: `MemoryStorage` from `src/platform/key-value-storage.ts`, passed in via options (see `tests/unit/app/start-app.test.ts`).
- Game content: `tests/fixtures/sample-game.ts` (`SAMPLE_GAME`) for engine tests (ENG-145).
- Frame/time: pass `dt` explicitly, e.g. `app.tick(0.05)`; the app caps frame time internally.

**What NOT to Mock:**

- Pure `core/` logic: test it directly with real inputs (it has no dependencies to mock).
- The seeded RNG: use `src/core/math/rng.ts` with a fixed seed so tests are deterministic (ENG-46).
- The test weapons and levels: use the builders in `tests/helpers/test-weapons.ts` (`testGun`, `testBeam`) instead of stubbing.

## Fixtures and Factories

**Test Data:**

- Factories return fresh objects with overrides, typed with `Partial<T>`:
  ```typescript
  export function testGun(
    overrides: Partial<ProjectileWeaponDefinition> = {},
  ): ProjectileWeaponDefinition {
    return {
      kind: 'projectile',
      id: 'gun',
      // ...defaults...
      ...overrides,
    };
  }
  ```
  Source: `tests/helpers/test-weapons.ts`.
- Small inline builders are preferred for entities: `function target(id, x, y, health = 10): ShotTarget` in `tests/unit/core/systems/beam.test.ts`.
- Named sample content lives in fixtures: `SAMPLE_GAME`, `SAMPLE_ENEMY_KINDS`, `SAMPLE_BOSS_KINDS`, `SAMPLE_SCENERY_LEVEL` in `tests/fixtures/`.
- Recorders hold state in exported arrays (`bonusFrames`, `bombFrames`) that tests read after running frames.

**Location:**

- `tests/helpers/` for builders used across files; `tests/fixtures/` for sample game content; an in-file `function` for builders used by a single test file.

## Coverage

**Requirements (`vitest.config.ts`, ENG-43, ENG-146):**

- Global `src/**/*.ts` (after exclusions): **70 % lines**.
- `src/core/**`: **90 % lines**, **85 % branches**, **90 % functions**, **90 % statements**.
- `src/game/sim/**`: same thresholds as `src/core/**`.
- Excluded (ENG-45): `src/main.ts`, `src/debug/**`, `src/render/**/*.visual.ts`, `src/fx/**/*.visual.ts`, `src/**/*.d.ts`.
- Coverage must never decrease between phases (ENG-44). Report old vs. new numbers in the phase report.
- Never lower thresholds to get a green gate (ENG-64 and CLAUDE.md).

**View Coverage:**

```bash
make coverage
# HTML report: coverage/index.html (reporter: text, text-summary, html, json-summary)
```

## Test Types

**Unit Tests:**

- Scope: every module under `src/`, one test file per module group.
- `core/` and `game/sim/`: pure, deterministic, no Babylon, no DOM. Tests use seeded RNG and explicit `dt`.
- `app/`, `ui/`, `audio/`, `input/`, `render/`: test wiring with fakes, `NullEngine`, `happy-dom`, and `MemoryStorage`.
- `game/config/` and `game/` content: data-level checks, e.g. `tests/unit/game/config/scoring.test.ts`, `tests/unit/game/game-definition.test.ts`, `tests/unit/game/scenery-levels.test.ts`.
- Some unit tests are slow (level generation). Keep each under the 30 s limit; unit suite target is under 30 s total (ENG-48).

**Integration Tests:**

- No separate integration suite. Cross-module behavior is tested in the unit tree (`tests/unit/app/start-app.test.ts` runs the whole app bootstrap on `NullEngine` with the sample game).
- `tests/helpers/score-run.ts`, `tests/helpers/level-metrics.ts`, `tests/helpers/boss-bot.ts`, and `tests/helpers/enemy-context.ts` provide scripted runs for longer scenarios.

**E2E Tests:**

- Framework: Playwright, Chromium only, WebGL via SwiftShader (`--use-angle=swiftshader`, `--enable-unsafe-swiftshader`).
- Runs against the built e2e app (`vite build --mode e2e`, served by `vite preview` on port 4173), never the dev server (ENG-51).
- The game exposes `window.__GAME_TEST__` in `e2e` mode only (ENG-52): `getState()`, `setSeed(n)`, `step(frames)`, `pause()`, `sendAction(action)`. Specs read state through `gameState(page)` and `expectState(page, {...})` from `tests/e2e/menu-helpers.ts`.
- Every e2e test fails on console errors, uncaught exceptions, or audio warnings (`tests/e2e/fixtures.ts`, ENG-53, P12-R05). Import `test` and `expect` from `./fixtures`, never from `@playwright/test` directly, so the guard is active.
- Specs run fully parallel (`fullyParallel: true`); tests share no state.
- `forbidOnly` in CI; `retries: 1` in CI; artifacts (trace, screenshot, video) retained on failure.
- Smoke suite (ENG-54) is `tests/e2e/smoke.spec.ts`.
- Example spec shape (from `tests/e2e/smoke.spec.ts`):
  ```typescript
  test('ENG-54, P12-R12: loading → title → ship select → ... → back to title', async ({ page }) => {
    await page.goto('./');
    await expect(page.locator('.title-screen')).toBeVisible({ timeout: LOAD_TIMEOUT });
    await expectState(page, { screen: 'title', selectedId: 'start' });
    await sendAction(page, 'confirm');
    await expectState(page, { screen: 'ship-select', selectedId: 'balanced' });
  });
  ```
- Use `LOAD_TIMEOUT` from `tests/e2e/menu-helpers.ts` for the initial load wait, and `advance(page, seconds)` to step the simulation rather than sleeping.

## Common Patterns

**Async Testing:**

```typescript
it('P01-R02: shows a loading screen with real progress, then the title by itself', async () => {
  app = startApp(new NullEngine(), SAMPLE_GAME, options({ overlay }));
  expect(screenOf(overlay)).toBe('loading');
  await app.loaded;
  expect(app.loadingProgress).toEqual([0, 0.25, 0.5, 0.75, 1]);
});
```

- `await` the object's `loaded` promise (or equivalent) rather than sleeping.
- For e2e, use `await expect.poll(async () => ...).toBe(...)` to wait on state changes.
- Deterministic time: call `app.tick(dt)` with explicit values; no `setTimeout` waits in unit tests (ENG-46).

**Error Testing:**

- Assert the message text when a function throws, because messages are part of the contract (see Error Handling in `CONVENTIONS.md`). Check the existing `tests/unit/app/*.test.ts` files for the exact `toThrow(...)` style before adding one.
- For invalid input that should fall back to a default (not throw), assert the returned value. Example from `tests/unit/app/saved-settings.test.ts`: `expect(parseVolume(null, 10, 6)).toBe(6);`.

**Numeric Comparisons:**

- Use `toBeCloseTo(value, digits)` for floating-point results (e.g. `expect(app.clock.stepSeconds).toBeCloseTo(1 / 60);`).

**Determinism Checks:**

- Seeded RNG tests in `tests/unit/core/math/rng.test.ts`. Simulation tests should pass the same seed and compare results across runs.

---

_Testing analysis: 2026-10-27_
