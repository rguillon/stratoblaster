# Performance improvement plan

**Date:** 2026-11-15 · **Based on:** [performance-analysis.md](performance-analysis.md) (commit `117f953`)

A plan, not yet a phase spec: nothing here is implemented. The owner has agreed that the design of
some enemies may change where it is needed (an exception to PERF-03, to be logged in
`DECISIONS.md` with the first step that uses it).

## 1. Goal and how each step is judged

The analysis found one dominant cost: the main thread's time is proportional to draw calls (about
7 µs each on the desktop used), and a busy frame has 1 300 to 3 900 of them, 58 to 83 % from
enemy models. On a processor four times slower, World 4 runs at about 21 frames per second.

**Targets** (measured with `tests/perf/analyse_perf.py`, same scenarios, same machine):

| Measure | Today | Target |
|---|---:|---:|
| Draw calls, 4-1@30, mean / max | 2 120 / 2 442 | under 700 / 900 |
| Main thread per frame, 4-1@30 and 4-5@200 | 10.6 ms | under 5 ms |
| Same under 4× CPU throttling | 46 to 48 ms (21 fps) | under 16.7 ms (60 fps) |
| Worst window seen (4-5 around 3:50, profiled) | 20 ms | under 9 ms |
| Allocation per frame, busy scenes | 1.1 to 2.2 MB | under 0.5 MB |

ENG-106's budget of 200 draw calls is not reached by this plan; §5 says what would be left.

**Every step** is one branch and one decision entry with before and after numbers (PERF-02),
re-measured on `1-1@30`, `4-1@30`, `4-5@200` and one boss scenario, plain and under 4× throttling.
A step that does not move its number is reverted rather than kept.

## 2. Where the draw calls come from

An enemy is a tree of nodes with one mesh per material per rigid part, and every mesh is drawn
twice (main pass, playfield glow layer):

| Part of an enemy model | Meshes | Source |
|---|---|---|
| Body | up to 7: hull, flesh, neon, vein, charge, and an edge trim for hull and for flesh | `enemy_mesh.add_surfaces` |
| Each moving piece (a gun slide, a wing, a head, a neck segment) | up to 3 to 6 of the same | `add_slides`, `add_wings`, jointed models |
| Each reactor | 4: exhaust cone, inner flame cone, 2 puffs | `reactor_flame.build_reactor_flame` |
| Each rotor | 1 | `enemy_engines.add_rotors` |

So a hydra is 41 meshes and 82 draw calls, a juggernaut 56 and 112. In the 4-1 frame measured,
20 enemies made 562 meshes: 220 of them reactor flame parts, about 200 on moving pieces, the rest
bodies. The player ship is 41 meshes, 31 of them reactor flame parts.

## 3. The steps, in order

Estimates are for the 4-1 frame of the analysis (1 269 draw calls, 9.2 ms to draw), from its
exact draw-call counts. They are estimates until measured.

### Step 1 — Reactor flames drawn as one shared layer

