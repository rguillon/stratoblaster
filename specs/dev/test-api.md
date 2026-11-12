# Test API

> **Area:** Dev · **Prefix:** `DEV-API` · **Related:** [../01-engineering.md](../01-engineering.md), [perf-tools.md](perf-tools.md), [debug-options.md](debug-options.md), [../graphics/readability.md](../graphics/readability.md), [../ui/screen-flow.md](../ui/screen-flow.md), [../performance.md](../performance.md)

The e2e build of the game exposes `window.__GAME_TEST__`, so the Playwright tests can read the game's
state, send it input and step it frame by frame. The generic rule (the API exists in the e2e build
only and is absent from the production bundle) is ENG-52 in
[../01-engineering.md](../01-engineering.md). This file says what the API gives beyond that rule: the
fields of its state, its actions, how it steps the game, its readability probe, and what else the
e2e build changes. It is a test tool: the player never sees it.

## Requirements

### DEV-API-01 — What `__GAME_TEST__` offers · MUST

The e2e build (`make e2e-build`, ENG-52) installs `window.__GAME_TEST__` on the game page with five
functions:

| Function | What it does | Requirement |
|----------|--------------|-------------|
| `getState()` | A snapshot of the app: menus, audio, perf, the level played | DEV-API-02 to DEV-API-06 |
| `sendAction(action)` | A menu action, or `bomb` | DEV-API-07 |
| `step(frames, render)` | Runs whole frames, then draws once | DEV-API-08 |
| `advance(seconds)` | Runs the frames of `seconds`, then draws once | DEV-API-08 |
| `readability(share)` | Measures how readable the level's frame is | DEV-API-09 |

The snapshots are plain JavaScript objects with camelCase keys (`selectedId`, `levelResult`), which
Playwright copies out of the page; their lists are copies, so a test cannot change the game's own.
None of it is in the production bundle (`make build` fails if `__GAME_TEST__` is found there, and
`make e2e-build` fails if it is missing from the e2e bundle).

**Acceptance criteria**
- Given the e2e build, then `window.__GAME_TEST__` has the five functions.
- Given the production build, then its bundle does not contain `__GAME_TEST__`.

**Discrepancy:** ENG-52 also lists `setSeed(n)` and `pause()`, and P12-R12 keeps a test-only
`pause()` apart from the game's pause. The API has neither: the game is deterministic without a
seed call, it only moves when stepped, and the game's own pause is sent with `sendAction('pause')`.

*Sources: ENG-52, P11-R08, P12-R12, D-195.*

### DEV-API-02 — The app's state · MUST

`getState()` gives:

