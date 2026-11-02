# Copyright (c) 2026 Renaud Guillon
"""Merges several devices (keyboard, gamepads...) into one stream of menu actions."""

# isort: split
# __pragma__ ("skip")
from collections.abc import Sequence
from typing import Protocol

from input.menu_action import MenuAction


class MenuActionSource(Protocol):
    """Anything that produces menu actions once per frame."""

    def update(self, dt_seconds: float) -> list[MenuAction]:
        """Return the menu actions since the last call."""


# __pragma__ ("noskip")


class MenuInput:
    """Merges several devices into one stream of menu actions."""

    def __init__(self, sources: Sequence[MenuActionSource]) -> None:
        self._sources = sources

    def update(self, dt_seconds: float) -> list[MenuAction]:
        """Return the menu actions since the last call."""
        actions: list[MenuAction] = []
        for source in self._sources:
            actions.extend(source.update(dt_seconds))
        return actions
