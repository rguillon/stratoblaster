# Phase 15 — Urban Rework

> Copy this file to `phase-NN-short-name.md` (e.g. `phase-03-enemies.md`).
> Fill the **Human** sections. Set **Status** to `Ready` when the agent may implement it.
> The agent fills the **Agent** sections and never edits the requirement sections.

**Status:** Ready  <!-- Draft | Ready -->
**Depends on:** Phase 14

---

## 🧑 Goal
Towns, cities and factories are laid out on a grid of 10 m tiles, like a city-building kit. Their roads have sidewalks and are built from a small kit of road pieces (straight, 90° turn, T, X) in sizes 1×1 to 4×4 tiles, plus adapter pieces where roads of different widths meet. Every building, factory and house covers a whole number of tiles, and all of them are new models made for the grid.

## 🧑 Requirements

> ID format `P15-Rxx`. Every requirement is **MUST** (no SHOULD / MAY).
> Write each requirement so it is testable. Add acceptance criteria when "done" isn't obvious.

**Words used in this phase**
- **Tile**: a square of ground `tile_size` on each side (about 10 m × 10 m), the base unit of the grid. The reviewer calls it a "block".
- **District**: a run of sections with a street grid (`TerrainSection.streets`). This phase applies to **every** district: Level Zero (industrial zone, city centre) and Worlds 1 to 4. That includes World 1's desert towns and market town and World 2's mining and company towns, not only the cities and factories (reviewer's choice, 2026-10-28).
- **Road of size N**: a road with N lanes each way, N tiles wide, sidewalks included (N = 1 to 4). Size 1 has one lane each way and a sidewalk on both sides.
- **Road piece**: one piece of a road of size N, N × N tiles: straight, turn, T, X, or an adapter (R04).
- **City block**: the rectangle of tiles between the roads of a district.
- **Footprint**: the W × D tiles a building or lot prop stands on.

### P15-R01 — The tile grid  · MUST
Each district is laid on one square grid of tiles. The grid is aligned with the level's X and Z axes and is continuous over the whole district: across its sections, and where the runout starts (the districts cut at the runout, reviewer 2026-10-28). Every road piece, building and lot prop of a district covers whole tiles of that grid. Each tile of a district is one of three things: road, the footprint of one building or lot prop, or open ground.

**Acceptance criteria**
- [ ] Given every level with districts (fixed seeds), when its districts are generated, then every road piece and every footprint starts on a tile edge and covers whole tiles (unit test over all levels).
- [ ] No tile is covered by two road pieces, by two footprints, or by a road piece and a footprint.
- [ ] Given a district made of several sections, or one cut where the runout starts, then all of its pieces and footprints sit on the same grid, with no shift at the boundaries.
- [ ] The same seed gives the same districts (ENG-18).

### P15-R02 — Roads with sidewalks  · MUST
Every road of a district has a sidewalk along both edges, with a kerb between the sidewalk and the roadway. A road of size N is N tiles wide, sidewalks included. It has N lanes each way and lane markings: a centre line, plus lane lines between the lanes of one direction when N ≥ 2. The base piece, a size-1 straight, is one tile: two lanes (one each way) and two sidewalks. A road keeps its size along its whole length.

The sizes used are 1 (streets), 2 (the 2×2 avenues of today) and 3 and 4 (World 4's boulevards). The share of each size in each world stays as it is today (`RoadRules.dual.avenues`, `RoadRules.boulevards`).

**Acceptance criteria**
- [ ] Given a size-1 road, its roadway is `tile_size − 2 × sidewalk_width` wide and each sidewalk is `sidewalk_width` wide.
- [ ] Given a road of size N ≥ 2, sidewalks run only along its two outer edges, and its roadway has N lanes each way.
- [ ] No road of a district changes size between two junctions (there is no tapering piece).
- [ ] From the playfield camera, the sidewalks can be told apart from the roadway and from the ground around them (`sidewalk_colour`, per world).

### P15-R03 — The road kit  · MUST
For each size N from 1 to 4, the kit has four N × N-tile pieces: a straight, a 90° turn, a T and an X (16 pieces). Every open side of a piece has exactly the cross-section of the straight piece of the same size (roadway, kerbs, sidewalks, markings), so any two pieces of one size join with no visible seam. At turns, Ts and Xs, the sidewalks go round the corners and stop at the roadway. Lane markings do not cross the junction area.

**Acceptance criteria**
- [ ] The 16 pieces exist and are shown on the `props/` page (R10).
- [ ] Given any two pieces of the same size joined side to side, then roadway, kerbs, sidewalks and markings line up exactly across the joint (unit test on the edge profiles of the pieces, plus the sample layout of R10).
- [ ] Given a turn, T or X, then the sidewalk is continuous round each corner, and no sidewalk crosses the roadway.

### P15-R04 — Adapter pieces  · MUST
Where roads of different sizes N > M meet, an adapter piece of N × N tiles joins them. For every pair of sizes (2-1, 3-1, 3-2, 4-1, 4-2, 4-3) there are two adapters:
- a **T adapter**: the size-M road ends on the size-N road, which goes on straight;
- an **X adapter**: the size-M road crosses the size-N road.

The size-M road enters the adapter on whole tiles of its sides, as close to the middle as the grid allows: in the middle when N − M is even, half a tile off the middle when it is odd (reviewer's choice, 2026-10-28). Both off-centre positions can be placed (mirrored). The open sides of the size-M road match the size-M straight piece, and those of the size-N road match the size-N straight piece.

A wider road never ends on a narrower one, and two roads of different sizes never meet at a turn.

**Acceptance criteria**
- [ ] The 12 adapters (T and X for each of the 6 pairs; a mirrored position may be the same model turned) exist and are shown on the `props/` page.
- [ ] Given an X adapter, the size-M road leaves it on both sides on the same tiles, so it goes on straight.
- [ ] Given every district of every level, no T has a narrower road going on with a wider road ending on it, and no turn joins two sizes (unit test).

### P15-R05 — Street layout on the grid  · MUST
The streets of a district are laid on the grid, using only pieces from the kit. Each road covers whole rows or columns of tiles. Each stretch of a size-N road between two junctions is a whole number of N-tile pieces, and each junction is one piece of the kit or one adapter.

**Kept from today:**
- the street spacing of each kind of district (today's `StreetGrid.rows` and `columns` ranges, rounded to whole tiles);
- the chance that each stretch is built (`links`);
- no dead end on screen;
- the first and last rows of a district are full roads;
- boulevards run straight through their district.

**Changed:** streets inside districts cross again, at X junctions and adapters as well as at Ts (reviewer's choice, 2026-10-28). This amends D-046 (phase 6 review, "no crossings") **for districts only**: winding roads and paths outside districts still never cross.

Where a tile cannot hold a road (water, or ground that is too steep: World 3's canals, World 4's river quays), no road is built on it. The roads that would reach it are cut back as they are today, so no dead end shows on screen.

**Acceptance criteria**
- [ ] Given every district of every level, every open side of every road piece meets one of three things: the matching open side of another piece, the ground past the screen edge (beyond `offscreenX`), or a winding road or path (R06) (unit test).
- [ ] Both X and T junctions occur in the districts of each world.
- [ ] Each road size that a world used before this phase still occurs in it.
- [ ] Every road in a district is made of kit pieces and adapters only: no other shape.

### P15-R06 — Joining the winding roads  · MUST
A winding road or path from outside a district (P04-R07, phase 6 rules) that reaches a district road joins it at a T on the district side, roadway to roadway. No gap, step or overlap shows from the playfield camera. Outside districts, roads and paths keep their current shape and look, with no sidewalks.

**Acceptance criteria**
- [ ] Given each level where a path or winding road reaches a district, its end lies on the open side of a T piece or T adapter of the district road (unit test).
- [ ] No gap or overlap shows at those joints (manual check, in the levels listed in the checklist).

### P15-R07 — Buildings sized in tiles  · MUST
This applies to every building, factory, house and other structure that can stand in a district, which means every model of the building groups listed in R09. Each one has a footprint of W × D whole tiles (W, D ≥ 1, not necessarily square), declared in the game config. Seen from above, its model stays inside that footprint at every height, `building_margin` from its edges: no roof, crane, chimney or pipe overhangs it.

It is placed at scale 1 (no random scale) and turned by quarter turns only (W and D swap). Outside districts, these models keep today's placement rules (along roads, in hamlets, as lone buildings), also at scale 1.

**Acceptance criteria**
- [ ] For every such model, a unit test builds it (`NullEngine`) and checks that its X/Z bounding box fits in its W × D tiles, minus `building_margin` on each side.
- [ ] Given every district of every level, every building stands on exactly its W × D tiles, at a quarter turn.
- [ ] No building floats above or sinks into the ground at a corner of its footprint, as seen from the playfield camera.

### P15-R08 — Filling the city blocks  · MUST
Each city block is packed with buildings of its section's groups, on whole tiles, without overlapping each other or the roads. A building that touches a road faces it: its front (declared with the model) is on a road side, and a corner building faces one of its roads. The share of a block's tiles covered by buildings follows the section's `buildingDensity`. At 1, every tile is covered (downtown, heavy industry, Level Zero's city centre).

Footprints of several sizes are mixed, so a district never looks like a checkerboard of equal squares (phase 4 review). A building larger than its block is never chosen. The tiles left over are open ground (the section's ground) or lot props (R09). The section's trees and plants grow only on open tiles and on lot props (parks, gardens), never on a road tile or a building's tile.

In districts, this replaces two arrangements from the phase 4 review: buildings in slots along the streets (`slotSpacing`, `setback`) and filled blocks (`BlockFill`).

**Acceptance criteria**
- [ ] Given every section with a district (fixed seeds), the share of its block tiles covered by buildings is within `density_tolerance` of its `buildingDensity`.
- [ ] Given every section with a district and buildings, at least 3 different footprints are placed in it, and no single footprint makes up more than `max_footprint_share` of its buildings.
- [ ] Every building that touches a road has its front on a road side (unit test).
- [ ] No tree or plant stands on a road tile or a building's tile.

### P15-R09 — New models  · MUST
New building models made for the grid replace every model that stood in a district. Every building group used by a district gets them:
- **Level Zero**: heavy industry (industrial zone), city (city centre);
- **World 1**: desert homes, outposts, villages (desert towns, market town);
- **World 2**: worker homes, mines, oil, refinery, industrial, heavy industry;
- **World 3**: heavy industry, industrial, docks, workshops, worker flats, terraces, suburbs, villages;
- **World 4**: town centre, mid-rise, offices, towers, skyscrapers, downtown, and the World 3 home groups it reuses.

Each group gets at least `models_per_group` models (a model shared by several groups counts for each of them). It has at least `footprints_per_group` different footprints, at least one of them not square, within the ranges of the footprint table below.

Each model keeps the character of the group it replaces, as described in P06-R06, P08-R07, P09-R06 and P10-R03. Some examples:
- chimneys and glowing furnaces for the foundries;
- cooling towers at the power plant;
- container yards and cranes on the docks;
- gardens round the suburban houses;
- glass towers downtown.

The models are generated from code in the darksynth style (GD-60), with lit windows and neon accents for the night levels.

There are also at least `lot_props` lot props for open tiles, with footprints from 1×1 to 2×2: a car park, a paved yard, a plaza, and a small park or garden. All worlds share them, coloured by each world's look.

Building models that no level places after this phase are removed with their tests, and the `props/` page no longer shows them.

**Acceptance criteria**
- [ ] For every group listed above, the config gives at least `models_per_group` models and `footprints_per_group` footprints, including a non-square one, all within the footprint table (unit test).
- [ ] The new models and road pieces pass the phase 14 checks: the background brightness cap (P14-R01) and the reserved colours (P14-R02).
- [ ] No model of the removed set is still registered in the game's view.

### P15-R10 — The kit and the models on the `props/` page, the grid in levels  · MUST
The `props/` page shows:
- a **Road kit** group with the 16 road pieces and the 12 adapters, each on a visible tile grid, with its name and size;
- a **sample layout** that joins every piece and adapter at least once, to check the joints;
- the new building models and lot props, grouped by building group. Each one stands on the tile grid with its footprint in tiles next to its name (e.g. `3×4`).

In a level, the URL debug option `tiles=1` (alongside the others, e.g. `?level=4-5&tiles=1`) draws the tile grid over the districts.

**Acceptance criteria**
- [ ] e2e: the `props/` page shows the Road kit group with at least 28 entries and the sample layout, and every building model has its footprint label.
- [ ] e2e: one level of each world, and Level Zero, load with `tiles=1` without console errors.

### P15-R11 — Cars on the new roads  · MUST
Cars keep driving on the district roads as they do today: along the straight runs, in lanes, hidden near the ends (phase 4 review). They use the lanes of the new road sizes. They drive on the roadway only, never on a sidewalk, a building or open ground, and go straight through X junctions.

**Acceptance criteria**
- [ ] Given every car lane in every district, its centre line lies within the roadway of every piece it passes (unit test).

### P15-R12 — Performance  · MUST
The phase 13 budgets hold with the new districts:
- level loading within `level_load_max_s`;
- long frames within `max_long_frames_per_min`, and no frame over `freeze_ms`;
- 60 FPS (ENG-101) and fewer than 200 draw calls (ENG-106) in the busiest districts: 2-5 at night, downtown in 4-5, and Level Zero's city centre.

Road pieces and repeated models are drawn with instances (ENG-104).

**Acceptance criteria**
- [ ] The P13-R01 measurement is run again on a World 1 desert town level, 2-5, 3-1, 4-5 and Level Zero, and the report gives the figures before and after this phase.
- [ ] The triangles in view at the busiest moment of 2-5, 4-5 and Level Zero's city centre are no more than at the end of phase 14 (both figures in the report).

### P15-R13 — Nothing else changes  · MUST
These stay as they are:
- each level's sections, length, scroll speed, looks (time of day, weather, lava), waves, bosses and music;
- the places each level shows, in the same order, with the same slow transitions between them (P06-R05, P08-R03, P09-R03, P10-R03): desert towns, mines, factories, docks, suburbs, villages, offices, skyscrapers…;
- outside districts, the ground, winding roads, paths, hamlets, lone buildings, trees and other props. The only exception is the R09 building models that also stand there.

The phase 14 readability checks still pass.

**Acceptance criteria**
- [ ] The existing unit and e2e tests on level contents (sections, durations, waves, bosses, looks) pass unchanged, except those about the street fronts, filled blocks and old models that this phase replaces.
- [ ] The P14-R08 readability e2e check passes for every world.

## 🧑 Tunable values
| Name | Value | Notes |
|------|-------|-------|
| tile_size | 10 world units | About 10 m; one size-1 road piece. Chosen so buildings stay about their present size next to the ships. |
| sidewalk_width | 2 world units | Per side. Leaves today's 6-unit roadway (two 3-unit lanes) on a size-1 road. |
| road_sizes | 1, 2, 3, 4 | Lanes each way = tiles wide (R02) |
| sidewalk_colour | per world | In each world's look (R02) |
| building_margin | 0.5 world unit | Gap from a model to the edges of its footprint (R07) |
| models_per_group | 5 | R09; a shared model counts for each group |
| footprints_per_group | 3, at least 1 not square | R09 |
| lot_props | 4 | R09: car park, paved yard, plaza, park or garden |
| density_tolerance | 0.1 | R08 |
| max_footprint_share | 60 % | R08 |
| street spacing | today's `StreetGrid` ranges, rounded to whole tiles | R05 |

**Footprint ranges** (in tiles, W × D, either way round; R09):
| Groups | Footprints |
|--------|------------|
| Houses, cottages, desert homes, outposts, village houses | 1×1 – 2×2 |
| Terraces (rows of houses) | 1×2 – 1×4 |
| Worker flats, workshops, farm buildings, greenhouses | 1×2 – 2×3 |
| Town centre, mid-rise, offices | 2×2 – 3×3 |
| Towers, skyscrapers | 2×2 – 3×3 |
| Downtown skyscrapers | 3×3 – 4×4 |
| Mines, oil, refinery, docks | 1×1 – 3×4 |
| Industrial (factories, warehouses, container yards, tanks, cooling towers) | 2×2 – 3×4 |
| Heavy industry (plants, works, foundries) | 3×3 – 4×6 |
| Lot props | 1×1 – 2×2 |

## 🧑 Out of scope for this phase
- Winding roads and paths outside districts: no sidewalks, no tiles, same shapes, and they still never cross.
- Bridges over rivers and canals.
- Street furniture: street lamps, traffic lights, signs, trees on the sidewalks, zebra crossings.
- Cars turning at junctions or stopping at crossings; new car models.
- Roads that change size along their length (tapers); diagonal or curved streets in districts.
- The title screen's city (`city-geometry.ts`) and boss models that carry cities.
- New sections or levels; changes to the order of places in a world.
- Props that are not buildings outside districts (trees, rocks, plants, desert and ice props).

## 🧑 Engineering additions for this phase
- Engine / game split (ENG-140 to ENG-148): the tile grid, the choice of road pieces and adapters, the street layout on the grid and the packing of footprints are generic engine code in `core/scenery/`. That code is pure and deterministic, and is tested with the sample game in `tests/fixtures/` (ENG-145). Tile size, road sizes, sidewalk width, the look of the pieces, the models, the footprints and the groups live in `src/game/`.
- Unit tests over every level with districts (fixed seeds) for R01, R04, R05, R07, R08 and R11, named with the requirement IDs.
- e2e tests named with the IDs for R10, covering one level of each world with districts and Level Zero.
- `DECISIONS.md`: one entry amending D-046 for districts (streets cross again inside districts), and one listing the removed models.
- Coverage never decreases (ENG-44); report old vs. new figures.

## 🧑 Manual validation checklist
- [ ] Runs on GitHub Pages / `make dev` without console errors
- [ ] `props/`: the road kit has a straight, a turn, a T and an X in sizes 1 to 4, plus the adapters; the sidewalks go round every corner; the sample layout shows no seam between pieces
- [ ] `props/`: every building shows its footprint in tiles and fits it; some footprints are not square; the houses, factories and towers are new and made for the grid
- [ ] In a level with `&tiles=1`, the roads and buildings line up with the grid
- [ ] A World 1 desert town, the 2-5 factories at night, World 3's docks and suburbs, 4-5 downtown and Level Zero's city all show roads with sidewalks, T and X crossings, and adapters where a street meets an avenue or a boulevard; the buildings fill whole tiles and face the streets, and nothing stands on a road
- [ ] Blocks don't look like a checkerboard of equal squares
- [ ] Cars stay on the roadway, in their lanes
- [ ] Levels load as fast as before and run at 60 FPS in the busiest districts

## 🧑 Notes, references, sketches
- Reviewer's request (in chat, 2026-10-28), lightly edited: "Completely rework the way props are managed in urban/factory areas, with a grid of blocks. The roads need sidewalks; a single slice of two-sided road with sidewalks is the base unit, about 10 × 10 m. Two-sided roads need a straight block, a 90° turn block, a T block and an X block. Apply the same concept to roads with more lanes: they always use a round number of blocks (2×2, 3×3…), so there are also adapter T and X blocks where two roads of different sizes cross. The other props (buildings, factories, houses…) always have a size that is a multiple of blocks; they don't all have to be square. Generate new models for this approach."
- Choices made with the reviewer while writing this spec (2026-10-28):
  1. Every street grid switches to tiles, in World 1 and World 2 towns as well as in cities and factories, so the engine keeps a single street system.
  2. Streets inside districts cross again (amends D-046 for districts only).
  3. Adapters stay on the grid: the narrower road is half a tile off the middle when the difference in size is odd.
- Cross-section of a size-1 straight piece (one tile, `tile_size` = 10):
  ```
  |<- 2 ->|<--- 3 --->|<--- 3 --->|<- 2 ->|
   sidewalk   lane ↑      lane ↓   sidewalk
          kerb      centre      kerb
                     line
  ```
- A 1-tile street crossing a 2×2 avenue (X adapter 2-1; each cell is one tile):
  ```
        | |
        | |
    ====+-+====
    ====+-+====
        | |
        | |
  ```
  The street takes one of the two tiles of the adapter's side: it stays on the grid, half a tile off the avenue's middle.

---

## 🧑 Review feedback
> After the agent reports, write corrections here, then say **"Fix phase 15"**.
> The agent ticks each item when fixed.

- [ ] 

---

## 🤖 Implementation report
> Filled by the agent. Do not edit (comment in Review feedback instead).

### Questions / blockers
None. The three choices were made with the reviewer when the spec was written.

### Plan
| Task | Requirement IDs |
|------|-----------------|
| Tile grid, street layout on tiles (rows carry the sizes, one-tile columns on the rows' lattices), crossings in districts | R01, R02, R05 |
| Road pieces from the streets (straight, turn, T, X, adapters), draped geometry with sidewalks, kerbs, lines | R02, R03, R04 |
| Packing blocks with buildings of whole tiles, facing the streets, lots | R07, R08 |
| 111 models made for the grid (38 archetypes), groups and footprint table; old district models removed | R09 |
| `props/` road kit, sample layout, footprint labels; `tiles=1` in levels and `level_zero/` | R10 |
| Car lanes off the sidewalks | R11 |
| Perf: generation profiled and cached (corner heights, numeric tile keys) | R12 |
| Old tests adapted; new unit and e2e tests | R13 |

### Requirement traceability
| ID | Status (Done / Partial / Not done) | Code | Tests | Notes |
|----|-----------------------------------|------|-------|-------|
| P15-R01 | Done | `core/scenery/tile-streets.ts`, `road-tiles.ts` | `tiles.test.ts`, `tile-districts.test.ts` | Grid from X = 0, Z = 0, so runout cuts stay on it |
| P15-R02 | Done | `tile-road-geometry.ts`, `TILE` in `game/config/tile-buildings.ts`, look `roads.tiles` | `road-kit.test.ts`, `tiles.test.ts` | Sidewalk colour shared, dimmed per world by P14 `toned` |
| P15-R03 | Done | `road-tiles.ts`, `tile-road-geometry.ts`, `game/view/props/road-kit.ts` | `road-tiles.test.ts`, `road-kit.test.ts` | |
| P15-R04 | Done | same | same | Wide–wide adapters (3-2, 4-2, 4-3) are in the kit only (D-157) |
| P15-R05 | Done | `tile-streets.ts`, `street-dead-ends.ts` (`keepCut`) | `tiles.test.ts`, `tile-districts.test.ts` | Amends D-046 in districts (D-158) |
| P15-R06 | Done | (no change) | `tile-districts.test.ts` | No winding road or path ever reaches a district (they keep out of its Z range since phase 4), so no joint exists |
| P15-R07 | Done | `district-packing.ts`, `tile-packing.ts`, `game/view/props/tile-*.ts` | `tile-models.test.ts`, `tile-districts.test.ts` | |
| P15-R08 | Done | same | `tiles.test.ts`, `tile-districts.test.ts` | Lots count in the density share (D-159) |
| P15-R09 | Done | `tile-buildings.ts`, `tile-model.ts`, `tile-*.ts` | `tile-models.test.ts`, `prop-models.test.ts` | 21 groups, 111 models + 5 lots; removed models in D-160 |
| P15-R10 | Done | `prop-groups.ts`, `road-kit.ts`, `prop-viewer-panel.ts`, `debug-options.ts`, `road-field.ts` | `road-kit.test.ts`, `e2e/urban-tiles.spec.ts` | |
| P15-R11 | Done | `traffic.ts` (`CarRules.sidewalk`) | `tiles.test.ts`, `tile-districts.test.ts` | |
| P15-R12 | Partial | `tile-packing.ts` (`TileGround`), numeric `tileKey` | `e2e/perf.spec.ts` (P13 load budget passes) | Reference-machine table not measured, see limitations |
| P15-R13 | Done | — | existing suites; `runout.test.ts`, `scenery-levels.test.ts`, `prop-models.test.ts` adapted | P14 readability e2e passes for every world |

### Gate results
```
Light verification (implementation): make typecheck ✔ / build ✔ / e2e 138 passed.
Lint, unit tests and coverage are deferred to /validate-phase.
Note: port 4173 was held by a `vite preview` of another project (/home/renaud/pewet), which
Playwright reused (reuseExistingServer); the e2e run was repeated on port 4174 with a temporary
config, not committed.
```

Ground generation (Node, fixed seeds, whole level with runout), before → after:
| Level | 0 | 1-5 | 2-4 | 2-5 | 3-1 | 4-1 | 4-5 |
|---|---|---|---|---|---|---|---|
| ms | 141 → 193 | 211 → 444 | 221 → 549 | 209 → 470 | 186 → 345 | 170 → 348 | 94 → 236 |
| buildings | 4.9k → 10.1k | 17k → 63k | 21k → 47k | 21k → 37k | 12k → 28k | 20k → 52k | 13k → 24k |

### How to test manually
- `props/`: group **Road kit** (each piece, `road-sample` joins every piece to straights), groups **Tiles: …** (footprints in the button names), **Tiles: lots**.
- Levels with the grid: `?level=1-5&t=200&tiles=1`, `?level=2-5&t=200`, `?level=3-3&t=120`, `?level=4-5&t=200&tiles=1`; `level_zero/?tiles=1`.
- Look for sidewalks, X and T crossings, adapters where a street crosses an avenue or boulevard, buildings filling whole tiles and facing the streets, cars in their lanes.

### Deviations from spec
- Wide roads are rows only; columns are one tile (D-157), so the wide–wide adapters never appear in levels.
- Lots count in a section's density share (D-159).
- Models no level placed before this phase (frozen, jungle) are kept, as before; only the replaced ones are removed (D-160).

### Known limitations
- R12: the before/after table on the reference machine (load time, long frames, triangles in view) was not measured here (no GPU browser); the P13 e2e load budget passes. Districts hold 1.5–3.7× as many (smaller) buildings, so triangles in view may be higher in 1-5 and 4-1 — please check FPS and the F3 overlay.
- In two final-boss runouts (3-1, 3-4) one row end can still meet nothing (seen only during the boss fight).
- The sidewalk colour is one tunable for all worlds (per-world dimming by P14).

### Suggestions for future phases
- Street lamps and zebra crossings on the kit; bridges over the canals and the river.
- Wide columns (avenues along the level) with a lattice that keeps 2, 3 and 4 apart.
