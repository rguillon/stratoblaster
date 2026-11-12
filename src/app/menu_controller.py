# Copyright (c) 2026 Renaud Guillon
"""Runs the menus: feeds input to the `MenuFlow`, shows the matching view.

Gives the "locked" feedback. Free of Babylon.
"""

from app.menu_flow import MenuFlow
from app.menu_state import MenuFlowOptions, MenuState
from app.menu_view_builder import MenuViewContext, build_menu_view
from app.saved_choices import load_saved_choices, save_high_score
from app.saved_settings import load_volumes, save_volumes
from app.settings_menu import Volumes
from config.audio import AUDIO_CONFIG
from config.dev_viewer import DEV_VIEWERS
from core.systems.level_run_types import LevelResult

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from core.content.game_definition import GameDefinition

# __pragma__ ("noskip")


class MenuControllerDeps:
    """Collaborators of a `MenuController`.

    `display` has `show(view)` and `shake_selected(text)`. `input` has `update(dt_seconds)`,
    returning the actions of the frame; `on_change(state)` and `on_feedback(command, feedback)` are
    optional (None).
    """

    def __init__(
        self,
        display: Any,
        input_source: Any,
        storage: Any,
        transition_seconds: float,
        result_delay_seconds: float | None,
        version: str,
        commit: str,
        on_change: Any,
        on_feedback: Any,
        dev_labels: dict[str, list[str]] | None = None,
        dev_groups: dict[str, list[str]] | None = None,
        fullscreen: Any | None = None,
    ) -> None:
        self.display = display
        self.input = input_source
        self.storage = storage
        self.transition_seconds = transition_seconds
        # Input is ignored this long after the "Level complete" overlay shows (UI-OVER-04).
        self.result_delay_seconds = result_delay_seconds
        self.version = version
        self.commit = commit
        # Called after every state change, e.g. to update the 3D scenes.
        self.on_change = on_change
        # Called after each command with what it did, e.g. for the menu sounds (AUD-ENGINE-09).
        self.on_feedback = on_feedback
        # The labels of each dev viewer's items (D-199); None: no dev menu.
        self.dev_labels = dev_labels
        # The group of each dev viewer's items (D-202); None: not in groups.
        self.dev_groups = dev_groups
        # The page's full screen (UI-TITLE-11, `app/page_fullscreen.py`: `supported()`,
        # `active()`, `toggle()`, `listen(on_change)`); None: no Full screen entry.
        self.fullscreen = fullscreen


def _with_new_high_score(result: LevelResult) -> LevelResult:
    """Return a copy of `result` that says it beat the high score (UI-OVER-02)."""
    return LevelResult(
        result.level_id,
        result.destroyed,
        result.spawned,
        result.outcome,
        result.score,
        True,
        result.checkpoint,
    )


def _dev_counts(labels: dict[str, list[str]] | None) -> list[int] | None:
    """How many items each dev viewer shows (D-199), in the order of `DEV_VIEWERS`."""
    if labels is None:
        return None
    return [len(labels[viewer]) for viewer in DEV_VIEWERS]


def _dev_groups(groups: dict[str, list[str]] | None) -> list[list[str]] | None:
    """Return the group of each dev viewer's items (D-202), in the order of `DEV_VIEWERS`."""
    if groups is None:
        return None
    return [groups.get(viewer, []) for viewer in DEV_VIEWERS]


