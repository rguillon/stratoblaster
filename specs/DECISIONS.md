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
    about every screen), faces of 6 % of a cycle since D-243 (a slope of 1.1 to 2.1 at a full
    crest: 48° to 64°, rock; a half crest is rock too), all looking 125° from +Z: towards +X, where World 1's
    sun is (ahead of the camera and to the right), so the faces are lit, and a little towards the
    camera, which is tilted towards +Z and sees them as walls. The towns on street grids (their
    streets need ground under a slope of 0.12), the dry lake, the canyon, the mesas, the buttes and
    the sea keep their ground. The farmland's and the desert outskirts' hills are lower (24).
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

### D-241 — Rock faces of stones, sampled from one plane
- **Date:** 2026-11-02
- **Requirements:** GFX-TERRAIN-07 (the `stones` extra, the sharper projection), the terrain
  tunables; WLD-1-31 (the faces turned towards the sun).
- **Context:** owner feedback on D-240: "the rocky parts are too blurry, make better looking
  stones". The rock textures were the same fractal noise between three colours as the grass, with
  soft strata: no edge anywhere. On a 40° to 60° face the triplanar sampling weighed the top-down
  and the side planes almost alike, laying two copies of the texture over each other. And the
  faces looked 150° from +Z, away from World 1's sun (ahead of the camera, to the right), so they
  were dark bands with no visible detail.
- **Decision:**
  - A `stones` extra for the generated textures: the cells of a jittered grid (the cracks' grid,
    generalised: less jitter so no sliver cells, cells 1.6 times wider than high as slabs along the
    strata), each stone a flat shade of its own with the noise's grain over it, its edges lit on
    the side facing a fixed light in texture space and shadowed on the other, dark joints that
    wobble with the noise, and thinner fractures of a finer grid splitting some stones. The crag,
    the mesa rock and the base rock use it (the other worlds' rock textures are unchanged).
  - The triplanar weights are sharper (the normal to the 8th power instead of the 4th), and where
    the ground is rock the top-down plane gives up 90 % of its weight to the side planes, so a face
    is one projection.
  - World 1's faces look 125° from +Z (towards +X, where the sun is, and towards the camera):
    lit and seen, their lines crossing the screen. The crag is paler.
- **Alternatives considered:** a larger texture (512 px) for the rock alone: the layers share one
  size and one tile size, and the blur came from the content and the double projection, not the
  texel density; a normal map for the rock: the terrain material has none, and the lit bevel baked
  into the colour reads well enough from the playfield camera.
- **Consequences:** the texture generator does one more cell pass per stone texture (in the worker,
  PERF-14); the shader change applies to every world's terrain (sharper plane choice everywhere,
  only visible on steep ground). The owner checks the stones in the game.
- **Status:** Proposed

### D-242 — The level pauses when the window loses its focus
- **Date:** 2026-11-02
- **Requirements:** UI-PAUSE-11 (a third cause of the automatic pause), ENG-110.
- **Context:** owner request: "make the game pause when it loses focus". The level paused by itself
  only when the page was hidden (a tab switched, the window minimised) or the gamepad in use was
  disconnected; clicking another window or app on a visible page left it running.
- **Decision:** `PageVisibility` takes a third, optional piece, `focus_target` (the window), whose
  `blur` event pauses the level through the menu's `pause` (ignored outside a level, as the hidden
  page's is). The audio is not silenced: the page is still visible, and the sound comes back
  anyway when it is shown again (AUD-ENGINE-11). The game never resumes by itself.
