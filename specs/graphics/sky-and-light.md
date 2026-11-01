# Sky and light

> **Area:** Graphics · **Prefix:** `GFX-SKY` · **Related:** [camera.md](camera.md), [terrain.md](terrain.md), [weather.md](weather.md), [buildings.md](buildings.md), [readability.md](readability.md), [art-direction.md](art-direction.md)

Each level is lit by a look: a time of day (the sun or the moon, the ambient light, the haze, the
sky's colours for reflections), two cloud layers between the ground and the ships, a haze, the
strength of the ground's lights and, optionally, mist, tints and a glow from below. The look may
change along the level, every number blending smoothly. The camera never sees the sky itself: the
"sky" only lights the scene and colours its reflections. Each level's own look is in its level file;
weather is in [weather.md](weather.md).

## Requirements

### GFX-SKY-01 — Sun, moon and ambient light · MUST

A scene has one directional light, the sun (or, at night, a dim cold moon), set by its elevation,
azimuth, colour and intensity, and a hemispheric ambient light with a sky colour, a ground colour
and an intensity. The ships, the enemies and the ground are all lit by them.

**Acceptance criteria**
- Given a look, then the sun's direction comes from its elevation and azimuth (unit test).

*Sources: P06-R10, P08-R04, D-020, D-064.*

### GFX-SKY-02 — Stable shadows · MUST

The sun casts soft (percentage-closer filtered) shadows from the terrain and the props onto the
ground. The shadow frustum is fixed (`frustum`, 1600 units round the ground in view) instead of fitted
to the scene every frame, and the sun's position moves by whole shadow texels across the light, so
shadows do not swim as the view scrolls. Beyond the frustum there are no shadows; it covers what the
camera sees. The shadows' darkness is the look's, softened by a heavy cloud cover (GFX-SKY-06).

**Acceptance criteria**
- Given two views a fraction of a texel apart, then the sun's position is the same (unit test).
- Manual: shadows hold still as the ground scrolls.

*Sources: D-020, D-024.*

### GFX-SKY-03 — Six times of day · MUST

The engine has six times of day: `dawn`, `morning`, `midday`, `afternoon`, `dusk` and `night`. Each sets
the sun's elevation, azimuth, colour and strength, the haze colour, the sky gradient used for
reflections, the environment's intensity, the ambient light, the clouds' colour and edge colour, the
strength of the ground's lights and a factor on the fog distances (the haze comes closer at dusk and
at night). At night the sun is a dim, cold moon, and the reflection gradient is moonlit, so the
ships' metal still catches light and keeps its shapes and colours.

**Acceptance criteria**
- Given the presets, then the six names exist and each has its sun, sky, ambient, clouds, ground
  lights and fog (unit test).

*Sources: P08-R04, D-064.*

### GFX-SKY-04 — A look for every level · MUST

Every level has its own look, so the light and the shadows differ from level to level. A look gives
its light either directly (sun, sky, ambient, fog and cloud values: World 1) or as a sky script: a time
of day, the cover of the two cloud layers and the optional fields below, resolved with the engine's
presets. A level's time of day does not change within it unless its look says so with a look change.

**Acceptance criteria**
- Given a sky look, then it resolves to the time of day's light with its cloud cover (unit test).
- Manual: the light and the shadows change from level to level.

*Sources: P06-R10, P08-R04, D-064.*

### GFX-SKY-05 — Look changes along the level · MUST

A look may change to another over a stretch of the level (`from`, `to`, in seconds of scrolling from
the level's start, turned into distances at the level's speed). Every number blends with a smooth
ease, halfway being exactly half: colours and numbers linearly, the sun's azimuth the short way
round, a weather's kind kept from the side that has some. The blend follows the ground's distance,
so a debug jump into the level starts with the look of that distance, without a jump in the look.

**Acceptance criteria**
- Given a change from A to B between d1 and d2, then at d1 the look is A, at d2 it is B, and halfway
  every number is halfway (unit test).
- Given a change that ends before it starts, then it is refused.

*Sources: P08-R04, D-064.*

### GFX-SKY-06 — Cloud cover and overcast · MUST

