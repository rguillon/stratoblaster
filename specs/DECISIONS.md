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

### D-008 — Menu architecture (phase 01)
- **Date:** 2026-10-23
- **Phase:** 1
- **Context:** Phase 01 adds the menu flow, three input devices, an HTML overlay and 3D scenes behind it, while keeping the engine game-agnostic (ENG-140) and the flow logic pure (P01-R01).
- **Decision:**
  - The screen state machine (`MenuFlow`) lives in `app/` as the phase asks, but is pure (no Babylon/DOM); the screen ids and transition table are in `core/menu/` so `render/` (backdrop) can use them, since nothing may import `app/` (D-003).
  - `MenuAction` (`up/down/left/right/confirm/back`) is defined in `input/`. Tapping a non-selected entry produces a seventh command, `{ select: index }`, because none of the six actions means "select entry N"; tapping the selected entry produces `confirm` (P01-R12).
  - The first ship of `PlayerShipRoster` is the default selection (Balanced in this game), rather than a new `defaultShipId` field.
  - `GameDefinition` gains `screen` (logical resolution, GD-02), `levels` (`LevelCatalog`), `texts` (`MenuTexts`: every menu string, ENG-140) and `view.menuBackdrop` (the 3D scene behind the menus, built by the game). The level grid helper `buildLevelGrid` is generic (`core/content/`); the 5 × 5 data and the unlocked list are in `src/game/`.
  - Two Babylon scenes: the game's backdrop is rendered on every menu screen; the engine's ship select stage is rendered over it (`autoClear = false`) on the ship select screen only. The backdrop hides its own ship there (`MenuBackdrop.showScreen`). Both scenes are built and their shaders compiled behind the loading screen, in 4 steps that drive the progress bar (ENG-108).
  - The highlighted ship is scaled up, sits on a glowing neon ring and is the only mesh lit by a key light (`includedOnlyMeshes`), so the others look dimmed; their HTML cards are faded too.
  - The canvas and the overlay share a `#stage` box fitted to the window with the 3:4 ratio (letterboxed). The overlay is laid out at 480 × 640 CSS px and scaled with a CSS transform.
  - Input is ignored during a screen transition (P01-R15) by a timer inside `MenuFlow`, so the test API obeys the same rule as the devices.
  - Menu entries are `div role="button"`, not `<button>`, so a focused button never turns Space/Enter into a second confirm.
- **Alternatives considered:** one scene with two cameras and layer masks (glow layer and clear handling get tricky); a canvas sized to the whole window with only the overlay letterboxed (ships would not line up with their cards on wide windows); jsdom-free UI tests with the existing fake DOM (too much fake API for event handling, see D-009).
- **Consequences:** Gameplay phases add a `play` screen to the flow (the `game` placeholder goes away) and reuse `MenuInput` / `HoldRepeater` for pause menus.
- **Status:** Accepted

### D-009 — `happy-dom` for UI unit tests
- **Date:** 2026-10-23
- **Phase:** 1
- **Context:** The menu overlay uses clicks, `classList`, `querySelector` and SVG elements. The fake DOM of D-004 would need to reimplement much of that.
- **Decision:** Add `happy-dom` (MIT, dev dependency only, not shipped) and opt in per test file with `// @vitest-environment happy-dom`. Other tests stay in the `node` environment.
- **Alternatives considered:** jsdom (heavier and slower); extending `tests/helpers/fake-dom.ts`.
- **Consequences:** No runtime dependency added (ENG-05 does not apply).
- **Status:** Accepted

### D-010 — Persistence in cookies, despite ENG-07's `localStorage`
- **Date:** 2026-10-23
- **Phase:** 1
- **Context:** ENG-07 says persistence uses `localStorage`, but the vision ("any persistence shall be handled by cookies"), GD-51 and P01-R04/R14 ask for cookies.
- **Decision:** Follow the vision, GD-51 and the phase: `platform/cookie-storage.ts` (`max-age` = `cookie_max_age`, `SameSite=Lax`, default path) behind the `KeyValueStorage` interface. Keys are prefixed with the game id: `stratoblaster_high_score`, `stratoblaster_last_ship`. A missing, undecodable or non-integer value reads as 0 / none.
- **Alternatives considered:** `localStorage` (contradicts three other specs).
- **Consequences:** Switching to `localStorage` later is one new `KeyValueStorage` class. ENG-07 could be updated to say "cookies".
- **Status:** Accepted

### D-011 — ENG-52 check in `make build`
- **Date:** 2026-10-23
- **Phase:** 1
- **Context:** `__GAME_TEST__` must be absent from the production bundle (ENG-52), and an e2e or build test must check it.
- **Decision:** `main.ts` installs the test API under `if (__E2E__)`; `__E2E__` is a build-time constant, so the production build drops the branch and the `debug/test-api.ts` module. `make build` then greps `dist/` and fails if `__GAME_TEST__` is found. The API provides `getState()` and `sendAction()` for now; `setSeed`, `step` and `pause` come with gameplay.
- **Alternatives considered:** a Playwright test reading `dist/` (depends on `make build` running first, which `make e2e` does not do).
- **Consequences:** CI runs this check through `make build`.
- **Status:** Accepted

### D-012 — Dark menu background, despite GD-61's pastel background
- **Date:** 2026-10-23
- **Phase:** 1
- **Context:** Review feedback on phase 1 asked to make the background dark on all menu screens. GD-61 and P01-R05 ask for a pastel background.
- **Decision:** Follow the review feedback. `TITLE_LOOK` uses a dark night palette: sky from near-black blue (top) to dark plum (horizon), the fog/clear colour equal to the horizon, a near-black purple floor. The sun and the neon grid keep their bright colours for the synthwave contrast. The CSS behind the canvas and the loading screen gradient are dark too.
- **Alternatives considered:** only darkening the canvas clear colour (hidden by the sky, no visible change).
- **Consequences:** GD-61 / P01-R05 could be reworded to "dark background". A unit test checks the backdrop colours stay dark and the sun/grid stay bright.
- **Status:** Accepted

### D-013 — Cyberpunk HUD style for the menus, in CSS only
- **Date:** 2026-10-23
- **Phase:** 1
- **Context:** Review feedback on phase 1 asked for a more technological / cyberpunk UI.
- **Decision:** Restyle the overlay in `index.html` only, with no markup change: dark glass panels with neon corner brackets (drawn as background layers, so the `::before` / `::after` selection markers stay free), a HUD frame with corner brackets around each screen, CRT scanlines and a vignette over the stage (`pointer-events: none`), uppercase headings with a cyan/pink chromatic split, a skewed and briefly glitching title, monospace system fonts for readouts (hint with a `>` prompt and blinking cursor, score, percent, level numbers, version), a segmented loading bar and hazard stripes on locked levels. Animations stop under `prefers-reduced-motion`. Large sans-serif text stays for entries and names, for kids.
- **Alternatives considered:** a bundled techno font (adds an asset and a licence to check; system monospace is enough); `clip-path` cut corners (they clip the glow of the selected entry).
- **Consequences:** The selection is still shown by the white frame, ▶ ◀ / ▲ markers and the dashed outline (P01-R13 greyscale criterion). Ship card stat lines may wrap instead of overflowing on narrow cards.
- **Status:** Accepted

### D-014 — Cyberpunk, not synthwave: generated night city and yellow / cyan / red HUD
- **Date:** 2026-10-23
- **Phase:** 1
- **Context:** Review feedback asked to remove the pastel background requirement and to make the UI look cyberpunk rather than synthwave. The striped sun and the pink neon grid were the most synthwave part.
- **Decision:**
  - Specs: the reviewer asked for the pastel requirement to go, so it was removed from GD-61, P01-R05, P01-R13 and the phase notes, and the phase text now says "cyberpunk, not synthwave". The `title_grid_scroll_speed` tunable became `title_city_scroll_speed`. GD-60 ("cyberpunk/synthwave") was left as is: it covers the whole game, not only the menus.
  - Backdrop: `game/view/city-geometry.ts` (pure, no Babylon) generates a street of dark towers in two rows, lit windows on the street side, neon roof trims and blade signs with bars as "text", dashed lane lines, a flat distant skyline and rain streaks, from a seeded mulberry32 generator (`core/math/rng.ts`, seed 2077), so the city is the same on every run. Each piece is two merged vertex-coloured meshes (dark structure excluded from glow, neon lights glowing). Two copies of a 200-unit chunk scroll towards the camera and wrap; the rain mesh holds its pattern twice and wraps the same way. Neon meshes use a 0.45 emissive scale: at full brightness the glow layer and ACES tone mapping turned the signs into white blobs.
  - Overlay: acid yellow `#fcee0a`, cyan `#00f0ff` and red `#ff2a55` on black; chamfered panels (`clip-path`) except on level cells, where it would hide the dashed outline of the selected cell; the selected entry is a solid yellow block with black text (also obvious in greyscale) plus its markers; logo in black on a yellow plate with a red / cyan glitch; `//` heading tags, a decorative `NET//LINK OK` tag, red locked state and "Locked!" status; a condensed system font stack (Bahnschrift, DIN, Roboto Condensed, Arial Narrow) before the previous fallbacks. The ship select ring is yellow (`config/menu.ts`).
  - `buildStripedDisc` and `render/geometry/floor-grid.ts` were removed with their tests (no other user).
- **Alternatives considered:** keeping the sun and grid and only recolouring them (still reads as synthwave); a `DynamicTexture` for windows (needs a canvas, does not work in the `NullEngine` unit tests); instanced boxes (more draw calls than two merged meshes per chunk).
- **Consequences:** About 4 draw calls for the city plus skyline and rain; 60 FPS still to be checked manually. The city's look is tuned in `game/config/title-look.ts`.
- **Status:** Accepted

### D-015 — Player shots: data-driven weapons, pure `ShotWorld`, defaults for unspecified values
- **Date:** 2026-10-23
- **Phase:** 3
- **Context:** Phase 3 asks for three weapons (bullet, laser, missile) with five levels and a `player_shots/` debug page. There is no gameplay or enemies yet, and the spec leaves speeds, fire rates, laser damage, missile motion and stream spacing open. The reviewer said the page is only for visual validation and may be built without gameplay.
- **Decision:**
  - Engine (`core/`): weapons are data (`WeaponDefinition`: projectile streams per level, or beam levels), registered through `GameDefinition.playerWeapons`. `ShotWorld` is a pure fixed-step simulation (fire volleys, constant velocity or constant acceleration up to a cap, homing on the closest living target re-chosen every step, direct or area damage, beam tracing with piercing that drops one level per target, pooled projectiles) against `ShotTarget` circles. Angles are in degrees from forward (+Y), positive to the right; playfield coordinates are logical pixels with Y up.
  - Presentation: `GameView.playerShotRenderers` maps weapon ids to `ShotRenderer`s fed a `ShotFrame` per frame; `GameView.playerShipScale` sizes ship models on the playfield. Shots are additive, vertex-coloured meshes (black is transparent), so soft edges need no texture and work in `NullEngine` tests. Nodes are reused through `NodePool`.
  - Unspecified values (bullet speed 600 px/s, 8 shots/s, 12 px dual spacing; laser 40/60/85/115/150 damage/s and 4-12 px widths; missile 150 → 700 px/s at 600 px/s², 180°/s homing, flat area damage; symmetric diagonals) are defaults in `game/config/player-weapons.ts`, listed in the phase report for review.
  - Debug page: orthographic top-down view of the 480×640 playfield, one ship at a time, dummy targets (a column for laser piercing, two side targets for homing), stream guides, controls and keys.
- **Alternatives considered:** Babylon `ParticleSystem` for laser particles (needs a texture; a small seeded particle stepper is enough and testable); class hierarchy per weapon (data plus two kinds covers the three weapons); showing all three ships at once (too cluttered on a 480 px wide playfield).
- **Consequences:** Gameplay phases can reuse `ShotWorld` per ship with enemy hitboxes as targets. Changing the numbers needs no code change.
- **Status:** Accepted

### D-016 — Game renamed Stratoblaster
- **Date:** 2026-10-23
- **Phase:** — (direct request, between phases 3 and 4)
- **Context:** The game is named Stratoblaster; the project used a working name until now.
- **Decision:** Every reference was replaced (`package.json` name, game id and title, page titles, README, specs, tests). The game id is the cookie prefix, so the cookies become `stratoblaster_high_score` and `stratoblaster_last_ship`. The title logo went from 68 px to 46 px (with less letter spacing) so the 13-letter name fits the 480 px screen; an e2e check now fails if the logo is wider than the screen.
- **Consequences:** A high score or last ship saved under the old cookie prefix is not read any more (no migration: nothing has been released). Git history, existing tags and the local folder name keep the old name.
- **Status:** Accepted

### D-017 — Title logo shrinks to fit the screen
- **Date:** 2026-10-23
- **Phase:** — (CI fix, between phases 3 and 4)
- **Context:** The menu uses system fonts only (P01-R05). On the Ubuntu CI runner none of the condensed fonts in the stack exist, so the logo falls back to DejaVu Sans and comes out 511 px wide on the 480 px screen; the D-016 e2e check fails.
- **Decision:** After a screen is mounted, `shrinkToFit()` (`src/ui/shrink-to-fit.ts`) lowers the logo's font size 1 px at a time until it fits its parent. The CSS size (46 px) stays the target on systems that have a condensed font.
- **Alternatives considered:** A smaller fixed size (shrinks the logo everywhere, and still depends on the widest fallback); bundling a font file (larger download, changes the system-fonts choice).
- **Consequences:** The logo can be a few pixels smaller on systems without condensed fonts.
- **Status:** Accepted

### D-018 — Faster CI
- **Date:** 2026-10-23
- **Phase:** — (direct request, between phases 3 and 4)
- **Context:** CI took about 3.7 min, almost all in the `e2e` job (about 3 min of tests at 2 workers, with software WebGL, plus 35 s of install). `check` (about 1.2 min) runs in parallel and was not the bottleneck.
- **Decision:**
  - `e2e` runs as a 3-shard matrix (`make e2e E2E_ARGS=--shard=N/3`), each shard on its own runner with the Playwright browser cache (ENG-72). `fullyParallel` is on, so shards are balanced per test rather than per file; the tests share no state.
  - `check` runs `make install SKIP_BROWSER=1`: unit tests run in Node, so Chromium and its system libraries are not installed there (ENG-71 still goes through `make install`).
  - The two fixed 1 s waits in the viewer e2e tests became `waitForFrames()` (10 animation frames).
- **Alternatives considered:** Running `e2e` in the `mcr.microsoft.com/playwright` image to skip `--with-deps`: the image has no `make`, so `apt-get install make` plus the image pull (about 2 GB) costs as much as it saves, and the image tag must be kept in sync with `@playwright/test` by hand. More workers on one runner: software rendering is CPU-bound and the runner has 4 vCPUs.
- **Consequences:** CI uses about 3× the e2e runner minutes (free for a public repository). Each failed shard uploads its own `playwright-report-N` artefact.
- **Status:** Accepted

### D-019 — ESLint 10 with eslint-plugin-import-x
- **Date:** 2026-10-23
- **Phase:** — (direct request, between phases 3 and 4)
- **Context:** Supersedes the ESLint part of D-002. `eslint-plugin-import` (last release 2.32.0, June 2025) still supports ESLint ≤ 9, which blocked Dependabot's ESLint and `@eslint/js` updates.
- **Decision:** Replace `eslint-plugin-import` with its maintained fork `eslint-plugin-import-x` (4.17) and upgrade `eslint` and `@eslint/js` to 10. Rules keep the same names under the `import-x/` prefix (`no-restricted-paths`, `no-default-export`); resolution uses `import-x/resolver-next` with the TypeScript and Node resolvers. TypeScript stays at `~6.0.3`: `typescript-eslint` 8.x still requires TypeScript < 6.1, so Dependabot ignores `typescript` ≥ 6.1.
- **Alternatives considered:** Staying on ESLint 9 until `eslint-plugin-import` supports 10 (no release in over a year).
- **Consequences:** ENG-12 names `eslint-plugin-import`; the human owner is to update it to `eslint-plugin-import-x`. Lint, test and Actions updates are grouped in Dependabot so peer-linked packages move together.
- **Status:** Accepted

### D-020 — Generated levels: data-driven terrain, tilted playfield camera, `level_zero/` page
- **Date:** 2026-10-23
- **Phase:** 4
- **Context:** Phase 4 asks for the tools that generate the real levels: a sculpted heightmap with textures blended by slope and altitude, an optional sea, optional cloud layers, props on flat ground, a camera tilted 35°, and a level of about 3 minutes. Gameplay does not exist yet. The reviewer accepted the 11 proposed defaults of the phase report ("defaults OK").
- **Decision:**
  - Units: one world unit is one logical pixel. X runs across the level (0 under the middle of the playfield), Z runs along it (the level scrolls towards +Z) and Y is up. The playfield is a plane at the flight altitude (320).
  - `core/scenery/` (pure, seeded): a `SceneryLevel` is a list of sections, each `seconds` long at the level's scroll speed, so the duration is simply the sum of the sections. Each section is a fractal relief (smooth or ridged, with a soft cap that keeps peaks under the flight plane) plus optional sculpt operations: `flatten` (plateau), `channel` (canyon along a winding line) and `shore` (coast). Neighbouring sections blend over a transition length. `PropPlacer` decides each grid cell from a hash of its coordinates, so terrain chunks can be placed in any order. `ScrollTrack` converts time to distance and handles the end of the level.
  - Camera (P04-R05): perspective, tilted 35° from straight down towards +Z, with a 40° vertical FOV. It is placed so that the bottom and top of the screen pass through the bottom and top edges of the 480×640 playfield (`render/scenery/playfield-framing.ts`).
  - Terrain: chunks of 320 × ~1100 units on an 8-unit grid, kept only around the camera; their meshes are reused (ENG-19). Normals come from one extra ring of height samples, so chunk seams do not show.
  - Look (`*.visual.ts`, not unit-tested): four ground textures and a noise texture generated in code at load time. A `StandardMaterial` plugin blends them by altitude and slope, using triplanar sampling and noise-jittered borders, and adds a surf band at the sea level, so standard lighting, shadows and fog still apply. The sea is a PBR plane with a drifting generated normal map (sky reflection and sun glint, no mirror reflection). Each cloud layer is a small shader over equalised noise, so coverage maps directly to the share of sky covered. The sun casts PCF shadows from the terrain and the props. A plain `SceneryKit` (flat `StandardMaterial`s) stands in for the real one in `NullEngine` unit tests.
  - Props (P04-R04): each model is pure vertex-coloured, flat-shaded geometry built with `render/geometry/solids.ts`. Each kind is drawn as one thin-instanced mesh, plus one for its self-lit accents (ENG-104). The glow layer only draws those accent meshes, so neon rings are open bands with no end caps (caps hidden inside a building would glow through it).
  - Content contract: `GameDefinition.sceneryLevels` (data) and `GameView.scenery` (camera, one look per level, one model per prop kind). Level Zero lives in `src/game/` and is not listed in level select. `src/game/config/` may import only `core/`, so the look is plain data there and typed in `game/view/scenery-bindings.ts`.
  - Debug page `level_zero/`: a fourth Vite entry, route `scenery-viewer`. It shows the first ship parked on the playfield, plus controls for pause, ×4, restart, seek, new seed, sea, playfield outline, and each cloud layer's on/off, intensity and opacity.
- **Alternatives considered:**
  - Babylon `WaterMaterial`: it renders reflection and refraction targets every frame, which is too costly for ENG-101.
  - A full `ShaderMaterial` for the terrain: it would need its own shadow and fog code.
  - One mesh per prop: too many draw calls.
  - An in-browser level editor that saves levels: rejected in the phase questions (Q2).
- **Consequences:**
  - With a perspective camera, the playfield seen on screen is a trapezoid. About 293 of the 480 logical pixels are visible across the bottom edge and about 493 across the top edge. The gameplay phase has to decide how ships map to the screen.
  - Quality presets (ENG-102) do not exist yet, so the shadow map size and the terrain grid are fixed.
  - New levels are data plus a look; new prop kinds are a geometry function plus a rule entry.
