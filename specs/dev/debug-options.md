# Debug options

> **Area:** Dev · **Prefix:** `DEV-OPT` · **Related:** [dev-menu.md](dev-menu.md), [perf-tools.md](perf-tools.md), [test-api.md](test-api.md), [../gameplay/level-flow.md](../gameplay/level-flow.md), [../gameplay/controls.md](../gameplay/controls.md), [../graphics/weather.md](../graphics/weather.md), [../graphics/sky-and-light.md](../graphics/sky-and-light.md), [../graphics/roads.md](../graphics/roads.md), [../bosses/common.md](../bosses/common.md)

So the levels, which last 4 to 5 minutes, can be checked by hand, the game page reads debug options
from its URL (for example `?level=1-3&t=120`): start any level straight away, at a given time or at
a boss, with the weather off, a forced time of day or the tile grid drawn. The `level` option turns
**debug mode** on, which adds playback keys and the FPS / polygons tile. Without these options the
game ignores the debug keys. The options are read once, when the page opens.

| Option or key | What it does | Requirement |
|---------------|--------------|-------------|
| `level=<id>` | Starts that level straight away, debug mode on | DEV-OPT-01 |
| `t=<seconds>` | Starts at that time | DEV-OPT-02 |
| `boss=mini`, `boss=final` | Starts at that boss's arrival | DEV-OPT-03 |
| `weather=0` | No weather | DEV-OPT-04 |
| `look=<time of day>` | Forces the time of day | DEV-OPT-05 |
| `tiles=1` | Draws the tile grid over the districts | DEV-OPT-06 |
| F, ← / → | Fast forward, jump back / on (debug mode) | DEV-OPT-08 |
| K | Breaks the boss's next part (debug mode) | DEV-OPT-09 |
| F2 | Shows or hides the FPS / polygons tile (any level) | [perf-tools.md](perf-tools.md) DEV-PERF-05 |
| F3 | Shows or hides the perf overlay (dev and e2e builds) | [perf-tools.md](perf-tools.md) DEV-PERF-03 |
| `dev` | Adds the Dev entry to the title screen | [dev-menu.md](dev-menu.md) DEV-MENU-01 |

## Requirements

### DEV-OPT-01 — `?level=` starts a level straight away · MUST

With `level=<id>` in the URL (for example `?level=2-4`), the game starts that level as soon as the
menus have loaded, skipping the title and level select screens. It is flown with the game's one
ship (`player`); there is no `ship=` option any more (D-326). Every level of every world is
accepted (1-1 to 4-5). The `level` option turns debug mode on; the other options of this file only
act with it. Without `level` (or with an empty one) there are no debug options. A level the game
does not know starts nothing: the title screen shows.

**Acceptance criteria**
- Given `?level=1-3`, then level 1-3 is being played, with the player ship.
- Given no `level` in the URL, then the game opens on its title screen and there is no debug mode.

*Sources: P06-R09, P08-R12, P09-R11, P10-R13, D-326.*

### DEV-OPT-02 — `t=` starts at a time · MUST

`t=<seconds>` starts the level at that time of its scroll, with the waves that come before it
skipped. A missing, negative or unreadable value starts at 0. The start time applies to the first
level played only, not to a Retry, a Continue or the next level.

**Acceptance criteria**
- Given `?level=1-3&t=120`, then 1-3 starts at 2:00, with the waves before 2:00 skipped: only its
  mini boss, arriving at 2:00, has come in.
- Given `?level=2-4&t=150`, then 2-4 starts at 2:30.
- Given `?level=3-3&t=120`, then 3-3 starts at 2:00, in its thunderstorm.

*Sources: P06-R09, P08-R12, P09-R11.*

### DEV-OPT-03 — `boss=` starts at a boss · MUST

`boss=mini` or `boss=final` starts the level at that boss's arrival, instead of at `t`. Any other
value is ignored. Like `t`, it applies to the first level played only.

**Acceptance criteria**
- Given `?level=1-3&boss=final`, then 1-3 starts at its final boss's arrival.
- Given `?level=4-5&boss=final`, then 4-5 starts at the Caldera Throne's arrival, over the magma
  lake, in the eruption look.
- Given `?level=2-1&boss=final`, then 2-1 starts at the Narwhal's arrival.

*Sources: P07-R09, P08-R12, P10-R13.*

### DEV-OPT-04 — `weather=0` turns the weather off · MUST

