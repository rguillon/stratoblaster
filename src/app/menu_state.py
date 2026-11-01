"""The menu flow's data: the feedback of a command, the snapshot
of the flow (`MenuState`) and the options of a `MenuFlow`.

Classes take their fields in the order listed, as positional arguments (Transcrypt drops keyword
arguments). Optional fields are passed as None.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Literal  # noqa: E402

from app.settings_menu import Volumes  # noqa: E402
from core.content.level_catalog import LevelCatalog  # noqa: E402
from core.menu.menu_screen import MenuScreen  # noqa: E402
from core.systems.level_run_types import LevelCheckpoint, LevelResult  # noqa: E402

# What a command did, so the presentation can give feedback (and its sound, AUD-ENGINE-09): a
# move, a new screen, a locked level, a level paused or resumed, a slider changed.
MenuFeedback = Literal["none", "moved", "screen", "locked", "paused", "resumed", "adjusted"]

__pragma__("noskip")


class MenuState:
    """Snapshot of the menu flow."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        screen: MenuScreen,
        selection: int,
        selected_id: str | None,
        highlighted_ship_id: str,
        chosen_ship_id: str | None,
        chosen_level_id: str | None,
        transitioning: bool,
        level_result: LevelResult | None,
        choice: int,
        attempt: int,
        resume: LevelCheckpoint | None,
        paused: bool,
        leaving: bool,
        volumes: Volumes,
        dev_viewer: str | None = None,
        dev_close_up: bool = False,
    ) -> None:
        self.screen = screen
        # Index of the selected entry on the current screen.
        self.selection = selection
        # Id of the selected entry (`start`, a ship id, a level id), or None.
        self.selected_id = selected_id
        # Ship highlighted on the ship select screen.
        self.highlighted_ship_id = highlighted_ship_id
        self.chosen_ship_id = chosen_ship_id
        self.chosen_level_id = chosen_level_id
        # True during a screen transition, while input is ignored (UI-FLOW-08).
        self.transitioning = transitioning
        # The result of the level just completed, while its overlay shows (UI-OVER-01).
        self.level_result = level_result
        # The choice selected on a "Game over" panel with a checkpoint (UI-OVER-06): 0 Continue,
        # 1 level select.
        self.choice = choice
        # Goes up each time a level starts, or starts again from a checkpoint.
        self.attempt = attempt
        # Where the level being played started again from (GAME-LIFE-11), or None from its start.
        self.resume = resume
        # Whether the level being played is paused (UI-PAUSE-03): on the pause menu, or on the
        # settings screen opened from it (UI-PAUSE-09).
        self.paused = paused
        # Whether the pause menu asks `Leave the level?` (UI-PAUSE-10); `choice` is then 0 No,
        # 1 Yes.
        self.leaving = leaving
        # The music and sound effect volumes, in slider steps (UI-SET-02).
        self.volumes = volumes
        # The dev viewer shown (D-199): one of `DEV_VIEWERS`, on the `dev-viewer` screen; None
        # elsewhere. `selection` is then the item it shows.
        self.dev_viewer = dev_viewer
        # The model viewers' close-up (or game size), the levels viewer's play (or stop).
        self.dev_close_up = dev_close_up


class MenuFlowOptions:
    """Data and settings of a `MenuFlow`."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        ship_ids: list[str],
        levels: LevelCatalog,
        initial_ship_id: str | None,
        transition_seconds: float,
        result_delay_seconds: float | None,
        volumes: Volumes | None,
        volume_steps: int | None,
        dev_counts: list[int] | None = None,
        dev_groups: list[list[str]] | None = None,
    ) -> None:
        # Ship ids in display order; the first one is the default selection.
        self.ship_ids = ship_ids
        self.levels = levels
        # Ship to highlight first instead of the default one (UI-SHIP-07). Ignored if unknown.
        self.initial_ship_id = initial_ship_id
        # Input is ignored for this long after each screen change (UI-FLOW-08).
        self.transition_seconds = transition_seconds
        # ...and for this long after the "Level complete" overlay shows (UI-OVER-04).
        self.result_delay_seconds = result_delay_seconds
        # The saved volumes (UI-SET-06); the highest step is `volume_steps`.
        self.volumes = volumes
        self.volume_steps = volume_steps
        # The dev menu (D-199): how many items each viewer of `DEV_VIEWERS` shows. None: no dev
        # menu (the title screen has no Dev entry).
        self.dev_counts = dev_counts
        # The group of each item of each viewer, in the same order (D-202): Up and Down jump from
        # group to group. None, or one group only: they move through the items as Left and Right.
        self.dev_groups = dev_groups
