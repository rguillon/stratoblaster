# Copyright (c) 2026 Renaud Guillon
"""Every reactor flame of a scene, drawn together (D-428, ENG-104, ENG-106).

A flame was four meshes (two cones, two or three puffs), a draw call each in every pass: a third of
the meshes of a busy playfield. Here a scene's flames share a few meshes drawn as thin instances:
one for the cones of each number of sides, one for each shape of puff. A flame is only a node at
its reactor and the numbers of its look; each frame, just before the scene works out what it
draws, the layer writes one matrix and one colour per cone and per puff of every flame whose node
is shown. The shapes, colours and motion are those of `reactor_flame.py`.
"""

from org.transcrypt.stubs.browser import __pragma__

from render.babylon import (
    babylon_constant,
    color3,
    color3_black,
    create_cylinder,
    create_polyhedron,
    new_standard_material,
    new_weak_map,
    weak_map_get,
    weak_map_set,
)
from render.glow_marks import mark_glows_as_drawn

# isort: split
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")

# A puff is stretched along the exhaust.
PUFF_STRETCH = 1.6
# Fewest instances a batch's buffers hold.
LEAST_CAPACITY = 16

_LAYERS: Any = new_weak_map()


def _floats(length: int) -> Any:
    """Return a zero-filled `Float32Array` of `length` numbers."""
    __pragma__("js", "{}", "return new Float32Array(length);")
    return [0.0 for _ in range(length)]


def _cone_options(sides: int) -> Any:
    """Options of `CreateCylinder` for a cone one unit long and wide at its base, without caps."""
    options: Any = None
    __pragma__(
        "js",
        "{}",
        "options = {height: 1, diameterTop: 0, diameterBottom: 1, tessellation: sides, "
        "cap: BABYLON.Mesh.NO_CAP};",
    )
    return options


def _polyhedron_options(kind: int) -> Any:
    """Options of `CreatePolyhedron`: `{ type, size: 1 }`."""
    options: Any = None
    __pragma__("js", "{}", "options = {type: kind, size: 1};")
    return options


def _world_to_ref(node: Any, target: Any) -> None:
    """Write `node`'s world matrix, worked out afresh, into `target` (no new object)."""
    __pragma__("js", "{}", "target.copyFrom(node.computeWorldMatrix(true));")


def _relative_to_ref(node: Any, inverse: Any, target: Any) -> None:
    """Write `node`'s world matrix, seen from the space `inverse` undoes, into `target`."""
    __pragma__("js", "{}", "node.computeWorldMatrix(true).multiplyToRef(inverse, target);")


def _new_matrix() -> Any:
    __pragma__("js", "{}", "return new BABYLON.Matrix();")
    return None


def _frame_of(scene: Any) -> int:
    frame: int = scene.getFrameId()
    return frame


class Batch:
    """One mesh drawn once per instance: its matrices and colours, in buffers that only grow."""

    def __init__(self, mesh: Any) -> None:
        self.mesh = mesh
        self.count = 0
        self.capacity = 0
        self.matrices = _floats(0)
        self.colors = _floats(0)
        self._grown = False

    def add(
        self, world: Any, scale: list[float], along: float, color: list[float], alpha: float
    ) -> None:
        """Add an instance: `scale`d, then moved `along` its Z, then placed by `world`.

        `world` holds the 16 numbers of a matrix; the instance is tinted `color` at `alpha`.
        """
        if self.count == self.capacity:
            self._grow()
        m = self.matrices
        k = self.count * 16
        sx = scale[0]
        sy = scale[1]
        sz = scale[2]
        m[k] = sx * world[0]
        m[k + 1] = sx * world[1]
        m[k + 2] = sx * world[2]
        m[k + 3] = 0
        m[k + 4] = sy * world[4]
        m[k + 5] = sy * world[5]
        m[k + 6] = sy * world[6]
        m[k + 7] = 0
        m[k + 8] = sz * world[8]
        m[k + 9] = sz * world[9]
        m[k + 10] = sz * world[10]
        m[k + 11] = 0
        m[k + 12] = along * world[8] + world[12]
        m[k + 13] = along * world[9] + world[13]
        m[k + 14] = along * world[10] + world[14]
        m[k + 15] = 1
        c = self.colors
        j = self.count * 4
        c[j] = color[0]
        c[j + 1] = color[1]
        c[j + 2] = color[2]
        c[j + 3] = alpha
        self.count += 1

    def _grow(self) -> None:
        capacity = self.capacity * 2 if self.capacity > 0 else LEAST_CAPACITY
        matrices = _floats(capacity * 16)
        colors = _floats(capacity * 4)
        for i in range(self.count * 16):
            matrices[i] = self.matrices[i]
        for i in range(self.count * 4):
            colors[i] = self.colors[i]
        self.matrices = matrices
        self.colors = colors
        self.capacity = capacity
        self._grown = True

    def upload(self) -> None:
        """Draw the instances added since the last upload, and start again from none."""
        count = self.count
        self.count = 0
        mesh = self.mesh
        mesh.setEnabled(count > 0)
        if count == 0:
            return
        if self._grown:
            self._grown = False
            mesh.thinInstanceSetBuffer("matrix", self.matrices, 16, False)
            mesh.thinInstanceSetBuffer("color", self.colors, 4, False)
            mesh.thinInstanceCount = count
            return
        # The count first: Babylon uploads only the first `thinInstanceCount` instances.
        mesh.thinInstanceCount = count
        mesh.thinInstanceBufferUpdated("matrix")
        mesh.thinInstanceBufferUpdated("color")