| Field | What it is |
|-------|------------|
| `screen` | The current screen ([../ui/screen-flow.md](../ui/screen-flow.md)), `pause` and `settings` included |
| `selection`, `selectedId` | The index selected on the screen, and the id of what it selects |
| `shipId`, `chosenLevelId` | The ship flown (the game's one ship, D-326) and the level chosen |
| `transitioning` | True during a screen transition, while input is ignored |
| `levelResult` | The "Level complete" / "Game over" result while its panel shows, or null: `levelId`, `destroyed`, `spawned`, `outcome`, `score`, `newHighScore` (only when there is one), `checkpoint` (`progress`, `bossesPassed`, `score`, or null) |
| `choice` | The choice selected on a "Game over" panel (0 Continue, 1 level select), or on the `Leave the level?` question (0 No, 1 Yes) |
| `attempt` | Goes up each time a level starts, or starts again from a checkpoint |
| `paused`, `leaving` | Whether the level is paused (pause menu, or settings opened from it), and whether the pause menu asks `Leave the level?` |
| `volumes` | The music and sound effect volumes (`music`, `sfx`), in slider steps |
| `music` | The id of the music playing (`menu`, `level-2-3`, `boss-2`), or null |
| `sounds` | The names of the last sound effects played, most recent last |
| `audio` | The audio context's state (`none` before the first user gesture) |
| `samples` | How many sound effect samples are decoded and ready (0 before the first user gesture) |
| `highScore` | The high score |
| `loadingProgress` | Every progress value the start-up loading screen showed, in order |
| `game` | The level being played (DEV-API-03), or null (in the menus, or while it loads) |
| `perf` | The perf monitor's numbers (DEV-API-06) |

**Acceptance criteria**
- Given a level, when `sendAction('pause')` is sent, then `paused` is true and `screen` is `pause`.
- Given level 2-3 playing, then `music` is `level-2-3`; during its mini boss fight, `boss-2`.
- Given a gun shot, then `sounds` lists the gun shot's sound.

*Sources: P11-R08, P12-R12, ENG-52.*

### DEV-API-03 — The level's state · MUST

`getState().game` gives, for the level being played:

| Field | What it is |
|-------|------------|
| `levelId`, `phase` | The level, and its phase (`playing`, `clearing`, `complete`, `over`) |
| `time`, `duration`, `timeScale` | The level's time and length in seconds, and its time scale (4 when fast-forwarded) |
| `enemies`, `destroyed`, `spawned`, `wavesTriggered` | Enemies on screen, destroyed, spawned, and the waves triggered |
| `player` | The ship's position (`x`, `y`, logical pixels) |
| `firing`, `shots`, `weaponLevel` | Whether the ship fires, its shots in flight, its weapon level |
| `bonuses`, `bonusesDropped`, `bonusKinds` | Bonuses falling, dropped so far, and the kind of each one falling |
| `score`, `bombs` | The score, and the bombs left |
| `enemyShots` | Enemy bullets in flight |
| `health`, `lives`, `invincible` | The ship's health, lives left, and invincibility time left |
| `boss`, `bossesDefeated` | The boss fought (DEV-API-04) or null, and the bosses defeated |
| `groundSpeed` | The ground's speed factor (a boss fight slows it) |
| `checkpoint` | Whether the level has passed a checkpoint |
| `sky` | The look where the view is (DEV-API-05) |

**Acceptance criteria**
- Given a level played in the e2e build, then `game` has `score`, `bombs` and each falling bonus's
  kind in `bonusKinds`, and `highScore` is in the state.

*Sources: P11-R08, ENG-52.*

### DEV-API-04 — The boss's state · MUST

`getState().game.boss` gives, for the boss being fought: `name`, `rank` (`mini` or `final`),
`state` (its state, e.g. `transforming`, `dying`), `stage`, `partsLeft` and `parts` (intact parts and
all its parts), `health` and `fullHealth`, `form` (the transformations done) and `hiddenParts` (the
parts still hidden, revealed by the next transformations). It is null when no boss is fought.

**Acceptance criteria**
- Given `?level=1-3&boss=final`, when K breaks one part in debug mode, then `partsLeft` goes down
  by one and `stage` up by one.

*Sources: ENG-52.*

### DEV-API-05 — The look where the view is · MUST

`getState().game.sky` gives how the level looks where the view is: `weather` and `secondWeather`,
`weatherParticles`, `rainRings`, `lightning`, `flash`, `aurora`, `groundLights`, `sunIntensity`,
`fogEnd`, `lava`, `liquidDepth`, `plumes` and `shotStyle`. The tests of the worlds' looks read them
(the weather, the lights at dusk and night, the debug options of
[debug-options.md](debug-options.md)).

**Acceptance criteria**
- Given `?level=3-3&weather=0`, then `weatherParticles` and `lightning` stay 0.

*Sources: ENG-52.*

### DEV-API-06 — The perf numbers · MUST

`getState().perf` gives the perf monitor's numbers ([perf-tools.md](perf-tools.md)), in
milliseconds: `longFrames`, `longestFrame`, `frames`, `lastLoad` (null before any level has loaded)
and `longestLoadStep`. No test needs the F3 overlay to read them.

**Acceptance criteria**
- Given a level loaded, then `lastLoad` and `longestLoadStep` are numbers.

*Sources: P13-R01, D-113.*

### DEV-API-07 — `sendAction` · MUST

`sendAction(action)` sends a menu action as an input device would (`up`, `down`, `left`, `right`,
`confirm`, `back`, `cancel`, `pause` and `resume`, [../ui/menu-input.md](../ui/menu-input.md)); `bomb`
sets a bomb off, as the bomb key does. Any other action is an error.

**Acceptance criteria**
- Given a level, when `sendAction('bomb')` is sent, then a bomb is fired as with the key.
- Given `sendAction('jump')`, then it throws.

*Sources: P11-R08, P12-R12, ENG-52.*

### DEV-API-08 — The tests step the game · MUST

The e2e build starts no render loop: nothing moves between two calls, so no test waits on game time
and the same calls give the same frames on any machine. `step(frames, render)` runs the whole app
(menus, fades, the level and its loading) by `frames` whole frames of 1/60 s, then draws once,
unless `render` is false. `frames` must be a whole number, 0 or more. `advance(seconds)` runs the
whole frames that last at least `seconds`, then draws once.

**Acceptance criteria**
- Given `step(3, false)`, then three frames run and nothing is drawn; given `step(3)`, then the
  last one is drawn.
- Given `step(-1)` or `step(1.5)`, then it throws.
- Given `advance(0.1)`, then 6 frames run.

*Sources: ENG-52, D-093, D-219.*

### DEV-API-09 — The readability probe · MUST

`readability(share)` measures how readable the level's current frame is, so the readability rules
([../graphics/readability.md](../graphics/readability.md)) can be checked automatically. It draws the
frame twice, as it is and without the playfield (the background alone), reads both back, and
returns a promise of a report:
- for the ship, the first enemy, the first enemy bullet and the first player shot wholly in view
  (`margin` inside the view; player shots at least `shot_ahead` ahead of the ship): the WCAG contrast
  ratio of the brightest pixel round it against the median of the same pixels without the playfield,
  measured within `ship_radius` of the ship, `shot_radius` of a player shot and its hit radius for an
  enemy or a bullet (`player`, `enemy`, `enemyBullet`, `playerShot`; null when none is in view);
- which enemy model was measured (`enemyModel`);
- the background luminance that only `share` of its pixels exceed (`backgroundLuminance`).

Off a level it gives a promise of null; a `share` outside 0..1 is an error. The pixel maths is pure
engine code. The thresholds it is checked against belong to
[../graphics/readability.md](../graphics/readability.md). It does not need the F3 overlay.

**Acceptance criteria**
- e2e: for one level of each world (1-2, 2-1, 3-1, 4-1, at a busy time), the probe measures the
  ship, an enemy, an enemy bullet and a player shot, and the test checks them against the
  readability thresholds.
- Given the title screen, then `readability(0.1)` resolves to null.

*Sources: P14-R08, D-125.*

### DEV-API-10 — What else the e2e build changes · SHOULD

The e2e tests check the game's state, not its frame times, and run on software WebGL. So besides
having no render loop (DEV-API-08), the e2e build:
- does not precompile a level's shaders while it loads (software WebGL compiles them one at a time,
  2 to 4 s per load);
