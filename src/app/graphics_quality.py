# Copyright (c) 2026 Renaud Guillon
"""The graphics quality of the session (D-410): chosen by the frames' times, or held by a setting.

While a level plays (not loading, not paused), each frame's interval and work go to the
`QualityGovernor`; when it changes the level, the page draws its new share of the pixels and the
level's scene gets its shadows and glows for it. A new level's scene gets the current level when it
is first seen. The level the game chose is kept between visits, so the next one starts there.
The setting holds a level instead: High (the full look), Medium or Low.
"""

from config.engine import QualityConfig
from core.loop.quality_governor import QualityGovernor
from render.quality import apply_quality, gpu_frame_ms

# isort: split
# __pragma__ ("skip")
from typing import Any

from host.key_value_storage import KeyValueStorage

# __pragma__ ("noskip")


# The Graphics quality setting's choices: the game decides, or a level held.
QUALITY_MODES = ["auto", "high", "medium", "low"]


def saved_level_key(game_id: str) -> str:
    """Return the storage key of the level the game chose last (D-410)."""
    return game_id + "_graphics_level"


def parse_level(raw: str | None, levels: int) -> int:
    """Return a stored level: a whole number from 0 to `levels - 1`; anything else reads as 0."""
    if raw is None or len(raw) != 1 or raw < "0" or raw > "9":
        return 0
    level = int(raw)
    return level if level < levels else 0


class GraphicsQuality:
    """The graphics quality of the session (see the module doc).

    `set_render_scale(share)`: makes the page draw `share` of its pixels across; `gpu_timer`: a
    timer of the GPU's frames, or None.
    """

    def __init__(
        self,
        config: QualityConfig,
        storage: KeyValueStorage,
        game_id: str,
        set_render_scale: Any,
        gpu_timer: Any = None,
    ) -> None:
        self._config = config
        self._storage = storage
        self._key = saved_level_key(game_id)
        self._set_render_scale = set_render_scale
        self._gpu_timer = gpu_timer
        self._mode = "auto"
        level = parse_level(storage.get(self._key), len(config.levels))
        self._governor = QualityGovernor(config, level)
        self._scene: Any = None
        self._playing = False
        self._apply()

    @property
    def level(self) -> int:
        """The current level: 0 for the full look, higher for fewer pixels and cheaper effects."""
        return self._governor.level

    @property
    def mode(self) -> str:
        """The setting: `auto` (the game decides) or the level held (`high`, `medium`, `low`)."""
        return self._mode

    def set_mode(self, mode: str) -> None:
        """Hold the level of `mode`, or let the game decide again (`auto`, from its last level)."""
        if mode not in QUALITY_MODES or mode == self._mode:
            return
        self._mode = mode
        if mode == "auto":
            self._governor.level = parse_level(
                self._storage.get(self._key), len(self._config.levels)
            )
        else:
            self._governor.level = self._held_level(mode)
        self._governor.restart()
        self._apply()

    def _held_level(self, mode: str) -> int:
        if mode == "medium":
            return self._config.medium
        if mode == "low":
            return self._config.low
        return 0

    def frame(self, interval_ms: float, work_ms: float, scene: Any, playing: bool) -> None:
        """Count a frame drawn `interval_ms` after the last one, its work taking `work_ms`.

        `scene`: the level's, or None in the menus; `playing`: whether the level plays (not loading
        or paused).
        """
        if scene is not self._scene:
            self._scene = scene
            if scene is not None:
                self._apply_to_scene()
        if not playing:
            self._playing = False
            return
        if not self._playing:
            self._playing = True
            self._governor.restart()
            return
        if self._mode != "auto":
            return
        gpu = gpu_frame_ms(self._gpu_timer) if self._gpu_timer is not None else None
        if self._governor.sample(interval_ms, work_ms, gpu):
            self._apply()
            self._storage.set(self._key, str(self._governor.level))

    def _apply(self) -> None:
        look = self._config.levels[self._governor.level]
        self._set_render_scale(look.render_scale)
        self._apply_to_scene()

    def _apply_to_scene(self) -> None:
        if self._scene is None:
            return
        look = self._config.levels[self._governor.level]
        apply_quality(self._scene, look.render_scale, look.shadow_filter)
