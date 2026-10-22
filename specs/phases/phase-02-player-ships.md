# Phase 02 — Player Ships

> Copy this file to `phase-NN-short-name.md` (e.g. `phase-03-enemies.md`).
> Fill the **Human** sections. Set **Status** to `Ready` when the agent may implement it.
> The agent fills the **Agent** sections and never edits the requirement sections.

**Status:** Ready  <!-- Draft | Ready -->
**Depends on: None** <!-- e.g. Phase 2 -->

---

## 🧑 Goal

This phase consists of desiging the different ships the player can use.

The ship 3D model shall be generated in code.

A test endpoint player_ship/ shall allow to view the 3 ships on the same screen rotating.

All the player ships shall have a shiny grey/blue look with blue light effects behind each reactor.

A base ship speed is 100px/s.

Speed and Health points shall only be stored as data for now.



## 🧑 Requirements

> ID format `P02-R01`. Priority: **MUST** / **SHOULD** / **MAY**.
> Write each requirement so it is testable. Add acceptance criteria when "done" isn't obvious.

### P02-R01 — Balanced ship  · MUST
A balanced ship with a maximal speed of 1, 100 health points.

The ship design shall be inspired from MACROSS DELTA VF-31J: dual reactor with wings going forward.


**Acceptance criteria**
- [ ] The ship design will be manually validated

### P02-R02 — Heavy ship  · MUST
A heavy ship with a maximal speed of 0.8 and 140 health points.

The ship design shall be inspired from a modern flying wing nuclear bomber.


**Acceptance criteria**
- [ ] The ship design will be manually validated

### P02-R03 — Ligh ship  · MUST
A ligh ship with a maximal speed of 1.4 and 80 health points.

The ship design shall have 4 wings, each haing an attached reactor


**Acceptance criteria**
- [ ] The ship design will be manually validated

---

## 🤖 Implementation report
> Filled by the agent. Do not edit (comment in Review feedback instead).

### Questions / blockers
<!-- Ambiguities found before implementing. If non-empty, agent stops and waits. -->

None open. The earlier questions were answered by the updated spec, or settled with the defaults below (also in `DECISIONS.md` D-004):

1. Precondition: "Depends on: None", so phase 02 is implemented before phase 01.
2. Speed: `maxSpeed` is a multiplier of the base speed of 100 px/s. Balanced 100, heavy 80, light 140 px/s.
3. Stats: data only, with no flight or damage logic.
4. Endpoint: a real page at `<base>/player_ship/` (a second Vite HTML entry), included in the production build so it can be checked on GitHub Pages.
5. Viewer: the 3 ships side by side, all rotating, with name and stats shown under each one. The camera can be orbited and zoomed with the mouse.
6. Reactor light: emissive nozzle and exhaust cone, made to bloom by a glow layer. No particles yet.
7. Heavy ship: a B-2 / B-21 style flying wing (the spec now says "flying wing").
8. Names: working names "Balanced", "Heavy" and "Light" (in `src/game/config/`, easy to rename).

### Plan
| Task | Requirement IDs |
|------|-----------------|
| `core/entities/player-ship.ts`: generic ship definition and roster types, speed in px/s, validation | P02-R01..R03 |
| `GameDefinition` gains `playerShips` (sim data) and a typed `view` slot (view bindings) | P02-R01..R03 |
| `src/game/config/player-ships.ts`: the 3 ships' speed and HP, base speed 100 px/s | P02-R01..R03 |
| Engine geometry helpers in `render/geometry/` (convex/star prism, lathe along Z, faceted flat-shaded lathe) | P02-R01..R03 |
| `src/game/view/`: shared shiny grey/blue materials, a reactor with blue glow, and 3 procedural ship models | P02-R01..R03 |
| Engine viewer: `render/model-showcase.ts` (layout + rotation), procedural environment and glow, `ui/caption-row.ts` | Goal (viewer) |
| `app/route.ts` + `app/start-ship-viewer.ts`, `player_ship/index.html`, Vite multi-page input | Goal (endpoint) |
| Unit tests (NullEngine) + e2e test for `player_ship/` | All |

