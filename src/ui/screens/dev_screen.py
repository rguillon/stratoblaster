# Copyright (c) 2026 Renaud Guillon
"""The dev menu and the dev viewers' screens (D-199), and the dev audio viewers' (DEV-MENU-19)."""

from ui.screens.elements import back_button, element, entry

# isort: split
# __pragma__ ("skip")
from typing import Any

from ui.menu_view import DevAudioView, DevChoice, DevMenuView, DevViewerView
from ui.screens.screen_handlers import ScreenHandlers

# __pragma__ ("noskip")


def render_dev_screen(doc: Any, view: DevMenuView, handlers: ScreenHandlers) -> Any:
    """Return the dev menu (DEV-MENU-03): one entry per viewer."""
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
        # D-206: over the menu, the wheel scrolls the menu.
        menu = event.target.closest(".dev-menu") if event.target is not None else None
        if menu:
            menu.scrollTop += event.deltaY
            return
        if handlers.on_wheel is not None:
            handlers.on_wheel(event.deltaY)

    return on_wheel


def _menu(doc: Any, entries: list[DevChoice], handlers: ScreenHandlers, columns: int = 3) -> Any:
    """Return the scrolling menu of a dev viewer's items (DEV-MENU-07, D-206): each group's heading.

    Then its items; a tap on an entry shows its item.
    """
    menu = element(doc, "div", "dev-menu")
    menu.style.setProperty("--dev-columns", str(columns))
    for choice in entries:
        kind = "dev-menu-group" if choice.heading else "dev-menu-item"
        line = entry(doc, kind, choice.index, choice.selected, handlers.on_tap)
        line.textContent = choice.label
        menu.append(line)
    return menu


def _press_listener(handlers: ScreenHandlers, index: int) -> Any:
    """Return a pointer-down listener on an audio button: it picks the item at once and holds it."""

    def on_down(_event: Any) -> None:
        handlers.on_tap(index)
        if handlers.on_hold is not None:
            handlers.on_hold(True)

    return on_down


def _audio_menu(doc: Any, entries: list[DevChoice], handlers: ScreenHandlers) -> Any:
    """Return the grid of an audio viewer's buttons (DEV-MENU-19): the dev viewers' menu.

    Over the whole screen. A button plays its item as soon as it is pressed, not on the release,
    and is held until the pointer is let go (`on_hold`): a held sound button repeats its sound.
    """
    menu = element(doc, "div", "dev-menu dev-audio-menu")
    for choice in entries:
        kind = "dev-menu-group" if choice.heading else "dev-menu-item"
        line = element(doc, "div", "menu-entry " + kind)
        line.setAttribute("role", "button")
        line.dataset.index = str(choice.index)
        if choice.selected:
            line.classList.add("selected")
            line.setAttribute("aria-current", "true")
        line.textContent = choice.label
        line.addEventListener("pointerdown", _press_listener(handlers, choice.index))
        menu.append(line)
    return menu


def _release_on(root: Any, handlers: ScreenHandlers) -> None:
    """Let go of the held button when the pointer is released or leaves the screen.

    On the screen's root: the screen is made anew when the item changes, so the button pressed may
    be gone by the release.
    """

    def on_up(_event: Any) -> None:
        if handlers.on_hold is not None:
            handlers.on_hold(False)

    for kind in ["pointerup", "pointercancel", "pointerleave"]:
        root.addEventListener(kind, on_up)


def _drag_to_turn(root: Any, handlers: ScreenHandlers) -> None:
    """Send drags on the screen to `on_turn`, by screen pixels, to turn the model (DEV-MENU-10).

    Drags on its Back button or its menu are left alone.
    """
    last: list[Any] = [None]

    def on_down(event: Any) -> None:
        if event.target is not None and event.target.closest(".menu-back, .dev-menu"):
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


def centre_menu(screen: Any) -> None:
    """Scrolls the menu of a shown dev viewer (D-206) so the item shown is in its middle.

    The menu is made anew each time the item changes.
    """
    menu = screen.querySelector(".dev-menu")
    if not menu:
        return
    selected = menu.querySelector(".dev-menu-item.selected")
    if selected:
        menu.scrollTop = selected.offsetTop - (menu.clientHeight - selected.offsetHeight) / 2


def render_dev_viewer_screen(doc: Any, view: DevViewerView, handlers: ScreenHandlers) -> Any:
    """Return a dev viewer, over its 3D view (DEV-MENU-05): the item's name and place in the list.

    A status line (the viewer writes it), the scrolling menu of its items by group (D-206), the
    hint. The wheel anywhere on the screen but the menu goes to `on_wheel`, a drag to `on_turn`.
    """
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
    if view.menu is not None:
        root.append(_menu(doc, view.menu, handlers, view.columns))
    root.append(element(doc, "div", "menu-hint dev-hint", view.hint))
    root.addEventListener("wheel", _wheel_listener(handlers))
    _drag_to_turn(root, handlers)
    return root


def render_dev_audio_screen(doc: Any, view: DevAudioView, handlers: ScreenHandlers) -> Any:
    """Return a dev audio viewer (DEV-MENU-19, DEV-MENU-20): a button per sound or track.

    In a scrolling grid (the dev viewers' menu, laid out over the whole screen), a status line (the
    viewer writes it: what plays) and the hint. A press on a button plays its item; held, it
    repeats it (`on_hold`).
    """
    root = element(doc, "div", "menu-screen dev-audio-screen")
    caption = element(doc, "div", "dev-caption")
    caption.append(element(doc, "div", "dev-status"))
    root.append(
        back_button(doc, view.back, handlers.on_back),
        element(doc, "h2", "menu-heading", view.heading),
        caption,
        _audio_menu(doc, view.entries, handlers),
        element(doc, "div", "menu-hint dev-hint", view.hint),
    )
    _release_on(root, handlers)
    return root
