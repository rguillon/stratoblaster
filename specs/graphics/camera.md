# Camera

> **Area:** Graphics · **Prefix:** `GFX-CAM` · **Related:** [terrain.md](terrain.md), [sky-and-light.md](sky-and-light.md), [props.md](props.md), [../gameplay/screen.md](../gameplay/screen.md), [../performance.md](../performance.md)

The game is seen through one fixed perspective camera above the playfield, tilted forward so the
ground ahead shows at the top of the screen. The playfield (where ships, enemies and shots live) is a
flat plane at the flight altitude; the generated ground scrolls beneath it. This file covers the
world's axes, the camera's placement, what part of the ground it sees and how deep it draws. How the
ships map to the screen and what they may reach is in [../gameplay/screen.md](../gameplay/screen.md).

## Requirements

### GFX-CAM-01 — World units and axes · MUST

One world unit is one logical pixel. X runs across the level (0 under the middle of the playfield),
Z runs along it (the level scrolls towards +Z) and Y is up. The playfield is the 540 × 720 playfield
window ([../gameplay/screen.md](../gameplay/screen.md)) laid flat on a plane at the flight altitude (`flightAltitude`, 320), its bottom edge at the
Z the level has reached. Every scenery height (ground, sea, clouds, props) is an absolute Y.

**Acceptance criteria**
- Given the camera config, then the playfield plane is at Y = `flightAltitude` and the ground's
  heights are below it.

*Sources: P04-R05, D-020.*

### GFX-CAM-02 — Tilted perspective camera · MUST

The camera is a perspective camera above the playfield, tilted `tiltDeg` (35°) from straight down
towards +Z, so it looks forward and the far ground is at the top of the screen. Its vertical field of
view is `fovDeg` (40°). It never turns and never moves across X: it only follows the level along Z.
It draws only into the playfield window's viewport of the canvas (D-252): nothing of the level
shows under the HUD's columns, and its aspect ratio is the window's.

**Acceptance criteria**
- Given the camera config, then the tilt is 35° from vertical towards +Z and the field of view 40°.
- Manual: the camera looks down at the ground, forward, the far ground at the top of the screen.

*Sources: P04-R05, D-020.*

### GFX-CAM-03 — Playfield framing · MUST

The camera stands above the playfield's centre line, behind its bottom edge, at the height where the
bottom and top edges of the window pass through the bottom and top edges of the playfield (about
621 above the flight plane and 166 behind its bottom edge for a 720 px tall window; 552 and 148
for the old 480 × 640, D-249). The framing refuses a tilt and field of view that would show the
horizon. Seen through the tilted camera the playfield is a trapezoid: about 330 of its 540 logical
pixels across the bottom edge and about 556 across the top (a little past the window's side edges
there).

**Acceptance criteria**
- Given the 540 × 720 playfield, then the bottom and top screen rays meet the flight plane at the
  playfield's bottom and top edges (unit test).
- Given a tilt plus half field of view of 90° or more, then framing fails.

*Sources: P04-R05, D-020.*

### GFX-CAM-04 — Ground drawn twice as big · MUST

The ground is drawn `groundScale` (2) times as big as it is generated, as if flying lower. The
terrain, roads, props, cars, water and rain rings hang from one ground node, scaled by `groundScale`
and moved along Z as the view scrolls, so the level still covers the same ground each second and it
passes twice as fast on screen. The clouds and the weather are not scaled. The terrain shader takes
its texture coordinates from the ground point, not the world point, so the textures grow with the
ground. The stage works out its chunks, props and cars in ground units.

**Acceptance criteria**
- Given a distance along the level, then the ground node is at the Z that puts that ground distance
  under the playfield's bottom edge, scaled by `groundScale` (unit test).
- Manual: buildings and roads look about twice the size they had before, clouds unchanged.

*Sources: D-135.*

### GFX-CAM-05 — The ground the camera sees · MUST