class FlameLayer:
    """The flames of one scene and the few meshes that draw them (see the module doc)."""

    def __init__(self, scene: Any) -> None:
        self._scene = scene
        self._material: Any = None
        # The batches by mesh name, and in a list to walk them without a dict's keys.
        self._by_name: dict[str, Batch] = {}
        self._batches: list[Batch] = []
        self._flames: list[Any] = []
        self._frame = -1
        # The glow layers and batches already told of each other (`_own_materials`).
        self._told_layers = 0
        self._told_batches = 0
        self._inverse = _new_matrix()
        self._world = _new_matrix()

        def draw(_a: Any = None, _b: Any = None) -> None:
            self.draw()

        scene.onBeforeActiveMeshesEvaluationObservable.add(draw)

    def cones(self, sides: int) -> Batch:
        """Return the batch of the cones of `sides` sides: tip at -Z, base at the origin."""
        name = "flame-cones-" + str(sides)
        batch = self._by_name.get(name)
        if batch is None:
            mesh = create_cylinder(name, _cone_options(sides), self._scene)
            # The cylinder grows along +Y: -90° round X points its tip to -Z, base at the origin.
            mesh.rotation.x = -3.141592653589793 / 2
            mesh.position.z = -0.5
            mesh.bakeCurrentTransformIntoVertices()
            batch = self._batch(name, mesh)
        return batch

    def puffs(self, kind: int) -> Batch:
        """Return the batch of the puffs of polyhedron `kind` (`CreatePolyhedron`'s types)."""
        name = "flame-puffs-" + str(kind)
        batch = self._by_name.get(name)
        if batch is None:
            mesh = create_polyhedron(name, _polyhedron_options(kind), self._scene)
            batch = self._batch(name, mesh)
        return batch

    def _batch(self, name: str, mesh: Any) -> Batch:
        mesh.material = self._flame_material()
        # Each instance has its own opacity: blended, and drawn with its own colours in a glow.
        mesh.hasVertexAlpha = True
        mesh.isPickable = False
        # Instances stand anywhere: never culled, bounds never fitted.
        mesh.alwaysSelectAsActiveMesh = True
        mesh.doNotSyncBoundingInfo = True
        mark_glows_as_drawn(mesh)
        mesh.setEnabled(False)
        batch = Batch(mesh)
        self._by_name[name] = batch
        self._batches.append(batch)
        return batch

    def _flame_material(self) -> Any:
        if self._material is None:
            material = new_standard_material("flames", self._scene)
            material.emissiveColor = color3(1, 1, 1)
            material.diffuseColor = color3_black()
            material.specularColor = color3_black()
            material.disableLighting = True
            material.backFaceCulling = False
            material.alphaMode = babylon_constant("ALPHA_COMBINE")
            # Below 1, so the material goes through the blended pass.
            material.alpha = 0.999
            material.disableDepthWrite = True
            self._material = material
        return self._material

    def add(self, flame: Any) -> None:
        """Draw `flame` from now on, whenever its node is shown, until its node is disposed."""
        self._flames.append(flame)

    def draw(self) -> None:
        """Write the instances of every flame shown; once per frame, before the scene's meshes."""
        frame = _frame_of(self._scene)
        if frame == self._frame:
            return
        self._frame = frame
        self._own_materials()
        batches = self._batches
        if len(batches) == 0:
            return
        # The instances are placed in the meshes' own space (they hang where they were adopted).
        _world_to_ref(batches[0].mesh, self._inverse)
        self._inverse.invert()
        flames = self._flames
        kept = 0
        for i in range(len(flames)):
            flame = flames[i]
            node = flame.node
            if node.isDisposed():
                continue
            flames[kept] = flame
            kept += 1
            if node.isEnabled():
                _relative_to_ref(node, self._inverse, self._world)
                flame.write(self._world.m)
        while len(flames) > kept:
            flames.pop()
        for i in range(len(batches)):
            batches[i].upload()

    def _own_materials(self) -> None:
        """Have each glow layer of the scene draw the flames as they are, each in its colour.

        Layers and batches only add up: each new pair is told once.
        """
        layers = self._scene.effectLayers
        count = 0 if layers == None else len(layers)
        batches = self._batches
        if count == self._told_layers and len(batches) == self._told_batches:
            return
        for i in range(count):
            layer = layers[i]
            if layer.referenceMeshToUseItsOwnMaterial == None:
                continue
            for k in range(len(batches)):
                if i >= self._told_layers or k >= self._told_batches:
                    layer.referenceMeshToUseItsOwnMaterial(batches[k].mesh)
        self._told_layers = count
        self._told_batches = len(batches)


def flame_layer(scene: Any) -> FlameLayer:
    """Return the flame layer of `scene`, made on first use."""
    layer: FlameLayer | None = weak_map_get(_LAYERS, scene)
    if layer is None:
        layer = FlameLayer(scene)
        weak_map_set(_LAYERS, scene, layer)
    return layer
