"""Texts of the engine's menu screens, provided by the game (ENG-140, ENG-144).

Ported from `core/content/menu-texts.ts`. The fields that the TypeScript made functions (plural
or parameterised texts) are callables.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402

__pragma__("noskip")


class MenuTexts:
    """The texts of the menu screens, the HUD, the pause menu and the settings screen."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        loading: str,
        high_score: str,
        start: str,
        start_hint: str,
        choose_ship: str,
        choose_ship_hint: str,
        choose_level: str,
        choose_level_hint: str,
        back: str,
        locked: str,
        game_level: Callable[[str], str],
        fire: str,
        level_complete: str,
        game_over: str,
        enemies_destroyed: Callable[[int, int], str],
        final_score: Callable[[int], str],
        new_high_score: str,
        continue_hint: str,
        continue_from_checkpoint: str,
        to_level_select: str,
        hud_health: str,
        hud_lives: Callable[[int], str],
        hud_weapon: Callable[[str, int, int], str],
        hud_bombs: Callable[[int], str],
        hud_score: Callable[[int], str],
        hud_high_score: Callable[[int], str],
        hud_bomb: Callable[[int], str],
        hud_mini_boss: str,
        hud_boss: str,
        unsupported: str,
        settings: str,
        settings_hint: str,
        music_volume: str,
        sfx_volume: str,
        pause_button: str,
        paused: str,
        resume: str,
        main_menu: str,
        pause_hint: str,
        leave_level: str,
        no: str,
        yes: str,
    ) -> None:
        """Fields as in the TypeScript, in the same order. The functions are: `game_level(level
        label)`, `enemies_destroyed(destroyed, spawned)`, `final_score(score)`, `hud_lives(lives)`,
        `hud_weapon(weapon name, level, levels)`, `hud_bombs(bombs)`, `hud_score(score)`,
        `hud_high_score(score)`, `hud_bomb(bombs)`.
        """
        self.loading = loading
        self.high_score = high_score
        self.start = start
        self.start_hint = start_hint
        self.choose_ship = choose_ship
        self.choose_ship_hint = choose_ship_hint
        self.choose_level = choose_level
        self.choose_level_hint = choose_level_hint
        self.back = back
        self.locked = locked
        self.game_level = game_level
        self.fire = fire
        self.level_complete = level_complete
        self.game_over = game_over
        self.enemies_destroyed = enemies_destroyed
        self.final_score = final_score
        self.new_high_score = new_high_score
        self.continue_hint = continue_hint
        self.continue_from_checkpoint = continue_from_checkpoint
        self.to_level_select = to_level_select
        self.hud_health = hud_health
        self.hud_lives = hud_lives
        self.hud_weapon = hud_weapon
        self.hud_bombs = hud_bombs
        self.hud_score = hud_score
        self.hud_high_score = hud_high_score
        self.hud_bomb = hud_bomb
        self.hud_mini_boss = hud_mini_boss
        self.hud_boss = hud_boss
        self.unsupported = unsupported
        self.settings = settings
        self.settings_hint = settings_hint
        self.music_volume = music_volume
        self.sfx_volume = sfx_volume
        self.pause_button = pause_button
        self.paused = paused
        self.resume = resume
        self.main_menu = main_menu
        self.pause_hint = pause_hint
        self.leave_level = leave_level
        self.no = no
        self.yes = yes
