# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/heavy_enemy_models.py`."""

import math
from typing import Any

import pytest
from helpers.view_probes import drawings_of, probe_builder

from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies import heavy_enemy_models as module


@pytest.fixture
def probe(monkeypatch: Any) -> Any:
    def run(builder: Any) -> Any:
        capture = probe_builder(monkeypatch, builder)
        return capture, drawings_of(capture)["body"]

    return run


def test_enm_spinner_02_spinner_has_four_guns_and_two_reactors(probe: Any) -> None:
    capture, body = probe(module.build_spinner)
    assert capture.name == "spinner"
    assert capture.neon == ENEMY_LOOK.neon.spinner
    assert len(body["muzzles"]) == 4
    assert [kind for _at, kind in body["muzzles"]] == ["gun"] * 4
    # One reactor in each engine pod, either side of the tail, raised over the ring.
    reactors = body["reactors"]
    assert len(reactors) == 2
    assert sorted(r.at[0] for r in reactors) == pytest.approx([
        -module.SPINNER_ENGINE["x"],
        module.SPINNER_ENGINE["x"],
    ])
    assert all(r.at[1] == module.SPINNER_LIFT for r in reactors)
    assert body["wings"] == []


def test_enm_spinner_01_the_ring_and_its_four_unlit_barrels_swivel_with_the_spin(
    probe: Any,
) -> None:
    """The ring (one slide about the centre, no recoil) and the four barrels turn with the spin."""
    _capture, body = probe(module.build_spinner)
    slides = body["slides"]
    assert len(slides) == 5
    assert all(piece.swivel for piece in slides)
    ring, barrels = slides[0], slides[1:]
    assert ring.pivot == [0, 0, 0]
    assert ring.distance == 0
    # The ring's edges are trimmed (hull); its spokes, mounts and collars are bare metal.
    assert len(ring.parts.hull.geometry.positions) > 0
    assert len(ring.parts.bare.geometry.positions) > 0
    assert ring.parts.neon.geometry.positions == []
    for i, barrel in enumerate(barrels):
        assert barrel.index == i
        assert barrel.distance > 0
        # ENM-SPINNER-02/03: no charge light, no edge trim on the guns.
        assert barrel.parts.neon.geometry.positions == []
        assert barrel.parts.hull.geometry.positions == []
        assert len(barrel.parts.bare.geometry.positions) > 0
    # Each muzzle sits out past the ring's outer wall.
    for at, _kind in body["muzzles"]:
        assert math.hypot(at[0], at[2]) > module.SPINNER_RING[0][0]


def test_p05_lancer_has_three_reactors_and_one_lance_gun(probe: Any) -> None:
    capture, body = probe(module.build_lancer)
    assert capture.name == "lancer"
    assert len(body["reactors"]) == 3
    assert len(body["muzzles"]) == 1


def test_p05_rocketeer_has_two_reactors_and_two_rocket_mouths(probe: Any) -> None:
    capture, body = probe(module.build_rocketeer)
    assert capture.name == "rocketeer"
    assert len(body["reactors"]) == 2
    assert len(body["muzzles"]) == 2


def test_heavy_kinds_are_bodies_with_their_neon_lights(probe: Any) -> None:
    for builder in (module.build_spinner, module.build_lancer, module.build_rocketeer):
        capture, body = probe(builder)
        assert len(body["parts"].neon.geometry.positions) > 0, capture.name
