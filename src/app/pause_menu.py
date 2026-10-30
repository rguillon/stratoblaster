"""The pause menu (P12-R02): Resume, Settings, Main menu. Main
menu asks `Leave the level?` with No (selected first) and Yes. Pure: the flow changes screens.
"""

import math

# The entries of the pause menu, in display order (P12-R02).
PAUSE_ENTRIES = ["resume", "settings", "main-menu"]


def _is_integer(value: float) -> bool:
    """Number.isInteger: false for fractions, infinities and NaN."""
    return value - math.floor(value) == 0


class PauseMenu:
    """The pause menu (P12-R02). The outcomes of its commands are `none`, `moved`, `ask`,
    `resume`, `settings` and `leave`: the flow carries out the last three.
    """

    def __init__(self) -> None:
        self._selection = 0
        self._leaving = False
        # On the question: 0 No, 1 Yes.
        self._choice = 0

    @property
    def selection(self) -> int:
        return self._selection

    @property
    def selected_id(self) -> str:
        return PAUSE_ENTRIES[self._selection] if self._selection < len(PAUSE_ENTRIES) else "resume"

    @property
    def leaving(self) -> bool:
        """Whether the `Leave the level?` question shows."""
        return self._leaving

    @property
    def choice(self) -> int:
        return self._choice

    def open(self) -> None:
        """The menu opens on Resume, without the question."""
        self._selection = 0
        self._leaving = False
        self._choice = 0

    def move(self, direction: str) -> str:
        if self._leaving:
            return self._choose(0 if direction in ["left", "up"] else 1)
        if direction in ["left", "right"]:
            return "none"
        return self.select(self._selection + (-1 if direction == "up" else 1))

    def select(self, index: int) -> str:
        if self._leaving:
            return self._choose(index) if index in [0, 1] else "none"
        if not _is_integer(index) or index < 0 or index >= len(PAUSE_ENTRIES):
            return "none"
        if index == self._selection:
            return "none"
        self._selection = index
        return "moved"

    def confirm(self) -> str:
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
        """Back: closes the question, or resumes the level."""
        if not self._leaving:
            return "resume"
        self._leaving = False
        return "ask"

    def _choose(self, choice: int) -> str:
        if choice == self._choice:
            return "none"
        self._choice = choice
        return "moved"
