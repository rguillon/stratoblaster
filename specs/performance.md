# Performance

> **Area:** Performance · **Prefix:** `PERF` · **Related:** [01-engineering.md](01-engineering.md), [dev/perf-tools.md](dev/perf-tools.md), [dev/test-api.md](dev/test-api.md), [ui/boot-and-loading.md](ui/boot-and-loading.md), [ui/ship-select.md](ui/ship-select.md), [ui/level-select.md](ui/level-select.md), [graphics/terrain.md](graphics/terrain.md), [graphics/roads.md](graphics/roads.md), [graphics/props.md](graphics/props.md), [graphics/traffic.md](graphics/traffic.md), [enemies/common.md](enemies/common.md), [bosses/common.md](bosses/common.md)

The game feels instant: every button press gets visible feedback straight away, a level starts
within a couple of seconds of being chosen, and play in every level runs without freezes or
hitches. This file gives the timing budgets and the rules that keep them: what is done ahead,
what is done in the ground worker, what is done once, what is drawn. It does not change the look,
the content or the rules of the game. The engine-wide targets (60 FPS, draw calls, bundle size,
instancing and pooling, ENG-100 to ENG-111) stay in [01-engineering.md](01-engineering.md); the
tools that measure the game are in [dev/perf-tools.md](dev/perf-tools.md).

## Requirements

### PERF-01 — How performance is measured · MUST

The **reference machine** is the ENG-101 target: a mid-range laptop with an integrated GPU of the
Intel Iris Xe / Apple M1 class, a 1080p screen, Chrome stable. Unless a requirement says
otherwise, the timings of this file are measured on the reference machine, on a production build
(`make build`, served by `make serve`), not on the e2e build.

A **long frame** is a frame whose time is above `long_frame_ms`. A **freeze** is a frame above
`freeze_ms`. The numbers are in **Tunable values**.

**Acceptance criteria**
- Given a timing budget of this file, then it is checked on the reference machine and a production
  build; an automated check on the e2e build (software WebGL) scales the limit by `e2e_slowdown`.

**Gap:** no measurement has been recorded on the reference machine yet: every figure in the
decisions (D-113 to D-233) was taken on software WebGL (SwiftShader) or in Node.

*Sources: P13-R01, P13-R03, P13-R04, ENG-101.*

### PERF-02 — Measured before it is optimised · MUST

A performance problem is measured before it is fixed, so every fix is backed by numbers. The
browser profiler and the perf monitor ([dev/perf-tools.md](dev/perf-tools.md)) find where the
time goes (for example shader compilation, ground generation on the main thread, garbage
collection, texture uploads, mesh or material creation during play). Every non-trivial optimisation
(precompilation, work spread over frames, work moved to the worker, pooling, caching, indexing) is
logged in `DECISIONS.md` with the cause found and the times before and after.

**Acceptance criteria**
- Given a decision that records an optimisation, then it names the cause that was measured and the
  time before and after the change.

*Sources: P13-R01, D-113.*

### PERF-03 — Optimisations do not change the game · MUST

A performance change keeps the game as it is: the same scenery, models, effects, music and
sounds; the same waves, enemy counts, timing and difficulty; the same scores. A faster way of
computing something gives the same result as the slow way: the same roads, buildings, trees,
heights and placements, and the same simulation for the same inputs and seed. A change to the
drawing gives the same frames: pixel for pixel, or within 1/255 where a shader reads less. A change
that would alter a result is made only with the reviewer's agreement (as for the building layout of
D-179).