The stage works out the ground the camera sees (its near and far Z and its widest half-width) at the
level's lowest ground: the lowest of its relief, its shores' sea beds and its water level. The water
is see-through, so the sea bed under it is seen too, further up the screen than the water's surface
at the same place (D-320; until then the window was worked out at the water level, and a band of
ungenerated ground showed through the water at the top of the screen). The
terrain is generated over that window plus `margin` (80) on every side, so the camera never sees the
edge of the generated ground. The camera never sees the sky above the horizon: the sky only lights
the scene and gives the reflections ([sky-and-light.md](sky-and-light.md)). With the ground drawn
twice as big, about ±390 units of ground show across the playfield window at the sea level
(±435 at a sea bed 55 under it; ±195 on the old 480 × 640 screen, ±500 on the whole 16:9 screen
between D-249 and D-252, ±210 and ±235 in the 540 × 720 window until D-253).

**Acceptance criteria**
- Given a level, then the terrain chunks cover the ground window plus the margin on both sides and
  both ends (unit test).
- Given a level without water, then the window is worked out at its lowest relief, not at 0.
- Given a level with water over a sea bed lower than it (relief or a shore's sea bed), then the
  window is worked out at that sea bed (unit test).

*Sources: P04-R01, D-020, D-064, D-147, D-320.*

### GFX-CAM-06 — Near and far planes · MUST

The camera draws from `near_clip` (200) to `far_clip` (4000). Nothing it draws comes nearer than the
flight plane (about 570 away at its nearest), so a near plane that far out costs nothing and keeps the
depth buffer fine at the ground (about 0.0004 units a step instead of about 0.07 with a near plane at
1). Thin flat parts of props standing just over the ground (plots, decks, lots 0.2 thick) therefore
never fight with it in depth.

**Acceptance criteria**
- Given the stage config, then the near plane stays under half the distance from the camera to the
  flight plane (unit test).
- Manual: in Worlds 1 and 2, the plots and lots of the buildings do not blink against the ground as
  the view scrolls.

*Sources: D-216.*

### GFX-CAM-07 — Drawing order of the ground, the sky and the ships · MUST

The scene is drawn in three groups, each keeping the depth of the one before: first the ground
(terrain, water, roads, props, cars); then the clouds, the weather, the aurora and the lightning
bolts; last what flies (ships, enemies, shots, bonuses). The ground's glow is composed right after
the ground group, so the clouds cover it like the rest of the ground, and neither the clouds nor the
ground's glow ever draw over a ship.

**Acceptance criteria**
- Manual: the lights of the buildings and cars are not brighter under a cloud, and a car's lights
  never show on top of the player ship.

*Sources: P04-R03, P04-R05 (phase 4 review: lights over the ship, lights brighter under the clouds).*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `tiltDeg` | 35° | `src/game/config/scenery_look.py` `PLAYFIELD_CAMERA` |
| `fovDeg` | 40° | vertical field of view, same place |
| `flightAltitude` | 320 | height of the playfield plane, same place |
| `groundScale` | 2 | the ground drawn twice as big, same place |
| `near_clip` | 200 | `src/config/scenery_stage.py` `SCENERY_STAGE_CONFIG` |
| `far_clip` | 4000 | same place |
| `margin` | 80 | ground generated round the window seen, same place |
| camera height over the flight plane | ≈ 621 for a 720 px tall window (552 for 480 × 640) | worked out by `frame_playfield` (`src/render/scenery/playfield_framing.py`) |

## Notes

- The phase 4 spec said "angled 35 %"; it was read as 35° from vertical and accepted (D-020, Q4).
- The trapezoid seen of the playfield was left to the gameplay phase; how ships are kept on screen
  is in [../gameplay/screen.md](../gameplay/screen.md).
- The dev viewers' cameras (orbit, zoom) are in [../dev/dev-menu.md](../dev/dev-menu.md).
