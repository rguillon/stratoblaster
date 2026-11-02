# Copyright (c) 2026 Renaud Guillon
"""A titled text block: one of the cards in a row (the ship select screen's ships)."""


class Caption:
    """A titled block of text lines."""

    def __init__(self, title: str, lines: list[str]) -> None:
        self.title = title
        self.lines = lines