### Requirement traceability
| ID | Status (Done / Partial / Not done) | Code | Tests | Notes |
|----|-----------------------------------|------|-------|-------|
| P02-R01 | Done (design awaits manual validation) | `src/game/config/player-ships.ts`, `src/game/view/balanced-ship.ts` | `tests/unit/game/player-ships.test.ts`, `tests/unit/game/view/player-ship-models.test.ts`, `tests/e2e/player-ship.spec.ts` | Speed ×1 (100 px/s), 100 HP. VF-31J cues: long pointed nose, framed canopy, dorsal spine, canards, LERX strakes, side intakes feeding 2 reactors, forward-swept wings (tests check the tip is ahead of the root) with accent bands and flap lines, canted twin tails with stripes, ventral fins, belly gun pod, blue nav lights. |
| P02-R02 | Done (design awaits manual validation) | `src/game/config/player-ships.ts`, `src/game/view/heavy-ship.ts` | same files | Speed ×0.8 (80 px/s), 140 HP. B-2 / B-21 style tailless flying wing (sawtooth trailing edge, span > 2× length): leading-edge accent bands, elevons, raised cockpit with a dark visor, dorsal intakes with dark mouths feeding 2 reactors, bomb bay doors underneath, nav lights. |
| P02-R03 | Done (design awaits manual validation) | `src/game/config/player-ships.ts`, `src/game/view/light-ship.ts` | same files | Speed ×1.4 (140 px/s), 80 HP. Reworked after review (it looked too much like an X-wing): a faceted tandem-wing interceptor. A small low front wing pair (anhedral) and a larger high rear pair (dihedral), each of the 4 wings carrying exactly 1 hexagonal reactor at its tip (tested), so the front flames stream under the rear wings. All polygonal (tested: only flames are round): fuselage with a smooth top, a faceted belly and a plain pointed nose, hexagonal canopy and nacelles, diamond-section twin cannons under the nose, accent collar, wing stripes, dorsal blade. |
| Goal: shared look | Done | `src/game/config/ship-look.ts`, `src/game/view/ship-materials.ts`, `ship-parts.ts` | `player-ship-models.test.ts` (GD-61 test) | Shiny grey/blue PBR metal (metallic ≥ 0.7, roughness ≤ 0.35, blue > red); every reactor has a blue emissive core and an animated flame behind it (outer exhaust cone, hotter inner cone, plasma puffs flowing backwards; length, width and brightness flicker), made to bloom by the glow layer. Flame tests: `reactor-flame.test.ts`. |
| Goal: `player_ship/` | Done | `player_ship/index.html`, `vite.config.ts`, `src/app/route.ts`, `src/app/start-ship-viewer.ts`, `src/render/model-showcase.ts`, `src/ui/` | `tests/unit/app/*.test.ts`, `tests/unit/render/model-showcase.test.ts`, `tests/e2e/player-ship.spec.ts` | 3 ships on one screen, all rotating, with name and stats captions; mouse orbit and zoom. |
| Goal: generated in code | Done | `src/render/geometry/` | `tests/unit/render/geometry/*.test.ts` | No model files: prisms (ear clipping) and lathes. |

### Gate results
Final gate, run at validation (2026-10-22, `/validate-phase 2`):
```
make check: lint ✔ (0 warnings) / typecheck ✔ / unit tests 100 passed (20 files)
coverage: lines 99.51% · statements 99.23% · branches 98.05% · functions 98.40% (thresholds met)
  at first review:          lines 99.38% · statements 99.02% · branches 97.01% · functions 97.75%
  previous phase (scaffold): lines 93.33% · statements 93.33% · branches 100% · functions 83.33%
build ✔ / e2e 3 passed
```
The first full run passed, but branch coverage had dropped to 94.59% with the review changes (flames, faceted lathe, triangle count). Fixed before validating: removed 3 unreachable fallbacks and tested the triangle count on a mesh without an index buffer. All figures are now above the first review's.

ENG-44: lines, statements and functions are above the scaffold's. Branches (98.05%, 101/103) are below its 100% (6/6). The 2 uncovered branches need a real WebGL engine: the procedural environment on, and camera controls attached to a canvas. Both run in the e2e test, which fails on any console error.

### How to test manually
1. `make dev`, then open http://localhost:5173/player_ship/ (or `<deployed site>/player_ship/` after deploy).
2. Check the 3 ships left to right: **Balanced**, **Heavy**, **Light**, all rotating slowly, with name, speed (×factor and px/s), HP and the model's polygon (triangle) count under each.
3. Drag with the mouse to orbit the camera, scroll to zoom.
4. Check the look: shiny grey/blue hull, blue glowing light behind every reactor (Balanced 2, Heavy 2, Light 4). Zoom in to see the details: trim, nav lights, intakes, cannons.
5. Check that http://localhost:5173/ (the game page) is unchanged and shows no captions.
6. Open the browser console: no errors.

### Deviations from spec
- None on MUST requirements. Open details were settled with the defaults listed in "Questions / blockers" and in `DECISIONS.md` D-004 / D-005.

### Known limitations
- Ship designs are low-poly and polygonal (D-007): flat-shaded prisms and faceted lathes (fuselages with a smooth top over a 3-facet belly, hexagonal canopies, intakes and reactors), each ship under 2,000 triangles (tested), with a detail pass (trim, nav lights, intakes, weapons). They are "inspired by" the references, not replicas; they need the manual review.
- Each ship is about 30–45 meshes. That is fine for the viewer, but in gameplay each ship should be merged into one mesh per material to stay within the draw-call budget (ENG-106).
- Reactor light is emissive geometry plus glow, animated in code (`game/view/reactor-flame.ts`, stepped by the showcase through `render/model-animation.ts`, D-006). There are no particles yet (pooling rules ENG-105 apply when exhaust particles come).
- The procedural environment's roughness blur is approximate (not prefiltered).
- Ship size in gameplay pixels is not defined yet; models use world units (about 4–6 units long).
- `player_ship/` ships in the production build (D-004).

### Suggestions for future phases
- A ship-select screen can reuse `ModelShowcase` and `shipCaption` as they are.
- Add exhaust particles and a thrust-dependent glow intensity once ships move.
- Define the gameplay scale (world units ↔ logical px of the 480×640 playfield) and hitbox sizes (GD-21) per ship.
