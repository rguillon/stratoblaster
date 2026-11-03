# Aurora Station — 2-3 final boss

> **Area:** bosses · **Prefix:** `FB-AURORA-STATION` · **Related:** [common.md](../common.md), [2-3 Oil fields](../../worlds/world-2/2-3-oil-fields.md), [World 2](../../worlds/world-2/world.md), [Snow Owl (2-3 mini)](../mini/2-3-snow-owl.md), [Hornet](../../enemies/hornet.md)

The Aurora Station is the final boss of 2-3, met at the level's end. It is a 5 L living ice
jellyfish: a bell of cold flesh under a frilled crown that turns slowly on top, a spine of bone out
to two cryo bladders, two dish emitters that aim lasers, and a brood pouch at its nose that launches
Hornets, in green and violet neon. It was designed as a flying research station of the Frozen North;
World 2 became the Industrial Desert (D-110) and the boss kept its name and its frost. Everything all
bosses share is in [common.md](../common.md).

## Requirements

### Look

#### FB-AURORA-STATION-01 — Silhouette and size · MUST

The Aurora Station spans `size`. Seen from above it is round in the middle (the bell, its crown on
top), a spine reaching out either side to a cryo cannon at each end, two dish emitters on arms ahead
of the bell, the hangar at its nose, and behind the bell two egg sacs and two broad frilled fins.

**Acceptance criteria**
- Given the bosses viewer, when it shows the Aurora Station, then it reads as a round bell with a turning crown, arms out to its guns and fins behind.

*Sources: P08-R10, P16-R06.*

#### FB-AURORA-STATION-02 — A living ice jellyfish · MUST

Its body is Cyber-Organic flesh with metal grafts (see [art direction](../../graphics/art-direction.md)),
drawn by code:
- the bell (the old hub): a wide octagonal drum of graphite flesh, rimed on top, a metal collar
  grafted round its crown, six green veins running out from the collar;
- a spine of bone across to the cryo bladders, with knots of bone along it and a metal ring near
  each end, and arms of sinew out to the dish emitters;
- two egg sacs of membrane behind the bell (the old habitat modules), iced on top, lit by rows of
  violet lamps, a reactor sac behind each, a tendril of sinew between them;
- two frilled fins of membrane on bone rays behind the spine (the old radiator wings), a green
  edge light on each.

*Sources: P08-R10, P16-R06.*

#### FB-AURORA-STATION-03 — Its parts and guns on the body · MUST

- Each dish emitter: a swollen node of flesh at the end of its arm with a metal socket (its pylon),
  and on it the turret, an upright dish facing down the screen, struts holding its projector at the
  focus, where the laser leaves from.
- Each cryo cannon: a cryo bladder of flesh, rimed over, two glands of coolant behind its turret, a
  single wide-bored barrel with a violet ring round its foot.
- The drone hangar: a brood pouch of flesh at the nose, roofed with snow, its mouth framed in
  violet, where its Hornets leave from.
- The crown on top (the old dish): a frilled bowl of membrane on a stalk, its rim violet, a feed
  horn lit green at its focus, snow caught on its rim, icicles under it.
- The core's guns: two hub guns either side of the hangar's spine, and the emitter collar under the
  crown's stalk, where its spirals leave from.

*Sources: P08-R10, P16-R06.*

#### FB-AURORA-STATION-04 — Lights and colours · MUST

Its neon is green (`neon`), with violet as its second colour. Green: the ring round the bell, the
veins, the spine's line on one side, the fins' edges, the crown's feed horn, the reactor sacs.
Violet: the collar's ring, the spine's line on the other side, the egg sacs' lamps, the hangar's
frame, the crown's rim, the cryo barrels' rings.

*Sources: P08-R10, P16-R06.*

#### FB-AURORA-STATION-05 — Frost · MUST

It keeps the World 2 frost although World 2 is now a desert: rime on the bell and the cryo bladders,
iced egg sacs, snow on the hangar's roof and in the crown, icicles under the fins and the crown,
ice crystals on the bell.

*Sources: P08-R10, D-110.*

#### FB-AURORA-STATION-06 — Moving pieces · MUST

