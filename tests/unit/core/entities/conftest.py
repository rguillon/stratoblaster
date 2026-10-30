"""Fixtures of the entity tests: a fake world (`ctx`) and a boss factory (`make_boss`)."""

from collections.abc import Callable
from typing import Any

import pytest
from helpers.fakes import FakeContext, ProbeBoss  # noqa: E402

from core.entities.boss import BossDeath, BossPartSpec, BossStats  # noqa: E402


def default_parts() -> list[BossPartSpec]:
    return [
        BossPartSpec(
            id="gun", x=-20, y=10, radius=5, health=3, shields_core=False, drop_chance=0.5
        ),
        BossPartSpec(
            id="shield", x=0, y=20, radius=6, health=4, shields_core=True, drop_chance=0.0
        ),
    ]


def boss_values(**overrides: Any) -> dict[str, Any]:
    """Keyword arguments of a `BossStats`: a gun and a shielding part, unless overridden."""
    values: dict[str, Any] = {
        "model": "boss",
        "radius": 40.0,
        "health": 100.0,
        "points": 1000.0,
        "name": "Probe",
        "core_radius": 12.0,
        "parts": default_parts(),
        "ground_speed": 1.0,
        "stage_pause": 1.5,
        "death": BossDeath(seconds=1.0, every=0.25),
    }
    values.update(overrides)
    return values


@pytest.fixture
def ctx() -> FakeContext:
    return FakeContext()


@pytest.fixture
def make_boss() -> Callable[..., ProbeBoss]:
    """A `ProbeBoss` at (x, y). With `fighting=True` it is already in place, so it can be hit."""

    def make(
        x: float = 100.0, y: float = 200.0, fighting: bool = False, **overrides: Any
    ) -> ProbeBoss:
        boss = ProbeBoss(x, y, BossStats(**boss_values(**overrides)))
        if fighting:
            boss.state = "fighting"
        return boss

    return make
