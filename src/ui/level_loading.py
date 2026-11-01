# Copyright (c) 2026 Renaud Guillon
"""The loading screen of a level (UI-LOAD-06): the menus' loading screen over the game screen.

With the level's real progress.
"""

from ui.menu_view import LoadingView
from ui.screens.elements import array_from, replace_children
from ui.screens.loading_screen import render_loading_screen

# isort: split
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


class LevelLoadingScreen:
    """The loading screen of a level (UI-LOAD-06).

    It fades in only after a short delay (CSS), so a quick load does not flash it (PERF-10).
    """

    def __init__(self, doc: Any, parent: Any, text: str) -> None:
        self._doc = doc
        self._parent = parent
        self._text = text
        self._root: Any = None

    def show(self, progress: float) -> None:
        """Show `progress` (0..1).

        Later calls update the screen in place: a new element would start its fade-in again,
        transparent, and the menus drawn behind it would show for a few frames.
        """
        root = render_loading_screen(self._doc, LoadingView(self._text, progress))
        if self._root is not None:
            replace_children(self._root, array_from(root.childNodes))
            return
        root.classList.add("level-loading")
        self._parent.append(root)
        self._root = root

    def dispose(self) -> None:
        """Dispose."""
        if self._root is not None:
            self._root.remove()
        self._root = None
