# Edge trim

> **Area:** Graphics · **Prefix:** `GFX-TRIM` · **Related:** [readability.md](readability.md), [art-direction.md](art-direction.md), [player-ships.md](player-ships.md), [shots.md](shots.md), [../enemies/common.md](../enemies/common.md), [../bosses/common.md](../bosses/common.md)

Every enemy and boss has a glowing edge trim built into its geometry (the player ship had one
until D-335; its edges glow instead, [GFX-SHIP-09](player-ships.md)): thin self-lit
ribbons just outside the edges the model shows from above. It is the "rim light" that makes the
ship and the enemies stand out from the ground ([GFX-READ](readability.md)). It replaced, at the
reviewer's request, the rim outline that drew each mesh a second time, fatter. Shots get no trim:
the enemy missiles keep that rim outline ([GFX-SHOT](shots.md)).

## Requirements

### GFX-TRIM-01 — A glowing trim built into every enemy and boss · MUST

Each enemy and boss model gets a self-lit trim as part of its own geometry, along its
silhouette seen from above. It is their rim light (GFX-READ-07, GFX-READ-09). No ship, enemy or boss
mesh is drawn a second time as an outline.

**Acceptance criteria**
- Given the player ship model, then it is built with no trim (D-335, unit test).
- Given each enemy and boss model, then it is built with a trim in its rim colour.
- Given a level in play, then no ship, enemy or boss mesh has Babylon's outline turned on.

*Sources: D-220, P14-R03, P14-R04, D-123.*

### GFX-TRIM-02 — Traced along the top-view silhouette · SHOULD

