# Copyright (c) 2026 Renaud Guillon
"""Builds the model of a boss (BOSS-47, GFX-ART-16) from its drawing: its core body.

Its parts on their own nodes (each flashing white when hit, smoking under half health, gone once
destroyed), its turrets and limbs, and an optional ring turning with the boss's spin. A new look
keeps the parts, joints, turrets and muzzles of the design (GFX-ART-18).
"""

import math

from core.entities.boss import Boss
from game.config.boss_look import BOSS_LOOK
from game.config.bosses.boss_guns import mount_order
from game.config.bosses.moving_regions import is_moving, ridden_region, standing_region

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
from game.config.record import concat, record
from game.view.bosses.boss_armour import REST, build_armour, hatch_opens
from game.view.bosses.boss_damage import build_smoke, effect_materials
from game.view.bosses.boss_gun_models import draw_mount, draw_stump
from game.view.bosses.boss_limbs import (
    ORIGIN,
    BossLimbs,
    JointFrame,
    JointFrames,
    boss_point,
    hang,
)
from game.view.bosses.boss_reveal import Slide, build_reveal
from game.view.bosses.hidden_weapon_shapes import weapon_drawing, weapon_slides
from game.view.enemies.enemy_materials import BODY_MATERIALS
from game.view.enemies.enemy_mesh import BuiltEnemyModel, build_enemy_model
from game.view.enemies.living_motion import new_breath
from game.view.enemies.organic_parts import opt
from render.babylon import (
    child_meshes,
    new_transform_node,
    node_name,
    set_enabled,
)
from render.edge_trim_mesh import set_trim_group

# isort: split
# __pragma__ ("skip")
from typing import Any

type Rgb = Any
type Vec3 = list[Any]
# __pragma__ ("noskip")


def _field(obj: Any, key: str) -> Any:
    """`obj?.[key]`: the field `key` of `obj`, or None when `obj` or the field is missing."""
    if obj == None or key not in obj:
        return None
    return obj[key]


def _point_of(spot: Any) -> list[Any]:
    """`bossPoint(...spot)`: a playfield point `[x, y]` or `[x, y, height]`, in model space."""
    if len(spot) > 2:
        return boss_point(spot[0], spot[1], spot[2])
    return boss_point(spot[0], spot[1])


class TurretView:
    """A piece's turret: its model, on a node turning around its pivot."""

    def __init__(self, pivot: Any, model: Any) -> None:
        self.pivot = pivot
        self.model = model


def _part_builder(draw: Any, at: list[Any]) -> Any:
    """Return the builder of a part drawn around its centre `at`."""

    def build(p: Any) -> None:
        draw(p, at)

    return build


class GunLit:
    """What a boss's models show of it: its charge lights, its barrels and its launchers.

    The barrels recoil (WPN-03) and the ports' rockets reload (WPN-07) on the boss's clock.
    """

    def __init__(self) -> None:
        self.charge: float = 0
        self.age: float = 0
        self.barrels: list[Any] = []
        self.launchers: list[Any] = []
        self.turret = None
        self.heading = math.pi

    def follow(self, boss: Any, charge: float) -> None:
        """Show `boss` (None for a model shown on its own) with its charge lights at `charge`."""
        self.charge = charge
        if boss != None:
            self.age = boss.age
            self.barrels = boss.barrels
            self.launchers = boss.launchers


# Seconds a gun mount takes to rise out of the hull when its boss first uses it (BOSS-58).
MOUNT_RISE_SECONDS = 0.8


