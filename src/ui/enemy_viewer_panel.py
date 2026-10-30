"""Controls of the enemies page (P05-R11), ported from `ui/enemy-viewer-panel.ts`: a button per
enemy kind, the view, the player's weapon and level, fire and pause toggles, and readouts."""

from org.transcrypt.stubs.browser import __pragma__, window

__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any  # noqa: E402

__pragma__("noskip")

from ui.panel_rows import clamp_index, count_at, fill_row, pick, set_text  # noqa: E402

VIEWS = ["behaviour", "model", "wireframe"]
VIEW_LABELS = ["Behaviour", "Model (M)", "Wireframe (V)"]
TOGGLES = ["fire", "paused", "living", "hitbox"]


class EnemyViewerSelection:
    """What the enemies page shows (P05-R11). Indices into the game's enemy kinds and weapons."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        kind: int,
        view: str,
        weapon: int,
        level: int,
        fire: bool,
        paused: bool,
        living: bool,
        hitbox: bool,
    ) -> None:
        self.kind = kind
        # `behaviour`: the enemy flies and attacks; `model`: its model alone, turning;
        # `wireframe`.
        self.view = view
        self.weapon = weapon
        # 1-based.
        self.level = level
        self.fire = fire
        self.paused = paused
        # P16-R10: the models' living motion (P16-R07) runs.
        self.living = living
        # P16-R10: the hit circles are drawn over the model in the model view.
        self.hitbox = hitbox


class EnemyViewerReadout:
    """Live numbers shown under the controls."""

    def __init__(
        self,
        enemies: int,
        shots: int,
        kills: int,
        score: int,
        stage: str | None = None,
    ) -> None:
        self.enemies = enemies
        self.shots = shots
        self.kills = kills
        self.score = score
        # A line about the boss shown (its stage, P07-R09), on the `bosses/` page.
        self.stage = stage


class EnemyGroup:
    """A heading over the kind buttons (P08-R12: the bosses grouped by world), placed before the
    kind at index `start`.
    """

    def __init__(self, label: str, start: int) -> None:
        self.label = label
        self.start = start


class EnemyViewerPanelOptions:
    """The options of an `EnemyViewerPanel`."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        doc: Any,
        parent: Any,
        kinds: list[str],
        weapons: list[str],
        level_counts: list[int],
        initial: EnemyViewerSelection,
        help_text: str,
        on_change: Callable[[EnemyViewerSelection], None],
        title: str | None = None,
        groups: list[EnemyGroup] | None = None,
    ) -> None:
        self.doc = doc
        self.parent = parent
        self.kinds = kinds
        self.weapons = weapons
        # Number of levels of each weapon.
        self.level_counts = level_counts
        self.initial = initial
        # A line about the keys, under the readouts.
        self.help_text = help_text
        self.on_change = on_change
        # Heading of the panel; `Enemies` when None (the `bosses/` page reuses it, P07-R09).
        self.title = title
        # Headings over the kind buttons; none when None.
        self.groups = groups


def _view_at(index: int) -> str:
    return VIEWS[index] if index >= 0 and index < len(VIEWS) else "behaviour"


