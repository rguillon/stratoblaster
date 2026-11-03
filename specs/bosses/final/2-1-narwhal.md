# Narwhal — 2-1 final boss

> **Area:** bosses · **Prefix:** `FB-NARWHAL` · **Related:** [common.md](../common.md), [2-1 Great erg](../../worlds/world-2/2-1-great-erg.md), [World 2](../../worlds/world-2/world.md), [Floe Breaker (2-1 mini)](../mini/2-1-floe-breaker.md)

The Narwhal is the final boss of 2-1, met at the level's end. It is a 5 L cyber-narwhal: a long
whale of cold teal flesh with a spiral horn of bone, fins and flukes, teal neon along its back,
and the fight is a chase (the ground scrolls faster). It was designed as a flying submarine over the
ice floes of the Frozen North; World 2 became the Industrial Desert (D-110) and the boss kept its
name and its frost, so it now chases over the desert. Everything all bosses share is in
[common.md](../common.md); this file gives only what is its own.

## Requirements

### Look

#### FB-NARWHAL-01 — Silhouette and size · MUST

The Narwhal is `size` long, from its tail to the tip of its horn. Seen from above it is a long,
round body, widest just behind its dorsal hump, closing to its head at the front; a long spiral
horn points straight down the screen from the head; a cruciform tail with flukes and a propeller
shroud ends it at the back. Its torpedo tubes swell from its flanks ahead of the middle and its two
ballast pods hang out either side behind it on short pylons.

**Acceptance criteria**
- Given the bosses viewer, when it shows the Narwhal, then it reads as a long whale with a horn ahead of it and a pod either side.

*Sources: P08-R10, P16-R06.*

#### FB-NARWHAL-02 — A living cyber-narwhal · MUST

Its body is Cyber-Organic flesh with metal grafts (see [art direction](../../graphics/art-direction.md)),
drawn by code:
- a whale's body of cold teal flesh, ribbed with bone at the front and back, metal bands grafted
  round it;
- a dorsal hump of graphite flesh where the sail was, its planes now membrane fins, feelers of
  sinew of two heights on top;
- tail flukes of teal flesh where the stern planes were, a rudder of sinew, the propeller shroud
  and its reactor;
- gill slits down both flanks, a blowhole with a grafted metal valve, ring seams round the hull.

The dressing is not a mirror image (whip antennas off-centre, a capstan, an escape hatch, a railing
on the forward deck).

*Sources: P08-R10, P16-R06.*

#### FB-NARWHAL-03 — Its parts and guns on the body · MUST

- The horn lance: a spiral horn of bone with darker bands, a metal collar grafted where it leaves
  the head, a teal light winding round it (a bead on each turn), its tip glowing as its laser
  charges.
- Each torpedo tube: a swollen blister of flesh on the flank, two metal tube mouths at its front
  whose torpedoes glow as a salvo charges, a teal line along its outer side.
- Each ballast pod: a ballast sac of flesh on a pylon of sinew, held in metal bands, a teal ring
  round its middle, a gland on its back, frost on top, two fan guns at its front.
- The core's guns: a twin-barrelled deck gun turning on the forward deck, and the spiral emitter on
  top of the hump (a teal ring, a white charge light).

*Sources: P08-R10, P16-R06.*

#### FB-NARWHAL-04 — Lights and colours · MUST

