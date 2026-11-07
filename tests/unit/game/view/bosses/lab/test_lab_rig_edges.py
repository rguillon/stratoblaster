# Copyright (c) 2026 Renaud Guillon
"""The Lab bosses' rigs and drawings at their edges (specs/bosses/lab/).

What the whole fights (`test_boss_models_live.py`) never meet: a region, part or mount a rig asks
for that its boss lacks, a boss without the part it looks for, a rope of no length, an outline read
past its ends, a shutter fully open, a bell whose belfry is gone, rotors stopping just short of a
blade.
"""

import math
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest
from helpers.bosses_top_fakes import FakeNode

from game.view.bosses import scorpion_model, storm_petrel_struts
from game.view.bosses.lab import (
    anvil_barge_parts,
    anvil_barge_rig,
    aqueduct_leviathan_rig,
    bell_keep_rig,
    bunker_saucer_rig,
    canard_gunship_rig,
    condor_lifter_rig,
    drill_fort_rig,
    gale_corvette_model,
    mortar_raft_parts,
    orbital_foundry_parts,
    rotor_bastion_rotors,
    seaplane_leviathan_model,
    sky_carrier_model,
    skyport_hub_rig,
    star_fort_rig,
    tiltrotor_behemoth_rig,
    twin_boom_lancer_rig,
    zeppelin_citadel_envelopes,
    zeppelin_citadel_rig,
)

FAR = 10_000.0


@pytest.mark.parametrize(
    "find",
    [
        anvil_barge_rig._region,
        bell_keep_rig._region,
        bunker_saucer_rig._region,
        rotor_bastion_rotors._region,
        skyport_hub_rig._region,
        star_fort_rig._region,
        zeppelin_citadel_rig._region,
        scorpion_model._mount,
        storm_petrel_struts._battery,
    ],
)
def test_a_region_part_or_mount_its_boss_lacks_is_an_error(find: Any) -> None:
    with pytest.raises(ValueError, match="nope"):
        find("nope")


def test_a_part_or_mount_its_boss_lacks_has_no_index() -> None:
    assert bell_keep_rig._part_index("nope") == -1
    assert skyport_hub_rig._part_index("nope") == -1
    assert bunker_saucer_rig._mount_index("nope") == -1


def test_a_region_its_design_lacks_is_none(monkeypatch: pytest.MonkeyPatch) -> None:
    bare = SimpleNamespace(armour=[])
    monkeypatch.setattr(canard_gunship_rig, "CANARD_GUNSHIP", bare)
    monkeypatch.setattr(orbital_foundry_parts, "ORBITAL_FOUNDRY", bare)
    monkeypatch.setattr(tiltrotor_behemoth_rig, "TILTROTOR_BEHEMOTH", bare)
    monkeypatch.setattr(twin_boom_lancer_rig, "TWIN_BOOM_LANCER", bare)
    assert canard_gunship_rig.door_region(0) is None
    assert orbital_foundry_parts._region("nope") is None
    assert tiltrotor_behemoth_rig.wing_region("left") is None
    assert twin_boom_lancer_rig._region(1) is None


def test_a_boss_without_the_part_a_rig_looks_for_has_it_standing() -> None:
    bare = SimpleNamespace(parts=[])
    assert aqueduct_leviathan_rig._broken(bare, "nope") is False
    assert drill_fort_rig._drill_broken(bare) is False
    assert condor_lifter_rig._destroyed(bare, "nope") is False
    assert tiltrotor_behemoth_rig._cannon_stands(bare, 0) is True
    assert tiltrotor_behemoth_rig._cannon_stands(SimpleNamespace(parts=None), 1) is True


def test_a_rope_of_no_length_is_not_drawn() -> None:
    layer = MagicMock()
    mortar_raft_parts.rope(layer, [1, 2, 3], [1, 2, 3], 0.5, [0, 0, 0])
    layer.box.assert_not_called()


def test_an_outline_read_past_its_ends_is_flat() -> None:
    assert anvil_barge_parts._horn_half_width(FAR) == 0
    assert seaplane_leviathan_model._x_at([[0, 0], [5, 5]], FAR) == 0
    profile = zeppelin_citadel_envelopes.PROFILE
    assert zeppelin_citadel_envelopes.radius_at(FAR) == profile[len(profile) - 1][1]


def test_a_sky_carrier_cut_past_its_outline_closes_on_the_centre_line() -> None:
    right = [[0.0, 0.0], [5.0, 5.0], [0.0, 10.0]]
    assert sky_carrier_model._x_at(right, FAR) == 0
    cut = sky_carrier_model._cut(right, 2, FAR)
    assert cut[0] == [0, 2]
    assert cut[len(cut) - 1] == [0, FAR]
    assert [5.0, 5.0] in cut


def test_a_gale_corvette_envelope_too_thin_for_rivets_has_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def boxes(rivet_x: float) -> int:
        monkeypatch.setattr(gale_corvette_model, "RIVET_X", rivet_x)
        p = MagicMock()
        gale_corvette_model._envelope(p)
        return len(p.bare.box.call_args_list)

    riveted = boxes(gale_corvette_model.RIVET_X)
    assert boxes(FAR) < riveted


def _model() -> Any:
    return SimpleNamespace(sync=MagicMock())


def test_the_bell_swings_on_when_its_belfry_is_not_among_the_boss_s_parts() -> None:
    rig = object.__new__(bell_keep_rig.KeepRig)
    node = FakeNode("bell", None)
    rig.bell = [node, _model()]
    rig.belfry = 99
    rig.clock = 0.0
    rig._show_bell(SimpleNamespace(age=1.0, form=0, parts=[]), None, 0.1)
    assert node.enabled is True
    rig.bell[1].sync.assert_called_once()


def test_a_shutter_fully_open_is_hidden() -> None:
    rig = object.__new__(bunker_saucer_rig.SaucerRig)
    node = FakeNode("shutter", None)
    shutter = [node, _model(), 0, [1, 0]]
    boss = SimpleNamespace(age=100.0, mounts=[SimpleNamespace(shown_at=0.0)])
    rig._show_shutter(shutter, boss, None, 0.1)
    assert node.enabled is False
    shutter[1].sync.assert_not_called()


def test_rotors_stopping_just_short_of_a_blade_turn_on_to_the_next() -> None:
    rig = object.__new__(tiltrotor_behemoth_rig.BehemothRig)
    third = tiltrotor_behemoth_rig.THIRD
    rig.spin = [third - 0.5, 0.0]
    rig.stopping = False
    rig.stop_from = [0.0, 0.0]
    rig.stop_at = [0.0, 0.0]
    rig._spin(0.05, 0.1)
    # Not a sudden stop half a radian on: round to the blade after.
    assert rig.stop_at[0] - rig.stop_from[0] == pytest.approx(0.5 + third)
    assert rig.stop_at[1] - rig.stop_from[1] == pytest.approx(third)
    assert math.isfinite(rig.spin[0])
