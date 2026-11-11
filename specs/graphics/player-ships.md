# Player ships

> **Area:** Graphics · **Prefix:** `GFX-SHIP` · **Related:** [../gameplay/player-ship.md](../gameplay/player-ship.md), [art-direction.md](art-direction.md), [edge-trim.md](edge-trim.md), [readability.md](readability.md), [shots.md](shots.md)

The look of the player's ship, the Balanced one (the Heavy and Light ships were removed, D-326):
its model, its materials, its reactors and animated flames, how it banks and how it glows. It is
generated in code (GFX-ART-01); its upper half, the side the playfield camera sees, is finely
built, its belly low-poly and polygonal (GFX-ART-09, D-327); its central body is faceted (D-336). Its speed, health and handling
are in [GAME-SHIP](../gameplay/player-ship.md).

## Requirements

### GFX-SHIP-01 — Balanced ship · MUST

The Balanced ship is a heavy variable fighter, an original design (owner, 2026-11-11, D-328: a
variable fighter "with full upgrades", in the genre but copying no existing design). It is about
5.2 model units long (4.8 until D-332).

**Central body** (owner, D-332: "make the central body longer and thiner, the central body had no
back reactor"): a long, slim fuselage, a needle nose swelling into the cockpit, widest behind it
(0.52 across), tapering to a point at the tail; nothing comes out of its back. A framed bubble
canopy set forward, a teardrop with its peak ahead of its middle, its front rounded off rather than
pointed (D-346, owner: "make the cockpit tip less pointy"); canards. Under the belly
(D-339, owner: "rework the undergun, make a cool looking laser and add two miniguns on it's
sides"; D-340: "make the lazer longer, it should go further than the tip of the ship, and rework
those weapons, make them better integrated into the hull"): a faceted keel fairing of hull metal
grows out of the belly, its top inside it; out of its nose, under the ship's nose and past its
tip, runs the laser (D-342, owner: "review the laze design, the rings sucks"; a barrel ringed by
accent coils before): two gunmetal rails tapering forward into prongs either side of a glowing
core rod, joined at their back by a bridge, a glowing emitter at the core's tip between the
prongs; a minigun sits in each flank of the fairing, its hull-metal drum half sunk in it as
a blister, six thick barrels round its axis out ahead of it, each hollow at its muzzle, held by a
gunmetal clamp (D-345: "increase the minigun size again, and add hole into the barrels"; D-346:
"spread the minguns a little more"; D-349: "and spread the minigun more again", the fairing
widened under the body's flanks, its top corners inside the hull's underside; D-341, owner:
"increase ther size of the miniguns, and make their cannons thicker"). It is one skin (D-327: "smoth the transition between the elements"), a loft through
cross-sections whose sizes follow smooth curves through hand-set stations, and it is faceted
(D-336, owner: "rework the central part, it's too round, add more details, make a better
connection with the wings"): each section is flat facets, flat-shaded so their edges read crisp: a
spine ridge from behind the canopy to the tail, a flat deck either side of it, bevelled shoulders,
flat chines, flat flanks and belly. The chines lie at the wings' top face and widen behind the
canards into flat strakes reaching the nacelles (1.28 across), along them and back to the
nacelles' ends: the body itself joins the nacelles, its strakes' leading edge one swept curve from
the canards to the intakes. Details: dark panel seams round the body at four places; three dark
vents on each strake, in front of the wing roots.

**Main reactors** (D-332: "spead the two main reactors, adding pieces of wings that connect them
to the central body"): two big nacelles standing out either side of the body, each with its
intake, joined to the body by its strakes (D-336; by a separate stub wing from D-332), along
their length. Each carries a canted tail on its top, leaning no further out than the nacelle's
edge, and a ventral fin under it.

**Wings:** forward-swept (D-330: "make the wings front sided"; the tip's leading and trailing
edges ahead of the root's, a square-cut tip with a chamfered front corner, running on a little
past the tip reactors, D-339: "make the wings go a little beyond the side reactors"), running out
of the nacelles towards their back
(D-333: "move the wings more to the back"), with flap and panel lines. The canards lie with their
top face at the body's chine edge, as the wings do, so their trim runs on from the body's beside
the cockpit (D-333: "lower the front wings so their highlight is aligned to the cockpit one").
Each tip carries twin reactors one over the other (D-330, D-331), one above the wing's plane
and one below, each with a small gunmetal fin at 45°, the upper one's up and out, the lower
one's down and out; one steel body wraps both (D-332: "add more body to the wings reactors,
connecting them"), a tall rounded rectangle in section, from their fronts to short of their
nozzles, and one octagonal intake at its front, stretched upright to the body's height, feeds both
(D-339, owner: "merge the two lateral intales into a single octogonal intake"; an intake each
before). A missile launcher runs through each wing (D-330; D-343, owner: "make the missile pods
hexagonal, higher and make them go trough the wings"; it hung under the wing on a pylon before;
D-344: "make the missile pods octogonal"): a steel octagon pod, flat on top, bottom and sides,
with crisp, barely rounded corners, flat-shaded, 1.35 times taller than wide,
its axis in the wing's plane, an accent band behind its front, two small fins at 45° under its tapered tail,
its front out ahead of the leading edge, so the playfield camera sees the seven accent missile
tips in its dark launch face.

**Reactors:** every reactor is a rounded polygon (D-330: "make the ship reactor rounded
hexagons"): its nacelle, rings, core and flame have the same sides, the nacelle's corners rounded.
The main reactors are octagons, flat on top, bottom and sides (D-339, owner: "make the main reactor
octogonal too"); the tip reactors stay hexagons. The main reactors and the tip pairs have a
visible intake at their front (owner: "add visible cool looking intakes on the reactors", "add
intake to the reactors"): a rounded polygon scoop in hull metal, of the reactor's sides, that runs on straight from the
nacelle, then angles inward a little to a thin lip (D-337, owner: "make it start flat, then angled
inward a little, and make a better inner part"), flush with the nacelle, which runs on at full size to it (D-340, owner: "remove the circular bump
around the intakes": it stood proud of the nacelle, with an accent band, before); inside, a dark
duct lining and fan face, matte black (D-347, owner: "make the back of the reactor intake mat
black"), with four flat horizontal steel fins across the duct in front of
it, each as wide as the duct's polygon at its height (D-338, owner: "replace the central helix by
horizontal fins in the reactors"; ten fan blades round a spinner before); the mouths
face forward, so the frontal menu camera looks straight into them. The two main reactors are taller
than wide (D-337: "make the main reactors higher"): their section stretched 1.3 times upright, the
tails and ventral fins standing on the taller nacelles. On the top and the bottom of each main
reactor sits a secondary intake (D-347, owner: "add secondary intake at the top and botton of each
of the main reactors, with a slope eaching the back of the reactor"): a silver scoop on the
nacelle's flat face, behind its front ring, its matte black mouth facing forward, its back a ramp
sloping down to the nacelle's back; a rounded arch in section, smooth-shaded, the ramp easing down
along a half cosine, three flat steel fins across its mouth (D-348, owner: "rework the secondary
intakes, smoth them a little and add fins like the others").

No gun stands on top (D-330), and the ship carries no light of its own but its reactors (D-327).

**Acceptance criteria**
- Given the Balanced model, then its wing tips' leading and trailing edges are ahead of their
  roots (forward-swept), the wing's root in the nacelle and its tip a little past the tip
  reactors' body; twin reactors one over the other at each wing tip, wrapped in one body from
  their fronts to short of their nozzles, one octagonal intake as wide and tall as the body feeding
  both, their fins canted 45°; the main reactors octagons with intakes (unit tests).
- Given the guns under the belly, then a laser lies on the centre line and a minigun of six
  barrels either side of it; the fairing's top lies inside the belly, the minigun drums half in
  its flanks, and the laser's rails clear under the nose, its core and prongs past the nose's tip
  (unit tests).
- Given the main reactors, then the body's strakes reach into them from their front to the wing
  roots' back, the body itself under half as wide as the gap between them, and the tails lean no
  further out than the nacelle's edge (unit tests).
- Given the central body, then it is 5.2 long, at most 0.6 wide past its strakes, and closes to a
  point at both ends; its seams lie along it and its vents on the flat of its strakes (unit
  tests).
- Given a rounded hexagon or rounded rectangle section, then its points lie inside the sharp
  shape, its sides where the sharp shape's are (unit tests).
- Given a reactor's intake, then its skin runs straight then angles inward to its lip, its duct
  lining faces the axis, and flat horizontal fins span the duct inside its hexagon, with no fan
  blades or spinner; the main reactors are taller
  than wide (unit tests).
- Given each missile pod, then the wing runs through it, its top above the wing and its bottom
  below, taller than wide, between root and tip, its front out ahead of the leading edge; no
  cannon (unit tests).
- Given a smooth-top lathe or a lofted skin, then its top's vertices share one normal pointing
  outward, each belly triangle has a single normal, and its triangles face outward (unit tests).
- Given the hull, then its top is mirrored, rises facet by facet from the flat strake to the spine
  and meets the wings' plane at the chine's edge (unit tests).
- The design is validated by eye (manual).

*Sources: P02-R01, D-327, D-328, D-330, D-331, D-332, D-333, D-336, D-337, D-338, D-339, D-340, D-341, D-342, D-343, D-344, D-345, D-346, D-347, D-348, D-349.*

### GFX-SHIP-02 — (removed) Heavy ship

Removed with the Heavy ship (D-326).

### GFX-SHIP-03 — (removed) Light ship

Removed with the Light ship (D-326).

### GFX-SHIP-04 — Satin grey/blue metal in three shades · MUST

The player ship's materials are made once per scene: a grey/blue physically based metal in three
shades (D-327, owner: "add different shades of metalic"): a light silver **hull** (the blended
body, the intake shells), a mid **steel** (the wings, canards, intake fins, missile
pods and the tip reactors' body) and a dark **gunmetal** (the tails, ventral fins, flaps, panel
lines, the body's seams and vents, the missile fins, the tip reactors' fins); a blue accent metal (the
reactors' rings, the missile pods' bands and missile tips), a dark canopy with a faint blue glow, a darker trim metal (frames, barrels, launch faces) and a dark
metal nozzle; the intakes' ducts and fan faces are a matte black, no metal and fully rough (D-347). The metals are satin, not mirrors (owner: "remove the ugly light spots, make something
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
D-330; measured 10,004 in the browser with its flames, its six reactors and their four finned intakes,
D-348). The round
parts' extra triangles go on their upper half only, the side the playfield camera sees: the
canopy 16 over 3; the canopy frame, mostly hidden, 8 over 2; the tip reactors' body, a rounded
rectangle of 12 points, smooth all round. The tip reactors are rounded
hexagons, 3 points a corner (18 round), their rings 2 (12 round); the main reactors and the tip
intakes octagons (24 round, rings 16); the missile pods crisp flat-shaded octagons, 2 points a
corner (16 round). The gun fairing is 6 flat facets round; the laser and the miniguns' drums are 8-sided, the
miniguns' barrels 6 and the missile tips 4. The central body is flat facets all round (D-336): 8 across the top,
7 round the underside, under a thousand triangles.

**Acceptance criteria**
- Given the player ship model, then it has fewer than 11,000 triangles (manual: the dev ship viewer's
  polygon count).
- Given the round parts, then at least three quarters of their triangles lie over the upper half;
  the faceted hull has under a thousand (unit tests).

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

The ship's glow is its own lights: its glowing extremities and its reactor flames (no nav lights
since D-327). There is no outline, trim or halo round it (D-335, owner: "remove the highlight as an
outter layer for the player's ship, instead make it look like it's the extremities of the wings and
cockpit that are glowing, no highlight on the guns"), and no hitbox marker (GFX-READ-08).

The extremities glow a self-lit cyan (`SHIP_LOOK.edgeGlow`), which blooms in the glow layer: a thin
strip along the leading edge of each main wing, body strake (in short strips along its curve,
D-336) and canard (and the canard's tip), and of each tail and ventral fin (and its tip; D-346,
owner: "add highlight to the vertical wings too"), half
on the panel and half out past it, a hair thicker than the panel so it caps the edge seen from
above and from ahead; and the canopy's frame, whose rim shows round the canopy. The guns (the
missile launchers, the laser, the miniguns and their fairing) and the reactors' bodies do not glow, but for the
laser's core and emitter, of the reactors' core light (D-339, D-342). The main wing's strip stops
either side of the tip reactors' body, so it does not cross their intake (D-339).

**Acceptance criteria**
- Given the ship model, then it has no trim; the main wings', strakes', canards', tails' and ventral
  fins' leading edges
  have a glowing strip, none of the guns do, and the canopy's frame is of the glowing material (unit
  tests).
- Given the ship in play, then it shows its glowing edges and flames and nothing else round it
  (manual).

*Sources: D-220, P14-R03, D-194, D-327, D-335, D-336.*

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
| Edge glow | emissive [0.25, 0.85, 1]; strips 0.035 wide, the panel's thickness + 0.006 | `ship_look.py` `SHIP_LOOK["edgeGlow"]`; `balanced_ship.py` `EDGE_GLOW` |
| Sections | hull 9 points over the top, 6 under it, all flat (D-336), canopy 16 / 3, intakes, nacelles, rings 12 / 3, canopy frame 8 / 2 (upper / lower facets) | `balanced_hull.py` `TOP_POINTS`; `ship_parts.py` `SMOOTH_PART_SECTION`; `balanced_ship.py` |
| Hull stations | 12 (z 2.75 to -2.45, closed at both ends), each gap cut in 3 | `balanced_hull.py` `STATIONS`, `STATION_STEPS` |
| Hull facets | chine root 1.1, shoulder 0.8, deck edge 0.4 of the body's half width; shoulder at 0.75 of the deck's height | `balanced_hull.py` `CHINE_ROOT`, `SHOULDER`, `DECK_EDGE`, `SHOULDER_HEIGHT` |
| Body details | seams at z 1.7, 0.55, -0.75, -1.75 (0.024 wide, 2% proud); 3 vents a side, x 0.34-0.5 from z -0.15 | `balanced_ship.py` `SEAM_ZS`, `SEAM`, `VENTS` |
| `profile_steps` | 3 | `balanced_ship.py` `PROFILE_STEPS` |
| Wing | forward-swept: root x 0.8 (z -0.7 to -1.85), tip x 2.3 (z 0.2 to -0.4, chamfered to 2.25, 0.24) | `balanced_ship.py` `BALANCED_WING` |
| Reactor section | hexagon (main reactors and tip intakes: octagon turned π/8), corners rounded at 0.3 of the radius, 3 points a corner (rings 2) | `ship_parts.py` `REACTOR_SIDES`, `polygon_turn`, `REACTOR_ROUNDING`, `REACTOR_CORNER_STEPS`, `RING_CORNER_STEPS`; `balanced_ship.py` `OCTAGON` |
| Reactor intake | straight at 1.0 radius (the nacelle's) to 0.24 ahead, angled in to 0.8 at 0.47; flush with the nacelle; dark duct, its end behind the fan face; fan face at 0.68 radii; 4 horizontal fins at heights ±0.14 and ±0.42, z 0.12 to 0.4, inside a 0.66 duct hexagon | `ship_parts.py` `REACTOR_INTAKE*` |
| Reactor scoops | top and bottom of each main reactor, z 0.5 to -1.0 of the nacelle, 0.16 wide, 0.1 high at the mouth, sunk 0.012; corners 0.035; a 0.06 lip then 4 eased ramp sections; mouth 0.72 of its size; fins at -0.28, 0, 0.28 of its height | `balanced_ship.py` `REACTOR_SCOOP` |
| Intake black | albedo [0.012, 0.012, 0.015], metallic 0, roughness 1 | `SHIP_LOOK["intakeBlack"]` |
| Tip reactors | x 1.98, y 0.125 and -0.125, z -0.4; radius 0.11, length 1.35 (0.95 until D-340); fins at 45° | `TIP_REACTOR`, `TIP_FIN`, `TIP_FIN_CANT` |
| Tail cant | 0.2 rad outwards, on the nacelles | `TAIL_CANT` |
| Nacelles | at x ±0.8, y -0.02, centre z -0.95; radius 0.22, length 2.0, 1.3 times taller than wide; with intakes | `REACTOR`, `REACTOR_HEIGHT`, `REACTOR_OFFSET_X`, `REACTOR_Y`, `REACTOR_Z` |
| Strakes | the body's chines, 0.64 half wide from z -0.4 to -1.2, 0.63 at -1.9; glowing edge from z 0.85 to -0.3 | `balanced_hull.py` `STATIONS`; `balanced_ship.py` `STRAKE_EDGE_ZS` |
| Tip reactors' body | rounded rectangle 0.125 x 0.255 half, corners 0.1; z 0.675 to -0.62 from the reactors' middle; one octagonal intake, radius 0.124, stretched 2.05 upright | `TIP_BODY`, `TIP_BODY_PROFILE`, `TIP_INTAKE` |
| Gun fairing | z -0.8 to 2.3, up to 0.21 half wide and 0.11 under the belly, its top 0.02 inside the belly and its top corners 0.02 inside the hull's underside (D-349) | `GUN_FAIRING`, `GUN_FAIRING_SECTION` |
| Laser | at y -0.1; glowing core z 2.1 to 3.06 (nose tip 2.75), radius 0.012; rails 0.034 thick, x 0.02 to 0.052, z 2.0 to prongs at 3.2; bridge z 2.0 to 2.2; emitter to 3.13 | `LASER`, `LASER_RAIL`, `LASER_BRIDGE`, `LASER_EMITTER` |
| Miniguns | at x ±0.27 (D-349), y -0.195, z 0.75; drum 0.9 long, radius 0.085, of hull metal; 6 six-sided barrels of radius 0.021 on a 0.048 ring, 0.5 long, each with a bore of 0.55 its radius, 0.06 deep (D-345, D-346) | `MINIGUN` |
| Missile pods | through the wing at x 1.3, y 0, z -0.4; octagon, radius 0.1, corners rounded 0.08, 1.35 times taller, 1.16 long; 7 tips | `MISSILE_POD`, `MISSILE_POD_ROUNDING`, `MISSILE_POD_PROFILE`, `MISSILE_TIPS` |

## Notes

- The ship is an original design (D-328): it takes the genre's traits (a variable fighter with
  big leg-like nacelles and an add-on weapons pack), not any existing design's shapes or colours.
- The ship models were first designed as references "inspired by" their models, not replicas; they were
  validated by eye in phase 2. The Heavy (a B-2 style flying wing) and the Light (a four-winged
  tandem interceptor) were removed with the ship select screen (D-326).
- The ships were first shown on a `player_ship/` viewer page, removed with the other debug pages
  (D-187); the dev menu's ship viewer shows them now (see [DEV-MENU](../dev/dev-menu.md)).
