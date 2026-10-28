# Architecture

Requirements: [`specs/01-engineering.md`](../specs/01-engineering.md).

## Layers

```
input/ ──actions──▶ app/ ──▶ core/ (pure, fixed 60 Hz step)
                              │
                         state + events
                              ▼
              render/  fx/  audio/  ui/   (read-only)
```

- `core/`: pure, deterministic, game-agnostic simulation. No Babylon, no DOM, no `Math.random` / `Date.now`.
- `render/`, `fx/`, `audio/`, `ui/`: read core state and react to core events; never mutate it.
- `input/`: turns devices into abstract actions.
- `app/`: the only place (with `main.ts`) that wires layers together.
- `config/`: engine tunables. `platform/`: browser wrappers. `debug/`: dev/e2e-only tools.

These rules are enforced by ESLint (`eslint.config.mjs`, `import/no-restricted-paths`).

## Engine / game split

Everything outside `src/game/` is a reusable engine. `src/game/` holds this game's content:

| Folder              | Contents                                                         | May import                                                                         |
| ------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `src/game/sim/`     | concrete bosses, enemies, weapons, levels (extend `core/` bases) | `core/`, `config/`, `game/sim/`, `game/config/`                                    |
| `src/game/view/`    | meshes, materials, effects, sounds for that content              | `render/`, `fx/`, `audio/`, `ui/`, `assets/`, `core/`, `game/sim/`, `game/config/` |
| `src/game/config/`  | game-specific tunables                                           | `core/`                                                                            |
| `src/game/index.ts` | the single `GameDefinition` export                               | anything in `game/`                                                                |

The engine never imports `src/game/`. `main.ts` imports `src/game/index.ts` and hands the `GameDefinition` to `app/`.
Engine tests use the sample game in `tests/fixtures/`, not `src/game/`.

## Pages and routes

The build has seven HTML entries sharing one bundle (`src/main.ts`):

| Page                      | Route (`app/route.ts`) | Started by                  |
| ------------------------- | ---------------------- | --------------------------- |
| `index.html`              | `game`                 | `app/start-app.ts`          |
| `player_ship/index.html`  | `player-ship-viewer`   | `app/start-ship-viewer.ts`  |
| `player_shots/index.html` | `player-shots-viewer`  | `app/start-shot-viewer.ts`  |
| `enemies/index.html`      | `enemy-viewer`         | `app/start-enemy-viewer.ts` |
| `bosses/index.html`       | `boss-viewer`          | `app/start-boss-viewer.ts`  |
| `boss/index.html`         | `boss-viewer`          | `app/start-boss-viewer.ts`  |

The player ship viewer shows every ship of `GameDefinition.playerShips` side by side, rotating
(`render/model-showcase.ts`), with name and stats captions (`ui/caption-row.ts`). It is lit by a
procedural sky cube map (`render/environment/`), so it downloads no asset.

The player shots viewer (phase 03) looks straight down on a `GameDefinition.screen`-sized
playfield (orthographic camera, one world unit per logical pixel, Y up). One ship fires the
selected weapon at the selected level at dummy targets (`app/dummy-targets.ts`); the panel
(`ui/shot-viewer-panel.ts`) and keys 1-9 / W / S / G / T switch level, weapon, ship, stream
guides and targets. A tile (`ui/stats-tile.ts`) shows the FPS and the triangles drawn per frame.

The generated level viewer of phase 04 (`level_zero/`) and its test level, Level Zero, were removed
(reviewer, 2026-10-28): the `enemies/` page and a boss with no level fly over the first playable
level's ground.

The enemies viewer (phase 05, `enemies/`) shows one kind of `GameDefinition.enemyKinds` at a
time over the first scenery level, under the same tilted camera. The kind spawns again once its
group has gone; the game's first ship flies with arrows / WASD and shoots with any weapon and
level, and cannot be hit. The model view switches to a close-up scene like `player_ship/`
(`app/enemy-close-up.ts`: dark background, orbit camera framed on the model), where ← / → switch
the kind. The panel
(`ui/enemy-viewer-panel.ts`) and keys N / B / M / X / 1-9 / F / P pick the kind, the view, the
weapon and level, fire and pause. e2e builds expose `window.__ENEMIES_TEST__`
(`debug/enemy-viewer-test-api.ts`: state and frame stepping).

The bosses viewer (phase 07, `bosses/`) works the same way for `GameDefinition.bossKinds`: the
picked boss comes in over the scenery of its level (`app/boss-viewer-stage.ts`, rebuilt when a
boss of another level is picked), the ground scrolls at its fight speed, and it comes again once
it has blown up. K destroys its next part; the panel shows its stage. The wireframe view draws
the hit circles of its core and of each part (the ones that shield the core in yellow). e2e
builds expose `window.__BOSSES_TEST__` (`debug/boss-viewer-test-api.ts`).

