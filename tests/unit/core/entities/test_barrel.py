# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/core/entities/barrel.py`."""

import math

import pytest

from core.entities.barrel import RECOIL_SECONDS, Barrel


def test_wpn_03_a_barrel_that_has_not_fired_does_not_recoil() -> None:
    assert Barrel([0, 0, 0]).recoil_at(5) == 0


def test_wpn_03_the_recoil_is_one_as_it_fires_and_zero_after_the_recoil_time() -> None:
    barrel = Barrel([0, 0, 0])
    barrel.kick(2)
    assert barrel.recoil_at(2) == 1
    assert 0 < barrel.recoil_at(2 + RECOIL_SECONDS / 2) < 1
    assert barrel.recoil_at(2 + RECOIL_SECONDS) == 0
    assert barrel.recoil_at(100) == 0


def test_wpn_03_a_barrel_firing_again_before_it_is_back_restarts_at_one() -> None:
    barrel = Barrel([0, 0, 0])
    barrel.kick(0)
    barrel.kick(RECOIL_SECONDS / 2)
    assert barrel.recoil_at(RECOIL_SECONDS / 2) == 1


def test_wpn_01_a_barrel_with_an_angle_reads_it_in_degrees() -> None:
    assert Barrel([1, 2, 3, 90]).angle == pytest.approx(math.pi / 2)
    assert Barrel([1, 2, 3]).angle is None
