# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/core/content/game_definition.py`."""

from core.content.game_definition import GameDefinition, LogicalScreen


def test_logical_screen_keeps_its_size() -> None:
    screen = LogicalScreen(640, 360)
    assert (screen.width, screen.height) == (640, 360)
    assert screen.viewport is None


def test_game_screen_01_a_playfield_window_is_a_screen_laid_in_a_viewport() -> None:
    """D-252."""
    window = LogicalScreen(540, 720, (0.25, 0, 0.5, 1))
    assert window.viewport == (0.25, 0, 0.5, 1)


def test_game_definition_keeps_every_field_in_order() -> None:
    names = [
        "id",
        "title",
        "screen",
        "player_ships",
        "player_weapons",
        "levels",
        "game_levels",
        "enemy_kinds",
        "boss_kinds",
        "boss_fights",
        "bonuses",
        "bombs",
        "hull",
        "texts",
        "view",
    ]
    values = {name: object() for name in names}
    values["id"] = "stratoblaster"
    values["title"] = "Stratoblaster"
    values["screen"] = LogicalScreen(640, 360)  # the default playfield is built from it
    # By position, in the order of the fields (ENG-151).
    definition = GameDefinition(*[values[name] for name in names])  # type: ignore[arg-type]
    for name in names:
        assert getattr(definition, name) is values[name]


def test_game_screen_01_the_playfield_is_the_whole_screen_unless_a_window_is_given() -> None:
    """D-252."""
    screen = LogicalScreen(640, 360)
    rest = [object()] * 12
    whole = GameDefinition("g", "G", screen, *rest)  # type: ignore[arg-type]
    assert (whole.playfield.width, whole.playfield.height) == (640, 360)
    assert whole.playfield.viewport is None
    window = LogicalScreen(320, 360, (0.25, 0, 0.5, 1))
    framed = GameDefinition("g", "G", screen, *rest, window)  # type: ignore[arg-type]
    assert framed.playfield is window
