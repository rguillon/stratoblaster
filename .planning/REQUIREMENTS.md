# Requirements: Stratoblaster

**Defined:** 2026-10-27
**Core Value:** A casual-friendly vertical shoot 'em up that feels responsive and holds 60 fps in a plain browser tab: dodge, shoot, collect, across 4 worlds of 5 levels.

## How to read this file

- Brownfield: every requirement below is **Validated** (all 12 phases are Validated in `specs/PROGRESS.md`). Checkboxes are ticked accordingly.
- `specs/` is the single source of truth (human-owned); this file is a derived view built from the ingest in `.planning/intel/`. IDs are verbatim from the specs: `GD-xx` (`specs/02-game-design.md`), `ENG-xx` (`specs/01-engineering.md`), `Pnn-Rxx` (`specs/phases/phase-NN-*.md`). The vision (`specs/00-vision.md`) carries no IDs, so its six statements are numbered `VISION-01..06` here.
- Descriptions follow the decision-adjusted (current) behaviour. Where human-owned spec text is stale against `specs/DECISIONS.md` or a later phase, the decision wins (14 warnings approved in `.planning/INGEST-CONFLICTS.md`); inline notes flag those cases. Do not edit requirement sections of `specs/` from here: they are human-owned.
- No requirement is LOCKED. SHOULD / MAY priorities are marked; everything else is MUST.
- Note for tooling: `Pnn-Rxx`, `GD-controls` and `GD-flow` do not match the `LETTERS-digits` shape that some GSD parsers expect. They are kept verbatim on purpose.

## v1 Requirements

### Vision (project level)

- [x] **VISION-01**: An old-school vertical shoot 'em up with modern graphics, inspired by Call of the Shadows gameplay but with 3D graphics (vision: elevator pitch, genre)
- [x] **VISION-02**: Casual players, accessible to kids; desktop browser first, mobile browser later (keep it in mind technically); World 1 levels about 4 minutes, later levels about 5 minutes
- [x] **VISION-03**: Core loop: avoid enemy bullets / lasers / missiles, shoot and destroy enemies, pick up bonuses (completed by Phase 11)
- [x] **VISION-04**: Pillars: responsive controls; 60 fps on a modest computer
- [x] **VISION-05**: Non-goals: no multiplayer, no backend or server, no user accounts; any persistence is handled by cookies
- [x] **VISION-06**: Definition of done: the first release is 4 worlds of 5 levels each (World 5 dropped, D-089)

### Game design (GD, cross-cutting)

- [x] **GD-01**: Vertical scrolling; ground speed varies per level
- [x] **GD-02**: Logical resolution 480x640, scaled to fit the window
- [x] **GD-03**: Responsive aspect ratio handling
- [x] **GD-controls**: Move with arrows / WASD (by key position, so AZERTY works), left stick, touch drag; shoot with Space, button, touch button; pause with Esc / P, button, touch button; weapon switch on E (D-043); bomb on R / Left Shift, gamepad X and LB, touch BOMB button (P11-R06). The GD section 2 table row giving E to the bomb is stale (superseded by D-043 and P11-R06)
- [x] **GD-10**: Little acceleration, quickly reaching maximum speed (ship feel; D-045)
- [x] **GD-20**: Start with 3 lives, more collectable as dropped bonuses, and a 100 % health bar
- [x] **GD-21**: Small hitbox for the player, visual-equivalent hitboxes for enemies
- [x] **GD-22**: 2 seconds of invincibility after a hit; the ship blinks
- [x] **GD-30**: Three main weapons: guns, laser, missiles
- [x] **GD-31**: Each weapon upgradable to level 5
- [x] **GD-32**: Secondary bombs: one bomb damages every enemy on screen, enough to kill most low-level enemies
- [x] **GD-33**: Weapon balance: guns are the reference; laser and missiles deal 70-100 % of the guns' dps at every level; guns spread widest, laser most focused and piercing, missiles home but take time to arrive (D-059)
- [x] **GD-40**: Enemies spawn (alone or in waves) according to how far the player has advanced
- [x] **GD-41**: Each level has one mini boss and one final boss
- [x] **GD-42**: The mini boss acts as a checkpoint
- [x] **GD-43**: Enemies shoot colourful bullets, missiles the player can shoot, or lasers with a 1 s warning line
- [x] **GD-44**: Enemies shoot in preset directions or aim at the player
- [x] **GD-45**: Each enemy kind has a preset movement: a predefined path or diving at the player
- [x] **GD-46**: Bosses have destructible parts; each destroyed part changes the attack pattern
- [x] **GD-50**: Killing an enemy gives points according to its difficulty
- [x] **GD-51**: High score persistence is based on a cookie
- [x] **GD-flow**: Flow Title -> Select Ship -> Select Level -> Game -> (lives = 0) Game Over -> Title; Game <-> Pause (the source marks section 7 as TODO / not finalised)
- [x] **GD-60**: All models generated from code; darksynth style (dark, neon magenta, violet and blood red, sunset gradients, chrome; was cyberpunk/synthwave, D-103)
- [x] **GD-61**: Player ship shiny grey/blue; enemies dark metallic with neon lights
- [x] **GD-62**: Particle effect on every projectile hit on a ship; explosions when a ship is destroyed
- [x] **GD-70**: Music is code-generated; one music per level and a more stressful one for boss fights
- [x] **GD-71**: Sound effects are software-generated