## Time of day, clouds and weather (phases 08, 09, 10)

```
SceneryLook.atmosphere (SkyScript: SkyLook + changes, game data)
        │ resolveSky (core/scenery/sky-look.ts, presets in config/time-of-day.ts, config/weather.ts)
        ▼
AtmosphereTrack (core/scenery/atmosphere.ts) ── at(distance) ──▶ Atmosphere (plain numbers)
        │                                                          │
render/scenery/SkyLayers ── applyAtmosphere (sun, ambient, haze) ◀─┘
        ├─ cloud layers (cover, colours, haze), WeatherLayer (GPU particles), AuroraLayer
        ├─ LightningLayer (LightningSchedule from the level's seed → flash, bolt; `flashed`)
        ├─ RainRings (scenery-stage: rings on the water when the weather kind has some)
        └─ SceneryKit.update (shadow darkness, ground lights); level-scene: sky environment
```

- A level's look has a fixed part (`SceneryLook`: ground textures, sea, roads, shadows) and,
  optionally, an `atmosphere`: a time of day (`dawn` … `night`), the cover of both cloud layers,
  a storm greyness, a weather (`{ kind, strength }`) and an aurora, with changes over stretches
  of the level (seconds of scroll). A look without one keeps its fixed sky (World 1).
- `AtmosphereTrack.at(distance)` blends every number smoothly between looks, following the ground
  distance, so a debug jump shows the right look. Nothing in `core/systems` reads it: weather and
  light are only a look (P08-R05).
- Weather kinds are data (`config/weather.ts`): particle count at strength 1, fall, wind, streak,
  size, colour, fog at strength 1. `WeatherLayer` draws one mesh of quads per kind, moved on the
  GPU (`weather-material.visual.ts`), and only the first `strength × max` of them.
- Phase 9: rain is a kind aligned with its fall (thin streaks), greying the haze, with rings on
  the water (`RainRings`, a plane at the water level the terrain hides). A look may have a
  `mist` (fog brought in, haze whitened), an ambient `tint` and `lightning` (0..1):
  `LightningSchedule` (`core/scenery/lightning.ts`, pure) draws the strikes from the level's seed
  (4–10 s apart, at most 2 flashes a second), `flashed` brightens the ambient light and the haze
  up to ×1.8 during a flash, and `LightningLayer` draws a bolt in the low clouds. The renderer
  asks for the flash at its own clock; nothing in the simulation reads it.
- Debug options: `weather=0` (lightning included) and `look=<time of day>` (`AtmosphereOptions`).
- Phase 10: a look may have a `secondWeather` falling at the same time as its weather (ash and
  embers together; `WeatherLayer` draws one mesh per kind present), a `cloudTint` (factors on the
  clouds' colours) and an `underglow` (fire or lava lighting the clouds, the haze and the ambient
  light from below, `UNDERGLOW` in `config/time-of-day.ts`). Weather kinds may be added on
  (`blend: 'add'`, self-lit sparks), flicker and fade near the top of their box (`ash`, falling
  slowly; `embers`, rising: a negative fall).
- Phase 10: lava (`SeaLook.lava`): the level's liquid at `sea.level` is drawn with a self-lit
  shader (`lava-material.visual.ts`: drifting, churning crust plates over a glowing melt), the
  terrain plugin scorches the rock by it and adds a glowing edge and cracks before the fog. The
  level scene draws the lava in the ground's glow layer with its own material
  (`referenceMeshToUseItsOwnMaterial`), the terrain chunks there too, black, so hills hide it
  (`SceneryStage.lava`, `watchTerrain`). Only a look.
- Phase 10: plumes (`PropGeometry.plumes`, kinds in `config/plumes.ts`): smoke and steam
  columns rising from a prop, one mesh of camera-facing puffs per prop kind and plume kind,
  drawn with the prop's own thin instances (`plume-layer.ts`, `plume-material.visual.ts`), lit by
  the atmosphere (`plumeLight`). `PropLine.drift` moves a line's pieces to and fro (ore wagons).
- Phase 10: `SceneryLook.shotStyle` names a style the game's enemy shot renderer draws the
  level's shots in (`EnemyBindings.shots(scene, style)`; World 4: dark rims and white cores).
- Scenery tools added for the jungle (phase 9): prop lines over water (`PropLine.overWater`) and
  set pieces at given places (`PropRules.landmarks`: a dam, waterfalls, a temple), placed before
  everything else, which keeps clear of them (`placeLandmark`).