The crown turns slowly on top at `crown_spin` (it is drawn on the model's ring; no part orbits). The
emitters' dishes and the cryo cannons' barrels turn on their turrets as they aim
(FB-AURORA-STATION-09, -10).

*Sources: P08-R10, D-073.*

#### FB-AURORA-STATION-07 — What its transformations shed · MUST

Its plating is armour drawn as pieces of its own ([common](../common.md), BOSS-42):

- First transformation: both fins (region `flanks`: each fin's own plan, from 20 to 84 px out
  either side, from 24 px to 48 px behind the centre) burst off, baring dark metal ribs and spars
  (`wing`) in their shape, and its two lances rise from them. Each piece is the frilled fin of
  membrane (from −0.6 to 1 px) on its bone rays with its green edge light; the fins' icicles hang
  from the core, under the frame once the fin is gone, and the metal bracket at each root stays.
- Second transformation: the bell's cap (region `bell`: the bell's octagon, 25 px round, its flat
  faces to the front) bursts off, baring a dark metal lattice (`shell`) over the bell's drum, and
  its two missile racks rise from it at the bell's front. The piece is the top of the drum from 3 px
  up to 7 px, rimed, the six green veins from the collar's foot to its rim and the crystals on it;
  the drum, the collar (standing from the drum through the cap), the crown's stalk and the hub guns
  stay with the core.

**Acceptance criteria**
- Given its design, then its first transformation sheds the flanks and both lances lie in them, its
  second the bell and both racks lie in it (unit test).
- Given its model, then it draws both regions' armour, and it holds together at rest and after each
  transformation (unit tests).

*Sources: D-221, D-224, D-227, D-229, D-254.*

### Behaviour

#### FB-AURORA-STATION-08 — Entry and movement · MUST

It comes in as every boss and stops with its centre at `stop_fraction` of the playfield's height. In
place it sways by up to `sway` and bobs by `bob`. During the fight the ground scrolls at
`ground_speed` of 2-3's speed.

*Sources: P08-R10.*

#### FB-AURORA-STATION-09 — Dish emitters: lasers on turrets · MUST

Parts `emitter-left` and `emitter-right`, at ±36 px across and 40 px ahead of the centre,
`emitter_radius` round with `emitter_hp` each. Both shield the core. Each fires a laser every 6.5 s
(first at 2 s and 5.25 s: one after the other), firing 1.8 s. The laser is on the dish's turret:
the dish aims at the player before the laser fires, follows the player only slowly during the warning
line, then holds still while the beam fires (no laser turns while it fires). Its laser is drawn in
the boss's green.

*Sources: P08-R10, D-072, D-073.*

#### FB-AURORA-STATION-10 — Cryo cannons · MUST

Parts `cryo-left` and `cryo-right`, at ±66 px across and 4 px behind the centre, `cryo_radius`
round with `cryo_hp` each. Both shield the core. Each turns on its turret and fires one cryo shell at
the player every 3.6 s (first at 1.4 s and 3.2 s): a slow, big violet shell that bursts, `cryo_burst`
after it is fired, into a ring of 8 small blue bullets.

*Sources: P08-R10, D-068.*

#### FB-AURORA-STATION-11 — Drone hangar · MUST

Part `hangar`, at the nose 56 px ahead of the centre, `hangar_radius` round with `hangar_hp`. It
does not shield the core. While it stands it launches 2 Hornets every 6.5 s (the first 3.5 s into a
stage).

*Sources: P08-R10.*

#### FB-AURORA-STATION-12 — Core and stage patterns · MUST

Its core (`core_radius`, `core_hp`) fires from its hub guns and, for spirals, from the collar under
the crown. One pattern per stage:
- stage 0: 1 red at the player every 3 s;
- stage 1: an aimed spread of 3 red, 12° apart, every 2.6 s;
- stage 2: aimed bursts of 4 red, 0.14 s apart, every 2.4 s;
- stage 3: a fan of 5 magenta, 14° apart, every 2.4 s;
- stage 4: a fan of 7 magenta, 12° apart, every 2.2 s, and 1 red at the player every 2.6 s;
- stage 5 (the last): two spirals turning opposite ways, rings of 5 every 0.5 s, green turning 14°
  and purple turning −19° a volley.

The last stage's spirals are fired by no earlier stage.

*Sources: P08-R10, D-068.*

#### FB-AURORA-STATION-13 — Rage · MUST

It is angry as every boss with `spirals` at heat `rage_heat` (two crossing spirals, green and
purple).

*Sources: D-068.*

