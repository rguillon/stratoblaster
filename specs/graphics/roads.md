# Roads

> **Area:** Graphics · **Prefix:** `GFX-ROAD` · **Related:** [terrain.md](terrain.md), [buildings.md](buildings.md), [traffic.md](traffic.md), [camera.md](camera.md), [props.md](props.md), [readability.md](readability.md), [../dev/debug-options.md](../dev/debug-options.md), [../performance.md](../performance.md)

Every level's ground carries generated roads. Outside towns, winding main roads run along the level
and dirt paths branch off them; none ever starts or ends on screen, and outside the districts no two
cross. Towns, cities and factories (the **districts**: runs of sections with a street grid) are laid
on a grid of 10-unit tiles, like a city-building kit: their roads have sidewalks and are made of a
small kit of road pieces in sizes of 1 to 4 tiles, with adapter pieces where roads of different sizes
meet. Buildings are in [buildings.md](buildings.md) and cars in [traffic.md](traffic.md).

**Words used here.** A *tile* is a square of ground `tile.size` (10) on each side. A *road of size N*
has N lanes each way and is N tiles wide, sidewalks included. A *road piece* is one N × N-tile piece
of a road: a straight, a 90° turn, a T, an X or an adapter. A *city block* is the rectangle of tiles
between the roads of a district.

## Requirements

### Winding roads and paths

### GFX-ROAD-01 — Winding main roads · MUST

`mainRoads` winding roads run along the whole level and a little beyond both ends (from 3 000 before
it), each a sine meander (amplitude and wavelength drawn from ranges) plus a noise wobble, centred
within ±`spread` of the middle. Their centre lines are sampled every `step`. The first `dual.mainRoads`
of them are 2×2 highways (`dual.width` 12, two lanes each way); the others are `mainWidth` (6) wide
with one lane each way. Roads and paths are generated from the level's seed.

**Acceptance criteria**
- Given a level, then it has the main roads asked for, they wind, and the same seed gives the same
  roads (unit tests).

*Sources: P04-R07, D-021, D-029.*

### GFX-ROAD-02 — Paths · MUST

Paths branch off a main road every `crossSpacing` (260–560), to the left or the right with a gentle
bend (up to `crossBend`), `crossWidth` (4) wide, and run to past the screen edge. Each tries both
directions and three bends, and is dropped if no try stays on buildable ground. A path widens to
`junction.width` (14) where it meets its main road and narrows back over `junction.length` (28), so it
merges into the road.

**Acceptance criteria**
- Given a level, then every path runs from a main road to past the screen edge, and widens at its
  junction (unit tests).

*Sources: P04-R07, D-021.*

### GFX-ROAD-03 — Roads only on buildable ground · MUST

No road or path is laid on ground lower than `minHeight` (the sea) or steeper than `maxSlope` (0.5),
and pieces shorter than `minRun` points are dropped. Where a main road cannot go on (water, a steep
slope, a district), it turns off the screen before the obstacle and comes back from the side after
it, trying earlier and earlier points until the turn stays on buildable ground. A section with no
buildable ground has no roads.

**Acceptance criteria**
- Given a level, then every point of a winding road is on buildable ground (unit test).

*Sources: P04-R07, D-021, D-024.*

### GFX-ROAD-04 — No road ends on screen · MUST

No road, path or street starts or ends where the camera can see it: they only end beyond
X = ±`offscreenX`, past the widest ground the camera sees ([camera.md](camera.md)). A main road leaves
the screen by turning towards the nearer side at most `turnRate` per step.

**Acceptance criteria**
- Given every level, then every main road and path starts and ends beyond ±`offscreenX` (unit
  tests).

*Sources: P04-R07, D-021, D-139.*

### GFX-ROAD-05 — No crossings outside the districts · MUST

Outside the districts, roads never cross; they only meet where a path joins a road (`noCrossings`,
`gap` 30). Each main road after the first follows the previous one on the side the first leaves
free, keeping `gap` clear of the roads laid before it. A path keeps `gap` clear of everything but the
main road it starts on, may end on another main road or a street (it is cut there), never on a path,
and only starts where its main road runs more along the level than across it.

**Acceptance criteria**
- Given every level, then no two winding roads or paths cross on screen (unit test).

