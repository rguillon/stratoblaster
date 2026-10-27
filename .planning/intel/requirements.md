# Requirements intel

Sources: `specs/00-vision.md` (PRD), `specs/02-game-design.md` GD-xx and `specs/phases/phase-NN-*.md` Pnn-Rxx (typed SPEC by the manifest; their behaviour requirements are extracted here as requirements, their technical contracts are in `constraints.md`). IDs are verbatim. Priority is MUST unless stated. Phase status for all phases: Validated (see `context.md` and `SYNTHESIS.md`).
Absent field = the source gives none. Competing variants: none found (no two PRDs define the same scope with different acceptance). Stale text in these requirement sections that later decisions override is listed in `/home/renaud/pewet/.planning/INGEST-CONFLICTS.md`, not corrected here.

# Vision (PRD)

## REQ-vision-pitch

- source: specs/00-vision.md
- description: An old school shoot 'em up with modern graphics; vertical scroller inspired by Call of the Shadows gameplay, with 3D graphics.
- acceptance: absent
- scope: genre, graphics

## REQ-vision-audience-platform

- source: specs/00-vision.md
- description: Casual players, accessible to kids. Desktop browser first, mobile browser later (keep it in mind for technical choices). World 1 levels last about 4 minutes, later levels about 5 minutes.
- acceptance: absent
- scope: audience, platform, session length

## REQ-vision-core-loop

- source: specs/00-vision.md
- description: Core loop: 1) avoid enemy bullets/laser/missiles, 2) shoot and destroy enemies, 3) pick up bonuses.
- acceptance: absent
- scope: core loop

## REQ-vision-pillars

- source: specs/00-vision.md
- description: Pillars: responsive controls; 60 fps on a modest computer.
- acceptance: absent
- scope: controls feel, frame rate

## REQ-vision-non-goals

- source: specs/00-vision.md
- description: Out of scope: no multiplayer; no backend/server; no user accounts; any persistence handled by cookies.
- acceptance: absent
- scope: non-goals, persistence

## REQ-vision-definition-of-done

- source: specs/00-vision.md
- description: First release = 4 worlds of 5 levels each (World 5 dropped by the reviewer, 2026-10-26; was 5 worlds).
- acceptance: absent
- scope: release scope

# Game design (GD-xx, specs/02-game-design.md)

## REQ-GD-01

- source: specs/02-game-design.md
- description: Vertical scrolling, ground speed varies per level.
- acceptance: absent
- scope: screen and camera

## REQ-GD-02

- source: specs/02-game-design.md
- description: Logical resolution 480x640, scaled to fit the window.
- acceptance: absent
- scope: screen

## REQ-GD-03

- source: specs/02-game-design.md
- description: Aspect ratio handling: responsive.
- acceptance: absent
- scope: screen

## REQ-GD-controls

- source: specs/02-game-design.md
- description: Controls table. Move: arrows/WASD (key position based, also AZERTY), left stick, touch drag. Shoot: Space, button, button. Special/bomb: E, button, button (E for bomb is superseded by D-043 and P11-R06). Pause: Esc/P, button, button.
- acceptance: absent
- scope: controls

## REQ-GD-10

- source: specs/02-game-design.md
- description: Input feel: the player ship has little acceleration but quickly reaches its maximal speed.
- acceptance: absent
- scope: controls feel

## REQ-GD-20

- source: specs/02-game-design.md
- description: Lives/health model: start with 3 lives; more lives collectable as dropped bonuses; a 100% health bar.
- acceptance: absent
- scope: player

## REQ-GD-21

- source: specs/02-game-design.md
- description: Hitbox: small hitbox for the player, visual-equivalent hitbox for enemies.
- acceptance: absent
- scope: player, collision

## REQ-GD-22

- source: specs/02-game-design.md
- description: Invincibility after a hit: 2 seconds; the ship blinks while invincible.
- acceptance: absent
- scope: player

## REQ-GD-30

- source: specs/02-game-design.md
- description: The player has 3 main weapons: guns, laser, missiles.
- acceptance: absent
- scope: weapons

## REQ-GD-31

- source: specs/02-game-design.md
- description: Each weapon is upgradable up to level 5.
- acceptance: absent
- scope: weapons

## REQ-GD-32

- source: specs/02-game-design.md
- description: Secondary bombs; one bomb damages every enemy on screen, enough to kill most low-level enemies.
- acceptance: absent
- scope: bombs

## REQ-GD-33

- source: specs/02-game-design.md
- description: Weapon balance (2026-10-25): guns are the reference; at every level laser and missiles deal 70-100 % of the guns' damage per second (every stream counted). Guns spread widest; laser most focused (one column, never misses, pierces) and out-damages missiles; missiles home but take time to arrive.
- acceptance: absent
- scope: weapon balance

## REQ-GD-40

- source: specs/02-game-design.md
- description: Enemies spawn (alone or in waves) based on how far the player advances in the level.
- acceptance: absent
- scope: enemies, spawning

## REQ-GD-41

- source: specs/02-game-design.md
- description: Each level has one mini boss and one final boss.
- acceptance: absent
- scope: bosses

## REQ-GD-42

- source: specs/02-game-design.md
- description: The mini boss acts as a checkpoint.
- acceptance: absent
- scope: checkpoint

## REQ-GD-43

- source: specs/02-game-design.md
- description: Enemies can shoot colourful bullets, missiles the player can shoot, or lasers (with a 1 s warning line before firing).
- acceptance: absent
- scope: enemy attacks

## REQ-GD-44

- source: specs/02-game-design.md
- description: Enemies can shoot in preset directions or aim at the player.
- acceptance: absent
- scope: enemy attacks

## REQ-GD-45

- source: specs/02-game-design.md
- description: Each enemy kind has a preset movement kind: a predefined path, or diving at the player.
- acceptance: absent
- scope: enemy movement

## REQ-GD-46

- source: specs/02-game-design.md
- description: Mini bosses and final bosses have destructible parts; each time a part is destroyed the attack pattern changes.
- acceptance: absent
- scope: bosses

## REQ-GD-50

- source: specs/02-game-design.md
- description: Killing an enemy gives points according to its difficulty.
- acceptance: absent
- scope: scoring

## REQ-GD-51

- source: specs/02-game-design.md
- description: High score persistence is based on a cookie.
- acceptance: absent
- scope: scoring, persistence

## REQ-GD-flow

- source: specs/02-game-design.md
- description: Game flow diagram (section 7): Title - start - Select Ship - Select level - Game - lives=0 - Game Over - any key - Title; Game to Pause and back via pause/resume. Marked TODO in source (screen list not finalised).
- acceptance: absent
- scope: game flow

## REQ-GD-60

- source: specs/02-game-design.md
- description: Art direction: all models generated from code; style darksynth (reviewer, 2026-10-26; was cyberpunk/synthwave): dark, neon magenta, violet and blood red, sunset gradients, chrome.
- acceptance: absent
- scope: visual style

