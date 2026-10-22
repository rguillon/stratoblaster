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

### D-004 — Player ship data and the `player_ship/` viewer
- **Date:** 2026-10-22
- **Phase:** 2
- **Context:** Phase 02 asks for 3 ship stat sets ("data only") and a test endpoint `player_ship/`. A few details were left open (Questions in the phase report).
- **Decision:**
  - The ship's `maxSpeed` is stored as `maxSpeedFactor`, a multiple of the roster's `baseSpeedPxPerSec` (100). Generic types are in `core/entities/player-ship.ts`, values in `src/game/config/player-ships.ts`.
  - `GameDefinition` becomes `GameDefinition<TView>` with a `view` slot. Its type (`GameView`, `render/game-view.ts`) is owned by the presentation layers, so `core/` stays Babylon-free while keeping a single game entry object (ENG-144).
  - `player_ship/` is a real page (second Vite HTML entry), included in the production build so it can be checked on GitHub Pages. `app/route.ts` picks the page from the URL path; `main.ts` stays the only entry script.
  - Viewer captions use plain DOM (`ui/`); `ui/` code takes `document` as a parameter and is unit-tested with a small fake (`tests/helpers/fake-dom.ts`) instead of adding jsdom.
- **Alternatives considered:** a query or hash route (`?view=player_ship`): a less natural URL. A dev-only page: could not be checked on the deployed site. Storing absolute px/s: the spec states speeds as factors.
- **Consequences:** If the viewer should not ship to players, removing the `playerShip` Vite input is enough.
- **Status:** Accepted

### D-005 — Procedural ship geometry and lighting without new dependencies
- **Date:** 2026-10-22
- **Phase:** 2
- **Context:** Ships are generated in code (GD-60). Babylon's `ExtrudePolygon` / `CreatePolygon` need the `earcut` package, and shiny PBR metal needs an environment map, which normally means downloading an `.env` file.
- **Decision:**
  - `render/geometry/`: an ear-clipping triangulation (≈40 lines) plus a flat-shaded planform prism builder for wings and tails, and a lathe helper along Z for fuselages and nacelles.
  - `render/environment/`: a 64×64 procedural sky-gradient cube map (`RawCubeTexture`) as the IBL source, plus ACES tone mapping and a glow layer that makes the reactors' emissive cores and exhaust cones bloom.
  - Engine wiring that needs a real WebGL context (`RawCubeTexture` fails under `NullEngine`) lives in `showcase-environment.visual.ts`, which is excluded from coverage per D-003. The pure face generation is unit-tested.
- **Alternatives considered:** adding `earcut` (a new runtime dependency); a downloaded `.env` file (needs a CC0 HDRI plus conversion); `StandardMaterial` specular only (does not read as shiny metal).
- **Consequences:** No new dependency and no asset download. Roughness blur on the procedural environment is approximate (mip-based, not prefiltered).
- **Status:** Accepted

### D-006 — Model animations (animated reactor flames)
- **Date:** 2026-10-22
- **Phase:** 2
- **Context:** After review, the reactor flames should move and flicker. Models are built by `ModelFactory` functions that return a plain node, and the viewer's frame time is injected (`frameSeconds`) so it can be driven in tests.
- **Decision:**
  - `render/model-animation.ts`: any node of a model can carry per-frame animations (`addModelAnimation(node, dt => ...)`, kept in a `WeakMap` so they go away with the node). `stepModelAnimations(root, dt)` runs those of a model; `ModelShowcase.update` calls it, so animations use the same injected frame time as the rotation.
  - The flame (`game/view/reactor-flame.ts`): an outer exhaust cone and a hotter inner cone whose length, width and brightness (`mesh.visibility`) flicker with a mean of sines at incommensurate frequencies, plus plasma puffs that loop from the nozzle to the tip, shrinking and fading. Each reactor gets its own phase from a hash of its name, so reactors do not flicker in sync. Tunables are in `REACTOR_FLAME` (`game/config/ship-look.ts`).
- **Alternatives considered:** `scene.onBeforeRenderObservable` inside each reactor (bypasses the injected frame time, harder to test); Babylon particle systems (need pooling per ENG-105 and a texture; better kept for when ships move); a `ModelFactory` returning `{ root, update }` (changes every factory and fixture for one feature).
- **Consequences:** Future animated parts (blinking lights, turrets) use the same hook. Whatever drives models in gameplay must call `stepModelAnimations`.
- **Status:** Accepted

### D-007 — Low-poly, polygonal ship models
- **Date:** 2026-10-22
- **Phase:** 2
- **Context:** After review, the ships should use polygons rather than cylinders, and the light ship's polygon count was too high (9.6k triangles, mostly from 400-triangle spheres used for small lights and plasma puffs).
- **Decision:**
  - Every ship part is flat-shaded: prisms for flat parts, and `createFacetedLatheAlongZ` (`render/geometry/lathe-z.ts`) for bodies of revolution. Fuselages (and the parts sitting on them) use a split section (`BODY_SECTION`): 20 fine facets over the upper half for a smooth top, 3 for a low-poly belly. Other parts have 6 equal sides (`PART_FACETS`, `game/view/ship-parts.ts`). The faceted lathe is built directly (`buildFacetedLatheVertexData`), as Babylon's lathe only supports equal sides. Reactors are always hexagonal, with polygonal ring bands and 6-sided flame cones.
  - Nav lights are octahedra and plasma puffs icosahedra. The flames stay smooth-shaded (translucent glow).
  - Budget: each player ship stays under 2,000 triangles; the viewer shows the count under each ship.
- **Alternatives considered:** smooth low-tessellation meshes (look blobby rather than faceted); a per-ship opt-in (inconsistent style across the roster).
- **Consequences:** Balanced 1,150, heavy 1,086, light 1,722 triangles, down from 15k to 19k. New parts should use the faceted helpers.
- **Status:** Accepted
