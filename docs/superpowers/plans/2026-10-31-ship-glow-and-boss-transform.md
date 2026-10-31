# Ship glow trim and boss transformations — implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans (reviewer chose to start
> coding directly: native execution). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** replace the rim outline of every ship by self-lit edge trim built into the geometry, and make
bosses reveal new weapon parts as they lose parts.

**Architecture:** a pure geometry helper computes top-view silhouette edges and ribbons; a Babylon glue
adds one trim mesh per solid mesh of a model. Bosses get hidden parts (`reveal: K`) and a
`"transforming"` state in `core/`; the game configs list hidden parts and reveal styles; the boss view
animates armour drops / unfolds.

**Tech stack:** Python (Transcrypt → JS), Babylon.js, pytest (CPython over `src/`), Playwright e2e.

**Spec:** `docs/superpowers/specs/2026-10-31-ship-glow-and-boss-transform-design.md`

## Global constraints

- `core/` stays pure (no Babylon, no DOM); code outside `src/game/` stays game-agnostic.
- Transcrypt subset: no keyword arguments at call sites of project functions, typing under
  `__pragma__("skip")`, `== None` for JS undefined where the codebase does it.
- Verification while coding: `make typecheck build e2e` only. Never lower thresholds.
- Triangle budgets (P16-R09): basic 400, veteran 700, elite 1200, mini boss 4000, final boss 10000.
- Geometry convention: Y up, playfield plane XZ; flat-shaded faces own their vertices; Babylon front
  face normal of triangle (i0, i1, i2) is `(p2 - p0) × (p1 - p0)`.

## Review focus

1. Meshes with shared vertices (Babylon `MeshBuilder` lathes) and meshes with per-face vertices must
   both give a closed trim: edges are matched by quantised position, not index.
2. Interior edges (a wing under the fuselage) must not light up: coverage test against the model's
   other up-facing triangles (spatial grid) in root space.
3. Mirrored / negatively scaled nodes (`mirror_x`): outward direction must still point out.
4. Several thresholds crossed in one step (bomb, `break_next`): transformations queue.
5. Boss dying while transforming or with hidden parts: hidden parts never become targets, death
   blasts unaffected.

---

### Task 1: `edge_trim` geometry helper

**Files:** create `src/render/geometry/edge_trim.py`; test `tests/unit/render/geometry/test_edge_trim.py`

**Produces:**
- `TrimOptions(width: float, offset: float, min_up: float = 0.2)`
- `silhouette_edges(positions: list[float], indices: list[int], cover: list[list[Vec3]] | None, min_up: float) -> list[TrimEdge]`
  — `TrimEdge(a: Vec3, b: Vec3, out: Vec3)` (out: unit horizontal vector away from the shape).
  Candidate = edge of an up-facing triangle (normal.y ≥ `min_up`) not shared with another up-facing
  triangle; dropped when the point `mid + out * eps` lies inside any triangle of `cover` projected on
  XZ (cover defaults to the up-facing triangles themselves).
- `trim_ribbons(edges: list[TrimEdge], options: TrimOptions) -> ColoredGeometry` — per edge a quad
  from `a + out*offset` / `b + out*offset` to `+ out*(offset+width)`, at the edge's heights, white
  vertex colours, plus a corner triangle joining consecutive ribbons sharing an endpoint.

Tests: a box → 4 edges, all `out` pointing away from centre, ribbons 8 tris + corners; two boxes, one
on top of the other smaller → only the bottom box's outer edges and the top box's; a box with shared
vertices gives the same as per-face vertices; a flat open quad (single face) gives 4 edges.

### Task 2: Babylon glue and player ships

**Files:** create `src/render/edge_trim_mesh.py`; modify `src/game/view/readability_view.py`
(`outlined_ships` → `trimmed_ships`), `src/game/config/readability.py` (`playerTrim`: color, width,
offset); tests `tests/unit/render/test_edge_trim_mesh.py`, update `test_readability_view.py`.