*Sources: D-046, D-052, D-158.*

### GFX-ROAD-06 — The look of winding roads and paths · MUST

Each winding road and path is a ribbon draped on the ground and cut on the terrain chunks, lifted
`lift` (0.6) and pulled towards the camera in depth so it never flickers against the terrain. Its soft
shoulders (`shoulder`, 2.5) fade to transparent and its surface is slightly see-through (main roads
85 %, paths 60 %) and worn (colour and opacity vary by `wear`, 30 %), so the road blends into the
ground. Main roads are worn dusty asphalt, paths packed dust. Ribbons are blended without writing
depth; paths are drawn before the roads, so the roads stay on top where they meet. Ribbons receive
shadows. The ground under a road is not flattened.

**Acceptance criteria**
- Manual: roads melt into the ground with soft edges, and a road stays on top where a path meets it.

*Sources: P04-R07, D-021.*

### GFX-ROAD-07 — Centre and lane lines · MUST

Main roads have a dashed yellow centre line (4 on, 4 off); paths have none. Roads of 2 or more lanes
each way have a double yellow centre line and white dashed lines between the lanes of one direction.
Lines are painted just above the road surface (`centreLine.lift`) in pieces of 2, so they follow the
ground and stop cleanly at crossings; pieces in a row become one quad while the ground under them
stays within 0.02 of a straight line.

**Acceptance criteria**
- Given a straight road on flat ground, then its line pieces are merged into one quad per run (unit
  test).

*Sources: D-028, D-029, D-137.*

### Districts on the tile grid

### GFX-ROAD-08 — The tile grid · MUST

Each district is laid on one square grid of tiles, aligned with the level's X and Z axes, its tile
edges at multiples of `tile.size` from X = 0 and Z = 0, so the grid is continuous over the whole
district: across its sections, and where a district is cut at the start of the final boss's runout.
Every road piece, building and lot of a district covers whole tiles of that grid. Each tile of a
district is one of three things: road, the footprint of one building or lot, or open ground. No tile
is covered by two of them. The same seed gives the same districts.

**Acceptance criteria**
- Given every level with districts (fixed seeds), then every road piece and every footprint starts on
  a tile edge and covers whole tiles, and no tile is covered twice (unit test).
- Given a district of several sections, or one cut where the runout starts, then all its pieces sit
  on the same grid.

*Sources: P15-R01, D-157.*

### GFX-ROAD-09 — Roads with sidewalks · MUST

