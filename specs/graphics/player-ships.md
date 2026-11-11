# Player ships

> **Area:** Graphics · **Prefix:** `GFX-SHIP` · **Related:** [../gameplay/player-ship.md](../gameplay/player-ship.md), [art-direction.md](art-direction.md), [edge-trim.md](edge-trim.md), [readability.md](readability.md), [shots.md](shots.md)

The look of the player's ship, the Balanced one (the Heavy and Light ships were removed, D-326):
its model, its materials, its reactors and animated flames, how it banks and how it glows. It is
generated in code (GFX-ART-01); its upper half, the side the playfield camera sees, is smooth and
finely built, its belly low-poly and polygonal (GFX-ART-09, D-327). Its speed, health and handling
are in [GAME-SHIP](../gameplay/player-ship.md).

## Requirements

### GFX-SHIP-01 — Balanced ship · MUST

The Balanced ship is a heavy variable fighter, an original design (owner, 2026-11-11, D-328: a
variable fighter "with full upgrades", in the genre but copying no existing design). It is about
5.2 model units long (4.8 until D-332).

**Central body** (owner, D-332: "make the central body longer and thiner, the central body had no
back reactor"): a long, slim fuselage, a needle nose swelling into the cockpit, widest behind it
(0.66 across at its chine), tapering to a point at the tail; nothing comes out of its back. A
framed bubble canopy set forward, a teardrop with its peak ahead of its middle; canards; a gun
pod under the belly. It is one blended skin (D-327: "smoth the transition between the elements"):
a loft through cross-sections, each section's top the smooth union of the rounded back and a thin
chine along the flanks, rounded into a fillet by a smooth maximum (`hull_fillet`), the chine's
edge as high as the wings' top faces; smooth-shaded on top over a flat three-facet belly; its
sizes follow smooth curves through hand-set stations.

**Main reactors** (D-332: "spead the two main reactors, adding pieces of wings that connect them
to the central body"): two big nacelles standing out either side of the body, each with its
intake, joined to the body by a stub wing reaching from inside the body's chine into the nacelle,
along its length. Each carries a canted tail on its top, leaning no further out than the nacelle's
edge, and a ventral fin under it.

**Wings:** forward-swept (D-330: "make the wings front sided"; the tip's leading and trailing
edges ahead of the root's, a square-cut tip), running out of the nacelles towards their back
(D-333: "move the wings more to the back"), with flap and panel lines. The canards lie with their
top face at the body's chine edge, as the wings do, so their trim runs on from the body's beside
the cockpit (D-333: "lower the front wings so their highlight is aligned to the cockpit one").
Each tip carries twin reactors one over the other (D-330, D-331), one above the wing's plane
and one below, each with its own intake and a small gunmetal fin at 45°, the upper one's up and
out, the lower one's down and out; one steel body wraps both (D-332: "add more body to the wings
reactors, connecting them"), a tall rounded rectangle in section, their intakes and nozzles out at
its ends. A missile launcher hangs under each wing (D-330): a steel rounded hexagon pod on a
gunmetal pylon, an accent band behind its front, two small fins at 45° under its tapered tail,
its front out ahead of the leading edge, so the playfield camera sees the seven accent missile
tips in its dark launch face.

**Reactors:** every reactor is a rounded hexagon (D-330: "make the ship reactor rounded
hexagons"): its nacelle, rings, core and flame have six sides, the nacelle's corners rounded. Each
has a visible intake at its front (owner: "add visible cool looking intakes on the reactors", "add
intake to the reactors"): a flared rounded hexagon scoop in hull metal with an accent lip, its duct
running back to a dark fan face, a spinner at its centre; the mouths face forward, so the frontal
menu camera looks straight into them.

No gun stands on top (D-330), and the ship carries no light of its own but its reactors (D-327).

**Acceptance criteria**
- Given the Balanced model, then its wing tips' leading and trailing edges are ahead of their
  roots (forward-swept), the wing's root in the nacelle; twin reactors one over the other at each
  wing tip, wrapped in one body short of their intakes and nozzles, their fins canted 45° (unit
  tests).
- Given the main reactors, then they stand clear of the central body, each end of the stub wing
  inside the body's chine or the nacelle, and the tails lean no further out than the nacelle's
  edge (unit tests).
- Given the central body, then it is 5.2 long, at most 0.7 wide, and closes to a point at both
  ends (unit tests).
- Given a rounded hexagon or rounded rectangle section, then its points lie inside the sharp
  shape, its sides where the sharp shape's are (unit tests).
- Given each missile pod, then it hangs wholly under its wing, between root and tip, its front
  out ahead of the leading edge; no cannon (unit tests).
- Given a smooth-top lathe or the lofted hull, then its top's vertices share one normal pointing
  outward, each belly triangle has a single normal, and its triangles face outward (unit tests).
- Given the hull, then its top is mirrored and meets the wings' plane at the chine's edge (unit
  tests).
- The design is validated by eye (manual).

*Sources: P02-R01, D-327, D-328, D-330, D-331, D-332, D-333.*

### GFX-SHIP-02 — (removed) Heavy ship

Removed with the Heavy ship (D-326).

### GFX-SHIP-03 — (removed) Light ship

Removed with the Light ship (D-326).

### GFX-SHIP-04 — Satin grey/blue metal in three shades · MUST

The player ship's materials are made once per scene: a grey/blue physically based metal in three
shades (D-327, owner: "add different shades of metalic"): a light silver **hull** (the blended
body, the intake shells), a mid **steel** (the wings, stub wings, canards, spinners, missile
pods and the tip reactors' body) and a dark **gunmetal** (the tails, ventral fins, flaps, panel
lines, the missile pylons and fins, the tip reactors' fins); a blue accent metal (the intake lips,
the reactors' rings, the missile pods' bands and missile tips), a dark canopy with a faint blue glow, a darker trim metal (frames, barrels, launch faces) and a dark
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
D-330; measured 8,196 in the browser with its flames and its six reactors, D-332). The extra triangles go on its upper half only, the side the
playfield camera sees: the hull's sections have 24 facets across the top and 3 under the belly, the
canopy 16 over 3; the canopy frame, mostly hidden, 8 over 2; the tip reactors' body, a rounded
rectangle of 12 points, smooth all round. The reactors and missile pods are rounded
hexagons, 3 points a corner (18 round), their rings 2 (12 round). The gun pod under the belly keeps
6 sides, the missile tips 4.

**Acceptance criteria**
- Given the player ship model, then it has fewer than 11,000 triangles (manual: the dev ship viewer's
  polygon count).
- Given the hull and its round parts, then at least three quarters of their triangles lie over the
  upper half (unit tests).

*Sources: D-007, D-327.*

### GFX-SHIP-06 — Reactors with a living blue flame · MUST

Each of the ship's six reactors (two in the nacelles, two on each wing tip, D-330, D-331) is a rounded hexagon metal nacelle with a smooth top (GFX-SHIP-05), ring bands, a
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
screen; the Balanced ship is then about 36 px long (34 until D-332), the length `L` other specs
measure in.

**Acceptance criteria**
- Given the Balanced ship on the playfield, then it is about 36 px long, nose towards the top.

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
| Sections | hull 24 / 3, canopy 16 / 3, intakes, nacelles, rings 12 / 3, canopy frame 8 / 2 (upper / lower facets) | `balanced_hull.py` `TOP_POINTS`; `ship_parts.py` `SMOOTH_PART_SECTION`; `balanced_ship.py` |
| Hull stations | 12 (z 2.75 to -2.45, closed at both ends), each gap cut in 3 | `balanced_hull.py` `STATIONS`, `STATION_STEPS` |
| `hull_fillet` | 0.1 model units | `balanced_hull.py` `FILLET` |
| `profile_steps` | 3 | `balanced_ship.py` `PROFILE_STEPS` |
| Wing | forward-swept: root x 0.8 (z -0.7 to -1.85), tip x 1.9 (z -0.05 to -0.75) | `balanced_ship.py` `BALANCED_WING` |
| Reactor section | hexagon, corners rounded at 0.3 of the radius, 3 points a corner (rings 2) | `ship_parts.py` `REACTOR_SIDES`, `REACTOR_ROUNDING`, `REACTOR_CORNER_STEPS`, `RING_CORNER_STEPS` |
| Reactor intake | flared scoop to 1.02 radii, lip, fan at 0.68 radii, spinner | `ship_parts.py` `REACTOR_INTAKE*` |
| Tip reactors | x 1.98, y 0.125 and -0.125, z -0.4; radius 0.11, length 0.95; fins at 45° | `TIP_REACTOR`, `TIP_FIN`, `TIP_FIN_CANT` |
| Tail cant | 0.2 rad outwards, on the nacelles | `TAIL_CANT` |
| Nacelles | at x ±0.8, y -0.02, centre z -0.95; radius 0.22, length 2.0; with intakes | `REACTOR`, `REACTOR_OFFSET_X`, `REACTOR_Y`, `REACTOR_Z` |
| Stub wings | from x 0.1-0.15 in the body to 0.62 in the nacelle, z 0.2 to -2.0 | `STUB_WING` |
| Tip reactors' body | rounded rectangle 0.125 x 0.255 half, corners 0.1; z 0.36 to -0.42 from the reactors' middle | `TIP_BODY`, `TIP_BODY_PROFILE` |
| Missile pods | under the wing at x 1.3, y -0.2, z -0.4; radius 0.1, 1.16 long; 7 tips | `MISSILE_POD`, `MISSILE_POD_PROFILE`, `MISSILE_TIPS` |

## Notes

- The ship is an original design (D-328): it takes the genre's traits (a variable fighter with
  big leg-like nacelles and an add-on weapons pack), not any existing design's shapes or colours.
- The ship models were first designed as references "inspired by" their models, not replicas; they were
  validated by eye in phase 2. The Heavy (a B-2 style flying wing) and the Light (a four-winged
  tandem interceptor) were removed with the ship select screen (D-326).
- The ships were first shown on a `player_ship/` viewer page, removed with the other debug pages
  (D-187); the dev menu's ship viewer shows them now (see [DEV-MENU](../dev/dev-menu.md)).
