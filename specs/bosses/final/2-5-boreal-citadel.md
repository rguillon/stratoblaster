# Boreal Citadel — 2-5 final boss

> **Area:** bosses · **Prefix:** `FB-BOREAL-CITADEL` · **Related:** [common.md](../common.md), [2-5 Factory district](../../worlds/world-2/2-5-factory-district.md), [World 2](../../worlds/world-2/world.md), [Ice Queen (2-5 mini)](../mini/2-5-ice-queen.md), [Hornet](../../enemies/hornet.md)

The Boreal Citadel is the final boss of 2-5 and World 2's last boss, the hardest so far. It is a
6 L colossal living beast carrying a city on its back: rimed flesh, a spine of bone down its middle,
spires of flesh and crystal for towers, its heart (the keep) banded in metal over the core, membrane
fins out to two aurora cannons, in aurora green and violet neon; its core fires every kind of
attack. It is one of the eight bosses that change shape as they transform: its bow doors swing open.
It was designed as the flying fortress of a polar city at night; World 2 became the Industrial
Desert (D-110), 2-5 is a factory district at night, and the boss kept its name and its frost.
Everything all bosses share is in [common.md](../common.md).

## Requirements

### Look

#### FB-BOREAL-CITADEL-01 — Silhouette and size · MUST

The Boreal Citadel is `size` across, the biggest boss of World 2. Seen from above it is a broad deck
pointed at the bow, an avenue down its middle carrying the keep over the centre, an engine block
across its tail, and a long outrigger fin either side reaching out to an aurora cannon.

**Acceptance criteria**
- Given the bosses viewer, when it shows the Boreal Citadel, then it reads as one huge creature carrying a city, a gun out on each side.

*Sources: P08-R10, P16-R06.*

#### FB-BOREAL-CITADEL-02 — A colossal beast · MUST

Its body is Cyber-Organic flesh with metal grafts (see [art direction](../../graphics/art-direction.md)),
drawn by code:
- the deck: the back of a colossal beast of teal flesh, rimed on top, bone ribs across it at the
  back, armour skirts lit by violet slits along its sides, snow drifts piled on it;
- the avenue down its middle: a raised ridge of bone (its spine), lamps along it;
- the outriggers: membrane fins, a bone sinew along each out to its cannon;
- the keep over the core: its heart, a stepped octagonal mound of graphite flesh, metal bands on its
  ledges, buttresses round it, a spire of crystal on top glowing at its tip;
- a gun deck of metal on the keep's front, missile hatches on the avenue behind it;
- arteries from the domes to the heart, a metal pipe grafted along each;
- the engine block across its tail, of dark metal, with grilles, heat-sink fins and four reactor
  sacs.

*Sources: P08-R10, P16-R06.*

#### FB-BOREAL-CITADEL-03 — The city on its back · MUST

The deck carries a city: towers grown as spires of flesh from its back (the tall ones of slate
flesh, the short ones of sinew), tapering, their pores lit like windows in green or violet, a
crystal grown out of each tip; two small heated domes glowing warm through the frost; masts and
dishes over the roofs. The
towers of its left half take the other window colour from its right half, so the city is not a
mirror image.

*Sources: P08-R10, P16-R06.*

#### FB-BOREAL-CITADEL-04 — Its parts and guns on the body · MUST

- Each aurora cannon: a turntable on its outrigger (a shoulder of muscle on the fin, ringed with
  violet), and on it the cannon itself: a swollen gun organ, frosted, with ribs along its flanks, a
  long metal barrel grafted in it with charge coils, a lens at its front where its laser leaves, and
  lit fins along its back like aurora curtains, green below and violet along their tops.
- Each missile battery, on the deck aft: an armoured growth, a mound of flesh under a snowed metal
  hatch plate, six hatches lit as its missiles load, violet strips down its sides, icicles under its
  front.
- Each dome generator, on the deck ahead: a glowing blister swelling from the flesh, aurora green
  through a ring of ice, held by bone spikes, three pylons with violet lights.
- The core's guns, on the keep: twin cannons on the gun deck, a laser lens between them, the ring
  emitter at the spire's tip, and four missile hatches behind the keep.

*Sources: P08-R10, P16-R06.*

#### FB-BOREAL-CITADEL-05 — Lights and colours · MUST

Its neon is aurora green (`neon`), with violet as its second colour. Green: the deck's lit rim, the
outriggers' edges, the veins, the keep's bottom and top rings, the domes, the cannons' curtains,
the reactor sacs. Violet: the avenue's edge lights, the skirts' slits, the keep's middle ring, the
gun deck's strip, the turntables' rings, the batteries' strips, the domes' pylons.

*Sources: P08-R10, P16-R06.*

#### FB-BOREAL-CITADEL-06 — Frost · MUST

It keeps the World 2 frost although World 2 is now a desert: rime on the deck, snow on the keep's
ledges and buttresses, the towers' roofs and the batteries, snow drifts on the deck, frosted cannon
pods, icicles under the deck's bow edges, the outriggers and the batteries.

*Sources: P08-R10, D-110.*

#### FB-BOREAL-CITADEL-07 — Moving pieces · MUST

