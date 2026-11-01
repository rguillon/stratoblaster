"""What the menu overlay can show: one view class per screen.
Each class has a `kind` and the fields of its interface, as
positional constructor arguments in the order listed."""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from ui.caption_row import Caption  # noqa: E402 (after the Transcrypt skip block, ENG-153)

__pragma__("noskip")


class LoadingView:
    """Loading screen (UI-LOAD-03)."""

    kind = "loading"

    def __init__(self, text: str, progress: float) -> None:
        self.text = text
        # 0..1.
        self.progress = progress


class TitleView:
    """Title screen (UI-TITLE-01)."""

    kind = "title"

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        title: str,
        high_score_label: str,
        high_score: int,
        start: str,
        settings: str,
        selected: int,
        hint: str,
        version: str,
        commit: str,
        dev: str | None = None,
    ) -> None:
        self.title = title
        self.high_score_label = high_score_label
        self.high_score = high_score
        self.start = start
        # The Settings entry under Start (UI-SET-01).
        self.settings = settings
        # The entry selected: 0 Start, 1 Settings.
        self.selected = selected
        self.hint = hint
        # Version and short commit hash (ENG-83).
        self.version = version
        self.commit = commit
        # The Dev entry under Settings (D-199, with `?dev`); None: no such entry.
        self.dev = dev


class BackView:
    """Fields shared by the screens that have a Back button."""

    def __init__(self, heading: str, hint: str, back: str, selected: int) -> None:
        self.heading = heading
        self.hint = hint
        self.back = back
        self.selected = selected


class ShipSelectView(BackView):
    """Ship select screen (UI-SHIP-02): one card per ship, under its 3D model."""

    kind = "ship-select"

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        heading: str,
        hint: str,
        back: str,
        selected: int,
        ships: list[Caption],
        cards_width_percent: float,
    ) -> None:
        BackView.__init__(self, heading, hint, back, selected)
        self.ships = ships
        # Width of the row of cards, in % of the screen, to line them up with the models.
        self.cards_width_percent = cards_width_percent


class LevelOption:
    """One level cell of the level select screen."""

    def __init__(self, label: str, locked: bool) -> None:
        self.label = label
        self.locked = locked


class LevelSelectView(BackView):
    """Level select screen (UI-LEVEL-01)."""

    kind = "level-select"

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        heading: str,
        hint: str,
        back: str,
        selected: int,
        columns: int,
        levels: list[LevelOption],
        locked_text: str,
    ) -> None:
        BackView.__init__(self, heading, hint, back, selected)
        self.columns = columns
        self.levels = levels
        self.locked_text = locked_text


class LevelChoices:
    """Choices of a "Game over" panel (UI-OVER-06): their labels, and the one selected."""

    def __init__(self, labels: list[str], selected: int) -> None:
        self.labels = labels
        self.selected = selected


class LevelCompleteView:
    """The "Level complete" overlay (UI-OVER-01), or "Game over" when every life is lost
    (UI-OVER-05)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        heading: str,
        over: bool,
        level: str,
        enemies: str,
        score: str,
        hint: str,
        new_high_score: str | None = None,
        choices: LevelChoices | None = None,
    ) -> None:
        self.heading = heading
        # Whether the game is over (the panel shows as a loss).
        self.over = over
        # The level's label, e.g. `1-2`.
        self.level = level
        # How many enemies were destroyed out of how many came.
        self.enemies = enemies
        # The attempt's score (UI-OVER-01).
        self.score = score
        # Shown when the score beat the saved high score (UI-OVER-02); none otherwise.
        self.new_high_score = new_high_score
        self.hint = hint
        # "Game over" after the mini boss (UI-OVER-06): Continue or level select; None otherwise.
        self.choices = choices


class PauseQuestion:
    """The `Leave the level?` question (UI-PAUSE-10), with its choices."""

    def __init__(self, text: str, choices: list[str], selected: int) -> None:
        self.text = text
        self.choices = choices
        self.selected = selected


class PauseView:
    """The pause menu (UI-PAUSE-07), over the dimmed playfield."""

    def __init__(
        self,
        heading: str,
        entries: list[str],
        hint: str,
        question: PauseQuestion | None = None,
    ) -> None:
        self.heading = heading
        # Resume, Settings, Main menu.
        self.entries = entries
        self.hint = hint
        # The `Leave the level?` question, when it shows; None otherwise.
        self.question = question


class GameScreenView:
    """Game screen (UI-FLOW-01): what the overlay shows over the level being played."""

    kind = "game"

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        level: str,
        fire: str,
        pause: str,
        complete: LevelCompleteView | None,
        paused: PauseView | None,
        selected: int,
    ) -> None:
        self.level = level
        # Label of the on-screen fire button.
        self.fire = fire
        # Label of the on-screen pause button (UI-PAUSE-02).
        self.pause = pause
        self.complete = complete
        # The pause menu, while the level is paused (UI-PAUSE-07).
        self.paused = paused
        # The entry selected on the panel (its choices, UI-OVER-06, or the pause menu), for taps.
        self.selected = selected


class SliderView:
    """One slider of the settings screen (UI-SET-02): value from 0 to `max`."""

    def __init__(self, label: str, value: int, max_value: int) -> None:
        self.label = label
        self.value = value
        self.max = max_value


class SettingsView(BackView):
    """Settings screen (UI-SET-02): the volume sliders."""

    kind = "settings"

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        heading: str,
        hint: str,
        back: str,
        selected: int,
        sliders: list[SliderView],
        over_level: bool,
    ) -> None:
        BackView.__init__(self, heading, hint, back, selected)
        self.sliders = sliders
        # Opened from the pause menu: the paused level shows dimmed behind it (UI-SET-07).
        self.over_level = over_level


class DevMenuView(BackView):
    """The dev menu (D-199): one entry per viewer."""

    kind = "dev"

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        heading: str,
        hint: str,
        back: str,
        selected: int,
        entries: list[str],
    ) -> None:
        BackView.__init__(self, heading, hint, back, selected)
        self.entries = entries


class DevChoice:
    """An entry of a dev viewer's menu (D-206): its `label`, the item it shows (`index` in the
    viewer's list), whether it is the one shown (`selected`: for a group, the shown item is in
    it), and whether it is a group's heading (`heading`) rather than an item."""

    def __init__(self, label: str, index: int, selected: bool, heading: bool = False) -> None:
        self.label = label
        self.index = index
        self.selected = selected
        self.heading = heading


class DevViewerView(BackView):
    """A dev viewer (D-199): the item shown over the 3D view, and where it is in the list. The
    status line (loading, the level's time) is written by the viewer itself, each frame."""

    kind = "dev-viewer"

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        heading: str,
        hint: str,
        back: str,
        selected: int,
        item: str,
        position: str,
        scrub: bool,
        menu: list[DevChoice] | None = None,
    ) -> None:
        BackView.__init__(self, heading, hint, back, selected)
        self.item = item
        # E.g. `3 / 40`.
        self.position = position
        # True: the wheel scrubs the level's time (the levels viewer); False: it moves through
        # the items.
        self.scrub = scrub
        # D-206, D-208: the scrolling menu of the items, each group's heading (to its first item)
        # before its items when they are in groups. None: no menu.
        self.menu = menu


__pragma__("skip")
# Everything the menu overlay can show.
type MenuView = (
    LoadingView
    | TitleView
    | ShipSelectView
    | LevelSelectView
    | GameScreenView
    | SettingsView
    | DevMenuView
    | DevViewerView
)
__pragma__("noskip")
