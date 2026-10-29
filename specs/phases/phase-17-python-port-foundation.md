# Phase 17 — Python port: foundation

> Requirements written by the agent at the owner's request ("update the specs yourself and start the port", 2026-10-29). Review them like any other phase.
> The agent fills the **Agent** sections and never edits the requirement sections.

**Status:** Ready  <!-- Draft | Ready -->
**Depends on:** Phase 16 (the TypeScript game on `main` is the reference for every port)

---

## 🧑 Goal
The project runs on Python 3.12 and uv, and the compile path works end to end: Python in `src/` compiles with Transcrypt into `dist/js/`, and the page runs it. The first real module (the seeded random generator) is ported and matches the TypeScript output exactly. The rest of the port follows in later phases. The game is **not** playable on this branch yet.

## 🧑 Requirements

### P17-R01 — uv toolchain  · MUST
`uv` manages the Python environment and every command. A clean clone reaches a working toolchain with one command.

**Acceptance criteria**
- [ ] Given a clean clone, when `make install` runs, then `uv sync --locked` succeeds with Python 3.12 and no Node.js.
- [ ] `pyproject.toml` pins Transcrypt (`transcrypt==3.9.5`), ruff, mypy and import-linter; `uv.lock` is committed.
- [ ] `.python-version` is `3.12`, and `requires-python` excludes 3.13 and later (ENG-04, ENG-154).

### P17-R02 — Transcrypt build  · MUST
`make build` compiles the Python sources to browser modules and assembles `dist/`.

**Acceptance criteria**
- [ ] Given the sources, when `make build` runs, then `dist/index.html` and `dist/js/main.js` exist and `dist/js/main.js` has no compiler pragma calls (ENG-23).
- [ ] Given `dist/`, when a browser loads `index.html`, then `main()` runs and sets the page title from the seeded RNG (no console errors).

### P17-R03 — Seeded RNG ported  · MUST
`core/math/rng.py` gives the same numbers as `src/core/math/rng.ts` (mulberry32), so generated content matches the TypeScript game for the same seed.

**Acceptance criteria**
- [ ] Given seeds 0, 1, 42, 123456789, 4294967295, -5 and 2147483648, when 1000 values are drawn from each, then they equal the TypeScript values exactly (0 mismatches over 7000 values; the check is recorded in the report).
- [ ] `random_in` and `pick` behave as in the TypeScript (`pick` raises on an empty list).
- [ ] The module uses no `random`, `time` or `datetime` (ENG-18).

### P17-R04 — Core purity is enforced  · MUST
The layering rule of ENG-11 is checked, not just written down.

**Acceptance criteria**
- [ ] Given a file in `src/core/` that imports `org` or `browser`, when `make lint` runs, then it fails (checked with a probe file, then removed).
- [ ] The one exception (`core.math.rng` → `__pragma__` from the Transcrypt stub) is listed in `pyproject.toml` and nowhere else.

## 🧑 Tunable values
| Name | Value | Notes |
|------|-------|-------|
| Seed for the title | 42 | Only a smoke-test value, replaced by the real title screen later |

## 🧑 Out of scope for this phase
- Porting any other module (the rest of `core/`, `render/`, `app/`, `game/`, `ui/`, …). Each comes in its own phase.
- Babylon.js vendoring (`make vendor`) and the render layer. Babylon is needed from the render phase.
- Unit tests (pytest) and coverage: the owner asked for code only. ENG-27..29 and ENG-40..48 wait for the test phase.
- E2E, CI and deployment workflows (`.github/workflows/`), README and `docs/architecture.md`. They are updated in the phase that makes them work.
- Removing the TypeScript code from the branch (done when the port reaches parity).

## 🧑 Engineering additions for this phase
- The page shell is `index.html` at the root; the TypeScript shell is in git history on `main`.

## 🧑 Manual validation checklist
- [ ] `make install && make build` completes on a clean clone.
- [ ] `make dev`, then open `http://localhost:5173`: the title reads `Stratoblaster 60`, with no console errors.
- [ ] `make lint` and `make typecheck` pass.

