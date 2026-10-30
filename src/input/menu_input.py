"""Merges several devices (keyboard, gamepads...) into one stream of menu actions, ported from
`input/menu-input.ts`."""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Sequence  # noqa: E402
from typing import Protocol  # noqa: E402

from input.menu_action import MenuAction  # noqa: E402


class MenuActionSource(Protocol):
    """Anything that produces menu actions once per frame."""

    def update(self, dt_seconds: float) -> list[MenuAction]: ...


__pragma__("noskip")


class MenuInput:
    """Merges several devices into one stream of menu actions."""

    def __init__(self, sources: Sequence[MenuActionSource]) -> None:
        self._sources = sources

    def update(self, dt_seconds: float) -> list[MenuAction]:
        actions: list[MenuAction] = []
        for source in self._sources:
            actions.extend(source.update(dt_seconds))
        return actions
