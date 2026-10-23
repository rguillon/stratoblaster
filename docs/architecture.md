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

The build has two HTML entries sharing one bundle (`src/main.ts`):

| Page                     | Route (`app/route.ts`) | Started by                 |
| ------------------------ | ---------------------- | -------------------------- |
| `index.html`             | `game`                 | `app/start-app.ts`         |
| `player_ship/index.html` | `player-ship-viewer`   | `app/start-ship-viewer.ts` |

The player ship viewer shows every ship of `GameDefinition.playerShips` side by side, rotating
(`render/model-showcase.ts`), with name and stats captions (`ui/caption-row.ts`). It is lit by a
procedural sky cube map (`render/environment/`), so it downloads no asset.

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
`levels`, a `LevelCatalog`), the logical `screen` size, the menu `texts`, and a `view` slot. The view slot's type
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
5. Run `make check`.
