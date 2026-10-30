"""Unit tests of `src/game/config/tile_model.py`."""

from game.config.tile_model import model


def test_p15_r09_a_model_id_names_its_archetype_and_its_tile_footprint() -> None:
    m = model("foundry", 3, 4)
    assert m.id == "tile-foundry-3x4"
    assert m.archetype == "foundry"
    assert m.tiles == [3, 4]
    assert m.seed == 1


def test_p15_r09_a_second_variant_of_a_footprint_gets_its_seed_in_the_id() -> None:
    m = model("foundry", 2, 2, 2)
    assert m.id == "tile-foundry-2x2-2"
    assert m.seed == 2
