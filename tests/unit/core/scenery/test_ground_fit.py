"""How a prop sits on the ground (P04-R04): `core/scenery/ground_fit.py`."""

import pytest

from core.scenery.ground_fit import lowest_under, standing_height


class _Plane:
    """Ground rising by `slope` per unit of X, at `base` where X is 0."""

    def __init__(self, base: float, slope: float = 0.0) -> None:
        self.base = base
        self.slope = slope

    def height(self, x: float, z: float) -> float:
        return self.base + self.slope * x


def test_lowest_under_takes_the_lowest_corner_and_centre() -> None:
    assert lowest_under(_Plane(10.0, 0.0), 5.0, 5.0, 3.0) == pytest.approx(10.0)
    assert lowest_under(_Plane(0.0, 1.0), 5.0, 0.0, 2.0) == pytest.approx(3.0)


def test_p04_r04_a_flat_spot_stands_at_its_lowest_ground() -> None:
    assert standing_height(_Plane(10.0), (0.0, 0.0, 2.0), (0.5, 0.0)) == pytest.approx(10.0)


def test_p04_r04_a_spot_on_too_steep_ground_does_not_stand() -> None:
    steep = _Plane(10.0, 1.0)
    assert standing_height(steep, (0.0, 0.0, 2.0), (0.5, 0.0)) is None
    assert standing_height(steep, (0.0, 0.0, 2.0), (5.0, 0.0)) == pytest.approx(8.0)


def test_p04_r04_a_spot_under_the_sea_limit_does_not_stand() -> None:
    assert standing_height(_Plane(-1.0), (0.0, 0.0, 2.0), (0.5, 5.0)) is None