`weather=0` turns the level's weather off (its rain, snow, lightning, falling ash or embers), to
compare looks. Any other value keeps the level's own weather.

**Acceptance criteria**
- Given `?level=3-3&weather=0`, then 3-3 shows no rain and no lightning.
- Given `?level=4-2&weather=0`, then 4-2 shows no falling ash.
- Given no debug option, then the weather is the level's own.

*Sources: P08-R12, P09-R11, P10-R13.*

### DEV-OPT-05 — `look=` forces the time of day · MUST

`look=<time of day>` forces the level's time of day, to compare looks: `dawn`, `morning`, `midday`,
`afternoon`, `dusk` or `night`. Any other value keeps the level's own.

**Acceptance criteria**
- Given `?level=2-5&t=120&look=midday`, then 2-5 (a night level) is lit as at midday: brighter
  sun, its ground lights off.
- Given no debug option, then the time of day is the level's own.

*Sources: P08-R12, P09-R11, P10-R13.*

### DEV-OPT-06 — `tiles=1` draws the tile grid · MUST

`tiles=1`, with the other options (for example `?level=4-5&tiles=1`), draws the grid of tiles over
the districts, to check how the road kit and the buildings sit on it
([../graphics/roads.md](../graphics/roads.md)). Any other value draws no grid.

**Acceptance criteria**
- e2e: given 1-5, 2-5, 3-3 and 4-5 with `t=200&tiles=1`, then each plays over its districts with the
  grid drawn, without console errors.

*Sources: P15-R10.*

### DEV-OPT-07 — The debug options work in every build · SHOULD

The URL debug options and their keys work in every build, the deployed production build included,
so a reviewer can check the levels on the live site.

**Acceptance criteria**
- Given the deployed game with `?level=3-1`, then 3-1 starts straight away and F, ← / → and K work.

*Sources: D-039.*

### DEV-OPT-08 — Playback keys · MUST

In debug mode, during play:
- F toggles fast forward: the level runs `fast_forward` times as fast, and F again returns to normal
  speed;
- ← and → jump `seek_step` seconds back and on along the level.

The ← and → keys then do not move the ship; A and D (and the gamepad and touch) still do.

**Acceptance criteria**
- Given `?level=1-3&t=120`, when F is pressed, then the level's time scale is 4; when → is pressed,
  then the level's time moves on by at least 10 s.

*Sources: P06-R09, D-039.*

### DEV-OPT-09 — K breaks the boss's next part · MUST

In debug mode, K destroys the next intact part of the boss being fought (hidden parts are skipped),
then its core once no part is left, so each stage, transformation and death can be checked quickly.
During a transformation, K ends it at once. Without a boss, or while it is dying, K does nothing.

**Acceptance criteria**
- Given a boss being fought in debug mode, when K is pressed, then one more part is destroyed and
  the stage goes up by one.
- Given K pressed until the boss is gone, then the level goes on as after a real kill (a final boss's
  death completes the level).

*Sources: P07-R09.*

### DEV-OPT-10 — Without debug mode the debug keys do nothing · MUST

Without the URL debug options, F, ← and → (as playback keys) and K change nothing in the level: the
arrows move the ship as usual, and the level's time and speed are untouched. No debug key acts while
the game is paused.

**Acceptance criteria**
- Given a level started from the menus, when F, → and → are pressed, then the time scale stays 1 and
  the time is not moved on, and no FPS / polygons tile shows.
- Given a level started from the menus, when K is pressed during a boss fight, then no part is
  destroyed.

*Sources: P06-R09, P07-R09.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `fast_forward` | 4 | Time scale while F is on. `src/config/game_play.py` `GAME_PLAY_CONFIG.debug.fast_forward` |
| `seek_step` | 10 s | Jump of ← / →. `GAME_PLAY_CONFIG.debug.seek_step` |
| default ship | `player` | The first ship of `src/game/config/player_ships.py` |
| times of day | dawn, morning, midday, afternoon, dusk, night | `src/core/scenery/atmosphere.py` `TIMES_OF_DAY` |

## Notes

- The old debug pages (`player_shots/`, `enemies/`, `bosses/`, `props/`, `level_zero/`) took their
  own options and keys; they were removed (D-161, D-187). The Dev menu ([dev-menu.md](dev-menu.md))
  replaces the model views, with K in its bosses viewer.
- Level Zero, which the old `tiles=1` acceptance test also loaded, was removed (D-161).
