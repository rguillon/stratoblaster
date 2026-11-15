# Copyright (c) 2026 Renaud Guillon
"""The settings screen (UI-SET-03): up / down pick a slider, left / right change it by one step.

A tap or a drag sets it. Pure: the app saves and applies the volumes. Only the music and sound
effects volumes exist (ENG-112 asks for more).
"""

import math

# Infinity without `math.inf`, which does not compile under Transcrypt.
INFINITY = float("Infinity")


class Volumes:
    """The settings (UI-SET-02): the two volumes and the graphics quality (D-410).

    Each volume is a step from 0 (silent) to the slider's maximum; the graphics quality a step of
    `GRAPHICS_CHOICES`, 0 for Auto.
    """

    def __init__(self, music: int, sfx: int, graphics: int = 0) -> None:
        self.music = music
        self.sfx = sfx
        self.graphics = graphics


# The sliders of the settings screen, in display order: the two volumes, then the graphics quality
# (D-410), whose steps are choices: Auto, High, Medium, Low.
SETTINGS_SLIDERS = ["music", "sfx", "graphics"]
GRAPHICS_CHOICES = 4


def volume_of(volumes: Volumes, slider: str) -> int:
    """Return the step of the slider `slider` (`music`, `sfx` or `graphics`)."""
    if slider == "graphics":
        return volumes.graphics
    return volumes.music if slider == "music" else volumes.sfx


def with_volume(volumes: Volumes, slider: str, step: int) -> Volumes:
    """Return a copy of `volumes` with the slider `slider` set to `step`."""
    if slider == "music":
        return Volumes(step, volumes.sfx, volumes.graphics)
    if slider == "sfx":
        return Volumes(volumes.music, step, volumes.graphics)
    return Volumes(volumes.music, volumes.sfx, step)


def _is_integer(value: float) -> bool:
    """Number.isInteger: false for fractions, infinities and NaN."""
    return value - math.floor(value) == 0


def _is_finite(value: float) -> bool:
    """Number.isFinite: false for infinities and NaN."""
    return value - value == 0


def _slider_at(index: int) -> str | None:
    """Return the id of the slider at `index`, or None when there is none.

    That None is JavaScript's `undefined`.
    """
    if not _is_integer(index) or index < 0 or index >= len(SETTINGS_SLIDERS):
        return None
    return SETTINGS_SLIDERS[index]


class SettingsMenu:
    """The settings screen (UI-SET-03): up / down pick a slider, left / right change it by one step.

    A tap or a drag sets it.
    """

    def __init__(self, volumes: Volumes, max_step: int) -> None:
        self._max_step = max_step
        self._selection = 0
        self._volumes = Volumes(
            _clamp(volumes.music, max_step),
            _clamp(volumes.sfx, max_step),
            _clamp(volumes.graphics, GRAPHICS_CHOICES - 1),
        )

    @property
    def selection(self) -> int:
        """Index of the selected slider."""
        return self._selection

    @property
    def selected_id(self) -> str:
        """The slider selected: `music` or `sfx`."""
        slider = _slider_at(self._selection)
        return slider if slider is not None else "music"

    @property
    def volumes(self) -> Volumes:
        """The volumes the menu edits."""
        return self._volumes

    def open(self) -> None:
        """Open the screen with the first slider selected."""
        self._selection = 0

    def move(self, direction: str) -> str:
        """Change the selected slider for left or right, or move the selection for up or down."""
        if direction in ["left", "right"]:
            current = volume_of(self._volumes, self.selected_id)
            return self.set(self._selection, current + (-1 if direction == "left" else 1))
        return self.select(self._selection + (-1 if direction == "up" else 1))

    def select(self, index: int) -> str:
        """Select slider `index` if it is valid and not already selected."""
        if not _is_integer(index) or index < 0 or index >= len(SETTINGS_SLIDERS):
            return "none"
        if index == self._selection:
            return "none"
        self._selection = index
        return "moved"

    def set(self, index: int, value: float) -> str:
        """Set slider `index` to `value` (rounded and clamped to the slider) and select it."""
        slider = _slider_at(index)
        if slider is None or not _is_finite(value):
            return "none"
        moved = index != self._selection
        self._selection = index
        step = _clamp(value, self._max_of(slider))
        if step == volume_of(self._volumes, slider):
            return "moved" if moved else "none"
        self._volumes = with_volume(self._volumes, slider, step)
        return "adjusted"

    def _max_of(self, slider: str) -> int:
        """Return the highest step of `slider`: the volumes' maximum, or the last choice."""
        return GRAPHICS_CHOICES - 1 if slider == "graphics" else self._max_step


def _clamp(value: float, max_step: int) -> int:
    """Return `value` rounded (halves up, as Math.round) and kept from 0 to `max_step`."""
    return min(max_step, max(0, math.floor(value + 0.5)))