**Produces:** `add_edge_trim(root: Any, color: Rgb, options: TrimOptions, name: str) -> list[Any]` —
for each solid mesh under `root` (`outline._is_solid` rule moved here as `is_solid`), reads its
positions / indices, builds edges in root space with the cover of all solid meshes, transforms ribbons
back to the mesh's local space, makes a child mesh with an unlit emissive material of `color`
(`backFaceCulling = False`, cached per scene and colour). Returns the trim meshes.

Steps: test with babylon stub (a root with one box mesh → one child trim mesh, emissive = colour);
implement; swap player ships to trim; run `make typecheck build e2e` (readability test must pass).

### Task 3: enemies and bosses trimmed, rim removed

**Files:** modify `src/game/view/enemies/enemy_mesh.py` (`add_surfaces`: no `set_outline`),
`build_enemy_model` caller adds `add_edge_trim(root, rim_of(neon) colour family, ENEMY_LOOK trim)`;
`src/game/config/enemy_look.py` (`trim`: width, offset per tier); `app/level_scene.py` (drop
`OutlineLayer` for ships; keep for missiles only if still used); tests updated
(`enemy-readability`, budgets).

Budget test: every enemy and boss model built with the stub, triangles (trim included) ≤ tier budget.

### Task 4: core transformation mechanics

**Files:** modify `src/core/entities/boss.py`, `src/core/entities/boss_pieces.py`; tests
`tests/unit/core/entities/test_boss_transform.py`.

**Produces:**
- `BossPartSpec(..., joint=None, reveal: int | None = None)`; `BossPart.hidden: bool`
  (`reveal is not None and boss.form < reveal`).
- `BossStats(..., joints=None, transforms: list[int] | None = None, transform_seconds: float = 1.5)`.
- `Boss.form: int` (transformations done), `Boss.transform: float` (0..1 progress, 0 when not
  transforming), state `"transforming"`, optional hook `on_transform(k: int, ctx)` called when
  transformation k (1-based) starts.
- Hidden parts: not in targets, `core_shielded` ignores them, `_source` none (game side), not
  counted by the thresholds; `break_next` skips them.

Tests: thresholds [2] with 4 original parts → transforming after the 2nd break; not vulnerable while
transforming; after `transform_seconds` hidden parts targetable; two thresholds crossed at once →
two transformations in a row; `full_health` constant across a transformation; dying while
transforming works; `on_transform` called with 1 then 2.

### Task 5: game wiring and view reveal styles

**Files:** `src/game/sim/boss_build.py` (`_part_spec` reads `reveal`; `boss_stats` sets
`transforms` default by tier: mini ⌈n/2⌉, final ⌈n/3⌉ and ⌈2n/3⌉ of original parts, override with
design `transforms`), `src/game/sim/bosses/world_boss.py` (`_source` none for hidden parts, turrets
not turned; `on_transform` → debris), `src/game/config/bosses/boss_kit.py` (`part(..., {"reveal": K})`,
`reveal` record `{"style": "armour"|"unfold", "plates": {...}}`), `src/game/view/bosses/boss_model.py`
and new `src/game/view/bosses/boss_reveal.py` (armour plates as meshes that fly off with
`boss.transform`; unfold: hidden part roots scaled 0.3→1 and rotated in about their pivot by
`boss.transform`, disabled before their form).

Tests: `boss_build` defaults per tier; `world_boss` hidden part fires nothing until revealed;
`boss_reveal` plate pose at transform 0 / 1, unfold scale at 0 / 1.

### Task 6–9: boss content, one world per task (World 1 first, then 2, 3, 4)

For each boss of the world: 1 (mini) or 2 (final) transformations, 1–3 hidden parts each, drawn with
the existing part kits, guns + volleys new to that boss, style chosen per model, health so fights
last ~20–30 % longer. Test (`tests/unit/game/config/test_boss_transforms.py`, parametrised over all
bosses): transformations count by tier; each reveal 1–3 parts with guns and ≥ 1 volley; fire rate at
start ≤ after transformation 1 ≤ after 2 (bullets/s from live sources, triggering parts taken as the
first original parts). e2e per world: `break_next` until a transformation, then a new part is a target.

### Task 10: decisions and wrap-up

`specs/DECISIONS.md` entries (trim as P14 rim light; transformation rules / GD-46), `make typecheck
build e2e`, commit.
