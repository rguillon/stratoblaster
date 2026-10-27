## Conflict Detection Report

Scope: 19 classified docs under specs/ (manifest overrides authoritative). docs/architecture.md is outside the ingest set (references to it were not followed and form no cycle). Cycle detection: no cycle among in-set cross_refs (specs/01-engineering.md refers to "README.md", read as the repository-root README of ENG-130, not specs/README.md). No UNKNOWN or low-confidence blocker (manifest types are authoritative). No ADR entry is marked locked, so no LOCKED-vs-LOCKED contradiction is possible. No PRD pair defines the same scope with different acceptance criteria, so there are no competing variants.

### BLOCKERS (0)

None.

### WARNINGS (14)

[WARNING] ENG-07 says localStorage, but the vision, GD-51 and D-010 say cookies
Found: specs/01-engineering.md ENG-07 "Persistence (settings, high scores) uses localStorage"; specs/00-vision.md non-goals "any persistence shall be handled by cookies"; specs/02-game-design.md GD-51 "based on a cookie"; specs/DECISIONS.md D-010 (Accepted) follows the cookies and notes "ENG-07 could be updated to say cookies"; P01-R04, P01-R14, P11-R03 and P12-R04 all use cookies.
Impact: ENG-07 text is stale in a human-owned spec; a roadmap or plan built from ENG-07 would prescribe the wrong store.
→ Confirm cookies win (synthesized intel treats D-010 as authoritative) and update ENG-07 in specs/01-engineering.md.

[WARNING] ENG-12 names eslint-plugin-import, but D-019 replaced it with eslint-plugin-import-x and ESLint 10
Found: specs/01-engineering.md ENG-12 "ESLint (flat config) ... plus eslint-plugin-import"; specs/DECISIONS.md D-019 (Accepted) "Replace eslint-plugin-import with eslint-plugin-import-x ... ESLint to 10" and "the human owner is to update ENG-12"; D-002 still pins ESLint ^9.39 (its ESLint part is superseded by D-019).
Impact: ENG-12 and D-002 are stale; D-094 also turned off some import-x rules that TypeScript covers.
→ Confirm D-019 wins and update ENG-12.

[WARNING] Player base speed still reads 100 px/s in the phase 2 spec; the shipped value is 225 px/s
Found: specs/phases/phase-02-player-ships.md Goal "A base ship speed is 100px/s" (P02-R01..R03 factors 1 / 0.8 / 1.4); specs/DECISIONS.md D-044 (150) and D-047 (225: balanced 225, heavy 180, light 315), both say the phase 2 text "is the reviewer's to update".
Impact: phase 2 text understates the speed by 2.25x; speed factors themselves are unchanged and valid.
→ Confirm D-047 wins and update the phase 2 Goal (the factors stay).

[WARNING] GD section 2 gives E to Special/bomb; E is the weapon switch and bombs use R / Left Shift
Found: specs/02-game-design.md controls table "Special / bomb: E, button, button"; specs/DECISIONS.md D-043 (E = KeyE switches weapon) and D-091 / P11-R06 (bomb: KeyR, ShiftLeft, gamepad X and LB, touch BOMB; "the GD section 2 binding of E to the bomb is superseded by D-043"). Phase 11 notes say the reviewer may update the GD table.
Impact: the controls table in the global design spec contradicts shipped controls.
→ Confirm D-043 and P11-R06 win and update the GD section 2 table (bomb row, and add the weapon switch).

[WARNING] Phase 6 tunables understate the shipped enemy counts and on-screen peaks
Found: specs/phases/phase-06-world-1.md tunables "enemies_spawned ~60 / ~80 / ~100 / ~120 / ~140" and "peak_on_screen 6 / 8 / 10 / 12 / 15"; specs/DECISIONS.md D-044 (+50 % density) and D-051 (fillers): 279 / 335 / 433 / 498 / 537 enemies, peaks 16 / 20 / 24 / 30 / 32, "far above the spec's tunables".
Impact: P06-R08 orderings (strict increases, second half heavier) still hold; only the absolute numbers are stale. 1-1 may be busier than "easy for a kid" (D-044 asks for a manual check).
→ Confirm the decisions win and refresh the P06 tunables, or accept as historical.

