# Ship glow trim and boss transformations — design

- **Date:** 2026-10-31
- **Branch:** `feat/ship-glow-boss-transform`
- **Status:** awaiting reviewer approval
- **Scope:** outside a phase, at the reviewer's request (in chat): "rework all the ships, replace the
  existing glowing effect by adding the glowing parts directly into the ship geometry … rework the
  bosses … make him spawn new weapons. The boss can transform, or drop an armor part to reveal the new
  weapons."

## Intent

What the reviewer said:

1. Every ship (player ships, enemies, mini bosses, final bosses) loses the current glow effect; glowing
   parts become part of the ship geometry.
2. Today, a boss that loses a part that shoots gets easier. Bosses must get harder: after losing parts,
   a boss reveals new weapons, by transforming or by dropping armour.

Answers given during design (reviewer, 2026-10-31):

- Ships concerned: **all** (3 player ships, every enemy kind, all 40 bosses).
- Glowing parts: **neon edge trim** along the silhouette (not detail lights).
- Revealed weapons: **new destroyable parts**.
- Cadence: **set transformation points** (mini boss once, final boss twice).

Success criteria:

- No ship, enemy or boss uses the `OutlineLayer` rim; each reads against every world's ground through
  its own trim (P14-R03/R04 e2e contrast checks still pass, thresholds unchanged).
- Every boss's live fire rate after each transformation is at least what it was before it.
- Triangle budgets (P16-R09) still hold.

## Part A — glowing edge trim (replaces the rim outline)

### What the current glow is

`src/render/outline.py`: a mesh flagged with `metadata.outline` is drawn a second time, fatter, in a rim
colour (`renderOutline`). Applied to the player ships (`readability_view.outlined_ships`, P14-R03), to
every enemy hull and boss part (`enemy_mesh.add_surfaces`, P14-R04) and to enemy missiles
(`enemy_shot_renderer`).

### Approach: hybrid automatic trim

- New pure helper `src/render/geometry/edge_trim.py`. Input: a model's geometry (positions, indices).
  It keeps the **top-view silhouette edges**: edges shared by a face whose normal points up (+Z towards
  the camera) and one whose normal points down, plus open (single-face) edges. Because enemies and
  bosses only turn around the vertical axis, these edges stay the silhouette whatever their heading;
  they are close enough under the 35° playfield camera.
- Along each kept edge it builds a thin ribbon (quad strip), pushed outward by a small offset, with
  mitred / capped corners so the trim reads as continuous.
- Options per model: `width`, `offset`, `skip` (edges or regions to leave out), `extra` (hand-placed
  strips). Defaults give the automatic trim; the player ships and the bosses' signature edges are
  hand-tuned through the options.