- **Status:** Accepted

### D-021 — Roads and paths, with buildings only along them
- **Date:** 2026-10-23
- **Phase:** 4 (review)
- **Context:** The reviewer asked for randomly generated roads or paths on the maps, with building props only along them, in the code and in the specs. The spec now has P04-R07.
- **Decision:**
  - `core/scenery/road-network.ts` (pure, seeded): `mainRoads` winding roads run along the whole level and a little beyond both ends (a sine meander plus noise wobble). Paths branch off a random main road every `crossSpacing`, going left or right with a gentle bend. Centre lines are sampled every `step`. Points under `minHeight` (the sea) or steeper than `maxSlope` are invalid, and valid pieces shorter than `minRun` points are dropped. Segments are indexed in 64-unit buckets for edge-distance queries.
  - Placement: buildings come only from slots every `slotSpacing` along the valid roads, on both sides. A building is set back `setback` from the road edge, faces the road, and must stay clear of the other roads. Buildings along paths also keep clear of the building rows of the roads they meet, so corners do not collide. Trees stay on their grid but keep `treeClearance` from road edges.
  - Ends off screen (review): no road starts or ends where the camera can see it (|X| < `offscreenX` = 420 in Level Zero; the camera sees up to about ±390). Each buildable run of a main road gets an exit turn at each end that is on screen. The turn runs towards the nearest side, then the other side, at `turnRate`, and is tried earlier and earlier along the run (4 points at a time, 40 tries) until it stays on buildable ground; otherwise the run is dropped. Paths start on a main road piece that passes there and run to beyond the screen edge. They try both directions and 3 bends, and are dropped if no try stays on buildable ground. Every road point is now buildable, so `RoadPoint.valid` is gone; points carry a width instead.
  - Junctions (review): a path widens to `junction.width` at its main road and narrows back to `crossWidth` over `junction.length` (smoothstep). Paths and roads are separate mesh layers, with paths at `alphaIndex` -2 and roads at -1, so roads are always drawn on top.
  - Look (review): every ribbon has 4 vertex rows. The outer shoulders fade to alpha 0 and the surface is slightly see-through and worn (hashed colour and opacity variation), so the road blends into the ground texture. Ribbons are blended without depth writes and drawn before the sea and clouds (`alphaIndex` -1).
  - Rendering: each terrain chunk gets one vertex-coloured ribbon mesh with the segments that start in it, draped on the height field, lifted 0.6 and pulled forward in depth (`zOffset`) so it never flickers against the terrain. It receives shadows.
  - Data: `SceneryLevel.roads` (`RoadRules`) and `SceneryLook.roads` (colours, lift). Level Zero has 2 main roads 6 units wide and paths 4 units wide.
- **Alternatives considered:**
  - Painting roads in the terrain shader: road data would have to go to the GPU, which is harder to keep chunk-local.
  - Flattening the terrain under the roads: changes the height field for little visible gain from this camera height.
  - A graph-based road planner (A* over slope): too much for a test level.
- **Consequences:** Sections with no usable road (open sea, steep mountains) get no buildings. A new seed (N) also changes the road network.
- **Status:** Accepted

### D-022 — Cloud layers always above the terrain
- **Date:** 2026-10-23
- **Phase:** 4 (review)
- **Context:** Cloud layers at fixed altitudes (170 and 250) cut through mountains and canyon walls, which looked bad. The reviewer asked for the clouds to stay on top.
- **Decision:** `terrainCeiling(level)` (`core/scenery/height-field.ts`) gives a height the ground never exceeds, whatever the seed. It takes, for each section, the highest of: the top of its relief (or its peak cap), its flattened band, and its sea bed. Carving only lowers the ground, and blending stays between neighbouring heights, so nothing else can raise it. `SceneryStage` places each layer at `max(look altitude, ceiling + cloudClearance)` (15 units). Level Zero's layers are now at 265 and 295: above the peaks (≤ 250) and under the ships (320).
- **Alternatives considered:**
  - Drawing the clouds without depth testing: they would also cover the ships.
  - Fading the clouds near the ground in the shader: it needs the scene depth, and the clouds would still look sliced.
- **Consequences:** A level whose ground rises close to the flight altitude leaves little room for clouds. The ceiling is a bound, not the real highest point, so it can sit a little above the actual peaks.
- **Status:** Accepted

### D-023 — Section ground cover, street grids, and dense, overlap-free buildings
- **Date:** 2026-10-23
- **Phase:** 4 (review)
- **Context:** The reviewer asked for three sections at the end of Level Zero: green ground with grass and trees, an industrial zone with a dense road maze packed with buildings, and a city centre.
- **Decision:**
  - `TerrainSection` gets four optional fields: `surface` (`lush` / `paved` shares), `trees` and `groups` (which tree kinds and building groups the section allows), and `streets` (a `StreetGrid`). `HeightField.surface(z)` blends the cover across transitions like the height.
  - Ground cover goes to the GPU in the terrain's vertex colours (red = 1 − lush/2, blue = 1 − paved/2), because Babylon already passes vertex colours to the standard material. The terrain plugin decodes it and mixes in two more generated textures (grass, concrete) through a noise threshold, so the cover comes in patches. The plain test material only shows a light tint.
  - Street grids (`core/scenery/street-grid.ts`):
    - A district is a run of consecutive sections with streets.
    - Each section adds streets across, from screen edge to screen edge, every `across` units; a street is kept only if it is all on buildable ground.
    - Each district adds `along` streets for its whole length. Like main roads, they turn off the screen at their ends, or run on past the ends of the level.
    - Streets across are drawn as paths (under the roads) and streets along as main roads.
  - Buildings are placed once per seed for the whole level, main-road slots first, with a bucket grid of placed footprints, so no two buildings overlap (gap = `setback`). This replaces the earlier rule that kept path buildings away from road building rows. `place(area)` returns the buildings whose centre is in the area, so chunks stay independent. Trees also avoid buildings.
  - New models: 3 living trees, 2 industrial buildings and 4 city buildings. City window bands are flat quads in dimmed colours (`windowDim`, `cyanDim`).
  - Level Zero: the sections were shortened (plains 14, hills 12, plateau 14, mountains 18, canyon 18, coast 14, open sea 14, landing 10) to make room for meadows, industrial zone and city centre (22 s each), still 180 s.
- **Alternatives considered:**
  - A per-section terrain material: hard seams at the section boundaries.
  - A custom vertex attribute: needs extra vertex shader code in the plugin.
  - Placing buildings per chunk with a neighbour check: the result would depend on the order chunks are built in.
- **Consequences:**
  - Placement now builds every building of the level up front, about 100 ms on a desktop and again after a new seed.
  - The city centre is the heaviest part of the level, at about 370k triangles.
- **Status:** Accepted

### D-024 — Straight street networks, buildings made of parts, stable shadows
- **Date:** 2026-10-23
- **Phase:** 4 (review)
- **Context:** In the industrial zone and the city centre, the reviewer wanted only straight road segments that merge into each other, with no winding roads or paths. They also asked for more diverse buildings, and for buildings that stop "blinking" as the ship advances.
- **Decision:**
  - `StreetGrid` is now `rows`, `columns` and `links`. `core/scenery/street-grid.ts` builds a rectilinear graph per district:
    - Each section has its own random columns (from past one screen edge to past the other) and rows.
    - The first and last rows of each section are always built, so the columns of two sections meet them at T-junctions.
    - Each other link is built with the chance `links`, if its ground is buildable.
    - A pass then removes dead ends on screen: it extends a street straight on, or cuts it back, until each one ends at another street or off the screen.
    - Built links are merged into maximal straight runs, which become roads of a new kind, `street`.
  - Winding roads and paths treat the districts as not buildable, so they turn off the screen before them, and paths no longer start there.
  - Street ribbons are opaque and unworn, and drawn in the road layer: crossings merge without seams.
  - Buildings made of parts (`game/view/props/industrial-parts.ts`, `city-parts.ts`): seeded generators register 8 variants each as their own prop kinds (`industrial-complex-N`, `city-building-N`), so they stay thin-instanced. Every part stays inside a fixed square (±12 and ±9 units), so one footprint per family holds; a test checks every variant.
  - Blinking: three causes and three fixes.
    - Shadows: the directional shadow frustum re-fitted to all casters every frame, so its texels swam as the view scrolled. The frustum is now fixed (`sun.shadow.frustum`, 1600 units, `autoUpdateExtends = false`), and `snappedLightPosition` moves the sun by whole texels across the light.
    - Specular: highlights on the flat-shaded facets changed with the view, so specular is now 0 on props and terrain.
    - Small lights: thin window bands smaller than a pixel aliased. Bands are now fewer and thicker, and the glow is down from 0.5 to 0.3.
- **Alternatives considered:**
  - Cascaded shadow maps: more passes, and they still need stabilising.
  - Snapping the camera instead: that makes the scrolling jerky.
- **Consequences:**
  - Shadows cover a fixed 1600-unit square around the view; beyond it there are none (it covers what the camera sees).
  - Model count is now 37: 21 hand-made and 16 made of parts.
- **Status:** Accepted

### D-025 — Bigger district buildings, square plans and fallback kinds
- **Date:** 2026-10-23
- **Phase:** 4 (review)
- **Context:** The reviewer found the blocks of the industrial zone and the city centre empty.
- **Decision:**
  - The generators made of parts take a half-side (`buildIndustrialComplex(seed, half)`, `buildCityBuilding(seed, half)`). `game/config/building-families.ts` lists 6 families of 8 variants: industrial complexes (half-side 12), works (18) and plants (30); city buildings (9), towers (14) and blocks (24, a wide podium with towers on it).
  - The industrial zone uses a `heavy-industry` group, mostly plants and works. The city group is mostly blocks and towers.
  - `PropKindRule.frontage` gives a square plan. Such a building stands right at the street setback, keeps that distance from other roads, and takes the box around its turned square for overlap tests. Other kinds still take the box around their footprint circle.
  - When a slot's drawn kind does not fit, it tries up to 3 smaller kinds of its group, from the largest down.
  - Slots are every 24 units instead of 34; the wasteland building densities were scaled by 0.7.
- **Alternatives considered:** Filling the inside of the blocks with yards or parking lots; that was not asked for, and might suit a later level.
- **Consequences:** The industrial zone draws about 550k triangles, the heaviest part of the level, to be checked against ENG-101 on real hardware. Quality presets could lower the density there.
- **Status:** Accepted

### D-026 — City blocks filled by podiums
- **Date:** 2026-10-23
- **Phase:** 4 (review)
- **Context:** The reviewer wanted bigger skyscraper bases, packed so that no bare ground shows in the city.
- **Decision:**
  - The street grid returns its blocks. A block is the cell between four grid lines, inset by half a street plus a 0.5 kerb on each side with a built street, and not inset on a side without one, so neighbouring blocks meet across a missing street.
  - A section with `blocks` (`BlockFill`) gets one podium per block: a unit-square model, stretched by a per-axis `PropPlacement.size` (thin-instance matrices support non-uniform scale) to the block and a random height.
  - 2–4 towers stand on each podium, one per part of the block (2 × 2 when it is wider than 40). Each is chosen among the section's kinds that fit the part, preferring the largest (within 75 %).
  - Street-front slots are skipped in those sections.
- **Alternatives considered:** Packing street-front buildings tighter still: this cannot guarantee full coverage of irregular blocks.
- **Review follow-up:** the city now uses an irregular grid (rows 45–95, columns 50–110, 70 % of links) and podiums 3–18 high. Blocks are cut into parts of about 30 (up to 3 × 3) for 2–9 towers, each shifted within its part.
- **Consequences:** The city reads as one continuous built mass, dark with lit bands. Podium window bands are stretched with the block, so they sit 0.002 units (scaled) off the walls.
- **Status:** Accepted

### D-027 — City buildings made of lots, along the factory streets

- **Date:** 2026-10-23 (phase 4 review)
- **Context:** Even with an irregular grid, podiums stretched over whole blocks still read as a series of squares.
- **Decision:**
  - The city centre uses the same street maze as the industrial zone and gets its buildings along the streets, without `blocks`. The city podium models are removed; the `blocks` option stays in the engine (D-026).
  - A city building is split into 1–4 unequal lots, each with its own facade and one of five volumes: stepped tower, round tower, slab, courtyard or L-shaped block (`city-lots.ts`).
  - Towers stand on a low base covering their lot.
- **Alternatives considered:** Keeping podiums with non-rectangular cut-outs: more geometry code, and it still reads as one mass per block.
- **Review follow-up:** to hide the ground, the city fills its blocks again, with `blocks` and no podiums. Buildings stand on the ground, one per part of about 30 (up to 4 × 4 parts), with no street-front slots. The city then draws about 1.04 M triangles at its densest.
- **Consequences:** The centres of deep blocks may show some ground, as in the industrial zone. The city draws about 0.95 M triangles at its densest (it was about 0.33 M), which still needs a check on real hardware against 60 FPS (ENG-101).
- **Status:** Accepted

### D-028 — Street corners, centre lines and cars

- **Date:** 2026-10-23 (phase 4 review)
- **Context:** Street corners showed notches and dark patches where soft edges overlapped. The review asked for a yellow centre line and cars.
- **Decision:**
  - Streets are drawn half their width past both ends, with a narrow soft edge (`streetShoulder`).
  - Centre lines are optional in `RoadLook` (`centreLine`), painted into the road mesh after the ribbons: solid on streets, broken where another street crosses (`inCrossing`), and dashed on main roads.
  - Cars are an optional `PropRules.cars` rule: one hashed draw per point of the streets and main roads, in a lane each way, and none in crossings. They are drawn as ordinary props (thin instances).
- **Alternatives considered:** Moving cars: they would need a traffic simulation and an update per frame (done later, see D-030).
- **Consequences:** Cars were static at first (superseded by D-030). A crossing test runs against every street for each line piece and car, which is cheap at this level's street counts.
- **Status:** Accepted

### D-029 — 2×2 roads

- **Date:** 2026-10-23 (phase 4 review)
- **Context:** The review asked for bigger roads, with two lanes each way.
- **Decision:**
  - `RoadRules.dual` sets the 2×2 roads: the first `mainRoads` main roads, and a share `avenues` of the street-grid lines. Each line is decided by a hash of its coordinate, so all its runs and the blocks beside it agree.
  - `Road.lanes` (1 or 2 each way) drives the markings (`road-lines.ts`) and the car lanes.
- **Alternatives considered:** Drawing a 2×2 road as two parallel roads with a median: this doubles the road geometry and complicates junctions and building slots.
- **Consequences:** Building slots, setbacks and block insets follow the wider roads, so the layouts of the industrial zone and the city change.
- **Status:** Accepted

### D-030 — Moving cars

- **Date:** 2026-10-23 (phase 4 review)
- **Context:** The review asked for the cars to move.
- **Decision:**
  - Each car follows its road at a constant speed, without a simulation. Its distance along the road is `start ± speed · time`, wrapped to the road length, so a car's position at any time is a closed form.
  - All the cars of a lane share one speed, so they keep their spacing and never overlap. Cars are hidden near road ends, so the wrap is not seen.
  - The cars in view are uploaded every frame into their own thin-instance meshes, so the static props are never re-uploaded.
- **Alternatives considered:** Turning at crossings, or cars that follow each other with braking. These need a real traffic simulation with state, more than a test level needs.
- **Consequences:** Cars pass through each other at crossings, and vanish and reappear at street ends. Per frame, placing about 570 cars takes about 1.3 ms in Node, plus their matrix upload.
- **Status:** Accepted

### D-031 — Props drawn only near the view

- **Date:** 2026-10-23 (phase 4 review)
- **Context:** The review asked for fewer polygons. Thin instances of one kind share one mesh, so frustum culling works per kind, not per instance. Every prop of the loaded terrain chunks was drawn, up to about 400 past the view.
- **Decision:**
  - `PropField.setWindow` filters placements by Z to the ground in view, plus `propReach` (40 before, 120 past, for tall towers).
  - The filtered range is `propStep` (40) wider each way, so instances are uploaded again only every 40 or so of scrolling, not every frame.
- **Alternatives considered:** One mesh per kind and per chunk, so frustum culling works. This multiplies the draw calls by the number of chunks (about 130 kinds × 6 chunks).
- **Consequences:** A prop taller than about 80 standing past the window could pop in at the top edge. The tallest props are about 60 high.
- **Status:** Accepted

### D-032 — First enemies: abstract `Enemy` with hooks, `EnemyWorld`, `enemies/` page over Level Zero
- **Date:** 2026-10-24
- **Phase:** 5
- **Context:** Phase 5 asks for 10 enemy kinds (shape and behaviour) and an `enemies/` debug page. There is no gameplay loop yet, and the spec leaves speeds, paths, bullet speeds and looks open.
- **Decision:**
  - Engine (`core/`): `Enemy` is an abstract class (a `ShotTarget`) with an `update(ctx, dt)` hook and an optional `onDestroyed(ctx)` hook (ENG-148). `EnemyContext` gives the player position and lets an enemy fire bullets, homing missiles and lasers, or spawn enemies. `EnemyKindDefinition.spawn` creates one group of a kind. `EnemyWorld` steps enemies and their shots (`EnemyShots`), scores and blows up destroyed enemies, removes enemies once they have been on the playfield and left it (or after 40 s), and lists enemies and missiles as targets for the player's `ShotWorld`. Shot looks are style keys the game's renderers know.
  - Content (`src/game/`): one class per enemy (state machines), tunables in `game/config/enemies.ts`. Sizes use L = 34 px (the balanced ship: 4.8 model units × 7). Hit radius = 85 % of half the model size, smaller for the wide or long ones (Strafer, Lancer, Rocketeer, Bulwark). Enemies only shoot while their centre is over the playfield. Unspecified values (speeds, paths, bullet speeds, missile homing 3.5 s at 90°/s, Lancer laser 10 px wide) are agent defaults listed in the phase report.
  - Models: vertex-coloured, flat-shaded `SolidBuilder` geometry (new `slab` extrusion), one dark PBR metal mesh and one unlit neon mesh per model, plus "charge" lights whose brightness follows `Enemy.charge` (gun ready, Lancer warning, Rocketeer reload, Spinner firing).
  - Page: the Level Zero scenery and tilted camera of `level_zero/`, with a "playfield" layer node that turns the XY playfield space of the shot renderers onto the flight plane. `render/node-adopter.ts` parents everything the drawing code creates to that layer and puts it in the above-the-clouds rendering group; new nodes are found by Babylon's increasing `uniqueId` (the scene's "new mesh" observable fires asynchronously, so it misses them). A second glow layer, above the clouds, makes the neon glow; additive shots are left out of it. The ship is held inside what the camera shows (`visibleHalfWidth`). The model view is a separate close-up scene like `player_ship/` (phase 5 review: dark background, camera framed on the model, ← / → switch the enemy); the page renders either scene. `ShotWorld.firing` lets the page hold fire. e2e builds expose `window.__ENEMIES_TEST__` (state, frame stepping) and `make build` checks it is absent from production.
- **Alternatives considered:** data-only enemy definitions (movement + attack enums): too rigid for state machines like the Spinner or the Splitter. An orthographic top-down page like `player_shots/`: the spec asks for the Level Zero scenery and the playfield camera. Changing every shot renderer to take a parent node: the adopter keeps the phase 3 renderers unchanged.
- **Consequences:** New enemies are a class plus a model. The gameplay phase can reuse `EnemyWorld`, `EnemyLayer` and the playfield layer as is; it still has to decide player damage and wave spawning.
- **Status:** Accepted

