# Copyright (c) 2026 Renaud Guillon
"""The imposters in view (D-211, GFX-PROP-10).

One quad per placement, facing the camera, showing the atlas frame of its kind nearest its heading
(`imposters.py`).

One mesh per kind and frame, its quads as thin instances (moved and scaled, never turned: the frame
shows the turn; ENG-104).
"""

from render.babylon import float32_array, set_enabled
from render.scenery.imposters import frame_of, frame_uv, imposter_quad
from render.scenery.prop_field import MATRIX_FLOATS, mesh_of, same_placements

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from core.scenery.ground_boxes import PropPlacement

# __pragma__ ("noskip")


# The normals of a quad's 4 corners, all up.
UP_NORMALS = [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0]


def _mesh_key(kind: str, frame: int) -> str:
    return kind + "#" + str(frame)


def placement_matrix(buffer: Any, at: int, p: PropPlacement) -> None:
    """Write the world matrix of `p`'s quad at float `at` of `buffer`.

    The quad is scaled and moved, not turned.
    """
    s = p.scale
    values = [s, 0, 0, 0, 0, s, 0, 0, 0, 0, s, 0, p.x, p.y, p.z, 1]
    for i in range(MATRIX_FLOATS):
        buffer[at + i] = values[i]


class ImposterField:
    """The imposters of `kinds` (their atlas rows, in order), drawn with `material`."""

    def __init__(
        self,
        scene: Any,
        kinds: list[str],
        look: Any,
        tilt: float,
        material: Any,
    ) -> None:
        self._look = look
        self._meshes: dict[str, Any] = {}
        # The placements each mesh drew last (D-212: unchanged groups are not uploaded again).
        self._drawn: dict[str, list[PropPlacement]] = {}
        headings: int = look.headings
        for k in range(len(kinds)):
            for i in range(headings):
                quad = imposter_quad(look, tilt, frame_uv(look, len(kinds), k, i))
                mesh = mesh_of("imposter-" + _mesh_key(kinds[k], i), quad, material, scene)
                # Lit as the ground round it, not as a wall facing the camera: normals up.
                mesh.setVerticesData("normal", UP_NORMALS, False)
                # Always drawn, its bounds never fitted to its instances (PERF-26).
                mesh.alwaysSelectAsActiveMesh = True
                mesh.doNotSyncBoundingInfo = True
                self._meshes[_mesh_key(kinds[k], i)] = mesh

    @property
    def meshes(self) -> list[Any]:
        """Every quad mesh."""
        return list(self._meshes.values())

    def place(self, placements: list[PropPlacement]) -> None:
        """Draws one imposter per placement (of a kind it knows), and no others."""
        headings: int = self._look.headings
        groups: dict[str, list[PropPlacement]] = {}
        for p in placements:
            key = _mesh_key(p.kind, frame_of(p.rotation, headings))
            if key not in self._meshes:
                continue
            group = groups.get(key)
            if group:
                group.append(p)
            else:
                groups[key] = [p]
        for key, mesh in self._meshes.items():
            group = groups.get(key)
            if not group:
                if len(self._drawn.get(key, [])) > 0:
                    set_enabled(mesh, False)
                    self._drawn[key] = []
                continue
            if key in self._drawn and same_placements(self._drawn[key], group):
                continue
            count = len(group)
            buffer = float32_array(count * MATRIX_FLOATS)
            for j in range(count):
                placement_matrix(buffer, j * MATRIX_FLOATS, group[j])
            mesh.thinInstanceSetBuffer("matrix", buffer, MATRIX_FLOATS, False)
            set_enabled(mesh, True)
            self._drawn[key] = group
