# Player ships

> **Area:** Graphics · **Prefix:** `GFX-SHIP` · **Related:** [../gameplay/player-ship.md](../gameplay/player-ship.md), [art-direction.md](art-direction.md), [edge-trim.md](edge-trim.md), [readability.md](readability.md), [shots.md](shots.md), [../ui/ship-select.md](../ui/ship-select.md)

The look of the three ships the player can fly, Balanced, Heavy and Light: their models, their
shared materials, their reactors and animated flames, how they bank and how they glow. Each is
generated in code (GFX-ART-01), low-poly and polygonal (GFX-ART-09). Their speed, health and
handling are in [GAME-SHIP](../gameplay/player-ship.md); the ship select screen that shows them is
in [UI-SHIP](../ui/ship-select.md).

## Requirements

### GFX-SHIP-01 — Balanced ship · MUST

The Balanced ship is inspired by the Macross Delta VF-31J: a long pointed nose, a framed bubble
canopy, a dorsal spine, canards, leading-edge strakes, side intakes feeding two reactors,
forward-swept wings (the tip's leading edge ahead of the root's) with accent bands and flap lines,
canted twin tails with stripes, ventral fins, a gun pod under the belly and blue nav lights. It is
about 4.8 model units long.

**Acceptance criteria**
- Given the Balanced model, then its wing tips' leading edges are ahead of their roots
  (forward-swept), and it has two reactors.
- The design is validated by eye (manual).

*Sources: P02-R01.*

### GFX-SHIP-02 — Heavy ship · MUST

The Heavy ship is a modern flying-wing bomber in the style of the B-2 / B-21: no fuselage and no
tail, swept leading edges with accent bands, a sawtooth trailing edge with elevons, a raised cockpit
with a dark visor, dorsal intakes with dark mouths feeding two reactors, bomb bay doors underneath
and nav lights. Its span (6 model units) is more than twice its length.

**Acceptance criteria**
- Given the Heavy planform, then it is a closed outline whose two sides mirror each other (unit
  tests).
- The design is validated by eye (manual).

*Sources: P02-R02.*

### GFX-SHIP-03 — Light ship · MUST

The Light ship has four wings, each with one reactor attached at its tip. It is a faceted
tandem-wing interceptor, like a dragonfly (not an X-wing look): a small front wing pair sits low
(anhedral) and a larger, swept rear pair sits high (dihedral), so the front flames stream under the
rear wings. It has a fuselage with a smooth top and a faceted belly, a plain pointed nose, a
hexagonal canopy and nacelles, diamond-section twin cannons under the nose, an accent collar, wing
stripes and a dorsal blade.

**Acceptance criteria**
- Given the Light model, then it has a front and a rear wing on each side, and each of the four
  wings carries exactly one reactor (unit test for the wings).
- The design is validated by eye (manual).

*Sources: P02-R03.*

### GFX-SHIP-04 — Shiny grey/blue materials · MUST

All the player ships share one set of materials per scene: a shiny grey/blue physically based metal
hull, a blue accent metal, a dark canopy with a faint blue glow, a darker trim metal (panel lines,
frames, intakes, barrels), a dark metal nozzle, and self-lit blue nav lights. The hull is metallic
at least 0.7, roughness at most 0.35, more blue than red. The metals take the brighter hull light of
GFX-ART-08.

**Acceptance criteria**
- Given a scene, then the ship materials are made once and shared by every ship (unit test).
- Given the hull material, then it is metallic ≥ 0.7, roughness ≤ 0.35, with an albedo more blue
  than red.

*Sources: GD-61, P02-R01, P02-R02, P02-R03, D-127.*

### GFX-SHIP-05 — Polygon budget · MUST

Each player ship is under 2,000 triangles. Its fuselage (and the parts sitting on it) uses a split
section, 20 facets over the upper half for a smooth top and 3 for a faceted belly; other round parts
have 6 sides; nav lights are octahedra.

**Acceptance criteria**
- Given each player ship model, then it has fewer than 2,000 triangles.

**Gap:** no unit test counts the ships' triangles since the Python port, and the count with the edge
trim (GFX-TRIM-01) was not measured (1,150 / 1,086 / 1,722 before the trim).

*Sources: D-007.*