class MountView:
    """A gun mount's model (BOSS-58), on a node at its pivot turning with its turret.

    `index` is its mount's among the boss's (`Boss.mounts`).
    """

    def __init__(
        self, index: int, pivot: Any, model: Any, rest: list[Any], rise: float, delay: float = 0
    ) -> None:
        self.index = index
        # Seconds it waits to rise, under a hatch until it has burst.
        self.delay = delay
        self.pivot = pivot
        self.model = model
        # Where its pivot is at rest, and how far it rises out of a hidden weapon's pod.
        self.rest = rest
        self.rise = rise

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Turn it with its mount's turret, its barrels recoiling (WPN-03).

        Hidden until its boss first fires from it, then rising out of the hull (BOSS-58).
        """
        mounts = boss.mounts if boss != None else []
        mount = mounts[self.index] if self.index < len(mounts) else None
        out = 1.0
        if mount != None:
            if mount.shown_at == None:
                set_enabled(self.pivot, False)
                return
            out = max(0, min(1, (boss.age - mount.shown_at - self.delay) / MOUNT_RISE_SECONDS))
        set_enabled(self.pivot, True)
        sunk = (1 - out * out * (3 - 2 * out)) * self.rise * 1.3
        self.model.root.position.set(-self.rest[0], -self.rest[1] - sunk, -self.rest[2])
        turret = mount.turret if mount != None else None
        self.pivot.rotation.y = turret.aim if turret != None else 0
        self.model.sync(lit, dt)


def build_mounts(design: Any, piece: str, holder: Any, look: Any) -> list[MountView]:
    """Return the models of the mounts on `piece` (a part id or `core`), on `holder`.

    Each on a node of its own at its pivot (BOSS-58).
    """
    mounts = _field(design, "mounts") or []
    order = mount_order(mounts)
    neon = look["neon"]
    result: list[MountView] = []
    for i in range(len(mounts)):
        mount = mounts[i]
        if mount.piece != piece:
            continue
        at = boss_point(mount.at[0], mount.at[1], mount.height)
        scene = holder.getScene()
        pivot = new_transform_node(design.id + "-" + mount.id + "-mount", scene)
        pivot.position.set(at[0], at[1], at[2])
        pivot.parent = holder
        model = build_enemy_model(
            design.id + "-" + mount.id + "-gun",
            scene,
            neon,
            _mount_builder(mount, order[i], neon),
            look["breath"],
        )
        model.root.position.set(-at[0], -at[1], -at[2])
        model.root.parent = pivot
        rise = mount.size if mount.kind != "missile" else 6
        hatched = any(r.mount == mount.id for r in _field(design, "armour") or [])
        result.append(MountView(i, pivot, model, at, rise, hatch_opens() if hatched else 0))
    return result


def _mount_builder(mount: Any, first: int, neon: Any) -> Any:
    """Return the builder of a mount's model (`boss_gun_models.draw_mount`)."""

    def build(p: Any) -> None:
        draw_mount(p, mount, first, neon)

    return build


def build_stumps(design: Any, piece: str, frame: Any, look: Any) -> list[Any]:
    """Return the stumps the mounts of part `piece` leave once it is destroyed (BOSS-18).

    One model on the part's frame, hidden while the part stands; none when it has no mount.
    """
    mounts = [m for m in _field(design, "mounts") or [] if m.piece == piece]
    if len(mounts) == 0:
        return []

    def build(p: Any) -> None:
        for mount in mounts:
            draw_stump(p, mount)

    model = build_enemy_model(
        design.id + "-" + piece + "-stump",
        frame.node.getScene(),
        look["neon"],
        build,
        look["breath"],
    )
    hang(model.root, ORIGIN, frame)
    set_enabled(model.root, False)
    return [model.root]


def show_mounts(views: list[MountView], boss: Any, lit: Any, dt: float) -> None:
    """Show the mounts of a piece (see `MountView.show`)."""
    for view in views:
        view.show(boss, lit, dt)


def build_turret(
    design: Any,
    piece: str,
    drawing: Any,
    holder: Any,
    neon: Rgb,
    breath: Any,
) -> TurretView | None:
    """Return the turret of `piece` on `holder` (its piece's model), if the boss's drawing has one.

    A piece of its own on its pivot (BOSS-29).
    """
    turrets = _field(drawing, "turrets")
    draw = _field(turrets, piece)
    gun = _field(design.guns, piece)
    turret = _field(gun, "turret")
    if draw == None and turret == None:
        return None
    if draw == None or turret == None:
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
    """Show a turret turned by its aim (+Y turns the nose, down the screen, clockwise)."""
    if view == None:
        return
    view.pivot.rotation.y = 0 if turret == None else turret.aim
    view.model.sync(lit, dt)


