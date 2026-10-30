"""Loading screen with a progress bar (P01-R02), ported from `ui/screens/loading-screen.ts`."""

from org.transcrypt.stubs.browser import __pragma__, window

__pragma__("skip")
from typing import Any  # noqa: E402

from ui.menu_view import LoadingView  # noqa: E402

__pragma__("noskip")

from ui.screens.elements import element  # noqa: E402


def render_loading_screen(doc: Any, view: LoadingView) -> Any:
    """Loading screen with a progress bar (P01-R02)."""
    root = element(doc, "div", "menu-screen loading-screen")
    percent = window.Math.round(window.Math.min(1, window.Math.max(0, view.progress)) * 100)
    bar = element(doc, "div", "loading-bar")
    bar.setAttribute("role", "progressbar")
    bar.setAttribute("aria-valuemin", "0")
    bar.setAttribute("aria-valuemax", "100")
    bar.setAttribute("aria-valuenow", str(percent))
    fill = element(doc, "div", "loading-fill")
    fill.style.width = str(percent) + "%"
    bar.append(fill)
    root.append(
        element(doc, "div", "loading-text", view.text),
        bar,
        element(doc, "div", "loading-percent", str(percent) + " %"),
    )
    return root
