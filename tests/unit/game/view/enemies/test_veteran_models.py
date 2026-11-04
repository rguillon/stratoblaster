# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/veteran_models.py`."""

from game.view.enemies.veteran_models import VETERAN_MODELS


def test_enm_01_the_veteran_era_kinds_have_their_builders() -> None:
    """Each veteran kind has its model.

    Kinds: ENM-WASP-01, ENM-MORTAR-01, ENM-PHANTOM-01.
    """
    assert set(VETERAN_MODELS) == {"wasp", "mortar", "phantom"}
    assert VETERAN_MODELS["wasp"].__name__ == "build_wasp"
    assert VETERAN_MODELS["mortar"].__name__ == "build_mortar"
    assert VETERAN_MODELS["phantom"].__name__ == "build_phantom"