## REQ-GD-61

- source: specs/02-game-design.md
- description: Palette: player ship shiny grey/blue; enemies dark metallic with neon lights.
- acceptance: absent
- scope: visual style

## REQ-GD-62

- source: specs/02-game-design.md
- description: Particle effect whenever a projectile hits a ship; explosions when a ship is destroyed.
- acceptance: absent
- scope: effects

## REQ-GD-70

- source: specs/02-game-design.md
- description: Music is code generated; one music per level, a more stressful music for a boss fight.
- acceptance: absent
- scope: audio

## REQ-GD-71

- source: specs/02-game-design.md
- description: SFX are software generated.
- acceptance: absent
- scope: audio

# Phase 1 - Main menu (specs/phases/phase-01-main-menu.md)

## REQ-P01-R01

- source: specs/phases/phase-01-main-menu.md
- description: Pure screen state machine in app/ with screens loading, title, ship-select, level-select, game (placeholder) and a Back action per menu screen.
- acceptance: Start on title goes to ship-select; Back returns; level-select Back keeps chosen ship; game Back (Esc) goes to title (superseded in game by P12-R01); invalid transitions rejected.
- scope: menu flow

## REQ-P01-R02

- source: specs/phases/phase-01-main-menu.md
- description: Loading screen with real progress bar (ENG-108), switches to title automatically.
- acceptance: Progress bar 0-100 % visible before title; title appears without user action.
- scope: loading

## REQ-P01-R03

- source: specs/phases/phase-01-main-menu.md
- description: If WebGL2 is unavailable show a clear friendly message and throw no errors (ENG-06).
- acceptance: Browser without WebGL2 shows an explanation and no console error.
- scope: capability check

## REQ-P01-R04

- source: specs/phases/phase-01-main-menu.md
- description: Title screen: game title (from src/game/), Start entry selected by default, high score from cookie (0 if none), version and short commit hash, controls hint.
- acceptance: No cookie shows 0; cookie 12345 shows 12345; corrupted cookie shows 0 without error; version matches package.json, hash injected at build.
- scope: title screen

## REQ-P01-R05

- source: specs/phases/phase-01-main-menu.md
- description: SHOULD. Code-generated animated 3D darksynth background (night city, neon, crimson sunset haze) with the balanced ship flying slowly; loops, 60 FPS.
- acceptance: Animated, generated in code (no downloaded asset); 60 FPS on reference hardware.
- scope: title background

## REQ-P01-R06

- source: specs/phases/phase-01-main-menu.md
- description: Ship select shows the 3 ships rotating with name, speed, health; Left/Right changes selection (wraps), Confirm stores the ship and goes to level-select; balanced selected by default; highlighted ship clearly visible, others dimmed.
- acceptance: Four criteria (default balanced, wrap on Right, Confirm stores and moves on, highlight visible).
- scope: ship select

## REQ-P01-R07

- source: specs/phases/phase-01-main-menu.md
- description: Level select grid of 4 worlds x 5 levels (5x5 until World 5 dropped, 2026-10-26); only 1-1 unlocked in this phase, others locked with padlock; level data from src/game/.
- acceptance: 20 entries 1-1 to 4-5; 1-1 highlighted; locked confirm gives feedback only; 1-1 confirm opens game; data from game, not engine.
- scope: level select

## REQ-P01-R08

- source: specs/phases/phase-01-main-menu.md
- description: Placeholder game screen showing chosen ship and level and how to go back (replaced by P06-R02).
- acceptance: Heavy ship + 1-1 shown; Back returns to title.
- scope: placeholder screen

## REQ-P01-R09

- source: specs/phases/phase-01-main-menu.md
- description: Keyboard menu navigation by physical key position: arrows/WASD move, Enter/Space confirm, Esc/Backspace back; held direction repeats after a delay.
- acceptance: AZERTY Z/Q/S/D move selection; holding Right moves once then repeats.
- scope: keyboard menus

## REQ-P01-R10

- source: specs/phases/phase-01-main-menu.md
- description: Gamepad menu navigation (standard mapping): stick/D-pad move, A confirm, B back, dead zone.
- acceptance: Whole flow doable with gamepad only; stick inside dead zone does not move.
- scope: gamepad menus

## REQ-P01-R11

- source: specs/phases/phase-01-main-menu.md
- description: Touch/mouse: every entry tappable (tap selects, tap on selected confirms), visible Back button on each non-title screen, targets at least 44x44 CSS px.
- acceptance: Whole flow with mouse only and with taps only.
- scope: touch menus

## REQ-P01-R12

- source: specs/phases/phase-01-main-menu.md
- description: input/ translates keyboard, gamepad and touch into abstract menu actions up/down/left/right/confirm/back; mapping in config.
- acceptance: Unit tests show Enter, Space, gamepad A and tap on selected entry all produce confirm.
- scope: input abstraction

## REQ-P01-R13

- source: specs/phases/phase-01-main-menu.md
- description: HTML/CSS overlay on 480x640 logical resolution scaled to fit; darksynth look for menus and HUD (text still mentions a chrome logo over a striped sun); kid-readable, selection obvious without colour alone; system or bundled fonts only.
- acceptance: Fully visible at 800x600, 1920x1080, 390x844; selected entry identifiable in greyscale.
- scope: menu layout and look

## REQ-P01-R14

- source: specs/phases/phase-01-main-menu.md
- description: MAY. Last chosen ship saved in a cookie and pre-selected next time.
- acceptance: Light ship chosen then reload highlights light ship.
- scope: persistence

## REQ-P01-R15

- source: specs/phases/phase-01-main-menu.md
- description: MAY. Short transitions (fade/slide, <= 300 ms); input ignored during a transition.
- acceptance: absent
- scope: transitions

# Phase 2 - Player ships (specs/phases/phase-02-player-ships.md)

## REQ-P02-R01

- source: specs/phases/phase-02-player-ships.md
- description: Balanced ship: max speed factor 1, 100 HP; design inspired by MACROSS DELTA VF-31J (dual reactor, wings going forward). Goal text states base ship speed 100 px/s (overridden by D-044/D-047).
- acceptance: Design manually validated.
- scope: player ship

## REQ-P02-R02

- source: specs/phases/phase-02-player-ships.md
- description: Heavy ship: max speed factor 0.8, 140 HP; inspired by a modern flying wing nuclear bomber.
- acceptance: Design manually validated.
- scope: player ship

## REQ-P02-R03

- source: specs/phases/phase-02-player-ships.md
- description: Light ship: max speed factor 1.4, 80 HP; 4 wings each with an attached reactor.
- acceptance: Design manually validated.
- scope: player ship

# Phase 3 - Player shots (specs/phases/phase-03-player-shots.md)

## REQ-P03-R01