### Phase 1: Main Menu

- [x] **P01-R01**: Pure screen state machine in `app/` (loading, title, ship-select, level-select, game, Back per menu screen); invalid transitions rejected. In-game Esc/Back to title is superseded by P12-R01
- [x] **P01-R02**: Loading screen with a real progress bar that switches to the title automatically
- [x] **P01-R03**: Clear friendly message and no errors when WebGL2 is unavailable
- [x] **P01-R04**: Title screen: game title from `src/game/`, Start selected by default, high score from the cookie (0 if none or corrupted), version and short commit hash, controls hint
- [x] **P01-R05** (SHOULD): Code-generated animated 3D darksynth background (night city, neon, crimson sunset haze) with the balanced ship flying slowly; 60 FPS. Sun emblem removed (D-103; the pilot model of D-104 was reverted)
- [x] **P01-R06**: Ship select shows the three rotating ships with name, speed, health; Left/Right wraps; Confirm stores the ship; balanced by default; highlighted ship clear, others dimmed
- [x] **P01-R07**: Level select grid of 4 worlds x 5 levels (20 entries, 1-1 to 4-5), data from `src/game/`; all unlocked (the phase-1 "only 1-1 unlocked" state was superseded by P06-R01 and D-089)
- [x] **P01-R08**: Placeholder game screen showing the chosen ship and level (replaced by P06-R02)
- [x] **P01-R09**: Keyboard menu navigation by physical key position (arrows/WASD, Enter/Space confirm, Esc/Backspace back), held direction repeats after a delay
- [x] **P01-R10**: Gamepad menu navigation (stick/D-pad, A confirm, B back, dead zone 0.35)
- [x] **P01-R11**: Touch/mouse: every entry tappable, visible Back button on non-title screens, targets at least 44x44 CSS px
- [x] **P01-R12**: `input/` translates keyboard, gamepad and touch into abstract menu actions (up/down/left/right/confirm/back), mapping in config
- [x] **P01-R13**: HTML/CSS overlay on the 480x640 logical resolution scaled to fit; darksynth look (D-103; the "striped sun" wording is stale); selection obvious without colour; fits 800x600, 1920x1080, 390x844
- [x] **P01-R14** (MAY): Last chosen ship saved in a cookie and pre-selected next time
- [x] **P01-R15** (MAY): Short transitions (at most 300 ms) with input ignored during a transition

### Phase 2: Player Ships

- [x] **P02-R01**: Balanced ship: speed factor 1, 100 HP; VF-31J-inspired design (dual reactor, wings going forward). Base speed is 225 px/s per D-047 (the Goal text saying 100 px/s is stale)
- [x] **P02-R02**: Heavy ship: speed factor 0.8, 140 HP; modern flying-wing bomber design
- [x] **P02-R03**: Light ship: speed factor 1.4, 80 HP; four wings each with an attached reactor

### Phase 3: Player Shots

- [x] **P03-R01**: Bullet: minigun tracer, levels 1-5 (single, dual, single + 2 diagonals, dual + 2 diagonals, single + 4 diagonals), 10 damage, 8 shots/s
- [x] **P03-R02**: Laser: bright blue with particle flow, 80/140/200/260/320 dps at levels 1-5 (GD-33), pierces a ship and continues one level lower
- [x] **P03-R03**: Missile: constant acceleration with reactor flame, targets the closest enemy within about 320 px, 14 damage, 4 per second per stream, level layouts 1-5
- [x] **P03-R10**: `player_shots/` debug page showing each ship's shots
- [x] **P03-R11**: Multi-stream levels fire their streams one after the other, evenly spaced, with unchanged overall rate (D-102)

