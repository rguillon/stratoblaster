# Architecture

Requirements: [`specs/01-engineering.md`](../specs/01-engineering.md).

## Layers

```
input/ ──actions──▶ app/ ──▶ core/ (pure, fixed 60 Hz step)
                              │
                         state + events
                              ▼
              render/  fx/  audio/  ui/   (read-only)
```

- `core/`: pure, deterministic, game-agnostic simulation. No Babylon, no DOM, no `Math.random` / `Date.now`.
- `render/`, `fx/`, `audio/`, `ui/`: read core state and react to core events; never mutate it.
- `input/`: turns devices into abstract actions.
- `app/`: the only place (with `main.ts`) that wires layers together.
- `config/`: engine tunables. `platform/`: browser wrappers. `debug/`: dev/e2e-only tools.

These rules are enforced by ESLint (`eslint.config.mjs`, `import/no-restricted-paths`).

## Engine / game split

Everything outside `src/game/` is a reusable engine. `src/game/` holds this game's content:

| Folder              | Contents                                                         | May import                                                                         |
| ------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `src/game/sim/`     | concrete bosses, enemies, weapons, levels (extend `core/` bases) | `core/`, `config/`, `game/sim/`, `game/config/`                                    |
| `src/game/view/`    | meshes, materials, effects, sounds for that content              | `render/`, `fx/`, `audio/`, `ui/`, `assets/`, `core/`, `game/sim/`, `game/config/` |
| `src/game/config/`  | game-specific tunables                                           | `core/`                                                                            |
| `src/game/index.ts` | the single `GameDefinition` export                               | anything in `game/`                                                                |

The engine never imports `src/game/`. `main.ts` imports `src/game/index.ts` and hands the `GameDefinition` to `app/`.
Engine tests use the sample game in `tests/fixtures/`, not `src/game/`.

## Pages and routes

The build has four HTML entries sharing one bundle (`src/main.ts`):

| Page                      | Route (`app/route.ts`) | Started by                    |
| ------------------------- | ---------------------- | ----------------------------- |
| `index.html`              | `game`                 | `app/start-app.ts`            |
| `player_ship/index.html`  | `player-ship-viewer`   | `app/start-ship-viewer.ts`    |
| `player_shots/index.html` | `player-shots-viewer`  | `app/start-shot-viewer.ts`    |
| `level_zero/index.html`   | `scenery-viewer`       | `app/start-scenery-viewer.ts` |

The player ship viewer shows every ship of `GameDefinition.playerShips` side by side, rotating
(`render/model-showcase.ts`), with name and stats captions (`ui/caption-row.ts`). It is lit by a
procedural sky cube map (`render/environment/`), so it downloads no asset.

The player shots viewer (phase 03) looks straight down on a `GameDefinition.screen`-sized
playfield (orthographic camera, one world unit per logical pixel, Y up). One ship fires the
selected weapon at the selected level at dummy targets (`app/dummy-targets.ts`); the panel
(`ui/shot-viewer-panel.ts`) and keys 1-9 / W / S / G / T switch level, weapon, ship, stream
guides and targets. A tile (`ui/stats-tile.ts`) shows the FPS and the triangles drawn per frame.

The generated level viewer (phase 04, `level_zero/`) flies the game's first scenery level
(`GameDefinition.sceneryLevels`) under the tilted playfield camera for its whole duration. The
panel (`ui/scenery-viewer-panel.ts`) and keys P / F / R / N / S / O / 1-9 / ← → pause,
fast-forward, restart, change the seed, switch the sea, the playfield outline and the cloud
layers, and seek.

## Generated levels (phase 04)

```
core/scenery/  SceneryLevel (data) ─▶ HeightField ─▶ PropPlacer      ScrollTrack (time ↔ distance)
                                          │              │
render/scenery/  TerrainChunks ◀──────────┘   PropField ◀┘   (thin instances)
                 SceneryStage: camera, sun, sea, cloud layers, chunks + props around the camera
                 SceneryKit: materials / textures / shadows (plain, or *.visual.ts for WebGL)
```

- `core/scenery/scenery-level.ts`: a level is a list of sections, each `seconds` long at the
  level's scroll speed (so the duration is the sum of the seconds). A section is a fractal relief
  (`smooth` or `ridged`, with an optional soft height cap) plus optional operations: `flatten`
  (a plateau band), `channel` (a canyon along a winding line) and `shore` (ground dropping under
  the sea on one side). Optional sea level; prop rules.
- `core/scenery/height-field.ts`: pure, seeded height function of a level; sections blend over
  `transition`. `core/math/noise.ts`: seeded gradient noise (optionally tiling), fBm, ridged noise.
- `core/scenery/prop-placement.ts`: a jittered grid of candidate spots; buildings need flat ground
  above `minHeight`, a low-frequency zone noise picks the building group per area (clusters), empty
  cells may get trees. Each cell is decided from a hash of its coordinates, so chunks can be placed
  independently.
- `render/scenery/playfield-framing.ts`: the camera is tilted `tiltDeg` from straight down and
  placed so the bottom and top of the screen pass through the bottom and top of the logical
  playfield, a plane at `flightAltitude`. One world unit is one logical pixel; X across (0 under
  the playfield middle), Z along the level, Y up.
- `render/scenery/scenery-stage.ts` keeps terrain chunks (`terrain-chunks.ts`, pooled meshes) and
  their props (`prop-field.ts`, one thin-instanced mesh per prop kind plus one for its self-lit
  accents) around the camera, and moves the sea and cloud planes with it.
