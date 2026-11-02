# Decisions log

> Agent appends an entry for every non-trivial technical choice not dictated by the specs
> (library choice, architecture pattern, deviation from a SHOULD, etc.).
> Human may veto by changing the status to `Rejected` and explaining why.
>
> D-001 to D-233 are in [`../specs_old/DECISIONS.md`](../specs_old/DECISIONS.md). Each of them is now
> held by a requirement, or marked superseded or obsolete: see
> [`TRACEABILITY.md`](TRACEABILITY.md) §2. Numbering continues from D-234. A decision that changes
> what the game does or how it is built is also written into the requirement it concerns (a new one,
> or an existing one updated), so the specs stay the single source of truth.

## Template

### D-NNN — <title>
- **Date:** YYYY-MM-DD
- **Requirements:** the requirement IDs it adds or changes
- **Context:** why a decision was needed
- **Decision:** what was chosen
- **Alternatives considered:**
- **Consequences:**
- **Status:** Accepted / Rejected / Superseded by D-xxx

---

<!-- Entries below -->

### D-234 — Specs organised by function, with new requirement IDs traced in the code
- **Date:** 2026-11-01
- **Requirements:** every file under `specs/` (see [README](README.md)).
- **Context:** owner request: the phase files had become a history of changes, with later phases,
  review feedback and 233 decisions amending earlier requirements. Finding what an enemy, a boss or
  a level must look like and do meant reading several phases and the log.