- Scenery tools added for the frozen lands: frozen lakes and crevasses in the height field
  (`core/scenery/ice-sculpt.ts`), props floating on the sea and lines of props such as a
  pipeline (`core/scenery/float-placement.ts`), drifting props (`PropField.drift`), crack lines
  in generated textures.

## Enemies with moving parts (P05-R13 to P05-R24)

- `core/entities/jointed-enemy.ts`: `JointedEnemy` (an `Enemy` whose `update` swings its joints,
  runs the kind's `act`, then places its parts) and `EnemyPart` (a hit circle with health and
  guns, on a `BossJointSpec` joint or orbiting with the enemy's `spin`; `shields` keeps shots off
  the hull). Destroyed parts go through `EnemyContext.breakPart` (blast, no bonus); the hull's
  death takes the parts with it. `swinging = false` holds the joints still.
- `EnemyLaserSpec.sweeps`: a beam that keeps turning with its owner while it fires (a laser on a
  moving arm); other beams keep the heading they fired at (phase 8 review).
- Game: the first eleven kinds are `FIRST_KINDS`, the veteran and elite kinds
  `game/sim/veteran-kinds.ts` and `elite-kinds.ts` (configs in `game/config/enemies-veteran.ts`
  and `enemies-elite.ts`); their models use `game/view/enemies/jointed-model.ts`
  (`buildJointedModel`: a node per joint, a ring for the spin, a sub-model per part, hidden once
  destroyed). The `enemies/` wireframe draws every hit target's circle.

## Bosses (phase 07)

```
core/systems/LevelRun ─progress─▶ BossFights ─(LevelBoss kind id)─▶ BossKindDefinition.spawn ─▶ EnemyWorld
                       ScrollTrack: held during a fight (progress waits, ground goes on), speed factor eased
Boss (core/entities/boss.ts) extends Enemy: hitTargets = intact BossParts + BossCore (shielded proxy)
  entering ─in place─▶ fighting (stage k = k parts destroyed, BossPattern per stage) ─core 0─▶ dying ─▶ destroyed
```

- `core/entities/boss.ts`: the abstract `Boss` (an `Enemy` that does not expire, takes no ramming
  damage and may have its own drop chance). Its `BossPart`s and its `BossCore` are the shot
  targets: their `health` setters ignore damage while the boss comes in, and the core's while a
  shielding part stands. Each destroyed part raises `stage`, pauses its fire (`stagePause`) and
  calls `onStageChange`; at 0 core health it blows up over `death.seconds` (`EnemyContext.explode`)
  before the enemy world removes it as destroyed. Parts may orbit its centre (`spin`). Concrete
  bosses implement `enter`, `move` and `updatePattern`.
- `core/entities/muzzle.ts`, `core/systems/gun-muzzles.ts` (phase 7 review, D-057): shots leave
  from a gun's muzzles (offsets from the enemy's centre as seen facing down, and a height), the one
  furthest along each shot's way, turned with the enemy's heading, a boss's `roll` and its ring's
  `spin`, then projected onto the playfield along the camera's line of sight
  (`EnemyContext.seen`, from the `PlayfieldEye` the app gets from `playfieldEye(screen, framing)`).
  The game's muzzles are the barrel tips its models mark (`EnemyParts.muzzle`). A boss piece's
  guns may be on a turret (`core/entities/boss-turret.ts`, D-058): its muzzles turn with its
  `aim` around its pivot, and `BossPattern.turnTurrets` turns it the way its next volley goes
  (D-060: at the player for aimed shots and bursts, along a fan's heading, spinning with a
  spiral ring); its model is drawn on its own node, turned by `aim`. A boss may also have
  moving limbs (`core/entities/boss-joint.ts`, D-061): joints that swing to and fro around their
  pivots, each hanging on another or on the body; a part on a joint (`BossPartSpec.joint`) moves
  with it, its hit circle and muzzles too.
- `core/systems/boss-pattern.ts`: a stage's volleys (aimed fans, preset fans, rings / spirals,
  bursts, homing missiles, lasers with their warning, launches), each from a part (it stops with
  that part) or the core; `patternSignature` names what still fires. After the pause that follows
  each destroyed part, a boss with `rageSeconds` is angry that long (`Boss.rage`, D-063): it fires
  its angry pattern (`Boss.updateRage`; the game's bullet hells are in
  `game/config/bosses/boss-rage.ts`) instead of its stage's. `BossPart` and `BossCore` are in
  `core/entities/boss-pieces.ts`.
