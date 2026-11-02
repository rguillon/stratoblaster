# Terrain

> **Area:** Graphics · **Prefix:** `GFX-TERRAIN` · **Related:** [camera.md](camera.md), [water.md](water.md), [sky-and-light.md](sky-and-light.md), [roads.md](roads.md), [props.md](props.md), [readability.md](readability.md), [../performance.md](../performance.md), [../worlds/world-1/world.md](../worlds/world-1/world.md)

Every level's ground is a height field generated from the level's data and seed: a row of sections
along the level, each a fractal relief with optional sculpt operations, dunes or scarps (hills with
one steep face), blending into the next. The ground is coloured by textures generated in code,
mixed by altitude, slope and each section's ground cover (grass, concrete, sand), and drawn in
chunks around the camera. This file also covers the
ground's glow layer and lava, a liquid the engine keeps but no level uses now. Which sections, covers
and colours each level has is in the world and level files.

## Requirements

### GFX-TERRAIN-01 — Ground made of sections · MUST

A level's ground is a list of sections laid end to end along Z from 0. Each section lasts `seconds`
at the level's scroll speed and has a name (shown by the debug tools), a relief and optional sculpt
operations, ground cover, street grid and prop densities. Before Z = 0 and past the level's end, the
ground goes on as the first and the last section. The ground is a pure function of the level and its
seed: the same seed gives the same heights everywhere, in any order they are asked for.

**Acceptance criteria**
- Given a level, then its sections are placed end to end from Z = 0 and each Z finds its section.
- Given the same level and seed twice, then every height is the same; another seed changes them.

*Sources: P04-R01, D-020.*

### GFX-TERRAIN-02 — Fractal relief · MUST

Each section's relief is fractal noise added to a base height: `smooth` (rolling ground from
`base − amplitude` to `base + amplitude`) or `ridged` (sharp crests from `base` up to
`base + amplitude`, mountain ranges), with a frequency and a number of octaves. A `max_height` softly
squashes the heights above it, so peaks stay under the flight altitude and, with a low cap, the
ground gets flat tops (mesas, buttes). The relief can make mountains, canyons or stay almost flat.

**Acceptance criteria**
- Given a ridged relief, then its heights stay between its base and its top.
- Given a `max_height`, then no height of the section exceeds it.

*Sources: P04-R01, D-020, D-200.*

### GFX-TERRAIN-03 — Sculpt operations · MUST

A section may sculpt its relief along a winding line (a meander across Z):
- `flatten`: a flat band of a given half-width and height (room for buildings), with a slope back to
  the relief and a little roughness left on it;
- `channel`: a canyon or river bed of a given floor half-width and floor height, its walls a given
  width from the floor to the rim (wide grassy banks or steep stone walls); a floor below the water
  level holds a river or a canal ([water.md](water.md));
- `shore`: the ground drops under the sea on one side of the line, over a given width, to a sea bed.

The operations blend with the relief and between sections like the relief.

**Acceptance criteria**
- Given a section with a channel, then the ground on the channel's line is at its floor height.
- Manual: canyons, coasts and plateaus read as such from the playfield camera.

*Sources: P04-R01, D-020, D-079.*

### GFX-TERRAIN-04 — Dunes · MUST

A section may have sand dunes on top of its relief: parallel crests every `wavelength`, facing
`angle_deg` from +Z, each with a long gentle windward slope and a short steep lee slope (78 % /
22 %), their lines wandering with noise (`warp`) and their heights varied, up to `height` above the
relief. World 2's erg uses them; World 1's desert has none (D-200).

**Acceptance criteria**
- Given a section with dunes, then the dunes add between 0 and their height to the relief.

*Sources: P06-R06, D-037, D-200.*

### GFX-TERRAIN-05 — Basins and crevasses · SHOULD

A section may have `lakes`: round basins, one chance in each square of `spacing`, flattened to a
`level` over a `radius` with a shore `edge` wide. Below the water level they hold ponds; below the
look's `lowHeight` they take its low ground layer (frozen or dry lake beds). A section may also have
`crevasses`: narrow cuts `depth` deep and `width` wide, about every `spacing`, running across the
level at an angle, bent by noise and broken into pieces (about `share` of each line cut). No level
uses either now.

