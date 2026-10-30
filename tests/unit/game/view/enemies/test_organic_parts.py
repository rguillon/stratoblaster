"""Unit tests of `src/game/view/enemies/organic_parts.py`."""

import pytest

from game.view.enemies.organic_parts import eyes, opt, reactor_sac
from render.geometry.solids import SolidBuilder


class _Parts:
    """The parts a model draws: real solid builders for the flesh and the veins, and a reactor hook
    that records where it was asked for."""

    def __init__(self) -> None:
        self.flesh = SolidBuilder()
        self.vein = SolidBuilder()
        self.reactors: list[tuple[list[float], float]] = []

    def reactor(self, at: list[float], radius: float) -> None:
        self.reactors.append((at, radius))


def _xs(builder: SolidBuilder) -> list[float]:
    return builder.geometry.positions[0::3]


def test_opt_returns_the_option_or_the_default_when_it_is_left_out():
    assert opt({"size": 2}, "size", 5) == 2
    assert opt({}, "size", 5) == 5
    # Only a missing key takes the default: a key set to 0 is an answer.
    assert opt({"size": 0}, "size", 5) == 0


def test_p16_r01_reactor_sac_swells_flesh_round_its_nozzle_and_hooks_the_reactor():
    parts = _Parts()
    reactor_sac(parts, [1, 2, 3], 2.0, [0.5, 0.5, 0.5])
    assert parts.reactors == [([1, 2, 3], 2.0)]
    # The sac is an organ: a closed lathe of flesh, its mouth at the nozzle.
    assert len(parts.flesh.geometry.positions) > 0
    assert len(parts.flesh.geometry.indices) > 0


def test_p16_r01_reactor_sac_runs_a_glowing_vein_from_its_back():
    parts = _Parts()
    glow = [0.5, 1.0, 0.5]
    reactor_sac(parts, [0, 0, 0], 2.0, glow)
    assert len(parts.vein.geometry.positions) > 0
    # The vein is lit in the given glow: every vertex colour carries it.
    colors = parts.vein.geometry.colors
    assert colors[0:3] == pytest.approx(glow)


def test_p16_r01_reactor_sac_takes_its_flesh_and_vein_length_when_given():
    parts = _Parts()
    short = _Parts()
    reactor_sac(parts, [0, 0, 0], 1.0, [1, 1, 1], vein_length=2)
    reactor_sac(short, [0, 0, 0], 1.0, [1, 1, 1], vein_length=20)
    # A longer vein reaches further forward (along +Z) than a shorter one.
    assert max(parts.vein.geometry.positions[2::3]) < max(short.vein.geometry.positions[2::3])


def test_p16_r01_eyes_are_lit_organs_spread_across_at_by_the_count_and_spacing():
    builder = SolidBuilder()

    class _Eyes:
        vein = builder

    eyes(_Eyes(), [0, 1, 2], {"count": 3, "size": 0.5, "spacing": 2.0}, [1, 0, 0])
    xs = _xs(builder)
    # Three eyes at x = -2, 0, 2, each about `size` across: the group is centred on `at` and as
    # wide as its outer eyes' centres plus their radii (the facets round a 5-sided lathe).
    assert (min(xs) + max(xs)) / 2 == pytest.approx(0, abs=0.1)
    assert 4.8 <= max(xs) - min(xs) <= 5.0


def test_p16_r01_eyes_default_to_two_eyes_spaced_one_point_four_apart():
    builder = SolidBuilder()

    class _Eyes:
        vein = builder

    eyes(_Eyes(), [0, 0, 0], {}, [1, 0, 0])
    xs = _xs(builder)
    # Two eyes at x = -0.7 and 0.7, each of the default size 0.6 across: 1.4 between the centres
    # plus the eyes' own radius at each end.
    assert (min(xs) + max(xs)) / 2 == pytest.approx(0, abs=0.1)
    assert 2.3 <= max(xs) - min(xs) <= 2.6
