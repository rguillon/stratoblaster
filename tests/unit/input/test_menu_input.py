"""Unit tests of `src/input/menu_input.py`."""

from input.menu_input import MenuInput


class FakeSource:
    def __init__(self, actions: list[str]) -> None:
        self.actions = actions
        self.dts: list[float] = []

    def update(self, dt_seconds: float) -> list[str]:
        self.dts.append(dt_seconds)
        return list(self.actions)


def test_p01_r12_actions_of_every_device_are_merged_in_source_order() -> None:
    keyboard = FakeSource(["up"])
    pad = FakeSource(["confirm", "back"])
    menu = MenuInput([keyboard, pad])
    assert menu.update(0.5) == ["up", "confirm", "back"]
    assert keyboard.dts == [0.5]
    assert pad.dts == [0.5]


def test_p01_r12_no_source_gives_no_action() -> None:
    assert MenuInput([]).update(1.0) == []
