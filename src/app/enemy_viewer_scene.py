"""The scene of the enemies page (P05-R11), ported from `app/enemy-viewer-scene.ts`."""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from app.level_scene import LevelSceneOptions, build_level_scene  # noqa: E402
from config.enemy_viewer import ENEMY_VIEWER_CONFIG as CFG  # noqa: E402


def build_enemy_viewer_scene(engine: Any, game: Any, environment: bool, glow: Any) -> Any:
    """Builds the scene of the enemies page (P05-R11): the ground of the game's first level under
    the tilted playfield camera, and the playfield layer above it. `glow` is the enemies' glow."""
    # The ground of the first playable level.
    level = game.game_levels[0].scenery if len(game.game_levels) > 0 else None
    if level is None:
        raise ValueError("The game has no level")
    return build_level_scene(
        engine,
        game,
        LevelSceneOptions(
            level, environment, glow, int(CFG.environment_cube_size), CFG.stage, None, None
        ),
    )
