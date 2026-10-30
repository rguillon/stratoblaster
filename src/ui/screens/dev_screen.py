"""The dev menu and the dev viewers' screens (D-199)."""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from typing import Any  # noqa: E402

from ui.menu_view import DevMenuView, DevViewerView  # noqa: E402
from ui.screens.screen_handlers import ScreenHandlers  # noqa: E402

__pragma__("noskip")

from ui.screens.elements import back_button, element, entry  # noqa: E402


def render_dev_screen(doc: Any, view: DevMenuView, handlers: ScreenHandlers) -> Any:
    """The dev menu: one entry per viewer."""
    root = element(doc, "div", "menu-screen dev-screen")
    entries = element(doc, "div", "dev-entries")
    for i, label in enumerate(view.entries):
        item = entry(doc, "dev-entry", i, i == view.selected, handlers.on_tap)
        item.textContent = label
        entries.append(item)
    root.append(
        back_button(doc, view.back, handlers.on_back),
        element(doc, "h2", "menu-heading", view.heading),
        entries,
        element(doc, "div", "menu-hint", view.hint),
    )
    return root


def _wheel_listener(handlers: ScreenHandlers) -> Any:
    def on_wheel(event: Any) -> None:
        event.preventDefault()
        if handlers.on_wheel is not None:
            handlers.on_wheel(event.deltaY)

    return on_wheel


def _drag_to_turn(root: Any, handlers: ScreenHandlers) -> None:
    """A drag on the screen (not on its Back button) goes to `on_turn`, by screen pixels."""
    last: list[Any] = [None]

    def on_down(event: Any) -> None:
        if event.target is not None and event.target.closest(".menu-back"):
            return
        last[0] = [event.clientX, event.clientY]
        root.setPointerCapture(event.pointerId)

    def on_move(event: Any) -> None:
        start = last[0]
        if start is None:
            return
        last[0] = [event.clientX, event.clientY]
        if handlers.on_turn is not None:
            handlers.on_turn(event.clientX - start[0], event.clientY - start[1])

    def on_up(_event: Any) -> None:
        last[0] = None

    root.addEventListener("pointerdown", on_down)
    root.addEventListener("pointermove", on_move)
    for kind in ["pointerup", "pointercancel"]:
        root.addEventListener(kind, on_up)


def render_dev_viewer_screen(doc: Any, view: DevViewerView, handlers: ScreenHandlers) -> Any:
    """A dev viewer, over its 3D view: the item's name and place in the list, a status line (the
    viewer writes it), the hint. The wheel anywhere on the screen goes to `on_wheel`, a drag to
    `on_turn`."""
    root = element(doc, "div", "menu-screen dev-viewer-screen")
    caption = element(doc, "div", "dev-caption")
    caption.append(
        element(doc, "div", "dev-item", view.item),
        element(doc, "div", "dev-position", view.position),
        element(doc, "div", "dev-status"),
    )
    root.append(
        back_button(doc, view.back, handlers.on_back),
        element(doc, "h2", "dev-heading", view.heading),
        caption,
        element(doc, "div", "menu-hint dev-hint", view.hint),
    )
    root.addEventListener("wheel", _wheel_listener(handlers))
    _drag_to_turn(root, handlers)
    return root
