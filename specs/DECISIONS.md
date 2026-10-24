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
