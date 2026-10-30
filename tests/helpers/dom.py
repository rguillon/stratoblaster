"""A small fake DOM for the UI tests: elements with a class list, attributes, listeners and
children, enough to read what a screen renders and to fire the events its handlers listen to.
Only the calls the game makes are modelled (the browser is not run)."""

import inspect
from collections.abc import Callable
from typing import Any


class FakeStyle:
    """A `CSSStyleDeclaration`: any property can be set and read back."""

    def __init__(self) -> None:
        self.__dict__["_values"] = {}

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        return self.__dict__["_values"].get(name, "")

    def __setattr__(self, name: str, value: Any) -> None:
        self.__dict__["_values"][name] = value


class FakeClassList:
    """A `DOMTokenList` over the element's class names."""

    def __init__(self, element: "FakeElement") -> None:
        self._element = element

    def _tokens(self) -> list[str]:
        return self._element.className.split()

    def _write(self, tokens: list[str]) -> None:
        self._element.className = " ".join(tokens)

    def add(self, name: str) -> None:
        tokens = self._tokens()
        if name not in tokens:
            tokens.append(name)
            self._write(tokens)

    def remove(self, name: str) -> None:
        self._write([token for token in self._tokens() if token != name])

    def contains(self, name: str) -> bool:
        return name in self._tokens()

    def toggle(self, name: str, force: bool | None = None) -> bool:
        present = self.contains(name)
        want = (not present) if force is None else force
        if want:
            self.add(name)
        else:
            self.remove(name)
        return want


class FakeRect:
    def __init__(self, left: float = 0, top: float = 0, width: float = 0, height: float = 0):
        self.left = left
        self.top = top
        self.width = width
        self.height = height


class FakeComputedStyle:
    def __init__(self, font_size: str = "16px") -> None:
        self.fontSize = font_size  # noqa: N815 (DOM name)


class FakeView:
    """The `defaultView` of the document: `getComputedStyle`, which reports the element's own
    font size when one was set (or 16 px)."""

    def getComputedStyle(self, element: "FakeElement") -> FakeComputedStyle:  # noqa: N802
        size = element.style.fontSize
        return FakeComputedStyle(size if size else "16px")


class FakeElement:
    """An element: tag, class name, text, style, attributes, children, listeners."""

    def __init__(self, doc: "FakeDocument", tag: str, namespace: str | None = None) -> None:
        self.ownerDocument = doc  # noqa: N815 (DOM name)
        self.tagName = tag
        self.namespace = namespace
        self.className = ""
        self.textContent = ""
        self.style = FakeStyle()
        self.dataset = FakeStyle()
        self.classList = FakeClassList(self)  # noqa: N815 (DOM name)
        self.hidden = False
        self.value: Any = None
        self.clientWidth = 0  # noqa: N815
        self.scrollWidth = 0  # noqa: N815
        self.offsetWidth = 0  # noqa: N815
        self.clientX = 0  # noqa: N815
        self.clientY = 0  # noqa: N815
        self.parentElement: FakeElement | None = None  # noqa: N815
        self.children: list[FakeElement] = []
        self.attributes: dict[str, str] = {}
        self.listeners: dict[str, list[Callable[..., Any]]] = {}
        self.rect = FakeRect()
        self.stopped = 0

    @property
    def childNodes(self) -> list["FakeElement"]:  # noqa: N802
        return list(self.children)

    def append(self, *nodes: "FakeElement") -> None:
        for node in nodes:
            if node.parentElement is not None:
                node.parentElement.children.remove(node)
            node.parentElement = self
            self.children.append(node)

    def replaceChildren(self, *nodes: "FakeElement") -> None:  # noqa: N802
        for child in self.children:
            child.parentElement = None
        self.children = []
        self.append(*nodes)

    def remove(self) -> None:
        if self.parentElement is not None:
            self.parentElement.children.remove(self)
            self.parentElement = None

    def setAttribute(self, name: str, value: Any) -> None:  # noqa: N802
        self.attributes[name] = str(value)
        if name == "class":
            self.className = str(value)

    def getAttribute(self, name: str) -> str | None:  # noqa: N802
        return self.attributes.get(name)

    def getBoundingClientRect(self) -> FakeRect:  # noqa: N802
        return self.rect

    def addEventListener(self, kind: str, listener: Callable[..., Any]) -> None:  # noqa: N802
        self.listeners.setdefault(kind, []).append(listener)

    def removeEventListener(self, kind: str, listener: Callable[..., Any]) -> None:  # noqa: N802
        self.listeners.get(kind, []).remove(listener)

    def listener_count(self, kind: str) -> int:
        return len(self.listeners.get(kind, []))

    def fire(self, kind: str, event: Any = None) -> None:
        """Dispatches an event of `kind` to the listeners on this element."""
        if event is None:
            event = FakeEvent(self)
        for listener in list(self.listeners.get(kind, [])):
            _call_listener(listener, event)

    def descendants(self) -> list["FakeElement"]:
        found: list[FakeElement] = []
        for child in self.children:
            found.append(child)
            found.extend(child.descendants())
        return found

    def querySelector(self, selector: str) -> "FakeElement | None":  # noqa: N802
        """A selector of one simple part: `.class`, `.a.b` or `tag`, or `.a .b` (descendant)."""
        parts = selector.split()
        if len(parts) > 1:
            head = self.querySelector(parts[0])
            return head.querySelector(" ".join(parts[1:])) if head is not None else None
        for node in self.descendants():
            if _matches(node, parts[0]):
                return node
        return None

    def querySelectorAll(self, selector: str) -> list["FakeElement"]:  # noqa: N802
        return [node for node in self.descendants() if _matches(node, selector)]


def _call_listener(listener: Callable[..., Any], event: Any) -> None:
    """Calls a listener with the event, as the browser does. A JavaScript function ignores the
    arguments it does not name, so a listener that takes none is called with none."""
    if len(inspect.signature(listener).parameters) == 0:
        listener()
    else:
        listener(event)


def _matches(node: FakeElement, selector: str) -> bool:
    if selector.startswith("."):
        classes = selector[1:].split(".")
        return all(name in node.className.split() for name in classes)
    return node.tagName == selector


class FakeEvent:
    """A pointer or mouse event: its position and whether it was stopped."""

    def __init__(self, target: FakeElement | None = None, x: float = 0, y: float = 0) -> None:
        self.target = target
        self.clientX = x  # noqa: N815
        self.clientY = y  # noqa: N815
        self.stopped = False

    def stopPropagation(self) -> None:  # noqa: N802
        self.stopped = True


class FakeDocument:
    """The document: element factories and the default view."""

    def __init__(self) -> None:
        self.defaultView = FakeView()  # noqa: N815
        self.created: list[FakeElement] = []

    def createElement(self, tag: str) -> FakeElement:  # noqa: N802
        element = FakeElement(self, tag)
        self.created.append(element)
        return element

    def createElementNS(self, namespace: str, tag: str) -> FakeElement:  # noqa: N802
        element = FakeElement(self, tag, namespace)
        self.created.append(element)
        return element
