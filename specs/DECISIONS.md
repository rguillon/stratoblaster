# Decisions log

> Agent appends an entry for every non-trivial technical choice not dictated by the specs
> (library choice, architecture pattern, deviation from a SHOULD, etc.).
> Human may veto by changing the status to `Rejected` and explaining why.
>
> D-001 to D-233 are in [`../specs_old/DECISIONS.md`](../specs_old/DECISIONS.md). Each of them is now
> held by a requirement, or marked superseded or obsolete: see
> [`TRACEABILITY.md`](TRACEABILITY.md) §2. Numbering continues from D-234. A decision that changes
> what the game does or how it is built is also written into the requirement it concerns (a new one,
> or an existing one updated), so the specs stay the single source of truth.

## Template

### D-NNN — <title>
- **Date:** YYYY-MM-DD
- **Requirements:** the requirement IDs it adds or changes
- **Context:** why a decision was needed
- **Decision:** what was chosen
- **Alternatives considered:**
- **Consequences:**
- **Status:** Accepted / Rejected / Superseded by D-xxx

---

<!-- Entries below -->

### D-234 — Specs organised by function, with new requirement IDs traced in the code
- **Date:** 2026-11-01
- **Requirements:** every file under `specs/` (see [README](README.md)).
- **Context:** owner request: the phase files had become a history of changes, with later phases,
  review feedback and 233 decisions amending earlier requirements. Finding what an enemy, a boss or
  a level must look like and do meant reading several phases and the log.