**Acceptance criteria**
- Given an index, a cache or a faster algorithm, then a unit test compares its answers with the
  full computation (e.g. the street index against a check of every street, the noise table against
  the old formula, the worker's ground against one generated at once).
- Given a change to the drawing, then screenshots of the levels before and after match within
  1/255.

*Sources: P13-R05, D-114, D-143, D-151, D-152, D-179.*

### PERF-04 — Instant button feedback · MUST

Every button and menu action reacts visibly within `input_feedback_ms` of the press, with the
keyboard, a gamepad or touch: the selection moves, the button shows its pressed state, or the next
screen (or a loading screen, PERF-10) appears. This covers the title screen, ship select, level
select, settings, the pause menu and its `Leave the level?` question, and the "Level complete" and
"Game over" panels.

**Acceptance criteria**
- Given any menu on the reference machine, when a button is pressed, then the visible reaction
  comes within `input_feedback_ms` (checked with the browser's performance panel).
- Given the pause menu during a World 4 level, when Resume, Settings or Main menu is confirmed,
  then the reaction comes within `input_feedback_ms`.

*Sources: P13-R02.*

### PERF-05 — Heavy work comes after the feedback · MUST

No heavy work (building a scene, generating ground or textures, generating music, compiling
shaders) runs between a press and its visible reaction. When an action needs heavy work, the
reaction shows first and the work follows: confirming a level (also Retry, Next level and
Continue) shows the game screen at once and only starts the level's loading, which then runs in
steps (PERF-09).

**Acceptance criteria**
- Given the level select, when a level is confirmed, then the press returns at once and the game
  screen (or its loading screen) shows; the level's ground and scene are built in the frames after.

*Sources: P13-R02, D-115.*

### PERF-06 — No long frames in the menus · MUST

In the menus, no frame is longer than `long_frame_ms`, except while a loading screen shows. The one
accepted exception is building the highlighted level ahead on the level select (PERF-13), whose
steps may make that screen stutter once, after the highlight has come to rest.

**Acceptance criteria**
- Given the title, ship select, settings and pause screens, when the player moves around and
  confirms, then no frame is over `long_frame_ms`.

*Sources: P13-R02, D-119.*

### PERF-07 — Moving the ship select highlight costs nothing · MUST

Highlighting another ship on the ship select screen compiles no shader and creates no texture or
buffer. Each ship has its own key light, which lights only that ship; highlighting a ship only sets
its light to the spot intensity and the others' to 0, so no material is dirtied. While the menus
load, behind the loading screen, each ship is drawn once highlighted (from the last to the first),
so the GPU driver has every highlight state ready before the first press.

**Acceptance criteria**
- Given ship select, when ← or → is pressed for the first time, then no shader is compiled or
  linked, and the highlight moves within `input_feedback_ms`.

*Sources: P13-R02, D-116, D-118.*

### PERF-08 — Fast level loading · MUST

From confirming a level on the level select (or Retry, Next level or Continue) to its first playable
frame takes at most `level_load_max_s`, for every level, the dense districts of Worlds 2 to 4
included.

**Acceptance criteria**
- Given each of the 20 levels on the reference machine, when it is confirmed, then it is playable
  within `level_load_max_s`.
- e2e: the first level of each world loads with its time recorded and under `level_load_max_s` ×
  `e2e_slowdown` ([dev/perf-tools.md](dev/perf-tools.md), DEV-PERF-07).

**Gap:** not measured on the reference machine. On software WebGL a level takes about 2.4 s
(1-1) to 4 s (4-1) from a cold confirmation (D-233).

*Sources: P13-R03, P15-R12.*

### PERF-09 — Levels load in steps · MUST

A level loads in steps, one per frame, so the page keeps responding: its ground (made in the ground
worker, PERF-14), its scenery textures, the street surfaces of its first screens, its scene, the
compilation of every shader in the scene, the enemy models it needs (one per frame, PERF-21), the
wait for the shaders, then a first drawing and the start. Its progress is the share of steps done.
Unit tests may load a level at once (without stepped loading).

**Acceptance criteria**
- Given a level confirmed, then each frame runs at most one loading step, and the loading screen's
  progress grows after each step.

*Sources: P13-R03, D-115, D-181, D-182.*

### PERF-10 — A loading screen only for a long load, and it keeps moving · MUST

A level's loading screen (the menus' loading screen over the game screen, with the level's real
progress, ENG-108; its look is in [ui/boot-and-loading.md](ui/boot-and-loading.md)) fades in only
once loading has taken `loading_screen_after_ms`, so a quick load does not flash it. While it shows,
its bar moves after every step, and no single step freezes the page for longer than
`loading_step_max_ms`: the page never looks frozen.

**Acceptance criteria**
- Given a level that takes longer than `loading_screen_after_ms` to load, then a loading screen
  shows and its progress bar moves with no frozen step longer than `loading_step_max_ms`.
- Given a level built ahead (PERF-13), when it is confirmed, then no loading screen shows.

**Gap:** on software WebGL the longest steps (the scene, the shaders) still take 0.3 to 0.9 s
(D-233: 0.86 s for 4-1); not checked on the reference machine.

*Sources: P13-R03, D-115.*

### PERF-11 — Work done once is kept · MUST

Work whose result does not change (generated ground and textures, shared materials, models, music)
is done once and reused, not repeated at each level start or Retry:
- each level's scenery with its runout is made once, so it is the same object between starts;
- the last generated grounds are kept (up to `kept_grounds`: the level played, for its Retry or
  Continue, and the levels prefetched);
- the generated ground, noise and water textures are kept (the `kept_textures` most recent, by
  their arguments);
- each prop model's geometry and normals are made the first time a level needs them and kept for
  the next levels (each level still makes its own meshes from them);
- the noise works out each lattice angle's cosine and sine once, not on every call.

**Acceptance criteria**
- Given a level that is retried, then the second start is no slower than the first.

*Sources: P13-R03, D-114, D-117, D-148.*

### PERF-12 — The highlighted level is prepared while it is chosen · MUST

On the level select, once the highlight has rested on a level for `prefetch_after`, its ground and
its scenery textures are made in the background (PERF-14), while the player is still choosing, so
passing over levels does not queue them all. A level confirmed before it was prefetched is asked
for at once.

**Acceptance criteria**
- Given the highlight moved across several levels without resting, then none of them is prefetched.
- Given the highlight rested on a level, then its ground is asked for once.

*Sources: D-117.*

### PERF-13 — The highlighted level is built ahead · MUST

Once the highlight has rested on a level for `build_ahead_after`, the level select runs that level's
loading steps for the highlighted ship, one per frame, hidden behind the menus: all its steps but
the last (the start). Confirming that level with the same ship (and not from a checkpoint) starts
it in that frame, with no loading screen. A level partly built carries on behind the loading screen.
The level built ahead is dropped when another level or ship is highlighted, and when the level
select is left. The level's HUD shows only when it starts. e2e builds do not build levels ahead
([dev/test-api.md](dev/test-api.md)).

**Acceptance criteria**
- Given the highlight rested on 4-1 until its build is done, when it is confirmed with the same
  ship, then it starts in the same frame, with no loading screen.
- Given a level built ahead, when another level is highlighted or the level select is left, then
  the level built ahead is disposed of.

*Sources: P13-R03, D-119.*

### PERF-14 — Ground generation runs in the ground worker; its messages carry plain data · MUST

A level's ground (its roads and placed buildings) and its scenery textures are generated in a Web
Worker, the ground worker (its own bundle, `js/ground_worker.js`), not on the main thread. The
messages both ways carry plain data only: objects, arrays and typed arrays, with no functions and no
class markers, and shared references kept as one copy. The main thread rebuilds its road network
and prop placer from that data without generating anything, and every query answers as on the
generated ground. The worker sends only what the main thread needs. Without a worker (unit tests),
or after a worker error, the main thread generates the ground itself, with the same result.

**Acceptance criteria**
- Given a level, then the road network and the placer rebuilt from the worker's data give the same
  roads, buildings and query answers as those generated on the main thread (unit test).
- Given a level message, then copying it to plain data and back loses no field (unit test).
- Given the worker fails, then the level still loads.

*Sources: P13-R03, D-117, D-142, D-177, D-178.*

### PERF-15 — The runout's ground comes after the rest · SHOULD

The runout (the ground past the level's end) is generated after the rest of the ground: its streets
with their own random stream, its buildings after. The level is ready as soon as the ground before
the runout is; the worker answers the runout after the jobs already waiting. A ground made from the
worker's two answers is the same as one generated at once.

**Acceptance criteria**
- Given a level, then the ground made in two answers equals the ground generated in one (unit test).

*Sources: D-141.*

### PERF-16 — Buildings are placed in chunks, as the level needs them · SHOULD

The buildings are placed in chunks of `placement_chunk` along Z, in increasing order, each chunk
depending only on the roads and the chunks before it. The ground worker places the chunks the level
asks for as the view moves (two screens ahead) and sends them in order; the chunks up to
`first_placed_z` are placed before the ground is sent, so the level starts with its first screens.
The main thread places a chunk itself only when a tree needs it before the worker has sent it.
The buildings and trees are the same whatever the order and the thread the chunks are placed in.

**Acceptance criteria**
- Given each level, when its chunks are placed one at a time, by far jumps, in random increasing
  order or by the worker and the main thread mixed, then the buildings and trees are identical
  (unit test).

*Sources: D-179.*

### PERF-17 — Street surfaces are made in the ground worker · SHOULD

The street surfaces of each terrain chunk (the textured pieces, the layered fallback, the tile grid)
and the road atlas they point into are made in the ground worker, for the spans the stage asks
for; the main thread only takes them. Without a worker, the same code runs on the main thread. A
chunk whose surfaces are not back yet waits for them. The loading waits for the surfaces of the
first screens (PERF-09).

**Acceptance criteria**
- Given a new terrain chunk during play, then its street surfaces are not built on the main thread.

*Sources: D-182.*

### PERF-18 — The loading never waits for the worker for ever · SHOULD

A loading step that waits for the worker gives up after a bounded number of frames and lets the
main thread do the work: the scenery textures after `texture_wait_frames`, the street surfaces of
the first screens after `road_wait_frames`. The ground step waits for the worker, and falls back to
the main thread after a worker error.

**Acceptance criteria**
- Given no answer from the worker, when `texture_wait_frames` have passed, then the scene makes its
  textures itself and the loading goes on.

*Sources: D-117, D-182.*

### PERF-19 — No freezes during play · MUST

During play, after the first second of a level, no frame is longer than `freeze_ms`, and long frames
are rare: at most `max_long_frames_per_min` per minute. This holds in every level, the dense
districts of Worlds 2 to 4 included, on the busiest waves and during every boss fight. New content
(models, districts, effects) must not bring these long frames back.

**Acceptance criteria**
- Given each level of Worlds 1 to 4, played to the end (or its final boss) on the reference machine,
  then no frame is longer than `freeze_ms` after the first second.
- Given any level, then long frames stay at or below `max_long_frames_per_min` per minute.
- Given the busiest wave and each final boss, then the perf monitor counts no more long frames than
  before the latest change to the models.

**Gap:** not measured on the reference machine. On software WebGL, rare stalls of several seconds
remain inside WebGL calls (SwiftShader's GPU process); they are not reproduced on a GPU.

*Sources: P13-R04, P15-R12, P16-R09.*

### PERF-20 — Shaders are compiled before they are needed · MUST

Every shader a level draws is compiled while it loads, not on the frame where a new kind of object
first appears:
- the materials of everything in the scene (forced compilation);
- the rim shaders of the meshes that have one (the loading waits for them too);
- the thin-instance variant of the bullet layers: one bullet of each colour is shown while the level
  loads, and hidden when it starts;
- the shaders of each enemy model, as it is built (PERF-21).

Where WebGL compiles in parallel, the loading waits for the shaders, up to `compile_frames` frames,
then draws one frame hidden behind the loading screen (or the menus), which finishes them. e2e
builds skip this precompilation ([dev/test-api.md](dev/test-api.md)).

**Acceptance criteria**
- Given the first appearance of each enemy kind, boss, bullet colour and effect in a level, then no
  shader is compiled on that frame.

**Discrepancy:** one variant of the purple enemy bullets (with `INSTANCESCOLOR`, which Babylon sets
on draw) is still compiled on its first draw, about 0.5 s in headless software WebGL; the warm-up
does not create it (D-183, cause open).

*Sources: P13-R04, D-115, D-180, D-182, D-183.*

### PERF-21 — The level's enemy models are built while it loads · MUST

The enemy and boss models a level needs are built while it loads, one per loading frame with its
shaders, not during play: the models of the kinds its waves bring, of its bosses, and of the enemies
others send out (the Hornets of a Carrier or of a boss, the Wasps of a Hatchery, the Phantoms of a Broodmother, the Splitters of a Hive and their pods). The models of kinds the level does not use are
not built; one left out by mistake is still built when its first enemy shows. Each model is built
once per level and reused for every enemy of its kind.

**Acceptance criteria**
- Given 4-2, when it loads, then only its own models are built (about 22, not the game's 61).
- Given play, then no enemy model is built.

*Sources: P13-R04, P16-R09, D-117, D-181, D-197.*

### PERF-22 — A level builds only the prop models it uses · SHOULD

A level's stage builds the models of the props the level can place (the building groups and trees
its sections allow, its floating props, lines, podiums and set pieces), not every prop model of the
game. Each model's geometry is made once for the game (PERF-11); each level makes its own meshes
from it.

**Acceptance criteria**
- Given each level, then every prop placed over the whole level is of a kind built for it, and
  every prop kind has a model (unit check).

*Sources: D-146, D-148.*

### PERF-23 — What appears during play is prepared ahead · MUST

What is created while the level scrolls (terrain chunks, props, trees, cars, enemies, bosses,
effects, weather) does not stall a frame: it is prepared ahead of time (while the level loads, in
the ground worker, out of sight), spread over several frames, pooled or reused (ENG-104, ENG-105).

**Acceptance criteria**
- Given the first appearance of each enemy kind, boss and effect in a level, then it causes no frame
  longer than `freeze_ms`.
- Given a new terrain chunk coming into view, then it causes no frame longer than `long_frame_ms`.

*Sources: P13-R04.*

### PERF-24 — Look-ups only look near · SHOULD

Work done for each new terrain chunk, or each frame, never scans the whole level:
- the street lines are indexed by bands of Z (`street_band`), so the crossing and meeting tests
  check only the streets near a point; the street lines and each road's Z span are made once per
  list of roads, and the roads with no point near a chunk are skipped;
- the cars are looked up by the buckets of Z their roads span (`traffic_bucket`), not among all the
  level's cars.

An index gives the same answers, in the same order, as the full scan.

**Acceptance criteria**
- Given the street index, then it answers as a check of every street (unit test).
- Given the traffic index, then it gives the same cars in the same order as a scan of the whole
  level (unit test).

*Sources: D-113, D-114, D-145.*

### PERF-25 — Props are drawn near the view, and uploaded only when they change · SHOULD

Only the props near the ground in view are drawn: the placements within `prop_reach` before and past
it. The drawn range is `prop_step` wider each way, so the instances are uploaded again only every
`prop_step` or so of scrolling, not every frame, and only for the kinds whose drawn placements
changed. Each chunk keeps the instance matrices of its props by kind, made on their first upload;
when the window moves, they are copied, not made again. The same instances are drawn in the same
order.

**Acceptance criteria**
- Given the view scrolls by less than `prop_step`, then no prop instance is uploaded again.
- Given the window moves, then only the kinds whose drawn placements changed are uploaded.

*Sources: D-031, D-114, D-149.*

### PERF-26 — Props and cars are drawn without fitting their bounds · SHOULD

The meshes of the props and cars are always drawn (never culled against the view) and their bounds
are never fitted to their instances: the props drawn are near the view anyway, the cars are placed
again every frame, and the sun's shadows use a fixed frustum that no caster's bounds change. The
look is the same.

*Sources: D-144, D-149.*

### PERF-27 — Cars are set up when needed and placed near the view only · SHOULD

A road's surface heights, for its cars, are worked out when a car is first placed on it, not for
every road when the level starts. The cars are placed only where the props are drawn (`prop_reach`
past the ground in view), not over every loaded terrain chunk. The cars are the same.

*Sources: D-150.*

### PERF-28 — The terrain is drawn last; flat ground casts no shadows · SHOULD

The opaque meshes under the clouds are drawn with the terrain last, so its costly shading is skipped
wherever a prop or car in front of it was drawn first. A terrain look may say that its terrain casts
no shadows; World 4's looks do, as its flat ground has nothing to shade. Frames are the same, pixel
for pixel.

*Sources: D-151.*

### PERF-29 — The terrain shader reads only what shows · SHOULD

The terrain shader works out each ground texture's share of a pixel's colour from its layers (low
ground, ground and its cover of sand, grass and paving, high ground, steep slopes) and reads only
the textures, and the planes of each, whose share is over `terrain_skip`, sharing what was left out
among the rest. On flat paved ground it reads one texture once instead of seven textures on three
planes each.

**Acceptance criteria**
- Given screenshots of six levels before and after, then they match within 1/255 (a few pixels of
  1-3 aside, 0.006 %).

*Sources: D-152.*

### PERF-30 — Nothing is read back from the GPU in loading or play · SHOULD

The game reads nothing back from the GPU while the menus or a level load or play: a read-back waits
for all the GPU's queued work. The sky's diffuse lighting (its spherical polynomial) is computed on
the CPU from the sky cube's faces, with Babylon's own function, when the cube is made and after each
sky update. Only the test API's readability probe reads pixels back
([dev/test-api.md](dev/test-api.md)).

**Acceptance criteria**
- Given a sky cube, then its lighting is set from its faces and equals Babylon's read-back value.

*Sources: D-197.*

### PERF-31 — Hot code avoids slow constructs · SHOULD

Code that runs many times per frame or per load (ground generation, per-pixel and per-vertex loops,
colour helpers, material creation) avoids what is slow under Transcrypt or in Babylon: for example
the built-in `min` and `max` in per-pixel code (comparisons instead), and materials marked dirty one
by one (Babylon's dirty marking is blocked while the enemy materials are made). The Transcrypt
rules themselves are in [01-engineering.md](01-engineering.md) §13.

*Sources: D-182.*

### PERF-32 — The busiest districts hold the frame budget · MUST

The frame rate target (ENG-101: 60 FPS) and the draw-call budget (ENG-106: fewer than 200 draw
calls per frame) hold in the busiest districts: 2-5 at night and downtown in 4-5. Road pieces and
repeated models are drawn as instances (ENG-104).

**Acceptance criteria**
- Given 2-5 at night and downtown 4-5 on the reference machine, then the game runs at 60 FPS with
  fewer than 200 draw calls.

**Gap:** not measured on the reference machine; the game has no draw-call counter (ENG-106 asks for
one in the debug overlay).

*Sources: P15-R12.*

### PERF-33 — Triangle budgets of the enemy and boss models · MUST

Each enemy and boss model stays within the triangle budget of its tier: tier 1 to tier 4, mini
boss, final boss (values below). Models are built once and shared (PERF-21). A unit test checks every
model against its budget.

**Acceptance criteria**
- Given each enemy and boss model, then its triangle count is within its tier's budget (unit test).

**Discrepancy:** no unit test checks the budgets since the Python port, and with the glowing edge
trim (D-220) many kinds were over their budget on the old roster (up to 516 against 400, the Spinner);
whether the trim counts is left to the reviewer (D-220), and the four tiers are to be measured again.

*Sources: P16-R09.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `long_frame_ms` | 50 | A frame above this is a long frame (3 frames at 60 FPS). `src/config/engine.py` `ENGINE_CONFIG.long_frame_ms` |
| `freeze_ms` | 100 | No frame may exceed this during play, after the first second. Spec value, not in code |
| `max_long_frames_per_min` | 3 | Per minute of play, per level. Spec value |
| `input_feedback_ms` | 100 | Press to visible reaction. Spec value |
| `level_load_max_s` | 2 | Confirm to first playable frame. `tests/e2e/test_perf.py` `LEVEL_LOAD_MAX_S` |
| `loading_screen_after_ms` | 300 | Then the loading screen fades in over 0.15 s. `index.html` `.level-loading` animation |
| `loading_step_max_ms` | 200 | Longest single frozen step while the loading screen shows. Spec value |
| `e2e_slowdown` | 10 | Factor on time limits in e2e (software WebGL). `tests/e2e/test_perf.py` `E2E_SLOWDOWN` |
| `prefetch_after` | 0.25 s | Rest of the highlight before a level is prefetched. `src/app/level_prepare.py` `PREFETCH_AFTER` |
| `build_ahead_after` | 0.6 s | Rest of the highlight before a level is built ahead. `src/app/game_session.py` `BUILD_AHEAD_AFTER` |
| `compile_frames` | 60 | Most frames the loading waits for parallel shader compilation. `src/app/game_session.py` `COMPILE_FRAMES` |
| `texture_wait_frames` | 60 | `src/app/level_prepare.py` `TEXTURE_WAIT_FRAMES` |
| `road_wait_frames` | 120 | `src/app/level_prepare.py` `ROAD_WAIT_FRAMES` |
| `kept_grounds` | 3 | `src/render/scenery/level_ground.py` `KEPT` |
| `kept_textures` | 48 | `src/render/scenery/procedural_textures.py` `KEPT_TEXTURES` |
| `placement_chunk` | 200 world units | `src/core/scenery/prop_placement.py` `CHUNK_SIZE` (the runout gate is 2 chunks, `RUNOUT_GATE`) |
| `first_placed_z` | 1600 | Chunks placed before the ground is sent. `src/render/scenery/level_ground.py` `FIRST_Z` |
| `street_band` | 32 world units | `src/core/scenery/road_traffic.py` `BUCKET` |
| `traffic_bucket` | 256 world units | `src/core/scenery/traffic.py` `BUCKET` |
| `prop_reach` | 40 before, 120 past | Around the ground in view. `src/config/scenery_stage.py` `SCENERY_STAGE_CONFIG.prop_reach` |
| `prop_step` | 40 | `src/config/scenery_stage.py` `SCENERY_STAGE_CONFIG.prop_step` |
| `terrain_skip` | 1/512 | `src/render/scenery/terrain_blend_plugin_visual.py` `TERRAIN_SKIP` |
| `tri_budget_tier1` | 400 | `src/game/config/enemy_look.py` `ENEMY_LOOK["budget"]["tier1"]` |
| `tri_budget_tier2` | 600 | `ENEMY_LOOK["budget"]["tier2"]` |
| `tri_budget_tier3` | 900 | `ENEMY_LOOK["budget"]["tier3"]` |
| `tri_budget_tier4` | 1200 | `ENEMY_LOOK["budget"]["tier4"]` |
| `tri_budget_mini_boss` | 4000 | `ENEMY_LOOK["budget"]["miniBoss"]` |
| `tri_budget_final_boss` | 10000 | `ENEMY_LOOK["budget"]["finalBoss"]` |

## Notes

- Phase 13 found three causes for the reported problems (D-113): road ribbons that checked every
  road of the level against every street at each new chunk (0.8 to 0.9 s per chunk in Worlds 3 and
  4), a level built inside the key press that confirmed it, and shaders recompiled the first time
  each ship was lit on ship select. PERF-05, PERF-07 and PERF-24 keep them from coming back.
- The ground worker was off for a while during the Python port (D-177) because Transcrypt objects
  cannot be structured-cloned; plain-data messages (D-178) brought it back.
- The music is scheduled 1.5 s ahead so that a frozen frame leaves no gap: see
  [audio/music.md](audio/music.md).
- The phase 13 before / after table (software WebGL) is in `specs_old/phases/phase-13-perf.md`.