Its neon is teal (`neon`). It lights: two lines along its back, edge strips on the hump and the
flukes, a line under its chin, keel lamps, the sail's front windows, a sonar window on its belly,
the horn's winding light, the tubes' and pods' lines and rings. Navigation lamps on the hump:
red to port (the screen's left), green to starboard.

*Sources: P08-R10, P16-R06.*

#### FB-NARWHAL-05 — Frost · MUST

It keeps the World 2 frost although World 2 is now a desert: patches of snow along its back between
the neon lines, a snow cap on the hump's flat top, a frozen crust on the forward deck, ice chunks,
crystals on its fins and flukes, rime on the pods.

*Sources: P08-R10, D-110.*

#### FB-NARWHAL-06 — What its transformations shed · MUST

Its plating is armour drawn as pieces of its own over the body ([common](../common.md), BOSS-42):
under both regions the core's hull is only the body's lower half, flat on top at 5.3 px, and each
region's armour is the cap over it, the hull's upper half from 5 px up (the snow patches and the
two neon lines on it), with what stands on the back there.

- First transformation: the plating of its back behind the hump (region `back`: from 8 px behind
  its centre to 41 px behind it, the hull's own plan, 35 px across at the widest) bursts off, baring
  a dark metal lattice (`shell`) on the flat deck, and its two lances rise from it. The cap carries
  the bone ribs and the metal band round the body there, two deck plates, the gland, the rear spines
  of ice, the blowhole and its valve, the escape hatch and the aft whip antenna.
- Second transformation: the plating of its spine (region `spine`: from 40 px ahead of its centre to
  8 px behind it, the hull's plan, 36 px across at the widest) bursts off the same way, and its two
  missile racks rise from it. The cap carries the hump (the dorsal sail with its fins, feelers,
  emitter, antenna, lamps and windows), the bone ribs and the metal band ahead of the hump, and the
  frozen crust of the forward deck.

The tail and the nose stay whole, the deck gun stands on a pedestal of the core, so the boss stays
one object (BOSS-52).

**Acceptance criteria**
- Given its design, then its first transformation sheds the back region and both lances lie in it,
  its second the spine region and both racks lie in it (unit test).
- Given its model, then it draws both regions' armour, and it holds together at rest and after each
  transformation (unit tests).

*Sources: D-221, D-224, D-227, D-229, D-254.*

### Behaviour

#### FB-NARWHAL-07 — Entry and movement: a chase · MUST

It comes in as every boss and stops with its centre at `stop_fraction` of the playfield's height. In
place it sways by up to `sway` and bobs by `bob`. The fight is a chase: the ground scrolls at
`ground_speed` of 2-1's speed, faster than the level.

*Sources: P08-R10.*

#### FB-NARWHAL-08 — Horn lance · MUST

Part `lance`, on the nose 70 px ahead of the centre, `lance_radius` round with `lance_hp`. It does
not shield the core. Every 6.5 s (first 2.5 s into a stage) it fires a laser straight down the
screen from the horn's tip, after the laser's warning line, firing for 1.4 s. Its laser is drawn in
the boss's teal.

*Sources: P08-R10, D-072.*

#### FB-NARWHAL-09 — Torpedo tubes · MUST

Parts `tube-left` and `tube-right`, at ±22 px across and 32 px ahead of the centre, `tube_radius`
round with `tube_hp` each. They do not shield the core. Each fires 2 homing missiles, 30° apart,
every 5.5 s, the two out of step (first at 3.5 s and 6.25 s).

*Sources: P08-R10.*

#### FB-NARWHAL-10 — Ballast pods · MUST

Parts `pod-left` and `pod-right`, at ±40 px across and 18 px behind the centre, `pod_radius` round
with `pod_hp` each. They shield the core. Each fires a fan of 3 green bullets, 15° apart, every
2.2 s (first at 0.8 s and 1.9 s), leaning 12° towards the other side, so the two fans cross under
the boss.

**Discrepancy:** the code leans each pod's fan 12° outwards, away from the other pod (`pod-left`
at heading −12°, `pod-right` at +12°, a positive heading being towards the screen's right), so the
two fans spread apart instead of crossing.

*Sources: P08-R10.*

#### FB-NARWHAL-11 — Core and stage patterns · MUST

Its core (`core_radius`, `core_hp`) fires from its deck gun (on a turret 32 px ahead of the centre,
turning to aim) and, for rings, from the hump's emitter. One pattern per stage:
- stage 0: 1 magenta bullet at the player every 3 s;
- stage 1: an aimed spread of 3 magenta, 12° apart, every 2.6 s;
- stage 2: aimed bursts of 4 magenta, 0.14 s apart, every 2.4 s;
- stage 3: a fan of 5 magenta, 14° apart, every 2.4 s;
- stage 4: a fan of 7 magenta, 12° apart, every 2.2 s, and 1 purple at the player every 2.6 s;
- stage 5 (the last): two spirals turning opposite ways, rings of 10 every 1.2 s, blue turning 13°
  and purple turning −17° a volley.

The last stage's spirals are fired by no earlier stage.

*Sources: P08-R10, D-068.*

#### FB-NARWHAL-12 — Rage · MUST

It is angry as every boss with a `vortex` at heat `rage_heat` (one fast magenta spiral, blue bursts
at the player).

*Sources: D-068.*

#### FB-NARWHAL-13 — First transformation: laser lances · MUST

It transforms a first time when 2 of its 5 original parts are destroyed. The transformation sheds its
back (FB-NARWHAL-06) and reveals a pair of laser lances, `lance-left` and `lance-right`, at ±12 px
across and 11 px behind the centre, `t1_radius` round with `t1_hp` each (0.8 of its horn lance's).
They shield the core and fire the lance's laser ([common.md](../common.md)), in the boss's teal,
first 1.2 s and 2.0 s into each stage.

*Sources: D-221, D-224, D-229, D-072.*

#### FB-NARWHAL-14 — Second transformation: missile racks · MUST

It transforms a second time when 4 of its 5 original parts are destroyed. The transformation sheds
its spine (FB-NARWHAL-06) and reveals a pair of missile racks, `rack-left` and `rack-right`, at
±9 px across and 13 px ahead of the centre, `t2_radius` round with `t2_hp` each (as much as its horn
lance). They shield the core and fire the rack's homing missiles ([common.md](../common.md)).

*Sources: D-221, D-224, D-229.*

#### FB-NARWHAL-15 — Health, points and death · MUST

Its full health is `full_hp` (core and original parts), `full_hp_with_weapons` with its hidden
weapons. It is worth `points`. Its core always drops a bonus; its parts drop one as final boss parts
do, its hidden weapons as hidden weapons do. It dies as every boss, and its death completes 2-1.

**Acceptance criteria**
- Given `?level=2-1&boss=final`, when K destroys the Narwhal part by part, then it transforms twice, dies, and the "Level complete" overlay shows 2-1 (e2e).

*Sources: P08-R10, P08-R11, D-068, D-221.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| size | 5 L (170 px) | `src/game/config/bosses/world_2/narwhal.py` `_NARWHAL["stats"]` |
| neon | teal (0.05, 0.95, 0.75) | `src/game/config/boss_look.py` `BOSS_LOOK.neon["narwhal"]` |
| stop_fraction | 0.74 | `stopFraction` |
| sway | 45 px, 8 s | `sway` |
| bob | 10 px, 4 s | `bob` |
| ground_speed | ×1.5 | `groundSpeed` (a chase) |
| core_radius / core_hp | 22 px / 2 300 | `coreRadius`, `coreHealth`; core drop 1 |
| lance_radius / lance_hp | 13 px / 1 100 | `fpart("lance" …)`; laser every 6.5 s, 1.4 s, 12 px wide |
| tube_radius / tube_hp | 10 px / 650 | `fpart("tube-…")` |
| pod_radius / pod_hp | 14 px / 900 | `fpart("pod-…")` |
| pod fan heading | −12° left pod, +12° right pod (see the discrepancy under FB-NARWHAL-10) | `volley.fan("pod-…", 2.2, 3, 15, GREEN, …, ∓12)` |
| bullets | magenta 185, green 180, blue 190, purple 195 px/s | `MAGENTA`, `GREEN`, `BLUE`, `PURPLE`; times the level's factors |
| rage_heat | 3 (`vortex`, magenta / blue) | `rage` |
| transformations | after 2 and 4 of 5 parts | `boss_build.default_transforms` |
| t1_radius / t1_hp | 10 px / 880 | `hidden_weapon("lance-…")`, pod 21.1 px high |
| t2_radius / t2_hp | 7 px / 1 100 | `hidden_weapon("rack-…")`, pod 26.1 px high |
| region `back` | the hull's plan from y 8 to 41 (x ±17.3 at y 8, ±13.7 at y 41), `shell`; cap 5–17 px | `armour_region("back", 1, …)`; `narwhal_armour.back_armour` |
| region `spine` | the hull's plan from y −40 to 8 (x ±18 at y −10, ±14 at y −40), `shell`; cap 5–17.5 px, the hump to 27 | `armour_region("spine", 2, …)`; `narwhal_armour.spine_armour` |
| full_hp / full_hp_with_weapons | 6 500 / 10 460 | core + parts |
| points | 16 000 (1 600 a part) | `points` |

## Notes

- The module docstrings still say "the Ice floes level" and call the health "placeholders"; both
  predate D-110 and D-068's tuning.
