"""What the menu overlay can show: one view class per screen.
Each class has a `kind` and the fields of its interface, as
positional constructor arguments in the order listed."""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from ui.caption_row import Caption  # noqa: E402

__pragma__("noskip")


class LoadingView:
    """Loading screen (P01-R02)."""

    kind = "loading"

    def __init__(self, text: str, progress: float) -> None:
        self.text = text
        # 0..1.
        self.progress = progress


class TitleView:
    """Title screen (P01-R04)."""

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
    ) -> None:
        self.title = title
        self.high_score_label = high_score_label
        self.high_score = high_score
        self.start = start
        # The Settings entry under Start (P12-R04).
        self.settings = settings
        # The entry selected: 0 Start, 1 Settings.
        self.selected = selected
        self.hint = hint
        # Version and short commit hash (ENG-83).
        self.version = version
        self.commit = commit


class BackView:
    """Fields shared by the screens that have a Back button."""

    def __init__(self, heading: str, hint: str, back: str, selected: int) -> None:
        self.heading = heading
        self.hint = hint
        self.back = back
        self.selected = selected


class ShipSelectView(BackView):
    """Ship select screen (P01-R06): one card per ship, under its 3D model."""

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
    """Level select screen (P01-R07)."""

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
    """Choices of a "Game over" panel (P07-R08): their labels, and the one selected."""

    def __init__(self, labels: list[str], selected: int) -> None:
        self.labels = labels
        self.selected = selected


class LevelCompleteView:
    """The "Level complete" overlay (P06-R03), or "Game over" when every life is lost (GD-20)."""

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
        # The attempt's score (P11-R03).
        self.score = score
        # Shown when the score beat the saved high score (P11-R03); none otherwise.
        self.new_high_score = new_high_score
        self.hint = hint
        # "Game over" after the mini boss (P07-R08): Continue or level select; None otherwise.
        self.choices = choices


class PauseQuestion:
    """The `Leave the level?` question (P12-R02), with its choices."""

    def __init__(self, text: str, choices: list[str], selected: int) -> None:
        self.text = text
        self.choices = choices
        self.selected = selected


class PauseView:
    """The pause menu (P12-R02), over the dimmed playfield."""

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
    """Game screen (P06-R02): what the overlay shows over the level being played."""

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
        # Label of the on-screen pause button (P12-R01).
        self.pause = pause
        self.complete = complete
        # The pause menu, while the level is paused (P12-R02).
        self.paused = paused
        # The entry selected on the panel (its choices, P07-R08, or the pause menu), for taps.
        self.selected = selected


class SliderView:
    """One slider of the settings screen (P12-R04): value from 0 to `max`."""

    def __init__(self, label: str, value: int, max_value: int) -> None:
        self.label = label
        self.value = value
        self.max = max_value


class SettingsView(BackView):
    """Settings screen (P12-R04): the volume sliders."""

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
        # Opened from the pause menu: the paused level shows dimmed behind it.
        self.over_level = over_level


__pragma__("skip")
# Everything the menu overlay can show.
type MenuView = (
    LoadingView | TitleView | ShipSelectView | LevelSelectView | GameScreenView | SettingsView
)
__pragma__("noskip")
