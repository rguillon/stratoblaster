"""Gamepad -> menu actions (P01-R10), ported from `input/gamepad-menu-input.ts`, polled once per
frame. Buttons fire on press; the D-pad and the left stick repeat while held. All connected
gamepads are merged."""

import math

from org.transcrypt.stubs.browser import __pragma__

from input.hold_repeater import HoldRepeater
from input.menu_action import is_menu_direction

__pragma__("skip")
from collections.abc import Callable, Mapping, Sequence  # noqa: E402
from typing import Any, Protocol  # noqa: E402

from input.keyboard_menu_input import RepeatTiming  # noqa: E402
from input.menu_action import MenuAction, MenuDirection  # noqa: E402


class _Button(Protocol):
    @property
    def pressed(self) -> bool: ...


class GamepadLike(Protocol):
    """The parts of a `Gamepad` the menu input reads."""

    @property
    def buttons(self) -> Sequence[_Button]: ...

    @property
    def axes(self) -> Sequence[float]: ...


# Returns the connected gamepads, like `navigator.getGamepads()`.
GamepadSource = Callable[[], Sequence[GamepadLike | None]]


class GamepadMenuBindings(RepeatTiming, Protocol):
    """Gamepad mapping and stick settings."""

    @property
    def gamepad_buttons(self) -> Mapping[int, MenuAction]: ...

    @property
    def gamepad_stick(self) -> "_Stick": ...

    @property
    def gamepad_dead_zone(self) -> float: ...


class _Stick(Protocol):
    @property
    def x_axis(self) -> int: ...

    @property
    def y_axis(self) -> int: ...


__pragma__("noskip")


def axis_value(axes: Sequence[float], index: int) -> float:
    value = axes[index] if 0 <= index < len(axes) else None
    return 0 if value is None else value


def stick_direction(x: float, y: float, dead_zone: float) -> MenuDirection | None:
    """Direction of a stick tilt, or None inside the dead zone (P01-R10)."""
    if math.hypot(x, y) < dead_zone:
        return None
    if abs(x) >= abs(y):
        return "right" if x > 0 else "left"
    return "down" if y > 0 else "up"


def _add(items: list[str], item: str) -> None:
    """Adds `item` to an insertion-ordered set (a list, as the order of the actions matters)."""
    if item not in items:
        items.append(item)


class GamepadMenuInput:
    """Gamepad -> menu actions (see the module doc)."""

    def __init__(self, source: GamepadSource, bindings: GamepadMenuBindings) -> None:
        self._source = source
        self._bindings = bindings
        self._repeater = HoldRepeater(
            bindings.repeat_delay_seconds, bindings.repeat_interval_seconds
        )
        self._pressed_buttons: list[str] = []

    def _read_held(self) -> list[str]:
        held: list[str] = []
        buttons = self._bindings.gamepad_buttons
        stick = self._bindings.gamepad_stick
        dead_zone = self._bindings.gamepad_dead_zone
        for pad in self._source():
            if not pad:
                continue
            for i in range(len(pad.buttons)):
                action = buttons.get(i)
                if pad.buttons[i].pressed and action is not None:
                    _add(held, action)
            x = axis_value(pad.axes, stick.x_axis)
            y = axis_value(pad.axes, stick.y_axis)
            tilt = stick_direction(x, y, dead_zone)
            if tilt is not None:
                _add(held, tilt)
        return held

    def update(self, dt_seconds: float) -> list[MenuAction]:
        """Polls the gamepads and returns the actions of this frame."""
        held = self._read_held()
        actions: list[MenuAction] = []
        for direction in self._repeater.held:
            if direction not in held:
                self._repeater.release(direction)
        repeats = self._repeater.update(dt_seconds)
        for action in held:
            if is_menu_direction(action):
                if self._repeater.press(action):
                    actions.append(action)
            elif action not in self._pressed_buttons:
                actions.append(action)
        self._pressed_buttons = held
        actions.extend(repeats)
        return actions


def browser_gamepads(nav: Any) -> GamepadSource:
    """Gamepad source reading `navigator.getGamepads()`, or no gamepad when unsupported."""

    def read() -> Sequence[GamepadLike | None]:
        if hasattr(nav, "getGamepads"):
            pads: Sequence[GamepadLike | None] = nav.getGamepads()
            return pads
        return []

    return read
