# Snow Owl — 2-3 mini boss

> **Area:** bosses · **Prefix:** `MB-SNOW-OWL` · **Related:** [common.md](../common.md), [2-3 Oil fields](../../worlds/world-2/2-3-oil-fields.md), [World 2](../../worlds/world-2/world.md), [Aurora Station (2-3 final)](../final/2-3-aurora-station.md)

The Snow Owl is the mini boss of 2-3, met at half the level. It is a 3 L living owl of cold flesh
with broad membrane wings on bone, a radar pod on each wing and one big round eye at its front that
fires a laser, in white neon. It is one of the eight bosses that change shape as they transform: its
wing tips slide out. It was designed as a recon drone over the tundra of the Frozen North; World 2
became the Industrial Desert (D-110) and the boss kept its name and its frost. Everything all
bosses share is in [common.md](../common.md).

## Requirements

### Look

#### MB-SNOW-OWL-01 — Silhouette and size · MUST

The Snow Owl spans `size` across its wings, wider than it is long: a plump body in the middle, broad rounded wings either side with a trailing edge cut into feathers, a radar pod on each
wing, and the round eye on a neck at the front of the body.

**Acceptance criteria**
- Given the bosses viewer, when it shows the Snow Owl, then it reads as a wide-winged bird with one big eye at its front.

*Sources: P08-R10, P16-R05.*

#### MB-SNOW-OWL-02 — A living owl · MUST

Its body is Cyber-Organic flesh with metal grafts (see [art direction](../../graphics/art-direction.md)),
drawn by code:
- broad membrane wings on bone struts, a layer of teal flesh rimed on their fronts, bone feather
  lines across the trailing edge, a metal ring grafted where each pod sits; their outer panels are
  pieces of their own (MB-SNOW-OWL-07);
- a plump body of teal flesh, its back flat under a shell of teal plates with dark seams rimed on
  top (the plating it sheds, MB-SNOW-OWL-07), bone ribs across it, a row of ice spines down the
  shell;
- a sinewy neck holding the eye, a metal ring round it;
- ear tufts of graphite flesh swept back over the head;
- reactor sacs at its tail.

Its wings are too big to flutter: they stay still.

*Sources: P08-R10, P16-R05.*

#### MB-SNOW-OWL-03 — Its parts and guns on the body · MUST

- Each radar pod: a swollen nacelle of graphite flesh on the wing, an iced metal radome grafted on
  it with a white ring, an antenna turning on top, two fan barrels poking out of the nacelle's front,
  a gland lit white.
- The sensor eye: a real eye in a lid of sinew facing forward, its lens ringed with white neon, a
  dark pupil, the iris lighting up as its laser charges, under a brow of bone capped with rime.
- The core's guns: two chin guns either side of the eye, and the crown emitter on its back between
  the ear tufts (a white ring), where its rings leave from.

*Sources: P08-R10, P16-R05.*

#### MB-SNOW-OWL-04 — Lights and colours · MUST