Its aurora cannons turn on their turntables to aim their lasers (FB-BOREAL-CITADEL-10). Nothing else
moves but the shared living motion of [common.md](../common.md) and its transformations.

*Sources: P08-R10, D-073.*

#### FB-BOREAL-CITADEL-08 — Its transformations change its shape · MUST

Its deck is a slab of flesh up to 4 px, under panels of rimed flesh up to its top (6 px):
its armour is drawn as panels of their own (D-254), lying on the deck's slab, and the core is drawn
without them.

- First transformation: its bow doors (regions `bow-doors-right` and `bow-doors-left`: the deck's
  panels of the bow from 40 px ahead of the centre to its nose, within 32 px of the centre line, a
  door either side) stay on and swing open sideways by `door_swing` about hinges at their rear outer
  corners, eased, as the armour of other bosses would burst. Each door carries what stands on it:
  the front towers, a heated city dome, a roof mast and a snow drift. The dark metal floor of its
  hold (`shell`) shows where they were, just over the deck's slab, with the hangar and two mortars
  rising in it.
- Second transformation: its wing panels (region `wings`: the deck's panels from 32 px out either
  side to the deck's edge, from 40 px ahead of the centre to 26 px behind it), with what stands on
  them (the side towers, snow drifts, the dish, a mast, a skirt and the arteries from the domes to
  the outriggers), burst off in three slices each, baring dark metal ribs and spars (`wing`) over
  the deck's slab, and its two heavy cannons rise from it.

The boss stays one object (the opened doors keep their whole body together; they overlap the hull
where they swing over it).

**Acceptance criteria**
- Given the bosses viewer, when K breaks both domes, then the bow doors swing open and a hangar and two mortars rise in the hold.

*Sources: D-224, D-227, D-230, D-254.*

### Behaviour

#### FB-BOREAL-CITADEL-09 — Entry and movement · MUST

It comes in as every boss and stops with its centre at `stop_fraction` of the playfield's height. In
place it sways by up to `sway` and bobs by `bob`, the least of World 2. During the fight the ground
slows to `ground_speed` of 2-5's speed.

*Sources: P08-R10.*

#### FB-BOREAL-CITADEL-10 — Aurora cannons: lasers on turrets · MUST

Parts `cannon-left` and `cannon-right`, on the outriggers at ±80 px across and 8 px ahead of the
centre, `cannon_radius` round with `cannon_hp` each. They do not shield the core. Each fires a laser
every 6.5 s (first at 2 s and 5.25 s: one after the other), firing 1.6 s. The laser is on the
cannon's turntable: it aims at the player before the laser fires, follows only slowly during the
warning line, then holds still while the beam fires (no laser turns while it fires). Its laser is
drawn in the boss's aurora green.

*Sources: P08-R10, D-072, D-073.*

#### FB-BOREAL-CITADEL-11 — Missile batteries · MUST

Parts `battery-left` and `battery-right`, aft at ±48 px across and 34 px behind the centre,
`battery_radius` round with `battery_hp` each. They do not shield the core. Each fires 2 homing
missiles, 24° apart, from its six cells every 5.5 s (first at 3.5 s and 6.25 s).

*Sources: P08-R10.*

#### FB-BOREAL-CITADEL-12 — Dome generators · MUST

Parts `dome-left` and `dome-right`, ahead at ±36 px across and 40 px ahead of the centre,
`dome_radius` round with `dome_hp` each (its sturdiest parts). They have no weapon; they are the only
original parts that shield the core.

*Sources: P08-R10.*

#### FB-BOREAL-CITADEL-13 — Core: every kind of attack · MUST

Its core (`core_radius`, `core_hp`) fires bullets from the twin cannons, rings from the spire, a
laser straight down the screen from the lens (it has no turret; drawn in the boss's green) and
homing missiles from the hatches: every kind of attack. One pattern per stage, each a new one:
- stage 0: an aimed spread of 3 purple, 10° apart, every 2.6 s;
- stage 1: a fan of 5 green, 14° apart, every 2.4 s;
- stage 2: aimed bursts of 4 purple, 0.12 s apart, every 2.3 s;
- stage 3: 2 homing missiles, 30° apart, every 5 s, and 1 magenta at the player every 2.2 s;
- stage 4: the laser every 5.5 s, firing 1.4 s, and a fan of 7 green, 12° apart, every 2.4 s;
- stage 5: a ring of 10 green every 2 s, and aimed bursts of 3 magenta every 2.6 s;
- stage 6 (the last): all of them at once with a spiral of its own, fired by no earlier stage: a
  ring of 16 purple every 1.2 s turning 9° a volley, the laser every 5 s (1.4 s), 2 missiles every
  6 s and a fan of 5 green every 2.8 s.

*Sources: P08-R10, D-068, D-072, D-073.*

#### FB-BOREAL-CITADEL-14 — Rage · MUST

It is angry after each of its transformations, when the weapons that one revealed
fire all out: the hangar and two mortars after the first, the two heavy cannons after the second.
For `boss_rage_seconds` it fires only those, `boss_rage_rate` times as often, instead of its
stage's pattern ([common](../common.md), BOSS-27). A lost part no longer angers it, and it
has no angry pattern of its own.

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only the weapons it revealed
  (unit: `test_boss_build.py` angry_pattern).
- Given a part is destroyed without a transformation, then it is not angry (unit test).

*Sources: D-068, D-256.*

#### FB-BOREAL-CITADEL-15 — First transformation: the bow opens · MUST

It transforms a first time when both dome generators are destroyed (named parts, whatever else is
lost). The transformation opens its bow doors (FB-BOREAL-CITADEL-08) and reveals, `t1_hp` each (0.8
of a dome's), all shielding the core:
- `hangar`, on the centre line 68 px ahead of the centre (`hangar_radius`), its two doors sliding
  apart, launching 2 Hornets every 7 s (first 3 s into a stage) ([common.md](../common.md));
- `mortar-left` and `mortar-right`, at ±20 px across and 48 px ahead of the centre
  (`mortar_radius`), firing green flak shells that burst into rings, first 1.2 s and 2.8 s into each
  stage.

*Sources: D-221, D-229, D-230.*

#### FB-BOREAL-CITADEL-16 — Second transformation: heavy cannons · MUST

It transforms a second time when both missile batteries are destroyed, once its first transformation
has been called (if the batteries go first, both transformations follow one another once the domes
are gone). The transformation sheds its wing armour (FB-BOREAL-CITADEL-08) and reveals a pair of heavy
cannons, `heavy-left` and `heavy-right`, at ±47 px across and 7 px ahead of the centre, `t2_radius`
round with `t2_hp` each (as much as a dome), firing aimed spreads of big green shells
([common.md](../common.md)). They shield the core.

*Sources: D-221, D-224, D-229, D-230.*

#### FB-BOREAL-CITADEL-17 — Health, points and death · MUST

Its full health is `full_hp` (core and original parts), `full_hp_with_weapons` with its hidden
weapons, the most of World 2. It is worth `points`. Its core always drops a bonus; its parts drop one
as final boss parts do, its hidden weapons as hidden weapons do. It dies as every boss, and its death
completes 2-5 and World 2.

*Sources: P08-R10, P08-R11, D-068, D-221.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| size | 6 L (204 px) | `src/game/config/bosses/world_2/boreal_citadel.py` `_BOREAL_CITADEL["stats"]` |
| neon | aurora green (0.35, 1, 0.6), violet second | `src/game/config/boss_look.py` `BOSS_LOOK.neon["boreal-citadel"]`; violet in `src/game/view/bosses/world_2/boreal_citadel_city.py` |
| stop_fraction | 0.75 | `stopFraction` |
| sway | 25 px, 11 s | `sway` |
| bob | 6 px, 5 s | `bob` |
| ground_speed | ×0.25 | `groundSpeed` |
| core_radius / core_hp | 24 px / 6 000 | `coreRadius`, `coreHealth`; core drop 1 |
| cannon_radius / cannon_hp | 15 px / 1 900 | `BOREAL_PARTS.cannon`; laser every 6.5 s, 1.6 s, 12 px wide |
| battery_radius / battery_hp | 14 px / 1 700 | `BOREAL_PARTS.battery` |
| dome_radius / dome_hp | 13 px / 2 150 | `BOREAL_PARTS.dome` |
| bullets | green 185, purple 195, magenta 190 px/s | `GREEN`, `PURPLE`, `MAGENTA`; times the level's factors (2-5: 1.15) |
| angry | the revealed weapons, BOSS-27 | `boss_build.angry_pattern` |
| transformations | both domes; both batteries | `transformParts` |
| door_swing | 0° → 75° about the `up` axis, hinge (±32, −40, 10) | `moving_region("bow-doors", 1, …, swing(…))` |
| moving region `bow-doors` | the bow's panels: x 0…32 (mirrored), from y −40 to the deck's bow edge and nose (y −83.7 on the centre line), `shell` | `moving_region("bow-doors", 1, …)`; drawn in `src/game/view/bosses/world_2/boreal_citadel_armour.py` |
| shed region `wings` | the deck's side panels: x 32 (mirrored) out to the deck's edge (55.3…59.7), y −40…26, `wing` | `armour_region("wings", 2, …)`; drawn in `boreal_citadel_armour.py` |
| hangar_radius / mortar_radius | 13 px / 8 px | `hidden_weapon("hangar" …)`, pod 9 px high; `hidden_weapon("mortar-…")`, pods 11 px high |
| t1_hp | 1 720 | hangar and mortars |
| t2_radius / t2_hp | 12 px / 2 150 | `hidden_weapon("heavy-…", "cannon", …)`, pod 16.4 px high |
| full_hp / full_hp_with_weapons | 17 500 / 26 960 | core + parts |
| points | 18 000 (1 800 a part) | `points` |

## Notes

- Its aurora cannons used to sweep their lasers (D-068); the reviewer saw them turn while firing and
  asked that no boss laser turn once it fires: they went on turntables (D-073), and its core laser
  fires straight down.
- The design of D-230 first showed one mortar in its hold; it shows two (D-230 as built).
