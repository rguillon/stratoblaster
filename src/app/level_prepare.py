"""Preparing a level's ground ahead of its play, ported from `app/level-prepare.ts` (P13-R03).

A level's scenery with its runout is made once per level, so its generated ground is reused.
"""

from org.transcrypt.stubs.browser import __pragma__

from core.content.game_level import find_game_level
from core.scenery.scenery_level import with_runout
from render.scenery.level_ground import request_level_ground
from render.scenery.procedural_textures import scenery_texture_jobs

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

# Each level's scenery with its runout (P13-R03): the levels, and their scenery at the same index.
_runout_levels = []  # type: list[Any]
_runout_scenery = []  # type: list[Any]


def _runout_index(level: Any) -> int:
    for i in range(len(_runout_levels)):
        if _runout_levels[i] is level:
            return i
    return -1


def scenery_with_runout(level: Any) -> Any:
    """The scenery of `level` with its runout, made once (P13-R03)."""
    index = _runout_index(level)
    if index >= 0:
        return _runout_scenery[index]
    runout = level.runout if level.runout is not None else 0
    scenery = with_runout(level.scenery, runout)
    _runout_levels.append(level)
    _runout_scenery.append(scenery)
    return scenery


def level_of(game: Any, level_id: str) -> Any:
    """The game level called `level_id`, or an error when it cannot be played."""
    level = find_game_level(game.game_levels, level_id)
    if level is None:
        raise ValueError('Level "' + level_id + '" cannot be played')
    return level


def prepare_level(game: Any, level_id: str) -> bool:
    """Asks for the ground of level `level_id` ahead of its `GamePlay` (P13-R03): true once it is
    ready (generated in the background when a worker does it, false until then).
    """
    return request_level_ground(scenery_with_runout(level_of(game, level_id)))


def prefetch_level(game: Any, level_id: str | None, loader: Any) -> None:
    """Starts preparing level `level_id` in the background, if it is one (P13-R03): its ground and
    its scenery textures, while the player is still choosing it. Nothing without a background
    loader.
    """
    level = None if level_id is None else find_game_level(game.game_levels, level_id)
    if loader is None or level is None:
        return
    request_level_ground(scenery_with_runout(level))
    look = game.view.scenery.looks.get(level.scenery.id)
    if look is not None:
        loader.prefetch_textures(scenery_texture_jobs(look, level.scenery.seed))


# Seconds the level select highlight rests on a level before it is prefetched.
PREFETCH_AFTER = 0.25


class LevelPrefetcher:
    """Prefetches the level highlighted on the level select screen once the highlight rests on it
    (P13-R03), so that moving across the grid does not queue every level passed over.
    """

    def __init__(self, game: Any, loader: Any) -> None:
        self._game = game
        self._loader = loader
        self._highlighted: str | None = None
        self._rest = 0.0
        self._done: list[str] = []

    def update(self, dt: float, level_id: str | None) -> None:
        """`dt` seconds later, with `level_id` highlighted (None: no level select shown)."""
        if level_id != self._highlighted:
            self._highlighted = level_id
            self._rest = 0.0
        self._rest += dt
        if level_id is None or self._rest < PREFETCH_AFTER or level_id in self._done:
            return
        self._done.append(level_id)
        prefetch_level(self._game, level_id, self._loader)

    def rested_on(self, seconds: float) -> str | None:
        """The level the highlight has rested on for `seconds` (at least until prefetched)."""
        if self._rest >= max(seconds, PREFETCH_AFTER):
            return self._highlighted
        return None

    def start(self, level_id: str) -> None:
        """The level being started now is prefetched at once, if it is not yet."""
        if level_id in self._done:
            return
        self._done.append(level_id)
        prefetch_level(self._game, level_id, self._loader)
