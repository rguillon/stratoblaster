"""Vertex-coloured rectangles for gradients (ported from `render/geometry/gradient-shapes.ts`)."""

from render.environment.gradient_cube import GradientStop

# A gradient rectangle needs at least this many stops.
MIN_STOPS = 2


class ColoredGeometry:
    """Raw vertex-coloured geometry (XYZ positions, RGBA colours, 4 per vertex)."""

    def __init__(self) -> None:
        self.positions: list[float] = []
        self.indices: list[int] = []
        self.colors: list[float] = []


def _push_row(geo: ColoredGeometry, half_width: float, y: float, rgb: list[float]) -> None:
    geo.positions.extend([-half_width, y, 0, half_width, y, 0])
    geo.colors.extend([rgb[0], rgb[1], rgb[2], 1, rgb[0], rgb[1], rgb[2], 1])


def _join_rows(geo: ColoredGeometry, r: int) -> None:
    """Joins row `r` (2 vertices) to the next row with two triangles."""
    a = r * 2
    geo.indices.extend([a, a + 1, a + 3, a, a + 3, a + 2])


def _stable_sorted_by_at(stops: list[GradientStop]) -> list[GradientStop]:
    """The stops sorted by `at`, keeping equal ones in their order (Transcrypt's sort is not
    stable and takes no comparator)."""
    result: list[GradientStop] = []
    for stop in stops:
        i = len(result)
        while i > 0 and result[i - 1].at > stop.at:
            i -= 1
        result.insert(i, stop)
    return result


def build_gradient_rect(width: float, height: float, stops: list[GradientStop]) -> ColoredGeometry:
    """A `width × height` rectangle centred on the origin whose colour goes from the bottom to
    the top through `stops` (`at` -1 = bottom edge, 1 = top edge). One vertex row per stop."""
    if len(stops) < MIN_STOPS:
        raise ValueError("A gradient rectangle needs at least 2 stops")
    geo = ColoredGeometry()
    for i, stop in enumerate(_stable_sorted_by_at(stops)):
        _push_row(geo, width / 2, (stop.at * height) / 2, stop.color)
        if i > 0:
            _join_rows(geo, i - 1)
    return geo
