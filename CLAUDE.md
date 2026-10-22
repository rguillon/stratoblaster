# CLAUDE.md — Agent operating instructions

This project is built with **specification-driven development**.
The specs in `specs/` are the single source of truth. Code follows specs, never the other way around.

## Spec map

| File | Purpose | Who edits |
|------|---------|-----------|
| `specs/00-vision.md` | What the game is, scope, non-goals | Human |
| `specs/01-engineering.md` | Code, tooling, Makefile, CI, tests, coverage, deployment | Human |
| `specs/02-game-design.md` | Game-wide rules that apply across all phases (controls, look & feel, audio, balance) | Human |
| `specs/phases/phase-NN-*.md` | Requirements for one phase | Human writes requirements; agent fills the "Implementation report" section |
| `specs/PROGRESS.md` | Phase status board | Agent updates, human validates |
| `specs/DECISIONS.md` | Log of technical decisions made by the agent | Agent appends, human may veto |

## Slash commands

`/implement-phase N`, `/fix-phase N`, `/validate-phase N` and `/new-phase N name` (in `.claude/commands/`) are shortcuts for the procedures below.

## Command: "Implement phase N"

When the user says **"Implement phase N"**:

1. **Read** `00-vision.md`, `01-engineering.md`, `02-game-design.md`, `PROGRESS.md`, `DECISIONS.md`, and the phase file `specs/phases/phase-NN-*.md`. Skim previous phase files for context.
2. **Check preconditions**:
   - All previous phases are `✅ Validated` in `PROGRESS.md` (otherwise stop and ask).
   - The phase file has status `Ready`. If it is `Draft`, stop and ask.
   - If any requirement is ambiguous, contradictory, or conflicts with an earlier spec, **list the questions and stop** before writing code. Do not guess on MUST requirements.
3. **Plan**: write a short plan (tasks mapped to requirement IDs) in the phase file's "Implementation report" section.
4. **Implement** with tests first (TDD) where the engineering spec requires it. Every requirement ID must be traceable to code and/or tests (mention the ID in test names or comments, e.g. `it("P3-R02: enemy dies after 3 hits")`).
5. **Verify**: run `make check` (or whatever full-gate target `01-engineering.md` defines). All gates must pass: lint, type-check, unit tests, coverage threshold, build. Never lower thresholds or skip tests to make the gate pass.
6. **Report**: fill the phase file "Implementation report" (what was done per requirement, deviations, how to test manually, known limitations). Append any non-trivial technical choice to `DECISIONS.md`.
7. **Update** `PROGRESS.md`: set phase to `🟡 Awaiting review`.
8. **Commit** on a branch `phase-NN` following the commit conventions in `01-engineering.md`. Do not merge or push unless the engineering spec says so.
9. **Stop.** Do not start the next phase.

## Command: "Fix phase N" / review feedback

When the user says **"Fix phase N"** (or adds items under "Review feedback" in the phase file):

1. Read the "Review feedback" section of the phase file.
2. Address each unchecked item, tick it, and note the fix in the report.
3. Re-run the full gate, update the report, keep status `🟡 Awaiting review`.

## Command: "Phase N validated"

Set the phase to `✅ Validated` in `PROGRESS.md` with the date, merge/push per `01-engineering.md`.

## Rules

- Do **only** what the current phase asks. Do not implement future-phase requirements, even if easy. Note ideas in the report under "Suggestions".
- Requirements marked `MUST` are mandatory; `SHOULD` are expected unless there is a documented reason; `MAY` are optional.
- If a spec is changed after a phase was validated, treat it as a regression requirement in the next phase, not as a reason to silently rewrite old code.
- Never edit the requirement sections of spec files. Only the agent-owned sections.
- Never bypass git hooks (`--no-verify`) or weaken lint/coverage config to get a green gate (ENG-64).
- Respect the layering in `01-engineering.md` §2: `core/` stays pure (no Babylon, no DOM).
- Respect the engine / game split in `01-engineering.md` §2.3: code outside `src/game/` stays game-agnostic (abstractions only). Concrete content (bosses, enemies, levels, game tunables) goes in `src/game/`.
