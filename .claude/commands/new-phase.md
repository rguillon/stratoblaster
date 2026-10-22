---
description: Create a new phase spec file from the template (e.g. /new-phase 4 bosses)
argument-hint: <phase number> <short-name>
---

Arguments: `$ARGUMENTS`. The first word is the phase number, the rest is the short name.

1. Copy `specs/phases/_TEMPLATE.md` to `specs/phases/phase-NN-<short-name>.md` (NN zero-padded, short name in kebab-case). If the file already exists, stop.
2. In the new file, replace `NN` / `PNN` with the phase number and `<Title>` with the short name in Title Case. Leave Status as `Draft`.
3. Add a row for the phase to `specs/PROGRESS.md` (⚪ Not started) and to the roadmap table in `specs/00-vision.md` if it isn't there yet.
4. Don't write any requirements or code. Reply with the path of the new file.