### Phase 4: Level Zero

- [x] **P04-R01**: Software-sculpted heightmap terrain with generated textures fading by slope or altitude
- [x] **P04-R02**: Optional sea level reflecting the sun, with natural shore (beach, depth-darkening shallows, broken surf)
- [x] **P04-R03**: Optional cloud layers with adjustable intensity and opacity (always above the terrain)
- [x] **P04-R04**: Flat areas populated with props (industrial buildings, technical items, futuristic homes, dead trees)
- [x] **P04-R05**: Camera on top pointing down, tilted 35 degrees to the back (the source writes "35%")
- [x] **P04-R06**: Level Zero lasts around 3 minutes
- [x] **P04-R07**: Randomly generated roads and paths; building props only along them

### Phase 5: First Enemies

- [x] **P05-R01**: Gnat: swarm drone, groups of 5 on the same S-shaped path, no shooting
- [x] **P05-R02**: Hornet: diver that pauses 0.5 s then dives at the recorded player position
- [x] **P05-R03**: Scout: flies straight down, one aimed bullet every 1.5 s
- [x] **P05-R04**: Strafer: crosses the top third, fan of 3 bullets (-15, 0, +15 degrees) every second
- [x] **P05-R05**: Weaver: sine-wave flyer, aimed bullet pair every 2 s
- [x] **P05-R06**: Spinner: spiral turret firing a spiral from four pods for 3 s
- [x] **P05-R07**: Lancer: stops, 1 s warning line then a 1.5 s laser
- [x] **P05-R08**: Rocketeer: two missile pods, missiles that turn toward the player and can be shot down
- [x] **P05-R09**: Bulwark: heavy gunship firing an aimed 5-bullet spread every 2 s
- [x] **P05-R10**: Splitter: curved path, aimed bullets, three pods that dive on death
- [x] **P05-R11**: `enemies/` debug page: pick a kind, model view, wireframe view with hit circles, shootable invulnerable ship, hit particles and explosions
- [x] **P05-R12**: Carrier: launches a Gnat from each side port every 3 s, never shoots
- [x] **P05-R13**: Moving parts engine feature: parts on swinging or orbiting joints with own hit circle, health, weapon and muzzles; destroyed parts score and drop nothing
- [x] **P05-R14**: Wasp (veteran): groups of 3, 3-bullet fan then dive
- [x] **P05-R15**: Mortar (veteran): slow shell that bursts into 8 bullets
- [x] **P05-R16**: Mantis (veteran): two swinging scythe arms firing bullet pairs
- [x] **P05-R17**: Phantom (veteran): fades out, reappears elsewhere and fires a 5-bullet spread, three times
- [x] **P05-R18**: Minelayer (veteran): crosses horizontally dropping mines that burst into 6 bullets
- [x] **P05-R19**: Hydra (elite): three swaying heads firing in turn
- [x] **P05-R20**: Orbiter (elite): core with three armoured orbiting drones and a ring shot
- [x] **P05-R21**: Scissor (elite): two sweeping laser arms with 1 s warning lines
- [x] **P05-R22**: Juggernaut (elite): two armour plates and two swinging shoulder cannons
- [x] **P05-R23**: Hive (elite): launches a Wasp every 4 s and fires every 3 s
- [x] **P05-R24**: 21 kinds in the game: veteran kinds in World 3 and World 4 waves, elites in World 4 only, Worlds 1-2 unchanged; difficulty rules P09-R08 and P10-R10 still hold (D-090)

### Phase 6: World 1

