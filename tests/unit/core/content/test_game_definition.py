"""Unit tests of `src/core/content/game_definition.py`."""

from core.content.game_definition import GameDefinition, LogicalScreen


def test_logical_screen_keeps_its_size() -> None:
    screen = LogicalScreen(640, 360)
    assert (screen.width, screen.height) == (640, 360)


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
    definition = GameDefinition(**values)  # type: ignore[arg-type]
    for name in names:
        assert getattr(definition, name) is values[name]
