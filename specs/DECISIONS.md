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
  Then (owner: "there is still a glow line at the front of the barrel, I only want the sides of the
  barrel to be highlighted. Also move the tip of the wings more to the front"): the Rocketeer's
  ports have no glowing rim (`muzzle(..., rim=False)`), its launchers' charge lights are two strips
  along their left and right edges, and the wing tips run from z 4 to 0 (were -1 to -5). Then
  (owner: "there is still a glowing line at the tip of the cannon, I want it gone, and replace the
  side yellow lines with highlight lines"): the line was the edge trim along the launcher's front
  edge (GFX-TRIM). Models get `EnemyParts.bare`, dark metal with no trim; the Rocketeer's launcher
  tubes and rimless ports are drawn on it, and its side lines are thin neon lines like the wings'
  (no longer the yellow charge strips).
  Then (owner: "make the darker tip longer so it merges into the body of the gun, remove useless
  geometry and get the hole in the barrel, I want to see the missiles coming out of the gun"):
  every enemy launcher tube (Rocketeer, Harrier, Mortar, Juggernaut) ran up to the mouth and its
  end cap closed the bore over the rocket. Tubes now stop where the port's well starts
  (`port_depth`); the Rocketeer's launcher is its port all along (`well` 7 px), with no tube.
- **Status:** Proposed

## D-279 — `make build` redoes only what changed (ENG-39)
- **Context:** the owner asked "rework the make build target so it only regenerate the files that
  needs it": every `make build` (and so every `make e2e`) re-ran `npm ci`, both Transcrypt builds
  with `-b` (every module), both esbuild bundles, and wiped and re-copied `dist/`, about 22 s.
- **Decision:** every build step is a file target. `npm ci` and the Playwright install leave
  stamps in `.make/` (git-ignored), redone after `node/package*.json` or `uv.lock` change.
  Transcrypt runs without `-b` (its own make mode recompiles only the modules newer than their
  JavaScript, and everything when its options change), one stamp per output directory
  (`build/game/.stamp`, `build/worker/.stamp`, `build/e2e/.stamp`) newer than every `src/**/*.py`.
  Each bundle is redone only after its Transcrypt stamp; `dist/index.html` after `index.html` or
  `src/build_info.py` (the commit); `public/` is copied (stamp `dist/.public`) when one of its files
  or Babylon.js changes. Babylon.js is checked again only when missing or after a Makefile change.
  The build checks (ENG-52, AUD-ENGINE-01) run with the step whose output they check, and a failing
  bundle is never left in place. `dist-e2e/` is rebuilt only after the e2e Transcrypt build or a
  `dist/` file changes.
- **Measured:** nothing changed 0.14 s; one module changed 1.9 s; from scratch 22 s as before. An
  incremental bundle is byte-identical to a clean one.
- **Limit:** a file removed from `public/` stays in `dist/` until `dist/` is deleted.
- **Status:** Proposed

## D-280 — Every boss shot leaves a gun mount; the core's guns go last (BOSS-58)
- **Context:** the owner asked to "apply the guns pattern to the bosses: one model for the guns, one
  for the lazer, one for the missiles", with every bullet, laser and missile "perfectly aligned with
  the guns", recoiling bullet guns, guns added where a pattern had none, and "when the player has
  destroyed the last remaining gun, the health shall hit zero". Most boss volleys (about 314 of 457)
  came from the core, from muzzles with no gun drawn; rings and fans left one point.
- **Decision (owner's choices):** the core is the last gun: it carries its own mounts and every
  part shields it. One barrel per bullet: a ring fires from a rotor with a barrel per bullet, a fan
  or a multi-shot aimed volley from the middle barrels of a fanned turret, counts snapped to the
  barrels. A boss's `mounts` (`boss_guns.gun_mount`, `laser_mount`, `missile_mount`) are data;
  `core/systems/boss_mounts.py` fires from them (each shot from a barrel's tip along it, the barrel
  kicked) and `view/bosses/boss_gun_models.py` draws them with the enemies' barrel, laser lens and
  missile port. A volley fires from the first mount of its piece that fits it, or the one it names.
  Parts hand the core their heading and age (a turned boss's guns turn with it; recoil on its
  clock). Hidden weapon kinds get one mount each; their pods stay. Rolled out on World 1 first,
  checked by the owner before Worlds 2–4.
- **Status:** Proposed

## D-281 — Laser at 125 % of the guns, missiles at 40 % (GAME-WPN-06, GAME-WPN-09, GAME-WPN-12)
- **Context:** with D-059 the laser dealt 80–100 % of the guns' damage per second and the missiles
  70 %. The missiles need no aiming at all (they home), so at 70 % they were the best pick almost
  everywhere, and the laser, which forces the ship to sit under its target, fell behind the guns
  above level 1.
- **Decision:** the guns stay the reference (the bosses were tuned with them, D-055). At every
  level the laser deals 125 % of the guns' damage per second (100 / 200 / 300 / 400 / 500): the
  owner asked for a laser "more powerful than the gun", since the guns' up to 5 streams are an
  advantage of their own. The missiles deal 40 % of the guns' (missile damage 14 → 8, same blast, rate and streams). The aim is that each weapon is
  the best pick for about a third of the waves.
- **Alternatives considered:** keeping 70–100 % and slowing the missiles' homing instead (keeps
  their strength against bosses, which do not dodge).
- **Consequences:** boss fight times with the guns are unchanged; with the laser they get shorter
  at every level, with the missiles longer. GAME-WPN-12's test checks the exact ratios.
- **Status:** Proposed

## D-282 — Heal bonus: 75 % of the weapon bonuses give back 20 % health (GAME-BONUS-11)
- **Context:** the owner asked to "add a Heal bonus that restore 20% of the player's health, replace
  75% of the current weapon upgrade bonus with this new one".
- **Decision:** a fourth bonus kind, `heal`. Every weapon bonus that drops (enemies, boss parts and
  cores, the final boss's sure drop included) turns into a heal bonus with 75 % chance, drawn from a
  source of its own (the run's seed + 3) after the weapon draw, so which enemies drop a bonus does
  not change (GAME-BONUS-05). It gives back 20 % of the ship's full health (20 for the Balanced, 28
  for the Heavy, 16 for the Light), never above full. It looks like a violet plus sign (its own
  shape, GFX-FX-12) and sounds like the life bonus's chime pitched up 4 semitones (`heal-bonus`,
  made from the same CC0 file).
- **Alternatives considered:** keeping the boss drops as weapon bonuses (fewer level-ups lost);
  a heal picked up at full health scoring points (as GAME-BONUS-10 does for lives and bombs).
- **Consequences:** a quarter of the weapon level-ups: from about 8 (1-1) to 23 (1-5) weapon bonuses
  per World 1 level (D-049) down to about 2 to 6; reaching level 5 takes several levels.
- **Status:** Proposed

## D-283 — Each level mixes enemy tiers by share of ships (ENM-50)
- **Context:** the owner asked: "1-1 shall have 80% of tier 1 enemies and 20% of tier 2, gradually
  more until 1-5 60% tier 1, 40% tier 2. 2-1 60% tier 2, 40% tier 1, 2-5 60% tier 2 40% tier 3 and so
  on. Each level shall have at least one example of each ship from each tier it has." Until then
  World N used only tier N, bringing its kinds in one role at a time (D-255).
- **Decision (owner's choices on the open points):** the share counts enemy ships (a Wasp group is
  5, filler included, carrier launches not). Worlds 2 and 3 keep their own tier at 60 % and slide the
  other 40 % linearly from the tier below to the tier above (10 points a level, so the middle levels
  mix three tiers); World 4 goes from 60 / 40 % (tier 4 / tier 3) to tier 4 only in 4-5; World 1 from
  80 / 20 % to 60 / 40 %. `tier_mix` gives each level's mix. `compose_beats` gives each beat to the
  tier furthest below its share (the filler that will follow a beat counted with it); each tier
  first brings its five kinds once (shooter, laser, missile, carrier, diver: the diver last, its
  waves being the biggest; a smaller tier one group each), then follows the role cycle. A wave
  brings no more groups than its tier lacks (the main tier never fewer than written), so a 10 % tier
  comes as small groups. The level composes its beats around the 10 s quiet stretch before each boss
  (`plan_beats`), so no beat bringing a kind is dropped there. The filler is the divers and
  shooters of every tier of the level; 1-1's stays the Hornet only (WLD-1-25: the Wasp shoots).
  Measured shares are within 5 points of the targets (unit test).
- **Consequences:** enemy HP per level (waves and filler, summed health) before → after, in
  thousands: World 1 6.6–11.4 → 7.8–11.0 (harder: tier 2 kinds and every tier 1 kind from 1-1);
  World 2 20–24 → 14–22 (2-1 lighter with tier 1); World 3 17–22 → 19–30; World 4 41–50 → 27–40
  (smaller waves: tier 4 waves are capped to the share too). The progression is steadier across
  worlds; World 4 is easier than before and may need its size factor raised. Ship counts per level
  change too (1-1 273 → 152, heavier kinds taking beats from Hornet and Scout waves). The per-level
  phrase tables in the level files no longer apply.
- **Status:** Proposed

## D-284 — Boss lasers follow the player at 12°/s, from every turret (BOSS-31)
- **Context:** the owner: "lower the rotating speed of the boss laser following the player,
  currently it's impossible to evade them". The laser rate (20°/s) applied only to turrets flagged
  as laser turrets (`turretLaser`, or a mount of kind `laser`); a laser fired from any other turret
  (a gun turret, BOSS-58 mounts) followed the player at the guns' 150°/s during its warning line and,
  for a sweeping beam, while it fired.
- **Decision:** every boss turret gets the laser rate, so while a laser of it shows it turns at
  `boss_laser_turn` whatever else it carries; the rate goes from 20 to 12°/s (about 63 px/s across
  at 300 px). The guns keep turning at 150°/s when no laser shows. The `turretLaser` flag in the
  boss data no longer changes anything.
- **Consequences:** sweeping beams and laser warning lines can be outrun everywhere; aimed lasers
  land a little further from a moving player.
- **Status:** Proposed

## D-285 — Grass and desert ground darkened under the brightness cap (GFX-READ-05)
- **Context:** the owner asked to resolve the strict xfails of GFX-READ-05: the grass greens of
  every world sat in the enemy family, and the desert browns, red rock and sand grains of Worlds 1
  and 2 in the enemy-shot family, above the 0.35 brightness cap. Owner's choice: darken them to the
  cap, keeping their hue.
- **Decision:** each texture holding such a colour (`GRASS`, `DESERT_ROCK`, `MESA_ROCK`,
  `DESERT_DIRT`, `DRIED_EARTH`, the sand's grains, the meadows' `lush` grass) has all its shades
  scaled by one factor, so its brightest flagged shade lands at 0.345: hue and the order of its
  shades kept. Factors: grass 0.70, lush grass 0.78, mesa rock 0.70, desert dirt 0.61, desert rock
  0.84, dried earth 0.86, sand grains 0.86.
- **Consequences:** grass and the desert ground are darker (desert dirt the most, about 40 %);
  enemies and shots stand out more on them. The palette unit tests run without xfail.
- **Status:** Proposed

## D-286 — Phone layout: menus across the window at their real size (UI-LOOK-02, UI-INPUT-11)
- **Context:** on a 390 × 844 phone the 16:9 stage, and the overlay scaled with it, is 390 × 219
  CSS px (scale 0.3): menus unreadable and touch targets of 13–17 CSS px. Two e2e tests were strict
  xfails waiting for "the mobile layout" (D-249). Owner's choice: build it.
- **Decision:** when the stage is scaled under `PHONE_SCALE` (0.5), `apply_stage_fit` gives the
  overlay the `phone` class; the menu overlay gives it `on-play` while a level is played with no
  panel over it. `#menu.phone:not(.on-play)` is fixed over the whole window, unscaled (one CSS
  pixel per logical pixel), so every screen, the pause menu, the settings and the end panels are laid
  out at their real size over the canvas, the HUD hidden under them. During play the overlay keeps
  to the 16:9 box, so the HUD lines up with the playfield. The level cells are 60 px there, so a row
  of five fits 390 px.
- **Alternatives considered:** bigger logical targets inside the 16:9 box (a 44 CSS px target would
  need about 150 logical px, so the level grid could not fit); a separate phone UI.
- **Consequences:** the 3D ships of the ship select stay in the 16:9 band while their cards sit at
  the bottom of the window, no longer under each ship. The HUD during play is still the small one.
- **Status:** Proposed

## D-287 — One tap or click selects and confirms (UI-INPUT-09)
- **Context:** the owner: "make it so a single click is enough for the UI buttons". A tap on an
  entry that was not selected only selected it; a second tap confirmed it.
- **Decision:** a tap sends the entry's selection then Confirm (`pointer_commands`), so one tap
  acts on every menu, the pause menu and the end panels. The dev viewers (`dev-viewer`,
  `dev-audio`) keep the two steps: picking an item there shows or plays it. The ship and level
  select hints say "tap to go".
- **Consequences:** a mis-tap on a menu goes straight through (a locked level still only shakes).

### D-288 — An AI player (`tests/ai/`) that learns the game and rates its levels; torch and numpy
- **Date:** 2026-11-07
- **Requirements:** none yet (requested by the human: `make learn`, `make rate`; the brain kept in
  `data/`); ENG-05 (new dev dependencies); ENG-18 (the AI is not `core/`).
- **Context:** the human wants a neural network that learns to play the game, then rates how hard
  each level is (as a percentage), to tune the levels' difficulty with it. Pure Python, no
  JavaScript, as fast as the CPU goes, all of it in a package under `tests/`.
- **Decision:** the package `tests/ai/` runs the game's own simulation in CPython: `game_env.py`
  builds a `LevelRun` as `app/game_play.py` does (same playfield, ship, weapons, bonuses, bombs,
  hull, bosses; the camera framing for the flight bounds and what is on screen; no fly-in journey,
  a 30 px muzzle offset instead of the one measured on the 3D model), steps it 4 fixed steps
  (1/60 s) per decision (15 decisions a second), and wraps the wave scripts' plain dicts as
  attribute records (the browser reads object literals as attributes). The brain sees two grids of
  16 channels (the whole playfield in 24 x 32 cells, and a 21 x 21 fovea of 12 px cells around the
  ship): enemies, boss pieces, their health, bullets / missiles (each with their velocity), laser
  warning lines and beams, the weapon / life / bomb bonuses, the ship, and where it cannot fly; and
  24 numbers (ship, health, lives, bombs, weapons, progress, boss, difficulty). The network
  (`brain.py`, about 2.5 M weights): two small convolutional encoders and a state MLP, a GRU (its
  memory), and heads for the move (9 directions), the bomb, the weapon switch, and the value; fire
  is always held. It learns by recurrent PPO (`learn.py`): worker processes play 12 episodes each
  while the learner updates from the previous round (one update late), sequences of 32 decisions
  replayed through the memory. The curriculum draws the level, a start anywhere in it (60 %), the
  weapons and their levels, lives, bombs and ship at random. The reward: progress, points, damage
  dealt and bonuses picked up, minus damage taken, lives lost, bombs used and the game over; plus a
  completed level. `make rate` plays each level 8 times (seeds 1000…) from its start with the same
  loadout (Balanced ship, every weapon at level 3, 3 lives, 3 bombs), greedy, and rates an episode
  `1 - (progress + health left) / 2`; a level's rating is the mean, in percent
  (`data/ratings.json`). `data/brain.pt` holds the weights and the learning stats,
  `data/brain.trainer.pt` the optimiser (to resume), `data/learn-log.csv` one line per update.
- **Dependencies (ENG-05):** `torch` (BSD-3-Clause; the CPU-only wheel, from the PyTorch CPU index
  on Linux so no CUDA libraries are installed; about 200 MB installed) for the network and its
  training; `numpy` (BSD-3-Clause, about 40 MB) for the observation grids. Both in the `dev` group:
  the game itself still has no Python run-time dependency.
- **Alternatives considered:** driving the browser build through Playwright (real time, and
  JavaScript); a numpy-only network (no automatic gradients for the GRU); a feed-forward network
  with stacked frames instead of a memory (the human asked for memory); stable-baselines3 / sb3-
  contrib's recurrent PPO (one more dependency, and its single-process loop wastes the cores).
- **Consequences:** about 700 decisions a second on 8 CPU cores (2.5 M an hour; the learner's
  backward pass is the bottleneck), so a competent brain takes hours to days of `make learn`; the
  ratings are relative to the brain's skill (a better brain rates every level easier); levels with
  enemies the CPython run had never met turned up two bugs of the browser game (see the next
  bullet).
- **Game bugs found (fixed):** the Harrier fired its missiles with its raw config record (keys
  `turnRateDeg`, `homingSeconds`) instead of an `EnemyMissileSpec`, and the Lancer its laser with
  its raw record (`warningSeconds`, `firingSeconds`) instead of an `EnemyLaserSpec`: `core/` read
  `undefined` in the browser (a NaN turn rate for the missiles; a laser with no warning that never
  ended). Both now build their spec as the Rocketeer, Sweeper and Scissor do; their unit tests
  asserted the raw record and now assert the spec.
- **Spec follow-up (owner's to edit):** ENG-37 lists the public make targets; `learn` and `rate`
  are new public targets (in `README.md`) and are not in it yet.
- **Lint:** `tests/ai/*` may `print` (T201), read the clock (TID251) and use `random` (S311): it is
  a command-line tool, not the deterministic simulation those rules protect.
- **Status:** Proposed

### D-289 — The AI player learns on an NVIDIA GPU, with every CPU core playing
- **Date:** 2026-11-07
- **Requirements:** none (requested by the human: make `make learn` faster on a server with an
  RTX 2060 and 64 CPU threads); ENG-05 (the CUDA build of torch).
- **Context:** on a CPU the learner's backward pass is the bottleneck (D-288): a third of the cores
  play, the learner has the rest. With a GPU the learner is fast, so many more cores can play; a
  round of 60 workers is then over a gigabyte of observations, too much to pickle through pipes.
- **Decision:** torch leaves the `dev` group for two groups that cannot be installed together:
  `ai-cpu` (a default group, the CPU-only wheels: `make check`, `make tests` and CI unchanged) and
  `ai-cuda` (the CUDA 12.6 wheels, torch 2.14.1: the newest torch with CUDA 12 wheels; any driver
  >= 525, Turing GPUs included; torch 2.15 has CUDA 13.2 wheels only). `make learn AI_TORCH=cuda`
  installs and uses it (`make rate` too). `ai.learn --device auto` (the default) learns on the GPU
  when torch sees one, with every core but two playing 8 episodes each and rounds of 64 decisions. The workers write their rounds into two rollout buffers in shared memory
  (`/dev/shm` files mapped by every process, in turn: one is played into while the learner learns
  from the other) and send back only the episodes' summaries; the weights are pickled once a
  round for all of them. The minibatches are a share of the round (12 an epoch), not a fixed size.
  `make rate` plays fewer episodes side by side when there are many cores, so none is idle.
- **Measured** (`glouton`: 2 x Xeon E5-2697A v4, 32 cores / 64 threads, RTX 2060): about 11,000
  decisions a second (2,800 with the CPU build on the same machine, 600 on an 8-core laptop). The
  playing is then the bottleneck: a worker alone plays 680 decisions a second, 180 with the 62
  others (the game's simulation is 52 % of it, the observation 25 %, the network 13 %); the GPU is
  about a third busy. More episodes per worker (16), fewer workers (31) or 3 epochs a round
  instead of 2 (8,800 a second: the learner's own CPU work slows the workers) were no faster.
- **Alternatives considered:** a central inference server on the GPU for the workers (the network
  is only 13 % of a worker's time); half-precision training (the learner already waits for the
  workers); CUDA 13.2 wheels (they need a driver >= 580 and give nothing more here).
- **Consequences:** on the GPU machine `uv run` without the group (as `make tests` does) switches
  torch back to the CPU build, and `make learn AI_TORCH=cuda` back again (a re-install of a few
  seconds from uv's cache); the lock file holds both builds. Faster still means a faster game
  simulation (`src/core/`), which is the game's code, not the AI's.
- **Status:** Proposed

### D-290 — `make serve-ai`: the brain plays the real game in a browser window
- **Date:** 2026-11-07
- **Requirements:** none (requested by the human: open a browser and watch the AI play the level
  chosen); DEV-API-01 (a sixth test API function); ENG-52 (test API in the e2e build only).
- **Context:** the brain decides in Python (D-288); the browser game is the JavaScript build.
  Replaying a Python run in the browser would need the two runtimes to stay bit-identical for
  minutes (their `sin`/`cos` may differ in the last bit, and the runs would drift apart); the test
  API's `getState()` gives counts, not where things are.
- **Decision:** the e2e build's test API gets `getScene()` (`src/debug/play_scene.py`): what is on
  the playfield of the level played, as plain arrays (the ship, its hull, bombs and weapons, the
  level's progress, the boss, and the position of each enemy and boss piece, bullet, missile,
  laser and bonus). `tests/ai/watch.py` serves `dist-e2e/`, opens it in a Chromium window
  (Playwright, already a dev dependency) and steps it at 60 frames a second (the e2e build only
  moves when stepped). While a level is played (not paused, not over) it reads the scene every 4
  frames, the brain decides, and it holds the game's own keys (arrows, Space, R, E) through the
  page; out of a level it lets go and the human uses the menus. The training builds its
  observations from the same `play_scene` (its two JavaScript helpers swapped for Python ones), so
  what the brain sees while watched is exactly what it learned from. `make e2e-build` is now a step
  of its own (ENG-37 already named it), used by `e2e` and `serve-ai`.
- **Alternatives considered:** the browser asking a Python server for each move (a change to the
  game's loop and input for a dev tool); a 2D replay of a Python run drawn on a canvas (not the
  real game); replaying the moves of a Python run (the runs drift, see the context).
- **Consequences:** `?level=` (with `make serve-ai LEVEL=...`) starts the level in debug mode
  (DEV-OPT-01). The watch is as fast as the browser draws: with software WebGL (no GPU) a frame
  takes some 200 ms (`WATCH_ARGS="--draw-every 4"` draws fewer). The scene of the browser's run
  comes from the JavaScript simulation, so the brain plays the very game a player plays.
- **Spec follow-up (owner's to edit):** DEV-API-01 lists five test API functions, now six
  (`getScene`); ENG-37's public targets lack `learn`, `rate` and `serve-ai`.
- **Status:** Superseded in part by D-291 (the server and the in-page player replace the
  Chromium window driven by Playwright; `getScene()` and the shared `play_scene` stay)

### D-291 — `make serve-ai` serves the game; the page asks the brain for its keys
- **Date:** 2026-11-07
- **Requirements:** none (requested by the human: no Chromium window of its own, it is slow in
  WSL; open the game in any browser); ENG-52 (the e2e build only).
- **Context:** D-290 stepped the game from Python through Playwright, so it needed a Chromium the
  script launched, which draws with software WebGL under WSL (some 200 ms a frame).
- **Decision:** `make serve-ai` starts a local HTTP server (`tests/ai/watch.py`, port 5174,
  `SERVE_AI_PORT`) of the e2e build, which sends `/` on to the game with `?ai` (and `level` and
  `ship` when given). With `?ai` (`ai_mode`, `app/debug_options.py`) the e2e build runs as the
  production game does (its own render loop, full render scale, shaders compiled ahead) with its
  test API on, and `debug/remote_player.py` posts the level played (its id, attempt, time,
  duration and `play_scene`) to `POST /ai` about every 4 frames (an interval of 4/60 s), one
  question at a time. The server's brain answers with the key codes to hold, which go to the
  level's controls (`controls.key`, as the keyboard's do); a held key is sent down again at each
  answer (no new press: the controls count presses on their transitions), so a lost focus does not
  leave it let go. Out of a level, while paused or over, or without an answer, every key is let go.
- **Alternatives considered:** keeping Playwright with the host's Chrome (`channel`), which WSL
  cannot reach; a WebSocket (one more protocol for 15 small questions a second); synchronous
  requests (they would stall the page's frame).
- **Consequences:** the brain decides on the wall clock (every 4/60 s), not every 4 frames, so at
  a frame rate under 60 it decides more often per frame than it learned; an answer reaches the
  game one frame or so after its question. `--host 0.0.0.0` serves it to other machines (glouton).
  The production bundle has none of it (the `ifdef e2e` block; `make build` checks
  `__GAME_TEST__` is absent).
- **Status:** Proposed

### D-292 — The AI player draws its moves (not the likeliest one) when watched and rating
- **Date:** 2026-11-07
- **Requirements:** none (the human saw the brain hold the ship in the bottom-left corner, firing
  missiles only, in `make serve-ai`).
- **Context:** the brain (1.8 h of learning) is a policy: a probability over its 9 moves, still
  wide (its first decision of 1-1: 60 % south-west, the rest spread). `serve-ai` and `make rate`
  played its likeliest move only, which turned that into "hold south-west". Measured on 1-1, 1-4,
  2-3, 3-1 and 4-2 (two seeds, missiles at level 3): camping in the corner reaches 71 % of the level
  and completes none; random moves 83 %, 60 % completed; the brain's likeliest moves 100 %, 90 %
  completed with 4.7 lives' worth of damage; its moves drawn 100 %, all completed, 2.2 lives'
  worth. It sees and dodges; its likeliest move alone hides it.
- **Decision:** `make serve-ai` and `make rate` draw the moves as the brain learned to play
  (`--greedy` for the likeliest). A rating episode draws from a generator of its own, seeded by the
  episode, so the ratings are the same however episodes are batched or how many cores there are.
  Ratings made before (`data/ratings.json`) used the likeliest moves.
- **Finding (for the game's balance):** the brain switches to the missiles and keeps them. With
  random moves (no aiming), at level 3 on the same levels with three seeds: bullets reach 36 % of
  the level (50 kills, none completed), the laser 33 % (29 kills, none), the missiles 81 % (242
  kills, 60 % completed). Homing missiles need no aiming; whether they are too strong is the owner's
  call (GAME-WPN).
- **Status:** Proposed

### D-293 — The watched brain decides every 4 steps, and taps its bomb and switch keys
- **Date:** 2026-11-07
- **Requirements:** none (the human saw the brain stay in the bottom-left corner in
  `make serve-ai`, not dodging and not picking up bonuses).
- **Context:** the same brain, fed the same scenes, moved over the whole screen in the Python game
  and stayed in the corner in the browser (the scenes were checked equal, to the bullets'
  coordinates). Two differences with how it learned: (1) D-291 asked on the wall clock, so with a
  slow drawing many steps passed between two decisions (some 23 instead of 4 in a headless
  browser); (2) a decision to switch weapon (or to set a bomb off) is one press of E (R) in
  learning, but the page held E down: one press for all the decisions after. The brain wants to
  switch at the start of a level until it has the missiles (99 % at its first decision) and keeps
  to its opening (down-left) meanwhile: with one press it never got there.
- **Decision:** the game session calls `step_watchers` after each step of a level (with the audio;
  `RunningApp.watch_steps`); the remote player asks after every 4th step and waits for the answer
  (a synchronous request: the page waits a few milliseconds for the brain), so the keys apply from
  the next step, as in learning, however fast the page draws. The answer is `[hold, tap]`: the
  arrows and Space are held; E and R are tapped (down and up before the next step: one press each
  decision that chooses one). The interval only lets the keys go out of a level.
- **Consequences:** in a headless browser the brain now moves over the whole screen, takes the
  missiles within 4 s and sets bombs off, as in the Python game. It still goes back to the corner
  often: after under 2 hours of learning, that is how it plays. A browser warns that synchronous
  requests are deprecated on the main thread (e2e build with `?ai` only).
- **Status:** Proposed

### D-294 — The AI player starts every level afresh, apart from the player's save
- **Date:** 2026-11-07
- **Requirements:** none (requested by the human: in `make serve-ai` the brain started with 60
  bombs and every weapon at level 5; it must start with 3 lives, 3 bombs and level 1 weapons, and
  get more only from the bonuses it picks up). GAME-WPN-15 and GAME-LIFE-12 (what is kept from a
  level to the next) do not apply to it.
- **Context:** the page kept the weapons and supplies of the levels completed before in its
  cookies, which every port of `localhost` shares: the AI's page read the player's save (and its
  own wins piled up in it), and wrote the AI's into the player's.
- **Decision:** with `?ai`, the page's storage is a `FreshStartStorage` (`src/debug/`, e2e builds
  only): in memory, for the page's life, never keeping the weapons and supplies. Every level then
  starts as from the level select with nothing kept; a Continue after a game over still starts from
  the checkpoint (its weapons, GAME-LIFE-11). The volumes, last ship and high score are kept for
  the page's life only. `make rate` rates with the same fresh start (every weapon at level 1, was
  3; `--weapon-level` changes it), and the learning episodes that start at a level's start (40 %)
  have it too (3 lives, 3 bombs, the first weapon at level 1); those that start in the middle keep
  loadouts that vary.
- **Consequences:** checked in a browser with a saved 60 bombs and level 5 weapons: the normal page
  starts with them, the `?ai` page with 3 lives, 3 bombs and the bullet at level 1. Ratings made
  before were with level 3 weapons.
- **Status:** Proposed

### D-295 — The brain learns on whole games, from 1-1 until the ship is lost, for the best score
- **Date:** 2026-11-07
- **Requirements:** none (requested by the human: learning games start at 1-1 with 3 lives and 3
  bombs, go on to the next level when one is cleared with the weapons, lives and bombs earned,
  until death or the last level (4-5) is cleared; the best score is the criterion; `make learn`'s
  output easier to understand). Replaces the curriculum of D-288 and D-294.
- **Decision:** `GameEnv(setup, campaign=LEVEL_IDS)`: when a level is cleared, the next starts
  (a new `LevelRun`, full health) with the weapon in use, the weapon levels, the lives and the
  bombs the cleared one ended with (GAME-WPN-15, GAME-LIFE-12), a seed of its own and its own time
  limit (its length + 240 s); the episode ends at a game over, a level over its limit, or 4-5
  cleared. Every learning episode is such a game, with the balanced ship only; no more starts in
  the middle of a level. The reward is the points scored (1 per 2000), nothing else: progress,
  damage, lives, bombs and bonuses pay only through the points they lead to (a life lost ends the
  scoring sooner). `gamma` 0.998 (was 0.995): about 30 s of play ahead. The brain whose games
  scored best on average over at least 20 games (one report's or more) is saved in
  `data/brain-best.pt` (`LearnStats.best_score`). `make learn` now says, every 10 s (`--report-seconds`), in words:
  the games ended and how (game over, too slow, all cleared), their average and best score, the
  levels cleared and the furthest reached, and the best average so far; the per-update numbers
  (losses, entropy, KL) go to `data/learn-log.csv` only, with new columns (an older log is moved
  to `learn-log.old.csv`). `make rate` and `make serve-ai` are unchanged (one level at a time).
- **Consequences:** the brain trained before resumes, but its value estimates were for the old
  reward: the first minutes relearn them. Later levels come up only once the brain gets that far,
  so they are learned late. Games last until the ship is lost: early reports can have no game
  ended yet.
- **Status:** Proposed

### D-296 — Faster learning: a cheaper view, and a little reward for staying alive
- **Date:** 2026-11-07
- **Requirements:** none (requested by the human: speed up the learning, by learning on the GPU
  machine, a faster observation, and a reward for staying alive). Amends D-295's reward.
- **Context:** a worker spent about 43 % of its time in the game, 32 % in the network and 20 %
  building what the brain sees; within that, a third went to the walls of the fovea (the camera
  framing worked out row by row) and most of the rest to drawing each shot in three channels.
- **Decision:** the fovea's walls are worked out for every row at once
  (`_Bounds.half_widths_at`, the same sums as `half_width_at`); each shot is placed once for its
  three channels; an enemy's cells are worked out once for its body and its health. The
  observation is the same, cell for cell (checked on 420 scenes of 7 levels), in about half the
  time (156 to 83 µs on the laptop). The reward adds 0.0005 a decision played (a point of score
  each, 15 a second), and charges 1 per bar of health lost and 1 per life lost (2,000 points
  each): the brain learns sooner that it scores only while it survives. The best brain is still
  chosen on the score alone.
- **Consequences:** about 10 % more moves a second per worker. The values the brain expects
  change again with the reward: its first minutes relearn them.
- **Status:** Proposed

### D-297 — A faster simulation for the AI player, the game played exactly as before
- **Date:** 2026-11-07
- **Requirements:** none (requested by the human: speed up the game's simulation for learning).
- **Context:** in CPython the simulation's time is spread over many small functions; the player's
  shots (moving them, and testing each against every target) were the largest share (about a
  quarter), then the enemies and bosses.
- **Decision:** the shots' hit test reads the shot's fields once and a target's health directly
  (`ShotWorld._collide`); the AI's on-screen test reads the camera's constants once
  (`_Bounds.in_view`, the same sums in the same order); a config record read in CPython is
  `dict.get` itself (`_Fields.__getattr__`, CPython only). The browser's game is unchanged in
  behaviour.
- **Consequences:** about 6.5 % more simulation steps a second (53 to 50 µs a step on the
  laptop). The same 30,000 decisions over the 20 levels play out identically (a fingerprint of
  every decision's state). The rest of the time is spread thin over the game's logic: larger
  gains need another approach (the network on the GPU, fewer decisions a second).
- **Status:** Proposed

### D-298 — With a GPU, one inference server decides for every worker
- **Date:** 2026-11-07
- **Requirements:** none (requested by the human: run the brain on the GPU for the workers, to
  learn faster).
- **Context:** each worker ran its own copy of the brain on its CPU core, for batches of 8
  episodes: about a third of its time.
- **Decision:** with `--inference server` (the default with a GPU), one process
  (`tests/ai/inference.py`) holds the brain on the learner's device and the memory of every
  episode. A worker (`ServedPlayer`) writes what its episodes see into the shared rollout and asks
  "decide for episodes a to b at step t"; the server batches every question waiting, decides, and
  writes the actions, log-probabilities, values and memories into the rollout, then answers. Only
  those small messages go through the pipes. A worker's episodes are in two groups, so it plays
  one while the server decides for the other. The value after a round's last decision comes from
  what the episodes see then (`next_*` arrays of the rollout buffer). The learner sends the server
  the weights before each round, as it did to the workers; the learner and the server take a core
  each (workers: the CPU threads less 3). On a CPU only, the workers still decide themselves.
  The server draws the actions and their log-probabilities without building PyTorch's
  distributions (`Decision.sample_with_log_prob`), gathers what the episodes see into pinned
  memory (one copy each to the GPU), and brings what it decided back in one copy: its first
  version spent 8 ms a batch on that and held glouton at the same 10,000 decisions a second.
- **Consequences:** the same decisions as the brain would make, step by step (a unit test replays
  them). On the laptop (8 threads, the server on the CPU) 1,884 decisions a second against 1,639.
  On glouton's GPU, the server alone answers batches of 30 questions (120 episodes) in 3.2 ms
  (was 7.7): about 38,000 decisions a second, more than the workers can play.
- **Status:** Proposed

### D-299 — A faster learner: whole sequences through cuDNN's GRU, and mixed precision
- **Date:** 2026-11-07
- **Requirements:** none (requested by the human: use glouton's idle CPU and GPU).
- **Context:** with the inference server (D-298) and 16 episodes a worker, glouton played about
  15,600 decisions a second, its CPUs 40 % busy: the workers played a round faster than the
  learner learned from the one before (1.9 s an update), and waited. The learner replayed the
  memory step by step (a `GRUCell`, 32 small steps forward and backward each minibatch).
- **Decision:** the memory is an `nn.GRU` (cuDNN's on a GPU): the learner replays every sequence
  in which no episode starts after its first step in one call, the others step by step as before.
  A brain saved with the `GRUCell` loads into it (the same weights, renamed; its optimiser's state
  fits). With a GPU the learner computes in half precision where it is safe (autocast, the losses
  scaled), the losses in full precision, and reads them once an update rather than once a
  minibatch. With a GPU, 16 episodes a worker and rounds of 32 decisions are the defaults.
- **Consequences:** an update of 31,232 decisions takes 1.1 s on glouton instead of 1.5 (both
  measured beside a running learner). The same decisions, step by step (unit test).
- **Status:** Proposed

### D-300 — `make learn` reports the games in progress and the best game so far
- **Date:** 2026-11-07
- **Requirements:** none (requested by the human: more explicit reports, with the best game so
  far).
- **Decision:** after each round every worker sends, with the games that ended, how each game it
  is playing stands (`GameProgress`: level, levels cleared, score, moves). Each report (every
  10 s) now says: the games being played (how many, their average moves, play time and score,
  how many got past 1-1, the furthest level), the one leading now, the games that ended since the
  last report and how, and the best game since learning started (score, level reached, levels
  cleared, play time, how it ended, at which update). The best game is kept in the brain's stats
  (`LearnStats.best_game`), so it survives a restart.
- **Status:** Proposed

### D-301 — The workers play under PyPy; what the brain sees is built in pure Python
- **Date:** 2026-11-08
- **Requirements:** none (requested by the human: simulate a whole level in seconds, not in about
  real time, "go with PyPy"). Amends D-288, D-298.
- **Context:** the game's simulation took about 50 µs a step in CPython (a 5-minute level is
  about 1 s of CPU), yet each game played about as fast as real time while learning: every worker
  played 16 games, built a numpy observation and waited for the brain every 4 steps, beside 61
  other workers on 32 hyperthreaded cores. Measured on a whole level with no brain (1-1, 4-5):
  PyPy 3.12 plays the same steps 4.7 to 5 times faster once its JIT is warm (the same scores to
  the point); the Transcrypt JavaScript under Node is slower than CPython. PyPy has no PyTorch,
  and its numpy is slow.
- **Decision:**
  - The workers are `python -m ai.play_worker` processes of PyPy (`--worker-python`, default
    PyPy 3.12 when `uv python find` sees it, else the learner's CPython), started with
    `subprocess`. They import no numpy and no torch: `game_env.py`, `episodes.py`, `sight.py`,
    `layout.py` and `play_worker.py` are pure Python (a unit test checks it).
  - The brain always decides in the inference server (D-298), on the GPU or the CPU: the
    in-worker brain is gone. On a CPU, half the cores play and a quarter decide.
  - What the brain sees is built in pure Python (`sight.py`): the non-zero cells of each grid,
    which a worker writes into the shared rollout file with `struct.pack_into` on an `mmap` (under
    PyPy several times faster than a `memoryview`'s items). `observation.py` makes numpy arrays of
    them for `make rate`, `make serve-ai` and the tests. The two views agree to 2.4e-7 with the
    numpy one they replace (1,200 scenes of four levels).
  - The rollout file's layout is computed once in pure Python (`layout.py`), for numpy and for the
    `mmap` alike.
  - The learner and the server talk to a worker through `multiprocessing` pipes whose file
    descriptors the worker inherits (PyPy and CPython frame their messages alike); the reports are
    dataclasses both runtimes import (`episodes.py`).
  - The field grid is 18 x 24 square cells of 30 px, for the 3:4 playfield of D-263 (it was 32 x
    24 for 1000 x 720). Brains saved before cannot be loaded: `make learn` starts a new one, and
    `make rate` / `make serve-ai` say so.
- **Consequences:** on the laptop (one worker, 16 games, warm JIT) a worker plays about 9,000
  decisions a second against 3,200 in CPython (2.8 times: the simulation 3 times, the sight 2.8
  times faster); PyPy's JIT takes a few minutes to warm up. With the GPU, the inference server
  (about 38,000 decisions a second, D-298) and the learner (about 28,000, D-299) become the
  limit, no longer the workers. On a CPU only, the learner is the limit. `make learn` installs
  PyPy 3.12 with uv.
- **Status:** Proposed

### D-302 — A small brain to try: 70 thousand weights instead of 2.2 million
- **Date:** 2026-11-08
- **Requirements:** none (requested by the human: a brain file of tens of kilobytes, like another
  game's 64 KB `brain.npz`, instead of about 10 MB). Amends D-299.
- **Context:** the brain had 2.24 million weights (about 9 MB in float32). Most of them were in
  the two Linear layers after the grid encoders' convolutions (the field and the fovea, still
  6 x 5 and 6 x 6 cells of 64 filters after two convolutions of stride 2) and in the 384-wide GRU.
- **Decision:**
  - `BrainShape.convs` gives the filters of each convolution of the grid encoders (all of stride
    2). A brain saved without it has the two convolutions of 32 and 64 filters it had.
  - `SMALL_SHAPE`: three convolutions of 16 filters (each grid down to 3 x 3 before its Linear),
    64 features for the field, 64 for the fovea, 32 for the state, a memory of 64. It has 69,742
    weights (about 136 KB in float16), 32 times fewer than the big one.
  - `make learn LEARN_ARGS="--fresh --shape small"` starts a small brain (`--shape big`, the
    default, the big one). A saved brain keeps its own shape when learning resumes; `make rate` and
    `make serve-ai` load either.
- **Consequences:** an experiment: whether the small brain plays nearly as well as the big one
  after as many hours of learning is to be measured (`make rate`). If it does, the brain could be
  saved as float16 weights to make its file smaller still.
- **Status:** Proposed

### D-303 — `make rate` plays up to 32 episodes side by side in each worker
- **Date:** 2026-11-09
- **Requirements:** none (requested by the human: `make rate` is too slow). Amends D-289.
- **Context:** a rating worker played at most 4 episodes side by side (`GROUP`), and the network
  was 80 % of its time. On one CPU thread a call to the network costs nearly the same for 1
  episode as for 32: the big brain 3.3 ms for 4 episodes and 4.5 ms for 32 (0.82 ms an episode
  against 0.14), the small one (D-302) 0.42 ms an episode against 0.08. A rating plays about a
  million decisions (8 episodes of 20 levels, about 7 minutes of game each).
- **Decision:** `GROUP` is 32: with 160 episodes on 8 cores, each worker plays its 20 in one
  batch. Each episode still draws its moves from its own seeded generator: the ratings repeat.
- **Consequences:** a decision costs 0.57 ms an episode with the big brain instead of 1.45 (2.5
  times faster), 0.52 instead of 1.12 with the small one. The network is then 55 % of the time,
  the simulation and the observation 35 %. Fewer, longer jobs: a worker whose episodes are on long
  levels may finish last. Rating with `make learn`'s PyPy workers and inference server would be
  faster still (not done).
- **Status:** Proposed

### D-304 — `make rate` gives the weapons the level of the world
- **Date:** 2026-11-09
- **Requirements:** none (requested by the human: in world 2 the player starts with level 2
  weapons, in world 3 level 3, in world 4 level 4). Amends D-294.
- **Context:** every level was rated from a fresh start, every weapon at level 1 (D-294). A
  player reaching world 4 has upgraded weapons: level 1 made the later worlds look harder than
  they are when played through.
- **Decision:** a level of world N is rated with every weapon at level N (at most the top level,
  5). `--weapon-level` still gives every level the same one; `RatingSettings.weapon_level` is
  `None` (by world) by default. Lives and bombs stay 3 and 3.
- **Consequences:** the ratings of worlds 2 to 4 are not comparable with those made before;
  `ratings.json` records `"weapon_level": null` for them.
- **Status:** Proposed

### D-305 — `make adjust-level`: tune a level until the brain rates it at a target
- **Date:** 2026-11-09
- **Requirements:** none (requested by the human: `make adjust-level 4-4 90` adapts 4-4 until it
  rates 90 %). Builds on D-289 (`make rate`) and D-304.
- **Context:** `make rate` measures each level's difficulty with the brain; balancing a level
  meant editing its factors by hand and rating again. A level's own tuning was its enemies'
  bullet speed and fire rate (ENM-22); its bosses' health was only written per boss, inside each
  boss's file.
- **Decision:**
  - A level's difficulty gets a third factor, `bossHealth` (`EnemyDifficulty.boss_health`,
    default 1): when a boss arrives, its core and every part get that many times their health
    (`Boss.scale_health`, applied by `BossFights`). Every level's is 1 (no change in play).
  - `make adjust-level LEVEL=4-4 TARGET=90` (`tests/ai/adjust.py`) turns one dial `k` that
    multiplies the three factors together (k = 1: the level as it is). Each step rates the level
    as `make rate` does, with the same seeds (two steps differ by `k` alone); `k` grows or shrinks
    by 1.25 until the target is bracketed, then is interpolated between the closest ratings either
    side. Episodes start at 16 and double once bracketed, up to 64. It stops within 2 % of the
    target (or within two standard errors at 64 episodes), after 10 steps at most.
  - The factors tried reach the episodes through `EpisodeSetup.difficulty`: no file changes during
    the search. At the end the level's line in `src/game/config/world_N/difficulty.py` is written
    (factors rounded to 0.01), and the steps are kept in `data/adjust-<level>.json`.
  - `k` stays within 0.5 … 2 and no factor passes 2 (the config checks' ceiling). When the dial
    runs out before the target, nothing is written.
- **Consequences:** the specs' "Difficulty" requirements of each level (e.g. LVL-4-4-05) and the
  worlds' tunables tables still give the old factors: the tool names those files, and the human
  updates them. It warns when the new factors make bullet speed or fire rate go down from one
  level to the next (WLD-N-19), which the unit tests check. A tuned level is tuned for the brain
  that rated it: a better brain rates every level easier.
- **Status:** Proposed

### D-306 — The brain file keeps float16 weights and no learning history
- **Date:** 2026-11-09
- **Requirements:** none (requested by the human: a smaller brain file). Follows D-302.
- **Context:** the small brain's file (D-302) was 622 KB: 288 KB of float32 weights and 262 KB of
  learning history (`LearnStats.history`, the last 2 000 updates), which the learning log
  (`data/learn-log.csv`) already has row by row.
- **Decision:** `save_brain` writes the weights in float16 and `load_brain` turns them back to
  float32; `LearnStats` has no `history` (an older file's is ignored when loaded). `make learn`
  also saves its float32 weights in the trainer file (`brain.trainer.pt`, never committed) and
  resumes from them when they fit the brain, so its restarts do not round the weights.
- **Consequences:** the small brain's file is 148 KB. On 30 game states, the float16 brain's move
  probabilities differ from the float32 one's by at most 0.0002 and its likeliest move is the same.
  A brain resumed without its trainer file starts from the rounded weights (a negligible change).
- **Status:** Proposed

### D-307 — Every enemy and boss is the same in every level; levels differ by their enemy count
- **Date:** 2026-11-09
- **Requirements:** none (requested by the human: the same fire rate and strength for one enemy in
  every level, the number of enemies being the only thing that changes). Replaces the per-level
  factors of ENM-22 (WLD-1-23, WLD-2-21, the levels' "Difficulty"), and the boss health factor
  of D-305. The specs still give the old factors: the human updates them.
- **Context:** a level scaled every enemy's and boss's fire rate and bullet speed (×0.8 in 1-1 up
  to ×1.35 in 4-5), and D-305 added a boss health factor: a kind fought in two levels was not the
  same enemy.
- **Decision:**
  - Every level's `EnemyDifficulty` is 1 and 1 (`AS_TUNED`): enemies and bosses fire and fly as
    tuned in their own files. The four `world_N/difficulty.py` tables are gone; the engine keeps
    `EnemyDifficulty` (ENM-22's mechanism, game-agnostic). The boss health factor is removed.
  - `src/game/config/level_enemies.py` gives each level one factor, `LEVEL_ENEMIES` (1: its waves
    as `level_plan` composes them, so no level changes until tuned). Each wave brings that many
    times its groups (the main tier's written groups too) and the filler comes that many times
    as often; the kinds, the tier mix, the pace and the bosses stay the level's.
  - `make adjust-level` (D-305) turns that factor alone, from 0.25 to 4, writing it to two
    decimals into `LEVEL_ENEMIES`. A rating episode composes the level again with the factor it
    tries (`EpisodeSetup.enemies`; each world's `SCENERIES` by level id).
- **Consequences:** World 4 is easier and 1-1 to 1-3 harder than before until the factors are
  tuned (their enemies fire at ×1 instead of ×1.1–1.35 or ×0.8–0.9). The ships do not grow in
  proportion to the factor: bigger waves take longer to come in, so fewer fit in the level (×2
  brings about ×1.4 the waves' ships in 1-1, plus twice the filler).
- **Status:** Proposed

### D-308 — `make adjust-levels`: every level adjusted, the targets rising evenly
- **Date:** 2026-11-09
- **Requirements:** none (requested by the human: 1-1 at 10 %, the difficulty rising linearly to
  99 % at 4-5, to run on a faster computer). Builds on D-305 and D-307.
- **Decision:** `make adjust-levels` (`ai.adjust --all`) adjusts the 20 levels in turn, as
  `make adjust-level` does one, level k (0..19) aiming at `FIRST_TARGET + k (LAST_TARGET -
  FIRST_TARGET) / 19` % (defaults 10 and 99: about 4.7 points a level), then prints a summary of
  each level's target, rating, enemies factor and outcome. A level whose factor runs out is left
  as it was.
- **Consequences:** a few hours on 8 cores (1-1 took 6 minutes; later levels are longer, and more
  of them need the most episodes). The factors fit the brain that rated them.
- **Status:** Proposed

### D-309 — A level drops as many bonuses whatever its enemy count
- **Date:** 2026-11-09
- **Requirements:** none (requested by the human, option 1 of three). Amends GAME-BONUS-02 and
  GAME-BONUS-03 (a destroyed enemy's chances), which the human updates. Follows D-307.
- **Context:** an enemy's chance to drop a bonus (weapon, heal, life, bomb) is its own, so twice
  the enemies dropped about twice the bonuses. Measured with the brain on 3-3 (16 episodes each),
  more enemies made the level easier: ×0.25 rated 26.1 %, ×0.5 18.3 %, ×1 17.3 %, ×2 16.6 %.
  `make adjust-level` could not converge: it took more enemies to be harder.
- **Decision:**
  - `GameLevel.bonus_scale` (default 1) multiplies every destroyed enemy's chances to drop a
    bonus, weapon (and so heal), life and bomb alike (`BonusWorld(scale=...)`). A boss part's own
    chance (BOSS-57) and the mini boss's life (GAME-BONUS-04) are not scaled.
  - `assemble_level` sets it to the ships the level's waves bring as composed (enemies factor 1)
    over the ships they bring at its factor: on average the level drops as many bonuses as it
    did, whatever its factor. A level at factor 1 is unchanged.
  - The search of `make adjust-level` no longer takes for granted that more enemies are harder:
    it goes the way its ratings so far go with the factor (least squares), and interpolates
    between the closest factors rated either side of the target.
- **Consequences:** 3-3 rates 3.8 % at ×0.25, 2.6 % at ×0.5, 17.3 % at ×1, 39.4 % at ×2 and
  47.9 % at ×4 (16 episodes each): harder with more enemies, but no more than about 50 % with this
  brain at the default highest factor (4); the higher targets of `make adjust-levels` (up to 99 %)
  may run out (`ADJUST_ARGS=--highest 8` lets it try more). Fewer enemies than composed drop more
  bonuses each.
- **Status:** Proposed

### D-310 — `make adjust-level` rates with 100 episodes
- **Date:** 2026-11-09
- **Requirements:** none (requested by the human: 100 simulations instead of 16). Amends D-305.
- **Decision:** each rating of `make adjust-level` and `make adjust-levels` plays 100 episodes
  (`--episodes` and `--max-episodes` both 100: they no longer start at 16 and double up to 64).
- **Consequences:** a rating's standard error is about 0.6 % for a spread of 6 %, against 1.5 % at
  16: the search is steadier, each step about six times longer than its first steps were.
- **Status:** Proposed

### D-311 — The enemies factor multiplies each wave once the level is composed
- **Date:** 2026-11-09
- **Requirements:** none (reported by the human: `make adjust-level` took more and more enemies and
  the rating got further from the target). Amends D-307.
- **Context:** the factor was applied while the level's beats were composed: bigger waves took
  longer to come in, fewer fitted, and every later beat moved. 1-2 brought 216 ships at ×1, 226 at
  ×1.4 and 295 at ×1.96, each a differently arranged level; the brain rated them 8.8 %, 9.9 % and
  4.5 % (100 episodes each).
- **Decision:** the beats are composed as written whatever the factor, and the factor multiplies
  the wave script's density (`WAVE_DENSITY × enemies`): each wave, and each filler group, brings
  that many times its groups at the time it would at ×1 (a lone heavy enemy's extra copies come
  one after the other, as the density already makes them). `level_filler` no longer takes it.
- **Consequences:** 1-2 keeps its 42 waves at any factor: 107 ships at ×0.5, 216 at ×1, 380 at
  ×1.96, 597 at ×3. Rated with the brain (48 episodes each): 0.0 % at ×0.5, 6.5 % at ×1, 17.5 % at
  ×1.5, 37.6 % at ×2 and 68.5 % at ×3, rising with the factor.
- **Status:** Proposed

### D-312 — `make adjust-level` adds enemies without a limit
- **Date:** 2026-11-09
- **Requirements:** none (requested by the human: do not stop at ×4, keep adding enemies until the
  target). Amends D-305 and D-309.
- **Decision:** the enemies factor has no upper limit by default (`--highest` still sets one);
  the search goes on until the rating is within the tolerance of the target, or at most
  `--max-steps` steps, now 20 instead of 10, a safety net for a target the brain never reaches,
  when the closest factor is written. The lower limit stays 0.25.
- **Consequences:** a level whose target needs ×10 gets it (about seven steps of ×1.4 from ×1, then
  the interpolation). Many enemies make long episodes: those steps are the slowest.
- **Status:** Proposed

### D-313 — The enemies that stop on the playfield spread down it
- **Date:** 2026-11-09
- **Requirements:** none (requested by the human: too many enemies camp in the top quarter of the
  screen, which shows with more than 20 on it). Departs from the stop heights of ENM-HORNET-04,
  ENM-STRAFER, ENM-SPINNER, ENM-LANCER, ENM-SPLITTER, ENM-HARRIER, ENM-SWEEPER, ENM-PRISM,
  ENM-WASP, ENM-PHANTOM-09, ENM-HYDRA, ENM-SCISSOR and ENM-JUGGERNAUT (the human updates the
  specs).
- **Context:** every enemy of a kind that stops did so at the same height, nearly all of them
  between 72 % and 82 % of the playfield's height: a crowd lined up along the top.
- **Decision:** each such kind stops at a height drawn at random, per enemy (per group for the
  Wasps), in a range reaching down to the middle of the playfield or below it (`stopRange`;
  `heightRange` for the Strafer's side pass; `placeY` for the Phantom): Hornet 45–80 %, Strafer
  40–85 %, Spinner 40–80 %, Lancer's first stop 55–85 %, Splitter 45–75 %, Harrier 45–85 %,
  Sweeper 45–80 %, Prism 45–80 %, Wasp 50–80 %, Phantom 40–82 %, Hydra 45–80 %, Scissor 50–82 %,
  Juggernaut 45–80 %. The kinds that cross the screen (Scout, Rocketeer, Mortar, carriers) are
  unchanged. `enemy_helpers.stop_height` draws them.
- **Consequences:** a third or more of the stops are below three quarters of the height; none
  comes below 40 %, out of the player's bottom part. Enemies lower down are closer to the player:
  the levels are harder, so the enemies factors need re-adjusting (`make adjust-levels`).
- **Status:** Proposed

### D-314 — Each tier hits harder: shot damage per tier, tougher and faster tiers 2 to 4
- **Date:** 2026-11-09
- **Requirements:** none (requested by the human: balance the enemies so the difficulty targets
  need a reasonable number of enemies). Departs from GAME-LIFE-03 (one damage per shot type for
  every enemy) and from the health of ENM-STRAFER-07, ENM-SPINNER-07, ENM-SPLITTER-09,
  ENM-WASP-11, ENM-MORTAR-10, ENM-PHANTOM-13, ENM-HARRIER-09, ENM-SWEEPER-09, ENM-HATCHERY-09,
  ENM-PRISM-12, ENM-BROODMOTHER-11, ENM-HYDRA-11, ENM-SCISSOR-14, ENM-JUGGERNAUT-14, ENM-HIVE-12,
  and the fire intervals of ENM-HYDRA, ENM-JUGGERNAUT and ENM-HIVE (the human updates the specs).
- **Context:** `make adjust-levels` (D-312) needed ×2 to ×3.3 enemies in worlds 2 and 3, ×3 to ×10
  in 4-1..4-3 and stopped unfinished at ×29 in 4-4 and 4-5. Every shot took 10 (bullet), 20
  (missile) or 25 (laser) off a 300-health budget, with 2 s of invincibility after each hit: the
  brain needed about 30 hits, a minute at the very least, to lose, which capped a 400 s level's
  rating near 92 % whatever the enemy count. Tiers 2 and 3 also died faster against their world's
  weapon level than tier 1 against level 1.
- **Decision:**
  - An enemy shot (bullet, missile, laser; and the bullets a burst makes) may carry its own
    `damage`; 0 or none keeps the hull's rule (`shot_damage`, core). Bosses keep the rule.
  - `TIER_DAMAGE` (`enemy_tiers.py`) gives each tier's kinds theirs: bullet / missile / laser
    10/20/25 (tier 1, as before), 15/25/30 (tier 2), 20/35/40 (tier 3), 40/55/60 (tier 4).
  - Health ×1.5 for tier 2 (Hatchery ×1.125: 450, to keep GAME-SCORE-03), ×1.25 for tier 3,
    ×1.25 for tier 4. Tier 4 fires faster: Hydra heads every 0.6 s (0.8), Juggernaut spread every
    1.8 s (2.5) and missiles every 1.8 s (2.4), Hive rings every 2.2 s (3).
- **Consequences:** rated by the brain at ×1 enemies, with D-313 (24 episodes each): 1-1 14.7 %,
  1-5 9.3 %, 2-3 18.6 %, 3-3 45.8 % (tier 4 still as in the first step), then 3-5 72.6 %, 4-1
  56.1 %, 4-3 76.9 %, 4-5 82.1 %. Against the 10 → 99 % targets that leaves factors of roughly
  ×0.8 to ×2.5, to be found by `make adjust-levels`. 99 % for 4-5 means the brain loses its three
  lives in the first 2 % of the level: with 2 s of invincibility per hit and 3 hits a life in
  tier 4, it cannot fall much below ~5 %, so 4-4 and 4-5 will stay short of 94 % and 99 %.
- **Status:** Proposed

### D-315 — The brain bombs and switches on purpose
- **Date:** 2026-11-10
- **Requirements:** none (requested by the human: the trained brain kept switching weapons and
  fired every bomb as soon as it had one). Amends D-292 (the bomb and switch are no longer drawn
  when playing) and D-296 (the reward).
- **Context:** the entropy bonus counted half of the bomb and switch heads' entropy. Where a press
  changes nothing (no bomb left, a bomb going off, weapons of equal level), that bonus was the only
  thing those heads learned from, and it pushed them toward pressing half the time. The habit
  carried over to the moment a bomb was picked up. A bomb also paid at once in points and cost
  nothing, and drawing the actions 15 times a second when rated or watched turned any small chance
  into presses every few seconds.
- **Decision:**
  - `mask_bomb` (`tests/ai/brain.py`) rules out "bomb" (logit −1e4) where none can go off. It reads
    the state vector's bombs left and bomb going off (`STATE_BOMBS`, `STATE_BOMB_ACTIVE`). There
    the choice is certain: no entropy, no gradient.
  - The bomb and switch heads count for `SPARE_ENTROPY` (0.1, was 0.5) of the entropy bonus.
  - `RewardWeights.bomb` = 0.25 per bomb set off (500 points, a quarter of a bar of health) and
    `RewardWeights.switch` = 0.002 per weapon switch (`StepInfo.switched`).
  - When playing (`Decision.sample`: `make rate`, `make adjust-level`, `make serve-ai`), the move is
    still drawn but the bomb and the switch are the likeliest choice. Learning still draws all
    three.
- **Consequences:** the brain's shape is unchanged: a trained brain keeps learning from where it
  is. Ratings change with how the brain plays, so the levels' enemies factors may need adjusting
  again once it has relearned. A brain that never rates a bomb above 50 % never bombs when played.

### D-316 — The enemies factors set from a scripted player's exposure, for 10 % to 70 %
- **Date:** 2026-11-10
- **Requirements:** none (requested by the human: rate the levels without the brain, which is not
  good enough, and set the enemies so the difficulty follows the targets; the human chose a top
  of 70 % once told 99 % cannot be reached). Amends D-305 (the default top target).
- **Context:**
  - The rating is `1 − (progress + health left) / 2`.
  - After each hit the ship is invincible for 2 s, so it loses at most one hit's damage every
    2 s, and 300 health takes at least 8–15 s to lose.
  - A 99 % rating means losing every life in the first 2 % of the level. Even at 8 times the
    enemies, 4-2 to 4-5 reach only 80–85 %.
  - The brain's own ratings asked for ×10.5 at 4-4 and ×28.9 at 4-5.
- **Method:**
  - **Exposure:** an unhittable ship, with no bombs and the guns at the world's level (D-304),
    aims at the nearest target and closes in on bosses. It plays the real simulation and records
    every hit it would take. At most 60 s of each boss fight is counted, so the turret's slow
    boss kills don't count against the level.
  - **Player model:** a player takes a share q of those hits, with the 2 s of invincibility and
    the balanced ship's 300 health over 3 lives. That gives a rating per episode.
  - **Calibration:** q = 3.37 % is the share that makes 1-1 at ×1 (the waves as composed) rate
    about 10 %.
  - **Fitting:**
    - Each level's factor is read off its rating against the factor (×0.75 to ×4, 8 seeds), then
      fitted locally over two more checks (12 and 16 fresh seeds).
    - 4-1 is kept at ×3.0 rather than ×2.99: below it, rounding takes its tier shares outside
      ENM-50's tolerance.
- **Decision:**
  - The 20 factors run from ×1.13 to ×3.16 (`level_enemies.py`): 216 to 860 ships per level, most
    in world 2, whose tier 2 enemies are weaker.
  - On 20 more fresh seeds, every level is within 5 points of its target, the noise between seed
    sets: 1-1 9.3 %, 2-3 32.9 %, 3-3 44.2 %, 4-1 57.7 %, 4-5 68.2 %.
  - `make adjust-levels` now aims at 70 % by default (`LAST_TARGET`, `--last`).
  - The waves are unchanged and every tier keeps its share (ENM-50).
- **Consequences:**
  - The percentages are relative to the model player: a better player rates every level lower.
    Only 1-1 is pinned (10 %).
  - Rating a level with the brain (`make rate`) gives other numbers.
  - The model's hit share is the same however dense the screen; a real player is hit more often
    on a crowded screen, so the later levels may feel harder than their numbers.
  - The probe scripts were one-off and are not kept in the repository.
- **Status:** Proposed

### D-317 — The HUD back over the playfield: light readouts in the window's corners
- **Date:** 2026-11-11
- **Requirements:** UI-HUD-01 to UI-HUD-08, UI-HUD-10, UI-HUD-12, UI-HUD-16, UI-LOOK-05.
- **Context:** owner: "put back the UI into the gaming area, make it light so it doesnt cover the
  area too much. Be creative dont just move the existing UI, design a new UI from scratch".
- **Decision:** the HUD is laid over the 540 × 720 playfield window. It has no panels and no
  backgrounds: only text outlined in black, and slim gauges, in the window's corners and along
  its edges, so the level shows through everywhere.
  - Top left: the score (22 px), its padding zeros drawn dim so the live digits stand out; under
    it the high score; under that, small and dim, the level played.
  - Top right: the lives (`♥ N`, green) over the bombs (`● N`, orange).
  - Top centre, during a boss fight: the boss gauge across the window, 200 × 4 px, filled from
    the left, with the boss's kind and name above it. It was a 300 px vertical gauge in the left
    column.
  - Right edge: the level's progress as a 2 px rail, filled from the bottom in the neon line,
    with a bright bead where the fill ends. It runs from 104 px to 616 px down the window.
  - Bottom left: the ship's callsign and `HP n / N` over a 130 × 6 px health bar cut into ten
    cells. Under 30 % health the bar turns red, the HP text turns red and the window's edges
    glow red, pulsing (only the glow's opacity is animated).
  - Bottom right: the weapon's name and one diamond pip per weapon level, lit up to its level.
    The `· Lv L/N` text and its `hudWeapon` text are gone.
  - The playfield window, the ship's bounds and every gameplay extent are unchanged (D-263).
  - The side columns stay opaque blue-black, but empty, with a cyan hairline on the window's
    edges; the game screen draws no neon frame. Since D-319 the columns are drawn by `#menu`
    for every screen. The touch fire
    and bomb buttons stay in the right column.
- **Alternatives considered:**
  - Widening the playfield back to the whole 16:9 screen with the HUD over it: this would undo
    the content extents of D-263 and the enemy counts the level adjustment fitted to the window
    (D-307 to D-316). The owner asked about the UI, not the playfield.
  - Glass panels in the corners: not light.
- **Consequences:** the ship flies under the bottom corners' readouts, which are thin and stay
  readable over it. The boss's kind is drawn over the boss's model when the boss stands at the
  very top.

### D-318 — 1-1 opens on big rocky islands crossed by roads
- **Date:** 2026-11-11
- **Requirements:** LVL-1-1-04, LVL-1-1-06, LVL-1-1-07, WLD-1-06, WLD-1-15, WLD-1-31.
- **Context:** owner: "add more island with roads and rocks at the start of level 1-1".
- **Decision:** 1-1's first section, "open sea" (35 s of deep water, −70 ± 30), becomes
  "rocky islands" (`ROCKY_ISLANDS`), and 1-1 now has World 1's two main roads (it had one).
  - **Relief:** −2 ± 55, features about 1 100 units across: big wooded islands between sea
    channels.
  - **Rocks:** World 1's scarps, 30 high, with their crag blocks.
  - Seconds, surface, trees and no buildings are unchanged.
- **Why these numbers:** roads only lie on land and must end off screen (GFX-ROAD-03,
  GFX-ROAD-04), so small islands carry none. Scarps at World 1's usual 340 units cut the land
  into strips the roads cannot cross. Measured in the first 35 s (road points 8 units apart, on
  screen):
  - islands at +4 ± 50 with scarps 340 apart: 85 points, and 1-1 fell to 78 % sea (under
    WLD-1-06's 80 %);
  - no scarps: 180 points, but no rocks;
  - scarps 1 000 apart, the chosen shape: 296 points (253 on the main roads, 43 on paths), and
    81.9 % sea over the whole level;
  - one main road instead of two, same shape: 214 points.
- **Consequences:**
  - The two main roads also run on the final green coast, a second road in the fishing
    village's section.
  - No building stands before the coast (checked: 65 buildings, all in the coast).
  - The wave plan, the enemies and the level's length are unchanged: the scenery is only drawn.

### D-319 — The menus in the game's 3:4 window
- **Date:** 2026-11-11
- **Requirements:** UI-LOOK-02, UI-SHIP-01, UI-SHIP-02.
- **Context:** owner: "make the main menues the same aspect ratio as the game".
- **Decision:**
  - **Same window as a level:** the menus use the 540 × 720 playfield window (D-263).
    - The cameras of the menu backdrop and of the ship select stage draw only in it, through
      the game's playfield viewport (`window_camera`). A game without a playfield window keeps
      the whole screen.
    - Every menu screen is laid out in the window.
    - `#menu` draws the same opaque blue-black side columns as round a level, with a cyan
      hairline on the window's edges.
  - **Kept out:** the game screen keeps the whole stage: its HUD is laid over the window itself
    (D-317). The side columns round a level are now `#menu`'s too, the game screen's own copy
    of them (D-317) is gone. The
    dev viewer's 3D views keep the whole stage. A phone's menus keep the whole window (D-286).
  - **Ship select:** the camera keeps its fixed horizontal field of view, so the three ships
    still span the window. To keep the outer ships' neon rings in view (they were already
    clipped at 16:9):
    - the ships are closer: spacing 7 → 6;
    - the framing has more room: margin 1.05 → 1.2 (the cards' row follows it);
    - the camera aims higher (target −1.2 → 0.6), so the ships sit nearer their cards.
- **Consequences:** the menus' 3D draws about 42 % of the 16:9 pixels. Settings over a paused
  level are now in the window too.
- **Status:** Proposed

### D-320 — The ground under the water is generated as far as it is seen
- **Date:** 2026-11-11
- **Requirements:** GFX-CAM-05, GFX-WATER-02, GFX-WATER-03.
- **Context:** owner: "on level 1-1, I sometime see slice of water that are not randered on the
  top of the screen".
- **Cause:** the stage worked out the ground the camera sees at the water level when a level has
  water. But the water is see-through (alpha 0.4), and its depth colour is painted on the terrain
  under it.
  - The top edge of the screen meets the sea bed further away than the water's surface: 1-1's
    deep water goes down to −100. In ground units, the far edge is at 672 for the surface and
    814 for the sea bed.
  - The ground was generated to 672 plus the 80 margin, rounded up to whole chunks of 320.
  - Whenever a chunk boundary fell just past 752, up to 62 units at the top had no sea bed. The
    water there was drawn over the clear colour, a band that came and went with the chunks.
- **Decision:** `lowest_ground` is the lowest of the relief, the shores' sea beds (1-2's coast at
  −55 over land relief of 6 and more) and the water level.
- **Consequences:**
  - 1-1's ground window grows from 672 to 814 deep, and from ±210 to ±255 across. 1-2's grows to
    the −55 sea bed.
  - The terrain chunks are about 13 % wider, and at most one more chunk is kept.
  - Levels without water are unchanged.
- **Status:** Proposed

### D-321 — A little explosion where a missile hits
- **Date:** 2026-11-11
- **Requirements:** GFX-FX-03, GFX-FX-05, GFX-FX-06.
- **Context:** owner: "add a little explosion when a missile hits an enemy".
- **Decision:**
  - **What it adds:** each player-missile impact (a shot impact with a blast radius) also sets
    off the engine's missile blast where it hit, the size of the missile's blast radius (10 px):
    a small fireball, ring, debris and embers, shrunk by `missileScale`.
  - **What stays:** the cyan impact disc stays.
  - **Not affected:** bullets and the laser have no blast radius and keep their sparks.
  - **Code:** the blasts are made in `app/hit_blasts.py` (`impact_blasts`), beside the hits on
    the player, from the impacts the step already reports. The simulation is unchanged.
- **Consequences:**
  - A missile volley at level 5 sets off up to five small blasts at once. They are counted
    against the blast particle caps like any other.
  - Missile hits on a shielded core (blocked) explode too: the missile still detonates.
- **Status:** Proposed

### D-322 — The Sweeper turns to its first edge while it brakes
- **Date:** 2026-11-11
- **Requirements:** ENM-SWEEPER-05, ENM-SWEEPER-06.
- **Context:** owner: "fix Sweeper animation: it starts straight but imediatly turns 45° then start
  shooting the laser, make the animation smoth".
- **Cause:** the Sweeper came in pointing straight down and, on the step it stopped, its heading
  was set to the arc's first edge, 35° to the side. The model jumped there in one frame.
- **Decision:**
  - **The turn:** it turns while it brakes (the last `brakeDistance`, 60 px, about 1.2 s). The
    heading goes from straight down to the first edge, eased in and out with the share of the
    brake covered. It is at the edge as it stops.
  - **The side:** it picks the side (away from the player) as it starts braking, not on
    stopping.
  - **Unchanged:** the warning, the sweep at a steady rate and the timing of the attack.
- **Consequences:**
  - The player's side is read about a second earlier than before.
  - A Sweeper spawned already inside its brake distance (only in tests) still turns at once.
- **Status:** Proposed

### D-323 — The UI redesigned in retro synthwave, made clear
- **Date:** 2026-11-11
- **Requirements:** UI-LOOK-03, UI-LOOK-04, UI-LOOK-06, UI-LOOK-08, UI-LOOK-09, UI-LOOK-12,
  UI-LOOK-14, UI-TITLE-05, UI-TITLE-08, UI-SHIP-02, UI-SHIP-03, UI-LEVEL-04, UI-LEVEL-09,
  UI-OVER-02, UI-OVER-09, UI-LOAD-02, UI-LOAD-05, UI-FLOW-08, UI-HUD-02 to UI-HUD-06, UI-HUD-16,
  UI-HUD-17.
- **Context:** owner: "redesign the UI completly, main menus and in game UI [...] Make something
  clear, modern, with a retro synthwave look". The neon blue/green look (D-198) glowed everywhere:
  glowing headings, a gradient selected block, a neon frame and bottom line on every screen, a
  pulsing chrome logo, pulsing hints, uppercase tracked labels at weights 700 to 900, 9 to 11 px
  HUD labels, spacing off the 4 px grid.
- **Decision:**
  - **Palette:** one night-violet ramp (`#0c0814`, glass `rgba(22, 15, 36, 0.86)`, three text
    roles), one hot pink accent `#ff4fa0` (selection, horizon line, sliders, progress, ship ring),
    player cyan `#4fd8ff` for the player's own gauges, red and orange kept for danger and bombs.
    No glows and no hue gradient in the chrome.
  - **The moment:** a flat striped sunset half sun behind the logo, yellow to orange to pink, the
    only gradient of the UI; the logo is solid italic capitals on a pink horizon line.
  - **The signature:** the horizon line, a 2 × 48 px pink rule under every heading.
  - **Shapes and type:** rounded glass entries (8 px) and panels (16 px) replace the chamfers;
    sentence case, weights 500 / 600, 4 px grid, no HUD text under 12 px.
  - **Copy:** no exclamation marks; the ship speed in plain words (`Speed: fast`).
  - **Motion:** nothing loops in the menus; a screen fades and rises 8 px; the low-health alarm is
    the one loop.
  - **Backdrop:** the title city re-lit at dusk: magenta sky low down, violet haze and towers,
    pink, violet and cyan windows and neon, pink lane lines.
- **Consequences:**
  - The specs' look sections, `index.html`'s styles, `title_look.py`, the ring colour and the texts
    changed together; the tests of the texts, the ring and the backdrop follow.
  - System fonts still (UI-LOOK-11): the look relies on the condensed stack, as before.
- **Status:** Proposed

### D-324 — Back to cyan, a chrome logo, no sun
- **Date:** 2026-11-11
- **Requirements:** UI-LOOK-03, UI-LOOK-06, UI-LOOK-08, UI-LOOK-12, UI-TITLE-08, UI-SHIP-03,
  UI-HUD-02 to UI-HUD-04, UI-OVER-09, UI-LOAD-05.
- **Context:** owner, on D-323: "remove the ugly sun from the main menue, put back a kick ass game
  name logo, and put back the cyan theme, the pink sucks".
- **Decision:**
  - **Palette:** the D-323 structure stays (one ramp, one accent, no glows, solid fills), on a
    blue-black ramp with electric cyan `#00e8ff` as the accent; green `#3dff9a` for the lives and
    a new high score.
  - **Logo:** black italic capitals at 60 px in a cold 80s chrome with a hard navy horizon across
    the middle, a thin pale outline and a 6 px solid teal edge cast down and right (stacked
    unblurred drop shadows), over a 4 px cyan bar. The striped sun is gone. It does not glow or
    move.
  - **Backdrop and ring:** back to the D-198 neon blue/green city and the cyan ring.
  - **Kept from D-323:** rounded glass entries, the horizon line under the headings, sentence
    case, the 4 px grid, the readable HUD, the copy without exclamation marks, still menus.
- **Consequences:** the D-323 backdrop colours and their test were reverted to the D-198 ones.
- **Status:** Proposed

### D-325 — The menu backdrop is the ship racing down a neon trench
- **Date:** 2026-11-11
- **Requirements:** UI-TITLE-07, UI-TITLE-08, UI-TITLE-10.
- **Context:** owner: "I want the ship to move like it is in a trench with a frontal facing
  camera, no more city background, put fast moving particles making it look like the ship flies
  fast".
- **Decision:**
  - **Shot:** the camera flies backwards 10 units ahead of the ship, 2.4 above it, looking back
    down the trench; the ship's nose points at it. The trench scrolls away behind the ship
    (60 units/s), so the scenery comes from beside the camera and shrinks into the haze.
  - **Trench:** generated from the seed, in stretches of 160 units (two end to end, one node):
    a floor with lit ribs every 10 units and a dashed guide line, two walls 16 high of panels 3 to
    9 long standing 0 to 1.4 out of the wall, lit slots on about half of them, a neon strip at the
    foot of each wall. Structure and lights are merged meshes, as the city's were (UI-TITLE-10).
  - **Speed streaks:** 220 thin quads along the trench, round its axis and facing it, 2 to 7 long,
    in stretches of 60 units moving away at 160 units/s, faster than the trench, so they read as
    rushing past. They glow.
  - **Ship:** sways 0.8 units side to side at 0.18 Hz, banking up to 0.35 rad into the sway, and
    floats 0.2 units at 0.5 Hz; it no longer turns on itself.
  - **Gone:** the city chunk, skyline and rain (`game/view/city_geometry.py` and its test).
- **Consequences:** the ship select screen, drawn over the backdrop, now has the trench behind it.
- **Status:** Proposed

### D-326 — One player ship, no ship select screen
- **Date:** 2026-11-11
- **Requirements:** GAME-SHIP-01, GAME-SHIP-02, GAME-SHIP-03, GAME-LIFE-01, GAME-WPN-05,
  UI-FLOW-01, UI-FLOW-02, UI-FLOW-05, UI-TITLE-06, UI-TITLE-09, UI-LEVEL-06, UI-LEVEL-08,
  UI-INPUT-09, UI-LOOK-08, UI-LOAD-03, PERF-07, DEV-OPT-01, DEV-MENU-12, DEV-API-02, ENG-07,
  ENG-54; removes UI-SHIP-01 to UI-SHIP-07.
- **Context:** owner: "now remove the heave and ligh ships, and the ship selection menu, only keep
  the balanced one."
- **Decision:**
  - **One ship:** the game's roster (`game/config/player_ships.py`) holds only the Balanced ship.
    The engine keeps the `PlayerShipRoster` type and flies its first ship: `MenuFlowOptions` and
    `MenuState` carry one `ship_id`, which `GameSession` builds the levels with.
  - **No ship select screen:** `ship-select` leaves `MenuScreen` and `MENU_TRANSITIONS`; Start on
    the title opens the level select, whose Back returns to the title.
  - **Gone:** the Heavy and Light ships and their models (`game/view/heavy_ship.py`,
    `light_ship.py`); the ship select view and screen (`ShipSelectView`,
    `ui/screens/ship_select_screen.py`), its 3D stage (`render/ship_select_stage.py`,
    `render/model_showcase.py`) and second menu scene, its tunables (`MENU_CONFIG.ship_select`),
    texts (`chooseShip`, `chooseShipHint`) and CSS; the ship caption (`ui/ship_caption.py`,
    `ui/caption_row.py`); the remembered ship (`<gameId>_last_ship` cookie); the backdrop's
    `showScreen` hook, which only hid its ship on that screen; the `ship=` debug option (and
    `--ship` / `SHIP=` of `make serve-ai`); the ship-highlight warm-up of the menus' loading.
  - **Test API:** `highlightedShipId` and `chosenShipId` become one `shipId`.
- **Consequences:** the menus' loading has two steps (the backdrop, then its shaders). PERF-07 is
  removed. The dev menu's ships viewer shows the one ship. An old `stratoblaster_last_ship`
  cookie is left unread. `create_torus` and `camera_fov_mode_horizontal_fixed` in
  `render/babylon.py` have no caller any more; they stay as Babylon wrappers.
- **Status:** Proposed

### D-327 — The Balanced ship rebuilt: one blended hull, smooth top, satin metal in three shades
- **Date:** 2026-11-11
- **Requirements:** GFX-SHIP-01, GFX-SHIP-04, GFX-SHIP-05, GFX-SHIP-06, GFX-SHIP-09, GFX-TRIM-05.
- **Context:** owner, in turn:
  - "rework the ship design to make it look better, more smoth, it's ok to increase polygon count
    but only on the upper half of the ship";
  - "add visible cool looking intakes on the reactors";
  - "rework the player's ship highlight, make it lighter";
  - "it looks like a bunch of basic shaped put together, smoth the transition between the elements
    with more complex looking parts";
  - "remove the ugly ligh spots, make something more smoth, and remove the inter-part transition
    more, add different shades of metalic".
- **Decision:**
  - **Blended hull:** the round fuselage, the dorsal spine and the strakes are replaced by one skin
    lofted through cross-sections (`render/geometry/section_loft.py`, generic; the ship's sections in
    `game/view/balanced_hull.py`). Each section's top is the smooth maximum of the fuselage's back,
    two nacelle shoulders and a chine sweeping into the wing roots, so the joints are fillets. The
    shoulders stand over the intakes and nacelles, which only show their mouths and nozzles; the
    tail is cut off square over the nozzles and capped.
  - **Winding:** every triangle of a loft is wound the same way, the direction chosen once for the
    whole skin. Chosen triangle by triangle, the inner slopes of the shoulders were turned inwards
    and culled, which left holes.
  - **Smooth top, low-poly belly:** the hull, canopy, intakes and nacelles are smooth-shaded on top
    (24, 16 or 12 facets) over a flat 3-facet belly (`LatheHalves`, `create_smooth_top_lathe_along_z`);
    hand-set profiles run through Catmull-Rom curves. Budget 4,500 triangles (was 2,000), at least
    three quarters of each part's on the upper half.
  - **Intakes:** a hollow, flared hull-metal scoop ahead of each reactor, a blue lip, a dark fan face
    ringed in blue metal and a spinner.
  - **No light spots:** the nav lights, the pale blue wing bands and the tail stripes are gone; the
    only lights left are the reactors. The nav-light helper and material are removed.
  - **Materials:** satin metal (roughness 0.42 to 0.5, was 0.25) in three shades: silver hull, steel
    wings, canards and spinners, gunmetal tails, fins and flaps.
  - **Trim:** the player trim is lighter, 0.5 px wide (was 0.9) in a softer cyan [0.3, 0.72, 0.82].
- **Consequences:**
  - The ship is about 3,600 triangles before the trim, counted from its parts (not measured in the
    browser).
  - The dev viewer's close-up draws the trim at its game width over a model drawn many times larger,
    so it looks much heavier there than in play.
  - The thinner, softer trim is checked against the ship's contrast floor by the readability e2e
    test (GFX-READ-07, 3:1).
- **Status:** Proposed

### D-328 — The player ship redesigned as a heavy variable fighter with an assault pack

- **Date:** 2026-11-11
- **Requirements:** GFX-SHIP-01, GFX-SHIP-04, GFX-SHIP-05, GFX-SHIP-06.
- **Context:** the owner asked to rewrite the ship to look like a specific, well-known anime
  variable fighter with its full upgrade pack, to tune it later so it would not infringe. A copy
  of that design was declined; the owner agreed to an original design in the same genre.
- **Decision:** keep the blended hull, canopy, intakes and tails of D-327, and change:
  - wings cranked and swept back (they were forward-swept), with gunmetal panel lines;
  - nacelles longer (2.0) and further back, their back third and nozzles out past the tail;
  - an assault pack on top:
    - two back boosters, each with its own reactor and flame (first steel tubes on the back;
      then, owner: "rework the blend between the inner and outer reactors so they dont just
      looks like tubes put next to each other", humps of the hull's skin: a `BOOSTER_HEIGHT`
      column in the stations, blended by the same smooth maximum as the shoulders, an accent
      band lofted across each; the hull runs on to z -2.0, one engine block whose tail face
      wraps the four engines; 31 points across the top, half evenly spaced, for the humps);
    - a conformal gunmetal armour plate over each nacelle shoulder, lofted from the hull's own
      top (`plate_sections`, `station_at` in `balanced_hull.py`);
    - a silver missile pod on each wing root, six forward launch tubes with accent tips;
    - a rail cannon on the right shoulder, its barrel between two accent rails;
  - the paint stays the project's three metal shades with blue accents.
- **Consequences:** the ship measures 6,752 triangles in the browser with its flames (3,996
  before; the trim adds about 200); the GFX-SHIP-05 budget goes from 4,500 to 7,000. The pack's
  triangles are all on the ship's top, seen from the playfield camera. The cannon makes the ship
  asymmetric; the hitbox is unchanged (gameplay is not touched).

### D-329 — The playfield window, not the whole 16:9 stage, is fitted to the browser window

- **Date:** 2026-11-11
- **Requirements:** GAME-SCREEN-02, UI-LOOK-02, ENG-110.
- **Context:** owner: "the display area get small for no good reason when I play with the
  browser size". Since D-317 and D-319 everything is drawn and laid out in the 540 × 720
  playfield window, but the fit still kept the whole 1280 × 720 stage in view. A window narrower
  than 16:9 shrank the playfield to make room for the opaque side columns: at 1000 × 900 it was
  421 × 562 px where 675 × 900 fits.
- **Decision:** `fit_stage` takes the game's playfield window. Its scale is the largest at which
  the playfield window fits (not the stage), the stage keeps its ratio and is placed so the window
  is centred. The stage's sides may run past the browser window's edges, clipped by `body`'s
  `overflow: hidden`. A window wide enough for the whole stage still shows it, centred, as before.
  A game without a playfield window fits the whole stage.
  - The phone layout (D-286) is still measured on the scale the whole stage would have
    (`StageFit.whole_scale`), so the same windows get it; their HUD and playfield are bigger now
    (0.72 instead of 0.3 on a 390 × 844 phone).
  - The touch fire and bomb buttons sat in the right side column, now possibly cropped: the fit
    tells the overlay how much of that column is in view (`--side-room`, `StageFit.side_room`).
    The buttons keep to its part in view, and move into the window's lower right corner, above
    the weapon readout, when less than 140 logical px of it is left (`narrow-sides`, as on a
    phone).
- **Consequences:** in a narrow window, the canvas is wider than the browser window; the 3D still
  draws only in the playfield's viewport, and the render scale cap (D-250) follows the larger
  scale. The dev viewer's 3D views, which use the whole stage, are cropped at the sides in such a
  window.

### D-330 — Rounded hexagon reactors, forward-swept wings with twin tip reactors, launchers under the wings, an unbroken trim

- **Date:** 2026-11-11
- **Requirements:** GFX-SHIP-01, GFX-SHIP-04, GFX-SHIP-05, GFX-SHIP-06, GFX-TRIM-02.
- **Context:** owner: "make the ship reactor rounded hexagons, make the wings front sided, add two
  reactors on the tip of each wing, with 45° lil wings on each and remove the gun on top of the
  ship. Also rework the ship highlight, it doesnt follow the wings geometry correctly"; then
  "rework the missiles pods, make them look cool, and under the wings" and "make it a dual reactor
  on the tip of each wing, and add intake to the reactors".
- **Decision:**
  - **Rounded hexagons:** `rounded_polygon` and `polygon_lathe_sections` (generic, in
    `section_loft.py`) loft a body round Z with a rounded polygon section. Every reactor's nacelle
    (smooth-shaded), rings (flat) and core are hexagons; the flame already was.
  - **Wings:** forward-swept, the tip pulled in to x 1.9; flap and panel lines follow the edges.
  - **Tip reactors:** two side by side on each tip, a steel fairing between them, each with a
    rounded hexagon intake (`build_reactor(..., intake=True)`); the outer one has two fins at 45°.
    "Two reactors on the tip of each wing" was read as a pair per tip.
  - **Gun on top:** the rail cannon is removed.
  - **Missile launchers:** under each wing on a pylon, rounded hexagon pods, their fronts out
    ahead of the leading edge with seven missile tips in a dark launch face; fins at 45° under the
    tail.
  - **Trim:** two causes of the broken outline.
    - The trim dropped a whole edge when its middle was covered by another part; it now probes
      each edge at 8 points and keeps the uncovered parts (GFX-TRIM-02, generic).
    - The nacelles peeked out from under the hull's edge, and the canted tails leaned past it,
      so the hull's and their outlines took turns: the aft chine is now 0.69 to 0.7 wide (the
      nacelles reach 0.64) and the tails cant 0.3 rad (0.4 before), their tips inside the edge.
- **Consequences:** the ship measures 10,398 triangles in the browser (6,752 before): eight
  reactors with their flames, two launchers. The GFX-SHIP-05 budget goes from 7,000 to 11,000.
  Gameplay and the hitbox are unchanged.