A look sets the cover of each cloud layer, from 0 (clear sky) to 1 (overcast). A heavy low cover
(from 0.45, full at 1) dims the sun (up to 60 %), softens the shadows, raises the ambient light (up to
45 %), greys the haze (up to 35 %) and makes the layers see-through (up to 65 %), so the ground still
shows from above. A look's `storm` (0..1) turns the clouds towards a dark storm grey.

**Acceptance criteria**
- Given a heavy cover, then the sun is dimmer and the ambient light brighter than in clear weather;
  a clear sky keeps the time of day's light and fog (unit tests).

*Sources: P08-R04, D-064.*

### GFX-SKY-07 — Haze and fog · MUST

A look has a fog that starts and ends at given distances, in the haze's colour, and the clear colour
of the scene is the haze. The time of day scales the fog distances; weather brings the fog's end in to
its kind's `fog_at_1` share at strength 1 and its start half as much ([weather.md](weather.md)).

**Acceptance criteria**
- Given clear weather, then the fog is the time of day's; given weather at strength 1, then the fog
  ends at its kind's share of the distance (unit test).

*Sources: P08-R04, D-064.*

### GFX-SKY-08 — Ground lights and brightness · MUST

The strength of the ground's lights (windows, street, neon and car lights) follows the time of day:
nearly off by day, on at dusk and at night. A look may set it itself (`groundLights`) and may scale
the sun and the ambient light (`brightness`), e.g. a bright midday city with its windows and cars lit
as at night.

**Acceptance criteria**
- Given a look with `groundLights`, then the ground lights take it instead of the time of day's.

*Sources: P08-R04, D-064, D-126.*

### GFX-SKY-09 — Shapes stay visible at night · MUST

At night the ground is dark, but its shapes can still be seen in the moonlight and by the ground's
lights, and the player ship and the enemies get enough light (the moon, the moonlit reflections) to
show their shapes and colours. The readability checks themselves are in
[readability.md](readability.md).

**Acceptance criteria**
- Manual: in a night level, the ground's shapes and the ships' shapes and colours are clearly seen.

*Sources: P08-R04, D-064.*

### GFX-SKY-10 — Sky reflections · MUST

The sky's gradient (under the horizon, at it, a little above and straight up) is turned into a cube
of reflections for the water and the ships' metal, rebuilt only when the gradient changes, at the
look's environment intensity. No sky dome is drawn: the tilted camera never sees the sky.

*Sources: D-020, D-064.*

### GFX-SKY-11 — Cloud layers · MUST

A level has up to two cloud layers, a low and a high one, between the highest ground and the ships.
Each is a plane that follows the camera and drifts at its own speed and direction (`drift`), drawn
from a generated noise texture cut at a threshold set by its coverage, so the coverage is the share of
the sky it covers. Each layer has a coverage, an opacity, a softness of its edges, a colour and a
colour for its thin edges. No layer is ever above the ships, so clouds never hide bullets or
enemies.

**Acceptance criteria**
- Given a layer at coverage 0, then it shows no cloud; at 1 it covers the sky.
- Manual: the clouds drift with depth between the ground and the ships.

*Sources: P04-R03, D-020.*

### GFX-SKY-12 — Clouds above the ground and its buildings · MUST

Each cloud layer flies at its look's altitude, raised if needed to stay `cloud_clearance` (15) above
the level's terrain ceiling, drawn at the ground's scale ([terrain.md](terrain.md)), so clouds never
pass through the terrain. A level's ground and buildings are low enough that the tallest building it
can place, standing on its terrain ceiling, stays the clearance under its lowest layer, so no
building pierces or fights with a cloud layer.

**Acceptance criteria**
- Given any level, then its cloud layers are at least the clearance above its terrain ceiling (unit
  test).
- Given each World 4 level, then its terrain ceiling plus its tallest building, scaled, stays the
  clearance under the lowest cloud layer (unit test).

*Sources: P04-R03, D-022, D-196.*

### GFX-SKY-13 — Cloud colours · MUST

The clouds take their colour from the time of day (pink-orange at dawn and dusk, white at midday,
blue-grey at night), turned towards dark grey by a storm. A look may tint them (`cloudTint`, factors
on their colours), or keep the time of day's colours whatever the storm, tint or glow from below
(`plainClouds`).

