# Copyright (c) 2026 Renaud Guillon
"""The Lab bosses' shape helpers off their outlines' ends (specs/bosses/lab/).

Each boss's outline helper reads its stations between its ends, and a flat value past them; a gun
on a fort's face points away from its centre, whichever way round the face is given.
"""

import pytest

from game.config.bosses.lab import (
    aegis_wing,
    cloud_dreadnought,
    condor_lifter,
    gale_corvette,
    seaplane_leviathan,
    star_fort,
    stratoliner_colossus,
    swing_wing_titan,
    twin_boom_lancer,
)

FAR = 10_000.0


def test_the_aegis_wing_s_edges_reach_its_tip_and_stop_past_its_sawtooth() -> None:
    wing = aegis_wing.WING
    assert aegis_wing.leading_y(0) == pytest.approx(wing[0][1])
    assert aegis_wing.leading_y(wing[2][0]) == pytest.approx(wing[2][1])
    assert aegis_wing.trailing_y(FAR) == wing[len(wing) - 1][1]


def test_the_cloud_dreadnought_s_hull_is_closed_before_its_bow_and_flat_past_its_stern() -> None:
    hull = cloud_dreadnought.HULL
    assert cloud_dreadnought.half_width(hull[0][0] - 1) == 0
    assert cloud_dreadnought.half_width(FAR) == hull[len(hull) - 1][1]


def test_a_fuselage_or_an_envelope_is_nothing_off_its_ends() -> None:
    assert condor_lifter.fuselage_at(FAR) == [0, 0, 0]
    assert stratoliner_colossus.fuselage_at(FAR) == [0, 0, 0]
    assert swing_wing_titan.fuselage_at(FAR, 1) == 0
    assert gale_corvette.envelope_radius(FAR) == 0
    assert twin_boom_lancer.pod_top(FAR) == 0


def test_a_seaplane_leviathan_part_takes_more_options() -> None:
    part = seaplane_leviathan.fpart("hidden", [0, 0], 5, 10, {"reveal": 1})
    assert part.reveal == 1
    assert part.dropChance == 0.6


def test_a_star_fort_face_gun_points_out_whichever_way_round_its_face_is() -> None:
    a = [10.0, 0.0]
    b = [0.0, 10.0]
    one = star_fort.face_gun(a, b, 0.5, 1)
    other = star_fort.face_gun(b, a, 0.5, 1)
    assert one == pytest.approx(other)
    # Inset towards the centre from the face's middle (5, 5).
    assert one[0] < 5
    assert one[1] < 5
