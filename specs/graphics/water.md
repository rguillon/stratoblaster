# Water

> **Area:** Graphics · **Prefix:** `GFX-WATER` · **Related:** [terrain.md](terrain.md), [weather.md](weather.md), [sky-and-light.md](sky-and-light.md), [camera.md](camera.md), [props.md](props.md), [readability.md](readability.md)

A level may have water: the sea, and the rivers, canals, lakes and ponds cut into its ground. All of
them lie under one water level per level, drawn by one see-through plane that reflects the sky and
the sun, while the terrain shader paints the water's colour, the beach and the surf on the ground
itself, so water and land meet with no hard line. Lava, the other liquid the engine can draw on that
level, is in [terrain.md](terrain.md); rain rings on the water are in [weather.md](weather.md).

## Requirements

### GFX-WATER-01 — One water level · MUST

A level has at most one water level (`sea.level`). The sea, rivers, canals, lakes and ponds are all
ground under it: a coast is a section with a `shore` or whose relief lies under the water level (a
**sea section**); a river or a canal is a channel cut below it; a lake or a pond is a basin flattened
below it ([terrain.md](terrain.md)). A level's water is one colour. A waterfall between two stretches
of a river is a set piece ([props.md](props.md)); both stretches are at the same water level.

**Acceptance criteria**
- Given a level with a river channel cut below its water level and no shore, then it has water and no
  sea section.

*Sources: P04-R02, D-079.*

### GFX-WATER-02 — A level without water draws none · MUST

A level whose data has no water level draws no water plane and no rain rings, and the terrain shader
skips its shore code. The ground the camera sees is then worked out at the level's lowest relief
([camera.md](camera.md)). A channel cut into such a level is a dry canyon.

**Acceptance criteria**
- Given a level without `sea`, then the stage has no water plane and no rain rings.

*Sources: P04-R02, D-147.*

### GFX-WATER-03 — The water's surface · MUST

The water plane is a see-through physically based surface (`alpha` 0.4 by default) with a generated
normal map of waves drifting slowly (`drift`), so it reflects the sky's gradient and catches the sun
in a bright glint (`sunGlint`). There is no mirror reflection of the terrain or the props. The plane
follows the camera along Z by whole wave tiles (`tileSize`), so the waves stay put on the ground. It
receives the sun's shadows.

**Acceptance criteria**
- Manual: the sea catches the sun and reflects the sky; its waves move slowly and do not slide with
  the camera.

*Sources: P04-R02, D-020, D-035.*

### GFX-WATER-04 — Water coloured by its depth · MUST

The terrain shader colours the ground under the water level by its depth: from turquoise shallows
(`shallow`) to the colour of the open sea (`deep`) at `depth` under it, mostly covering the ground in
deep water. The sea bed's relief shows faintly through the water. The water plane over it only adds
the reflections and the glints.

**Acceptance criteria**
- Manual: the shallows by the shore are lighter and the water darkens with depth, with no hard line
  where the water plane meets the ground.

*Sources: P04-R02, D-035.*

### GFX-WATER-05 — Beach · MUST

Above the water, on gentle slopes, the ground turns to a sand beach (`sand`) over `beach` of height,
fading into the ground's own texture, darker where the swash wets it. Steep shores get no beach.

*Sources: P04-R02, D-035.*

### GFX-WATER-06 — Surf · MUST

Where the water meets the land, a broken line of foam swashes up and down the beach, and bands of
foam roll in from the shallows (`foam`: colour, width, spacing, speed and reach), broken up by noise,
so the shore looks natural.

**Acceptance criteria**
- Manual: a coast shows a sand beach, shallows darkening with depth and broken surf rolling in.

*Sources: P04-R02, D-035.*

### GFX-WATER-07 — Flowing water · MUST

A level's water drifts its waves by its look's `drift`. River and canal water flows down the screen,
the way the player came from (a drift of [0, 16]), and its waves stay on the water as the view
scrolls.

**Acceptance criteria**
- Manual (on a level with a river): the river flows down the screen.

*Sources: P09-R06, D-079.*

### GFX-WATER-08 — Banks and quays · SHOULD

A river or canal's banks are its channel's walls: wide sloping banks (grass) or narrow steep walls
(stone quays and embankments), set by the channel's wall width. No level has rivers, canals or quays
now: World 3 has no water and World 4 is city ground only (reviewer, 2026-10-28).

*Sources: P09-R03, P10-R03, D-079.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `sea.alpha` | 0.4 | `src/game/config/scenery_look.py` `BASE_SCENERY_LOOK.sea` |
| `sea.roughness` / `sunGlint` | 0.3 / 1.6 | same place |
| `sea.normalMap` | 256 px, frequency 5, 3 octaves, strength 4 | same place |
| `sea.tileSize` | 320 | the plane moves by whole tiles |
| `sea.drift` | [3, 7] (sea); [0, 16] (rivers, `RIVER_FLOW`) | `src/game/config/world_3/looks.py` |
| `shore.sand` / `beach` | [0.72, 0.62, 0.45] / 4 | `BASE_SCENERY_LOOK.terrain.shore`; World 1 sets its own colours (`src/game/config/world_1/looks.py` `TERRAIN`) |
| `shore.shallow` / `deep` / `depth` | [0.1, 0.5, 0.48] / [0.03, 0.17, 0.2] / 30 | same place |
| `shore.foam` | width 0.7, spacing 2.5, speed 0.3, reach 7 | same place |
| channel `wall` | 45 (banks), 14 (quays) | `src/game/config/world_3/scenery.py` `river`, `src/game/config/world_4/scenery.py` `quays` |

## Notes

- Today only World 1's 1-1 and 1-2 have water (the open sea and the coast); Worlds 2 to 4 have none
  (D-147 for World 4; reviewer, 2026-10-28 for World 3). See the world files.
- Known limitations: no mirror reflection (a second render of the scene costs too much); the wave
  pattern repeats every `tileSize`; with the water switched off, the ground under it has no tint.
