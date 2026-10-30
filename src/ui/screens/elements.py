"""DOM helpers of the menu screens, ported from `ui/screens/elements.ts`."""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any  # noqa: E402

# The DOM is not in the type stubs, so its objects are `Any` (TypeScript: `Pick<Document, ...>`).
MenuDocument = Any
HtmlElement = Any
TapHandler = Callable[[int], None]
__pragma__("noskip")

SVG = "http://www.w3.org/2000/svg"


def element(doc: MenuDocument, tag: str, class_name: str, text: str | None = None) -> HtmlElement:
    """Creates `<tag class="class_name">text</tag>`."""
    el = doc.createElement(tag)
    el.className = class_name
    if text is not None:
        el.textContent = text
    return el


def tap_listener(on_tap: TapHandler, index: int) -> Callable[[object], None]:
    """A click listener that reports entry `index`. A factory, so that each listener keeps its
    own index."""

    def handler(_event: object) -> None:
        on_tap(index)

    return handler


def entry(
    doc: MenuDocument,
    class_name: str,
    index: int,
    selected: bool,
    on_tap: TapHandler,
) -> HtmlElement:
    """A tappable menu entry (P01-R11). Uses `role="button"` on a `div` rather than `<button>`,
    so the browser never turns Space / Enter into a second click: the keyboard goes through
    the menu input only.
    """
    el = element(doc, "div", "menu-entry " + class_name)
    el.setAttribute("role", "button")
    el.dataset.index = str(index)
    if selected:
        el.classList.add("selected")
        el.setAttribute("aria-current", "true")
    el.addEventListener("click", tap_listener(on_tap, index))
    return el


def back_button(doc: MenuDocument, label: str, on_back: Callable[[], None]) -> HtmlElement:
    """The on-screen Back button of a menu screen (P01-R11)."""
    el = element(doc, "div", "menu-back", "◀ " + label)
    el.setAttribute("role", "button")
    el.addEventListener("click", on_back)
    return el


def padlock(doc: MenuDocument) -> HtmlElement:
    """A small padlock icon for locked levels."""
    svg = doc.createElementNS(SVG, "svg")
    svg.setAttribute("viewBox", "0 0 16 16")
    svg.setAttribute("class", "padlock")
    svg.setAttribute("aria-label", "locked")
    shackle = doc.createElementNS(SVG, "path")
    shackle.setAttribute("d", "M4.5 7V5a3.5 3.5 0 0 1 7 0v2")
    shackle.setAttribute("fill", "none")
    shackle.setAttribute("stroke", "currentColor")
    shackle.setAttribute("stroke-width", "1.6")
    body = doc.createElementNS(SVG, "rect")
    for key, value in [("x", "3"), ("y", "7"), ("width", "10"), ("height", "8"), ("rx", "1.5")]:
        body.setAttribute(key, value)
    body.setAttribute("fill", "currentColor")
    svg.append(shackle, body)
    return svg


def array_from(source: Any) -> list[Any]:
    """`Array.from(source)`: a JavaScript array copy of a NodeList or an iterable. (`from` is a
    Python keyword, so `window.Array.from` cannot be written.)
    """
    __pragma__("js", "{}", "return Array.from(source);")
    return []


def replace_children(el: HtmlElement, nodes: list[HtmlElement]) -> None:
    """`el.replaceChildren(...nodes)`: a JavaScript spread, which Transcrypt has no call for."""
    __pragma__("js", "{}", "el.replaceChildren(...nodes);")