**Acceptance criteria**
- Given a section with crevasses, then they cut deepest on their line (unit test).

*Sources: P08-R07, D-066.*

### GFX-TERRAIN-06 — Terrain ceiling · MUST

The engine gives, for each level, a height its ground never exceeds whatever the seed: for each
section the highest of the top of its relief (or its peak cap), its dunes and scarps, its flattened
band and its sea bed. Carving only lowers the ground and blending stays between neighbouring
heights, so nothing else can raise it. The cloud layers are kept above it ([sky-and-light.md](sky-and-light.md)).

**Acceptance criteria**
- Given any level and seed, then no height of its ground is above its ceiling (unit test).

*Sources: D-022, D-037, D-240.*

### GFX-TERRAIN-07 — Ground textures generated in code · MUST

Every ground texture is generated in code when the level loads (or in the background worker), from
three colours, a noise frequency and a number of octaves, plus optional extras: `speckle` (scattered
pebbles or tufts of another colour), `strata` (horizontal layers, for rock walls) and `cracks` (the
cell edges of a jittered grid, for dried or frozen lake beds cracked into plates). A noise texture
for the borders and patches and a normal map for the water are generated the same way. No texture
is downloaded. Each texture is sampled from the three axis planes, weighted by the ground's normal,
so steep slopes are not stretched.

**Acceptance criteria**
- Given the same look and seed, then the generated pixels are the same; a texture with `cracks` has
  darker crack lines than one without (unit test).

*Sources: P04-R01, D-020, D-066, D-200.*

### GFX-TERRAIN-08 — Layers by altitude and slope · MUST

The terrain shader blends four layers of the look by height and slope: `low` (under `lowHeight`:
wet sand by the shore, or a dry lake bed), `ground` (the default ground), `high` (above `highHeight`:
snow on peaks) and `steep` (bare rock where the slope is within `steepSlope`, over all the others).
Borders are softened over `heightBlend` and jittered by noise (`jitter`), so they never look
straight. A large-scale noise tints the bare ground in patches (`tints`, over `tintTileSize`).
Lighting, shadows and fog are those of the standard material.

**Acceptance criteria**
- Manual: the textures change with altitude and slope, with no straight border between layers.

*Sources: P04-R01, D-020.*

### GFX-TERRAIN-09 — Ground covers: grass, concrete and sand · MUST

Each section may cover its ground with three covers, as shares from 0 to 1 over the `ground` layer:
`lush` (grass), `paved` (concrete and asphalt) and `sandy` (desert sand, or red desert dirt where a
world's look says so). The covers blend between sections like the height, and fade in through noise,
in patches rather than as a flat gradient: sand over the ground, grass over the sand, paving over
all. Steep slopes stay rock and peaks stay snow under any cover. The covers reach the shader in the
terrain's vertex colours (red, green and blue channels).

**Acceptance criteria**
- Given two sections with different covers, then the cover is blended over the transition like the
  height (unit test).
- Manual: grass, concrete and sand read from the playfield camera and fade into each other.

*Sources: P04-R01, P06-R05, P06-R06, P08-R07, D-023, D-037.*

### GFX-TERRAIN-10 — Slow changes between sections · MUST

Two sections blend over the level's `transition` (in Z), both their heights and their covers, so a
level changes its ground slowly. A level may blend over a longer stretch than another (World 1: 420
units; Worlds 2 to 4: 900), and its sections may step a cover by small amounts, so the ground goes
from sand to concrete or from concrete to grass in small steps. Without a transition, the change is
sudden.

**Acceptance criteria**
- Given a level with a transition, then near a section boundary the ground is a blend of both
  sections, and the blend is complete at the transition's ends (unit test).

*Sources: P06-R05, P08-R03, P09-R03, P10-R03, D-020.*

### GFX-TERRAIN-11 — Desert features · MUST

The engine's tools make an American desert, not sand dunes: dried red land (a `sandy` cover drawn as
red-orange dirt with dark pebbles over dried brown earth), cracked dry lakes (low flats under
`lowHeight`, drawn with a pale cracked hardpan), mesas and buttes (smooth relief squashed under a low
`max_height`, so it has flat tops, a flat floor and steep walls between, drawn as strongly layered red
rock from a slope of 0.2, D-240), canyons (channels) and no snow (the `high` layer out of reach). Which
levels use them is in the World 1 files.

