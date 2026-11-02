# Copyright (c) 2026 Renaud Guillon
"""The pause menu (UI-PAUSE-07): Resume, Settings, Main menu.

Main menu asks `Leave the level?` with No (selected first) and Yes (UI-PAUSE-10). Pure: the flow
changes screens.
"""

import math

# The entries of the pause menu, in display order (UI-PAUSE-07).
PAUSE_ENTRIES = ["resume", "settings", "main-menu"]


def _is_integer(value: float) -> bool:
    """Number.isInteger: false for fractions, infinities and NaN."""
    return value - math.floor(value) == 0


class PauseMenu:
    """The pause menu (UI-PAUSE-07).

    The outcomes of its commands are `none`, `moved`, `ask`,. `resume`, `settings` and `leave`: the
    flow carries out the last three.
    """

    def __init__(self) -> None:
        self._selection = 0
        self._leaving = False
        # On the question: 0 No, 1 Yes.
        self._choice = 0

    @property
    def selection(self) -> int:
        """Index of the selected entry of the pause menu."""
        return self._selection

    @property
    def selected_id(self) -> str:
        """Id of the selected entry (`resume` when out of range)."""
        return PAUSE_ENTRIES[self._selection] if self._selection < len(PAUSE_ENTRIES) else "resume"

    @property
    def leaving(self) -> bool:
        """Whether the `Leave the level?` question shows."""
        return self._leaving

    @property
    def choice(self) -> int:
        """Index of the answer chosen on the question (0 No, 1 Yes)."""
        return self._choice

    def open(self) -> None:
        """Open the menu on Resume, without the question."""
        self._selection = 0
        self._leaving = False
        self._choice = 0

    def move(self, direction: str) -> str:
        """Move the selection, or the answer while the question shows, for `direction`."""
        if self._leaving:
            return self._choose(0 if direction in ["left", "up"] else 1)
        if direction in ["left", "right"]:
            return "none"
        return self.select(self._selection + (-1 if direction == "up" else 1))

    def select(self, index: int) -> str:
        """Select entry `index`, or answer `index` while the question shows."""
        if self._leaving:
            return self._choose(index) if index in [0, 1] else "none"
        if not _is_integer(index) or index < 0 or index >= len(PAUSE_ENTRIES):
            return "none"
        if index == self._selection:
            return "none"
        self._selection = index
        return "moved"

    def confirm(self) -> str:
        """Confirm the selected entry, or the answer to the question."""
        if self._leaving:
            if self._choice == 1:
                return "leave"
            self._leaving = False
            return "ask"
        entry = self.selected_id
        if entry == "resume":
            return "resume"
        if entry == "settings":
            return "settings"
        self._leaving = True
        self._choice = 0
        return "ask"

    def back(self) -> str:
        """Back: closes the question, or resumes the level (UI-PAUSE-08)."""
        if not self._leaving:
            return "resume"
        self._leaving = False
        return "ask"

    def _choose(self, choice: int) -> str:
        if choice == self._choice:
            return "none"
        self._choice = choice
        return "moved"