- **What:** every reactor flame of the playfield (the ship's, every enemy's, the enemy missiles')
  is drawn by three thin-instanced meshes for the whole level: exhaust cone, inner cone, puff.
  Each flame keeps a nozzle node on its model; each frame the layer writes one matrix and one
  colour (with its fade in the alpha) per cone and per puff, as the bullet layers already do.
  The flicker and puff motion stay as computed today (`flicker`, `puff_progress`).
- **Removes:** 4 meshes per reactor, in both passes. 4-1 frame: 220 meshes, about 440 draw
  calls (35 % of the frame). Ship: 31 meshes, 62 draw calls in every frame of the game.
- **Look:** the same shapes, colours and motion. One difference to check: see-through flames are
  sorted against each other per layer instead of per mesh. If that shows, the fallback is to make
  them additive.
- **Design alternative if the layer proves awkward:** enemy flames without puffs (2 meshes per
  reactor instead of 4). Half the gain, a visible change.
- **Risk:** medium. A new renderer, and per-frame matrix maths moves from Babylon to game code;
  it must not allocate (see step 5).

### Step 2 — One mesh per material per enemy, moving pieces included

- **What:** an enemy's slides, wings, heads and neck segments stop being separate meshes. Their
  geometry is merged into the body's mesh of the same material, and each moving piece becomes a
  bone of one skeleton per model (rigid skinning, one bone per vertex). The code that moves a
  slide or flutters a wing sets the bone instead of a node. `mesh_merge.merge_still_meshes`
  already does the merge for still parts; this extends it to rigid moving ones.
- **Result:** every enemy is at most 7 meshes whatever its number of moving pieces: hydra 41 → 7
  (with step 1), juggernaut 56 → 7, hornet 14 → 7.
- **Removes:** 4-1 frame, about 340 remaining enemy meshes → about 140, so 400 more draw calls.
- **Look:** unchanged if the edge trim follows the bones. The trim is built per mesh from its
  silhouette (`render/edge_trim_mesh.py`); how it behaves on a skinned mesh is the first thing to
  prototype, on one kind (hydra), before converting the rest.
- **Design fallback, allowed by the owner:** if skinning the trims or a jointed model costs too
  much, simplify the worst kinds instead: fewer separate slides on the juggernaut (16), fewer
  neck segments on the hydra, wings that flutter as one piece.
- **Risk:** high. It touches every enemy model builder and the trim. Do it kind by kind behind
  the same `BuiltEnemyModel` interface, heaviest kinds first (hydra, broodmother, juggernaut,
  hatchery, scissor, phantom), measuring after each.
- **Bosses** (45 to 82 meshes, one on screen, about 1 ms) come last and only if steps 1 to 4
  leave them as a visible share; their destroyable parts make them harder.

### Step 3 — The playfield glow draws only what it needs

- **What:** today the playfield glow layer includes every playfield mesh that is not additive
  (`level_scene.playfield_layer`): neon, but also hulls, flesh and trims as black occluders. Keep
  the meshes that emit (neon, vein, charge, trims) and, as occluders, only the body's hull and
  flesh; leave out anything that neither glows nor can hide a light.
- **Removes:** after steps 1 and 2 the gain is small in count (the flames are gone from it, each
  enemy is 7 meshes) but it is cheap to do first as a quick win: before steps 1 and 2 it is
  27 to 47 % of a busy frame's draw calls.
- **Look:** needs the owner's eye. Without a hull as occluder, a light under a wing glows through
  it. Screenshots of each kind before and after.
- **Risk:** low.

### Step 4 — Less work per mesh that remains

Cheap engine settings, each measured alone and kept only if it shows:

- Playfield meshes are always on screen: `alwaysSelectAsActiveMesh` and no bounding-info sync,
  as the blasts and enemy shots already have. Aims at the active-mesh evaluation (0.7 to 4.4 ms).
- Freeze the materials that never change (hull, flesh, neon, trims, props), leaving the animated
  ones (vein, charge) alone. Aims at `isReadyForSubMesh`, `needAlphaTestingForMesh` and the
  binding checks (about 1 ms together in busy frames). Nothing in the code freezes a material
  today.
- Bake the per-piece `-skin` offset nodes into the geometry: one transform node less per moving
  piece (900 to 1 500 nodes are walked per frame).
- **Risk:** low, but each can break a material that is changed later (quality changes, fades):
  the e2e and readability tests cover that.

### Step 5 — Allocation churn in per-frame code

- **What:** the modules that allocate most per frame: `enemy_shot_renderer` (up to 380 KB),
  `missile_smoke` (290 KB at the peak), `reactor_flame` (up to 160 KB, rewritten by step 1),
  `core.scenery.traffic` (60 to 80 KB), `blast_particles`, `blast_renderer`, `muzzle`,
  `jointed_enemy`. The usual causes under Transcrypt are `enumerate`, tuple unpacking, list
  building and closures in loops (ENG-157); replace them with index loops and reused buffers.
- **Gain:** not frame time on a fast machine (the collector costs under 0.06 ms per frame) but
  fewer collection pauses on a slow one. Babylon's own share (190 to 690 KB) falls with the draw
  calls.
- **Risk:** low. Same results, unit tests compare.

### Step 6 — Traffic

- **What:** 0.3 to 0.4 ms of game code per frame in Worlds 3 and 4 (`core.scenery.traffic`,
  `traffic_layer`, `imposter_field`) plus 48 draw calls. Profile it alone first; D-412 already
  made it one pass, so what is left needs a look before a plan.
- **Risk:** low. Do it only if it is still a visible share after steps 1 to 4.

### Step 7 — Pixels (after a measurement on the reference machine)

- **What:** the canvas, its 4× MSAA buffer and both glow layers' targets cover the whole 16:9
  stage, while the level is drawn in 42 % of it. Options: size the canvas to the playfield while
  a level plays, or size the glow targets to the viewport. Also the shadow map (2048², half-float,
  32 MB).
- **First:** run `analyse_perf.py --gpu metal` on the M1. On the desktop the GPU frame is under
  1 ms and proves nothing about an integrated GPU. D-410's automatic quality already protects
  slow GPUs, so this step may not be needed.
- **Risk:** medium (canvas size touches the stage fit and the menus over the level).

### Step 8 — Loading

- **What:** the enemy models' geometry, edge trims and materials are built again for every level:
  400 to 500 ms of a 1.3 to 1.9 s load. Keep each kind's geometry and trims for the session, as
  the prop models' are (PERF-11); each level still makes its own meshes from them.
- **Gain:** nothing on a first load, 300 to 400 ms on every later level, Retry and Continue.
- **Order:** after step 2, which changes what a model's geometry is.
- Also confirm the 360 to 710 ms frame at 0 % progress from the level select (the analysis saw it
  only in the cold `?level=` path).

### Step 9 — Download (optional, large)

- Babylon is 1.84 MB gzip of 2.45 MB. A tree-shaken ES-module build would cut it but undoes D-173
  (the vendored UMD file).
- Boss models and config are half of `game.js` and are needed one level at a time. Loading them
  per level needs code splitting, which Transcrypt's single-entry build does not give for free.
- Neither affects the frame rate. Only worth doing if the first visit's wait matters.

## 4. A guard so it does not come back

With step 1: a unit test that counts the meshes of every enemy and boss model against a budget per
tier, beside the triangle budgets of PERF-33 (whose own test is missing since the Python port).
New content that adds meshes then fails a test instead of a frame. The perf monitor already
records draw calls; the F3 overlay can show them (ENG-106 asks for it).

## 5. What the plan is expected to give

For the 4-1 frame (1 269 draw calls: enemies 1 056, everything else 213):

| After | Enemy draw calls | Frame draw calls | Draw time, estimated |
|---|---:|---:|---:|
| Today | 1 056 | 1 269 | 9.2 ms |
| Step 1 (flames) | about 620 | about 830 | 6 ms |
| Step 2 (one mesh per material) | about 280 | about 500 | 3.6 ms |
| Step 3 (glow membership) | about 240 | about 460 | 3.3 ms |
| Step 4 (per-mesh work) | same | same | 2.5 to 3 ms |

That is about 60 % fewer draw calls and a third of the drawing time, which should bring World 4
to 60 fps under 4× throttling on average but probably not at the worst peaks. What would remain
above ENG-106's 200: 7 meshes per enemy in two passes, buildings (50 to 170), traffic (48),
shots (40 to 150). Going further means one mesh per enemy (a single enemy material carrying
lit, neon and trim surfaces), which is a shader project of its own and not planned here.

## 6. Suggested order of work

1. Step 3 (glow membership) and step 4: small, low risk, measurable in a day.
2. Step 1 (flame layer) with the mesh-budget test of §4.
3. Step 2 on the hydra as a prototype, then decide between skinning every kind and simplifying
   the worst ones.
4. Step 5, then re-run the full analysis and decide on steps 6 to 9 from the new numbers.

## 7. Decisions needed from the owner

1. **Flames:** identical look through a shared layer (step 1 as written), or simpler enemy flames
   without puffs (less work, visible change)?
2. **Glow occluders:** may a light glow through a wing or a gun that passes over it (step 3)?
3. **Step 2 fallback:** if skinning the edge trim is not practical, which is preferred: fewer
   moving pieces on the heavy kinds, or keeping them and accepting about 830 draw calls?
4. **Process:** should this become a phase spec (requirements written by the owner, PERF-03
   amended for the enemy design changes) before any code, or go step by step on `perf/*`
   branches with a decision entry each?