- [x] **P06-R01**: World 1 row 1-1 to 1-5 all unlocked; levels never locked by progress
- [x] **P06-R02**: Game screen plays the chosen level: scrolling scenery, ship with the game controls inside the playfield, shooting, wave-scripted enemies, hit particles and explosions. Superseded in part: weapon levels carry across completed levels (D-071) instead of restarting at guns level 1; Esc no longer leaves (P12-R01)
- [x] **P06-R03**: Level end with a "Level complete" overlay and next level highlighted; for all worlds the level now ends when the final boss is destroyed (P07-R06)
- [x] **P06-R04**: Each World 1 level lasts 240 s +/- 10 s
- [x] **P06-R05**: One journey sea -> green grass -> desert across 1-1 Open sea, 1-2 Green coast, 1-3 Green country, 1-4 Dry lands, 1-5 Deep desert, with props rising per level (D-109)
- [x] **P06-R06**: New generated ground and props: sand and dunes, grass, dry bushes, palms, cacti, futuristic desert homes and outposts, farms
- [x] **P06-R07**: Per-level deterministic wave scripts triggered by scrolled distance, kinds introduced level by level
- [x] **P06-R08**: Difficulty rises 1-1 to 1-5 (enemy count, total HP, peak on screen strictly up; speed and rate factors never down; second half heavier). The enemy-count and peak tunables are stale (D-044, D-051)
- [x] **P06-R09**: Debug URL options (`?level=`, `t=`, F fast-forward, 10 s jumps), ignored without debug options
- [x] **P06-R10**: Fixed time of day per level, from midday (1-1) to dusk with town lights (1-5)

### Phase 7: Bosses

- [x] **P07-R01**: Boss engine: core plus destroyable parts with HP and hit circles, shielding parts, damage feedback; mini bosses 2-3 parts, final bosses 4-6
- [x] **P07-R02**: Boss health bar as a slim vertical gauge on the left edge (D-105), name, part notches
- [x] **P07-R03**: Ground speed eases over 2 s to each boss's fight factor and back; scenery never runs out; no wave skipped
- [x] **P07-R04**: Stages: each destroyed part changes the attack pattern; destroyed parts stop firing; 1 s pause on stage change; last stage unique
- [x] **P07-R05**: Ten World 1 bosses (Reef Warden / Storm Petrel to Sentinel / Overlord), staying within x 107-373, no damage until in place
- [x] **P07-R06**: Mini boss at mid-level, final boss at level end, no waves while a boss lives; the level ends when the final boss is destroyed
- [x] **P07-R07**: Destroyed parts may drop weapon bonuses, final core always drops one, deterministic from the level seed
- [x] **P07-R08**: Mini boss checkpoint; after game over Continue (full lives, saved weapons) or Level select
- [x] **P07-R09**: `bosses/` debug page and `boss=mini|final` / K debug options
- [x] **P07-R10**: Boss difficulty: HP strictly up 1-1 to 1-5, final above mini

### Phase 8: World 2

- [x] **P08-R01**: World 2 row 2-1 to 2-5 unlocked; finishing 1-5 highlights 2-1
- [x] **P08-R02**: Each level 300 s +/- 10 s
- [x] **P08-R03**: Industrial Desert journey: 2-1 Great erg, 2-2 Mining mesas, 2-3 Oil fields, 2-4 Industrial belt, 2-5 Factory district; no sea, slow transitions (D-110)
- [x] **P08-R04**: Engine atmosphere: time of day, cloud cover and colour, haze, ground lights, smooth look change along the level
- [x] **P08-R05**: Weather engine with kind and strength 0-1 that never changes the simulation; snow is the first kind (no level uses it since D-110; the "2-4 blizzard" acceptance is historical)
- [x] **P08-R06**: Looks: 2-1 morning, 2-2 midday, 2-3 afternoon, 2-4 dusk (smog), 2-5 night (smog); no weather
- [x] **P08-R07**: Ground is World 1 desert covered by paved industrial concrete; new oil pumpjack prop
- [x] **P08-R08**: Wave scripts with fillers; 2-1 leads with five kinds, 2-2 adds Splitter and Lancer, 2-3 to 2-5 all base kinds (read with P05-R24)
- [x] **P08-R09**: Difficulty strictly up 2-1 to 2-5; 2-1 at least 1-3 and 2-5 above 1-5
- [x] **P08-R10**: Ten World 2 bosses (Floe Breaker / Narwhal to Ice Queen / Boreal Citadel)
- [x] **P08-R11**: Boss difficulty: HP strictly up, final above mini, each above the World 1 boss of the same level and kind
- [x] **P08-R12**: Debug options accept World 2 levels plus `weather=0` and `look=`; `bosses/` lists World 2 bosses

### Phase 9: World 3

