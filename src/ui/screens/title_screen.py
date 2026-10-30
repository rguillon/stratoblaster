"""Title screen (P01-R04): high score, game title,
Start, Settings (P12-R04), controls hint and version."""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from typing import Any  # noqa: E402

from ui.menu_view import TitleView  # noqa: E402
from ui.screens.screen_handlers import ScreenHandlers  # noqa: E402

__pragma__("noskip")

from ui.screens.elements import element, entry  # noqa: E402


def render_title_screen(doc: Any, view: TitleView, handlers: ScreenHandlers) -> Any:
    """Renders the title screen (P01-R04)."""
    root = element(doc, "div", "menu-screen title-screen")
    score = element(doc, "div", "title-score")
    score.append(
        element(doc, "div", "title-score-label", view.high_score_label),
        element(doc, "div", "title-high-score", str(view.high_score)),
    )
    start = entry(doc, "title-start", 0, view.selected == 0, handlers.on_tap)
    start.textContent = view.start
    settings = entry(doc, "title-settings", 1, view.selected == 1, handlers.on_tap)
    settings.textContent = view.settings
    version = element(doc, "div", "title-version")
    version.append(
        element(doc, "div", "version-number", "v" + view.version),
        element(doc, "div", "version-commit", view.commit),
    )
    root.append(
        score,
        element(doc, "h1", "title-name", view.title),
        start,
        settings,
        element(doc, "div", "menu-hint title-hint", view.hint),
        version,
    )
    return root