Its neon is white (`neon`): lines along its wings' leading edges, a light on each ear tuft's tip,
lines along the body, the pods' rings and glands, the eye's ring and lens, the crown's ring, the
reactor sacs. Navigation lamps at the wing tips: red to port (the screen's left), green to
starboard.

*Sources: P08-R10, P16-R05.*

#### MB-SNOW-OWL-05 — Frost · MUST

It keeps the World 2 frost although World 2 is now a desert: rime on the wings' fronts and its back,
iced radomes, icicles under the wings' trailing edges, the pods and the eye's brow, ice crystals on
its body and by the eye.

*Sources: P08-R10, D-110.*

#### MB-SNOW-OWL-06 — Moving pieces · MUST

The antenna on each radar pod turns. The wings stay still. Nothing else moves but the shared living
motion of [common.md](../common.md) and its transformation (MB-SNOW-OWL-07).

*Sources: P08-R10, P16-R05.*

#### MB-SNOW-OWL-07 — Its transformation changes its shape · MUST

At its transformation ([common](../common.md), BOSS-42, BOSS-45), its armour drawn as pieces of its
own:
- the outer panel of each wing (region `wingtips`, mirrored: the wing beyond 30 px out, its leading
  edge from 9.2 px ahead at the root to 5 px ahead at 48 px out, out to 56 px, back to 12 px behind)
  is a piece of its own: the wing's membrane slab and its rime beyond 30 px, with its leading
  edge's white neon, the pod's socket ring and its navigation lamp (no icicles hang from it). It
  stays on and slides `tip_slide` further out, eased, as the armour of other bosses would burst;
  the dark metal spars of a wing frame (`wing`) show on a floor just under the wing's slab in the
  gap it leaves, and a sweeper rides each new tip;
- the plating of its back (region `back`, not mirrored: the flat deck of the back, x ±4.5 at 22 px
  behind, ±6 at 18 behind, ±7.5 from 4 behind to 6 ahead) is a shell of teal plates with dark seams,
  snow on it, lying on the flattened back (its deck at 5.9 px) from a point on the tail 24 px behind
  to a point sunk in the head's rise 8.5 px ahead, 5.5 to 12.4 px high, carrying the lit glands and
  stripes, the ice crystals, the spine row and the sensor's hood. It bursts into its five slices,
  baring a dark metal lattice (`shell`) on the deck, and its mortar rises from it; the crown emitter
  stands on a stem from the deck.

The boss stays one object: the slid tips keep their whole body together.

**Acceptance criteria**
- Given the bosses viewer, when K breaks both wing pods, then the wing tips slide out with a sweeper on each, the back bursts and a mortar rises.
- Given its model, then it draws every region's armour, and it holds together with and without it
  (unit tests).

*Sources: D-224, D-227, D-230, D-254.*

### Behaviour

#### MB-SNOW-OWL-08 — Entry and movement · MUST

It comes in as every boss and stops with its centre at `stop_fraction` of the playfield's height. In
place it sways by up to `sway` and bobs by `bob`. During the fight the ground scrolls at
`ground_speed` of 2-3's speed.

*Sources: P08-R10.*

#### MB-SNOW-OWL-09 — Wing radar pods · MUST

Parts `pod-left` and `pod-right`, at ±38 px across and 2 px ahead of the centre, `pod_radius` round
with `pod_hp` each. Both shield the core. Each fires a fan of 3 magenta bullets, 14° apart, every
2.3 s (first at 0.9 s and 2 s), leaning 10° towards the other side, so the two fans cross under the
owl.

*Sources: P08-R10.*

#### MB-SNOW-OWL-10 — Sensor eye · MUST

Part `eye`, 30 px ahead of the centre, `eye_radius` round with `eye_hp`. It sits in front of the core
and does not shield it, so it can always be shot. Every 5.5 s (first 3 s into a stage) it fires a
laser straight down the screen from its lens, after the laser's warning line, firing for 1.4 s. The
laser is drawn in the boss's white and is seen leaving the lens, not from under the brow round it.

*Sources: P08-R10, D-072.*

#### MB-SNOW-OWL-11 — Core and stage patterns · MUST

Its core (`core_radius`, `core_hp`) fires red bullets from its chin guns and, for rings, from the
crown emitter. One pattern per stage:
- stage 0: 1 red at the player every 3 s;
- stage 1: an aimed spread of 3 red, 12° apart, every 2.4 s;
- stage 2: aimed bursts of 4 red, 0.14 s apart, every 2.2 s;
- stage 3 (the last): a ring of 12 blue every 1.4 s turning 8° a volley, and 1 purple at the player
  every 2.4 s.

The last stage's ring is fired by no earlier stage.

*Sources: P08-R10, D-068.*

#### MB-SNOW-OWL-12 — Rage · MUST

It is angry as every boss with a `flower` at heat `rage_heat` (a dense, slowly turning blue ring,
small magenta fans at the player).

*Sources: D-068.*

#### MB-SNOW-OWL-13 — Transformation · MUST

It transforms once, when both wing pods are destroyed (whatever happened to its eye): the pods stand
on the wing tips, which must be gone before the tips move. The transformation reshapes it
(MB-SNOW-OWL-07) and reveals three weapons, `transform_hp` each (0.8 of a pod's), all shielding the
core:
- `sweeper-left` and `sweeper-right`, riding the slid tips (±61 px across, 1 px ahead of the centre,
  `sweeper_radius` round), firing the sweeper's laser that follows the player while it fires
  ([common.md](../common.md)), in the boss's white, first 1.2 s and 3.8 s into each stage;
- `mortar` on its back (8 px behind the centre, `mortar_radius` round), firing purple flak shells
  that burst into rings ([common.md](../common.md)), first 2.0 s into each stage.

*Sources: D-221, D-229, D-230, D-072.*

#### MB-SNOW-OWL-14 — Health, points and death · MUST

Its full health is `full_hp` (core and original parts), `full_hp_with_weapons` with its hidden
weapons. It is worth `points`. Its parts drop a bonus as mini boss parts do, its hidden weapons as
hidden weapons do. It dies as every boss.

*Sources: P08-R10, P08-R11, D-068, D-221.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| size | 3 L (102 px) | `src/game/config/bosses/world_2/snow_owl.py` `_SNOW_OWL["stats"]` |
| neon | white (0.85, 0.92, 1) | `src/game/config/boss_look.py` `BOSS_LOOK.neon["snow-owl"]` |
| stop_fraction | 0.73 | `stopFraction` |
| sway | 65 px, 7.5 s | `sway` |
| bob | 9 px, 3.4 s | `bob` |
| ground_speed | ×0.5 | `groundSpeed` |
| core_radius / core_hp | 18 px / 1 250 | `coreRadius`, `coreHealth` |
| pod_radius / pod_hp | 13 px / 850 | `part("pod-…")` |
| eye_radius / eye_hp | 11 px / 600 | `part("eye" …)`; laser every 5.5 s, 1.4 s, 12 px wide |
| bullets | magenta 180, red 190, blue 185, purple 195 px/s | `MAGENTA`, `RED`, `BLUE`, `PURPLE`; times the level's factors |
| rage_heat | 4.5 (`flower`, blue / magenta) | `rage` |
| transformation | both pods destroyed | `transformParts` |
| tip_slide | 16 px out | `moving_region("wingtips", 1, …, slide([[0, 0, 0], [16, 0, 0]]))` |
| region `wingtips` | x 30…56 (mirrored), y −9.2 at x 30 to −5 at x 48…56, back to y 12; the panel −1.2–2.1 px; `wing` | `moving_region("wingtips", 1, …)`; `src/game/view/bosses/world_2/snow_owl_armour.py` |
| region `back` | x ±4.5 at y 22, ±6 at y 18, ±7.5 at y 4…−6, not mirrored; shell 5.5–12.4 px on the deck at 5.9; `shell` | `armour_region("back", 1, …)`; `snow_owl_armour.py` |
| sweeper_radius / mortar_radius | 6 px / 9 px | `hidden_weapon("sweeper-…")`, pods 7 px high; `hidden_weapon("mortar" …)`, pod 14 px high |
| transform_hp | 680 | each hidden weapon |
| full_hp / full_hp_with_weapons | 3 550 / 5 590 | core + parts |
| points | 5 500 (550 a part) | `points` |

## Notes

- The design note of D-230 first had the tips folded up over its back and swinging out; they slide
  out instead (D-230 as built).
- Its three hidden weapons (two sweepers and a mortar) make its full health with weapons the
  highest of the World 2 mini bosses (see P08-R11 in [World 2](../../worlds/world-2/world.md)).
