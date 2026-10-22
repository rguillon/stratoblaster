# Decisions log

> Agent appends an entry for every non-trivial technical choice not dictated by the specs
> (library choice, architecture pattern, deviation from a SHOULD, etc.).
> Human may veto by changing the status to `Rejected` and explaining why — the agent then reworks it in the next "Fix phase".

## Template

### D-NNN — <title>
- **Date:** YYYY-MM-DD
- **Phase:** N
- **Context:** why a decision was needed
- **Decision:** what was chosen
- **Alternatives considered:**
- **Consequences:**
- **Status:** Accepted / Rejected / Superseded by D-xxx

---

<!-- Entries below -->

### D-001 — 3D engine: Babylon.js + TypeScript + Vite
- **Date:** 2026-10-22
- **Phase:** 0 (specs)
- **Context:** The game is a fully client-side 3D shoot 'em up with high visual quality: dynamic shadows, lighting, glow/bloom, particles (explosions, smoke, fire). It is served as static files from GitHub Pages.
- **Decision:** TypeScript (strict) + Babylon.js, built with Vite.
- **Alternatives considered:**
  - *Three.js*: the largest ecosystem, but particles (three.quarks), post-processing (pmndrs/postprocessing), an inspector and audio all need third-party libraries. More glue code and more versions to keep in sync.
  - *PlayCanvas*: excellent, but built around its cloud editor. The code-first workflow is less common.
  - *Unity / Godot web export*: large builds, slow load times, weak unit/e2e testing in a JS toolchain, and harder CI.
  - *Raw WebGL/WebGPU*: far too much engine work.
- **Consequences:** Babylon comes with shadows, PBR, a post-processing pipeline, GPU particles with fire/smoke/explosion presets, glow, an audio engine, `NullEngine` for headless unit tests, WebGPU support and an inspector. The bundle is larger than Three.js, so deep ES-module imports for tree-shaking are needed (ENG-02, ENG-107).
- **Status:** Accepted

### D-002 — Toolchain versions: ESLint 9 and TypeScript 6.0
- **Date:** 2026-10-22
- **Phase:** 0 (scaffold)
- **Context:** ENG-12 requires `eslint-plugin-import`, whose latest release (2.32) supports ESLint ≤ 9. `typescript-eslint` 8.x supports TypeScript < 6.1.
- **Decision:** Pin ESLint `^9.39`, `@eslint/js` `^9.39` and TypeScript `~6.0.3`. Everything else is at its latest version (Vite 8, Vitest 5, Playwright 1.64, Babylon.js 9).
- **Alternatives considered:** ESLint 10 with `eslint-plugin-import-x` (deviates from ENG-12); TypeScript 7 (not supported by typescript-eslint yet).
- **Consequences:** Upgrade ESLint and TypeScript once the plugins support them; Dependabot will flag the updates.
- **Status:** Accepted

### D-003 — Scaffold conventions
- **Date:** 2026-10-22
- **Phase:** 0 (scaffold)
- **Context:** Several engineering requirements leave the mechanism open.
- **Decision:**
  - ENG-82: Vite `base: './'` (relative). The build works under any GitHub Pages sub-path without knowing the repo name.
  - ENG-45: pure GPU/visual setup files in `render/` and `fx/` use the `*.visual.ts` suffix; only those are excluded from coverage.
  - ENG-11 / ENG-142: layering is enforced with `import/no-restricted-paths` zones, Babylon is banned in pure code with `no-restricted-imports`, and `Math.random` / `Date.now` / browser globals with `no-restricted-properties` / `no-restricted-globals`. Additionally, nothing outside `app/` and `main.ts` may import `app/`.
  - ENG-100: `core/loop/FixedStepClock` (60 Hz, max 5 steps per frame, excess time dropped after a stall).
  - Prettier ignores `specs/`, `CLAUDE.md` and `.claude/` so human-written specs are never reformatted.
  - Vite `chunkSizeWarningLimit` raised to 1500 kB: Babylon alone exceeds the 500 kB default; ENG-107 is the real budget.
- **Consequences:** ENG-52 (test API) and the full ENG-54 smoke suite are not implemented yet; they need the title screen and gameplay, and will come with the phases that add them.
- **Status:** Accepted