- The ribbons go into the model's existing self-lit layer:
  - player ships: the player cyan (today's `LOOK.playerOutline.color`), on the ships' light material;
  - enemies and bosses: the `neon` layer, in the enemy's neon colour (enemy colour family, P14-R02).
  They bloom in the existing playfield glow layer.
- Boss parts: each destroyable part's trim is built on that part's own mesh, so it goes dark / away
  when the part is destroyed, and is dark while the part is hidden (Part B). This keeps P14-R04's "the
  player can see which parts can still be hit".

### Removed

- `outline_model` / `set_outline` calls on player ships, enemy hulls and boss parts.
- `OutlineLayer`, `compile_outlines`, `outlines_ready` and their wiring in `app/level_scene.py` once
  nothing ship-like uses them. Enemy missiles keep their rim (they are not ships); if they are the last
  user, the layer stays for them only.

### Constraints

- Triangle budgets per tier (P16-R09) and the player ships' budgets: a unit test builds every model and
  checks its count, trim included.
- Readability: the P14 e2e contrast tests must pass without the rim. A failing model gets a wider or
  brighter trim; thresholds are never lowered.
- Invincibility blinking (GD-22) still applies to the whole ship, trim included (it is part of the
  model).

### Spec reading

P14-R03/R04 ask for an "outline / rim glow" / "rim light or outline". The edge trim is read as a
built-in rim light; recorded in `DECISIONS.md`, requirement text untouched.

## Part B — boss transformations

### Rules

- A boss design lists **hidden weapon parts**: ordinary destroyable parts (guns, volleys, health,
  drop chance) with `reveal: K`, the transformation that brings them.
- **Triggers** count destroyed *original* parts only (revealed parts do not trigger). Defaults:
  - mini boss: one transformation at ⌈n/2⌉ original parts destroyed;
  - final boss: two, at ⌈n/3⌉ and ⌈2n/3⌉.
  A design may override the thresholds.
- **Transforming**: a state of `transform_seconds` (default 1.5 s). The boss does not fire and takes no
  damage while its armour drops or its limbs unfold. At the end, transformation K's parts are revealed:
  they become hit targets and their volleys fire; then the usual rage burst follows.
- If several thresholds are crossed at once (e.g. a bomb, or `break_next`), the transformations run one
  after the other.
- **Revealed parts shield the core** by default (`shields: True`), so the player cannot skip them.
- **Health bar**: hidden parts count in `full_health` and `remaining_health` from the start, so the bar
  never grows mid-fight.
- **Kept**: the core's per-stage volleys, stage pauses, rage and break rings work as today; revealed
  weapons come on top.
- If the core is destroyed (only possible once no shielding part is left) the boss dies as today,
  hidden parts included.

### Engine (`src/core/`, game-agnostic)

- `BossPartSpec`: new optional `reveal: int | None`. A hidden part (`BossPart.hidden`) is not in the hit
  or shot targets, is not a volley source, its turret does not turn, it is not counted by
  `core_shielded` while hidden.
- `BossStats`: new optional `transforms: list[int] | None` (thresholds) and `transform_seconds`.
- `Boss`: new state `"transforming"`; `_break_parts` checks the thresholds after counting the original
  parts destroyed, queues transformations; `vulnerable` is false while transforming; at the end of one,
  parts with that `reveal` are revealed and targets rebuilt. New optional hook
  `on_transform(k, ctx)` (as `on_stage_change`). New field `transform` (0..1 progress, for the view) and
  `form` (number of transformations done).
- `break_next` (P07-R09) goes on through the transformations: it skips hidden parts, so the next
  destroy may trigger a transformation.

### Game (`src/game/`)

- `boss_kit`: `part(..., {"reveal": K})`, a `transforms` override, `reveal` record with `style` and the
  armour plates (for `armour`) or folds (for `unfold`).
- `world_boss.py`: patterns include every part's volleys; hidden parts give no source until revealed
  (as destroyed ones do now). `on_transform` throws armour debris.
- `boss_build.boss_stats`: default thresholds from the tier (mini / final) and the number of original
  parts.

### Reveal styles (view)

- **`armour`** (mechanical bosses): armour plates are their own meshes over the hidden weapons. At the
  transformation they break off as debris: thrown outward, spinning, falling, gone after about 1.5 s
  (existing blast / debris code). The weapons beneath rise slightly and their trim lights up.
- **`unfold`** (organic / jointed bosses): hidden weapons sit folded into the hull (scaled down,
  rotated in about a pivot, trim dark) and swing out with `transform` progress, using the existing limb
  / joint helpers.
- The view reads `boss.form` and `boss.transform`; nothing in `core/` knows about plates or folds.

### Content (all 40 bosses)

- Mini bosses: 1 transformation; final bosses: 2. Each reveals 1–3 weapon parts.
- Weapon parts reuse the existing part kits (`mini_boss_shapes`, `final_boss_shapes`, `overlord_parts`,
  world kits), with guns, muzzles and volleys.
- Revealed volleys use patterns new to that boss (missiles, lasers, aimed fans, rings), in the world's
  bullet colours.
- Health tuned so that a fight lasts about 20–30 % longer than today.
- Each boss picks `armour` or `unfold` to fit its model.

### Difficulty guard

A config test, for every boss: the live fire rate (bullets per second from the sources live at that
moment: core plus intact, revealed parts) at the fight's start, and just after each transformation
(assuming the triggering parts were the first original parts destroyed). Each must be ≥ the one before.
Also checked: tier → number of transformations, each transformation reveals 1–3 parts, every revealed
part has guns and at least one volley, budgets hold.

## Testing

- Unit (`tests/unit`): `edge_trim` (silhouette edges of simple solids, ribbon widths, open edges);
  boss transformation (thresholds, hidden parts not targetable / not firing, invulnerable while
  transforming, queued transformations, health bar constant, `break_next`, `on_transform` called);
  config checks above; models' triangle budgets with trim.
- e2e: readability contrast tests (unchanged thresholds) without the rim; per world, a boss test
  uses `break_next` to trigger a transformation and checks new parts appear and fire.
- Verification during the work: `make typecheck build e2e` only (CLAUDE.md); `make check` at
  validation.

## Work order (one commit or more each)

1. `edge_trim` helper and tests.
2. Player ships: trim, rim removed; readability e2e.
3. Enemies and bosses: trim, rim removed; `OutlineLayer` removed if unused.
4. Core transformation mechanics and tests.
5. View: reveal styles.
6. Boss content, one world per commit (World 1 first), with the difficulty guard.
7. `DECISIONS.md`: trim as P14's rim light; transformation rules; GD-46's "attack pattern changes" now
   including reveals.

## Out of scope

- Detail lights (panel seams, vents) beyond the trim.
- Re-tuning regular enemies' difficulty.
- Changing the enemy missiles' rim.
