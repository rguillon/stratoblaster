"""Unit tests of `src/game/config/bonus_look.py`."""

from core.math.color import in_family
from game.config.bonus_look import BONUS_LOOK
from game.config.readability import READABILITY


def test_gfx_fx_12_life_and_bomb_bonuses_have_their_own_look() -> None:
    assert BONUS_LOOK.life is not None
    assert BONUS_LOOK.bomb is not None
    assert BONUS_LOOK.life != BONUS_LOOK.bomb


def test_gfx_fx_11_the_frame_is_inset_inside_the_bonus() -> None:
    assert 0 < BONUS_LOOK.frameInset < 1
    assert BONUS_LOOK.size > 0


def _saturated(color: list[float]) -> bool:
    high = max(color)
    return high > 0 and (high - min(color)) / high >= 0.5


def test_d231_the_bonuses_colours_are_in_the_pickups_violet_family() -> None:
    """GFX-ART-07, GFX-READ-04."""
    colours = [
        BONUS_LOOK.frame,
        BONUS_LOOK.chevrons,
        BONUS_LOOK.flash.color,
        *BONUS_LOOK.halo.colors[:3],
        BONUS_LOOK.life.rim,
        BONUS_LOOK.life.heart,
        *BONUS_LOOK.life.halo[:3],
        BONUS_LOOK.bomb.shell,
        BONUS_LOOK.bomb.highlight,
        *BONUS_LOOK.bomb.halo[:3],
    ]
    for colour in colours:
        # Pale ones (a highlight) belong to no family; the others to the pickups'.
        if _saturated(colour):
            assert in_family(colour, READABILITY.families.pickup), colour
