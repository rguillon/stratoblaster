# Harbour Kraken — 2-2 final boss

> **Area:** bosses · **Prefix:** `FB-HARBOUR-KRAKEN` · **Related:** [common.md](../common.md), [2-2 Mining mesas](../../worlds/world-2/2-2-mining-mesas.md), [World 2](../../worlds/world-2/world.md), [Fjord Lynx (2-2 mini)](../mini/2-2-fjord-lynx.md), [Hornet](../../enemies/hornet.md)

The Harbour Kraken is the final boss of 2-2, met at the level's end; the ground stops for its fight.
It is a 5 L living kraken: a shelled mantle of cold flesh with a head and beak amidships, four
tentacles swinging at the shoulder and the elbow, each ending in a clawed gun-fist, and a brood sac
at its stern that launches Hornets, in orange neon. It was designed as a cargo crane-ship fighting
over a harbour of the Frozen North; World 2 became the Industrial Desert (D-110), 2-2 has no harbour
any more, and the boss kept its name and its frost. Everything all bosses share is in
[common.md](../common.md).

## Requirements

### Look

#### FB-HARBOUR-KRAKEN-01 — Silhouette and size · MUST

The Harbour Kraken is `size` long. Seen from above it is a long, ship-like mantle with a raised
forecastle at the bow and a head amidships; four tentacles reach out from it, two either side, the
fore pair angled forward and the aft pair back, their gun-fists hanging well out past its flanks;
the brood sac sits on its stern.

**Acceptance criteria**
- Given the bosses viewer, when it shows the Harbour Kraken, then it reads as one long body with four arms swinging out from it.

*Sources: P08-R10, P16-R06.*

#### FB-HARBOUR-KRAKEN-02 — A living kraken · MUST

Its body is Cyber-Organic flesh with metal grafts (see [art direction](../../graphics/art-direction.md)),
drawn by code:
- the mantle of slate flesh under a ridged shell of graphite plates, a fringe of flesh along each
  flank;
- a forecastle of sinew, rimed on top, a metal plate grafted on it;
- the head amidships, its great eyes across its brow (two orange organs and a charge bar lit as it
  fires), a spiracle of sinew with an orange ring and a sooty mouth (the old funnel), a mast;
- the beak at the bow, of bone, a dark metal laser emitter grafted in it, a twin gun on a metal
  mount either side;
- frosted hatch covers along the deck between the tentacles;
- three reactor sacs and two fins of sinew at the stern.

*Sources: P08-R10, P16-R06.*

#### FB-HARBOUR-KRAKEN-03 — Its parts on the body · MUST

- Each tentacle rises from a root on the deck (a swollen ring of muscle with a metal collar, an
  orange ring, a cog), its thick upper length banded with metal (the boom, on the shoulder), then a
  lighter length out to its tip (the jib, on the elbow).
- Each crane's grab cannon hangs from the tentacle's tip: a clubbed fist, four bone hooks round a
  grafted cannon that fires at the player.
- The container bay at the stern: a brood sac of membrane full of eggs, each lit by a gland, its
  mouth held open by metal, an orange-lit gantry over it, armour plates grafted on its shell; its
  Hornets leave through the mouth.

*Sources: P08-R10, P16-R06.*

#### FB-HARBOUR-KRAKEN-04 — Lights and colours · MUST