class FlashGroup:
    """A piece of the model shown for a part, or the core, with its hit flash."""

    def __init__(self, model: Any, flash: Any) -> None:
        self.model = model
        self._flash = flash
        self._hulls: list[Any] = []
        for mesh in child_meshes(model.root, False):
            material = mesh.material
            name = node_name(material) if material != None else ""
            if name in BODY_MATERIALS:
                self._hulls.append([mesh, material])

    def show(self, since_hit: float) -> None:
        """Flashes white for a moment after a hit (BOSS-17)."""
        on = since_hit < BOSS_LOOK.flash.seconds
        for hull in self._hulls:
            hull[0].material = self._flash if on else hull[1]
            hull[0].useVertexColors = not on


class PartView:
    """The pieces of one part: its model (its turret and its mounts) and its smoke."""

    def __init__(
        self,
        group: Any,
        turret: Any,
        smoke: Any,
        reveal: Any = None,
        mounts: Any = None,
        stumps: Any = None,
    ) -> None:
        self.group = group
        self.turret = turret
        self.smoke = smoke
        # How it comes out as the boss transforms, if it is hidden at first (`boss_reveal`).
        self.reveal = reveal
        # Its gun mounts (BOSS-58).
        self.mounts: list[MountView] = mounts if mounts != None else []
        # What its destroyed weapons leave: a stump where each mount stood (BOSS-18).
        self.stumps: list[Any] = stumps if stumps != None else []


def build_boss_model(design: Any, scene: Any, neon: Rgb, drawing: Any) -> BuiltEnemyModel:
    """Build the model of a boss (BOSS-47) from `drawing`, in the colour `neon`: its core body.

    Its parts on their own nodes (each flashing white when hit, smoking under half health, replaced
    by gone once destroyed), and an optional ring turning with the boss's spin.
    """
    name = design.id
    # A drawing is an object literal of functions: its fields read as attributes (`drawing.core`).
    drawing = record(drawing)
    flash = effect_materials(scene)["flash"]
    root = new_transform_node(name, scene)
    # BOSS-51: its core, parts and limbs breathe as one creature.
    look = {"flash": flash, "neon": neon, "breath": new_breath()}
    body = build_body(design, drawing, root, look)
    core = body["core"]
    core_turret = body["core_turret"]
    ring_node = body["ring_node"]
    ring = body["ring"]
    joints = JointFrames(design, root)
    # The nodes the weapons riding a moving region hang from (D-230).
    carriers = _carriers(design, root)
    parts = [
        build_part(
            design,
            spec,
            drawing,
            _holder(design, spec, joints, [root, ring_node], carriers),
            look,
            _remains(design, spec, carriers),
        )
        for spec in design.stats.parts
    ]
    limbs = BossLimbs(
        design,
        _field(drawing, "limbs"),
        joints,
        _limb_builder(design, scene, neon, look),
    )
    # Its armour regions, drawn as pieces of their own over the core (D-254): they burst off or
    # move as it transforms.
    armour = _armour_views(design, drawing, root, look, carriers)
    rig = _rig_view(drawing, root, look)
    lit = GunLit()
    core_mounts = body["core_mounts"]

    def sync(boss: Any, dt: float) -> None:
        is_boss = isinstance(boss, Boss)
        # After a part is destroyed, its lights strobe while it holds its fire (BOSS-22).
        lit.follow(boss if is_boss else None, strobe(boss))
        enemy = lit
        core.model.sync(enemy, dt)
        show_mounts(core_mounts, boss if is_boss else None, enemy, dt)
        if ring != None:
            ring.model.sync(enemy, dt)
        limbs.show(boss if is_boss else None, enemy, dt)
        for view in concat(armour, rig):
            view.show(boss if is_boss else None, enemy, dt)
        if not is_boss:
            show_turret(core_turret, None, enemy, dt)
            return
        show_turret(core_turret, boss.core.turret, enemy, dt)
        # It rolls into its sideways moves (BOSS-11). Screen right is the model's -X (its
        # nose points down the screen): +Z rolls -X down.
        root.rotation.z = boss.roll
        ring_node.rotation.y = boss.spin
        core.show(boss.core.since_hit)
        if ring != None:
            ring.show(boss.core.since_hit)
        for i in range(len(boss.parts)):
            view = parts[i] if i < len(parts) else None
            if view != None:
                show_part(view, boss.parts[i], enemy, dt)
                show_mounts(view.mounts, boss, enemy, dt)
                if view.reveal != None:
                    view.reveal.show(boss.form, boss.transforming_into, boss.transform)

    return BuiltEnemyModel(root, sync)


