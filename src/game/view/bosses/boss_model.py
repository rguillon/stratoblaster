"""Builds the model of a boss (P07-R05) from its drawing, ported from `bosses/boss-model.ts`: its
core body, its parts on their own nodes (each flashing white when hit, smoking under half health,
replaced by a burnt stump once destroyed), its turrets and limbs, and an optional ring turning with
the boss's spin.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.entities.boss import Boss  # noqa: E402
from game.config.boss_look import BOSS_LOOK  # noqa: E402
from game.view.bosses.boss_damage import build_smoke, build_stump, effect_materials  # noqa: E402
from game.view.bosses.boss_limbs import (  # noqa: E402
    ORIGIN,
    BossLimbs,
    JointFrames,
    boss_point,
    hang,
)
from game.view.enemies.enemy_materials import BODY_MATERIALS  # noqa: E402
from game.view.enemies.enemy_mesh import BuiltEnemyModel, build_enemy_model  # noqa: E402
from game.view.enemies.living_motion import new_breath  # noqa: E402
from game.view.enemies.organic_parts import opt  # noqa: E402
from render.babylon import (  # noqa: E402
    child_meshes,
    new_transform_node,
    node_name,
    set_enabled,
)

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Rgb = Any
type Vec3 = list[Any]
__pragma__("noskip")

# The charge lights of the stumps spark on their own: a stand-in enemy for their sync.
STUMP_STATE = {"charge": 0}


def _field(obj: Any, key: str) -> Any:
    """`obj?.[key]`: the field `key` of `obj`, or None when `obj` or the field is missing."""
    if obj == None or key not in obj:  # noqa: E711
        return None
    return obj[key]


def _point_of(spot: Any) -> list[Any]:
    """`bossPoint(...spot)`: a playfield point `[x, y]` or `[x, y, height]`, in model space."""
    if len(spot) > 2:  # noqa: PLR2004
        return boss_point(spot[0], spot[1], spot[2])
    return boss_point(spot[0], spot[1])


class TurretView:
    """A piece's turret: its model, on a node turning around its pivot."""

    def __init__(self, pivot: Any, model: Any) -> None:
        self.pivot = pivot
        self.model = model


def _part_builder(draw: Any, at: list[Any]) -> Any:
    """The builder of a part drawn around its centre `at`."""

    def build(p: Any) -> None:
        draw(p, at)

    return build


def build_turret(
    design: Any,
    piece: str,
    drawing: Any,
    holder: Any,
    neon: Rgb,
    breath: Any,
) -> TurretView | None:
    """The turret of `piece` on `holder` (its piece's model), if the boss's drawing has one."""
    turrets = _field(drawing, "turrets")
    draw = _field(turrets, piece)
    gun = _field(design.guns, piece)
    turret = _field(gun, "turret")
    if draw == None and turret == None:  # noqa: E711
        return None
    if draw == None or turret == None:  # noqa: E711
        raise ValueError('Boss "' + design.id + '": "' + piece + '" needs a turret and its drawing')
    scene = holder.getScene()
    at = _point_of(turret)
    pivot = new_transform_node(design.id + "-" + piece + "-pivot", scene)
    pivot.position.set(at[0], at[1], at[2])
    pivot.parent = holder
    model = build_enemy_model(
        design.id + "-" + piece + "-turret",
        scene,
        neon,
        _part_builder(draw, at),
        breath,
    )
    model.root.position.set(-at[0], -at[1], -at[2])
    model.root.parent = pivot
    return TurretView(pivot, model)


def show_turret(view: Any, turret: Any, lit: Any, dt: float) -> None:
    """Shows a turret turned by its aim (+Y turns the nose, down the screen, clockwise)."""
    if view == None:  # noqa: E711
        return
    view.pivot.rotation.y = 0 if turret == None else turret.aim  # noqa: E711
    view.model.sync(lit, dt)


class FlashGroup:
    """A piece of the model shown for a part, or the core, with its hit flash."""

    def __init__(self, model: Any, flash: Any) -> None:
        self.model = model
        self._flash = flash
        self._hulls: list[Any] = []
        for mesh in child_meshes(model.root, False):
            material = mesh.material
            name = node_name(material) if material != None else ""  # noqa: E711
            if name in BODY_MATERIALS:
                self._hulls.append([mesh, material])

    def show(self, since_hit: float) -> None:
        """Flashes white for a moment after a hit (P07-R01)."""
        on = since_hit < BOSS_LOOK.flash.seconds
        for hull in self._hulls:
            hull[0].material = self._flash if on else hull[1]
            hull[0].useVertexColors = not on


class PartView:
    """The pieces of one part: its model (and turret), its smoke, its stump."""

    def __init__(self, group: Any, turret: Any, smoke: Any, stump: Any) -> None:
        self.group = group
        self.turret = turret
        self.smoke = smoke
        self.stump = stump


