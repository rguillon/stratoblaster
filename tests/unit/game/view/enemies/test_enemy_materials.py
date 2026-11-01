# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/enemy_materials.py`."""

from typing import Any
from unittest.mock import MagicMock

import pytest

from core.math.color import hue_saturation, in_family
from game.config.enemy_look import ENEMY_LOOK
from game.config.readability import READABILITY
from game.view.enemies import enemy_materials as em


class Col:
    """A colour stand-in: `color3` and friends return it; `scale` multiplies its channels."""

    def __init__(self, r: float, g: float, b: float) -> None:
        self.r = r
        self.g = g
        self.b = b

    def scale(self, k: float) -> "Col":
        return Col(self.r * k, self.g * k, self.b * k)


@pytest.fixture
def babylon(monkeypatch: Any) -> None:
    """Replace the Babylon calls of the materials; every new material is a fresh mock."""
    monkeypatch.setattr(em, "color3", Col)
    monkeypatch.setattr(em, "color3_black", lambda: Col(0, 0, 0))
    monkeypatch.setattr(em, "block_material_marks", lambda _scene, _block: False)
    monkeypatch.setattr(em, "new_pbr_material", lambda name, _scene: MagicMock(name=name))
    monkeypatch.setattr(em, "new_standard_material", lambda name, _scene: MagicMock(name=name))
    monkeypatch.setattr(em, "_ENEMY_CACHE", [])
    monkeypatch.setattr(em, "_TINTED_CACHE", [])
    monkeypatch.setattr(em, "_FLAME_CACHE", [])


def test_enm_38_enemy_colour_is_moved_into_the_enemies_hue_family() -> None:
    family = READABILITY.families.enemy
    for color in ([1, 0, 0], [0, 1, 0], [0.2, 0.4, 0.9], [1, 0.1, 0.85]):
        assert in_family(em.enemy_color(color), family), color


def test_d231_an_enemy_is_bright_yellow_or_bright_green_never_in_between() -> None:
    """ENM-38, GFX-ART-05: warm neon turns yellow, cool neon green."""
    yellow, green = READABILITY.enemyHues
    # Red, orange and magenta neon turns yellow; green, cyan and blue green.
    for color, hue in [
        ([1, 0.08, 0.1], yellow),
        ([1, 0.5, 0.05], yellow),
        ([1, 0.1, 0.85], yellow),
        ([0.2, 1, 0.3], green),
        ([0.1, 0.95, 1], green),
        ([0.15, 0.4, 1], green),
    ]:
        snapped = em.enemy_color(color)
        assert hue_saturation(snapped)[0] == pytest.approx(hue), color
        assert max(snapped) == pytest.approx(max(color))


def test_gfx_read_06_greys_are_not_moved_by_the_family() -> None:
    assert list(em.enemy_color([0.5, 0.5, 0.5])) == pytest.approx([0.5, 0.5, 0.5])


def test_enm_47_rim_is_lifted_towards_white_by_the_outline_whitening() -> None:
    whiten = READABILITY.enemyTrim.whiten
    strength = READABILITY.enemyTrim.strength
    rim = em.rim_of([0, 0.5, 1])
    assert rim == pytest.approx([
        (0 + whiten) * strength,
        (0.5 + 0.5 * whiten) * strength,
        (1 + 0) * strength,
    ])


def test_gfx_read_06_in_enemy_family_folds_each_vertex_colour_and_keeps_alpha(
    monkeypatch: Any,
) -> None:
    seen = {}

    def keep(geo: Any, colors: Any) -> Any:
        seen["colors"] = colors
        return ("geo", geo, colors)

    monkeypatch.setattr(em, "_with_colors", keep)
    geo = MagicMock()
    geo.colors = [1, 0, 0, 1, 0.5, 0.5, 0.5, 1]
    result = em.in_enemy_family(geo)
    folded = seen["colors"]
    # Red is folded into the family, the grey stays grey, and the alpha channels are untouched.
    assert folded[3] == 1
    assert folded[7] == 1
    assert folded[4:7] == pytest.approx([0.5, 0.5, 0.5])
    assert folded[0:3] != pytest.approx([1, 0, 0])
    assert result[1] is geo


def test_gfx_read_06_in_enemy_family_reads_missing_channels_as_zero(monkeypatch: Any) -> None:
    seen = {}
    monkeypatch.setattr(em, "_with_colors", lambda _geo, colors: seen.setdefault("c", colors))
    geo = MagicMock()
    geo.colors = [None, None, None, 1]
    em.in_enemy_family(geo)
    assert seen["c"][3] == 1


@pytest.mark.usefixtures("babylon")
def test_p05_unlit_material_is_white_light_with_no_shading() -> None:
    mat = em.unlit("neon", scene=object())
    assert mat.emissiveColor.r == 1
    assert mat.emissiveColor.g == 1
    assert mat.diffuseColor.r == 0
    assert mat.specularColor.r == 0
    assert mat.disableLighting is True


@pytest.mark.usefixtures("babylon")
def test_gfx_art_08_metal_takes_the_hull_settings_of_the_enemy_look() -> None:
    """Also GFX-ART-15: the hull metal's settings."""
    mat = em.metal("hull", Col(1, 1, 1), scene=object())
    assert mat.metallic == ENEMY_LOOK.hull.metallic
    assert mat.roughness == ENEMY_LOOK.hull.roughness
    assert mat.directIntensity == READABILITY.hullLight.direct
    assert mat.environmentIntensity == READABILITY.hullLight.environment


