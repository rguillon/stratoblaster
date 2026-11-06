# Copyright (c) 2026 Renaud Guillon
"""A boss model's turrets drawn on real solid builders, round their pivots (BOSS-29).

`probe_builder` captures what the model hands to `build_boss_model`; each turret of its drawing is
then drawn round the pivot of its gun (`design.guns[piece].turret`), as `boss_model.build_turret`
does, and checked against the gun's muzzles. `read_as_records` lets a drawing that reads a dict
literal by attribute run under CPython. `drawn_mounts` builds a boss model on fake nodes and returns
its gun mounts' models (BOSS-58).
"""

from types import SimpleNamespace
from typing import Any

import pytest

from game.config.record import record
from game.view.bosses import boss_armour, boss_limbs, boss_model
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import _point_of
from helpers.bosses_top_fakes import patch_models
from helpers.view_probes import drawn, probe_builder

# The muzzle kinds a turret's gun lists its muzzles under.
KINDS = ["gun", "laser"]


def drawn_turrets(monkeypatch: Any, builder: Any) -> dict[str, Any]:
    """Return each turret of the boss model `builder` makes, by piece: `[pivot, drawn, gun]`.

    `drawn` is what the turret draws round its `pivot` (model space), `gun` the design's gun.
    """
    capture = probe_builder(monkeypatch, builder)
    drawing = record(capture.drawing)
    result: dict[str, Any] = {}
    for piece, draw in (drawing.get("turrets") or {}).items():
        gun = capture.design.guns[piece]
        at = _point_of(gun.turret)
        result[piece] = [at, drawn(lambda p, d=draw, a=at: d(p, a)), gun]
    return result


def read_as_records(monkeypatch: Any, module: Any, name: str) -> None:
    """Make `module.name` read the dicts it is given as records (`record`), as the browser does.

    A drawing that hands a dict literal to a shape reading its fields as attributes (`spec.radius`)
    works in the browser, where the literal is a JavaScript object, but not under CPython, where it
    is a dict (ENG-160).
    """
    original = getattr(module, name)

    def wrapped(*args: Any) -> Any:
        return original(*[record(a) if isinstance(a, dict) else a for a in args])

    monkeypatch.setattr(module, name, wrapped)


def check_turret(turret: list[Any]) -> None:
    """Check a turret (`drawn_turrets`): a hull, and one muzzle ahead of its pivot per gun muzzle.

    Of the same kinds as the gun's.
    """
    at = turret[0]
    parts = turret[1]
    gun = turret[2]
    assert len(parts["parts"].hull.geometry.positions) > 0
    muzzles = parts["muzzles"]
    for kind in KINDS:
        wanted = gun.get(kind) or []
        assert len([m for m in muzzles if m[1] == kind]) == len(wanted), kind
    assert len(muzzles) > 0
    for m in muzzles:
        # The barrels point forward, down the screen (+Z), from the pivot.
        assert m[0][2] > at[2]


def drawn_mounts(monkeypatch: Any, builder: Any) -> dict[str, Any]:
    """Return the gun mounts the boss model `builder` makes draw (BOSS-58), by mount id.

    Each `[mount, model, drawn]`: the design's mount, its model (on its pivot node) and what it drew
    (`collect_parts`). The model is built on fake nodes (`bosses_top_fakes`), without its rig.
    """
    capture = probe_builder(monkeypatch, builder)
    made = patch_models(monkeypatch, boss_model, boss_armour, boss_limbs)
    monkeypatch.setattr(boss_model, "build_smoke", lambda *_args: SimpleNamespace(node=None))
    monkeypatch.setattr(boss_model, "effect_materials", lambda _scene: {"flash": "FLASH"})
    monkeypatch.setattr(boss_model, "child_meshes", lambda node, _direct: list(node.meshes))
    monkeypatch.setattr(boss_model, "set_trim_group", lambda _node: None)
    drawing = {key: value for key, value in capture.drawing.items() if key != "rig"}
    design = capture.design
    boss_model.build_boss_model(design, object(), capture.neon, drawing)
    result: dict[str, Any] = {}
    for mount in design.mounts or []:
        name = design.id + "-" + mount.id + "-gun"
        if name in made.models:
            result[mount.id] = [mount, made.models[name], made.drawn[name]]
    return result


def check_mounts(mounts: dict[str, Any], design: Any) -> None:
    """Check every mount of `design` is drawn, on its pivot where its design puts it (BOSS-58).

    A gun's or a laser's with a muzzle per barrel of the design's, a missile block's with none.
    """
    assert sorted(mounts) == sorted(mount.id for mount in design.mounts)
    for mount, model, parts in mounts.values():
        pivot = model.root.parent
        assert pivot.name == design.id + "-" + mount.id + "-mount"
        at = boss_point(mount.at[0], mount.at[1], mount.height)
        assert pivot.position.xyz() == pytest.approx(at)
        assert len(parts["parts"].hull.geometry.positions) > 0
        if mount.kind != "missile":
            assert len(parts["muzzles"]) == mount.barrels, mount.id
