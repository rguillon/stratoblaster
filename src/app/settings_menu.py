"""The settings screen (P12-R04), ported from `app/settings-menu.ts`: up / down pick a slider,
left / right change it by one step, a tap or a drag sets it. Pure: the app saves and applies the
volumes.
"""

import math

# Infinity without `math.inf`, which does not compile under Transcrypt.
INFINITY = float("Infinity")


class Volumes:
    """The two volume settings (P12-R04), each a step from 0 (silent) to the slider's maximum."""

    def __init__(self, music: int, sfx: int) -> None:
        self.music = music
        self.sfx = sfx


# The sliders of the settings screen, in display order.
SETTINGS_SLIDERS = ["music", "sfx"]


def volume_of(volumes: Volumes, slider: str) -> int:
    """The step of the slider `slider` (`music` or `sfx`)."""
    return volumes.music if slider == "music" else volumes.sfx


def with_volume(volumes: Volumes, slider: str, step: int) -> Volumes:
    """A copy of `volumes` with the slider `slider` set to `step`."""
    if slider == "music":
        return Volumes(step, volumes.sfx)
    return Volumes(volumes.music, step)


def _is_integer(value: float) -> bool:
    """Number.isInteger: false for fractions, infinities and NaN."""
    return value - math.floor(value) == 0


def _is_finite(value: float) -> bool:
    """Number.isFinite: false for infinities and NaN."""
    return value - value == 0


def _slider_at(index: int) -> str | None:
    """The id of the slider at `index`, or None (JavaScript's `undefined`) when there is none."""
    if not _is_integer(index) or index < 0 or index >= len(SETTINGS_SLIDERS):
        return None
    return SETTINGS_SLIDERS[index]


class SettingsMenu:
    """The settings screen (P12-R04): up / down pick a slider, left / right change it by one step,
    a tap or a drag sets it.
    """

    def __init__(self, volumes: Volumes, max_step: int) -> None:
        self._max_step = max_step
        self._selection = 0
        self._volumes = Volumes(self._clamp(volumes.music), self._clamp(volumes.sfx))

    @property
    def selection(self) -> int:
        return self._selection

    @property
    def selected_id(self) -> str:
        """The slider selected: `music` or `sfx`."""
        slider = _slider_at(self._selection)
        return slider if slider is not None else "music"

    @property
    def volumes(self) -> Volumes:
        return self._volumes

    def open(self) -> None:
        """The screen opens with the first slider selected."""
        self._selection = 0

    def move(self, direction: str) -> str:
        if direction in ["left", "right"]:
            current = volume_of(self._volumes, self.selected_id)
            return self.set(self._selection, current + (-1 if direction == "left" else 1))
        return self.select(self._selection + (-1 if direction == "up" else 1))

    def select(self, index: int) -> str:
        if not _is_integer(index) or index < 0 or index >= len(SETTINGS_SLIDERS):
            return "none"
        if index == self._selection:
            return "none"
        self._selection = index
        return "moved"

    def set(self, index: int, value: float) -> str:
        """Sets slider `index` to `value` (rounded and clamped to the slider) and selects it."""
        slider = _slider_at(index)
        if slider is None or not _is_finite(value):
            return "none"
        moved = index != self._selection
        self._selection = index
        step = self._clamp(value)
        if step == volume_of(self._volumes, slider):
            return "moved" if moved else "none"
        self._volumes = with_volume(self._volumes, slider, step)
        return "adjusted"

    def _clamp(self, value: float) -> int:
        # Math.round: halves go up.
        return min(self._max_step, max(0, math.floor(value + 0.5)))
