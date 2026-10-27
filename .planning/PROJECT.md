# Stratoblaster

## What This Is

Stratoblaster (package name `stratoblaster`) is an old-school vertical shoot 'em up with modern 3D graphics, running entirely in the browser with no backend: the player picks one of three ships and flies 20 levels (4 worlds x 5 levels) against waves of enemies and bosses, with weapons, bombs, score, generated darksynth music and sound effects. It is deployed to GitHub Pages at https://rguillon.github.io/stratoblaster/. Target runtime is desktop and mobile browsers with keyboard, gamepad and touch input; it is built for casual players and is meant to be accessible to kids. Everything (3D models, terrain, music, sound effects) is generated in code.

## Core Value

Responsive controls and a steady 60 fps on a modest computer, so that the core loop (avoid enemy fire, shoot enemies, pick up bonuses) is fun for casual players in a plain browser tab. If anything else slips, the game must still feel responsive and readable.

## Source of Truth and Working Agreement

- **`specs/` is the single source of truth** and is human-owned: `specs/00-vision.md`, `specs/01-engineering.md` (ENG-xx), `specs/02-game-design.md` (GD-xx), `specs/phases/phase-NN-*.md` (Pnn-Rxx requirements plus the agent-filled implementation report), `specs/PROGRESS.md` (status board) and `specs/DECISIONS.md` (agent decision log, D-001..D-112, the human may veto).
- **`.planning/` is a derived view** built from `specs/` by the ingest of 2026-10-27 (`.planning/intel/`, `.planning/INGEST-CONFLICTS.md`, `.planning/codebase/`). On any conflict, `specs/` plus `specs/DECISIONS.md` win. Agents never edit the requirement sections of `specs/`; stale human-owned spec text is a to-do for the human (see `STATE.md`).
- `CLAUDE.md` governs the process: code follows specs; do only the current phase; requirement IDs traceable in tests; one branch `phase-NN` per phase; Conventional Commits; never bypass git hooks or weaken lint/coverage config.
- **`CLAUDE.md` governs the verification gate** (it takes precedence over the older wording of ENG-32 and `specs/README.md`): at implement and fix time run the light gate only (`make typecheck build e2e`); the full gate `make check` (lint, typecheck, unit tests, coverage thresholds, build, e2e) runs once, at validation (`/validate-phase`).
- Phase commands: `/new-phase N name` (human-defined requirements), `/implement-phase N`, `/fix-phase N`, `/validate-phase N`.

## Requirements

### Validated

All twelve phases are Validated per `specs/PROGRESS.md` (see `ROADMAP.md` for dates, branches, tags and coverage; `REQUIREMENTS.md` for IDs).

- ✓ Main menu flow with loading, darksynth title, ship select and 4 x 5 level select; keyboard, gamepad and touch navigation; high score and last ship in cookies — Phase 1
- ✓ Three code-generated, low-poly player ships (balanced, heavy, light) — Phase 2
- ✓ Bullet, laser and missile weapons with five levels each, `player_shots/` viewer — Phase 3
- ✓ Generated terrain, sea, clouds, roads and props under a 35-degree tilted playfield camera (Level Zero) — Phase 4
- ✓ 21 enemy kinds (11 base, 5 veteran, 5 elite) with generated models, paths and attacks, `enemies/` viewer — Phase 5
- ✓ World 1 (levels 1-1..1-5, sea to green grass to desert, about 4 min each), wave scripts, rising difficulty — Phase 6
- ✓ Boss engine, ten World 1 bosses, boss health bar, mini boss checkpoint, level end on the final boss — Phase 7
- ✓ World 2 Industrial Desert (2-1..2-5), atmosphere and weather engine, ten bosses — Phase 8
- ✓ World 3 Industrial Towns (3-1..3-5), rain and lightning, ten bosses — Phase 9
- ✓ World 4 Metropolis (4-1..4-5), ash and embers, ten bosses ending with the Caldera Throne — Phase 10
- ✓ Score, saved high score, lives, bombs and their bonuses — Phase 11
- ✓ Pause menu, generated music and sound effects, settings with Music and SFX volumes — Phase 12
- ✓ Full first-release scope of the vision (4 worlds of 5 levels) — Phases 6-10