def _rig_view(drawing: Any, root: Any, look: Any) -> list[Any]:
    """Return the boss's rig of its own (D-228: the Scorpion's tail, posed as it transforms).

    If it has one: a list of none or one view.
    """
    rig = _field(drawing, "rig")
    if rig == None:
        return []
    return [rig.build(root, look["neon"], look["breath"])]


def _holder(design: Any, spec: Any, joints: JointFrames, nodes: list[Any], carriers: Any) -> Any:
    """Return the frame part `spec` hangs on.

    For one that orbits it is the turning ring (`nodes[1]`), the carrier of the moving region it
    rides (D-230); otherwise it is the boss (`nodes[0]`).
    """
    ridden = ridden_region(design, spec)
    if ridden != None:
        return JointFrame(carriers[ridden.id], ORIGIN)
    return joints.frame(
        opt(spec, "joint", None), nodes[1] if opt(spec, "orbits", False) else nodes[0]
    )


def _carriers(design: Any, root: Any) -> dict[str, Any]:
    """Return the nodes on `root` for each moving region of `design` (D-230), by key.

    The weapons riding it hang from the one keyed by its id, what its parts standing on it from
    the start leave from the one keyed by its id and `REST` (see `boss_armour.MovingView`).
    """
    result: dict[str, Any] = {}
    for region in _field(design, "armour") or []:
        if is_moving(region):
            for key in [region.id, region.id + REST]:
                node = new_transform_node(design.id + "-" + key + "-carrier", root.getScene())
                node.parent = root
                result[key] = node
    return result


def _remains(design: Any, spec: Any, carriers: Any) -> Any:
    """Return the frame what part `spec` leaves once destroyed hangs on (BOSS-18), if not its own.

    The moving piece it stands on, so its stumps and smoke move with the piece; None otherwise.
    """
    region = standing_region(design, spec)
    if region == None:
        return None
    return JointFrame(carriers[region.id + REST], ORIGIN)


def _armour_views(design: Any, drawing: Any, root: Any, look: Any, carriers: Any) -> list[Any]:
    """Return the views of the design's armour regions (`build_armour`), flashing with the core.

    There are none when the design has no armour.
    """
    regions = _field(design, "armour")
    if regions == None or len(regions) == 0:
        return []
    flash = look["flash"]

    def flash_of(model: Any) -> FlashGroup:
        return FlashGroup(model, flash)

    return build_armour(design, drawing, root, look["neon"], look["breath"], flash_of, carriers)


def _limb_builder(design: Any, scene: Any, neon: Rgb, look: Any) -> Any:
    """Return the builder of a limb's model (see `BossLimbs`), flashing with its owner."""

    def build(limb: str, draw: Any) -> Any:
        model = build_enemy_model(
            design.id + "-" + limb + "-limb", scene, neon, draw, look["breath"]
        )
        return FlashGroup(model, look["flash"])

    return build


def build_body(design: Any, drawing: Any, root: Any, look: Any) -> dict[str, Any]:
    """Return the core body and its turret on `root`, and the ring that turns (BOSS-34).

    The core is drawn by the drawing's core; the ring turns with the boss's spin.
    """
    core_draw = drawing.core
    flash = look["flash"]
    neon = look["neon"]
    name = design.id
    scene = root.getScene()
    core_model = build_enemy_model(name + "-core", scene, neon, core_draw, look["breath"])
    core_model.root.parent = root
    core_turret = build_turret(design, "core", drawing, core_model.root, neon, look["breath"])
    core_mounts = build_mounts(design, "core", core_model.root, look)
    core = FlashGroup(core_model, flash)
    ring_node = new_transform_node(name + "-ring", scene)
    ring_node.parent = root
    ring_draw = _field(drawing, "ring")
    ring = None
    if ring_draw != None:
        ring = FlashGroup(
            build_enemy_model(name + "-ringbody", scene, neon, ring_draw, look["breath"]),
            flash,
        )
        ring.model.root.parent = ring_node
    return {
        "core": core,
        "core_turret": core_turret,
        "core_mounts": core_mounts,
        "ring_node": ring_node,
        "ring": ring,
    }


