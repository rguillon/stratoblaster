"""In-game controls (GD §2, GD-10, P06-R02, P11-R06)

Which keys and gamepad buttons shoot and set bombs off, and how the left stick and the touch drag
move the ship. Kept in config so they can be remapped later (ENG-112). Moving uses the arrows /
WASD by key position (`HeldDirections`).
"""


class DpadButtons:
    """D-pad buttons of the standard mapping: up, down, left, right."""

    def __init__(self, up: float, down: float, left: float, right: float) -> None:
        self.up = up
        self.down = down
        self.left = left
        self.right = right


class GameStick:
    """Left stick axes (+X right, +Y down) and the tilt below which it is ignored."""

    def __init__(self, x_axis: float, y_axis: float, dead_zone: float) -> None:
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.dead_zone = dead_zone


class GameControlsConfig:
    """The in-game controls, in the order of `GAME_CONTROLS_CONFIG`."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        fire_keys: list[str],
        switch_keys: list[str],
        bomb_keys: list[str],
        fire_buttons: list[float],
        bomb_buttons: list[float],
        dpad: DpadButtons,
        stick: GameStick,
        acceleration_seconds: float,
    ) -> None:
        # `KeyboardEvent.code` of the keys that shoot while held.
        self.fire_keys = fire_keys
        # Keys that switch to the next weapon, once per press (phase 6 review: E, by position).
        self.switch_keys = switch_keys
        # Keys that set a bomb off, once per press (P11-R06): R and the left Shift, by position.
        self.bomb_keys = bomb_keys
        # Standard-mapping gamepad buttons that shoot while held: A, and the right trigger.
        self.fire_buttons = fire_buttons
        # Gamepad buttons that set a bomb off, once per press (P11-R06): X / Square and LB.
        self.bomb_buttons = bomb_buttons
        self.dpad = dpad
        self.stick = stick
        # Seconds from rest to full speed (GD-10, phase 6 review, from 0.08 s).
        self.acceleration_seconds = acceleration_seconds


GAME_CONTROLS_CONFIG = GameControlsConfig(
    ["Space"],
    ["KeyE"],
    ["KeyR", "ShiftLeft"],
    [0, 7],
    [2, 4],
    DpadButtons(12, 13, 14, 15),
    GameStick(0, 1, 0.2),
    0.18,
)
