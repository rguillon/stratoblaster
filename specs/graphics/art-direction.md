# Art direction

> **Area:** Graphics · **Prefix:** `GFX-ART` · **Related:** [readability.md](readability.md), [edge-trim.md](edge-trim.md), [player-ships.md](player-ships.md), [shots.md](shots.md), [effects.md](effects.md), [../enemies/common.md](../enemies/common.md), [../bosses/common.md](../bosses/common.md), [../ui/look-and-layout.md](../ui/look-and-layout.md)

The look of the game as a whole: everything is made in code, the mood is darksynth, every kind of
object has its palette, and the models are low-poly and flat-shaded, built from a shared geometry
kit. It also sets the Cyber-Organic style every enemy and boss shares. It does not describe one
model: each ship, enemy and boss has its own file, and the rules that keep the playfield readable
(reserved colour families, contrast) are in [readability.md](readability.md). The menus' and HUD's
palette is in [UI-LOOK](../ui/look-and-layout.md).

## Requirements

### GFX-ART-01 — Everything generated in code · MUST

Every model and visual of the game (ships, enemies, bosses, shots, effects, bonuses, ground, props)
is built by code when the game runs. The game loads no model, texture or image file for its 3D
look; a texture it needs is generated in code.

**Acceptance criteria**
- Given the built game, then it ships no model, texture or image asset: the 3D look comes from code
  only.

*Sources: GD-60, D-005.*

### GFX-ART-02 — Geometry and lighting without extra dependencies · SHOULD

The engine has its own geometry builders (ear-clipping triangulation, flat-shaded prisms, faceted
lathes, the solids of GFX-ART-10), so no triangulation package is added. Shiny metal is lit by a
procedural sky-gradient environment cube (image-based lighting) with ACES tone mapping, so no
environment map is downloaded. A glow layer makes the self-lit parts (reactors, neon, shots) bloom.
The pure geometry is unit-tested without a WebGL context.

**Acceptance criteria**
- Given the geometry builders, when they run under the unit tests (no WebGL), then they return
  their faces.
- Given a scene with ships, then its metal is lit by the generated environment cube and its
  self-lit parts bloom.

*Sources: D-005.*

### GFX-ART-03 — Darksynth direction · MUST

The style is darksynth: dark grounds and hulls, glowing neon lights, sunset gradients and
chrome-like shiny metal. The colour of each kind of gameplay object is the one set in GFX-ART-04 to
GFX-ART-07 and reserved in [GFX-READ](readability.md); the backgrounds stay dark under them.

**Acceptance criteria**
- Given one level of each world, when it is played, then it reads dark, with neon accents, and the
  gameplay objects glow over it (manual).

*Sources: GD-60, D-231.*

### GFX-ART-04 — Player ship palette · MUST

The player ships are shiny grey/blue metal with blue accents and a dark canopy. Their lights are
blue to cyan: the reactor cores and flames, the nav lights and the edge trim (see
[GFX-SHIP](player-ships.md), [GFX-TRIM](edge-trim.md)). The player's shots share the cyan / ice
blue family.

**Acceptance criteria**
- Given a player ship, then its hull metal is grey/blue (more blue than red) and every light on it
  is blue to cyan.

*Sources: GD-61, P02-R01, P02-R02, P02-R03, P14-R02.*

### GFX-ART-05 — Enemy and boss lights: bright yellow or bright green · MUST

Enemies and bosses are dark bodies with neon lights. Every light of an enemy or a boss (neon,
veins, eyes, charge lights, reactor cores and flames, edge trim) is bright yellow (hue 60°) or
bright green (hue 125°), keeping its brightness: the hue of the colour its table gives is moved to
the nearer of the two. Warm neon (red, orange, magenta) turns yellow; cool neon (green, cyan, blue)
turns green. There is no shade in between (no khaki) and no pink, magenta, violet or red light on
an enemy or a boss. An enemy's lights take the hue of its tier instead (60° to 135°, on the same
yellow to green ladder, [ENM-49](../enemies/common.md)); the two hues above are the bosses'.

**Acceptance criteria**
- Given any enemy or boss model, then the hue of each of its coloured lights is 60° or 125° (greys
  aside).
- Given an enemy whose neon table colour is magenta, then it is drawn yellow; given a cyan one,
  green.
- Given an enemy, then its reactor flames are in its neon colour.

*Sources: GD-61, D-231, P16-R01.*

### GFX-ART-06 — Enemy and boss body shades · MUST

