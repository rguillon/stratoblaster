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

### D-252 — The level drawn and played in a 540 × 720 window between the HUD's columns
- **Date:** 2026-11-02
- **Requirements:** GAME-SCREEN-01, GAME-SCREEN-04, GAME-SCREEN-05, GAME-SCREEN-06, GFX-CAM-01,
  GFX-CAM-02, GFX-CAM-03, GFX-CAM-05, UI-HUD-01, UI-HUD-03, UI-HUD-07, GFX-ROAD-19, WLD-1-20,
  WLD-3-13, WLD-4-13, GFX-FX-10, ENM-09, GAME-BONUS-07, ENG-144.
- **Context:** owner: "make the UI more vertical, and restrict the player's movement to the new
  window size. Dont draw the background outside the playing area."
- **Decision:** the game definition gets a `playfield` (ENG-144, one more optional positional
  piece, ENG-151): a logical screen of its own with a `viewport` of the canvas. This game's is
  540 × 720 (3:4) at x = 370 of the 1280 × 720 screen, the width left by two 370 px HUD columns.
  The scenery camera draws only into that viewport (Babylon `Viewport`, set on the stage camera
  from the stage options), so its aspect ratio is the window's and nothing of the level is drawn
  under the columns, which are opaque. Every gameplay use of the screen (the ship's bounds and
  start, the enemies' spawn area, the shots' and bonuses' area, what is on screen, the enemy
  shots' eye point, the audio pan, the dev viewers' framing) reads `game.playfield` instead; the
  stage fit and the overlay keep `game.screen`. The ship's bounds are the width seen of the
  window less the side margin: the `panel` margin of D-251 is gone with the columns outside the
  window. The column readouts are one under the other (the ship, its lives, its bombs each on a
  line), the health bar and the score a size up.
