# How to use these specs

## 1. Write the specs (once)
1. `00-vision.md` — what the game is.
2. `01-engineering.md` — Makefile, CI, tests, coverage, GitHub Pages, git workflow.
3. `02-game-design.md` — global game rules (controls, style, scoring...). Can be filled progressively.

## 2. Write phases
For each phase: run `/new-phase N short-name` (or copy `phases/_TEMPLATE.md` → `phases/phase-NN-name.md` by hand), fill requirements, set **Status: Ready**.

Tip: make **Phase 1** a technical skeleton (Makefile, CI, empty canvas deployed to GitHub Pages) so all the engineering requirements are validated before any gameplay.

## 3. Loop
| You say | Agent does |
|---------|-----------|
| `/implement-phase N` | Reads specs → asks questions if ambiguous → plans → TDD → `make check` → fills report → status 🟡 → stops |
| *(you test, write items in "Review feedback")* `/fix-phase N` | Fixes each item → `make check` → updates report |
| `/validate-phase N` | Marks ✅, merges per git rules |

The plain-English versions ("Implement phase 3", ...) work too. Full agent rules are in `/CLAUDE.md`; the slash commands live in `/.claude/commands/`.
