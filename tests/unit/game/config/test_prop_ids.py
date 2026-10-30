"""Unit tests of `src/game/config/prop_ids.py`."""

from game.config.prop_ids import PROP_IDS


def test_p04_r04_prop_ids_are_unique_and_well_formed() -> None:
    ids = list(PROP_IDS.values())
    assert len(set(ids)) == len(ids)
    for prop_id in ids:
        assert prop_id == prop_id.lower() and " " not in prop_id, prop_id
