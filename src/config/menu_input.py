"""Menu input mapping and feel (P01-R09, P01-R10, P01-R12, P12-R01)

Kept in config so it can be remapped later (ENG-112).
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Literal  # noqa: E402

# The abstract menu actions; it is only
# used to type the mappings here, so it is defined here rather than on its own.
MenuAction = Literal["up", "down", "left", "right", "confirm", "back", "cancel", "pause", "resume"]
__pragma__("noskip")


class MenuGamepadStick:
    """Left stick axes of the standard mapping (+X right, +Y down)."""

    def __init__(self, x_axis: float, y_axis: float) -> None:
        self.x_axis = x_axis
        self.y_axis = y_axis


class MenuInputConfig:
    """The menu input tunables, in the order of `MENU_INPUT_CONFIG`."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        keyboard: dict[str, MenuAction],
        gamepad_buttons: dict[int, MenuAction],
        gamepad_stick: MenuGamepadStick,
        gamepad_dead_zone: float,
        repeat_delay_seconds: float,
        repeat_interval_seconds: float,
    ) -> None:
        # `KeyboardEvent.code` -> action: physical key positions, so AZERTY works too.
        self.keyboard = keyboard
        # Standard-mapping gamepad button index -> action (A = 0, B = 1, Select / View = 8,
        # Start = 9, D-pad = 12..15).
        self.gamepad_buttons = gamepad_buttons
        self.gamepad_stick = gamepad_stick
        # `gamepad_dead_zone`: stick magnitude below which input is ignored.
        self.gamepad_dead_zone = gamepad_dead_zone
        # `menu_repeat_delay`: hold time before a held direction starts repeating.
        self.repeat_delay_seconds = repeat_delay_seconds
        # `menu_repeat_interval`: time between repeats while held.
        self.repeat_interval_seconds = repeat_interval_seconds


MENU_INPUT_CONFIG = MenuInputConfig(
    {
        "ArrowUp": "up",
        "ArrowDown": "down",
        "ArrowLeft": "left",
        "ArrowRight": "right",
        "KeyW": "up",
        "KeyS": "down",
        "KeyA": "left",
        "KeyD": "right",
        "Enter": "confirm",
        "NumpadEnter": "confirm",
        "Space": "confirm",
        # Back on the menu screens, pause in a level (GD §2, P12-R01).
        "Escape": "cancel",
        "Backspace": "back",
        "KeyP": "pause",
    },
    {
        0: "confirm",
        1: "back",
        8: "pause",
        9: "pause",
        12: "up",
        13: "down",
        14: "left",
        15: "right",
    },
    MenuGamepadStick(0, 1),
    0.35,
    0.35,
    0.12,
)