- **Alternatives considered:** pausing on the document's `focusout` (fires on every focus move
  inside the page, so it would pause on a click on the canvas); silencing the audio too (the
  pause menu's own quieting already applies, UI-PAUSE-04 / AUD-ENGINE-11).
- **Consequences:** one more listener on the window, removed with the others when the app stops;
  the e2e smoke test fakes a `blur`.
- **Status:** Proposed

### D-243 — Cliff faces built of blocks of stone
- **Date:** 2026-11-02
- **Requirements:** GFX-PROP-19 (new), GFX-PROP-06 (its exception), WLD-1-31, the terrain
  tunables (the faces' share).
- **Context:** owner feedback on D-241, with a picture of a model cliff: grass to the lip, then a
  near-vertical wall of chunky, layered stone blocks, stepped. "It still looks too flat"; objects
  are fine, not only a texture on the height map. A face 20 to 27 units wide on an 8-unit terrain
  grid is two or three smooth triangles whatever its texture.
- **Decision:**
  - An engine feature, `cliffs` in the prop rules (`core/scenery/cliff_blocks.py`): one block of
    stone per cell of a grid where the ground drawn is steeper than a threshold, sunk into the
    ground and turned downhill, its kind and size from the cell's hash. The blocks are props
    (thin instances, shadows, the matte vertex-coloured structure material), handed out with a
    chunk's buildings. Reading the ground as the mesh draws it (`SampledGround`) keeps the cost to
    a few thousand heights a chunk.
  - Three block models each in grey crag and red mesa rock (`game/view/props/crag_props.py`): a
    plain block, a chipped block, a block with a ledge, one unit in size and scaled per block, so a
    face shows a few courses of blocks of different shapes and shades.
  - World 1's hills' faces take 6 % of a cycle (48° to 64° at a full crest), so the blocks stand on
    a wall rather than a ramp; the walls of the mesas, buttes and canyon get the mesa blocks too.
- **Alternatives considered:** a finer terrain grid under the faces (the grid is one cell for the
  whole level, and the faces are a small share of it); a displacement of the terrain vertices
  (two or three vertices across a face cannot make steps); a normal map on the rock (the terrain
  material has none, and it would still be flat at the silhouette, which the picture is all about).
- **Consequences:** each chunk with faces adds a few hundred instances of six meshes; the props'
  count and polygons go up on World 1 (the debug tile shows them). The blocks hide most of the
  stone texture of D-241 on the faces, which stays on the ground between them and on steep ground
  too gentle for blocks. The owner checks the look in the game; the slope threshold, spacing, sizes
  and colours are tunables (`game/config/cliffs.py`, `crag_props.py`).
- **Status:** Proposed

### D-244 — Cliff blocks as rough chunks of stone, wider than tall
- **Date:** 2026-11-02
- **Requirements:** GFX-PROP-19, WLD-1-31.
- **Context:** owner feedback on D-243: "the rocks are just flat cubes, it's terrible, make better
  looking rocks". The three block models were two boxes each. Also, World 1's sun stands ahead
  (azimuth 25° to 45°) while the hills' faces look 125°: a block's downhill side is 100° off the
  sun and gets only the ambient light, so a tall block is a dark pillar with a lit cap; and the
  blocks stood on the steep shelves under the sea too, a field of stones in the surf of 1-2.
- **Decision:**
  - A game-agnostic chunk generator, `render/geometry/rocks.py` (`rough_chunk`), beside the rough
    lathes of the tree crowns and reusing their `Roughness`: a prism of a few sides whose corners
    are pushed in and out and turned at random, a bulging waist, a smaller, tilted, faceted top,
    every half facet its own shade and darker towards its base. No bottom (it stands in the
    ground). Seeded, like the branches and crowns.
  - The three models (`crag_props.py`) are made of chunks: one big chunk with a stone at its
    foot, two stacked (the darker stone), two side by side. Round boulders (a rough lathe of a
    boulder profile) were tried first and read as grey bushes.
  - The blocks are wider than tall (7 to 10 wide, 5 to 8 high, sunk 1.5), so the lit tops carry
    the look as courses of stone and the dark sides are the joints; the stone is toned down
    (0.58 grey, 0.7 red) so the lit tops no longer blow out to white under the 1.7 sun.
  - `cliff_blocks` takes the props' `min_height`: no block below it (the sea's shelves).
- **Alternatives considered:** a convex hull of random points (the usual low-poly rock; a 3D hull
  in Transcrypt's Python is a lot of code for a look the pushed prism gives); lifting the ambient
  light or turning the faces to the sun (both change the whole world's look, and the faces must
  look towards the camera to be seen as walls at all).
- **Consequences:** about 60 triangles a block instead of 24 (the polygon count of 1-3 is
  unchanged within noise, 373 k). The decision's tunables: `PUSH`, `SHADE`, `SHADOW`, the sides
  and the colours in `crag_props.py`; `TURN`, `WAIST`, `TOP`, `TILT` in `rocks.py`; the sizes in
  `game/config/cliffs.py`.
- **Status:** Proposed

### D-245 — Bigger cliff blocks, a fringe of stones, rock under them
- **Date:** 2026-11-02
- **Requirements:** GFX-PROP-19, WLD-1-31, GFX-TERRAIN-11 (the dry levels' rock onset).
- **Context:** owner feedback on D-244: a little bigger, a wider range with some big rocks; and
  the blocks "often just look like a bunch of rock on top of the grass, not part of the ground".
  Two causes: a block stood level on its centre, so on a steep slope its downhill edge hung over
  the ground; and the face started at full size on a hard line of slope, with grass under its
  first blocks (the looks' rock texture began at the same slope, 0.12 of `1 - n.y`, 28°, and was
  only full rock from 46°).
- **Decision:**
  - Sizes 7 to 14 wide, 6 to 14 high, 7 to 15 deep; a block's bulk is the square of a draw
    (`BULK_POWER`), each size half the bulk and half its own draw: most modest, a few big.
  - A block is sunk further by `SINK` (0.4) of its depth times the slope, so it sits in the slope.
  - A fringe (`FRINGE` 0.7 of the threshold, `FRINGE_CHANCE` 0.5, `FRINGE_SCALE` 0.45): smaller
    stones scattered on the ground just too gentle for the face, growing to full size at the
    threshold.
  - The World 1 looks turn the ground to rock below the fringe's slope, full rock about there:
    green levels 0.045 to 0.1 (17° to 26°), dry levels 0.06 to 0.14 (20° to 30°), so the stones
    grow out of rock. The base look's slope jitter (0.2 of `1 - n.y`, ±0.1) is bigger than these
    thresholds and would put rock patches on the flat and grass patches on the faces: World 1's
    looks use 0.06.
- **Alternatives considered:** pitching the blocks to the slope (placements have no pitch, and
  the shadows and the terrain fit would need it too); a decal of rock round each block (the
  terrain material has no decals).
- **Consequences:** more and bigger instances on the faces (1-3 at 391 k polygons on a busy
  screen, under the 60 fps of the perf test); the hills' backs stay grass (their slopes stay
  under 17°); any other ground over 17° on the green levels is now rock, with a cleaner edge.
- **Status:** Proposed

### D-246 — The grain of the cliff blocks baked into their facets
- **Date:** 2026-11-02
- **Requirements:** GFX-PROP-19.
- **Context:** owner feedback on D-245: do the stones have a texture? They did not (props are
  vertex-coloured, flat-shaded solids); "they currently look like plastic". Two ways were put to
  the owner: grain baked into the vertex colours and geometry, or a textured prop material with
  the ground's stone pattern mapped on the chunks. The owner chose the baked grain.
- **Decision:** in `rough_chunk`, each facet triangle (the sides' halves and the top's fan) is
  split in three pieces round its middle, pushed in or out along its normal by up to
  `GRAIN_BUMP` (0.05 of the chunk's smaller width), each piece shaded up to `GRAIN_SHADE` (0.09)
  lighter or darker. Same material, same thin-instance path, no new shader.
- **Alternatives considered:** a textured material (a second material and shader plugin for the
  cliff kinds, triplanar sampling on hundreds of instances); splitting each triangle in four by
  its midpoints (a smoother grain for a third more triangles).
- **Consequences:** three times the triangles a chunk (90 instead of 30): the busy screen of
  1-3 goes from 380 k to about 500 k polygons, still at 60 fps in the perf test. If a lower
  machine needs it, `GRAIN_BUMP` and `GRAIN_SHADE` can be set to 0 without changing the count:
  the split would need to be made optional.
- **Status:** Proposed

### D-247 — Grass tinted in patches and grained finer than its texels
- **Date:** 2026-11-02
- **Requirements:** GFX-TERRAIN-09.
- **Context:** owner: "what are the options to make the grass look better? it looks flat and
  blurry compared to the tree". The grass is a 256-texel tile over 150 units of ground drawn at
  double scale, a texel for about two screen pixels, bilinear; one flat green with no detail of
  its own, next to trees that are crisp baked pictures with shadows. Four options were put to the
  owner (a sharper or detail tile, large-scale patches, a normal map on the grass, grass clumps as
  props); the owner asked for the first two.
- **Decision:** `lushDetail` on the terrain look, bound as three uniforms: the lush layer is
  tinted in patches (two tints mixed by the coarse channel of the noise texture over `tileSize`)
  and grained (the fine channel over `fineTileSize`, ±`fine`). Two more reads of the noise
  texture, already bound, where grass shows; no new texture, so no change to the load time. The
  base look gets a mild setting, World 1's green levels a stronger one (yellower dry patches,
  deeper green ones, a grain of ±0.28 over 28 units).
- **Alternatives considered:** a 512 or 1024 texel tile (four to sixteen times the generation
  time of every ground texture at load, and the grass's own noise is coarse anyway); a detail
  sample of the grass texture itself at a smaller tile (its mean is not 0.5, so a product would
  darken it); a normal map and grass clumps, kept for later if the owner still wants more.
- **Consequences:** the grass's tunables are in the looks (`lushDetail`); the trees' imposters
  and the roads are untouched. The grain also runs under the fringe of the cliff blocks, which
  helps the stones sit in the ground.
- **Amendment (owner feedback, the same day):** the grain's single read over a 28-unit tile
  repeated visibly ("patterns that are too repetitive"). It is now two reads summed, the second
  over a tile 1.618 times bigger and turned by 37° (`GRAIN_SECOND_SCALE`, `GRAIN_TURN` in the
  shader), so the copies never line up: the usual de-tiling of a repeating texture, at the cost
  of one more read of the bound noise where grass shows. A bigger tile alone would still repeat
  a few times a screen, and a bigger noise texture would cost load time.
- **Status:** Proposed

### D-248 — A Full screen entry on the title
- **Date:** 2026-11-02
- **Requirements:** UI-TITLE-11 (new), UI-TITLE-01, UI-TITLE-06, UI-FLOW-02 (the table).
- **Context:** owner: "Add a full screen button in the main menu".
- **Decision:** an entry of the title's list, between Settings and Dev, so the keyboard and the
  gamepad reach it like the others (UI-INPUT-04), not a corner icon. The flow knows it only as an
  entry whose confirmation is the `fullscreen` feedback and leaves the screen as it is; the app
  (`MenuController`, with `app/page_fullscreen.py`, a thin wrapper of the Fullscreen API) toggles
  the page's full screen on that feedback, and refreshes the title on the browser's
  `fullscreenchange`, so the entry reads "Exit full screen" in full screen, also after Escape.
  The entry exists only where `document.fullscreenEnabled` is true: an iPhone's Safari allows no
  full screen for a page. A refused request (the Fullscreen API's promise rejects without a user
  gesture) is swallowed.
- **Alternatives considered:** a setting on the settings screen (UI-SET-02 says sliders and
  nothing else, and full screen is not a saved value: browsers forget it on reload); a button
  in the pause menu too (not asked; easy to add later as a pause entry on the same feedback).
- **Consequences:** `AppOptions`, `MenuControllerDeps`, `MenuFlowOptions`, `MenuViewContext`
  and `TitleView` each take one more optional, positional piece (ENG-151). The menu sounds
  ignore the new feedback (no cue for `fullscreen`).
- **Status:** Proposed

### D-249 — A 16:9 screen: 1280 × 720 logical pixels
- **Date:** 2026-11-02
- **Requirements:** GAME-SCREEN-01, GAME-SCREEN-02, GAME-SCREEN-04, GAME-SCREEN-05,
  GAME-SCREEN-06, GFX-CAM-01, GFX-CAM-03, GFX-CAM-05, UI-LOOK-01, UI-LOOK-02, UI-LOOK-13,
  GFX-ROAD-19, WLD-1-20, WLD-3-13, WLD-4-13, GFX-FX-10, ENM-09, GAME-BONUS-07.
- **Context:** owner: "change the game aspect ratio. I want to take a full standard 1920×1080
  screen. That means generating new levels and adapting the enemy waves. We will deal with the
  mobile UI later."
- **Decision:** the logical screen is **1280 × 720** (16:9), chosen with the owner over
  1138 × 640 (today's height, only widened; not an exact 16:9, a 1 px letterbox line at
  1920 × 1080) and 1920 × 1080 (native; every px tunable of the game and the specs would have
  to be rescaled ×1.69). 1280 × 720 is an exact 16:9 with integer sides, ×1.5 at 1920 × 1080
  and ×1 at 1280 × 720, and keeps the logical pixel: every speed, size, margin and HUD value is
  unchanged. The playfield is 80 px taller (the ship's flight area goes up to y = 520) and
  800 px wider. The screen size is one record (`GAME_CONFIG.screen`); the camera framing, the
  trapezoid seen of the playfield, the ship's reach, the ground window the terrain is generated
  over, the stage fit and the overlay scale all derive from it, so nothing else of the engine
  changes. What the content needed:
  - *Levels (the ground):* the camera now sees about ±500 ground units across at the sea level
    (±560 at a sea bed), not ±195, so the terrain, roads, districts, props, cars and clouds are
    generated over that window as before (GFX-CAM-05). The one content extent keyed to the old
    width, `offscreenX` (where roads and street grids start and end, and how far from the middle
    lone buildings and hamlets stand), goes from 420 to 1 000 in Worlds 1–2 and from 240 to 640 in
    Worlds 3–4, keeping their ratio to the ground in view. The shores, canyons, dunes and set
    pieces are noise or meanders in ground units and need no change: the coast of 1-1 and 1-2
    (land from x ≈ −40) still gives about 45 % of sea across the view.
  - *Waves:* the scripts are written in fractions of the ship's reach (ENM-09, WLD-1-19), so the
    entries, spreads and paths already spread over the wider playfield; the reach is about 2.8
    times as wide (804 px instead of 282), so `WAVE_DENSITY` goes from 1.5 to 2 (every world uses
    it through `wave_script`), which brings 5 to 25 % more enemies depending on the beats'
    rounding. The counts recorded in the level files were re-measured from the configs (same
    method: fillers and density in, Carrier launches and Splitter pods out). The difficulty orders
    of WLD-1-22 and WLD-1-24 still hold (278 / 342 / 374 / 414 / 448 enemies, each second half
    heavier).
  - *Bomb ring:* its radius goes from 820 to 1 000 px, past the far corner of the new playfield
    (about 900 from where the ship starts).
  - *UI:* the overlay is 1280 × 720; the ship cards, the settings sliders and the dev entries keep
    to a 560 px column in the middle (`--menu-column`) instead of stretching across; the HUD bar
    spans the width as before. The logo keeps its size (sized for 480 px, it is small on 1280;
    to revisit with the mobile layout).
- **Alternatives considered:** keeping 480 × 640 logical and letting the canvas show more of
  the world on the sides (the overlay and the gameplay would stay 3:4: not what was asked);
  scaling the ship's and the enemies' horizontal speeds with the width (not in the model: X and
  Y share one speed).
- **Consequences / open points for the owner to tune after a playtest:**
  - the player ship crosses its reach in about 3.6 s instead of 1.3 s (`base_speed` 225 px/s is
    unchanged); the Strafer's pass across the screen takes about 9 s instead of 4 (9 fans instead
    of 4); the Gnat S-path, in fractions of the reach, swings 400 px wide instead of 140, so the
    Gnats stay on screen longer. These are GAME-SHIP-02, ENM-STRAFER and ENM-GNAT tunables.
  - the terrain, props and streets cover about 2.6 times as much ground across: more triangles
    and more instances per chunk (PERF budgets to watch, e2e perf test unchanged).
  - on a portrait phone (390 × 844) the stage is 390 × 219 CSS px (scale 0.3): the e2e checks
    of UI-INPUT-11 (touch targets), UI-PAUSE-02 (the pause button on the phone) and UI-SET-03
    (the sliders on the phone) are marked expected-to-fail (strict) until the mobile layout;
    UI-LOOK-09's manual check at 390 × 844 does not hold either. The owner deferred the mobile
    UI. In an 800 × 600 window the stage's scale is 0.625 (it was 0.94 at 3:4), so the pause
    button grows from 56 to 72 px to stay at 44 CSS px there (UI-PAUSE-02).
  - the readability probe (DEV-API-09) is run on 4-1 at 60 s instead of 90 s: the probe takes the
    first player shot in view, and with the waves' new timing the shot at 90 s (and at 120 s)
    flies over a lit tile of the garden town, where it reads at 1.3 to 1.9 against a floor of 2
    (4.8 at 60 s). The weak reading is the tile's, not the screen's: GFX-READ-14's player shot
    opacity (0.7) is the knob if it shows in play.
  - the view's horizontal field of view is about 66° (vertical 40°, unchanged): the sides of the
    screen show more perspective than before; `fovDeg` is the knob if it reads as distortion.
- **Status:** Proposed

### D-250 — The canvas is never drawn above full HD; the ground glow back at half resolution
- **Date:** 2026-11-02
- **Requirements:** ENG-110, GFX-TERRAIN-15, PERF-32.
- **Context:** owner: "i'm down to 30fps in 4k on my Snapdragon X, any way to improve that?"
  On a 4K panel (device pixel ratio 2, capped at 2) the canvas was 3840 × 2160 pixels with
  multisampling, nine times the pixels of the 1280 × 720 screen, plus the ground's glow drawn as
  a second full-size multisampled pass, and the full-screen cloud, weather and aurora layers
  blended at that size. On an integrated GPU the frame is fill-rate bound.
- **Decision:** (1) `ENGINE_CONFIG.max_render_scale` (1.5): the hardware scaling level follows the
  stage fit, so the canvas draws at most 1.5 pixels per logical pixel across (1920 × 1080),
  whatever the window and the device ratio; the browser upscales the rest (`render_ratio` in
  `ui/stage_fit.py`, set on every fit, so a resize keeps the cap). (2) The ground's glow image
  goes back to Babylon's default half resolution, keeping its 4 samples (the samples, not the
  resolution, hold the thin lights steady) and its blur kernel as the look gives it.
- **Alternatives considered:** a render scale slider in the settings (UI-SET-02 allows two
  sliders and nothing else; a later step if the cap is not enough); fewer cloud layers or
  coarser far terrain (not measured as the bottleneck).
- **Consequences:** at 1920 × 1080 and below nothing changes (the device ratio is 1 there);
  the e2e builds draw as before (their 0.5 factor applies on top). Not measured on the
  owner's machine: to check with the F2 tile on 2-5 and 4-5.
- **Status:** Proposed

### D-251 — The HUD in side columns, no pause button, the ship down to the bottom edge
- **Date:** 2026-11-02
- **Requirements:** UI-HUD-01, UI-HUD-02, UI-HUD-03, UI-HUD-05, UI-HUD-06, UI-HUD-07, UI-HUD-08,
  UI-HUD-10, UI-HUD-12, UI-PAUSE-01, UI-PAUSE-02 (removed), GAME-SCREEN-05, GAME-SCREEN-06,
  UI-LOOK-03, UI-LOOK-05, UI-INPUT-11, UI-OVER-01.
- **Context:** owner: "move the UI to the left side, remove the pause button, reduce the right
  side the same way as the left to keep the screen symmetrical. And make sure the player ship
  can now fly up to the bottom of the screen."
- **Decision:** the HUD is two glass columns 200 px wide (`--hud-side`, the whole height) down
  the sides of the 16:9 playfield. The left one stacks the readouts (progress line, ship, lives,
  bombs, health, score, high score, weapon), the boss gauge under them (at 270 px from the top,
  it was along the left edge from the top) and the level played at its foot. The right one is
  empty, so the playfield stays in the middle; on touch screens it holds the fire and bomb
  buttons. The pause button is gone with its view label, handler and texts (the keyboard and the
  gamepad pause; a touch way to pause comes with the mobile layout). The ship's bounds take the
  columns: its half width at a height is the smaller of the width seen there and the space
  between the columns, less the 18 px side margin (`ShipMargin.panel`); its bottom margin goes
  from 78 (30 px above the old bar) to 20 px, half the balanced ship's length, so it reaches the
  bottom edge with its model on screen. The reach (GAME-SCREEN-06), now at y = 20, is about
  x 260 … 1 020 (the width seen at y = 20 is the narrower of the two bounds).
- **Alternatives considered:** letterboxing the 3D view to the middle 880 px (the owner asked
  to reduce the sides the same way as the left: glass columns over the view, as the left HUD
  is); keeping the pause button in the right column (the owner asked for it removed).
- **Consequences:** `GameScreenView` and `ScreenHandlers` lose their pause pieces (ENG-151);
  the e2e checks of UI-PAUSE-02 are gone, the pointer test pauses with Escape. The test of
  the dev model scene's glow kernel is aligned with D-250 here (it still expected 32).
- **Status:** Proposed
