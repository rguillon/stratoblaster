# Props

> **Area:** Graphics · **Prefix:** `GFX-PROP` · **Related:** [buildings.md](buildings.md), [traffic.md](traffic.md), [roads.md](roads.md), [terrain.md](terrain.md), [water.md](water.md), [sky-and-light.md](sky-and-light.md), [art-direction.md](art-direction.md), [../performance.md](../performance.md), [../dev/dev-menu.md](../dev/dev-menu.md)

Props are everything that stands on the generated ground: buildings and lots
([buildings.md](buildings.md)), cars ([traffic.md](traffic.md)) and trees, gathered in woods on the
grass and in sparse dead woods in the desert. All are models generated from code, drawn with thin
instances near the view; trees and cars are drawn as imposters, pictures baked once from detailed
models. The engine can also float props on the water, lay lines of props, place set pieces and send
up plumes of smoke and steam; no level uses those now. Props are only scenery.

## Requirements

### GFX-PROP-01 — Props are scenery only · MUST

Props cannot be destroyed and nothing collides with them; they are not an input of the simulation.

*Sources: P04-R04, D-020.*

### GFX-PROP-02 — The props there are · MUST

The game's props are: the buildings and lots made for the grid of tiles, the cars, the six living
trees and the four dead trees, and the road kit (shown only by the dev props viewer: the levels draw
their streets). There is no other hand-made prop: the shared and World 1 props (homes, huts, masts,
farms, wind turbine and every plant) were deleted, the building groups that drew from them now draw
from the grid's buildings, and no plant other than the trees grows.

**Acceptance criteria**
- Given the game's prop models, then none of the deleted shared or World 1 props is among them (unit
  test).

*Sources: P04-R04, P06-R06, D-207, D-212, D-214.*

### GFX-PROP-03 — No model no level places · MUST

A prop model that no level places (checked over the prop kinds and car kinds of every level) is
removed with its builder and its tests, and the dev props viewer no longer shows it. The road kit is
kept for the viewer.

**Acceptance criteria**
- Given every prop model of the game (the road kit apart), then some level places it.

*Sources: P15-R09, D-160, D-163, D-207.*

### GFX-PROP-04 — Models made in code, low-poly and matte · MUST

Every prop is generated from code: vertex-coloured, flat-shaded, low-poly geometry standing on Y = 0,
with no bottom faces, in the darksynth palette of weathered concrete, dark metal and small neon
accents ([art-direction.md](art-direction.md)). A model has up to five parts: its structure, its
self-lit lights, its windows ([buildings.md](buildings.md)), its plumes and a shadow stand-in. Props
are matte (no specular), so their facets do not flicker as the view scrolls. New props are as light in
polygons as the existing ones.

**Acceptance criteria**
- Given every prop model, then it builds a well-formed prop (unit test).

*Sources: P04-R04, P06-R06, D-020, D-024.*

### GFX-PROP-05 — Thin instances near the view · MUST

Each kind of prop is one mesh drawn once per placement with thin instances (plus one mesh for its
lights and one for its windows), and only the models of the kinds the level places are built.
Placements are grouped by terrain chunk and come and go with the chunks. Only the props near the
ground in view are drawn (`prop_reach`: 40 before it, 120 past it, as tall buildings show from
further), and they are uploaded again only when the view leaves the range drawn, which is `prop_step`
(40) wider each way.

**Acceptance criteria**
- Given a view, then the props drawn are those within the reach band, re-uploaded in steps (unit
  test).

*Sources: P04-R04, D-020, D-031.*

### GFX-PROP-06 — Props stand on flat ground · MUST

A prop stands only where the ground under its footprint is flat enough (`maxSlope` for buildings,
`treeMaxSlope` for trees, which stand on rougher ground), above `minHeight` (above the sea), at the
lowest ground under it. Placement is decided by hashes of where a prop stands, so the props are the
same whatever order the terrain chunks are built in.

**Acceptance criteria**
- Given a spot on too steep ground or under the sea limit, then no prop stands there (unit tests).

*Sources: P04-R04, D-020.*

### Trees and woods

### GFX-PROP-07 — Woods on the grass · MUST

With `forests` set, trees gather in woods on the grass: a low-frequency noise (`frequency` 1/300)
runs over the ground, and a tree grows where it is over `threshold` (0.27) and, by chance, up to
`edge` (0.06) over it, which gives ragged edges, clearings and a few trees outside. The woods' cover
is the section's `treeDensity` times its grass share (blended between sections as the ground cover
is); less cover raises the threshold towards 1. In a wood, each 50-unit cell tries `treesPerCell` (70)
trees, give or take 20 %, so cells never show as squares. Trees keep `treeClearance` (3) from the
roads, keep clear of the buildings and stay off steep ground and the sea. The kinds are drawn by
weight among the kinds the section lists (oaks, pines, birches, poplars, bushes, a few copper beeches).

