"""Unit tests of `src/game/view/enemies/veteran_models.py`."""

from game.view.enemies.veteran_models import VETERAN_MODELS


def test_p05_r14_to_r18_the_five_veteran_kinds_have_their_builders():
    assert set(VETERAN_MODELS) == {"wasp", "mortar", "mantis", "phantom", "minelayer"}
    assert VETERAN_MODELS["wasp"].__name__ == "build_wasp"
    assert VETERAN_MODELS["mortar"].__name__ == "build_mortar"
    assert VETERAN_MODELS["mantis"].__name__ == "build_mantis"
    assert VETERAN_MODELS["phantom"].__name__ == "build_phantom"
    assert VETERAN_MODELS["minelayer"].__name__ == "build_minelayer"