class EnemyViewerPanel:
    """Controls of the enemies page: a button per enemy kind, the view (behaviour, model or
    wireframe), the player's weapon and level, fire and pause toggles, and readouts. `update`
    changes the selection from code (keyboard shortcuts).
    """

    def __init__(self, options: EnemyViewerPanelOptions) -> None:
        doc = options.doc
        self._options = options
        self._selection = options.initial
        self._rows: dict[str, Any] = {}
        self._readouts: dict[str, Any] = {}
        self.root = doc.createElement("div")
        self.root.className = "enemy-panel"
        title = doc.createElement("div")
        title.className = "enemy-title"
        title.textContent = options.title if options.title is not None else "Enemies"
        self.root.append(title)
        self._add_row("kind", _kind_change)
        self._add_row("view", _view_change)
        self._add_row("weapon", _weapon_change)
        self._add_row("level", _level_change)

        def toggle_change(i: int) -> dict[str, Any]:
            return self._toggle_change(i)

        self._add_row("toggles", toggle_change)
        for key in ["enemies", "shots", "kills", "score", "stage"]:
            el = doc.createElement("div")
            el.className = "enemy-readout enemy-" + key
            self._readouts[key] = el
            self.root.append(el)
        help_el = doc.createElement("div")
        help_el.className = "enemy-help"
        help_el.textContent = options.help_text
        self.root.append(help_el)
        options.parent.append(self.root)
        self._render()

    @property
    def selection(self) -> EnemyViewerSelection:
        return self._selection

    def update(self, change: dict[str, Any]) -> None:
        """Changes the selection by the fields of `change`, keeping the indices and the level in
        range.
        """
        s = self._selection
        kind = clamp_index(pick(change, "kind", s.kind), len(self._options.kinds))
        weapon = clamp_index(pick(change, "weapon", s.weapon), len(self._options.weapons))
        levels = count_at(self._options.level_counts, weapon)
        level = window.Math.min(window.Math.max(1, pick(change, "level", s.level)), levels)
        self._selection = EnemyViewerSelection(
            kind,
            pick(change, "view", s.view),
            weapon,
            level,
            pick(change, "fire", s.fire),
            pick(change, "paused", s.paused),
            pick(change, "living", s.living),
            pick(change, "hitbox", s.hitbox),
        )
        self._render()
        self._options.on_change(self._selection)

    def show_readout(self, readout: EnemyViewerReadout) -> None:
        """Shows the live numbers."""
        set_text(self._readouts, "enemies", "Enemies: " + str(readout.enemies))
        set_text(self._readouts, "shots", "Enemy shots: " + str(readout.shots))
        set_text(self._readouts, "kills", "Destroyed: " + str(readout.kills))
        set_text(self._readouts, "score", "Score: " + str(readout.score))
        set_text(self._readouts, "stage", "" if readout.stage is None else readout.stage)

    def _add_row(self, name: str, change: Callable[[int], dict[str, Any]]) -> None:
        row = self._options.doc.createElement("div")
        row.className = "enemy-row enemy-" + name

        def on_click(event: Any) -> None:
            button = event.target.closest("button")
            if button:
                index = window.Number(button.dataset.index)
                if window.Number.isInteger(index):
                    self.update(change(index))

        row.addEventListener("click", on_click)
        self._rows[name] = row
        self.root.append(row)

    def _toggle_change(self, i: int) -> dict[str, Any]:
        """The change that inverts toggle `i` (see `TOGGLES`)."""
        if i < 0 or i >= len(TOGGLES):
            return {}
        s = self._selection
        current = [s.fire, s.paused, s.living, s.hitbox][i]
        return {TOGGLES[i]: not current}

    def _render(self) -> None:
        """Rebuilds the buttons (the level row depends on the weapon) and marks the selected
        ones.
        """
        s = self._selection
        count = count_at(self._options.level_counts, s.weapon)
        levels = ["L" + str(i + 1) for i in range(count)]
        groups = self._options.groups if self._options.groups is not None else []
        kind_row = self._rows["kind"]
        fill_row(self._options.doc, kind_row, self._options.kinds, lambda i: i == s.kind, groups)
        fill_row(
            self._options.doc, self._rows["view"], VIEW_LABELS, lambda i: VIEWS[i] == s.view, []
        )
        weapon_row = self._rows["weapon"]
        fill_row(self._options.doc, weapon_row, self._options.weapons, lambda i: i == s.weapon, [])
        fill_row(self._options.doc, self._rows["level"], levels, lambda i: i + 1 == s.level, [])
        states = [s.fire, s.paused, s.living, s.hitbox]
        labels = ["Fire (F)", "Pause (P)", "Motion (L)", "Hitbox (H)"]
        fill_row(self._options.doc, self._rows["toggles"], labels, lambda i: states[i] is True, [])


def _kind_change(i: int) -> dict[str, Any]:
    return {"kind": i}


def _view_change(i: int) -> dict[str, Any]:
    return {"view": _view_at(i)}


def _weapon_change(i: int) -> dict[str, Any]:
    return {"weapon": i}


def _level_change(i: int) -> dict[str, Any]:
    return {"level": i + 1}