- `core/systems/boss-fights.ts`: brings the level's bosses (`GameLevel.bosses`, by distance) in,
  holds the track and eases its speed to the boss's `groundSpeed`, builds the health bar data
  (`BossBar`), and records the bosses defeated. `LevelRun` starts no wave during a fight, ends a
  level with a final boss when that boss is destroyed, saves a `LevelCheckpoint` (progress,
  bosses passed, `RunArsenal` weapons) when the mini boss is destroyed, and can start from one.
- Destroyed parts go to `EnemyWorld.brokenParts`, which the bonus world drops from with each
  part's own `dropChance`.
- Presentation: boss models are enemy models (`GameView.enemies.models`); the game builds them
  with `game/view/bosses/boss-model.ts` (a node per part, a white flash on hits, smoke under half
  health, a stump once destroyed; `boss-limbs.ts` puts a node per joint, turned by its angle,
  carrying the parts and the limbs drawn on it). The HUD's `ui/boss-bar.ts` shows the bar; after the mini boss
  the "Game over" panel offers Continue (`MenuFlow` `attempt` / `resume`, `GameSession` starts the
  level again from the checkpoint). `GameLevel.runout` draws extra ground past the level's end
  (`withRunout`). `?level=…&boss=mini|final` starts at a boss; K destroys a part (debug only).

## Score, lives and bombs (phase 11)

```
EnemyWorld.score ◀── destroyed enemies (points) + broken boss parts (BossStats.partPoints)
LevelRun.score  ◀── + bonus points at the most (BonusRules.overflowPoints)  ─▶ checkpoint.score
LevelControls.bomb ─▶ PlayerBombs.fire ─▶ damageTarget(every on-screen shot target)
                                       └▶ EnemyShots.clear() while active; no hit lands
BonusWorld.drop(targets, special) ─▶ Bonus { kind: weapon | life | bomb } ─▶ LevelRun #collect
GameSession.end / MenuController.completeLevel ─▶ recordScore ─▶ high score cookie
```

- `core/systems/player-bombs.ts` (`BombRules`, `PlayerBombs`): bombs left, the one going off,
  top-up after a lost life. `LevelRunOptions.bombs` is optional (no bombs without it).
