"""Vertex-coloured, textured quads (D-210: one quad per building wall, mapped on the windows'
atlas)."""

from render.geometry.gradient_shapes import ColoredGeometry


class TexturedGeometry(ColoredGeometry):
    """A `ColoredGeometry` with texture coordinates (UV, 2 per vertex)."""

    def __init__(self) -> None:
        ColoredGeometry.__init__(self)
        self.uvs: list[float] = []


class QuadBuilder:
    """Builds textured quads into one `TexturedGeometry`."""

    def __init__(self) -> None:
        self.geometry = TexturedGeometry()

    def quad(self, corners: list[list[float]], uv: list[float], color: list[float]) -> None:
        """A flat quad, its corners (two up one edge, then two down the other) going
        counter-clockwise seen from the front (as `SolidBuilder.face`), showing the texture's
        `[u0, v0, u1, v1]` (u1 on its first edge, v0 along its first and last corners), tinted by
        `color`."""
        geo = self.geometry
        base = len(geo.positions) // 3
        for corner in corners:
            geo.positions.extend([corner[0], corner[1], corner[2]])
            geo.colors.extend([color[0], color[1], color[2], 1])
        u0 = uv[0]
        v0 = uv[1]
        u1 = uv[2]
        v1 = uv[3]
        geo.uvs.extend([u1, v0, u1, v1, u0, v1, u0, v0])
        # Babylon front faces have the normal (c - a) × (b - a), hence the swapped order.
        geo.indices.extend([base, base + 2, base + 1, base, base + 3, base + 2])
