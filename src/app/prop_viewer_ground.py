"""The ground of the `props/` page (phase 15), ported from `app/prop-viewer-ground.ts`: a plain
floor over the layout, the lines of the grid of tiles over it, and the road tiles of the layout."""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from config.prop_viewer import PROP_VIEWER_CONFIG as CFG  # noqa: E402
from render.babylon import (  # noqa: E402
    color3,
    color3_black,
    color4,
    create_colored_line_system,
    create_ground,
    new_standard_material,
    new_transform_node,
    vector3,
)


class ViewerTiles:
    """The grid of tiles of the props page: `tile` (its rules), `look` (how its roads look, None:
    no road is drawn) and `pieces` (models drawn as road pieces, by id, centred on the origin;
    None when there are none)."""

    def __init__(self, tile: Any, look: Any, pieces: Any) -> None:
        self.tile = tile
        self.look = look
        self.pieces = pieces


def _floor(scene: Any, bounds: list[float], parent: Any) -> None:
    """A plain floor over `bounds` ([x0, x1, z0, z1], in world units)."""
    x0 = bounds[0]
    x1 = bounds[1]
    z0 = bounds[2]
    z1 = bounds[3]
    ground = create_ground("props-ground", x1 - x0, z1 - z0, 1, scene)
    ground.position.set((x0 + x1) / 2, 0, (z0 + z1) / 2)
    material = new_standard_material("props-ground", scene)
    material.diffuseColor = color3(CFG.ground.color[0], CFG.ground.color[1], CFG.ground.color[2])
    material.specularColor = color3_black()
    ground.material = material
    ground.isPickable = False
    ground.parent = parent


def _grid_lines(scene: Any, bounds: list[float], size: float, parent: Any) -> None:
    """Lines along every tile edge of [x0, x1] x [z0, z1] (world units), above the roads."""
    x0 = bounds[0]
    x1 = bounds[1]
    z0 = bounds[2]
    z1 = bounds[3]
    y = CFG.grid.height
    lines: list[list[Any]] = []
    x = x0
    while x <= x1 + 1e-6:
        lines.append([vector3(x, y, z0), vector3(x, y, z1)])
        x += size
    z = z0
    while z <= z1 + 1e-6:
        lines.append([vector3(x0, y, z), vector3(x1, y, z)])
        z += size
    color = color4(CFG.grid.color[0], CFG.grid.color[1], CFG.grid.color[2], 1)
    colors: list[list[Any]] = [[color for _vertex in line] for line in lines]
    mesh = create_colored_line_system("props-tile-grid", lines, colors, scene)
    mesh.isPickable = False
    mesh.parent = parent


def build_viewer_ground(scene: Any, layout: Any, tiles: Any, roads: Any) -> Any:
    """The floor, the grid and the roads of `layout`, under one node; the floor reaches `margin`
    tiles beyond the layout. `roads` is the ViewerRoads (None: no road tiles)."""
    root = new_transform_node("props-floor", scene)
    t = tiles.tile.size
    m = CFG.ground.margin
    bx0 = layout.bounds[0]
    bx1 = layout.bounds[1]
    bz0 = layout.bounds[2]
    bz1 = layout.bounds[3]
    bounds = [(bx0 - m) * t, (bx1 + m) * t, (bz0 - m) * t, (bz1 + m) * t]
    _floor(scene, bounds, root)
    _grid_lines(scene, bounds, t, root)
    mesh = roads.mesh("props-roads", layout.roads) if roads else None
    if mesh:
        mesh.isPickable = False
        mesh.parent = root
    return root
