"""Plumbing of a top-down playfield (ported from `render/shot-playfield.ts`).

The playfield is the XY plane at Z = 0, one world unit per logical pixel, Y up, seen from -Z.
`size` objects have `width` and `height`; `muzzle` has `x` and `y`; a target has `id`, `x`, `y`,
`radius`, `health` and `max_health`; streams have `angleDeg` and `offsetX`.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from render.babylon import (
    color3,
    color3_black,
    create_line_system,
    create_plane,
    create_torus,
    new_standard_material,
    new_transform_node,
    set_enabled,
    vector3,
)

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


def _flat_material(label: str, color: list[float], scene: Any) -> Any:
    mat = new_standard_material(label, scene)
    mat.emissiveColor = color3(color[0], color[1], color[2])
    mat.diffuseColor = color3_black()
    mat.specularColor = color3_black()
    mat.disableLighting = True
    mat.backFaceCulling = False
    return mat


def build_playfield_grid(
    scene: Any,
    size: Any,
    cell: float,
    depth: float,
    color: list[float],
) -> Any:
    """A grid of lines every `cell` pixels over a `width × height` playfield, at `depth` behind
    the playfield plane, so it stays behind the ships and the shots."""
    width = size.width
    height = size.height
    lines: list[list[Any]] = []
    x = 0.0
    while x <= width:
        lines.append([vector3(x, 0, depth), vector3(x, height, depth)])
        x = x + cell
    y = 0.0
    while y <= height:
        lines.append([vector3(0, y, depth), vector3(width, y, depth)])
        y = y + cell
    grid = create_line_system("playfield-grid", lines, scene)
    grid.color = color3(color[0], color[1], color[2])
    grid.isPickable = False
    return grid


def build_stream_guides(
    scene: Any,
    muzzle: Any,
    streams: list[Any],
    length: float,
    color: list[float],
) -> Any:
    """Straight lines from the launch point along each stream (angles from +Y, positive to the
    right)."""
    lines: list[list[Any]] = []
    for s in streams:
        a = (s.angleDeg * math.pi) / 180
        start = vector3(muzzle.x + s.offsetX, muzzle.y, 0.5)
        end = start.add(vector3(math.sin(a) * length, math.cos(a) * length, 0))
        lines.append([start, end])
    guides = create_line_system("stream-guides", lines, scene)
    guides.color = color3(color[0], color[1], color[2])
    guides.isPickable = False
    return guides


class TargetMarkerRing:
    """The ring look: `thickness`, the `color` while alive and the `dead_color`."""

    def __init__(self, thickness: float, color: list[float], dead_color: list[float]) -> None:
        self.thickness = thickness
        self.color = color
        self.dead_color = dead_color


class TargetHealthBarLook:
    """The health bar look: `width`, `height`, `gap` below the ring, and its two colours."""

    def __init__(
        self,
        width: float,
        height: float,
        gap: float,
        color: list[float],
        back_color: list[float],
    ) -> None:
        self.width = width
        self.height = height
        self.gap = gap
        self.color = color
        self.back_color = back_color


class TargetMarkerLook:
    """How the target markers look: the ring and the health bar."""

    def __init__(self, ring: TargetMarkerRing, health_bar: TargetHealthBarLook) -> None:
        self.ring = ring
        self.health_bar = health_bar


class _Marker:
    def __init__(self, root: Any, ring: Any, bar: Any, back: Any) -> None:
        self.root = root
        self.ring = ring
        self.bar = bar
        self.back = back


class TargetMarkers:
    """A ring per target with a health bar under it; dead targets are drawn dim, without a
    bar."""

    def __init__(self, scene: Any, targets: list[Any], look: TargetMarkerLook) -> None:
        self._look = look
        self._alive = _flat_material("target-ring", look.ring.color, scene)
        self._dead = _flat_material("target-ring-dead", look.ring.dead_color, scene)
        bar_mat = _flat_material("target-health", look.health_bar.color, scene)
        back_mat = _flat_material("target-health-back", look.health_bar.back_color, scene)
        self._markers: list[_Marker] = []
        for target in targets:
            label = "target-" + str(target.id)
            root = new_transform_node(label, scene)
            ring = create_torus(
                label + "-ring",
                target.radius * 2,
                look.ring.thickness,
                32,
                scene,
            )
            ring.rotation.x = math.pi / 2
            bar = create_plane(label + "-health", 1, scene)
            back = create_plane(label + "-health-back", 1, scene)
            bar.material = bar_mat
            back.material = back_mat
            for mesh in [ring, bar, back]:
                mesh.parent = root
                mesh.isPickable = False
            self._markers.append(_Marker(root, ring, bar, back))

    def sync(self, targets: list[Any]) -> None:
        """Moves the markers to their targets and shows their health."""
        hb = self._look.health_bar
        for i in range(len(self._markers)):
            if i >= len(targets):
                continue
            marker = self._markers[i]
            target = targets[i]
            alive = target.health > 0
            fraction = max(0, target.health / target.max_health)
            marker.root.position.set(target.x, target.y, 0)
            marker.ring.material = self._alive if alive else self._dead
            bar_y = -target.radius - hb.gap
            marker.back.position.set(0, bar_y, 0.2)
            marker.back.scaling.set(hb.width, hb.height, 1)
            marker.bar.position.set((-hb.width * (1 - fraction)) / 2, bar_y, 0.1)
            marker.bar.scaling.set(max(0.001, hb.width * fraction), hb.height, 1)
            set_enabled(marker.bar, alive)
            set_enabled(marker.back, alive)
