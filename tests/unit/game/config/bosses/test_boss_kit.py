"""Unit tests of `src/game/config/bosses/boss_kit.py`."""

import pytest

from game.config.bosses.boss_kit import (
    BOSS_TIMING,
    MISSILE,
    bullet,
    bursting,
    cells,
    laser_of,
    mirror,
    only_after,
    only_while,
    part,
    stages,
    stats,
    twin,
    volley,
    volley_muzzles,
    volley_on_turret,
    with_own_lasers,
)
from game.config.enemies import ENEMY_UNIT
from game.config.record import record
from game.config.scoring import boss_part_points


def _design(guns: dict, shots: list) -> object:
    """A design with the given guns, its one stage firing `shots`."""
    return record({"id": "test-boss", "guns": guns, "stages": [shots], "rage": None})


def test_p07_r05_twin_puts_two_muzzles_either_side_of_the_centre_line() -> None:
    assert twin(10, 0, 3) == [[10, 0, 3], [-10, 0, 3]]


def test_p07_r05_twin_with_a_gap_spreads_the_pair_around_x() -> None:
    assert twin(10, 0, 3, gap=4) == [[6, 0, 3], [14, 0, 3]]


def test_p07_r05_mirror_flips_every_muzzle_left_to_right() -> None:
    assert mirror([[1, 2, 3], [-4, 5, 6]]) == [[-1, 2, 3], [4, 5, 6]]


def test_p07_r05_cells_is_a_grid_of_missile_cells_in_x_then_y_order() -> None:
    assert cells([1, 2], [5, 6], 7) == [[1, 5, 7], [1, 6, 7], [2, 5, 7], [2, 6, 7]]


def test_p07_r05_part_takes_its_position_and_defaults_its_options() -> None:
    p = part("wing", [1.5, -2], 5, 100)
    assert (p["id"], p["x"], p["y"], p["radius"], p["health"]) == ("wing", 1.5, -2, 5, 100)
    assert p["shieldsCore"] is True
    assert p["dropChance"] == 0.5
    assert "orbits" not in p and "joint" not in p


def test_p07_r05_part_takes_its_given_options() -> None:
    p = part("arm", [0, 0], 4, 50, {"shields": False, "drop": 0.1, "orbits": True, "joint": "j"})
    assert p["shieldsCore"] is False
    assert p["dropChance"] == 0.1
    assert p["orbits"] is True
    assert p["joint"] == "j"


def test_p07_r05_stats_sizes_the_boss_from_its_size_in_enemy_units() -> None:
    s = stats(
        {
            "id": "b",
            "name": "B",
            "size": 4,
            "coreRadius": 20,
            "coreHealth": 900,
            "points": 1000,
            "groundSpeed": 0.5,
            "parts": [],
        }
    )
    assert s["radius"] == (4 * ENEMY_UNIT) / 2
    assert s["health"] == 900
    assert s["partPoints"] == boss_part_points(1000) == 100
    assert s["stagePause"] == BOSS_TIMING["stagePause"]
    assert "coreDropChance" not in s and "joints" not in s


def test_p07_r05_stats_adds_the_optional_core_drop_and_joints() -> None:
    s = stats(
        {
            "id": "b",
            "name": "B",
            "size": 2,
            "coreRadius": 10,
            "coreHealth": 1,
            "points": 0,
            "groundSpeed": 0,
            "parts": [],
            "coreDrop": 0.25,
            "joints": {"j": 1},
        }
    )
    assert s["coreDropChance"] == 0.25
    assert s["joints"] == {"j": 1}


def test_p07_r05_stages_fires_each_stage_with_the_parts_volleys_and_its_own_core_volleys() -> None:
    parts = [{"from": "p"}]
    core = [[{"from": "core", "n": 1}], [{"from": "core", "n": 2}]]
    out = stages(parts, core)
    assert out == [
        [{"from": "p"}, {"from": "core", "n": 1}],
        [{"from": "p"}, {"from": "core", "n": 2}],
    ]


def test_p07_r05_only_while_and_only_after_tag_a_volley_with_its_part() -> None:
    shot = {"from": "core"}
    assert only_while(shot, "mast") == {"from": "core", "needs": "mast"}
    assert only_after(shot, "mast") == {"from": "core", "after": "mast"}
    assert shot == {"from": "core"}


def test_p07_r05_bullet_and_missile_and_laser_carry_their_style() -> None:
    assert bullet("dart", 90) == {"speed": 90, "radius": 4, "style": "dart"}
    assert bullet("dart", 90, 7)["radius"] == 7
    assert MISSILE["style"] == "rocketeer" and MISSILE["homingSeconds"] == 3
    laser = laser_of(2.5, 9)
    assert laser == {"warningSeconds": 1, "firingSeconds": 2.5, "width": 9, "style": "lancer"}


def test_p07_r05_bursting_splits_the_spec_into_after_count_and_small_bullet() -> None:
    small = bullet("small", 60, 2)
    b = bursting("cryo", 40, 9, [1.5, 6, small])
    assert b["speed"] == 40 and b["radius"] == 9 and b["style"] == "cryo"
    assert b["burst"] == {"after": 1.5, "count": 6, "bullet": small}


