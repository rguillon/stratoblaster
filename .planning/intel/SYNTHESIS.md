# Ingest synthesis (entry point for gsd-roadmapper)

Mode: new. Precedence: ADR > SPEC > PRD > DOC. Manifest: /home/renaud/pewet/.planning/ingest-manifest.yaml (all 19 classifications carry manifest_override, types authoritative). Excluded from the set: docs/architecture.md (ENG-131 / ENG-147 back-reference; covered by /home/renaud/pewet/.planning/codebase/ARCHITECTURE.md).

## Status

STATUS: AWAITING USER. 0 blockers, 14 warnings, 16 info. The warnings are stale-text confirmations ("later decisions win"), no competing PRD variants and no locked-decision contradictions. Details: /home/renaud/pewet/.planning/INGEST-CONFLICTS.md

## Doc counts by type (19)

- PRD: 1 (specs/00-vision.md)
- SPEC: 14 (specs/01-engineering.md, specs/02-game-design.md, phase-01 .. phase-12)
- ADR: 1 (specs/DECISIONS.md, 112 decisions)
- DOC: 3 (specs/PROGRESS.md, specs/README.md, specs/phases/_TEMPLATE.md which is an empty template and was skipped)
- Cycles: none. UNKNOWN or low-confidence blockers: none.

## What the project is

A 100 % client-side browser vertical shoot 'em up, named Stratoblaster (D-016), built with TypeScript strict + Babylon.js + Vite, tested with Vitest and Playwright, deployed to GitHub Pages; darksynth look, all models, music and SFX generated in code. First release scope: 4 worlds x 5 levels (World 5 dropped, D-089). Engine outside src/game/ is game-agnostic (ENG-140..ENG-148).

## Phase status (all complete)

All 12 phases are Validated per specs/PROGRESS.md; roadmapper should mark them complete. Phase 0 (project scaffold: tooling, Makefile, hooks, CI, deploy, 2026-10-22) is logged only, not on the board.

- Phase 1 Main menu: Validated 2026-10-23, branch phase-01, 99.61 % lines
- Phase 2 Player ships: Validated 2026-10-22, phase-02, 99.51 %
- Phase 3 Player shots: Validated 2026-10-23, phase-03, 99.45 %
- Phase 4 Level Zero: Validated 2026-10-23, phase-04, 99.35 %
- Phase 5 First enemies: Validated 2026-10-24, phase-05, 99.27 %
- Phase 6 World 1: Validated 2026-10-25, phase-06, 99.33 %
- Phase 7 Bosses: Validated 2026-10-25, phase-07, 99.34 %
- Phase 8 World 2: Validated 2026-10-25, phase-08, 99.26 %
- Phase 9 World 3: Validated 2026-10-26, phase-09, 99.35 %
- Phase 10 World 4: Validated 2026-10-26, phase-10, 99.42 %
- Phase 11 Score, lives and bombs: Validated 2026-10-26, phase-11, 99.42 %
- Phase 12 Pause, music and settings: Validated 2026-10-27, phase-12, 99.4 % (reviewer validated without re-running make check; latest full gate 1591 unit tests, 99.4 % lines, 87.87 % branches, 117 e2e)

Caveat (warning in the report): the post-validation reworks of phases 6, 8, 9, 10 (D-109..D-112) are logged "awaiting the reviewer's check". Dependencies: P02 none; P01 after P02; P03 after P02; P04 after P03; each later phase after the previous one.

## Intel files

- /home/renaud/pewet/.planning/intel/decisions.md : 112 decisions D-001..D-112; 111 accepted (D-040 "partly supersedes D-013", D-091 "reviewer approved the spec" included), 1 reverted (D-104); 0 locked. Several accepted entries are superseded in effect by later ones (listed in the conflicts report).
- /home/renaud/pewet/.planning/intel/requirements.md : 163 requirements. Vision 6 (REQ-vision-_), GD 27 (REQ-GD-_), phase requirements 130: P01 15, P02 3, P03 5 (R01, R02, R03, R10, R11), P04 7, P05 24, P06 10, P07 10, P08 12, P09 11, P10 13, P11 8, P12 12. IDs verbatim. Phase and GD requirements come from SPEC-typed docs but are behaviour requirements, so they are listed here rather than in constraints.md.
- /home/renaud/pewet/.planning/intel/constraints.md : 18 constraint groups (nfr 7, protocol 8, schema 1, api-contract 2): ENG-01..ENG-148 (ENG-62 removed, no ENG-102), controls, cookie schema, test API and debug endpoints, phase tunables.
- /home/renaud/pewet/.planning/intel/context.md : 9 topics: phase board and log, project identity, spec-driven process (README), template (skipped), world journey, visual and audio direction, engine/game split, codebase-map pointer.

## Conflict summary

- Blockers: 0
- Competing variants: 0
- Warnings (stale text in human-owned specs where decisions or later phases win): 14, notably ENG-07 vs D-010, ENG-12 vs D-019, P02 speed 100 vs D-047 (225), GD bomb key E vs D-043 / P11-R06, P06 tunables vs D-044 / D-051, P06-R02 weapon start vs D-071, world-rework leftovers in P08 / P09 / P10 / P12, "eleven kinds" vs P05-R24, DECISIONS statuses not updated, reworks awaiting reviewer check, gate wording (ENG-32 / README vs CLAUDE.md).
- Info (auto-resolved): 16.

## Guidance for the roadmapper

- Treat all twelve phases as delivered. Remaining work is whatever the user adds next; the first release scope (4 x 5 levels, score, bombs, pause, music, settings) is complete per the board.
- Where a decision (D-xxx) conflicts with spec text, the decision wins (recorded in the report). Do not generate tasks to "fix" stale spec text unless the user confirms.
- Unused-but-kept engine tools (snow, aurora, lava, frozen and jungle props) are intentional (D-110..D-112), not gaps.
- Not in scope of any phase: quality presets (ENG-102 removed), remapping, master volume, graphics settings (D-095), score across levels, name entry and leaderboards (P11 out of scope).
