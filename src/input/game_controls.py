"""The player's in-game controls (P06-R02, GD §2): arrows /
WASD (by key position) or the left stick / D-pad move, Space or the gamepad button shoots while
held, and on touch screens the ship follows the finger dragged anywhere while the on-screen button
shoots. E switches the weapon; R, the left Shift, a gamepad button or the on-screen bomb button set
a bomb off (P11-R06). All devices are merged."""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.systems.player_flight import FlightInput
from input.gamepad_menu_input import axis_value
from input.held_directions import HeldDirections

__pragma__("skip")
from collections.abc import Sequence  # noqa: E402
from typing import Protocol  # noqa: E402

from input.gamepad_menu_input import GamepadLike, GamepadSource  # noqa: E402


class _Dpad(Protocol):
    @property
    def up(self) -> int: ...

    @property
    def down(self) -> int: ...

    @property
    def left(self) -> int: ...

    @property
    def right(self) -> int: ...


class _Stick(Protocol):
    @property
    def x_axis(self) -> int: ...

    @property
    def y_axis(self) -> int: ...

    @property
    def dead_zone(self) -> float: ...


class GameControlBindings(Protocol):
    """Which inputs shoot and move the ship."""

    @property
    def fire_keys(self) -> Sequence[str]: ...

    @property
    def switch_keys(self) -> Sequence[str]: ...

    @property
    def bomb_keys(self) -> Sequence[str]:
        """Keys that set a bomb off, once per press (P11-R06)."""
        ...

    @property
    def fire_buttons(self) -> Sequence[int]: ...

    @property
    def bomb_buttons(self) -> Sequence[int]:
        """Gamepad buttons that set a bomb off, once per press (P11-R06)."""
        ...

    @property
    def dpad(self) -> _Dpad: ...

    @property
    def stick(self) -> _Stick: ...


__pragma__("noskip")


class ControlState:
    """The controls of one simulation step."""

    def __init__(self, move: FlightInput, fire: bool, switch_weapon: bool, bomb: bool) -> None:
        self.move = move
        self.fire = fire
        # Switch to the next weapon (once per press).
        self.switch_weapon = switch_weapon
        # Set a bomb off (once per press, P11-R06).
        self.bomb = bomb


class _Presses:
    """Counts the presses of a set of keys: held keys repeat their key-downs, which do not count."""

    def __init__(self) -> None:
        self._held: list[str] = []
        self.count = 0

    def key(self, codes: Sequence[str], code: str, down: bool) -> bool:
        """Whether `code` is one of `codes`; a press if it goes down while not held."""
        if code not in codes:
            return False
        if down and code not in self._held:
            self.count += 1
        if down:
            if code not in self._held:
                self._held.append(code)
        elif code in self._held:
            self._held.remove(code)
        return True

    def take(self) -> bool:
        """Takes one press, if there is one."""
        if self.count <= 0:
            return False
        self.count -= 1
        return True

    def clear(self) -> None:
        self._held.clear()
        self.count = 0


class _PadInput:
    """One gamepad's direction (Y up), and whether its fire and bomb buttons are down."""

    def __init__(self, x: float, y: float, fire: bool, bomb: bool) -> None:
        self.x = x
        self.y = y
        self.fire = fire
        self.bomb = bomb


def _no_gamepads() -> Sequence[GamepadLike | None]:
    return []


def _button_held(gamepad: GamepadLike, index: int) -> bool:
    buttons = gamepad.buttons
    return 0 <= index < len(buttons) and bool(buttons[index].pressed)


def _any_held(gamepad: GamepadLike, indices: Sequence[int]) -> bool:
    return any(_button_held(gamepad, index) for index in indices)


def _pad_input(gamepad: GamepadLike, bindings: GameControlBindings) -> _PadInput:
    """One gamepad's direction (the stronger of the stick and the D-pad, Y up) and buttons."""
    stick = bindings.stick
    dpad = bindings.dpad
    sx = axis_value(gamepad.axes, stick.x_axis)
    sy = -axis_value(gamepad.axes, stick.y_axis)
    px = sx if math.hypot(sx, sy) >= stick.dead_zone else 0
    py = sy if math.hypot(sx, sy) >= stick.dead_zone else 0
    bx = (1 if _button_held(gamepad, dpad.right) else 0) - (
        1 if _button_held(gamepad, dpad.left) else 0
    )
    by = (1 if _button_held(gamepad, dpad.up) else 0) - (
        1 if _button_held(gamepad, dpad.down) else 0
    )
    x = bx if math.hypot(bx, by) > math.hypot(px, py) else px
    y = by if math.hypot(bx, by) > math.hypot(px, py) else py
    return _PadInput(
        x,
        y,
        _any_held(gamepad, bindings.fire_buttons),
        _any_held(gamepad, bindings.bomb_buttons),
    )