### D-033 — Low-poly shaping primitives: `SolidBuilder.loft` and `bevelSlab`
- **Date:** 2026-10-24
- **Phase:** 5 (review)
- **Context:** The reviewer found most enemy ships looked like cubes put together (boxes and straight extrusions), and asked for better geometry without raising the polygon count much.
- **Decision:** Two engine primitives in `render/geometry/solids.ts`, flat-shaded like the others. `loft(section, stations)`: a convex cross-section (u across, v up) stretched through Z stations of half width, bottom and top; a zero-size station closes it to a point, `open` leaves the bottom side and caps out (canopies). `bevelSlab(outline, [y0, waist, y1], [insetBottom, insetTop])`: a slab whose sides slope from the outline at the waist to faces inset by a miter offset (`insetOutline`, tips clamped at 3× the distance). They cost about 2 triangles more per outline side or section side than a slab or box. Enemy models use them for fuselages, wings and plates.
- **Alternatives considered:** More sides on lathes and boxes: more polygons without changing the silhouettes. Smooth-shaded Babylon builders (`ExtrudeShape`, `CreateTube`): not vertex-coloured per face, and off the flat-shaded look of D-007.
- **Consequences:** About 19 % more polygons over the 10 enemy models in the close-up view. The player ships and props are unchanged; they can use the primitives later. Later in the same review, `loft` gained `paint` (some faces in another colour), so canopies are painted on one fuselage instead of being separate solids.
- **Status:** Accepted

### D-034 — Explosion particles as thin instances, one mesh per layer
- **Date:** 2026-10-24
- **Phase:** 5 (review)
- **Context:** The reviewer asked for bigger, more realistic explosions with burning debris. That means hundreds of particles per blast (fireballs, smoke, debris, trailing embers and smoke wisps), each with its own colour as it cools. The blast renderer drew each particle as a cloned mesh from a pool (one draw call each), coloured only by its vertex colours.
- **Decision:** `createBlastRenderer` draws each layer (smoke, shock rings, fireballs, debris, embers, flashes) as one disc mesh of thin instances, with a matrix and a colour per instance (`thinInstanceSetBuffer('color')`, multiplied into the vertex colours). The buffers grow by powers of two and are refilled every frame; `thinInstanceCount` shows the live part. Fire and smoke are alpha blended (vertex alpha, a soft disc); flashes, rings, debris and embers are added on. The meshes are never culled, and `alphaIndex` keeps smoke under fire. The `enemies/` page's glow layer leaves out vertex-alpha meshes, because the glow layer ignores instance colours and drew them white.
- **Alternatives considered:** Keep the node pool: up to about a thousand draw calls during a busy fight, and no colour per particle without a material each. Babylon's `ParticleSystem`: GPU-friendly, but it emits in world space with its own emitters and textures, and would not stay deterministic and unit-testable like the pure `BlastParticles` simulation.
- **Consequences:** An explosion, or many at once, costs six draw calls. Each layer is capped at 1200 particles. Any later effect drawn the same way must stay out of the glow layer or be additive.
- **Status:** Accepted

### D-035 — Water colour painted on the terrain, by depth
- **Date:** 2026-10-24
- **Phase:** 5 (review)
- **Context:** The reviewer found the sea/land junction ugly: the near-opaque sea plane cut the ground with a hard line, with a uniform band of foam on the land, and no shallows.
- **Decision:** The terrain shader colours the ground under the sea level by its depth (turquoise shallows to the deep sea colour) and paints the beach and the surf; the sea plane becomes mostly see-through (alpha 0.4) and only adds reflections and glints.
- **Alternatives considered:** A depth-aware sea shader (reading the depth buffer, or the height field as vertex alpha on a subdivided sea plane): the true water depth on the water itself, but a depth pass or a much denser sea mesh, costly on the software GPU of the tests.
- **Consequences:** No extra pass or mesh. The underwater ground is lit and shaded like land, so seabed relief shows faintly through the water. With the sea switched off, the ground has no water tint.
- **Status:** Accepted

### D-036 — Playable levels: `GameLevel`, distance-triggered wave runner, pure `LevelRun`
- **Date:** 2026-10-24
- **Phase:** 6
- **Context:** Phase 6 turns the placeholder game screen into real levels: scenery, wave scripts by distance (GD-40), a level end, difficulty per level, and debug shortcuts. The engine must stay game-agnostic (§2.3).
- **Decision:**
  - Content: `GameDefinition.gameLevels` lists `GameLevel`s (`core/content/game-level.ts`): a `SceneryLevel`, a `WaveScript` and an `EnemyDifficulty`; the id is the level select entry's. World 1 is data in `src/game/config/world-1/` (sections, props, looks, waves, difficulty) assembled in `src/game/sim/world-1.ts`. Wave beats are written in seconds for readability and turned into distances at the level's ground speed.
  - `core/systems/wave-runner.ts`: a wave is `{ at, kind, count, interval, entry, spread? }`; groups are queued by time once the distance is passed, so waves overlap. The runner only knows kind ids; `EnemySpawnArea.entry` (side + position) tells the kind where to come in, and kinds that cannot follow it (path kinds) mirror their path towards it.
  - Difficulty: `EnemyWorld` takes `{ bulletSpeed, fireRate }`; bullet speeds are multiplied when fired, and `EnemyContext.fireRate` is applied by each enemy to its attack timer (`tick(dt * ctx.fireRate)`). Carrier launches and Lancer lasers are not "fire rate" and stay as tuned.
  - `core/systems/level-run.ts` (pure): scroll, waves, `EnemyWorld`, `ShotWorld` (first weapon, level 1), `PlayerFlight` (top speed reached in 0.08 s, GD-10; bounds from the tilted camera). Phases `playing → clearing → complete`; `clearing` ends when no enemy is left or after `endWait` (10 s). `seek()` clears the screen and skips the waves before that point.
  - `app/game-play.ts` runs a `LevelRun` at 60 Hz over `app/level-scene.ts` (scenery + playfield layer, now shared with the enemies page); `app/game-session.ts` starts and ends it with the game screen. `MenuFlow.completeLevel()` shows the overlay; input is ignored for 1 s so a held fire key does not skip it; Confirm goes to level select on the next unlocked level (or the same one).
- **Alternatives considered:** waves triggered by time (the spec asks for distance); a data-only enemy spawn description (kinds already have their own spawn code, P05); running the level inside `MenuFlow` (it would mix menus and gameplay state).
- **Consequences:** a level is data plus a look; the player cannot be hit yet (out of scope), so the "Level complete" counts only enemies.
- **Status:** Accepted

### D-037 — Desert ground: a `sandy` ground cover and dunes in the height field
- **Date:** 2026-10-24
- **Phase:** 6
- **Context:** P06-R06 asks for a sand texture that fades into rock with slope and altitude, and dunes made with the heightmap tools.
- **Decision:** `Surface` gets `sandy`, stored in the free green channel of the terrain's vertex colours and mixed by the terrain shader like `lush` and `paved` (a new `TerrainLook.sand` texture; it only replaces the `ground` layer, so slopes still turn to rock). The desert looks also use sand for their `ground` and `low` layers and a red layered rock for `steep`, with a higher slope threshold so only cliffs are rock. `TerrainSection.dunes` adds crests every `wavelength` with a long windward slope and a short lee slope (78 % / 22 %), crest lines bent and heights varied by noise; `terrainCeiling` includes them. Desert levels have a lower side sun so the dunes cast shading.
- **Alternatives considered:** a separate desert terrain material (seams between sections); dunes as a sculpt operation along a path like `channel` (dunes cover whole sections).
- **Consequences:** no extra texture fetch outside sandy sections' blend; the sampler is named `terrainSandy` because `terrainSand` was already the shore's uniform.
- **Status:** Accepted

### D-038 — World 1 balance measured by a play-through without shooting
- **Date:** 2026-10-24
- **Phase:** 6
- **Context:** P06-R08 asks for enemy count, total HP and the peak on screen to go up strictly, and ~60/~80/~100/~120/~140 enemies with peaks 6/8/10/12/15. "On screen" depends on how well the player shoots.
- **Decision:** the unit test plays each level through with a ship that never fires (`tests/unit/game/sim/world-1.test.ts`), counting every enemy added (Carrier launches included), their health, and the most enemy centres over the playfield at once. Results: 66 / 82 / 124 / 156 / 184 enemies, 1320 / 1910 / 3310 / 4770 / 6940 HP, peaks 6 / 8 / 11 / 12 / 17; the second half always has more HP. Factors 0.8 / 0.85 / 0.9 / 1.0 / 1.1 for bullet speed and fire rate.
- **Alternatives considered:** counting from the scripts alone (misses Carrier launches and how long kinds stay on screen); a simulated player that shoots (results would depend on its aim).
- **Consequences:** counts in 1-3 to 1-5 are above the "~" tunables, mostly because each Carrier launches about 20 Gnats; the order is kept, as the tunables allow. A calm stretch around 1:50–2:10 in each level is left for a future mini boss / checkpoint (spec note).
- **Status:** Accepted

### D-039 — Game screen controls and debug options
- **Date:** 2026-10-24
- **Phase:** 6
- **Context:** P06-R02 asks for the GD §2 controls (keys, gamepad, touch drag and button); P06-R09 for URL debug options with the Level Zero playback keys, ignored without them.
- **Decision:** `input/game-controls.ts` merges held keys (arrows / WASD by position, Space), the left stick, D-pad and A / right trigger, and a touch drag (the ship covers the dragged distance at most at its top speed) with an on-screen fire button shown on coarse pointers only. The menu input keeps handling Esc (Back) and Confirm. `?level=…&t=…&ship=…` work in every build (so a reviewer can use them on GitHub Pages); with them, F toggles ×4 and ← / → jump 10 s, and those two arrows then do not move the ship (A / D still do). The FPS / polygons tile shows only in debug mode.
- **Alternatives considered:** debug options only in dev / e2e builds (ENG-111 style): the spec asks for them to check the levels by hand, including on the deployed game.
- **Consequences:** in debug mode, ← / → are taken by the playback keys.
- **Status:** Accepted

### D-040 — CRT scanline overlay removed
- **Date:** 2026-10-24
- **Phase:** 6 (review)
- **Context:** The CRT scanlines and vignette over the stage (D-013) drew visible horizontal lines across the playfield once the game screen showed real levels. The reviewer asked for the overlay to be removed.
- **Decision:** `#stage::after` (scanlines + vignette) is gone from `index.html`. The rest of the cyberpunk HUD (corner brackets, chamfered panels, colours) stays.
- **Consequences:** The menus lose their faint scanlines; the levels show without any overlay.
- **Status:** Accepted (partly supersedes D-013)

### D-041 — In-game HUD, no Back button over the playfield
- **Date:** 2026-10-24
- **Phase:** 6 (review)
- **Context:** The reviewer asked to remove the Back button from the in-game view and to add a basic HUD (health, weapon level, etc.).
- **Decision:** `ui/game-hud.ts` (`GameHud`), owned by the running level (`GamePlay`) and drawn in the menu overlay at the logical resolution: the ship's name and health bar, the weapon and its level, a bar of the level's progress, and the enemies destroyed. It updates every frame but only touches the page when a shown value changes, and never takes pointer input. Its texts come from `MenuTexts` (`hudHealth`, `hudWeapon`, `hudDestroyed`). The game screen view has no Back button; Esc / Backspace / gamepad B still leave (P06-R02).
- **Alternatives considered:** the HUD inside the game screen's `MenuView` (the overlay would re-render every frame); a Babylon GUI layer (a new package, and the menus are already HTML).
- **Consequences:** health shows full until the player can be hit (GD-20, a later phase); no score (GD-50, out of scope). On touch screens, leaving a level early waits for pause.
- **Status:** Accepted

### D-042 — Only enemies on screen can be shot
- **Date:** 2026-10-24
- **Phase:** 6 (review)
- **Context:** The reviewer saw explosion lights in the wrong place. Player bullets fly on until 80 px past the playfield, and enemies are targets as soon as they spawn, just above the top edge; the tilted camera also shows less than the playfield's width at the bottom. A play-through of 1-1 to 1-3 found 7–42 % of the explosions (5 to 29 per level) out of view, mostly just above the top edge, where only their glow showed.
- **Decision:** `LevelRunOptions.inView` decides which targets the player's shots can hit: only enemies and missiles whose centre is on screen. `GamePlay` gives it the camera's visible area (`visibleHalfWidth`); the default is the playfield rectangle. The same play-through now finds no explosion out of view.
- **Alternatives considered:** removing player shots at the top edge (shots near the edge would vanish before reaching an enemy just coming in); hiding blasts out of view (enemies would still die unseen).
- **Consequences:** enemies take no damage until they come into view. The `enemies/` debug page (phase 5) is unchanged.
- **Status:** Accepted

### D-043 — E switches weapon in game
- **Date:** 2026-10-24
- **Phase:** 6 (review)
- **Context:** The reviewer asked for a key to switch between weapons in game: E on an AZERTY keyboard. Phase 6 starts every level with the guns at level 1 (P06-R02); weapon pick-ups and upgrades come later (GD-31).
- **Decision:** `GAME_CONTROLS_CONFIG.switchKeys` (`KeyE`, a key position, so the same key on AZERTY and QWERTY) makes `GameControls` report one `switchWeapon` per press (key-down repeats ignored). `LevelRun` cycles through `LevelRunOptions.weapons` (the game's player weapons) at the starting level; shots in flight keep flying. The HUD shows the weapon fired. The ship still starts each level with the first weapon.
- **Alternatives considered:** a debug-only key (the reviewer wants it in the game); one key per weapon (1-3 are free, but one key was asked for).
- **Consequences:** GD §2 gives E to Special / bomb: bombs will need another key when they come. No gamepad or touch binding yet.
- **Status:** Accepted

### D-044 — Faster ships (+50 %) and denser waves (+50 %)
- **Date:** 2026-10-24
- **Phase:** 6 (review)
- **Context:** The reviewer asked to raise the player's base speed by 50 % and to increase the enemy density.
- **Decision:**
  - `PLAYER_SHIPS.baseSpeedPxPerSec` goes from 100 to 150 px/s: balanced 150, heavy 120, light 210 px/s. The ships' factors (P02-R01..R03) are unchanged. `specs/phases/phase-02-player-ships.md` still says 100 px/s: its requirement text is the reviewer's to update.
  - `WAVE_DENSITY` (1.5, `game/config/world-1/waves.ts`) multiplies the groups of every beat, rounded. A one-group beat gets its extra groups 1.5 s apart and 0.3 across the screen (from the top) or a little lower (from the sides), so they do not come in on top of each other. The beats stay written as before; `waveScript(speed, beats, 1)` gives the old scripts.
  - Measured as in D-038 (no shooting): 119 / 143 / 213 / 270 / 321 enemies, 2270 / 3180 / 5620 / 8130 / 11860 HP, peaks 11 / 14 / 16 / 18 / 22 on screen; each level's second half still has more HP. The strict order of P06-R08 holds.
- **Consequences:** the counts and peaks are now well above the spec's tunable values (~60 … ~140 enemies, peaks 6 … 15); 1-1 is busier than "easy for a kid" may allow, to be judged in the manual check. Supersedes the numbers of D-038.
- **Status:** Accepted

### D-045 — Ship banks when moving sideways; a felt acceleration
- **Date:** 2026-10-24
- **Phase:** 6 (review)
- **Context:** The reviewer asked for the player ship to roll when moving left / right, and for a little more acceleration in its movements.
- **Decision:** `GamePlay` banks the ship model around its nose by up to 35° at full sideways speed (the wing on the side it flies to dips), easing towards that at 8 per second, so it rolls in and levels out smoothly; it is visual only (`config/game-play.ts`, `roll`). The time from rest to full speed (`GAME_CONTROLS_CONFIG.accelerationSeconds`) goes from 0.08 s to 0.18 s, so starts and stops are felt (GD-10 still holds: top speed in under a fifth of a second).
- **Alternatives considered:** banking from the input instead of the speed (it would snap with the keys); a stronger acceleration (shorter time) — "more acceleration" was read as a more noticeable speed-up, a one-value change either way.
- **Consequences:** none on the simulation besides the longer speed-up.
- **Status:** Accepted

### D-046 — No road crossings; lone buildings and hamlets away from the roads
- **Date:** 2026-10-24
- **Phase:** 6 (review)
- **Context:** The reviewer found roads crossing each other ugly ("only path to road is permitted"), and asked for a few props not connected to roads, and for groups of buildings close together spawned from time to time. Roads, paths and street grids are phase 4 engine code (`core/scenery`), used by Level Zero too.
- **Decision:** Three opt-in rules, set for World 1 only (`world-1/props.ts`):
  - `RoadRules.noCrossings { gap }`: the street grids are laid first; each main road after the first follows the previous one on the side the first leaves free, from `gap` to `gap + 2 × amplitude` beside it, and every piece of main road keeps `gap` clear of the roads laid before it (pieces are laid one at a time, so a road leaving the screen and coming back does not cross itself); a path keeps `gap` clear of everything except the main road it starts on, and may end on another main road or street (it is cut there), never on a path; in street grids every crossing (a node with streets leaving it on all four sides) becomes a T-junction: its streets up or down the level are removed, then the dead ends are fixed again, never extending a street into a new crossing — one pass, as neither step makes a crossing.
  - `PropRules.loners { cell, chance, clearance }`: one building per square of `cell` units with the chance `chance × buildingDensity`, at least `clearance` from every road, of the area's building group, turned at random.
  - `PropRules.hamlets` (`HamletRules`): one every `spacing` along the level, in sections with buildings and no street grid; the centre is tried at 6 places across the level, away from the roads; 5–9 buildings of the area's group within `radius`, all facing about the same way, `gap` apart.
  World 1 values: gap 30; loners every 150 units with chance 0.15, 18 from the roads; hamlets every 700–1400 units, 5–9 buildings within 32, gap 2, 18 from the roads.
- **Measured** (fixed seeds, whole levels): road crossings on screen 0 / 23 / 14 / 83 / 266 before → 0 in every level; every path ends off screen or on a main road; lone buildings 0 / 4 / 5 / 16 / 3, hamlet buildings about 0 / 48 / 25 / 43 / 6 (1-1 is mostly sea, 1-5 mostly street grid). Lone buildings and hamlets stand within half of `offscreenX` of the middle, so most are in view.
- **Alternatives considered:** making it the engine default (it would rewrite Level Zero, phase 4, validated); keeping the main roads in separate bands across the screen (much smaller meanders); 4-way crossings kept in the city grids (the request had no exception for them).
- **Consequences:** World 1 roads and buildings change (other layouts from the same seeds). Level Zero is unchanged; to get the same there, set the three rules in `level-zero.ts`. `RoadNetwork` indexes each road as it is laid, and exposes `offscreenX`; paths are laid by `road-paths.ts`, lone buildings and hamlets by `away-placement.ts` (files kept under the lint size limits). A first version counted built links to find crossings; where two sections meet, overlapping links made it loop, and 1-5's roads took 44 s to generate (e2e timeouts) — counting sides fixed it (about 0.2 s, as before).
- **Status:** Accepted

### D-047 — Player base speed raised again, to 225 px/s
- **Date:** 2026-10-24
- **Phase:** 6 (review)
- **Context:** The reviewer asked for the ships' base speed to go up by 50 % again, after D-044 (100 → 150 px/s).
- **Decision:** `PLAYER_SHIPS.baseSpeedPxPerSec` 150 → 225: balanced 225, heavy 180, light 315 px/s. The ships' speed factors, the acceleration time (0.18 s to full speed, D-045) and the roll (scaled to each ship's top speed) are unchanged.
- **Alternatives considered:** raising the speed factors instead (the base speed is the one value the request names).
- **Consequences:** the light ship crosses the 480 px playfield in about 1.5 s. Enemy density and waves are unchanged. `phase-02-player-ships.md` still says 100 px/s (see D-044).
- **Status:** Accepted

