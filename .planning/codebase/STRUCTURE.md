---
last_mapped_commit: f4b3594074f5b8d67c594e038113c45d65d18a7c
last_mapped_at: 2026-10-27
---

# Codebase Structure

**Analysis Date:** 2026-10-27

## Directory Layout

```
pewet/                          # repo root (package name "stratoblaster")
├── index.html                  # game page
├── player_ship/index.html      # ship viewer page
├── player_shots/index.html     # shots viewer page
├── level_zero/index.html       # scenery viewer page
├── enemies/index.html          # enemies viewer page
├── bosses/index.html           # bosses viewer page
├── boss/index.html             # alias of bosses viewer
├── src/                        # all TypeScript (541 files)
│   ├── main.ts                 # bootstrap (only file importing src/game/index.ts)
│   ├── app/                    # wiring, game state machine, page starters (33 files)
│   ├── core/                   # pure simulation, no Babylon/DOM (56 files)
│   ├── game/                   # THIS game's content (341 files)
│   ├── render/                 # Babylon presentation (47 files)
│   ├── ui/                     # DOM HUD and screens (22 files)
│   ├── audio/                  # Web Audio synth and players (11 files)
│   ├── input/                  # device to action mapping (8 files)
│   ├── config/                 # engine tunables (14 files)
│   ├── platform/               # browser storage and WebGL checks (3 files)
│   ├── assets/                 # loading task runner (1 file)
│   ├── debug/                  # e2e and debug test APIs (4 files)
│   ├── fx/                     # placeholder (.gitkeep only)
│   └── globals.d.ts            # ambient globals (e.g. __E2E__)
├── tests/
│   ├── unit/                   # mirrors src/ (app, core, audio, assets, game, ...)
│   ├── fixtures/               # sample game used to test the engine (ENG-145)
│   ├── helpers/                # shared test helpers (fake-dom, fake-audio, boss-bot, ...)
│   └── e2e/                    # Playwright specs (world-1..4, menus, viewers)
├── public/assets/              # static assets (audio, env, models, textures; mostly empty)
├── specs/                      # specification source of truth (see CLAUDE.md)
│   ├── phases/                 # phase-NN-*.md requirement files
│   ├── PROGRESS.md, DECISIONS.md
├── docs/architecture.md        # architecture reference
├── .claude/commands/           # implement-phase, fix-phase, validate-phase, new-phase
├── .github/workflows/          # ci.yml, deploy.yml
├── .husky/                     # git hooks (pre-commit, pre-push)
├── .planning/codebase/         # generated codebase maps (this document)
├── eslint.config.mjs           # lint and layer rules
├── vite.config.*               # build (Vite), entry pages
├── playwright.config.ts        # e2e config
├── Makefile                    # make typecheck | build | e2e | lint | test | coverage | check
└── package.json                # scripts, Babylon and dev dependencies
```

## Directory Purposes

**`src/app/`:**

- Purpose: game state machine, menu flow, session and play objects, viewer scene builders, saved settings and scores.
- Contains: `start-app.ts`, `start-{ship,shot,scenery,enemy,boss}-viewer.ts`, `game-session.ts`, `game-play.ts`, `game-play-hud.ts`, `game-play-state.ts`, `level-scene.ts`, `menu-*.ts`, `pause-menu.ts`, `settings-menu.ts`, `saved-*.ts`, `page-audio.ts`, `game-audio.ts`, `route.ts`, `debug-options.ts`, `rate-meter.ts`, plus viewer helpers (`enemy-viewer-*.ts`, `shot-viewer-scene.ts`, `boss-viewer-stage.ts`, `dummy-targets.ts`, `enemy-close-up.ts`).
- Key files: `src/app/start-app.ts`, `src/app/route.ts`, `src/app/game-session.ts`.

**`src/core/`:**

