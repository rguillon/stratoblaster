---
last_mapped_commit: f4b3594074f5b8d67c594e038113c45d65d18a7c
last_mapped_at: 2026-10-27
---

<!-- refreshed: 2026-10-27 -->

# Architecture

**Analysis Date:** 2026-10-27

## System Overview

```text
┌──────────────────────────────────────────────────────────────────────┐
│  Entry pages (7 HTML files, one bundle)   `src/main.ts`              │
│  route via `src/app/route.ts` → start-*.ts                           │
└───────────┬───────────────────────────────────────────┬──────────────┘
            │ game                                      │ viewers / debug
            ▼                                           ▼
┌──────────────────────────┐              ┌──────────────────────────────┐
│ app/  (wiring + state)   │              │ app/start-*-viewer.ts,        │
│ start-app.ts, GameSession│              │ shot/enemy/boss/scenery scene │
│ MenuController, GamePlay │              │ `debug/*-test-api.ts` (e2e)   │
└──┬──────────┬────────┬───┘              └──────────────┬───────────────┘
   │actions   │ state  │ render/ui/audio calls          │
   ▼          ▼        ▼                                 ▼
┌────────┐ ┌───────────────────────────────────────────────────────────┐
│ input/ │ │ core/  PURE fixed-step simulation (no Babylon, no DOM)    │
│ actions│ │ systems/ entities/ scenery/ content/ menu/ loop/ math/    │
└────────┘ └──────────────▲───────────────────────────▲────────────────┘
                          │ implemented by            │ registers via
                          │                           │ GameDefinition
┌─────────────────────────┴───────────┐     ┌─────────┴──────────────────┐
│ game/sim/  concrete bosses, enemies,│     │ game/index.ts  GAME        │
│ weapons, levels (extends core/)     │◀────│ (single GameDefinition)    │
│ game/config/  game tunables         │     └─────────┬──────────────────┘
└─────────────────────────────────────┘               │
                                                     ▼
┌──────────────────────────────────────────────────────────────────────┐
│ render/ ui/ audio/ (read-only presentation) ◀── game/view/ (visuals) │
│ babylon-facing: render/game-view.ts, render/scenery/, render/geometry│
│ platform/ (storage, webgl) · config/ (engine tunables) · assets/      │
└──────────────────────────────────────────────────────────────────────┘
```

## Pattern Overview

**Overall:** Layered engine plus game-content package. A pure, deterministic simulation in `src/core/` is driven by a fixed-step clock from `src/app/`. Presentation layers read simulation state and never mutate it. Everything outside `src/game/` is a game-agnostic engine; `src/game/` supplies all concrete content via one `GameDefinition` object.

**Key Characteristics:**

- `core/` is pure: no Babylon, no DOM, no `Math.random` / `Date.now` (seeded RNG in `src/core/math/rng.ts`, `dt` passed from the loop).
- Fixed-timestep loop: `src/core/loop/fixed-step-clock.ts` (`FixedStepClock`), used by `src/app/start-app.ts`.
- Single content entry point: `src/game/index.ts` exports `GAME: GameDefinition<GameView>`; `src/main.ts` is the only file outside `src/game/` that imports it (ENG-144).
- Abstract bases in `core/` (`Enemy`, `Boss`, `Weapon`, `Level`) are extended by concrete classes in `src/game/sim/` (ENG-141).
- Layer boundaries are enforced by ESLint `import-x/no-restricted-paths` in `eslint.config.mjs` (zones at lines ~54–82) and stricter purity rules for `src/core/**` and `src/game/sim/**` (`PURE_RULES`, line ~129).
- Only `src/app/` and `src/main.ts` wire layers together; nothing else may import `app/`.

## Layers

**`core/` (pure simulation):**

- Purpose: deterministic game rules, entities, level running, scenery placement math.
- Location: `src/core/`
- Contains: `systems/` (e.g. `src/core/systems/level-run.ts`, `wave-runner.ts`, `boss-fights.ts`, `enemy-world.ts`, `shot-world.ts`, `player-bombs.ts`, `bonus-world.ts`), `entities/` (`src/core/entities/enemy.ts`, `boss.ts`, `jointed-enemy.ts`, `weapon.ts`, `player-ship.ts`), `scenery/` (`src/core/scenery/scenery-level.ts`, `height-field.ts`, `road-network.ts`, `atmosphere.ts`, `lightning.ts`), `content/` (`src/core/content/game-definition.ts`, `game-level.ts`, `level-catalog.ts`), `menu/` (`src/core/menu/menu-screen.ts`, `grid-cursor.ts`), `loop/`, `math/`.
- Depends on: `config/` only.
- Used by: `app/`, `render/`, `ui/`, `audio/` (read-only), `game/sim/`.

**`game/sim/` (this game's simulation content):**

- Purpose: concrete bosses, enemies, levels, wave scripts.
- Location: `src/game/sim/` (e.g. `src/game/sim/enemies/*.ts` one file per enemy kind, `src/game/sim/bosses/world-boss.ts`, `src/game/sim/world-1.ts` … `world-4.ts`, `src/game/sim/levels.ts`, `src/game/sim/enemy-kinds.ts`, `src/game/sim/boss-kinds.ts`).
- Depends on: `core/`, `config/`, `game/sim/`, `game/config/`.
- Used by: `src/game/index.ts`.

**`game/config/` (game tunables):**

- Purpose: enemy HP, boss patterns, scoring, looks data, level data.
- Location: `src/game/config/` (e.g. `src/game/config/game.ts`, `src/game/config/scoring.ts`, `src/game/config/bosses/world-2/*.ts`, `src/game/config/world-N/*.ts`).
- Depends on: `core/` (types only).

**`game/view/` (this game's visuals and sounds):**

- Purpose: meshes, materials, effects, and audio recipes for the game's content.
- Location: `src/game/view/` (e.g. `src/game/view/enemies/enemy-bindings.ts`, `src/game/view/scenery-bindings.ts`, `src/game/view/audio/game-audio.ts`, `src/game/view/bosses/*.ts`, `src/game/view/props/*.ts`, `src/game/view/shots/*.ts`).
- Depends on: `render/`, `fx/`, `audio/`, `ui/`, `assets/`, `core/`, `game/sim/`, `game/config/`.
- Used by: `src/game/index.ts` (bindings hung on `GameDefinition.view`).

**`app/` (wiring and game state machine):**

- Purpose: boot, menus, game session, pause, saved settings and scores, page starters.
- Location: `src/app/`
- Contains: `start-app.ts` (`startApp`, game page), `game-session.ts` (`GameSession`), `game-play.ts` (`GamePlay`), `level-scene.ts`, `menu-controller.ts`, `menu-flow.ts`, `menu-scenes.ts`, `game-audio.ts`, `page-audio.ts`, `saved-*.ts`, and viewer starters `start-{ship,shot,scenery,enemy,boss}-viewer.ts`.
- Depends on: all engine layers (it is the only layer allowed to).
- Used by: `src/main.ts`.

**`render/` (Babylon presentation):**

- Purpose: scene graph, cameras, materials, meshes, scenery stage. Read-only with respect to `core/`.
- Location: `src/render/`. Key files: `src/render/game-view.ts` (`GameView` contract), `src/render/enemy-layer.ts`, `src/render/scenery/scenery-stage.ts`, `src/render/scenery/scenery-kit.ts`, `src/render/scenery/weather-layer.ts`, `src/render/model-showcase.ts`, `src/render/geometry/*.ts`, `src/render/*.visual.ts` materials.
- Depends on: `core/` (read), `config/`, `assets/`.

**`ui/` (DOM and HUD):**

- Purpose: HUD, panels, menu screens, shrink-to-fit stage.
- Location: `src/ui/` (e.g. `src/ui/game-hud.ts`, `src/ui/menu-overlay.ts`, `src/ui/screens/*.ts`, `src/ui/boss-bar.ts`, `src/ui/stage-fit.ts`).
- Depends on: `core/` (read), `config/`.

**`audio/` (Web Audio):**

- Purpose: synth, sequencer, music and SFX players, driven by level cues.
- Location: `src/audio/` (e.g. `src/audio/synth.ts`, `src/audio/music-player.ts`, `src/audio/sfx-player.ts`, `src/audio/level-cues.ts`, `src/audio/audio-output.ts`).

**`input/` (devices to actions):**

- Purpose: keyboard, gamepad, pointer, touch to abstract `MenuCommand` / game actions.
- Location: `src/input/` (e.g. `src/input/game-controls.ts`, `src/input/keyboard-menu-input.ts`, `src/input/gamepad-menu-input.ts`, `src/input/menu-action.ts`).

**`platform/` (browser wrappers):**

- Location: `src/platform/` (`cookie-storage.ts`, `key-value-storage.ts`, `webgl-support.ts`).

**`assets/`:** `src/assets/loading-tasks.ts` runs the loading task list.

**`debug/` (dev and e2e only):** `src/debug/test-api.ts`, `src/debug/viewer-test-api.ts`, `src/debug/enemy-viewer-test-api.ts`, `src/debug/boss-viewer-test-api.ts`. Installed on `window` only in e2e builds (`__E2E__`).

**`fx/`:** Declared in `docs/architecture.md`, but `src/fx/` currently contains only `.gitkeep`. Effects live under `src/render/` and `src/game/view/` instead.

## Data Flow

### Primary Request Path (a game frame)

1. `src/main.ts` `startGame` builds the Babylon engine and calls `startApp(engine, GAME, options)` (`src/app/start-app.ts`).
2. `startApp` drives the `FixedStepClock` (`src/core/loop/fixed-step-clock.ts`); each fixed step calls into the active `GameSession` / `GamePlay`.
3. Player input arrives through `src/input/game-controls.ts` as abstract actions and is passed to `LevelRun` (`src/core/systems/level-run.ts`).
4. `LevelRun` advances `ScrollTrack` → `WaveRunner` (`src/core/systems/wave-runner.ts`) which spawns enemies via their kind definitions into `EnemyWorld` and `ShotWorld`; `BossFights` holds the track during boss fights.
5. Presentation reads the resulting core state each frame: `src/app/level-scene.ts` and `src/render/game-view.ts` draw entities, `src/ui/game-hud.ts` draws the HUD, and `src/audio/level-cues.ts` reacts to level state.

### Menu / Flow Path

1. `src/input/menu-input.ts` (keyboard, gamepad, pointer) produces `MenuCommand`s.
2. `src/app/menu-controller.ts` forwards them to `src/app/menu-flow.ts` (`MenuFlow`), a state machine over menu states in `src/core/menu/menu-screen.ts` and `src/app/menu-state.ts`.
3. Starting a level: `MenuFlow` → `GameSession` (`src/app/game-session.ts`) → `GamePlay` (`src/app/game-play.ts`).
4. A level result goes back as `MenuFlow.completeLevel`; `MenuController.recordScore` saves high scores via `src/app/saved-settings.ts`/`saved-choices.ts` and `src/platform/cookie-storage.ts`.

### Scenery Path

`SceneryLook` (game data in `src/game/config/*/scenery*.ts`) → `resolveSky` / `AtmosphereTrack` (`src/core/scenery/atmosphere.ts`, `sky-look.ts`) → render in `src/render/scenery/scenery-stage.ts` and `sky-layers.ts`, with `src/render/scenery/weather-layer.ts` and `lightning-layer.ts` reading the atmosphere. Nothing in `core/systems` reads atmosphere (weather is look-only).

**State Management:**

- Simulation state lives in core objects (`LevelRun`, `EnemyWorld`, `ShotWorld`, `PlayerFlight`, `BossFights`), mutated only by `core/` update methods.
- Menu and app state lives in `app/` (`MenuFlow` state, `MenuController`, `GameSession`).
- Persistent state (settings, high scores, saved weapons) goes through `KeyValueStorage` (`src/platform/key-value-storage.ts`), backed by cookies in `src/platform/cookie-storage.ts`.

## Key Abstractions

**`GameDefinition`:**

- Purpose: the one object through which the game registers all content and view bindings.
- Definition: `src/core/content/game-definition.ts` (`GameDefinition<TView>`).
- Instance: `src/game/index.ts` (`GAME`).
- Pattern: registry object passed to `startApp` and viewers; engine discovers content only through it.

**`Enemy` / `JointedEnemy` / `Boss`:**

- Purpose: base classes for shot targets with health, movement, parts and joints.
- Examples: `src/core/entities/enemy.ts`, `src/core/entities/jointed-enemy.ts`, `src/core/entities/boss.ts` (with `boss-pieces.ts`, `boss-joint.ts`, `boss-turret.ts`, `boss-roll.ts`).
- Pattern: abstract class; concrete kinds in `src/game/sim/enemies/` and `src/game/sim/bosses/` (`world-boss.ts`) implement `enter`, `move`, `updatePattern`.

**`EnemyKindDefinition` / `BossKindDefinition`:**

- Purpose: data-plus-factory for spawnable enemies and bosses; `WaveRunner` refers to them by id only.
- Examples: `src/game/sim/enemy-kinds.ts`, `src/game/sim/boss-kinds.ts`, `src/game/sim/veteran-kinds.ts`, `src/game/sim/elite-kinds.ts`.

**`GameLevel` / `SceneryLevel` / `WaveScript`:**

- Purpose: a playable level (scenery, waves, difficulty, bosses).
- Examples: `src/core/content/game-level.ts`, `src/core/scenery/scenery-level.ts`, `src/game/sim/levels.ts`, `src/game/sim/scenery-levels.ts`.

**`GameView` binding contracts:**

- Purpose: presentation factories the game supplies (`enemies`, `scenery`, `bonuses`, `bombs`, `audio`, `playerShipModels`, `playerShotRenderers`, `menuBackdrop`).
- Examples: `src/render/game-view.ts`, `src/game/view/enemies/enemy-bindings.ts`, `src/game/view/scenery-bindings.ts`.

**`AtmosphereTrack`:**

- Purpose: blends look numbers by ground distance into plain `Atmosphere` values for the renderer.
- Example: `src/core/scenery/atmosphere.ts`.

**`BombRules` / `PlayerBombs`, `BonusWorld`:**

- Purpose: bombs and pickups (weapon, life, bomb) as core systems with game-supplied rules (`src/game/config/bombs.ts`, `src/game/config/bonuses.ts`).
- Examples: `src/core/systems/player-bombs.ts`, `src/core/systems/bonus-world.ts`.

## Entry Points

**Main bootstrap (all pages):**

- Location: `src/main.ts`
- Triggers: any of the seven HTML pages (`index.html`, `player_ship/index.html`, `player_shots/index.html`, `level_zero/index.html`, `enemies/index.html`, `bosses/index.html`, `boss/index.html`).
- Responsibilities: create the engine, pick the route, pass `GAME` to the matching starter.

**Route resolver:**

- Location: `src/app/route.ts` (`resolveRoute`, `AppRoute`)
- Triggers: `window.location.pathname`, works under any deployment sub-path.

**Game page:**

- Location: `src/app/start-app.ts` (`startApp`)
- Triggers: route `game` (`index.html`).

**Viewer pages:**

- Locations: `src/app/start-ship-viewer.ts`, `start-shot-viewer.ts`, `start-scenery-viewer.ts`, `start-enemy-viewer.ts`, `start-boss-viewer.ts`.

**Debug and e2e hooks:**

- Locations: `src/debug/*-test-api.ts`, `src/app/debug-options.ts` (`?level=…&boss=…`, `weather=0`, `look=…`).

## Architectural Constraints

- **Threading:** Single-threaded browser main thread. Rendering and simulation share the thread; `core/` is stepped at a fixed rate by the clock, rendering runs on the Babylon render loop (disabled in e2e builds with `renderLoop: !__E2E__`).
- **Global state:** `window` is touched only in `src/main.ts`, `src/app/start-app.ts` and `src/debug/*`. `src/game/config/` holds module-level constant tables (read-only use).
- **Circular imports:** Not detected by the layering rules; the lint zones forbid the main cycles (`core` ↔ `app`, `game` → engine).
- **Engine/game boundary:** Code outside `src/game/` must not name concrete content. `docs/architecture.md` mentions it; `src/game/index.ts` is the only place that assembles content.
- **Documentation drift:** `docs/architecture.md` lists `fx/` and a core event bus (`specs/01-engineering.md` §2 mentions `core/events/`), but `src/fx/` and `src/core/events/` contain only `.gitkeep`. Events are not routed through a bus; systems expose state that `app/` and `render/` read each frame.

## Anti-Patterns

### Importing `src/game/` from engine code

**What happens:** An engine file imports a concrete boss, enemy, level or view binding from `src/game/`.
**Why it's wrong:** Breaks ENG-140/142; the lint zones in `eslint.config.mjs` will fail, and the engine stops being reusable.
**Do this instead:** Add an abstraction in `core/` or the relevant engine layer and let `src/game/` implement it, registered through `GameDefinition` (`src/game/index.ts`).

### Mutating core state from presentation

**What happens:** A `render/`, `ui/`, or `audio/` module writes to `LevelRun`, `EnemyWorld`, or entity fields.
**Why it's wrong:** Presentation must be read-only (ENG-11); mutation there breaks determinism and fixed-step replay.
**Do this instead:** Expose a read model or method in `core/` and call it from `app/` in the fixed step (see `src/app/game-play.ts`).

### Adding imports of `app/` from other layers

**What happens:** `render/`, `ui/`, `core/`, `input/` or `game/` import from `src/app/`.
**Why it's wrong:** Only `app/` and `main.ts` may wire layers (eslint zone at `eslint.config.mjs` ~line 79).
**Do this instead:** Pass the needed callback or options object from `app/` into the lower layer's factory.

## Error Handling

**Strategy:** Boot failures show a fatal message in the `#fatal` element (`showFatal` in `src/main.ts`). Missing WebGL is detected in `src/platform/webgl-support.ts` before start. Storage access is wrapped so bad cookie or JSON values fall back to defaults (`src/app/saved-settings.ts`, `src/app/saved-choices.ts`).

**Patterns:**

- Core returns and records state (e.g. `LevelRun` phase `playing` → `clearing` → `complete`) rather than throwing in normal play.
- Test-only hooks throw if a required element is missing (`element(id)` in `src/main.ts`).

## Cross-Cutting Concerns

**Logging:** Not detected as a dedicated module; the debug overlay uses `statsParent` (`src/app/debug-options.ts`).
**Validation:** Game data is typed TypeScript objects; there is no runtime schema validation.
**Authentication:** Not applicable. The app is client-only with no accounts or server calls (ENG-07).

---

_Architecture analysis: 2026-10-27_