[WARNING] Phase 6 says every level starts with the guns at level 1, but D-071 carries weapon levels across completed levels
Found: specs/phases/phase-06-world-1.md P06-R02 "starts every level with the guns at level 1", start_weapon tunable "guns, level 1", and a note "every level starts again at level 1"; specs/DECISIONS.md D-071 (Accepted): weapon and levels saved on Level complete under `<game id>_weapons` and each level starts from them (a game over saves nothing).
Impact: a plan following P06-R02 would drop persistent weapon levels.
→ Confirm D-071 wins and amend P06-R02 and its tunable.

[WARNING] Stale look and menu wording in phase 1 and phase 4
Found: specs/phases/phase-01-main-menu.md P01-R13 "a chrome logo over a striped sun" while D-103 / D-104 and the phase 12 review feedback removed the sun emblem; P01 tunable "worlds x levels_per_world 5 x 5" while P01-R07 and D-089 say 4 x 5; specs/phases/phase-04-level-zero.md Goal "Level zero is reachable from the main menu as the first level" while D-020 (reviewer accepted the defaults) says Level Zero is not in the level select and is reached through the level_zero/ page.
Impact: low; wording only, behaviour follows the decisions.
→ Confirm and fix the three phrases.

[WARNING] Worlds 2 to 4 reworks left old wording in the requirement sections
Found: specs/phases/phase-08-world-2.md still says "blizzard" and "aurora" in P08-R04 manual validation, P08-R05 acceptance (60 FPS in the 2-4 blizzard), the P08-R08 table (sea, fjords, tundra, blizzard), the Engineering additions and the P08-R10 boss looks (frost themed); specs/phases/phase-10-world-4.md P10-R05 (lava MUST), the P10-R09 table (sea, lava rivers, foundries) and P10-R13 acceptance (magma lake, eruption look); specs/phases/phase-12-pause-music-settings.md P12-R06 names World 2 "Frozen North", World 3 "Jungle", World 4 "Volcanic Lands". D-110, D-111, D-112 say the levels no longer use snow, aurora, lava, sea or jungle, while the engine tools and bosses stay.
Impact: some acceptance criteria cannot be met by any current level (for example 2-4 blizzard, 4-5 over a magma lake); a verifier could flag false failures.
→ Confirm the decisions win and mark those criteria and names as historical or amend them.

[WARNING] Phases 9 and 10 say "eleven phase 5 kinds"; phase 5 now adds ten more kinds to Worlds 3 and 4
Found: specs/phases/phase-09-world-3.md P09-R07 ("only uses the kinds listed ... 3-2 to 3-5 use all eleven") and specs/phases/phase-10-world-4.md P10-R09 ("uses all eleven kinds"); specs/phases/phase-05-first-enemies.md P05-R24 (added 2026-10-26, D-090: veteran kinds in Worlds 3 and 4, elites in World 4, 21 kinds). The phase 10 implementation report already says "P10-R09's eleven kinds now reads together with P05-R24".
Impact: strictly read, "only the eleven" tests contradict the 21-kind roster.
→ Confirm P05-R24 and D-090 win and add a note to P09-R07 and P10-R09.

[WARNING] Level select wording about greyed-out worlds and World 5 is stale in phases 8 and 9
Found: specs/phases/phase-08-world-2.md P08-R01 "Worlds 3 to 5 stay greyed out" and checklist "worlds 3 to 5 stay locked"; specs/phases/phase-09-world-3.md P09-R01 "Worlds 4 and 5 stay greyed out"; D-089 dropped World 5 and the grid is 4 x 5 with all 20 levels unlocked. P11 out-of-scope also cites "Phase 13" (sounds) and "Phase 14" (settings) that phase 12 delivered.
Impact: low; these are phase-time statements.
→ Confirm they are historical; optionally annotate.