- Purpose: deterministic simulation and rules, game-agnostic.
- Contains:
  - `systems/`: `level-run.ts` (level state), `level-run-types.ts`, `wave-runner.ts`, `enemy-world.ts`, `enemy-shots.ts`, `enemy-motion.ts`, `shot-world.ts`, `projectile-motion.ts`, `beam.ts`, `boss-fights.ts`, `boss-pattern.ts`, `player-flight.ts`, `player-hits.ts`, `player-hull.ts`, `player-bombs.ts`, `bonus-world.ts`, `run-arsenal.ts`, `gun-muzzles.ts`.
  - `entities/`: `enemy.ts`, `jointed-enemy.ts`, `boss.ts`, `boss-pieces.ts`, `boss-joint.ts`, `boss-roll.ts`, `boss-turret.ts`, `muzzle.ts`, `player-ship.ts`, `shot-target.ts`, `weapon.ts`.
  - `scenery/`: `scenery-level.ts`, `height-field.ts`, `road-network.ts`, `road-paths.ts`, `road-traffic.ts`, `traffic.ts`, `prop-placement.ts`, `float-placement.ts`, `away-placement.ts`, `ground-fit.ts`, `ice-sculpt.ts`, `atmosphere.ts`, `sky-look.ts`, `lightning.ts`, `scroll-track.ts`, `lanes.ts`, `street-grid.ts`, `draws.ts`.
  - `content/`: `game-definition.ts`, `game-level.ts`, `level-catalog.ts`, `menu-texts.ts`.
  - `menu/`: `menu-screen.ts`, `grid-cursor.ts`. `loop/`: `fixed-step-clock.ts`. `math/`: `rng.ts`, `noise.ts`.
  - `events/`: empty (`.gitkeep`).
- Key files: `src/core/content/game-definition.ts`, `src/core/systems/level-run.ts`, `src/core/entities/boss.ts`.

**`src/game/`:**

- Purpose: all concrete content of this game.
- Contains:
  - `index.ts`: the single `GAME: GameDefinition` export.
  - `sim/`: concrete enemies (`sim/enemies/*.ts`, one file per kind: `gnat.ts`, `hornet.ts`, `scissor.ts`, ...), bosses (`sim/bosses/world-boss.ts`, `boss-launches.ts`), kinds registries (`enemy-kinds.ts`, `veteran-kinds.ts`, `elite-kinds.ts`, `boss-kinds.ts`), levels (`levels.ts`, `scenery-levels.ts`, `assemble-level.ts`, `world-1.ts` … `world-4.ts`).
  - `config/`: tunables. Flat files (`game.ts`, `scoring.ts`, `bombs.ts`, `hull.ts`, `bonuses.ts`, `boss-fights.ts`, `enemies.ts`, `enemies-veteran.ts`, `enemies-elite.ts`, `levels.ts`, `level-zero.ts`, `player-ships.ts`, `player-weapons.ts`, `menu-texts.ts`, `cars.ts`, `prop-look.ts`, `scenery-look.ts`, `ship-look.ts`, `shot-look.ts`, `title-look.ts`, `building-families.ts`, `bomb-look.ts`, `bonus-look.ts`, `boss-look.ts`, `enemy-look.ts`, `enemy-look-elite.ts`) and per-world folders `world-1/` … `world-4/` (`bosses.ts`, `difficulty.ts`, `looks.ts`, `props.ts`, `scenery*.ts`, `waves.ts`), plus `config/bosses/` (`boss-kit.ts`, `boss-rage.ts`, `mini-bosses.ts`, `final-bosses.ts`, `world-2/`, `world-3/`, `world-4/` boss files).
  - `view/`: visuals and audio for the content: `enemies/` (model files per kind), `bosses/` (boss models and greebles), `props/` (per-world prop families), `shots/`, `bombs/`, `bonuses/`, `audio/` (`game-audio.ts`, `compose-*.ts`, `instruments.ts`, `music-styles.ts`, `sound-designs.ts`), `scenery-bindings.ts`, `player-ship-models.ts`, `heavy-ship.ts`, `light-ship.ts`, `title-backdrop.ts`.
- Key files: `src/game/index.ts`, `src/game/view/enemies/enemy-bindings.ts`, `src/game/view/scenery-bindings.ts`.

**`src/render/`:**

- Purpose: Babylon scene, models, scenery stage. Read-only with respect to core.
- Contains: `game-view.ts`, `enemy-layer.ts`, `model-showcase.ts`, `model-animation.ts`, `node-pool.ts`, `node-adopter.ts`, `mesh-stats.ts`, `ship-select-stage.ts`, `shot-playfield.ts`; `environment/` (sky cube maps); `geometry/` (`prism.ts`, `lathe-z.ts`, `solids.ts`, `outline.ts`, `triangulate.ts`, `gradient-shapes.ts`); `scenery/` (scenery stage, kit, terrain chunks, road field, prop field, weather, clouds, aurora, lightning, plumes, rain rings, traffic, `*.visual.ts` shader materials).

**`src/ui/`:**