def build_boss_model(design: Any, scene: Any, neon: Rgb, drawing: Any) -> BuiltEnemyModel:
    """Builds the model of a boss (P07-R05) from `drawing`, in the colour `neon`: its core body, its
    parts on their own nodes (each flashing white when hit, smoking under half health, replaced by
    a burnt stump once destroyed), and an optional ring turning with the boss's spin."""
    name = design.id
    flash = effect_materials(scene)["flash"]
    root = new_transform_node(name, scene)
    # P16-R07: its core, parts and limbs breathe as one creature.
    look = {"flash": flash, "neon": neon, "breath": new_breath()}
    body = build_body(design, drawing, root, look)
    core = body["core"]
    core_turret = body["core_turret"]
    ring_node = body["ring_node"]
    ring = body["ring"]
    joints = JointFrames(design, root)
    parts: list[PartView] = []
    for spec in design.stats.parts:
        holder = joints.frame(
            opt(spec, "joint", None),
            ring_node if opt(spec, "orbits", False) else root,
        )
        parts.append(build_part(design, spec, drawing, holder, look))
    limbs = BossLimbs(
        design,
        _field(drawing, "limbs"),
        joints,
        _limb_builder(design, scene, neon, look),
    )
    lit: Any = {"charge": 0}

    def sync(boss: Any, dt: float) -> None:
        # After a part is destroyed, its lights strobe while it holds its fire (P07-R04).
        lit["charge"] = strobe(boss)
        enemy = lit
        core.model.sync(enemy, dt)
        if ring != None:  # noqa: E711
            ring.model.sync(enemy, dt)
        is_boss = isinstance(boss, Boss)
        limbs.show(boss if is_boss else None, enemy, dt)
        if not is_boss:
            show_turret(core_turret, None, enemy, dt)
            return
        show_turret(core_turret, boss.core.turret, enemy, dt)
        # It rolls into its sideways moves (phase 7 review). Screen right is the model's -X (its
        # nose points down the screen): +Z rolls -X down.
        root.rotation.z = boss.roll
        ring_node.rotation.y = boss.spin
        core.show(boss.core.since_hit)
        if ring != None:  # noqa: E711
            ring.show(boss.core.since_hit)
        for i in range(len(boss.parts)):
            view = parts[i] if i < len(parts) else None
            if view != None:  # noqa: E711
                show_part(view, boss.parts[i], enemy, dt)

    return BuiltEnemyModel(root, sync)


def _limb_builder(design: Any, scene: Any, neon: Rgb, look: Any) -> Any:
    """The builder of a limb's model (see `BossLimbs`), flashing with its owner."""

    def build(limb: str, draw: Any) -> Any:
        model = build_enemy_model(
            design.id + "-" + limb + "-limb", scene, neon, draw, look["breath"]
        )
        return FlashGroup(model, look["flash"])

    return build


def build_body(design: Any, drawing: Any, root: Any, look: Any) -> dict[str, Any]:
    """The core body (and its turret) on `root`, and the ring turning with the boss's spin."""
    flash = look["flash"]
    neon = look["neon"]
    name = design.id
    scene = root.getScene()
    core_model = build_enemy_model(name + "-core", scene, neon, drawing.core, look["breath"])
    core_model.root.parent = root
    core_turret = build_turret(design, "core", drawing, core_model.root, neon, look["breath"])
    core = FlashGroup(core_model, flash)
    ring_node = new_transform_node(name + "-ring", scene)
    ring_node.parent = root
    ring_draw = _field(drawing, "ring")
    ring = None
    if ring_draw != None:  # noqa: E711
        ring = FlashGroup(
            build_enemy_model(name + "-ringbody", scene, neon, ring_draw, look["breath"]),
            flash,
        )
        ring.model.root.parent = ring_node
    return {
        "core": core,
        "core_turret": core_turret,
        "ring_node": ring_node,
        "ring": ring,
    }


def build_part(design: Any, spec: Any, drawing: Any, frame: Any, look: Any) -> PartView:
    """The model, smoke and stump of one part, on `frame` (the boss, its turning ring or a
    joint)."""
    flash = look["flash"]
    neon = look["neon"]
    name = design.id
    scene = frame.node.getScene()
    draw = _field(drawing.parts, spec.id)
    if draw == None:  # noqa: E711
        raise ValueError('Boss "' + name + '" has no drawing for its part "' + spec.id + '"')
    at = boss_point(spec.x, spec.y)
    model = build_enemy_model(
        name + "-" + spec.id,
        scene,
        neon,
        _part_builder(draw, at),
        look["breath"],
    )
    hang(model.root, ORIGIN, frame)
    turret = build_turret(design, spec.id, drawing, model.root, neon, look["breath"])
    spot = new_transform_node(name + "-" + spec.id + "-spot", scene)
    hang(spot, at, frame)
    smoke = build_smoke(name + "-" + spec.id, spec.radius, scene, spot)
    stump = build_stump(name + "-" + spec.id, spec.radius, scene, spot)
    return PartView(FlashGroup(model, flash), turret, smoke, stump)


def strobe(enemy: Any) -> Any:
    """The brightness of a boss's charge lights: its own, a strobe during a stage change, and a fast
    flicker while it is angry (phase 7 review)."""
    if not isinstance(enemy, Boss):
        return enemy.charge
    if enemy.pause > 0:
        return 1 if math.floor(enemy.pause * BOSS_LOOK.stageStrobeHz * 2) % 2 == 0 else 0
    if enemy.rage <= 0:
        return enemy.charge
    hz = BOSS_LOOK.rageFlicker.hz
    dim = BOSS_LOOK.rageFlicker.dim
    return 1 if math.floor(enemy.rage * hz * 2) % 2 == 0 else dim


def show_part(view: PartView, part: Any, lit: Any, dt: float) -> None:
    """A part: its model while it stands (flashing, smoking), its stump once destroyed."""
    destroyed = part.destroyed
    set_enabled(view.group.model.root, not destroyed)
    set_enabled(view.stump.node, destroyed)
    smoking = not destroyed and part.health < part.max_health * BOSS_LOOK.smoke.below
    set_enabled(view.smoke.node, smoking)
    if destroyed:
        view.stump.sync(STUMP_STATE, dt)
        return
    view.group.model.sync(lit, dt)
    show_turret(view.turret, part.turret, lit, dt)
    view.group.show(part.since_hit)
    if smoking:
        view.smoke.step(dt)
