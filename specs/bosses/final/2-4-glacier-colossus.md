# Glacier Colossus — 2-4 final boss

> **Area:** bosses · **Prefix:** `FB-GLACIER-COLOSSUS` · **Related:** [common.md](../common.md), [2-4 Industrial belt](../../worlds/world-2/2-4-industrial-belt.md), [World 2](../../worlds/world-2/world.md), [Avalanche (2-4 mini)](../mini/2-4-avalanche.md)

The Glacier Colossus is the final boss of 2-4, met at the level's end. It is a 5.5 L glacier titan:
a vast shelled body of cold flesh with glacier ice grown through it and gill-like heat vents glowing
down its back; two cutter lasers aim from its beam, two ore cannons and a heat sink guard its bow and
a missile pod its stern, in red-orange neon. Like the Boreal Citadel it has six parts, the most in
World 2. It was designed as a mining ship over a glacier of the Frozen
North; World 2 became the Industrial Desert (D-110) and the boss kept its name and its frost.
Everything all bosses share is in [common.md](../common.md).

## Requirements

### Look

#### FB-GLACIER-COLOSSUS-01 — Silhouette and size · MUST

The Glacier Colossus is `size` across. Seen from above it is a broad, blunt hull with a raised upper
deck along its middle and a brain hump towards its bow; a cutter stands out on a pylon at each end of
its beam, the ore cannons and the heat sink sit across its bow, the missile pod on its stern.

**Acceptance criteria**
- Given the bosses viewer, when it shows the Glacier Colossus, then it reads as one broad, heavy body with a gun out on each side.

*Sources: P08-R10, P16-R06.*

#### FB-GLACIER-COLOSSUS-02 — A living glacier titan · MUST

Its body is Cyber-Organic flesh with metal grafts (see [art direction](../../graphics/art-direction.md)),
drawn by code:
- a vast body of sinew, its top teal, under a ridged teal shell along the raised upper deck;
- a brain hump of graphite flesh where the bridge tower was, four eyes round it, the core's twin
  guns on its front;
- the heat stack behind the hump: a spiracle of slate flesh breathing heat, a metal ring grafted
  round its mouth, glowing at its top, two smaller sooted spiracles beside it;
- heat vents along each side of the deck: gill slits glowing between dark metal grilles, veins out
  from the shell to the rim;
- glacier ice grown through the flesh on the stern, crystals over the shell, a row of ice spines
  down its back, bone ribs on its flanks;
- metal grafts: a plate on the bow deck, a weathered patch, two masts; reactors at the stern.

*Sources: P08-R10, P16-R06.*

#### FB-GLACIER-COLOSSUS-03 — Its parts and guns on the body · MUST