### Active

None. The next phase is undefined: the human defines it with `/new-phase` (requirements are human-owned). No new requirements are invented here.

### Out of Scope

- Multiplayer, backend or server, user accounts — vision non-goals; persistence is cookies only
- World 5 — dropped by the reviewer on 2026-10-26 (D-089); the Caldera Throne is the last boss
- Quality presets and graphics settings — ENG-102 removed (D-095)
- Master volume and key remapping — only Music and SFX sliders were specified (D-095)
- Score carried across levels, name entry, leaderboards — out of scope in the phase 11 spec
- Downloaded audio or model assets — everything is generated in code

## Context

- **Status:** brownfield. Phases 1-12 are Validated (milestone v1.0, first release content complete as of 2026-10-27). Latest full gate on record (after the World 4 rework): 1591 unit tests, 99.4 % lines, 87.87 % branches, 117 e2e.
- **Tech environment:** TypeScript strict, Babylon.js 9 (the only runtime dependency, deep ES-module imports), Vite 8, Vitest 5 with coverage-v8, Playwright (Chromium), ESLint 10, Prettier, Husky, Node 24 LTS. Built and run through the `Makefile`.
- **Architecture:** layered (`core/` pure simulation with no Babylon or DOM; `render`, `fx`, `audio`, `input`, `ui` read core state; `app/` wires layers) and an engine / game split: everything outside `src/game/` is game-agnostic, concrete content (enemies, bosses, weapons, levels, tunables, models, music styles) lives in `src/game/`. See `.planning/codebase/ARCHITECTURE.md` and `docs/architecture.md`.
- **Debug and viewer pages** (production build includes them): `player_ship/`, `player_shots/`, `level_zero/`, `enemies/`, `bosses/`, `boss/`; debug URL options on the game screen (`?level=N-M&t=&ship=&boss=&weather=0&look=`).
- **World journey today:** the four worlds are one continuous journey (sea to green grass to desert, Industrial Desert, factories to garden villages, houses to skyscrapers); bosses and wave scripts keep their original frost, jungle and volcanic themes. Unused-but-kept engine tools (snow, aurora, lava, frozen and jungle props) are intentional (D-110..D-112), not gaps.
- **Provenance:** `.planning/intel/` (synthesised decisions, requirements, constraints, context), `.planning/INGEST-CONFLICTS.md` (0 blockers, 14 warnings approved: decisions and later phases win over stale spec text), `.planning/codebase/` (derived map from the earlier mapping run, not authoritative).

## Constraints

- **Tech stack**: TypeScript strict (`noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitOverride`), Babylon.js, Vite, Node 24, minimal runtime dependencies (each new one needs a `DECISIONS.md` entry) — ENG-01..ENG-05
- **Platform**: WebGL2 required with a clear message when missing; last 2 versions of desktop Chrome, Edge, Firefox, Safari; touch controls exist for mobile browsers — ENG-06, P01-R03, P01-R11
- **Persistence**: no backend, same-origin static fetches only; settings, high score, last ship and weapon levels in cookies prefixed with the game id, 365-day max age — VISION-05, D-010
- **Performance**: 60 FPS at 1080p on a mid-range integrated GPU, initial JS about 1.5 MB gzip or less, fixed 60 Hz simulation step — ENG-100, ENG-101, ENG-107 (the 60 FPS target has only been checked under software rendering, see `STATE.md`)
- **Determinism**: seeded RNG and injected clock in `core/`, no `Math.random` or `Date.now` — ENG-18, ENG-46
- **Layering**: `core/` pure; engine game-agnostic; dependency direction enforced by lint — ENG-11, ENG-140..ENG-148
- **Quality gate**: ESLint zero warnings, tsc zero errors, `src/core/**` coverage 90 % lines / 85 % branches / 90 % functions / 90 % statements, whole `src/` 70 % lines, coverage never decreases, thresholds never lowered, hooks never bypassed — ENG-12, ENG-14, ENG-43, ENG-44, ENG-64
- **Assets and audio**: all models, textures, music and sound effects generated in code; no audio file may reach `dist/`; third-party assets only CC0 or CC-BY listed in `CREDITS.md`; MIT license — GD-60, GD-70, GD-71, P12-R05, ENG-121..ENG-125
- **Photosensitivity**: at most 3 lightning flashes in any second; bomb flash under 3 per second — P09-R05, P11-R05
- **Process**: specs first; requirement IDs appear in test names; verification gate per `CLAUDE.md` (light at implement/fix, full at validation) — CLAUDE.md, ENG-42

