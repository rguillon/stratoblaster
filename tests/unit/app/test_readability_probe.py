"""Unit tests of `src/app/readability_probe.py`."""
# adability_probe.py` (P14-R08): where each kind of object is on the playfield, and which of them
# is in view. The pixel reads need the render layer and are not run here.

from types import SimpleNamespace

from app.readability_probe import Spot, _first_in_view, _spots_of
from config.game_play import GAME_PLAY_CONFIG

CFG = GAME_PLAY_CONFIG.readability_probe


def everything_in_view(x: float, y: float) -> bool:
    return True


def nothing_in_view(x: float, y: float) -> bool:
    return False


def test_p14_r08_the_first_item_wholly_in_view_is_the_one_measured() -> None:
    items = [SimpleNamespace(x=500, y=500, radius=5), SimpleNamespace(x=10, y=20, radius=5)]
    spot = _first_in_view(items, lambda x, y: x < 100, lambda item: item.radius)
    assert spot is not None
    assert (spot.x, spot.y, spot.radius) == (10, 20, 5)


def test_p14_r08_an_item_with_its_margin_outside_the_view_is_skipped() -> None:
    items = [SimpleNamespace(x=0, y=0, radius=5)]
    assert _first_in_view(items, nothing_in_view, lambda item: item.radius) is None


def test_p14_r08_the_spots_are_the_ship_and_the_first_of_each_kind_in_view() -> None:
    run = SimpleNamespace(
        ship=SimpleNamespace(x=100, y=50),
        enemies=SimpleNamespace(
            enemies=[SimpleNamespace(x=200, y=300, radius=12)],
            shots=SimpleNamespace(
                bullets=[
                    SimpleNamespace(alive=False, x=1, y=1, radius=2),
                    SimpleNamespace(alive=True, x=150, y=200, radius=3),
                ]
            ),
        ),
        shots=SimpleNamespace(
            projectiles=[
                SimpleNamespace(alive=True, x=100, y=60),  # over the ship: not measured
                SimpleNamespace(alive=True, x=110, y=200),
            ]
        ),
    )
    spots = _spots_of(run, everything_in_view)
    assert (spots.player.x, spots.player.y, spots.player.radius) == (100, 50, CFG.ship_radius)
    assert spots.enemy is not None
    assert spots.enemy.radius == 12
    assert spots.enemy_bullet is not None
    assert spots.enemy_bullet.radius == 3
    assert isinstance(spots.player_shot, Spot)
    assert spots.player_shot.radius == CFG.shot_radius


def test_p14_r08_nothing_is_measured_when_nothing_is_in_view() -> None:
    run = SimpleNamespace(
        ship=SimpleNamespace(x=0, y=0),
        enemies=SimpleNamespace(
            enemies=[SimpleNamespace(x=5, y=5, radius=1)],
            shots=SimpleNamespace(bullets=[]),
        ),
        shots=SimpleNamespace(projectiles=[]),
    )
    spots = _spots_of(run, nothing_in_view)
    assert spots.enemy is None
    assert spots.enemy_bullet is None
    assert spots.player_shot is None
