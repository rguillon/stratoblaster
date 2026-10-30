"""Controls of the shots viewer (P03-R10), ported from `ui/shot-viewer-panel.ts`: a row of buttons
per choice (ship, weapon, level) and two toggles, plus readouts."""

from org.transcrypt.stubs.browser import __pragma__, window

__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any  # noqa: E402

__pragma__("noskip")

from ui.panel_rows import count_at, fill_row, pick, set_text  # noqa: E402


class ShotViewerSelection:
    """What the shots viewer shows (P03-R10). Indices into the game's ships and weapons."""

    def __init__(self, ship: int, weapon: int, level: int, guides: bool, targets: bool) -> None:
        self.ship = ship
        self.weapon = weapon
        # 1-based.
        self.level = level
        self.guides = guides
        self.targets = targets


class ShotViewerReadout:
    """Live numbers shown under the controls."""

    def __init__(self, summary: str, shots: int, damage_per_second: float, kills: int) -> None:
        self.summary = summary
        self.shots = shots
        self.damage_per_second = damage_per_second
        self.kills = kills


class ShotViewerPanelOptions:
    """The options of a `ShotViewerPanel`."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        doc: Any,
        parent: Any,
        ships: list[str],
        weapons: list[str],
        level_counts: list[int],
        initial: ShotViewerSelection,
        on_change: Callable[[ShotViewerSelection], None],
    ) -> None:
        self.doc = doc
        self.parent = parent
        self.ships = ships
        self.weapons = weapons
        # Number of levels of each weapon.
        self.level_counts = level_counts
        self.initial = initial
        self.on_change = on_change


class ShotViewerPanel:
    """Controls of the shots viewer. `update` changes the selection from code (keyboard
    shortcuts).
    """

    def __init__(self, options: ShotViewerPanelOptions) -> None:
        doc = options.doc
        self._options = options
        self._selection = options.initial
        self._rows: dict[str, Any] = {}
        self._readouts: dict[str, Any] = {}
        self.root = doc.createElement("div")
        self.root.className = "shot-panel"
        self._add_row("ship", lambda i: {"ship": i})
        self._add_row("weapon", lambda i: {"weapon": i})
        self._add_row("level", lambda i: {"level": i + 1})
        self._add_row("toggles", lambda i: self._flip("guides" if i == 0 else "targets"))
        for key in ["summary", "shots", "damage", "kills"]:
            el = doc.createElement("div")
            el.className = "shot-readout shot-" + key
            self._readouts[key] = el
            self.root.append(el)
        options.parent.append(self.root)
        self._render()

    @property
    def selection(self) -> ShotViewerSelection:
        return self._selection

    def update(self, change: dict[str, Any]) -> None:
        """Changes the selection by the fields of `change`, keeping the level within the selected
        weapon's levels.
        """
        s = self._selection
        weapon = pick(change, "weapon", s.weapon)
        levels = count_at(self._options.level_counts, weapon)
        level = window.Math.min(window.Math.max(1, pick(change, "level", s.level)), levels)
        self._selection = ShotViewerSelection(
            pick(change, "ship", s.ship),
            weapon,
            level,
            pick(change, "guides", s.guides),
            pick(change, "targets", s.targets),
        )
        self._render()
        self._options.on_change(self._selection)

    def show_readout(self, readout: ShotViewerReadout) -> None:
        """Shows the live numbers."""
        set_text(self._readouts, "summary", readout.summary)
        set_text(self._readouts, "shots", "Shots in flight: " + str(readout.shots))
        damage = window.Number(readout.damage_per_second).toFixed(1)
        set_text(self._readouts, "damage", "Damage/s: " + str(damage))
        set_text(self._readouts, "kills", "Targets destroyed: " + str(readout.kills))

    def _flip(self, toggle: str) -> dict[str, Any]:
        """The change that inverts one toggle (`guides` or `targets`)."""
        if toggle == "guides":
            return {"guides": not self._selection.guides}
        return {"targets": not self._selection.targets}

    def _add_row(self, name: str, change: Callable[[int], dict[str, Any]]) -> None:
        row = self._options.doc.createElement("div")
        row.className = "shot-row shot-" + name

        def on_click(event: Any) -> None:
            button = event.target.closest("button")
            if button:
                index = window.Number(button.dataset.index)
                if window.Number.isInteger(index):
                    self.update(change(index))

        row.addEventListener("click", on_click)
        self._rows[name] = row
        self.root.append(row)

    def _render(self) -> None:
        """Rebuilds the buttons (the level row depends on the weapon) and marks the selected
        ones.
        """
        s = self._selection
        count = count_at(self._options.level_counts, s.weapon)
        levels = ["L" + str(i + 1) for i in range(count)]
        fill_row(
            self._options.doc,
            self._rows["ship"],
            self._options.ships,
            lambda i: i == s.ship,
            [],
        )
        fill_row(
            self._options.doc,
            self._rows["weapon"],
            self._options.weapons,
            lambda i: i == s.weapon,
            [],
        )
        fill_row(self._options.doc, self._rows["level"], levels, lambda i: i + 1 == s.level, [])
        fill_row(
            self._options.doc,
            self._rows["toggles"],
            ["Guides (G)", "Targets (T)"],
            lambda i: s.guides if i == 0 else s.targets,
            [],
        )
