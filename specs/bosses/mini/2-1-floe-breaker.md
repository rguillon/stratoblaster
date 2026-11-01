# Floe Breaker — 2-1 mini boss

> **Area:** bosses · **Prefix:** `MB-FLOE-BREAKER` · **Related:** [common.md](../common.md), [2-1 Great erg](../../worlds/world-2/2-1-great-erg.md), [World 2](../../worlds/world-2/world.md), [Narwhal (2-1 final)](../final/2-1-narwhal.md)

The Floe Breaker is the mini boss of 2-1, the first World 2 boss, met at half the level. It is a 3 L
ice-ram: a shelled sea beast of cold flesh with a bone ram at its bow and a harpoon gun on a muscle
bulging from each flank, in cyan neon. It was designed as an icebreaker hovership for the Frozen
North; World 2 became the Industrial Desert (D-110) and the boss kept its name and its frost, so it
now flies over the desert. Everything all bosses share (parts and core, stages, rage, turrets,
transformations, wounds, death, checkpoint) is in [common.md](../common.md); this file gives only
what is its own.

## Requirements

### Look

#### MB-FLOE-BREAKER-01 — Silhouette and size · MUST

The Floe Breaker is `size` long. Seen from above it is an icebreaker's hull: long, sharp at the
bow, square at the stern, widest a little behind its middle, with a ridged ram along its front
deck whose point is the front of the boss (down the screen). The two harpoon guns stand out on
either flank, a little ahead of the middle.

**Acceptance criteria**
- Given the bosses viewer, when it shows the Floe Breaker, then it reads as a pointed ram ahead of a long, square-sterned body, a gun on each flank.

*Sources: P08-R10, P16-R05.*

#### MB-FLOE-BREAKER-02 — A living ice-ram · MUST

Its body is Cyber-Organic flesh with metal grafts (see [art direction](../../graphics/art-direction.md)),
drawn by code:
- a belly of cold teal flesh, rimed on top, where the hover skirt was, ice teeth along its rim;
- a shell of teal plates with dark seams over its back;
- a brain hump of dark graphite flesh behind the middle, bone ribs across it, two spiracles
  breathing out of the back behind it, each capped by a sooted metal valve;
- a ram of bone, crusted with ice on its top facets towards the point, three metal ice-breaking
  blades grafted along each side at its waterline, a fringe of flesh on each flank;
- reactor sacs at the stern, lit cyan.

