"""The dev viewers of the app (D-199): the viewer the menu flow shows on its `dev-viewer` screen,
built when it opens and dropped when it closes; the mouse wheel over it (D-208: it zooms, or
scrubs the levels viewer's time).
"""

from org.transcrypt.stubs.browser import __pragma__

from app.dev_viewer import DevViewer

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from app.dev_catalog import DevItem  # noqa: E402

__pragma__("noskip")


class DevSession:
    """Runs the dev viewer the flow shows (see the module doc). `status_root`: the element whose
    `.dev-status` line the viewer's status is written into (None: not written)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        engine: Any,
        game: Any,
        catalog: dict[str, list[DevItem]],
        environment: bool,
        status_root: Any,
    ) -> None:
        self._engine = engine
        self._game = game
        self._catalog = catalog
        self._environment = environment
        self._status_root = status_root
        self.viewer: DevViewer | None = None

    @property
    def active(self) -> bool:
        """Whether a dev viewer is shown."""
        return self.viewer is not None

    def sync(self, state: Any) -> None:
        """Opens, changes or closes the viewer as the flow's state says."""
        name = state.dev_viewer
        if name is None:
            self._drop()
            return
        if self.viewer is not None and self.viewer.viewer != name:
            self._drop()
        if self.viewer is None:
            items = self._catalog[name]
            self.viewer = DevViewer(self._engine, self._game, name, items, self._environment)
        self.viewer.show(state.selection, state.dev_close_up)

    def wheel(self, delta_y: float) -> None:
        """The wheel turned by `delta_y` pixels: the levels viewer scrubs; the others zoom (D-208:
        in when it turns up, out when it turns down)."""
        viewer = self.viewer
        if viewer is None:
            return
        if viewer.viewer == "levels":
            viewer.scrub(delta_y)
            return
        viewer.zoom(delta_y)

    def turn(self, dx: float, dy: float) -> None:
        """A drag over the viewer, by (`dx`, `dy`) screen pixels, turns its model."""
        if self.viewer is not None:
            self.viewer.turn(dx, dy)

    def frame(self, dt: float) -> None:
        """Moves the viewer on by `dt` seconds, and shows its status."""
        viewer = self.viewer
        if viewer is None:
            return
        viewer.frame(dt)
        if self._status_root is None:
            return
        # Read again each frame: the overlay makes a new line each time the item changes.
        line = self._status_root.querySelector(".dev-status")
        status = viewer.status
        if line and line.textContent != status:
            line.textContent = status

    def render(self) -> bool:
        """Draws the viewer's scene; False when there is none to draw yet."""
        scene = self.viewer.scene if self.viewer is not None else None
        if scene is None:
            return False
        scene.render()
        return True

    def _drop(self) -> None:
        if self.viewer is not None:
            self.viewer.dispose()
        self.viewer = None

    def dispose(self) -> None:
        self._drop()
