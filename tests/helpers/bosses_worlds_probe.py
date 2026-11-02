# Copyright (c) 2026 Renaud Guillon
"""Helpers of the World 2 to 4 boss model tests (`tests/unit/game/view/bosses/world_N/`).

`turret_drawings` runs a boss's turret drawings at their pivots, as `boss_model.build_turret` does
in the browser (the shared `drawings_of` draws the body, ring, limbs and parts only).
`fresh_copy` runs a module's source again under a private name, so that a test can see the values
it computes at import time from a patched config (the original module is left as it is).
`geometry_size` counts the vertices a drawing made, and `drawn_at` draws one part function.
"""

import importlib.util
from collections.abc import Callable
from types import ModuleType
from typing import Any

from game.config.record import record
from game.view.bosses.boss_limbs import boss_point
from helpers.view_probes import drawn


def turret_point(design: Any, piece: str) -> list[Any]:
    """Return the model-space pivot of `piece`'s turret (`bossPoint(...gun.turret)`)."""
    spot = design.guns[piece].turret
    if len(spot) > 2:
        return boss_point(spot[0], spot[1], spot[2])
    return boss_point(spot[0], spot[1])


def design_muzzles(design: Any, piece: str, kind: str) -> list[list[Any]]:
    """Return the model-space muzzles of kind `kind` (`gun`, `laser`, `ring`...) of `piece`."""
    return [boss_point(m[0], m[1], m[2]) for m in design.guns[piece][kind]]


def turret_drawings(capture: Any) -> dict[str, dict[str, Any]]:
    """Run every turret drawing of a boss capture on real solid builders, keyed by its piece.

    Each drawing is handed its turret's pivot, as `boss_model.build_turret` does.
    """
    drawing = record(capture.drawing)
    out: dict[str, dict[str, Any]] = {}
    for piece, draw in (drawing.get("turrets") or {}).items():
        at = turret_point(capture.design, piece)
        out[piece] = drawn(lambda p, d=draw, a=at: d(p, a))
    return out


def drawn_at(draw: Callable[[Any, Any], None], at: list[float]) -> dict[str, Any]:
    """Run the part drawing `draw(parts, at)` on real solid builders."""
    return drawn(lambda p: draw(p, at))


def geometry_size(result: dict[str, Any]) -> int:
    """Return how many vertex coordinates a drawing made, over all its builders."""
    parts = result["parts"]
    return sum(
        len(builder.geometry.positions)
        for builder in (parts.hull, parts.flesh, parts.vein, parts.neon, parts.charge)
    )


def muzzle_kinds(result: dict[str, Any]) -> list[str]:
    """Return the kinds of the muzzles a drawing marked, in order."""
    return [kind for _at, kind in result["muzzles"]]


def fresh_copy(module: ModuleType) -> ModuleType:
    """Run `module`'s source again as a new module (not registered in `sys.modules`).

    Its import-time values are computed from the config as it is now (patch it first).
    """
    spec = importlib.util.spec_from_file_location(module.__name__ + "_fresh", module.__file__)
    if spec is None or spec.loader is None:
        msg = "cannot load " + module.__name__
        raise ImportError(msg)
    copy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(copy)
    return copy
