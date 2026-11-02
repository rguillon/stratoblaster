# Copyright (c) 2026 Renaud Guillon
"""Title screen (UI-TITLE-01).

High score, game title, Start, Settings (UI-SET-01), Full screen (UI-TITLE-11, where the browser
allows it), Dev (DEV-MENU-01, D-199, with `?dev`), controls hint and version.
"""

from ui.screens.elements import element, entry

# isort: split
# __pragma__ ("skip")
from typing import Any

from ui.menu_view import TitleView
from ui.screens.screen_handlers import ScreenHandlers

# __pragma__ ("noskip")


def render_title_screen(doc: Any, view: TitleView, handlers: ScreenHandlers) -> Any:
    """Render the title screen: the high score (UI-TITLE-03), the game's name (UI-TITLE-02).

    The entries, the controls hint (UI-TITLE-05) and the version and commit (UI-TITLE-04).
    """
    root = element(doc, "div", "menu-screen title-screen")
    score = element(doc, "div", "title-score")
    score.append(
        element(doc, "div", "title-score-label", view.high_score_label),
        element(doc, "div", "title-high-score", str(view.high_score)),
    )
    # The entries in order, each with its index (UI-TITLE-06): the optional ones after the two
    # of every title.
    labels = [["title-start", view.start], ["title-settings", view.settings]]
    if view.fullscreen is not None:
        labels.append(["title-fullscreen", view.fullscreen])
    if view.dev is not None:
        labels.append(["title-dev", view.dev])
    entries = []
    for index, label in enumerate(labels):
        item = entry(doc, label[0], index, view.selected == index, handlers.on_tap)
        item.textContent = label[1]
        entries.append(item)
    version = element(doc, "div", "title-version")
    version.append(
        element(doc, "div", "version-number", "v" + view.version),
        element(doc, "div", "version-commit", view.commit),
    )
    root.append(
        score,
        element(doc, "h1", "title-name", view.title),
    )
    for item in entries:
        root.append(item)
    root.append(
        element(doc, "div", "menu-hint title-hint", view.hint),
        version,
    )
    return root