Every road of a district has a sidewalk along both outer edges, with a kerb between the sidewalk and
the roadway. A road of size N is N tiles wide, sidewalks included, with N lanes each way and its lane
markings: a centre line, plus lane lines between the lanes of one direction when N ≥ 2. The base
piece, a size-1 straight, is one tile: a roadway of `tile.size − 2 × tile.sidewalk` (6, two 3-unit
lanes) and two sidewalks `tile.sidewalk` (2) wide. A road keeps its size along its whole length: there
is no tapering piece. The sizes used are 1 (streets), 2 (avenues, `dual.avenues` of the grid lines)
and 3 and 4 (World 4's boulevards, `boulevards`).

**Acceptance criteria**
- Given a size-1 road, then its roadway is 6 wide and each sidewalk 2.
- Given a road of size N ≥ 2, then sidewalks run only along its two outer edges and its roadway has N
  lanes each way.
- Given every district, then no road changes size between two junctions.

**Discrepancy:** no road of size 4 is laid: World 4's boulevards are all size 3 (`boulevards`: 3
lanes, 18 wide, 20 % of the lines; `src/game/config/world_4/props.py`, whose comment says "the
4-lane ones dropped, 3 × 3 is enough", reviewer 2026-10-28, commit a34f13b; no decision records it).

*Sources: P15-R02, D-029, D-136, D-157.*

### GFX-ROAD-10 — Sidewalks stand out · MUST

From the playfield camera, the sidewalks can be told apart from the roadway and from the ground round
them: dark asphalt roadway, grey sidewalks, pale kerbs, each world with its own sidewalk colour.

**Acceptance criteria**
- Manual: in a district of each world, sidewalks, kerbs and roadway read apart.

**Discrepancy:** one road look serves every world (`BASE_SCENERY_LOOK.roads.tiles`); its sidewalk
colour is only dimmed by each world's tone ([readability.md](readability.md)), not set per world
(reported as a known limitation of phase 15).

*Sources: P15-R02.*

### GFX-ROAD-11 — The road kit · MUST

For each size N from 1 to 4, the kit has four N × N-tile pieces: a straight, a 90° turn, a T and an X.
Every open side of a piece has exactly the cross-section of the straight piece of its size (roadway,
kerbs, sidewalks, markings), so any two pieces of one size join with no visible seam. At turns, Ts
and Xs the sidewalks go round the corners and stop at the roadway; no sidewalk crosses the roadway,
and lane markings do not cross the junction area.

**Acceptance criteria**
- Given any two pieces of one size joined side to side, then roadway, kerbs, sidewalks and markings
  line up across the joint (unit test on the pieces' edges, and the kit's sample layout).
- Given a turn, T or X, then the sidewalk is continuous round each corner.

**Discrepancy:** the kit has sizes 1 to 3 only (12 pieces; `SIZES = [1, 2, 3]` in
`src/game/view/props/road_kit.py`, "the 4 × 4 roads dropped, reviewer 2026-10-28", no decision).

*Sources: P15-R03.*

### GFX-ROAD-12 — Adapter pieces · MUST

Where roads of sizes N > M meet, an N × N-tile adapter joins them. For every pair of sizes (2-1, 3-1,
3-2, 4-1, 4-2, 4-3) there are two: a T adapter (the size-M road ends on the size-N road, which goes
on straight) and an X adapter (the size-M road crosses it and leaves on the same tiles on the other
side). The size-M road enters on whole tiles of the adapter's sides, as close to the middle as the
grid allows: in the middle when N − M is even, half a tile off when it is odd, either way round. Its
open sides match the size-M straight and the others the size-N straight. A wider road never ends on
a narrower one, and two roads of different sizes never meet at a turn.

**Acceptance criteria**
- Given every district of every level, then no T has a narrower road going on with a wider one ending
  on it, and no turn joins two sizes (unit test).

**Discrepancy:** with the kit's sizes 1 to 3, there are adapters for 2-1, 3-1 and 3-2 only (6).

*Sources: P15-R04, D-157.*

### GFX-ROAD-13 — Wide rows, one-tile columns · SHOULD

In a district the rows (roads across the level) carry the sizes: one tile, avenues and boulevards.
Columns (roads along the level) are one tile wide, and stand where the junction of every wide row they
cross starts on a multiple of that row's size, so every wide row is made of whole N × N pieces and the
column is as close to the middle of its adapter as the grid allows. A wide row is built along its
whole line; one whose ground does not allow it is a one-tile street. The rows shared by two parts of
a district are one tile wide. So adapters between two wide roads are in the kit, but no level lays
them.

**Acceptance criteria**
- Given a district, then a column stands only where its junctions land on the lattice of the wide
  rows it crosses (unit test).

*Sources: D-157.*

### GFX-ROAD-14 — Street layout on the grid · MUST

The streets of a district are laid on the grid using only kit pieces and adapters: each road covers
whole rows or columns of tiles, each stretch of a size-N road between two junctions is a whole number
of N-tile pieces, and each junction is one kit piece or one adapter. Each kind of district keeps its
street spacing (`rows` and `columns` ranges, rounded to whole tiles) and the chance `links` that each
stretch between two crossings is built. The first and last rows of a district are full roads.
Boulevards run straight through their district. Where a tile cannot hold a road (water, ground too
steep), no road is built on it.

**Acceptance criteria**
- Given every district of every level, then every road is made of kit pieces and adapters only, and
  every open side of a piece meets the matching side of another piece, the ground past the screen
  edge, or a winding road (unit test).

*Sources: P15-R05, D-024, D-157.*

### GFX-ROAD-15 — Crossings inside the districts · MUST

Inside the districts, streets cross again: X junctions and adapters occur as well as Ts, whatever
`noCrossings` says for the winding roads. Winding roads and paths outside the districts still never
cross (GFX-ROAD-05).

**Acceptance criteria**
- Given the districts of each world, then both X and T junctions occur in them.

*Sources: P15-R05, D-158.*

### GFX-ROAD-16 — No dead end on screen · MUST

A street of a district that stops on screen goes on straight, or is cut back, until it ends at
another street or off the screen. A stretch cut back is never built again, so the removal always
ends. A stretch whose ground cannot hold a road is never extended over it.

**Acceptance criteria**
- Given every district, then no street ends on screen (unit test).

*Sources: P15-R05, D-024, D-052, D-158.*

### GFX-ROAD-17 — Boulevards · MUST

World 4's street grids have wide boulevards on a share of their lines, picked by a hash of the line so
all its stretches agree: 3 lanes each way (18 wide) on 12 % of the lines and 4 lanes each way (24
wide) on 8 %. A boulevard is built along its whole line and runs straight through its district. Its
markings are a double yellow line in the middle and dashed white lines between the lanes.

**Discrepancy:** World 4 has only 3-lane boulevards, on 20 % of its lines (see GFX-ROAD-09).

*Sources: D-136, P15-R02.*

### GFX-ROAD-18 — Winding roads meet the districts cleanly · MUST

Winding roads and paths keep out of the districts: they turn off the screen before a district and
come back after it, and no path starts in one. Should one reach a district road, it joins it at a T on
the district side, roadway to roadway, with no gap, step or overlap showing. Outside the districts,
roads and paths keep their own shape and look, with no sidewalks and no tiles.

**Acceptance criteria**
- Given each level, then no winding road or path ends inside a district other than on the open side
  of a T piece or T adapter (unit test).

*Sources: P15-R06, P15-R13, D-024.*

### GFX-ROAD-19 — Street grids only where they show · SHOULD

A district's streets end beyond ±`offscreenX`: 420 in Worlds 1 and 2, 300 in Worlds 3 and 4,
where the ground drawn twice as big shows about ±210 of it across the playfield window (±235 at a
sea bed; 240 in Worlds 3 and 4 for ±195 on the old 480 × 640 screen, D-139; 1 000 and 640 for
±500 on the whole 16:9 screen between D-249 and D-252). A street grid the level starts in begins 400
before Z = 0, its first row out of view; the winding roads still begin 3 000 before.

**Acceptance criteria**
- Given the grids of Worlds 3 and 4, then they reach past the ground in view; a grid the level starts
  in starts more than a row of blocks below it (unit tests).

*Sources: D-139, D-140.*

### GFX-ROAD-20 — Street pieces drawn from a road atlas · MUST

Each kind of street piece is painted once, pixel by pixel, into one road atlas (64 pixels a tile,
slots for pieces up to 3 tiles, padded so mipmaps do not bleed), and each piece of a district is drawn
as one surface draped on the ground, cut on a lattice of the world and textured from its slot, so no
stacked layers fight in depth. The roadway's corners are rounded: the sidewalk corners into a
junction get a kerb radius (3), and the outside of a turn sweeps round as a quarter ring. Ts and Xs
get zebra crossings on their arms (stripes 0.6 wide, 0.6 apart, 3 deep), the lane lines stopping
before them. A piece the atlas has no room for is drawn as layers (sidewalk, kerb, roadway, lines).

**Acceptance criteria**
- Manual: in a district, the corners are rounded, Ts and Xs have zebra crossings, and pieces join
  without seams.

*Sources: P15-R03 (phase 15 review, reviewer 2026-10-28).*

### GFX-ROAD-21 — The road atlas reaches every chunk · MUST

The street surfaces of every terrain chunk come with the latest road atlas and its version, from the
ground worker or the main thread alike; each version is uploaded once. A new road look drops the old
look's atlas, and a new seed takes its street surfaces from its own ground. So streets are never
drawn untextured (white), whatever the time the level starts at, after a Retry or a Continue, or for
a level built ahead.

**Acceptance criteria**
- Given a level started at a later time, then its streets show asphalt, sidewalks and kerbs (unit
  tests on the sources; P14-R08 readability e2e on 3-1 and 4-1).

**Discrepancy:** a stage never changes its seed (each level builds its own stage), so "a new seed
takes its street surfaces from its own ground" has no code: the stage's re-seeding, which only
tests called, was removed (D-237).

*Sources: D-217.*

### GFX-ROAD-22 — Opaque street middles · SHOULD

In levels whose roads are all streets, the even middle of each street is drawn opaque and written in
depth (depth offset −1), so the terrain under it is not shaded; its soft edges and lane markings stay
see-through and are drawn over it (depth offset −2), so the markings always stay on top. Elsewhere a
street drawn before a main road or a path would end up under it, so nothing changes there.

*Sources: D-153.*

### GFX-ROAD-23 — Asking whether a spot is clear of the roads · SHOULD

Props ask the road network whether a spot is clear of every road by a given distance; the answer
comes from an index of the road segments in buckets, searching only the buckets a road in reach can
be in, and is the same as comparing the exact distance to the nearest road edge.

**Acceptance criteria**
- Unit test: the clearance answer agrees with the edge distance.

*Sources: D-021, D-138.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `mainRoads` / `spread` | 2 / 200 | `src/game/config/world_1/props.py` `WORLD_1_ROADS` (Worlds 2–4 reuse it) |
| `meander` | amplitude 80–180, wavelength 1300–2600 | same place |
| `mainWidth` / `crossWidth` | 6 / 4 | same place |
| `dual` | width 12, 1 main road, avenues 0.25 of the grid lines | same place |
| `crossSpacing` / `crossBend` | 260–560 / 40 | same place |
| `junction` | width 14, length 28 | same place |
| `offscreenX` | 420 (Worlds 1–2), 300 (Worlds 3–4; 240 before D-249, 640 until D-252) | `src/game/config/world_1/props.py` `WORLD_1_ROADS`, `src/game/config/world_3/props.py` `WORLD_3_ROADS` |
| `turnRate` / `step` / `minRun` | 0.05 / 8 / 6 | `WORLD_1_ROADS` |
| `minHeight` / `maxSlope` | 3 / 0.5 | same place |
| `noCrossings.gap` | 30 | same place |
| `boulevards` | 3 lanes, 18 wide, 20 % | `src/game/config/world_4/props.py` (D-136: 12 % + 8 % of 4 lanes) |
| `tile.size` / `tile.sidewalk` | 10 / 2 | `src/game/config/tile_buildings.py` `TILE` |
| `STREETS_BEFORE` / `LEVEL_MARGIN` | 400 / 3 000 | `src/core/scenery/road_network.py` |
| road look | main (0.36, 0.33, 0.3), path (0.66, 0.57, 0.43), opacity 0.85 / 0.6, shoulder 2.5, street shoulder 0.4, wear 0.3, lift 0.6 | `src/game/config/scenery_look.py` `BASE_SCENERY_LOOK.roads` |
| lines | yellow (0.7, 0.56, 0.12), lanes (0.7, 0.7, 0.66), width 0.35, dash 4, lift 0.05 | `BASE_SCENERY_LOOK.roads.centreLine` |
| tile road look | roadway (0.2, 0.2, 0.22), sidewalk (0.38, 0.37, 0.38), kerb (0.55, 0.54, 0.52), kerb 0.35, line 0.3, lift 0.15 | `BASE_SCENERY_LOOK.roads.tiles` |
| road atlas | 64 px a tile, slots of 3 tiles, 8 × 8 slots, pad 4 | `src/render/scenery/road_atlas.py` |
| corners and zebras | kerb radius 3; zebra depth 3, stripe 0.6, gap 0.6, 1 before the lines | `src/render/scenery/road_paint.py` |

## Notes

- Superseded street rules of phase 4 (still in the engine for street grids without tiles, used by no
  level): street fronts with building slots and setbacks, podiums filling the blocks (`BlockFill`),
  irregular grids of 6-wide streets.
- In practice no winding road or path reaches a district (they keep out of its Z range), so the T
  joints of GFX-ROAD-18 never occur in the levels.
- The `tiles=1` debug option that draws the grid over the districts, and the dev viewer's road kit
  and sample layout, are in [../dev/debug-options.md](../dev/debug-options.md) and
  [../dev/dev-menu.md](../dev/dev-menu.md).
- Known gap: the unit tests over every level (fixed seeds) asked by the acceptance criteria of
  GFX-ROAD-05, -08, -12, -14, -15, -16, -18 and -19 (phase 15's district checks, D-139's and D-140's
  grid checks) were not carried over to the Python port; the engine's own tests on sample levels
  remain.
