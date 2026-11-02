# Copyright (c) 2026 Renaud Guillon
"""Stand-ins for the Babylon nodes and the model builder of the boss model tests (ENG-47).

`FakeNode` is a transform node (its position, rotation and scaling, its parent, whether it is
enabled, the meshes under it), and `ModelBuilder` replaces `enemy_mesh.build_enemy_model`: it runs
each drawing on real solid builders (`collect_parts`) and keeps what it drew by model name, with no
scene built. `patch_models` puts both in the modules given.
"""

from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

from game.view.enemies.enemy_mesh import collect_parts


class FakeVector:
    """A Babylon Vector3: three numbers and `set`."""

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        self.x = x
        self.y = y
        self.z = z

    def set(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z

    def xyz(self) -> list[float]:
        """Return the vector as a list."""
        return [self.x, self.y, self.z]


class FakeNode:
    """A transform node: its name, scene, parent, pose, whether it is enabled and its meshes."""

    def __init__(self, name: str, scene: Any) -> None:
        self.name = name
        self.scene = scene
        self.parent: Any = None
        self.position = FakeVector()
        self.rotation = FakeVector()
        self.scaling = FakeVector(1.0, 1.0, 1.0)
        self.metadata: Any = None
        self.enabled = True
        # The meshes under it (`child_meshes`): a model's root gets one hull mesh.
        self.meshes: list[Any] = []

    def getScene(self) -> Any:
        return self.scene

    def setEnabled(self, on: bool) -> None:
        self.enabled = on

    def isEnabled(self) -> bool:
        return self.enabled


def hull_mesh() -> Any:
    """Return a mesh in the enemies' hull material (one a boss's hit flash lights up)."""
    return SimpleNamespace(material=SimpleNamespace(name="enemy-hull"), useVertexColors=True)


class FakeModel:
    """A built model: its root node (with one hull mesh), and the `(lit, dt)` it was synced with."""

    def __init__(self, name: str, scene: Any) -> None:
        self.root = FakeNode(name, scene)
        self.root.meshes.append(hull_mesh())
        self.synced: list[tuple[Any, float]] = []

    def sync(self, lit: Any, dt: float) -> None:
        self.synced.append((lit, dt))


class ModelBuilder:
    """`build_enemy_model`: runs each drawing on real solid builders and records it by name."""

    def __init__(self) -> None:
        self.models: dict[str, FakeModel] = {}
        self.drawn: dict[str, dict[str, Any]] = {}

    def __call__(self, name: str, scene: Any, _neon: Any, draw: Any, _breath: Any = None) -> Any:
        self.drawn[name] = collect_parts(draw)
        model = FakeModel(name, scene)
        self.models[name] = model
        return model

    def faces(self, name: str, layer: str = "hull") -> int:
        """Return how many triangles the model `name` has in `layer`."""
        return len(getattr(self.drawn[name]["parts"], layer).geometry.indices) // 3


def patch_models(monkeypatch: pytest.MonkeyPatch, *modules: ModuleType) -> ModelBuilder:
    """Give the modules fake nodes (`new_transform_node`) and a recording model builder.

    Returns the builder.
    """
    builder = ModelBuilder()
    for module in modules:
        if hasattr(module, "new_transform_node"):
            monkeypatch.setattr(module, "new_transform_node", FakeNode)
        if hasattr(module, "build_enemy_model"):
            monkeypatch.setattr(module, "build_enemy_model", builder)
    return builder
