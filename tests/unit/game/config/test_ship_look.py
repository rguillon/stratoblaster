# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/ship_look.py`."""

from game.config.ship_look import PLAYER_SHIP_SCALE, SHIP_LOOK


def test_the_player_ship_has_a_positive_scale() -> None:
    """GFX-SHIP-07."""
    assert PLAYER_SHIP_SCALE > 0


def test_the_ship_look_has_its_hull_canopy_and_reactor_colours() -> None:
    """GFX-SHIP-04, GFX-ART-04."""
    for name in ("hull", "accent", "canopy", "reactorCore", "reactorFlame"):
        assert SHIP_LOOK[name] is not None, name


def test_gfx_ship_04_the_three_metal_shades_are_satin_blue_grey_and_step_darker() -> None:
    """D-327: silver, steel, gunmetal; satin (no hard light spots), each darker than the last."""
    shades = [SHIP_LOOK.hull, SHIP_LOOK.hullMid, SHIP_LOOK.hullDark]
    for look in shades:
        red, _green, blue = look.albedo
        assert look.metallic >= 0.7
        assert 0.4 <= look.roughness <= 0.55
        assert blue > red
    brightness = [sum(look.albedo) for look in shades]
    assert brightness == sorted(brightness, reverse=True)
    assert len(set(brightness)) == 3