**Acceptance criteria**
- Given World 1's dry levels, then they have no dunes, their dry lake lies under `lowHeight`, and
  their buttes stand flat-topped under the flight altitude (unit tests).
- Manual: the dry lake, the mesas and the buttes read as such from the playfield camera.

*Sources: P06-R06, D-200.*

### GFX-TERRAIN-12 — Matte ground · MUST

The terrain has no specular highlight (`specular` 0), so its facets do not flicker as the view
scrolls.

*Sources: D-024.*

### GFX-TERRAIN-13 — Shadows on and from the ground · MUST

The terrain receives the sun's shadows ([sky-and-light.md](sky-and-light.md)) and casts them on
itself and on the props. A terrain look may say its ground casts none (`castsShadows` false), for
ground flat enough to have nothing to shade (World 4's city).

**Acceptance criteria**
- Given a look with `castsShadows` false, then no terrain chunk is in the shadow map.

*Sources: D-020, D-151.*

### GFX-TERRAIN-14 — Terrain in chunks · MUST

The terrain is a row of chunks along Z, each `chunk_length` (320) long on a grid of `cell` (8) units,
as wide as the ground the camera sees plus the margin ([camera.md](camera.md)). Only the chunks under
the camera exist; the mesh of a chunk that scrolls out of view is reused for a new one (ENG-19).
Normals come from one extra ring of height samples, so the seams between chunks do not show. Every
vertex is at a multiple of the cell.

**Acceptance criteria**
- Given the stage, then only the chunks covering the ground in view plus the margin exist, and every
  terrain vertex is at a multiple of `cell` (unit tests).
- Manual: no seam shows between chunks.

*Sources: P04-R01, D-020, D-212.*

### GFX-TERRAIN-15 — The ground's glow · MUST

The ground's self-lit accents (windows, lamps, neon, car lights, lava) bloom through a glow layer of
their own: only the accent meshes glow, at the look's `glow.intensity` (0.3 by default). The glow
image is drawn at full resolution, its blur kernel doubled to spread as wide on screen, and
antialiased (4 samples), so lights thinner than a pixel neither blink nor flicker as the ground
scrolls. The props, the tree imposters (cut out by their alpha) and the terrain chunks are drawn into
it black, so a light behind a building or a hill does not glow through it. A car's imposter quad is
not, as it stands in front of its own far lights and would hide them ([traffic.md](traffic.md)). The
glow is composed under the clouds ([camera.md](camera.md)).

**Acceptance criteria**
- Manual: small lights hold steady as the ground scrolls, and a light hidden behind a building or a
  hill does not glow through it.

*Sources: D-020, D-131, D-132, D-212.*

### GFX-TERRAIN-16 — Lava · MUST

A level's liquid may be lava instead of water (`sea.lava`), on the same single liquid level
([water.md](water.md)), for lava rivers, pools and lakes cut below it. Lava is drawn by one self-lit
shader: dark red crust plates (moving cells whose centres wander, so it churns) over a glowing melt,
drifting down the screen with the liquid's drift, cracks opening and closing between the plates,
bright orange-yellow and white-hot at their heart. It is fogged but never quite hidden, so it shows at
night. No level has lava now; the engine keeps it with its tests.

**Acceptance criteria**
- Manual (on a test level): the lava reads as molten and moving from the playfield camera, by day and
  by night.

*Sources: P10-R05, D-084, D-129.*

### GFX-TERRAIN-17 — The lava's hot edge · MUST

Where rock meets lava, the terrain shader skips the beach and the surf, scorches the rock dark near
the lava and adds a bright glowing edge at its level (`edge.width` above it) and glowing cracks a
little higher (up to `edge.cracks`), flickering, before the fog.

*Sources: P10-R05, D-084.*

### GFX-TERRAIN-18 — Lava glows, and is only a look · MUST

The lava blooms in the ground's glow layer with its own material, and the terrain chunks are drawn
there black, so the hills hide the lava plane that runs under them. The lava casts no real light on
the ships, and flying over it does nothing: it is not an input of the simulation.

**Acceptance criteria**
- Unit test: lava is not an input of the simulation.

*Sources: P10-R05, D-084.*

### GFX-TERRAIN-19 — Scarps: hills with one steep face · MUST

A section may have `scarps` on top of its relief: hills each with a short steep face on one side
and a long slow slope on the other, as the dunes are made (GFX-TERRAIN-04), but with the face's
share of a cycle set by the section (`face`, 0..1; the dunes' is fixed at 22 %) and their crests
falling from `height` to `lowest` (a share of `height`; 0 lets the ridges break into separate
hills) with a noise of their own over 1.2 wavelengths, often at either end. Their lines wander
with noise (`warp`, in wavelengths) and their faces look towards `angle_deg` from +Z. Where the
face is steep enough, the look's `steep` layer draws it as bare rock (GFX-TERRAIN-08): a rocky side
and a grassy or dusty one. World 1's land uses them ([../worlds/world-1/world.md](../worlds/world-1/world.md),
WLD-1-31).

**Acceptance criteria**
- Given a section with scarps, then they add between 0 and their height to the relief (unit test).
- Given straight scarps of a constant height, then along their direction the ground drops much
  more steeply at the face than it rises on the back (unit test).
- Given scarps whose `lowest` is 0, then some crests fall near the relief (unit test).
- Manual: from the playfield camera, the hills read as a rocky face on one side and a slow slope on
  the other.

*Sources: D-240.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `chunk_length` | 320 | `src/config/scenery_stage.py` `SCENERY_STAGE_CONFIG` |
| `cell` | 8 | terrain grid, same place |
| `textureSize` / `tileSize` | 256 px / 150 units | `src/game/config/scenery_look.py` `BASE_SCENERY_LOOK.terrain` |
| `lowHeight` / `highHeight` / `heightBlend` | 7 / 205 / 12 | base look; World 1's dry levels: `highHeight` 1000 (`src/game/config/world_1/looks.py` `DRY_TERRAIN`) |
| `steepSlope` | 0.22–0.45 | base look; World 1's green levels 0.12–0.3 (`TERRAIN`), its dry levels 0.2–0.42 (`DRY_TERRAIN`), `src/game/config/world_1/looks.py` (D-240) |
| `jitter` | height 30, slope 0.2 | base look |
| `noiseTileSize` / `tintTileSize` | 300 / 1600 | base look |
| `specular` | 0 | base look |
| hardpan `cracks` | 0.75 | `HARDPAN`, `src/game/config/world_1/looks.py` |
| mesa rock `strata` | 0.6 | `MESA_ROCK`, same place |
| scarps `face` / `lowest` / `angle_deg` / `warp` | 0.08 / 0 / 150 / 0.8 | World 1's hills, `src/game/config/world_1/scenery_coast.py` `scarps` (`SCARP_FACE`, `SCARP_ANGLE`); heights 24–40 over wavelengths 320–360 per section |
| `SCARP_BEND_SCALE` / `SCARP_CREST_SCALE` / `SCARP_CREST_SPREAD` | 3 / 1.2 wavelengths / 0.45 | `src/core/scenery/height_field.py` |
| `transition` | 420 (World 1), 900 (Worlds 2–4) | per level, `src/game/config/world_*/scenery*.py` (`TRANSITION`) |
| `glow` | intensity 0.3, blur 16 | base look; full resolution, 4 samples (`src/app/level_scene.py` `ground_glow_look`, `GROUND_GLOW_SAMPLES`) |
| `castsShadows` | False in World 4 | `src/game/config/world_4/looks.py` `city` |

## Notes

- Per world, briefly: World 1 goes from grass to red desert (dry lake, mesas, buttes, canyon);
  World 2 from sand (dunes) to concrete; World 3 from concrete to grass; World 4 is flat paved city
  ground, low enough for its skyscrapers to stay under the clouds (`CITY_GROUND`, D-196). Details are
  in the world files.
- Known limitations: the clouds cast no shadow on the ground; roads are draped on the ground without
  flattening it.
- The terrain shader reads only the textures whose share shows; that and the other speed-ups of the
  ground are in [../performance.md](../performance.md).
- Known gap: the unit test of GFX-TERRAIN-18 (lava is not an input of the simulation) was not carried
  over to the Python port; the simulation imports nothing of the scenery looks.