- source: specs/phases/phase-03-player-shots.md
- description: Bullet: minigun tracer at constant velocity (white-hot head cooling to orange then red); levels 1-5: single forward, dual forward, single + 2 diagonals (10 deg), dual + 2 diagonals, single + 4 diagonals (10 and 20 deg); 10 damage per bullet.
- acceptance: absent
- scope: player weapons

## REQ-P03-R02

- source: specs/phases/phase-03-player-shots.md
- description: Laser: bright blue with particle flow; damage per second 80/140/200/260/320 at levels 1-5 (GD-33, was 40/60/85/115/150); after level 1 the beam pierces a ship continuing at one level lower.
- acceptance: absent
- scope: player weapons

## REQ-P03-R03

- source: specs/phases/phase-03-player-shots.md
- description: Missile: constant acceleration with reactor flame; targets closest enemy within about 320 px; base damage 14 for a 10 px radius (was 8); 4 missiles per second per stream; level layouts 1-5 (single forward; two diagonals 10 deg; forward + two diagonals; four diagonals 10/20 deg; forward + four diagonals).
- acceptance: absent
- scope: player weapons

## REQ-P03-R11

- source: specs/phases/phase-03-player-shots.md
- description: When a bullet or missile level has several streams they fire one after the other, evenly spaced over each volley, with unchanged overall rate (bullets 8/s, missiles 4/s per stream). Added 2026-10-26.
- acceptance: A two-stream level over one volley period fires each stream once, never both at the same instant, and each stream fires its rate over a second (unit test).
- scope: player weapons

## REQ-P03-R10

- source: specs/phases/phase-03-player-shots.md
- description: player_shots/ debug endpoint showing each ship's shots for visual validation.
- acceptance: absent
- scope: debug page

# Phase 4 - Level Zero (specs/phases/phase-04-level-zero.md)

## REQ-P04-R01

- source: specs/phases/phase-04-level-zero.md
- description: Software-sculpted heightmap base for mountains, canyons or flat terrain; software-generated textures fading by slope or altitude.
- acceptance: Manual visual validation.
- scope: terrain

## REQ-P04-R02

- source: specs/phases/phase-04-level-zero.md
- description: Optional sea level simulating water reflecting the sun; natural shore (sand beach, shallows darkening with depth, broken surf).
- acceptance: Manual visual validation.
- scope: sea

## REQ-P04-R03

- source: specs/phases/phase-04-level-zero.md
- description: Optional cloud layers with adjustable intensity and opacity.
- acceptance: Manual visual validation.
- scope: clouds

## REQ-P04-R04

- source: specs/phases/phase-04-level-zero.md
- description: Flat ground areas populated with props: industrial buildings, technical/scientific items, futuristic homes, dead trees.
- acceptance: Manual visual validation.
- scope: props

## REQ-P04-R05

- source: specs/phases/phase-04-level-zero.md
- description: Camera on top pointing down, angled 35 (written as "35%") to the back.
- acceptance: Manual visual validation.
- scope: camera

## REQ-P04-R06

- source: specs/phases/phase-04-level-zero.md
- description: Level Zero lasts around 3 minutes.
- acceptance: absent
- scope: duration

## REQ-P04-R07

- source: specs/phases/phase-04-level-zero.md
- description: Randomly generated roads or paths across the maps; building props only along those roads.
- acceptance: Manual visual validation.
- scope: roads, props

# Phase 5 - Enemies (specs/phases/phase-05-first-enemies.md; HP, speeds, points in constraints.md tunables)

## REQ-P05-R01

- source: specs/phases/phase-05-first-enemies.md
- description: Gnat (swarm drone): small flat disc with three ducted-fan arms and neon ring; groups of 5 following the same S-shaped path from the top; does not shoot; killed by one level-1 bullet.
- acceptance: 5 Gnats follow the same path with a fixed delay; manual visual validation.
- scope: enemy

## REQ-P05-R02

- source: specs/phases/phase-05-first-enemies.md
- description: Hornet (diver): arrow head with red neon eye; enters from top, pauses 0.5 s turning to the player, dives at the recorded player position, accelerating; does not shoot.
- acceptance: Dives toward position recorded at end of pause; manual visual validation.
- scope: enemy

## REQ-P05-R03

- source: specs/phases/phase-05-first-enemies.md
- description: Scout (aimed shooter): small delta wing with cyan strips; flies straight down slowly and fires one aimed bullet every 1.5 s.
- acceptance: Each bullet travels along the Scout-to-player line at fire time; manual visual validation.
- scope: enemy

## REQ-P05-R04

- source: specs/phases/phase-05-first-enemies.md
- description: Strafer (fan shooter): wide flat flying wing with magenta lights; crosses horizontally in the top third; every second fires a fan of 3 bullets at -15, 0, +15 degrees from straight down.
- acceptance: Three bullets at -15/0/+15 whatever the player position; manual visual validation.
- scope: enemy

## REQ-P05-R05

- source: specs/phases/phase-05-first-enemies.md
- description: Weaver (sine flyer): twin-hull catamaran with green neon bar; sways along a sine wave; every 2 s fires a pair of aimed bullets, one per hull.
- acceptance: two criteria listed in source (details not extracted)
- scope: enemy

## REQ-P05-R06

- source: specs/phases/phase-05-first-enemies.md
- description: Spinner (spiral turret): ring with four spoke pods and orange core; descends to the upper half, spins 3 s firing a spiral from four pods, leaves upward.
- acceptance: three criteria listed in source (details not extracted)
- scope: enemy

## REQ-P05-R07

- source: specs/phases/phase-05-first-enemies.md
- description: Lancer (laser): needle hull with nose emitter; stops in the top part, 1 s warning line then laser for 1.5 s, then moves away.
- acceptance: two criteria listed in source (details not extracted)
- scope: enemy

## REQ-P05-R08

- source: specs/phases/phase-05-first-enemies.md
- description: Rocketeer (missile carrier): bulky hull with two missile pods; descends slowly; every 3 s launches one missile per pod; missiles turn toward the player with a limited turn rate and can be shot down.
- acceptance: three criteria listed in source (details not extracted)
- scope: enemy

## REQ-P05-R09

- source: specs/phases/phase-05-first-enemies.md
- description: Bulwark (heavy gunship): armoured wide hull with blue visor; moves to the upper third, drifts 8 s, leaves; every 2 s fires an aimed 5-bullet spread 10 degrees apart.
- acceptance: two criteria listed in source (details not extracted)
- scope: enemy

## REQ-P05-R10

- source: specs/phases/phase-05-first-enemies.md
- description: Splitter: hexagonal core with three pods and purple seams; curved path; one aimed bullet every 2.5 s; on death three pods dive at the player like Hornets.
- acceptance: two criteria listed in source (details not extracted)
- scope: enemy

## REQ-P05-R11