- Each cutter: a pylon of sinew and metal out on the beam (it stays when the cutter is gone), a
  shoulder of muscle on it ringed with neon (the cutter's mount), and the cutter itself turning on
  it: a limb of flesh with an armour plate on its back, a red-orange stripe along its sides, its laser
  emitter at the front and a saw disc on its flank, frost on top.
- Each ore cannon: an armoured growth, a swollen organ under an octagonal metal casemate, two fat
  barrels, a red-orange ring round its foot, snow on its roof.
- The heat sink at the bow: a gill organ, its fleshy lamellae glowing red-orange between them; the
  ice round it has melted, frost only on its outer rims.
- The missile pod on the stern: a brood sac of flesh, four metal tubes grafted in it, the missiles
  growing inside lighting up as a salvo charges, vents and frost on its back.

*Sources: P08-R10, P16-R06.*

#### FB-GLACIER-COLOSSUS-04 — Lights and colours · MUST

Its neon is red-orange (`neon`): a band round the hull's rim, a band round the hump with its eyes,
the stack's ring and glow, the heat vents, the veins, lamps on its flanks, the cutters' stripes and
mounts, the ore cannons' rings, the heat sink's lamellae, the masts' lights, the reactors.

*Sources: P08-R10, P16-R06.*

#### FB-GLACIER-COLOSSUS-05 — Frost · MUST

It keeps the World 2 frost although World 2 is now a desert: snow caps on the decks and the hump,
icicles all round under the hull's rim, glacier ice and crystals on the stern, snow on the ore
cannons and the cutters; none round the warm heat sink.

*Sources: P08-R10, D-110.*

#### FB-GLACIER-COLOSSUS-06 — Moving pieces · MUST

Its cutters turn on their mounts to aim their lasers (FB-GLACIER-COLOSSUS-09). Nothing else moves but
the shared living motion of [common.md](../common.md) and its transformations.

*Sources: P08-R10, D-073.*

#### FB-GLACIER-COLOSSUS-07 — What its transformations shed · MUST

Its plating is armour drawn as pieces of its own ([common](../common.md), BOSS-42):

- First transformation: the plating of both stern flanks (region `flanks`: a plate on the stern
  deck either side of the upper deck, from the upper deck's edge out to the rim, from 34 px to 77 px
  behind the centre) bursts off, baring dark metal ribs and spars (`wing`) on the deck, and its two
  ring emitters rise from it. Each plate is a slab of teal flesh on the deck (9.7 to 12.2 px)
  carrying the aft heat vent, the glacier ice grown on the stern, a snow cap and the aft veins out
  to the rim.
- Second transformation: the shell (region `wings`: the shell's plan along the upper deck, from
  6 px ahead of the centre to 58 px behind it, 56 px across at the widest) bursts off, baring dark
  metal ribs and spars (`wing`) on the upper deck, and its two sweepers rise from under its flanks.
  The piece is the ridged teal shell (15.8 to 24 px) with the row of ice spines down its ridge and
  the crystals over it; the heat stack, the brain hump and the missile pod stand on the upper deck
  through it.

The decks stay under both, and the cutters' pylons reach under their mounts: the boss stays one
object (BOSS-52).

**Acceptance criteria**
- Given its design, then its first transformation sheds the flanks and both ring emitters lie in
  them, its second the wings and both sweepers lie in it (unit test).
- Given its model, then it draws both regions' armour, and it holds together at rest and after each
  transformation (unit tests).

*Sources: D-221, D-224, D-227, D-229, D-254.*

### Behaviour

#### FB-GLACIER-COLOSSUS-08 — Entry and movement · MUST

It comes in as every boss and stops with its centre at `stop_fraction` of the playfield's height. In
place it sways by up to `sway` and bobs by `bob`. During the fight the ground slows to
`ground_speed` of 2-4's speed.

*Sources: P08-R10.*

#### FB-GLACIER-COLOSSUS-09 — Cutter lasers on turrets · MUST

Parts `cutter-left` and `cutter-right`, out on the beam at ±80 px across and 10 px ahead of the
centre, `cutter_radius` round with `cutter_hp` each. They do not shield the core. Each fires a laser
every 6.5 s (first at 2 s and 5.25 s: one after the other), firing 1.4 s. The laser is on the
cutter's turret: it aims at the player before the laser fires, follows only slowly during the warning
line, then holds still while the beam fires. Its laser is drawn in the boss's red-orange.

*Sources: P08-R10, D-072, D-073.*

#### FB-GLACIER-COLOSSUS-10 — Ore cannons · MUST

Parts `ore-left` and `ore-right`, at ±44 px across and 28 px ahead of the centre, `ore_radius`
round with `ore_hp` each. Both shield the core. Each fires a fan of 3 big orange shells, 18° apart,
straight down, every 2.6 s (first at 0.9 s and 2.2 s).

*Sources: P08-R10.*

#### FB-GLACIER-COLOSSUS-11 — Heat sink · MUST

Part `heat-sink`, at the bow 48 px ahead of the centre, `sink_radius` round with `sink_hp` (its
sturdiest part). It has no weapon and shields the core.

*Sources: P08-R10.*

#### FB-GLACIER-COLOSSUS-12 — Missile pod · MUST

Part `missile-pod`, on the stern 46 px behind the centre, `pod_radius` round with `pod_hp`. It does
not shield the core. It fires 2 homing missiles, 30° apart, every 5.5 s (first at 3 s) from its four
tubes.

*Sources: P08-R10.*

#### FB-GLACIER-COLOSSUS-13 — Core and stage patterns · MUST

Its core (`core_radius`, `core_hp`) fires from twin guns on the hump's front and, for rings, from
the top of its heat stack. One pattern per stage:
- stage 0: 1 red at the player every 2.8 s;
- stage 1: an aimed spread of 3 red, 12° apart, every 2.4 s;
- stage 2: aimed bursts of 4 red, 0.13 s apart, every 2.4 s;
- stage 3: a ring of 8 magenta every 2.2 s;
- stage 4: a fan of 7 red, 12° apart, every 2.4 s, and aimed bursts of 3 red every 2.8 s;
- stage 5: a ring of 10 magenta every 1.8 s turning 7° a volley, and 1 red at the player every
  2.6 s;
- stage 6 (the last): two spirals turning opposite ways, rings of 14 every 1.3 s, magenta turning 9°
  and red turning −11° a volley.

The last stage's spirals are fired by no earlier stage.

*Sources: P08-R10, D-068.*

#### FB-GLACIER-COLOSSUS-14 — Rage · MUST

It is angry as every boss with a `flower` at heat `rage_heat` (a dense, slowly turning red ring,
small magenta fans at the player).

*Sources: D-068.*

#### FB-GLACIER-COLOSSUS-15 — First transformation: ring emitters · MUST

It transforms a first time when 2 of its 6 original parts are destroyed. The transformation sheds its
stern flanks (FB-GLACIER-COLOSSUS-07) and reveals a pair of ring emitters (orbs), `orb-left` and
`orb-right`, at ±36 px across and 53 px behind the centre, `t1_radius` round with `t1_hp` each (0.8 of
the heat sink's), firing orange rings ([common.md](../common.md)), first 1.2 s and 2.0 s into each
stage. They shield the core.

*Sources: D-221, D-224, D-229.*

#### FB-GLACIER-COLOSSUS-16 — Second transformation: sweepers · MUST

It transforms a second time when 4 of its 6 original parts are destroyed. The transformation sheds
its flanks amidships (FB-GLACIER-COLOSSUS-07) and reveals a pair of sweepers, `sweeper-left` and
`sweeper-right`, at ±25 px across and 29 px behind the centre, `t2_radius` round with `t2_hp` each (as
much as the heat sink), firing the sweeper's laser that follows the player while it fires
([common.md](../common.md)), in the boss's red-orange. They shield the core.

*Sources: D-221, D-224, D-229, D-072.*

#### FB-GLACIER-COLOSSUS-17 — Health, points and death · MUST

Its full health is `full_hp` (core and original parts), `full_hp_with_weapons` with its hidden
weapons. It is worth `points`. Its core always drops a bonus; its parts drop one as final boss parts
do, its hidden weapons as hidden weapons do. It dies as every boss, and its death completes 2-4.

*Sources: P08-R10, P08-R11, D-068, D-221.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| size | 5.5 L (187 px) | `src/game/config/bosses/world_2/glacier_colossus.py` `_GLACIER_COLOSSUS["stats"]` |
| neon | red-orange (1, 0.35, 0.08) | `src/game/config/boss_look.py` `BOSS_LOOK.neon["glacier-colossus"]` |
| stop_fraction | 0.75 | `stopFraction` |
| sway | 30 px, 10 s | `sway` |
| bob | 6 px, 5 s | `bob` |
| ground_speed | ×0.3 | `groundSpeed` |
| core_radius / core_hp | 22 px / 4 400 | `coreRadius`, `coreHealth`; core drop 1 |
| cutter_radius / cutter_hp | 15 px / 1 200 | `COLOSSUS_CUTTER`; laser every 6.5 s, 1.4 s, 12 px wide |
| ore_radius / ore_hp | 15 px / 1 700 | `COLOSSUS_ORE`; shells orange 160 px/s, radius 6 (`ORE`) |
| sink_radius / sink_hp | 16 px / 1 900 | `COLOSSUS_HEAT_SINK` |
| pod_radius / pod_hp | 14 px / 900 | `COLOSSUS_POD` |
| bullets | red 190, magenta 185 px/s | `RED`, `MAGENTA`; times the level's factors (2-4: 1.1) |
| rage_heat | 6 (`flower`, red / magenta) | `rage` |
| transformations | after 2 and 4 of 6 parts | `boss_build.default_transforms` |
| t1_radius / t1_hp | 12 px / 1 520 | `hidden_weapon("orb-…")`, pod 23.8 px high |
| t2_radius / t2_hp | 9 px / 1 900 | `hidden_weapon("sweeper-…")`, pod 23.1 px high |
| region `flanks` | the stern deck's plan either side of the upper deck: (31, 34), (58, 34), (44, 66), (21, 77), (10, 77), (10, 61), (24, 57) (mirrored), `wing`; plate 9.7–12.2 px | `armour_region("flanks", 1, …)`; `glacier_colossus_armour.flank_armour` |
| region `wings` | the shell's plan, y −6…58, x ±28 at y 26, `wing`; shell 15.8–24 px | `armour_region("wings", 2, …)`; `glacier_colossus_armour.wings_armour` |
| full_hp / full_hp_with_weapons | 13 000 / 19 840 | core + parts |
| points | 14 000 (1 400 a part) | `points` |
