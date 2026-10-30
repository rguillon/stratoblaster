"""Draws enemies on a top-down playfield (ported from `render/enemy-layer.ts`).

The playfield is the XY plane at Z = 0, Y up, seen from -Z (see `game_view.ShotFrame`): one
model per enemy, at its position, its nose along its heading. Models are kept per model key and
reused when enemies come and go (ENG-19).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from render.babylon import child_meshes, dispose_node, new_transform_node, node_name, set_enabled

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any  # noqa: E402

EnemyModelFactory = Callable[[Any], Any]
__pragma__("noskip")


class _Slot:
    """A model on screen (or kept for reuse): its pivot, the model, and its kind."""

    def __init__(self, pivot: Any, model: Any, key: str) -> None:
        self.pivot = pivot
        self.model = model
        self.key = key


def _contains(items: list[Any], item: Any) -> bool:
    """Membership by identity (enemies are objects): `in` on a list compiles to `indexOf`."""
    return item in items


class EnemyLayer:
    """One model per enemy, shown at its position with its nose along its heading."""

    def __init__(self, scene: Any, models: dict[str, Any]) -> None:
        self._scene = scene
        self._models = models
        # The enemies drawn, with their slots (two parallel lists: enemies are objects).
        self._slot_enemies: list[Any] = []
        self._slot_values: list[_Slot] = []
        # Slots kept for reuse, by model key.
        self._free: dict[str, list[_Slot]] = {}
        self._created = 0
        # The kinds with a model built.
        self._built: list[str] = []

    @property
    def model_count(self) -> int:
        """Number of models built so far (shown or kept for reuse)."""
        return self._created

    @property
    def count(self) -> int:
        """Number of enemies drawn."""
        return len(self._slot_values)

    def sync(self, enemies: list[Any], dt_seconds: float) -> None:
        """Shows `enemies` (and hides the models of the others)."""
        enemies_now = list(self._slot_enemies)
        slots_now = list(self._slot_values)
        for i in range(len(enemies_now)):
            if not _contains(enemies, enemies_now[i]):
                self._release(enemies_now[i], slots_now[i])
        for enemy in enemies:
            slot = self._find_slot(enemy)
            if slot is None:
                slot = self._take(enemy)
            slot.pivot.position.set(enemy.x, enemy.y, 0)
            slot.pivot.rotation.z = -enemy.heading
            slot.model.sync(enemy, dt_seconds)

    def prepare_next(self) -> list[Any]:
        """Builds one hidden model of the next kind not built yet, kept for reuse (P13-R04), and
        returns its meshes (e.g. to compile their shaders), or none once every kind has one.

        Called once per frame, it gets every kind ready before its first appearance without
        freezing a frame.
        """
        key = None
        for k in self._models.keys():  # noqa: SIM118 (Transcrypt: iterate keys() explicitly)
            if not _contains(self._built, k):
                key = k
                break
        if key is None:
            return []
        slot = self._build(key)
        set_enabled(slot.pivot, False)
        self._keep(key, slot)
        return child_meshes(slot.pivot, False)

    def clear(self) -> None:
        """Hides every model."""
        enemies_now = list(self._slot_enemies)
        slots_now = list(self._slot_values)
        for i in range(len(enemies_now)):
            self._release(enemies_now[i], slots_now[i])

    def _find_slot(self, enemy: Any) -> Any:
        for i in range(len(self._slot_enemies)):
            if self._slot_enemies[i] is enemy:
                return self._slot_values[i]
        return None

    def _take(self, enemy: Any) -> _Slot:
        free = self._free.get(enemy.model)
        slot = free.pop() if free and len(free) > 0 else self._build(enemy.model)
        set_enabled(slot.pivot, True)
        self._slot_enemies.append(enemy)
        self._slot_values.append(slot)
        return slot

    def _release(self, enemy: Any, slot: _Slot) -> None:
        set_enabled(slot.pivot, False)
        for i in range(len(self._slot_enemies)):
            if self._slot_enemies[i] is enemy:
                self._slot_enemies.pop(i)
                self._slot_values.pop(i)
                break
        self._keep(slot.key, slot)

    def _keep(self, key: str, slot: _Slot) -> None:
        free = self._free.get(key)
        if not free:
            free = []
            self._free[key] = free
        free.append(slot)

    def _build(self, key: str) -> _Slot:
        factory = self._models.get(key)
        if not factory:
            raise ValueError("No model for enemy " + key)
        pivot = new_transform_node("enemy-" + key + "-" + str(self._created), self._scene)
        self._created += 1
        # Models face +Z with +Y up: a holder turns the nose to +Y and the top to -Z (the camera).
        holder = new_transform_node(node_name(pivot) + "-holder", self._scene)
        holder.parent = pivot
        holder.rotation.x = -math.pi / 2
        model = factory(self._scene)
        model.root.parent = holder
        if not _contains(self._built, key):
            self._built.append(key)
        return _Slot(pivot, model, key)

    def dispose(self) -> None:
        for slot in self._slot_values:
            dispose_node(slot.pivot)
        for key in self._free.keys():  # noqa: SIM118 (Transcrypt: iterate keys() explicitly)
            for slot in self._free[key]:
                dispose_node(slot.pivot)
        self._slot_enemies = []
        self._slot_values = []
        self._free = {}
