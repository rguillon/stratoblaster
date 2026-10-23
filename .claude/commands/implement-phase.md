---
description: Implement a spec phase (e.g. /implement-phase 3)
argument-hint: <phase number>
---

Implement phase **$ARGUMENTS**.

The phase file is `specs/phases/phase-NN-*.md`, where NN is $ARGUMENTS zero-padded to two digits (3 → `03`).
If $ARGUMENTS is empty or not a number, or no matching file exists, stop and ask.

Follow the **"Implement phase N"** procedure in `CLAUDE.md` exactly. Key points:
- Check that all earlier phases are ✅ Validated in `specs/PROGRESS.md` and that this phase's status is `Ready`.
- If any requirement is ambiguous, list your questions in the report's "Questions / blockers" section and **stop**.
- Write unit tests with the code and put requirement IDs in test names, but do **not** run lint, unit tests or coverage: run only `make typecheck build e2e`. The full `make check` runs in `/validate-phase`.
- Fill the 🤖 Implementation report, log decisions in `specs/DECISIONS.md`, set the phase to 🟡 Awaiting review, and commit on branch `phase-NN`.
- Do not start the next phase.

End with a short summary: the requirement status table, the light verification results (noting that lint, unit tests and coverage are deferred to `/validate-phase`) and the manual test steps.