### D-048 — Enemies from the top come in where the ship can reach
- **Date:** 2026-10-24
- **Phase:** 6 (review)
- **Context:** With the tilted camera the screen shows more of the playfield at the top (±247 px around the middle) than at the bottom (±146 px), and the ship's reach at the bottom is ±133 px. Enemies coming in from the top across 15–85 % of the width (up to ±168 px) could stay in an upper corner the player cannot shoot at.
- **Decision:** `EnemySpawnArea.topRange` (optional, default the whole width) is the X range the kinds coming in from the top keep to: their entry position, their random X range and the X of the paths that come in from the top (Gnat, Splitter) are fractions across it instead of across the width. `LevelRun` sets it to the ship's reach at the bottom of its flight area (`bounds.centerX ± bounds.halfWidthAt(bounds.minY)`: 107–373 px in the game). Side passes (Strafer) still cross the whole width. The `enemies/` page (phase 5) does not use `LevelRun` and is unchanged.
- **Measured** (no shooting, seed 606): enemies coming in from the top start between x 128 and 367; counts and HP unchanged; peaks on screen 11 / 14 / 15 / 18 / 20 (were 11 / 14 / 16 / 18 / 22), still strictly going up.
- **Alternatives considered:** the bottom edge of the screen (±146 px, a little wider than the ship can go); squeezing only the spawn X and not the paths (Gnats and Splitters would still sweep out to the corners).
- **Consequences:** waves are a little narrower; a Weaver's sway can still take it slightly past the range.
- **Status:** Accepted

### D-049 — Weapon bonuses dropped by destroyed enemies
- **Date:** 2026-10-24
- **Phase:** 6 (review)
- **Context:** The reviewer asked for bonuses dropped by some destroyed enemies that level the weapons up (GD-31). Phase 6 had them out of scope; asked, the reviewer moved weapon bonuses into phase 6 (bombs and extra lives stay out), chose that each weapon keeps its own level, and a drop chance by toughness.
- **Decision:**
  - Core: `BonusWorld` (`core/systems/bonus-world.ts`, pure). A destroyed enemy (`EnemyWorld.destroyed`, new) drops a bonus with the chance `perHealth × maxHealth` kept within [`min`, `max`], drawn from its own seeded random source (the enemies play the same with or without bonuses). The bonus drops within the ship's reach at the bottom of the screen (as D-048), falls at `fallSpeed`, and is picked up when the ship's centre comes within `pickupRadius`; missed ones go past the bottom edge. `LevelRun` raises the weapon in use by a level per bonus picked up (up to its last level; the shot cooldown restarts, so the new level fires at once), and keeps a level per weapon, so switching (E) gets each weapon back at its level. `LevelRunOptions.bonuses` is optional (none without it).
  - Content: `GameDefinition.bonuses` (`game/config/bonuses.ts`: `perHealth` 0.0015, `min` 0.06, `max` 0.2, fall 45 px/s, pickup 22 px); `GameView.bonuses` renderer (`game/view/bonuses/`, look in `config/bonus-look.ts`).
  - Look: a hexagon badge (radius 11 px) with an acid-yellow frame, a dark face and two cyan chevrons pointing up, swinging ±50° from side to side (a whole spin showed it edge on half the time) over a small pulsing yellow halo, in front of the ships and explosions; it glows with the playfield's neon. Picking one up flashes a cyan ring out. The HUD's weapon line shows the new level.
  - Test API: `weaponLevel`, `bonuses`, `bonusesDropped` in the game state.
- **Measured** (simulated play-through firing all the time and flying to the bonuses, seed 606): 8 / 13 / 12 / 16 / 23 bonuses dropped and picked up in 1-1 … 1-5, the first after 40–90 s; the weapon in use reaches level 5 in every level (after about 3 minutes in 1-1).
- **Alternatives considered:** one level shared by every weapon, or the switched-to weapon back at level 1 (asked; the reviewer chose per-weapon levels); bonuses marked in the wave scripts (asked; chance by toughness chosen); drifting the bonus sideways towards the ship (picking up stays a matter of flying over it).
- **Consequences:** levels start again at weapon level 1 (nothing carries over between levels yet). A bonus picked up at the last level is lost. Bombs and extra lives (GD-20, GD-32) are still to come.
- **Status:** Accepted

### D-050 — Player damage, lives and game over
- **Date:** 2026-10-24
- **Phase:** 6 (review)
- **Context:** The reviewer asked for player damage from bullet hits and ship collisions. Phase 6 had damage, lives and game over out of scope; asked, the reviewer chose the full GD-20/21/22 (health bar, 3 lives, small hitbox, 2 s blinking invincibility, game over), damage from every enemy shot and from ramming, and a "Game over" panel leading back to level select.
- **Decision:**
  - Core: `PlayerHull` (`core/systems/player-hull.ts`, pure: health, lives, invincibility) and `findPlayerHits` (`player-hits.ts`: enemy bullets, missiles, firing laser beams and enemies touching the hitbox, the most damaging first). Each step `LevelRun` lands at most one hit, the most damaging, when the ship is not invincible: the bullet goes, the missile blows up, the beam is marked (a beam hurts once), the rammed enemy takes `ramDamage` (killed by it, it counts as destroyed and can drop a bonus). A hit gives `invincibleSeconds` of invincibility; while invincible, shots and enemies go through the ship. At 0 health a life is lost and the ship comes back with full health, invincible, where it is; at 0 lives the phase is `over`: the ship is gone (no moves, shots or pickups), the waves stop, the enemies go on. `LevelResult.outcome` is `complete` or `over`. `LevelRunOptions.hull` is optional (no damage without it).
  - Content (`game/config/hull.ts`): 3 lives; 2 s invincible; hitbox radius 5 px (the ships' models are about 30 px across); bullet 10, missile 20, laser 25, collision 30; ramming takes 40 from the enemy (enemies with up to 40 health blow up: Gnat, Hornet, Scout, Strafer, Weaver, Splitter pods; tougher ones are hurt). Each ship's `maxHealth` (balanced 100, heavy 140, light 80) is its health bar.
  - App: the ship blinks 10 times a second while invincible; a hit makes a small spark where it landed, a lost life a blast on the ship; once the game is over the "Game over" overlay comes after 2 s (`GAME_PLAY_CONFIG.damage`). The overlay is the "Level complete" panel with the heading "Game over" in red; Confirm goes to level select on the level played (not the next one). The HUD shows the ship's health (red under 30 %) and the lives (`♥ N`, after the ship's name). Test API: `health`, `lives`, `invincible`.
- **Measured** (simulation, seed 606, balanced ship): standing still in the middle, the 3 lives last 82 / 85 / 78 / 62 / 58 s in 1-1 … 1-5 (mostly bullets); a bot that only weaves and fires (no dodging) finishes 1-1 to 1-3 with 2–3 lives and loses 1-4 and 1-5 at about 1:50 and 2:15. The e2e level tests stay well under the first lost life.
- **Alternatives considered:** damage only, or no death (asked; full model chosen); bullets and ramming only (asked); restarting the level or going to the title on game over (asked); several hits landing in one step (one hit, then invincibility, is GD-22's intent).
- **Consequences:** lives and health start again full in every level; no checkpoints (GD-42, mini bosses) and no extra lives from bonuses yet (GD-20). The difficulty for a kid in 1-1 is to be judged in the manual check.
- **Status:** Accepted

### D-051 — Filler groups in the lulls of the World 1 levels
- **Date:** 2026-10-24
- **Phase:** 6 (review)
- **Context:** The reviewer found the levels empty. Measured with a player always shooting (simulation, seed 606), no enemy was on screen 54 / 39 / 30 / 23 / 14 % of the time in 1-1 … 1-5, about one enemy on average in 1-1, and each of 1-1 to 1-4 had a 20–30 s lull around the middle.
- **Decision:** the written beats stay; `fill` (`world-1/waves.ts`) adds light groups in their lulls: after each beat, one group from the top every `maxGap` seconds while the next beat is more than one and a half gaps away, the kinds taken in turn and the entry positions alternating (0.3, 0.7, 0.5, 0.2, 0.8). `maxGap` goes down from its `start` at the first beat to its `end` at the last, so each level fills up as it goes (its second half keeps more enemy HP, P06-R08). Fillers per level (`WORLD_1_FILLERS`): 1-1 Hornets and Gnats only (they do not shoot), 4.5 → 3 s; 1-2 Hornet, Gnat, Weaver, Scout, 3.5 → 2.4 s; 1-3 the same, 3.3 → 2.2 s; 1-4 Gnat, Weaver, Hornet, Scout, Splitter, 3.2 → 2 s; 1-5 the same and Spinners, 3 → 1.6 s. The 50 % density (D-044) applies to them too.
- **Measured** (seed 606): with a player always shooting, no enemy on screen 30 / 23 / 14 / 13 / 6 % of the time, 1.6 / 2.1 / 2.6 / 3.0 / 3.8 on average (were 0.9 / 1.0 / 1.9 / 2.6 / 3.0); without shooting, 279 / 335 / 433 / 498 / 537 enemies, 4470 / 6300 / 9140 / 12610 / 16920 HP, peaks 16 / 20 / 24 / 30 / 32 on screen: still strictly going up, second halves above first halves. A bot weaving and firing without dodging keeps 2 lives in 1-1 and 1-2 (as before the fill in 1-1) and loses 1-3 to 1-5 (it lost 1-3 to 1-5 before too).
- **Alternatives considered:** a higher `WAVE_DENSITY` (more groups at the same moments: the lulls stay); writing the extra beats by hand (about a hundred beats; the filler is tunable with two numbers per level); fixed gaps (tried: 1-1, with the longest lulls, got more filler than 1-2 and its first half got heavier than its second).
- **Consequences:** about twice as many enemies; the counts and peaks are now far above the spec's tunables (~60 … ~140 enemies, peaks 6 … 15; see D-044), and the unit test's caps for 1-1 are raised to 300 enemies and a peak of 18. More enemy models at once: the 60 FPS check of 1-5 (manual) matters more.
- **Status:** Accepted

### D-052 — Dead-end removal and path starts without crossings
- **Date:** 2026-10-25
- **Phase:** 6 (review)
- **Context:** The unit tests found two defects of the no-crossings road layout (D-046). Removing the dead ends with T-junctions only could go round: a street went on to the next crossing, was cut back there because going on would make a crossing, which left the street behind it a dead end that went on again, and so on; it stopped at the 500-pass limit with dead ends on screen. And a path could start on the first on-screen point of a main road piece coming in from the side of the screen (as the main roads do around a district), run on top of it and cross it.
- **Decision:** with `tees`, a link cut back while removing dead ends is never built again (`Link.cut`), so the removal ends (each pass either builds a link that was never cut or cuts one for good). Without crossings, a path only starts where its main road runs more along the level than across it (`runsAlong`). Both apply only without crossings, so Level Zero (P04) lays out as before.
- **Alternatives considered:** a lower pass limit (leaves the dead ends); dropping every path that has not left its own road after a few points (more random draws change, and the start choice is the cause).
- **Consequences:** the World 1 street grids and paths change a little (other seeds' layouts); the street grids are laid faster (no more 500 passes).
- **Status:** Accepted

### D-053 — Bosses as enemies with shot-target proxies for their parts and core
- **Date:** 2026-10-25
- **Phase:** 7
- **Context:** P07-R01 needs several destroyable parts per boss, a core that takes no damage while shielding parts stand, and no damage while the boss comes in. The player's shots, homing missiles, beams and collisions all work on `ShotTarget`s through `damageTarget`, and the enemy world, the shots and the views already handle `Enemy`s.
- **Decision:** `Boss` (`core/entities/boss.ts`) extends `Enemy`; its parts (`BossPart`) and its core (`BossCore`) are separate `ShotTarget`s whose `health` setters drop damage while the boss is not in place (and, for the core, while a shielding part stands). `Enemy.hitTargets` (the enemy itself by default) is what the enemy world exposes to the shots and to collisions. The boss's own `health` only says it is still there: it goes to 0 when its death blasts are over, so the enemy world removes it as destroyed as for any enemy. Generic hooks were added to the engine: `Enemy.expires` (a boss is never culled), `rammable`, `dropChance`, `EnemyContext.explode` / `breakPart`, `LaserOwner` (lasers from a part).
- **Alternatives considered:** a separate boss world next to the enemy world (would duplicate shooting, targets, collisions and drawing); making each part an `Enemy` (stages, shield and death would need cross-enemy links).
- **Consequences:** shots at a shielded core spark and are used up (as P07-R01 says), so a shielding part right behind the core could never be hit: the boss designs keep shielding parts out of the core's shadow (unit test). `ShotWorld.totalDamage` counts damage dealt before a proxy drops it.
- **Status:** Accepted

### D-054 — Level progress and ground distance kept apart during fights
- **Date:** 2026-10-25
- **Phase:** 7
- **Context:** P07-R03 changes the ground speed for a fight (from stopped to ×1.5) and says no wave is skipped or squeezed by a fight; P07-R06 says no wave starts while a boss is fought. Waves are triggered by distance (P06-R07).
- **Decision:** `ScrollTrack` keeps two distances: `distance`, the ground flown over (the scenery), and `progress`, how far the level has got (waves, bosses, end, HUD progress, `time`). While a boss is fought the track is `held`: the ground goes on at `speed × speedFactor` (eased over 2 s with a smoothstep), the progress waits. After the fight the level goes on from where the boss came. Seeking keeps the ground's lead.
- **Alternatives considered:** waves paused but the distance going on (the waves due during the fight would all come at once afterwards); a time-based level (breaks the distance triggers of P06).
- **Consequences:** the scenery gets ahead of the level by about each fight's time × its speed factor (e.g. 1-1's coast comes a bit before its last 30 s of waves), and the final fight keeps scrolling past the level's end: `GameLevel.runout` draws that many extra seconds of the level's last section (`withRunout`: 150 / 80 / 30 / 70 / 75 s for 1-1 … 1-5); past it, the terrain still goes on, without props. The level's scroll time stays 240 s (P06-R04); fights add to the time played.
- **Status:** Accepted

### D-055 — Data-driven stage patterns and World 1 boss tuning
- **Date:** 2026-10-25
- **Phase:** 7
- **Context:** P07-R04 asks for a different pattern at every stage and lets the agent design the ten bosses' patterns; P07-R10 gives fight-time ranges for a player with guns at level 3 always on target.
- **Decision:** a stage's pattern is data (`BossPatternSpec`: volleys of generic shapes fired from a part or the core, `core/systems/boss-pattern.ts`). In each World 1 boss the parts' volleys are the same in every stage (each stops with its part) and the core fires something new at every stage, ending (all parts gone) with a ring or spiral not used before; so every order of destruction gives a new pattern at each stage (unit test over all orders). After each destroyed part the boss holds its fire 1 s and flashes. Health was tuned with a simulated player (`tests/helpers/boss-bot.ts`: flies under the next shielding part, then the others, then the core, leading the bullets): 1-1 … 1-5 mini 30 / 33 / 38 / 43 / 44 s, final 59 / 72 / 82 / 92 / 104 s, full health 2 200 → 3 910 (mini) and 5 770 → 15 780 (final). Two part positions of the spec's suggestions moved so they can be shot: the Scorpion's stinger and the Sentinel's drone bay hang in front of the core.
- **Alternatives considered:** a hand-written class per boss (ten classes for what is mostly data); patterns chosen by which part was destroyed (many more combinations to design).
- **Consequences:** bosses that launch enemies (Gull Mothership: Gnats; Sentinel: Hornets) count them as spawned; the parts' drop chances are 50 % (mini) and 60 % (final), the final bosses' cores 100 %.
- **Status:** Accepted

### D-056 — Continue from the mini boss checkpoint
- **Date:** 2026-10-25
- **Phase:** 7
- **Context:** P07-R08 (GD-42): after the mini boss, a game over offers Continue (selected first) or level select.
- **Decision:** `LevelRun` saves a `LevelCheckpoint` (progress, bosses passed, weapons and their levels from `RunArsenal`) when the mini boss is destroyed and puts it in a "Game over" result. `MenuFlow` shows the two choices (left / right / up / down or a tap pick, Confirm takes) and on Continue counts a new `attempt` with `resume` set; `GameSession` then starts the level again (a new `GamePlay`) from the checkpoint, with 3 full lives. The checkpoint is forgotten when the level is left (a new attempt from the level select has none).
- **Alternatives considered:** restoring the same `LevelRun` in place (the scene, HUD and effects would have to be reset by hand).
- **Consequences:** the scene is rebuilt on Continue (a short pause while the scenery is generated, as when a level starts).
- **Status:** Accepted

### D-057 — Shots leave from the barrels, as the camera sees them
- **Date:** 2026-10-25
- **Phase:** 7 (review)
- **Context:** the reviewer saw enemy bullets, lasers and missiles start away from the barrels of their guns. They started at a part's or an enemy's centre (or one radius ahead for lasers), and on the playfield plane, while the models' barrels stand up to ~20 px above it under a camera tilted 35°.
- **Decision:** a gun has muzzles: offsets from its enemy's centre as seen when it faces down the screen, plus a height (`core/entities/muzzle.ts`). They are game data (`BossDesign.guns` by piece and by what they fire; `ENEMY_CONFIG.*.muzzles`), copied from the barrel tips the models mark (`EnemyParts.muzzle`), and a unit test keeps the two equal. A shot leaves from the muzzle furthest along its way (side-by-side ones in turn, `GunMuzzles`), turned with the enemy's heading, a boss's roll and an orbiting part's spin, then projected along the camera's line of sight onto the playfield (`EnemyContext.seen`, from the `PlayfieldEye` the app takes from the scenery framing); aimed shots are aimed from that point. Lasers project their emitter the same way each step. The boss roll moved from the view into `Boss` (same rule, `BOSS_TIMING.roll`) so the simulation knows it.
- **Alternatives considered:** drawing bullets at their muzzle's height and letting them sink to the playfield (the shots would not be where they hit for their first frames, and lasers would need sloped beams); moving the models' barrels to the old spawn points (not where a gun is).
- **Consequences:** the simulation depends on the camera's geometry through `PlayfieldEye` (without one, e.g. in unit tests, shots start straight below their muzzles). Launches (hangars, drone bay) and the Refinery Titan's tank bursts still start at their part's centre.
- **Status:** Accepted

### D-058 — Boss turrets follow the player
- **Date:** 2026-10-25
- **Phase:** 7 (review)
- **Context:** the reviewer wants the bosses' turrets to turn and follow the player when they fire bullets aimed at the player. The turrets were drawn into their piece's merged meshes, barrels down the screen.
- **Decision:** a piece's guns may be on a turret (`Guns.turret`: its pivot, game data; `BossStats.turrets` → `BossTurret`, `BossPiece.turret` in core). Volleys from its `gun`s are flagged `turret`; their muzzles turn with its `aim` around the pivot (`BossPiece.place(muzzle, true)`). `BossPattern.turnTurrets`, called by `WorldBoss` at every step (fire pauses included), turns a turret towards the player at up to `BOSS_TIMING.turretTurnDeg` (150°/s) while the stage fires aimed shots or bursts from it, back to rest otherwise. In the view each turret is its own model on a pivot node under its piece (`BossDrawing.turrets`), turned by its `aim`; it flashes, hides and lights with its piece.
- **Alternatives considered:** turning the whole part model (the mounts, sponsons and ammunition racks would turn too); turning turrets in the view only (shots would no longer leave from the barrels).
- **Consequences:** shots aimed at the player still leave from the barrel tips and are aimed from there, so the game plays as before. Only turrets fire at the player turn: the guns fixed in hulls stay put.
- **Status:** Accepted

### D-059 — Player weapon balance
- **Date:** 2026-10-25
- **Phase:** 7 (review)
- **Context:** the reviewer asked to balance the player weapons' damage, specs and code. With every stream counted, the laser dealt 50 % of the guns' damage per second (40-150 against 80-400) and the missiles 40 % (32-160), with no clear reason to choose them.
- **Decision:** the guns stay the reference: they are the starting weapon and the bosses' health was tuned with guns at level 3 (D-055). New rule GD-33: at every level the laser and the missiles deal 70-100 % of the guns' damage per second, the laser more than the missiles. Laser 80 / 140 / 200 / 260 / 320 damage/s (100 % at L1, then 80-88 %: one column, instant, never misses, pierces at the level below); missiles 14 damage (56-280 damage/s, 70 %: they home on everything in range, but take time to arrive, overkill 10-health enemies and can chase a weak enemy instead of the boss). The guns' diagonals miss small or far targets, so on a single boss their real damage is closer to their forward streams; the laser becomes the best boss weapon at high levels, the guns the best against wide waves, the missiles the safest.
- **Alternatives considered:** raising the guns too (every boss and level would need re-tuning); equal raw damage for all three (the laser's focus and the missiles' homing would make the guns pointless).
- **Consequences:** fights with the laser or missiles get shorter than before; with the guns they are unchanged. Bonus drop chances depend on enemy health, not on the weapon, so they do not change.
- **Status:** Accepted

### D-060 — Every boss turret turns the way it fires
- **Date:** 2026-10-25
- **Phase:** 7 (review)
- **Context:** the reviewer saw the turrets not turning. With D-058 only turrets firing aimed shots turned, and only while their stage fired at the player: from the top of the screen at the ship below, that is a few degrees, and turrets firing fans or rings stayed at rest. The reviewer chose for every turret to turn.
- **Decision:** `BossPattern.turnTurrets` points each turret the way its next volley goes (the one with the least time left; a burst under way first): at the player for aimed shots and bursts (as before), along the fan's preset heading for fans, and with the ring for rings, spinning on from the last ring's turn to the next one's as it gets ready (the closest of the ring's equal turns, so it never spins back). The turn rate stays 150°/s. Three more guns are turrets (`Guns.turret` pivots and `BossDrawing.turrets`): the Reef Warden's prow cannon, the Mesa Fortress's fan cannon and the Refinery Titan's rotary turrets (base kept on the part so it still flashes on hits).
- **Alternatives considered:** turning turrets further than they aim (shots would no longer leave from the barrels, D-057); aiming at the player whatever they fire (fans and rings would leave from barrels pointing elsewhere).
- **Consequences:** fans in World 1 all fire straight down, so a turret between aimed shots and a fan swings back to rest before the fan; spiral turrets spin all through their stage. Guns built into hulls, blades, claws or pods, lasers (they fire straight down) and missile cells do not turn. Shots are unchanged: they still leave the barrel facing their way.
- **Status:** Accepted

