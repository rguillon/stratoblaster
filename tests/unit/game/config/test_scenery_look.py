"""Unit tests of `src/game/config/scenery_look.py`."""

from game.config.scenery_look import BASE_SCENERY_LOOK, PLAYFIELD_CAMERA, texture


def test_p04_r05_texture_is_its_colours_and_frequency() -> None:
    t = texture(["a", "b"], 0.5)
    assert t.colors == ["a", "b"]
    assert t.frequency == 0.5
    assert "cracks" not in t


def test_p04_r05_texture_takes_the_optional_fields_it_is_given() -> None:
    t = texture(["a"], 1, {"speckle": 0.2, "cracks": 0.1})
    assert t.speckle == 0.2
    assert t.cracks == 0.1


def test_p04_r05_the_base_scenery_look_has_every_section_the_scenery_reads() -> None:
    for name in ("sky", "fog", "sun", "ambient", "terrain", "sea", "clouds", "roads", "props"):
        assert BASE_SCENERY_LOOK[name] is not None, name


def test_p04_r05_the_playfield_camera_looks_down_the_screen() -> None:
    assert PLAYFIELD_CAMERA is not None
