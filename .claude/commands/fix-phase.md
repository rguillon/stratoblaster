---
description: Apply review feedback for a phase (e.g. /fix-phase 3)
argument-hint: <phase number>
---

Fix phase **$ARGUMENTS** (file `specs/phases/phase-NN-*.md`, NN = $ARGUMENTS zero-padded to two digits).

Follow the **"Fix phase N"** procedure in `CLAUDE.md`:
- Address every unchecked item in the "🧑 Review feedback" section, and any `Rejected` entries for this phase in `specs/DECISIONS.md`.
- Tick each item once it's fixed and note the fix in the Implementation report.
- Re-run `make check`, update the gate results, keep the status 🟡 Awaiting review, and commit on branch `phase-NN`.

If an item is unclear or conflicts with the spec, ask instead of guessing. End with a list of the items fixed and the gate results.
