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
canards, leading-edge extensions, intakes feeding two big engine nacelles, forward-swept wings
(owner, D-330: "make the wings front sided"; the tip's leading and trailing edges ahead of the
root's, a square-cut tip) with flap and panel lines, canted twin tails standing inside the hull's
outline seen from above, ventral fins and a gun pod under the belly.

Every reactor is a rounded hexagon (owner, D-330: "make the ship reactor rounded hexagons"): its
nacelle, rings, core and flame have six sides, the nacelle's corners rounded. Each wing tip carries
twin reactors side by side (owner: "add two reactors on the tip of each wing, with 45° lil wings on
each", then "make it a dual reactor on the tip of each wing, and add intake to the reactors"), each
with its own intake (a flared rounded hexagon scoop, an accent lip, a dark fan face and a spinner),
joined by a steel fairing, the outer one carrying two small gunmetal fins at 45° above and below
the wing's plane.

The pack: two booster engines on the back either side of the centre line, each a hump of the
hull's own skin with an accent band laid across it and its own reactor and flame (owner: "rework
the blend between the inner and outer reactors so they dont just looks like tubes put next to
each other"): the humps swell out of the back behind the cockpit and blend through fillets into
the back and the nacelle shoulders, and the hull runs aft to one engine block whose tail face
wraps the four engines, their nozzles coming out of it together; a gunmetal armour plate laid over
each nacelle shoulder, following the hull; and a missile launcher under each wing (owner: "rework
the missiles pods, make them look cool, and under the wings"): a steel rounded hexagon pod hung on
a gunmetal pylon, an accent band behind its front, two small fins at 45° under its tapered tail,
its front out ahead of the leading edge, so the playfield camera sees the seven accent missile tips
in its dark launch face. No gun stands on top (D-330: the rail cannon on the right shoulder was
removed). The ship carries no light of its own but its reactors (D-327: the nav lights, the pale
blue wing bands and the tail stripes are gone). It is about 4.8 model units long.

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
- Given the Balanced model, then its wing tips' leading and trailing edges are ahead of their
  roots (forward-swept); it has two nacelles, each with an intake ahead of it (a shell, a lip, a
  fan face, a glowing fan ring and a spinner), and twin reactors side by side at each wing tip,
  their fins canted 45° (unit tests).
- Given a rounded hexagon section, then its points lie between the hexagon's sides and corners,
  its sides where the sharp hexagon's are (unit test).
- Given the hull, then the booster humps stand over the back and over their engines, and its tail
  face lies just ahead of all four nozzles (unit tests).
- Given the pack, then each missile pod hangs wholly under its wing, between root and tip, its
  front out ahead of the leading edge; no cannon; each armour plate's top follows the hull a
  thickness over it (unit tests).
- Given the hull, then aft it is wider than the nacelles and the tails lean no further out than
  its edge, so the trim runs along it unbroken (unit tests).
- Given a smooth-top lathe or the lofted hull, then its top's vertices share one normal pointing
  outward, each belly triangle has a single normal, and its triangles face outward (unit tests).
- Given the hull at the widest stations, then its top between the back and a shoulder never dips
  under three quarters of the lower of the two, and it meets the wing plane at the chine's edge
  (unit tests).
- The design is validated by eye (manual).

*Sources: P02-R01, D-327, D-328, D-330.*

### GFX-SHIP-02 — (removed) Heavy ship

Removed with the Heavy ship (D-326).

### GFX-SHIP-03 — (removed) Light ship

Removed with the Light ship (D-326).

### GFX-SHIP-04 — Satin grey/blue metal in three shades · MUST

The player ship's materials are made once per scene: a grey/blue physically based metal in three
shades (D-327, owner: "add different shades of metalic"): a light silver **hull** (the blended
hull, the intake shells), a mid **steel** (the wings, canards, spinners, missile pods and the tip
reactors' fairings) and a dark **gunmetal** (the tails, ventral fins, flaps, panel lines, armour
plates, the missile pylons and fins, the tip reactors' fins); a blue accent metal (the intake lips
and fan rings, the bands across the booster humps, the missile pods' bands and missile tips), a
dark canopy with a faint blue glow, a darker trim metal (frames, barrels, launch faces) and a dark
metal nozzle. The metals are satin, not mirrors (owner: "remove the ugly light spots, make something
more smoth"): metallic at least 0.7, roughness 0.4 to 0.55, so the light rolls smoothly over the
hull instead of breaking into hard white spots. Each shade is more blue than red, and each darker
than the one before. The metals take the brighter hull light of GFX-ART-08.

**Acceptance criteria**
- Given a scene, then the ship materials are made once and shared by every model using them (unit test).
- Given the hull, steel and gunmetal looks, then each is metallic ≥ 0.7 with a roughness from 0.4
  to 0.55 and an albedo more blue than red, and each is darker than the one before (unit test).

*Sources: GD-61, P02-R01, D-127.*

### GFX-SHIP-05 — Polygon budget · MUST

The player ship is under 11,000 triangles (2,000 until D-327, 4,500 until D-328, 7,000 until
D-330; measured 10,398 in the browser with its flames and its eight reactors, D-330). The extra triangles go on its upper half only, the side the
playfield camera sees: the hull's sections have 30 facets across the top and 3 under the belly, the
canopy 16 over 3, the intakes, nacelles and their rings 12 over 3; the canopy
frame, mostly hidden, 8 over 2; the armour plates and booster bands lie wholly on top. The reactors and missile pods are rounded
hexagons, 3 points a corner (18 round), their rings 2 (12 round). The gun pod under the belly keeps
6 sides, the missile tips 4.

**Acceptance criteria**
- Given the player ship model, then it has fewer than 11,000 triangles (manual: the dev ship viewer's
  polygon count).
- Given the hull and its round parts, then at least three quarters of their triangles lie over the
  upper half (unit tests).

*Sources: D-007, D-327.*

### GFX-SHIP-06 — Reactors with a living blue flame · MUST

Each of the ship's eight reactors (two in the nacelles, one behind each booster, D-328, two on each
wing tip, D-330) is a rounded hexagon metal nacelle with a smooth top (GFX-SHIP-05), ring bands, a
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
| Triangle budget | 11,000 | GFX-SHIP-05 |
| Sections | hull 30 / 3, canopy 16 / 3, intakes, nacelles, rings 12 / 3, canopy frame 8 / 2 (upper / lower facets) | `balanced_hull.py` `TOP_POINTS`; `ship_parts.py` `SMOOTH_PART_SECTION`; `balanced_ship.py` |
| Hull stations | 12 (to the tail face at z -2.0), each gap cut in 3 | `balanced_hull.py` `STATIONS`, `STATION_STEPS` |
| `hull_fillet` | 0.1 model units | `balanced_hull.py` `FILLET` |
| Shoulders | at x = ±0.42, 0.22 half wide | `balanced_hull.py` `SHOULDER_X`, `SHOULDER_HALF_WIDTH` |
| `profile_steps` | 3 | `balanced_ship.py` `PROFILE_STEPS` |
| Wing | forward-swept: root x 0.4 (z 0.05 to -1.05), tip x 1.9 (z 0.55 to -0.15) | `balanced_ship.py` `BALANCED_WING` |
| Reactor section | hexagon, corners rounded at 0.3 of the radius, 3 points a corner (rings 2) | `ship_parts.py` `REACTOR_SIDES`, `REACTOR_ROUNDING`, `REACTOR_CORNER_STEPS`, `RING_CORNER_STEPS` |
| Reactor intake | flared scoop to 1.02 radii, lip, fan at 0.68 radii, spinner | `ship_parts.py` `REACTOR_INTAKE*` |
| Tip reactors | x 1.97 and 2.2, z 0.2; radius 0.11, length 0.95; fins at 45° | `TIP_REACTOR`, `TIP_FIN`, `TIP_FIN_CANT` |
| Tail cant | 0.3 rad outwards | `TAIL_CANT` |
| Nacelles | radius 0.22, length 2.0, centre z -1.15 | `REACTOR`, `REACTOR_Z` |
| Booster humps | at x ±0.18, 0.17 half wide, up to 0.42 high | `balanced_hull.py` `BOOSTER_X`, `BOOSTER_HALF_WIDTH`, `STATIONS` |
| Booster engines | y 0.28, z -1.85; radius 0.09, length 0.5 | `balanced_ship.py` `BOOSTER_ENGINE` |
| Armour plates | x 0.29 to 0.57, z 0.35 to -0.6, 0.035 thick, 9 points across | `ARMOUR_XS`, `ARMOUR_ZS`, `ARMOUR_THICKNESS`, `ARMOUR_POINTS` |
| Missile pods | under the wing at x 1.15, y -0.2, z 0.2; radius 0.1, 1.16 long; 7 tips | `MISSILE_POD`, `MISSILE_POD_PROFILE`, `MISSILE_TIPS` |

## Notes

- The ship is an original design (D-328): it takes the genre's traits (a variable fighter with
  big leg-like nacelles and an add-on weapons pack), not any existing design's shapes or colours.
- The ship models were first designed as references "inspired by" their models, not replicas; they were
  validated by eye in phase 2. The Heavy (a B-2 style flying wing) and the Light (a four-winged
  tandem interceptor) were removed with the ship select screen (D-326).
- The ships were first shown on a `player_ship/` viewer page, removed with the other debug pages
  (D-187); the dev menu's ship viewer shows them now (see [DEV-MENU](../dev/dev-menu.md)).
