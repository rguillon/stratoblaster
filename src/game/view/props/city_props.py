"""Rows of lit windows for the buildings of the city centre (Phase 4 review) (see
`city_lots.py`)."""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from render.geometry.solids import SolidBuilder  # noqa: E402

__pragma__("noskip")


def window_bands(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    lights: SolidBuilder,
    size: list[float],
    span: list[float],
    gap: float,
    band: float,
    color: list[float],
    at: list[float],
    proud: float = 0.1,
) -> None:
    """Rows of lit windows on the 4 faces (few and thick: thin bands under a pixel shimmered as
    the view scrolled) of a `w × d` block, from `y0` to `y1`, every `gap`, each row `band` high:
    one flat quad per face and row, just off the walls (2 triangles each). `proud` is how far
    the bands stand off the walls."""
    w = size[0]
    d = size[1]
    y0 = span[0]
    y1 = span[1]
    x = at[0]
    z = at[1]
    x0 = x - w * 0.43
    x1 = x + w * 0.43
    xl = x - w / 2 - proud
    xr = x + w / 2 + proud
    z0 = z - d * 0.43
    z1 = z + d * 0.43
    zf = z - d / 2 - proud
    zb = z + d / 2 + proud
    # The bottom edge of each face, from (x, z) to (x, z), counter-clockwise seen from outside.
    faces = [
        [x0, zf, x1, zf],
        [x1, zb, x0, zb],
        [xl, z1, xl, z0],
        [xr, z0, xr, z1],
    ]
    y = y0
    while y + band <= y1:
        t = y + band
        for face in faces:
            ax = face[0]
            az = face[1]
            bx = face[2]
            bz = face[3]
            lights.face(
                [
                    [ax, y, az],
                    [ax, t, az],
                    [bx, t, bz],
                    [bx, y, bz],
                ],
                color,
            )
        y += gap
