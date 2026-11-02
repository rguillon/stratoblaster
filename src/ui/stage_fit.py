# Copyright (c) 2026 Renaud Guillon
"""Places the game stage in the window (GAME-SCREEN-02, UI-LOOK-02)."""

from org.transcrypt.stubs.browser import window

# isort: split
# __pragma__ ("skip")
from typing import Any

from core.content.game_definition import LogicalScreen

# __pragma__ ("noskip")


class StageFit:
    """Where the game stage goes in the window, in CSS pixels."""

    def __init__(self, left: float, top: float, width: float, height: float, scale: float) -> None:
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        # CSS pixels per logical pixel.
        self.scale = scale


def fit_stage(view_width: float, view_height: float, logical: LogicalScreen) -> StageFit:
    """Largest stage with the logical aspect ratio that fits a `view_width x view_height` window.

    Centred (GAME-SCREEN-02): never cropped, never stretched.
    """
    scale = float(
        window.Math.max(
            0, window.Math.min(view_width / logical.width, view_height / logical.height)
        )
    )
    # Exactly the overlay's scaled size, not rounded to whole pixels: the overlay is scaled by
    # `scale`, and a stage a fraction smaller would clip its bottom edge (D-249).
    width = logical.width * scale
    height = logical.height * scale
    return StageFit(
        float(window.Math.floor((view_width - width) / 2)),
        float(window.Math.floor((view_height - height) / 2)),
        width,
        height,
        scale,
    )


def _px(n: float) -> str:
    return str(n) + "px"


def apply_stage_fit(stage: Any, overlay: Any, fit: StageFit, logical: LogicalScreen) -> None:
    """Places the stage (canvas container) in the window and scales the menu overlay.

    Which is laid out at the logical resolution (UI-LOOK-01), to the stage size.
    """
    stage.style.left = _px(fit.left)
    stage.style.top = _px(fit.top)
    stage.style.width = _px(fit.width)
    stage.style.height = _px(fit.height)
    overlay.style.width = _px(logical.width)
    overlay.style.height = _px(logical.height)
    overlay.style.transform = "scale(" + str(fit.scale) + ")"
