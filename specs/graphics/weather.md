# Weather

> **Area:** Graphics · **Prefix:** `GFX-WEATHER` · **Related:** [sky-and-light.md](sky-and-light.md), [water.md](water.md), [props.md](props.md), [readability.md](readability.md), [../dev/debug-options.md](../dev/debug-options.md), [../performance.md](../performance.md)

A level's look may have weather: particles falling or rising through the air between the ground and
the flight altitude, behind everything that flies. The engine has four kinds as data (snow, rain,
falling ash, rising embers), two of which can fall at once, plus lightning on top of a storm and rain
rings on the water. Weather is only a look: nothing in the simulation reads it. Smoke and steam
plumes rise from props and are in [props.md](props.md). Which level has which weather is in the
level files.

## Requirements

### GFX-WEATHER-01 — Weather kinds as data · MUST

A look's weather is a kind and a strength from 0 (none) to 1 (heaviest). The kinds are data
(`WEATHER_KINDS`): the most particles at strength 1, how near the fog comes at 1, the fall speed
range, the sideways wind at strengths 0 and 1, the particle size range, how much a particle streaks
at 1, its sway, its colour and opacity and the box of air it fills, plus optional fields any kind may
use: `align` (stretch each particle along its fall instead of sideways), `haze` (the haze turns a
share of the way to a colour), `rings` (rings on the water), `blend` (`add`: added onto what is
behind), `flicker` and `fade_high` (fade out over the top share of the box). A new kind needs no
change to how levels use weather.

**Acceptance criteria**
- Given the weather config, then snow, rain, ash and embers are kinds with all their fields in range
  (unit test).

*Sources: P08-R05, D-065, D-076, D-082.*

### GFX-WEATHER-02 — Particles in a box of air that scrolls with the ground · MUST

A weather's particles fill a box of air round the view (`volume`: about ±420 across, 1100 along,
from the ground to 300 high) that follows the view along Z, while each particle keeps its world Z, so
the particles scroll with the ground, at different depths between the clouds and the ground. They
fall, sway and are blown along X by a wind growing with the strength, all on the GPU, and fade into
the haze. Each kind present is one mesh of quads drawn in one draw call; nothing is uploaded per
frame.

**Acceptance criteria**
- Manual: snow and rain fall with depth and scroll with the ground.

*Sources: P08-R05, D-065.*

### GFX-WEATHER-03 — Strength · MUST

At strength 0 no particle is drawn; at strength 1 the kind's `max_particles` are; in between, in
proportion (the first `round(max × strength)` quads). The strength also sets how near the fog comes
(to `fog_at_1` of its distance at 1, its start half as much) and how far the haze turns to the kind's
colour.

**Acceptance criteria**
- Given a weather of strength 0, then no particle is drawn; of strength 1, the kind's most (unit
  test).

*Sources: P08-R05, P09-R05, P10-R06, D-065.*

### GFX-WEATHER-04 — Drawn behind what flies · MUST

Weather is drawn after the cloud layers, in the group under the ships, without writing depth, so
every ship, enemy, shot and bonus is drawn over it, and the terrain hides the particles behind its
hills. Flakes between the camera and the clouds are drawn over the clouds, as falling snow is. Even
at strength 1 the particles stay faint and never hide the player ship, the enemies, their shots or
the bonuses.

**Acceptance criteria**
- Manual: in the heaviest weather, the enemy shots and the bonuses are still easy to see.

*Sources: P08-R05, P09-R05, P10-R06, D-065.*

### GFX-WEATHER-05 — Weather is only a look · MUST

Weather (rain, lightning and rain rings included) never changes how anything moves, shoots or takes
damage: it is not an input of the simulation. A level played with and without its weather (debug
option `weather=0`, which clears both weathers and the lightning) has the same waves, paths, shots and
damage.

**Acceptance criteria**
- Unit test: the simulation does not read the weather.

*Sources: P08-R05, P09-R05, P10-R06, D-076, D-077.*

### GFX-WEATHER-06 — Weather changes along the level · MUST

Weather is part of the look, so a look change can start it, stop it or grow it (e.g. snow growing
into a blizzard, a shower over the middle third of a level, embers growing to their strongest at the
final boss). A blend between two kinds keeps the kind of the side that has some.

**Acceptance criteria**
- Given a change from no weather to a weather, then the kind is the weather's and the strength grows
  over the change (unit test).

*Sources: P08-R05, D-064.*

### GFX-WEATHER-07 — Snow · MUST

Snowflakes are soft white discs (opacity 0.5) falling slowly (26–48 units/s) and swaying, drifting a
little sideways; at strength 1 (a blizzard) they are dense (1 500) and streak sideways in a strong
wind, and the fog ends at 55 % of its clear distance. No level has snow now.

*Sources: P08-R05, D-065.*

### GFX-WEATHER-08 — Rain · MUST

Rain is thin, light streaks (2 000 at strength 1, 0.35–0.55 wide and 16 times as long, opacity 0.32)
falling fast (380–520 units/s) at a slight slant (a wind of 30–70), each stretched along its fall at
every strength. The haze comes closer and greyer with the strength (fog end at 60 % at 1, the haze
45 % of the way to grey).

**Acceptance criteria**
- Manual: rain looks light and fast; shots and bonuses stay visible through it.

*Sources: P09-R05, D-076.*

### GFX-WEATHER-09 — Rain rings on the water · MUST