### GFX-SHIP-06 — Reactors with a living blue flame · MUST

Every reactor (Balanced 2, Heavy 2, Light 4) is a hexagonal metal nacelle with polygonal ring bands,
a blue self-lit core at its nozzle and an animated blue flame behind it: an outer exhaust cone, a
shorter, hotter inner cone, and plasma puffs that flow from the nozzle down the exhaust, shrinking
and fading. The flame's length, width and brightness flicker (mixed sines), each reactor with its
own phase, so no two flicker in step. The core and flame bloom in the glow layer.

**Acceptance criteria**
- Given a reactor, then it has a nacelle, a core, an exhaust cone, an inner cone and puffs.
- Given a flame stepped over time, then its length, width and brightness vary within their flicker
  amounts and its puffs travel down the exhaust and start again (unit tests).

*Sources: P02-R01, P02-R02, P02-R03, D-006.*

### GFX-SHIP-07 — Size and heading on the playfield · SHOULD

On the playfield a ship is drawn `PLAYER_SHIP_SCALE` logical pixels per model unit, nose up the
screen; the Balanced ship is then about 34 px long, the length `L` other specs measure in.

**Acceptance criteria**
- Given the Balanced ship on the playfield, then it is about 34 px long, nose towards the top.

*Sources: D-015.*

### GFX-SHIP-08 — The ship banks as it moves sideways · MUST

The ship model rolls about its nose axis when it moves sideways: the wing on the side it flies to
dips, up to `max_deg` at full sideways speed, easing towards that at `ease_per_sec`, so it rolls in
and levels out smoothly. The bank follows the ship's speed, not the keys. It is visual only: the
hitbox and the shots are unchanged.

**Acceptance criteria**
- Given the ship flying right at full speed, then it settles at a bank of `max_deg`, its right wing
  down; given it stops, it levels out.

*Sources: D-045.*

### GFX-SHIP-09 — How the ship glows · MUST

The ship's glow is its own lights: its cyan edge trim (GFX-TRIM-05), its reactor flames and its nav
lights. There is no other outline or halo round it, and no hitbox marker (GFX-READ-08).

**Acceptance criteria**
- Given the ship in play, then it shows its trim, flames and nav lights and nothing else round it.

*Sources: D-220, P14-R03, D-194.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| Hull | albedo [0.56, 0.63, 0.74], metallic 0.9, roughness 0.25 | `src/game/config/ship_look.py` `SHIP_LOOK["hull"]` |
| Accent | albedo [0.16, 0.3, 0.6], metallic 0.75, roughness 0.3 | `SHIP_LOOK["accent"]` |
| Canopy | albedo [0.03, 0.08, 0.18], emissive [0, 0.06, 0.12] | `SHIP_LOOK["canopy"]` |
| Nav lights | emissive [0.45, 0.85, 1] | `SHIP_LOOK["navLight"]` |
| Reactor core / exhaust / flame / plasma | [0.35, 0.75, 1] / [0.1, 0.45, 1] α 0.45 / [0.55, 0.85, 1] α 0.75 / [0.3, 0.7, 1] α 0.6 | `SHIP_LOOK` |
| Flame flicker | length ±0.14, width ±0.06, brightness ±0.2; 5.3, 11.7, 19.1 Hz | `REACTOR_FLAME` in `ship_look.py` |
| Inner flame | 0.6 length, 0.55 width of the exhaust cone | `REACTOR_FLAME` |
| Puffs | 3, 1.8 exhaust lengths/s, 1.1 nacelle radius | `REACTOR_FLAME` |
| `PLAYER_SHIP_SCALE` | 7 px per model unit | `ship_look.py` |
| Bank | `max_deg` 35°, `ease_per_sec` 8 | `src/config/game_play.py` `ShipRoll(35, 8)` |
| Triangle budget | 2,000 per ship | GFX-SHIP-05 |

## Notes

- The ship models were designed as references "inspired by" their models, not replicas; they were
  validated by eye in phase 2. The Light ship was reworked after review, as it first looked too much
  like an X-wing.
- The ships were first shown on a `player_ship/` viewer page, removed with the other debug pages
  (D-187); the dev menu's ship viewer shows them now (see [DEV-MENU](../dev/dev-menu.md)).
