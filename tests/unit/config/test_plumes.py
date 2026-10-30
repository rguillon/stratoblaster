"""Unit tests of `src/config/plumes.py`."""

from config.plumes import PLUME_KINDS


def test_p10_r08_there_are_smoke_and_steam_plumes() -> None:
    assert set(PLUME_KINDS) == {"smoke", "steam"}


def test_p10_r08_every_plume_rises_with_growing_puffs_that_stay_faint() -> None:
    for kind in PLUME_KINDS.values():
        assert kind.puffs > 0
        assert kind.seconds > 0
        assert kind.height > 0
        assert 0 < kind.size[0] < kind.size[1]
        assert 0 < kind.alpha <= 1
        assert 0 <= kind.self_lit <= 1
        assert all(0 <= channel <= 1 for channel in kind.color)


def test_p10_r08_smoke_is_taller_and_slower_than_steam() -> None:
    smoke = PLUME_KINDS["smoke"]
    steam = PLUME_KINDS["steam"]
    assert smoke.height > steam.height
    assert smoke.seconds > steam.seconds