def build_part(
    design: Any, spec: Any, drawing: Any, frame: Any, look: Any, remains: Any = None
) -> PartView:
    """Return the model and smoke of one part, on `frame`.

    The frame is the boss, its turning ring or a joint; what it leaves once destroyed (its smoke and
    stumps) hangs on `remains` if given (the moving piece it stands on, BOSS-18).
    """
    left = remains if remains != None else frame
    flash = look["flash"]
    neon = look["neon"]
    name = design.id
    scene = frame.node.getScene()
    draw = _field(drawing.parts, spec.id)
    weapon = _field(_field(design, "weapons"), spec.id)
    if draw == None and weapon != None:
        # A hidden weapon, drawn from its look (`hidden_weapon_shapes`).
        draw = weapon_drawing(weapon, neon)
    if draw == None:
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
    # Trimmed along its own outline, wherever it sits on the hull (BOSS-48, GFX-TRIM-08,
    # GFX-READ-09).
    set_trim_group(model.root)
    turret = build_turret(design, spec.id, drawing, model.root, neon, look["breath"])
    mounts = build_mounts(design, spec.id, model.root, look)
    spot = new_transform_node(name + "-" + spec.id + "-spot", scene)
    hang(spot, at, left)
    smoke = build_smoke(name + "-" + spec.id, spec.radius, scene, spot)
    reveal = None
    if opt(spec, "reveal", None) != None:
        slides = _weapon_slides(design, spec, weapon, model.root, mounts, look)
        reveal = build_reveal(design, spec, model.root, slides)
    stumps = build_stumps(design, spec.id, left, look)
    return PartView(FlashGroup(model, flash), turret, smoke, reveal, mounts, stumps)


def _weapon_slides(
    design: Any, spec: Any, weapon: Any, holder: Any, mounts: list[MountView], look: Any
) -> list[Slide]:
    """Return what slides out of a hidden weapon as it unfolds.

    Its mounts rise out of its pod (BOSS-58); a hangar's doors slide open (a model of its own each
    on `holder`).
    """
    result: list[Slide] = [Slide(view.pivot, view.rest, [0, 1, 0], view.rise) for view in mounts]
    if weapon == None:
        return result
    slides = weapon_slides(weapon, look["neon"])
    for k in range(len(slides)):
        slide = slides[k]
        model = build_enemy_model(
            design.id + "-" + spec.id + "-slide-" + str(k),
            holder.getScene(),
            look["neon"],
            _part_builder(slide[0], boss_point(spec.x, spec.y)),
            look["breath"],
        )
        model.root.parent = holder
        result.append(Slide(model.root, [0, 0, 0], slide[1], slide[2]))
    return result


def strobe(enemy: Any) -> Any:
    """Return the brightness of a boss's charge lights: its own, a strobe during a stage change.

    And a fast flicker while it is angry (BOSS-22, BOSS-27).
    """
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
    """Show a part: its model while it stands (flashing, smoking: BOSS-17).

    Once destroyed, only the stumps of its weapons (BOSS-18).
    """
    destroyed = part.destroyed
    if part.hidden and view.reveal == None:
        # Retired (D-228): it has left the fight.
        set_enabled(view.group.model.root, False)
        set_enabled(view.smoke.node, False)
        for stump in view.stumps:
            set_enabled(stump, False)
        return
    set_enabled(view.group.model.root, not destroyed)
    for stump in view.stumps:
        # A weapon still hidden when the boss dies never came out: it leaves nothing.
        set_enabled(stump, destroyed and not part.hidden)
    smoking = not destroyed and part.health < part.max_health * BOSS_LOOK.smoke.below
    set_enabled(view.smoke.node, smoking)
    if destroyed:
        return
    view.group.model.sync(lit, dt)
    show_turret(view.turret, part.turret, lit, dt)
    view.group.show(part.since_hit)
    if smoking:
        view.smoke.step(dt)