- does not build the highlighted level ahead on the level select (PERF-13);
- shows the F3 perf overlay ([perf-tools.md](perf-tools.md));
- draws fewer pixels, without multisampling (`e2e_render_scale`, no antialiasing).

Everything else, the ground worker included, is as in production.

*Sources: D-115, D-119, D-195.*

### DEV-API-11 — The tests step through a level's loading · SHOULD

The e2e helpers step through a level's loading without drawing its frames, and give the page time
between their checks so the ground worker's messages arrive; they draw the frame where the loading
stopped. Helpers that poll the state step without drawing and draw only the frame where their check
holds, since a drawn level frame costs some 200 ms under software WebGL.

**Acceptance criteria**
- Given a level confirmed in a test, when the helper waits for its load, then the level is playing
  and only the last loading frame was drawn.

*Sources: D-115, D-117, D-219.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| frame | 1/60 s | One stepped frame (ENG-100). `src/config/engine.py` `ENGINE_CONFIG.simulation_hz` |
| `e2e_render_scale` | 0.5 | Pixels drawn per screen pixel, across. `src/config/engine.py` `ENGINE_CONFIG.e2e.render_scale` |
| e2e antialias | off | `ENGINE_CONFIG.e2e.antialias` |
| `ship_radius` | 14 px | `src/config/game_play.py` `GAME_PLAY_CONFIG.readability_probe.ship_radius` |
| `shot_radius` | 5 px | `GAME_PLAY_CONFIG.readability_probe.shot_radius` |
| `margin` | 12 px | `GAME_PLAY_CONFIG.readability_probe.margin` |
| `shot_ahead` | 60 px | `GAME_PLAY_CONFIG.readability_probe.shot_ahead` |

## Notes

- The old debug pages had their own test APIs (`__SCENERY_TEST__`, `__SHOTS_TEST__`); they went with
  the pages (D-187).
- The test API does not report the dev viewers' state (which viewer, which item).