## 🧑 Notes, references, sketches
- Transcrypt constraints measured on this phase: `DECISIONS.md` D-170 and `01-engineering.md` §13.
- Reference implementation: `src/core/math/rng.ts` on `main`.

---

## 🧑 Review feedback
> After the agent reports, write corrections here, then say **"Fix phase 17"**.
> The agent ticks each item when fixed.

- [ ] 

---

## 🤖 Implementation report
> Filled by the agent. Do not edit (comment in Review feedback instead).

### Questions / blockers
- None. The owner authorized the spec changes and the port start.

### Plan
| Task | Requirement IDs |
|------|-----------------|
| Spec rewrite for Python + Transcrypt + uv (01-engineering, D-169..171) | ENG-01..05, 12..36, 40..61, 82..84, §13 |
| uv project (`pyproject.toml`, `uv.lock`, `.python-version`) | P17-R01 |
| Makefile for Python, Transcrypt build, `index.html` shell | P17-R02 |
| Port `core/math/rng.ts` → `core/math/rng.py`, parity check | P17-R03 |
| import-linter contract for core purity, probed | P17-R04 |

### Requirement traceability
| ID | Status (Done / Partial / Not done) | Code | Tests | Notes |
|----|-----------------------------------|------|-------|-------|
| P17-R01 | Done | `pyproject.toml`, `uv.lock`, `.python-version`, `Makefile` | none (tests deferred) | `make install` uses `uv sync --locked` |
| P17-R02 | Done | `Makefile` (`build`), `index.html`, `src/main.py` | none (tests deferred) | Node run of `dist/js/main.js` prints `Stratoblaster 60` |
| P17-R03 | Done | `src/core/math/rng.py` | parity script, not committed (tests deferred) | 7000 values, 0 mismatches |
| P17-R04 | Done | `pyproject.toml` (`[tool.importlinter]`) | probe checked | the only exception is the `__pragma__` import |

### Gate results
```
make lint        ruff check ✔ / ruff format --check ✔ / lint-imports ✔ (1 contract kept)
make typecheck   mypy --strict ✔ (4 source files)
make build       Transcrypt ✔ / pragma leak check ✔
tests            not run (deferred by the owner)
coverage         not measured (deferred)
e2e              not run (deferred)
```

### How to test manually
1. `make install && make build`
2. `make dev`, open `http://localhost:5173`: the page reads "Python port in progress" and the title reads `Stratoblaster 60`.
3. Check the console is empty.

### Deviations from spec
- ENG-84 (cache busting) and ENG-103..112 were not touched; they are later phases.
- The Makefile has no `test`, `coverage` or `e2e` target yet (ENG-27..30 deferred).
- Git hooks: Husky (npm) is replaced by the `pre-commit` tool (ENG-60): `ruff format` and `ruff check --fix` on staged files, `make typecheck` on commit, `make check-fast` on push. `.husky/` is removed. The TypeScript toolchain files (`package.json`, `vite.config.ts`, `eslint.config.mjs`, ...) stay until parity.
- `ruff` runs on `src/` only; the TypeScript files on `main` are not checked by the Python gates.
- Recorded in `DECISIONS.md`: D-169 (the port), D-170 (Transcrypt constraints), D-171 (build, lint exception).

### Known limitations
- The game does not run on this branch. The page is a shell.
- Only `core/math/rng` is ported. The Babylon layer, the app and the game content are not.
- `ruff format` and mypy pass, but the Transcrypt output is not minified (`-n`).

### Suggestions for future phases
- Port `core/math` next (`min-heap`, `noise`, `color`), each with a comparison against the TypeScript output, as done for the RNG.
- Add a `make vendor` target that fetches the pinned Babylon.js build and checks its SHA-256 (ENG-02).
- Restore the test gate with pytest, using the TypeScript suite as the reference.