- **What it undoes of D-249:** the playfield is a 3:4 window again (×1.125 the old 480 × 640), so
  the content extents that followed the wide view go back: `WAVE_DENSITY` 2 → 1.5 (the level
  files' counts re-measured, the original figures), `offscreenX` 1 000 → 420 in Worlds 1–2 and
  640 → 300 in Worlds 3–4 (the window shows ±210 ground units at the sea level, ±235 at a sea bed:
  240 would end streets in view), the bomb ring 1 000 → 820 px (the window's far corner is about
  690 from the ship's start). The ship's reach at y = 20 is about x 120 … 420.
- **Alternatives considered:** keeping the 3D view across the whole screen behind glass columns
  (the owner: nothing drawn outside the playing area, and the narrower view also costs about
  2.4 times fewer ground pixels and chunks across); changing the logical screen to 540 × 720 and
  putting the columns outside the stage (the stage is the 16:9 screen, UI-LOOK-02).
- **Consequences:** the ship crosses its reach in about 1.3 s again; the enemies' timing of
  D-249's open points is back to the 480 × 640 game's. The e2e checks on the HUD and the
  readability probe run on the window (the probe projects through the camera's viewport).
- **Status:** Proposed

### D-253 — A 1000 × 720 playfield window, the HUD columns 140 px
- **Date:** 2026-11-02
- **Requirements:** GAME-SCREEN-01, GAME-SCREEN-04, GAME-SCREEN-06, GFX-CAM-01, GFX-CAM-03,
  GFX-CAM-05, UI-HUD-01, UI-HUD-04, UI-HUD-10, GFX-ROAD-19, WLD-1-20, WLD-3-13, WLD-4-13,
  GFX-FX-10, ENM-09, GAME-BONUS-07.
- **Context:** owner, on D-252's layout: "the lateral bars are far too big, make the playing area
  at least square", then, on a 720 × 720 window with 280 px columns: "reduce the lateral bar
  more, about half their current size."
- **Decision:** the playfield window is **1000 × 720** (25:18), from x = 140 to 1 140 of the
  1280 × 720 screen, the HUD columns 140 px each (`--hud-side`, `GAME_CONFIG.playfield`). Nothing
  else of the engine changes: the camera's viewport, the ship's bounds and reach, the spawn area,
  the ground window and the audio pan all derive from the window record (D-252). What follows
  from the width:
  - the camera sees ±305 px of the playfield across the bottom edge and ±514 across the top
    (±165 and ±278 in the 540 px window); the ship's reach at y = 20 is about x 207 … 793,
    586 px wide (300 before, 804 on the whole 16:9 screen);
  - the ground in view is about ±390 units at the sea level and ±435 at a sea bed (±210 / ±235),
    so `offscreenX` goes to 780 in Worlds 1–2 and 560 in Worlds 3–4 (their ratio to the ground
    in view kept: 2 × and about 1.3 ×);
  - the bomb ring's radius goes from 820 to 900 px: the window's far corner is about 860 from
    the ship's start (750 before);
  - `WAVE_DENSITY` goes back to 2, as on the whole screen (D-249): the reach is nearly twice as
    wide as the 540 px window's, and the waves, written in fractions of it, would come in thin
    at 1.5. The level files' counts are D-249's again (measured from the configs).
  - the column contents fit 140 px: 12 px of padding, the health text under its bar (116 px
    wide, 160 before), the score at 22 px, the weapon line allowed to wrap; the touch fire and
    bomb buttons stay centred in the right column.
- **Alternatives considered:** a square window (720 × 720, 280 px columns: the owner's first
  ask, found still too wide once seen); a 4:3 window (960 × 720, 160 px columns: not what was
  asked); a 16:9 window with the HUD over the level (D-252 settled that the level is drawn only
  in the window).
- **Consequences / open points for the owner:** the reach is nearly twice D-252's, so the ship
  crosses it in about 2.6 s instead of 1.3 (`base_speed` unchanged) and the Strafer's and Gnat's
  paths, in fractions of the reach, are about twice as wide (D-249's open points, to a lesser
  degree). The view draws about 1.85 times the ground pixels of the 540 px window (0.78 of the
  whole screen's).
- **Status:** Proposed

### D-254 — Boss armour drawn as pieces of its own, no longer cut out of the body
- **Date:** 2026-11-02
- **Requirements:** BOSS-42, BOSS-43, BOSS-44, BOSS-45, BOSS-52; each boss's shedding requirement
  as its model is redrawn (MB-SENTINEL-05 first).
- **Context:** owner: "I dont want the code to cut into an existing part to generate the pieces
  after an explosion. I want the bosses to have all their possible parts defined in code and
  simply replace the intact hull by broken pieces when needed." Until now the armour regions were
  carved out of the core's triangles at build time (`cut_armour`: faces near the outlines
  subdivided, the ones inside moved to the region), chunked on a grid, their frame derived from
  the carved faces, and a hold-together analysis (`islands.py`) added stems, pylons and bridges or
  moved hanging pieces of the core into the region.
- **Decision:** a boss drawing gets an `armour` field, one entry per region id: its `whole`
  armour (a drawing, as it rests on the core), and optionally the `pieces` it bursts into (a list
  of drawings) and the `frame` it leaves (a drawing). The core is drawn without the armour. The
  engine only toggles nodes: the whole piece until the burst, the pieces flying from the middle of
  what each draws until `reveal.burstEnd`, the frame from the burst on; a moving region's whole
  piece rides its mover node. The defaults the owner chose: pieces left out are plates cracked
  from the region's outline (`render/geometry/plates.py`: the outline triangulated, cut down to
  about a third of its size, its inner corners nudged, the triangles grown into at most
  `armour.chunks` connected groups whose boundaries are the plates), `armour.plate` px thick at
  the top of the armour, in its hull colour (else its flesh's, else its lights'); a frame left out
  is drawn from the outline (`boss_frame.frame_drawings`: a floor slab in the outline just over
  the armour's lowest point, the ribs of `frame_lines` clipped to it). The hold-together
  automation is gone: BOSS-52 keeps its unit test (the states composed from the drawings) and the
  drawings are fixed by hand where they do not hold. The cut, `shatter.py` (now
  `mesh_triangles.py`: reading and appending triangles only), `islands.py` (now a test helper),
  `boss_stems.py`, the pylons and bridges, and the `armour.cut` tunable are removed. A region the
  model draws no armour for has no view while the bosses are migrated: the bosses not yet drawn,
  and those whose drawings do not hold yet, are strict expected failures (ENG-163) struck off one
  by one; the migration goes one world at a time and ends with no expected failure left. The
  region outlines stay in the config: the blasts of a shed region (BOSS-37), the check that a
  hidden weapon lies in a shed region, and the plates and frame drawn by default come from them;
  a region's `heights` now only tell whether a weapon rides a moving piece.
- **Alternatives considered:** hand-drawn pieces for every region (kept as the override: hundreds
  of shapes to author otherwise); shattering the standalone region drawing (still a triangle
  split); the frame drawn into the core and always there (triangles at rest, pokes through the
  armour); dropping BOSS-52's test with the automation (pieces could float unnoticed).
- **Consequences:** every boss model (all 40 have regions) must draw its armour apart from its
  core, and 19 of them must hold together without stems; until a boss is redrawn it sheds nothing
  visible and its weapons unfold out of its hull. At rest a boss may look slightly different from
  before, as its armour is now a piece lying on the core rather than the core's own skin. D-224,
  D-227 and D-230 are superseded where they describe the cut, the chunks, the stems and pylons.
- **Status:** Proposed

### D-255 — Four enemy tiers of five roles, one world each, one colour theme each
- **Date:** 2026-11-03
- **Requirements:** ENM-01, ENM-02, ENM-03, ENM-38, ENM-49, ENM-50.
- **Context:** the enemies were 21 kinds in three tiers (basic, veteran, elite) that joined the
  waves world by world, each kind with its own neon colour snapped to yellow or green. The reviewer
  asked for four tiers, each with one diver, one shooter, one missile launcher, one laser and one
  carrier (launching divers), tier N assigned to world N, redesigning kinds where needed, with a
  colour theme per tier picked against its world's ground.
- **Decision:** 20 kinds in `src/game/config/enemy_tiers.py` (ENM-01): tier 1 Hornet, Scout,
  Rocketeer, Lancer, Carrier; tier 2 Wasp, Strafer, Harrier, Sweeper, Hatchery; tier 3 Phantom,
  Spinner, Mortar, Prism, Broodmother; tier 4 Splitter, Juggernaut, Hydra, Scissor, Hive. Gnat,
  Weaver, Bulwark, Mantis, Minelayer and Orbiter are removed; Harrier, Sweeper, Hatchery, Prism and
  Broodmother are new; Mortar, Phantom, Splitter, Hydra and Hive are redesigned to their role, and
  the Carrier and the bosses' hangars launch Hornets. World N uses only tier N's kinds (ENM-50),
  its waves composed from them in `src/game/config/wave_plans.py`. Each tier has a neon hue on the
  yellow-green ladder (60° / 110° / 85° / 135°) and a hull tint (steel blue / teal / indigo /
  graphite) (ENM-49): the model builder takes both from the tier of its model key, so a kind's
  models need no colour of their own; the readability enemy family (60°–140°) is unchanged and the
  bosses keep the two `enemyHues`.
- **Alternatives considered:** widening the enemy hue family to give the tiers more separate hues
  (changes the readability rules for bosses and shots); keeping older tiers in later worlds (the
  reviewer asked for one tier a world); keeping the removed kinds as fillers.
- **Consequences:** the triangle budgets are per tier (400 / 600 / 900 / 1200); World 1 has no
  Gnat swarms and its waves are composed like the others instead of written by hand; contrast of
  tier 3's chartreuse on the grass of 3-4 and 3-5 relies on brightness more than hue.
- **Status:** Proposed

### D-256 — Bosses are angry only when new weapons come out, and their weapons are the bullet hell

- **Date:** 2026-11-03
- **Requirements:** BOSS-27 (BOSS-28 removed), BOSS-37; every boss file's angry requirement.
- **Context:** a boss was angry for 3 s after each lost part, firing a bullet hell of four shapes
  from its core (`boss_rage.py`, a heat per boss). The reviewer asked for it only when the boss
  reveals a hidden weapon, the bullet hell coming from the new weapons, whatever their kind.
- **Decision:** a lost part only pauses the boss. At the end of a transformation it is angry for 6 s
  (`BOSS_TIMING.rageSeconds`): `boss_build.angry_pattern` takes the volleys and launches of the
  weapons that transformation revealed, fired `rageRate` (3) times as often, a missile rack with
  `rageMissiles` (2) times as many missiles, a laser no oftener than warning + beam +
  `rageLaserGap` (0.6 s). Nothing else fires meanwhile. `boss_rage.py` and every design's `rage`
  record are removed; no boss needed a new weapon since every boss transforms (BOSS-35).
- **Alternatives considered:** keeping the core patterns beside the weapons (the hell would not come
  from the new weapons); a per-boss angry pattern in data (more to author and keep in step with
  each boss's weapons).
- **Consequences:** how hot a rage is now depends on the weapon kinds revealed, not a heat number;
  the BOSS-55 "heat goes up" criterion is gone; a rage whose weapons are all destroyed is silent.
  The per-boss specs' angry sections and measured fight times need a new look.
- **Status:** Proposed

### D-257 — View buttons in the enemies and bosses viewers: model, wireframe, game view

- **Date:** 2026-11-03
- **Requirements:** DEV-MENU-21.
- **Context:** the enemies and bosses viewers only showed the model pinned at the middle, dropping
  what it fires; the reviewer asked for buttons to switch to a wireframe view and to a view where
  its movements and actions can be seen.
- **Decision:** `DEV_VIEW_MODES` (model, wireframe, game view) with a button row over the viewer's
  menu. Wireframe sets the scene's `forceWireframe`. The game view runs a real `EnemyWorld` (the
  player at the bottom middle) and draws its enemies, shots and blasts with the game's renderers,
  at game size. A tap on a view button is the menu index `-1 - view`, so the pointer path and the
  flow need no new command type; the dev screen's drag-to-turn leaves the buttons alone.
- **Alternatives considered:** a new menu command type for view taps (more plumbing for one
  button row); Enter cycling the views (no buttons, as asked).
- **Consequences:** the game view does not draw the player's ship nor test hits on it; hit circles
  are not drawn in the wireframe.
- **Status:** Proposed

### D-258 — A harder, immediate rage

- **Date:** 2026-11-03
- **Requirements:** BOSS-27.
- **Context:** after a transformation the new weapons often took several seconds to open fire: the
  stage pause of the part that called for it was still running, and each volley waited its whole
  (shortened) interval for its first shot. The reviewer asked for a stronger rage that starts at once.
- **Decision:** the end of a transformation cancels the pause; each angry volley's first shot comes
  `rageFirst` (0.15 s) + `rageStagger` (0.2 s) × its place after the rage starts (never later than
  its interval). The rage lasts 8 s (was 6), fires 4.5× as often (was 3×) and a rack launches 3×
  the missiles (was 2×).
- **Alternatives considered:** only shortening `first` (the pause would still delay it).
- **Consequences:** a rage is about twice as dense as D-256's; the lasers stay bounded by their
  warning and beam. Not yet judged by play.
- **Status:** Proposed

### D-259 — A turret's volley waits until the turret points the way the shots go

- **Date:** 2026-11-04
- **Requirements:** BOSS-29.
- **Context:** the reviewer saw bullets leave a boss's twin gatlings away from their barrels, now
  and then. Aimed shots were aimed from the muzzle at the player at once, while the turret chases
  the player at 150°/s, so a volley due while the turret was still turning (a weapon just
  revealed, a player who moved fast) left barrels pointing elsewhere. The angry opening fire
  (D-258) made it much more frequent.
- **Decision:** `BossPattern.step` holds a due aimed, burst, missile or fan volley on a turret until
  the turret is within `AIM_TOLERANCE` (6°) of its aim, a burst checking before each bullet. Rings,
  lasers and guns off a turret never wait.
- **Alternatives considered:** aiming the shots along the barrels (the player could be missed for
  seconds); a turret that turns instantly (loses the readable swing).
- **Consequences:** a volley can come up to a turret's swing (a fraction of a second) late; its timer
  does not catch up. Only checked against bullets, not on the real game by eye.
- **Status:** Proposed

### D-260 — Waves are one big wave of one kind at a time, and divers come in from the sides

- **Date:** 2026-11-04
- **Requirements:** WLD-1-19, WLD-1-20, WLD-1-21, WLD-2-19, ENM-08 (the specs still describe the
  old phrases and filler; to be updated by the human).
- **Context:** the plans cycled through kinds with a beat every 6 s or so, while one wave of 8
  groups lasts as long, and the filler mixed divers and shooters into every lull, so several kinds
  were on screen together. Every kind but the Strafer came in from the top.
- **Decision:** `compose_beats` starts the next beat only when the previous wave has come in
  (`wave_duration`) plus `SETTLE` (2 s) plus a breather that shrinks over the level (`gap`), so
  kinds do not overlap. Waves of several groups are bigger and tighter (`size` grows with level and
  world). A kind comes in another way each time it comes round (`KIND_ENTRY` lists its ways: line,
  mirrored line, side column, pincer), mirrored every other round. `Wave.alternate` makes every
  other group come from the opposite edge. The Hornet and the Wasp accept a side entry: they fly in
  level from the edge to a stop in that side's half (`HornetOptions.stop_x`), then aim and dive as
  usual. The filler repeats the kind of the beat before it, after its wave, and only for kinds in
  the level's filler (heavy kinds get none).
- **Alternatives considered:** dropping the filler (spec'd MUST); side entries for the Phantom and
  Splitter (their movement is built on a top entry, left for later).
- **Consequences:** about 20 waves per level instead of about 50 beats, 300 groups instead of 400 to
  500; the difficulty ramp (WLD-1-22) and density are tuned by numbers, not yet judged by play.
- **Status:** Proposed

### D-261 — The sound effects are CC0 samples, not synthesised
- **Date:** 2026-11-04
- **Requirements:** AUD-ENGINE-01 (changed), AUD-ENGINE-04, AUD-SFX-01, AUD-SFX-02, AUD-SFX-04,
  AUD-SFX-08 (changed), ENG-120, ENG-122, ENG-123, ENG-124, ENG-126, ENG-143, DEV-API-02 (`samples`)
- **Context:** requested by the human: use open-source sounds instead of the synthesised ones. The
  specs forbade any audio file (AUD-ENGINE-01, ENG-126); ENG-120 to ENG-123 already allowed CC0 file
  assets with credits and a manifest.
- **Decision:** the 29 sound effects are samples from Kenney's CC0 "Sci-Fi Sounds" and "Interface
  Sounds" packs (downloaded from OpenGameArt: kenney.nl refuses scripted downloads), each made mono,
  44.1 kHz, cut where long, peak-normalised to −1 dBFS and shipped as `public/sfx/<name>.ogg` and
  `.mp3` (MP3 for browsers without Ogg Vorbis, picked with `canPlayType`). `SoundDesign` now names a
  sample, its level, priority, length and flags instead of synth layers; `SampleBank` fetches every
  file at start-up and decodes it when the context is created (it only exists after a gesture,
  AUD-ENGINE-03); `SfxPlayer` plays a decoded sample through the same voice pool, panner and bus as
  before (`play_sample`). A sample not ready or failed is silent. The sound recipes
  (`sound_recipes.py`) and the synthesised designs were removed; `flatten_layers` moved to
  `instruments.py`. The music stays synthesised. `make build` now checks that audio files are only in
  `sfx/` and that every `.ogg` has its `.mp3`; the e2e test checks the files fetched, found, and
  decoded (test API `samples`). The player gun first used a Kenney laser shot; at the human's request it became a minigun burst built from single shots of the CC0 AK-47 recording of the Free Firearm Sound Library (six shots 21 ms apart, AUD-SFX-02). The laser hum is the one loop: its tail is cross-faded into its head.
- **Alternatives considered:** keeping the synthesised sounds as a fallback when a sample is missing
  (more code, hides a load failure); decoding before the gesture with an `OfflineAudioContext` (a
  second context, different sample rate); a typed manifest in `src/assets/` (the sound designs
  already name each file once); `<audio>` elements (no panning or looping without gaps).
- **Consequences:** about 630 KB more in `dist/`; sounds asked for in the first fraction of a second
  after the first key press may be silent if the decode is not over; the samples were picked by file
  name and duration and not listened to, so the reviewer may want to swap some (AUD-SFX-08 notes);
  the loudness was set from the old gains, not measured against the music beyond the AUD-SFX-06 check.
- **Status:** Proposed

### D-262 — Three variants of the small and large explosions, and sounds for K in the bosses viewer
- **Date:** 2026-11-04
- **Requirements:** AUD-SFX-01, AUD-SFX-09 and AUD-SFX-10 (new), DEV-MENU-14
- **Context:** requested by the human: three different `explosion-small` and `explosion-large`, played
  at random; and in the dev bosses viewer, K should sound the explosions too.
- **Decision:** `SoundDesign.sample` became `samples` (a list). `SfxPlayer` picks one at random for
  each play with the seeded generator of `core/math/rng.py` (`VARIANT_SEED`), never the one played
  last for that sound. The six recordings: Kenney `explosionCrunch_000`, `_002`, `_001`; compufox's
  `explosion2`, `explosion1_0` and `explosion3` (CC0 on OpenGameArt; `explosion-small-3` first came from number99's `explosion`, 4 LU louder than the others, and was replaced on the human's request), processed as the
  others. The viewer collects what blew up (`DevViewer.take_cues`: the radii of the explosions, the
  parts broken, a boss gone) and `DevSession` has `GameAudio.play_blasts` play them as `LevelCues`
  would: large or small by radius, `part-destroyed`, then `boss-destroyed`.
- **Follow-up (same day):** the boss's death blasts were still too regular (a blast every
  `BossDeath.every`, the same few recordings). Each play of `explosion-small`, `explosion-large` and
  `boss-part-destroyed` is now varied by a `SoundJitter` (pitch, level, start delay, AUD-SFX-10),
  from the same seeded generator; `play_sample` takes a `rate` and a `delay`. The simulation's blast
  timing is unchanged.
- **Alternatives considered:** `Math.random` (not reproducible); variants as separate cues picked by
  `LevelCues` (the core would then choose sounds); cycling in order (predictable).
- **Consequences:** 4 more samples, 35 more KB in `dist/`; the voice pool counts a variant sound at
  its longest recording; the picks are not chosen by ear (reviewer to listen).
- **Status:** Proposed

### D-263 — Back to the original 3:4 playfield, the HUD still outside it
- **Date:** 2026-11-04
- **Requirements:** GAME-SCREEN-01, GAME-SCREEN-04, GAME-SCREEN-06, GFX-CAM-01, GFX-CAM-05,
  UI-HUD-01, GFX-ROAD-19, WLD-1-20, WLD-3-13, WLD-4-13, ENM-09.
- **Context:** owner: "revert to the original screen ratio but keep the UI outside the playing
  area". Asked how to lay out the side space, the owner chose D-252's 370 px columns.
- **Decision:** undoes D-253: the playfield window is **540 × 720** (3:4) at x = 370 of the
  1280 × 720 screen, the HUD columns 370 px (`--hud-side`). The extents that followed the wider
  view go back as D-252 set them: `WAVE_DENSITY` 2 → 1.5, `offscreenX` 780 → 420 (Worlds 1–2) and
  560 → 300 (Worlds 3–4), the bomb ring 900 → 820 px. The ship's reach is about x 120 … 420.
- **Consequences:** the ship crosses its reach in about 1.3 s again. The wave counts recorded in
  the level specs were not re-measured with the new density (open point). Column contents keep the
  D-253 sizes.
- **Status:** Proposed

### D-264 — Nothing enters laterally in the bottom third
- **Date:** 2026-11-04
- **Requirements:** ENM-08, ENM-HORNET-10, ENM-WASP-11.
- **Context:** owner: "make sure no enemy spawn laterally in the first bottom 1/3 of the screen".
- **Decision:** a side entry's height is its position (kept off the corners) but never below a
  third of the playfield height (`side_height`, `SIDE_MIN_HEIGHT` in `enemy_helpers.py`): Hornets,
  Strafers and Wasp columns (the column is shifted up as a whole). Random side passes obey it too.
- **Status:** Proposed

### D-265 — Recorded explosions replace the vocal-sounding ones
- **Date:** 2026-11-04
- **Requirements:** AUD-SFX-01, AUD-SFX-08, AUD-SFX-09.
- **Context:** owner: "replace all the explosion sounds, those sound mouth generated".
- **Decision:** the six explosion variants, `boss-part-destroyed`, `boss-destroyed` and `life-lost` are
  now CC0 recordings from OpenGameArt (Explosion, Chunky Explosion, Muffled Distant Explosion,
  Explosion somewhere far, Battle at sea), processed as the others (mono, 44.1 kHz, trimmed to the
  same lengths so the sound designs are unchanged, peak -1 dBFS). The Kenney `explosionCrunch` and
  `lowFrequency_explosion` and compufox samples are gone.
- **Consequences:** picked by name and duration, not listened to: the reviewer is to listen and swap
  any that is still wrong (a candidate: 0.17 s `explosion_dull.flac`, too short as it is).
- **Status:** Proposed

### D-266 — The Prism aims at the player and fires two parallel beams straight ahead
- **Date:** 2026-11-04
- **Requirements:** ENM-PRISM-05, ENM-PRISM-06, ENM-PRISM-07, ENM-PRISM-08.
- **Context:** owner: "rework Prism, his two laser always shoot straight forward but the ship orient
  itself pointing to the player before shooting, but stops rotating once it starts shooting".
- **Decision:** the sweeping X of beams is gone. The Prism has an `aim` state (`aimSeconds`, eased
  turn as the Hornet's) before each of its `bursts`; the nose freezes when the warning lines show
  (the warning belongs to the shooting) and the beams follow the Prism's heading, not a sweep angle.
  `bursts` is now a count and `gapSeconds` is replaced by `aimSeconds`; `Prism.sweep` is gone.
- **Consequences:** the two beams are parallel, 42 px apart; the player is hit by dodging sideways
  at the lock instant, not by outrunning a sweep. The tunables (`aimSeconds` 1 s) are for the
  owner to tune after playing.
- **Status:** Proposed

### D-267 — The Prism arrives fast, aims while it brakes and fires when it stops
- **Date:** 2026-11-04
- **Requirements:** ENM-PRISM-05, ENM-PRISM-07.
- **Context:** owner: "rework the movements of Prism, I want it to arrive quickly and slow down to a
  stop, start targeting while it's still slowing down and only fire when it stops."
- **Decision:** `entrySpeed` 150 -> 320 px/s and `brakeDistance` 60 -> 220 px (the slowdown lasts
  about 1.8 s). The eased turn to the player starts as soon as the Prism is below `entrySpeed`; the
  first burst starts when it reaches its stop point. The `aim` state remains only between bursts.
- **Status:** Proposed

### D-268 — Barrels: one shot, one barrel, with its own pose and recoil (slice 1: the Strafer)
- **Date:** 2026-11-04
- **Requirements:** WPN-01, WPN-02, WPN-03, WPN-04, ENM-STRAFER-03, ENM-STRAFER-06.
- **Context:** owner: every weapon of every enemy and boss must be recognised at once: every bullet
  from a Reef-Warden-style barrel that recoils, the bullet starting exactly at the barrel's tip along
  its direction; lasers like the Overlord's; missiles out of hexagonal ports; three guns on each side
  of the Strafer for its fan. Delivered in slices (engine, enemies, mini bosses, final bosses);
  owner chose rotating multi-barrel turrets for fans and rings, and kept each boss's laser tint.
- **Decision:** a muzzle config entry `[x, y, height, angleDeg]` is a fixed `Barrel` (angle optional:
  without it the gun is not converted yet and fires as before). `GunMuzzles.shoot(ctx, source,
  heading, fire)` fires one shot from the fixed barrel pointing nearest `heading` (within 6°), from
  its tip along the barrel's own heading; a shot no barrel can take is held. The recoil is a pure
  function of the source's `age` and the barrel's firing age (`Barrel.recoil_at`, eased 1 to 0 over
  0.18 s), so the sim needs no per-frame step. Enemies list their barrels in `Enemy.barrels`; the
  model draws each as a fixed housing and a sliding barrel (`EnemyParts.slide`) and `sync` slides it
  back by `barrelRecoil` (0.35) of its length times the recoil. The Strafer is the pilot: six
  barrels, fanned ±15°.
- **Consequences:** the other enemies and every boss still fire as before until their slice; the
  lasers (WPN-06) and missiles (WPN-07 to WPN-09) are the next slices of the engine work.
- **Status:** Proposed

### D-269 — Barrels are drawn mirrored, and held by a gun pod on each flank
- **Date:** 2026-11-04
- **Requirements:** WPN-01, WPN-03, WPN-04, ENM-21.
- **Context:** owner: the Strafer's barrels floated and the wrong ones recoiled.
- **Decision:** the config's X is right of an enemy facing down the screen, but a model turned to
  face down has its +X on the screen's left, so a fixed barrel is drawn with its X and yaw mirrored
  (`recoil_barrel`) and the one that fires is the one drawn firing. Each Strafer flank gets a hull
  gun pod from the body out to the housings, so the barrels are held to it. The ENM-21 test expects
  a barrel's marked muzzle at -X.
- **Consequences:** other asymmetric models keep their (unchecked) X until they are converted.
- **Status:** Proposed

### D-270 — Slice 2: every enemy that fires bullets has barrels
- **Date:** 2026-11-04
- **Requirements:** WPN-01 to WPN-04.
- **Context:** owner: "do the same for all the other enemies and bosses".
- **Decision:** fixed banks of barrels, one per shot, for the Wasp (3 fanned 12°), the Phantom (5),
  the Juggernaut's back turret (7, fanned 9°), the Spinner (one per pod, which spins with the body)
  and the Hive (12 rim vents, which now fire along themselves: the old vents were drawn mirrored).
  `fire_aimed` fires each fan shot from the barrel pointing nearest its way, and holds it if none
  does (the Wasp and Phantom already point at the player when they fire). `GunMuzzles.fire_all`
  fires every barrel (rings). The Scout, which flies nose-down, has a gun on a swivel
  (`Enemy.turret`, the bosses' `BossTurret`) turning at 150°/s to the player; a due shot waits until
  it points within 6°, and the model barrel turns and recoils. The Harrier, Hydra, Mortar and
  Rocketeer (missiles) and the lasers (Lancer, Prism, Sweeper, Scissor) are WPN-06 to WPN-09's
  slice; the Juggernaut's shoulder cannons already fire along their barrels.
- **Consequences:** a Scout over the player's own height cannot turn fast enough to fire; its shots
  wait while it flies past. Bosses (BOSS-29 turrets) are the next slice.
- **Status:** Proposed

### D-271 — Slice 3: missile flight and ports, laser lenses
- **Date:** 2026-11-05
- **Requirements:** WPN-06 to WPN-09.
- **Context:** owner: "do the missiles and lasers first".
- **Decision:** `EnemyMissileSpec.flight` (`MissileFlight`: launch seconds, climb seconds, arc
  radius, values in `game/config/weapons.py`). A missile flies straight for 0.25 s before the
  homing time runs (WPN-08). A missile from an upward silo (`BossMissilesShape.up`, true for every
  boss rack unless the volley says otherwise; river leviathan and glacier colossus fire forward)
  has a height: it climbs 0.3 s, points at the player, arcs down to the plane over πR of travel
  (R = 40, height `R·(1+cos πt)/2`), then homes. While its height is above 0 it is neither a shot
  target nor a hit on the player. The renderer raises it towards the camera by its height. In the
  models, `muzzle(at, kind, direction)` draws the port itself: kind "missile" a hexagonal port
  (`weapon_ports.hex_port`, standing up by default or "forward"), kind "laser" a hex barrel with
  two coils and a white-hot lens (`laser_lens`), as the Overlord's cannons, so every owner gets
  the same weapon with no per-model drawing. All lasers already shared one renderer (same warning
  line, beam and flare; only the owner's colour differs). The Harrier passed its raw config record
  as a spec; it now uses `missile_spec` like the others. The Hydra's heads, which fire from the
  eye at the player, keep a gun muzzle.
- **Consequences:** boss models that drew their own hatch or lens keep it under the new port; a
  boss's laser/missile muzzles are not yet barrels that recoil (WPN-05 slice).
- **Status:** Proposed

### D-272 — Scout redesigned as an airplane with a turret gun
- **Date:** 2026-11-05
- **Requirements:** ENM-SCOUT-01 to ENM-SCOUT-03, WPN-02.
- **Context:** owner: "redesign the scout, put his gun on a turret, no more insect wings, air plane
  wings and a bigger body".
- **Decision:** a fatter fuselage (4.2 wide, 5.2 tall), fixed metal swept wings with a neon leading
  edge and a tailplane (no `flap`), one reactor under each wing root, a fin, and a turret ring under
  the gun's pivot. The gun is raised to height 4.6 to sit on the ring. The footprint stays within
  ENM-12 (about 28 px).
- **Consequences:** the Scout has no fluttering wings; ENM-SCOUT-02's tail booms are gone.
- **Status:** Proposed

### D-273 — The Juggernaut's turret sweeps its spread with parallel barrels
- **Date:** 2026-11-05
- **Requirements:** ENM-JUGGERNAUT-11, WPN-01 to WPN-03.
- **Context:** owner: "rework the juggernaut dome, make all the barrels parallel, the turret shall
  turn while shooting and with a little delay between each canon the bullets will still shoot like
  a fan".
- **Decision:** a fixed collar and a turning mantlet (a slide of no recoil turning about the
  turret's pivot) with seven parallel barrels on `Enemy.turret` (240°/s). When a spread is due its
  seven headings are fixed, centred on the player, and the turret steps across them from the side
  it is nearest: each barrel fires in turn once the turret reaches its heading and `sweepGap`
  (0.08 s) after the last. Slides can now turn about a centre (`Slide.centre`) rather than their
  own root.
- **Consequences:** a spread takes about half a second to leave; the player can see it coming.
- **Status:** Proposed

### D-274 — The Hydra and the Juggernaut swap weapons and roles
- **Date:** 2026-11-05
- **Requirements:** ENM-HYDRA-09, ENM-HYDRA-14, ENM-HYDRA-15, ENM-JUGGERNAUT-06, ENM-JUGGERNAUT-10,
  WLD-4-17.
- **Context:** owner: "Switch Hydra and Juggernaut, make Hydra shoot bullets, replace Juggernaut arm
  canons with rocket launchers".
- **Decision:** the Hydra is tier 4's shooter: each head, in turn every 0.8 s, fires a burst of 3
  green bullets from a recoiling gun on its brow, along the head. The Juggernaut is tier 4's missile
  launcher: its shoulder cannons become hexagonal launcher tubes with a port at the tip, each
  launching the Hydra's former missile along itself every 2.4 s (straight out of the port first,
  WPN-08). The tier roles swap, so World 4's levels bring the Hydra in 4-1 and the Juggernaut in
  4-2, and the filler draws Splitters and Hydras; the world specs are updated to match.
- **Consequences:** the Juggernaut, the heavier kind, comes less often; the Hydra more.
- **Status:** Proposed

### D-275 — Hollow missile ports wider than their rockets, reloading
- **Date:** 2026-11-05
- **Requirements:** WPN-07.
- **Context:** owner: "for every rocket launcher, make the cannon bigger than the rocket, and the top
  shall be hollow until a rocket is here".
- **Decision:** a port's size comes from its missile's hit radius: the hexagonal bore's inner radius
  is 1.15 times the drawn rocket's (`ENEMY_LOOK.missile`), the wall 0.6 px; each launcher tube
  (Harrier rails, Rocketeer pods, Mortar barrel, Juggernaut arms) is as wide as its port all along.
  The port is a hollow well (one revolved profile: outer wall, rim, inner wall) with a dark floor.
  Each port's rocket is a sliding piece (`Slide.kind` "rocket") tied to `Enemy.launchers[index]`,
  a `Barrel` kicked as its missile leaves: hidden for the first 35 % of the 1.2 s reload, then
  rising up the well, eased out. Boss pieces report no launchers yet, so their ports are always
  loaded (their volleys' guns become per-port with WPN-05).
- **Consequences:** the Mortar's barrel is now a thick hexagonal tube.
- **Status:** Proposed

### D-276 — The Scout's turret further back, a bigger gun
- **Date:** 2026-11-05
- **Requirements:** ENM-SCOUT-03, WPN-02.
- **Context:** owner: "move the scout turret further to the back and make the canon bigger".
- **Decision:** the turret's pivot moves from 6 px ahead of the centre to 2 px behind it (config
  `turret.y` 2), its ring 3.6 px wide; the barrel is 9 px long and 1 px thick (was 6.5 and 0.6),
  so its tip is at `[0, -7.8, 4.9]`. Owner: the reactors were floating; each now ends a tapered
  nacelle (8.5 px, 1.9 px round its nozzle) that grows out of the fuselage's flank.
- **Status:** Proposed

### D-277 — The Scout is one blended airframe
- **Date:** 2026-11-05
- **Requirements:** ENM-SCOUT-01, ENM-SCOUT-02.
- **Context:** owner: "rework the scout body, no longer look like an insect, make it looks so the
  wings and engines are fully part of the body" (and, before, "remove the vertical wing").
- **Decision:** the flesh lobes, eyes and vein are replaced by a metal fighter fuselage
  (`FIGHTER_SECTION` loft, 5 px half wide in the middle, a point at the nose); wing-root fairings
  join the wings to the nose's flanks; the engines are hexagonal nacelles lofted into the
  fuselage's flanks, swelling round their nozzles; the fin is gone. The cyber-organic touch is a
  flesh canopy ahead of the turret, with a neon visor (ENM-35 still finds flesh on it).
- **Status:** Proposed

### D-278 — The Rocketeer's pods on one wing each, lit on their flanks
- **Date:** 2026-11-05
- **Requirements:** ENM-ROCKETEER-02.
- **Context:** owner: "don't highlight the barrel of the guns but their sides, make the pieces
  connecting the body to the guns a single wing, and make the wings cross the guns and show to the
  outer side of the ship".
- **Decision:** the two sinews per side become one swept metal wing from the body's flank (x 5)
  through the pod's middle to 7 px past its centre (3 px past the sac), with a neon light behind its
  leading edge on the part out past the pod. The vein along the top of each pod becomes two veins
  along its flanks. The model stays within ENM-12's footprint (about 47 px across, size 1.3 L).
- **Status:** Proposed
