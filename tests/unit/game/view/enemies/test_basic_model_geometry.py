# Copyright (c) 2026 Renaud Guillon
"""Unit tests of the basic enemies' models against their config.

The footprint against the size (ENM-12), and the muzzles against the config's muzzles (ENM-21).
"""

from typing import Any

import pytest
from helpers.view_probes import drawings_of, probe_builder

from game.config.enemies import ENEMY_CONFIG, ENEMY_UNIT
from game.view.enemies.enemy_models import ENEMY_MODELS

# The basic kinds: the nine of `ENEMY_CONFIG`, each with its model key (`stats.model`).
BASIC_BY_MODEL = {kind["stats"]["model"]: kind for kind in ENEMY_CONFIG.values()}

# ENM-12 (`hitbox_footprint_tolerance`, specs/enemies/common.md: 15 %); checked here at 10 %.
FOOTPRINT_TOLERANCE = 0.10


@pytest.fixture
def probe(monkeypatch: Any) -> Any:
    def run(builder: Any) -> Any:
        capture = probe_builder(monkeypatch, builder)
        return drawings_of(capture)["body"]

    return run


def _footprint(body: Any) -> float:
    """Return the model's footprint seen from above, in logical pixels.

    Its longest extent across or along, its rotors included, its reactors as their nozzles (their
    flames are not drawn here).
    """
    xs: list[float] = []
    zs: list[float] = []
    parts = body["parts"]
    for builder in (parts.hull, parts.flesh, parts.vein, parts.neon, parts.charge):
        xs.extend(builder.geometry.positions[0::3])
        zs.extend(builder.geometry.positions[2::3])
    for spot in body["reactors"] + body["rotors"]:
        xs.extend([spot.at[0] - spot.radius, spot.at[0] + spot.radius])
        zs.extend([spot.at[2] - spot.radius, spot.at[2] + spot.radius])
    for wing in body["wings"]:
        for builder in (wing.parts.hull, wing.parts.flesh, wing.parts.neon, wing.parts.vein):
            xs.extend(builder.geometry.positions[0::3])
            zs.extend(builder.geometry.positions[2::3])
    return max(max(xs) - min(xs), max(zs) - min(zs))


def _config_muzzles(kind: dict) -> list[list[float]]:
    """Return the config's muzzles of a kind.

    Its `muzzles` (a list), or its `muzzle` (one of the lancer's).
    """
    if kind.get("muzzles") is not None:
        return [list(m) for m in kind["muzzles"]]
    if kind.get("muzzle") is not None:
        return [list(kind["muzzle"])]
    return []


def test_enm_12_the_basic_kinds_are_the_nine_of_the_config() -> None:
    assert len(BASIC_BY_MODEL) == 9
    assert set(BASIC_BY_MODEL) <= set(ENEMY_MODELS)


@pytest.mark.parametrize("model", sorted(BASIC_BY_MODEL))
def test_enm_12_each_basic_model_footprint_is_within_10_percent_of_its_size(
    probe: Any, model: Any
) -> None:
    """The footprint from above, in L (ENEMY_UNIT logical pixels), against the kind's size."""
    body = probe(ENEMY_MODELS[model])
    size = BASIC_BY_MODEL[model]["size"]
    footprint_in_l = _footprint(body) / ENEMY_UNIT
    assert abs(footprint_in_l - size) <= FOOTPRINT_TOLERANCE * size, (model, footprint_in_l, size)


@pytest.mark.parametrize("model", sorted(BASIC_BY_MODEL))
def test_enm_21_each_basic_model_marks_the_config_muzzles(probe: Any, model: Any) -> None:
    """The model's marked muzzles are the config's muzzles.

    A config muzzle is (X right, Y up

        when facing down the screen, height); the model's nose is +Z, so it is (X, height, -Y). A
    barrel with an angle is drawn the way it truly turns on screen: the model's X is the config's
    mirrored (a model turned to face down has its +X to the screen's left).
    """
    body = probe(ENEMY_MODELS[model])
    expected = [
        [-x if angle else x, height, -y]
        for x, y, height, *angle in _config_muzzles(BASIC_BY_MODEL[model])
    ]
    marked = [list(at) for at, _kind in body["muzzles"]]
    assert len(marked) == len(expected), model
    # Each config muzzle is marked once, up to float noise.
    unmatched = list(marked)
    for want in expected:
        match = next(
            (got for got in unmatched if got == pytest.approx(want, abs=1e-6)),
            None,
        )
        assert match is not None, (model, want)
        unmatched.remove(match)
