"""The boss health bar (P07-R02): a slim gauge up the left edge of
the playfield, with the boss's kind and name written along it and the health of its parts filling
it from the bottom."""

from org.transcrypt.stubs.browser import __pragma__, window

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from ui.screens.elements import element, replace_children  # noqa: E402


class BossBarFrame:
    """What the boss health bar shows on one frame (P07-R02)."""

    def __init__(self, name: str, rank: str, share: float, notches: list[float]) -> None:
        self.name = name
        # Its kind, e.g. `MINI BOSS` or `BOSS`.
        self.rank = rank
        # Share of the bar filled, 0..1.
        self.share = share
        # Where each destroyable part's share ends along the bar, 0..1.
        self.notches = notches


def _percent(share: float) -> str:
    clamped = window.Math.min(1, window.Math.max(0, share))
    return str(window.Math.round(clamped * 1000) / 10) + "%"


class BossBar:
    """The boss health bar (P07-R02): the boss's kind and name written along it, and the health of
    its core and parts together filling it from the bottom, with a notch at the end of each part's
    share. Hidden while no boss is fought; the page is touched only on changes.
    """

    def __init__(self, doc: Any, parent: Any) -> None:
        self._doc = doc
        self.root = element(doc, "div", "boss-bar")
        self.root.hidden = True
        label = element(doc, "div", "boss-label")
        self._rank = element(doc, "span", "boss-rank")
        self._name = element(doc, "span", "boss-name")
        label.append(self._rank, self._name)
        bar = element(doc, "div", "boss-track")
        self._fill = element(doc, "div", "boss-fill")
        self._notches = element(doc, "div", "boss-notches")
        bar.append(self._fill, self._notches)
        self.root.append(label, bar)
        parent.append(self.root)
        self._shown = ""
        self._notch_key = ""

    def update(self, frame: BossBarFrame | None) -> None:
        """Shows `frame`, or hides the bar when there is no boss."""
        key = "|".join([frame.rank, frame.name, _percent(frame.share)]) if frame is not None else ""
        if key == self._shown:
            return
        self._shown = key
        self.root.hidden = frame is None
        if frame is None:
            return
        self._rank.textContent = frame.rank
        self._name.textContent = frame.name
        self._fill.style.height = _percent(frame.share)
        self._set_notches(frame.notches)

    def _set_notches(self, notches: list[float]) -> None:
        key = ",".join([_percent(at) for at in notches])
        if key == self._notch_key:
            return
        self._notch_key = key
        nodes: list[Any] = []
        for at in notches:
            notch = element(self._doc, "div", "boss-notch")
            notch.style.bottom = _percent(at)
            nodes.append(notch)
        replace_children(self._notches, nodes)