**Acceptance criteria**
- Given woods, then trees grow on the grass where the noise is high, and fewer with a lower density
  (unit tests).
- Manual: World 1's green land is wooded almost everywhere there is grass, with clearings.

*Sources: D-212.*

### GFX-PROP-08 — Dead woods in the desert · MUST

A section may have `woods` (`cover`, `keep`, `scatter`) for ground that is not grass: its woods cover
the ground by `cover` in place of the grass share (not blended between sections), only `keep` of a
wood's trees grow (sparse woods), and `scatter` of the trees tried outside the woods grow alone.
Whether a tree is kept is a draw of its own, apart from its edge draw, so the woods are not streaked.
The desert has dead woods in patches (cover 0.55, keep 0.15, scatter 0.01: about 9 dead trees per
10 000 square units, a few alone between them); a dry lake has only a lone dead tree here and there.

**Acceptance criteria**
- Given a section with woods and no grass, then its woods grow and keep about `keep` of their trees,
  and lone trees are scattered outside them (unit tests).

*Sources: D-214, D-218.*

### GFX-PROP-09 — Tree models · MUST

The living trees are an oak, a copper beech, a birch, a poplar, a pine and a bush. A crown is a few
clumps, each a dark rough core under a cloud of small leaf tufts (about 9 per unit of surface), each
tuft a three-sided pyramid pointing outward and a little askew, coloured from a palette of 3 or 4
greens and shaded ±12 %, darker deeper in the crown and lower down; pines are tiers of drooping needle
tufts on dark cones; the birch has a few thin branches. They do not look like plastic. The dead trees
are a dead broad tree, a dead pine, a charred snag and a dry brush: limbs forking into smaller ones,
in pale sun-bleached wood that stands out on the red ground. All their triangles are in the bake.

**Acceptance criteria**
- Manual: the woods look like foliage, not plastic balls; the dead trees read as bare wood from the
  playfield camera.

*Sources: D-212, D-214.*

### GFX-PROP-10 — Imposters · MUST

The playfield camera never turns, so a model's picture depends only on its heading. A kind drawn as
an imposter is baked when the level starts, from `headings` headings, into one atlas: a row per kind
(rows rounded up to a power of two) and a column per heading, each frame `framePx` pixels showing
`frameSize` units round a point `centre` up, drawn by an orthographic camera on a layer of its own
looking the way the playfield camera does, the models unlit and shaded by a fixed light from the
look's `ambient`. Once drawn with its mesh ready for 2 frames, the bake's mesh and camera are disposed.
In play each placement is one quad facing the camera, a thin instance of the mesh of its kind and
nearest heading (moved and scaled, never turned), moved towards the camera along the line of sight
so its bottom clears the ground (which does not move it on screen), its normals up so it is lit like
the ground round it, drawn 1.3 times as bright as the props' structure. A level bakes only the tree
kinds its sections allow. Without the real kit (unit tests) the detailed models are drawn instead.

**Acceptance criteria**
- Given a heading, then the frame shown is the nearest one; every triangle of a quad faces the
  camera; a quad low over the ground is lifted to clear it (unit tests).

*Sources: D-211, D-212, D-214.*

### GFX-PROP-11 — Trees drawn as imposters · MUST

When the look asks for tree imposters, every tree kind of the level is drawn as one (4 headings, as a
tree turned is another tree; 256-pixel frames, as the leaves are small; 13 units across, centred 5 up;
shaded harder than the cars). The tree quads hide the glow of the lights behind them (they are drawn
black in the ground's glow layer, cut out by their alpha). They do not receive shadows.

*Sources: D-212, D-218.*

### GFX-PROP-12 — Tree shadows · MUST

Each tree has a shadow stand-in: one low-poly ellipsoid round its crown, or a cone for a pine (about
20 triangles; a dead tree's is its trunk and main limbs in 7 to 25 triangles, the same seed at a smaller
depth). It is drawn with the tree's instances only into the shadow map (a material writing no colour
or depth, on a layer no camera sees), so trees cast a shadow of their shape and nothing else.

**Acceptance criteria**
- Manual: the woods cast shadows on the ground.

*Sources: D-212, D-214.*

### GFX-PROP-13 — Trees stand on the ground drawn · MUST

