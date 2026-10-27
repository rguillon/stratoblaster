# Progress

> Agent updates this after each phase. Human validates by saying **"Phase N validated"**.
> Statuses: ⚪ Not started · 🔵 In progress · 🟡 Awaiting review · 🔴 Changes requested · ✅ Validated

| Phase | File | Status | Branch | Coverage | Validated on |
| ------- | ------ | -------- | -------- | ---------- | -------------- |
| 1 | `phases/phase-01-main-menu.md` | ✅ Validated | `phase-01` | 99.61% lines | 2026-10-23 |
| 2 | `phases/phase-02-player-ships.md` | ✅ Validated | `phase-02` | 99.51% lines | 2026-10-22 |
| 3 | `phases/phase-03-player-shots.md` | ✅ Validated | `phase-03` | 99.45% lines | 2026-10-23 |
| 4 | `phases/phase-04-level-zero.md` | ✅ Validated | `phase-04` | 99.35% lines | 2026-10-23 |
| 5 | `phases/phase-05-first-enemies.md` | ✅ Validated | `phase-05` | 99.27% lines | 2026-10-24 |
| 6 | `phases/phase-06-world-1.md` | ✅ Validated | `phase-06` | 99.33% lines | 2026-10-25 |
| 7 | `phases/phase-07-bosses.md` | ✅ Validated | `phase-07` | 99.34% lines | 2026-10-25 |
| 8 | `phases/phase-08-world-2.md` | ✅ Validated | `phase-08` | 99.26% lines | 2026-10-25 |
| 9 | `phases/phase-09-world-3.md` | ✅ Validated | `phase-09` | 99.35% lines | 2026-10-26 |
| 10 | `phases/phase-10-world-4.md` | ✅ Validated | `phase-10` | 99.42% lines | 2026-10-26 |
| 11 | `phases/phase-11-score-lives-bombs.md` | ✅ Validated | `phase-11` | 99.42% lines | 2026-10-26 |
| 12 | `phases/phase-12-pause-music-settings.md` | ✅ Validated | `phase-12` | 99.4% lines | 2026-10-27 |
| 13 | `phases/phase-13-perf.md` | ✅ Validated | `phase-13` | 2026-10-27 | 99.28 % lines |

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
- 2026-10-24 — 5 — Review fix: new enemy P05-R12 Carrier (slow, fat, launches Gnats from its side vents), added to the spec at the reviewer's request; light verification green (typecheck, build, 40 e2e); still awaiting review.
- 2026-10-24 — 5 — Review fix: Carrier reworked (no landing deck; two glowing launch ports on each side, each launching a Gnat); light verification green (typecheck, build, 40 e2e, the known model view flake passing on rerun); still awaiting review.
- 2026-10-24 — 5 — Review fix: wireframe view on `enemies/` (V), the model view drawn as lines; light verification green (typecheck, build, 40 e2e); still awaiting review.
- 2026-10-24 — 5 — Review fix: dark grey background for the model and wireframe views; light verification green (typecheck, build, 40 e2e); still awaiting review.
- 2026-10-24 — 5 — Review fix: readable wireframe (light hull lines) and the hit circle shown in the wireframe view; light verification green (typecheck, build, 40 e2e); still awaiting review.
- 2026-10-24 — 5 — Review fix: details only visible from below removed (Gnat turret, lens and arms; Scout, Weaver and Bulwark under-hull guns); light verification green (typecheck, build, 40 e2e, the known model view flake passing on rerun); still awaiting review.
- 2026-10-24 — 5 — Fix: the model view's shaders compiled in the background before it is first shown (the flaky model view e2e test); light verification green (typecheck, build, 40 e2e); still awaiting review.
- 2026-10-24 — 5 — Review fix: enemy hulls tinted towards and outlined in their neon colour, to stand out on the ground; light verification green (typecheck, build, 40 e2e); still awaiting review.
- 2026-10-24 — 5 — Review fix: the neon outline around the enemy hulls removed (the tinted metal stays); light verification green (typecheck, build, 40 e2e); still awaiting review.
- 2026-10-24 — 5 — Review fix: bigger, more realistic explosions (flash, shock ring, fireball cluster, lingering smoke, burning debris trailing embers and smoke); light verification green (typecheck, build, 40 e2e); still awaiting review.
- 2026-10-24 — 5 — Review fix: smaller explosions for the tiny ships (big ones unchanged); light verification green (typecheck, build, 40 e2e); still awaiting review.
- 2026-10-24 — 5 — Review fix: the sea/land junction reworked (sand beach, shallows tinted by depth, broken foam and rolling surf, see-through sea); light verification green (typecheck, build, 40 e2e); still awaiting review.
- 2026-10-24 — 5 — Review fix: player missiles only home on enemies within 320 px (half the screen); light verification green (typecheck, build, 40 e2e); still awaiting review.
- 2026-10-24 — 5 — Review fix: the player's bullets are now minigun tracers instead of green blobs; light verification green (typecheck, build, 40 e2e); still awaiting review.
- 2026-10-24 — 5 — At the reviewer's request, the specs corrected to match the review fixes (P03-R01, P03-R03, P04-R02, P05-R01, P05-R11); still awaiting review.
- 2026-10-24 — 5 — Review fix: player missiles more visible (bigger, lighter, with a motor flare and an exhaust trail); light verification green (typecheck, build, 40 e2e); still awaiting review.
- 2026-10-24 — 5 — Validated: full gate green after fixes (668 unit tests, 99.27% lines, 88.83% branches, 40 e2e); squash-merged into `main`, tagged `v0.05.0`.
- 2026-10-24 — 6 — Spec settled with the reviewer (World 1 has 5 levels of ~4 min, no bosses yet) and set to Ready.
- 2026-10-24 — 6 — Implemented World 1 (five playable levels, wave scripts, level end, desert ground and props, debug URL options); awaiting review.
- 2026-10-25 — 6 — Validated: full gate green (789 unit tests, 99.33% lines, 89.5% branches, 50 e2e); already squash-merged into `main` (#16), tagged `v0.06.0`.
- 2026-10-25 — 7 — Spec file created; requirements drafted by the agent at the reviewer's request (Draft).
- 2026-10-25 — 7 — Open choices settled by the reviewer (all defaults) and set to Ready.
- 2026-10-25 — 7 — Implemented bosses: engine `Boss` (parts, shielded core, stages, death), fights with ground speed and checkpoint, ten World 1 bosses with code-generated models, boss health bar, Continue panel and the `bosses/` debug page (D-053..D-056); awaiting review.
- 2026-10-25 — 7 — Review fix: `boss/` debug endpoint (same page as `bosses/`); still awaiting review.
- 2026-10-25 — 7 — Review fix: bosses roll into their sideways moves (up to 12°); still awaiting review.
- 2026-10-25 — 7 — Review fix: more detailed, asymmetric boss models, seven of them with fat armour over a visible mechanism (2,180–4,164 triangles each); still awaiting review.
- 2026-10-25 — 7 — Review fix: enemy and boss shots leave from the tips of their barrels, as the tilted camera sees them (D-057); small guns drawn on the Scout, Strafer, Weaver and Bulwark; still awaiting review.
- 2026-10-25 — 7 — Review fix: boss turrets turn to follow the player while they fire at the player (D-058); still awaiting review.
- 2026-10-25 — 7 — Review fix: player weapons balanced, the laser and missiles at 70-100 % of the guns' damage per second (GD-33, D-059); still awaiting review.
- 2026-10-25 — 7 — Review fix: every boss turret turns the way its next volley goes (at the player, along a fan, spinning with a spiral); three more turrets (Reef Warden prow cannon, Mesa Fortress fan cannon, Refinery Titan rotary turrets) (D-060); still awaiting review.
- 2026-10-25 — 7 — Review fix: bosses can have moving limbs (joints swinging, parts moving with them); the Scorpion's arms swing at the shoulder and elbow, its claws turn at the wrist and open and close their jaws (D-061); still awaiting review.
- 2026-10-25 — 7 — Review fix: shots go through a shielded boss core to the parts behind it; Mesa Fortress health re-tuned for P07-R10 (D-062); still awaiting review.
- 2026-10-25 — 7 — Review fix: bosses get angry for 3 s after each destroyed part and its pause, firing a bullet hell denser from 1-1 to 1-5 (D-063); still awaiting review.
- 2026-10-25 — 7 — Validated: full gate green after fixes (939 unit tests, 99.34% lines, 88.69% branches, 54 e2e); squash-merged into `main`, tagged `v0.07.0`.
- 2026-10-25 — 8 — Spec file created; requirements drafted by the agent at the reviewer's request (World 2, the Frozen North; level looks, time of day, clouds and snow) (Draft).
- 2026-10-25 — 9 — Spec file created; requirements drafted by the agent at the reviewer's request (World 3, the Jungle; rain and lightning) (Draft).
- 2026-10-25 — 10 — Spec file created; requirements drafted by the agent at the reviewer's request (World 4, the Volcanic Lands; lava, falling ash and embers) (Draft).
- 2026-10-25 — 8 — Implemented World 2 (five levels, time of day / clouds / weather engine, snow, aurora, frozen ground and props, ten bosses); light verification run; awaiting review.
- 2026-10-25 — 8 — Review changes: persistent weapon levels, enemy bullets as balls of plasma, laser colours per boss, lasers on turrets locked once firing, laser flares; e2e tests drive the level clock (D-075).
- 2026-10-25 — 8 — Validated: full gate green (1084 unit tests, 99.26% lines, 88.04% branches, 65 e2e); squash-merged into `main`, tagged `v0.08.0`.
- 2026-10-26 — 9 — Implemented World 3 (the Jungle): five levels, rain and lightning, jungle props, ten bosses; awaiting review.
- 2026-10-26 — 9 — Validated: full gate green (1210 unit tests, 99.35% lines, 87.25% branches, 77 e2e); squash-merged into `main`, tagged `v0.09.0`.
- 2026-10-26 — 10 — Implemented World 4 (Volcanic Lands): lava, falling ash and embers, smoke and steam plumes, contrast shots, 31 props, ten bosses; awaiting review.
- 2026-10-26 — 10 — Review fix: World 5 removed from the specs and the code, the level grid is 4 × 5 (D-089); still awaiting review.
- 2026-10-26 — 10 — Review fix: ten new enemy kinds (five veteran, five elite, some with moving parts; P05-R13 to P05-R24), in the World 3 and World 4 waves (D-090); still awaiting review.
- 2026-10-26 — 10 — Validated: full gate green (1384 unit tests, 99.42% lines, 87% branches, 88 e2e); squash-merged into `main`, tagged `v0.10.0`.
- 2026-10-26 — 11 — Spec drafted by the agent at the reviewer's request and approved (D-091). Implemented score, high score, checkpoint score, bombs (R / Left Shift / X / LB / touch), life and bomb bonuses (D-092); light verification green (typecheck, build, 95 e2e); awaiting review.
- 2026-10-26 — 11 — Validated: full gate green (1432 unit tests, 99.42% lines, 87.18% branches, 95 e2e); squash-merged into `main`, tagged `v0.11.0`.
- 2026-10-26 — — — e2e tests step the game instead of waiting on real time: no render loop in e2e builds, `step(frames)` on every test API (D-093); typecheck, build and e2e green (101 e2e, 3.6 min instead of 7.5); full gate not run.
- 2026-10-26 — — — Faster git hooks: incremental `tsc`, Prettier and ESLint caches, `import-x` rules that TypeScript covers turned off (D-094); `pre-push` about 18.5 s warm instead of 65 s, `pre-commit` about 8 s instead of 11 on 27 files; `make lint`, `make typecheck` and `make check-fast` green.
- 2026-10-26 — 12 — Implemented pause (Esc / P / Start / Select / ❚❚, auto pause on a hidden page or a lost gamepad), the pause menu, the Settings screen with saved volumes, a Web Audio engine, generated level / boss / menu music and jingles, and every sound effect (D-096..D-098); light verification green (typecheck, build, 116 e2e); awaiting review.
- 2026-10-26 — 12 — Review fix: a full synthwave menu theme, as loud as the level tracks, and all the music made synthwave (echo and reverb sends, gated snares, synth toms, supersaws; outrun, dreamwave, darksynth flavours) (D-099); light verification green (typecheck, build, 116 e2e); still awaiting review.
- 2026-10-26 — 12 — Review fix: stressful boss tracks (pushed kicks, snare rolls, rolling octave bass, chord stabs, tense chords) and more energetic synthwave everywhere (faster tempos, sixteenth arpeggios, no breakdowns, risers) (D-100); light verification green (typecheck, build, 116 e2e); still awaiting review.
- 2026-10-26 — 12 — Review fix: darksynth in every world and the menu, a minigun rattle for the gun (D-101); bullet and missile streams fire in turn (P03-R11 added, D-102); light verification green (typecheck, build, 116 e2e); still awaiting review.
- 2026-10-26 — 12 — Review fix: darksynth menus and HUD, cyberpunk references dropped (GD-60, P01-R05, P01-R13 amended at the reviewer's request; D-103), then no sun on the logo (a pilot model in place of the menu ship was tried, then reverted to the ship at the reviewer's request, D-104); the boss health bar moved to a gauge on the left edge so it no longer hides the boss (P07-R02 amended, D-105); light verification green (typecheck, build, 116 e2e); still awaiting review.
- 2026-10-26 — 12 — Review fix: bullets leave from inside the ship, drawn under it (D-106); enemy explosions are short, muffled booms (D-107); light verification green (typecheck, build, 116 e2e); still awaiting review.
- 2026-10-26 — 12 — Review fix: realistic, layered explosion sounds for every blast (D-108); light verification green (typecheck, build, 116 e2e); still awaiting review.
- 2026-10-26 — 6 — Review change after validation, at the reviewer's request: World 1 reworked as one gradient (sea → green grass → desert, more and more props), farm props, a time of day per level (P06-R05, R06 amended, P06-R10 added; D-109); light verification green (typecheck, build, 116 e2e); full gate not run; awaiting the reviewer's check.
- 2026-10-27 — 6 — Review change after validation, at the reviewer's request: 1-5 ends on the desert ("Deep desert"), no factory or city in World 1 (D-109 amended). Light verification green (typecheck, build, 116 e2e); awaiting the reviewer's check.
- 2026-10-27 — 8 — Review change after validation, at the reviewer's request: World 2 reworked as the Industrial Desert, from the desert to the factories with slow transitions (sections blend over 900 units, sand stepping down to concrete, building groups mixing in), a time of day per level (morning, midday, afternoon, dusk, night), an oil pumpjack prop; no snow or aurora (P08-R03, R06, R07 amended; D-110). Untracked the self-referencing `node_modules` symlink committed by #24. Light verification green (typecheck, build, 116 e2e); full gate not run; awaiting the reviewer's check.
- 2026-10-27 — 8 — Review change, at the reviewer's request: no sea in World 2, rivers allowed (spec note in P08-R03, D-110 amended); World 2 already had none, 2-1 renamed "Great erg" so its name no longer suggests one, the test now checks no shore, sea bed or floating ice. Light verification green (typecheck, build, 117 e2e); full gate not run.
- 2026-10-27 — 8 — Test fix: the World 2 footprint test checks the buildings only (the plants are World 1's, whose footprints space their trunks). Full gate green: `make check` (lint, typecheck, 1573 unit tests, coverage 99.41 % lines / 87.89 % branches, build, 117 e2e); awaiting the reviewer's check.
- 2026-10-27 — 9 — Review change after validation, at the reviewer's request: World 3 reworked, from the factories World 2 ends on to garden villages of small houses (no tower), slow transitions (sections blend over 900 units, concrete stepping down to grass, building groups mixing in); no sea, a canal then a river; three new home models (P09-R03, R04 notes, R06 amended; D-111). Full gate green: `make check` (lint, typecheck, 1580 unit tests, coverage 99.41 % lines / 87.97 % branches, build, 117 e2e); awaiting the reviewer's check.
- 2026-10-27 — 10 — Review change after validation, at the reviewer's request: World 4 reworked as the Metropolis, from the houses World 3 ends on to a downtown of skyscrapers, slow transitions (sections blend over 900 units, grass stepping down to concrete, taller building groups mixing in), the river on between quays; no sea, no lava; a new family of 8 skyscrapers (P10-R03, R04 notes, R05 note, R08 amended; D-112). Full gate green: `make check` (lint, typecheck, 1591 unit tests, coverage 99.4 % lines / 87.87 % branches, build, 117 e2e); awaiting the reviewer's check.
- 2026-10-27 — CI — At the reviewer's request: the e2e tests run in a single CI job instead of 3 shards (D-018 amended).
- 2026-10-27 — 12 — Validated by the reviewer, without re-running `make check` for this phase (reviewer's choice): already squash-merged into `main` as #23, tagged `v0.12.0` on 6da41c0; coverage from the latest full gate (World 4 rework: 1591 unit tests, 99.4 % lines, 87.87 % branches, 117 e2e).
- 2026-10-27 — 13 — Set Ready by the reviewer. Implemented: perf monitor + F3 overlay + test API numbers + `scripts/measure-perf.mjs`; causes found (O(roads²) road ribbons per chunk, all prop kinds re-uploaded, level built inside the key press, regenerated ground and textures); street index, caches, noise tables, stepped level loading behind a loading screen with shader precompile and prebuilt enemy models (D-113..D-115). Software WebGL only (no reference machine): long sim frames in Worlds 2–4 19–25 → 0–3 per 2 min, level confirm 2.4 s → 48 ms. Light verification green (typecheck, build, 122 e2e); awaiting review.
- 2026-10-27 — 13 — Review fixes: one key light per ship on ship select (no shader rebuild on highlight, 186 → 6 ms; D-116); the highlighted level is prepared in a worker while it is chosen, enemy models built during play (load 3.7–4 s → 0.44–0.51 s once the highlight has rested; D-117). Still awaiting review.
- 2026-10-27 — 13 — Second review round (focus on 4-1): the level the level select highlight rests on is built ahead, so Confirm starts it in the same frame (D-119); each ship drawn highlighted once while the menus load, for the ship-select freeze, which can't be reproduced on software WebGL (D-118). Light verification green (typecheck, build, 122 e2e). Still awaiting review.
- 2026-10-27 — 13 — Review fix: the music no longer stops during level loading steps; it is scheduled 1.5 s ahead before each step (D-120). Light verification green (typecheck, build, 122 e2e). Still awaiting review.
- 2026-10-27 — 13 — Review fix: the music is scheduled 1.5 s ahead (was 100 ms, P12 tunable), so it no longer stops during loading or the first frames of a level (D-120). Light verification: typecheck, build green; e2e 121 passed + 1 known flaky timeout (World 2 dusk lights, passed alone). Still awaiting review.
- 2026-10-27 — 13 — Validated: full gate green (1617 unit tests, 99.28 % lines, 87.83 % branches, 122 e2e); squash-merged into `main`, tagged `v0.13.0`.
