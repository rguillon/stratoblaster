# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/readability.py`."""

import importlib
from typing import Any

import pytest
from helpers.color_families import in_family

from core.math.color import relative_luminance
from game.config.readability import READABILITY

YELLOW = (1, 1, 0)
LIME = (0.5, 1, 0)
GREEN = (0, 1, 0)


def test_gfx_read_04_each_gameplay_family_has_a_hue_window_and_a_saturation_floor() -> None:
    families = READABILITY.families
    assert set(families.keys()) == {"player", "enemy", "enemyShot", "pickup"}
    for name, family in families.items():
        assert 0 <= family["from"] < 360, name
        assert 0 <= family["to"] < 360, name
        assert 0 < family.minSaturation <= 1, name


def _hues(family: dict[str, float]) -> set[int]:
    """Return the whole degrees `family`'s hue range covers."""
    span = (family["to"] - family["from"] + 360) % 360
    return {(family["from"] + d) % 360 for d in range(int(span) + 1)}


def test_d231_enemies_and_bosses_are_yellow_to_green_with_no_pink() -> None:
    enemy = READABILITY.families.enemy
    assert all(in_family(color, enemy) for color in (YELLOW, LIME, GREEN))
    for pink in ((1, 0, 1), (1, 0.2, 0.6), (0.6, 0.2, 1), (1, 0, 0.1)):
        assert not in_family(pink, enemy)


def test_d231_the_enemies_two_hues_are_a_yellow_and_a_green_in_their_family() -> None:
    """GFX-ART-05."""
    yellow, green = READABILITY.enemyHues
    assert 55 <= yellow <= 65
    assert 115 <= green <= 135
    family = READABILITY.families.enemy
    for hue in (yellow, green):
        assert (hue - family["from"]) % 360 <= (family["to"] - family["from"]) % 360


def test_gfx_read_04_families_do_not_share_their_hues() -> None:
    families = READABILITY.families
    names = list(families.keys())
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            assert not _hues(families[a]) & _hues(families[b]), (a, b)


def test_gfx_read_02_tones_are_fractions_and_the_background_is_dark() -> None:
    """Also GFX-READ-01 (the background's brightness cap)."""
    assert all(0 < tone <= 1 for tone in READABILITY.tones.values())
    assert 0 < READABILITY.backgroundMaxLuminance < 0.5


def test_gfx_read_07_contrast_thresholds_are_positive() -> None:
    """Also GFX-READ-09, GFX-READ-10 (contrasts) and GFX-READ-15 (effects)."""
    assert READABILITY.minObjectContrast > 0
    assert READABILITY.minBulletContrast >= READABILITY.minObjectContrast
    assert 0 < READABILITY.effectMaxScreenShare <= 1
    assert 0 < READABILITY.effectMaxDuration < 1


def _colours_under(obj: Any, path: str, out: list[tuple[str, list[float]]]) -> None:
    """Every RGB colour of `obj` (a look's subtree) is listed with its path.

    Each is a list of three channels in 0..1. The `tints` are multipliers, not colours, and are left
    out.
    """
    if isinstance(obj, dict):
        for key in obj:
            if key != "tints":
                _colours_under(obj[key], f"{path}.{key}", out)
    elif isinstance(obj, (list, tuple)):
        is_colour = len(obj) == 3 and all(isinstance(c, (int, float)) for c in obj)
        if is_colour and all(0 <= channel <= 1 for channel in obj):
            out.append((path, list(obj)))
        else:
            for i, item in enumerate(obj):
                _colours_under(item, f"{path}[{i}]", out)


def _background_palettes() -> dict[int, list[tuple[str, list[float]]]]:
    """Return the background palette of each world is its ground, shore and water colours.

    Taken from its levels' looks (GFX-READ-02; the sky is not the background).
    """
    palettes: dict[int, list[tuple[str, list[float]]]] = {}
    for world in range(1, 5):
        looks = importlib.import_module(f"game.config.world_{world}.looks")
        colours: list[tuple[str, list[float]]] = []
        for name in dir(looks):
            if name.startswith("LEVEL_") and name.endswith("_LOOK"):
                look = getattr(looks, name)
                for key in ("terrain", "water"):
                    if look.get(key) is not None:
                        _colours_under(look[key], f"{name}.{key}", colours)
        palettes[world] = colours
    return palettes


def test_gfx_read_05_each_world_has_a_background_palette_to_check() -> None:
    palettes = _background_palettes()
    assert set(palettes) == {1, 2, 3, 4}
    for world, colours in palettes.items():
        assert len(colours) >= 10, world


@pytest.mark.xfail(
    strict=True,
    reason=(
        "GFX-READ-05: the desert browns of World 1 (dry lands, deep desert sand and steep ground) "
        "and the steep ground of World 2 fall in the enemy-shot family above the 0.35 brightness "
        "cap"
    ),
)
def test_gfx_read_05_no_background_colour_is_in_the_enemy_shot_family_above_the_cap() -> None:
    cap = READABILITY.backgroundMaxLuminance
    family = READABILITY.families.enemyShot
    for world, colours in _background_palettes().items():
        for path, colour in colours:
            if in_family(colour, family):
                assert relative_luminance(colour) <= cap, (world, path, colour)


@pytest.mark.xfail(
    strict=True,
    reason=(
        "GFX-READ-05: the lush grass greens (every world's grass) fall in the enemy family above "
        "the 0.35 brightness cap, as do the desert browns in the enemy-shot family"
    ),
)
def test_gfx_read_05_no_background_colour_is_in_a_reserved_family_above_the_cap() -> None:
    cap = READABILITY.backgroundMaxLuminance
    for world, colours in _background_palettes().items():
        for path, colour in colours:
            for name, family in READABILITY.families.items():
                if in_family(colour, family):
                    assert relative_luminance(colour) <= cap, (world, path, name, colour)
