# Progress

> Agent updates this after each phase. Human validates by saying **"Phase N validated"**.
> Statuses: ⚪ Not started · 🔵 In progress · 🟡 Awaiting review · 🔴 Changes requested · ✅ Validated

| Phase | File | Status | Branch | Coverage | Validated on |
| ------- | ------ | -------- | -------- | ---------- | -------------- |
| 1 | `phases/phase-01-main-menu.md` | ✅ Validated | `phase-01` | 99.61% lines | 2026-10-23 |
| 2 | `phases/phase-02-player-ships.md` | ✅ Validated | `phase-02` | 99.51% lines | 2026-10-22 |
| 3 | `phases/phase-03-player-shots.md` | ✅ Validated | `phase-03` | 99.45% lines | 2026-10-23 |
| 4 | `phases/phase-04-level-zero.md` | ✅ Validated | `phase-04` | 99.35% lines | 2026-10-23 |
| 5 | `phases/phase-05-first-enemies.md` | 🟡 Awaiting review | `phase-05` | | |

## Log
<!-- Agent appends one line per event: date — phase — event -->
- 2026-10-22 — 0 — Project scaffold created (tooling, Makefile, hooks, CI, deploy).
- 2026-10-22 — 2 — Implemented player ships + `player_ship/` viewer; awaiting review (phase 1 skipped: phase 2 has no dependency).
- 2026-10-22 — 2 — Detail pass on the 3 ship models (trim, nav lights, intakes, weapons); still awaiting review.
- 2026-10-22 — 2 — Review changes: animated reactor flames, light ship reworked as a tandem-wing interceptor, low-poly polygonal ships (D-006, D-007), polygon counts in the viewer.
- 2026-10-22 — 2 — Validated: full gate green (100 unit tests, 99.51% lines, 98.05% branches, 3 e2e); squash-merged into `main`, tagged `v0.02.0`.
- 2026-10-23 — 1 — Implemented the main menu flow (loading, title, ship select, level select, placeholder game screen) with keyboard, gamepad and touch input; light verification green (typecheck, build, 23 e2e); awaiting review.
- 2026-10-23 — 1 — Review fix: dark menu background (D-012); light verification green (typecheck, build, 23 e2e); still awaiting review.
- 2026-10-23 — 1 — Review fix: cyberpunk HUD style for the menus (D-013); light verification green (typecheck, build, 23 e2e); still awaiting review.
- 2026-10-23 — 1 — Review fix: pastel requirement removed from the specs; cyberpunk night city backdrop and yellow / cyan / red HUD (D-014); light verification green (typecheck, build, 23 e2e); still awaiting review.
- 2026-10-23 — 1 — Validated: full gate green (228 unit tests, 99.61% lines, 96.53% branches, 23 e2e); squash-merged into `main`, tagged `v0.01.0`.
- 2026-10-23 — 3 — Implemented player shots (bullet, laser, missile, 5 levels each) and the `player_shots/` debug page; unspecified values use agent defaults (D-015); light verification green (typecheck, build, 27 e2e); awaiting review.
- 2026-10-23 — 3 — Review fix: glow at the base of the laser; light verification green (typecheck, build, 27 e2e); still awaiting review.
- 2026-10-23 — 3 — Review fix: missile diagonal streams widened to ±25° / ±45°; light verification green (typecheck, build, 27 e2e); still awaiting review.
- 2026-10-23 — 3 — Review fix: missiles launch from the ship centre and are drawn under the ship; light verification green (typecheck, build, 27 e2e); still awaiting review.
- 2026-10-23 — 3 — Review fix: bullet hits throw sparkling metal sparks instead of a green glow; light verification green (typecheck, build, 27 e2e); still awaiting review.
- 2026-10-23 — 3 — Review fix: smaller bullets (visual radius 7 → 4.5 px); light verification green (typecheck, build, 27 e2e); still awaiting review.
- 2026-10-23 — 3 — Review fix: FPS / polygons debug tile on `player_shots/`; light verification green (typecheck, build, 27 e2e); still awaiting review.
- 2026-10-23 — 3 — Review fix: brighter bullet core; light verification green (typecheck, build, 27 e2e); still awaiting review.
- 2026-10-23 — 3 — Review fix: bullets and laser start at each ship's nose tip (measured on the model); light verification green (typecheck, build, 27 e2e); still awaiting review.
- 2026-10-23 — 3 — Review fix: bullets 40 triangles (was 98), hit sparks 12 (was 40); light verification green (typecheck, build, 27 e2e); still awaiting review.
- 2026-10-23 — 3 — Review fix: round, smooth laser base glow (24 sides, 6 rings); light verification green (typecheck, build, 27 e2e); still awaiting review.
- 2026-10-23 — 3 — Validated: full gate green (314 unit tests, 99.45% lines, 90.8% branches, 27 e2e); squash-merged into `main`, tagged `v0.03.0`.
- 2026-10-23 — 4 — Blocked before implementation: 11 questions with proposed defaults in the phase report (entry point, camera angle, tools, duration end, look of terrain/sea/clouds/props).
- 2026-10-23 — 4 — Implemented with the accepted defaults (D-020): generated terrain, sea, clouds and props, the 35° playfield camera and a 3:00 Level Zero on the `level_zero/` page; light verification green (typecheck, build, 32 e2e); awaiting review.
- 2026-10-23 — 4 — Review fix: smaller props (buildings ×0.5–0.65, trees ×0.45–0.75, 50-unit grid) so the ground reads as far below the ship; light verification green (typecheck, build, 32 e2e); still awaiting review.
- 2026-10-23 — 4 — Review fix: P04-R07 added to the spec at the reviewer's request; randomly generated roads and paths, buildings only along them (D-021); light verification green (typecheck, build, 32 e2e; the phase 1 gamepad test once went over its 30 s timeout under load); still awaiting review.
- 2026-10-23 — 4 — Review fix: clouds always above the terrain (height field ceiling, layers at 265 / 295; D-022); light verification green (typecheck, build, 32 e2e); still awaiting review.
- 2026-10-23 — 4 — Review fix: roads blend with the ground (soft see-through edges, worn surface); level_zero/ e2e tests run one at a time so they no longer starve the menu tests; light verification green (typecheck, build, 32 e2e twice); still awaiting review.
- 2026-10-23 — 4 — Review fix: roads start and end off screen (main roads turn off before obstacles, paths run to the screen edge); paths widen at junctions and are drawn under the roads; light verification green (typecheck, build, 32 e2e); still awaiting review.
- 2026-10-23 — 4 — Review fix: Level Zero ends with meadows (grass, living trees), an industrial zone (dense street maze) and a city centre (street grid, towers); still 3:00 (D-023); light verification green (typecheck, build, 32 e2e); still awaiting review.
- 2026-10-23 — 4 — Review fix: straight merging streets in the industrial zone and city centre (winding roads and paths kept out), 16 buildings assembled from parts, matte props and texel-snapped shadows against blinking (D-024); light verification green (typecheck, build, 32 e2e); still awaiting review.
- 2026-10-23 — 4 — Review fix: bigger buildings made of parts (works, plants, towers, blocks) packed edge to edge in the industrial zone and city centre (D-025); light verification green (typecheck, build, 33 e2e); still awaiting review.
- 2026-10-23 — 4 — Review fix: city blocks covered by stretched podiums with towers on top, no bare ground left (D-026); light verification green (typecheck, build, 33 e2e); still awaiting review.
- 2026-10-23 — 4 — Review fix: irregular city grid, varied podium heights, more and shifted towers; light verification green (typecheck, build, 33 e2e); still awaiting review.
- 2026-10-23 — 4 — Review fix: city on the industrial zone's street maze, buildings made of varied lots (D-027); light verification green (typecheck, build, 33 e2e); still awaiting review.
- 2026-10-23 — 4 — Review fix: building lights no longer glow through the clouds; light verification green (typecheck, build, 33 e2e); still awaiting review.
- 2026-10-23 — 4 — Review fix: city blocks packed with buildings on the ground, no bare ground; light verification green (typecheck, build, 34 e2e); still awaiting review.
- 2026-10-23 — 4 — Review fix: square street corners, yellow centre lines, cars on streets and main roads (D-028); light verification green (typecheck, build, 34 e2e); still awaiting review.
- 2026-10-23 — 4 — Review fix: 2×2 highway and avenues with lane markings and cars in both lanes (D-029); light verification green (typecheck, build, 34 e2e); still awaiting review.
- 2026-10-23 — 4 — Review fix: moving cars with headlight beams and tail lights (D-030); light verification green (typecheck, build, 34 e2e); still awaiting review.
- 2026-10-23 — 4 — Review fix: more varied industrial complexes (5 layouts, 9 kinds of equipment) and 16 variants per building family; light verification green (typecheck, build, 34 e2e); still awaiting review.
- 2026-10-23 — 4 — Review fix: more varied city (14 kinds of lots, more facade, window and roof colours); light verification green (typecheck, build, 34 e2e); still awaiting review.
- 2026-10-23 — 4 — Review fix: about a third fewer polygons in the industrial zone and the city (D-031); light verification green (typecheck, build, 34 e2e); still awaiting review.
- 2026-10-23 — 4 — Review fix: city plazas and parking garages no longer flicker with the ground; light verification green (typecheck, build, 34 e2e); still awaiting review.
- 2026-10-23 — 4 — Review fix: the glow of the car lights no longer shows over the ship; light verification green (typecheck, build, 35 e2e); still awaiting review.
- 2026-10-23 — 4 — Review fix: no more green roofs in the industrial zone; light verification green (typecheck, build, 35 e2e); still awaiting review.
- 2026-10-23 — 4 — Validated: full gate green after fixes (545 unit tests, 99.35% lines, 89.94% branches, 35 e2e); squash-merged into `main`, tagged `v0.04.0`.
- 2026-10-24 — 5 — Requirements drafted by the agent at the reviewer's request; set Ready by the reviewer.
- 2026-10-24 — 5 — Implemented 10 enemy kinds (engine `Enemy` / `EnemyWorld`, code-generated models, shots, explosions) and the `enemies/` debug page over Level Zero (D-032); light verification green (typecheck, build, 40 e2e); awaiting review.
- 2026-10-24 — 5 — Review fix: model view like player_ship/ (close up, dark background, ← / → switch the enemy), P05-R11 updated at the reviewer's request; light verification green (typecheck, build, 40 e2e); still awaiting review.
- 2026-10-24 — 5 — Review fix: reactor flames on the enemies (1 to 4 each, in their neon colour; none on the Spinner); light verification green (typecheck, build, 40 e2e); still awaiting review.
- 2026-10-24 — 5 — Review fix: lighter enemy reactors (about 40 triangles each instead of 150); light verification green (typecheck, build, 40 e2e); still awaiting review.
- 2026-10-24 — 5 — Review fix: every enemy reactor in the same light blue; light verification green (typecheck, build, 40 e2e); still awaiting review.
- 2026-10-24 — 5 — Review fix: less boxy enemy ships (lofted fuselages, bevelled wings and plates, about 19 % more polygons); light verification green (typecheck, build, 40 e2e); still awaiting review.
- 2026-10-24 — 5 — Review fix: more aggressive enemy ships (fangs, horns, claws, saw teeth, slanted neon eyes; about 19 % more polygons); light verification green (typecheck, build, 40 e2e); still awaiting review.
- 2026-10-24 — 5 — Review fix: spikes removed, ship parts integrated (painted canopies on one fuselage, faired pods, one-piece armour, wedge pods); light verification green (typecheck, build, 40 e2e); still awaiting review.
- 2026-10-24 — 5 — Review fix: the Gnat reworked as an unmanned tri-rotor drone (ducted fans, spinning rotors); light verification green (typecheck, build, 40 e2e); still awaiting review.
- 2026-10-24 — 5 — Review fix: smooth Hornet movement (brakes into its stop, eased turn, dives from rest); light verification green (typecheck, build, 40 e2e, the known model view flake passing on rerun); still awaiting review.