class GameControls:
    """The player's in-game controls: all devices are merged (see the module doc)."""

    def __init__(
        self, bindings: GameControlBindings, gamepads: GamepadSource | None = None
    ) -> None:
        self._bindings = bindings
        self._gamepads: GamepadSource = gamepads if gamepads is not None else _no_gamepads
        self.keys = HeldDirections()
        self._fire_keys: list[str] = []
        self._switches = _Presses()
        self._bombs = _Presses()
        # Whether a gamepad's bomb button was down at the last read (a press is a new one).
        self._pad_bomb_held = False
        self._touch_fire = False
        # Drag distance not flown yet, in logical pixels.
        self._drag_x = 0.0
        self._drag_y = 0.0
        # Slot of the gamepad last used to play, if any (P12-R03).
        self._pad_in_use: int | None = None
        self._pad_lost = False

    def key(self, code: str, down: bool) -> bool:
        """A key going down or up (`code`: `KeyboardEvent.code`); whether it is a control."""
        if self.keys.key(code, down):
            return True
        if self._switches.key(self._bindings.switch_keys, code, down):
            return True
        if self._bombs.key(self._bindings.bomb_keys, code, down):
            return True
        if code not in self._bindings.fire_keys:
            return False
        if down:
            if code not in self._fire_keys:
                self._fire_keys.append(code)
        elif code in self._fire_keys:
            self._fire_keys.remove(code)
        return True

    def set_touch_fire(self, held: bool) -> None:
        """The on-screen fire button is held (`True`) or let go."""
        self._touch_fire = held

    def bomb(self) -> None:
        """The on-screen bomb button was tapped (P11-R06)."""
        self._bombs.count += 1

    def drag(self, dx: float, dy: float) -> None:
        """The finger moved by (`dx`, `dy`) logical pixels, Y up: the ship follows it."""
        self._drag_x += dx
        self._drag_y += dy

    def clear(self) -> None:
        """Lets go of everything (e.g. the window lost the focus, so key-ups would be missed)."""
        self.keys.clear()
        self._fire_keys.clear()
        self._switches.clear()
        self._bombs.clear()
        self._touch_fire = False
        self._drag_x = 0
        self._drag_y = 0

    def take_disconnect(self) -> bool:
        """Whether the gamepad that was in use has been disconnected since the last call (P12-R03:
        the level pauses). Reported once."""
        lost = self._pad_lost
        self._pad_lost = False
        return lost

    def read(self, dt: float, max_speed: float) -> ControlState:
        """The controls for a step of `dt` seconds of a ship flying at `max_speed`: the strongest of
        the keys, the gamepads and the drag, which is used up as the ship covers it."""
        pad = self._read_gamepads()
        keys = self.keys.direction
        move = (
            FlightInput(pad.x, pad.y)
            if math.hypot(pad.x, pad.y) > math.hypot(keys.x, keys.y)
            else keys
        )
        reach = max_speed * dt
        dragged = math.hypot(self._drag_x, self._drag_y)
        if dragged > 0 and reach > 0:
            share = min(1, reach / dragged)
            move = FlightInput((self._drag_x / reach) * share, (self._drag_y / reach) * share)
            self._drag_x -= self._drag_x * share
            self._drag_y -= self._drag_y * share
        if pad.bomb and not self._pad_bomb_held:
            self._bombs.count += 1
        self._pad_bomb_held = pad.bomb
        fire = len(self._fire_keys) > 0 or self._touch_fire or pad.fire
        switch_weapon = self._switches.take()
        bomb = self._bombs.take()
        return ControlState(move, fire, switch_weapon, bomb)

    def _read_gamepads(self) -> _PadInput:
        best = _PadInput(0, 0, False, False)
        fire = False
        bomb = False
        gamepads = self._gamepads()
        self._check_pad_in_use(gamepads)
        for slot in range(len(gamepads)):
            gamepad = gamepads[slot]
            if not gamepad:
                continue
            pad = _pad_input(gamepad, self._bindings)
            if pad.fire or pad.bomb or pad.x != 0 or pad.y != 0:
                self._pad_in_use = slot
            fire = fire or pad.fire
            bomb = bomb or pad.bomb
            if math.hypot(pad.x, pad.y) > math.hypot(best.x, best.y):
                best = pad
        length = math.hypot(best.x, best.y)
        scale = 1 / length if length > 1 else 1
        return _PadInput(best.x * scale, best.y * scale, fire, bomb)

    def _check_pad_in_use(self, gamepads: Sequence[GamepadLike | None]) -> None:
        """The gamepad in use is gone from its slot: it was disconnected (P12-R03)."""
        if self._pad_in_use is None:
            return
        if self._pad_in_use < len(gamepads) and gamepads[self._pad_in_use]:
            return
        self._pad_in_use = None
        self._pad_lost = True