### D-061 — Moving boss limbs: joints in the simulation
- **Date:** 2026-10-25
- **Phase:** 7 (review)
- **Context:** the reviewer wants bosses to have moving parts besides turrets, starting with the Scorpion's arms and claws.
- **Decision:** joints are engine data (`BossJointSpec`: pivot, parent joint, swing amplitude / period / phase; `BossJoints` in `core/entities/boss-joint.ts`), stepped by `Boss.update` all the time the boss is there. A part may hang on a joint (`BossPartSpec.joint`): `Boss` places its centre, and `BossPart.place` its muzzles, through the joint chain (turret first, then joints from the part's up to the body, then roll and the boss's position). Joints are checked at construction (no missing parent, no loop, no part both orbiting and on a joint). The view mirrors them: a node per joint at its pivot, nested as the joints are, turned by `Boss.joints.angle` (`boss-limbs.ts`); parts on a joint, their smoke and stumps hang on its node, and `BossDrawing.limbs` draws what else moves (the Scorpion's upper arms, forearms and jaws; a jaw belongs to its claw and goes with it). Swings are smooth sine waves, out of step between the two arms.
- **Alternatives considered:** animating the limbs in the view only (the claws' hit circles and barrels would stay where the model no longer is, against D-057); limbs that reach for the player (more behaviour to tune; a swing is enough for the look asked).
- **Consequences:** the claws' hit circles move up to about 8 px and their barrel tips up to about 15 px, and their shots with them; fight times were not re-tuned. Joints do not roll with the boss in the hit circles (as before for every part). A limb drawn on the body flashes with the core; the jaws flash with their claw.
- **Status:** Accepted

### D-062 — Shots go through a shielded boss core
- **Date:** 2026-10-25
- **Phase:** 7 (review)
- **Context:** the reviewer found that a shielded core stopped the player's bullets (they sparked on it, P07-R01), so the parts behind it could only be reached with the laser.
- **Decision:** `Enemy` gets `shotTargets` (what the player's shots can hit, `hitTargets` by default); `EnemyWorld.targets` is built from it. A `Boss` fighting with its core shielded leaves the core out of it: bullets, missiles (they no longer home on the core) and the laser go through to the parts. Coming in, and once the core can be damaged, the core is a shot target again. `hitTargets` keeps the core, so the ship still bumps into it. Mesa Fortress re-tuned for P07-R10: core 3000 (was 2420), silos 1500 (were 890); fight 83.0 s with the D-055 bot.
- **Alternatives considered:** letting only bullets through (missiles would still home on the core and be wasted); moving the parts out from behind the cores (changes the designs and models of several bosses).
- **Consequences:** P07-R01's "shots that hit the core make sparks" now holds only while the boss comes in (noted in the phase report's deviations). The D-055 fight times shift slightly for bosses with parts behind their core.
- **Status:** Accepted

### D-063 — Angry bosses: a bullet hell after each destroyed part
- **Date:** 2026-10-25
- **Phase:** 7 (review)
- **Context:** the reviewer wants every boss to get angry after the player destroys one of its parts and fire a bullet hell for a few seconds.
- **Decision:** engine: `BossStats.rageSeconds`; `Boss.rage` starts at it when a part is destroyed (with the stage's pause) and runs down once the pause is over, `Boss.updateRage` firing instead of `updatePattern` meanwhile; a new destroyed part starts it again, death stops it. Game: `BossDesign.rage` (a `BossPatternSpec` fired from the core, fresh after each part), 3 s for every boss (`BOSS_TIMING.rageSeconds`), four shapes built from a heat 0 (1-1 mini) to 4.5 (1-5 final) that sets the bullets a second (20 + 8 × heat) and their speed (120 + 8 × heat px/s, slower than the stages'); the Overlord shares its rate between two shapes. While angry the charge lights flicker at 14 Hz, and the turrets follow the angry pattern.
- **Alternatives considered:** angry instead of the pause (no warning before the hell); angry patterns from the parts left (some bosses have no armed part left, and it would differ with the order of destruction); a faster version of the stage's own pattern (not a bullet hell for bosses with few guns).
- **Consequences:** each boss now has 3 s of dense fire per part (2 to 4 times a fight), the hardest moments of the fights; whether 1-1's 20 bullets a second at 120 px/s is right for a kid is to be checked by hand (P07-R10 manual validation). Fight times with the simulated player do not change.
- **Status:** Accepted

### D-064 — Time of day, clouds and weather as an engine "atmosphere" along the level
- **Date:** 2026-10-25
- **Phase:** 8
- **Context:** P08-R04 asks for a documented look per level (time of day, cover of both cloud layers, haze, ground lights) that may change over a stretch of the level, blending every parameter and following the distance; P08-R05 for weather as data. The World 1 looks were fixed values in `SceneryLook`, applied once when the scene was built.
- **Decision:**
  - `core/scenery/atmosphere.ts` (pure): an `Atmosphere` is every number that changes (sun height / direction / colour / strength / shadow darkness, haze, sky gradient for reflections, ambient light, fog, each cloud layer's cover / opacity / colours, ground lights, weather `{ kind, strength }`, aurora). `blendAtmosphere` mixes two of them (colours and numbers linearly, the sun's azimuth the short way round, the weather's kind kept from the side that has some); `AtmosphereTrack` gives the atmosphere at a distance: a start look, then each change over `[from, to]` eased with a smoothstep (halfway is exactly half).
  - `core/scenery/sky-look.ts`: the game's data is a `SkyScript` (`SkyLook` = time of day, cloud cover, `storm`, weather, aurora; changes in seconds of scroll). `resolveSky` turns it into an atmosphere from the engine presets `config/time-of-day.ts` (six times of day; at night a dim, cold moon, and a moonlit reflection gradient so the ships keep their shapes and colours). A heavy low cover dims the sun, softens shadows, raises the ambient light, greys the haze and makes the layers see-through (`OVERCAST`), so the ground still shows from above. The weather brings the fog's end in to its kind's `fogAt1` (0.55 for snow, `blizzard_fog`) and its start half as much.
  - `render/scenery/sky-layers.ts` builds the lights, cloud layers, weather and aurora, and applies the atmosphere every frame (`applyAtmosphere`, cloud colours / cover, shadow darkness and ground lights in the kits, the reflection cube and environment intensity in `level-scene.ts`, rebuilt only when the gradient changes).
  - `SceneryLook.atmosphere` is optional: a look without it keeps its fixed values (`lookAtmosphere`), so Level Zero and World 1 look exactly as before. Debug: `weather=0` and `look=<time of day>` (`AtmosphereOptions`, through `GameDebugOptions` to the stage; a forced time of day on a fixed look uses its own cloud cover).
- **Alternatives considered:** blending whole `SceneryLook`s (their textures are built once; only the light changes over a level); time-based look changes (a debug jump would show the wrong look); a visible sky dome (the 35° camera never sees the sky: the "sky" only lights and reflects).
- **Consequences:** every frame sets a handful of light and material values (no allocation besides the sun's direction). Look changes follow the ground distance (D-054), so after a fight the look is a little ahead of the level's progress.
- **Status:** Accepted

### D-065 — Snow as GPU particles, behind the playfield; aurora as an additive sheet
- **Date:** 2026-10-25
- **Phase:** 8
- **Context:** P08-R05: snowflakes across the playfield at different depths, scrolling with the ground, up to a blizzard that streaks sideways, never hiding what flies, at 60 FPS; weather kinds as data. P08-R06: an aurora in the night haze of 2-5, without flashes.
- **Decision:** `config/weather.ts` lists kinds (count at strength 1: 1 500 for snow, fall and wind speeds, size, streak, sway, colour, opacity 0.5, the box of air they fill). `WeatherLayer` builds one mesh of quads per kind with a random `flake` attribute each; the shader places them in a box that follows the view along Z while each flake keeps its world Z (so they scroll with the ground), falls, sways and is blown along X by a wind growing with the strength, stretching the quads at strength 1, faded into the haze. Only the first `round(1 500 × strength)` quads are drawn (one sub-mesh), so nothing is uploaded per frame. They are drawn after the cloud layers in the group under the ships, without writing depth, so every ship, shot and bonus is drawn over them; the terrain's depth hides flakes behind hills. The aurora is a sheet just above the highest cloud layer, two slowly bending curtains (green, violet) with fine rays, added on top and strongest in the far haze, moving over tens of seconds.
- **Alternatives considered:** Babylon `ParticleSystem` (CPU emitters per frame, not tied to the ground); flakes over the ships too (they would hide shots, against P08-R05).
- **Consequences:** one draw call per weather kind and one for the aurora. Flakes between the camera and the clouds are drawn over the clouds, as falling snow is.
- **Status:** Accepted

### D-066 — Frozen ground: ice in the existing texture slots, lakes, crevasses, floating ice, a pipeline
- **Date:** 2026-10-25
- **Phase:** 8
- **Context:** P08-R07 asks for snow, snow-covered rock showing dark rock on slopes, glacier ice with crevasses cut with the heightmap tools, frozen lakes (flat shiny ice with cracks and a snowy edge), ice floes and icebergs drifting on the sea, and a pipeline running along 2-3.
- **Decision:** the terrain shader's layers are slots each look fills: World 2's `ground` and `high` are snow, `steep` dark rock (only cliffs, `steepSlope` 0.4–0.75), `low` (under `lowHeight` 6) cracked lake ice, the `sandy` cover glacier ice and `paved` trodden snow. Generated textures get `cracks` (cell edges of a tiling jittered grid). Height field: `TerrainSection.lakes` flattens round basins to their level (under `lowHeight`, so they show lake ice with a snowy shore) and `crevasses` cuts narrow, broken lines (`core/scenery/ice-sculpt.ts`); fjords are a flattened shelf with a channel below the sea along the same line. Props: `PropRules.floating` puts ice on the sea where it is deep enough under the whole footprint, with the chance of each section's `floatDensity`, at the sea level; `PropKindRule.drift` sways each floating kind slowly (the kind's mesh moves, `PropField.drift`); `PropRules.lines` lays one piece every `spacing` along a meander (the 2-3 pipeline), placed before the buildings so they keep clear (`core/scenery/float-placement.ts`). Snowy roads: light road colours with dark lane and centre lines as wheel tracks.
- **Alternatives considered:** a fourth ground cover in the vertex colours (all four channels are used: a new attribute and shader code); an animated per-instance drift (an upload every frame for hundreds of floes).
- **Consequences:** the floes of one kind drift together; World 2's roads reuse World 1's rules (D-046). Level Zero and World 1 are unchanged (the new rules are opt-in).
- **Status:** Accepted

### D-067 — World 2 waves composed from plans; balance measured as in World 1
- **Date:** 2026-10-25
- **Phase:** 8
- **Context:** P08-R08/R09: five 5-minute scripts with given lead kinds, strictly harder from 2-1 to 2-5 per minute of scroll, 2-1 ≥ 1-3 and 2-5 > 1-5.
- **Decision:** each level is a `WavePlan` (`game/config/world-2/waves.ts`): a cycle of phrases (kind, groups, interval, side, position, spread), a beat every `gap` seconds shrinking over the level, groups growing by 60 % over it; then the World 1 density, filler and quiet stretches (`assembleLevel`, shared with World 1). Measured without shooting (seed 606): 116.8 / 120.4 / 121.4 / 172 / 233 enemies per minute, 2 466 / 3 384 / 3 666 / 6 016 / 7 360 HP per minute, peaks 22 / 23 / 36 / 37 / 51 (World 1 now: 1-3 104.8 / 2 235, 1-5 130.3 / 4 150); every second half heavier. Factors 0.9 / 0.95 / 1 / 1.1 / 1.15.
- **Alternatives considered:** about 200 hand-written beats (World 1's way; the plans are tuned with a few numbers).
- **Consequences:** like World 1 (D-051), the peaks are far above the tunable `peak_on_screen` (10 … 17); their order is kept. Carriers' Gnats make 2-3's peak jump.
- **Status:** Accepted

### D-068 — Boss engine additions for World 2, and World 2 boss tuning
- **Date:** 2026-10-25
- **Phase:** 8
- **Context:** P08-R10's bosses need a radar mast that makes the other weapons aim while it stands (Fjord Lynx), sweeping lasers (Aurora Station, Glacier Colossus, Boreal Citadel) and slow bullets that burst into rings (Aurora Station's cryo cannons). P08-R11 gives fight times.
- **Decision:** generic engine data: `BossVolley.needs` / `after` (fires only while a part stands / once it is destroyed; `patternSignature` and turret aiming take them into account), `EnemyLaserSpec.sweepDeg` (the warning line on one side, the beam sweeping to the other while it fires), `EnemyBulletSpec.burst` (after `after` s the bullet becomes a ring of `count` bullets; the level's bullet speed factor applies to both). The ten models and designs were made in parallel by sub-agents following the phase 7 conventions (muzzles drawn from the designs' constants, frost and snow details) and registered after World 1's. Health tuned with the D-055 bot (guns level 3): mini 32.8 / 40.3 / 41.1 / 45.4 / 51.3 s, final 66.7 / 86.7 / 97.0 / 108.0 / 113.6 s; full health 2 720 / 2 880 / 3 550 / 3 800 / 4 200 (mini) and 6 500 / 7 000 / 8 600 / 13 000 / 17 500 (final), each above the World 1 boss of its level and rank. Angry patterns (D-063) go on from World 1: heat 2.5 → 7.
- **Alternatives considered:** a hand-written boss class for the Lynx (its rule is data: two conditions on volleys).
- **Consequences:** the Harbour Kraken's final fight is over 2-2's inland end (the harbour is at its start: 2-2 has to end where 2-3 begins).
- **Status:** Accepted

### D-069 — Enemy bullets as blended blobs of energy
- **Date:** 2026-10-25
- **Phase:** 8 (revised after review)
- **Context:** enemy bullets were glow discs added onto what is behind them; over bright snow they washed out to white, against P08-R04/R05 (shots as easy to see as in World 1). A first fix put a dark disc under each bullet; the reviewer asked for it to go and for colourful blobs of energy with fading borders instead, no bigger than before.
- **Decision:** each bullet is a disc of the same size: a white-hot core going over to its colour, which it keeps to its edge while its vertex opacity fades out (`ENEMY_LOOK.bullets.fade`), drawn with alpha blending (`blendedTemplate`) rather than additively, so its colour is kept over bright ground. An additive white-hot core (a child of the template, so every clone has one) pulses in size with the bullet's age (2.5 Hz, ±30 %): a change of size of a small glow, not a flash of the screen.
- **Alternatives considered:** a dark backing disc under each bullet (first version; the reviewer did not want the dark ring); a different bullet style per world (every renderer and style would double).
- **Consequences:** the new look shows in every level, World 1 included.
- **Status:** Accepted

### D-070 — The bosses page grouped by world
- **Date:** 2026-10-25
- **Phase:** 8
- **Context:** P08-R12: the `bosses/` page lists the World 2 bosses after World 1's, grouped by world, each over the scenery and look of its level.
- **Decision:** `EnemyViewerPanel` takes optional `groups` (headings before a kind index); the bosses page derives them from the level each boss is fought in. The level's scene (and its look, weather included) is already the one the boss belongs to (P07-R09).
- **Consequences:** none on the `enemies/` page.
- **Status:** Accepted

### D-071 — Weapon levels kept from one completed level to the next
- **Date:** 2026-10-25
- **Phase:** 8 (review)
- **Context:** the reviewer asked for the weapon levels to persist once a level is finished; until now every level started with every weapon at level 1 (phase 6 known limitation).
- **Decision:** on "Level complete", `GameSession` saves the run's `RunArsenal.snapshot()` (weapon in use and each weapon's level) as JSON under `<game id>_weapons` in the app's key-value storage (cookies); each level then starts from it (`LevelRunOptions.startWeapons`, restored before a checkpoint's weapons). An unreadable value reads as none. A game over saves nothing.
- **Alternatives considered:** keeping them in memory only (lost on reload); saving them at every bonus (a level lost would still raise the weapons).
- **Consequences:** there is no way yet to start again from level 1 weapons but clearing the cookies; a "new game" reset can come with scoring / save slots.
- **Status:** Accepted

### D-072 — Laser colours by boss, and beams locked once firing
- **Date:** 2026-10-25
- **Phase:** 8 (review)
- **Context:** every enemy laser was red; the reviewer asked for more colours, and for a laser that may follow the player while it aims to keep its direction once locked.
- **Decision:** a boss's lasers take its kind id as style (`withOwnLasers`, applied when the boss kinds are built), and the view colours a style with that boss's neon (`laserPalette`: a white-hot beam core, the colour around it, fading out), red for the Lancer and unknown styles. In the engine (`EnemyShots`), a laser's warning line follows its owner's heading; when it starts firing it keeps the heading its owner had then (`locked`), its sweep turning from it, and it still leaves from the emitter.
- **Alternatives considered:** a colour argument on every boss laser volley (20 boss files to keep in step with their neon).
- **Consequences:** lasers fired along a swinging joint (the Scorpion's stinger) no longer swing while they fire.
- **Status:** Accepted

### D-073 — Lasers on turrets instead of sweeping lasers
- **Date:** 2026-10-25
- **Phase:** 8 (review)
- **Context:** the reviewer saw the Boreal Citadel's laser turn while it fired (its sweep, D-068) and asked that no boss laser turn once it fires, lasers going on rotating turrets where needed.
- **Decision:** `EnemyLaserSpec.sweepDeg` is removed. A piece's lasers can be on its turret (`Guns.turretLaser`, `BossVolley.turret`): `BossPattern.turnTurrets` aims that turret at the player until the beam fires and holds it still while it fires, and the laser follows the turret's heading (piece heading + turret aim) until it locks (D-072). The Aurora Station's emitters, the Glacier Colossus's cutters and the Boreal Citadel's cannons are on turrets (their models draw the turning part as the turret, on a mount); the Harbour Kraken's and the Citadel's core lasers fire straight down.
- **Alternatives considered:** keeping sweeps but locked (no sweep at all then); turrets for core lasers too (the cores' lenses are built into their hulls).
- **Consequences:** those lasers now threaten where the player is rather than sweeping an area; fight times were not measured again. After review, a laser turret follows the player at only 20°/s during the warning line (`laserTurnRateDeg`), so the beam can be outrun.
- **Status:** Accepted

### D-074 — Enemy bullets as balls of plasma, drawn as thin instances
- **Date:** 2026-10-25
- **Phase:** 8 (review)
- **Context:** the enemy bullet (a flat blob with a pulsing core) was to feel like a ball of energy or plasma. More layers per bullet would have cost a draw call each per bullet as cloned meshes (already two each), against the ENG-106 budget in dense boss patterns.
- **Decision:** each bullet is, back to front, a faint flickering aura, a deep-coloured body (blended, so it shows over snow), two curled swirls of brighter plasma (`buildSwirl`: lobed rings turned more the further out) spinning opposite ways, and a pulsing core. Each layer of each colour is one mesh of thin instances (a matrix per bullet, as the blasts, D-034), so all bullets cost at most 5 × 6 draw calls however many fly. Their colours are worked out in `ENEMY_LOOK.bullets.styles`; spins, sizes and flicker in `ENEMY_LOOK.bullets`.
- **Alternatives considered:** a noise shader on a quad (truer plasma, but a custom material outside the vertex-colour look of the other shots, and not checkable under `NullEngine`); keeping cloned meshes (up to 5 draw calls per bullet).
- **Consequences:** bullet layers are drawn under the other transparent meshes (`alphaIndex`), as one block per layer; a bullet no longer has a node of its own.
- **Status:** Accepted

### D-075 — e2e tests drive the level clock, and e2e builds draw fewer pixels
- **Date:** 2026-10-25
- **Phase:** 8 (validation)
- **Context:** e2e tests failed on CI and locally under load: a level's clock gains at most `maxFrameSeconds` (0.1 s) a frame, and under software WebGL a level frame can take seconds, so "wait 4 s of level time" took over a minute on a CI runner (about 0.04× real time). Entering a level also blocks the page for more than the 5 s `expectState` polled, and clicks (Playwright waits for a stable element over animation frames) crawled on the `enemies/` page.
- **Decision:** `__GAME_TEST__.advance(seconds)` (e2e builds only, ENG-52) runs the level being played at once, one fixed step a frame, without rendering (`GamePlay.advance`); the e2e helper `waitForLevelTime` loads the level, then advances it instead of waiting for frames. `expectState` gives the `game` screen the loading timeout. e2e builds render at half resolution across and without multisampling (`ENGINE_CONFIG.e2e`): tests read the game's state, not its pixels.
- **Alternatives considered:** longer timeouts (slower tests, and still at the mercy of the runner's speed); fewer e2e workers (slower overall); GPU rendering on CI (not available on the hosted runners).
- **Consequences:** the World specs and the menu, gamepad and `enemies/` specs pass at 6× CPU throttling in Chromium. Production builds are unchanged. A level advanced through the test API still runs every step of the game's logic, with the keys held at the time.
- **Status:** Accepted

### D-076 — Rain as a weather kind: streaks along their fall, a greyer haze, rings on the water
- **Date:** 2026-10-26
- **Phase:** 9
- **Context:** P09-R05 asks for thin, light streaks falling fast at a slight slant at different depths, scrolling with the ground, a haze closer and greyer with the strength, faint rings on the water, never hiding what flies, at 60 FPS; weather kinds are data (P08-R05).
- **Decision:** `rain` is a new entry of `config/weather.ts` (2 000 streaks at strength 1, falling at 380–520 units/s, a wind of 30–70 for the slant, 0.35–0.55 wide, 16× as long, opacity 0.32), with three optional fields any kind may use: `align: 'fall'` (the shader stretches each particle along its velocity, as thin as its size across the view, at every strength; snow keeps `wind`: sideways in a blizzard), `haze` (the haze turns `share × strength` of the way to a grey) and `rings`. Rings are a plane at the water level following the view (`RainRings`, one draw call) whose shader draws, in each 9-unit cell, a ring spreading from a random point and fading over 0.8 s, fewer cells ringing in light rain; it does not write depth, so the terrain above the water hides it: rings show on the sea, rivers, swamps, lakes and pools only. It is drawn right after the water, under the ships.
- **Alternatives considered:** splash particles on the ground (thousands more quads, and drops landing on hills read as noise from 320 up); rings in the sea's PBR material (a material plugin for one effect).
- **Consequences:** two draw calls for rain (streaks, rings). Rain and its rings are only a look: nothing in the simulation reads them (unit test).
- **Status:** Accepted

### D-077 — Lightning: strikes drawn from the level's seed, a capped flash, a bolt in the clouds
- **Date:** 2026-10-26
- **Phase:** 9
- **Context:** P09-R05: flashes at random times from the level's seed, the same twice, at most 3 in any 1 s and on average one every few seconds (`lightning_gap` 4–10 s), each about 0.15 s, the ambient light and sky at most ×1.8 the storm's, sometimes a bolt in the clouds; weather never changes the simulation.
- **Decision:** `core/scenery/lightning.ts` (pure): `LightningSchedule(seed)` draws strikes one after another, 4–10 s apart; a strike is one flash or, with a chance of 0.35, two flashes 0.25 s apart (a flicker), so at most 2 flashes fall in any second. A flash rises in 0.03 s and fades out by 0.15 s (`LIGHTNING`, `config/weather.ts`). `flashed(atmosphere, flash)` multiplies the ambient intensity, the haze (clear colour and fog, each channel capped at 1) and the environment intensity by up to `1 + 0.8 × flash × lightning`, no haze channel past 0.85 (`maxHaze`, added at validation). A look's `lightning` (0..1) blends like any number, so 3-3's storm builds its lightning with its clouds. `LightningLayer` asks the schedule at the scene's clock (seconds since the level's scene started), applies the flash through `SkyLayers` and, for 60 % of the strikes, draws a jagged bolt with two forks (`boltLines`, seeded by the strike) flat in the lowest cloud layer, added on top while the strike's flashes last. `weather=0` removes the lightning with the rain.
- **Alternatives considered:** flashes driven by the simulation's random numbers (weather would become an input of the simulation, against P08-R05); a white overlay over the screen (would wash out the shots and bonuses); strikes timed by the ground distance (no lightning while the ground stops for a fight).
- **Consequences:** flashes follow the scene's clock, so after a pause or a frame-time hitch they come at the same seconds of scene time, not of level progress. The flash never touches the ships' emissive neon or the shots, which stay as bright as before (P09-R04 readability).
- **Status:** Accepted

### D-078 — Mist and an ambient tint as look parameters
- **Date:** 2026-10-26
- **Phase:** 9
- **Context:** P09-R04: 3-1's morning mist, close and white over the water, lifting over the first half (`morning_mist`: fog end at 40 % of the clear distance, back to 100 %); 3-2's green-tinted ambient under the canopy. `SkyLook` had no way to say either.
- **Decision:** `SkyLook.mist { fog, white }` brings the fog's end to `fog` of its distance (its start half as much, like weather) and turns the haze `white` of the way to a pale mist colour; `SkyLook.tint` multiplies the ambient sky and ground colours. Both resolve into the atmosphere, so a look change blends them away (3-1: a change from the misty morning to the plain morning over 0–150 s).
- **Alternatives considered:** a fog distance per section of terrain (the look follows the distance already; no second mechanism).
- **Consequences:** none for the earlier levels (both optional, default no mist, no tint).
- **Status:** Accepted

### D-079 — One water level for the sea, rivers, swamps and lakes; set pieces and lines over water
- **Date:** 2026-10-26
- **Phase:** 9
- **Context:** P09-R03/R06: a delta, rivers flowing down the screen, a swamp, a lake held by a giant dam, waterfalls where the river drops over cliffs, pipelines across the swamp; 3-2 to 3-5 have "no sea section (rivers, lakes and swamps are not sea)". The engine has one water plane per level, at `sea.level`.
- **Decision:** every World 3 level has a water level (0); rivers are channels cut below it, swamps relief around it, the lake a wide channel, the pools of 3-5 lakes flattened below it. A **sea section** is a section with a coast (`shore`) or whose relief lies under the water level (`relief.base < 0`): only 3-1's open sea and delta mouth (80 of 300 s; 23 % of its ground under the sea). The water flows by drifting its waves down the screen (`sea.drift [0, 16]`). Two generic placement tools: `PropLine.overWater` (pieces stand on the ground or at the water level: the swamp pipelines), and `PropRules.landmarks` (a set piece of a kind at a given place, on a path its width across it, on the ground or the water, placed before everything else, which keeps clear of its footprint box: every placement checks the set pieces and lines, as they are larger than the placer's neighbour buckets): the waterfalls (a rock ledge across the river with a falling white sheet and spray, four in 3-3), the great pyramid the Stone Idol stops over, the dam across 3-4's lake and its power plant. The stone causeway of 3-3 is a line along the temples' paved band.
- **Alternatives considered:** a second water plane per river at its own height (the terrain shader paints water by depth under one level; waterfalls between two real water levels would need both); carving the cliff into the river bed for the waterfalls (the channel floor is flat per section; the drop would cut the river dry).
- **Consequences:** the water is one colour per level (3-4's is darker, swamp water). The upper and lower rivers of a waterfall are at the same level: the drop is in the set piece.
- **Status:** Accepted

### D-080 — World 3 waves and balance, measured as in Worlds 1 and 2
- **Date:** 2026-10-26
- **Phase:** 9
- **Context:** P09-R07/R08: five 5-minute scripts with given lead kinds, strictly harder from 3-1 to 3-5 per minute of scroll and in peak on screen, 3-1 ≥ 2-3 and 3-5 > 2-5 on the same measures.
- **Decision:** `WavePlan`s as World 2's (D-067), groups growing by 70 % over each level, gaps 4.9 → 3.5 s (3-1) down to 4 → 2.7 s (3-5); 3-2 leads with swarms of 6 Hornets and Lancers, 3-3 with Spinners and Rocketeers, 3-4 with two Carriers per cycle, 3-5 with Bulwarks around a Carrier. Measured without shooting (seed 606): 178.8 / 194.4 / 215.0 / 262.6 / 308.4 enemies a minute, 4 214 / 5 694 / 6 884 / 8 068 / 10 506 HP a minute, peaks 38 / 41 / 47 / 55 / 58 (2-3: 121.4, 3 666, 36; 2-5: 233.4, 7 360, 51). Factors 1 / 1.05 / 1.1 / 1.2 / 1.25.
- **Consequences:** as in Worlds 1 and 2, the peaks are far above the tunable `peak_on_screen` (13 … 19), in its order.
- **Status:** Accepted

### D-081 — The ten World 3 bosses, and their tuning
- **Date:** 2026-10-26
- **Phase:** 9
- **Context:** P09-R09/R10: ten bosses with moving jaws, legs, a swaying serpent body and buzzing wings, full health strictly up from 3-1 to 3-5, above World 2's bosses of the same rank, fight times within the tunables.
- **Decision:** no engine change: every boss is data on the phase 7/8 boss engine (joints for the Croc's jaws, the Leviathan's five-joint spine, the Spider's hips and knees, the Mosquito's wings; laser turrets; launches; homing missiles; tanks that burst into rings; slow bullets that burst). The designs and models were made in parallel by sub-agents, one level each, against the same conventions, each given a full-health band between World 2's and the next World 3 level's, so the orderings hold by construction; health was tuned with the D-055 bot (guns level 3). Full health mini / final: 3 200 / 6 800, 3 780 / 9 050, 4 200 / 9 950, 4 500 / 14 000, 5 100 / 19 500; fights 41.6 / 87.5, 44.4 / 90.6, 47.3 / 102.4, 51.4 / 115.2, 54.7 / 127.1 s. Some parts were placed for the bot's spread to reach them (the Spider's forelegs raised forward, the Stone Idol's eyes ±32 apart, the Verdant Crown's root generators 64 apart), and some hit circles enlarged (Leviathan, Jaguar). Angry patterns go on from World 2: heat 4.5 (3-1 mini) to 9 (3-5 final). Neon colours in `BOSS_LOOK.neon`.
- **Alternatives considered:** a new engine hook to keep the Croc's jaws in step with its jaw cannon's bursts after a stage change (they are in step in its first stage only).
- **Consequences:** the Croc's jaws and its bursts drift apart after the first destroyed part; the Leviathan's ring turrets fire from their axis (their emitters do not move when they turn).
- **Status:** Accepted

### D-082 — Two weathers at once, falling ash and rising embers
- **Date:** 2026-10-26
- **Phase:** 10
- **Context:** P10-R04/R06: 4-4 has falling ash and embers together; embers are small glowing sparks rising past the camera, flickering as they cool, never mistaken for bullets. A look had one weather.
- **Decision:** `SkyLook.secondWeather` (and `Atmosphere.secondWeather`, optional, blended from or to none) falls at the same time as `weather`; both bring the fog in and tint the haze. `WeatherLayer` draws one mesh per kind present, `weather=0` clears both. Two kinds in `config/weather.ts`: `ash` (1 500 grey flakes falling at 12–26 units/s, swaying, the haze closer and brown-grey with the strength) and `embers` (800 orange sparks 0.45–0.85 across, a negative fall so they rise, added on, flickering by 0.65 at 4.5 Hz, fading out over the top 45 % of their box). New optional kind fields: `blend: 'add'`, `flicker`, `fadeHigh`.
- **Alternatives considered:** a list of weathers on every look (every World 2–3 look, fixture and test to change); embers as a GPU particle system (another system to drive and pool).
- **Consequences:** embers are at most 0.85 units across against bullets of radius 4 (drawn 6.4) and have no rim; they move up only. Two draw calls in 4-4.
- **Status:** Accepted

### D-083 — Clouds lit from below, and tinted clouds
- **Date:** 2026-10-26
- **Phase:** 10
- **Context:** P10-R04: ash-tinted pink and brown-grey clouds; clouds and smoke "lit orange from below", a red-lit eruption sky; 4-3's lava glow taking over as the sunset fades.
- **Decision:** `SkyLook.cloudTint` multiplies the clouds' colours; `SkyLook.underglow { color, strength }` turns the clouds’ edges 75 %, their body 20 %, the haze 35 % and the ambient ground light 60 % of the way to its colour at strength 1 (`UNDERGLOW`). 4-3's look changes from dusk (underglow 0.25) to night (0.8) over 60–280 s: the sun sets while the lava light grows; 4-5's eruption raises it to 1 with the embers by the final boss.
- **Alternatives considered:** a time-of-day preset per World 4 level (presets are shared by all worlds).
- **Consequences:** none for earlier looks (both optional).
- **Status:** Accepted

### D-084 — Lava as the level's liquid: a self-lit shader, a hot edge, a glow occluded by the terrain
- **Date:** 2026-10-26
- **Phase:** 10
- **Context:** P10-R05: lava rivers, pools, slag rivers and a magma lake; self-lit, flowing and churning, a bright hot edge on the rock, glowing with the existing glow tools, no real lights, only a look, 60 FPS.
- **Decision:** a level's liquid stays one plane at `sea.level` (D-079); a look's `sea.lava` (`LavaLook`) draws it with a shader (`lava-material.visual.ts`): Worley plates whose centres wander (churn), a warp drifting them, cracks opening and closing between them, glowing and white-hot at their heart, flowing by `sea.drift`, fogged but never quite hidden. The terrain plugin, in lava mode, skips the beach and surf, scorches the rock near the lava and adds an emissive edge (`edge.width` above it) and glowing cracks (up to `edge.cracks` above) before the fog. The ground glow layer draws the lava with its own material; the terrain chunks are added to it too (black), as the plane runs under every hill. In 4-3 … 4-5 the "sea sections" stay none (no shore, relief above the level): lava fills channels and lakes cut below it, as World 3's rivers.
- **Alternatives considered:** a uniform glow colour for the lava in the glow layer (no bloom on the cracks); glowing without occlusion (the plane would glow through the hills); a separate lava plane per river (one liquid level is enough).
- **Consequences:** the terrain is drawn once more, at the glow map's resolution, in the lava levels only. One drift per level (4-5's lake flows slower than 4-3's rivers).
- **Status:** Accepted

### D-085 — Smoke and steam plumes from props; wagons moving on a line
- **Date:** 2026-10-26
- **Phase:** 10
- **Context:** P10-R08: vents and cinder cones send up slow, soft, see-through smoke; steam over the hot coast; moving ore wagons on rail lines.
- **Decision:** a prop model may list `plumes` (a point and a kind, `smoke` or `steam` in `config/plumes.ts`). `PropField` builds one mesh per prop kind and plume kind: `puffs` camera-facing quads per column, drawn with the prop's own thin instances, lifted, grown, bent and faded on the GPU (each placed prop out of step), lit by the atmosphere, blended without writing depth, under the clouds. `PropLine.drift` moves a line's pieces to and fro together, as floating props drift: ore wagons are a second line on the rail's path.
- **Alternatives considered:** particle systems per vent (a system per emitter); wagons as road traffic (rails are not roads).
- **Consequences:** a plume mesh per smoking kind (a few draw calls); wagons all move together.
- **Status:** Accepted

### D-086 — A shot style per level: contrast outlines in World 4
- **Date:** 2026-10-26
- **Phase:** 10
- **Context:** P10-R07: over lava and red skies, enemy and boss bullets and laser warning lines need a light core or contrasting outline in World 4, other worlds unchanged.
- **Decision:** `SceneryLook.shotStyle` (engine, a name) is passed to the game's enemy shot renderer (`EnemyBindings.shots(scene, style)`). The game's `contrast` style (`ENEMY_LOOK.contrast`) adds, per bullet colour, a dark blended rim 1.3 × the bullet behind its body and a white spark at its heart (thin instances, two more draw calls per colour), and gives laser warning lines a white core, 1.5 × as wide. Every World 4 look names it.
- **Alternatives considered:** contrast everywhere (would change the validated worlds; spec default).
- **Consequences:** the shot style follows the scenery look, so the `bosses/` page shows World 4 bosses with it too.
- **Status:** Accepted

### D-087 — World 4 waves and balance, measured as in Worlds 1 to 3
- **Date:** 2026-10-26
- **Phase:** 10
- **Context:** P10-R09/R10: every kind from 4-1, leads per level, strictly harder from 4-1 to 4-5, 4-1 ≥ 3-3 and 4-5 > 3-5.
- **Decision:** `WavePlan`s as World 3's (D-080), every kind in every cycle, the lead kinds twice or three times per cycle; gaps and growth chosen by sweeping them with the D-038 play-through (the measure is not monotonic in the gap: cycles line up differently). Measured without shooting (seed 606): 220.8 / 246.0 / 247.2 / 298.6 / 388.8 enemies a minute, 7 004 / 8 178 / 9 472 / 9 668 / 12 544 HP a minute, peaks 53 / 54 / 57 / 64 / 66 (3-3: 215.0, 6 884, 47; 3-5: 308.4, 10 506, 58). Factors 1.1 / 1.15 / 1.2 / 1.3 / 1.35.
- **Consequences:** as in Worlds 1–3, the peaks are far above the tunable `peak_on_screen` (15 … 21), in its order; 4-5 is a big step up from 4-4.
- **Status:** Accepted

### D-088 — The ten World 4 bosses, and their tuning
- **Date:** 2026-10-26
- **Phase:** 10
- **Context:** P10-R11/R12: ten bosses with moving claws, drills, fists and wings, full health strictly up from 4-1 to 4-5, above World 3's bosses of the same rank, fight times within the tunables.
- **Decision:** no engine change: every boss is data on the boss engine (joints, turrets, orbiting parts, launches, homing missiles, tanks bursting into rings, slow bullets that burst), made in parallel by five sub-agents, one level each, each given a full-health band between World 3's and the next World 4 level's, so the orderings hold by construction; health tuned with the D-055 bot. Full health mini / final: 3 650 / 7 800, 4 180 / 9 700, 4 500 / 12 400, 5 150 / 14 800, 5 550 / 21 200; fights 44.4 / 89.2, 48.0 / 100.7, 53.2 / 112.4, 56.3 / 126.2, 59.7 / 137.6 s. Angry heats evened out afterwards to go on from World 3's 9: minis 9.5 → 13.5, finals 10 → 14. Some parts placed for the bot's spread (as D-081).
- **Consequences:** the Crab's mortar and the Dreadnought's rack are seldom destroyed in the bot's fights (they sit behind the core); a player can still shoot them.
- **Status:** Accepted

### D-089 — World 5 dropped: a 4 × 5 level grid
- **Date:** 2026-10-26
- **Phase:** 10
- **Context:** The reviewer asked to remove World 5 from the specs and the code.
- **Decision:** `LEVELS_CONFIG.worlds` goes from 5 to 4: the level select shows 20 levels, `1-1` … `4-5`, all unlocked. The engine keeps locked levels (`buildLevelGrid`, the padlock and the "locked" feedback) for any other game's data; they are unit tested with sample grids, and no e2e test can reach a locked level any more. The requirement texts that named World 5 (vision, P01-R07, P06-R01, P10-R01, phase 8 and 10 notes) were changed at the reviewer's request, each with a dated note.
- **Consequences:** after 4-5 the level select keeps 4-5 highlighted because it is the last level (`MenuFlow` already did this for a last level). The Caldera Throne is the game's last boss.
- **Status:** Accepted

### D-090 — Ten veteran and elite enemy kinds, with moving parts
- **Date:** 2026-10-26
- **Phase:** 10 (requirements added to phase 5: P05-R13 to P05-R24)
- **Context:** The reviewer asked for 10 new, harder enemy kinds, some with moving parts like the bosses, in the spec, and in the harder worlds.
- **Decision:**
  - The requirements went into the phase 5 spec (the reviewer's choice), each with a dated note.
  - The kinds come in two tiers: five **veterans** (Wasp, Mortar, Mantis, Phantom, Minelayer), from World 3; five **elites** (Hydra, Orbiter, Scissor, Juggernaut, Hive), in World 4 only.
  - Engine: `JointedEnemy` / `EnemyPart` reuse the bosses' `BossJoints` (D-061). Parts give no points and never drop a bonus. A shielding part makes shots pass through the hull, as a boss's shielded core does. `swinging` holds the joints still, and `EnemyLaserSpec.sweeps` lets a beam turn with its owner (the Scissor). The phase 8 rule "a beam keeps its heading" stays the default.
  - Built in parallel by two sub-agents, one per tier.
  - Waves:
    - World 3 brings in a veteran kind at each level (Wasp, Mortar, Minelayer, Mantis, Phantom).
    - World 4 uses every veteran kind in every level. The elites come in two in 4-1 (Hydra, Orbiter), then Scissor, Hive and Juggernaut.
    - Gaps and growth were re-swept with the D-038 play-through. 4-2 gets two more Splitter / Spinner phrases to keep its lead kinds frequent.
- **Measured** (without shooting, seed 606; enemies / HP per minute / peak):
  - 3-1 180.8 / 4 384 / 37; 3-2 184.0 / 5 494 / 38; 3-3 190.0 / 6 452 / 45; 3-4 219.0 / 7 744 / 50; 3-5 247.8 / 8 952 / 53.
  - 4-1 195.2 / 7 496 / 53; 4-2 204.4 / 9 216 / 55; 4-3 211.2 / 10 644 / 57; 4-4 225.0 / 11 238 / 62; 4-5 302.0 / 13 752 / 64.
  - Every ordering of P09-R08 and P10-R10 holds, and every second half is heavier.
- **Consequences:**
  - World 3 (validated in phase 9) changes: its waves, and its enemies per minute in 3-3 to 3-5, which went down from 215 / 263 / 308 because the heavier kinds take beat slots. Its HP per minute stays about the same.
  - The HP measure counts hulls only, not parts.
  - GD-50 (tougher enemies score more) is tested on the first eleven kinds only: the Phantom (90 HP, 450 points) scores more than its HP suggests, as its cloak makes it harder.
  - The models were only smoke-checked in software rendering; they need a look in `enemies/`.
- **Status:** Accepted

### D-091 — Phase 11 spec defaults (score, lives, bombs)
- **Date:** 2026-10-26
- **Phase:** 11 (spec drafted by the agent at the reviewer's request)
- **Context:** The reviewer asked the agent to fill the Phase 11 spec. GD-20, GD-32, GD-50 and GD-51 leave the bomb key, bomb supply, bomb effect, extra-life source and score rules open, and GD §2's E key is taken by the weapon switch (D-043).
- **Decision:**
  - The score is per level attempt (levels are played one by one, P06-R01). Every enemy destroyed by the player scores its kind's points; a boss part scores 10 % of its boss's points, a boss core its boss's points. The checkpoint keeps the score, and Continue restores it.
  - The high score is saved to the existing cookie whenever an attempt ends (complete, game over or leaving with Esc), so leaving never loses it.
  - Bombs: 3 at the start, topped back up to 3 after a lost life, 5 at most. One press fires one bomb for 1 s: 100 damage to every on-screen enemy and boss part (not a shielded core), clears the enemy bullets, missiles and lasers, and makes the player invincible. Keys `KeyR` and `ShiftLeft`, gamepad X and LB, and a touch `BOMB` button.
  - Extra lives: a rare life bonus (1 %) and an always-dropping life bonus from each mini boss core; bomb bonuses at 3 %. At most one bonus per enemy, so the weapon bonus rate (D-049) barely changes. At the maximum, a pick-up scores points instead.
- **Alternatives considered:** a score carried across levels (levels are not chained); extra lives from score thresholds (GD-20 asks for dropped bonuses); a bomb that also kills bosses outright (it would trivialise the fights); the E key (D-043).
- **Consequences:** GD §2's "Special / bomb: E" row is superseded by D-043 and P11-R06. The reviewer may change any default before setting the spec to `Ready`.
- **Status:** Accepted (reviewer approved the spec, 2026-10-26)

### D-092 — Phase 11 implementation choices
- **Date:** 2026-10-26
- **Phase:** 11
- **Context:** The Phase 11 spec (D-091) leaves some technical points open: where the bomb button lives, how the life and bomb draws affect the weapon bonuses, what "on screen" means for the shots a bomb clears, and when the high score is checked.
- **Decision:**
  - Bonus kinds: `BonusWorld` always makes the weapon draw on the main bonus source (`seed + 1`), and draws life and bomb from a source of their own (`seed + 2`, `LevelRun`). The weapon bonuses' draws stay exactly as before Phase 11. A life or bomb bonus replaces the weapon bonus of the same enemy (at most one bonus).
  - Bombs: the damage lands once, on every shot target on screen when the bomb goes off (the same list the player's shots aim at, so a shielded core is left out). Every enemy shot is cleared on every step while the bomb lasts, not only at the start, and the player cannot be hit meanwhile. The ship does not blink: it is not the GD-22 invincibility.
  - Score: `EnemyWorld.score` holds the attempt's score (enemy points, boss part points from `BossStats.partPoints`, bonus points at the most). After a Continue it starts from `LevelCheckpoint.score`.
  - High score: `MenuController.recordScore` saves it whenever an attempt ends. That covers `completeLevel` (complete or game over, before Continue is offered, which also sets `LevelResult.newHighScore` for the panel) and `GameSession.end` (Esc, Continue, leaving).
  - Touch bomb button: part of the HUD, which updates every frame (it shows the bombs left), not of the game screen overlay, which redraws only on menu changes. It is the only HUD element that takes taps. Presses made before a level starts are cleared, so a bomb key pressed on a menu does not carry into the level.
  - Test API: the game state also gives `score`, `bombs`, `enemyShots` and `bonusKinds`, the top level gives `highScore`, and `sendAction('bomb')` presses the bomb.
- **Measured** (P11-R07, simulated play-through of World 1, seed 606: firing all the time, flying to the weapon bonuses only, no damage; weapon bonuses dropped with the D-049 rules vs. with P11's, then life / bomb bonuses dropped):
  - 1-1: 24 vs 24 (0 %), 2 / 8
  - 1-2: 29 vs 29 (0 %), 5 / 10
  - 1-3: 34 vs 34 (0 %), 5 / 10
  - 1-4: 43 vs 41 (−5 %), 7 / 11
  - 1-5: 50 vs 47 (−6 %), 9 / 12
  - The life counts include each mini boss's. The simulator is not D-049's (that one was not kept), so the absolute counts differ from its 8 to 23; the comparison is between the same simulator with and without the new rules.
- **Alternatives considered:**
  - Drawing every kind from one source: the shifted draws moved the weapon bonus counts by up to 32 %.
  - Clearing the shots only when the bomb goes off: shots fired during the bomb would hit right after it.
  - The bomb button in the game screen overlay: it could not show the bombs left without redrawing the overlay every frame.
- **Consequences:**
  - A player shooting most enemies gets more life and bomb bonuses than the spec's estimate of about one extra life per level. The levels have more kills than that estimate assumed, and the lives and bombs then often sit at their most, scoring points instead. The chances are tunables (`game/config/bonuses.ts`).
- **Status:** Accepted

### D-093 — e2e builds have no render loop: the tests step the game
- **Date:** 2026-10-26
- **Phase:** — (test infrastructure, after phase 11)
- **Context:** The e2e suite took 7.5 min locally (95 tests, 4 workers) and its tests still waited on real time: boss stages, death blasts, the "Level complete" overlay, the bomb, the game over and the menu fades ran at the speed of the software-rendered frames, and the viewer pages were checked by waiting for frames, the FPS or the damage counter to change. The render loop also kept every page drawing at full speed, so heavy specs ran one at a time (`mode: 'default'`) to avoid starving each other, with timeouts of up to 20 min.
- **Decision:** In e2e builds (`__E2E__`), the game and the `level_zero/`, `player_shots/`, `enemies/` and `bosses/` pages start no render loop: nothing moves until a test steps them (ENG-52, `step(frames)`). `RunningApp.step(frames, render = true)` runs the whole app (menus, fades, the result delay, the level being played) by whole 1/60 s frames, then renders once; `__GAME_TEST__` exposes `step(frames, render?)` and `advance(seconds)` on top of it (`GamePlay.advance` is gone). The viewer pages get `step(frames)` that renders once at the end (`__SCENERY_TEST__` and `__SHOTS_TEST__` are new; `make build` checks they are absent from production). The e2e helpers (`tests/e2e/menu-helpers.ts`) step instead of waiting: `stepUntil` steps a few frames between checks, `waitIdle` / `sendAction` / `expectState` step through fades without drawing and render once, `destroyBoss` breaks the parts left and steps on to the result overlay. The serial modes and long timeouts are gone; the 40-boss and 21-kind viewer tests are split into groups that run in parallel.
- **Alternatives considered:** keeping the render loop and stepping on top of it (the loop still burns the CPU, and game time still passes between checks, so results depend on the machine); a render loop with a frame time of 0 (same CPU cost, nothing gained over no loop); rendering after every stepped frame (several times slower under software WebGL).
- **Consequences:** `make e2e` takes 3.6 min locally (101 tests), with no test waiting on game time; what is left is loading, level generation and the frames the tests draw. Tests are deterministic (the same frames in the same order on any machine). The canvas only changes when a test steps, so failure screenshots and videos show the last stepped frame. The FPS shown by the debug tiles in e2e builds is frames per simulated second (60). `player_ship/` keeps its render loop (no game time; its test only waits for a few frames).
- **Status:** Accepted

### D-094 — Faster git hooks: tool caches, incremental type check, no import rules TypeScript covers
- **Date:** 2026-10-26
- **Phase:** — (tooling, after phase 11)
- **Context:** The hooks were slow (ENG-65 asks for under 15 s). Measured locally: `pre-commit` took about 11 s on 27 staged files (type-aware ESLint 5.8 s, `tsc` 5 s); `pre-push` (`make check-fast`) took about 65 s (ESLint on the whole repository 38 s, Prettier 7 s, `tsc` 5 s, unit tests 13 s). A third of the ESLint time went to `import-x` rules that check what TypeScript already checks.
- **Decision:**
  - `make typecheck` runs `tsc --incremental` with its build info in `node_modules/.cache/tsc/` (sound: TypeScript re-checks whatever a change can affect).
  - Prettier runs with `--cache` everywhere (its output depends only on the file, the config and its version).
  - ESLint uses a content cache in `node_modules/.cache/eslint/` in `lint-staged` and `make check-fast` only; `make lint` and `make check` (the full gate, CI) lint every file.
  - `import-x/no-unresolved`, `namespace`, `default` and `no-named-as-default-member` are off: `make typecheck` reports unresolved modules and missing default, named and namespace exports, and runs in every hook and gate (typescript-eslint's performance guide recommends this). The layering rules (`import-x/no-restricted-paths`), `no-default-export`, `export` and `no-duplicates` stay.
- **Alternatives considered:** dropping type-aware ESLint rules from the hooks (they catch real bugs; the gate would find them late); unit tests on changed files only at push (`vitest --changed`; misses tests affected through imports it does not see); Vitest `isolate: false` (about 3 s less, but test files would share module state).
- **Consequences:** measured locally, `pre-commit` takes about 8 s on the same 27 files (Prettier 1 s, ESLint 4.7 s, `tsc` 2.2 s) and a few seconds on a small commit; `make check-fast` takes about 18.5 s when the caches are warm, 12 s of which are the unit tests, and about 44 s cold. With the ESLint cache, a file is not re-linted at push when only a file it imports changed, so a type-aware lint error can wait for `make check` / CI. `make clean` removes `node_modules/.cache`.
- **Status:** Accepted

### D-095 — Phase 12 spec defaults (pause, music, settings)
- **Date:** 2026-10-26
- **Phase:** 12 (spec drafted by the agent at the reviewer's request)
- **Context:** The reviewer asked the agent to fill the Phase 12 spec with software-generated music and sound, pause / resume / main menu, and music and sound volume settings. GD §2 binds Pause to `Esc / P`, but P01-R09, P06-R02 and D-041 made `Esc` leave the level; GD-70 / GD-71 leave the music and sound design open; ENG-07 and ENG-120 assume `localStorage` and audio files.
- **Decision:**
  - In the game screen, `Escape`, `KeyP`, gamepad Start and Select, and a touch `❚❚` button pause; `Backspace` and gamepad B do nothing there. Leaving a level goes through the pause menu (Resume, Settings, Main menu with a `Leave the level?` No / Yes question). `Escape` stays Back in the menus.
  - The level pauses itself when the page is hidden or the gamepad in use is disconnected, and never resumes by itself.
  - A Settings screen, from the title and the pause menu, has two 0–10 sliders (Music 6, Sound effects 8 by default), saved in cookies (D-010). No master volume, remapping or graphics settings.
  - All audio is generated with the Web Audio API: music and SFX buses into a limiter, a lookahead sequencer, unlock on the first input. One deterministic track per level in a per-world style, one boss track per world, a menu theme, and three jingles. A fixed list of sound effects, at most 16 voices with priorities.
- **Alternatives considered:** keeping `Esc` = leave and pausing with `P` only (contradicts GD §2, and a single key that quits a level is easy to hit by accident); a pause countdown (slower to resume, not asked); per-level hand-written music data (20 songs by hand, against GD-70's "code generated").
- **Consequences:** P06-R02 and D-041's "Esc leaves" wording is superseded in the game screen. ENG-54's pause/resume smoke step and ENG-110's hidden-tab pause are covered. The rest of ENG-112 stays unscheduled. Quality presets (ENG-102) were removed from `01-engineering.md` by the reviewer (2026-10-26).
- **Status:** Accepted

### D-096 — Pause as menu screens; Escape is its own action
- **Date:** 2026-10-26
- **Phase:** 12
- **Context:** P12-R01..R04 add a pause menu and a settings screen, and make Escape pause in a level while it stays Back in the menus; Backspace and gamepad B must do nothing in a level. The level must not advance at all while paused, and the fixed-step clock must not catch up.
- **Decision:**
  - `pause` and `settings` are `MenuScreen`s of the pure `MenuFlow` (`pause ⇄ game`, `pause → settings → pause`, `pause → title`, `title ⇄ settings`; `game → title` is gone). `MenuState.paused` is true on the pause menu and on the settings opened from it. The pause menu and the settings sliders are small pure helpers (`app/pause-menu.ts`, `app/settings-menu.ts`).
  - New menu actions: `cancel` (the Escape key: Back in the menus, pause in a level), `pause` (P, gamepad Start / Select, the `❚❚` button; resumes from the pause menu) and `resume` (test API); a `{ set, value }` command for slider taps. `back` does nothing in a level, nor on the "Level complete" / "Game over" panels.
  - Freezing: while paused, `start-app`'s frame ticker does not call `GamePlay.frame` (it still renders the last frame), so the level's own clock gets no time at all. The controls are cleared on pause and resume; debug keys are ignored while paused.
  - Auto pause: `visibilitychange` to hidden and `GameControls.takeDisconnect()` (the slot of the gamepad last used to play is empty) call `MenuController.pause()`.
  - The `❚❚` button sits at the top right under the weapon readout (the corner itself holds the readout, and moving the readout left would cover the score).
- **Alternatives considered:** pausing inside `GamePlay` with a flag (the level would still be asked to step, and the pause menu would live outside the menu flow); mapping Escape to `pause` and treating `pause` as Back in the menus (gamepad Start and P would then go back on menu screens); keyboard bindings that depend on the screen (input would need to know the flow).
- **Consequences:** P01-R09, P06-R02 and D-041's "Esc / B leave the level" no longer hold in a level. e2e tests leave levels with a `leaveLevel` helper (pause, Main menu, Yes).
- **Status:** Accepted

### D-097 — A small Web Audio engine instead of Babylon's audio; cues from the core state
- **Date:** 2026-10-26
- **Phase:** 12
- **Context:** All music and sounds are generated (GD-70, GD-71, P12-R05); audio must react to the core without changing it (ENG-11); limits on voices, priorities and retriggers (P12-R10); everything must be unit-testable without real audio.
- **Decision:**
  - `src/audio/` uses the Web Audio API directly: oscillators and looped noise through biquad filters and gain envelopes (`synth.ts`), a pure lookahead `Sequencer` (100 ms ahead, every frame and on a 25 ms timer), a `MusicPlayer` (one track per gain node: cross-fades, fades, jingles, pause at position), a pure `VoicePool` (16 voices; a new sound replaces the oldest one of lower or equal priority; the same sound within 30 ms is not replayed but makes the playing one ×1.25 louder) and an `SfxPlayer` (stereo panning by x, at most ±0.6). Babylon's audio engine is built around audio files and spatial sound, which this game does not use.
  - `AudioOutput` creates the context lazily, only during a user gesture that browsers accept as activation (`navigator.userActivation.isActive`), so there is never an autoplay warning: music and SFX buses (volume `(step / 10)²` × the game's mix) into a `DynamicsCompressor` used as a limiter (−1 dBFS, ratio 20). Without Web Audio, or if it throws, it stays silent. The page hidden suspends the context.
  - `LevelCues` reads a `LevelRun` after each step (`GamePlayOptions.onStep`) and turns state differences into engine cues (`fire:<weapon>`, `beam-start:<weapon>`, `enemy-bullet`, `laser-warning`, `hit`, `hit-blocked`, `blast-large`, `bonus:<kind>`, ...), one per kind and step. A game maps cues to `SoundDesign`s (`GameView.audio: AudioBindings`). For `hit-blocked`, `ShotImpact.blocked` was added and `damageTarget` now returns the damage really taken (0 on a shielded core).
  - `app/game-audio.ts` decides the music from the menu state and the run (boss bar → boss track; mini boss destroyed → level track from its start; final boss → its track until the end; level ended → fade and jingle) and keeps the e2e state (track id, last sound names, context state). The SFX limits count in app time, so e2e runs are deterministic.
- **Alternatives considered:** Babylon `AudioEngineV2` (file-oriented, heavier to fake in tests); an `AudioWorklet` synth (more code, no need at this note density); a core event bus for sounds (a bigger change to `core/`, when the state already says everything).
- **Consequences:** No runtime dependency and no audio file (`make build` now fails if one gets into `dist/`). ENG-120's audio formats do not apply.
- **Status:** Accepted

### D-098 — Generated music: per-world styles and a seeded composer
- **Date:** 2026-10-26
- **Phase:** 12
- **Context:** P12-R06..R08: one track per level from its data, a style per world, deterministic, at least 60 s before it loops; a faster boss track per world; a calm menu theme; jingles.
- **Decision:** `src/game/view/audio/`: a `MusicStyle` per world (tempo range from the tunables, scales, chord progressions, instruments, drum and bass feels, arpeggio rate, registers): World 1 major / mixolydian, saw bass in eighths, four-on-the-floor, square lead; World 2 dorian / minor, soft bass, half-time claps, glassy arpeggios and bells; World 3 dorian / minor, plucked bass, shakers and toms, marimba and flute; World 4 phrygian / harmonic minor, heavy detuned saws, slow heavy kicks and low toms, brass. `composeTrack` seeds the level's RNG from an FNV-1a hash of its track id: key, tempo, scale, bass rhythm, arpeggio shape, three themes (progression + a two-bar motif walked on the scale), the order and energy of 8-bar sections, enough sections for 60 s. A boss track is the world style at its top tempo + 20–30 BPM, in a darker scale, full energy, busier bass and drums. Tracks are composed once and kept. The mix (music 0.5, SFX 0.8) keeps the loudest sound effect peak (gain × sum of layer gains) within +6 dB of the loudest instrument peak; gun shots and the laser hum are quieter than hits and explosions (unit tested on the data).
- **Alternatives considered:** hand-written songs (20 by hand, against "code generated"); a Markov melody model (less control over phrasing for little gain).
- **Consequences:** The style tables are the knobs for the review by ear.
- **Status:** Accepted

### D-099 — Synthwave music: echo and reverb sends, 80s drum machine, a full menu track
- **Date:** 2026-10-26
- **Phase:** 12 (review)
- **Context:** The reviewer asked for music on the main menus and for all the music to be synthwave. The menu theme (D-098) was a quiet 84 BPM pad-and-bell piece (−25.8 dB RMS at the default volume); the tracks had no echo or reverb, a marimba and a flute in World 3, plain snares.
- **Decision:**
  - Engine: `TrackMixer` (one per playing track) gives each instrument an input with sends to a tempo-synced echo (`echoBeats` 0.75, feedback 0.35) and a shared reverb (a `ConvolverNode` on the music bus, with a generated decaying-noise impulse of 2.2 s); both fade with the track. `Instrument.echo` / `reverb` set the sends; `AudioBindings.effects` turns them on.
  - Game: synthwave instruments (gated snare, Simmons-style toms at several pitches for descending fills, supersaw lead, detuned saw pads, plucked saw / square and FM-bell arpeggios with echoes); off-beat open hats; World 1 outrun, World 2 dreamwave, World 3 synthwave on toms and shakers, World 4 darksynth with rolling sixteenth basses. The menu theme: 88 BPM, E minor, i–VI–III–VII, a backbeat, pumping octave bass, every section full (`MusicStyle.energies`).
  - Mix: music bus 0.8 (was 0.5), SFX 1 (was 0.8): the music sits around −17 to −20 dB RMS at the default volume; the loudest sound stays within +6 dB of the music.
- **Alternatives considered:** echoes written as extra notes (twice the notes, no feedback tail); a per-instrument reverb (one convolver per instrument costs more for little gain); keeping the menu theme calm and sparse (the reviewer did not notice it).
- **Consequences:** Loudness and style were checked with an offline render in Chromium (`OfflineAudioContext`), not by ear: the reviewer's listening is the final check.
- **Status:** Accepted

### D-100 — Stressful boss tracks and more energetic synthwave
- **Date:** 2026-10-26
- **Phase:** 12 (review)
- **Context:** The reviewer asked for more stressful boss music and for all the music to be more energetic synthwave. Boss tracks (D-098, D-099) were the level style faster, with one extra kick; levels had bare breakdowns, half-time dreamwave in World 2 and eighth-note arpeggios in Worlds 2 and 4.
- **Decision:**
  - Boss tracks have their own drums, bass and chord stabs (`compose-boss.ts`): pushed kicks, sixteenth hats, rising snare rolls, a root/octave sixteenth bass, 3-3-2 supersaw stabs, tense progressions (`BOSS_PROGRESSIONS`) in harmonic minor or phrygian. They stay in their world's instruments, so a boss still sounds like its world.
  - Every track has a noise riser into each section. Levels: tempos raised by 8–14 BPM (tunable amended), sixteenth arpeggios, no breakdown at energy 0; World 2 moves from half time to a driving backbeat. The menu theme goes to 100 BPM, still slower than every level.
- **Alternatives considered:** dissonant alarm-like leads (tritones, sirens), judged unpleasant for a child (P12-R09's spirit); boss-specific instruments per world (more data for little gain over the stabs and drums).
- **Consequences:** Boss tracks are 2–3 dB louder than the level tracks (denser), within the master limiter; checked offline, not by ear.
- **Status:** Accepted

### D-101 — Darksynth everywhere, a minigun gun
- **Date:** 2026-10-26
- **Phase:** 12 (review)
- **Context:** The reviewer asked for more darksynth music and for the player's bullets to sound like a minigun ("BRRRT"). Worlds 1–3 and the menu used bright or modal scales and lighter instruments; the gun was one zap per volley (8 a second).
- **Decision:**
  - Every style plays minor, harmonic minor or phrygian keys with the heavy kick and dark pads; the growling `bass-heavy` (a resonant square layer added) in Worlds 1 and 4 and the menu. Worlds stay apart by drum feel, lead, arpeggio and tempo.
  - The gun sound is a burst of 6 short rounds, 21 ms apart, made of delayed layers in one sound design: one burst per volley fills the 125 ms to the next, so the rattle is continuous while firing, with no engine change (no new looping cue) and one voice per volley.
- **Alternatives considered:** a looping "firing" cue like the laser hum (needs a new engine cue and a stop on release; the bursts already stop within one volley); raising the gun's fire rate (gameplay change, out of scope).
- **Consequences:** The data test's peak counts only layers that start together. If the gun's `shotsPerSecond` changes, the burst (`MINIGUN` in `sound-designs.ts`) must follow; a unit test checks it covers one volley.
- **Status:** Accepted

### D-102 — Alternating shot streams, one fire cue per volley
- **Date:** 2026-10-26
- **Phase:** 12 (review; requirement added to phase 3 as P03-R11)
- **Context:** The reviewer asked that multi-stream bullet and missile levels fire their streams in turn instead of all at once, without changing the global firing rate.
- **Decision:** `ShotWorld` keeps one cooldown and a next-stream index: a shot every 1 / (shotsPerSecond × streams) s, streams in their listed order (the weapon data already lists them centre first, then left / right pairs from the inside out). Selecting a weapon or releasing fire restarts from the first stream, at once. `ShotWorld.volleys` counts volleys (each time the first stream fires); `LevelCues` emits `fire:<weapon>` per volley instead of per new projectile, at the ship's x.
- **Alternatives considered:** random stream order (less readable, not deterministic per seed without an RNG); a sound per shot (the minigun bursts would pile up into a buzz, and a 5-stream level would take 5 voices).
- **Consequences:** The order of the streams in `player-weapons.ts` is now the firing order.
- **Status:** Accepted

### D-103 — Darksynth look for the menus and the HUD, no cyberpunk
- **Date:** 2026-10-26
- **Phase:** 12 (review; look requirements in phase 1, P01-R05 and P01-R13)
- **Context:** The reviewer asked to rework the main menu and the game UI, drop the cyberpunk reference and make it darksynth, matching the music (D-099..D-101). D-013 and D-014 had made the overlay cyberpunk (acid yellow / cyan / red, glitch split, corner brackets, terminal hints) over a night city.
- **Decision:**
  - Overlay (`index.html` only, same markup): tokens `--hot` (magenta), `--violet`, `--red`, black-violet glass, `--sunset` and `--chrome` gradients. The logo is chrome italic letters (background-clipped gradient with a horizon line) in a slow magenta / red glow, over a striped sunset sun drawn in CSS (`.title-sun`, a masked gradient disc; removed at the reviewer's request, D-104). Neon glows replace the red / cyan glitch split; a thin neon frame and a sunset line replace the corner brackets and the status tag; hints lose the terminal prompt and cursor (a slow pulse). Selected entries are a magenta gradient block with black text, markers unchanged (they still show without colour).
  - Backdrop: the night city stays, recoloured: crimson sunset sky, near-black skyline, magenta / red / violet windows and neon, magenta lane lines, dimmer near windows.
- **Alternatives considered:** a 3D striped sun behind the skyline (tried: the fogged towers of the street hide all but a sliver of it, so it read as an odd shape); replacing the city by the classic sun and neon grid (more synthwave than darksynth, and the reviewer asked to rework the look, not the scene).
- **Consequences:** D-013 and D-014 are superseded for the look. All the game's pages share these styles (the debug viewers too).
- **Status:** Accepted

### D-104 — A pilot instead of the ship in the menu backdrop (reverted)
- **Date:** 2026-10-26
- **Phase:** 12 (review; P01-R05)
- **Context:** The reviewer asked to remove the sun from the main menu and to replace the ship by a model of a fighter pilot with tons of wires linking the helmet to the seat, then refined it over four rounds (a close-up, anime-styled; cel-shaded; mirrored and more realistic; after a 90s anime reference image).
- **Decision:** the pilot was generated in code (pure part data, then Babylon meshes with a cel-shading shader and ink outlines). The reviewer then asked to revert to the player ship and to delete all the pilot code: the backdrop shows the balanced ship again (`title_ship_rotation_speed`), and the pilot model, its meshes, its curve helpers, the toon material and their tests are deleted. Only the sun emblem's removal stays.
- **Alternatives considered:** keeping the pilot code unused for later (the reviewer asked for it to be deleted).
- **Consequences:** none left in the code; this entry records the experiment.
- **Status:** Reverted

### D-105 — The boss health bar moves to the left edge
- **Date:** 2026-10-26
- **Phase:** 12 (review; P07-R02)
- **Context:** The reviewer found that the boss's name and health bar, a panel at the top of the playfield, hid the boss, which fights in the upper part of the screen.
- **Decision:** a slim vertical gauge up the left edge, under the player's health panel (top 96 px, 300 px tall, 8 px wide, no panel): it fills from the bottom, the part notches are ticks across it, the kind and name are written along it bottom to top. The left edge is clear of the score, the pause button and, on touch screens, the fire and bomb buttons (bottom right).
- **Alternatives considered:** a slimmer, see-through bar at the top (still over the boss); the bottom of the screen (over the player's ship); the top HUD row in place of the progress bar (too narrow between the health panel and the pause button for the name).
- **Consequences:** P07-R02 amended at the reviewer's request.
- **Status:** Accepted

### D-106 — Bullets leave from inside the ship, under it
- **Date:** 2026-10-26
- **Phase:** 12 (review; P03-R01)
- **Context:** The reviewer asked for the bullets to start further into the ship, as if shot from under it. They started 3 px below the nose tip (the muzzle, phase 3 review), drawn level with the ship.
- **Decision:** an optional `launchBack` on projectile weapons (engine): shots start that far behind their launch point. The bullet sets 13 px (16 px below the nose tip, inside the hull); its tracers are drawn 8 units under the playfield plane (`SHOT_LOOK.bullet.depth`), so the ship is drawn over them as they leave, as the missiles already are (depth 20).
- **Alternatives considered:** a deeper muzzle for every weapon (`muzzleInset`): the laser and its base glow would start inside the hull too.
- **Consequences:** none for the hits: a bullet starts 13 px lower and reaches enemies 13 px later (22 ms at 600 px/s).
- **Status:** Accepted

### D-107 — Enemy explosions as short, muffled booms
- **Date:** 2026-10-26
- **Phase:** 12 (review; P12-R09)
- **Context:** The reviewer found the enemy explosion sound annoying: each was a long low-pass hiss from 3 200 Hz with a sustain, so a busy wave turned into a wash of bright noise.
- **Decision:** a `boom` recipe for the enemy explosions: a deep falling sine thump, a low noise body closing fast (900 → 110 Hz small, 1 200 → 110 Hz large), a 30 ms band-passed crackle for definition; no sustain, 0.22 s small and 0.5 s large. Boss part, boss and life-lost blasts keep the longer `blast`, so the big moments still stand out.
- **Alternatives considered:** fewer explosion sounds per second (a per-sound minimum interval in the engine): kept for later if a busy wave still feels crowded.
- **Consequences:** none on the priorities or the mix rules (P12-R10 data tests unchanged).
- **Status:** Accepted

### D-108 — Realistic, layered explosions
- **Date:** 2026-10-26
- **Phase:** 12 (review; P12-R09)
- **Context:** After D-107 (short muffled booms for the enemies), the reviewer asked for more realistic explosion sounds.
- **Decision:** one `explosion` recipe (`sound-recipes.ts`) for every blast, in three sizes (small, large, huge): a 12 ms high-passed noise crack, a low-passed noise body closing from a few kHz to 180 Hz over the blast, a sub-bass sine thump gliding down by half, a low-passed rumble tail for the large and huge sizes, and 3–8 short band-passed debris crackles at fixed, uneven delays (so a sound is the same every time). The boss dies in a chain of three. The old `blast` and `boom` recipes are gone. Bomb, boss and life-lost gains are lowered so the loudest sound stays within +6 dB of the music (P12-R10).
- **Alternatives considered:** recorded samples (GD-71: sound is generated); random debris per play (the engine plays fixed designs; fixed uneven spacing sounds natural enough).
- **Consequences:** supersedes D-107's booms. A busy wave peaks at −5.8 dBFS at the default volume in the offline render.
- **Status:** Accepted

### D-109 — World 1 as one gradient: sea, green grass, desert
- **Date:** 2026-10-26
- **Phase:** 6 (review after validation, at the reviewer's request; P06-R05, R06, R10)
- **Context:** The reviewer asked for World 1 to start on the sea, then green grass, then desert, with more and more props along the way, the five levels cut from that one gradient; 1-1 at midday and the other levels at other times of day.
- **Decision:** one ground for the whole world (`looks.ts`): dry earth by default, covered by section with grass (`lush`), sand or pavement, so the land fades from green to sand through the `surface` shares the sections already blend; red rock and sand below only in 1-4 and 1-5. Cut: 1-1 open sea, green coast; 1-2 green coast, meadows, groves, farmland; 1-3 green country, the grass yellowing at the end (new `scenery-country.ts`); 1-4 dry lands to the desert; 1-5 desert city. Each level starts on the very section the previous one ended on (shared constants). Two new building groups (`villages`, `farms`) and three new props (farmhouse, greenhouse, grain silos; World 2's wind turbine reused by id, as World 2's props import World 1's roads). The bare desert stretches (rock, dunes, mesas: almost no prop fits on them) are kept short, and an oasis town and a desert town with streets keep 1-4 fuller than 1-3. Time of day fixed per level, the sun lower each level: 72° midday, 55°, 35°, 14° sunset, 8° dusk with the city lights brighter (darksynth sky: magenta haze, violet zenith).
- **Alternatives considered:** a time of day moving within each level (World 2's sky scripts): not asked, and the levels can be played in any order; one look per section instead of per level (the engine has one look per level).
- **Consequences:** level names change (1-2 Green coast, 1-3 Green country, 1-4 Dry lands). The bosses and wave scripts are unchanged; some boss names (e.g. 1-3's Dust devil, Mesa fortress) now fly over greener land than they were named for.
- **Amended (2026-10-27, reviewer):** 1-5 ends on the desert too, as "Deep desert" (dunes, oasis villages, a rocky pass, desert towns, a great oasis town on the sand); 1-4 ends on desert outskirts, its mesas without mines. No industrial zone and no city in World 1: they are for other worlds. A great oasis town with dense streets keeps 1-5 the fullest level.
- **Status:** Accepted

### D-110 — World 2 reworked: from the desert to the factories
- **Date:** 2026-10-27
- **Phase:** 8 (review after validation, at the reviewer's request; P08-R03, R06, R07 amended)
- **Context:** The reviewer asked for World 2 to start in the desert and end in factories, with slow transitions along the levels, and a different time of day for each level, "3 days, 1 night", as in World 1.
- **Decision:** World 2 becomes the Industrial Desert, one gradient cut into five levels (`world-2/scenery.ts`, replacing `scenery-coast.ts` and `scenery-inland.ts`): 2-1 Sand sea (oasis edge, great dunes, sand sea, rocky desert, outposts, the first mines in the last 30 s), 2-2 Mining mesas (mines on mesas and in a canyon, a mining town, open pits, the first oil wells), 2-3 Oil fields (pumpjacks, a company town, refineries, tank farms, the first factories), 2-4 Industrial belt (workers' suburbs, warehouses, a power plant, factory yards, the factory district), 2-5 Factory district (foundries, rail yards, heavy industry, great works filling every block). Slow transitions three ways: the sections blend over 900 units (about 15 s; World 1: 420), the ground cover steps from sand to the `paved` cover a little in each section (sand share 0.89 → 0.67 → 0.39 → 0.17 → 0.05 of each level, paved 0.005 → 0.14 → 0.40 → 0.67 → 0.89), and each building group first comes in mixed with the one before it (outposts + mines, mines + oil, oil + refinery, refinery + industrial, industrial + heavy industry). Each level starts on the very section the previous one ended on (shared constants). One ground (`world-2/looks.ts`): World 1's dry earth, sand and red desert rock, with a stained industrial concrete as the paved cover. Eight new building groups from existing models (World 1's desert homes, outposts and mine headframes, Level Zero's factories, warehouses, tanks, refineries, cooling towers and container yards, the industrial buildings made of parts), plus one new model, an oil pumpjack (`oil-props.ts`). The industrial variants now share their group's weight instead of each taking it, so the 16 variants no longer swamp the hand-made buildings. Time of day: "3 days, 1 night" read as three day levels (morning, midday, afternoon), dusk for 2-4 (between day and night), night for 2-5; fixed within each level (no sky script changes, as in World 1); smog greys the clouds a little from 2-3 on (`storm` 0.15 → 0.35). No weather and no aurora: snow and the aurora belonged to the Frozen North.
- **Alternatives considered:** four day levels and a night (dawn added): "3 days" asked for three; a sandstorm weather in the desert levels or soot over the factories: not asked; new factory and foundry models: the Level Zero and World 4 industry already fits, and World 4's foundries are volcanic in look.
- **Consequences:** the ten World 2 bosses and the wave scripts are unchanged, so the frost-themed bosses (Floe Breaker, Narwhal, Harbour Kraken, Snow Owl, Glacier Colossus, Ice Queen, Boreal Citadel…) now fly over the desert and the factories. The 22 frozen prop models and 3 polar families stay in the game but no level places them; the engine tools made for them (frozen lakes, crevasses, floating ice, snow, aurora) stay and keep their own tests. The ground speeds (70 / 65 / 60 / 55 / 60) and the 300 s levels are kept. Props per level 2 982 / 6 548 / 9 087 / 11 182 / 12 049, buildings 1 553 / 4 883 / 8 570 / 11 039 / 12 049 (each level's seed), each second half fuller than the first. Also fixed on the way: the World 1 rework merge (#24) had committed a `node_modules` symlink pointing at itself, which left the main checkout without dependencies; it is untracked and `.gitignore` now ignores `node_modules` whether it is a folder or a link.
- **Status:** Accepted