Where it rains on a level with water, faint rings spread on it: a plane at the water level follows
the view, and in each 9-unit cell a ring spreads from a random point to 2.2 across over 0.8 s and
fades, fewer cells ringing in light rain. The plane writes no depth, so the terrain above the water
hides it: rings show on the sea, rivers, lakes and ponds only. It is drawn right after the water, in
one draw call.

**Acceptance criteria**
- Given rain of strength 0 or no water, then no ring shows.

*Sources: P09-R05, D-076.*

### GFX-WEATHER-10 — Lightning strikes · MUST

A storm's look may have lightning (strength 0..1, blended like any number). Strikes come at random
times drawn from the level's seed, so the same level flashes at the same times every play: one strike
every 4–10 s, each one flash or, with a chance of 0.35, two flashes 0.25 s apart. A flash rises in
0.03 s and fades out by 0.15 s. There are never more than 3 flashes in any 1 s. Strikes follow the
scene's clock, so they still come while the ground stops for a fight.

**Acceptance criteria**
- Unit test: over a long storm, never more than 3 flashes in any 1 s window, and the gap between
  strikes is within 4–10 s.
- Unit test: the same seed flashes at the same times.

*Sources: P09-R05, D-077.*

### GFX-WEATHER-11 — Lightning flash · MUST

A flash lights the whole scene for a moment: the ambient light, the haze (clear colour and fog) and
the environment's intensity are multiplied by up to `1 + 0.8 × flash × lightning` (at most 1.8 times
the storm's), no haze channel going past 0.85, so the playfield never turns white. A flash never
touches the ships' neon or the shots, and no overlay is drawn over the screen. These limits keep the
lightning mild for players with photosensitivity.

**Acceptance criteria**
- Manual: lightning is dramatic but not blinding; shots and bonuses stay visible.

*Sources: P09-R05, D-077.*

### GFX-WEATHER-12 — Lightning bolts · MUST

Some strikes (60 %) also draw a jagged bolt with two forks, shaped from the strike's seed, flat in the
lowest cloud layer, added on top while the strike's flashes last.

*Sources: P09-R05, D-077.*

### GFX-WEATHER-13 — Falling ash · MUST

Falling ash is grey flakes (1 500 at strength 1, opacity 0.42) falling slowly (12–26 units/s) and
drifting, like a dull snow; with the strength the haze comes closer (fog end at 50 % at 1) and turns
brown-grey (60 % of the way).

*Sources: P10-R06, D-082.*

### GFX-WEATHER-14 — Rising embers · MUST

Embers are small glowing orange sparks (800 at strength 1, 0.45–0.85 across) rising from the ground
and drifting up past the camera (a negative fall of 28–58 units/s), added onto what is behind them,
flickering as they cool (by up to 65 %, 4.5 times a second) and fading out over the top 45 % of their
box of air. They are never mistaken for enemy bullets: smaller than any bullet (bullets are 4 in
radius, drawn 6.4), with no outline or glow ring, and they only move up the screen.

**Acceptance criteria**
- Manual: in the heaviest embers, embers are never confused with enemy bullets.

*Sources: P10-R06, D-082.*

### GFX-WEATHER-15 — Two weathers at once · MUST

A look may have a second weather (`secondWeather`) falling at the same time as its weather (e.g.
falling ash and rising embers). Both bring the fog in and tint the haze, each kind is its own mesh,
and a look change blends the second weather from or to none.

**Acceptance criteria**
- Given a look with two weathers, then both kinds are drawn; `weather=0` clears both.

*Sources: P10-R06, D-082.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| snow | 1 500; fog 0.55; fall 26–48; wind 6→120; size 1.4–2.6; streak 4; sway 6 @ 0.35 Hz; opacity 0.5 | `src/config/weather.py` `WEATHER_KINDS["snow"]` |
| rain | 2 000; fog 0.6; fall 380–520; wind 30–70; size 0.35–0.55; streak 16; opacity 0.32; haze 0.45 to grey | `WEATHER_KINDS["rain"]` |
| rain rings | cell 9, 1 per cell, radius 2.2, 0.8 s, alpha 0.32 | `WEATHER_KINDS["rain"].rings` |
| ash | 1 500; fog 0.5; fall 12–26; wind 4–36; size 1–1.9; opacity 0.42; haze 0.6 to brown-grey | `WEATHER_KINDS["ash"]` |
| embers | 800; fog 0.92; fall −58 to −28; wind 6–26; size 0.45–0.85; opacity 0.9; added; flicker 0.65 @ 4.5 Hz; fade over top 45 % | `WEATHER_KINDS["embers"]` |
| box of air | ±420 across, 1100 along, 0–300 high (embers 0–280) | `_VOLUME` |
| lightning | gap 4–10 s; flash 0.15 s, rise 0.03 s; double 0.35, 0.25 s apart; ×1.8 at most; haze ≤ 0.85; bolt 0.6; ≤ 3 per second | `src/config/weather.py` `LIGHTNING` |

## Notes

- Per world, briefly: no level has snow now (World 2 lost it in its rework); World 3 has rain and a
  thunderstorm with lightning; World 4 has falling ash and rising embers, both at once in 4-4. See the
  level files.
- Smoke and steam plumes are not weather: they rise from props ([props.md](props.md)).
- The `weather=0` and `look=` debug options are in [../dev/debug-options.md](../dev/debug-options.md).
- Known gap: the unit test of GFX-WEATHER-05 was not carried over to the Python port. The simulation
  (`src/core/systems/`) imports nothing of the atmosphere, the sky looks or the weather, so it cannot
  read them.