- [x] **P09-R01**: World 3 row 3-1 to 3-5 unlocked; finishing 2-5 highlights 3-1
- [x] **P09-R02**: Each level 300 s +/- 10 s
- [x] **P09-R03**: Journey from the factories to garden villages of small houses; canals, rivers and ponds, no sea, no skyscraper; slow transitions (D-111)
- [x] **P09-R04**: Looks: 3-1 morning mist, 3-2 midday rain, 3-3 afternoon thunderstorm, 3-4 dusk rain, 3-5 night rain
- [x] **P09-R05**: Rain and lightning weather kinds, at most 3 flashes in any second, seeded, never changing the simulation
- [x] **P09-R06**: Ground and props: concrete giving way to grass, damp earth, canal stone, asphalt roads, small homes
- [x] **P09-R07**: Wave scripts with fillers; 3-1 leads with six kinds, 3-2 to 3-5 all base kinds (read with P05-R24: veteran kinds appear)
- [x] **P09-R08**: Difficulty strictly up 3-1 to 3-5; 3-1 at least 2-3 and 3-5 above 2-5
- [x] **P09-R09**: Ten World 3 bosses (Mangrove Croc / River Leviathan to Jaguar / Verdant Crown)
- [x] **P09-R10**: Boss difficulty above the World 2 boss of the same level and kind
- [x] **P09-R11**: Debug options accept World 3 levels with `weather=0` and `look=`; `bosses/` lists World 3 bosses

### Phase 10: World 4

- [x] **P10-R01**: World 4 row 4-1 to 4-5 unlocked as the last row (World 5 dropped, D-089)
- [x] **P10-R02**: Each level 300 s +/- 10 s
- [x] **P10-R03**: Metropolis journey from houses to downtown skyscrapers; no sea, no lava; slow 900-unit transitions (D-112)
- [x] **P10-R04**: Per-level looks (time of day, clouds, weather) kept after the rework
- [x] **P10-R05**: Lava as a liquid-ground engine feature; no World 4 level uses it since D-112 (feature and tests kept)
- [x] **P10-R06**: Falling ash and rising embers weather kinds, usable together
- [x] **P10-R07**: World 4 enemy bullets get a light contrasting outline or core for readability
- [x] **P10-R08**: Ground and props: more concrete, stone quays, river water, houses, flats, towers and a new family of 8 skyscrapers
- [x] **P10-R09**: Wave scripts with fillers using all base kinds from 4-1 (read with P05-R24: veterans and elites appear)
- [x] **P10-R10**: Difficulty strictly up 4-1 to 4-5; 4-1 at least 3-3 and 4-5 above 3-5; beatable by a casual player
- [x] **P10-R11**: Ten World 4 bosses (Cinder Crab / Steam Dreadnought to Ember Herald / Caldera Throne, the last boss of the game)
- [x] **P10-R12**: Boss difficulty above the World 3 boss of the same level and kind; Caldera Throne the hardest and still beatable
- [x] **P10-R13**: Debug options accept World 4 levels with `weather=0` and `look=`; `bosses/` lists World 4 bosses (the "magma lake" / "eruption look" acceptance text is historical)

### Phase 11: Score, Lives and Bombs

- [x] **P11-R01**: Per-attempt score from 0; destroyed enemies add their kind's points; boss part scores 10 % of boss points, core scores the boss points
- [x] **P11-R02**: HUD shows a 7-digit score top-centre and a HI line (larger of saved and current)
- [x] **P11-R03**: A higher score is saved to the high score cookie when an attempt ends; panels show the score and "New high score!"
- [x] **P11-R04**: The checkpoint also saves the score; Continue restarts with it and the starting bombs
- [x] **P11-R05**: Bombs: 3 at start, 1 s effect with shockwave and flash, 100 damage once to every on-screen enemy and boss part, clears enemy fire, player invincible
- [x] **P11-R06**: Bomb controls: R and Left Shift, gamepad X and LB, touch BOMB button; E keeps switching weapon
- [x] **P11-R07**: Life and bomb bonuses (1 % and 3 % drop chance), mini boss core always drops a life, maxima convert to 5,000 / 2,000 points
- [x] **P11-R08**: e2e test API also returns score, high score, bombs and bonuses with kind; `sendAction('bomb')` fires a bomb

### Phase 12: Pause, Music and Settings

