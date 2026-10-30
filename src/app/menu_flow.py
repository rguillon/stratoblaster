"""Screen state machine of the menus (P01-R01): Title → Ship
select → Level select → Game, with Back on each screen; Game ⇄ Pause, and Settings from the title
or the pause menu (P12-R02, P12-R04). Pure: no Babylon, no DOM, time comes from `update`.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from app.dev_groups import group_jump, group_starts
from app.menu_state import MenuFlowOptions, MenuState
from app.pause_menu import PauseMenu
from app.settings_menu import SettingsMenu, Volumes
from config.dev_viewer import DEV_VIEWERS
from core.content.level_catalog import first_unlocked_level
from core.menu.grid_cursor import GridShape, move_cursor
from core.menu.menu_screen import can_transition
from input.menu_action import MenuSelect, is_menu_direction

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from core.menu.menu_screen import MenuScreen  # noqa: E402
from core.systems.level_run_types import LevelCheckpoint, LevelResult  # noqa: E402
from input.menu_action import MenuCommand  # noqa: E402

__pragma__("noskip")

# The title screen's entries (P01-R04, P12-R04); `dev` after them with the dev menu (D-199).
TITLE_ENTRIES = ["start", "settings"]

# Volumes and slider size when the options give none.
DEFAULT_VOLUMES = Volumes(10, 10)
DEFAULT_VOLUME_STEPS = 10


def _index_of(values: list[str], value: str) -> int:
    """`Array.indexOf`: the index of `value`, or -1."""
    for i in range(len(values)):
        if values[i] == value:
            return i
    return -1


def _at(values: list[Any], index: int) -> Any:
    """`values[index]`, or None (JavaScript's `undefined`) when there is no such entry."""
    if index < 0 or index >= len(values):
        return None
    return values[index]


def _level_index(levels: list[Any], level_id: str | None) -> int:
    """`findIndex` on the level id, or -1."""
    for i in range(len(levels)):
        if levels[i].id == level_id:
            return i
    return -1


def _is_integer(value: float) -> bool:
    return value - math.floor(value) == 0


class MenuFlow:
    """Screen state machine of the menus (P01-R01). Pure: no Babylon, no DOM."""

    def __init__(self, options: MenuFlowOptions) -> None:
        if len(options.ship_ids) == 0:
            raise ValueError("The menu needs at least one ship")
        if len(options.levels.levels) == 0:
            raise ValueError("The menu needs at least one level")
        self._options = options
        self._screen: MenuScreen = "loading"
        self._title_index = 0
        initial = options.initial_ship_id if options.initial_ship_id is not None else ""
        self._ship_index = max(0, _index_of(options.ship_ids, initial))
        self._level_index = first_unlocked_level(options.levels)
        self._chosen_ship_id: str | None = None
        self._chosen_level_id: str | None = None
        self._transition_left = 0.0
        self._revision = 0
        self._result: LevelResult | None = None
        self._choice = 0
        self._attempt = 0
        self._resume: LevelCheckpoint | None = None
        self._pause = PauseMenu()
        self._settings = SettingsMenu(
            options.volumes if options.volumes is not None else DEFAULT_VOLUMES,
            options.volume_steps if options.volume_steps is not None else DEFAULT_VOLUME_STEPS,
        )
        # The screen the settings screen was opened from, which Back goes back to.
        self._settings_from: MenuScreen = "title"
        # The dev menu (D-199): the viewer picked, the item each viewer shows, and each viewer's
        # toggle (close-up for the models, play for the levels).
        counts = options.dev_counts
        self._title_entries = list(TITLE_ENTRIES)
        if counts is not None:
            self._title_entries.append("dev")
        self._dev_counts: list[int] = list(counts) if counts is not None else []
        groups = options.dev_groups
        self._dev_groups: list[list[str]] = list(groups) if groups is not None else []
        self._dev_index = 0
        self._dev_items = [0 for _ in DEV_VIEWERS]
        self._dev_toggles = [viewer != "levels" for viewer in DEV_VIEWERS]

    @property
    def revision(self) -> int:
        """Increases on every state change, so views know when to refresh."""
        return self._revision

    @property
    def state(self) -> MenuState:
        selection = self._selection()
        return MenuState(
            self._screen,
            selection,
            self._selected_id(selection),
            self._ship_id(self._ship_index),
            self._chosen_ship_id,
            self._chosen_level_id,
            self._transition_left > 0,
            self._result,
            self._pause.choice if self._screen == "pause" else self._choice,
            self._attempt,
            self._resume,
            self.paused,
            self._screen == "pause" and self._pause.leaving,
            self._settings.volumes,
            self._dev_viewer(),
            self._screen == "dev-viewer" and self._dev_toggles[self._dev_index],
        )

    def _dev_viewer(self) -> str | None:
        """The dev viewer shown, on the `dev-viewer` screen (D-199)."""
        if self._screen != "dev-viewer":
            return None
        viewer: str = DEV_VIEWERS[self._dev_index]
        return viewer

    @property
    def paused(self) -> bool:
        """Whether the level being played is paused (P12-R01)."""
        return self._screen == "pause" or (
            self._screen == "settings" and self._settings_from == "pause"
        )

    def go_to(self, screen: MenuScreen) -> bool:
        """Goes to `screen` if the flow allows it (P01-R01). Returns False and changes nothing
        otherwise.
        """
        if not can_transition(self._screen, screen):
            return False
        if screen == "level-select":
            self._level_index = first_unlocked_level(self._options.levels)
        if screen == "game":
            self._start_level(None)
        if screen == "settings":
            self._open_settings()
        if screen == "pause" and self._screen == "game":
            self._pause.open()
        if screen == "title" and self._screen not in ["settings", "dev"]:
            self._title_index = 0
        self._result = None
        self._screen = screen
        self._transition_left = self._options.transition_seconds
        self._changed()
        return True

    def pause(self) -> bool:
        """Pauses the level being played (P12-R01, P12-R03): the pause menu shows. Ignored on
        other screens, and on the "Level complete" or "Game over" panel.
        """
        if self._screen != "game" or self._result is not None:
            return False
        return self.go_to("pause")

    def finish_loading(self) -> None:
        """Called when loading completes: shows the title screen."""
        self.go_to("title")

    def complete_level(self, result: LevelResult) -> None:
        """Shows the "Level complete" (or "Game over") overlay on the game screen (P06-R03); Confirm
        then goes to the level select screen. Ignored on other screens.
        """
        if self._screen != "game" or self._result is not None:
            return
        self._result = result
        self._choice = 0
        delay = self._options.result_delay_seconds
        self._transition_left = delay if delay is not None else self._options.transition_seconds
        self._changed()

    def play_direct(self, ship_id: str, level_id: str) -> bool:
        """Starts a level straight away with the given ship, skipping the menus (P06-R09 debug
        options). Returns False, and changes nothing, if the ship or the level is unknown or the
        level is locked.
        """
        ship_index = _index_of(self._options.ship_ids, ship_id)
        level_index = _level_index(self._options.levels.levels, level_id)
        level = _at(self._options.levels.levels, level_index)
        if ship_index < 0 or level is None or not level.unlocked:
            return False
        self._ship_index = ship_index
        self._level_index = level_index
        self._chosen_ship_id = ship_id
        self._chosen_level_id = level_id
        self._result = None
        self._start_level(None)
        self._screen = "game"
        self._transition_left = 0.0
        self._changed()
        return True

    def update(self, dt_seconds: float) -> None:
        """Advances the transition timer."""
        if self._transition_left <= 0:
            return
        self._transition_left = max(0, self._transition_left - dt_seconds)
        if self._transition_left == 0:
            self._changed()

    def dispatch(self, command: MenuCommand) -> str:
        """Applies a menu command to the current screen. Ignored while loading or in a
        transition.
        """
        if self._screen == "loading" or self._transition_left > 0:
            return "none"
        if isinstance(command, str):
            on_viewer = self._screen == "dev-viewer"
            return self._on_dev_viewer(command) if on_viewer else self._action(command)
        if isinstance(command, MenuSelect):
            return self._select(command.select)
        return self._adjusted(self._settings.set(command.set, command.value))

    def _action(self, command: str) -> str:
        if self._screen == "pause":
            return self._on_pause(command)
        if self._screen == "settings":
            return self._on_settings(command)
        if self._screen == "game" and self._result is None:
            return self._in_level(command)
        if is_menu_direction(command):
            return self._move(command)
        if command in ["back", "cancel"]:
            return self._back()
        return self._confirm() if command == "confirm" else "none"

    def _in_level(self, command: str) -> str:
        """In a level (P12-R01): Escape, P, Start and Select pause it; Back and the other actions do
        nothing.
        """
        if command not in ["pause", "cancel"]:
            return "none"
        return "paused" if self.pause() else "none"

    def _on_pause(self, command: str) -> str:
        """The pause menu (P12-R02): Back, Escape, P and Start resume the level."""
        if is_menu_direction(command):
            return self._pause_outcome(self._pause.move(command))
        if command == "confirm":
            return self._pause_outcome(self._pause.confirm())
        return self._pause_outcome(self._pause.back())

    def _pause_outcome(self, outcome: str) -> str:
        if outcome == "resume":
            return self._resume_level()
        if outcome in ["settings", "leave"]:
            target: MenuScreen = "title" if outcome == "leave" else "settings"
            return "screen" if self.go_to(target) else "none"
        if outcome != "none":
            self._changed()
        return "screen" if outcome == "ask" else outcome

    def _resume_level(self) -> str:
        """Back to the level, as it was: not a new attempt (P12-R01)."""
        self._screen = "game"
        self._transition_left = self._options.transition_seconds
        self._changed()
        return "resumed"

    def _on_settings(self, command: str) -> str:
        """The settings screen (P12-R04): Back returns to where it was opened from."""
        if is_menu_direction(command):
            return self._adjusted(self._settings.move(command))
        if command not in ["back", "cancel"]:
            return "none"
        return "screen" if self.go_to(self._settings_from) else "none"

    def _on_dev_viewer(self, command: str) -> str:
        """A dev viewer (D-199): the four directions show the item before or after (round the
        list), Up and Down the first item of the group before or after when the viewer's items are
        in groups (D-202), Confirm flips the viewer's toggle, Back and Escape return to the dev
        menu.
        """
        if is_menu_direction(command):
            counts = self._dev_counts
            count = counts[self._dev_index] if self._dev_index < len(counts) else 0
            if count <= 1:
                return "none"
            step = -1 if command in ["left", "up"] else 1
            index = self._dev_items[self._dev_index]
            starts = group_starts(_at(self._dev_groups, self._dev_index) or [])
            if command in ["up", "down"] and len(starts) > 1:
                self._dev_items[self._dev_index] = group_jump(starts, index, step)
            else:
                self._dev_items[self._dev_index] = (index + step + count) % count
            self._changed()
            return "moved"
        if command == "confirm":
            self._dev_toggles[self._dev_index] = not self._dev_toggles[self._dev_index]
            self._changed()
            return "adjusted"
        if command in ["back", "cancel"]:
            return "screen" if self.go_to("dev") else "none"
        return "none"

    def _select_dev_item(self, index: int) -> str:
        """A dev viewer's button was tapped (D-204): it shows item `index`."""
        counts = self._dev_counts
        count = counts[self._dev_index] if self._dev_index < len(counts) else 0
        if not _is_integer(index) or index < 0 or index >= count:
            return "none"
        if index == self._dev_items[self._dev_index]:
            return "none"
        self._dev_items[self._dev_index] = index
        self._changed()
        return "moved"

    def _adjusted(self, feedback: str) -> str:
        if feedback != "none":
            self._changed()
        return feedback

    def _open_settings(self) -> None:
        self._settings_from = self._screen
        self._settings.open()

    def _changed(self) -> None:
        self._revision += 1

    def _start_level(self, checkpoint: LevelCheckpoint | None) -> None:
        """A new attempt at the chosen level, from its start or from `checkpoint`."""
        self._attempt += 1
        self._resume = checkpoint

    def _choosing(self) -> bool:
        """The "Game over" panel offers Continue or level select (P07-R08)."""
        return (
            self._screen == "game"
            and self._result is not None
            and self._result.checkpoint is not None
        )

    def _ship_id(self, index: int) -> str:
        ship = _at(self._options.ship_ids, index)
        return ship if ship is not None else ""

    def _selection(self) -> int:
        if self._screen == "pause":
            return self._pause.selection
        if self._screen == "settings":
            return self._settings.selection
        indices = {
            "title": self._title_index,
            "ship-select": self._ship_index,
            "level-select": self._level_index,
            "dev": self._dev_index,
            "dev-viewer": self._dev_items[self._dev_index],
        }
        index: int = indices.get(self._screen, 0)
        return index

    def _selected_id(self, selection: int) -> str | None:
        screen = self._screen
        if screen in ["title", "dev"]:
            entries = self._title_entries if screen == "title" else DEV_VIEWERS
            entry: str | None = _at(entries, selection)
            return entry
        if screen == "pause":
            return self._pause.selected_id
        if screen == "settings":
            return self._settings.selected_id
        if screen == "ship-select":
            return self._ship_id(selection)
        if screen == "level-select":
            level = _at(self._options.levels.levels, selection)
            return level.id if level is not None else None
        return None

    def _grid(self) -> GridShape | None:
        if self._screen == "title":
            return GridShape(len(self._title_entries), 1, False)
        if self._screen == "dev":
            return GridShape(len(DEV_VIEWERS), 1, False)
        if self._screen == "ship-select":
            count = len(self._options.ship_ids)
            return GridShape(count, count, True)
        if self._screen == "level-select":
            levels = self._options.levels
            return GridShape(len(levels.levels), levels.columns, False)
        return None

    def _set_selection(self, index: int) -> str:
        if index == self._selection():
            return "none"
        if self._screen == "title":
            self._title_index = index
        elif self._screen == "ship-select":
            self._ship_index = index
        elif self._screen == "dev":
            self._dev_index = index
        else:
            self._level_index = index
        self._changed()
        return "moved"

    def _move(self, direction: str) -> str:
        if self._choosing():
            return self._choose(0 if direction in ["left", "up"] else 1)
        grid = self._grid()
        if grid is None:
            return "none"
        # The direction is one of the four names `move_cursor` takes (see `is_menu_direction`).
        cursor_direction: Any = direction
        return self._set_selection(move_cursor(self._selection(), cursor_direction, grid))

    def _select(self, index: int) -> str:
        if self._screen == "dev-viewer":
            return self._select_dev_item(index)
        if self._screen == "pause":
            return self._pause_outcome(self._pause.select(index))
        if self._screen == "settings":
            return self._adjusted(self._settings.select(index))
        if self._choosing():
            return self._choose(index) if index in [0, 1] else "none"
        grid = self._grid()
        if grid is None or not _is_integer(index) or index < 0 or index >= grid.count:
            return "none"
        return self._set_selection(index)

    def _back(self) -> str:
        previous: dict[str, MenuScreen] = {
            "ship-select": "title",
            "level-select": "ship-select",
            "dev": "title",
        }
        if self._screen not in previous:
            return "none"
        return "screen" if self.go_to(previous[self._screen]) else "none"

    def _confirm(self) -> str:
        screen = self._screen
        if screen == "title":
            targets: list[MenuScreen] = ["ship-select", "settings", "dev"]
            target: MenuScreen = targets[self._title_index]
            return "screen" if self.go_to(target) else "none"
        if screen == "dev":
            return "screen" if self.go_to("dev-viewer") else "none"
        if screen == "ship-select":
            self._chosen_ship_id = self._ship_id(self._ship_index)
            return "screen" if self.go_to("level-select") else "none"
        if screen == "level-select":
            return self._confirm_level()
        if screen == "game":
            return self._leave_completed_level()
        return "none"

    def _leave_completed_level(self) -> str:
        """From the "Level complete" overlay to the level select screen, on the next level; from
        the "Game over" overlay, on the level played (GD-20).
        """
        result = self._result
        if result is None:
            return "none"
        checkpoint = result.checkpoint
        if checkpoint is not None and self._choice == 0:
            return self._continue(checkpoint)
        levels = self._options.levels.levels
        played = _level_index(levels, self._chosen_level_id)
        after = _at(levels, played + 1)
        won = result.outcome == "complete"
        nxt = played + 1 if won and after is not None and after.unlocked else played
        if not self.go_to("level-select"):
            return "none"
        self._level_index = max(0, nxt)
        return "screen"

    def _choose(self, choice: int) -> str:
        if choice == self._choice:
            return "none"
        self._choice = choice
        self._changed()
        return "moved"

    def _continue(self, checkpoint: LevelCheckpoint) -> str:
        """The level starts again from its checkpoint, on the game screen (P07-R08)."""
        self._result = None
        self._start_level(checkpoint)
        self._transition_left = self._options.transition_seconds
        self._changed()
        return "screen"

    def _confirm_level(self) -> str:
        level = _at(self._options.levels.levels, self._level_index)
        if level is None or not level.unlocked:
            return "locked"
        self._chosen_level_id = level.id
        return "screen" if self.go_to("game") else "none"