Its neon is orange (`neon`): edge strips along the mantle's rim, glowing veins from the head to the
stern, the eyes, the funnel's and the emitter's rings, the tentacles' lines and roots, the gantry,
the reactor sacs. Navigation lamps on the head: red to port (the screen's left), green to starboard.

*Sources: P08-R10, P16-R06.*

#### FB-HARBOUR-KRAKEN-05 — Frost · MUST

It keeps the World 2 frost although World 2 is now a desert: a snow cap on the forecastle and the
head, frosted hatch covers, rimed tentacles and hooks, ice crystals on the shell, rows of icicles
under its flanks, its bow and its tentacles.

*Sources: P08-R10, D-110.*

#### FB-HARBOUR-KRAKEN-06 — Swinging tentacles · MUST

Its four tentacles are moving limbs on two joints each (the limb rules of
[common.md](../common.md)): each swings at its shoulder (`shoulder_swing`) and bends at its elbow
(`elbow_swing`), its grab cannon riding the elbow. The four are out of step (`swing_phases`), so no
two arms move together, and each right arm mirrors its left one. The grab cannons' hit circles and
muzzles move with them.

**Acceptance criteria**
- Given the bosses viewer with motion on, then the four arms swing, never all the same way at once.

*Sources: P08-R10, D-061.*

#### FB-HARBOUR-KRAKEN-07 — What its transformations shed · MUST

Its ridged shell is armour drawn as pieces of its own over the mantle ([common](../common.md),
BOSS-42), lofted in three sections: the stub under the head (14 px behind the centre to 17 px
ahead) stays with the core; the two others are its regions.

- First transformation: the fore plating (region `back`: the shell ahead of the head and the
  forecastle, from 17 px to 72 px ahead of its centre, their plan bulged to 46 px across at the
  gatlings) bursts off, baring a dark metal lattice (`shell`) on the mantle, and its two gatlings
  rise from it either side of the head. The piece carries the shell's plates from the head's front
  to its nose (3.8 to 9 px), the forecastle of sinew (3.8 to 8 px) with its metal plate and snow
  cap, the bow hatch cover with its gland, and the first length of the veins.
- Second transformation: the aft plating (region `wings`: the shell behind the head, from 14 px to
  62 px behind its centre, the shell's plan either side of the centre line, bulged to 59 px across at
  the batteries and clear of the aft tentacles' roots) bursts off, baring dark metal ribs and spars
  (`wing`), and its two gun batteries rise from its flanks. The piece carries the shell's plates
  from the head's rear to its tail (3.8 to 11 px), the aft hatch cover, the crystals on the shell
  and the veins' last length.

The mantle stays under both, the tentacles' roots and the head stand on it, and the bow guns'
mounts reach down to it: the boss stays one object (BOSS-52).

**Acceptance criteria**
- Given its design, then its first transformation sheds the back region and both gatlings lie in
  it, its second the wings region and both batteries lie in it (unit test).
- Given its model, then it draws both regions' armour, and it holds together at rest and after each
  transformation (unit tests).

*Sources: D-221, D-224, D-227, D-229, D-254.*

### Behaviour

#### FB-HARBOUR-KRAKEN-08 — Entry and movement: the ground stops · MUST

It comes in as every boss and stops with its centre at `stop_fraction` of the playfield's height. In
place it sways by up to `sway` and bobs by `bob`. During its fight the ground stops
(`ground_speed` ×0): the fight is over 2-2's end, where the level meets 2-3.

*Sources: P08-R10, D-068.*

#### FB-HARBOUR-KRAKEN-09 — Grab cannons · MUST

Four parts, `crane-fore-left`, `crane-fore-right`, `crane-aft-left` and `crane-aft-right`, at
the tentacles' tips (at rest ±70 px across and 44 px ahead of the centre, ±72 px across and 34 px
behind it), `grab_radius` round with `grab_hp` each. All four shield the core. Each fires aimed
bursts of 3 red bullets, 0.16 s apart, every 3 s, one after the other round the boss (first at 1,
1.75, 2.5 and 3.25 s into a stage).

*Sources: P08-R10.*

#### FB-HARBOUR-KRAKEN-10 — Container bay · MUST

Part `container-bay`, on the stern 46 px behind the centre, `bay_radius` round with `bay_hp`. It
does not shield the core. While it stands it launches a group of 3 Hornets every 7 s (the first 3 s
into a stage).

*Sources: P08-R10.*

#### FB-HARBOUR-KRAKEN-11 — Core and stage patterns · MUST

Its core (`core_radius`, `core_hp`) fires a laser in every stage, straight down the screen from the
beak's emitter (it has no turret), drawn in the boss's orange, and bullets from the twin guns either
side of it. One pattern per stage:
- stage 0: the laser every 7 s, firing 1.5 s;
- stage 1: the laser every 6 s (1.5 s), and 1 magenta at the player every 2.6 s;
- stage 2: the laser every 5.5 s (1.5 s), and a fan of 5 magenta, 14° apart, every 2.6 s;
- stage 3: the laser every 5.5 s (1.6 s), and an aimed spread of 3 magenta, 12° apart, every 2.4 s;
- stage 4: the laser every 5 s (1.6 s), and a fan of 7 magenta, 12° apart, every 2.2 s;
- stage 5 (the last): the laser every 4.5 s (1.6 s), and a ring of 14 orange every 1.4 s turning
  9° a volley (a spiral fired by no earlier stage).

*Sources: P08-R10, D-068, D-072, D-073.*

#### FB-HARBOUR-KRAKEN-12 — Rage · MUST

It is angry as every boss with a `vortex` at heat `rage_heat` (one fast orange spiral, magenta
bursts at the player).

*Sources: D-068.*

#### FB-HARBOUR-KRAKEN-13 — First transformation: gatlings · MUST

It transforms a first time when 2 of its 5 original parts are destroyed. The transformation sheds
its fore plating (FB-HARBOUR-KRAKEN-07) and reveals a pair of gatlings, `gatling-left` and
`gatling-right`, at ±13 px across and 35 px ahead of the centre, `t1_radius` round with `t1_hp` each
(0.8 of a grab cannon's), firing red bursts at the player ([common.md](../common.md)), first 1.2 s
and 2.0 s into each stage. They shield the core.

*Sources: D-221, D-224, D-229.*

#### FB-HARBOUR-KRAKEN-14 — Second transformation: gun batteries · MUST

It transforms a second time when 4 of its 5 original parts are destroyed. The transformation sheds
its aft flanks (FB-HARBOUR-KRAKEN-07) and reveals a pair of gun batteries, `battery-left` and
`battery-right`, at ±29 px across and 29 px behind the centre, `t2_radius` round with `t2_hp` each
(as much as a grab cannon), firing red fans straight down ([common.md](../common.md)). They shield
the core.

*Sources: D-221, D-224, D-229.*

#### FB-HARBOUR-KRAKEN-15 — Health, points and death · MUST

Its full health is `full_hp` (core and original parts), `full_hp_with_weapons` with its hidden
weapons. It is worth `points`. Its core always drops a bonus; its parts drop one as final boss parts
do, its hidden weapons as hidden weapons do. It dies as every boss, and its death completes 2-2.

*Sources: P08-R10, P08-R11, D-068, D-221.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| size | 5 L (170 px) | `src/game/config/bosses/world_2/harbour_kraken.py` `_HARBOUR_KRAKEN["stats"]` |
| neon | orange (1, 0.5, 0.08) | `src/game/config/boss_look.py` `BOSS_LOOK.neon["harbour-kraken"]` |
| stop_fraction | 0.75 | `stopFraction` |
| sway | 35 px, 10 s | `sway` |
| bob | 6 px, 5 s | `bob` |
| ground_speed | ×0 | `groundSpeed` |
| core_radius / core_hp | 22 px / 2 700 | `coreRadius`, `coreHealth`; core drop 1 |
| crane rest points | shoulder (±28, −26) / (±28, 15), elbow (±50, −34) / (±52, 27), grab (±70, −44) / (±72, 34) | `CRANE_REST` (fore / aft) |
| shoulder_swing | ±10° fore, ±9° aft, 5.2 s | `SWING`, `crane_joints` |
| elbow_swing | ±18° fore, ±16° aft, 3.7 s | `SWING`, `crane_joints` |
| swing_phases | 0, 0.31, 0.58, 0.83 of a period (elbows +0.2) | `SWING` |
| grab_radius / grab_hp | 13 px / 900 | `grab(crane, 900)` |
| bay_radius / bay_hp | 16 px / 700 | `fpart("container-bay" …)` |
| launches | 3 Hornets every 7 s, first at 3 s | `launches` |
| bullets | red 190, magenta 185, orange 175 px/s | `RED`, `MAGENTA`, `ORANGE`; times the level's factors |
| laser | 12 px wide, 1 s warning | `boss_kit.laser_of` |
| rage_heat | 4 (`vortex`, orange / magenta) | `rage` |
| transformations | after 2 and 4 of 5 parts | `boss_build.default_transforms` |
| t1_radius / t1_hp | 11 px / 720 | `hidden_weapon("gatling-…")`, pod 12.7 px high |
| t2_radius / t2_hp | 11 px / 900 | `hidden_weapon("battery-…")`, pod 16.9 px high |
| region `back` | the shell's and forecastle's plan from y −17 to −72 (x ±18 at y −17, ±23 at y −48, ±9 at y −68), `shell` | `armour_region("back", 1, …)`; `harbour_kraken_armour.back_armour` |
| region `wings` | the aft shell's plan from y 14 to 62 either side of the centre line (x 0…20 at y 14, 0…29.5 at y 24…36, 0…6 at y 62; mirrored), `wing` | `armour_region("wings", 2, …)`; `harbour_kraken_armour.wings_armour` |
| full_hp / full_hp_with_weapons | 7 000 / 10 240 | core + parts |
| points | 10 500 (1 050 a part) | `points` |

## Notes

- P08-R10 asked for the ground to stop "over the harbour". The fight was put at 2-2's inland end
  (2-2 has to end where 2-3 begins, D-068), and since the 2026-10-27 rework (D-110) 2-2 has no
  harbour at all. The ground still stops.
