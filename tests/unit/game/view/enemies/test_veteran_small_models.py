# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/veteran_small_models.py`."""

from typing import Any

import pytest
from helpers.view_probes import drawings_of, probe_builder

from game.view.enemies import vetelite_organic
from game.view.enemies import veteran_small_models as module


@pytest.fixture
def probe(monkeypatch: Any) -> Any:
    def run(builder: Any) -> Any:
        # `_with_wing` copies a wing with `Object.assign` in the browser, and as a record of the
        # same fields under CPython; a plain dict merge stands in for it here.
        monkeypatch.setattr(
            vetelite_organic,
            "_with_wing",
            lambda wing, root, tips: {**wing, "root": root, "tips": tips},
        )
        capture = probe_builder(monkeypatch, builder)
        return capture, drawings_of(capture)["body"]

    return run


def test_enm_wasp_05_wasp_has_two_pairs_of_wings_two_reactors_and_a_bank_of_three_nose_guns(
    probe: Any,
) -> None:
    capture, body = probe(module.build_wasp)
    assert capture.name == "wasp"
    # Two membrane pairs of wings: four flaps in all.
    assert len(body["wings"]) == 4
    assert len(body["reactors"]) == 2
    assert len(body["muzzles"]) == 3


def test_enm_phantom_05_phantom_is_a_flying_wing_with_two_reactors_and_a_bank_of_five_guns(
    probe: Any,
) -> None:
    capture, body = probe(module.build_phantom)
    assert capture.name == "phantom"
    assert len(body["reactors"]) == 2
    assert len(body["muzzles"]) == 5
    assert len(body["parts"].flesh.geometry.positions) > 0


class _Mesh:
    """A stand-in mesh: it takes the visibility a sync gives it."""

    def __init__(self) -> None:
        self.visibility = 1
        self.isVisible = True


class _Enemy:
    def __init__(self, opacity: float) -> None:
        self.opacity = opacity


def test_enm_phantom_06_the_edge_trim_fades_with_the_phantom(monkeypatch: Any) -> None:
    """The trim meshes are added after the builder returns, so they must be listed at sync."""
    body = _Mesh()
    trims: list[_Mesh] = []
    root = object()

    def children(node: Any, _direct_only: Any) -> Any:
        assert node is root
        return [body, *trims]

    monkeypatch.setattr(module, "build_enemy_model", lambda *_args: _Built(root))
    monkeypatch.setattr(module, "child_meshes", children)
    monkeypatch.setattr(module, "Phantom", _Enemy)
    built = module.build_phantom(object())
    # The edge trim is added to the model after it is built, as `add_edge_trim` does.
    trims.append(_Mesh())
    built.sync(_Enemy(0.3), 0.0)
    assert body.visibility == pytest.approx(0.3)
    assert trims[0].visibility == pytest.approx(0.3)
    assert trims[0].isVisible
    built.sync(_Enemy(0), 0.0)
    assert not body.isVisible
    assert not trims[0].isVisible


class _Built:
    def __init__(self, root: Any) -> None:
        self.root = root

    def sync(self, _enemy: Any, _dt: Any) -> None:
        return None
