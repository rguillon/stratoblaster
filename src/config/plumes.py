"""Plume kinds (phase 10, P10-R08), ported from `config/plumes.ts`.

A kind of plume is a column of soft, see-through puffs rising from a prop, growing and fading as
they rise, drifting with the wind. Only a look; kept faint so it never hides what flies above it.
"""


class PlumeKind:
    """A kind of plume."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        puffs: float,
        seconds: float,
        height: float,
        lean: float,
        size: tuple[float, float],
        color: tuple[float, float, float],
        alpha: float,
        self_lit: float,
    ) -> None:
        # Puffs in one column (each its own quad), and the seconds one takes to rise to the top.
        self.puffs = puffs
        self.seconds = seconds
        # Height the column rises to and how far the wind bends it sideways at the top (world
        # units).
        self.height = height
        self.lean = lean
        # Puff size (world units across) at the bottom and at the top.
        self.size = size
        # Colour, lit by the scene's light, and the most opaque a puff is (it fades in and out).
        self.color = color
        self.alpha = alpha
        # Share (0..1) of its colour it keeps at night, as if lit from below by fire.
        self.self_lit = self_lit


# The plume kinds of the engine (phase 10).
PLUME_KINDS = {
    # Slow grey-brown smoke columns from vents, cinder cones and chimneys.
    "smoke": PlumeKind(7, 9, 70, 18, (5, 22), (0.34, 0.32, 0.3), 0.32, 0.1),
    # White steam rising where the hot coast meets the sea, and from cooling towers and wells.
    "steam": PlumeKind(6, 6, 45, 10, (4, 18), (0.86, 0.87, 0.88), 0.26, 0.05),
}