- source: specs/phases/phase-05-first-enemies.md
- description: enemies/ debug page over Level Zero scenery with the playfield camera: pick a kind, model view (close up, left/right arrows switch), wireframe view (V, with hit circles), a shootable invulnerable player ship, hit particles and explosions, FPS/polygons tile.
- acceptance: Page loads without console errors and every kind can be picked; picked enemy spawns and behaves; arrows switch enemies in model view; manual visual validation.
- scope: debug page

## REQ-P05-R12

- source: specs/phases/phase-05-first-enemies.md
- description: Carrier (Gnat launcher), added 2026-10-24: fat carrier with two launch ports per side; flies slowly down; never shoots; every 3 s a Gnat leaves each side port; stops launching in the lower part of the screen.
- acceptance: Gnats appear at side ports when launch timer expires; never shoots; manual visual validation.
- scope: enemy

## REQ-P05-R13

- source: specs/phases/phase-05-first-enemies.md
- description: Moving parts (engine feature): parts hang on swinging or orbiting joints, with own hit circle, health, weapon and muzzles; destroyed parts blow up and stop firing but score nothing and drop nothing; enemy dies when its hull reaches 0 HP taking remaining parts.
- acceptance: Unit tests: part hit circle and muzzle follow the joint; destroying a part leaves the enemy alive.
- scope: engine feature

## REQ-P05-R14

- source: specs/phases/phase-05-first-enemies.md
- description: Wasp (armed diver, veteran): groups of 3; pauses 0.4 s, fires a 3-bullet fan (+/-12 deg) at the player, then dives.
- acceptance: three criteria listed in source (details not extracted)
- scope: enemy

## REQ-P05-R15

- source: specs/phases/phase-05-first-enemies.md
- description: Mortar (burst shells, veteran): every 2.5 s lobs a slow shell at the player that bursts into 8 bullets 1.2 s later.
- acceptance: two criteria listed in source (details not extracted)
- scope: enemy

## REQ-P05-R16

- source: specs/phases/phase-05-first-enemies.md
- description: Mantis (scythe arms, veteran, moving parts): stops in the upper half 6 s with two swinging arm parts that fire pairs of bullets.
- acceptance: three criteria listed in source (details not extracted)
- scope: enemy

## REQ-P05-R17

- source: specs/phases/phase-05-first-enemies.md
- description: Phantom (cloaker, veteran): three times fades out 0.4 s, hidden 0.8 s, reappears elsewhere and fires a spread of 5 bullets.
- acceptance: three criteria listed in source (details not extracted)
- scope: enemy

## REQ-P05-R18

- source: specs/phases/phase-05-first-enemies.md
- description: Minelayer (mines, veteran): crosses horizontally like a Strafer; every 0.8 s drops a mine that bursts into 6 bullets 1.5 s later.
- acceptance: two criteria listed in source (details not extracted)
- scope: enemy

## REQ-P05-R19

- source: specs/phases/phase-05-first-enemies.md
- description: Hydra (three heads, elite, moving parts): stays 7 s in the upper third with three swaying necks; heads fire in turn, one every 0.5 s.
- acceptance: three criteria listed in source (details not extracted)
- scope: enemy

## REQ-P05-R20

- source: specs/phases/phase-05-first-enemies.md
- description: Orbiter (orbiting drones, elite, moving parts): core with three orbiting armoured drones that catch shots; core fires a ring every 3 s; stays 8 s.
- acceptance: two criteria listed in source (details not extracted)
- scope: enemy

## REQ-P05-R21

- source: specs/phases/phase-05-first-enemies.md
- description: Scissor (twin lasers, elite, moving parts): two laser arms angled 25 degrees out; each shows a 1 s warning line then fires a 2 s laser; arms sweep (15 degrees in tunables).
- acceptance: three criteria listed in source (details not extracted)
- scope: enemy

## REQ-P05-R22

- source: specs/phases/phase-05-first-enemies.md
- description: Juggernaut (armoured brute, elite, moving parts): two armour plates and two swinging shoulder cannons; drifts 10 s in the upper third.
- acceptance: two criteria listed in source (details not extracted)
- scope: enemy

## REQ-P05-R23

- source: specs/phases/phase-05-first-enemies.md
- description: Hive (Wasp launcher, elite): flies slowly down; every 4 s launches a Wasp from its ring; also fires every 3 s.
- acceptance: two criteria listed in source (details not extracted)
- scope: enemy

## REQ-P05-R24

- source: specs/phases/phase-05-first-enemies.md
- description: New kinds in the game: enemies/ page lists 21 kinds; veteran kinds in World 3 and World 4 waves, elites in World 4 only (Worlds 1 and 2 unchanged); World 3 introduces one veteran per level from 3-1 (3-5 uses all five); World 4 uses all five veterans each level and brings in elites two in 4-1 then at least one more per level; P09-R08 and P10-R10 difficulty rules still hold.
- acceptance: 21 kinds pickable without console errors (e2e); unit test of kinds per level; P09-R08 and P10-R10 still pass.
- scope: enemy roster, waves

# Phase 6 - World 1 (specs/phases/phase-06-world-1.md)

## REQ-P06-R01

- source: specs/phases/phase-06-world-1.md
- description: World 1 has 5 levels 1-1 to 1-5, all unlocked; levels never locked by progress; Worlds 2 to 4 greyed until built (World 5 dropped).
- acceptance: Row shows exactly 1-1..1-5 unlocked; confirming starts the level; fresh start can confirm 1-5; worlds 2-4 greyed out at that time.
- scope: level select

## REQ-P06-R02

- source: specs/phases/phase-06-world-1.md
- description: Game screen plays the chosen level: scrolling scenery, ship at bottom moving with game controls and staying in the playfield, Space/button/touch to shoot starting with guns level 1, enemies from wave script, hit particles and explosions, Back (Esc) to title (superseded by P12-R01).
- acceptance: Heavy ship flies over 1-1; stays on screen at edges; enemy explodes at 0 HP; Back goes to title.
- scope: gameplay

## REQ-P06-R03

- source: specs/phases/phase-06-world-1.md
- description: Level end: no spawns after the scroll reaches the level length; once screen is clear (max 10 s) a "Level complete" overlay shows level and destroyed/spawned counts; Confirm returns to level-select with next level highlighted (changed by P07-R06 to end on final boss).
- acceptance: Three criteria (no spawn after length; overlay content; Confirm highlights next level).
- scope: level end

## REQ-P06-R04

- source: specs/phases/phase-06-world-1.md
- description: Each World 1 level lasts about 4 minutes (240 s +/- 10 s at ground speed).
- acceptance: Unit test: length / ground speed between 230 and 250 s.
- scope: duration

## REQ-P06-R05