[WARNING] Quality presets were removed but ENG-103, ENG-106 and phase 1 still refer to them
Found: specs/01-engineering.md has no ENG-102 (removed by the reviewer 2026-10-26 per D-095), yet ENG-103 "cascaded on High", ENG-106 "< 200 draw calls per frame on Medium"; specs/phases/phase-01-main-menu.md out-of-scope "quality presets (ENG-102)"; D-020 "Quality presets (ENG-102) do not exist yet".
Impact: dangling references to a removed requirement.
→ Confirm there are no presets (budgets apply to the single configuration) and tidy ENG-103 and ENG-106.

[WARNING] DECISIONS.md entries superseded in effect still read "Accepted"
Found: specs/DECISIONS.md D-014 (cyberpunk look; look superseded by D-103); D-013 (partly superseded by D-040 and by D-103); D-015 (laser 40/60/85/115/150 and missile 8 damage; superseded by D-059 / GD-33); D-038 (counts superseded by D-044, then D-051); D-044 (150 px/s; superseded by D-047); D-069 (look replaced by D-074); D-107 (booms replaced by D-108); D-041 ("Esc leaves" superseded by D-095 / D-096); D-068's sweepDeg (removed by D-073); D-064..D-066, D-076..D-079, D-082..D-086 describe the original World 2-4 looks that D-110..D-112 no longer use (engines kept). D-104 is correctly "Reverted".
Impact: a consumer reading statuses literally would treat superseded choices as live.
→ Synthesized intel keeps each status as written and annotates supersession; consider setting those entries to "Superseded by D-xxx" in specs/DECISIONS.md.

[WARNING] Post-validation world reworks are logged "awaiting the reviewer's check"
Found: specs/PROGRESS.md log: phase 6 World 1 rework (D-109, 2026-10-26 and 2026-10-27, full gate not run at that time), phase 8 (D-110), phase 9 (D-111), phase 10 (D-112) each end "awaiting the reviewer's check" with no later confirmation; phase 12 "Validated by the reviewer, without re-running make check for this phase". The board still shows all 12 phases Validated.
Impact: phases are complete per the board, but the rework acceptance and one full gate for phase 12 are not recorded. CLAUDE.md says a spec change after validation is a regression requirement for the next phase.
→ Mark phases 1-12 complete as the board says, and record that the reviewer's check of the four reworks is still to be confirmed.

[WARNING] Verification gate wording differs between the specs and CLAUDE.md
Found: specs/01-engineering.md ENG-32 "make check ... used by CI and by the agent before every report" and specs/README.md loop table (`make check` in implement and fix); /CLAUDE.md (outside the ingest set, project instructions) says implement and fix run only `make typecheck build e2e` and the full `make check` only at validation.
Impact: ambiguity about which gate a planned phase must run.
→ Confirm CLAUDE.md governs (later and operational) and align ENG-32 and the README table.

### INFO (16)

[INFO] Auto-resolved: speed D-047 over D-044 over phase 2
Note: base speed 100 (specs/phases/phase-02-player-ships.md) then 150 (D-044) then 225 px/s (D-047); ADR over SPEC and later over earlier. Synthesized intel uses 225 px/s (balanced 225, heavy 180, light 315). D-044 numbers for waves were in turn extended by D-051.

[INFO] Auto-resolved: bomb and weapon-switch keys
Note: D-043 (E switches weapon) and D-091 / P11-R06 (bomb on R, Left Shift, X, LB, BOMB button) win over the GD section 2 bomb row; the GD controls row is recorded as superseded in requirements.md.

[INFO] Auto-resolved: persistence store
Note: D-010 (cookies) wins over ENG-07 (localStorage); consistent with the vision, GD-51, P01, P11 and P12. Cookie keys: `<gameId>_high_score`, `_last_ship`, `_music_volume`, `_sfx_volume`, `_weapons`.

