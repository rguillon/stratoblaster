# Buildings

> **Area:** Graphics · **Prefix:** `GFX-BLDG` · **Related:** [roads.md](roads.md), [props.md](props.md), [sky-and-light.md](sky-and-light.md), [terrain.md](terrain.md), [art-direction.md](art-direction.md), [readability.md](readability.md), [../performance.md](../performance.md)

Every building, factory, house and lot of the game is a model generated from code for the grid of
10-unit tiles: it covers W × D whole tiles and is built from a seed, so the models of a group differ.
In the districts, buildings pack the city blocks between the streets; outside them they stand along
the winding roads, alone or in hamlets. Their windows and doors are quads of one generated atlas, lit
at dusk and at night. Which groups each section uses is in the world and level files.

## Requirements

### Placement

### GFX-BLDG-01 — Buildings along the roads outside the districts · MUST

Outside the districts, buildings stand only along the roads and paths: in slots every `slotSpacing`
(24) on both sides, set back `setback` (2) from the road edge and facing it. A slot gets a building
with the chance of its section's `buildingDensity`, if the ground under the footprint is flat enough
(`maxSlope` 0.12), above `minHeight` (4), clear of the other roads and of the buildings already
placed. Slots along main roads are served first, so they get the street fronts. A low-frequency noise
(`zoneFrequency`, 1/700) picks the building group of each area among the groups its section allows,
so buildings of one kind gather in clusters. No two buildings overlap. The same seed places the same
buildings, whatever the order the ground is asked for in.

**Acceptance criteria**
- Given a level, then its buildings outside the districts stand along roads, set back and facing them,
  on flat ground, with no overlap (unit tests).

*Sources: P04-R07, P15-R13, D-021, D-023.*

### GFX-BLDG-02 — Lone buildings and hamlets · MUST

A few buildings stand away from the roads: one per square of `loners.cell` (150), with the chance
`loners.chance` (0.15) times the section's building density, at least `loners.clearance` (18) from
every road, turned at random. From time to time (every 700–1400 along the level, in sections with
buildings and no street grid), a hamlet gathers 5–9 buildings of one group within 32 of its centre,
all facing about the same way, 2 apart and 18 from every road; its centre is tried at a few places
across the level. Both stand within half of `offscreenX` of the middle, so most are in view.

*Sources: P15-R13, D-046.*

### GFX-BLDG-03 — Buildings sized in tiles · MUST

Every building, factory, house and other structure that can stand in a district has a footprint of W
× D whole tiles (W, D ≥ 1, not necessarily square), declared in the game config with the model. Seen
from above, the model stays inside that footprint at every height, `building_margin` (0.5) from its
edges: no roof, crane, chimney or pipe overhangs it. It is placed at scale 1 and turned by quarter
turns only (W and D swap). Outside the districts the same models stand by the rules of GFX-BLDG-01
and -02, also at scale 1.

**Acceptance criteria**
- Given every model made for the grid, then its X/Z bounds fit its W × D tiles less the margin on
  each side (unit test).

*Sources: P15-R07, D-160, D-162.*

### GFX-BLDG-04 — Buildings sit on the ground · MUST

A building stands at the lowest ground under its footprint, so it never floats above the ground at a
corner; in a district, a tile is fit to build on only if its corners are above `minHeight` and differ
by at most `maxSlope` over half a tile, so it does not sink in either.

**Acceptance criteria**
- Given a packed spot, then it stands at the lowest ground under it (unit test).
- Manual: no building floats or sinks at a corner, seen from the playfield camera.

*Sources: P15-R07, D-159.*

### GFX-BLDG-05 — Filling the city blocks · MUST

