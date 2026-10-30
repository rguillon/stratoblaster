"""Tunables and texts of the dev viewers (reviewer, 2026-10-30, D-199): a Dev entry on the
title screen (with `?dev` in the URL) opens a menu of viewers of the player ships, the enemies,
the bosses, the props and the levels, drawn as in game.
"""


class DevViewerTexts:
    """Texts of the dev menu and viewers (a developer tool: not the game's texts)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        entry: str,
        heading: str,
        hint: str,
        labels: dict[str, str],
        models_hint: str,
        levels_hint: str,
        loading: str,
        groups_hint: str,
        grid_note: str,
    ) -> None:
        # The title screen's entry.
        self.entry = entry
        # The dev menu's heading and hint.
        self.heading = heading
        self.hint = hint
        # The label of each viewer, by its id (`DEV_VIEWERS`).
        self.labels = labels
        # The hint of the model viewers and of the levels viewer.
        self.models_hint = models_hint
        self.levels_hint = levels_hint
        # Shown while a viewer's scene is being built.
        self.loading = loading
        # The hint of a model viewer whose items are in groups (D-202: the props).
        self.groups_hint = groups_hint
        # The props viewer's status line: what a square of its grid is (D-205).
        self.grid_note = grid_note


class DevPropStageConfig:
    """How the props viewer shows a prop (D-205): alone on a plain floor ruled in blocks, under
    studio lights, no level's ground loaded.

    `clear_color`: the background (RGBA). `ambient_intensity`; `key_direction`, `key_intensity`,
    `fill_direction`, `fill_intensity`: a hemispheric light and two directional lights, the fill
    from the other side so the faces away from the key are not black. `environment_stops`
    ([height, r, g, b] each), `environment_intensity`, `glow` ([intensity, blur kernel size]): the
    image-based lighting and glow, when the viewer has them. `floor_color`, `grid_color` (RGB): the
    floor and the lines of the grid, one square per block (the game's tile), `grid_lift` above the
    floor. `grid_reach`: blocks of grid beyond the prop's footprint, each way. `pitch`: the
    camera's starting angle from straight up (radians); `pitch_range`: the lowest and highest it
    is dragged to. `view_shift`: how far right the prop is drawn, as a share of half the view's
    width, to clear the menu on the left (D-206).
    """

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        clear_color: list[float],
        ambient_intensity: float,
        key_direction: list[float],
        key_intensity: float,
        fill_direction: list[float],
        fill_intensity: float,
        environment_stops: list[list[float]],
        environment_intensity: float,
        glow: list[float],
        floor_color: list[float],
        grid_color: list[float],
        grid_lift: float,
        grid_reach: int,
        pitch: float,
        pitch_range: list[float],
        view_shift: float,
    ) -> None:
        self.clear_color = clear_color
        self.ambient_intensity = ambient_intensity
        self.key_direction = key_direction
        self.key_intensity = key_intensity
        self.fill_direction = fill_direction
        self.fill_intensity = fill_intensity
        self.environment_stops = environment_stops
        self.environment_intensity = environment_intensity
        self.glow = glow
        self.floor_color = floor_color
        self.grid_color = grid_color
        self.grid_lift = grid_lift
        self.grid_reach = grid_reach
        self.pitch = pitch
        self.pitch_range = pitch_range
        self.view_shift = view_shift


class DevViewerConfig:
    """How the dev viewers show things.

    `close_up_fill`: share of the screen height the model fills in the close-up (the camera's field
    of view narrowed, so the ground is magnified with it). `wheel_step`, `scrub_seconds`: the
    levels viewer's wheel moves the time by `scrub_seconds` per `wheel_step` pixels. `scrub_ease`:
    how fast the levels viewer catches up with the wheel, per second. `zoom_per_pixel`,
    `zoom_range`: in the model viewers the wheel zooms (D-208), by e^(`zoom_per_pixel`) per pixel,
    within `zoom_range` (times the view without zoom). `model_seed`: the random
    numbers the enemies and bosses are spawned with (their look only). `turn_per_pixel`: radians a
    model turns per pixel dragged.
    """

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        close_up_fill: float,
        wheel_step: float,
        scrub_seconds: float,
        scrub_ease: float,
        zoom_per_pixel: float,
        model_seed: int,
        texts: DevViewerTexts,
        turn_per_pixel: float,
        props: DevPropStageConfig,
        zoom_range: list[float],
    ) -> None:
        self.close_up_fill = close_up_fill
        self.wheel_step = wheel_step
        self.scrub_seconds = scrub_seconds
        self.scrub_ease = scrub_ease
        self.zoom_per_pixel = zoom_per_pixel
        self.zoom_range = zoom_range
        self.model_seed = model_seed
        self.texts = texts
        self.turn_per_pixel = turn_per_pixel
        self.props = props


# The viewers of the dev menu, in order (their ids).
DEV_VIEWERS = ["ships", "enemies", "bosses", "props", "levels"]

DEV_VIEWER_CONFIG = DevViewerConfig(
    0.35,
    100,
    4,
    10,
    0.0015,
    7,
    DevViewerTexts(
        "Dev",
        "Dev tools",
        "▲ ▼ to pick · Enter or tap to open",
        {
            "ships": "Player ships",
            "enemies": "Enemies",
            "bosses": "Bosses",
            "props": "Props",
            "levels": "Levels",
        },
        "Wheel: zoom · ◀ ▶ or menu: next · Drag: turn · Enter: close-up / game size · Esc: back",
        "Wheel: scrub · Arrows: level · Enter: play / stop · Esc: back",
        "Building…",
        "Wheel: zoom · ◀ ▶ or menu: next · ▲ ▼: group · Drag: turn · Enter: close-up / game size"
        " · Esc: back",
        "1 square = 1 block",
    ),
    0.01,
    DevPropStageConfig(
        [0.12, 0.1, 0.18, 1],
        1,
        [-0.4, -1, 0.6],
        1.9,
        [0.5, -0.6, -0.7],
        0.9,
        [
            [-1, 0.06, 0.05, 0.08],
            [0, 0.5, 0.5, 0.6],
            [1, 0.85, 0.9, 1],
        ],
        1.2,
        [0.6, 32],
        [0.07, 0.07, 0.1],
        [0.2, 0.75, 0.9],
        0.3,
        8,
        1.0,
        [0.15, 1.45],
        0.34,
    ),
    [0.25, 8],
)
