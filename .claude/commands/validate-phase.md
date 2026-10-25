---
description: Mark a phase as validated and merge it (e.g. /validate-phase 3)
argument-hint: <phase number>
---

The user has validated phase **$ARGUMENTS** (NN = $ARGUMENTS zero-padded to two digits).

Follow the **"Phase N validated"** procedure in `CLAUDE.md`:
- Check that every item in the phase's "Review feedback" section is ticked. If any are open, list them and ask before continuing.
- Run the full gate `make check` (lint, typecheck, unit tests, coverage, build, e2e). This is the first time lint, unit tests and coverage run for this phase. If anything fails, fix the cause on branch `phase-NN` (never lower thresholds, skip tests or weaken lint), commit, and re-run until it passes. Record the gate results in the phase report.
- Set the phase to ✅ Validated in `specs/PROGRESS.md` with today's date and the coverage figure, and add a line to the Log.
- Merge using the git workflow in `specs/01-engineering.md` (ENG-92–93: squash-merge `phase-NN` into `main`, push, tag `v0.NN.0`), **without leaving `phase-NN`**: never `git checkout` / `git switch` to `main`. Build the squash commit directly on `main` with git plumbing:
  ```bash
  git fetch origin
  # main must be up to date with origin/main, and phase-NN must contain it; otherwise stop and ask.
  git merge-base --is-ancestor origin/main main && git merge-base --is-ancestor main phase-NN
  SQUASH=$(git commit-tree "phase-NN^{tree}" -p main -m "Phase NN: <phase name>" -m "<summary>" -m "<attribution trailer>")
  git update-ref refs/heads/main "$SQUASH" "$(git rev-parse main)"   # fails if main moved meanwhile
  git push origin main
  git tag -a v0.NN.0 -m "Phase NN: <phase name>" "$SQUASH" && git push origin v0.NN.0
  git push origin phase-NN
  ```
  The working tree stays on `phase-NN` throughout (its tree is the same as the new `main`).
