# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/veteran_small_models.py`."""

import math
from typing import Any

import pytest
from helpers.view_probes import drawings_of, probe_builder

from game.config.enemies_veteran import VETERAN_CONFIG
from game.view.enemies import vetelite_organic
from game.view.enemies import veteran_small_models as module
from render.geometry.solids import SolidBuilder


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


def test_enm_wasp_05_wasp_is_a_single_fan_drone_with_three_nose_guns_and_no_wings(
    probe: Any,
) -> None:
    capture, body = probe(module.build_wasp)
    assert capture.name == "wasp"
    # One fan spinning in its duct: a rotor, no wing and no reactor.
    assert body["wings"] == []
    assert body["reactors"] == []
    assert [(r.at, r.radius) for r in body["rotors"]] == [([0, 0.2, 0], module.WASP_FAN)]
    # Its three guns' muzzles at the pod's front, the config's in model space, with no barrel.
    expected = [[[-m[0], m[2], -m[1]], "gun"] for m in VETERAN_CONFIG.wasp.muzzles]
    assert body["muzzles"] == expected
    assert len(expected) == 3
    assert body["slides"] == []


def test_enm_wasp_04_wasp_has_a_charge_lens_on_its_nose_pod(probe: Any) -> None:
    _capture, body = probe(module.build_wasp)
    pos = body["parts"].charge.geometry.positions
    assert len(pos) > 0
    # Set in the top of the pod, at the nose: it bulges out of the pod's top.
    top = module.WASP_POD_AT[1] + module.WASP_POD[1]
    assert min(pos[2::3]) > 0
    assert min(pos[1::3]) >= top + module.WASP_LENS[0][1] - 1e-6
    assert max(pos[1::3]) > top


def test_enm_wasp_01_the_duct_s_inside_and_struts_are_bare_its_outside_trimmed(
    probe: Any,
) -> None:
    _capture, body = probe(module.build_wasp)
    parts = body["parts"]
    # The trimmed hull reaches the duct's outer wall; the bare metal stays within its inner wall.
    hull_xs = parts.hull.geometry.positions[0::3]
    bare = parts.bare.geometry.positions
    assert max(hull_xs) == pytest.approx(module.WASP_DUCT[1])
    assert len(bare) > 0
    inner = module.WASP_DUCT[0]
    assert all(math.hypot(bare[i], bare[i + 2]) <= inner + 0.5 for i in range(0, len(bare), 3))
    # Its neon: the duct's lip and the light along the back.
    assert len(parts.neon.geometry.positions) > 0


def test_enm_phantom_05_phantom_is_a_flying_wing_with_two_reactors_and_a_bank_of_five_guns(
    probe: Any,
) -> None:
    capture, body = probe(module.build_phantom)
    assert capture.name == "phantom"
    assert len(body["reactors"]) == 2
    assert len(body["muzzles"]) == 5
    assert len(body["parts"].flesh.geometry.positions) > 0


def test_enm_phantom_03_phantom_s_five_guns_are_barrels_with_no_housing_at_the_muzzles(
    probe: Any,
) -> None:
    """Its guns are sunk in the wing: five recoiling barrels, no fixed housing on the body."""
    _capture, body = probe(module.build_phantom)
    muzzles = VETERAN_CONFIG.phantom.muzzles
    slides = body["slides"]
    assert [piece.index for piece in slides] == list(range(len(muzzles)))
    assert len(slides) == 5
    for piece in slides:
        assert not piece.swivel
        # A lit barrel: trimmed metal, with a charge light at its tip.
        assert len(piece.parts.hull.geometry.positions) > 0
        assert len(piece.parts.neon.geometry.positions) > 0
    # The body's own metal is the nose cap alone: no housing at any barrel's root.
    nose = SolidBuilder().loft(module.POD_SECTION, module.PHANTOM_NOSE, module.H.panel, None, None)
    assert body["parts"].hull.geometry.positions == nose.geometry.positions


def test_enm_phantom_06_the_phantom_is_a_plain_model_that_no_longer_fades(
    monkeypatch: Any,
) -> None:
    """It no longer cloaks: the built model is `build_enemy_model`'s, its sync not wrapped."""
    built = object()
    monkeypatch.setattr(module, "build_enemy_model", lambda *_args: built)
    assert module.build_phantom(object()) is built
