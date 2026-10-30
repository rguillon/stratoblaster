"""The dev menu and the dev viewers' screens (D-199)."""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from typing import Any  # noqa: E402

from ui.menu_view import DevChoice, DevMenuView, DevViewerView  # noqa: E402
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
        # D-204: over a row of buttons, the wheel scrolls the row.
        row = event.target.closest(".dev-choices") if event.target is not None else None
        if row:
            row.scrollLeft += event.deltaY
            return
        if handlers.on_wheel is not None:
            handlers.on_wheel(event.deltaY)

    return on_wheel


def _choice_row(
    doc: Any, class_name: str, choices: list[DevChoice], handlers: ScreenHandlers
) -> Any:
    """A row of buttons (D-204), each showing its item when tapped."""
    row = element(doc, "div", "dev-choices " + class_name)
    for choice in choices:
        button = entry(doc, "dev-choice", choice.index, choice.selected, handlers.on_tap)
        button.textContent = choice.label
        row.append(button)
    return row


def _drag_to_turn(root: Any, handlers: ScreenHandlers) -> None:
    """A drag on the screen (not on its Back button or its buttons) goes to `on_turn`, by screen
    pixels."""
    last: list[Any] = [None]

    def on_down(event: Any) -> None:
        if event.target is not None and event.target.closest(".menu-back, .dev-choices"):
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


def centre_choices(screen: Any) -> None:
    """Scrolls each row of buttons of a shown dev viewer (D-204) so its selected one is in the
    middle (the rows are made anew each time the item changes)."""
    for row in screen.querySelectorAll(".dev-choices"):
        selected = row.querySelector(".selected")
        if selected:
            row.scrollLeft = selected.offsetLeft - (row.clientWidth - selected.offsetWidth) / 2


def render_dev_viewer_screen(doc: Any, view: DevViewerView, handlers: ScreenHandlers) -> Any:
    """A dev viewer, over its 3D view: the item's name and place in the list, a status line (the
    viewer writes it), the buttons of its groups and of the items of the group shown (D-204), the
    hint. The wheel anywhere on the screen goes to `on_wheel`, a drag to
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
    )
    if view.groups is not None and view.choices is not None:
        root.append(
            _choice_row(doc, "dev-groups", view.groups, handlers),
            _choice_row(doc, "dev-props", view.choices, handlers),
        )
    root.append(element(doc, "div", "menu-hint dev-hint", view.hint))
    root.addEventListener("wheel", _wheel_listener(handlers))
    _drag_to_turn(root, handlers)
    return root
