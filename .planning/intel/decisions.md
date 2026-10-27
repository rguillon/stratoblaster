# Decisions intel

Source for every entry: `specs/DECISIONS.md` (type ADR, manifest override, file-level `locked: false`).
Status values below are the per-entry statuses recorded in the source (111 Accepted, 1 Reverted). No entry carries a "locked" marker, so none is treated as LOCKED; nothing here can trigger a LOCKED-vs-LOCKED blocker.
Format note: `status` is `accepted` / `reverted` as written in the source; annotations in parentheses come from the source text itself (supersession notes). Template entry "D-NNN" is skipped.
Where a later entry changes an earlier one, see the INFO section of `/home/renaud/pewet/.planning/INGEST-CONFLICTS.md`.

## D-001: 3D engine Babylon.js + TypeScript + Vite

- source: specs/DECISIONS.md
- status: accepted (2026-10-22, phase 0)
- decision: TypeScript (strict) + Babylon.js built with Vite. Deep ES-module imports for tree-shaking. Alternatives rejected: Three.js, PlayCanvas, Unity/Godot web export, raw WebGL.
- scope: engine, toolchain

## D-002: Toolchain versions ESLint 9 and TypeScript 6.0

- source: specs/DECISIONS.md
- status: accepted (ESLint part later superseded by D-019 per D-019's own text)
- decision: Pin ESLint ^9.39, @eslint/js ^9.39, TypeScript ~6.0.3; everything else latest (Vite 8, Vitest 5, Playwright 1.64, Babylon.js 9).
- scope: toolchain

## D-003: Scaffold conventions

- source: specs/DECISIONS.md
- status: accepted
- decision: Vite base './' (relative, ENG-82); `*.visual.ts` suffix for pure GPU/visual files excluded from coverage (ENG-45); layering enforced with import/no-restricted-paths and no-restricted-imports/properties/globals (ENG-11, ENG-142); FixedStepClock 60 Hz, max 5 steps per frame (ENG-100); Prettier ignores specs/, CLAUDE.md, .claude/; chunkSizeWarningLimit 1500 kB. ENG-52 test API and full ENG-54 smoke suite deferred to later phases.
- scope: scaffold, lint layering, build config

## D-004: Player ship data and the player_ship/ viewer

- source: specs/DECISIONS.md
- status: accepted
- decision: maxSpeed stored as maxSpeedFactor times roster baseSpeedPxPerSec (100 at that time); GameDefinition<TView> with a view slot; player_ship/ is a real second Vite HTML entry routed by app/route.ts; viewer captions in plain DOM, UI tested with a small fake DOM.
- scope: phase 2, ships data, viewer page

## D-005: Procedural ship geometry and lighting without new dependencies

- source: specs/DECISIONS.md
- status: accepted
- decision: In-house ear-clipping triangulation and prism/lathe helpers (no earcut); 64x64 procedural sky cube map as IBL with ACES tone mapping and glow layer; GPU-dependent wiring in `showcase-environment.visual.ts`.
- scope: rendering, models

## D-006: Model animations (animated reactor flames)

- source: specs/DECISIONS.md
- status: accepted
- decision: `render/model-animation.ts` per-node animations stepped by `stepModelAnimations(root, dt)` using injected frame time; reactor flame = flickering outer/inner cones plus plasma puffs, tunables in REACTOR_FLAME.
- scope: models, animation

## D-007: Low-poly, polygonal ship models

- source: specs/DECISIONS.md
- status: accepted
- decision: Flat-shaded faceted parts (split body section, 6-sided parts, hexagonal reactors, octahedron lights); each player ship under 2,000 triangles; viewer shows triangle count.
- scope: models, polygon budget

## D-008: Menu architecture (phase 01)

- source: specs/DECISIONS.md
- status: accepted
- decision: Pure MenuFlow state machine in app/ with screen ids in core/menu/; MenuAction defined in input/ plus a `{select: index}` command; GameDefinition gains screen, levels, texts, view.menuBackdrop; two Babylon scenes (game backdrop plus engine ship-select stage); canvas/overlay in a 3:4 `#stage` scaled by CSS transform; input ignored during transitions; menu entries are `div role="button"`.
- scope: menus, screen flow, input

## D-009: happy-dom for UI unit tests

- source: specs/DECISIONS.md
- status: accepted
- decision: Add happy-dom (MIT, dev only), opt in per test file with `// @vitest-environment happy-dom`.
- scope: unit testing

## D-010: Persistence in cookies, despite ENG-07's localStorage

- source: specs/DECISIONS.md
- status: accepted
- decision: Follow the vision, GD-51 and the phase: `platform/cookie-storage.ts` behind a KeyValueStorage interface (max-age cookie_max_age, SameSite=Lax); keys prefixed with game id (`stratoblaster_high_score`, `stratoblaster_last_ship`); bad values read as 0/none. Source notes ENG-07 could be updated to say "cookies".
- scope: persistence, high score, last ship

## D-011: ENG-52 check in make build

- source: specs/DECISIONS.md
- status: accepted
- decision: Test API installed under build-time `__E2E__`; `make build` greps dist/ and fails if `__GAME_TEST__` is present. Initially only getState and sendAction.
- scope: test API, build check

## D-012: Dark menu background, despite GD-61 pastel background

- source: specs/DECISIONS.md
- status: accepted
- decision: Follow review feedback: TITLE_LOOK uses a dark night palette; sun and grid stay bright. Pastel requirement later removed from specs (D-014).
- scope: menu look

## D-013: Cyberpunk HUD style for the menus, in CSS only

- source: specs/DECISIONS.md
- status: accepted (partly superseded by D-040; look superseded by D-103 per D-103's own text; source status line still reads Accepted)
- decision: Restyle overlay in index.html only: dark glass panels, neon corner brackets, CRT scanlines, uppercase headings, monospace readouts; selection still shown without colour.
- scope: menu look

## D-014: Cyberpunk, not synthwave: generated night city and yellow/cyan/red HUD

- source: specs/DECISIONS.md
- status: accepted (look superseded by D-103 per D-103's own text; source status line still reads Accepted)
- decision: Pastel requirement removed from specs; title backdrop is a seeded generated night city (seed 2077); overlay in acid yellow #fcee0a, cyan, red; striped sun and pink grid removed; title_grid_scroll_speed became title_city_scroll_speed.
- scope: menu look, title backdrop

## D-015: Player shots: data-driven weapons, pure ShotWorld, defaults

- source: specs/DECISIONS.md
- status: accepted (laser/missile numbers superseded by D-059)
- decision: Weapons are data (WeaponDefinition) registered via GameDefinition.playerWeapons; pure fixed-step ShotWorld; shots rendered as additive vertex-coloured meshes; defaults bullet 600 px/s 8 shots/s, laser 40/60/85/115/150 dps, missile 150 to 700 px/s; player_shots/ debug page.
- scope: player weapons, debug page

## D-016: Game renamed Stratoblaster

- source: specs/DECISIONS.md
- status: accepted
- decision: Game name is Stratoblaster everywhere (package name, game id, page titles, README, specs, tests). Game id is the cookie prefix; logo reduced to 46 px. No migration of old cookies.
- scope: naming, cookies

## D-017: Title logo shrinks to fit the screen

- source: specs/DECISIONS.md
- status: accepted
- decision: `shrinkToFit()` lowers the logo font size 1 px at a time until it fits (system fonts differ on CI).
- scope: title screen

## D-018: Faster CI

- source: specs/DECISIONS.md
- status: accepted (amended 2026-10-27 by reviewer)
- decision: e2e originally a 3-shard matrix; check job installs without Chromium (SKIP_BROWSER=1); fixed waits replaced by waitForFrames. Amended: e2e runs in a single job again, no shards, one playwright-report artefact.
- scope: CI

## D-019: ESLint 10 with eslint-plugin-import-x

- source: specs/DECISIONS.md
- status: accepted (supersedes ESLint part of D-002)
- decision: Replace eslint-plugin-import with eslint-plugin-import-x 4.17; ESLint and @eslint/js to 10; TypeScript stays ~6.0.3. Source says the human owner is to update ENG-12.
- scope: lint toolchain

## D-020: Generated levels: data-driven terrain, tilted playfield camera, level_zero/ page

- source: specs/DECISIONS.md
- status: accepted (reviewer accepted the 11 proposed defaults)
- decision: One world unit = one logical pixel; core/scenery/ pure seeded sections; perspective camera tilted 35 degrees, 40 degree FOV; terrain chunks 320x~1100 on an 8-unit grid; textures blended by altitude/slope via StandardMaterial plugin; props as thin instances; Level Zero lives in src/game/ and is not listed in level select; debug page level_zero/ (route scenery-viewer).
- scope: terrain, camera, Level Zero

## D-021: Roads and paths, with buildings only along them

- source: specs/DECISIONS.md
- status: accepted
- decision: Seeded road network (main roads, paths, junction widening); buildings only from slots along valid roads; roads end off screen; ribbons draped on terrain with soft see-through edges.
- scope: roads, props (P04-R07)

## D-022: Cloud layers always above the terrain

- source: specs/DECISIONS.md
- status: accepted
- decision: terrainCeiling(level) bounds ground height; each cloud layer placed at max(look altitude, ceiling + 15). Level Zero layers at 265 and 295.
- scope: clouds

## D-023: Section ground cover, street grids, dense overlap-free buildings

- source: specs/DECISIONS.md
- status: accepted
- decision: TerrainSection gains surface (lush/paved), trees, groups, streets; ground cover passed in vertex colours; buildings placed once per seed with a footprint grid; Level Zero ends with meadows, industrial zone, city centre (still 180 s).
- scope: scenery

## D-024: Straight street networks, buildings made of parts, stable shadows

- source: specs/DECISIONS.md
- status: accepted
- decision: Rectilinear StreetGrid (rows, columns, links); buildings assembled from seeded parts (8 variants per family, own prop kinds); fixed shadow frustum 1600 units with texel-snapped sun; specular 0 on props/terrain.
- scope: scenery, shadows

## D-025: Bigger district buildings, square plans and fallback kinds

- source: specs/DECISIONS.md
- status: accepted
- decision: Generators take a half-side; 6 families of 8 variants; PropKindRule.frontage; slot spacing 24 units; fallback to smaller kinds.
- scope: scenery props

## D-026: City blocks filled by podiums

- source: specs/DECISIONS.md
- status: accepted
- decision: Street grid returns blocks; BlockFill sections get a stretched podium per block with 2-4 towers; irregular grid follow-up.
- scope: scenery city

## D-027: City buildings made of lots, along the factory streets

- source: specs/DECISIONS.md
- status: accepted
- decision: City centre uses the industrial street maze; buildings split into 1-4 lots with five volumes; city podium models removed, `blocks` option kept in engine; follow-up fills blocks with buildings on the ground.
- scope: scenery city

## D-028: Street corners, centre lines and cars

- source: specs/DECISIONS.md
- status: accepted
- decision: Streets drawn half their width past both ends; optional centre lines painted into the road mesh; cars as an optional PropRules.cars rule drawn as thin instances.
- scope: roads, traffic

## D-029: 2x2 roads

- source: specs/DECISIONS.md
- status: accepted
- decision: RoadRules.dual sets 2x2 roads (first mainRoads and a share `avenues` of grid lines); Road.lanes drives markings and car lanes.
- scope: roads

## D-030: Moving cars

- source: specs/DECISIONS.md
- status: accepted (supersedes static cars of D-028)
- decision: Each car follows its road at constant speed with a closed-form position (start +/- speed*time, wrapped); one speed per lane; cars uploaded each frame as thin instances; hidden near road ends.
- scope: traffic

## D-031: Props drawn only near the view

- source: specs/DECISIONS.md
- status: accepted
- decision: PropField.setWindow filters placements by Z to the ground in view plus propReach (40 before, 120 past); range widened by propStep 40 so instances are re-uploaded only every ~40 units.
- scope: props performance

## D-032: First enemies: abstract Enemy with hooks, EnemyWorld, enemies/ page

- source: specs/DECISIONS.md
- status: accepted
- decision: Core `Enemy` abstract class (ShotTarget) with update(ctx, dt) and optional onDestroyed(ctx); EnemyContext lets enemies fire bullets, homing missiles, lasers or spawn enemies; EnemyKindDefinition.spawn; EnemyWorld steps enemies and shots; enemies/ debug page over Level Zero.
- scope: phase 5 enemies engine

## D-033: Low-poly shaping primitives SolidBuilder.loft and bevelSlab

- source: specs/DECISIONS.md
- status: accepted
- decision: Two engine primitives in render/geometry/solids.ts: loft(section, stations) and bevelSlab(outline, heights, insets), flat-shaded.
- scope: models

## D-034: Explosion particles as thin instances, one mesh per layer

- source: specs/DECISIONS.md
- status: accepted
- decision: createBlastRenderer draws each explosion layer (smoke, shock rings, fireballs, debris, embers, flashes) as one disc mesh of thin instances with per-instance matrix and colour.
- scope: fx explosions

## D-035: Water colour painted on the terrain, by depth

- source: specs/DECISIONS.md
- status: accepted
- decision: Terrain shader colours ground under sea level by depth (turquoise shallows to deep) and paints beach and surf; sea plane mostly see-through (alpha 0.4).
- scope: sea rendering (P04-R02)

## D-036: Playable levels: GameLevel, distance-triggered wave runner, pure LevelRun

- source: specs/DECISIONS.md
- status: accepted
- decision: GameDefinition.gameLevels lists GameLevel (SceneryLevel, WaveScript, EnemyDifficulty); World 1 is data in src/game/config/world-1/; LevelRun is pure.
- scope: phase 6 level engine

## D-037: Desert ground: sandy cover and dunes

- source: specs/DECISIONS.md
- status: accepted
- decision: Surface gets `sandy` in the green vertex-colour channel mixed by the terrain shader; dunes in the height field.
- scope: desert ground

## D-038: World 1 balance measured by a play-through without shooting

- source: specs/DECISIONS.md
- status: accepted (numbers superseded by D-044, per D-044)
- decision: Unit test plays each level with a ship that never fires, counting enemies, HP and screen peaks (66/82/124/156/184 enemies; factors 0.8/0.85/0.9/1.0/1.1).
- scope: balance measurement

## D-039: Game screen controls and debug options

- source: specs/DECISIONS.md
- status: accepted
- decision: input/game-controls.ts merges keys (arrows/WASD by position, Space), left stick, D-pad, A/right trigger and touch drag with an on-screen fire button; debug URL options.
- scope: game controls

## D-040: CRT scanline overlay removed

- source: specs/DECISIONS.md
- status: accepted (partly supersedes D-013)
- decision: `#stage::after` (scanlines and vignette) removed from index.html; rest of the HUD style stays.
- scope: menu look

## D-041: In-game HUD, no Back button over the playfield

- source: specs/DECISIONS.md
- status: accepted ("Esc leaves" wording superseded in the game screen by D-095)
- decision: ui/game-hud.ts shows ship name and health bar, weapon and level, level progress bar, enemies destroyed; no Back button in game; Esc/Backspace/gamepad B still left the level at that time.
- scope: HUD

## D-042: Only enemies on screen can be shot

- source: specs/DECISIONS.md
- status: accepted
- decision: LevelRunOptions.inView limits which targets player shots can hit to those whose centre is on screen.
- scope: gameplay

## D-043: E switches weapon in game

- source: specs/DECISIONS.md
- status: accepted
- decision: GAME_CONTROLS_CONFIG.switchKeys = KeyE (key position); LevelRun cycles through the game's weapons at the starting level. Source notes GD section 2 gives E to Special/bomb, so bombs need another key.
- scope: controls

## D-044: Faster ships (+50 %) and denser waves (+50 %)

- source: specs/DECISIONS.md
- status: accepted (ship speed superseded by D-047; counts further changed by D-051)
- decision: baseSpeedPxPerSec 100 to 150; WAVE_DENSITY 1.5; measured 119/143/213/270/321 enemies. Source says phase-02 spec still says 100 px/s and its text is the reviewer's to update; counts are above the P06 tunables.
- scope: speed, wave density

## D-045: Ship banks when moving sideways; a felt acceleration

- source: specs/DECISIONS.md
- status: accepted
- decision: Ship model banks up to 35 degrees at full sideways speed, easing at 8 per second; visual only. Acceleration time 0.18 s to full speed.
- scope: ship feel (GD-10)

## D-046: No road crossings; lone buildings and hamlets away from roads

- source: specs/DECISIONS.md
- status: accepted
- decision: Three opt-in rules set for World 1 only: RoadRules.noCrossings and related lone-building/hamlet rules.
- scope: roads, World 1 props

## D-047: Player base speed raised again to 225 px/s

- source: specs/DECISIONS.md
- status: accepted
- decision: baseSpeedPxPerSec 150 to 225 (balanced 225, heavy 180, light 315); speed factors unchanged. Source says phase-02 spec still says 100 px/s.
- scope: speed

## D-048: Enemies from the top come in where the ship can reach

- source: specs/DECISIONS.md
- status: accepted
- decision: EnemySpawnArea.topRange limits the X range of top-entry kinds and their paths to the ship's reach (bosses stay inside x 107-373 per P07-R05).
- scope: spawning

## D-049: Weapon bonuses dropped by destroyed enemies

- source: specs/DECISIONS.md
- status: accepted
- decision: Pure BonusWorld; a destroyed enemy drops a bonus with chance perHealth x maxHealth kept within [min, max], drawn from its own seeded source.
- scope: bonuses

## D-050: Player damage, lives and game over

- source: specs/DECISIONS.md
- status: accepted
- decision: Pure PlayerHull (health, lives, invincibility) and findPlayerHits (enemy bullets, missiles, firing lasers, enemies touching the hitbox, most damaging first).
- scope: GD-20..GD-22

## D-051: Filler groups in the lulls of the World 1 levels

- source: specs/DECISIONS.md
- status: accepted
- decision: `fill` adds light groups in the lulls between written beats with maxGap shrinking from start to end; measured 279/335/433/498/537 enemies and peaks 16/20/24/30/32. Source says counts are far above the spec tunables.
- scope: waves, balance

## D-052: Dead-end removal and path starts without crossings

- source: specs/DECISIONS.md
- status: accepted
- decision: With `tees`, a link cut back during dead-end removal is never built again (Link.cut); without crossings a path starts only where its main road allows.
- scope: street grids

## D-053: Bosses as enemies with shot-target proxies for parts and core

- source: specs/DECISIONS.md
- status: accepted
- decision: Boss extends Enemy; BossPart and BossCore are separate ShotTargets whose health setters drop damage while the boss is not in place or the core is shielded.
- scope: boss engine (P07-R01)

## D-054: Level progress and ground distance kept apart during fights

- source: specs/DECISIONS.md
- status: accepted
- decision: ScrollTrack keeps `distance` (ground flown) and `progress` (waves, bosses, end, HUD); while a boss is fought the track is held.
- scope: boss ground speed (P07-R03)

## D-055: Data-driven stage patterns and World 1 boss tuning

- source: specs/DECISIONS.md
- status: accepted
- decision: A stage pattern is data (BossPatternSpec volleys of generic shapes, core/systems/boss-pattern.ts); bosses tuned with guns at level 3.
- scope: boss patterns (P07-R04)

## D-056: Continue from the mini boss checkpoint

- source: specs/DECISIONS.md
- status: accepted
- decision: LevelRun saves a LevelCheckpoint (progress, bosses passed, weapons and levels) when the mini boss is destroyed; Game over shows Continue/Level select.
- scope: checkpoint (GD-42, P07-R08)

## D-057: Shots leave from the barrels, as the camera sees them

- source: specs/DECISIONS.md
- status: accepted
- decision: Guns have muzzles (offsets from the enemy centre plus a height); data in BossDesign.guns and ENEMY_CONFIG.*.muzzles.
- scope: shots origin

## D-058: Boss turrets follow the player

- source: specs/DECISIONS.md
- status: accepted (extended by D-060)
- decision: A piece's guns may sit on a turret (Guns.turret); volleys from them are flagged and their muzzles turn with its aim around the pivot.
- scope: boss turrets

## D-059: Player weapon balance

- source: specs/DECISIONS.md
- status: accepted
- decision: New rule GD-33: laser and missiles deal 70-100 % of guns' dps; laser 80/140/200/260/320 dps; missile damage 14 (was 8); guns remain reference.
- scope: weapon balance (GD-33)

## D-060: Every boss turret turns the way it fires

- source: specs/DECISIONS.md
- status: accepted
- decision: BossPattern.turnTurrets points each turret the way its next volley goes (at the player, along fan heading, with rings).
- scope: boss turrets

## D-061: Moving boss limbs: joints in the simulation

- source: specs/DECISIONS.md
- status: accepted
- decision: Joints are engine data (BossJointSpec: pivot, parent, swing amplitude/period/phase; BossJoints), stepped by Boss.update; parts hang on joints.
- scope: boss limbs

## D-062: Shots go through a shielded boss core

- source: specs/DECISIONS.md
- status: accepted
- decision: Enemy gets `shotTargets`; a Boss with a shielded core leaves the core out so shots reach parts behind it.
- scope: boss shielding

## D-063: Angry bosses: a bullet hell after each destroyed part

- source: specs/DECISIONS.md
- status: accepted
- decision: BossStats.rageSeconds (3 s); Boss.rage starts when a part is destroyed and Boss.updateRage fires an angry pattern instead of the stage's.
- scope: boss behaviour

## D-064: Time of day, clouds and weather as an engine atmosphere along the level

- source: specs/DECISIONS.md
- status: accepted
- decision: core/scenery/atmosphere.ts (pure) holds every changing number (sun, haze, sky, ambient, fog, cloud layers) blended along the level.
- scope: atmosphere engine (P08-R04)

## D-065: Snow as GPU particles behind the playfield; aurora as additive sheet

- source: specs/DECISIONS.md
- status: accepted (no level uses snow or aurora since D-110; engine kept)
- decision: config/weather.ts lists kinds (snow 1,500 at strength 1); WeatherLayer builds one quad mesh per kind.
- scope: weather engine (P08-R05)

## D-066: Frozen ground: ice in existing texture slots, lakes, crevasses, floating ice

- source: specs/DECISIONS.md
- status: accepted (no level places the frozen props since D-110; tools kept)
- decision: Terrain shader layer slots filled by each look; World 2 original look used snow, dark rock, lake ice, glacier ice.
- scope: frozen ground tools

## D-067: World 2 waves composed from plans; balance measured as in World 1

- source: specs/DECISIONS.md
- status: accepted
- decision: Each level is a WavePlan (cycle of phrases; beat every `gap`, groups growing by 60 %).
- scope: World 2 waves

## D-068: Boss engine additions for World 2, and World 2 boss tuning

- source: specs/DECISIONS.md
- status: accepted
- decision: Generic engine data BossVolley.needs/after, EnemyLaserSpec.sweepDeg (sweepDeg removed by D-073).
- scope: boss engine, World 2 bosses

## D-069: Enemy bullets as blended blobs of energy

- source: specs/DECISIONS.md
- status: accepted (revised; replaced in look by D-074)
- decision: Each bullet a disc with white-hot core fading to colour, alpha-blended.
- scope: enemy bullet look

## D-070: The bosses page grouped by world

- source: specs/DECISIONS.md
- status: accepted
- decision: EnemyViewerPanel takes optional groups; bosses page groups bosses by the level they are fought in.
- scope: bosses/ page

## D-071: Weapon levels kept from one completed level to the next

- source: specs/DECISIONS.md
- status: accepted
- decision: On "Level complete" GameSession saves RunArsenal.snapshot() as JSON under `<game id>_weapons` in cookies; each level starts from it; game over saves nothing.
- scope: weapon persistence

## D-072: Laser colours by boss, and beams locked once firing

- source: specs/DECISIONS.md
- status: accepted
- decision: A boss's lasers take its kind id as style (withOwnLasers); view colours a style with the boss's neon.
- scope: boss lasers

## D-073: Lasers on turrets instead of sweeping lasers

- source: specs/DECISIONS.md
- status: accepted (supersedes sweepDeg of D-068)
- decision: EnemyLaserSpec.sweepDeg removed; lasers sit on turrets (Guns.turretLaser, BossVolley.turret); the turret aims until the beam fires then holds.
- scope: boss lasers

## D-074: Enemy bullets as balls of plasma, drawn as thin instances

- source: specs/DECISIONS.md
- status: accepted (replaces look of D-069)
- decision: Bullet = flickering aura, deep-coloured body, two counter-spinning swirls, bright core; thin instances.
- scope: enemy bullet look

## D-075: e2e tests drive the level clock; e2e builds draw fewer pixels

- source: specs/DECISIONS.md
- status: accepted (advance partly reworked by D-093)
- decision: `__GAME_TEST__.advance(seconds)` runs the level at once without rendering; e2e builds render at half resolution without multisampling.
- scope: e2e infrastructure

## D-076: Rain as a weather kind

- source: specs/DECISIONS.md
- status: accepted
- decision: `rain` entry in config/weather.ts (2,000 streaks at strength 1, 380-520 units/s fall, slant 30-70, 16x long streaks) with three optional fields any kind may use (e.g. align).
- scope: weather engine (P09-R05)

## D-077: Lightning: strikes from the level seed, capped flash, bolt in the clouds

- source: specs/DECISIONS.md
- status: accepted
- decision: core/scenery/lightning.ts LightningSchedule(seed): strikes 4-10 s apart, one flash or (chance 0.35) two flashes 0.25 s apart, at most 2 flashes in any second.
- scope: lightning, photosensitivity

## D-078: Mist and an ambient tint as look parameters

- source: specs/DECISIONS.md
- status: accepted
- decision: SkyLook.mist {fog, white} and SkyLook.tint.
- scope: sky looks

## D-079: One water level for sea, rivers, swamps and lakes; set pieces over water

- source: specs/DECISIONS.md
- status: accepted
- decision: Every World 3 level has a water level (0); rivers are channels below it, swamps relief around it; sea section defined by coast; set pieces and lines over water.
- scope: water engine

## D-080: World 3 waves and balance, measured as in Worlds 1 and 2

- source: specs/DECISIONS.md
- status: accepted
- decision: WavePlans as World 2's; groups grow 70 % over each level; gaps 4.9 to 3.5 s (3-1) down to 4 to 2.7 s (3-5).
- scope: World 3 waves

## D-081: The ten World 3 bosses, and their tuning

- source: specs/DECISIONS.md
- status: accepted
- decision: No engine change; every boss is data on the phase 7/8 boss engine (joints, laser turrets, launches, homing missiles).
- scope: World 3 bosses

## D-082: Two weathers at once, falling ash and rising embers

- source: specs/DECISIONS.md
- status: accepted
- decision: SkyLook.secondWeather (and Atmosphere.secondWeather) falls at the same time as weather; WeatherLayer draws one mesh per kind present.
- scope: weather engine (P10-R06)

## D-083: Clouds lit from below, and tinted clouds

- source: specs/DECISIONS.md
- status: accepted
- decision: SkyLook.cloudTint and SkyLook.underglow {color, strength}.
- scope: sky looks

## D-084: Lava as the level's liquid: self-lit shader, hot edge, glow occluded by terrain

- source: specs/DECISIONS.md
- status: accepted (no level uses lava since D-112; engine kept)
- decision: A level's liquid stays one plane at sea.level; a look's sea.lava (LavaLook) draws it with a Worley-plate shader.
- scope: lava engine (P10-R05)

## D-085: Smoke and steam plumes from props; wagons moving on a line

- source: specs/DECISIONS.md
- status: accepted
- decision: Prop models may list `plumes` (smoke/steam kinds in config/plumes.ts); PropField builds one mesh per prop kind and plume kind.
- scope: props

## D-086: A shot style per level: contrast outlines in World 4

- source: specs/DECISIONS.md
- status: accepted
- decision: SceneryLook.shotStyle (engine name) is passed to the game's enemy shot renderer; game's `contrast` style adds a dark blended rim.
- scope: shot readability (P10-R07)

## D-087: World 4 waves and balance, measured as in Worlds 1 to 3

- source: specs/DECISIONS.md
- status: accepted
- decision: WavePlans as World 3's, every kind in every cycle; gaps and growth chosen by sweeping with the D-038 play-through.
- scope: World 4 waves

## D-088: The ten World 4 bosses, and their tuning

- source: specs/DECISIONS.md
- status: accepted
- decision: No engine change; every boss is data on the boss engine, made in parallel by five sub-agents (one level each).
- scope: World 4 bosses

## D-089: World 5 dropped: a 4 x 5 level grid

- source: specs/DECISIONS.md
- status: accepted
- decision: LEVELS_CONFIG.worlds 5 to 4; level select shows 20 levels 1-1 to 4-5, all unlocked; engine keeps locked-level support for other games. Requirement texts naming World 5 were changed with dated notes. The Caldera Throne is the last boss.
- scope: level grid, vision scope

## D-090: Ten veteran and elite enemy kinds, with moving parts

- source: specs/DECISIONS.md
- status: accepted
- decision: P05-R13 to P05-R24 added to the phase 5 spec; five veterans (Wasp, Mortar, Mantis, Phantom, Minelayer) from World 3, five elites (Hydra, Orbiter, Scissor, Juggernaut, Hive) in World 4.
- scope: enemies

## D-091: Phase 11 spec defaults (score, lives, bombs)

- source: specs/DECISIONS.md
- status: accepted (reviewer approved the spec, 2026-10-26)
- decision: Score per level attempt; boss part scores 10 % of boss points, core its points; high score saved when an attempt ends; bombs 3 at start, max 5, 100 damage, 1 s, keys R / Left Shift, gamepad X and LB, touch BOMB; life bonus 1 %, bomb bonus 3 %, mini boss core always drops a life.
- scope: score, bombs, lives

## D-092: Phase 11 implementation choices

- source: specs/DECISIONS.md
- status: accepted
- decision: BonusWorld keeps weapon draws on the main source (seed+1); life and bomb drawn from their own source (seed+2, LevelRun) so weapon bonus draws are unchanged.
- scope: bonuses determinism

## D-093: e2e builds have no render loop: the tests step the game

- source: specs/DECISIONS.md
- status: accepted
- decision: In **E2E** builds the game and debug pages start no render loop; `step(frames, render?)` and `advance(seconds)` drive them; `__SCENERY_TEST__` and `__SHOTS_TEST__` added and checked absent from production.
- scope: e2e infrastructure (ENG-52)

## D-094: Faster git hooks

- source: specs/DECISIONS.md
- status: accepted
- decision: tsc --incremental with cache in node_modules/.cache/tsc; Prettier and ESLint caches; import-x rules covered by TypeScript turned off.
- scope: hooks (ENG-65)

## D-095: Phase 12 spec defaults (pause, music, settings)

- source: specs/DECISIONS.md
- status: accepted
- decision: In game: Escape, KeyP, gamepad Start/Select and a touch pause button pause; Backspace and gamepad B do nothing; leaving goes through pause menu. Auto-pause on hidden page or lost gamepad. Settings screen with two 0-10 sliders (Music 6, SFX 8) in cookies; no master volume. All audio generated with Web Audio. Source notes quality presets (ENG-102) were removed from the engineering spec by the reviewer on 2026-10-26.
- scope: pause, audio, settings

## D-096: Pause as menu screens; Escape is its own action

- source: specs/DECISIONS.md
- status: accepted
- decision: `pause` and `settings` are MenuScreens of the pure MenuFlow (pause to game, pause to settings, pause to title, title to settings); `game to title` removed; MenuState.paused.
- scope: pause flow

## D-097: A small Web Audio engine instead of Babylon's audio; cues from core state

- source: specs/DECISIONS.md
- status: accepted
- decision: src/audio/ uses Web Audio directly: oscillators and noise through filters and gain envelopes, lookahead Sequencer, MusicPlayer, limiter.
- scope: audio engine (P12-R05)

## D-098: Generated music: per-world styles and a seeded composer

- source: specs/DECISIONS.md
- status: accepted
- decision: src/game/view/audio/ holds a MusicStyle per world (tempo, scales, progressions, instruments, drum/bass feels).
- scope: music (P12-R06)

## D-099: Synthwave music: echo and reverb sends, 80s drum machine, a full menu track

- source: specs/DECISIONS.md
- status: accepted
- decision: TrackMixer per playing track with tempo-synced echo and shared generated reverb on the music bus.
- scope: music

## D-100: Stressful boss tracks and more energetic synthwave

- source: specs/DECISIONS.md
- status: accepted
- decision: Boss tracks have own drums, bass and chord stabs (compose-boss.ts): pushed kicks, sixteenth hats, snare rolls, rolling octave bass, tense progressions.
- scope: boss music (P12-R07)

## D-101: Darksynth everywhere, a minigun gun

- source: specs/DECISIONS.md
- status: accepted
- decision: Every style plays minor, harmonic minor or phrygian keys with heavy kick and dark pads; growling bass-heavy in Worlds 1 and 4 and the menu; minigun rattle for the gun.
- scope: music, SFX

## D-102: Alternating shot streams, one fire cue per volley

- source: specs/DECISIONS.md
- status: accepted
- decision: ShotWorld keeps one cooldown and a next-stream index: a shot every 1/(shotsPerSecond x streams) s, streams in listed order (P03-R11).
- scope: player shots (P03-R11)

## D-103: Darksynth look for the menus and the HUD, no cyberpunk

- source: specs/DECISIONS.md
- status: accepted (supersedes the look of D-013 and D-014)
- decision: Overlay tokens --hot (magenta), --violet, --red, --sunset, --chrome; chrome italic logo; neon glows replace glitch split; selected entries a magenta gradient block with markers unchanged; backdrop night city recoloured crimson/magenta/violet.
- scope: menu and HUD look (GD-60, P01-R05, P01-R13)

## D-104: A pilot instead of the ship in the menu backdrop (reverted)

- source: specs/DECISIONS.md
- status: reverted
- decision: A generated pilot model replaced the ship, then the reviewer asked to revert to the balanced ship and delete all pilot code. Only the sun emblem's removal stays (per the source).
- scope: title backdrop (P01-R05)

## D-105: The boss health bar moves to the left edge

- source: specs/DECISIONS.md
- status: accepted
- decision: Slim vertical gauge up the left edge under the player's health panel (top 96 px, 300 px tall, 8 px wide, no panel); fills from the bottom; part notches as ticks; name written along it.
- scope: boss bar (P07-R02)

## D-106: Bullets leave from inside the ship, under it

- source: specs/DECISIONS.md
- status: accepted
- decision: Optional `launchBack` on projectile weapons; bullet sets 13 px behind launch point; tracers drawn 8 units under the playfield plane.
- scope: player bullets (P03-R01)

## D-107: Enemy explosions as short, muffled booms

- source: specs/DECISIONS.md
- status: accepted (superseded by D-108 per D-108's text)
- decision: `boom` recipe: falling sine thump, low noise body, 30 ms crackle; 0.22 s small, 0.5 s large.
- scope: explosion SFX

## D-108: Realistic, layered explosions

- source: specs/DECISIONS.md
- status: accepted (supersedes D-107's booms)
- decision: One `explosion` recipe for every blast in three sizes: 12 ms crack, closing noise body, sub-bass thump; a busy wave peaks at -5.8 dBFS at default volume.
- scope: explosion SFX

## D-109: World 1 as one gradient: sea, green grass, desert

- source: specs/DECISIONS.md
- status: accepted (amended 2026-10-27 by reviewer: 1-5 ends on "Deep desert", no factory or city in World 1)
- decision: One ground for World 1; levels cut 1-1 open sea, 1-2 Green coast, 1-3 Green country, 1-4 Dry lands, 1-5 desert; time of day fixed per level with sun at 72/55/35/14/8 degrees; new villages and farms groups. Bosses and waves unchanged.
- scope: World 1 scenery (P06-R05, R06, R10)

## D-110: World 2 reworked: from the desert to the factories

- source: specs/DECISIONS.md
- status: accepted (amended 2026-10-27: no sea anywhere in World 2, rivers allowed)
- decision: World 2 becomes the Industrial Desert: 2-1 Great erg, 2-2 Mining mesas, 2-3 Oil fields, 2-4 Industrial belt, 2-5 Factory district; sections blend over 900 units; times of day morning, midday, afternoon, dusk, night; new oil pumpjack prop. Frost-themed bosses and wave scripts unchanged; frozen props and snow/aurora tools kept but unused by levels.
- scope: World 2 scenery (P08-R03, R06, R07)

## D-111: World 3 reworked: from the factories to the garden villages

- source: specs/DECISIONS.md
- status: accepted
- decision: World 3 becomes a gradient: 3-1 Canal works, 3-2 Docklands, 3-3 Workers' quarter, 3-4 Suburbs, 3-5 Garden villages; no sea (canal and river); 900-unit transitions; three new home models; sky scripts (rain, storm) kept. Jungle bosses and waves unchanged; jungle props kept but unused.
- scope: World 3 scenery (P09-R03, R04, R06)

## D-112: World 4 reworked: from the houses to the skyscrapers

- source: specs/DECISIONS.md
- status: accepted
- decision: World 4 becomes the Metropolis: 4-1 Garden town, 4-2 Inner town, 4-3 Midtown, 4-4 Business district, 4-5 Downtown; new family of 8 skyscrapers; river between quays; no sea, no lava; sky scripts (ash, embers) kept. Volcanic bosses and waves unchanged; lava engine and volcanic props kept but unused.
- scope: World 4 scenery (P10-R03, R04, R05, R08)
