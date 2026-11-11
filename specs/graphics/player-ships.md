# Player ships

> **Area:** Graphics · **Prefix:** `GFX-SHIP` · **Related:** [../gameplay/player-ship.md](../gameplay/player-ship.md), [art-direction.md](art-direction.md), [edge-trim.md](edge-trim.md), [readability.md](readability.md), [shots.md](shots.md)

The look of the player's ship, the Balanced one (the Heavy and Light ships were removed, D-326):
its model, its materials, its reactors and animated flames, how it banks and how it glows. It is
generated in code (GFX-ART-01); its upper half, the side the playfield camera sees, is smooth and
finely built, its belly low-poly and polygonal (GFX-ART-09, D-327). Its speed, health and handling
are in [GAME-SHIP](../gameplay/player-ship.md).

## Requirements

### GFX-SHIP-01 — Balanced ship · MUST

The Balanced ship is a heavy variable fighter carrying a full assault pack, an original design
(owner, 2026-11-11, D-328: a variable fighter "with full upgrades", in the genre but copying no
existing design): a long pointed nose, a framed bubble canopy set forward, a broad flat back,
canards, leading-edge extensions, intakes feeding two big engine nacelles that run out past the
tail, cranked wings swept back (the leading edge sweeps less past a kink halfway out; a square-cut
tip) with flap and panel lines, canted twin tails, ventral fins and a gun pod under the belly. The
pack on top: two booster engines on the back either side of the centre line, each a steel casing
with an accent band and its own reactor and flame; a gunmetal armour plate laid over each nacelle
shoulder, following the hull; a silver missile pod on each wing root, an accent stripe on top and
six launch tubes in its dark front face, the missiles' accent tips showing; and a long rail cannon
on the right shoulder, a gunmetal housing on a mount, its barrel between two accent rails, reaching
almost to the nose. It carries no light of its own but its reactors (D-327: the nav lights, the
pale blue wing bands and the tail stripes are gone). It is about 4.8 model units long.

