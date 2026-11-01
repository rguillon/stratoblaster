# Copyright (c) 2026 Renaud Guillon
"""The dev viewers of the app, in the game page (DEV-MENU-02, D-199).

The viewer the menu flow shows on its `dev-viewer` screen, built when it opens and dropped when it
closes; the mouse wheel over it (DEV-MENU-11, D-208: it zooms, or scrubs the levels viewer's time);
K in the bosses viewer (breaks the boss's next part, DEV-MENU-14).
"""

from app.dev_viewer import DevViewer
from config.dev_viewer import DEV_VIEWER_CONFIG as CFG

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from app.dev_catalog import DevItem

# __pragma__ ("noskip")


class DevSession:
    """Runs the dev viewer the flow shows (see the module doc).

    `status_root`: the element whose `.dev-status` line the viewer's status is written into (None:
    not written).
    """

    def __init__(
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
        # Stops listening to the keyboard (see `listen`).
        self._stop_keys: Any = None

    @property
    def active(self) -> bool:
        """Whether a dev viewer is shown."""
        return self.viewer is not None

    def sync(self, state: Any) -> None:
        """Open, change or close the viewer as the flow's state says."""
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
        """Scrub the levels viewer, or zoom the others, as the wheel turns by `delta_y` pixels.

        It zooms in when it turns up and out when it turns down (D-208).
        """
        viewer = self.viewer
        if viewer is None:
            return
        if viewer.viewer == "levels":
            viewer.scrub(delta_y)
            return
        viewer.zoom(delta_y)

    def listen(self, target: Any) -> None:
        """Listen for the viewer's keys (see `key`) on `target` (None: nothing listens)."""
        if target is None:
            return

        def on_key(event: Any) -> None:
            if self.key(event.code, event["type"] == "keydown"):
                event.preventDefault()

        target.addEventListener("keydown", on_key)
        target.addEventListener("keyup", on_key)

        def stop() -> None:
            target.removeEventListener("keydown", on_key)
            target.removeEventListener("keyup", on_key)

        self._stop_keys = stop

    def key(self, code: str, down: bool) -> bool:
        """Return a key pressed over the viewer: K breaks the boss's next part in the bosses viewer.

        Returns whether the key was used.
        """
        viewer = self.viewer
        if viewer is None or viewer.viewer != "bosses" or code != CFG.break_key:
            return False
        if down:
            viewer.break_part()
        return True

    def turn(self, dx: float, dy: float) -> None:
        """Turn the viewer's model as it is dragged by (`dx`, `dy`) screen pixels (DEV-MENU-10)."""
        if self.viewer is not None:
            self.viewer.turn(dx, dy)

    def frame(self, dt: float) -> None:
        """Move the viewer on by `dt` seconds, and show its status (DEV-MENU-05)."""
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
        """Releases the viewer and the keys it listens to."""
        self._drop()
        if self._stop_keys is not None:
            self._stop_keys()
        self._stop_keys = None
