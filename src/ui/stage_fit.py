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

    def __init__(
        self,
        left: float,
        top: float,
        width: float,
        height: float,
        scale: float,
        whole_scale: float | None = None,
        side_room: float | None = None,
    ) -> None:
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        # CSS pixels per logical pixel.
        self.scale = scale
        # The scale the whole stage would have, fitted in the window (the phone layout's measure).
        self.whole_scale = scale if whole_scale is None else whole_scale
        # Logical pixels of the stage in view right of the playfield window: its whole right side
        # column, or what the window's edge leaves of it (touch buttons sit there, D-329).
        self.side_room = side_room


def _floor(n: float) -> float:
    return float(window.Math.floor(n))


def _scale(view_width: float, view_height: float, width: float, height: float) -> float:
    """Return the largest scale at which `width x height` fits in a window of the given size."""
    return float(window.Math.max(0, window.Math.min(view_width / width, view_height / height)))


def _left(view_width: float, width: float, centre: float) -> float:
    """Left of a stage `width` wide in the window: centred, or, when wider, with `centre` centred.

    A stage wider than the window keeps its edges outside it, so it shows no bar.
    """
    if width <= view_width:
        return _floor((view_width - width) / 2)
    return _floor(window.Math.min(0, window.Math.max(view_width - width, view_width / 2 - centre)))


def fit_stage(
    view_width: float,
    view_height: float,
    logical: LogicalScreen,
    playfield: LogicalScreen | None = None,
) -> StageFit:
    """Fit the stage of the `logical` screen to a `view_width x view_height` window.

    Never stretched (GAME-SCREEN-02). Without a `playfield` window, the whole stage fits: the
    largest one with the logical aspect ratio, centred, never cropped. With one, the playfield
    window is what must fit (everything is drawn and laid out in it, D-252, D-317, D-319): it is as
    large as the window allows, centred, and the stage round it may run past the window's edges,
    cropping only the side columns, instead of shrinking the window with them (owner: "the display
    area get small for no good reason when I play with the browser size").
    """
    whole = _scale(view_width, view_height, logical.width, logical.height)
    scale = whole
    centre_x = logical.width / 2
    centre_y = logical.height / 2
    viewport = playfield.viewport if playfield is not None else None
    if playfield is not None and viewport is not None:
        scale = _scale(view_width, view_height, playfield.width, playfield.height)
        centre_x = (viewport[0] + viewport[2] / 2) * logical.width
        centre_y = (viewport[1] + viewport[3] / 2) * logical.height
    width = _floor(logical.width * scale)
    height = _floor(logical.height * scale)
    left = _left(view_width, width, centre_x * scale)
    side_room = None
    if viewport is not None and scale > 0:
        column = (1 - viewport[0] - viewport[2]) * logical.width
        window_right = left + (viewport[0] + viewport[2]) * logical.width * scale
        side_room = max(0.0, min(column, (view_width - window_right) / scale))
    return StageFit(
        left,
        _left(view_height, height, centre_y * scale),
        width,
        height,
        scale,
        whole,
        side_room,
    )


def render_ratio(device_ratio: float, fit: StageFit, max_render_scale: float) -> float:
    """Return the canvas pixels drawn per CSS pixel of the stage (D-250, ENG-110).

    The device pixel ratio (already capped), lowered so the canvas never draws more than
    `max_render_scale` pixels per logical pixel across: a 4K panel is drawn at 1920 x 1080 for
    a 1280 x 720 screen at 1.5. A stage with no room keeps the device ratio.
    """
    if fit.scale <= 0:
        return device_ratio
    return min(device_ratio, max_render_scale / fit.scale)


# Below this many CSS pixels per logical pixel (a phone, D-286), the menus are laid out across the
# whole window at their real size instead of being scaled down with the stage (UI-LOOK-02).
PHONE_SCALE = 0.5
# The class the overlay carries then.
PHONE_CLASS = "phone"
# Under this many logical pixels of the right side column in view, the touch buttons that sit in
# it (index.html, `.game-fire`, `.hud-bomb-button`: 92 px wide, 24 px from each edge) move into the
# playfield window; the overlay then carries this class (D-329).
SIDE_ROOM_MIN = 140
NARROW_SIDES_CLASS = "narrow-sides"


def phone_layout(fit: StageFit) -> bool:
    """Whether the stage is so small that the menus are laid out for a phone (UI-LOOK-02)."""
    return 0 < fit.whole_scale < PHONE_SCALE


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
    # On a phone the menus take the whole window instead (index.html, `#menu.phone`, D-286); the
    # HUD over a level being played keeps to the stage.
    # How much of the right side column is in view, for the touch buttons in it (D-329).
    room = fit.side_room
    if room is not None:
        overlay.style.setProperty("--side-room", _px(room))
    if room is not None and room < SIDE_ROOM_MIN:
        overlay.classList.add(NARROW_SIDES_CLASS)
    else:
        overlay.classList.remove(NARROW_SIDES_CLASS)
    if phone_layout(fit):
        overlay.classList.add(PHONE_CLASS)
    else:
        overlay.classList.remove(PHONE_CLASS)