@pytest.mark.usefixtures("babylon")
def test_gfx_art_15_flesh_is_waxy_and_barely_metallic() -> None:
    mat = em.flesh_of("flesh", Col(1, 1, 1), scene=object())
    assert mat.metallic == ENEMY_LOOK.flesh.metallic
    assert mat.roughness == ENEMY_LOOK.flesh.roughness


@pytest.mark.usefixtures("babylon")
def test_p05_enemy_materials_are_made_once_per_scene() -> None:
    scene = object()
    first = em.enemy_materials(scene)
    assert em.enemy_materials(scene) is first
    other = em.enemy_materials(object())
    assert other is not first
    assert first.hull is not first.flesh


def test_body_materials_are_the_hull_and_flesh_that_flash_when_a_part_is_hit() -> None:
    assert em.BODY_MATERIALS == ["enemy-hull", "enemy-flesh"]


@pytest.mark.usefixtures("babylon")
def test_p05_tinted_hull_is_cached_per_scene_colour_and_kind() -> None:
    scene = object()
    neon = [1, 0, 0]
    hull = em.tinted_hull(scene, neon)
    assert em.tinted_hull(scene, neon) is hull
    assert em.tinted_hull(scene, neon, flesh=True) is not hull
    assert em.tinted_hull(scene, [0, 0, 1]) is not hull


@pytest.mark.usefixtures("babylon")
def test_p05_tinted_hull_glows_with_its_neon_at_the_hull_self_light() -> None:
    neon = [1, 0.5, 0]
    mat = em.tinted_hull(object(), neon)
    k = ENEMY_LOOK.hull.selfLight
    assert mat.emissiveColor.r == pytest.approx(1 * k)
    assert mat.emissiveColor.g == pytest.approx(0.5 * k)


@pytest.mark.usefixtures("babylon")
def test_p05_tinted_hull_is_tinted_towards_the_neon_by_the_tint() -> None:
    neon = [0, 0, 0]
    mat = em.tinted_hull(object(), neon)
    # Black neon: the albedo is pushed towards 1 - tint on every channel.
    assert mat.albedoColor.r == pytest.approx(1 - ENEMY_LOOK.hull.tint)


@pytest.mark.usefixtures("babylon")
def test_p05_flame_materials_are_shared_by_colour_and_scene() -> None:
    scene = object()
    flame = em.flame_materials(scene, [0, 0.5, 1])
    assert em.flame_materials(scene, [0, 0.5, 1]) is flame
    assert em.flame_materials(scene, [1, 0.5, 0]) is not flame
    assert flame.exhaust.alpha == pytest.approx(ENEMY_LOOK.reactor.exhaustAlpha)
    assert flame.flame.alpha == pytest.approx(ENEMY_LOOK.reactor.flameAlpha)
    assert flame.plasma.alpha == pytest.approx(ENEMY_LOOK.reactor.plasmaAlpha)
    assert flame.exhaust.backFaceCulling is False


@pytest.mark.usefixtures("babylon")
def test_p05_flame_is_a_whiter_core_than_its_exhaust() -> None:
    flame = em.flame_materials(object(), [0, 0, 0])
    assert flame.flame.emissiveColor.r == pytest.approx(ENEMY_LOOK.reactor.whiten)
    assert flame.exhaust.emissiveColor.r == 0


@pytest.mark.parametrize(
    "shade",
    [
        [0.2, 0.1, 0.05],  # Rust.
        [0.6, 0.45, 0.14],  # Gilding.
        [0.1, 0.11, 0.025],  # Olive.
        [0.17, 0.16, 0.12],  # Sandstone.
        [0.13, 0.035, 0.045],  # Crimson flesh.
        [0.1, 0.04, 0.07],  # Plum.
    ],
)
def test_d231_warm_and_pink_body_shades_are_greyed(shade: Any) -> None:
    """ENM-39, GFX-ART-06: no khaki, no pink body."""
    greyed = em.body_color(shade)
    assert hue_saturation(greyed)[1] == pytest.approx(READABILITY.enemyBody.maxSaturation)
    assert max(greyed) == pytest.approx(max(shade))


@pytest.mark.parametrize(
    "shade",
    [
        [0.05, 0.2, 0.06],  # Moss.
        [0.03, 0.09, 0.095],  # Teal.
        [0.15, 0.19, 0.24],  # Ice.
        [0.1, 0.105, 0.12],  # Blue-grey metal.
        [0.18, 0.18, 0.17],  # Bone: already near grey.
    ],
)
def test_d231_green_teal_blue_and_grey_body_shades_are_kept(shade: Any) -> None:
    assert em.body_color(shade) == shade


def test_d231_in_body_shades_greys_each_vertex_colour_and_keeps_alpha(monkeypatch: Any) -> None:
    seen = {}
    monkeypatch.setattr(em, "_with_colors", lambda _geo, colors: seen.setdefault("c", colors))
    geo = MagicMock()
    geo.colors = [0.2, 0.1, 0.05, 0.5, 0.05, 0.2, 0.06, 1]
    em.in_body_shades(geo)
    greyed = seen["c"]
    assert greyed[3] == 0.5
    assert greyed[4:] == [0.05, 0.2, 0.06, 1]
    most = READABILITY.enemyBody.maxSaturation
    assert hue_saturation(greyed[0:3])[1] == pytest.approx(most)
