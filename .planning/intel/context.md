# Context intel

Topic-keyed notes with source attribution. DOCs in this ingest set: `specs/PROGRESS.md`, `specs/README.md`, `specs/phases/_TEMPLATE.md` (skipped, see below). `docs/architecture.md` was excluded from the ingest set by the manifest (ENG-131/ENG-147 back-reference); its content is covered by `/home/renaud/pewet/.planning/codebase/ARCHITECTURE.md`.

## Topic: Phase status board (all phases complete)

- source: specs/PROGRESS.md
- note: Statuses legend: not started / in progress / awaiting review / changes requested / Validated. All 12 phases are Validated (marked complete) as of 2026-10-27. Phase 0 (project scaffold: tooling, Makefile, hooks, CI, deploy; 2026-10-22) is logged but not on the board.

Phase | Spec file | Status | Branch | Coverage (lines) | Validated on
1 | phases/phase-01-main-menu.md | Validated | phase-01 | 99.61 % | 2026-10-23
2 | phases/phase-02-player-ships.md | Validated | phase-02 | 99.51 % | 2026-10-22
3 | phases/phase-03-player-shots.md | Validated | phase-03 | 99.45 % | 2026-10-23
4 | phases/phase-04-level-zero.md | Validated | phase-04 | 99.35 % | 2026-10-23
5 | phases/phase-05-first-enemies.md | Validated | phase-05 | 99.27 % | 2026-10-24
6 | phases/phase-06-world-1.md | Validated | phase-06 | 99.33 % | 2026-10-25
7 | phases/phase-07-bosses.md | Validated | phase-07 | 99.34 % | 2026-10-25
8 | phases/phase-08-world-2.md | Validated | phase-08 | 99.26 % | 2026-10-25
9 | phases/phase-09-world-3.md | Validated | phase-09 | 99.35 % | 2026-10-26
10 | phases/phase-10-world-4.md | Validated | phase-10 | 99.42 % | 2026-10-26
11 | phases/phase-11-score-lives-bombs.md | Validated | phase-11 | 99.42 % | 2026-10-26
12 | phases/phase-12-pause-music-settings.md | Validated | phase-12 | 99.4 % | 2026-10-27

## Topic: Phase validation log highlights

- source: specs/PROGRESS.md
- note: Phase 2 was implemented before phase 1 (phase 2 has no dependency). Squash-merge tags v0.NN.0 per phase (v0.01.0 .. v0.12.0). Gate results from the log: phase 2 100 unit tests, 3 e2e; phase 1 228 unit / 23 e2e; phase 3 314 / 27; phase 4 545 / 35; phase 5 668 / 40; phase 6 789 / 50; phase 7 939 / 54; phase 8 1084 / 65; phase 9 1210 / 77; phase 10 1384 / 88; phase 11 1432 / 95 e2e. Phase 12 validated 2026-10-27 by the reviewer without re-running make check (PR #23, tag v0.12.0 on 6da41c0; coverage from the latest full gate: 1591 unit tests, 99.4 % lines, 87.87 % branches, 117 e2e).
- note: Post-validation reviewer-requested reworks (logged 2026-10-26/27): World 1 gradient (phase 6, D-109, full gate not run at that time), World 2 Industrial Desert (phase 8, D-110, full gate green: 1573 unit tests, 99.41 % lines, 117 e2e), World 3 (phase 9, D-111, 1580 unit tests, 99.41 %), World 4 Metropolis (phase 10, D-112, 1591 unit tests, 99.4 %). Each log line ends "awaiting the reviewer's check"; no later entry records that check. Other infrastructure entries: e2e tests step the game (D-093), faster hooks (D-094), CI e2e in a single job (D-018 amended).

## Topic: Project identity

- source: specs/DECISIONS.md (D-016); specs/PROGRESS.md
- note: The game is named Stratoblaster (D-016); the game id is the cookie prefix. Git history, existing tags and the local folder name keep the earlier working name (D-016). 100 % client-side browser shoot 'em up, deployed to GitHub Pages (ENG-80..ENG-85).

## Topic: Spec-driven process

- source: specs/README.md
- note: Write specs once in order: 00-vision.md, 01-engineering.md, 02-game-design.md (can be filled progressively). Then per phase run `/new-phase N short-name` (or copy phases/_TEMPLATE.md to phases/phase-NN-name.md), fill requirements, set Status: Ready. Tip: make phase 1 a technical skeleton (Makefile, CI, empty canvas deployed to GitHub Pages) so engineering requirements are validated before gameplay (not how this project went: phase 0 scaffold was done outside the board).
- note: Loop: `/implement-phase N` reads specs, asks questions if ambiguous, plans, does TDD, `make check`, fills the report, sets status awaiting-review and stops; reviewer writes items in "Review feedback" then `/fix-phase N`; `/validate-phase N` marks Validated and merges per git rules. Plain-English versions work too. Full agent rules are in /CLAUDE.md; slash commands live in /.claude/commands/. Note: README says `make check` runs in implement/fix, while CLAUDE.md (outside this set) says light verification (typecheck, build, e2e) there and the full gate only at validation.

## Topic: Phase template (skipped)

- source: specs/phases/_TEMPLATE.md
- note: Empty copy-and-fill template with placeholder sections (goal, requirements PNN-Rxx, tunable values, out of scope, engineering additions, manual validation checklist, review feedback, implementation report). No concrete content extracted by design.

## Topic: World journey (current shipped design)

- source: specs/DECISIONS.md (D-109..D-112); specs/phases/phase-06-world-1.md .. phase-10-world-4.md
- note: The four worlds are now one continuous journey, each level starting on the section the previous ended on: World 1 sea to green grass to desert (levels about 4 min, times of day midday to dusk); World 2 Industrial Desert, desert to factories (5 min levels, morning, midday, afternoon, dusk, night); World 3 factories to garden villages (rain, storm, lightning kept); World 4 Metropolis, houses to skyscrapers (ash and embers kept). Bosses and wave scripts of Worlds 2-4 keep their original frost, jungle and volcanic themes and now fly over the reworked scenery. Level grid is 4 x 5 = 20 levels, all unlocked (D-089). The Caldera Throne (4-5 final) is the last boss.

## Topic: Visual and audio direction (current)

- source: specs/02-game-design.md (GD-60); specs/DECISIONS.md (D-099..D-101, D-103)
- note: Darksynth: dark, neon magenta/violet/blood red, sunset gradients, chrome; menus and HUD restyled (D-103); music is code-generated synthwave/darksynth with per-world styles and stressful boss tracks; the menu backdrop shows the balanced ship over a recoloured night city with no sun emblem (D-104).

## Topic: Engine versus game split

- source: specs/01-engineering.md; specs/DECISIONS.md
- note: Everything outside src/game/ is a game-agnostic engine; unused-but-kept engine tools after the world reworks: snow, aurora, frozen ground tools (D-110), jungle set pieces and water tools (D-111), lava, volcanic props and plumes (D-112).

## Topic: Codebase map pointer

- source: /home/renaud/pewet/.planning/codebase/*.md (derived, not locked decisions)
- note: ARCHITECTURE, CONCERNS, CONVENTIONS, INTEGRATIONS, STACK, STRUCTURE, TESTING exist from an earlier mapping run and were not consumed as authoritative inputs.
