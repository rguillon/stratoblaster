"""Stand-ins for the Babylon objects the tests of `render/` need. Babylon runs only in the browser,
so `render.babylon` returns None under CPython. `patch_babylon` replaces, in one module, every
function it imported from `render.babylon` with a Python version of it (the ones listed in
`BABYLON_FAKES`), and leaves the others alone."""

from __future__ import annotations

import math
from typing import Any

import pytest

from render import babylon

# Babylon's `Number.MAX_VALUE`: the default draw order of a mesh.
NUMBER_MAX_VALUE = 1.7976931348623157e308


class FakeVector:
    """A Babylon Vector3: the arithmetic the render code uses, on plain numbers."""

    def __init__(self, x: float = 0, y: float = 0, z: float = 0) -> None:
        self.x = x
        self.y = y
        self.z = z

    def set(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z

    def _of(self, x: float, y: float, z: float) -> FakeVector:
        return FakeVector(x, y, z)

    def add(self, other: FakeVector) -> FakeVector:
        return self._of(self.x + other.x, self.y + other.y, self.z + other.z)

    def subtract(self, other: FakeVector) -> FakeVector:
        return self._of(self.x - other.x, self.y - other.y, self.z - other.z)

    def scale(self, k: float) -> FakeVector:
        return self._of(self.x * k, self.y * k, self.z * k)

    def length(self) -> float:
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalizeToNew(self) -> FakeVector:  # noqa: N802 (Babylon's name)
        if self.length() == 0:
            return self._of(0, 0, 0)
        return self.scale(1 / self.length())

    def normalize(self) -> FakeVector:
        # Babylon leaves a zero vector as it is.
        if self.length() > 0:
            scaled = self.normalizeToNew()
            self.set(scaled.x, scaled.y, scaled.z)
        return self


class FakeNode:
    """A transform node (or a mesh, with `is_mesh`): the fields the render code reads and writes."""

    def __init__(self, name: str = "", unique_id: float = 0, is_mesh: bool = False) -> None:
        self.name = name
        self.uniqueId = unique_id
        self.is_mesh = is_mesh
        self._parent: FakeNode | None = None
        self.children: list[FakeNode] = []
        self.position = FakeVector()
        self.rotation = FakeVector()
        self.absoluteScaling = FakeVector(1, 1, 1)
        self.metadata: Any = None
        self.material: Any = None
        self.hasVertexAlpha = False
        self.renderingGroupId = 0
        self.alphaIndex = NUMBER_MAX_VALUE
        self.renderOutline = False
        self.outlineColor: Any = None
        self.outlineWidth = 0.0
        self.subMeshes: list[Any] = []
        self.scene: FakeScene | None = None
        self.enabled = True
        self.disposed = False

    @property
    def parent(self) -> FakeNode | None:
        return self._parent

    @parent.setter
    def parent(self, value: FakeNode | None) -> None:
        # Like Babylon: a node is a child of its parent, and only of that one.
        if self._parent is not None:
            self._parent.children.remove(self)
        self._parent = value
        if value is not None:
            value.children.append(self)

    def setEnabled(self, on: bool) -> None:  # noqa: N802 (Babylon's name)
        self.enabled = on

    def isEnabled(self) -> bool:  # noqa: N802
        return self.enabled

    def dispose(self) -> None:
        self.disposed = True

    def getScene(self) -> FakeScene | None:  # noqa: N802
        return self.scene

    def computeWorldMatrix(self, force: bool) -> None:  # noqa: N802
        return None


class FakeScene:
    """A scene: nodes are numbered from one counter, as Babylon numbers them."""

    def __init__(self) -> None:
        self.meshes: list[FakeNode] = []
        self.transformNodes: list[FakeNode] = []
        self._counter = 0

    def getUniqueId(self) -> float:  # noqa: N802
        return self._counter

    def next_id(self) -> float:
        self._counter += 1
        return self._counter

    def add_node(self, name: str = "", is_mesh: bool = False) -> FakeNode:
        node = FakeNode(name, self.next_id(), is_mesh)
        node.scene = self
        (self.meshes if is_mesh else self.transformNodes).append(node)
        return node


class FakeTypedArray(list):  # type: ignore[type-arg]
    """A typed array: zero-filled, and `set(values, offset)` writes a run of values."""

    def __init__(self, length: int) -> None:
        super().__init__([0] * length)

    def set(self, values: Any, offset: int = 0) -> None:
        for i, value in enumerate(values):
            self[offset + i] = value


class FakeWeakMap:
    """A `WeakMap` by identity (a dict is enough for the tests)."""

    def __init__(self) -> None:
        self._items: dict[int, tuple[Any, Any]] = {}

    def get(self, key: Any) -> Any:
        item = self._items.get(id(key))
        return None if item is None else item[1]

    def set(self, key: Any, value: Any) -> None:
        self._items[id(key)] = (key, value)


def _fake_weak_map_get(weak_map: FakeWeakMap, key: Any) -> Any:
    return weak_map.get(key)


def _fake_weak_map_set(weak_map: FakeWeakMap, key: Any, value: Any) -> None:
    weak_map.set(key, value)


def _fake_child_meshes(node: FakeNode, direct_only: bool) -> list[FakeNode]:
    return [child for child in _walk(node, direct_only) if child.is_mesh]


def _fake_descendants(node: FakeNode, direct_only: bool) -> list[FakeNode]:
    return _walk(node, direct_only)


def _walk(node: FakeNode, direct_only: bool) -> list[FakeNode]:
    result: list[FakeNode] = []
    for child in node.children:
        result.append(child)
        if not direct_only:
            result.extend(_walk(child, False))
    return result


def _fake_new_transform_node(label: str, scene: FakeScene) -> FakeNode:
    return scene.add_node(label)


def _fake_new_mesh(label: str, scene: FakeScene) -> FakeNode:
    return scene.add_node(label, is_mesh=True)


def _fake_object_with_field(old: Any, key: str, value: Any) -> dict[str, Any]:
    copy = dict(old) if isinstance(old, dict) else {}
    copy[key] = value
    return copy


def _fake_metadata_field(metadata: Any, key: str) -> Any:
    if isinstance(metadata, dict) and key in metadata:
        return metadata[key]
    return None


def _fake_is_instance_of(value: Any, class_name: str) -> bool:
    return bool(getattr(value, "is_mesh", False)) if class_name == "Mesh" else False


def _fake_scene_meshes(scene: FakeScene) -> list[FakeNode]:
    return scene.meshes


def _fake_scene_transform_nodes(scene: FakeScene) -> list[FakeNode]:
    return scene.transformNodes


def _fake_scene_unique_id(scene: FakeScene) -> float:
    return float(scene.getUniqueId())


def _fake_unique_id(node: FakeNode) -> float:
    return node.uniqueId


def _fake_node_name(node: FakeNode) -> str:
    return node.name


def _fake_dispose_node(node: FakeNode) -> None:
    node.dispose()


def _fake_set_enabled(node: FakeNode, on: bool) -> None:
    node.setEnabled(on)


def _fake_color3(r: float, g: float, b: float) -> FakeSettable:
    return FakeSettable(r, g, b)


def _fake_constant(key: str) -> str:
    return key


class FakeSettable:
    """A colour Babylon fills in with `set(r, g, b[, a])`, and reads back as `values`."""

    def __init__(self, *values: float) -> None:
        self.values: tuple[float, ...] = values

    def set(self, *values: float) -> None:
        self.values = values

    def scale(self, factor: float) -> FakeSettable:
        return FakeSettable(*(v * factor for v in self.values))


class FakeLight:
    """A light: where it points and how it lights."""

    def __init__(self, label: str, direction: Any = None) -> None:
        self.name = label
        self.direction = direction
        self.diffuse = FakeSettable(1, 1, 1)
        self.specular = FakeSettable(1, 1, 1)
        self.groundColor = FakeSettable(0, 0, 0)  # noqa: N815 (Babylon's name)
        self.intensity = 1.0


def _fake_vector3(x: float, y: float, z: float) -> FakeVector:
    return FakeVector(x, y, z)


def _fake_cross(a: FakeVector, b: FakeVector) -> FakeVector:
    return FakeVector(a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x)


def _fake_dot(a: FakeVector, b: FakeVector) -> float:
    return a.x * b.x + a.y * b.y + a.z * b.z


def _fake_color4(r: float, g: float, b: float, a: float) -> FakeSettable:
    return FakeSettable(r, g, b, a)


def _fake_light(label: str, direction: Any, scene: Any) -> FakeLight:
    return FakeLight(label, direction)


BABYLON_FAKES: dict[str, Any] = {
    "float32_array": FakeTypedArray,
    "uint32_array": FakeTypedArray,
    "uint8_array": FakeTypedArray,
    "color3_black": lambda: FakeSettable(0, 0, 0),
    "vector3_cross": _fake_cross,
    "vector3_dot": _fake_dot,
    "color4": _fake_color4,
    "new_directional_light": _fake_light,
    "new_hemispheric_light": _fake_light,
    "fog_mode_linear": lambda: 2,
    "vector3": _fake_vector3,
    "vector3_down": lambda: FakeVector(0, -1, 0),
    "vector3_up": lambda: FakeVector(0, 1, 0),
    "vector3_zero": lambda: FakeVector(0, 0, 0),
    "child_meshes": _fake_child_meshes,
    "color3": _fake_color3,
    "babylon_constant": _fake_constant,
    "descendants": _fake_descendants,
    "dispose_node": _fake_dispose_node,
    "is_instance_of": _fake_is_instance_of,
    "metadata_field": _fake_metadata_field,
    "new_mesh": _fake_new_mesh,
    "new_transform_node": _fake_new_transform_node,
    "new_weak_map": FakeWeakMap,
    "node_name": _fake_node_name,
    "number_max_value": lambda: NUMBER_MAX_VALUE,
    "object_with_field": _fake_object_with_field,
    "scene_meshes": _fake_scene_meshes,
    "scene_transform_nodes": _fake_scene_transform_nodes,
    "scene_unique_id": _fake_scene_unique_id,
    "set_enabled": _fake_set_enabled,
    "unique_id": _fake_unique_id,
    "weak_map_get": _fake_weak_map_get,
    "weak_map_set": _fake_weak_map_set,
}


def patch_babylon(monkeypatch: pytest.MonkeyPatch, module: Any) -> None:
    """Replaces, in `module`, the `render.babylon` functions that have a fake here."""
    for name, fake in BABYLON_FAKES.items():
        if getattr(module, name, None) is getattr(babylon, name, object()):
            monkeypatch.setattr(module, name, fake)
