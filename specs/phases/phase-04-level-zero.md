# Phase 04 — Level Zero

> Copy this file to `phase-NN-short-name.md` (e.g. `phase-03-enemies.md`).
> Fill the **Human** sections. Set **Status** to `Ready` when the agent may implement it.
> The agent fills the **Agent** sections and never edits the requirement sections.

**Status:** Ready
**Depends on:** Plase 3

---

## 🧑 Goal

Level Zero is a test level used to build the components to generate the real levels.

Level zero is reachable from the main menue as the first level.

## 🧑 Requirements

### P04-R01 — Generated heightmap  · MUST

The base of each level shall be a software sculpted heightmap that can be used to generate montains, canyons or stay relativly flat.
Software generated textures that fade between each others according to the slope or altitude shall be used to create realistic terrains.

**Acceptance criteria**
- [ ] Manual visual validation


### P04-R02 — Sea level  · MUST

An optional sea level shall allow to simulate nice looking water (reflecting the sun)

**Acceptance criteria**
- [ ] Manual visual validation

### P04-R03 — Cloud layers  · MUST

Optional cloud layers with adjustable intensity and opacity shall allow to simulate clouds.

**Acceptance criteria**
- [ ] Manual visual validation

### P04-R04 — Props  · MUST

Flat area on the ground shall populated with props. The base props for starting are several industrial buildings, technical/scientific stuff, futuristic looking homes and dead trees.

**Acceptance criteria**
- [ ] Manual visual validation


### P04-R05 — Camera  · MUST

The camera shall be on the top, pointing down, angled 35% to the back.

**Acceptance criteria**
- [ ] Manual visual validation

### P04-R06 — Duration  · MUST

Level zero shall last around 3 minuteS.

### P04-R07 — Roads  · MUST

Randomly generated roads or paths shall run across the maps. The building props shall only be placed along those roads.

**Acceptance criteria**
- [ ] Manual visual validation

---

## 🧑 Review feedback

- [x] Improve the roads (the corners look bad), add a central yellow line and some cars. *Fixed (D-028):*
  - *Corners: each street goes on by half its width past both ends, under the street it meets, so corners are square with no notch. Streets get a narrow soft edge (0.4 instead of 2.5), so the edges of crossing streets no longer pile up into dark patches.*
  - *Yellow centre line: solid along the streets, stopping where another street crosses; dashed (4 on, 4 off) along the main roads; none on the paths. It is painted in pieces of 2 just above the road surface, so it follows the ground.*
  - *Cars: 6 models (4 sedan colours, a van, a truck), with headlights and red tail lights. They stand in one lane each way of the streets and main roads, facing their way (right-hand traffic), with a 30 % chance per road point. None stands in a crossing. Placement is a pure hash, so terrain chunks agree (`core/scenery/road-traffic.ts`).*
- [x] Add more props in the city, larger ones if needed: no ground should show. *Fixed (D-027 follow-up):*
  - *The city's blocks are filled again, without podiums: the `blocks` option now accepts no podium, and then puts buildings on the ground in every part of the block, side by side.*
  - *Blocks are cut into parts of about 30, now up to 4 × 4. Each part gets the largest city kind that fits it, so the existing families (up to `city-block`) are big enough and no new family was needed.*
  - *Block buildings now take their ground, so trees keep out of them.*
  - *A unit test covers blocks filled without podiums. The district e2e test is split in two (meadows and industrial zone; city centre), to keep margin under SwiftShader. No timeout was changed.*
- [x] The building lights look bad under the clouds: the clouds make them brighter. *Fixed:* the glow layer was composed after every mesh, so the glow of the lights was added on top of the clouds. The clouds now draw in the next rendering group (keeping its depth), and the glow is composed right after the group below them, so the clouds cover the glow like the rest of the ground.
- [x] The city is still a bunch of squares: make it more diverse, with the same road pattern as the factory. *Fixed (D-027):*
  - *The city centre now uses the industrial zone's street maze (rows 45–90 apart, columns 50–110 apart, 60 % of links) and, like it, gets its buildings along the streets. Block podiums are gone from the city (D-026 superseded); the block fill stays as an engine option.*
  - *City buildings are assembled from lots: small ones fill one lot; medium ones are split into 2 or 3 unequal lots, and the largest into 4. Each lot has its own facade and is one of: a stepped tower (1–3 tiers on a plan as long as its lot), a round octagonal tower with lit rings, a low slab with roof units and a neon sign, a courtyard block, or an L-shaped block with a taller corner wing. Towers stand on a low base covering their lot, so little ground shows.*
