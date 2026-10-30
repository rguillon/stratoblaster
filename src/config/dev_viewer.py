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


class DevViewerConfig:
    """How the dev viewers show things.

    `close_up_fill`: share of the screen height the model fills in the close-up (the camera's field
    of view narrowed, so the ground is magnified with it). `wheel_step`: wheel delta (pixels) per
    model in the model viewers. `scrub_seconds`: level seconds per wheel step of `wheel_step` in
    the levels viewer. `scrub_ease`: how fast the levels viewer catches up with the wheel, per
    second. `max_wheel_steps`: most models one wheel event moves by. `model_seed`: the random
    numbers the enemies and bosses are spawned with (their look only). `turn_per_pixel`: radians a
    model turns per pixel dragged.
    """

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        close_up_fill: float,
        wheel_step: float,
        scrub_seconds: float,
        scrub_ease: float,
        max_wheel_steps: int,
        model_seed: int,
        texts: DevViewerTexts,
        turn_per_pixel: float,
    ) -> None:
        self.close_up_fill = close_up_fill
        self.wheel_step = wheel_step
        self.scrub_seconds = scrub_seconds
        self.scrub_ease = scrub_ease
        self.max_wheel_steps = max_wheel_steps
        self.model_seed = model_seed
        self.texts = texts
        self.turn_per_pixel = turn_per_pixel


# The viewers of the dev menu, in order (their ids).
DEV_VIEWERS = ["ships", "enemies", "bosses", "props", "levels"]

DEV_VIEWER_CONFIG = DevViewerConfig(
    0.35,
    100,
    4,
    10,
    3,
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
        "Wheel / arrows: next · Drag: turn · Enter: close-up / game size · Esc: back",
        "Wheel: scrub · Arrows: level · Enter: play / stop · Esc: back",
        "Building…",
    ),
    0.01,
)
