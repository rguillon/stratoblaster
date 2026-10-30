"""Unit tests of `src/game/view/enemies/enemy_materials.py`."""

from unittest.mock import MagicMock

import pytest

from core.math.color import hue_saturation
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
def babylon(monkeypatch):
    """Replaces the Babylon calls of the materials; every new material is a fresh mock."""
    monkeypatch.setattr(em, "color3", Col)
    monkeypatch.setattr(em, "color3_black", lambda: Col(0, 0, 0))
    monkeypatch.setattr(em, "block_material_marks", lambda scene, block: False)
    monkeypatch.setattr(em, "new_pbr_material", lambda name, scene: MagicMock(name=name))
    monkeypatch.setattr(em, "new_standard_material", lambda name, scene: MagicMock(name=name))
    monkeypatch.setattr(em, "_ENEMY_CACHE", [])
    monkeypatch.setattr(em, "_TINTED_CACHE", [])
    monkeypatch.setattr(em, "_FLAME_CACHE", [])


def test_p14_r02_enemy_colour_is_moved_into_the_enemies_hue_family():
    family = READABILITY.families.enemy
    for color in ([1, 0, 0], [0, 1, 0], [0.2, 0.4, 0.9]):
        hue, _sat = hue_saturation(em.enemy_color(color))
        # The family runs from `from` degrees, through the top of the wheel, to `to`.
        assert hue >= family["from"] or hue <= family["to"]


def test_p14_r02_greys_are_not_moved_by_the_family():
    assert list(em.enemy_color([0.5, 0.5, 0.5])) == pytest.approx([0.5, 0.5, 0.5])


def test_p14_r04_rim_is_lifted_towards_white_by_the_outline_whitening():
    whiten = READABILITY.enemyOutline.whiten
    strength = READABILITY.enemyOutline.strength
    rim = em.rim_of([0, 0.5, 1])
    assert rim == pytest.approx(
        [(0 + whiten) * strength, (0.5 + 0.5 * whiten) * strength, (1 + 0) * strength]
    )


def test_p14_r02_in_enemy_family_folds_each_vertex_colour_and_keeps_alpha(monkeypatch):
    seen = {}

    def keep(geo, colors):
        seen["colors"] = colors
        return ("geo", geo, colors)

    monkeypatch.setattr(em, "_with_colors", keep)
    geo = MagicMock()
    geo.colors = [1, 0, 0, 1, 0.5, 0.5, 0.5, 1]
    result = em.in_enemy_family(geo)
    folded = seen["colors"]
    # Red is folded into the family, the grey stays grey, and the alpha channels are untouched.
    assert folded[3] == 1 and folded[7] == 1
    assert folded[4:7] == pytest.approx([0.5, 0.5, 0.5])
    assert folded[0:3] != pytest.approx([1, 0, 0])
    assert result[1] is geo


def test_p14_r02_in_enemy_family_reads_missing_channels_as_zero(monkeypatch):
    seen = {}
    monkeypatch.setattr(em, "_with_colors", lambda geo, colors: seen.setdefault("c", colors))
    geo = MagicMock()
    geo.colors = [None, None, None, 1]
    em.in_enemy_family(geo)
    assert seen["c"][3] == 1


def test_p05_unlit_material_is_white_light_with_no_shading(babylon):
    mat = em.unlit("neon", scene=object())
    assert mat.emissiveColor.r == 1 and mat.emissiveColor.g == 1
    assert mat.diffuseColor.r == 0
    assert mat.specularColor.r == 0
    assert mat.disableLighting is True


def test_p16_r01_metal_takes_the_hull_settings_of_the_enemy_look(babylon):
    mat = em.metal("hull", Col(1, 1, 1), scene=object())
    assert mat.metallic == ENEMY_LOOK.hull.metallic
    assert mat.roughness == ENEMY_LOOK.hull.roughness
    assert mat.directIntensity == READABILITY.hullLight.direct
    assert mat.environmentIntensity == READABILITY.hullLight.environment


def test_p16_r01_flesh_is_waxy_and_barely_metallic(babylon):
    mat = em.flesh_of("flesh", Col(1, 1, 1), scene=object())
    assert mat.metallic == ENEMY_LOOK.flesh.metallic
    assert mat.roughness == ENEMY_LOOK.flesh.roughness


def test_p05_enemy_materials_are_made_once_per_scene(babylon):
    scene = object()
    first = em.enemy_materials(scene)
    assert em.enemy_materials(scene) is first
    other = em.enemy_materials(object())
    assert other is not first
    assert first.hull is not first.flesh


def test_body_materials_are_the_hull_and_flesh_that_flash_when_a_part_is_hit():
    assert em.BODY_MATERIALS == ["enemy-hull", "enemy-flesh"]


def test_p05_tinted_hull_is_cached_per_scene_colour_and_kind(babylon):
    scene = object()
    neon = [1, 0, 0]
    hull = em.tinted_hull(scene, neon)
    assert em.tinted_hull(scene, neon) is hull
    assert em.tinted_hull(scene, neon, flesh=True) is not hull
    assert em.tinted_hull(scene, [0, 0, 1]) is not hull


def test_p05_tinted_hull_glows_with_its_neon_at_the_hull_self_light(babylon):
    neon = [1, 0.5, 0]
    mat = em.tinted_hull(object(), neon)
    k = ENEMY_LOOK.hull.selfLight
    assert mat.emissiveColor.r == pytest.approx(1 * k)
    assert mat.emissiveColor.g == pytest.approx(0.5 * k)


def test_p05_tinted_hull_is_tinted_towards_the_neon_by_the_tint(babylon):
    neon = [0, 0, 0]
    mat = em.tinted_hull(object(), neon)
    # Black neon: the albedo is pushed towards 1 - tint on every channel.
    assert mat.albedoColor.r == pytest.approx(1 - ENEMY_LOOK.hull.tint)


def test_p05_flame_materials_are_shared_by_colour_and_scene(babylon):
    scene = object()
    flame = em.flame_materials(scene, [0, 0.5, 1])
    assert em.flame_materials(scene, [0, 0.5, 1]) is flame
    assert em.flame_materials(scene, [1, 0.5, 0]) is not flame
    assert flame.exhaust.alpha == pytest.approx(ENEMY_LOOK.reactor.exhaustAlpha)
    assert flame.flame.alpha == pytest.approx(ENEMY_LOOK.reactor.flameAlpha)
    assert flame.plasma.alpha == pytest.approx(ENEMY_LOOK.reactor.plasmaAlpha)
    assert flame.exhaust.backFaceCulling is False


def test_p05_flame_is_a_whiter_core_than_its_exhaust(babylon):
    flame = em.flame_materials(object(), [0, 0, 0])
    assert flame.flame.emissiveColor.r == pytest.approx(ENEMY_LOOK.reactor.whiten)
    assert flame.exhaust.emissiveColor.r == 0