The bodies of the enemies and bosses (metal hull and flesh) are dark, neutral slates and greys, so
an enemy's yellow or green is its lights'. A body shade whose hue is from 100° to 250° (moss green,
teal, ice blue) keeps its colour; any other (yellow, olive, brown, red, pink: rust, brass, gilding,
sandstone) is greyed to a saturation of at most 0.1. The hull metal is tinted 0.3 of the way
towards the enemy's neon and glows 0.04 of it; the flesh is tinted 0.15 of the way. The tint
colour goes through the same rule, so a green enemy's metal is faintly green and a yellow one's
stays neutral. Body shades stay dark (under 0.2) so the enemies keep their contrast with the
ground; small metal details (rivets, about 0.24) and a few boss paints (World 2's ice, the
Toucan's beak) are brighter, as their files say.

**Acceptance criteria**
- Given a warm or pink body shade, then it is drawn greyed (saturation ≤ 0.1); given a green, teal,
  blue or grey one, it is kept.
- Given a yellow enemy, then its hull is not tinted yellow (no olive or khaki metal).

*Sources: D-231, P16-R01, GD-61.*

### GFX-ART-07 — Enemy shot and bonus palette · MUST

Enemy bullets, missiles and lasers are orange to amber round a white-hot core. Bonuses are a blue
violet (about hue 262°), which does not read pink; their kinds are told apart by their shapes (see
[GFX-FX](effects.md)). Neither uses yellow or green, the enemies' colours.

**Acceptance criteria**
- Given every enemy bullet style, then its colour is orange to amber; given every bonus, its
  colours are blue violet to purple.

*Sources: D-231, P14-R02.*

### GFX-ART-08 — Brighter hulls · MUST

The metal of the player ships, the enemies and the bosses takes 1.8 times the direct light (sun,
lamps) and 1.8 times the sky reflections, so they stand out brighter than the scenery. The scenery
lights are unchanged.

**Acceptance criteria**
- Given the ship, enemy and boss metal materials, then their direct and environment light factors
  are `hullLight`.

*Sources: D-127.*

### GFX-ART-09 — Low-poly, polygonal models · MUST

Models are made of polygons, not smooth round shapes. Every solid part is flat-shaded: prisms for
flat parts, faceted lathes for bodies of revolution (a fuselage may use a split section, finer on
top, coarse underneath), other round parts with 6 equal sides. Reactors are hexagonal, with
polygonal ring bands and 6-sided flame cones; small lights are octahedra and plasma puffs
icosahedra or tetrahedra. Only the translucent glows (flames, glow discs) are smooth-shaded.

**Acceptance criteria**
- Given any ship, enemy or boss model, then its solid parts are flat-shaded polygons (manual, and
  per-model tests where they exist).

*Sources: D-007.*

### GFX-ART-10 — Shaping primitives · SHOULD

The engine's solid builder gives flat-shaded, vertex-coloured shapes so models do not look like
boxes put together, at a low polygon cost: boxes, lathes, rings, cylinders, slabs; a bevelled slab
(sides sloping from the outline at a waist to faces inset by a miter offset); and a loft (a convex
cross-section stretched through stations along Z, closing to a point at a zero-size station,
optionally open underneath, with some faces painted another colour). A bevelled slab or a loft
costs about 2 triangles more per side than a plain slab or box. New models use these and the
faceted helpers.

**Acceptance criteria**
- Given a loft with a zero-size end station, then it closes to a point; given `paint`, then the
  painted faces take the other colour (unit tests).
- Given a bevelled slab, then its top and bottom faces are inset from the outline at the waist.

*Sources: D-033.*

### GFX-ART-11 — Model animations driven by the frame time · SHOULD

Animated parts of a model (reactor flames, rotors, wings, pulsing lights) are per-frame animations
attached to the model's nodes. They run when whatever draws the model (the game, a dev viewer)
steps the model with its frame time, and they are dropped with their node. A flicker is a mean of
sines at incommensurate frequencies, with a phase from the part's name, so two parts never move in
step.

**Acceptance criteria**
- Given a model with animations, when it is stepped with a frame time, then each animation runs
  with that time; given a node that is disposed, then its animations go with it.
- Given two reactors with different names, then they do not flicker in step.

*Sources: D-006.*

### GFX-ART-12 — Cyber-Organic bodies with cyber grafts · MUST

Every enemy and boss looks like living tissue fused with machinery. Its body is organic: rounded,
swollen, asymmetric-but-balanced shapes (pods, segmented abdomens, carapace shells, ribcages,
skull-like heads, tendrils, mandibles), not boxes and plain wedges. Cyber parts are grafted on and
read as man-made: metal plates with rivets, armour bands, ports, pipes, cables, barrels, nozzles,
with straight edges and metal shades. A model is mostly flesh, with metal on its nose, guns, joints
and reactors.

**Acceptance criteria**
- Given every enemy and boss model, then its body is made of organic shapes and its grafts of metal
  (manual, in the dev viewer).

*Sources: P16-R01, D-165.*

### GFX-ART-13 — Wings and reactors as living parts · MUST

Kinds that had wings keep them: membranes stretched on bone or metal struts, from the root out to
each tip, or metal wings with an organic root. Reactors are kept, at the back, read as glowing
organs: a flesh sac or bulb round the nozzle and a vein running from it into the body.

**Acceptance criteria**
- Given an enemy kind that had wings and reactors, then its model still has them (manual).

*Sources: P16-R01.*

### GFX-ART-14 — Lights as veins, eyes and glands · MUST

The lights of an enemy or a boss are neon veins, eyes and glowing glands rather than plain neon
strips: veins pulse, steady lights stay on, and charge lights brighten as an attack charges. They
take the enemy's colour (GFX-ART-05).

**Acceptance criteria**
- Given an enemy model, then its lights are veins, eyes, glands or charge lights in its neon colour
  (manual).

*Sources: P16-R01, D-165.*

### GFX-ART-15 — Two body materials: flesh and hull · SHOULD

An enemy or boss body has two materials. The flesh is a waxy, barely metallic material (metallic
0.25, roughness 0.5) in the flesh shades (slate, graphite, teal, sinew, bone, membrane). The hull
is the dark metal (metallic 0.85, roughness 0.38) in the hull shades, only for what is grafted on.
Both are tinted and lit as GFX-ART-06 says, both carry the edge trim ([GFX-TRIM](edge-trim.md)),
and both flash white when a boss part is hit.

**Acceptance criteria**
- Given the enemy materials of a scene, then there is one flesh and one hull material with these
  settings, and both are the body materials a boss hit flashes (unit tests).

*Sources: D-165, P16-R01.*

### GFX-ART-16 — The tier reads from the look · MUST

The look grows with the tier: a tier 1 kind is one body with a few grafts; each higher tier has more
armour plates, limbs, organs and veins than the one below; a tier 4 kind is heavily armoured, with
plated shells;
a boss is one creature whose destroyable parts are organs, limbs or armoured growths.

**Acceptance criteria**
- Given the enemies side by side in the dev viewer, then the tier of each is readable from its look
  (manual).

*Sources: P16-R01.*

### GFX-ART-17 — Engine-agnostic organic shape kit · MUST

The organic shapes come from reusable builders in the engine, outside `src/game/`, that know
nothing of what they draw: segmented bodies of swollen segments, carapaces (ridged shells with
darker seams), tendrils and curves (tentacles, mandibles, sinews, necks), ribs (arches over a
back), organs (bulbs, sacs, heads), membrane wings, veins, riveted armour plates and grown (uneven,
seeded) outlines. The pieces that are this game's (the reactor sac, eyes, each world's boss pieces)
are built from them in `src/game/`.

