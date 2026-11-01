"""Whether a boss model holds together as one object (D-227), at rest and after each of its
transformations: its core (what the armour cut leaves), the armour still on, the pieces of the
regions that move (D-230) as they rest or once moved, the frames of the regions shed (with their
pylons), the parts standing (with their turrets) and the hidden weapons revealed (with what slides
out of them)."""

from typing import Any

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.moving_regions import is_moving
from game.config.record import record
from game.view.bosses.boss_armour import (
    LAYERS,
    cut_armour,
    lasting_surfaces,
    rooted,
    supports_in,
)
from game.view.bosses.boss_frame import frame_drawings
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import _part_builder, part_supports, rest_stems
from game.view.bosses.boss_models import BOSS_MODELS
from game.view.bosses.boss_stems import stems_drawing
from game.view.bosses.hidden_weapon_shapes import weapon_drawing, weapon_slides
from game.view.bosses.region_motion import posed
from game.view.enemies.enemy_mesh import collect_parts
from helpers.view_probes import probe_builder
from render.geometry.islands import bounds_of, loose_triangles, pieces
from render.geometry.shatter import triangles

NEON = [1.0, 0.0, 1.0]


def _drawn(draw: Any) -> list[Any]:
    parts = collect_parts(draw)["parts"]
    result: list[Any] = []
    for layer in LAYERS:
        result.extend(triangles(getattr(parts, layer).geometry))
    return result


def _field(obj: Any, key: str) -> Any:
    if obj is None:
        return None
    return obj.get(key) if hasattr(obj, "get") else getattr(obj, key, None)


def _part_tris(design: Any, drawing: Any, spec: Any) -> list[Any]:
    at = boss_point(spec.x, spec.y)
    weapon = _field(_field(design, "weapons"), spec.id)
    draw = _field(drawing.get("parts"), spec.id)
    if draw is None and weapon is not None:
        draw = weapon_drawing(weapon, NEON)
    result = _drawn(_part_builder(draw, at)) if draw is not None else []
    # Turrets turn on top of their part (some drawings read object literals CPython cannot run):
    # the part itself stands for them here.
    if weapon is not None:
        for slide in weapon_slides(weapon, NEON):
            result.extend(_drawn(_part_builder(slide[0], at)))
    return result


def _initial_core(design: Any, drawing: Any, cut: Any) -> list[Any]:
    """The triangles of the boss at rest: the core's kept parts, the armour still on, the ring and
    the stems holding the loose pieces (D-227)."""
    core: list[Any] = []
    for layer in LAYERS:
        core.extend(cut.kept[layer])
        core.extend(cut.floating.get(layer, []))
    if drawing.get("ring") is not None:
        core.extend(_drawn(drawing["ring"]))
    # The stems holding its loose pieces, on its core (D-227).
    core.extend(_drawn(stems_drawing(rest_stems(design, drawing, cut, NEON), NEON)))
    return core


def _reveal_count(design: Any) -> int:
    """The most transformations a boss has: the highest `reveal` of its parts (D-227)."""
    forms = 0
    for spec in design.stats.parts:
        if spec.get("reveal") is not None:
            forms = max(forms, spec["reveal"])
    return forms


def _destroyed_by(design: Any, forms: int) -> list[set[str]]:
    """The sets of part ids destroyed by each transformation (D-228's `transformParts`)."""
    named = design.get("transformParts") or []
    gone: list[set[str]] = [set()]
    for ids in named:
        gone.append(gone[-1] | set(ids))
    while len(gone) <= forms:
        gone.append(gone[-1])
    return gone


def _region_tris(design: Any, cut: Any, supports: list[Any], form: int) -> list[Any]:
    """The armour regions' triangles at `form`: the pose when the region is on or moving (D-230),
    else the frame drawings when it is held."""
    tris: list[Any] = []
    for k, region in enumerate(design.armour):
        layers = cut.regions[k]
        if region.form > form or is_moving(region):
            # On still, or moved into its new pose (D-230).
            for layer in LAYERS:
                tris.extend(posed(layers[layer], region, form))
        if region.form > form or region.frame is None:
            continue
        held = supports_in(region, supports)
        drawings = frame_drawings(
            cut.frames[k], region.frame, NEON, held, cut.floors[k], cut.bridges[k]
        )
        tris.extend(_drawn(drawings[0]))
        tris.extend(_drawn(drawings[1]))
    return tris


def _part_tris_at(design: Any, drawing: Any, form: int, gone: list[set[str]]) -> list[Any]:
    """The triangles of the parts alive at `form`: hidden ones appear with their reveal, retired
    ones leave at their retirement, and the destroyed ones are out (D-228)."""
    tris: list[Any] = []
    for spec in design.stats.parts:
        if spec.get("joint") is not None or spec.get("orbits"):
            continue
        reveal = spec.get("reveal")
        if reveal is not None and reveal > form:
            continue
        retire = spec.get("retire")
        if retire is not None and retire <= form:
            continue
        if spec["id"] in gone[form]:
            # Destroyed for its transformation to come (D-228's `transformParts`).
            continue
        tris.extend(_part_tris(design, drawing, spec))
    return tris


def boss_states(boss_id: str, design: Any, monkeypatch: Any) -> list[list[Any]]:
    """The triangles of the boss model at rest and after each transformation."""
    capture = probe_builder(monkeypatch, BOSS_MODELS[boss_id])
    drawing = record(capture.drawing)
    regions = design.armour
    cut = cut_armour(drawing.core, regions)
    core = _initial_core(design, drawing, cut)
    supports = rooted(part_supports(design, drawing, NEON), lasting_surfaces(cut))
    forms = _reveal_count(design)
    rig = drawing.get("rig")
    gone = _destroyed_by(design, forms)
    states: list[list[Any]] = []
    for form in range(forms + 1):
        tris = list(core)
        if rig is not None:
            # Its rig (D-228), unfolded from the first transformation on.
            tris.extend(rig.triangles(1 if form >= 1 else 0))
        tris.extend(_region_tris(design, cut, supports, form))
        tris.extend(_part_tris_at(design, drawing, form, gone))
        states.append(tris)
    return states


def loose_pieces(tris: list[Any], least: float) -> list[list[float]]:
    """The bounds of the pieces of `tris` not held to the rest, at least `least` px across."""
    loose = loose_triangles(tris, BOSS_LOOK.armour.hold)
    hanging = [tris[i] for i in range(len(tris)) if loose[i]]
    result: list[list[float]] = []
    for piece in pieces(hanging):
        b = bounds_of([hanging[i] for i in piece])
        if max(b[3] - b[0], b[4] - b[1], b[5] - b[2]) >= least:
            result.append(b)
    return result