- [x] **P12-R01**: Pause via Escape, P, gamepad Start/Select, touch pause button; resume is exact; Backspace and gamepad B do nothing in the game
- [x] **P12-R02**: Pause menu: Resume, Settings, Main menu with a "Leave the level?" confirmation
- [x] **P12-R03**: Automatic pause when the page is hidden or the gamepad in use disconnects; never resumes by itself
- [x] **P12-R04**: Settings screen (from title and pause) with Music and Sound effects sliders 0-10 saved in cookies
- [x] **P12-R05**: Web Audio engine generating all music and effects in code (no audio files; ENG-120 audio formats do not apply)
- [x] **P12-R06**: Every level 1-1 to 4-5 has its own generated music; per-world darksynth styles and tempo ranges. The World 2-4 theme names in the text are stale (D-110..D-112)
- [x] **P12-R07**: Boss fights cross-fade to a faster, stressful world boss track plus jingles
- [x] **P12-R08**: One looping menu theme across title, ship select, level select and settings from title
- [x] **P12-R09**: Every game event plays its own generated sound, told apart (minigun rattle for the gun)
- [x] **P12-R10**: At most 16 simultaneous sounds with priority replacement
- [x] **P12-R11**: Audio follows pause and page visibility
- [x] **P12-R12**: e2e test API also gives paused, screen, volumes, music track id, last sounds; `sendAction` accepts pause and resume

### Engineering constraints (ENG, cross-cutting; full text in `specs/01-engineering.md`)

All MUST unless marked. The gate `make check` (lint, typecheck, unit tests, coverage thresholds, build, e2e) enforces the testable ones at each phase validation. SHOULD and MAY items have not been individually re-audited by this roadmap.

- [x] **ENG-01..ENG-09** Tech stack: TypeScript strict, Babylon.js (deep imports), Vite, Node 24 LTS + npm, minimal runtime dependencies, last 2 versions of desktop Chrome/Edge/Firefox/Safari with WebGL2, no backend, custom collision (no physics engine); ENG-08 (WebGPU) is MAY. ENG-07 says localStorage but cookies are used (D-010; ENG-07 text is stale)
- [x] **ENG-10, ENG-11** Directory layout and layering enforced by lint (`core/` pure, no Babylon or DOM)
- [x] **ENG-12..ENG-19** Lint and style: ESLint (D-019: ESLint 10 with eslint-plugin-import-x, ENG-12 text is stale), Prettier, tsc zero errors, naming rules, no magic numbers (tunables in `src/config/` and `src/game/config/`), deterministic simulation; ENG-16 and ENG-19 are SHOULD
- [x] **ENG-20..ENG-36** Makefile is the single entry point (`help`, `install`, `dev`, `build`, `lint`, `format`, `typecheck`, `test`, `coverage`, `e2e`, `check-fast`, `check`); ENG-33, ENG-34 SHOULD; ENG-35, ENG-36 MAY. CLAUDE.md governs when each gate runs (light verification at implement/fix, full `make check` at validation); ENG-32's "before every report" wording is stale
- [x] **ENG-40..ENG-48** Vitest with coverage-v8, test-driven, each requirement ID in a test name, thresholds (`src/core/**` 90 % lines / 85 % branches / 90 % functions / 90 % statements; whole `src/` 70 % lines), coverage never decreases, deterministic tests; ENG-47, ENG-48 SHOULD
- [x] **ENG-50..ENG-57** Playwright Chromium against the built e2e app, `window.__GAME_TEST__` test API absent from production, tests fail on console errors, smoke suite; ENG-55 SHOULD, ENG-56 MAY
- [x] **ENG-60, ENG-61, ENG-63, ENG-64, ENG-65** Husky hooks (pre-commit lint-staged + typecheck, pre-push `make check-fast`), never bypass hooks; ENG-65 SHOULD. ENG-62 was removed (no commit-msg hook)
- [x] **ENG-70..ENG-79** CI (GitHub Actions): `check` and `e2e` jobs, artefacts, Dependabot; ENG-76, ENG-77 SHOULD; ENG-78, ENG-79 MAY. See the CI e2e observation in `STATE.md`
- [x] **ENG-80..ENG-85** GitHub Pages deploy after CI on main, sub-path safe (Vite `base: './'`, D-003), version + commit hash on the title; ENG-84 SHOULD; ENG-85 MAY (PR previews: no)
- [x] **ENG-90..ENG-94** Conventional Commits, one branch `phase-NN` per phase, squash-merge and tag `v0.NN.0` on validation; ENG-94 SHOULD
- [x] **ENG-100, ENG-101, ENG-103..ENG-112** Fixed 60 Hz step, 60 FPS at 1080p on a mid-range integrated GPU, graphics feature set, thin instances, loading screen, no console errors, resize / auto-pause / context-loss handling; ENG-106, ENG-107, ENG-111, ENG-112 SHOULD. There is no ENG-102 (quality presets removed, D-095); ENG-103 and ENG-106 still mention High/Medium presets (stale). ENG-112 was only scheduled for music and SFX sliders
- [x] **ENG-120..ENG-125** Asset formats and licensing (procedural, CC0, CC-BY, `CREDITS.md`, typed manifest, MIT); the OGG/MP3 audio part does not apply to generated audio (P12-R05); ENG-124 SHOULD
- [x] **ENG-130..ENG-133** README with live link, `docs/architecture.md`, TSDoc on public `core/` API, `CREDITS.md`; ENG-132 SHOULD
- [x] **ENG-140..ENG-148** Engine / game split: code outside `src/game/` is game-agnostic, concrete content in `src/game/`, one `GameDefinition` entry point, lint-enforced direction; ENG-148 SHOULD

