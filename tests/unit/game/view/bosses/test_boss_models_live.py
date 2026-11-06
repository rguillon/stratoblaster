# Copyright (c) 2026 Renaud Guillon
"""Every boss model built on fake nodes and shown through a whole fight (BOSS-47, BOSS-58).

Each boss of the game comes in its own model (`boss_models.BOSS_MODELS`), built on the fakes of
`bosses_top_fakes` (every drawing run on real solid builders), and is shown frame by frame as its
world boss fights: its parts broken one after the other (as K does, DEV-OPT-09) through its
transformations to its death. Its guns rise out as it first fires from them, its hatches burst, its
rigs and moving pieces move, its destroyed weapons leave their stumps (BOSS-18).
"""

import sys
from types import SimpleNamespace
from typing import Any

import pytest
from helpers.bosses_top_fakes import FakeNode, patch_models
from helpers.bosses_top_turrets import read_as_records
from helpers.enemy_steps import area
from helpers.fakes import FakeContext
from helpers.view_probes import probe_builder

from game.sim.boss_kinds import BOSS_DESIGNS
from game.sim.bosses.world_boss import WorldBoss
from game.view.bosses import boss_model
from game.view.bosses.boss_models import BOSS_MODELS

# Drawings handing a dict literal to a shape that reads it by attribute, as the browser does: under
# CPython they read it as a record (`read_as_records`, ENG-160).
AS_RECORDS = {"floe-breaker": [("game.view.bosses.world_2.floe_breaker_model", "turret")]}

# A frame, and how often a part is broken (long enough for each transformation to play out).
DT = 0.1
BREAK_EVERY = 2.5
# A fight never lasts longer than this (seconds): every boss dies well before.
LONGEST = 400


class _Smoke:
    """A part's smoke: its node, stepped each frame."""

    def __init__(self, name: str, scene: Any, parent: Any) -> None:
        self.node = FakeNode(name + "-smoke", scene)
        self.node.parent = parent

    def step(self, _dt: float) -> None:
        """Drift (nothing to draw here)."""


def _view_modules() -> list[Any]:
    """Return the boss view modules (every boss's model, rig and parts), loaded by `BOSS_MODELS`."""
    return [
        module
        for name, module in sorted(sys.modules.items())
        if name.startswith("game.view.bosses") and module is not None
    ]


def _built(monkeypatch: pytest.MonkeyPatch, design: Any) -> Any:
    """Return the boss's model, built on fake nodes, and what it built (`ModelBuilder`)."""
    capture = probe_builder(monkeypatch, BOSS_MODELS[design.id])
    made = patch_models(monkeypatch, *_view_modules())
    for module, name in AS_RECORDS.get(design.id, []):
        read_as_records(monkeypatch, sys.modules[module], name)
    monkeypatch.setattr(
        boss_model, "build_smoke", lambda name, _r, scene, parent: _Smoke(name, scene, parent)
    )
    monkeypatch.setattr(boss_model, "effect_materials", lambda _scene: {"flash": "FLASH"})
    monkeypatch.setattr(boss_model, "child_meshes", lambda node, _direct: list(node.meshes))
    monkeypatch.setattr(boss_model, "set_trim_group", lambda _node: None)
    model = boss_model.build_boss_model(design, object(), capture.neon, capture.drawing)
    return SimpleNamespace(model=model, made=made)


def _fight(model: Any, boss: WorldBoss) -> None:
    """Show `boss` fighting to its death, a part broken every `BREAK_EVERY` seconds."""
    ctx = FakeContext()
    clock = 0.0
    since_break = 0.0
    while boss.health > 0 and clock < LONGEST:
        boss.update(ctx, DT)
        model.sync(boss, DT)
        clock += DT
        since_break += DT
        if since_break >= BREAK_EVERY:
            since_break = 0.0
            boss.break_next()
    assert boss.health == 0, "still alive after the longest fight"
    assert boss.state == "dying"


@pytest.mark.parametrize("design", BOSS_DESIGNS, ids=[d.id for d in BOSS_DESIGNS])
def test_boss_58_every_boss_model_shows_a_whole_fight(design: Any) -> None:
    mp = pytest.MonkeyPatch()
    try:
        built = _built(mp, design)
        # At rest first, as the dev viewer's stand-in shows it.
        built.model.sync(SimpleNamespace(charge=0.3), DT)
        boss = WorldBoss(design, area(width=480, height=640))
        boss.open_fire()
        _fight(built.model, boss)
    finally:
        mp.undo()
    # Every gun mount was drawn, on its pivot, and came out as the boss fired from it.
    for mount in design.mounts or []:
        assert design.id + "-" + mount.id + "-gun" in built.made.models, mount.id
