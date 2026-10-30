"""Builds what the menu overlay shows for the current state
(P01-R04, R06, R07, P06-R02, R03, P12-R02, P12-R04).
"""

from org.transcrypt.stubs.browser import __pragma__

from app.settings_menu import SETTINGS_SLIDERS
from config.dev_viewer import DEV_VIEWER_CONFIG, DEV_VIEWERS
from ui.menu_view import (
    DevMenuView,
    DevViewerView,
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
        dev_labels: dict[str, list[str]] | None = None,
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
        # The labels of each dev viewer's items (D-199); None: no dev menu.
        self.dev_labels = dev_labels


def _pause_view(state: MenuState, ctx: MenuViewContext) -> PauseView:
    """The pause menu (P12-R02), and its `Leave the level?` question when it shows."""
    texts: Any = ctx.game.texts
    question = None
    if state.leaving:
        question = PauseQuestion(texts.leaveLevel, [texts.no, texts.yes], state.choice)
    return PauseView(
        texts.paused,
        [texts.resume, texts.settings, texts.mainMenu],
        texts.pauseHint,
        question,
    )


def _settings_view(state: MenuState, ctx: MenuViewContext) -> SettingsView:
    """The settings screen (P12-R04): one slider per volume."""
    texts: Any = ctx.game.texts
    labels = {"music": texts.musicVolume, "sfx": texts.sfxVolume}
    sliders: list[SliderView] = []
    for slider in SETTINGS_SLIDERS:
        value = state.volumes.music if slider == "music" else state.volumes.sfx
        sliders.append(SliderView(labels[slider], value, ctx.volume_steps))
    return SettingsView(
        texts.settings,
        texts.settingsHint,
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
    texts: Any = ctx.game.texts
    choices = None
    if result.checkpoint is not None:
        choices = LevelChoices(
            [texts.continueFromCheckpoint, texts.toLevelSelect],
            state.choice,
        )
    over = result.outcome == "over"
    return LevelCompleteView(
        texts.gameOver if over else texts.levelComplete,
        over,
        label(result.level_id),
        texts.enemiesDestroyed(result.destroyed, result.spawned),
        texts.finalScore(int(result.score)),
        texts.continueHint,
        texts.newHighScore if result.new_high_score else None,
        choices,
    )


def _selected_on_game(state: MenuState, paused: PauseView | None) -> int:
    """The entry taps select on the game screen: the pause menu's, or the panel's choice."""
    if paused is not None:
        return state.choice if paused.question is not None else state.selection
    result = state.level_result
    return state.choice if result is not None and result.checkpoint is not None else 0


def _game_view(state: MenuState, ctx: MenuViewContext) -> GameScreenView:
    texts: Any = ctx.game.texts
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
        texts.gameLevel(label(state.chosen_level_id)),
        texts.fire,
        texts.pauseButton,
        complete,
        paused,
        _selected_on_game(state, paused),
    )


def _dev_view(state: MenuState, ctx: MenuViewContext) -> Any:
    """The dev menu, or the dev viewer shown (D-199)."""
    texts = DEV_VIEWER_CONFIG.texts
    back: str = ctx.game.texts.back
    viewer = state.dev_viewer
    if viewer is None:
        entries = [texts.labels[v] for v in DEV_VIEWERS]
        return DevMenuView(texts.heading, texts.hint, back, state.selection, entries)
    labels = ctx.dev_labels[viewer] if ctx.dev_labels is not None else []
    index = state.selection
    item = labels[index] if index < len(labels) else ""
    scrub = viewer == "levels"
    return DevViewerView(
        texts.labels[viewer],
        texts.levels_hint if scrub else texts.models_hint,
        back,
        index,
        item,
        str(index + 1) + " / " + str(len(labels)),
        scrub,
    )


def build_menu_view(state: MenuState, ctx: MenuViewContext) -> Any:
    """The view of the current screen: one of the classes of `ui/menu_view`."""
    game = ctx.game
    texts: Any = game.texts
    screen = state.screen
    if screen == "loading":
        return LoadingView(texts.loading, ctx.progress)
    if screen == "title":
        return TitleView(
            game.title,
            texts.highScore,
            ctx.high_score,
            texts.start,
            texts.settings,
            state.selection,
            texts.startHint,
            ctx.version,
            ctx.commit,
            DEV_VIEWER_CONFIG.texts.entry if ctx.dev_labels is not None else None,
        )
    if screen == "ship-select":
        ships = [ship_caption(game.player_ships, ship.id) for ship in game.player_ships.ships]
        return ShipSelectView(
            texts.chooseShip,
            texts.chooseShipHint,
            texts.back,
            state.selection,
            ships,
            ctx.cards_width_percent,
        )
    if screen == "level-select":
        options = [LevelOption(entry.label, not entry.unlocked) for entry in game.levels.levels]
        return LevelSelectView(
            texts.chooseLevel,
            texts.chooseLevelHint,
            texts.back,
            state.selection,
            game.levels.columns,
            options,
            texts.locked,
        )
    if screen in ["game", "pause"]:
        return _game_view(state, ctx)
    in_dev = screen in ["dev", "dev-viewer"]
    return _dev_view(state, ctx) if in_dev else _settings_view(state, ctx)