- source: specs/phases/phase-06-world-1.md
- description: Five levels are one journey sea -> green grass -> desert with more props along the way (reworked 2026-10-26, amended 2026-10-27: 1-5 ends in desert, no factory or city); table: 1-1 Open sea, 1-2 Green coast, 1-3 Green country, 1-4 Dry lands, 1-5 Deep desert; each level begins where the previous ended; prop counts rise per level and in each second half.
- acceptance: Five unit-test criteria (sea share down to 1-3, grass/sand shares, prop and building counts, continuity) plus manual visual validation.
- scope: World 1 scenery

## REQ-P06-R06

- source: specs/phases/phase-06-world-1.md
- description: New generated ground and props: sand and dunes, grass cover, dry bushes, palms, cacti, futuristic desert homes and outposts, farms (farmhouse, greenhouse, silos), no industrial zone or city; light polygons (D-031), matte (D-024).
- acceptance: Manual visual validation.
- scope: World 1 props

## REQ-P06-R07

- source: specs/phases/phase-06-world-1.md
- description: Per-level wave scripts in src/game/ triggered by scrolled distance (GD-40); kinds introduced over the world: 1-1 Gnat, Hornet, Scout, Strafer; 1-2 adds Weaver, Splitter; 1-3 adds Carrier, Spinner; 1-4 adds Lancer, Rocketeer; 1-5 every kind incl. Bulwark; deterministic.
- acceptance: Waves spawn at their distance and not before; kind lists per level; same level twice gives same waves.
- scope: waves

## REQ-P06-R08

- source: specs/phases/phase-06-world-1.md
- description: Increasing difficulty 1-1 to 1-5: enemy count, total HP and peak on-screen count strictly up; bullet speed and fire-rate factors never down; second half of each level has more HP than first.
- acceptance: Unit tests for the strict increases, factors, second-half HP; manual feel check.
- scope: balance

## REQ-P06-R09

- source: specs/phases/phase-06-world-1.md
- description: Debug URL options (e.g. ?level=1-3&t=120): start any level, start time, F x4 fast forward, left/right jump 10 s; ignored without debug options; FPS/polygons tile when debug is on.
- acceptance: ?level=1-3&t=120 starts at 2:00 skipping earlier waves; no option means keys do nothing.
- scope: debug

## REQ-P06-R10

- source: specs/phases/phase-06-world-1.md
- description: Time of day per level (added 2026-10-26): 1-1 midday, then early afternoon, late afternoon, sunset (1-4), dusk with town lights (1-5); fixed within a level.
- acceptance: Unit test sun highest in 1-1 and lower each level; manual visual validation.
- scope: looks

# Phase 7 - Bosses (specs/phases/phase-07-bosses.md)

## REQ-P07-R01

- source: specs/phases/phase-07-bosses.md
- description: Boss = core plus destroyable parts each with own HP and hit circle; shielding parts block core damage; boss dies when core hits 0; damaged parts flash and smoke under 50 %; destroyed parts explode leaving stumps; mini bosses 2-3 parts, final bosses 4-6.
- acceptance: Unit tests for part destruction, core shield, core death, part counts; manual visual validation.
- scope: boss engine

## REQ-P07-R02

- source: specs/phases/phase-07-bosses.md
- description: Boss health bar as a slim vertical gauge on the left edge of the playfield under the player HUD (amended 2026-10-26, D-105) showing name and kind, fills in 1 s, notches for each part.
- acceptance: Bar appears full with name; drop equals part damage / full HP; gone on death; readable manually.
- scope: HUD

## REQ-P07-R03

- source: specs/phases/phase-07-bosses.md
- description: Ground speed eases over 2 s to each boss's fight factor (some slow, one stops x0, one chases) and back after the kill; scenery never runs out; level distance moves with the ground so no wave is skipped.
- acceptance: Unit tests of 0.5 factor easing and recovery; 5-minute fight keeps scrolling; smoothness checked manually.
- scope: boss fights

## REQ-P07-R04

- source: specs/phases/phase-07-bosses.md
- description: Stages: stage k = k parts destroyed; weapons on destroyed parts stop; each stage has its own pattern never equal to the previous; last stage unique; 1 s no-fire pause on stage change; patterns use GD-43/GD-44 attacks and may launch phase 5 enemies.
- acceptance: Unit tests for stage change, weapon stop, pause, unique last stage.
- scope: boss patterns

## REQ-P07-R05

- source: specs/phases/phase-07-bosses.md
- description: Ten World 1 bosses (mini + final per level): Reef Warden / Storm Petrel (1-1), Breakwater / Gull Mothership (1-2), Dust Devil / Mesa Fortress (1-3), Scorpion / Refinery Titan (1-4), Sentinel / Overlord (1-5), with fight ground speed factors x0.5, x1.5, x0.4, x0.6, x0.5, x0, x0.5, x0.3, x0.6, x0.25; come from top, stay within x 107-373, no damage until in place.
- acceptance: One mini and one final per level; hit circles inside x 107-373; no HP loss while coming in; manual model validation.
- scope: World 1 bosses

## REQ-P07-R06

- source: specs/phases/phase-07-bosses.md
- description: Mini boss at middle of level length, final boss when scroll reaches level length; no new waves while a boss lives (10 s free before); touching a boss hurts the player; level ends when final boss is destroyed (replaces P06-R03 for World 1).
- acceptance: Unit tests (mini at half length, no waves during boss, level complete only after final boss death, collision damage) plus e2e.
- scope: boss fights

## REQ-P07-R07

- source: specs/phases/phase-07-bosses.md
- description: Destroyed parts may drop weapon bonuses with per-boss chance; final boss core always drops one; drops deterministic from the level seed.
- acceptance: Chance 1 drops, chance 0 does not, final boss drops, same fight same drops.
- scope: bonuses

## REQ-P07-R08

- source: specs/phases/phase-07-bosses.md
- description: Destroying the mini boss saves a checkpoint (distance, weapon levels); after game over, panel offers Continue (3 full lives, saved weapons, earlier waves skipped) or Level select; forgotten when the level is left.
- acceptance: Panel offers both; Continue restarts just after the mini boss; without checkpoint panel unchanged.
- scope: checkpoint (GD-42)

## REQ-P07-R09

- source: specs/phases/phase-07-bosses.md
- description: bosses/ debug page (pick boss, model and wireframe views, invulnerable shooting ship, K destroys next part, stage shown, FPS tile); game screen debug options also take boss=mini|final and K while debug on.
- acceptance: Page loads without errors; K advances stage; ?level=1-3&boss=final starts at the final boss; no debug option means K does nothing.
- scope: debug

## REQ-P07-R10

- source: specs/phases/phase-07-bosses.md
- description: Boss difficulty: mini and final HP strictly up 1-1 to 1-5; each final has more HP than its mini; boss bullets use the level's speed and rate factors.
- acceptance: Unit tests of HP orderings and simulated fight times within tunable ranges; manual check.
- scope: balance