- Purpose: HUD, panels, menu screens.
- Contains: `game-hud.ts`, `boss-bar.ts`, `caption-row.ts`, `menu-overlay.ts`, `menu-view.ts`, `*-viewer-panel.ts`, `shot-viewer-panel.ts`, `stats-tile.ts`, `stage-fit.ts`, `shrink-to-fit.ts`, `ship-caption.ts`, `weapon-summary.ts`, `screens/` (`title-screen.ts`, `game-screen.ts`, `level-select-screen.ts`, `ship-select-screen.ts`, `settings-screen.ts`, `pause-panel.ts`, `loading-screen.ts`, `elements.ts`, `screen-handlers.ts`).

**`src/audio/`:**

- Purpose: engine-level audio plumbing: `synth.ts`, `sequencer.ts`, `music-player.ts`, `sfx-player.ts`, `voice-pool.ts`, `track-mixer.ts`, `audio-output.ts`, `audio-bindings.ts`, `audio-types.ts`, `level-cues.ts`.

**`src/input/`:**

- Purpose: keyboard, gamepad, pointer and touch input to `MenuCommand` and game actions: `game-controls.ts`, `keyboard-menu-input.ts`, `gamepad-menu-input.ts`, `pointer-menu-input.ts`, `menu-input.ts`, `menu-action.ts`, `hold-repeater.ts`, `held-directions.ts`.

**`src/config/`:**

- Purpose: engine tunables (ENG-17). Files: `engine.ts`, `game-play.ts`, `menu.ts`, `menu-input.ts`, `audio.ts`, `game-controls.ts`, `time-of-day.ts`, `weather.ts`, `plumes.ts`, `ship-viewer.ts`, `shot-viewer.ts`, `enemy-viewer.ts`, `boss-viewer.ts`, `scenery-viewer.ts`.

**`src/platform/`:** `cookie-storage.ts`, `key-value-storage.ts`, `webgl-support.ts`.

**`src/assets/`:** `loading-tasks.ts`.

**`src/debug/`:** `test-api.ts`, `viewer-test-api.ts`, `enemy-viewer-test-api.ts`, `boss-viewer-test-api.ts` (e2e `window.__*_TEST__` hooks).

**`tests/unit/`:** mirrors `src/` (e.g. `tests/unit/core/systems/`, `tests/unit/core/scenery/`, `tests/unit/app/`, `tests/unit/audio/`, `tests/unit/game/`).

**`tests/e2e/`:** Playwright specs such as `world-1.spec.ts`, `bosses.spec.ts`, `menu-keyboard.spec.ts`, `player-shots.spec.ts`, with `fixtures.ts` and `menu-helpers.ts`.

**`public/assets/`:** `audio/`, `env/`, `models/`, `textures/`. Each holds only `.gitkeep` in the tracked tree.

## Key File Locations

**Entry Points:**

- `src/main.ts`: bootstrap for every page.
- `src/app/start-app.ts`: game page (`startApp`).
- `src/app/route.ts`: URL to route.

**Configuration:**

- `eslint.config.mjs`: layer zones and purity rules.
- `src/config/*.ts`: engine tunables.
- `src/game/config/*.ts`: game tunables.
- `package.json`: scripts and engines (Node 24).
- `.nvmrc`, `.prettierrc.json`, `.editorconfig`: formatting and runtime.

**Core Logic:**

- `src/core/systems/level-run.ts`: level state machine.
- `src/core/systems/wave-runner.ts`: wave spawning.
- `src/core/systems/boss-fights.ts`: boss encounters.
- `src/core/scenery/scenery-level.ts`: scenery generation.

**Testing:**

- `tests/unit/`: Vitest unit tests.
- `tests/fixtures/`: sample game for engine tests.
- `tests/e2e/`: Playwright end-to-end tests.
- `tests/helpers/`: shared fakes.

## Naming Conventions

**Files:**

- kebab-case for all TypeScript files: `level-run.ts`, `boss-joint.ts`, `game-session.ts`.
- Babylon material shaders end in `.visual.ts`: `src/render/scenery/lava-material.visual.ts`, `src/render/environment/showcase-environment.visual.ts`.
- Viewer starters: `start-<viewer>-viewer.ts` in `src/app/`.
- Per-kind game files named after the kind: `src/game/sim/enemies/gnat.ts`, `src/game/view/enemies/elite-hive-model.ts`.
- Per-world config folders: `src/game/config/world-N/` and `src/game/sim/world-N.ts`.
- Test files: `<name>.test.ts` (unit, Vitest) and `<name>.spec.ts` (e2e, Playwright).
- HTML pages: directory with `index.html`.