**Acceptance criteria**
- Given a storm, then the clouds are greyer; given `plainClouds`, then they are not (unit test).

*Sources: P08-R04, D-064, D-083.*

### GFX-SKY-14 — Clouds lit from below · MUST

A look may have a glow from below (`underglow`: a colour and a strength 0..1), as fire, lava or a
city's lights light the sky from the ground: at strength 1 the clouds' edges turn 75 % of the way to
its colour, their body 20 % (dark smoke stays dark), the haze 35 % and the ambient light from the
ground 60 %. It blends like any number, so a look change can make it grow as the sun sets.

**Acceptance criteria**
- Given an underglow, then the clouds' colours move towards its colour by those shares (unit test).

*Sources: D-083.*

### GFX-SKY-15 — Mist · MUST

A look may have a mist (`mist`: `fog`, `white`): the fog ends at `fog` of its usual distance (its start
half as much) and the haze turns `white` of the way to a pale mist colour. A look change can lift it
(e.g. a morning mist over the first half of a level).

**Acceptance criteria**
- Given a mist, then the fog comes closer and the haze is paler; a change to a look without mist
  blends it away (unit test).

*Sources: D-078.*

### GFX-SKY-16 — Ambient tint · SHOULD

A look may tint the ambient light (`tint`: factors on the ambient sky and ground colours), e.g. a dim
yellowish light under an ash cloud.

*Sources: D-078.*

### GFX-SKY-17 — Aurora · SHOULD

A look may have an aurora (strength 0..1): a sheet just above the highest cloud layer with two slowly
bending curtains (green, violet) and fine rays, added on top and strongest in the far haze, moving
over tens of seconds, never flashing. No level has one now.

*Sources: D-065.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| times of day: sun elevation / azimuth / strength | dawn 9° / −62° / 1.45; morning 30° / 48° / 1.75; midday 62° / 20° / 1.7; afternoon 34° / 42° / 1.6; dusk 7° / 66° / 1.15; night (moon) 42° / −28° / 0.6 | `src/config/time_of_day.py` `TIME_OF_DAY` |
| times of day: ground lights | 0.7 / 0.15 / 0.1 / 0.2 / 1.2 / 1.5 | same order, same place |
| times of day: fog factor | 1 / 1 / 1 / 1 / 0.95 / 0.85 | same order, same place |
| overcast | from cover 0.45 to 1: sun −60 %, ambient +45 %, haze grey 35 %, thinning 65 % | `OVERCAST`, same place |
| underglow | edges 75 %, body 20 %, haze 35 %, ground 60 % | `UNDERGLOW`, same place |
| mist colour | (0.9, 0.92, 0.9) | `MIST_COLOR`, `src/core/scenery/sky_look.py` |
| shadows | map 2048, frustum 1600, bias 0.0008, normal bias 0.6, darkness 0.35 | `src/game/config/scenery_look.py` `BASE_SCENERY_LOOK.sun.shadow` |
| `sun_distance` | 2500 | `src/config/scenery_stage.py` |
| cloud layers (base look) | low: altitude 265, coverage 0.3, opacity 0.75, tile 1100, drift (6, 3), softness 0.12; high: 295, 0.2, 0.5, 1600, (10, −2), 0.18 | `BASE_SCENERY_LOOK.clouds` |
| `cloud_clearance` | 15 | `src/config/scenery_stage.py` |
| World 4 daylight | `groundLights` 1.5, `brightness` 1.3, `plainClouds` | `src/game/config/world_4/looks.py` `DAYLIGHT` |

## Notes

- Per world, briefly: World 1's looks give their light directly, from midday (1-1) to dusk (1-5);
  World 2 goes morning to night; World 3 morning to night with mist, rain and a storm; World 4 is a
  bright midday city with a glow from below. See the level files.
- The background is darkened at the source: each world's tone dims the props' lit colours, the haze
  and the clouds as the atmosphere is resolved (`SceneryLook.tone`, `toned` in
  `src/render/scenery/atmosphere_of.py`); that rule and the tones are in
  [readability.md](readability.md) (GFX-READ-02).
- Known limitations: the clouds cast no shadow on the ground, and their shader skips the scene's
  tone mapping.