# Phase 8 - World 2 (specs/phases/phase-08-world-2.md; reworked 2026-10-27 to the Industrial Desert, D-110)

## REQ-P08-R01

- source: specs/phases/phase-08-world-2.md
- description: World 2 row shows 2-1 to 2-5 all unlocked; after 2-5 highlights 2-5, after 1-5 highlights 2-1.
- acceptance: Exact row; fresh start can confirm 2-5; 1-5 completion highlights 2-1; worlds 3-5 greyed at that time.
- scope: level select

## REQ-P08-R02

- source: specs/phases/phase-08-world-2.md
- description: Each level about 5 minutes: 300 s +/- 10 s scroll.
- acceptance: Unit test: length / speed between 290 and 310 s.
- scope: duration

## REQ-P08-R03

- source: specs/phases/phase-08-world-2.md
- description: One journey from deep desert to factories (2-1 Great erg, 2-2 Mining mesas, 2-3 Oil fields, 2-4 Industrial belt, 2-5 Factory district) with slow transitions; no sea, rivers allowed; sand share down and paved share up; props rise per level.
- acceptance: Seven criteria (no sea, sand/paved shares, group exclusions, prop counts, continuity, longer blends, manual validation).
- scope: World 2 scenery

## REQ-P08-R04

- source: specs/phases/phase-08-world-2.md
- description: Engine level look: time of day (dawn, morning, midday, afternoon, dusk, night), cloud cover/colour, haze, ground lights, smooth look change along the level; readability always preserved.
- acceptance: Look data matches table; look change blends parameters linearly; ?level=2-5&t=... starts with correct look; manual validation.
- scope: atmosphere engine

## REQ-P08-R05

- source: specs/phases/phase-08-world-2.md
- description: Weather engine with kind and strength 0-1; first kind snow (flakes behind ships, shots, bonuses; never changes simulation); kinds are data. No World 2 level uses snow since the rework.
- acceptance: Strength 0 draws none, strength 1 draws max; weather is not an input to the simulation; manual validation and 60 FPS in the 2-4 blizzard (stale since rework).
- scope: weather engine

## REQ-P08-R06

- source: specs/phases/phase-08-world-2.md
- description: Looks: 2-1 morning, 2-2 midday, 2-3 afternoon, 2-4 dusk, 2-5 night; cloud covers 0.15/0.1, 0.2/0.15, 0.25/0.2, 0.35/0.25 (smog), 0.4/0.3 (smog); no weather; no change within level.
- acceptance: Unit test look data matches; manual validation, readable at dusk and night.
- scope: looks

## REQ-P08-R07

- source: specs/phases/phase-08-world-2.md
- description: Ground is World 1 desert covered by paved industrial concrete; buildings from World 1 desert homes/outposts, Level Zero industry and made-of-parts industry; new oil pumpjack prop. Original frozen ground/props kept for the record (models stay but unused).
- acceptance: Manual validation; pumpjack under triangle budget and fits footprint; World 2 props use no frozen prop.
- scope: World 2 props

## REQ-P08-R08

- source: specs/phases/phase-08-world-2.md
- description: Wave scripts with fillers using the eleven phase 5 kinds; 2-1 leads Gnat, Hornet, Scout, Strafer, Weaver; 2-2 adds Splitter, Lancer; 2-3 to 2-5 every kind (table still mentions sea, fjords, tundra, blizzard).
- acceptance: Each script only uses kinds for its level and 2-3..2-5 use all eleven; deterministic.
- scope: waves

## REQ-P08-R09

- source: specs/phases/phase-08-world-2.md
- description: Difficulty strictly up 2-1 to 2-5 per minute measures and peak on screen; factors never down; second half more HP; across worlds 2-1 >= 1-3 and 2-5 > 1-5.
- acceptance: Unit tests for each; manual feel.
- scope: balance

## REQ-P08-R10

- source: specs/phases/phase-08-world-2.md
- description: Ten World 2 bosses: Floe Breaker / Narwhal, Fjord Lynx / Harbour Kraken, Snow Owl / Aurora Station, Avalanche / Glacier Colossus, Ice Queen / Boreal Citadel, with fight speeds including a stop (x0) and chases; 2-3 parts mini, 4-6 final.
- acceptance: One mini and one final per level with right part counts; radar-mast aiming rule tested; hit circles in reach; manual model validation.
- scope: World 2 bosses

## REQ-P08-R11

- source: specs/phases/phase-08-world-2.md
- description: Boss difficulty: HP strictly up, final > mini, each World 2 boss above the World 1 boss of the same level and kind; fight times within tunable ranges.
- acceptance: Unit tests plus manual validation.
- scope: balance

## REQ-P08-R12

