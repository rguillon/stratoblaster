# Performance analysis: which component uses which resource

**Date:** 2026-11-15 · **Commit:** `117f953` (main, after "Rework perfs" #57) · **Branch:** `perf/analysis`

This is a measurement report (PERF-02: measured before it is optimised). It changes nothing in the
game. It says where the main thread's time, the GPU's time, the memory, the loading time and the
download go, component by component, so the next optimisations can be chosen from numbers.
Every table behind it is in [performance-analysis-data.md](performance-analysis-data.md).

## 1. Summary

| Resource | Where it goes | Largest consumers |
|---|---|---|
| **Main thread, in play** | 3.7 ms per frame in a quiet World 1 scene, 10.6 ms in World 4, 20 ms at the worst peak seen (4-5 around 3:50), on a desktop Ryzen 9. 80 to 85 % of it is Babylon drawing the scene; the simulation and the view updates are 0.8 to 1.7 ms. | **Enemy models** (58 to 83 % of the draw calls of a busy frame), then the **playfield glow layer**, which draws every playfield mesh a second time |
| **Draw calls** | 690 to 2 120 per frame on average, peaks of 2 500 to 3 900. Budget (ENG-106): 200. | Enemies: 11 to 56 meshes each, each drawn twice. Player ship: 82. Buildings: 50 to 170. Traffic: 48 |
| **GPU** | 0.6 to 0.95 ms per frame on a Radeon RX 9060 XT at 1080p. Most of it does not depend on what is on screen. | Pixel count (half the pixels across: −45 %), the two glow layers (30 to 40 %), buildings (up to 30 %), shadows (12 to 18 %), terrain (10 to 30 %) |
| **JS heap** | 77 MB at the title, 120 to 160 MB in a level | Not broken down by component (see §8) |
| **Allocation rate** | 0.5 to 2.2 MB per frame (30 to 72 MB/s) | Enemy shot renderer, Babylon's drawing, reactor flames, missile smoke, traffic |
| **GPU memory** | About 150 MB, estimated | The multisampled canvas (71 MB), the shadow map (32 MB), glow targets (20 MB), road atlas (13 MB), car imposter atlas (11 MB). All geometry together is under 8 MB |
| **Level loading** | 1.3 to 1.9 s cold; the main thread works 1.1 to 1.4 s of it | Model geometry (edge trims, solids) 250 to 375 ms, the scene set-up 150 ms, enemy materials 70 ms, traffic and roads 60 to 110 ms each; workers: ground 0.4 to 1.1 s |
| **Start-up** | 0.85 s to the title on a local server | Babylon (220 ms), the title's models (90 ms), menus' DOM (85 ms), evaluating the game's config (80 ms) |
| **Download** | 2.45 MB gzip of JavaScript before the title (budget ENG-107: 1.5 MB) | `babylon.js` 1.84 MB gzip (75 %). In `game.js` (566 KB gzip), boss models and boss config are half the bytes |

The one finding that dominates the rest: **the frame's cost is proportional to the number of
draw calls, about 7 µs each on this machine, and the enemies make most of them.** A scene costs
the same main-thread time whether its meshes hold 3 000 triangles or 150 000. The scenery, which
holds 90 % of the triangles, is cheap because it is already instanced.

On a processor four times slower (Chrome's CPU throttling), World 4 runs at about 21 frames per
second (46 to 48 ms of work per frame) while World 1 holds 60 (14 ms).

## 2. How it was measured

- **Machine:** Ryzen 9 3900X, Radeon RX 9060 XT, Linux, Chromium 156 (Playwright's), headless with
  the real GPU through ANGLE/Vulkan, 1920 × 1080, 60 Hz. This is much faster than the reference
  machine of PERF-01: read the milliseconds as relative weights, not as what a laptop sees. The
  GPU figures in particular are small here and say little about an integrated GPU.
- **Build:** the production code (`make build`), bundled without minification so a profile's frames
  name their Python module. Minified and unminified run at the same speed (4.45 against 4.76 ms
  per frame on the same scene).
- **One change to the game while measuring:** the ship has 99 lives. Left alone and firing, it
  lost its three lives within a scenario and the game over was being measured. The graphics
  quality is held at High.
- **Scenarios:** nine, each a level at a time of its run with the fire key held and the ship not
  moving: `1-1@30`, `2-1@30`, `3-1@30`, `4-1@30` (seconds into the level), `2-5@120` (night),
  `3-3@120` (thunderstorm), `4-5@200` (downtown), `1-3@final` and `4-5@final` (final bosses).
  Each runs 12 s to let the waves arrive, then 15 s of plain frame timing, 15 s under the CPU
  profiler, 8 s under the allocation profiler, and last the frozen-frame test below.
  A ship that does not move kills fewer enemies than a player would, so the busy scenes are
  somewhat busier than real play.
- **Main thread by component:** Chrome's sampling CPU profiler (0.5 ms). Each sample goes to the
  component of the deepest game function on its stack, with the Babylon and browser time it
  called. Samples with no game function on the stack are Babylon drawing the scene; they are
  split by drawing phase, and attributed to components by the next method.
- **Drawing cost by component:** the game's loop is stopped on one frame and that frame is drawn
  90 times as it is, then 90 times with one thing taken away (a component's meshes hidden, a glow
  layer off, the shadows off, half the pixels). The differences in main-thread time, GPU time
  (`EXT_disjoint_timer_query`) and draw calls are what that thing costs. Draw-call differences
  are exact. Main-thread differences are noisy: the same whole frame measured four times varies
  by 0.1 to 0.5 ms, so a component under about 0.4 ms is not resolved by time; use its draw calls.
- **Loading:** each of the 20 levels, cold, from `?level=`, once plain and once profiled.
- The profiler adds 10 to 20 % to a frame. Totals under the profiler are therefore higher than the
  plain frame times, and the two windows are 15 s apart in the level.

To run it again: `uv run python tests/perf/analyse_perf.py --out <dir>` (about 35 minutes), then
`uv run python tests/perf/perf_report.py <dir>`. `--cpu-slowdown 4` emulates a slow processor,
`--only play --scenarios 4-1@30` runs one scenario.

## 3. The frame in play

Per frame at 60 Hz, plain timing, mean of 15 s. "Work" is the main thread from the engine's begin
to its end of frame; "draw" is the part inside `scene.render()`.

| Scenario | Work ms | p95 | Draw ms | Sim + view ms | GPU ms | Draw calls (mean / max) | Active meshes |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1-1@30 | 3.74 | 5.4 | 2.93 | 0.81 | 0.73 | 689 / 1 184 | 227 |
| 1-3@final | 4.89 | 5.7 | 3.94 | 0.95 | 0.74 | 873 / 932 | 283 |
| 4-5@final | 5.02 | 5.9 | 3.73 | 1.29 | 0.73 | 780 / 942 | 269 |
| 2-1@30 | 6.20 | 9.5 | 5.11 | 1.09 | 0.62 | 1 198 / 2 200 | 355 |
| 2-5@120 | 7.16 | 9.9 | 5.58 | 1.58 | 0.85 | 1 307 / 2 050 | 389 |
| 3-1@30 | 7.85 | 12.4 | 6.45 | 1.40 | 0.78 | 1 509 / 2 814 | 448 |
| 3-3@120 | 8.00 | 10.3 | 6.50 | 1.49 | 0.85 | 1 535 / 2 106 | 455 |
| 4-1@30 | 10.61 | 11.9 | 8.94 | 1.66 | 0.95 | 2 120 / 2 442 | 605 |
| 4-5@200 | 10.67 | 12.3 | 9.01 | 1.66 | 0.80 | 2 075 / 2 548 | 597 |

- Work follows draw calls closely: 5.4 µs per draw call in 1-1, 5.0 in 4-1. Nothing else on the
  frame explains the differences between scenarios.
- Outside the frame, the browser's own work (compositing, the swap) is a constant 0.85 to 1.1 ms.
- No frame over 50 ms in any plain window; the longest was 23 ms.
- **Peak:** in the profiled window of `4-5@200` (about 3:50 into 4-5) the frame averaged 20 ms
  of work with 3 880 draw calls, and the main thread had 0.4 ms of idle per frame: this machine
  was dropping frames there. Part of that is the profiler and part the ship that does not move,
  but it shows the level's worst case is twice its average.

Under 4× CPU throttling (10 s windows):

| Scenario | Work ms | p95 | Draw ms | Sim + view ms | Frame interval p99 |
|---|---:|---:|---:|---:|---:|
| 1-1@30 | 14.2 | 21.2 | 11.3 | 3.0 | 33 ms |
| 4-1@30 | 46.0 | 56.9 | 37.5 | 8.5 | 69 ms |
| 4-5@200 | 48.1 | 59.2 | 37.8 | 10.3 | 95 ms |

## 4. Main thread by component

CPU profile, ms per frame. The first three rows are Babylon drawing; §5 says which meshes they
draw. (The profiled window of 4-5@200 is the peak described above.)

| Component | 1-1@30 | 1-3@final | 2-1@30 | 2-5@120 | 3-1@30 | 3-3@120 | 4-1@30 | 4-5@200 | 4-5@final |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Babylon: main pass, draw submission | 1.16 | 1.68 | 3.69 | 2.05 | 5.03 | 1.88 | 4.27 | 7.11 | 1.51 |
| Babylon: glow layers (scene drawn again) | 0.87 | 1.19 | 2.82 | 1.55 | 3.88 | 1.38 | 3.26 | 5.49 | 1.04 |
| Babylon: active meshes (culling, world matrices) | 0.68 | 0.94 | 2.41 | 1.27 | 3.23 | 1.15 | 2.85 | 4.43 | 0.81 |
| Browser outside the frame | 0.84 | 0.87 | 0.89 | 0.85 | 0.87 | 0.90 | 0.91 | 1.09 | 0.89 |
| Enemy shots | 0.09 | 0.10 | 0.27 | 0.24 | 0.31 | 0.14 | 0.25 | 0.66 | 0.15 |
| Traffic | 0.01 | 0.06 | 0.08 | 0.03 | 0.34 | 0.41 | 0.40 | 0.30 | 0.34 |
| Audio (music, sounds) | 0.12 | 0.18 | 0.13 | 0.23 | 0.11 | 0.20 | 0.16 | 0.20 | 0.14 |
| Enemies (simulation and view update) | 0.06 | 0.07 | 0.18 | 0.10 | 0.19 | 0.09 | 0.22 | 0.47 | 0.05 |
| Babylon: scene render, other | 0.09 | 0.12 | 0.16 | 0.13 | 0.17 | 0.13 | 0.18 | 0.26 | 0.11 |
| Effects and bonuses | 0.09 | 0.06 | 0.20 | 0.08 | 0.09 | 0.07 | 0.11 | 0.16 | 0.08 |
| Reactor flames (ship and enemies) | 0.05 | 0.04 | 0.09 | 0.08 | 0.15 | 0.06 | 0.16 | 0.22 | 0.04 |
| Player shots | 0.04 | 0.05 | 0.09 | 0.10 | 0.12 | 0.07 | 0.11 | 0.14 | 0.07 |
| Babylon: shadow map pass | 0.05 | 0.08 | 0.04 | 0.14 | 0.13 | 0.10 | 0.08 | 0.07 | 0.05 |
| Bosses | – | 0.16 | – | 0.13 | – | 0.09 | 0.01 | 0.06 | 0.11 |
| Everything else (level run, scenery streaming, sky, props, HUD, input, GC…) | 0.37 | 0.40 | 0.45 | 0.56 | 0.50 | 0.34 | 0.50 | 0.61 | 0.30 |
| **Total busy** | **4.5** | **6.0** | **11.5** | **7.5** | **15.2** | **7.0** | **13.5** | **21.3** | **5.7** |

What it says:

- **Babylon's drawing is 60 to 80 % of the busy time** everywhere. It has three parts of similar
  size: submitting the main pass, drawing the scene again for the glow layers, and evaluating the
  active meshes (culling and world matrices of 230 to 600 meshes under 900 to 1 500 transform
  nodes).
- **The game's own code is small:** all Python modules together answer for 0.6 to 2.4 ms per
  frame. The largest are `game.view.enemies.enemy_shot_renderer` (0.04 to 0.42 ms),
  `game.view.reactor_flame` (0.04 to 0.22), `core.scenery.traffic` plus
  `render.scenery.traffic_layer` plus `imposter_field` (0.3 to 0.4 in Worlds 3 and 4),
  `audio.synth` (0.04 to 0.10) and `game.view.enemies.enemy_mesh` (0.02 to 0.20).
- **The simulation is negligible.** `core.systems.*` and `core.entities.*` never reach 0.3 ms.
- The HUD's DOM (0.01 to 0.05 ms), input, the terrain and road streaming, the sky and weather and
  garbage collection (0.01 to 0.06 ms) are each too small to matter on a frame.
- One oddity: `app.game_play` took 0.30 ms per frame in 2-5@120 against 0.02 to 0.04 elsewhere
  (with `app.page_audio` at 0.09). Not explained; worth a look if 2-5 is worked on.

## 5. What drawing each component costs

Frozen-frame test. Draw calls are exact; the frames are busy instants, not averages.

### Draw calls by component

| Component | 1-1@30 | 2-1@30 | 3-1@30 | 4-1@30 | 4-5@200 | 2-5@120 (boss) | 4-5@final |
|---|---:|---:|---:|---:|---:|---:|---:|
| Enemies and bosses | 274 | 388 | 568 | 1 056 | 484 | 96 | 156 |
| Player ship | (hidden) | 82 | 82 | (hidden) | 82 | (hidden) | 82 |
| Buildings and props | 7 | 59 | 168 | 104 | 50 | 122 | 50 |
| Traffic | 48 | 37 | 48 | 48 | 46 | 48 | 48 |
| Player shots | 48 | 7 | 9 | 25 | 47 | 28 | 32 |
| Enemy shots | 12 | 18 | 12 | 12 | 101 | 12 | 36 |
| Terrain | 12 | 12 | 12 | 8 | 6 | 9 | 6 |
| Roads, sky, weather, effects | 12 | 7 | 11 | 6 | 8 | 5 | 6 |
| **Whole frame** | **421** | **620** | **920** | **1 269** | **834** | **330** | **426** |
| Main thread to draw it, ms | 3.16 | 4.53 | 6.50 | 9.17 | 6.42 | 2.58 | 2.96 |

("Hidden": the ship was blinking after a hit on that frame.)

### Enemies

Each enemy is its own tree of meshes, one draw call per mesh, and every mesh is drawn twice: once
in the main pass and once in the playfield glow layer.

| Kind | Meshes per enemy | Draw calls per enemy | Measured main thread per enemy, ms |
|---|---:|---:|---:|
| splitter | 11 | 22 | 0.13 to 0.26 |
| hornet, scout | 14 | 24 to 28 | 0.17 to 0.18 |
| spinner | 20 | 40 | 0.21 to 0.22 |
| phantom | 29 | 58 | 0.17 to 0.40 |
| scissor | 32 | 64 | 0.39 |
| broodmother | 35 | 70 | 0.28 to 0.56 |
| hatchery, hydra | 41 | 82 | 0.41 to 0.68 |
| juggernaut | 56 | 112 | (not resolved) |
| Bosses (mesa-fortress, ice-queen, stone-idol, caldera-throne) | 45 to 82 | 90 to 164 | 0.74 to 1.08 |

- In `4-1@30`, 20 enemies on screen made 562 meshes and 1 056 draw calls: 83 % of the frame's
  draw calls and 7.4 of its 9.2 ms. Five broodmothers and five hydras alone cost 5.5 ms.
- A large part of those meshes are **reactor flames**: each reactor is four meshes (exhaust,
  flame, two puffs). A broodmother's six reactors are 24 of its 35 meshes; in the 4-1 frame the
  reactor parts were 220 of the 562 enemy meshes.
- The rest are hull, neon, flesh and their edge-trim meshes per moving part ("slide", "wing",
  "head", "neck").
- Triangle counts do not matter here: those 562 meshes hold 17 700 triangles in all.
- A level also keeps 600 to 1 630 enemy meshes in the scene (the pooled models of every kind it
  uses, bosses included), of which 50 to 560 are shown. The hidden ones cost little: taking them
  out of the scene's list saved 0.1 to 0.3 ms, within noise.

### The player ship

41 meshes (D-406 merged its still parts; its six reactors keep 31 meshes for exhausts, flames
and puffs, the rest being the canopy, the visor and the merged hull pieces), 82 draw calls, 0.3 to 0.6 ms. It is the same cost as
one large enemy, in every frame of the game.

### The glow layers and the shadows

| Taken away | Draw calls saved | Main thread saved, ms | GPU saved (of 0.7 to 0.9 ms) |
|---|---:|---:|---:|
| Playfield glow layer | 50 to 533 (every playfield mesh that is not additive) | 0.3 to 2.8 | 0.07 to 0.13 |
| Ground glow layer | 33 to 86 (lights, windows, and the props, cars and terrain as occluders) | 0.2 to 0.9 | 0.14 to 0.23 |
| Both | 106 to 594 | 0.8 to 3.8 | 0.22 to 0.36 |
| Shadows | 8 to 34 | under 0.4 | 0.08 to 0.15 |

- The playfield glow layer includes every playfield mesh except additive ones and those with
  vertex alpha (`app/level_scene.py`, `playfield_layer`): hulls, trims and flesh are drawn there
  black, as occluders, beside the neon that actually glows. It is 27 to 47 % of the draw calls
  of a busy frame.
- The shadow map draws few meshes (it is instanced scenery) and is cheap on the main thread.

### Scenery

- **Buildings and props:** 50 to 170 draw calls for 50 000 to 146 000 triangles and 600 to 3 900
  thin instances. The largest GPU consumer among the components (up to 0.30 ms of 0.90) and
  0.2 to 0.9 ms of main thread. Each kind is drawn in the main pass, the shadow map and the
  ground glow.
- **Traffic:** a constant 48 draw calls (cars plus their imposters), 0.2 to 0.6 ms to draw, plus
  0.3 to 0.4 ms of its own code per frame in Worlds 3 and 4 (placing cars, uploading instance
  buffers). Together it is the largest scenery item on the main thread.
- **Terrain, roads, sky, weather:** 20 to 30 draw calls together. Not resolved by time.

## 6. GPU

On this GPU a frame costs 0.6 to 0.95 ms, and **most of it is fixed**: with every mesh hidden the
frame still costs 0.56 ms (clearing and resolving the multisampled canvas, the glow
layers' blur and merge passes, the shadow map's clear).

| What | GPU ms saved when taken away |
|---|---:|
| Half the pixels across | 0.29 to 0.42 (about 45 % of the frame) |
| Twice the pixels across | costs 1.1 to 1.5 more |
| Both glow layers | 0.22 to 0.36 |
| Buildings and props | 0.02 to 0.30 |
| Terrain | 0.04 to 0.24 |
| Shadows | 0.08 to 0.15 |
| Enemies and bosses | 0.02 to 0.11 |
| Sky and weather | 0.03 to 0.08 |
| Traffic, shots, ship, roads | under 0.05 each |

Two structural facts that weigh on a slower GPU:

- **The canvas is the whole 16:9 stage, the level is drawn in 42 % of it.** The scenery camera's
  viewport is x 0.289 to 0.711 (D-252); the canvas is 1920 × 1080 with 4× MSAA. The multisampled
  buffer, its resolve, and both glow layers' targets (960 × 540 each, with their blur passes) are
  sized for the full canvas, 2.4 times the pixels the level uses.
- **GPU time follows pixels, not content.** That agrees with D-410's M1 figures (11.1 ms, 3.6 ms
  at half resolution) and with the automatic quality's choice of lowering the render scale first.

These are relative weights on a GPU with a lot of headroom. Absolute GPU cost needs a run on the
reference machine: `analyse_perf.py --gpu metal` on the M1.

## 7. Memory

**GPU memory, estimated from sizes and formats (4-1): about 150 MB.**

| Item | MB | Belongs to |
|---|---:|---|
| Canvas: 1920 × 1080, 4× MSAA colour and depth, plus resolve | 71 | Engine |
| Shadow map 2048 × 2048, half-float | 32 | Shadows |
| Glow layers: two main targets (one 4× MSAA) and four blur targets | 20 | Glow |
| Road atlas 1600 × 1600 with mipmaps | 13 | Roads |
| Car imposter atlas 2048 × 1024 with mipmaps | 11 (two of them, 21, were alive in 1-1) | Traffic |
| Ground, noise and water textures (a dozen at 256², one at 512²) | 5 | Terrain, props, sky |
| Enemy and boss geometry (every pooled model) | 1.8 to 4.0 | Enemies |
| Roads geometry | 0.7 to 1.2 | Roads |
| Player ship geometry | 0.75 | Ship |
| Terrain geometry | 0.5 to 0.7 | Terrain |
| Buildings and props: geometry plus instance buffers | 0.3 to 1.0 | Props |
| Traffic, shots, effects: geometry plus instance buffers | under 0.3 each | |

Render targets are 90 % of it. Geometry is negligible.

**JS heap:** 77 MB once the title shows, about 130 MB after the level select has built a level
ahead, 120 to 160 MB in play, with no trend by world. A level holds 390 to 630 materials, 730 to
1 530 transform nodes and 990 to 2 090 meshes; only 35 to 39 shader programs.

**Allocation rate in play** (sampled, garbage included), KB per frame:

| Component | Quiet scenes | Busy scenes (2-1, 3-1, 4-1) | Peak (4-5@200) |
|---|---:|---:|---:|
| Enemy shots (`enemy_shot_renderer`, `missile_smoke`, `core.systems.enemy_shots`) | 55 to 77 | 239 to 431 | 728 |
| Babylon drawing (main pass, glow, active meshes) | 150 to 200 | 360 to 550 | 680 |
| Reactor flames (`game.view.reactor_flame`) | 22 to 50 | 71 to 149 | 162 |
| Traffic (`core.scenery.traffic`) | 11 to 16 in World 1 | 44 to 102 | 73 |
| Enemies (`enemy_mesh`, `enemy_world`, `jointed_enemy`, `muzzle`) | 7 to 40 | 74 to 110 | 162 |
| Effects and bonuses (`blast_particles`, `blast_renderer`, `spark_bursts`) | 31 to 59 | 47 to 54 | 152 |
| Player shots | 22 to 33 | 28 to 46 | 72 |
| **Total** | **500 to 660** | **1 070 to 1 400** | **2 190** |

The heap's own growth between collections agrees: 30 to 72 MB/s. On this machine the collector
then costs only 0.01 to 0.06 ms per frame, but that many young collections per second is a source
of uneven frames on a slower processor.

## 8. Level loading

Cold start from `?level=`, from the frame the loading screen is added to the frame it goes.

| World | Total | Main thread busy | Longest single frame | Worker: ground | Worker: textures (two workers, summed) | Worker: roads |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 1.60 to 1.85 s | 1.28 to 1.44 s | 470 to 710 ms | 0.58 to 1.12 s | 0.64 to 0.77 s | up to 0.70 s (1-2, 1-3) |
| 2 | 1.31 to 1.59 s | 1.06 to 1.26 s | 360 to 410 ms | 0.36 to 0.95 s | 0.41 to 0.44 s | up to 0.36 s |
| 3 | 1.41 to 1.55 s | 1.20 to 1.27 s | 370 to 400 ms | 0.80 to 0.91 s | 0.43 to 0.45 s | up to 0.13 s |
| 4 | 1.35 to 1.55 s | 1.16 to 1.27 s | 390 to 400 ms | 0.79 to 0.96 s | 0.43 to 0.44 s | about 0.2 s |

All 20 levels are within `level_load_max_s` (2 s) on this machine. Every level has one frame of
360 to 710 ms at 0 % progress, above `loading_step_max_ms` (200 ms, PERF-10). In this cold path
the page's own start-up overlaps the load (the menu scenes cost 55 to 80 ms inside it), so that
frame should be confirmed from the level select before acting on it.

Main thread during a load, by component (ms; the levels are alike apart from World 1):

| Component | ms | Mostly |
|---|---:|---|
| Model geometry | 250 to 375 | `render.geometry.edge_trim` 82 to 116, `render.geometry.solids` 71 to 155 |
| Scene set-up | 145 to 165 | `app.level_scene` (shader compilation and the glow set-up are called from it) |
| Loading steps | 96 to 117 | `app.game_session` |
| Enemies | 72 to 108 | `game.view.enemies.enemy_materials` 58 to 78 |
| Traffic | 58 to 109 | `render.scenery.imposters` 24 to 64 (the atlas bake), `core.scenery.traffic` 6 to 62 |
| Roads | 38 to 107 | `core.scenery.road_segments` 19 to 83 |
| Buildings and props | 52 to 94 | `prop_field`, `window_atlas` |
| Sky and weather | 39 to 76 | environment cube, sky gradient |
| Terrain | 110 to 150 in World 1, 21 to 34 elsewhere | `height_field`, `ground_fit`, noise (World 1 only) |
| Garbage collection | 32 to 54 | |
| Player ship | 19 to 25 | |

The enemy and boss models (geometry, edge trims and materials) are the largest single item: about
400 to 500 ms of the 1.1 to 1.4 s, built again for every level.

## 9. Start-up and menus

- Title screen 849 ms after the request, with no network delay. Of 820 ms profiled: Babylon
  220 ms (parsing and evaluating 8.5 MB, engine creation), the title's ship and backdrop 130 ms
  (`section_loft`, `mesh_merge`, `ship_model`, `plates`), `app.menu_scenes` 65 ms, evaluating the
  game's config at import 80 ms (`game.config.bosses.boss_kit` 20, `world_1.waves` 18,
  `wave_plans` 10), the environment cube 49 ms, idle 113 ms.
- Title screen at rest: 0.78 ms of work, 97 draw calls, 0.42 ms of GPU. Level select: 1.04 ms.
- While the level select builds the highlighted level ahead, one frame took 127 ms (the accepted
  exception of PERF-06).

## 10. Download

| File | KB | KB gzip |
|---|---:|---:|
| `vendor/babylon.js` | 8 540 | 1 842 |
| `js/game.js` | 1 736 | 566 |
| `js/ground_worker.js` | 120 | 37 |
| 34 sound effects (`.ogg`; the `.mp3` set is the fallback) | 332 | 313 |
| `index.html` | 37 | 8 |

`game.js` by package: `game.view.bosses` 642 KB (37 %, 264 modules), `game.config.bosses` 221 KB
(13 %), `render.scenery` 125 KB, `app` 96 KB, `core.scenery` 91 KB, `game.view.enemies` 70 KB,
`core.systems` 58 KB. Everything is downloaded and evaluated before the title screen.

## 11. Candidates, by what the numbers say they are worth

Not decisions, and nothing here is implemented. Ordered by measured weight.

1. **Enemy draw calls** (58 to 83 % of a busy frame; World 4 at 21 fps on a 4× slower CPU).
   Fewer meshes per enemy: merge the still parts per material as D-406 did for the ship, and
   draw reactor flames and puffs (a quarter to 40 % of the enemy meshes, 31 of the ship's 41) as thin instances shared across
   enemies. Halving the meshes halves the main pass, the glow pass and the active-mesh
   evaluation together.
2. **The playfield glow pass** (27 to 47 % of draw calls, up to 2.8 ms). Draw only the meshes
   that emit light there, or fewer occluders. This needs a look at the frames: the hulls are
   there so neon does not glow through them.
3. **The player ship** (82 draw calls in every frame): same two levers.
4. **Active mesh evaluation** (0.7 to 4.4 ms): falls with the mesh count of 1 and 3; beyond that,
   900 to 1 500 transform nodes are walked per frame.
5. **Allocation churn** in `enemy_shot_renderer`, `reactor_flame`, `missile_smoke` and
   `core.scenery.traffic` (up to 1.3 MB per frame between them at the peak).
6. **Traffic** (0.3 to 0.4 ms of code plus 48 draw calls): the largest game-side item.
7. **Pixels on a slow GPU:** the canvas, its MSAA and the glow targets cover 2.4 times the area
   the level is drawn in; the shadow map is 32 MB.
8. **Loading:** enemy geometry, edge trims and materials are rebuilt per level (400 to 500 ms).
9. **Download:** Babylon is 75 % of the JavaScript; boss code is half of the game's bundle and is
   needed only by the level that fights that boss.

Not worth optimising on these numbers: the simulation (`core/`), the HUD, input, terrain and road
streaming in play, the sky and weather, the shadow pass on the main thread, the hidden pooled
meshes, the title screen.

## 12. Limits of this report

- One machine, far above the reference one. Nothing was measured on an integrated GPU.
- The ship stands still and fires: enemy counts are higher than in real play.
- The frozen-frame cost of small components (under 0.4 ms) is inside the noise.
- The JS heap is not broken down by component, and the workers' CPU time is known per job, not per
  module.
- The audio thread (Web Audio rendering) is not measured; only the music and sound scheduling on
  the main thread is (0.1 to 0.2 ms per frame).
