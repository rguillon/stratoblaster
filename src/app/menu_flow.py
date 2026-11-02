# Copyright (c) 2026 Renaud Guillon
"""Screen state machine of the menus (UI-FLOW-02): Title → Ship select → Level select → Game.

With Back on each screen (UI-FLOW-05); Game ⇄ Pause, and Settings from the title or the pause menu
(UI-SET-01, UI-PAUSE-09). Pure: no Babylon, no DOM, time comes from `update`.
"""

import math

from app.dev_groups import group_jump, group_starts
from app.menu_state import MenuFlowOptions, MenuState
from app.pause_menu import PauseMenu
from app.settings_menu import SettingsMenu, Volumes
from config.dev_viewer import DEV_AUDIO_VIEWERS, DEV_VIEWERS
from core.content.level_catalog import first_unlocked_level
from core.menu.grid_cursor import GridShape, move_cursor
from core.menu.menu_screen import can_transition
from input.menu_action import MenuSelect, is_menu_direction

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from core.menu.menu_screen import MenuScreen
from core.systems.level_run_types import LevelCheckpoint, LevelResult
from input.menu_action import MenuCommand

# __pragma__ ("noskip")


# The title screen's entries (UI-TITLE-01, UI-TITLE-06); `dev` after them with the dev menu
# (DEV-MENU-01, D-199).
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
    """Screen state machine of the menus (UI-FLOW-01). Pure (UI-FLOW-04): no Babylon, no DOM."""

    def __init__(self, options: MenuFlowOptions) -> None:
        if len(options.ship_ids) == 0:
            msg = "The menu needs at least one ship"
            raise ValueError(msg)
        if len(options.levels.levels) == 0:
            msg = "The menu needs at least one level"
            raise ValueError(msg)
        self._options = options
        self._screen: MenuScreen = "loading"
        self._title_index = 0
        # The saved ship is highlighted first, else the first one (UI-SHIP-05).
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
        # The dev menu (DEV-MENU-03, D-199): the viewer picked, the item each viewer shows, and
        # each viewer's toggle (close-up for the models, play for the levels).
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
        """The menu state the view draws now."""
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
        """Return the dev viewer shown, on the `dev-viewer` screen (D-199)."""
        if self._screen != "dev-viewer":
            return None
        viewer: str = DEV_VIEWERS[self._dev_index]
        return viewer

    @property
    def paused(self) -> bool:
        """Whether the level being played is paused (UI-PAUSE-03).

        It is on the pause menu, or on the settings screen opened from it, over the paused level
        (UI-SET-07).
        """
        return self._screen == "pause" or (
            self._screen == "settings" and self._settings_from == "pause"
        )

    def go_to(self, screen: MenuScreen) -> bool:
        """Goes to `screen` if the flow allows it (UI-FLOW-02).

        Returns False and changes nothing otherwise (UI-FLOW-03).
        """
        if not can_transition(self._screen, screen):
            return False
        if screen == "level-select":  # The first level highlighted on arrival (UI-LEVEL-06).
            self._level_index = first_unlocked_level(self._options.levels)
        if screen == "game":
            self._start_level(None)
        if screen == "settings":
            self._open_settings()
        if screen == "pause" and self._screen == "game":
            self._pause.open()
        if screen == "title" and self._screen not in ["settings", "dev"]:
            self._title_index = 0  # Start selected (UI-TITLE-06).
        self._result = None
        self._screen = screen
        self._transition_left = self._options.transition_seconds
        self._changed()
        return True

    def pause(self) -> bool:
        """Pauses the level being played (UI-PAUSE-01, UI-PAUSE-11): the pause menu shows.

        Ignored on other screens, and on the "Level complete" or "Game over" panel (UI-PAUSE-06).
        """
        if self._screen != "game" or self._result is not None:
            return False
        return self.go_to("pause")

    def finish_loading(self) -> None:
        """Show the title screen, now that loading is complete (UI-LOAD-04)."""
        self.go_to("title")

    def complete_level(self, result: LevelResult) -> None:
        """Show the "Level complete" (or "Game over") overlay on the game screen (UI-OVER-01).

        Confirm then goes to the level select screen. Ignored on other screens. Input waits
        `result_delay_seconds` first (UI-OVER-04).
        """
        if self._screen != "game" or self._result is not None:
            return
        self._result = result
        self._choice = 0
        delay = self._options.result_delay_seconds
        self._transition_left = delay if delay is not None else self._options.transition_seconds
        self._changed()

    def play_direct(self, ship_id: str, level_id: str) -> bool:
        """Start a level straight away with the given ship, skipping the menus.

        For the DEV-OPT-01 debug options. Returns False, and changes nothing, if the ship or the
        level is unknown or the level is locked.
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
        """Advances the transition timer (UI-FLOW-08)."""
        if self._transition_left <= 0:
            return
        self._transition_left = max(0, self._transition_left - dt_seconds)
        if self._transition_left == 0:
            self._changed()

    def dispatch(self, command: MenuCommand) -> str:
        """Apply a menu command, from any device (UI-INPUT-01), to the current screen.

        Ignored while loading or in a transition (UI-FLOW-08).
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
        """Return what `command` means on the current screen (UI-INPUT-02)."""
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
        """Pause the level being played on Escape, P, Start or Select (UI-PAUSE-01).

        Back and the other actions do nothing (UI-PAUSE-05, UI-FLOW-06).
        """
        if command not in ["pause", "cancel"]:
            return "none"
        return "paused" if self.pause() else "none"

    def _on_pause(self, command: str) -> str:
        """Apply `command` on the pause menu and return its feedback.

        Back, Escape, P and Start resume the level (UI-PAUSE-08).
        """
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
        """Back to the level, as it was: not a new attempt (UI-PAUSE-08)."""
        self._screen = "game"
        self._transition_left = self._options.transition_seconds
        self._changed()
        return "resumed"

    def _on_settings(self, command: str) -> str:
        """Apply `command` on the settings screen and return its feedback.

        Back returns to where it was opened from (UI-SET-01, UI-FLOW-05).
        """
        if is_menu_direction(command):
            return self._adjusted(self._settings.move(command))
        if command not in ["back", "cancel"]:
            return "none"
        return "screen" if self.go_to(self._settings_from) else "none"

    def _on_dev_viewer(self, command: str) -> str:
        """Apply `command` on a dev viewer and return its feedback (DEV-MENU-06, D-199).

        The four directions show the item before or after (round the list), Up and Down the first
        item of the group before or after when the viewer's items are in groups (D-202), Confirm
        flips the viewer's toggle, Back and Escape return to the dev menu. On an audio viewer the
        item picked plays (DEV-MENU-19): the feedback is `played`, so no menu sound covers it.
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
            return self._dev_feedback("moved")
        if command == "confirm":
            self._dev_toggles[self._dev_index] = not self._dev_toggles[self._dev_index]
            self._changed()
            return self._dev_feedback("adjusted")
        if command in ["back", "cancel"]:
            return "screen" if self.go_to("dev") else "none"
        return "none"

    def _select_dev_item(self, index: int) -> str:
        """Show item `index`: the dev viewer's menu item was tapped (DEV-MENU-07, D-204)."""
        counts = self._dev_counts
        count = counts[self._dev_index] if self._dev_index < len(counts) else 0
        if not _is_integer(index) or index < 0 or index >= count:
            return "none"
        if index == self._dev_items[self._dev_index]:
            return "none"
        self._dev_items[self._dev_index] = index
        self._changed()
        return self._dev_feedback("moved")

    def _dev_feedback(self, feedback: str) -> str:
        """Return `feedback`, or `played` on an audio viewer, whose item picked plays."""
        return "played" if DEV_VIEWERS[self._dev_index] in DEV_AUDIO_VIEWERS else feedback

    def _adjusted(self, feedback: str) -> str:
        if feedback != "none":
            self._changed()
        return feedback

    def _open_settings(self) -> None:
        """Open the settings screen.

        Back returns to the screen it was opened from: the title or the pause menu (UI-PAUSE-09).
        """
        self._settings_from = self._screen
        self._settings.open()

    def _changed(self) -> None:
        self._revision += 1

    def _start_level(self, checkpoint: LevelCheckpoint | None) -> None:
        """Start a new attempt at the chosen level, from its start or from `checkpoint`."""
        self._attempt += 1
        self._resume = checkpoint

    def _choosing(self) -> bool:
        """Return whether the "Game over" panel offers Continue or level select (UI-OVER-06).

        It does only with a checkpoint (UI-OVER-08).
        """
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
        """Return the grid the arrows move in.

        The title's entries (UI-TITLE-06), the ships, round (UI-SHIP-04), the levels (UI-LEVEL-05).
        """
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
        """Back on the menu screens (UI-FLOW-05, UI-SHIP-06)."""
        previous: dict[str, MenuScreen] = {
            "ship-select": "title",
            "level-select": "ship-select",
            "dev": "title",
        }
        if self._screen not in previous:
            return "none"
        return "screen" if self.go_to(previous[self._screen]) else "none"

    def _confirm(self) -> str:
        """Confirm the choice on the current screen.

        The title's entry (UI-TITLE-06), the ship (UI-SHIP-06), the level, or the end panel's
        choice.
        """
        screen = self._screen
        result = self._result
        if screen == "dev":
            return "screen" if self.go_to("dev-viewer") else "none"
        if screen == "ship-select":
            self._chosen_ship_id = self._ship_id(self._ship_index)
            return "screen" if self.go_to("level-select") else "none"
        if screen == "level-select":
            return self._confirm_level()
        if screen == "game" and result is not None:
            return self._leave_completed_level(result)
        # The title screen: `_action` sends the other screens' commands elsewhere.
        targets: list[MenuScreen] = ["ship-select", "settings", "dev"]
        target: MenuScreen = targets[self._title_index]
        return "screen" if self.go_to(target) else "none"

    def _leave_completed_level(self, result: LevelResult) -> str:
        """Leave the "Level complete" or "Game over" overlay (`result`) for the level select screen.

        From "Level complete", on the next level (UI-OVER-03, UI-LEVEL-07; after a world's last
        level the next world's first: WLD-1-02, WLD-2-02); from "Game over", on the level played
        (UI-FLOW-07), unless Continue is chosen (UI-OVER-07).
        """
        checkpoint = result.checkpoint
        if checkpoint is not None and self._choice == 0:
            return self._continue(checkpoint)
        levels = self._options.levels.levels
        played = _level_index(levels, self._chosen_level_id)
        after = _at(levels, played + 1)
        won = result.outcome == "complete"
        nxt = played + 1 if won and after is not None and after.unlocked else played
        # The game screen may always go back to the level select screen (UI-FLOW-07).
        self.go_to("level-select")
        self._level_index = max(0, nxt)
        return "screen"

    def _choose(self, choice: int) -> str:
        if choice == self._choice:
            return "none"
        self._choice = choice
        self._changed()
        return "moved"

    def _continue(self, checkpoint: LevelCheckpoint) -> str:
        """Restart the level from its checkpoint, on the game screen (UI-OVER-07, GAME-LIFE-11)."""
        self._result = None
        self._start_level(checkpoint)
        self._transition_left = self._options.transition_seconds
        self._changed()
        return "screen"

    def _confirm_level(self) -> str:
        """Start the chosen level if it is open (UI-LEVEL-08).

        A locked one gives the locked feedback (UI-LEVEL-04).
        """
        level = _at(self._options.levels.levels, self._level_index)
        if level is None or not level.unlocked:
            return "locked"
        self._chosen_level_id = level.id
        return "screen" if self.go_to("game") else "none"