**Directories:**

- Lowercase, single word or hyphenated: `scenery`, `boss-viewer`, `world-2`.

**Identifiers (from code):**

- Classes are PascalCase (`LevelRun`, `GameSession`); functions and variables camelCase; constants UPPER_SNAKE (`GAME_CONFIG`, `ENGINE_CONFIG`, `BOSS_KINDS`).
- Config objects are exported as `*_CONFIG` or `*_RULES` constants.

## Where to Add New Code

**New engine feature (generic, no game content):**

- Abstraction or system: `src/core/systems/<name>.ts` (pure, tests in `tests/unit/core/systems/<name>.test.ts`).
- Presentation for it: `src/render/<name>.ts` or `src/render/scenery/` for scenery.
- Tunables: `src/config/<name>.ts`.
- Tests: `tests/unit/core/...` or `tests/unit/render/...`; engine tests should use `tests/fixtures/`.

**New enemy kind:**

- Simulation: `src/game/sim/enemies/<kind>.ts`, extending `core/entities/enemy.ts` or `jointed-enemy.ts`.
- Register in `src/game/sim/enemy-kinds.ts` (or `veteran-kinds.ts` / `elite-kinds.ts`).
- Tunables: `src/game/config/enemies.ts` (or `enemies-veteran.ts`, `enemies-elite.ts`); look in `src/game/config/enemy-look.ts`.
- Visuals: `src/game/view/enemies/<kind>-model.ts` and bind in `src/game/view/enemies/enemy-bindings.ts`.
- Tests: `tests/unit/game/...`, e2e in `tests/e2e/enemies.spec.ts`.

**New boss:**

- Simulation: `src/game/sim/bosses/` (or extend `world-boss.ts`), register in `src/game/sim/boss-kinds.ts`.
- Config: `src/game/config/bosses/world-N/<boss>.ts`, `src/game/config/world-N/bosses.ts`.
- Visuals: `src/game/view/bosses/<boss>-model.ts`.

**New level or world:**

- Level data: `src/game/sim/world-N.ts`, `src/game/sim/levels.ts`, `src/game/sim/scenery-levels.ts`.
- Config: `src/game/config/world-N/` (`waves.ts`, `difficulty.ts`, `scenery.ts`, `looks.ts`, `props.ts`).
- Scenery look and props visuals: `src/game/view/props/<world>-*.ts`.
- Register in `src/game/index.ts` through the existing `GAME` fields if a new registry is needed.

**New scenery or weather kind:**

- Math: `src/core/scenery/`.
- Renderer: `src/render/scenery/`.
- Data: `src/config/weather.ts`, `src/config/time-of-day.ts`, `src/config/plumes.ts`.

**New screen or menu:**

- Menu logic: `src/core/menu/`, `src/app/menu-flow.ts`, `src/app/menu-scenes.ts`.
- DOM: `src/ui/screens/<name>-screen.ts`.

**New viewer page:**

- HTML at `<name>/index.html` (copy an existing one), route in `src/app/route.ts`, starter `src/app/start-<name>-viewer.ts`, branch in `src/main.ts`, and add to the Vite entries.

**New sound:**

- Recipe: `src/game/view/audio/sound-recipes.ts` or `sound-designs.ts`.
- Engine audio plumbing: `src/audio/`.

**Utilities:**

- Math: `src/core/math/` (RNG, noise).
- Platform: `src/platform/`.
- Engine-shared render helpers: `src/render/geometry/`.
- Test helpers: `tests/helpers/`.

## Special Directories

**`public/assets/`:**

- Purpose: static assets served as-is.
- Generated: No.
- Committed: Yes, but only `.gitkeep` placeholders are tracked in the subfolders.

**`.planning/codebase/`:**

- Purpose: generated codebase maps for GSD commands.
- Generated: Yes (by `/gsd-map-codebase`).
- Committed: Per project policy.

**`specs/`:**

- Purpose: requirement source of truth (human-edited requirement sections; agent-owned report sections).
- Generated: No.
- Committed: Yes.

**`dist/` (build output, not tracked):**

- Purpose: Vite build output.
- Generated: Yes.
- Committed: No (ignored via `.gitignore`).

**`src/fx/`:**

- Purpose: reserved for effects per `docs/architecture.md`; currently empty.
- Committed: Yes (`.gitkeep`).

---

_Structure analysis: 2026-10-27_