Metal shows only where it is grafted: frosted armour plates on the back, the bow chasers' mount on
the ram, an antenna stalk and a small dish on the hump, the sponsons' mounts. The dressing is not a
mirror image: an egg sac to port (the screen's left), a coiled tow sinew on the stern to starboard.

*Sources: P08-R10, P16-R05.*

#### MB-FLOE-BREAKER-03 — Its parts and guns on the body · MUST

- Each harpoon gun sits on a sponson either side of the middle: a muscle of graphite flesh bulging
  from the flank, an octagonal frosted metal mount on top, a cable reel outboard (a gland of sinew),
  ice crystals and a sinew round it, a cyan light on its outer side. Its turret carries one long
  barrel with barbs near the tip.
- The core's guns: two short bow chasers on a dark metal mount grafted on the ram, and the frost
  beacon on top of the hump (a metal beacon, a cyan ring round it, a white charge light at its top),
  where its rings leave from.

*Sources: P08-R10, P16-R05.*

#### MB-FLOE-BREAKER-04 — Lights and colours · MUST

Its neon is cyan (`neon`). It lights: a line of photophores round the belly where the skirt's band
was, a stripe along each side of the ram, a row of five eyes across the hump's brow over a cyan bar,
glowing veins and lit glands down its flanks, the beacon's ring and the reactor sacs. Navigation
lamps sit at the stern: red to port (the screen's left), green to starboard.

*Sources: P08-R10, P16-R05.*

#### MB-FLOE-BREAKER-05 — Frost · MUST

It keeps the World 2 frost although World 2 is now a desert: ice crust on the ram, frosted plates,
clusters of ice crystals grown through the flesh (on its back, flanks, sponsons and stern), a short
row of ice spines on the stern, ice teeth under the belly's rim.

*Sources: P08-R10, D-110.*

#### MB-FLOE-BREAKER-06 — Moving pieces · MUST

Two hover fans, each in a ring of flesh either side of the stern, spin. The harpoon turrets turn as
they aim (MB-FLOE-BREAKER-09). Nothing else moves but the shared living motion of
[common.md](../common.md).

*Sources: P08-R10, P16-R05.*

#### MB-FLOE-BREAKER-07 — What its transformation sheds · MUST

At its transformation the plating over its front half (region `back`: from 57 px ahead of its
centre to 3 px behind it, 60 px across, one region on the centre line) bursts off in chunks,
baring a dark metal lattice frame (`shell`), and its two gatlings rise from it either side of the
ram. Only the upper part of the body is cut, so the keel, the sponsons and the harpoon guns stay,
and the boss stays one object.

**Acceptance criteria**
- Given the bosses viewer, when K breaks a harpoon gun, then the front plating bursts, a dark lattice shows and two gatlings unfold from it; nothing of the boss is left hanging in the air.

*Sources: D-221, D-224, D-227, D-229.*

### Behaviour

#### MB-FLOE-BREAKER-08 — Entry and movement · MUST

It comes in as every boss and stops with its centre at `stop_fraction` of the playfield's height.
In place it sways left and right by up to `sway` and bobs by `bob`. During the fight the ground
scrolls at `ground_speed` of 2-1's speed.

*Sources: P08-R10.*

#### MB-FLOE-BREAKER-09 — Harpoon guns · MUST

It has two destroyable parts, `harpoon-left` and `harpoon-right`, at ±30 px across and 4 px ahead of
its centre, each `harpoon_radius` round with `harpoon_hp`. Both shield the core. Each turns on its
turret to aim and fires aimed bursts of 3 red bullets, 0.16 s apart, every 2.6 s, the two out of step
(first at 1 s and 2.3 s into a stage). They fire the same in every stage while they stand.

*Sources: P08-R10.*

#### MB-FLOE-BREAKER-10 — Core and stage patterns · MUST

Its core (`core_radius`, `core_hp`) fires from its bow chasers and, for rings, from the frost
beacon. One pattern per stage (a stage more for each destroyed part, see
[common.md](../common.md)):
- stage 0: a fan of 3 magenta bullets, 18° apart, every 3 s;
- stage 1: an aimed spread of 3 magenta, 12° apart, every 2.2 s;
- stage 2 (the last): a ring of 10 blue every 1.7 s, and a fan of 5 magenta, 14° apart, every 2.6 s.

The last stage's ring is fired by no earlier stage.

*Sources: P08-R10, D-068.*

#### MB-FLOE-BREAKER-11 — Rage · MUST

After the pause that follows each destroyed part it is angry as every boss, with a `curtain` at heat
`rage_heat` (blue fans sweeping, a magenta ring under them): the mildest rage of World 2.

*Sources: D-068.*

#### MB-FLOE-BREAKER-12 — Transformation · MUST

It transforms once, when one of its two harpoon guns is destroyed (half its original parts). The
transformation sheds its front plating (MB-FLOE-BREAKER-07) and reveals a pair of gatlings,
`gatling-left` and `gatling-right`, at ±12 px across and 27 px ahead of its centre, `weapon_radius`
round with `weapon_hp` each (0.8 of a harpoon gun's), firing red bullets. They shield the core and
fire the gatling's bursts at the player ([common.md](../common.md)), first 1.2 s and 2.0 s into each
stage, from then on in every stage while they stand.

*Sources: D-221, D-224, D-229.*

#### MB-FLOE-BREAKER-13 — Health, points and death · MUST

Its full health is `full_hp` (core and harpoon guns), `full_hp_with_weapons` with its gatlings
(the health bar counts them from the start). It is worth `points`. Its parts drop a bonus as mini
boss parts do, its gatlings as hidden weapons do. It dies as every boss.

*Sources: P08-R10, P08-R11, D-068, D-221.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| size | 3 L (102 px) | `src/game/config/bosses/world_2/floe_breaker.py` `_FLOE_BREAKER["stats"]` |
| neon | cyan (0.1, 0.85, 1) | `src/game/config/boss_look.py` `BOSS_LOOK.neon["floe-breaker"]` |
| stop_fraction | 0.72 | `stopFraction` |
| sway | 65 px, 7 s | `sway` |
| bob | 8 px, 3.5 s | `bob` |
| ground_speed | ×0.5 | `groundSpeed` |
| core_radius / core_hp | 18 px / 1 420 | `coreRadius`, `coreHealth` |
| harpoon_radius / harpoon_hp | 13 px / 650 | `part("harpoon-left" …)` |
| bullets | red 190, magenta 180, blue 185 px/s, radius 4 | `RED`, `MAGENTA`, `BLUE`; times the level's factors (2-1: 0.9) |
| rage_heat | 2.5 (`curtain`, blue / magenta) | `rage` |
| transformation | after 1 of 2 parts | `boss_build.default_transforms` |
| weapon_radius / weapon_hp | 10 px / 520 | `FLOE_BREAKER`, `hidden_weapon("gatling-…")`; pod 12 px high |
| region `back` | x −30…30, y −57…3, from 1.7 px up, `shell` | `armour_region("back", 1, …)` |
| full_hp / full_hp_with_weapons | 2 720 / 3 760 | core + parts |
| points | 5 500 (550 a part) | `points`; part share in `src/game/config/scoring.py` |

## Notes

- The module docstrings still call 2-1 "the Ice floes level" and the health values "placeholders":
  both predate the 2026-10-27 rework (D-110) and the tuning of D-068.
- Phase 8 stage patterns were the agent's design, kept by the reviewer (P08-R10 implementation report).
