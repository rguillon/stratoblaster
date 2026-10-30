"""Controls of the props page (reviewer, 2026-10-28), ported from `ui/prop-viewer-panel.ts`: a
button per group, a button per prop of the shown group, and a readout of the picked prop. Uses the
enemies page's styles."""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any, Protocol  # noqa: E402


class PropGroupLike(Protocol):
    """A group of props (`PropGroup` in `render/game-view.ts`, not ported yet): its label, the
    ids of its props, and optional notes shown after some ids' names."""

    label: str
    ids: list[str]
    notes: dict[str, str] | None


__pragma__("noskip")

from ui.screens.elements import array_from, replace_children  # noqa: E402

HELP = "Drag to turn, wheel to zoom. Click a prop, or ←/→ to step through them."


class PropViewerSelection:
    """What the props page shows: a group, and the prop picked in it (index into its ids)."""

    def __init__(self, group: int, prop: int) -> None:
        self.group = group
        self.prop = prop


class PropViewerPanelOptions:
    """The options of a `PropViewerPanel`."""

    def __init__(
        self,
        doc: Any,
        parent: Any,
        groups: list[PropGroupLike],
        initial: PropViewerSelection,
        on_change: Callable[[PropViewerSelection], None],
        on_wireframe: Callable[[bool], None] | None = None,
    ) -> None:
        self.doc = doc
        self.parent = parent
        self.groups = groups
        self.initial = initial
        self.on_change = on_change
        # Called with True for the wireframe view, False for the normal one. No buttons when None.
        self.on_wireframe = on_wireframe


def _group_at(groups: list[PropGroupLike], index: int) -> Any:
    if index >= 0 and index < len(groups):
        return groups[index]
    return None


class PropViewerPanel:
    """Controls of the props page: a button per group, a button per prop of the shown group, and a
    readout of the picked prop.
    """

    def __init__(self, options: PropViewerPanelOptions) -> None:
        doc = options.doc
        self._options = options
        self._selection = options.initial
        self.root = self._element("div", "enemy-panel")
        self.root.append(self._element("div", "enemy-title", "Props"))
        self._group_row = self._element("div", "enemy-row prop-groups")
        self._prop_row = self._element("div", "enemy-row prop-kinds")
        self._readout = self._element("div", "enemy-readout prop-readout")
        self.root.append(self._group_row, self._prop_row, self._readout)
        self.root.append(self._element("div", "enemy-help", HELP))
        if options.on_wireframe is not None:
            self._group_row.before(self._view_row(options.on_wireframe))
        for i, group in enumerate(options.groups):
            button = doc.createElement("button")
            button.textContent = group.label + " (" + str(len(group.ids)) + ")"
            button.addEventListener("click", self._group_handler(i))
            self._group_row.append(button)
        options.parent.append(self.root)
        self._render(True)

    @property
    def selection(self) -> PropViewerSelection:
        return self._selection

    def update(self, selection: PropViewerSelection) -> None:
        """Sets the selection from code (keys, clicks on the scene), without calling `on_change`."""
        regroup = selection.group != self._selection.group
        self._selection = selection
        self._render(regroup)

    def set_readout(self, text: str) -> None:
        """Shows `text` (the picked prop's id and size) under the buttons."""
        self._readout.textContent = text

    def _choose(self, selection: PropViewerSelection) -> None:
        self.update(selection)
        self._options.on_change(selection)

    def _group_handler(self, group: int) -> Callable[[Any], None]:
        def handler(_event: Any) -> None:
            self._choose(PropViewerSelection(group, 0))

        return handler

    def _prop_handler(self, group: int, prop: int) -> Callable[[Any], None]:
        def handler(_event: Any) -> None:
            self._choose(PropViewerSelection(group, prop))

        return handler

    def _view_row(self, on_wireframe: Callable[[bool], None]) -> Any:
        """The Normal / Wireframe buttons, Normal first and picked."""
        row = self._element("div", "enemy-row prop-views")
        buttons: list[Any] = []
        for i, label in enumerate(["Normal", "Wireframe"]):
            button = self._options.doc.createElement("button")
            button.textContent = label
            button.classList.toggle("selected", i == 0)
            buttons.append(button)
        for i, button in enumerate(buttons):
            button.addEventListener("click", _view_handler(buttons, button, on_wireframe, i == 1))
            row.append(button)
        return row

    def _element(self, tag: str, class_name: str, text: str = "") -> Any:
        el = self._options.doc.createElement(tag)
        el.className = class_name
        el.textContent = text
        return el

    def _render(self, regroup: bool = True) -> None:
        s = self._selection
        for i, b in enumerate(array_from(self._group_row.children)):
            b.classList.toggle("selected", i == s.group)
        group = _group_at(self._options.groups, s.group)
        if regroup:
            ids = group.ids if group is not None else []
            nodes: list[Any] = []
            for i, prop_id in enumerate(ids):
                button = self._options.doc.createElement("button")
                note = group.notes.get(prop_id) if group.notes is not None else None
                button.textContent = prop_id + " · " + note if note else prop_id
                button.addEventListener("click", self._prop_handler(s.group, i))
                nodes.append(button)
            replace_children(self._prop_row, nodes)
        for i, b in enumerate(array_from(self._prop_row.children)):
            b.classList.toggle("selected", i == s.prop)


def _view_handler(
    buttons: list[Any], button: Any, on_wireframe: Callable[[bool], None], wireframe: bool
) -> Callable[[Any], None]:
    def handler(_event: Any) -> None:
        for b in buttons:
            b.classList.toggle("selected", b == button)
        on_wireframe(wireframe)

    return handler