[INFO] Auto-resolved: lint plugin and ESLint version
Note: D-019 (eslint-plugin-import-x, ESLint 10) wins over ENG-12 and over the ESLint pin of D-002.

[INFO] Auto-resolved: Vite base path
Note: D-003 sets `base: './'` (relative) rather than deriving the base from the repository name (ENG-82); the outcome (works under any GitHub Pages sub-path) satisfies the intent. ADR over SPEC.

[INFO] Auto-resolved: generated audio over audio-file formats
Note: P12-R05 states ENG-120's audio formats (OGG/MP3) do not apply because all audio is generated with Web Audio (GD-70, GD-71, D-097). The scoping is explicit in the later spec; no files are loaded.

[INFO] Auto-resolved: Esc behaviour in the game screen
Note: P12-R01 and D-095 / D-096 supersede P01-R01 (game: Back/Esc to title), P06-R02, D-041 and the phase 11 out-of-scope note ("Esc still leaves"): Escape and P pause; Backspace and gamepad B do nothing in the game; leaving goes through the pause menu. Stated explicitly in the later requirement text, so no user action is needed.

[INFO] Auto-resolved: weapon balance numbers
Note: GD-33 and D-059 (laser 80/140/200/260/320 dps, missile damage 14) win over D-015 defaults; P03-R02 and P03-R03 already carry the new numbers with "was" notes.

[INFO] Auto-resolved: menu and HUD look
Note: D-103 (darksynth) supersedes the look of D-013 and D-014 (cyberpunk); D-040 removed the CRT overlay; D-104 (pilot model) is Reverted, only the sun emblem removal stays; GD-60, P01-R05, P01-R13 and P07-R02 were amended with dated notes.

[INFO] Auto-resolved: World 1-4 reworks over the original world designs
Note: D-109 (World 1 gradient), D-110 (Industrial Desert), D-111 (factories to garden villages), D-112 (Metropolis) override the original themes (Frozen North, Jungle, Volcanic Lands) in P06, P08, P09, P10 requirement text, which were amended with dated "Reworked" notes. Boss designs, wave scripts, rain/ash weather and the sky scripts are kept; snow, aurora, lava, frozen and jungle tools are kept but unused by levels.

[INFO] Auto-resolved: eleven versus 21 enemy kinds
Note: P05-R24 and D-090 (added after phase 10) win over the "eleven kinds" wording of P09-R07 and P10-R09; P05-R24 requires the difficulty rules P09-R08 and P10-R10 to be re-measured, which phase 10's report records.

[INFO] Auto-resolved: level grid and World 5
Note: D-089 (4 x 5 grid, 20 levels, all unlocked, Caldera Throne last boss) wins; the vision, P01-R07, P06-R01, P10-R01 and phase 8 notes were amended with dated notes. P06-R01 states levels are never locked by progress.

[INFO] Auto-resolved: Level Zero access
Note: D-020 (reviewer accepted the 11 proposed defaults) keeps Level Zero out of the level select, reachable through the level_zero/ page; P04 Goal wording is stale (see the phase 1 and 4 warning).

[INFO] Auto-resolved: P07-R06 changes P06-R03
Note: P07-R06 declares itself a regression requirement on phase 6: for World 1 the level ends when the final boss is destroyed (P06-R03's end-of-scroll rule is replaced). Later worlds follow the same rule.

[INFO] Auto-resolved: test API staging
Note: ENG-52 / ENG-54 were staged: D-003 deferred them, D-011 added the build-time `__GAME_TEST__` absence check, D-075 and D-093 added advance and step; P11-R08 and P12-R12 extend the API. No conflict with ENG-52.

[INFO] Auto-resolved: CI e2e job layout
Note: D-018 first sharded e2e (3 jobs) against ENG-72's single `e2e` job; amended 2026-10-27 to a single job, consistent with ENG-72.
