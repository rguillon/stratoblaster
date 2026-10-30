"""The loading screen of a level (P13-R03), ported from `ui/level-loading.ts`: the menus' loading
screen over the game screen, with the level's real progress."""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from ui.menu_view import LoadingView  # noqa: E402
from ui.screens.elements import array_from, replace_children  # noqa: E402
from ui.screens.loading_screen import render_loading_screen  # noqa: E402


class LevelLoadingScreen:
    """The loading screen of a level (P13-R03). It fades in only after a short delay (CSS), so a
    quick load does not flash it.
    """

    def __init__(self, doc: Any, parent: Any, text: str) -> None:
        self._doc = doc
        self._parent = parent
        self._text = text
        self._root: Any = None

    def show(self, progress: float) -> None:
        """Shows `progress` (0..1). Later calls update the screen in place: a new element would
        start its fade-in again, transparent, and the menus drawn behind it would show for a few
        frames.
        """
        root = render_loading_screen(self._doc, LoadingView(self._text, progress))
        if self._root is not None:
            replace_children(self._root, array_from(root.childNodes))
            return
        root.classList.add("level-loading")
        self._parent.append(root)
        self._root = root

    def dispose(self) -> None:
        if self._root is not None:
            self._root.remove()
        self._root = None
