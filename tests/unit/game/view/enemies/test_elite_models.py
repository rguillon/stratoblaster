"""Unit tests of `src/game/view/enemies/elite_models.py`."""

from game.view.enemies.elite_models import ELITE_MODELS


def test_enm_01_the_five_elite_kinds_have_their_builders():
    """Each elite kind has its model (ENM-HYDRA-01, ENM-ORBITER-01, ENM-SCISSOR-01,
    ENM-JUGGERNAUT-01, ENM-HIVE-01)."""
    assert set(ELITE_MODELS) == {"hydra", "orbiter", "scissor", "juggernaut", "hive"}
    assert ELITE_MODELS["hydra"].__name__ == "build_hydra"
    assert ELITE_MODELS["orbiter"].__name__ == "build_orbiter"
    assert ELITE_MODELS["scissor"].__name__ == "build_scissor"
    assert ELITE_MODELS["juggernaut"].__name__ == "build_juggernaut"
    assert ELITE_MODELS["hive"].__name__ == "build_hive"
