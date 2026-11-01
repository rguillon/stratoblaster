"""Unit tests of `src/game/config/ship_look.py`."""

from game.config.ship_look import PLAYER_SHIP_SCALE, SHIP_LOOK


def test_the_player_ship_has_a_positive_scale() -> None:
    """GFX-SHIP-07."""
    assert PLAYER_SHIP_SCALE > 0


def test_the_ship_look_has_its_hull_canopy_and_reactor_colours() -> None:
    """GFX-SHIP-04, GFX-ART-04."""
    for name in ("hull", "accent", "canopy", "reactorCore", "reactorFlame"):
        assert SHIP_LOOK[name] is not None, name
