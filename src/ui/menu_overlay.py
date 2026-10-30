"""The HTML/CSS menu overlay (P01-R13) It renders a view and
turns taps and clicks into menu commands (P01-R11); it never reads raw keys or gamepad buttons."""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any, Protocol  # noqa: E402

from ui.menu_view import MenuView  # noqa: E402
from ui.screens.elements import MenuDocument  # noqa: E402


class GameTouchHandlers(Protocol):
    """Touch controls of the game screen (P06-R02), in logical pixels with Y up."""

    def fire(self, held: bool) -> None: ...

    def drag(self, dx: float, dy: float) -> None: ...


__pragma__("noskip")

from input.menu_action import MenuSet  # noqa: E402
from input.pointer_menu_input import pointer_command  # noqa: E402
from ui.menu_view import (  # noqa: E402
    DevMenuView,
    DevViewerView,
    GameScreenView,
    LevelSelectView,
    LoadingView,
    ShipSelectView,
    TitleView,
)
from ui.screens.dev_screen import (  # noqa: E402
    centre_choices,
    render_dev_screen,
    render_dev_viewer_screen,
)
from ui.screens.game_screen import render_game_screen  # noqa: E402
from ui.screens.level_select_screen import render_level_select_screen  # noqa: E402
from ui.screens.loading_screen import render_loading_screen  # noqa: E402
from ui.screens.screen_handlers import ScreenHandlers  # noqa: E402
from ui.screens.settings_screen import render_settings_screen  # noqa: E402
from ui.screens.ship_select_screen import render_ship_select_screen  # noqa: E402
from ui.screens.title_screen import render_title_screen  # noqa: E402
from ui.shrink_to_fit import shrink_to_fit  # noqa: E402


class MenuOverlayOptions:
    """Settings of a `MenuOverlay`."""

    def __init__(self, transition_seconds: float) -> None:
        # Fade-in time of a new screen, in seconds (P01-R15).
        self.transition_seconds = transition_seconds


def _render_loading(doc: MenuDocument, view: Any, _handlers: ScreenHandlers) -> Any:
    return render_loading_screen(doc, view)


# Each view class, and its screen's renderer (`renderer(doc, view, handlers)`).
_RENDERERS: list[Any] = [
    [LoadingView, _render_loading],
    [TitleView, render_title_screen],
    [ShipSelectView, render_ship_select_screen],
    [LevelSelectView, render_level_select_screen],
    [GameScreenView, render_game_screen],
    [DevMenuView, render_dev_screen],
    [DevViewerView, render_dev_viewer_screen],
]


def _render_screen(doc: MenuDocument, view: MenuView, handlers: ScreenHandlers) -> Any:
    """Renders the screen `view` shows (the view's class picks the renderer; the settings screen
    when none does)."""
    for pair in _RENDERERS:
        if isinstance(view, pair[0]):
            return pair[1](doc, view, handlers)
    settings: Any = view
    return render_settings_screen(doc, settings, handlers)


def _selected_index(view: MenuView) -> int:
    return view.selected if hasattr(view, "selected") else 0


class MenuOverlay:
    """The HTML/CSS menu overlay (P01-R13), laid out at the logical resolution. A new screen fades
    in; `shake_selected` gives the "locked" feedback (P01-R07).
    """

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        doc: MenuDocument,
        root: Any,
        on_command: Callable[[Any], None],
        options: MenuOverlayOptions,
        touch: GameTouchHandlers | None = None,
        on_wheel: Callable[[float], None] | None = None,
        on_turn: Callable[[float, float], None] | None = None,
    ) -> None:
        """`on_wheel(delta_y)`: the mouse wheel turned over a dev viewer; `on_turn(dx, dy)`: a drag
        over it, in screen pixels (D-199)."""
        self._doc = doc
        self._root = root
        self._on_command = on_command
        self._options = options
        self._touch = touch
        self._on_wheel = on_wheel
        self._on_turn = on_turn
        self._current: Any = None
        self._view: MenuView | None = None

    def _scale(self) -> float:
        """Screen pixels per logical pixel: the overlay is laid out at the logical size and
        scaled.
        """
        shown = self._root.getBoundingClientRect().width
        laid_out = self._root.offsetWidth
        return shown / laid_out if shown > 0 and laid_out > 0 else 1

    @property
    def root(self) -> Any:
        """The element the screens are shown in."""
        return self._root

    @property
    def view(self) -> MenuView | None:
        """The view shown last."""
        return self._view

    def _handlers_for(self, view: MenuView) -> ScreenHandlers:
        def on_tap(index: int) -> None:
            self._on_command(pointer_command(index, _selected_index(view)))

        def on_back() -> None:
            self._on_command("back")

        def on_fire(held: bool) -> None:
            if self._touch is not None:
                self._touch.fire(held)

        def on_drag(dx: float, dy: float) -> None:
            scale = self._scale()
            if self._touch is not None:
                self._touch.drag(dx / scale, -dy / scale)

        def on_pause() -> None:
            self._on_command("pause")

        def on_set(index: int, value: float) -> None:
            self._on_command(MenuSet(index, value))

        return ScreenHandlers(
            on_tap, on_back, on_fire, on_drag, on_pause, on_set, self._on_wheel, self._on_turn
        )

    def show(self, view: MenuView) -> None:
        """Replaces the overlay content with `view`. A new screen fades in."""
        is_new_screen = self._view is None or self._view.kind != view.kind
        self._view = view
        screen = _render_screen(self._doc, view, self._handlers_for(view))
        screen.dataset.screen = view.kind
        if is_new_screen and view.kind != "loading":
            screen.classList.add("menu-enter")
            screen.style.animationDuration = str(self._options.transition_seconds) + "s"
        if self._current is not None:
            self._current.remove()
        self._root.append(screen)
        self._current = screen
        logo = screen.querySelector(".title-name")
        if logo:
            shrink_to_fit(logo)
        centre_choices(screen)

    def shake_selected(self, text: str) -> None:
        """ "Locked" feedback (P01-R07): shakes the selected entry and shows `text`."""
        if self._current is None:
            return
        selected = self._current.querySelector(".menu-entry.selected")
        if selected:
            selected.classList.remove("shake")
            # Reading the layout forces a reflow, so the CSS animation restarts.
            selected.getBoundingClientRect()
            selected.classList.add("shake")
        status = self._current.querySelector(".menu-status")
        if status:
            status.textContent = text

    def dispose(self) -> None:
        if self._current is not None:
            self._current.remove()
        self._current = None
        self._view = None
