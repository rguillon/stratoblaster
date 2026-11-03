# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/elite_models.py`."""

from game.view.enemies.elite_models import ELITE_MODELS


def test_enm_01_the_elite_era_kinds_have_their_builders() -> None:
    """Each elite kind has its model.

    Kinds: ENM-HYDRA-01, ENM-SCISSOR-01, ENM-JUGGERNAUT-01, ENM-HIVE-01.
    """
    assert set(ELITE_MODELS) == {"hydra", "scissor", "juggernaut", "hive"}
    assert ELITE_MODELS["hydra"].__name__ == "build_hydra"
    assert ELITE_MODELS["scissor"].__name__ == "build_scissor"
    assert ELITE_MODELS["juggernaut"].__name__ == "build_juggernaut"
    assert ELITE_MODELS["hive"].__name__ == "build_hive"