def test_p07_r05_volley_builders_set_the_shape_kind_and_the_optional_first_shot() -> None:
    b = bullet("x", 1)
    aimed = volley.aimed("core", 2, 3, 10, b)
    assert aimed["from"] == "core" and aimed["every"] == 2
    assert aimed["shape"] == {"kind": "aimed", "count": 3, "spacingDeg": 10, "bullet": b}
    assert "first" not in aimed
    fan = volley.fan("p", 1, 5, 8, b, 0.5, 30)
    assert fan["first"] == 0.5
    assert fan["shape"]["headingDeg"] == 30
    ring = volley.ring("core", 4, 8, 15, b)
    assert ring["shape"] == {"kind": "ring", "count": 8, "turnDeg": 15, "bullet": b}
    burst = volley.burst("core", 3, 2, 0.1, b)
    assert burst["shape"]["kind"] == "burst" and burst["shape"]["gap"] == 0.1
    missiles = volley.missiles("core", 6, 2, 20, 1)
    assert missiles["shape"]["missile"] == MISSILE and missiles["first"] == 1
    laser = volley.laser("core", 5, 1.5)
    assert laser["shape"]["kind"] == "laser"
    assert laser["shape"]["laser"]["firingSeconds"] == 1.5


def test_p07_r05_volley_muzzles_picks_the_guns_its_kind_fires_from() -> None:
    guns = {"gun": [[0, 0, 1]], "ring": [[1, 1, 1]], "missile": [[2, 2, 1]], "laser": [[3, 3, 1]]}
    b = bullet("x", 1)
    design = _design({"core": guns}, [])
    assert volley_muzzles(design, volley.aimed("core", 1, 1, 0, b)) == [[0, 0, 1]]
    assert volley_muzzles(design, volley.ring("core", 1, 1, 0, b)) == [[1, 1, 1]]
    assert volley_muzzles(design, volley.missiles("core", 1, 1, 0)) == [[2, 2, 1]]
    assert volley_muzzles(design, volley.laser("core", 1, 1)) == [[3, 3, 1]]
    assert volley_muzzles(design, volley.burst("core", 1, 1, 0, b)) == [[0, 0, 1]]


def test_p07_r05_volley_muzzles_fires_a_ring_from_the_gun_when_it_has_no_ring() -> None:
    design = _design({"core": {"gun": [[0, 0, 1]]}}, [])
    ring = volley.ring("core", 1, 1, 0, bullet("x", 1))
    assert volley_muzzles(design, ring) == [[0, 0, 1]]


def test_p07_r05_volley_muzzles_is_empty_for_a_launch() -> None:
    design = _design({"core": {"gun": [[0, 0, 1]]}}, [])
    launch = {"from": "core", "shape": {"kind": "launch"}}
    assert volley_muzzles(design, launch) == []


@pytest.mark.xfail(
    strict=True,
    reason="BUG: CPython twin of volley_muzzles: `guns = {}` has no `.gun` attribute (the browser "
    "reads undefined, so no muzzles)",
)
def test_p07_r05_volley_muzzles_of_a_piece_without_guns_is_empty() -> None:
    no_guns = _design({"core": None}, [])
    assert volley_muzzles(no_guns, volley.aimed("core", 1, 1, 0, bullet("x", 1))) == []


def test_p07_r05_volley_on_turret_needs_a_turret_on_the_firing_piece() -> None:
    b = bullet("x", 1)
    aimed = volley.aimed("p", 1, 1, 0, b)
    on = _design({"p": {"turret": [0, 0], "gun": [[0, 0, 1]]}}, [])
    off = _design({"p": {"gun": [[0, 0, 1]]}}, [])
    assert volley_on_turret(on, aimed) is True
    assert volley_on_turret(off, aimed) is False
    assert volley_on_turret(_design({"p": None}, []), aimed) is False


def test_p07_r05_volley_on_turret_counts_lasers_only_when_the_turret_carries_them() -> None:
    laser = volley.laser("p", 1, 1)
    carried = _design({"p": {"turret": [0, 0], "turretLaser": True, "laser": [[0, 0, 1]]}}, [])
    not_carried = _design({"p": {"turret": [0, 0], "laser": [[0, 0, 1]]}}, [])
    assert volley_on_turret(carried, laser) is True
    assert volley_on_turret(not_carried, laser) is False


def test_p07_r05_with_own_lasers_recolours_every_laser_volley_with_the_design_id() -> None:
    laser = volley.laser("core", 5, 1)
    aimed = volley.aimed("core", 1, 1, 0, bullet("x", 1))
    design = record({"id": "boss-x", "guns": {}, "stages": [[laser, aimed]], "rage": [laser]})
    own = with_own_lasers(design)
    assert own["stages"][0][0]["shape"]["laser"]["style"] == "boss-x"
    assert own["stages"][0][1] == aimed
    assert own["rage"][0]["shape"]["laser"]["style"] == "boss-x"
    assert own["id"] == "boss-x"
    assert laser["shape"]["laser"]["style"] == "lancer"


def test_p07_r05_with_own_lasers_leaves_a_design_without_rage_alone() -> None:
    design = record({"id": "boss-y", "guns": {}, "stages": [[]], "rage": None})
    own = with_own_lasers(design)
    assert own["stages"] == [[]]
    assert own["rage"] is None
