"""Keyboard -> menu actions (P01-R09) Keys are matched
by `KeyboardEvent.code` (physical position), so WASD positions work on AZERTY. Held directions
repeat with our own timing; the browser's auto-repeat events are ignored."""

from org.transcrypt.stubs.browser import __pragma__

from input.hold_repeater import HoldRepeater
from input.menu_action import is_menu_direction

__pragma__("skip")
from collections.abc import Callable, Mapping  # noqa: E402
from typing import Protocol  # noqa: E402

from input.menu_action import MenuAction  # noqa: E402


class MenuKeyEvent(Protocol):
    """The parts of a keyboard event the menu input reads."""

    @property
    def code(self) -> str: ...

    @property
    def repeat(self) -> bool: ...

    def preventDefault(self) -> None: ...  # noqa: N802 (DOM name)


class RepeatTiming(Protocol):
    """Key repeat timing."""

    @property
    def repeat_delay_seconds(self) -> float: ...

    @property
    def repeat_interval_seconds(self) -> float: ...


class _KeyUpEvent(Protocol):
    @property
    def code(self) -> str: ...


class _Target(Protocol):
    def addEventListener(self, kind: str, listener: Callable[..., None]) -> None: ...  # noqa: N802

    def removeEventListener(self, kind: str, listener: Callable[..., None]) -> None: ...  # noqa: N802


__pragma__("noskip")


class KeyboardMenuInput:
    """Keyboard -> menu actions (see the module doc)."""

    def __init__(self, bindings: Mapping[str, MenuAction], timing: RepeatTiming) -> None:
        self._bindings = bindings
        self._queue: list[MenuAction] = []
        self._repeater = HoldRepeater(timing.repeat_delay_seconds, timing.repeat_interval_seconds)
        # The keys held down: an action keeps repeating while any key bound to it is still down.
        self._held: list[str] = []

    def key_down(self, event: MenuKeyEvent) -> None:
        action = self._bindings.get(event.code)
        if action is None:
            return
        event.preventDefault()
        if event.repeat:
            return
        if is_menu_direction(action) and event.code not in self._held:
            self._held.append(event.code)
        if not is_menu_direction(action) or self._repeater.press(action):
            self._queue.append(action)

    def key_up(self, event: _KeyUpEvent) -> None:
        action = self._bindings.get(event.code)
        if action is None or not is_menu_direction(action):
            return
        if event.code in self._held:
            self._held.remove(event.code)
        still_held = [code for code in self._held if self._bindings.get(code) == action]
        # len(): an empty list is truthy in JavaScript, so `not still_held` would never release.
        if len(still_held) == 0:
            self._repeater.release(action)

    def release_all(self) -> None:
        """Forgets held keys, e.g. when the window loses focus and key-ups would be missed."""
        self._repeater.release_all()
        self._held.clear()

    def update(self, dt_seconds: float) -> list[MenuAction]:
        """Returns the actions since the last call: presses first, then the repeats due."""
        actions: list[MenuAction] = list(self._queue)
        actions.extend(self._repeater.update(dt_seconds))
        self._queue.clear()
        return actions

    def listen(self, target: _Target) -> Callable[[], None]:
        """Listens to `keydown`, `keyup` and `blur` on `target`. Returns a function that stops."""

        def down(e: MenuKeyEvent) -> None:
            self.key_down(e)

        def up(e: _KeyUpEvent) -> None:
            self.key_up(e)

        def blur() -> None:
            self.release_all()

        target.addEventListener("keydown", down)
        target.addEventListener("keyup", up)
        target.addEventListener("blur", blur)

        def stop() -> None:
            target.removeEventListener("keydown", down)
            target.removeEventListener("keyup", up)
            target.removeEventListener("blur", blur)

        return stop
