# Ice Queen — 2-5 mini boss

> **Area:** bosses · **Prefix:** `MB-ICE-QUEEN` · **Related:** [common.md](../common.md), [2-5 Factory district](../../worlds/world-2/2-5-factory-district.md), [World 2](../../worlds/world-2/world.md), [Boreal Citadel (2-5 final)](../final/2-5-boreal-citadel.md)

The Ice Queen is the mini boss of 2-5, met at half the level, the hardest mini boss of World 2. It
is a slender 3.5 L ice-wraith: a needle body of cold flesh with swept membrane wings on bone and
crystals grown through it, under a crown ring that turns over it carrying three crystal shards that
fire spirals, in pale blue and violet neon. It was designed as a crystal interceptor of the Frozen
North; World 2 became the Industrial Desert (D-110) and the boss kept its name and its frost.
Everything all bosses share is in [common.md](../common.md).

## Requirements

### Look

#### MB-ICE-QUEEN-01 — Silhouette and size · MUST

The Ice Queen is `size` long. Seen from above it is a slender needle closing to a point at the
front, its wings swept far back from its middle, small canards at the nose, crystal fins leaning
back at its tail, and a round crown ring over it, wider than its body, carrying three shards.

**Acceptance criteria**
- Given the bosses viewer, when it shows the Ice Queen, then it reads as a needle-like craft under a turning ring of three crystals.

*Sources: P08-R10, P16-R05.*

#### MB-ICE-QUEEN-02 — A living ice-wraith · MUST

Its body is Cyber-Organic flesh with metal grafts (see [art direction](../../graphics/art-direction.md)),
drawn by code:
- a slender body of dark flesh, its rear a flat deck under the plating it sheds (MB-ICE-QUEEN-07),
  rimed on its back, bone ribs across it, closing to a bone needle at the nose, a crystal canopy on
  its back with a sensor crystal at the nose;
- swept wings of membrane stretched on bone struts, too long to flutter, frosted metal canards at
  the nose, frosted armour plates, seams and a vent on the wings, a crystal pod under each;
- swollen engine sacs of flesh on the wing roots, reactor sacs and reactors at the tail, glands
  lit violet;
- the crystal spire over the core, grown out of a swollen gland on its back;
- crystals grown at its wing tips, along its spine (low, under the ring) and leaning back at its tail
  as fins.

*Sources: P08-R10, P16-R05.*

#### MB-ICE-QUEEN-03 — Its crown, shards and guns · MUST

- The crown ring: a rim of sinew and bone round the body, a metal hub round the spire, three spokes
  from the hub to the rim.
- Each crystal shard lies along the ring between its two muzzles: faceted ice grown from a sac of
  flesh, banded with violet neon, a light at each tip where its bullets leave, a pale spike pointing
  out of the ring, a dark metal clamp holding it to the ring.
- The core's guns: twin crystal cannons by the nose, and the spire's glowing tip, where its spiral
  leaves from.

*Sources: P08-R10, P16-R05.*

#### MB-ICE-QUEEN-04 — Lights and colours · MUST

Its neon is pale blue (`neon`), with violet as its second colour. Pale blue: the wings' tip
edges, lines along its flanks, the strips on its engine sacs, the ring's inner band and hub, the
reactor sacs. Violet: the wings' and canards' leading edges, lines at the nose, the glands, the
spire's ring, the ring's outer band, the shards' bands.

*Sources: P08-R10, P16-R05.*

#### MB-ICE-QUEEN-05 — Frost · MUST

It keeps the World 2 frost although World 2 is now a desert: rime and snow on its back and its
engine sacs, frosted canards and plates, pale faceted crystals (palest at their tips) on its wings,
spine, tail and ring, icicles under its wings.

*Sources: P08-R10, D-110.*

#### MB-ICE-QUEEN-06 — The turning crown · MUST

The crown ring turns over the body at `spin_rate`, carrying the shards round the core; their hit
circles and muzzles turn with it (orbiting parts, see [common.md](../common.md)).

*Sources: P08-R10.*

#### MB-ICE-QUEEN-07 — What its transformation sheds · MUST

At its transformation the plating over its rear is the armour it sheds ([common](../common.md),
BOSS-42), drawn as a piece of its own: a shell of graphite plates with dark seams, snow on its
ridge, lying over the flattened rear of the fuselage (a deck at 5.5 px) and the engine sacs either
side, from a point on the tail 57 px behind the centre to a point sunk in the body's rise 6 px
behind, 5 to 10 px high and up to 16.5 px out, the violet glands on it; the tail's crystal fins are
rooted in the deck and grow through it. Its region (`back`, not mirrored) is a lozenge over the deck
and the sacs: x ±2 at 6 px behind, ±13 at 14, ±16 from 26 to 44, ±12 at 50, ±3 at 57 px behind. It
bursts into its five slices, baring a dark metal lattice (`shell`) on the deck and the sacs, and its
two gun batteries rise from the sacs either side of the spine. The boss stays one object.