- `core/systems/bonus-world.ts`: `BonusKind`; `BonusRules.special` gives the life and bomb
  chances, drawn from a random source of their own (`seed + 2`) so the weapon bonuses drop as
  before; `place(kind, at)` drops a given kind (the mini boss's life bonus). `HullRules.maxLives`
  caps the lives.
- `app/`: `MenuController.recordScore` saves a beaten high score (`saveHighScore`), and
  `completeLevel` marks the result `newHighScore`; `GameSession` records the score of a level
  left early and hands the saved high score to `GamePlay` for the HUD (`SessionScores`).
- Presentation: `GameView.bonuses` draws each kind, `GameView.bombs` (optional, `BombRenderer`)
  the shockwave and flash; `GameHud` shows the score, the high score, the bomb icons and the touch
  bomb button (`HudSetup.onBomb`).
- Readability (phase 14): `SceneryLook.tone` dims the props, the haze and the clouds under the
  playfield (the game darkens the ground, water and road colours in its looks); meshes ask for a rim with `setOutline` (`render/outline.ts`) and get one when `GameView.outline`
  is set; `GameView.hitboxMarker` (optional) draws a marker on the ship's hitbox. Colour families
  and contrast maths are pure (`core/math/color.ts`, `core/math/pixel-contrast.ts`).

## Levels (phase 06)

```
input/GameControls (keys, stick, drag, fire) ─┐
                                              ▼
core/systems/LevelRun: ScrollTrack ─distance─▶ WaveRunner ─(kind id, entry)─▶ EnemyKindDefinition.spawn
                       PlayerFlight (bounds)    EnemyWorld (difficulty) ◀─▶ ShotWorld
                       phase: playing ─scroll ends─▶ clearing ─last enemy gone / endWait─▶ complete
app/GamePlay: LevelScene (scenery + playfield layer) ◀─ draws ship, EnemyLayer, shots, blasts
app/GameSession: starts / ends a GamePlay with the game screen; result ─▶ MenuFlow.completeLevel
```

- `GameDefinition.gameLevels`: one `GameLevel` per playable level (`core/content/game-level.ts`):
  its `SceneryLevel`, its `WaveScript` and its `EnemyDifficulty` (bullet speed and fire rate
  factors). Its id is the id of its level select entry.
- `core/systems/wave-runner.ts`: waves start when the scroll passes their distance (GD-40); each
  brings `count` groups of a kind, one every `interval` s, at an entry (side and position). The
  runner knows kinds by id only; kinds read `EnemySpawnArea.entry`. `stop()` at the end of the
  scroll, `skipTo(distance)` for debug seeking.
- `core/systems/level-run.ts`: one play of a level, pure and deterministic; `player-flight.ts`
  moves the ship with a short acceleration inside bounds given by the view (the tilted camera
  shows less of the playfield at the bottom).
- `app/game-play.ts` runs a `LevelRun` at 60 Hz and draws it on `app/level-scene.ts` (the
  scenery stage and the playfield layer, shared with the enemies page). The game screen's
  overlay (`ui/screens/game-screen.ts`) has Back, the level label, a touch fire button, a drag
  area and the "Level complete" panel. URL options (`app/debug-options.ts`,
  `?level=1-3&t=120&ship=heavy`) start a level straight away with the playback keys (F ×4,
  ← / → 10 s) and the FPS / polygons tile.

## Enemies (phase 05)

- `core/entities/enemy.ts`: the abstract `Enemy` (a `ShotTarget` with a model key, points, a
  heading and a `charge` for the visuals) with an `update(ctx, dt)` hook and an optional
  `onDestroyed(ctx)` hook; `EnemyContext` lets it see the player and fire bullets, homing
  missiles and lasers, or spawn other enemies. `EnemyKindDefinition` spawns one group of a kind.
- `core/systems/enemy-motion.ts`: predefined paths (Catmull-Rom, followed by distance), fans of
  headings. `core/systems/enemy-shots.ts`: pooled bullets and missiles (missiles are shot
  targets) and lasers (warning, then firing, following their owner's emitter).
  `core/systems/enemy-world.ts`: steps enemies and shots, scores and removes destroyed enemies
  (with their `onDestroyed` spawns), removes the ones that left, and lists the targets of the
  player's shots (enemies and missiles).
- Presentation: `GameView.enemies` gives an `EnemyModel` factory per model key (nose +Z, in
  logical pixels), an enemy shot renderer and a blast renderer, all drawn in playfield space
  (`ShotFrame` space). `render/enemy-layer.ts` places and reuses the models.
  `render/node-adopter.ts` moves what drawing code creates into another space and rendering
  group: the enemies page uses it to draw the playfield (ships, shots, explosions) on the tilted
  level view, above the clouds, with its own glow layer.

## Districts on a grid of tiles (phase 15)

With `RoadRules.tiles` (`{ size, sidewalk }`), the sections with a street grid are laid on one
grid of square tiles per district (`core/scenery/tile-streets.ts`, pure):

```
District ── tileStreetRuns ──▶ straight streets (Road, kind 'street', width = N tiles)
                                + blocks (whole tiles)
streets ── roadPieces (core/scenery/road-tiles.ts) ──▶ RoadPiece[]: straight / turn / tee /
          cross, N × N tiles, with open sides { size, offset }; adapters where sizes differ
blocks + pieces ── packDistricts (district-packing.ts, tile-packing.ts) ──▶ buildings of
          PropKindRule.tiles (W × D), scale 1, quarter turns, facing a street; PropRules.lots
          where no building fits
pieces ── render/scenery/tile-road-geometry.ts ──▶ sidewalks, kerbs, roadways and lines,
          draped on the ground, in the opaque streets field of `RoadLayers`
```

- Rows (along X) may be wide (`dual.avenues`, `boulevards`: N lanes each way, N tiles); columns
  are one tile. A column sits where the junction piece of every wide row it crosses starts on
  that row's N-tile lattice (`columnFits`), so a row is made of whole N × N pieces. A wide row
  whose ground does not allow it is a one-tile street. Streets cross in districts (no
  T-junction-only rule there); dead ends on screen are removed without building a cut link
  again (`removeDeadEnds(…, keepCut)`).
- Cars keep `CarRules.sidewalk` off each edge of a street. `levelPropKinds` includes the lots.
- Game: `game/config/tile-buildings.ts` (tile size, building groups and their models, lots),
  `game/view/props/tile-*.ts` (models built for any W × D tiles), `road-kit.ts` (the kit and its
  sample layout for `props/`). `?level=…&tiles=1` draws the grid over the districts.

## Generated levels (phase 04)

```
core/scenery/  SceneryLevel (data) ─▶ HeightField ─▶ PropPlacer      ScrollTrack (time ↔ distance)
                                          │              │
render/scenery/  TerrainChunks ◀──────────┘   PropField ◀┘   (thin instances)
                 SceneryStage: camera, sun, sea, cloud layers, chunks + props around the camera
                 SceneryKit: materials / textures / shadows (plain, or *.visual.ts for WebGL)
```

- `core/scenery/scenery-level.ts`: a level is a list of sections, each `seconds` long at the
  level's scroll speed (so the duration is the sum of the seconds). A section is a fractal relief
  (`smooth` or `ridged`, with an optional soft height cap) plus optional operations: `flatten`
  (a plateau band), `channel` (a canyon along a winding line) and `shore` (ground dropping under
  the sea on one side). Optional sea level; prop rules.
- `core/scenery/height-field.ts`: pure, seeded height function of a level; sections blend over
  `transition`. `core/math/noise.ts`: seeded gradient noise (optionally tiling), fBm, ridged noise.
- `core/scenery/road-network.ts`: seeded winding main roads along the level and paths branching
  off them. No road starts or ends on screen: before the sea or steep ground a main road turns
  off the screen sideways, and paths run from their road to beyond the screen edge, widening at
  the junction. Building slots line both sides of the roads.
- `core/scenery/prop-placement.ts`: buildings stand only in the road slots (set back from the
  edge, facing the road), on flat ground above `minHeight`; a low-frequency zone noise picks the
  building group per area (clusters). Dead trees grow on a grid of cells, away from the roads.
  Every slot and cell is decided from a hash, so chunks can be placed independently.
- `render/scenery/road-geometry.ts` / `road-field.ts`: draped, soft-edged ribbon meshes per
  terrain chunk, in two layers (paths drawn before roads, so roads stay on top).
- `render/scenery/playfield-framing.ts`: the camera is tilted `tiltDeg` from straight down and
  placed so the bottom and top of the screen pass through the bottom and top of the logical
  playfield, a plane at `flightAltitude`. One world unit is one logical pixel; X across (0 under
  the playfield middle), Z along the level, Y up.
- `render/scenery/scenery-stage.ts` keeps terrain chunks (`terrain-chunks.ts`, pooled meshes) and
  their props (`prop-field.ts`, one thin-instanced mesh per prop kind plus one for its self-lit
  accents) around the camera, and moves the sea and cloud planes with it.
- `render/scenery/scenery-kit.visual.ts` (needs WebGL, not unit-tested): generated textures
  (`procedural-textures.ts`, pure and tested) blended by altitude and slope in a
  `StandardMaterial` plugin (`terrain-blend-plugin.visual.ts`); a PBR sea with a drifting
  generated normal map; cloud layers as a small shader (`cloud-material.visual.ts`); PCF sun
  shadows. `createPlainSceneryKit` stands in for it in unit tests.
- Props are geometry, not meshes: `PropModelFactory` returns vertex-coloured, flat-shaded
  `ColoredGeometry` built with `render/geometry/solids.ts` (boxes, bodies of revolution, rings).

## Shots (phase 03)

- `core/entities/weapon.ts`: data-only `WeaponDefinition`s. A projectile weapon fires streams
  (offset + angle) per level from the ship's muzzle or centre, with a fire rate, launch speed, constant acceleration up to a cap,
  optional homing on the closest target, and direct or area damage. A beam weapon has a damage
  per second and width per level; above level 1 it goes through a target and continues one
  level lower.
- `core/systems/shot-world.ts`: pure, fixed-step simulation of one ship's shots against
  `ShotTarget`s (circles with health): fires volleys, moves projectiles
  (`projectile-motion.ts`), traces beams (`beam.ts`), applies damage and reports impacts.
  Projectiles are pooled.
- `render/game-view.ts`: `ShotRenderer`s draw one weapon's shots per frame from a `ShotFrame`
  (its projectiles, beam segments and impacts). `render/node-pool.ts` reuses nodes;
  `render/shot-playfield.ts` draws the grid, stream guides and target markers.

## Pause, settings and audio (phase 12)

```
Esc / P / Start / Select / ❚❚ ─▶ MenuAction cancel | pause ─▶ MenuFlow: game ⇄ pause ─▶ settings
page hidden, gamepad lost ─────▶ MenuController.pause()        (PauseMenu, SettingsMenu)
MenuState.paused ─▶ GameSession.paused: the level is kept, GamePlay.frame is not called
MenuState.volumes ─▶ saved-settings (cookies) and GameAudio.setVolumes

             GameAudio (app/) ──── reads MenuState, LevelRun after each step (onStep)
              │      │      └─ LevelCues (audio/): state diffs ─▶ SoundCue ─▶ SfxPlayer ─▶ VoicePool
              │      └─ MusicPlayer: Sequencer (lookahead) ─▶ synth playVoice ─▶ TrackMixer
              │                    (per instrument: track fader, echo send, reverb send)
              ▼
AudioOutput: AudioContext (made on the first gesture) ─▶ music bus (+ reverb), sfx bus ─▶ limiter
```

- Pause (P12-R01..R03): `core/menu/menu-screen.ts` has `pause` and `settings` screens. Escape is
  the `cancel` action (Back in the menus, pause in a level); P, gamepad Start and Select and the
  touch button send `pause`; `back` (Backspace, B) does nothing in a level. While
  `MenuState.paused` (the pause menu, or the settings opened from it), `start-app`'s frame
  ticker draws the level without calling `GamePlay.frame`: its fixed-step clock gets no time, so
  nothing moves and nothing catches up. `GameSession` clears the controls on pause and resume and
  ignores the debug keys. `visibilitychange` (page hidden) and `GameControls.takeDisconnect()`
  (the gamepad last used to play is gone from its slot) call `MenuController.pause()`.
- Settings (P12-R04): `app/settings-menu.ts` (two sliders, 0 … `volume_steps`), saved in cookies
  `<gameId>_music_volume` / `<gameId>_sfx_volume` (`app/saved-settings.ts`, invalid values read
  as the defaults of `config/audio.ts`). The title has a Settings entry; Back returns to where the
  screen was opened from.
- Audio engine (`src/audio/`, game-agnostic): `audio-types.ts` (tone layers, instruments, sound
  designs, tracks of notes), `synth.ts` (oscillators / noise through filters and envelopes),
  `sequencer.ts` (pure note scheduling with loops and seeking), `music-player.ts` (cross-fades,
  fades, jingles, pause at position), `track-mixer.ts` (per-instrument inputs with sends to a
  tempo-synced echo and to the music reverb, faded with the track), `voice-pool.ts` and `sfx-player.ts` (16 voices, priorities,
  30 ms retrigger, panning), `audio-output.ts` (lazy context, buses, limiter, `(step / 10)²`
  volume curve, silent fallback), `level-cues.ts` (cues from the core state: audio never changes
  it). The context is only created during a user gesture (`navigator.userActivation`), so no
  autoplay warning shows; a 25 ms timer (`AppOptions.every`) and every frame schedule 100 ms ahead.
- `app/game-audio.ts` decides the music: the menu theme on the menu screens (kept playing across
  them), the level's track from its start, the boss track while a boss bar shows (back to the
  level track after the mini boss, kept after the final boss), a fade and a jingle when the level
  ends, nothing new while paused; and plays the menu sounds from `MenuController`'s feedback.
- Game content (`src/game/view/audio/`, `GameView.audio: AudioBindings`): `music-styles.ts` (one
  style per world, all darksynth-leaning synthwave (D-099, D-101): outrun drive, cold bells, toms, heaviest;
  tempo range, scales, chords, instruments, drum and bass feels),
  `compose-track.ts` / `compose-parts.ts` / `compose-melody.ts` (a seeded, pure composer: the
  level id's hash picks key, tempo, sections, motifs), `compose-boss.ts` (the boss tracks'
  driving drums with snare rolls, rolling octave bass, 3-3-2 chord stabs and tense progressions;
  the risers into each section, D-100), `instruments.ts`, `jingles.ts`,
  `sound-designs.ts` (one sound per cue; the gun a minigun burst per volley, D-101), `game-audio.ts` (tracks made once, mix levels).
- Test API (P12-R12): `paused`, `leaving`, `volumes`, `music` (track id), `sounds` (last names),
  `audio` (context state); `sendAction('pause' | 'resume')`.

## Menus (phase 01)

```
keyboard ─┐                                   ┌─▶ ui/MenuOverlay (HTML, 480×640 logical)
gamepad  ─┼─▶ input/ ─MenuAction─▶ app/MenuController ─▶ app/MenuFlow (pure state machine)
taps     ─┘   (pointerCommand)            │
                                          └─▶ app/menu-scenes: game backdrop + render/ShipSelectStage
```

- `app/menu-flow.ts`: pure screen state machine `loading → title → ship-select → level-select → game`,
  with Back on each screen (transition table in `core/menu/menu-screen.ts`), and from a completed
  level back to level select, on the next level (phase 06). Input is ignored while a screen fades
  in, and for a moment after the "Level complete" overlay shows.
- `input/`: keyboard (by `KeyboardEvent.code`, so layouts do not matter), gamepads (polled every frame,
  dead zone) and taps all become the same `MenuAction`s (`up`, `down`, `left`, `right`, `confirm`,
  `back`). Bindings and repeat timings are in `config/menu-input.ts`.
- `ui/`: the overlay renders a `MenuView` (built by `app/menu-view-builder.ts`) and turns taps into
  commands. `ui/stage-fit.ts` fits the 480×640 stage (canvas + overlay) in the window.
- 3D: the game provides `GameView.menuBackdrop` (a scene behind every menu screen); the engine draws
  the ship select stage (`render/ship-select-stage.ts`) over it on the ship select screen. Both scenes
  are built and compiled behind the loading screen (`assets/loading-tasks.ts`).
- Persistence: `platform/cookie-storage.ts` behind the `KeyValueStorage` interface; keys are prefixed
  with the game id (`app/saved-choices.ts`).
- e2e builds expose `window.__GAME_TEST__` (`debug/test-api.ts`, ENG-52); `make build` fails if it
  leaks into the production bundle.

## Content contract

`GameDefinition<TView>` (`core/content/`) carries simulation data (e.g. `playerShips`, a
`PlayerShipRoster` from `core/entities/player-ship.ts`, whose first ship is the default choice;
`levels`, a `LevelCatalog`; `playerWeapons`, the `WeaponDefinition`s every ship can fire), the
logical `screen` size, the menu `texts`, and a `view` slot. The view slot's type
is defined by the presentation layers (`render/game-view.ts` → `GameView`) so `core/` never sees
Babylon types. Models are `ModelFactory` functions: `(scene) => TransformNode`, nose towards +Z,
+Y up. Generic geometry helpers live in `render/geometry/` (planform prisms with ear-clipping
triangulation, bodies of revolution along Z).

## Game loop

`app/start-app.ts` runs Babylon's render loop. Each frame, `core/loop/FixedStepClock` turns the real frame time
into a whole number of 1/60 s simulation steps plus an interpolation factor `alpha` for rendering (ENG-100).
After a long stall, the step count is capped and excess time is dropped. The menus then read the frame's
input, update the overlay, and animate and render the menu scenes (frame time capped at 0.1 s). On the game
screen, the level being played (`app/game-play.ts`) runs its own fixed-step clock instead, and only its
scene is rendered; while it is paused (phase 12) its clock is not advanced at all, and its last frame is
drawn again. The audio is scheduled on the audio clock, every frame and on a 25 ms timer.

## Making a new game from this template

1. Delete the contents of `src/game/` (keep the folder structure) and of `tests/unit/game/`.
2. Create `src/game/index.ts` exporting a `GameDefinition` (see `src/core/content/game-definition.ts`).
3. Implement concrete content in `src/game/sim/` by extending the abstract classes in `src/core/entities/`.
4. Add visuals and sounds in `src/game/view/`, tunables in `src/game/config/`, assets under `public/assets/`.
   Declare the player ships in `GameDefinition.playerShips` and one model per ship id in
   `GameDefinition.view.playerShipModels`, the levels in `GameDefinition.levels` (e.g. with
   `buildLevelGrid`), the menu texts in `GameDefinition.texts`, the logical resolution in
   `GameDefinition.screen`, and the 3D scene behind the menus in `GameDefinition.view.menuBackdrop`.
   Declare the player weapons in `GameDefinition.playerWeapons`, one shot renderer per weapon id
   in `GameDefinition.view.playerShotRenderers`, and the ships' size on the playfield in
   `GameDefinition.view.playerShipScale` (logical pixels per model unit).
   Declare the levels with generated ground in `GameDefinition.sceneryLevels` (`SceneryLevel`
   data), and in `GameDefinition.view.scenery` the playfield camera, one `SceneryLook` per
   scenery level id and one `PropModelFactory` per prop kind id.
   Declare the enemies in `GameDefinition.enemyKinds` (classes extending `Enemy`), and in
   `GameDefinition.view.enemies` one `EnemyModelFactory` per model key, the enemy shot and
   blast renderers and the playfield glow.
   Declare the playable levels in `GameDefinition.gameLevels` (`GameLevel`: a scenery level with
   a look in `view.scenery.looks`, a wave script of enemy kind ids, and the difficulty factors),
   one per unlocked entry of `GameDefinition.levels`. Each level starts with the first player
   weapon at level 1.
   Declare the bosses in `GameDefinition.bossKinds` (classes extending `Boss`, with a model per
   model key in `GameDefinition.view.enemies.models`), the fight timings in
   `GameDefinition.bossFights`, and each level's bosses in `GameLevel.bosses` (a mini boss saves
   a checkpoint; a final boss ends the level).
   Declare the bombs in `GameDefinition.bombs` (`BombRules`), the life and bomb bonus chances and
   their points at the most in `GameDefinition.bonuses`, and each boss's `partPoints` in its
   `BossStats`; optionally, a bomb renderer in `GameDefinition.view.bombs`.
   Optionally, give the game music and sounds in `GameDefinition.view.audio` (`AudioBindings`):
   a track per `MusicRequest` (menu, level, boss, jingle), the instruments its notes name, one
   `SoundDesign` per `SoundCue` (see `audio/level-cues.ts`), the large explosion radius and the
   mix. Add the new menu texts (settings, pause menu) to `GameDefinition.texts`.
5. Run `make check`.
