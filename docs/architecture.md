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

## Game loop

`app/start-app.ts` runs Babylon's render loop. Each frame, `core/loop/FixedStepClock` turns the real frame time
into a whole number of 1/60 s simulation steps plus an interpolation factor `alpha` for rendering (ENG-100).
After a long stall, the step count is capped and excess time is dropped.

## Making a new game from this template

1. Delete the contents of `src/game/` (keep the folder structure) and of `tests/unit/game/`.
2. Create `src/game/index.ts` exporting a `GameDefinition` (see `src/core/content/game-definition.ts`).
3. Implement concrete content in `src/game/sim/` by extending the abstract classes in `src/core/entities/`.
4. Add visuals and sounds in `src/game/view/`, tunables in `src/game/config/`, assets under `public/assets/`.
5. Run `make check`.