Each city block of a district is packed with buildings of its section's groups, on whole tiles,
without overlapping each other or the roads. The free tiles of a block are taken in a random order
(from the block's hash); each gets the first kind that fits with that tile at a corner: the kind drawn
for its area's group, then the group's other kinds from the largest down, then the lots. Packing
stops when the buildings and lots cover the section's `buildingDensity` of the block's tiles fit to
build on; at 1, every tile is covered. A building larger than its block is never chosen. The tiles
left over are open ground (the section's ground cover) or lots.

**Acceptance criteria**
- Given every section with a district (fixed seeds), then the share of its block tiles covered is
  within 0.1 of its `buildingDensity` (unit test).

*Sources: P15-R08, D-159.*

### GFX-BLDG-06 — Buildings face the street · MUST

A building that touches a road faces it: its front (−Z of the model) is on a road side, by quarter
turns, and a corner building faces one of its roads. A non-square building that could only face a
road along its long side is not placed there. A building that touches no road turns by half turns from
the way its footprint was fitted, so it never stands across its tiles.

**Acceptance criteria**
- Given every district, then every building touching a road has its front on a road side (unit test).

*Sources: P15-R08, D-159, D-164.*

### GFX-BLDG-07 — Mixed footprints · MUST

Footprints of several sizes are mixed, so a district never looks like a checkerboard of equal squares:
every section with a district and buildings places at least 3 different footprints, and no single
footprint makes up more than 60 % of its buildings. Trees and plants grow only on open tiles and on
lots, never on a road tile or a building's tile.

**Acceptance criteria**
- Given every section with a district (fixed seeds), then at least 3 footprints are placed and none is
  more than 60 % of its buildings (unit test).
- Manual: blocks do not look like a checkerboard of equal squares.

*Sources: P15-R08.*

### The models

### GFX-BLDG-08 — Building groups · MUST

Sections pick their buildings from groups. Every group has at least 5 models (a model shared by
several groups counts for each) and at least 3 footprints, one of them not square, within the group's
footprint range (see the table below). The groups are: heavy industry, desert homes, outposts, homes
(the small homes of villages and worker towns), industrial (mines, oil fields, refineries, factories
and warehouses as one group), docks, workshops, worker flats, residences (terraces and suburbs as one
group), town centre, mid-rise, offices, towers, skyscrapers and downtown.

**Acceptance criteria**
- Given the config, then every group has at least 5 models and 3 footprints, one not square, all
  within its range (unit test).

*Sources: P15-R09, D-160.*

### GFX-BLDG-09 — Models with the character of their group · MUST

Each model is built for its W × D tiles from a seed, in the darksynth style ([art-direction.md](art-direction.md)),
with lit windows and neon accents for the night, and keeps its group's character. Among them: adobe
homes with flat roofs, parapets and windcatchers, and a courtyard house round a fountain; small homes
of the future on paved plots, each of its own silhouette (a capsule, a dome, stacked cubes, stacked
containers, a lit grow tower, a home beside a solar shed); residences without tile roofs (cantilevered
slabs, pods, a row of modules under solar panels, stepped terraces, a house on stilts, a wedge under a
sloping metal roof); water towers, solar farms, radio masts and depots; mine headframes, ore silos and
mine works; pumpjacks, white oil tanks and gas flares; refineries of columns and pipe racks; factories
with saw-tooth halls and chimneys; warehouses with loading doors; container yards and dock cranes;
hyperbolic cooling towers; foundries with molten furnace mouths and tall stacks; power plants;
workshops and blocks of flats; and the city buildings below.

**Acceptance criteria**
- Given every archetype, then it has a builder, builds a well-formed model standing on the ground,
  and the same seed builds the same model (unit tests).
- Manual: the houses, factories and towers read as such from the playfield camera.

*Sources: P15-R09, P08-R07, P10-R08, D-160.*

### GFX-BLDG-10 — City buildings, towers and skyscrapers · MUST

The city buildings (mid-rise blocks, offices, towers, skyscrapers) each take the silhouette their seed
names, so the models of a group all differ: stepped tiers, a slab with fins, a round tower, twin
towers with a bridge, a needle set back off-centre, or blocks of two heights side by side; some are
asymmetric, lit their own way on each face, with an annex and a fin on one side. The towers rise
above the mid-rise blocks, and the skyscrapers are the tallest buildings of the game, glass towers
reading as a skyline.

**Acceptance criteria**
- Given the city models, then the towers stand taller than the mid-rise blocks (unit test).
- Manual: downtown reads as a skyline of skyscrapers.

*Sources: P10-R03, P10-R08, P15-R09.*

### GFX-BLDG-11 — Lots · MUST

At least 4 lot props fill the open tiles of the blocks, with footprints from 1 × 1 to 2 × 2: a car
park, a paved yard, a plaza and a small park or garden (with a few low trees of its own). Every world
uses them, coloured by its look's tone. Lots are low next to the towers.

*Sources: P15-R09.*

### Windows, doors and lights

### GFX-BLDG-12 — The windows' atlas · MUST

The windows of every building are painted once, when the scene starts, into one generated texture:
512 × 512 pixels of 8-pixel window cells, with one band of columns for each of 4 styles (square
punched windows, ribbons along the floor, tall narrow windows, a curtain wall of large panes). Each
floor of a band gets a random activity that sets how many of its windows are lit; a lit window gets a
colour (mostly warm lamps, sometimes a cold office light or a screen), a brightness, sometimes a
half-lowered blind, and a soft one-pixel halo. Its colours are the light (black where nothing is lit)
and its alpha the shape (0 on the wall between windows). About one window in five is lit.

**Acceptance criteria**
- Given the atlas, then it has one band per style, a lit window is opaque with a halo, a dark window
  is opaque and dark, and the wall between shows through (unit tests).

*Sources: D-210.*

### GFX-BLDG-13 — One window quad per wall · MUST

Each volume of a building at least 4 high gets one quad per wall, `WINDOW_OFFSET` (0.08) off it, from
one floor up to one under the roof, mapped on a block of the atlas: one cell per `WINDOW_CELL` (2.5 ×
3) of wall, from a random column of the volume's style band (a wider wall gets wider windows rather
than leave the band) and a random row. A box has one style; an asymmetric building has one per wall,
so each side looks different. The quads are tinted by the building's window colour, half of it over
white. A round tower gets one quad per facet, following its taper. The quads are a third geometry of
the model (its windows), next to its structure and its lights.

**Acceptance criteria**
- Given a box, then it gets one quad per wall just off it, mapped one cell per window in its style's
  band (unit tests).

*Sources: D-210.*

### GFX-BLDG-14 — Doors and glass fronts · MUST

Every window and door of a building on a wall is a quad of the atlas. The atlas has two door styles
after the windows' bands, 2 columns each: a glazed door and a wide bay (a loading or garage door),
standing on the bottom of their cell and lit more often than windows. A building may put one quad of a
given style on one wall (a glass front) or one door (one cell, a window cell's size, at the foot of a
wall). What is not a window or a door on a wall stays geometry: roof lights, a glass band that is part
of a volume, lit strips on plinths, neon signs and strips.

**Acceptance criteria**
- Given a door, then it is one cell of its band standing on the ground (unit test).

*Sources: D-215.*

### GFX-BLDG-15 — How windows are lit · MUST

The windows are drawn with the atlas as their diffuse texture and its alpha as their shape, so the
wall shows between them. Their light is the emissive colour scaled by the ground's lights (off by day,
on at dusk and at night, [sky-and-light.md](sky-and-light.md)), plus a faint share of the sunlight
(`glass`, 0.25), so dark windows stay black. They are blended without writing depth: each quad lies
over its own opaque wall. The ground's glow draws them with their own material, so only lit windows
glow.

