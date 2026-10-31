# Boss armour shedding: design

Date: 2026-10-31. Branch: `feat/ship-glow-boss-transform`.
Follows `2026-10-31-ship-glow-and-boss-transform-design.md` (Part B). Replaces its two reveal styles.

## Goal

When a boss transforms, it should look like it is breaking apart, not like new turrets are
zooming in. Each transformation sheds a whole region of the boss's own armour. The armour breaks
into chunks that fly off, a dark metal frame shows underneath, and the hidden weapons unfold
mechanically from that frame.

Reference case, the Jaguar (3-5): its whole spotted wing pelt bursts off, a gunmetal wing
skeleton shows, and two lasers unfold on the wings.

Scope: all 40 bosses, built with a shared kit (approach 1, "armour carved from the boss's own
body").

## What the player sees

The boss looks exactly as it does today until it transforms. A transformation lasts 2.0 s
(up from 1.5 s) and runs in four beats. The fractions below are tunables in `BOSS_LOOK.reveal`.

1. **Strain (0 to 0.15).** Seam lines across the region that is about to go glow brighter in the
   boss's neon, and the region shudders.
2. **Burst (at 0.15).** The region's armour splits into chunks along the seam grid: at most 10 per
   region and 24 per boss. Each chunk is thrown outward from the boss's centre and up. It tumbles,
   falls and shrinks away by 0.6. Small blasts (`ctx.explode`) pop along the region.
3. **Exposed frame (from 0.15 onward).** A dark gunmetal frame, generated from the region's outline,
   takes its place: spars, ribs and pipes, with thin glowing seams in the boss's neon. It keeps its
   own glowing edge trim.
4. **Hinged unfold (0.4 to 1.0).** Each weapon revealed by the transformation starts folded flat in
   the frame and swings up on its hinge (0.4 to 0.75). Its barrel then slides out along its axis
   with a small overshoot and settle (0.7 to 1.0). Nothing scales.

A final boss sheds one region per transformation, so it gets more skeletal at each one. The old
octagon plates and the swing-and-grow unfold are removed.

## How it's built

### Armour regions (model side)

A boss drawing (the record with `core`, `parts`, `limbs`) gets an optional `armour` field: a list
of regions. Each region has these fields:

| Field | Meaning |
|---|---|
| `id` | Region name, e.g. `"wings"`. |
| `form` | The transformation that sheds it (1, or 1 and 2 for final bosses). |
| `outline` | XZ polygon in model space (closed; use `symmetric` for mirrored shapes). |
| `heights` | `[bottom, top]` of the region. |
| `frame` | `"wing"` (edge spar and root-to-tip ribs), `"shell"` (rib lattice for domes and backs) or `"ring"` (radial spokes for discs and halos). |
| `draw(p)` | Draws the region's armour with the usual `EnemyParts` builders. |

Each model moves the drawing of its armour out of `core` into its regions. For the Jaguar, that
is the wing pelt, the rosettes and the leading-edge lights. The model at rest looks the same as
before.

### Kit modules

| Module | Layer | Job |
|---|---|---|
| `src/render/geometry/shatter.py` | pure | Splits triangles into chunks by centroid on an XZ grid. Merges neighbouring cells until there are at most `max_chunks` chunks, re-centres each chunk, and returns their centres. |
| `src/render/shatter_mesh.py` | render | Builds one child mesh per chunk (same material) under the armour node. |
| `src/game/view/bosses/boss_armour.py` | view | Builds the regions: the armour as chunks, the seam lines (a neon layer brightened in the strain beat), and the hidden frame. Each tick it poses the chunks (shudder, then throw, tumble, fall and shrink; the old `plate_pose` generalised), hides them after the burst and disposes them. |
| `src/game/view/bosses/boss_frame.py` | view | Draws the frame from an outline, a style and heights: spars and ribs, pipes, neon seams. New shade `BOSS_LOOK.frame` (darker gunmetal than `ENEMY_LOOK.hull.panel`). |
| `src/game/view/bosses/boss_reveal.py` | view | Hinged unfold only. A weapon's `mount` gives its hinge point and fold direction. The pose is a rotation about the hinge (flat to standing), then the barrel node slides out along its axis with an overshoot ease. |

### Trim

The armour keeps its trim at rest, and each chunk clears its trim once it starts flying. The frame
is its own trim group, so it gets its edges even though it is built under the armour. It stays
disabled until the burst.

### Sim and core

There is almost no change: transformations, hidden parts, `form`, `transforming_into` and
`transform` already exist. `BOSS_TIMING.transformSeconds` goes from 1.5 to 2.0, and the view reads
the beat fractions from `BOSS_LOOK.reveal`. The `ctx.explode` call in `on_transform` spreads its
blasts over the shed regions' outlines rather than only over the parts' spots. The regions come
from config: see "Weapons and config".

### Dev viewer

There is no change. K already breaks parts until a transformation, which plays the full reveal.

## Weapons and config

- `hidden_weapon(...)` gets a `mount`: the hinge offset from the part's spot and the fold direction
  (the weapon lies along it when folded). `with_weapons` loses its style argument.
- Each boss config gets its regions' gameplay half: `armour: [{id, form, outline}]`. The sim uses
  it for the blasts and the tests use it for the checks. The model reads the same record and adds
  `heights`, `frame` and `draw`.
- Each boss's hidden weapons are re-picked to fit its shed region, from the four existing kinds
  (gatling, lance, rack, orb). Every transformation must still raise the boss's fire rate
  (`test_boss_transforms`). The Jaguar's form 1 becomes two lances, one on each wing frame.
- Every hidden part must lie inside a region shed by its own transformation.

## Rollout

The work goes in batches, each with dev-viewer screenshots before and after the burst:

1. the kit, plus the Jaguar;
2. World 1;
3. World 2;
4. World 3;
5. World 4.

Each boss gets the frame style that fits it best: wings for winged bosses, shells for domed or
organic backs, rings for discs. Final bosses get two regions, one per transformation.

## Testing

- **Pure:**
  - shatter: chunk cap; every triangle lands in exactly one chunk; centres are correct;
  - frame: geometry lies within the outline; spar and rib counts are as expected per style;
  - hinged unfold: folded at 0, deployed at 1, overshoot in between, scale always 1;
  - burst curve: chunks are gone by the end of the burst window.
- **Config, every boss:**
  - each transformation sheds at least one region;
  - each hidden part lies inside its region;
  - fire rate escalates;
  - chunk budget per boss.
- **View, with fakes:**
  - the frame is hidden before the burst and shown after;
  - chunks are disposed after the burst;
  - revealed parts never scale.
- **E2E:** the existing `tests/e2e/test_boss_transform.py`.
- **Light check:** `make typecheck build e2e`.

## Records

D-224 in `specs/DECISIONS.md`: armour shedding replaces the reveal styles of D-221, and transform
time goes from 1.5 s to 2.0 s.

## Out of scope

- No change to the player ships or the enemies.
- No new weapon kinds.
- No change to when transformations happen (still at 1/2 for mini bosses, and at 1/3 and 2/3 for
  final bosses).

## Changes made while building it (see D-224)

- **The armour is cut out automatically, not redrawn.** No model got a `drawing.armour` with its own
  `draw(p)`. Instead, the core's drawing is recorded and its faces inside a region's outline (and
  heights) are cut out of it. Regions live wholly in config (`armour_region`): outline, mirror,
  heights and frame style.
- **The frame's floor is the armour's own top view**, flattened and darkened. The ribs are clipped
  to it, and only the floor carries the glowing trim.
- **Strain is a strobe and shudder of the whole armour**, not glowing seam lines.
- **Weapon kinds are unchanged** except the Jaguar's, which became lances. Lances are longer
  (1.9 radii).
