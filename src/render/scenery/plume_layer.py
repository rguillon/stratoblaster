"""Smoke and steam columns rising from props (phase 10, P10-R08): the quads of the puffs and the
meshes that draw them. The material of each kind lifts, grows and fades the puffs frame by frame.

Ported from `render/scenery/plume-layer.ts`.
"""

from org.transcrypt.stubs.browser import __pragma__

from config.plumes import PLUME_KINDS

# `%` keeps JavaScript's rounding (the TypeScript phase of each column uses it).
__pragma__("jsmod")
from render.babylon import apply_vertex_data, new_mesh, set_enabled, vertex_data_of  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any, Protocol  # noqa: E402

from config.plumes import PlumeKind  # noqa: E402
from core.scenery.atmosphere import Atmosphere  # noqa: E402
from render.scenery.scenery_look import PropPlume  # noqa: E402

Rgb = tuple[float, float, float]


class PlumeMaterial(Protocol):
    """The material of one kind of plume, driven frame by frame."""

    material: Any

    def set(self, frame: "PlumeFrame") -> None: ...


PlumeMaterialFactory = Callable[[Any, PlumeKind], PlumeMaterial]
__pragma__("noskip")


class PlumeFog:
    """The haze the plumes fade into."""

    def __init__(self, color: Rgb, start: float, end: float) -> None:
        self.color = color
        self.start = start
        self.end = end


class PlumeFrame:
    """What the plumes show on one frame."""

    def __init__(
        self,
        time: float,
        camera_position: Any,
        right: Any,
        up: Any,
        light: Rgb,
        fog: PlumeFog,
    ) -> None:
        self.time = time
        self.camera_position = camera_position
        """The camera's right and up directions, to face the puffs to it."""
        self.right = right
        self.up = up
        """How lit the puffs are (the scene's light), and the haze they fade into."""
        self.light = light
        self.fog = fog


class PlumeLightLook:
    """Share of the sun's light the puffs take, and the most light they show."""

    sun = 0.35
    most = 1.2


PLUME_LIGHT = PlumeLightLook

# Draw order among the see-through meshes of the ground: after the water.
PLUME_ALPHA_INDEX = 2

# One puff's quad: its corners, as `position` (x, y) around the puff's centre.
CORNERS = [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)]


class PlumeGeometry:
    """The geometry of a prop's plumes of one kind: positions, `puff` attributes and indices."""

    def __init__(
        self,
        positions: list[float],
        puffs: list[float],
        scales: list[float],
        indices: list[int],
    ) -> None:
        self.positions = positions
        """Per vertex: where its column starts (model space) and its puff's phase (0..1)."""
        self.puffs = puffs
        """Per vertex: its column's scale."""
        self.scales = scales
        self.indices = indices


def plume_geometry(plumes: list[PropPlume], kind: PlumeKind) -> PlumeGeometry:
    """The quads of `plumes` (phase 10): `kind.puffs` per column, each puff a quad around the
    column's foot whose `phase` spreads the puffs evenly up the column; the material lifts, grows
    and fades them."""
    positions: list[float] = []
    puffs: list[float] = []
    scales: list[float] = []
    indices: list[int] = []
    for column in range(len(plumes)):
        plume = plumes[column]
        for i in range(int(kind.puffs)):
            # Columns start out of step, so neighbouring chimneys do not puff together.
            phase = (i + ((column * 0.37) % 1)) / kind.puffs
            v = len(positions) // 3
            for x, y in CORNERS:
                positions.extend([x, y, 0])
                puffs.extend(plume.at)
                puffs.append(phase)
                scales.append(plume.scale if plume.scale is not None else 1)
            indices.extend([v, v + 1, v + 2, v, v + 2, v + 3])
    return PlumeGeometry(positions, puffs, scales, indices)


def plume_light(atmosphere: Atmosphere) -> Rgb:
    """How lit a plume is under `atmosphere`: its ambient light plus some of the sun's."""
    ambient = atmosphere.ambient
    sun = atmosphere.sun

    def lit(sky: float, color: float) -> float:
        return min(
            PLUME_LIGHT.most,
            sky * ambient.intensity + color * PLUME_LIGHT.sun * sun.intensity,
        )

    return (
        lit(ambient.sky[0], sun.color[0]),
        lit(ambient.sky[1], sun.color[1]),
        lit(ambient.sky[2], sun.color[2]),
    )


def build_plume_meshes(
    scene: Any,
    name: str,
    plumes: Any,
    material: Callable[[str], Any],
    kinds: Any = None,
) -> list[Any]:
    """The plume meshes of a prop kind (phase 10, P10-R08): one per plume kind it has, drawn with
    the prop's own thin instances (so every placed prop smokes), always selected (the puffs rise
    far above the prop's bounds), see-through and never writing depth."""
    table = PLUME_KINDS if kinds is None else kinds
    ids: list[str] = []
    for p in plumes:
        if p.kind not in ids:
            ids.append(p.kind)
    meshes: list[Any] = []
    for id in ids:
        kind = table.get(id)
        mat = material(id)
        if not kind or not mat:
            continue
        geometry = plume_geometry([p for p in plumes if p.kind == id], kind)
        mesh = new_mesh(name + "-plume-" + id, scene)
        data = vertex_data_of(geometry.positions, geometry.indices)
        apply_vertex_data(data, mesh)
        mesh.setVerticesData("puff", geometry.puffs, False, 4)
        mesh.setVerticesData("puffScale", geometry.scales, False, 1)
        mesh.material = mat
        mesh.isPickable = False
        mesh.alwaysSelectAsActiveMesh = True
        mesh.alphaIndex = PLUME_ALPHA_INDEX
        set_enabled(mesh, False)
        meshes.append(mesh)
    return meshes