- **Decision:**
  - The old `specs/` moved, unchanged, to `specs_old/`. The new specs have one file per feature,
    enemy kind, boss and level, in `gameplay/`, `ui/`, `audio/`, `graphics/`, `enemies/`,
    `bosses/` (`common.md`, `mini/`, `final/`), `worlds/world-N/` (`world.md` and one file per
    level) and `dev/`, plus `01-engineering.md` and `performance.md`.
  - Requirement IDs are `<file prefix>-NN` (`ENM-GNAT-04`, `LVL-2-3-05`, `BOSS-12`). `ENG` keeps its
    numbers. The old `GD-xx` and `Pxx-Ryy` IDs are retired; `TRACEABILITY.md` maps each one, and each
    old decision, to the new IDs.
  - The requirements describe the game as it is today: the old text, every later amendment (review
    feedback, decisions), and the current code for numbers. Where the code and the latest request
    disagree with nothing to explain it, the requirement keeps the request and says
    `**Discrepancy:**`; where nothing implements it, it says so.
  - Implementation choices in the old decisions became general requirements (mostly `ENG`,
    `PERF`), not one requirement per decision (owner's choice).
  - The code and tests were re-tagged to the new IDs (owner's choice): comments, docstrings and test
    names name the new IDs; decision references (`D-xxx`) stay as history.
- **Alternatives considered:** keeping the old IDs in the code with a mapping table only (smaller
  change, but two ID schemes to read side by side); one requirement per decision (owner: no).
- **Consequences:** `CLAUDE.md`, `.claude/commands/`, `specs_old/phases/_TEMPLATE.md` and
  `specs_old/PROGRESS.md` still describe the phase-by-phase workflow; adapting them is left to the
  owner (owner's choice: specs only).
- **Status:** Accepted

### D-235 — Ruff `ALL` without inline `# noqa`: Transcrypt's constraints in `pyproject.toml`
- **Date:** 2026-11-01
- **Requirements:** ENG-12, ENG-14, ENG-15, ENG-151, ENG-153, ENG-157, ENG-159, ENG-161.
- **Context:** owner request: Ruff now selects `ALL` rules, `make check` must pass, and the code must
  carry no `# noqa` (there were about 1,700, most of them asked for by ENG-14, ENG-153 and ENG-161).
- **Decision:**
  - The rules Transcrypt makes impossible to follow are ignored in `pyproject.toml`, each with its
    reason (owner's choice): `E711` (ENG-161), `FBT001`-`FBT003`, `PLR0913` and `PLR0917` (ENG-151),
    `SIM118` (ENG-159), `SIM110` and `PLR1730` (ENG-157), `PLW0108`, `SIM105`, `E722`; per file, the
    camelCase names of Babylon, the DOM and the config records (`N802`, `N803`, `N815`, ENG-15) and
    `ARG001` in the modules whose arguments are read by `__pragma__("js", ...)` code.
  - The module-level skip blocks became comment-form pragmas after the runtime imports (owner's
    choice), so no import follows a statement (`E402`):
    `# isort: split`, `# __pragma__ ("skip")`, the typing imports and aliases, `# __pragma__
    ("noskip")`. Transcrypt reads `# __pragma__ (...)` comments as pragmas (`pragmasFromComments` in
    its compiler); `# isort: split` keeps the sorted runtime imports out of the block, and
    `__pragma__` is a Ruff `task-tags` entry so the comments are not commented-out code (`ERA001`).
    The first import of the block must be the first one in isort order, so the skip comment stays
    above it.
  - Generic functions use PEP 695 type parameters (`UP047`): Transcrypt (run under Python 3.12)
    compiles them and drops the annotations.
  - Every Python file starts with `# Copyright (c) 2026 Renaud Guillon` (`CPY001`, owner's choice).
  - Docstring summaries are one imperative line (`D401`, `D205`); the summaries an earlier autofix
    had cut mid-sentence were rewritten.
  - deptry ignores `DEP001` for `org`, Transcrypt's compile-time stub package.
- **Alternatives considered:** keeping inline `# noqa` with reasons (owner: no); refactoring away
  positional flags and long argument lists (a large refactor against ENG-151); a global `E402`
  ignore (owner: restructure the skip blocks instead).
- **Consequences:** the ENG-14, ENG-15, ENG-151, ENG-153, ENG-157 and ENG-161 texts still mention
  `# noqa` comments; updating them is left to the owner (requirement sections).
- **Status:** Proposed

### D-236 — 100 % unit coverage: unreachable code is removed, never excluded
- **Date:** 2026-11-02
- **Requirements:** ENG-43 (changed), ENG-29, ENG-45, ENG-75, ENG-76, ENG-145, ENG-146 (texts updated).
- **Context:** the owner raised `fail_under` from 70 to 100 % and dropped the per-package gates and
  the HTML report. The unit tests were then completed (89.8 % → 99.87 %); the last 63 lines and
  branches could not be reached by any honest test: defensive guards that earlier code makes
  impossible, a cache read only JavaScript performs, a mypy-only `raise`.
- **Decision:** reach 100 % by tests, and remove or restructure the code no input can reach (owner's
  choice, over `# pragma: no cover` or tests that feed private functions impossible inputs):
  - Dead guards are deleted after checking they are dead in the browser too (`undefined`, NaN, an
    empty list being truthy). One was not: `traffic.py` stops NaN on a zero-length road, so that
    check moved to where cars are added (a road with no length gets none), with its test.
  - Guards that only narrowed a type for mypy are replaced by code whose types carry the invariant
    (`cast` does not exist at run time under Transcrypt): kinds looked up in a dict by id
    (`boss_fights.py`, `level_run.py`, validated by their constructors), `draws.weighted_pick` for
    lists that are never empty, `music_player._start` returning what it made,
    `menu_flow._leave_completed_level` taking its result.
  - A value only JavaScript sets is read through a small `__pragma__("js")` helper the tests can
    patch (`ship_materials._cached_materials`, ENG-158).
  - Functions no code calls are deleted with their tests.
- **Alternatives considered:** `# pragma: no cover` with a reason on each line (weakens the gate,
  CLAUDE.md); covering guards by calling private functions with inputs the callers never produce
  (tests of impossible states); a threshold under 100 %.
- **Consequences:** every line and branch of `src/` is run by a unit test, so any new unreachable
  code fails `make tests`. CPython-only gaps (a JavaScript-only helper whose Python body is a
  placeholder) are covered by tests that call the placeholder and say so.
- **Status:** Proposed

### D-237 — `src/` holds only code the game runs; what only tests call lives in `tests/`
- **Date:** 2026-11-02
- **Requirements:** GAME-SHIP-08, GAME-WPN-19, BOSS-38, GFX-ROAD-21 (discrepancies noted), BOSS-21,
  ENG-145, ENG-49.
- **Context:** with coverage at 100 % (D-236), a scan of `src/` (no import, call, attribute read or
  JavaScript string names it) found about 60 functions, classes and methods that only tests used:
  engine checks nothing ran (`validate_weapons`, `validate_player_ship_roster`, ...), measuring
  tools (`in_family`, `pattern_signature`), a fake (`MemoryStorage`), accessors for tests
  (`EnemyLayer.count`, `SceneryStage.has_sea`, ...), the first props viewer's `SceneryStage`
  methods (D-199), unused Babylon wrappers and typing Protocols, and `config/shot_viewer.py`.
- **Decision:** the owner asked to take them out of `src/`:
  - Code whose only subject was itself is deleted with its tests.
  - Tools tests use to check other code or the game's data move into test code:
    `tests/helpers/color_families.py` (`in_family`), `tests/helpers/memory_storage.py`
    (`MemoryStorage`), and the test files that use them (`_check_roster`, `_check_weapons` in
    `test_player_build.py`, `_pattern_signature` in `test_boss_parts_and_stages.py`).
  - Accessors are deleted; tests read the state directly.
  - `ship_parts.tag_part` went too: its tag was read only by a test-only reader.
  - Every requirement ID keeps a test named after it (ENG-42).
- **Alternatives considered:** wiring the unused engine checks into the game (a change of
  behaviour, not a clean-up); keeping test-only code in `src/` (it counts as product code and must
  stay covered).
- **Consequences:** the engine refuses no bad roster or weapon data at run time (it never did; the
  game's data is checked by unit tests). BOSS-38's health rule is applied by hand in the configs. A
  stage cannot be re-seeded. The scan cannot tell methods apart when other classes share their name
  (`count`, `clear`, ...): those were checked by hand where flagged.
- **Status:** Proposed

### D-238 — Sounds and music viewers in the Dev menu, as audio viewers without a scene
- **Date:** 2026-11-02
- **Requirements:** DEV-MENU-19, DEV-MENU-20 (new); DEV-MENU-03 (entries list), the dev-menu
  tunables (`DEV_VIEWERS`, `DEV_AUDIO_VIEWERS`).
- **Context:** owner request: a sound menu in the dev view with a button for every sound, and a
  music menu for the music, to check the game's generated audio by hand.
- **Decision:**
  - Two more viewers of the dev menu, `Sounds` and `Music`, on the flow's existing `dev-viewer`
    screen (counts, items, toggle, Back), so the menu flow, the controller and the test API need no
    new screen. Their view is a `DevAudioView` (`dev-audio`): the dev viewers' scrolling menu laid
    out as a grid over the whole screen, one button per item, with the status line and the hint;
    no 3D scene (`DevSession.active` stays false, the menu backdrop shows).
  - The item picked plays: `DevAudioViewer` (`src/app/dev_audio_viewer.py`) follows the flow's
    state and plays on a change of item or of the toggle (Confirm flips it, so "play again" costs no
    new command); opening the viewer plays nothing. The flow answers `played` (a new
    `MenuFeedback`) instead of `moved` / `adjusted` on an audio viewer, so no menu sound covers the
    sound picked.
  - A sound button plays on the pointer's press, not on the release (`pointerdown`, not `click`),
    and held it repeats: the screen reports the hold (`on_hold`) and `DevAudioViewer` plays the
    item again from the game's frames (`hold_delay`, then every `hold_interval`), not from a DOM
    timer, so the e2e tests step it (ENG-58). The release is heard on the screen's root, as the
    button pressed is made anew when the item changes. The music viewer's buttons do not repeat.
  - `GameAudio` gets `play_cue` (a cue's sound alone, unpanned; a looping one kept until the next
    cue or `stop_cue`) and `play_music` (a track from its start, a jingle over the music), and
    leaves the music alone on the music viewer's screen (`menu_changed`); the dev menu's screen
    brings the menu theme back.
  - The catalog lists the sounds by cue (the engine's `AudioBindings.sounds`) and the music by
    composing every request the engine can make (menu, each level's level and boss track, the
    jingles) and keeping each track id once: about 0.1 s in CPython for the whole game, only with
    `?dev`, and the tracks are the ones the game then plays (they are cached). A music item's id
    names its request (`menu`, `level:1-1`, `boss:1-1`, `jingle:complete`), read back by
    `music_request`; its label is the track's id, as the test API reports it.
- **Alternatives considered:** a separate screen kind in the flow (more state machine for the same
  behaviour); listing the boss tracks per level without composing (20 buttons for 4 tracks);
  playing on every selection change including the first (a sound on opening the viewer, over the
  dev menu's confirm sound); a `Stop` button in the music viewer (Back does it).
- **Consequences:** the dev viewers' texts gain the two hints and the `Playing: ` prefix;
  `DevSession` takes the game's audio. The music viewer's `Playing` line shows whatever plays, the
  menu theme included, with its time. The requirement text of DEV-MENU-03 and the viewers list
  were amended (agent, per D-234's rule that a decision is written into the requirement it
  concerns); the owner may veto.
- **Status:** Proposed

### D-239 — Realistic sound effects: filtered noise, sines, bells and clicks, no chip sweeps
- **Date:** 2026-11-02
- **Requirements:** AUD-SFX-08 (new); AUD-SFX-01 (the sounds' descriptions), AUD-SFX-02 (the
  minigun's thump), the tunables table.
- **Context:** owner request: "make the sounds more realistic, no more 90s videogame pew". The
  sounds were square and sawtooth tones with pitch sweeps (the enemy shot, the lasers, the hits,
  the falling tones of the deaths) and chip chimes (the rewards, the menus); only the explosions
  (D-108) and the minigun were layered noise.
- **Decision:**
  - Six small recipes in `sound_recipes.py`, all filtered noise or sines: `click` (noise through a
    band-pass, a few ms), `thump` (a sine falling by half), `whoosh` (noise through a band-pass
    sweeping between two cut-offs), `rumble` (low-passed noise), `ring` (noise through a band-pass
    of Q 30, which rings like struck metal) and `bell` (a sine fundamental under a quieter, shorter
    partial at 2.76 ×, as a struck bell's). `chime` is gone.
  - Every design is rebuilt from them (see AUD-SFX-01's table): the lasers are air sweeps, hums and
    surges; the missiles ignition, exhaust and rumble; the enemy shot a dull crack; the hits cracks,
    clanks and thuds, the shield two inharmonic rings; the deaths and the bomb keep their
    explosions under air sweeps, falling sines and rumbles instead of falling square or sawtooth
    tones; the rewards are bells; the menus clicks, with a bell tap for confirm and back and a
    falling or rising low tone for pause and resume. The minigun's thump is a low-passed triangle
    instead of a square. No square or sawtooth layer remains (a unit test checks it).
  - The levels were checked offline (a NumPy render of every layer: oscillators, noise, biquads,
    envelopes, glides): each sound's peak and RMS were brought back within the old one's range,
    which meant boosting the narrow-band clicks and rings (a band-pass of Q 4 to 30 passes little
    of the noise) and lowering the bells and the player-hit; the missile's hiss and the hum's air
    were cut so no sound is a long bright hiss (AUD-SFX-07).
- **Alternatives considered:** a wave-shaper for distortion and grit (the engine has no such node;
  not needed); recorded samples (AUD-ENGINE-01: generated only); keeping the chimes for the menus
  (the owner asked for no chip sounds at all).
- **Consequences:** the sound names and cues are unchanged, so the e2e tests and the test API are
  untouched. The tests of the recipes and designs follow the new data. The reviewer checks the
  sounds by ear in the Dev menu's sounds viewer (DEV-MENU-19).
- **Status:** Proposed

### D-240 — Scarps: World 1's hills have one rocky face and a slow slope on the other side
- **Date:** 2026-11-02
- **Requirements:** GFX-TERRAIN-19 (new), GFX-TERRAIN-06 (the ceiling counts the scarps),
  WLD-1-31 (new), LVL-1-2-04, LVL-1-3-04, LVL-1-4-04, LVL-1-5-04 (the section tables), the terrain
  tunables.
- **Context:** owner request: rocky sides where the slope is high enough, as in the mountains of
  Ireland, and most of the time hills with one rocky side and a slow grass or desert slope on the
  other. The ground of World 1 was fractal relief only, so gentle (a median slope of 3° to 5°, under
  13° almost everywhere) that the look's steep layer never showed on the land, and every hill was
  symmetrical.
- **Decision:**
  - A new section feature in the engine, `scarps`, made by the dunes' ridge generator
    (`_ridge_shape`, shared): wandering ridges whose cycle is a long rise and a short drop, but
    with the drop's share set by the section (`face`) and the crest heights spread from `lowest` to
    the full height by a sharper curve over a shorter noise of their own (1.2 wavelengths), so the
    ridges pinch out into separate hills; the lines bend over 3 wavelengths, as the dunes'. The
    faces look towards `angle_deg`. Bounded between 0 and `height`, so the terrain ceiling just
    adds `height`; a section with scarps has no known steepness (the roads measure the slope, as
    over the dunes).
  - World 1's open-land sections carry scarps of 24 to 40 over 320 to 360 of wavelength (a hill
    about every screen), faces of 8 % of a cycle (a slope of 0.8 to 1.6 at a full crest: 40° to
    58°, rock; a half crest is rock too), all looking 150° from +Z (towards +X and the camera,
    which is tilted towards +Z and sees them as walls). The towns on street grids (their streets
    need ground under a slope of 0.12), the dry lake, the canyon, the mesas, the buttes and the sea
    keep their ground. The farmland's and the desert outskirts' hills are lower (24).
  - The World 1 looks turn steep ground to rock sooner: the green levels from a slope of 0.12 to
    0.3 (28° to 46°; a grey crag texture, `CRAG`, lightly layered), the dry levels from 0.2 to 0.42
    (37° to 55°; the mesa rock, which now also covers the canyon walls and more of the mesa walls).
- **Alternatives considered:**
  - Shearing the relief sideways by its own height (a domain warp), so one side of every hill
    steepens: measured on the real reliefs, it steepens the steepest 1 % of the ground from 13° to
    18° at most before it folds over, because the fractal relief is too gentle to drive it.
    Rejected.
  - Steeper fractal relief (more amplitude, shorter wavelengths) and a lower rock threshold alone:
    rock on both sides, no slow slope.
  - Reusing `dunes` with new optional fields: the World 1 specs and tests say the desert has no
    dunes (WLD-1-10, D-200), and a windward share is not a face; a feature of its own is clearer.
- **Consequences:** `TerrainSection` has a last optional field `scarps`; the config mapping, the
  ceiling and the steepness bound know it; World 2 to 4 are unchanged. The ceilings of 1-2 and 1-3
  rise by the scarps' height (the green hills to 122, the rocky pass to 130), still under the
  clouds and the flight. Buildings and roads keep off the faces (slope limits), so the sections
  with scarps have somewhat fewer buildings. The owner checks the look in the game; the heights,
  face share and angle are tunables.
- **Status:** Proposed