- `render/scenery/scenery-kit.visual.ts` (needs WebGL, not unit-tested): generated textures
  (`procedural-textures.ts`, pure and tested) blended by altitude and slope in a
  `StandardMaterial` plugin (`terrain-blend-plugin.visual.ts`); a PBR sea with a drifting
  generated normal map; cloud layers as a small shader (`cloud-material.visual.ts`); PCF sun
  shadows. `createPlainSceneryKit` stands in for it in unit tests.
- Props are geometry, not meshes: `PropModelFactory` returns vertex-coloured, flat-shaded
  `ColoredGeometry` built with `render/geometry/solids.ts` (boxes, bodies of revolution, rings).

## Shots (phase 03)

- `core/entities/weapon.ts`: data-only `WeaponDefinition`s. A projectile weapon fires streams
  (offset + angle) per level from the ship's muzzle or centre, with a fire rate, launch speed, constant acceleration up to a cap,
  optional homing on the closest target, and direct or area damage. A beam weapon has a damage
  per second and width per level; above level 1 it goes through a target and continues one
  level lower.
- `core/systems/shot-world.ts`: pure, fixed-step simulation of one ship's shots against
  `ShotTarget`s (circles with health): fires volleys, moves projectiles
  (`projectile-motion.ts`), traces beams (`beam.ts`), applies damage and reports impacts.
  Projectiles are pooled.
- `render/game-view.ts`: `ShotRenderer`s draw one weapon's shots per frame from a `ShotFrame`
  (its projectiles, beam segments and impacts). `render/node-pool.ts` reuses nodes;
  `render/shot-playfield.ts` draws the grid, stream guides and target markers.

## Menus (phase 01)

```
keyboard ─┐                                   ┌─▶ ui/MenuOverlay (HTML, 480×640 logical)
gamepad  ─┼─▶ input/ ─MenuAction─▶ app/MenuController ─▶ app/MenuFlow (pure state machine)
taps     ─┘   (pointerCommand)            │
                                          └─▶ app/menu-scenes: game backdrop + render/ShipSelectStage
```

- `app/menu-flow.ts`: pure screen state machine `loading → title → ship-select → level-select → game`,
  with Back on each screen (transition table in `core/menu/menu-screen.ts`). Input is ignored while a
  screen fades in.
- `input/`: keyboard (by `KeyboardEvent.code`, so layouts do not matter), gamepads (polled every frame,
  dead zone) and taps all become the same `MenuAction`s (`up`, `down`, `left`, `right`, `confirm`,
  `back`). Bindings and repeat timings are in `config/menu-input.ts`.
- `ui/`: the overlay renders a `MenuView` (built by `app/menu-view-builder.ts`) and turns taps into
  commands. `ui/stage-fit.ts` fits the 480×640 stage (canvas + overlay) in the window.
- 3D: the game provides `GameView.menuBackdrop` (a scene behind every menu screen); the engine draws
  the ship select stage (`render/ship-select-stage.ts`) over it on the ship select screen. Both scenes
  are built and compiled behind the loading screen (`assets/loading-tasks.ts`).
- Persistence: `platform/cookie-storage.ts` behind the `KeyValueStorage` interface; keys are prefixed
  with the game id (`app/saved-choices.ts`).
- e2e builds expose `window.__GAME_TEST__` (`debug/test-api.ts`, ENG-52); `make build` fails if it
  leaks into the production bundle.

## Content contract

`GameDefinition<TView>` (`core/content/`) carries simulation data (e.g. `playerShips`, a
`PlayerShipRoster` from `core/entities/player-ship.ts`, whose first ship is the default choice;
`levels`, a `LevelCatalog`; `playerWeapons`, the `WeaponDefinition`s every ship can fire), the
logical `screen` size, the menu `texts`, and a `view` slot. The view slot's type
is defined by the presentation layers (`render/game-view.ts` → `GameView`) so `core/` never sees
Babylon types. Models are `ModelFactory` functions: `(scene) => TransformNode`, nose towards +Z,
+Y up. Generic geometry helpers live in `render/geometry/` (planform prisms with ear-clipping
triangulation, bodies of revolution along Z).

## Game loop

`app/start-app.ts` runs Babylon's render loop. Each frame, `core/loop/FixedStepClock` turns the real frame time
into a whole number of 1/60 s simulation steps plus an interpolation factor `alpha` for rendering (ENG-100).
After a long stall, the step count is capped and excess time is dropped. The menus then read the frame's
input, update the overlay, and animate and render the menu scenes (frame time capped at 0.1 s).

## Making a new game from this template

1. Delete the contents of `src/game/` (keep the folder structure) and of `tests/unit/game/`.
2. Create `src/game/index.ts` exporting a `GameDefinition` (see `src/core/content/game-definition.ts`).
3. Implement concrete content in `src/game/sim/` by extending the abstract classes in `src/core/entities/`.
4. Add visuals and sounds in `src/game/view/`, tunables in `src/game/config/`, assets under `public/assets/`.
   Declare the player ships in `GameDefinition.playerShips` and one model per ship id in
   `GameDefinition.view.playerShipModels`, the levels in `GameDefinition.levels` (e.g. with
   `buildLevelGrid`), the menu texts in `GameDefinition.texts`, the logical resolution in
   `GameDefinition.screen`, and the 3D scene behind the menus in `GameDefinition.view.menuBackdrop`.
   Declare the player weapons in `GameDefinition.playerWeapons`, one shot renderer per weapon id
   in `GameDefinition.view.playerShotRenderers`, and the ships' size on the playfield in
   `GameDefinition.view.playerShipScale` (logical pixels per model unit).
   Declare the levels with generated ground in `GameDefinition.sceneryLevels` (`SceneryLevel`
   data), and in `GameDefinition.view.scenery` the playfield camera, one `SceneryLook` per
   scenery level id and one `PropModelFactory` per prop kind id.
5. Run `make check`.
