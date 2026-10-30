"""Unit tests of `src/core/content/menu_texts.py`."""

import inspect

from core.content.menu_texts import MenuTexts


def _all_strings(**overrides: object) -> dict[str, object]:
    """Every parameter of `MenuTexts`, as a placeholder string unless overridden."""
    params = [p for p in inspect.signature(MenuTexts.__init__).parameters if p != "self"]
    values: dict[str, object] = {name: name for name in params}
    values.update(overrides)
    return values


def test_menu_texts_keeps_each_text_under_its_own_name() -> None:
    params = [p for p in inspect.signature(MenuTexts.__init__).parameters if p != "self"]
    values = {name: object() for name in params}
    texts = MenuTexts(**values)  # type: ignore[arg-type]
    for name in params:
        assert getattr(texts, name) is values[name]


def test_menu_texts_has_the_functions_of_its_parameterised_texts() -> None:
    def game_level(label: str) -> str:
        return "Level " + label

    texts = MenuTexts(**_all_strings(game_level=game_level))  # type: ignore[arg-type]
    assert texts.game_level("1-1") == "Level 1-1"
