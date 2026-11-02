# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/scenery/window_material_visual.py`: windows (D-210, GFX-BLDG-15)."""

from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest
from helpers.render_fakes import patch_babylon

from render.scenery import window_material_visual
from render.scenery.scenery_kit import LIGHTS_Z_OFFSET
from render.scenery.window_material_visual import ANISOTROPY, add_window_material, glow_windows

ATLAS = SimpleNamespace(size=256, glass=[0.2, 0.25, 0.3])
TEXTURE_CLASS = SimpleNamespace(TRILINEAR_SAMPLINGMODE=3, WRAP_ADDRESSMODE=1)


@pytest.fixture
def raw_textures(monkeypatch: pytest.MonkeyPatch) -> list[tuple[Any, ...]]:
    patch_babylon(monkeypatch, window_material_visual)
    monkeypatch.setattr(window_material_visual, "babylon_class", {"Texture": TEXTURE_CLASS}.get)
    monkeypatch.setattr(
        window_material_visual, "kept_window_atlas", lambda atlas: ("pixels", atlas)
    )
    monkeypatch.setattr(
        window_material_visual,
        "new_standard_material",
        lambda label, _scene: SimpleNamespace(label=label),
    )
    made: list[tuple[Any, ...]] = []

    def raw_texture(*args: Any) -> SimpleNamespace:
        made.append(args)
        return SimpleNamespace()

    monkeypatch.setattr(window_material_visual, "new_raw_texture", raw_texture)
    return made


def _look(windows: Any) -> SimpleNamespace:
    return SimpleNamespace(props=SimpleNamespace(windows=windows, lightIntensity=0.7))


def test_d210_a_look_without_a_windows_atlas_gets_no_window_material(
    raw_textures: list[tuple[Any, ...]],
) -> None:
    materials = SimpleNamespace()
    add_window_material(materials, object(), _look(None))
    assert not hasattr(materials, "windows")
    assert raw_textures == []


def test_d210_the_atlas_is_uploaded_once_as_a_tiling_mipmapped_texture(
    raw_textures: list[tuple[Any, ...]],
) -> None:
    scene = object()
    materials = SimpleNamespace()
    add_window_material(materials, scene, _look(ATLAS))
    assert raw_textures == [
        (("pixels", ATLAS), 256, 256, "TEXTUREFORMAT_RGBA", scene, True, False, 3),
    ]
    texture = materials.windows.diffuseTexture
    assert (texture.wrapU, texture.wrapV) == (1, 1)
    assert texture.anisotropicFilteringLevel == ANISOTROPY
    assert texture.hasAlpha is True


def test_gfx_bldg_15_the_windows_glow_by_the_accents_light_and_are_cut_out_of_their_quads(
    raw_textures: list[tuple[Any, ...]],
) -> None:
    materials = SimpleNamespace()
    add_window_material(materials, object(), _look(ATLAS))
    assert len(raw_textures) == 1
    material = materials.windows
    assert material.label == "prop-windows"
    # The atlas is the diffuse texture: a dark window stays dark.
    assert material.useAlphaFromDiffuseTexture is True
    assert material.diffuseColor.values == (0.2, 0.25, 0.3)
    assert material.specularColor.values == (0, 0, 0)
    assert material.emissiveColor.values == (0.7, 0.7, 0.7)
    assert material.disableDepthWrite is True
    assert material.zOffset == LIGHTS_Z_OFFSET


def test_gfx_bldg_15_the_glow_layer_draws_the_windows_with_their_own_material() -> None:
    layer = MagicMock()
    mesh = object()
    glow_windows(layer, mesh)
    layer.referenceMeshToUseItsOwnMaterial.assert_called_once_with(mesh)