- **Decision:**
  - The old `specs/` moved, unchanged, to `specs_old/`. The new specs have one file per feature,
    enemy kind, boss and level, in `gameplay/`, `ui/`, `audio/`, `graphics/`, `enemies/`,
    `bosses/` (`common.md`, `mini/`, `final/`), `worlds/world-N/` (`world.md` and one file per
    level) and `dev/`, plus `01-engineering.md` and `performance.md`.
  - Requirement IDs are `<file prefix>-NN` (`ENM-GNAT-04`, `LVL-2-3-05`, `BOSS-12`). `ENG` keeps its
    numbers. The old `GD-xx` and `Pxx-Ryy` IDs are retired; `TRACEABILITY.md` maps each one, and each
    old decision, to the new IDs.
  - The requirements describe the game as it is today: the old text, every later amendment (review
    feedback, decisions), and the current code for numbers. Where the code and the latest request
    disagree with nothing to explain it, the requirement keeps the request and says
    `**Discrepancy:**`; where nothing implements it, it says so.
  - Implementation choices in the old decisions became general requirements (mostly `ENG`,
    `PERF`), not one requirement per decision (owner's choice).
  - The code and tests were re-tagged to the new IDs (owner's choice): comments, docstrings and test
    names name the new IDs; decision references (`D-xxx`) stay as history.
- **Alternatives considered:** keeping the old IDs in the code with a mapping table only (smaller
  change, but two ID schemes to read side by side); one requirement per decision (owner: no).
- **Consequences:** `CLAUDE.md`, `.claude/commands/`, `specs_old/phases/_TEMPLATE.md` and
  `specs_old/PROGRESS.md` still describe the phase-by-phase workflow; adapting them is left to the
  owner (owner's choice: specs only).
- **Status:** Accepted

### D-235 — Ruff `ALL` without inline `# noqa`: Transcrypt's constraints in `pyproject.toml`
- **Date:** 2026-11-01
- **Requirements:** ENG-12, ENG-14, ENG-15, ENG-151, ENG-153, ENG-157, ENG-159, ENG-161.
- **Context:** owner request: Ruff now selects `ALL` rules, `make check` must pass, and the code must
  carry no `# noqa` (there were about 1,700, most of them asked for by ENG-14, ENG-153 and ENG-161).
- **Decision:**
  - The rules Transcrypt makes impossible to follow are ignored in `pyproject.toml`, each with its
    reason (owner's choice): `E711` (ENG-161), `FBT001`-`FBT003`, `PLR0913` and `PLR0917` (ENG-151),
    `SIM118` (ENG-159), `SIM110` and `PLR1730` (ENG-157), `PLW0108`, `SIM105`, `E722`; per file, the
    camelCase names of Babylon, the DOM and the config records (`N802`, `N803`, `N815`, ENG-15) and
    `ARG001` in the modules whose arguments are read by `__pragma__("js", ...)` code.
  - The module-level skip blocks became comment-form pragmas after the runtime imports (owner's
    choice), so no import follows a statement (`E402`):
    `# isort: split`, `# __pragma__ ("skip")`, the typing imports and aliases, `# __pragma__
    ("noskip")`. Transcrypt reads `# __pragma__ (...)` comments as pragmas (`pragmasFromComments` in
    its compiler); `# isort: split` keeps the sorted runtime imports out of the block, and
    `__pragma__` is a Ruff `task-tags` entry so the comments are not commented-out code (`ERA001`).
    The first import of the block must be the first one in isort order, so the skip comment stays
    above it.
  - Generic functions use PEP 695 type parameters (`UP047`): Transcrypt (run under Python 3.12)
    compiles them and drops the annotations.
  - Every Python file starts with `# Copyright (c) 2026 Renaud Guillon` (`CPY001`, owner's choice).
  - Docstring summaries are one imperative line (`D401`, `D205`); the summaries an earlier autofix
    had cut mid-sentence were rewritten.
  - deptry ignores `DEP001` for `org`, Transcrypt's compile-time stub package.
- **Alternatives considered:** keeping inline `# noqa` with reasons (owner: no); refactoring away
  positional flags and long argument lists (a large refactor against ENG-151); a global `E402`
  ignore (owner: restructure the skip blocks instead).
- **Consequences:** the ENG-14, ENG-15, ENG-151, ENG-153, ENG-157 and ENG-161 texts still mention
  `# noqa` comments; updating them is left to the owner (requirement sections).
- **Status:** Proposed

### D-236 — 100 % unit coverage: unreachable code is removed, never excluded
- **Date:** 2026-11-02
- **Requirements:** ENG-43 (changed), ENG-29, ENG-45, ENG-75, ENG-76, ENG-145, ENG-146 (texts updated).
- **Context:** the owner raised `fail_under` from 70 to 100 % and dropped the per-package gates and
  the HTML report. The unit tests were then completed (89.8 % → 99.87 %); the last 63 lines and
  branches could not be reached by any honest test: defensive guards that earlier code makes
  impossible, a cache read only JavaScript performs, a mypy-only `raise`.
- **Decision:** reach 100 % by tests, and remove or restructure the code no input can reach (owner's
  choice, over `# pragma: no cover` or tests that feed private functions impossible inputs):
  - Dead guards are deleted after checking they are dead in the browser too (`undefined`, NaN, an
    empty list being truthy). One was not: `traffic.py` stops NaN on a zero-length road, so that
    check moved to where cars are added (a road with no length gets none), with its test.
  - Guards that only narrowed a type for mypy are replaced by code whose types carry the invariant
    (`cast` does not exist at run time under Transcrypt): kinds looked up in a dict by id
    (`boss_fights.py`, `level_run.py`, validated by their constructors), `draws.weighted_pick` for
    lists that are never empty, `music_player._start` returning what it made,
    `menu_flow._leave_completed_level` taking its result.
  - A value only JavaScript sets is read through a small `__pragma__("js")` helper the tests can
    patch (`ship_materials._cached_materials`, ENG-158).
  - Functions no code calls are deleted with their tests.
- **Alternatives considered:** `# pragma: no cover` with a reason on each line (weakens the gate,
  CLAUDE.md); covering guards by calling private functions with inputs the callers never produce
  (tests of impossible states); a threshold under 100 %.
- **Consequences:** every line and branch of `src/` is run by a unit test, so any new unreachable
  code fails `make tests`. CPython-only gaps (a JavaScript-only helper whose Python body is a
  placeholder) are covered by tests that call the placeholder and say so.
- **Status:** Proposed

### D-237 — `src/` holds only code the game runs; what only tests call lives in `tests/`
- **Date:** 2026-11-02
- **Requirements:** GAME-SHIP-08, GAME-WPN-19, BOSS-38, GFX-ROAD-21 (discrepancies noted), BOSS-21,
  ENG-145, ENG-49.
- **Context:** with coverage at 100 % (D-236), a scan of `src/` (no import, call, attribute read or
  JavaScript string names it) found about 60 functions, classes and methods that only tests used:
  engine checks nothing ran (`validate_weapons`, `validate_player_ship_roster`, ...), measuring
  tools (`in_family`, `pattern_signature`), a fake (`MemoryStorage`), accessors for tests
  (`EnemyLayer.count`, `SceneryStage.has_sea`, ...), the first props viewer's `SceneryStage`
  methods (D-199), unused Babylon wrappers and typing Protocols, and `config/shot_viewer.py`.
- **Decision:** the owner asked to take them out of `src/`:
  - Code whose only subject was itself is deleted with its tests.
  - Tools tests use to check other code or the game's data move into test code:
    `tests/helpers/color_families.py` (`in_family`), `tests/helpers/memory_storage.py`
    (`MemoryStorage`), and the test files that use them (`_check_roster`, `_check_weapons` in
    `test_player_build.py`, `_pattern_signature` in `test_boss_parts_and_stages.py`).
  - Accessors are deleted; tests read the state directly.
  - `ship_parts.tag_part` went too: its tag was read only by a test-only reader.
  - Every requirement ID keeps a test named after it (ENG-42).
- **Alternatives considered:** wiring the unused engine checks into the game (a change of
  behaviour, not a clean-up); keeping test-only code in `src/` (it counts as product code and must
  stay covered).
- **Consequences:** the engine refuses no bad roster or weapon data at run time (it never did; the
  game's data is checked by unit tests). BOSS-38's health rule is applied by hand in the configs. A
  stage cannot be re-seeded. The scan cannot tell methods apart when other classes share their name
  (`count`, `clear`, ...): those were checked by hand where flagged.
- **Status:** Proposed
