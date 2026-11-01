"""Whether a boss model holds together as one object (BOSS-52, D-227), at rest and after each of its
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


def _core_triangles(design: Any, drawing: Any, cut: Any) -> list[Any]:
    """The core left by the armour cut, its ring, and the stems holding its loose pieces."""
    core: list[Any] = []
    for layer in LAYERS:
        core.extend(cut.kept[layer])
        core.extend(cut.floating.get(layer, []))
    if drawing.get("ring") is not None:
        core.extend(_drawn(drawing["ring"]))
    # The stems holding its loose pieces, on its core (D-227).
    core.extend(_drawn(stems_drawing(rest_stems(design, drawing, cut, NEON), NEON)))
    return core


def _last_form(design: Any) -> int:
    """The highest form at which a part is revealed (0 when none is)."""
    forms = 0
    for spec in design.stats.parts:
        if spec.get("reveal") is not None:
            forms = max(forms, spec["reveal"])
    return forms


def _gone_by_form(design: Any, forms: int) -> list[set[str]]:
    """The ids of the parts destroyed before each form (D-228's `transformParts`)."""
    gone: list[set[str]] = [set()]
    for ids in design.get("transformParts") or []:
        gone.append(gone[-1] | set(ids))
    while len(gone) <= forms:
        gone.append(gone[-1])
    return gone


def _armour_triangles(design: Any, cut: Any, supports: Any, form: int) -> list[Any]:
    """The regions still on or moved into their new pose, and the frames of the regions shed."""
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
    """The parts standing at `form`, with their turrets."""
    tris: list[Any] = []
    for spec in design.stats.parts:
        if _part_shown(spec, form, gone):
            tris.extend(_part_tris(design, drawing, spec))
    return tris


def boss_states(boss_id: str, design: Any, monkeypatch: Any) -> list[list[Any]]:
    """The triangles of the boss model at rest and after each transformation."""
    capture = probe_builder(monkeypatch, BOSS_MODELS[boss_id])
    drawing = record(capture.drawing)
    cut = cut_armour(drawing.core, design.armour)
    core = _core_triangles(design, drawing, cut)
    supports = rooted(part_supports(design, drawing, NEON), lasting_surfaces(cut))
    forms = _last_form(design)
    gone = _gone_by_form(design, forms)
    rig = drawing.get("rig")
    states: list[list[Any]] = []
    for form in range(forms + 1):
        tris = list(core)
        if rig is not None:
            # Its rig (D-228), unfolded from the first transformation on.
            tris.extend(rig.triangles(1 if form >= 1 else 0))
        tris.extend(_armour_triangles(design, cut, supports, form))
        tris.extend(_parts_triangles(design, drawing, gone[form], form))
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