- source: specs/phases/phase-08-world-2.md
- description: Debug options accept World 2 levels; weather=0 and look=<time of day> options; bosses/ page lists World 2 bosses after World 1 grouped by world.
- acceptance: Four criteria (t=150 start, weather=0 behaviour, bosses page, no option means level's own look).
- scope: debug

# Phase 9 - World 3 (specs/phases/phase-09-world-3.md; reworked 2026-10-27, D-111)

## REQ-P09-R01

- source: specs/phases/phase-09-world-3.md
- description: World 3 row 3-1 to 3-5 all unlocked; after 2-5 highlights 3-1, after 3-5 highlights 3-5 (text also says Worlds 4 and 5 stay greyed).
- acceptance: Exact row; 2-5 completion highlights 3-1; later worlds greyed at that time.
- scope: level select

## REQ-P09-R02

- source: specs/phases/phase-09-world-3.md
- description: Each level 300 s +/- 10 s scroll.
- acceptance: Unit test between 290 and 310 s.
- scope: duration

## REQ-P09-R03

- source: specs/phases/phase-09-world-3.md
- description: Reworked: from the factories World 2 ended on to small-building habitations, no skyscrapers, no sea (canals, rivers, ponds), slow transitions; each level begins where the previous ended.
- acceptance: Seven criteria listed in source (details not extracted).
- scope: World 3 scenery

## REQ-P09-R04

- source: specs/phases/phase-09-world-3.md
- description: Looks: 3-1 morning with mist; 3-2 midday cumulus, rain 0.4 over middle third; 3-3 afternoon thunderstorm, rain 0.8 with lightning; 3-4 dusk, rain 0.3; 3-5 night, rain 0.5 stopping before the final boss.
- acceptance: Look data matches table incl. changes; manual validation, always readable.
- scope: looks

## REQ-P09-R05

- source: specs/phases/phase-09-world-3.md
- description: Weather kinds rain (streaks, haze, rain rings) and lightning (flash lighting scene, bolt in clouds, seeded, at most 3 flashes in any 1 s, mild brightness rise); weather never changes the simulation.
- acceptance: Six criteria incl. max 3 flashes per second over long storm, same flashes for same level, 60 FPS in the 3-3 storm.
- scope: weather engine

## REQ-P09-R06

- source: specs/phases/phase-09-world-3.md
- description: Reworked ground and props: concrete giving way to grass, damp earth, canal stone, grey-green water, asphalt roads, small homes (flats, terraces, pitched-roof houses); original jungle requirement retained in text.
- acceptance: Manual validation; each new prop under triangle budget.
- scope: World 3 props

## REQ-P09-R07

- source: specs/phases/phase-09-world-3.md
- description: Wave scripts with fillers using the eleven phase 5 kinds (superseded in part by P05-R24 adding veteran kinds); 3-1 leads Gnat, Hornet, Scout, Strafer, Weaver, Splitter; 3-2..3-5 every kind.
- acceptance: Each script only uses kinds for its level and 3-2..3-5 use all eleven; deterministic.
- scope: waves

## REQ-P09-R08

- source: specs/phases/phase-09-world-3.md
- description: Difficulty strictly up 3-1 to 3-5; factors never down; second half more HP; 3-1 >= 2-3 and 3-5 > 2-5.
- acceptance: Four criteria (strict increases, cross-world, second half, manual).
- scope: balance

## REQ-P09-R09

- source: specs/phases/phase-09-world-3.md
- description: Ten World 3 bosses: Mangrove Croc / River Leviathan, Toucan / Canopy Spider, Stone Idol / Sky Temple, Mosquito / Dam Breaker, Jaguar / Verdant Crown; fight speeds incl. chase x1.4 (3-1 mini) and stop x0 (Stone Idol).
- acceptance: Three criteria listed in source (details not extracted).
- scope: World 3 bosses

## REQ-P09-R10

- source: specs/phases/phase-09-world-3.md
- description: Boss difficulty as P08-R11, each above the World 2 boss of same level and kind.
- acceptance: Three criteria listed in source.
- scope: balance

## REQ-P09-R11

- source: specs/phases/phase-09-world-3.md
- description: Debug options accept World 3 levels with weather=0 and look=; bosses/ lists World 3 bosses after World 2.
- acceptance: Three criteria listed in source.
- scope: debug

# Phase 10 - World 4 (specs/phases/phase-10-world-4.md; reworked 2026-10-27 to the Metropolis, D-112)

## REQ-P10-R01

- source: specs/phases/phase-10-world-4.md
- description: World 4 row 4-1 to 4-5 all unlocked; last row (World 5 dropped); after 3-5 highlights 4-1, after 4-5 highlights 4-5.
- acceptance: Three criteria listed in source.
- scope: level select

## REQ-P10-R02

- source: specs/phases/phase-10-world-4.md
- description: Each level 300 s +/- 10 s scroll.
- acceptance: Unit test between 290 and 310 s.
- scope: duration

## REQ-P10-R03

- source: specs/phases/phase-10-world-4.md
- description: Reworked: from garden-village houses through town, mid-rise and offices to a downtown of skyscrapers; no sea, no lava; slow transitions (900 units); each level begins where previous ended.
- acceptance: Six criteria listed in source.
- scope: World 4 scenery

## REQ-P10-R04

- source: specs/phases/phase-10-world-4.md
- description: Per-level looks (time of day, clouds, weather); times of day, clouds and weather kept after the rework (glow from below is the city's).
- acceptance: Two criteria listed in source.
- scope: looks

## REQ-P10-R05

- source: specs/phases/phase-10-world-4.md
- description: Lava as a liquid-ground engine feature; since the rework no World 4 level has lava (feature and tests kept).
- acceptance: Three criteria listed in source.
- scope: lava engine

## REQ-P10-R06

- source: specs/phases/phase-10-world-4.md
- description: Two new weather kinds, falling ash and rising embers, usable together.
- acceptance: Four criteria listed in source.
- scope: weather engine

## REQ-P10-R07

- source: specs/phases/phase-10-world-4.md
- description: World 4 enemy bullets keep phase 5 colours but get a light contrasting outline/core so they stand out on red/orange/dark backgrounds.
- acceptance: Two criteria listed in source.
- scope: shot readability

## REQ-P10-R08

- source: specs/phases/phase-10-world-4.md
- description: Reworked ground and props: World 3 ground with more concrete, stone quays, river water; houses, terraces, flats, city blocks and towers made of parts, plus a new family of 8 skyscrapers (110-170 high at full scale).
- acceptance: Two criteria listed in source.
- scope: World 4 props

## REQ-P10-R09

- source: specs/phases/phase-10-world-4.md
- description: Wave scripts with fillers using the eleven phase 5 kinds all from 4-1 (read together with P05-R24 which adds veteran and elite kinds).
- acceptance: Each World 4 script uses all eleven kinds; deterministic.
- scope: waves

## REQ-P10-R10

- source: specs/phases/phase-10-world-4.md
- description: Difficulty strictly up 4-1 to 4-5; second half more HP; 4-1 >= 3-3 and 4-5 > 3-5; remain beatable by a casual player; peaks lowered if 60 FPS cannot hold.
- acceptance: Four criteria (strict increases, cross-world, second half, manual).
- scope: balance

## REQ-P10-R11

- source: specs/phases/phase-10-world-4.md
- description: Ten World 4 bosses: Cinder Crab / Steam Dreadnought, Ash Wraith / Geyser Rig, Magma Salamander / Obsidian Golem, Furnace Drake / Foundry Ark, Ember Herald / Caldera Throne (last boss of the game, x0 ground stop).
- acceptance: Three criteria listed in source.
- scope: World 4 bosses

## REQ-P10-R12

- source: specs/phases/phase-10-world-4.md
- description: Boss difficulty as P08-R11, each above the World 3 boss of same level and kind; Caldera Throne hardest so far and still beatable.
- acceptance: Three criteria listed in source.
- scope: balance

## REQ-P10-R13

- source: specs/phases/phase-10-world-4.md
- description: Debug options accept World 4 levels with weather=0 and look=; bosses/ lists World 4 bosses after World 3 (acceptance text still mentions the magma lake and eruption look).
- acceptance: Three criteria listed in source.
- scope: debug

# Phase 11 - Score, lives and bombs (specs/phases/phase-11-score-lives-bombs.md)

## REQ-P11-R01

- source: specs/phases/phase-11-score-lives-bombs.md
- description: Per-attempt score from 0; destroyed enemies add their kind's points (shot, bomb or ramming); leaving the screen scores nothing; boss part scores boss_part_points_share (10 %) of boss points, core scores boss points; more-health kinds never score less.
- acceptance: Five unit-test criteria (Gnat, ramming/bomb, leaving, boss 10000 example, roster monotonic).
- scope: scoring (GD-50)

## REQ-P11-R02

- source: specs/phases/phase-11-score-lives-bombs.md
- description: HUD shows score zero-padded to 7 digits top-centre and HI line (larger of saved high score and current score) under it, readable at 800x600 and 390x844 without overlap.
- acceptance: 12 340 saved shows HI 0012340; HI follows once beaten; e2e screenshot check.
- scope: HUD

## REQ-P11-R03

- source: specs/phases/phase-11-score-lives-bombs.md
- description: When an attempt ends (complete, game over, or leaving) a higher score is saved in the high score cookie; Level complete and Game over panels show the score and "New high score!".
- acceptance: Four criteria (new high score, no overwrite when lower, leaving with Esc, unreadable cookie).
- scope: high score (GD-51)

## REQ-P11-R04

- source: specs/phases/phase-11-score-lives-bombs.md
- description: Checkpoint also saves the score; Continue restarts with that score and starting bombs; high score checked at game over before Continue is offered.
- acceptance: 8 000 checkpoint then 9 500 game over, Continue gives 8 000; cookie holds 9 500 first.
- scope: checkpoint score

## REQ-P11-R05

- source: specs/phases/phase-11-score-lives-bombs.md
- description: Bombs: bombs_start (3) per attempt and after Continue, restored to that after a lost life, shown in HUD; one bomb per press for 1 s with shockwave ring and flash (< 3/s), 100 damage once to every on-screen enemy and boss part (not a shielded core), clears enemy bullets, missiles, lasers, player invincible.
- acceptance: Eight unit-test criteria (start count, mixed enemies, shots cleared, invincibility, hold fires once, none left, refill rule, shielded core).
- scope: bombs (GD-32)

## REQ-P11-R06

- source: specs/phases/phase-11-score-lives-bombs.md
- description: Bomb controls: keyboard R and Left Shift (by key position), gamepad X (button 2) and LB (button 4), touch BOMB button; E keeps switching weapon (GD section 2 E binding superseded by D-043).
- acceptance: Four criteria (keys, gamepad, touch with fire and drag simultaneously, E switches weapon only).
- scope: controls

## REQ-P11-R07

- source: specs/phases/phase-11-score-lives-bombs.md
- description: Life bonus (pink heart) and bomb bonus (orange B sphere) join weapon bonus; at most one bonus per enemy; mini boss core always drops a life; life_drop_chance 1 %, bomb_drop_chance 3 %; maxima lives_max 5, bombs_max 5 convert to 5 000 / 2 000 points.
- acceptance: Six criteria (pickup counts, at-maximum points, mini boss life drop, determinism, weapon bonus rate within 10 %).
- scope: bonuses (GD-20)

## REQ-P11-R08

- source: specs/phases/phase-11-score-lives-bombs.md
- description: e2e test API also gives score, highScore, bombs and bonuses with kind; sendAction accepts bomb; absent from production bundle.
- acceptance: getState returns the fields; sendAction('bomb') fires a bomb.
- scope: test API

# Phase 12 - Pause, music and settings (specs/phases/phase-12-pause-music-settings.md)

## REQ-P12-R01

- source: specs/phases/phase-12-pause-music-settings.md
- description: Pause via Escape, KeyP, gamepad Start/Select, touch pause button; nothing advances while paused; resume exact; in game Escape/Backspace/gamepad B no longer leave directly (supersedes P01-R09, P06-R02, D-041 for the game screen).
- acceptance: Four criteria (pause triggers, 10 s pause state identity, Backspace/B do nothing, pause button size and overlap).
- scope: pause

## REQ-P12-R02

- source: specs/phases/phase-12-pause-music-settings.md
- description: Pause menu (Resume default, Settings, Main menu with "Leave the level?" No/Yes); back and pause controls resume.
- acceptance: Six criteria incl. high score saved on leaving, keyboard/gamepad/tap only.
- scope: pause menu

## REQ-P12-R03

- source: specs/phases/phase-12-pause-music-settings.md
- description: Automatic pause when page hidden or the gamepad in use disconnects; never resumes by itself.
- acceptance: Three criteria (hidden page, gamepad loss, still paused after show).
- scope: auto pause (ENG-110)

## REQ-P12-R04

- source: specs/phases/phase-12-pause-music-settings.md
- description: Settings screen from title (entry under Start) and pause menu; two sliders 0-10 (Music, Sound effects) saved in cookies on every change; audible feedback; Back returns to origin.
- acceptance: Six criteria (defaults, persistence, invalid cookie, SFX 0 silent, back target, keyboard/gamepad/tap).
- scope: settings

## REQ-P12-R05

- source: specs/phases/phase-12-pause-music-settings.md
- description: Web Audio engine generating all music and SFX in code (no audio files; ENG-120 audio formats do not apply): music and SFX buses into a limiter, lookahead sequencer, unlock on first user gesture, silent fallback.
- acceptance: Four criteria (no audio file in build, context not running before input, no AudioContext tolerated, 60 fps in busiest World 4 level).
- scope: audio engine (GD-70, GD-71)

## REQ-P12-R06

- source: specs/phases/phase-12-pause-music-settings.md
- description: Every level (1-1 to 4-5) has its own generated music from level data; per-world darksynth/synthwave styles; energetic, faster tempos (World 1 128-140 BPM, World 2 112-124, World 3 120-132, World 4 104-116).
- acceptance: Four criteria listed in source.
- scope: level music

## REQ-P12-R07

- source: specs/phases/phase-12-pause-music-settings.md
- description: Boss fights cross-fade to a world boss track (stressful, 20-30 BPM faster) plus jingles.
- acceptance: Four criteria listed in source.
- scope: boss music, jingles

## REQ-P12-R08

- source: specs/phases/phase-12-pause-music-settings.md
- description: Menu theme: one looping energetic synthwave track for title, ship select, level select and settings from title; keeps playing between these screens.
- acceptance: Two criteria listed in source.
- scope: menu music

## REQ-P12-R09

- source: specs/phases/phase-12-pause-music-settings.md
- description: Every event in the source's event table plays its own generated sound, designed to be told apart (groups include player weapons, with a minigun rattle for the gun).
- acceptance: Three criteria listed in source.
- scope: sound effects

## REQ-P12-R10

- source: specs/phases/phase-12-pause-music-settings.md
- description: Mixing limits: at most sfx_voices_max (16) simultaneous sounds with priority replacement (player and bombs highest, enemy shots lowest).
- acceptance: Three criteria listed in source.
- scope: audio mixing

## REQ-P12-R11

- source: specs/phases/phase-12-pause-music-settings.md
- description: Audio follows pause and page: pause freezes music at position and stops effects; hidden page suspends audio.
- acceptance: Three criteria listed in source.
- scope: audio lifecycle

## REQ-P12-R12

- source: specs/phases/phase-12-pause-music-settings.md
- description: e2e test API also gives paused, current screen (incl. pause, settings), volumes, playing track id, last sound effects; sendAction accepts pause and resume.
- acceptance: Three criteria listed in source.
- scope: test API