Trees stand on the terrain as its mesh draws it: their cell's ground is sampled on the mesh's own
grid (the terrain's `cell`) and read back on the mesh's two triangles per cell, so on hilly ground no
tree floats or sinks.

**Acceptance criteria**
- Given a cell's sampled ground, then its heights match the terrain mesh's (unit test).

*Sources: D-212, D-218.*

### GFX-PROP-14 — Woods grow out of sight · SHOULD

A chunk that comes in during play gets its buildings at once and its trees over the next frames, one
row of cells per frame, unless it reaches into the ground where trees can be seen (the ground in view,
`tree_reach` (40) wider at both ends): then it gets them at once, and so does the rest of a waiting
chunk that comes into sight. The level's first chunks get theirs while it loads. Adding a row keeps the
trees already there, uploads nothing unless a new tree is in the props' window, and drops the trees of
a chunk that is gone. So woods never blink out or come into sight bare.

**Acceptance criteria**
- Given a chunk coming in out of sight, then it grows its trees a row per frame; one placed in sight
  gets them with its buildings (unit tests).

*Sources: D-212, D-218.*

### Engine tools no level uses now

### GFX-PROP-15 — Floating props · SHOULD

`floating` puts props on the water: in cells of `cellSize`, up to `perCell` each with the chance of
the section's `floatDensity`, where the water is at least `depth` deep under the whole footprint, at
the water level. A floating kind may drift slowly to and fro (`drift`: up to x and z over a period),
all its props together (the kind's mesh moves). No level floats props now.

**Acceptance criteria**
- Given a level with floating rules, then its floating props stand on the water, deep enough (unit
  test).

*Sources: P08-R07, D-066.*

### GFX-PROP-16 — Lines of props · SHOULD

`lines` lay one piece of a kind every `spacing` along a meander, turned along it, where the ground is
above the water and no steeper than `maxSlope`, in the sections listed; they are placed before the
buildings, which keep clear of them. A line may cross water (`overWater`: its pieces stand at the
water level where the ground is under it), and its pieces may move to and fro together (`drift`: ore
wagons on a rail line). No level lays lines now.

*Sources: P08-R07, P10-R08, D-066, D-079, D-085.*

### GFX-PROP-17 — Set pieces · SHOULD

`landmarks` place one prop of a kind at a given Z, at a given X or on a meander (its width across it),
on the ground or at the water level, before everything else and whatever the slope; every other
placement keeps clear of its footprint box (e.g. a waterfall across a river, a dam across a lake, a
temple). No level places set pieces now.

*Sources: P09-R06, D-079.*

### GFX-PROP-18 — Smoke and steam plumes · SHOULD

A prop model may list plumes (a point and a kind, `smoke` or `steam`). Each column is a few soft,
camera-facing puffs drawn with the prop's own thin instances, lifted, grown, bent by the wind and
faded on the GPU, each prop out of step with the others, lit by the scene's light (keeping a share of
its colour at night, as if lit from below), fogged, blended without writing depth, under the clouds.
Smoke is slow and tall (grey-brown, 70 high over 9 s); steam is quicker and lower (white, 45 high
over 6 s). Plumes stay faint so they never hide what flies. No model has plumes now.

**Acceptance criteria**
- Given the plume kinds, then every plume rises with growing puffs that stay faint, smoke taller and
  slower than steam (unit tests).

*Sources: P10-R08, D-085, D-129.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `prop_reach` / `prop_step` | 40 before, 120 past / 40 | `src/config/scenery_stage.py` `SCENERY_STAGE_CONFIG` |
| `tree_reach` | 40 | same place |
| `cellSize` / `treeClearance` / `treeMaxSlope` | 50 / 3 / 0.45 | `src/game/config/world_1/props.py` `WORLD_1_PROPS` |
| `FORESTS` | frequency 1/300, threshold 0.27, edge 0.06 | `src/game/config/trees.py` |
| `TREES_PER_CELL` | 70 (±20 %) | same place |
| `DESERT_WOODS` / `LONE_DEAD_TREES` | 0.55 / 0.15 / 0.01; 0 / 0 / 0.004 | same place |
| `TREE_KINDS` | weights and scales (living 1.3–2.1, dead oak 1.6–2.4) | same place |
| `TREE_IMPOSTERS` | 4 headings, 256 px, 13 units, centre 5, ambient 0.6 | same place |
| imposter brightness / quad clearance | 1.3 / 0.05 | `src/render/scenery/imposter_bake_visual.py` `BRIGHTER`, `src/render/scenery/imposters.py` `QUAD_CLEARANCE` |
| tree triangles | living 1 350–5 290, dead 96–385 (in the bake only) | `src/game/view/props/tree_props.py`, `dead_tree_props.py` |
| `PLUME_KINDS` | smoke: 7 puffs, 9 s, 70 high, lean 18, 5→22 across, alpha 0.32; steam: 6, 6 s, 45, lean 10, 4→18, 0.26 | `src/config/plumes.py` |

## Notes

- Per world, briefly: only World 1 has trees (woods on its green land and coast, dying woods on its
  dry grass, dead woods in its desert); Worlds 2 to 4 grow none. See the world files.
- D-207 first removed every plant; D-212 and D-214 brought trees back as imposters.
- D-162 stretched every hand-made prop to whole tiles; those props are gone (D-207) and the stretch
  was removed (D-218). The cars keep their own size ([traffic.md](traffic.md)).
- Known gaps: no test caps a prop model's triangles, and no unit test checks GFX-PROP-03 over every
  level (checked by hand for this rewrite: every model but the road kit is placed by some level).