- [x] The city is too much a series of squares: make it more diverse, like the factory. *Fixed:*
  - *The city's street grid is now irregular like the industrial zone's: rows 45–95 apart, columns 50–110 apart, 70 % of links built, so blocks vary in size and merge where a street is missing.*
  - *Podium heights vary more, from 3 to 18.*
  - *Each block is cut into parts of about 30 units (up to 3 × 3), with 2–9 towers on each podium. Each tower is shifted within the room its part leaves, so towers do not line up.*
- [x] Make the skyscraper bases bigger and pack them more: no grey ground visible in the city. *Fixed (D-026):*
  - *The street grid now also gives its blocks: the ground between the streets of each cell, up to 0.5 from the street edge, or to the middle of a street that was not built.*
  - *In the city centre (`blocks` section option), each block gets a podium stretched to cover it, 5–12 high. A podium is a unit-square model with window rows and a lit band; there are 4 variants, and thin instances now take a per-axis size.*
  - *2–4 towers stand on each podium, one per quarter of the block, chosen among the city kinds that fit there. Street-front slots are skipped in those sections.*
  - *A unit test checks that every point of a filled district is on a street or in a block.*
- [x] Create bigger props for the factories and the city, the blocks look empty. *Fixed (D-025):*
  - *The generators made of parts now take a size. They add two families for each district: industrial works (half-side 18) and plants (30), and city towers (14) and blocks (24, a wide podium with towers on it). That makes 69 models.*
  - *The industrial zone has its own building group, made mostly of plants and works. The city's group is made mostly of blocks and towers.*
  - *Buildings with a square plan (`frontage`) stand right at the street setback and pack edge to edge, using a box overlap test instead of a circle around their diagonal.*
  - *A slot whose building does not fit tries up to 3 smaller kinds of its group.*
  - *Slots are every 24 units instead of 34; the wasteland densities were scaled by 0.7 to keep their look.*
- [x] In the factory area, remove the vertical roads and horizontal paths: only straight road segments that merge into each other, same for the city. Create more diverse factory and building parts. Make the buildings less shiny, they look like they are blinking when the ship advances. *Fixed (D-024):*
  - *The winding roads and the paths now stay out of the industrial zone and the city centre: they turn off the screen before them.*
  - *The districts get a network of straight streets on a rectilinear grid. Rows are 45–90 apart and columns 50–110 apart in the industrial zone (60 % of links built: a maze); in the city they are a regular 62–66 × 72–76 grid (92 % built). The first and last rows of a section are full streets.*
  - *No street ends on screen: a street that stops at a crossing goes on straight, or is cut back, until it ends at another street or off the screen.*
  - *Streets are opaque and evenly coloured, so crossings and T-junctions merge without seams. Buildings line them, aligned with the grid.*
  - *New buildings assembled from parts. Eight industrial complexes: a hall with one of four roofs (flat with units, sawtooth, pitched, barrel), 0–3 chimneys, a side strip with tanks, an annex or a pipe rack, and lit doors. Eight city buildings: 1–3 tiers stepping back, five facade and three window colours, five crowns (spire, antenna, pyramid, helipad, roof units), and sometimes a neon sign.*
  - *Blinking. The shadow map no longer re-fits itself to the scene every frame: it has a fixed 1600-unit frustum and the sun moves by whole shadow texels, so shadows stop swimming. Props and terrain are matte (no specular). Window bands are fewer and thicker, and the glow is softer (0.5 → 0.3).*
- [x] Add a section at the end of Level Zero with more green ground, grass and trees; then an industrial section, a dense road maze packed with various buildings; then a final city centre section. *Fixed (D-023):*
  - *Three sections now end the level: **meadows** (1:54), **industrial zone** (2:16) and **city centre** (2:38). The other sections were shortened so the level still lasts exactly 3:00 (P04-R06), and the final plains section was removed.*
  - *Sections can cover their ground with grass ("lush") or concrete ("paved"). Both are new generated textures, blended in the terrain shader in noisy patches, and fade over the section transitions.*
  - *Sections can choose their tree kinds and building groups. Three new living trees (conifer, broadleaf, bush) grow in the meadows. Two new industrial buildings (container yard, refinery) join the industrial group. A new city group (glass tower, office block, apartment block, stepped tower) appears only in the city centre.*
  - *Sections can have a street grid. Streets across run every 50–95 units (industrial, a maze) or every 62–66 units (city, regular blocks), from screen edge to screen edge. Streets along the district (4 wobbling, then 5 straight) turn off the screen at both ends, or run on past the end of the level.*
  - *Buildings are now decided once for the whole level, main roads first, and none may overlap another. That allows dense packing (building density 1 in the new districts). Trees keep clear of buildings too.*
  - *City windows are flat quads (2 triangles a face) in dimmer colours, so hundreds of them neither bloom into white blobs nor cost a million triangles.*
