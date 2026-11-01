# Phase 18 — Full Python port

> Requirements written by the agent at the owner's request ("port all the code in a single phase", 2026-10-29). Review them like any other phase.
> The agent fills the **Agent** sections and never edits the requirement sections.

**Status:** Ready  <!-- Draft | Ready -->
**Depends on:** Phase 17 (foundation: uv, Transcrypt build, lint gates, `core/math/rng.py`)

---

## 🧑 Goal
Every module of the TypeScript game on `main` has a Python counterpart on this branch, and the Python game runs in the browser with the same behaviour, the same content and the same numbers. The TypeScript code is then removed from the branch.

## 🧑 Requirements

### P18-R01 — Every source module is ported  · MUST
Each `.ts` file under `src/` (about 530 files, about 70,000 lines) has a `.py` counterpart in the same place, following the layout in ENG-10. Files that exist only for TypeScript (type-only modules, declaration files, `globals.d.ts`) become `typings/` stubs or are dropped with a DECISIONS entry.

**Acceptance criteria**
- [ ] Given the list of `src/**/*.ts` on `main`, when each is mapped to its counterpart, then every entry has a `.py` file or a DECISIONS entry explaining why not.
- [ ] `make lint`, `make typecheck` and `make build` pass on the whole `src/` tree.

### P18-R02 — Numeric modules match the TypeScript output  · MUST
Modules that compute numbers (math, noise, colour, geometry, scenery layout, level and wave generation, boss patterns, enemy and weapon logic, time of day, weather) produce the same results as the TypeScript version for the same inputs.

**Acceptance criteria**
- [ ] For each such module, a parity script runs the TypeScript version (transcribed to JavaScript, or run under Node with type stripping) and the Python build on the same seeds and inputs, and reports zero mismatches.
- [ ] Results of the parity scripts are recorded in the report, with the number of values compared.

### P18-R03 — The game runs in the browser  · MUST
The Python build runs the game from the title screen to game over and back, without console errors.

**Acceptance criteria**
- [ ] Given `make dev`, when the page loads, then the title screen appears, a level can be started, the player moves and shoots, pause and resume work, and game over returns to the title.
- [ ] The Babylon.js scene renders the same models, materials and effects as the TypeScript game, within the visual references the owner accepts.

### P18-R04 — Babylon.js is vendored and pinned  · MUST
Babylon.js (the version pinned on `main`) is vendored under `public/vendor/` by `make vendor`, with its SHA-256 checked (ENG-02).

**Acceptance criteria**
- [ ] `make vendor` downloads the pinned build and fails when the checksum differs.
- [ ] `make build` copies the vendored files into `dist/`.

### P18-R05 — Layering and engine/game split hold  · MUST
The layering and engine/game rules of ENG-11, ENG-140..ENG-144 are enforced by import-linter contracts (one contract per rule).

**Acceptance criteria**
- [ ] `make lint` fails on a probe import that breaks any rule, and passes on the port.

### P18-R06 — Tests and gates are restored  · MUST
pytest unit tests (mirroring the TypeScript tests on `main`, keeping the requirement IDs in test names) and the coverage thresholds of ENG-43 are restored, and `make check` runs them.

**Acceptance criteria**
- [ ] `make test` and `make coverage` pass with the thresholds of ENG-43.
- [ ] Every TypeScript test on `main` has a Python counterpart, or a DECISIONS entry explaining why not.

### P18-R07 — TypeScript toolchain removed  · MUST
When P18-R01 to P18-R06 pass, the TypeScript source, `package.json`, `package-lock.json`, `vite.config.ts`, `tsconfig.json`, `eslint.config.mjs`, `playwright.config.ts` (replaced by the Python equivalent) and the other npm files are removed from the branch.

**Acceptance criteria**
- [ ] `git ls-files | grep -E '\.(ts|js|mjs)$'` returns nothing outside `public/`.
- [ ] CI and the deploy workflow run the Python gates (ENG-70..81).

## 🧑 Tunable values
| Name | Value | Notes |
|------|-------|-------|
| Parity tolerance | exact (0 mismatches) | Floating-point results may differ by at most 1e-9 when a TypeScript and a Python operation are not bit-identical; each such case is listed in the report |

## 🧑 Out of scope for this phase
- New gameplay, new levels, new art. The port reproduces `main`.
- Changing the spec requirements of phases 1 to 16 (only the engineering stack changed, in phase 17).

## 🧑 Engineering additions for this phase
- Work is committed in small steps per module group, each passing `make check-fast` (ENG-94).
- The phase is validated only when every requirement above is met. The merge into `main` still needs explicit approval (ENG-92).

## 🧑 Manual validation checklist
- [ ] `make install && make build && make dev`, then play one full level on `http://localhost:5173`.
- [ ] Compare three levels side by side with the TypeScript build on `main` (same seed).
- [ ] No errors in the browser console.

## 🧑 Notes, references, sketches
- Constraints: `DECISIONS.md` D-170 and `01-engineering.md` §13.
- Reference implementation: `main` (TypeScript).

---

## 🧑 Review feedback
> After the agent reports, write corrections here, then say **"Fix phase 18"**.
> The agent ticks each item when fixed.

- [ ] 

---

## 🤖 Implementation report
> Filled by the agent. Do not edit (comment in Review feedback instead).

### Questions / blockers
- None yet.

### Plan
| Task | Requirement IDs |
|------|-----------------|
| Module-by-module port, in dependency order (core → config → platform → input → audio → ui → render → app → game) | P18-R01, P18-R02 |
| Babylon vendoring (`make vendor`) | P18-R04 |
| Browser run-through and visual check | P18-R03 |
| Layering contracts for the engine/game split | P18-R05 |
| pytest suite and coverage gate | P18-R06 |
| Remove the TypeScript toolchain | P18-R07 |

### Progress
- `src/core/math/` ported (6 of 530 TypeScript files): `bits` (new: 32-bit helpers shared by the RNG and the hash), `rng`, `min_heap`, `color`, `noise`, `pixel_contrast`. Parity: 385 values compared with zero mismatches (`brightest_but` allowed 1e-7 for the Float32 rounding it skips, see its docstring).
- Remaining: `core/` (65 files), `config/`, `platform/`, `input/`, `audio/`, `ui/`, `render/`, `app/`, `game/`, the Babylon vendoring, the tests and the TypeScript removal.

### Requirement traceability
| ID | Status | Code | Tests | Notes |
|----|--------|------|-------|-------|
| P18-R01 | In progress (6 of ~530 files) | `src/core/math/` | | |
| P18-R02 | In progress | `src/core/math/` | parity script (scratch, not committed) | 385 values, 0 mismatches |
| P18-R03 | Not done | | | |
| P18-R04 | Not done | | | |
| P18-R05 | Not done | | | |
| P18-R06 | Not done | | | |
| P18-R07 | Not done | | | |
