# Copyright (c) 2026 Renaud Guillon
"""Whether a boss model holds together as one object (BOSS-52, D-254).

At rest and after each of its transformations: its core, the armour still on, the pieces of the
regions that move (BOSS-45) as they rest or once moved, the frames of the regions shed, the parts
standing (with their turrets) and the hidden weapons revealed (with what slides out of them). The
game draws no stem or pylon of its own any more: the drawings must hold together as drawn.
"""

from typing import Any

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.moving_regions import is_moving, motion_value, move_point
from game.config.record import record
from game.view.bosses.boss_armour import (
    LAYERS,
    all_triangles,
    drawn_layers,
    most_pieces,
    region_drawing,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import _part_builder
from game.view.bosses.boss_models import BOSS_MODELS
from game.view.bosses.hidden_weapon_shapes import weapon_drawing, weapon_slides
from game.view.bosses.region_motion import to_config, to_model
from helpers.islands import bounds_of, loose_triangles, pieces
from helpers.view_probes import probe_builder
from render.geometry.mesh_triangles import Vertex

NEON = [1.0, 0.0, 1.0]


def moved_triangles(tris: list[Any], motion: Any, value: Any) -> list[Any]:
    """`tris` (model space) moved by `value` of `motion` from the pose as drawn."""
    return [
        [Vertex(to_model(move_point(motion, value, to_config(v.position))), v.color) for v in tri]
        for tri in tris
    ]


def posed(tris: list[Any], region: Any, form: int) -> list[Any]:
    """`tris` (model space) as `region` rests, or moved once a boss has done `form` transformations.

    A region that does not move is left as drawn.
    """
    if not is_moving(region):
        return tris
    return moved_triangles(
        tris, region.motion, motion_value(region.motion, 1 if form >= region.form else 0)
    )


def _drawn(draw: Any) -> list[Any]:
    return all_triangles(drawn_layers(draw))


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


def _core_triangles(drawing: Any) -> list[Any]:
    """Return the core as drawn, and its ring."""
    core = _drawn(drawing.core)
    if drawing.get("ring") is not None:
        core.extend(_drawn(drawing["ring"]))
    return core


def _last_form(design: Any) -> int:
    """Return the highest form at which a part is revealed (0 when none is)."""
    forms = 0
    for spec in design.stats.parts:
        if spec.get("reveal") is not None:
            forms = max(forms, spec["reveal"])
    return forms


def _gone_by_form(design: Any, forms: int) -> list[set[str]]:
    """Return the ids of the parts destroyed before each form (D-228's `transformParts`)."""
    gone: list[set[str]] = [set()]
    for ids in design.get("transformParts") or []:
        gone.append(gone[-1] | set(ids))
    while len(gone) <= forms:
        gone.append(gone[-1])
    return gone


def region_drawings(design: Any, drawing: Any) -> list[Any]:
    """Return how each armour region of `design` is drawn by `drawing` (None when it is not)."""
    regions = design.get("armour") or []
    if len(regions) == 0:
        return []
    armour = drawing.get("armour")
    most = most_pieces(regions)
    return [region_drawing(armour, region, NEON, most) for region in regions]


def _armour_triangles(design: Any, drawn: list[Any], form: int) -> list[Any]:
    """Return the regions still on or moved into their new pose, and the shed regions' frames."""
    tris: list[Any] = []
    for k, region in enumerate(design.armour):
        if drawn[k] is None:
            continue
        if region.form is None:
            # A hatch over a gun mount (BOSS-58): it bursts as its gun first comes into use, at a
            # stage, not a transformation; drawn on.
            tris.extend(_drawn(drawn[k].whole))
            continue
        if region.form > form or is_moving(region):
            # On still, or moved into its new pose (BOSS-45).
            tris.extend(posed(_drawn(drawn[k].whole), region, form))
        if region.form <= form and drawn[k].frame is not None:
            for frame in drawn[k].frame:
                tris.extend(_drawn(frame))
    return tris


def _part_shown(spec: Any, form: int, gone: set[str]) -> bool:
    """Whether a part stands at `form`: not a joint or an orbit, revealed and not yet retired."""
    if spec.get("joint") is not None or spec.get("orbits"):
        return False
    reveal = spec.get("reveal")
    if reveal is not None and reveal > form:
        return False
    retire = spec.get("retire")
    if retire is not None and retire <= form:
        return False
    # Destroyed for its transformation to come (D-228's `transformParts`).
    return spec["id"] not in gone


def _parts_triangles(design: Any, drawing: Any, gone: set[str], form: int) -> list[Any]:
    """Return the parts standing at `form`, with their turrets."""
    tris: list[Any] = []
    for spec in design.stats.parts:
        if _part_shown(spec, form, gone):
            tris.extend(_part_tris(design, drawing, spec))
    return tris


def boss_drawing(boss_id: str, monkeypatch: Any) -> Any:
    """Return the drawing of a boss model, as a record."""
    return record(probe_builder(monkeypatch, BOSS_MODELS[boss_id]).drawing)


def boss_states(boss_id: str, design: Any, monkeypatch: Any) -> list[list[Any]]:
    """Return the triangles of the boss model at rest and after each transformation."""
    drawing = boss_drawing(boss_id, monkeypatch)
    core = _core_triangles(drawing)
    drawn = region_drawings(design, drawing)
    forms = _last_form(design)
    gone = _gone_by_form(design, forms)
    rig = drawing.get("rig")
    states: list[list[Any]] = []
    for form in range(forms + 1):
        tris = list(core)
        if rig is not None and rig.get("triangles") is not None:
            # Its rig (D-228), unfolded from the first transformation on. A rig that only moves
            # pieces as the boss transforms (the Storm Petrel's battery struts) draws none at rest.
            tris.extend(rig.triangles(1 if form >= 1 else 0))
        tris.extend(_armour_triangles(design, drawn, form))
        tris.extend(_parts_triangles(design, drawing, gone[form], form))
        states.append(tris)
    return states


def loose_pieces(tris: list[Any], least: float) -> list[list[float]]:
    """Return the bounds of the pieces of `tris` not held to the rest.

    Only those at least `least` px across.
    """
    loose = loose_triangles(tris, BOSS_LOOK.armour.hold)
    hanging = [tris[i] for i in range(len(tris)) if loose[i]]
    result: list[list[float]] = []
    for piece in pieces(hanging):
        b = bounds_of([hanging[i] for i in piece])
        if max(b[3] - b[0], b[4] - b[1], b[5] - b[2]) >= least:
            result.append(b)
    return result


__all__ = ["LAYERS", "boss_drawing", "boss_states", "loose_pieces", "moved_triangles", "posed"]