An edge is traced when it borders exactly one up-facing triangle (the Y of its unit normal at least
`min_up`), where no up-facing triangle of the same trim group lies just outside it, seen from
above: it is probed at several points along it, and only its covered parts are left out (D-330: a
whole edge was dropped when its middle was covered, leaving gaps where a fin or a wing crossed a
hull's edge). Seen from above, these edges stay the silhouette however the model turns about the vertical
axis (enemies and bosses do nothing else), and the 35° playfield camera is close enough to that.
Vertices are matched by position, so flat-shaded solids (each face its own vertices) and meshes with
shared vertices give the same edges.

**Acceptance criteria**
- Given a box, then its four top edges are traced, each with its outward direction (unit test).
- Given two boxes side by side in one group, then the edges they share are not traced (unit test).
- Given an edge half covered by another part, then its other half is still traced (unit test).
- Given the same solid with shared and with per-face vertices, then the same edges are traced (unit
  test).

*Sources: D-220.*

### GFX-TRIM-03 — Thin ribbons just outside the edges · SHOULD

Along each traced edge the trim is a flat ribbon facing up, `width` wide, set `offset` out from the
edge. A run of edges turning by less than about 15° is drawn as one ribbon; where two ribbons turn
by more than about 20°, a wedge fills the corner. A ribbon costs two triangles. A mirrored mesh
still gets its trim outside.

**Acceptance criteria**
- Given a traced edge, then its ribbon lies outside the edge and faces up (unit test).
- Given a straight run of edges, then it is one ribbon without a corner; given a curved outline,
  then it is drawn with fewer ribbons than edges (unit tests).

*Sources: D-220.*

### GFX-TRIM-04 — The trim is part of its mesh · MUST

Each mesh that asks for a trim gets one child mesh holding its ribbons, so the trim moves, turns,
blinks and hides with its mesh: a blinking ship blinks with its trim, a hidden boss part hides its
trim. Only solid meshes ask for a trim: added-on, see-through or vertex-alpha meshes (flames, glows)
get none.

**Acceptance criteria**
- Given a trimmed mesh, then its trim is its child (unit test).
- Given a flame or glow mesh of a model, then it gets no trim (unit test).
- Given an enemy or boss hit and flashing, then its trim flashes with it.

*Sources: D-220, P14-R03.*

### GFX-TRIM-05 — (removed) Player ship trim

The player ship has no trim since D-335 (owner, 2026-11-11: "remove the highlight as an outter
layer for the player's ship, instead make it look like it's the extremities of the wings and
cockpit that are glowing, no highlight on the guns"): its wings', canards' and canopy's edges glow
instead (GFX-SHIP-09). Until then it was a soft cyan ribbon round its silhouette (D-220, D-327).

*Sources: D-220, P14-R03, D-327, D-335.*

### GFX-TRIM-06 — Enemy and boss trim · MUST

An enemy's or boss's trim takes its neon colour (after GFX-ART-05, so bright yellow or bright green)
`enemyTrim.whiten` of the way to white, times `enemyTrim.strength`. It is `enemyTrim.width` wide and
set `enemyTrim.offset` out, in logical pixels. Its hull and flesh meshes ask for it.

**Acceptance criteria**
- Given an enemy's neon, then its rim colour is that neon lifted towards white by `whiten` and
  multiplied by `strength` (unit test).
- Given the enemy model factories, then they trim with the enemy trim's width and offset (unit
  test).

*Sources: D-220, D-231, P14-R04, D-123.*

### GFX-TRIM-07 — The trim is a light · SHOULD

The trim is unlit and drawn from both sides, with one material per colour and scene. The level's
haze does not dim it (no fog), and the enemy strength goes above 1 so the scene's tone mapping does
not dim it below the contrast GFX-READ-09 asks for. It blooms in the playfield's glow layer.

**Acceptance criteria**
- Given two meshes trimmed in the same colour in one scene, then they share one material (unit
  test).
- Given a trim mesh, then fog does not apply to it.

*Sources: D-220.*

### GFX-TRIM-08 — Trim groups for destroyable boss parts · MUST

A boss's destroyable part is a trim group of its own: its meshes are trimmed along their own
silhouette, as if the rest of the boss were not there, so each part keeps its whole outline wherever
it sits on the hull and the player sees which parts can still be hit. The rest of a model's meshes
hide each other's inner edges.

**Acceptance criteria**
- Given a boss part over the hull, then its whole outline is trimmed, edges over the hull included
  (unit test on trim groups).

*Sources: D-220, P14-R04.*

### GFX-TRIM-09 — Pieces that ask for no trim · SHOULD

A piece of a model may ask for no trim, or take back its requests: e.g. the armour a boss sheds as
it transforms and the ribs of the frame it leaves (the frame's floor is its own trim group, so the
frame reads as dark metal with a glowing outline).

**Acceptance criteria**
- Given a mesh whose trim request was taken back, then it gets no trim (unit test).

*Sources: D-220.*

### GFX-TRIM-10 — A game-agnostic trim builder · SHOULD

The silhouette and ribbon maths is a pure engine module, unit-tested without Babylon. The engine
wiring gives each requesting mesh its trim mesh; the game only sets the colours, widths and offsets
and asks for the trims.

**Acceptance criteria**
- Given the pure trim module, then it runs under the unit tests without a WebGL context.

*Sources: D-220.*

## Tunable values

All in `src/game/config/readability.py` `READABILITY`, sizes in logical pixels.

| Name | Value | Notes |
|------|-------|-------|
| `enemyTrim.whiten` | 0.25 | share of the way to white |
| `enemyTrim.strength` | 2.6 | above 1: survives tone mapping |
| `enemyTrim.width` / `offset` | 1.4 / 0.1 | |
| `min_up` | 0.2 | `src/render/geometry/edge_trim.py` `TrimOptions` |
| Merge / corner angles | about 15° / 20° | `edge_trim.py` `_MERGE` 0.966, `_STRAIGHT` 0.94 (cosines) |

## Notes

- With 0.5 / 1 for `whiten` / `strength`, the World 1-1 Hornets measured 2.1 to 2.4:1 against the
  clouds (3:1 needed); with 0.25 / 2.6 all four worlds pass.
- Cost: the trim adds 16 to 180 triangles to an enemy (measured on the old roster: Gnat 390 → 486,
  Spinner 336 → 516, Hornet 296 → 375). D-220 left open for the reviewer whether the tier budgets
  of ENM-03 (400 for tier 1) count the trim (8 of the 11 old basic kinds went over with it, up to
  the Spinner's 516; to be measured again with the four tiers). The rim
  outline it replaced cost more on the GPU but was not geometry. No unit test checks the budgets
  since the Python port.
- D-220's status is "Proposed"; it records a reviewer request.
