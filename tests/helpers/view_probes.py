"""Stand-ins for the view's geometry builders, so the model code runs under CPython with no
Babylon: a recorder logs every call made on it (`rec.hull.cylinder(...)` is logged as
`("hull.cylinder", args, kwargs)`), and `probe_builder` captures what a model builder hands to
`build_enemy_model` / `build_boss_model` (its name, colour and drawing), with no scene built."""

import sys
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock

from game.config.record import record
from game.view.bosses.boss_limbs import boss_point
from game.view.enemies.enemy_mesh import collect_parts


class _Call:
    """A path of attribute accesses on a recorder; calling it records the call."""

    def __init__(self, path: str, log: list[tuple[str, tuple[Any, ...], dict[str, Any]]]) -> None:
        self._path = path
        self._log = log

    def __getattr__(self, name: str) -> "_Call":
        if name.startswith("__"):
            raise AttributeError(name)
        return _Call(f"{self._path}.{name}" if self._path else name, self._log)

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        self._log.append((self._path, args, kwargs))


def recorder() -> tuple[Any, list[tuple[str, tuple[Any, ...], dict[str, Any]]]]:
    """A recording stand-in for a builder, and its call log (`(path, args, kwargs)` triples)."""
    log: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []
    return _Call("", log), log


def paths(log: list[tuple[str, tuple[Any, ...], dict[str, Any]]]) -> list[str]:
    """The paths of the calls in `log`, in order."""
    return [path for path, _args, _kwargs in log]


@dataclass
class EnemyCapture:
    """What an enemy model builder asked `build_enemy_model` for."""

    name: str
    neon: list[float]
    draw: Callable[[Any], None]


@dataclass
class BossCapture:
    """What a boss model builder asked `build_boss_model` for."""

    design: Any
    neon: list[float]
    drawing: dict[str, Any]


@dataclass
class JointedCapture:
    """What a jointed enemy builder asked `build_jointed_model` for: its design and drawing."""

    name: str
    neon: list[float]
    design: Any
    drawing: dict[str, Any]


def probe_builder(monkeypatch: Any, builder: Callable[..., Any]) -> Any:
    """Calls `builder(scene)` with the model builders of its module replaced by recorders, and
    returns the capture (an `EnemyCapture`, `JointedCapture` or `BossCapture`). Nothing is built
    in a scene."""
    module = sys.modules[builder.__module__]
    captured: list[Any] = []

    def jointed(name: str, _scene: Any, neon: list[float], design: Any, drawing: Any) -> Any:
        captured.append(JointedCapture(name, neon, design, drawing))
        return MagicMock()

    def enemy(name: str, _scene: Any, neon: list[float], draw: Any, _breath: Any = None) -> Any:
        captured.append(EnemyCapture(name, neon, draw))
        return MagicMock()

    def boss(design: Any, _scene: Any, neon: list[float], drawing: dict[str, Any]) -> Any:
        captured.append(BossCapture(design, neon, drawing))
        return MagicMock()

    if hasattr(module, "build_enemy_model"):
        monkeypatch.setattr(module, "build_enemy_model", enemy)
    if hasattr(module, "build_boss_model"):
        monkeypatch.setattr(module, "build_boss_model", boss)
    if hasattr(module, "build_jointed_model"):
        monkeypatch.setattr(module, "build_jointed_model", jointed)
    builder(MagicMock())
    assert len(captured) == 1, "the builder must hand exactly one model to the scene"
    return captured[0]


class _Parts:
    """The parts a drawing gets, as the game's models use them: `muzzle(at)` may leave the kind out
    (Transcrypt passes `undefined` there, which the game reads as a gun)."""

    def __init__(self, parts: Any) -> None:
        self._parts = parts

    def __getattr__(self, name: str) -> Any:
        return getattr(self._parts, name)

    def muzzle(self, at: Any, kind: str | None = None) -> None:
        self._parts.muzzle(at, "gun" if kind is None else kind)


def drawn(draw: Callable[[Any], None]) -> dict[str, Any]:
    """Runs a drawing on real solid builders (pure geometry): its parts, reactors, rotors, wings
    and muzzles, as `enemy_mesh.collect_parts` gathers them."""
    return collect_parts(lambda parts: draw(_Parts(parts)))


def drawings_of(capture: Any) -> dict[str, dict[str, Any]]:
    """Runs every drawing of a capture on real solid builders, keyed by its place in the model:
    `body`, `ring`, `core`, `limbs.<joint>` and `parts.<id>`."""
    if isinstance(capture, EnemyCapture):
        return {"body": drawn(capture.draw)}
    # `build_boss_model` makes the drawing's objects records first (`record`), as the game does.
    drawing = record(capture.drawing)
    out: dict[str, dict[str, Any]] = {}
    body = drawing.get("body", drawing.get("core"))
    if body is not None:
        out["body"] = drawn(body)
    if drawing.get("ring") is not None:
        out["ring"] = drawn(drawing["ring"])
    for joint, limb in (drawing.get("limbs") or {}).items():
        # A limb is a record `{draw}` (as the models build them), or a drawing itself.
        out["limbs." + joint] = drawn(getattr(limb, "draw", limb))
    if not isinstance(capture, BossCapture):
        # A jointed enemy's parts are drawn on their own: each takes the builder alone.
        for part_id, draw in (drawing.get("parts") or {}).items():
            out["parts." + part_id] = drawn(draw)
        return out
    spots = {spec.id: spec for spec in capture.design.stats.parts}
    for part_id, draw in (drawing.get("parts") or {}).items():
        # A boss part's drawing is handed the point it sits at (`boss_model._part_builder`).
        spec = spots[part_id]
        at = boss_point(spec.x, spec.y)
        out["parts." + part_id] = drawn(lambda p, d=draw, a=at: d(p, a))
    return out


def jointed_design_ids(capture: Any) -> tuple[list[str], list[str]]:
    """The part ids the design asks for, and the part ids its drawing draws (a jointed model)."""
    design_ids = [spec.id for spec in capture.design.parts]
    return design_ids, list((capture.drawing.get("parts") or {}).keys())
