"""Builds what the menu overlay shows for the current state, ported from `app/menu-view-builder.ts`
(P01-R04, R06, R07, P06-R02, R03, P12-R02, P12-R04).
"""

from org.transcrypt.stubs.browser import __pragma__

from app.settings_menu import SETTINGS_SLIDERS
from ui.menu_view import (
    GameScreenView,
    LevelChoices,
    LevelCompleteView,
    LevelOption,
    LevelSelectView,
    LoadingView,
    PauseQuestion,
    PauseView,
    SettingsView,
    ShipSelectView,
    SliderView,
    TitleView,
)
from ui.ship_caption import ship_caption

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from app.menu_state import MenuState  # noqa: E402
from core.content.game_definition import GameDefinition  # noqa: E402
from core.systems.level_run_types import LevelResult  # noqa: E402

__pragma__("noskip")


class MenuViewContext:
    """What a menu view needs besides the flow state."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        game: GameDefinition,
        high_score: int,
        version: str,
        commit: str,
        cards_width_percent: float,
        progress: float,
        volume_steps: int,
    ) -> None:
        self.game = game
        # The best score so far.
        self.high_score = high_score
        # Version and short commit hash (ENG-83).
        self.version = version
        self.commit = commit
        # Width of the row of ship cards, in % of the screen.
        self.cards_width_percent = cards_width_percent
        # Loading progress, 0..1.
        self.progress = progress
        # The volume sliders' highest step (P12-R04).
        self.volume_steps = volume_steps


def _pause_view(state: MenuState, ctx: MenuViewContext) -> PauseView:
    """The pause menu (P12-R02), and its `Leave the level?` question when it shows."""
    texts = ctx.game.texts
    question = None
    if state.leaving:
        question = PauseQuestion(texts.leave_level, [texts.no, texts.yes], state.choice)
    return PauseView(
        texts.paused,
        [texts.resume, texts.settings, texts.main_menu],
        texts.pause_hint,
        question,
    )


def _settings_view(state: MenuState, ctx: MenuViewContext) -> SettingsView:
    """The settings screen (P12-R04): one slider per volume."""
    texts = ctx.game.texts
    labels = {"music": texts.music_volume, "sfx": texts.sfx_volume}
    sliders: list[SliderView] = []
    for slider in SETTINGS_SLIDERS:
        value = state.volumes.music if slider == "music" else state.volumes.sfx
        sliders.append(SliderView(labels[slider], value, ctx.volume_steps))
    return SettingsView(
        texts.settings,
        texts.settings_hint,
        texts.back,
        state.selection,
        sliders,
        state.paused,
    )


def _complete_view(
    result: LevelResult,
    state: MenuState,
    ctx: MenuViewContext,
    label: Any,
) -> LevelCompleteView:
    """The "Level complete" (or "Game over") panel (P06-R03), with its choices (P07-R08)."""
    texts = ctx.game.texts
    choices = None
    if result.checkpoint is not None:
        choices = LevelChoices(
            [texts.continue_from_checkpoint, texts.to_level_select],
            state.choice,
        )
    over = result.outcome == "over"
    return LevelCompleteView(
        texts.game_over if over else texts.level_complete,
        over,
        label(result.level_id),
        texts.enemies_destroyed(result.destroyed, result.spawned),
        texts.final_score(int(result.score)),
        texts.continue_hint,
        texts.new_high_score if result.new_high_score else None,
        choices,
    )


def _selected_on_game(state: MenuState, paused: PauseView | None) -> int:
    """The entry taps select on the game screen: the pause menu's, or the panel's choice."""
    if paused is not None:
        return state.choice if paused.question is not None else state.selection
    result = state.level_result
    return state.choice if result is not None and result.checkpoint is not None else 0


def _game_view(state: MenuState, ctx: MenuViewContext) -> GameScreenView:
    texts = ctx.game.texts
    levels = ctx.game.levels.levels

    def label(level_id: str | None) -> str:
        for level in levels:
            if level.id == level_id:
                return level.label
        return "?"

    result = state.level_result
    paused = _pause_view(state, ctx) if state.screen == "pause" else None
    complete = None if result is None else _complete_view(result, state, ctx, label)
    return GameScreenView(
        texts.game_level(label(state.chosen_level_id)),
        texts.fire,
        texts.pause_button,
        complete,
        paused,
        _selected_on_game(state, paused),
    )


def build_menu_view(state: MenuState, ctx: MenuViewContext) -> Any:
    """The view of the current screen: one of the classes of `ui/menu_view`."""
    game = ctx.game
    texts = game.texts
    screen = state.screen
    if screen == "loading":
        return LoadingView(texts.loading, ctx.progress)
    if screen == "title":
        return TitleView(
            game.title,
            texts.high_score,
            ctx.high_score,
            texts.start,
            texts.settings,
            state.selection,
            texts.start_hint,
            ctx.version,
            ctx.commit,
        )
    if screen == "ship-select":
        ships = [ship_caption(game.player_ships, ship.id) for ship in game.player_ships.ships]
        return ShipSelectView(
            texts.choose_ship,
            texts.choose_ship_hint,
            texts.back,
            state.selection,
            ships,
            ctx.cards_width_percent,
        )
    if screen == "level-select":
        options = [LevelOption(entry.label, not entry.unlocked) for entry in game.levels.levels]
        return LevelSelectView(
            texts.choose_level,
            texts.choose_level_hint,
            texts.back,
            state.selection,
            game.levels.columns,
            options,
            texts.locked,
        )
    if screen in ["game", "pause"]:
        return _game_view(state, ctx)
    return _settings_view(state, ctx)
