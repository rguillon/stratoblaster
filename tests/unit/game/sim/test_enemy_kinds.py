"""Unit tests of `src/game/sim/enemy_kinds.py`."""

import pytest
from helpers.enemy_steps import area

from game.config.enemies import ENEMY_CONFIG, ENEMY_SPAWN_MARGIN
from game.sim.enemies.gnat import Gnat
from game.sim.enemies.strafer import Strafer
from game.sim.enemy_kinds import ENEMY_KINDS, FIRST_KINDS, side_pass

FIRST_IDS = [
    "gnat",
    "hornet",
    "scout",
    "strafer",
    "weaver",
    "spinner",
    "lancer",
    "rocketeer",
    "bulwark",
    "splitter",
    "carrier",
]


def test_p05_r01_every_kind_of_the_game_is_listed_once_with_a_unique_id() -> None:
    ids = [kind.id for kind in ENEMY_KINDS]
    assert len(ids) == len(set(ids)) == 21
    assert [kind.id for kind in FIRST_KINDS] == FIRST_IDS


def test_p05_r01_each_kind_has_a_name_and_a_spawn_function() -> None:
    for kind in ENEMY_KINDS:
        assert kind.name
        assert callable(kind.spawn)


def test_p05_r01_a_gnat_group_comes_in_as_its_configured_number_of_gnats() -> None:
    kind = next(k for k in ENEMY_KINDS if k.id == "gnat")
    group = kind.spawn(area())
    assert len(group) == ENEMY_CONFIG.gnat.groupSize
    assert all(isinstance(g, Gnat) for g in group)


def test_p05_r01_a_strafer_from_a_left_entry_starts_just_left_of_the_playfield() -> None:
    kind = next(k for k in ENEMY_KINDS if k.id == "strafer")
    (strafer,) = kind.spawn(area(width=400, side="left", position=0.3))
    assert isinstance(strafer, Strafer)
    assert strafer.x == pytest.approx(-ENEMY_SPAWN_MARGIN)
    assert strafer.heading == pytest.approx(3.14159265 / 2, rel=1e-6)


def test_p05_r01_a_strafer_from_a_right_entry_starts_just_right_of_the_playfield() -> None:
    kind = next(k for k in ENEMY_KINDS if k.id == "strafer")
    (strafer,) = kind.spawn(area(width=400, side="right", position=0.3))
    assert strafer.x == pytest.approx(400 + ENEMY_SPAWN_MARGIN)


def test_p05_r01_a_side_pass_follows_the_entry_side_and_height() -> None:
    from_left, y = side_pass(area(width=400, height=600, side="left", position=0.5), 0.2)
    assert from_left is True
    assert y == pytest.approx(300)
    from_right, y = side_pass(area(width=400, height=600, side="right", position=0.5), 0.2)
    assert from_right is False


def test_p05_r01_a_side_pass_without_an_entry_takes_its_own_height() -> None:
    _, y = side_pass(area(width=400, height=600), 0.25)
    assert y == pytest.approx(150)


# BUG: the joints of hydra, juggernaut and scissor are config records (see test_juggernaut.py).
JOINTED = {"hydra", "juggernaut", "scissor"}


@pytest.mark.parametrize(
    "kind",
    [
        pytest.param(
            k,
            marks=pytest.mark.xfail(
                strict=True, raises=TypeError, reason="BUG: config joints read as snake_case"
            )
            if k.id in JOINTED
            else (),
            id=k.id,
        )
        for k in ENEMY_KINDS
    ],
)
@pytest.mark.parametrize("side", [None, "top", "left", "right"])
def test_p05_r01_every_kind_spawns_a_group_from_any_wave_entry(kind, side) -> None:
    group = kind.spawn(area(width=400, height=600, side=side, position=0.4))
    assert group
    for enemy in group:
        assert enemy.health > 0