**Acceptance criteria**
- Given each builder, then unit tests check its vertex counts or shape, its bounds, and that it is
  the same for the same seed.
- Given the code outside `src/game/`, then it names no concrete enemy or boss.

*Sources: P16-R02, D-165.*

### GFX-ART-18 — A new look keeps the gameplay points · SHOULD

Reworking the look of a model keeps its part ids, joints, turrets and muzzles where they were, so
the simulation and its tests are untouched by a visual change.

**Acceptance criteria**
- Given a reworked model, then its part ids, joints, turrets and muzzles are those of the model it
  replaces, and the gameplay tests pass unchanged.

*Sources: D-168.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| Enemy light hues | 60°, 125° (bosses; an enemy's is its tier's, ENM-49) | `src/game/config/readability.py` `READABILITY["enemyHues"]` (GFX-ART-05) |
| Enemy body hue window | 100°–250°, else saturation ≤ 0.1 | `READABILITY["enemyBody"]` (GFX-ART-06) |
| Hull tint / self-light | 0.3 / 0.04 | `src/game/config/enemy_look.py` `ENEMY_LOOK["hull"]` |
| Hull metallic / roughness | 0.85 / 0.38 | `ENEMY_LOOK["hull"]` |
| Hull shades | base 0.1, panel 0.16, dark 0.045 (about) | `ENEMY_LOOK["hull"]` |
| Flesh metallic / roughness / tint | 0.25 / 0.5 / 0.15 | `ENEMY_LOOK["flesh"]` |
| Flesh shades | slate, graphite, teal, sinew, bone, membrane, wound | `ENEMY_LOOK["flesh"]`, all under 0.2 |
| Hull light | direct × 1.8, environment × 1.8 | `READABILITY["hullLight"]` (GFX-ART-08) |
| Player ship materials | see [GFX-SHIP](player-ships.md) | `src/game/config/ship_look.py` `SHIP_LOOK` |
| Bonus colours | blue violet, hue about 262° | `src/game/config/bonus_look.py` `BONUS_LOOK` |
| Enemy bullet colours | orange to amber | `ENEMY_LOOK["bullets"]["styles"]` |
| Round part facets / fuselage section | 6 / 20 on top + 3 underneath | `src/game/view/ship_parts.py` `PART_FACETS`, `BODY_SECTION` |

## Notes

- GD-60 named the darksynth colours "neon magenta, violet and blood red". The reviewer later moved
  the menus and the HUD to neon blue/green (D-198, see UI-LOOK) and the enemies and bosses to bright
  yellow or bright green, the bonuses to violet (D-231, 2026-11-01). D-231 recorded that GD-60,
  P14-R02 and P16-R01 ("deep crimson, purple, dark teal" flesh) still named the old colours; this
  file carries the new ones.
- D-231's earlier step, D-121, squeezed the whole hue wheel into the old violet / magenta / red
  family; that gave in-between shades and is replaced for the enemies' lights by the two hues.
- The P16 triangle budgets per tier (basic 400 … final boss 10 000) are in the enemy and boss
  common files.