#### FB-AURORA-STATION-14 — First transformation: laser lances · MUST

It transforms a first time when 2 of its 5 original parts are destroyed. The transformation sheds
its rear flanks (FB-AURORA-STATION-07) and reveals a pair of laser lances, `lance-left` and
`lance-right`, at ±47 px across and 35 px behind the centre, `t1_radius` round with `t1_hp` each
(0.8 of a dish emitter's). They shield the core and fire the lance's laser
([common.md](../common.md)), in the boss's green, first 1.2 s and 2.0 s into each stage.

*Sources: D-221, D-224, D-229, D-072.*

#### FB-AURORA-STATION-15 — Second transformation: missile racks · MUST

It transforms a second time when 4 of its 5 original parts are destroyed. The transformation sheds
its bell's cap (FB-AURORA-STATION-07) and reveals a pair of missile racks, `rack-left` and
`rack-right`, at ±7 px across and 21 px ahead of the centre, `t2_radius` round with `t2_hp` each (as
much as a dish emitter). They shield the core and fire the rack's homing missiles
([common.md](../common.md)).

*Sources: D-221, D-224, D-229.*

#### FB-AURORA-STATION-16 — Health, points and death · MUST

Its full health is `full_hp` (core and original parts), `full_hp_with_weapons` with its hidden
weapons. It is worth `points`. Its core always drops a bonus; its parts drop one as final boss parts
do, its hidden weapons as hidden weapons do. It dies as every boss, and its death completes 2-3.

*Sources: P08-R10, P08-R11, D-068, D-221.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| size | 5 L (170 px) | `src/game/config/bosses/world_2/aurora_station.py` `_AURORA_STATION["stats"]` |
| neon | green (0.3, 1, 0.55), violet second | `src/game/config/boss_look.py` `BOSS_LOOK.neon["aurora-station"]`; violet in `src/game/view/bosses/world_2/aurora_station_parts.py` |
| stop_fraction | 0.74 | `stopFraction` |
| sway | 35 px, 10 s | `sway` |
| bob | 6 px, 5 s | `bob` |
| ground_speed | ×0.4 | `groundSpeed` |
| crown_spin | 0.35 rad/s | `spinRate` |
| core_radius / core_hp | 22 px / 3 000 | `coreRadius`, `coreHealth`; core drop 1 |
| emitter_radius / emitter_hp | 13 px / 1 250 | `fpart("emitter-…")`; laser every 6.5 s, 1.8 s, 12 px wide |
| cryo_radius / cryo_hp | 15 px / 1 150 | `fpart("cryo-…")` |
| cryo shell | violet 95 px/s, radius 8; bursts after `cryo_burst` 1.3 s into 8 blue at 150 px/s | `CRYO_SHELL` |
| hangar_radius / hangar_hp | 14 px / 800 | `fpart("hangar" …)` |
| launches | 2 Hornets every 6.5 s, first at 3.5 s | `launches` |
| bullets | red 190, magenta 185, green 180, purple 175 px/s | `RED`, `MAGENTA`, `GREEN`, `PURPLE`; times the level's factors |
| rage_heat | 5 (`spirals`, green / purple) | `rage` |
| transformations | after 2 and 4 of 5 parts | `boss_build.default_transforms` |
| t1_radius / t1_hp | 11 px / 1 000 | `hidden_weapon("lance-…")`, pod 6 px high |
| t2_radius / t2_hp | 5 px / 1 250 | `hidden_weapon("rack-…")`, pod 9.6 px high |
| region `flanks` | each fin's plan: (20, 24), (76, 26), (84, 32), (84, 46), (20, 48) (mirrored), `wing`; fin −0.6–1 px | `armour_region("flanks", 1, …)`; `aurora_station_armour.flank_armour` |
| region `bell` | the bell's octagon, 25 px round, flats to the front, `shell`; cap 3–7 px | `armour_region("bell", 2, …)`; `aurora_station_armour.bell_armour` |
| full_hp / full_hp_with_weapons | 8 600 / 13 100 | core + parts |
| points | 13 000 (1 300 a part) | `points` |

## Notes

- P08-R10 gave the dish emitters "laser sweeps". At the reviewer's request no laser turns while it
  fires: the emitters aim their lasers from turrets instead (D-073).
- The module docstring still says "the Tundra level" and calls the health "placeholders".