class MenuController:
    """Runs the menus: see the module doc."""

    def __init__(self, game: GameDefinition, deps: MenuControllerDeps) -> None:
        self.game = game
        self.deps = deps
        saved = load_saved_choices(deps.storage, game.id)
        self._high_score = saved.high_score
        volume_steps = int(AUDIO_CONFIG.volume_steps)
        # The default volumes, where none is saved (UI-SET-05).
        defaults = AUDIO_CONFIG.default_volumes
        self._saved_volumes: Volumes = load_volumes(
            deps.storage, game.id, volume_steps, Volumes(int(defaults.music), int(defaults.sfx))
        )
        self._progress = 0.0
        self._shown_revision = -1
        self._shown_progress = -1.0
        self._shown_fullscreen: bool | None = None
        self.flow = MenuFlow(
            MenuFlowOptions(
                # The game's one ship (D-326): the first of its roster.
                game.player_ships.ships[0].id,
                game.levels,
                deps.transition_seconds,
                deps.result_delay_seconds,
                self._saved_volumes,
                volume_steps,
                _dev_counts(deps.dev_labels),
                _dev_groups(deps.dev_groups),
                self._fullscreen() is not None,
            )
        )
        # The title's Full screen entry follows the page (UI-TITLE-11): Escape leaves full
        # screen without the menu.
        if deps.fullscreen is not None:
            deps.fullscreen.listen(self.refresh)
        self.refresh()

    def set_progress(self, progress: float) -> None:
        """Set the loading progress shown on the loading screen, 0..1 (UI-LOAD-03)."""
        self._progress = progress
        self.refresh()

    def finish_loading(self) -> None:
        """Tells the flow that loading finished, and refreshes the view."""
        self.flow.finish_loading()
        self.refresh()

    @property
    def high_score(self) -> float:
        """The best score saved so far (UI-TITLE-03)."""
        return self._high_score

    def record_score(self, score: float) -> bool:
        """Return a level attempt ended with `score` (GAME-SCORE-05): above the high score.

        It is saved as the new one, and the title screen shows it (UI-TITLE-03). Returns whether it
        beat the high score.
        """
        if not score > self._high_score:
            return False
        self._high_score = score
        save_high_score(self.deps.storage, self.game.id, score)
        return True

    def complete_level(self, result: LevelResult) -> None:
        """Show the "Level complete" (or "Game over") overlay (UI-OVER-01).

        After saving its score if it beat the high score: the overlay then says so (UI-OVER-02).
        """
        beaten = self.record_score(result.score)
        self.flow.complete_level(_with_new_high_score(result) if beaten else result)
        self.refresh()

    def play_direct(self, level_id: str) -> bool:
        """Start a level straight away (DEV-OPT-01 debug options); see `MenuFlow.play_direct`."""
        started = self.flow.play_direct(level_id)
        self.refresh()
        return started

    def command(self, command: Any) -> None:
        """Apply one command and show its result at once (PERF-04).

        The command comes from any device, or the test API.
        """
        feedback = self.flow.dispatch(command)
        if feedback == "locked":  # The locked level's shake (UI-LEVEL-04).
            self.deps.display.shake_selected(self.game.texts.locked)
        if feedback == "fullscreen" and self.deps.fullscreen is not None:  # UI-TITLE-11.
            self.deps.fullscreen.toggle()
        if self.deps.on_feedback is not None:
            self.deps.on_feedback(command, feedback)
        self.refresh()

    def pause(self) -> bool:
        """Pauses the level being played (UI-PAUSE-11).

        The page is hidden, and the gamepad in use is disconnected. Returns whether it paused.
        """
        paused = self.flow.pause()
        if paused and self.deps.on_feedback is not None:
            self.deps.on_feedback("pause", "paused")
        self.refresh()
        return paused

    def tick(self, dt_seconds: float) -> None:
        """Advances time by one frame: transition timer, then the input of the frame."""
        self.flow.update(dt_seconds)
        for action in self.deps.input.update(dt_seconds):
            self.command(action)
        self.refresh()

    def refresh(self) -> None:
        """Show the current view if anything changed since the last call."""
        revision = self.flow.revision
        fullscreen = self._fullscreen()
        if (
            revision == self._shown_revision
            and self._progress == self._shown_progress
            and fullscreen == self._shown_fullscreen
        ):
            return
        self._shown_revision = revision
        self._shown_progress = self._progress
        self._shown_fullscreen = fullscreen
        state: MenuState = self.flow.state
        self._remember_volumes(state.volumes)
        self.deps.display.show(
            build_menu_view(
                state,
                MenuViewContext(
                    self.game,
                    int(self._high_score),
                    self.deps.version,
                    self.deps.commit,
                    self._progress,
                    int(AUDIO_CONFIG.volume_steps),
                    self.deps.dev_labels,
                    self.deps.dev_groups,
                    fullscreen,
                ),
            )
        )
        if self.deps.on_change is not None:
            self.deps.on_change(state)

    def _fullscreen(self) -> bool | None:
        """Whether the page is full screen (UI-TITLE-11); None where the browser allows none."""
        fullscreen = self.deps.fullscreen
        if fullscreen is None or not fullscreen.supported():
            return None
        active: bool = fullscreen.active()
        return active

    def _remember_volumes(self, volumes: Volumes) -> None:
        """Save the volumes on every change (UI-SET-06)."""
        saved = self._saved_volumes
        if volumes.music == saved.music and volumes.sfx == saved.sfx:
            return
        save_volumes(self.deps.storage, self.game.id, volumes)
        self._saved_volumes = volumes
