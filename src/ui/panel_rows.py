"""Helpers shared by the viewer panels (`enemy_viewer_panel`, `shot_viewer_panel`,
`prop_viewer_panel`). They have no TypeScript file of their own: they hold the code the TypeScript
panels repeat (button rows, readouts, clamping)."""

from org.transcrypt.stubs.browser import __pragma__, window

__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any  # noqa: E402

__pragma__("noskip")

from ui.screens.elements import array_from, replace_children  # noqa: E402


def count_at(counts: list[int], index: int) -> int:
    """`levelCounts[index] ?? 1`: the number of levels of a weapon, 1 when it is unknown."""
    if index >= 0 and index < len(counts):
        return counts[index]
    return 1


def clamp_index(value: int, count: int) -> int:
    """Keeps an index within `0 .. count - 1` (0 when there is nothing to pick)."""
    return int(window.Math.min(window.Math.max(0, value), window.Math.max(0, count - 1)))


def pick(change: dict[str, Any], key: str, fallback: Any) -> Any:
    """The value `key` of a partial change, or the current `fallback` when the change omits it."""
    return change.get(key, fallback)


def _group_from(groups: list[Any], index: int) -> Any:
    """The heading that starts at button `index`, or None."""
    for group in groups:
        if group.start == index:
            return group
    return None


def _button(doc: Any, label: str, index: int) -> Any:
    button = doc.createElement("button")
    button["type"] = "button"
    button.dataset.index = str(index)
    button.textContent = label
    return button


def fill_row(
    doc: Any,
    row: Any,
    labels: list[str],
    selected: Callable[[int], bool],
    groups: list[Any],
) -> None:
    """Rebuilds the buttons of `row` when their count changed, then marks the selected ones. A
    group heading goes before the button it starts at (P08-R12).
    """
    if len(array_from(row.querySelectorAll("button"))) != len(labels):
        nodes: list[Any] = []
        for i, label in enumerate(labels):
            group = _group_from(groups, i)
            if group is not None:
                heading = doc.createElement("div")
                heading.className = "enemy-group"
                heading.textContent = group.label
                nodes.append(heading)
            nodes.append(_button(doc, label, i))
        replace_children(row, nodes)
    buttons = array_from(row.querySelectorAll("button"))
    for i, button in enumerate(buttons):
        button.classList.toggle("selected", selected(i))
        button.setAttribute("aria-pressed", "true" if selected(i) else "false")


def set_text(readouts: dict[str, Any], key: str, text: str) -> None:
    """Writes a readout's text, only when it changed."""
    el = readouts.get(key)
    if el and el.textContent != text:
        el.textContent = text
