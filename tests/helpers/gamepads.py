"""Fake gamepads for the input tests: a standard-mapping pad whose buttons and axes are set by the
test. Both the menu input and the game controls poll pads of this shape."""


class FakeButton:
    def __init__(self, pressed: bool = False) -> None:
        self.pressed = pressed


class FakeGamepad:
    """A gamepad with `button_count` buttons (all up) and `axis_count` axes (all at rest)."""

    def __init__(self, button_count: int = 17, axis_count: int = 4) -> None:
        self.buttons = [FakeButton() for _ in range(button_count)]
        self.axes = [0.0] * axis_count

    def press(self, *indices: int) -> "FakeGamepad":
        for index in indices:
            self.buttons[index].pressed = True
        return self

    def release(self, *indices: int) -> "FakeGamepad":
        for index in indices:
            self.buttons[index].pressed = False
        return self

    def tilt(self, x: float, y: float) -> "FakeGamepad":
        """Sets the left stick (axes 0 and 1 of the standard mapping)."""
        self.axes[0] = x
        self.axes[1] = y
        return self