## v2 Requirements

None defined. The next phase is undefined and will be created by the human with `/new-phase`; its requirements will be human-written in `specs/phases/`.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature                                               | Reason                                                                                                |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Multiplayer                                           | Vision non-goal                                                                                       |
| Backend, server, user accounts                        | Vision non-goal; persistence is cookies only (D-010)                                                  |
| World 5 (a fifth world of levels)                     | Dropped by the reviewer 2026-10-26 (D-089); the grid is 4 x 5 and the Caldera Throne is the last boss |
| Quality presets / graphics settings                   | ENG-102 removed (D-095); budgets apply to the single configuration                                    |
| Master volume, key remapping                          | Not scheduled; only Music and SFX sliders were specified (D-095)                                      |
| Score carried across levels, name entry, leaderboards | Out of scope in the phase 11 spec; score is per level attempt with a single saved high score          |
| Level locking by progress                             | Levels are never locked (P06-R01, D-089); the engine keeps locked-level support for other games       |
| Downloaded audio or model assets                      | Everything is generated in code (GD-60, GD-70, GD-71, D-097)                                          |

## Traceability

Every requirement maps to exactly one phase, or is cross-cutting (validated across the whole build and enforced by the gate). Status is Complete for all: all 12 phases are Validated.

| Requirement                                     | Phase         | Status   | Delivered mainly in                                                      |
| ----------------------------------------------- | ------------- | -------- | ------------------------------------------------------------------------ |
| P01-R01 .. P01-R15 (15)                         | Phase 1       | Complete | -                                                                        |
| P02-R01 .. P02-R03 (3)                          | Phase 2       | Complete | -                                                                        |
| P03-R01, P03-R02, P03-R03, P03-R10, P03-R11 (5) | Phase 3       | Complete | -                                                                        |
| P04-R01 .. P04-R07 (7)                          | Phase 4       | Complete | -                                                                        |
| P05-R01 .. P05-R24 (24)                         | Phase 5       | Complete | -                                                                        |
| P06-R01 .. P06-R10 (10)                         | Phase 6       | Complete | Post-validation rework D-109 awaiting the reviewer's check               |
| P07-R01 .. P07-R10 (10)                         | Phase 7       | Complete | -                                                                        |
| P08-R01 .. P08-R12 (12)                         | Phase 8       | Complete | Post-validation rework D-110 awaiting the reviewer's check               |
| P09-R01 .. P09-R11 (11)                         | Phase 9       | Complete | Post-validation rework D-111 awaiting the reviewer's check               |
| P10-R01 .. P10-R13 (13)                         | Phase 10      | Complete | Post-validation rework D-112 awaiting the reviewer's check               |
| P11-R01 .. P11-R08 (8)                          | Phase 11      | Complete | -                                                                        |
| P12-R01 .. P12-R12 (12)                         | Phase 12      | Complete | -                                                                        |
| VISION-01                                       | Cross-cutting | Complete | Phases 5-10 (genre, content)                                             |
| VISION-02                                       | Cross-cutting | Complete | Phases 1, 6-10 (touch menus, level lengths)                              |
| VISION-03                                       | Cross-cutting | Complete | Phase 11 completes the core loop                                         |
| VISION-04                                       | Cross-cutting | Complete | All phases; 60 FPS on reference hardware never measured (see `STATE.md`) |
| VISION-05                                       | Cross-cutting | Complete | Phases 1, 11, 12 (cookies)                                               |
| VISION-06                                       | Cross-cutting | Complete | Phases 6-10 (4 worlds x 5 levels)                                        |
| GD-01                                           | Cross-cutting | Complete | Phases 4, 6                                                              |
| GD-02                                           | Cross-cutting | Complete | Phase 1 (P01-R13)                                                        |
| GD-03                                           | Cross-cutting | Complete | Phase 1 (P01-R13)                                                        |
| GD-controls                                     | Cross-cutting | Complete | Phases 1, 6, 11, 12                                                      |
| GD-10                                           | Cross-cutting | Complete | Phase 6 (D-045)                                                          |
| GD-20                                           | Cross-cutting | Complete | Phases 6, 11 (D-050, P11-R07)                                            |
| GD-21                                           | Cross-cutting | Complete | Phase 6 (D-050)                                                          |
| GD-22                                           | Cross-cutting | Complete | Phase 6 (D-050)                                                          |
| GD-30                                           | Cross-cutting | Complete | Phase 3                                                                  |
| GD-31                                           | Cross-cutting | Complete | Phase 3                                                                  |
| GD-32                                           | Cross-cutting | Complete | Phase 11 (P11-R05)                                                       |
| GD-33                                           | Cross-cutting | Complete | Phase 3 (D-059)                                                          |
| GD-40                                           | Cross-cutting | Complete | Phase 6 (P06-R07)                                                        |
| GD-41                                           | Cross-cutting | Complete | Phase 7                                                                  |
| GD-42                                           | Cross-cutting | Complete | Phase 7 (P07-R08)                                                        |
| GD-43                                           | Cross-cutting | Complete | Phase 5                                                                  |
| GD-44                                           | Cross-cutting | Complete | Phase 5                                                                  |
| GD-45                                           | Cross-cutting | Complete | Phase 5                                                                  |
| GD-46                                           | Cross-cutting | Complete | Phase 7 (P07-R01, P07-R04)                                               |
| GD-50                                           | Cross-cutting | Complete | Phase 11 (P11-R01)                                                       |
| GD-51                                           | Cross-cutting | Complete | Phase 11 (P11-R03)                                                       |
| GD-flow                                         | Cross-cutting | Complete | Phases 1, 12                                                             |
| GD-60                                           | Cross-cutting | Complete | All phases (D-103 darksynth look)                                        |
| GD-61                                           | Cross-cutting | Complete | Phases 2, 5                                                              |
| GD-62                                           | Cross-cutting | Complete | Phases 3, 5                                                              |
| GD-70                                           | Cross-cutting | Complete | Phase 12                                                                 |
| GD-71                                           | Cross-cutting | Complete | Phase 12                                                                 |
| ENG-01 .. ENG-09 (9)                            | Cross-cutting | Complete | Gate: `make check`                                                       |
| ENG-10 .. ENG-19 (10)                           | Cross-cutting | Complete | Gate: lint, typecheck                                                    |
| ENG-20 .. ENG-36 (17)                           | Cross-cutting | Complete | Makefile                                                                 |
| ENG-40 .. ENG-48 (9)                            | Cross-cutting | Complete | Gate: unit tests, coverage                                               |
| ENG-50 .. ENG-57 (8)                            | Cross-cutting | Complete | Gate: e2e                                                                |
| ENG-60, ENG-61, ENG-63 .. ENG-65 (5)            | Cross-cutting | Complete | Git hooks (ENG-62 removed)                                               |
| ENG-70 .. ENG-79 (10)                           | Cross-cutting | Complete | CI; see CI e2e observation in `STATE.md`                                 |
| ENG-80 .. ENG-85 (6)                            | Cross-cutting | Complete | Deploy workflow                                                          |
| ENG-90 .. ENG-94 (5)                            | Cross-cutting | Complete | Git workflow                                                             |
| ENG-100, ENG-101, ENG-103 .. ENG-112 (12)       | Cross-cutting | Complete | Rendering and performance (no ENG-102)                                   |
| ENG-120 .. ENG-125 (6)                          | Cross-cutting | Complete | Assets and licensing                                                     |
| ENG-130 .. ENG-133 (4)                          | Cross-cutting | Complete | Documentation                                                            |
| ENG-140 .. ENG-148 (9)                          | Cross-cutting | Complete | Engine / game split                                                      |

**Coverage:**

- v1 requirements: 273 total (6 vision, 27 GD, 130 phase requirements, 110 ENG; ENG-62 is removed and ENG-102 does not exist)
- Mapped to a phase: 130 phase requirements (Phases 1-12)
- Cross-cutting (validated, not phase-bound): 143 (6 vision, 27 GD, 110 ENG)
- Unmapped: 0

---

_Requirements defined: 2026-10-27_
_Last updated: 2026-10-27 after roadmap creation from the ingest of `specs/`_