**Acceptance criteria**
- Given its model, then it draws the back region's armour, and it holds together with and without
  it (unit tests).

*Sources: D-221, D-224, D-227, D-229, D-254.*

### Behaviour

#### MB-ICE-QUEEN-08 — Entry and movement · MUST

It comes in as every boss and stops with its centre at `stop_fraction` of the playfield's height. In
place it sways by up to `sway` and bobs by `bob`. During the fight the ground scrolls at
`ground_speed` of 2-5's speed.

*Sources: P08-R10.*

#### MB-ICE-QUEEN-09 — Crystal shards · MUST

Three parts, `shard-1` to `shard-3`, a third of a turn apart on the crown, `shard_orbit` from the
core (at a spin of 0, the first straight ahead of it), `shard_radius` round with `shard_hp` each.
All three shield the core. Every 0.9 s each fires a pair of purple bullets in opposite directions,
each from the tip pointing its way, the pair turned 21° more at each volley, so each shard throws a
two-armed spiral as the crown carries it round; the
three are out of step (first at 0.4, 0.7 and 1 s). They fire the same in every stage while they
stand.

*Sources: P08-R10.*

#### MB-ICE-QUEEN-10 — Core and stage patterns · MUST

Its core (`core_radius`, `core_hp`) fires aimed bursts from its nose cannons and, once it stands
alone, a spiral from the spire. One pattern per stage:
- stage 0: bursts of 3 magenta, 0.15 s apart, every 2.6 s;
- stage 1: bursts of 4 magenta, 0.13 s apart, every 2.3 s;
- stage 2: bursts of 5 magenta, 0.11 s apart, every 2.2 s, and an aimed spread of 3 blue, 14° apart,
  every 3.3 s;
- stage 3 (the last): a ring of 14 blue every 1.2 s turning 11° a volley, and bursts of 4 magenta,
  0.12 s apart, every 2.4 s.

The last stage's spiral is fired by no earlier stage.

*Sources: P08-R10, D-068.*

#### MB-ICE-QUEEN-11 — Rage · MUST

It is angry as every boss with a `flower` at heat `rage_heat` (a dense, slowly turning purple ring,
small blue fans at the player): the hottest mini boss rage of World 2.

*Sources: D-068.*

#### MB-ICE-QUEEN-12 — Transformation · MUST

It transforms once, when 2 of its 3 shards are destroyed. The transformation sheds its rear plating
(MB-ICE-QUEEN-07) and reveals a pair of gun batteries, `battery-left` and `battery-right`, at ±12 px
across and 39 px behind the centre, `weapon_radius` round with `weapon_hp` each (0.8 of a shard's),
firing purple fans straight down ([common.md](../common.md)), first 1.2 s and 2.0 s into each stage.
They shield the core.

*Sources: D-221, D-224, D-229.*

#### MB-ICE-QUEEN-13 — Health, points and death · MUST

Its full health is `full_hp` (core and shards), `full_hp_with_weapons` with its batteries. It is
worth `points`. Its parts drop a bonus as mini boss parts do, its batteries as hidden weapons do. It
dies as every boss.

*Sources: P08-R10, P08-R11, D-068, D-221.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| size | 3.5 L (119 px) | `src/game/config/bosses/world_2/ice_queen.py` `_ICE_QUEEN["stats"]` |
| neon | pale blue (0.55, 0.65, 1), violet second | `src/game/config/boss_look.py` `BOSS_LOOK.neon["ice-queen"]`; violet in `src/game/view/bosses/world_2/ice_queen_shards.py` |
| stop_fraction | 0.74 | `stopFraction` |
| sway | 65 px, 6.5 s | `sway` |
| bob | 8 px, 3 s | `bob` |
| ground_speed | ×0.6 | `groundSpeed` |
| spin_rate | 0.85 rad/s | `spinRate` |
| core_radius / core_hp | 18 px / 1 680 | `coreRadius`, `coreHealth` |
| shard_orbit | 42 px, muzzles 13 px either side, 13 px high | `ICE_QUEEN_SHARD`, `SHARD_TURNS` |
| shard_radius / shard_hp | 13 px / 840 | `ice_queen_parts` |
| bullets | purple 190, magenta 195, blue 185 px/s | `PURPLE`, `MAGENTA`, `BLUE`; times the level's factors (2-5: 1.15) |
| rage_heat | 6.5 (`flower`, purple / blue) | `rage` |
| transformation | after 2 of 3 parts | `boss_build.default_transforms` |
| weapon_radius / weapon_hp | 10 px / 670 | `hidden_weapon("battery-…")`, pod 16.5 px high |
| region `back` | a lozenge, not mirrored: x ±2 at y 6, ±13 at y 14, ±16 at y 26…44, ±12 at y 50, ±3 at y 57; plating 5–10 px on the deck at 5.5; `shell` | `armour_region("back", 1, …)`; `src/game/view/bosses/world_2/ice_queen_armour.py` |
| full_hp / full_hp_with_weapons | 4 200 / 5 540 | core + parts |
| points | 7 000 (700 a part) | `points` |