Its hull is one blended skin, not a set of basic shapes put together (owner, 2026-11-11, D-327:
"rework the ship design to make it look better, more smoth" and "it looks like a bunch of basic
shaped put together, smoth the transition between the elements with more complex looking parts"):
a loft through cross-sections along the ship, each section's top the smooth union of the
fuselage's rounded back, two nacelle shoulders running from the intakes to the reactors, and a thin
chine sweeping out into the wing roots (the leading-edge extension, which replaces the strakes and
the separate spine). Where they meet, a smooth maximum (`hull_fillet`) rounds the joint into a
fillet, so the shoulders swell out of the back with only a shallow saddle between them and the
chine melts into the wings. The sizes follow smooth curves through hand-set stations. The skin is
smooth-shaded on top (normals averaged round each vertex) over a flat three-facet belly. The
canopy, intakes and nacelles are smooth-topped bodies of revolution, their profiles smooth curves
through a few hand-set points. The fuselage is a long needle nose swelling into the cockpit, widest
behind it; the canopy a teardrop bubble with its peak ahead of its middle.

Each reactor is fed by a visible intake just ahead of it (owner: "add visible cool looking intakes
on the reactors"): a hollow, flared scoop in hull metal, oval, with a blue accent lip round its
mouth; its duct turns in and runs back to a dark fan face ringed in blue metal, a spinner at its
centre. The mouths face forward, so the frontal menu camera looks straight into them.

**Acceptance criteria**
- Given the Balanced model, then its wing tips' leading edges are behind their roots (swept
  back), sweeping less outboard of the kink, and it has two reactors, each with an intake ahead of
  it (a shell, a lip, a fan face, a glowing fan ring and a spinner) (unit tests).
- Given the pack, then the boosters sit on the back inside the armour plates, the cannon over the
  right plate, the missile pods on the wings between root and tip, and each armour plate's top
  follows the hull a thickness over it (unit tests).
- Given a smooth-top lathe or the lofted hull, then its top's vertices share one normal pointing
  outward, each belly triangle has a single normal, and its triangles face outward (unit tests).
- Given the hull at the widest stations, then its top between the back and a shoulder never dips
  under three quarters of the lower of the two, and it meets the wing plane at the chine's edge
  (unit tests).
- The design is validated by eye (manual).

*Sources: P02-R01, D-327.*

### GFX-SHIP-02 — (removed) Heavy ship

Removed with the Heavy ship (D-326).

### GFX-SHIP-03 — (removed) Light ship

Removed with the Light ship (D-326).

### GFX-SHIP-04 — Satin grey/blue metal in three shades · MUST

The player ship's materials are made once per scene: a grey/blue physically based metal in three
shades (D-327, owner: "add different shades of metalic"): a light silver **hull** (the blended
hull, the intake shells, the missile pods), a mid **steel** (the wings, canards, spinners and
booster casings) and a dark **gunmetal** (the tails, ventral fins, flaps, panel lines, armour plates
and the cannon's housing); a blue accent metal (the intake lips and fan rings, the booster bands,
the pods' stripes and missile tips, the cannon's rails), a dark canopy with a faint blue glow, a darker trim metal (frames, barrels) and a dark metal
nozzle. The metals are satin, not mirrors (owner: "remove the ugly light spots, make something
more smoth"): metallic at least 0.7, roughness 0.4 to 0.55, so the light rolls smoothly over the
hull instead of breaking into hard white spots. Each shade is more blue than red, and each darker
than the one before. The metals take the brighter hull light of GFX-ART-08.

**Acceptance criteria**
- Given a scene, then the ship materials are made once and shared by every model using them (unit test).
- Given the hull, steel and gunmetal looks, then each is metallic ≥ 0.7 with a roughness from 0.4
  to 0.55 and an albedo more blue than red, and each is darker than the one before (unit test).

*Sources: GD-61, P02-R01, D-127.*

### GFX-SHIP-05 — Polygon budget · MUST

The player ship is under 7,000 triangles (2,000 until D-327, 4,500 until D-328; measured 6,398 in
the browser with its flames, D-328). The extra triangles go on its upper half only, the side the
playfield camera sees: the hull's sections have 24 facets across the top and 3 under the belly, the
canopy 16 over 3, the intakes, nacelles, booster casings and their rings 12 over 3; the canopy
frame, mostly hidden, 8 over 2; the armour plates lie wholly on top. The gun pod under the belly and
the cannon's housing and barrel keep 6 sides, the missile tips 4.

**Acceptance criteria**
- Given the player ship model, then it has fewer than 7,000 triangles (manual: the dev ship viewer's
  polygon count).
- Given the hull and its round parts, then at least three quarters of their triangles lie over the
  upper half (unit tests).

*Sources: D-007, D-327.*

### GFX-SHIP-06 — Reactors with a living blue flame · MUST

Each of the ship's reactors (two in the nacelles, one behind each booster, D-328) is a metal nacelle with a smooth top (GFX-SHIP-05), ring bands, a
blue self-lit core at its nozzle and an animated blue flame behind it: an outer exhaust cone, a
shorter, hotter inner cone, and plasma puffs that flow from the nozzle down the exhaust, shrinking
and fading. The flame's length, width and brightness flicker (mixed sines), each reactor with its
own phase, so no two flicker in step. The core and flame bloom in the glow layer.

**Acceptance criteria**
- Given a reactor, then it has a nacelle, a core, an exhaust cone, an inner cone and puffs.
- Given a flame stepped over time, then its length, width and brightness vary within their flicker
  amounts and its puffs travel down the exhaust and start again (unit tests).

*Sources: P02-R01, D-006.*

### GFX-SHIP-07 — Size and heading on the playfield · SHOULD

On the playfield the ship is drawn `PLAYER_SHIP_SCALE` logical pixels per model unit, nose up the
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

The ship's glow is its own lights: its cyan edge trim (GFX-TRIM-05) and its reactor flames (no nav
lights since D-327). There is no other outline or halo round it, and no hitbox marker
(GFX-READ-08).

**Acceptance criteria**
- Given the ship in play, then it shows its trim and flames and nothing else round it.

*Sources: D-220, P14-R03, D-194, D-327.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| Hull (silver) | albedo [0.6, 0.66, 0.76], metallic 0.8, roughness 0.42 | `src/game/config/ship_look.py` `SHIP_LOOK["hull"]` |
| Steel | albedo [0.4, 0.45, 0.54], metallic 0.85, roughness 0.45 | `SHIP_LOOK["hullMid"]` |
| Gunmetal | albedo [0.2, 0.23, 0.29], metallic 0.85, roughness 0.5 | `SHIP_LOOK["hullDark"]` |
| Accent | albedo [0.16, 0.3, 0.6], metallic 0.75, roughness 0.4 | `SHIP_LOOK["accent"]` |
| Canopy | albedo [0.03, 0.08, 0.18], emissive [0, 0.06, 0.12] | `SHIP_LOOK["canopy"]` |
| Reactor core / exhaust / flame / plasma | [0.35, 0.75, 1] / [0.1, 0.45, 1] α 0.45 / [0.55, 0.85, 1] α 0.75 / [0.3, 0.7, 1] α 0.6 | `SHIP_LOOK` |
| Flame flicker | length ±0.14, width ±0.06, brightness ±0.2; 5.3, 11.7, 19.1 Hz | `REACTOR_FLAME` in `ship_look.py` |
| Inner flame | 0.6 length, 0.55 width of the exhaust cone | `REACTOR_FLAME` |
| Puffs | 3, 1.8 exhaust lengths/s, 1.1 nacelle radius | `REACTOR_FLAME` |
| `PLAYER_SHIP_SCALE` | 7 px per model unit | `ship_look.py` |
| Bank | `max_deg` 35°, `ease_per_sec` 8 | `src/config/game_play.py` `ShipRoll(35, 8)` |
| Triangle budget | 7,000 | GFX-SHIP-05 |
| Sections | hull 24 / 3, canopy 16 / 3, intakes, nacelles, rings 12 / 3, canopy frame 8 / 2 (upper / lower facets) | `balanced_hull.py` `TOP_POINTS`; `ship_parts.py` `SMOOTH_PART_SECTION`; `balanced_ship.py` |
| Hull stations | 11, each gap cut in 3 | `balanced_hull.py` `STATIONS`, `STATION_STEPS` |
| `hull_fillet` | 0.1 model units | `balanced_hull.py` `FILLET` |
| Shoulders | at x = ±0.42, 0.22 half wide | `balanced_hull.py` `SHOULDER_X`, `SHOULDER_HALF_WIDTH` |
| `profile_steps` | 3 | `balanced_ship.py` `PROFILE_STEPS` |
| Wing | cranked, swept back: root x 0.4, kink x 1.2, tip x 2.05 to 2.1 | `balanced_ship.py` `BALANCED_WING` |
| Nacelles | radius 0.22, length 2.0, centre z -1.15 | `REACTOR`, `REACTOR_Z` |
| Boosters | at x ±0.18, y 0.3, z -0.95; casing radius 0.12; engine radius 0.1, length 0.5 | `BOOSTER_AT`, `BOOSTER_CASING`, `BOOSTER_ENGINE` |
| Armour plates | x 0.29 to 0.57, z 0.35 to -0.6, 0.035 thick, 9 points across | `ARMOUR_XS`, `ARMOUR_ZS`, `ARMOUR_THICKNESS`, `ARMOUR_POINTS` |
| Missile pods | x 0.84 to 1.18, z -0.15 to -0.86, 0.15 high; 3 × 2 tubes | `MISSILE_POD`, `MISSILE_TUBES` |
| Rail cannon | x 0.43; housing 0.95 long; barrel 1.7 long; rails 1.5 long | `CANNON` |

## Notes

- The ship is an original design (D-328): it takes the genre's traits (a variable fighter with
  big leg-like nacelles and an add-on weapons pack), not any existing design's shapes or colours.
- The ship models were first designed as references "inspired by" their models, not replicas; they were
  validated by eye in phase 2. The Heavy (a B-2 style flying wing) and the Light (a four-winged
  tandem interceptor) were removed with the ship select screen (D-326).
- The ships were first shown on a `player_ship/` viewer page, removed with the other debug pages
  (D-187); the dev menu's ship viewer shows them now (see [DEV-MENU](../dev/dev-menu.md)).