- [x] Make sure the roads start and end off screen, not in the middle of the screen; work on the merging between a path and a road: the road stays on top, the path widens at the junction. *Fixed:*
  - *Roads only start and end beyond X = ±420, past the widest ground the camera sees (about ±390, checked by a test against the camera framing).*
  - *Where a main road cannot go on (sea, steep slope), it now turns off the screen before the obstacle and comes back from the side after it, trying earlier points until the turn is on buildable ground.*
  - *Paths run from a main road to past the screen edge. Each tries both directions and three bends, and is dropped if none stays on buildable ground. They now start only on road pieces that pass there (29 paths in Level Zero, was 12).*
  - *Paths widen from 4 to 14 at their junction, narrowing back over 28 units.*
  - *Paths are drawn in their own mesh layer before the roads, so the roads stay on top.*
  - *The road slope limit went from 0.35 to 0.5, so dirt paths can cross rolling ground (D-021).*
- [x] Make the roads blend better with the ground. *Fixed: each ribbon now has soft shoulders (2.5 units) on both sides that fade to transparent, so the road melts into the ground. Its surface is slightly see-through (main roads 85 %, paths 60 %), so the ground texture shows through. Colour and opacity vary along the road (30 % wear). The ribbons are drawn blended without writing depth, so crossings mix instead of hiding each other.*
- [x] The clouds can pass through the heightmap, it looks bad: make sure the clouds stay on top. *Fixed: the height field now has a ceiling, a height its ground never exceeds whatever the seed (top of each section's relief or peak cap, flattened band or sea bed). The stage lifts any cloud layer to at least 15 units above that ceiling. Level Zero's layers moved from 170 / 250 to 265 / 295, above the peaks (≤ 250) and under the ships (320) (D-022).*
- [x] Add (in the code and in the specs) randomly generated roads or paths on the maps and only place the building props along those roads. *Fixed: requirement P04-R07 added at the reviewer's request. Two winding main roads run along the level, with paths branching off them every 260–560 units. All are generated from the seed and break where they would run into the sea or up steep slopes. Buildings now stand only in slots along roads and paths, set back from the edge and facing the road; trees keep off them (D-021).*
- [x] Reduce the scale of the props, make them look like the plane is further away. *Fixed: buildings are drawn at ×0.5–0.65 (was ×1.1–1.4) and dead trees at ×0.45–0.75 (was ×0.9–1.5). Footprints shrink to match: the model radius at its largest scale, now checked by a test. The candidate grid goes from 80 to 50 units so the ground keeps its density. The plains now hold about 700 props and the scene draws about 190k triangles (was about 130k).*

---

## 🤖 Implementation report
> Filled by the agent. Do not edit (comment in Review feedback instead).

### Questions / blockers
**Resolved, 2026-10-23.** The reviewer answered "defaults OK", so every proposed default below is implemented as written (see D-020). The original questions are kept for reference.

1. **Entry point and gameplay.** Gameplay does not exist yet, and the `game` screen is still a placeholder (P01-R08). Is Level Zero:
   (a) a debug page like `player_shots/` (`level_zero/`) that scrolls the level by itself, or
   (b) a playable level that the player starts from level select, which needs ship movement, a game loop and pause, none of which any phase specifies yet?
   *Proposed: (a). The page is `level_zero/` and it is not in level select. A player ship sits at a fixed point on the playfield to show scale. It does not move or shoot.*
2. **"Tools to generate the real levels."** Does this mean (a) code: a data-driven level description (terrain sculpt operations, sea, clouds, prop rules, seed) that the engine turns into a 3D level, or (b) an in-browser editor that can save levels?
   *Proposed: (a). The `level_zero/` page also gets a small live panel: sea on/off, cloud intensity and opacity per layer, scroll speed, jump to time, new seed. You can try values there, but nothing is saved.*
3. **Heightmap sculpting.** *Proposed:* a seeded noise base (fBm) plus a list of operations placed along the level: `plains`, `hills`, `mountains` (ridged noise), `canyon` (a winding path carved into raised ground), `plateau` (flattened ground for props) and `coast` (ground that drops below sea level). These blend smoothly into each other. Level Zero shows every kind across its 3 minutes. Peaks stay below the flight altitude so they never cross the playfield. The terrain is wider than the playfield so the tilted camera never shows its edges. Is that what you meant by "software sculpted"?
4. **Camera, P04-R05.** "Angled 35% to the back": I read this as **35°** from vertical. Is the camera placed behind the playfield and tilted to look forward (in the scroll direction, so the far terrain is at the top of the screen)? Or is it tilted the other way? Should it be a perspective camera (the `player_shots/` page uses an orthographic one)?
   *Proposed: perspective camera with a 40° vertical FOV, placed behind the playfield and tilted 35° from vertical to look forward. The 480×640 logical playfield (GD-02) is a flat plane at the flight altitude, framed to fill the screen. The terrain scrolls beneath it.*
5. **Duration and end, P04-R06.** GD-01 says ground speed varies per level, but the spec gives no value. What happens after about 3 minutes?
   *Proposed: a `level_zero_scroll_speed` tunable, with the level length computed from it to last 180 s. At the end the page stops and shows "Level end", and you can restart it. The panel shows elapsed time and has a ×4 fast-forward.*
6. **Terrain look, P04-R01.** Should the ground look natural or cyberpunk? The props list (dead trees, industrial buildings) suggests a polluted wasteland.
   *Proposed: wasteland palette. Dusty ochre sand and dry earth on flat, low ground. Grey-brown rock on steep slopes. Dirty snow above an altitude. Wet dark sand near the shore. The textures are generated in code at load time and blended per pixel by altitude and slope in a custom shader, with a little noise so the borders don't look straight.*
7. **Sea, P04-R02.** Does "reflecting the sun" mean a sun glint plus a sky reflection (animated generated normal map, Fresnel sky colour, bright specular sun path, foam near the shore)? Or must the water show a true mirror reflection of the terrain and props? A mirror reflection renders the scene a second time, which risks the 60 FPS target on integrated GPUs (ENG-101).
   *Proposed: sun glint and sky reflection, without a mirror reflection.*
8. **Lighting / time of day.** The menus are a night city. A sun on the sea suggests daytime.
   *Proposed: late afternoon with a low, warm sun and light haze. One directional light that casts shadows from props and terrain, using the quality presets (ENG-102).*
9. **Clouds, P04-R03.** Where are the layers: between the ground and the ship, above the ship, or both?
   *Proposed: up to 2 layers, both below the flight altitude, scrolling with parallax at their own speeds. They cast soft shadows on the ground if that fits the budget. "Intensity" means coverage (how much of the sky is cloud), and "opacity" means how transparent the clouds are. No layer above the ship, so clouds never hide bullets or enemies.*
10. **Props, P04-R04.**
    *Proposed:*
    - **Where props go:** flat ground means slope below a threshold and above sea level. Each level sets its own seeded density. Props stay out of canyons.
    - **Set:** 4 industrial (factory hall with chimneys, storage tanks/silos, warehouse, cooling tower), 3 technical/scientific (radar dish, antenna mast, observatory dome), 3 futuristic homes, 2 dead trees.
    - **Look:** low-poly and flat-shaded, as in D-007. Dark metal with small neon accents, in the style of GD-60/61.
    - **Rendering:** thin instances (ENG-104).
    - **Gameplay:** props are scenery only. They cannot be destroyed and they cannot collide with anything.

    Is that set right?
11. **Level description location.** Generic terrain, sea, cloud and prop builders go in the engine (`render/`, `core/`). Level Zero's data and the prop models go in `src/game/` (ENG-140/141). Just confirming that you also want Level Zero in `GameDefinition` as a level, even though level select does not list it.

### Plan
| Task | Requirement IDs |
|------|-----------------|
| Seeded noise (`core/math/noise.ts`): gradient noise (optionally tiling), fBm, ridged | P04-R01 |
| Level data and layout (`core/scenery/scenery-level.ts`): sections in seconds, relief, flatten / channel / shore operations, sea, prop rules | P04-R01, R02, R04, R06 |
| Height field (`core/scenery/height-field.ts`): sculpted, blended sections, soft peak cap | P04-R01 |
| Prop placement (`core/scenery/prop-placement.ts`): flat ground, zones, trees, chunk-independent | P04-R04 |
| Scroll track (`core/scenery/scroll-track.ts`): time ↔ distance, end, pause / ×4 / seek | P04-R06 |
| Camera framing (`render/scenery/playfield-framing.ts`) | P04-R05 |
| Terrain chunks, prop field (thin instances), sea and cloud planes, sun (`render/scenery/`) | P04-R01..R04 |
| Generated textures, terrain blend plugin, PBR sea, cloud shader, shadows (`*.visual.ts`) | P04-R01..R03 |
| Prop geometry helper (`render/geometry/solids.ts`) and the 12 prop models (`game/view/props/`) | P04-R04 |
| Level Zero data and look (`game/config/level-zero.ts`, `scenery-look.ts`), registration in `GAME` | P04-R01..R06 |
| `level_zero/` page: route, panel, keys, stats tile, ship for scale, playfield outline | P04-R01..R06 |
| Unit tests (engine with the sample game, game content), e2e `level-zero.spec.ts`, docs | all |
| Review: road network (main roads + paths), building slots along roads, road ribbons per chunk | P04-R07 |

### Requirement traceability
| ID | Status (Done / Partial / Not done) | Code | Tests | Notes |
|----|-----------------------------------|------|-------|-------|
| P04-R01 | Done | `core/math/noise.ts`, `core/scenery/height-field.ts`, `render/scenery/terrain-chunks.ts`, `terrain-geometry.ts`, `procedural-textures.ts`, `terrain-blend-plugin.visual.ts`, `game/config/level-zero.ts` | `noise.test.ts`, `height-field.test.ts`, `terrain-geometry.test.ts`, `terrain-chunks.test.ts`, `procedural-textures.test.ts`, `scenery-levels.test.ts`, e2e `level-zero.spec.ts` | Plains, hills, plateau, mountains, canyon (with a river), coast and open sea with islands. Ground, shore, rock and snow textures blended by altitude and slope. Manual visual validation. |
| P04-R02 | Done | `render/scenery/scenery-stage.ts` (sea plane), `scenery-kit.visual.ts` (PBR + generated normal map), surf in the terrain plugin | `scenery-stage.test.ts`, `procedural-textures.test.ts`, `scenery-viewer-panel.test.ts`, e2e | Optional per level (`SceneryLevel.sea`); toggled with S. Sky reflection and sun glint, no mirror reflection (Q7). Manual visual validation. |
| P04-R03 | Done | `render/scenery/scenery-stage.ts` (layers), `cloud-material.visual.ts`, `game/config/scenery-look.ts` | `scenery-stage.test.ts`, `scenery-viewer-panel.test.ts`, `start-scenery-viewer.test.ts`, e2e | 2 layers between the highest peaks and the flight plane (review: never through the terrain). Each layer has an on/off switch and intensity (coverage) and opacity sliders. Manual visual validation. |
| P04-R04 | Done (review: smaller props; 21 models with living trees, industrial and city buildings) | `core/scenery/prop-placement.ts`, `render/scenery/prop-field.ts`, `render/geometry/solids.ts`, `game/view/props/*` | `prop-placement.test.ts`, `prop-field.test.ts`, `solids.test.ts`, `prop-models.test.ts`, `scenery-levels.test.ts` | 4 industrial (factory, storage tanks, warehouse, cooling tower), 3 technical / scientific (radar dish, antenna mast, observatory), 3 homes (cube home, dome home, stilt pod), 2 dead trees. Manual visual validation. |
| P04-R05 | Done | `render/scenery/playfield-framing.ts`, `scenery-stage.ts`, `game/config/scenery-look.ts` (`PLAYFIELD_CAMERA`) | `playfield-framing.test.ts`, `scenery-stage.test.ts`, `start-scenery-viewer.test.ts` | "35%" read as 35° from vertical (Q4). Perspective camera, 40° FOV, looking forward. O shows the playfield outline. Manual visual validation. |
| P04-R07 | Done (added in review) | `core/scenery/road-network.ts`, `prop-placement.ts` (buildings from road slots), `render/scenery/road-geometry.ts`, `road-field.ts`, `game/config/level-zero.ts` (`ROAD_RULES`), `scenery-look.ts` (`roads`) | `road-network.test.ts`, `prop-placement.test.ts`, `road-geometry.test.ts`, `scenery-stage.test.ts`, `scenery-levels.test.ts` | Main roads are worn asphalt, 6 wide; paths are packed dust, 4 wide. Both have soft, see-through edges that blend into the ground (review). Manual visual validation. |
| P04-R06 | Done (still 180 s with the 3 new sections) | `core/scenery/scroll-track.ts`, `scenery-level.ts` (`levelDuration`), `app/start-scenery-viewer.ts` | `scroll-track.test.ts`, `scenery-level.test.ts`, `scenery-levels.test.ts` (exactly 180 s), `start-scenery-viewer.test.ts`, e2e | 60 px/s, 10,800 px long. At the end the level stops and shows "Level end" (Q5). |

### Gate results
Light verification only (CLAUDE.md, step 5). Lint, unit tests and coverage run in the full `make check` gate of `/validate-phase`.
```
make typecheck  ✔ (0 errors)
make build      ✔ (ENG-52 check passed; main chunk 1,338 kB / 342 kB gzip)
make e2e        ✔ 32 passed (27 from earlier phases + 5 new in level-zero.spec.ts)
Review fix (smaller props): typecheck ✔, build ✔, e2e 32 passed. In the first full run,
menu-gamepad.spec.ts (phase 1) went over its 30 s timeout under load; it passed alone in 14 s,
and the next full run passed 32/32.
Review fix (irregular city): typecheck ✔, build ✔, e2e 33 passed.
Review fix (city with factory streets and buildings made of lots): typecheck ✔, build ✔, e2e 33 passed.
Review fix (glow under the clouds): typecheck ✔, build ✔, e2e 33 passed.
Review fix (city blocks packed with buildings): typecheck ✔, build ✔. In the first e2e run, 1 of 33 tests failed under load (output lost); the next two full runs passed 33/33. After splitting the district test: e2e 34 passed.
Review fix (square street corners, centre lines, cars): typecheck ✔, build ✔, e2e 34 passed.
Review fix (city blocks filled by podiums): typecheck ✔, build ✔, e2e 33 passed.
Review fix (bigger, packed district buildings): typecheck ✔, build ✔, e2e 33 passed. The section e2e test went over its 30 s timeout under SwiftShader with the heavier districts, so it was split in two (wasteland sections; meadows, industrial zone and city centre). No timeout was changed.
Review fix (straight streets, building parts, no blinking): typecheck ✔, build ✔, e2e 32 passed.
Review fix (meadows, industrial zone, city centre): typecheck ✔, build ✔, e2e 32 passed (the section e2e test now also visits the 3 new sections).
Review fix (roads off screen, junctions): typecheck ✔, build ✔, e2e 32 passed.
Review fix (roads blend with the ground): typecheck ✔, build ✔, e2e 32 passed twice in a row.
The first runs failed one phase 1 menu test each (gamepad, then AZERTY). Each failure was the
30 s timeout, with the page simply too slow, and each test passed alone. Cause: the 5 heavy
level_zero/ tests ran in parallel and starved the other specs of CPU. level-zero.spec.ts now
runs its tests one after another in one worker (`mode: 'default'`); no timeout was changed.
Review fix (clouds above the terrain): typecheck ✔, build ✔, e2e 32 passed.
Review fix (roads, P04-R07): typecheck ✔, build ✔, e2e 32 passed. In an earlier run of this fix,
menu-gamepad.spec.ts (phase 1, not touched here) went over its 30 s timeout under the full
parallel load (32.4 s); it passed alone and in the final full run.
```
Lint, unit tests and coverage were not run as a gate. While debugging, I ran the new core tests and `start-scenery-viewer.test.ts` once (109 passing at that point). ESLint was also run on `src/` (clean), and the pre-commit hook lints staged files. The render, UI and game tests written after that have only been type-checked.

### How to test manually
1. `make dev`, then open http://localhost:5173/level_zero/ (or `level_zero/` on GitHub Pages).
2. The level starts at once. The balanced ship sits at the bottom of the playfield to show the scale; it does not move or shoot (Q1).
3. Keys and controls:
   - **Playback:** **P** pause, **F** ×4 fast-forward, **R** restart, **← / →** jump 10 s; the time slider seeks.
   - **Ground:** **N** new seed (rebuilds terrain and props).
   - **Layers:** **S** sea on/off, **1** / **2** cloud layer on/off, each with Intensity and Opacity sliders.
   - **O** shows the 480×640 playfield outline on the flight plane.
4. Sections and their times (also shown as "Section:" in the panel):

   | Time | Section | What to look for |
   |------|---------|------------------|
   | 0:00 | plains | Buildings and dead trees |
   | 0:14 | hills | Rolling ground |
   | 0:26 | plateau | A flat town: industrial, labs, homes |
   | 0:40 | mountains | Rock on slopes, snow on peaks; roads turn off the screen |
   | 0:58 | canyon | Mesa with a river in the canyon |
   | 1:16 | coast | Shore with surf |
   | 1:30 | open sea | Islands |
   | 1:44 | landing | Coast again, first grass and bushes |
   | 1:54 | meadows | Green grass, conifers, broadleaf trees and bushes (review) |
   | 2:16 | industrial zone | Maze of straight streets packed with varied industrial buildings on concrete (review) |
   | 2:38 | city centre | Regular grid of straight streets, varied towers, offices and apartment blocks (review) |
   | 3:00 | — | The level stops with "Level end" (P04-R06) |
5. P04-R07: roads (dark) and paths (light dust) wind across the map, and every building stands along one, facing it. No road starts or ends on screen. Paths flare where they meet a road. N gives another road network.
6. To check: the textures change with altitude and slope (P04-R01); the sea catches the sun (R02); the clouds react to their sliders (R03); props stand only on flat ground (R04); the camera looks down at 35° towards the top of the screen (R05); the level lasts 3:00 (R06).
7. The FPS / polygons tile is at the top right. 60 FPS on an integrated GPU (ENG-101) still has to be checked on real hardware: headless SwiftShader only gives 10–40 FPS. The scene draws about 100–190k triangles in most sections, about 550k in the industrial zone and about 390k in the city centre (dense buildings made of parts, all thin-instanced). This is the main thing to check against 60 FPS on real hardware.

### Deviations from spec
- None from the requirements. The interpretations agreed in the questions (Q1–Q11) are listed in D-020.
- ENG-102 quality presets do not exist in the project yet. The shadow map size (2048), the terrain grid (8 units) and the texture sizes are fixed values in config.

### Known limitations
- **Trapezoid playfield.** With a perspective camera tilted 35°, the playfield is a trapezoid on screen. The screen shows about 293 of the 480 logical pixels across the bottom edge and about 493 across the top. Mapping gameplay to the screen is left to the gameplay phase (see Suggestions).
- **CPU work on scroll.** Terrain chunks and their props are generated on the main thread (about every 5 s at ×1, more often at ×4). A short hitch is possible on slow machines.
- **Clouds.** They cast no shadows on the ground, and their shader does not go through the ACES tone mapping used by the rest of the scene.
- **Sea.** There is no mirror reflection of terrain or props (decided in Q7). The wave pattern repeats every 320 units.
- **Props.** They are scenery only: they cannot be destroyed and nothing collides with them.
- **Panel.** On narrow windows the panel covers part of the canvas.
- **Roads.** Roads are drawn on the terrain without flattening it, and they follow the ground's ups and downs. Where two main roads cross, their ribbons simply overlap. In the sections a road has to avoid (mountains, coast, open sea), there are no roads, and so no buildings.
- **Dense districts.** The city centre draws about 370k triangles (half of them window bands), the heaviest part of the level: to be checked on real hardware (ENG-101). The city's glowing windows and trims still bloom a little; the glow strength is `glow.intensity` in `scenery-look.ts`. The streets of the districts follow the ground but do not flatten it.
- **Gamepad e2e test.** The phase 1 `menu-gamepad.spec.ts` takes close to its 30 s timeout under full parallel load. The heavy `level_zero/` tests now run one at a time, which removed the timeouts seen during the review fixes.

### Suggestions for future phases
- **Gameplay mapping.** Either keep this camera and limit ship movement to the visible trapezoid, or project the 2D logical playfield onto the tilted plane so that the full 480 px width is visible at the bottom. The second option needs a wider FOV or a higher camera.
- **Performance.** Move chunk generation to a Web Worker, or spread it over several frames.
- **Quality presets (ENG-102).** Shadow map size, terrain cell size, glow on/off and cloud layer count are natural knobs.
- **Cloud shadows.** The terrain plugin can sample the cloud texture to darken the ground under the clouds.
- **Ground targets.** Props are already placed by rules, so ground enemies (turrets on buildings) can reuse the placer.