**Acceptance criteria**
- Manual: at dusk and at night, some windows are lit and glow; by day, lit windows show faintly and
  dark ones are black.

*Sources: D-210.*

### GFX-BLDG-16 — Lights of the buildings · MUST

A building's self-lit accents (neon trims and signs, lamps, door lights, warning lights) are a
separate lights geometry of its model, drawn as their own thin-instanced mesh, glowing in the ground's
glow layer at the strength of the ground's lights. Neon rings are open bands with no end caps, so a cap
hidden inside a building never glows through it. The lights are drawn just in front of their walls
(depth offset −2), so they do not flicker against them as the ground scrolls.

**Acceptance criteria**
- Manual: the lights hold steady on their walls as the ground scrolls, and none glows through a wall.

*Sources: D-020, D-134, P08-R04.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `slotSpacing` / `setback` | 24 / 2 | `src/game/config/world_1/props.py` `WORLD_1_ROADS` |
| `maxSlope` / `minHeight` / `zoneFrequency` | 0.12 / 4 / 1/700 | `WORLD_1_PROPS` (Worlds 2–4 alike) |
| `loners` | cell 150, chance 0.15, clearance 18 | same place |
| `hamlets` | every 700–1400, 5–9 buildings, radius 32, gap 2, clearance 18 | same place |
| `tile.size` / `BUILDING_MARGIN` | 10 / 0.5 | `src/game/config/tile_buildings.py` |
| density tolerance / most of one footprint | 0.1 / 60 % | P15-R08 checks |
| footprint ranges (tiles, either way round) | heavy industry 3×3–4×6; desert homes, outposts 1×1–2×2; homes 1×1–2×3; industrial, docks 1×1–3×4; workshops, worker flats 1×2–2×3; residences 1×1–2×4; town centre, mid-rise, offices, towers, skyscrapers 2×2–3×3; downtown 3×3–4×4; lots 1×1–2×2 | `TILE_GROUPS[...].range`, same place |
| models | 99 buildings of 29 archetypes, 5 lots | `TILE_GROUPS`, `LOT_MODELS`, same place |
| window atlas | 512 px, 8-px cells, 4 styles (lit 0.18 / 0.2 / 0.15 / 0.22), 2 doors (0.5 / 0.45), brightness 0.45–1, blinds 0.25, glass 0.25, seed 4242 | `src/game/config/window_look.py` `WINDOW_ATLAS` |
| `WINDOW_CELL` / `WINDOW_OFFSET` / `WINDOW_TINT` | 2.5 × 3 / 0.08 / 0.5 | same place |
| lights' depth offset | −2 | `src/render/scenery/scenery_kit.py` `LIGHTS_Z_OFFSET` |

## Notes

- The groups were merged at the reviewer's request while phase 15 was built (2026-10-28, recorded in
  the code): the villages and worker homes are one group of small homes, the terraces and suburbs one
  group of residences, the mines, oil, refineries and industrial works one industrial group.
- Removed models: the phase 4 industrial complexes, city blocks and towers made of parts, the World 3
  and World 4 families of parts, and every hand-made building (D-160, D-161, D-163, D-207). Builders of
  a few archetypes no model uses now (house, villa, cottage, terrace, farmhouse, barn, greenhouse)
  remain in `src/game/view/props/tile_homes.py`.
- Per world, briefly: World 1 has desert homes, outposts, homes and docks; World 2 desert homes,
  outposts, homes, industrial and heavy industry; World 3 heavy industry to homes; World 4 town centre
  to downtown. See the world files.
- No test caps a building model's triangles; the largest model made for the grid has about 550.
