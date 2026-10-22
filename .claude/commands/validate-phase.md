---
description: Mark a phase as validated and merge it (e.g. /validate-phase 3)
argument-hint: <phase number>
---

The user has validated phase **$ARGUMENTS** (NN = $ARGUMENTS zero-padded to two digits).

Follow the **"Phase N validated"** procedure in `CLAUDE.md`:
- Check that every item in the phase's "Review feedback" section is ticked. If any are open, list them and ask before continuing.
- Run `make check` one last time.
- Set the phase to ✅ Validated in `specs/PROGRESS.md` with today's date and the coverage figure, and add a line to the Log.
- Merge (or push / open a PR) using the git workflow in `specs/01-engineering.md` (ENG-70–74). Tag the release if ENG-74 says so.