## Key Decisions

Accepted agent decisions that constrain future work. The full log (112 entries, D-001..D-112) is `specs/DECISIONS.md`; the human may veto any of them. **No decision is LOCKED.** Where an Accepted entry was superseded in effect by a later one, it is shown under its superseder.

<decisions>

| Decision                                                                                                                                                                 | Rationale                                                                                                               | Outcome                                        |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| D-001 TypeScript strict + Babylon.js + Vite, deep ES-module imports                                                                                                      | Browser 3D with tree-shaking; Three.js, PlayCanvas, Unity/Godot export and raw WebGL rejected                           | Accepted                                       |
| D-003 Scaffold conventions: Vite `base: './'`, `*.visual.ts` excluded from coverage, layering by lint, 60 Hz fixed step                                                  | Works under any GitHub Pages sub-path (replaces ENG-82's repo-name base); keeps GPU-only code out of coverage           | Accepted                                       |
| D-010 Persistence in cookies (key prefix = game id), not localStorage                                                                                                    | Follows the vision, GD-51 and P01; ENG-07 text is stale                                                                 | Accepted                                       |
| D-016 Game named Stratoblaster                                                                                                                                           | Game id is the cookie prefix; no migration of old cookies                                                               | Accepted                                       |
| D-019 ESLint 10 with eslint-plugin-import-x                                                                                                                              | Replaces eslint-plugin-import and the ESLint pin of D-002; ENG-12 text is stale                                         | Accepted                                       |
| D-020 Generated levels: seeded data-driven terrain, 35-degree tilted camera, Level Zero on the `level_zero/` page and not in level select                                | Reviewer accepted the 11 proposed defaults                                                                              | Accepted                                       |
| D-036 Playable levels as data: `GameLevel`, distance-triggered wave runner, pure `LevelRun`                                                                              | Keeps the engine game-agnostic                                                                                          | Accepted                                       |
| D-039 Game controls merged in `input/game-controls.ts`; D-043 E switches weapon                                                                                          | Key-position based, AZERTY-safe; bomb needs another key (D-091)                                                         | Accepted                                       |
| D-047 Player base speed 225 px/s (balanced 225, heavy 180, light 315)                                                                                                    | Supersedes D-044's 150 px/s and the 100 px/s in the phase 2 text; D-044's wave density stays, counts extended by D-051  | Accepted (D-044 superseded)                    |
| D-049, D-050, D-092 Weapon, life and bomb bonuses; pure player hull; separate seeded sources                                                                             | Deterministic drops; weapon draws unchanged when life and bomb bonuses were added                                       | Accepted                                       |
| D-053..D-063, D-068, D-073 Boss engine as data (parts, shields, joints, turrets, stage patterns, rage, laser turrets)                                                    | Ten bosses per world need no engine change per boss                                                                     | Accepted (D-068's `sweepDeg` removed by D-073) |
| D-056 Mini boss checkpoint with Continue / Level select                                                                                                                  | GD-42                                                                                                                   | Accepted                                       |
| D-059 Weapon balance: laser 80/140/200/260/320 dps, missile 14 damage                                                                                                    | Supersedes D-015's laser and missile numbers (GD-33)                                                                    | Accepted (D-015 numbers superseded)            |
| D-064, D-065, D-066, D-076..D-079, D-082..D-086 Atmosphere, weather (snow, rain, lightning, ash, embers), frozen ground, lava, plumes, contrast shots as engine tools    | Generic engine features; original World 2-4 looks no longer used by levels since D-110..D-112, tools kept               | Accepted (tools kept, unused)                  |
| D-071 Weapon levels carry from one completed level to the next (`<game id>_weapons` cookie)                                                                              | Supersedes P06-R02's "start at guns level 1"; a game over saves nothing                                                 | Accepted                                       |
| D-074 Enemy bullets as plasma balls on thin instances                                                                                                                    | Replaces the look of D-069                                                                                              | Accepted (D-069 look superseded)               |
| D-075, D-093 e2e builds render at low cost and have no render loop; tests drive `advance()` / `step()`                                                                   | Deterministic, fast e2e; test APIs verified absent from production                                                      | Accepted                                       |
| D-089 World 5 dropped: 4 x 5 grid, all 20 levels unlocked                                                                                                                | Reviewer decision 2026-10-26; Caldera Throne is the last boss                                                           | Accepted                                       |
| D-090 Ten veteran and elite enemy kinds (P05-R13..R24)                                                                                                                   | 21 kinds; veterans from World 3, elites in World 4                                                                      | Accepted                                       |
| D-091 Phase 11 defaults (score per attempt, 3 bombs, keys R / Left Shift, life and bomb drops)                                                                           | Reviewer approved the spec 2026-10-26                                                                                   | Accepted                                       |
| D-094 Faster git hooks (incremental tsc, lint caches)                                                                                                                    | Hooks stay under about 15 s (ENG-65) without weakening checks                                                           | Accepted                                       |
| D-095, D-096 Pause as menu screens (Escape, P, Start/Select, touch); Backspace and B do nothing in game; Music and SFX sliders only                                      | Supersedes D-041's "Esc leaves"; no master volume, no presets                                                           | Accepted (D-041 superseded)                    |
| D-097..D-102 Small Web Audio engine; generated per-world darksynth music and stressful boss tracks; layered explosions                                                   | No audio files (ENG-120 audio part waived by P12-R05); D-108 supersedes D-107's booms                                   | Accepted (D-107 superseded by D-108)           |
| D-103 Darksynth look for menus and HUD                                                                                                                                   | Supersedes the cyberpunk look of D-013 and D-014; D-040 removed the CRT overlay                                         | Accepted (D-013, D-014 look superseded)        |
| D-104 Pilot model in the menu backdrop                                                                                                                                   | Reviewer asked to revert to the balanced ship; only the sun emblem removal stays                                        | Reverted                                       |
| D-105 Boss health bar on the left edge                                                                                                                                   | Keeps the playfield clear                                                                                               | Accepted                                       |
| D-018 CI: e2e in a single job (amended 2026-10-27)                                                                                                                       | Consistent with ENG-72; initial 3-shard layout dropped                                                                  | Accepted                                       |
| D-109, D-110, D-111, D-112 World reworks: World 1 gradient (sea to green to desert), World 2 Industrial Desert, World 3 factories to garden villages, World 4 Metropolis | Reviewer requested 2026-10-26/27; bosses and wave scripts kept, snow, aurora, lava, frozen and jungle tools kept unused | Accepted, awaiting the reviewer's check        |

</decisions>

---

_Last updated: 2026-10-27 after roadmap creation from the ingest of `specs/` (brownfield, phases 1-12 Validated)_
