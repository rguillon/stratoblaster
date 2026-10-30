"""Unit tests of `src/game/config/prop_look.py`."""

from game.config.prop_look import PROP_COLORS, PROP_LIGHTS


def test_p04_r04_every_prop_colour_is_an_rgb_triple_in_range() -> None:
    for name, color in PROP_COLORS.items():
        assert len(color) == 3, name
        assert all(0 <= c <= 1 for c in color), name


def test_p04_r04_every_prop_light_has_a_colour() -> None:
    for name, light in PROP_LIGHTS.items():
        assert light is not None, name
        assert len(light) >= 1, name
