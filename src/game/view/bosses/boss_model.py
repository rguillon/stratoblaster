# Copyright (c) 2026 Renaud Guillon
"""Builds the model of a boss (BOSS-47, GFX-ART-16) from its drawing: its core body.

Its parts on their own nodes (each flashing white when hit, smoking under half health, gone once
destroyed), its turrets and limbs, and an optional ring turning with the boss's spin. A new look
keeps the parts, joints, turrets and muzzles of the design (GFX-ART-18).
"""

import math

from core.entities.boss import Boss
from game.config.boss_look import BOSS_LOOK
from game.config.bosses.moving_regions import is_moving, ridden_region

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
from game.config.record import concat, record
from game.view.bosses.boss_armour import LAYERS, build_armour, cut_armour
from game.view.bosses.boss_damage import build_smoke, effect_materials
from game.view.bosses.boss_limbs import (
    ORIGIN,
    BossLimbs,
    JointFrame,
    JointFrames,
    boss_point,
    hang,
)
from game.view.bosses.boss_reveal import Slide, build_reveal
from game.view.bosses.boss_stems import stems_drawing, stems_for
from game.view.bosses.hidden_weapon_shapes import (
    turret_slide,
    weapon_drawing,
    weapon_slides,
    weapon_turret_drawing,
)
from game.view.bosses.region_motion import posed
from game.view.enemies.enemy_materials import BODY_MATERIALS
from game.view.enemies.enemy_mesh import (
    BuiltEnemyModel,
    build_enemy_model,
    collect_parts,
)
from game.view.enemies.living_motion import new_breath
from game.view.enemies.organic_parts import opt
from render.babylon import (
    child_meshes,
    new_transform_node,
    node_name,
    set_enabled,
)
from render.edge_trim_mesh import set_trim_group
from render.geometry.shatter import triangles

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
    weapon = _field(_field(design, "weapons"), piece)
    if draw == None and weapon != None:
        # A hidden weapon's turret, drawn from its look (`hidden_weapon_shapes`).
        draw = weapon_turret_drawing(weapon, neon)
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
    """The pieces of one part: its model (and turret) and its smoke."""

    def __init__(self, group: Any, turret: Any, smoke: Any, reveal: Any = None) -> None:
        self.group = group
        self.turret = turret
        self.smoke = smoke
        # How it comes out as the boss transforms, if it is hidden at first (`boss_reveal`).
        self.reveal = reveal


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
    # Its armour regions are cut out of its core (docs/superpowers/specs/2026-10-31-boss-armour-
    # shedding-design.md): they burst off as it transforms.
    cut = _armour_cut(design, drawing)
    core_draw = drawing.core if cut is None else cut.core_drawing()
    body = build_body(design, drawing, root, look, core_draw)
    core = body["core"]
    core_turret = body["core_turret"]
    ring_node = body["ring_node"]
    ring = body["ring"]
    joints = JointFrames(design, root)
    # The nodes the weapons riding a moving region hang from (D-230).
    carriers = _carriers(design, root)
    parts = [
        build_part(
            design, spec, drawing, _holder(design, spec, joints, [root, ring_node], carriers), look
        )
        for spec in design.stats.parts
    ]
    limbs = BossLimbs(
        design,
        _field(drawing, "limbs"),
        joints,
        _limb_builder(design, scene, neon, look),
    )
    armour = _armour_views(design, drawing, cut, root, look, carriers)
    rig = _rig_view(drawing, root, look)
    _build_stems(design, drawing, cut, root, look)
    lit: Any = {"charge": 0}

    def sync(boss: Any, dt: float) -> None:
        # After a part is destroyed, its lights strobe while it holds its fire (BOSS-22).
        lit["charge"] = strobe(boss)
        enemy = lit
        core.model.sync(enemy, dt)
        if ring != None:
            ring.model.sync(enemy, dt)
        is_boss = isinstance(boss, Boss)
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


def _build_stems(design: Any, drawing: Any, cut: Any, root: Any, look: Any) -> None:
    """Build the stems holding the boss's loose pieces to it (D-227), a model on `root`, if any."""
    stems = rest_stems(design, drawing, cut, look["neon"])
    if len(stems) == 0:
        return
    model = build_enemy_model(
        design.id + "-stems",
        root.getScene(),
        look["neon"],
        stems_drawing(stems, look["neon"]),
        look["breath"],
    )
    model.root.parent = root


def _armour_cut(design: Any, drawing: Any) -> Any:
    """Return the design's armour regions cut out of its core's drawing (`cut_armour`).

    None if it has no armour.
    """
    regions = _field(design, "armour")
    if regions == None or len(regions) == 0:
        return None
    return cut_armour(drawing.core, regions)


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
    """Return a node on `root` for each moving region of `design` (D-230), by its id.

    The weapons riding it hang from it (see `boss_armour.MovingView`).
    """
    result: dict[str, Any] = {}
    for region in _field(design, "armour") or []:
        if is_moving(region):
            node = new_transform_node(design.id + "-" + region.id + "-carrier", root.getScene())
            node.parent = root
            result[region.id] = node
    return result


def _armour_views(
    design: Any, drawing: Any, cut: Any, root: Any, look: Any, carriers: Any = None
) -> list[Any]:
    """Return the views of the armour regions `cut`, flashing with the core.

    There are none when `cut` is None.
    """
    if cut is None:
        return []
    flash = look["flash"]

    def flash_of(model: Any) -> FlashGroup:
        return FlashGroup(model, flash)

    supports = part_supports(design, drawing, look["neon"])
    return build_armour(
        design, cut, root, look["neon"], look["breath"], flash_of, supports, carriers
    )


def _standing_parts(design: Any, drawing: Any, neon: Rgb, hidden: bool) -> list[Any]:
    """Return the parts standing on the boss, each `[spec, parts]`.

    Not those on joints, nor orbiting ones; the hidden ones too when `hidden`. Each one's `parts`
    are its drawing's parts at its spot (`collect_parts`). Every part has a drawing or a weapon
    look: `build_part`, run first, raises otherwise.
    """
    result: list[Any] = []
    weapons = _field(design, "weapons")
    for spec in design.stats.parts:
        if opt(spec, "joint", None) != None or opt(spec, "orbits", False):
            continue
        if not hidden and opt(spec, "reveal", None) != None:
            continue
        weapon = _field(weapons, spec.id)
        if weapon != None and _field(weapon, "rig"):
            # On a rig (D-228), not standing on the boss.
            continue
        if ridden_region(design, spec) != None:
            # Riding a moving region's piece (D-230).
            continue
        draw = _field(drawing.parts, spec.id)
        if draw == None and weapon != None:
            draw = weapon_drawing(weapon, neon)
        at = boss_point(spec.x, spec.y)
        result.append([spec, collect_parts(_part_builder(draw, at))["parts"]])
    return result


def rest_stems(design: Any, drawing: Any, cut: Any, neon: Rgb) -> list[Any]:
    """Return what holds the boss's loose pieces to it at rest (`boss_stems.stems_for`).

    Its core (with its armour on) and the parts standing on it.
    """
    tris: list[Any] = []
    lasting: list[Any] = []
    if cut is None:
        core = collect_parts(drawing.core)["parts"]
        for layer in LAYERS:
            tris.extend(triangles(getattr(core, layer).geometry))
    else:
        for layer in LAYERS:
            lasting.extend(cut.kept[layer])
            tris.extend(cut.kept[layer])
            tris.extend(cut.floating.get(layer, []))
            for k in range(len(cut.regions)):
                # A moving region's piece as it rests (D-230).
                tris.extend(posed(cut.regions[k][layer], design.armour[k], 0))
    for entry in _standing_parts(design, drawing, neon, False):
        for layer in LAYERS:
            tris.extend(triangles(getattr(entry[1], layer).geometry))
    rig = _field(drawing, "rig")
    if rig != None:
        # Its rig at rest stays on through every transformation (D-228).
        at_rest = rig.triangles(0)
        tris.extend(at_rest)
        lasting.extend(at_rest)
    return stems_for(tris, lasting)


def part_supports(design: Any, drawing: Any, neon: Rgb) -> list[Any]:
    """Where the parts stand on the boss (D-227), `[x, z, height, width]` in model space.

    Under each part's spot, how high a pylon must reach to meet it (into its lower half), its
    radius. Parts on joints or orbiting are left out.
    """
    result: list[Any] = []
    for entry in _standing_parts(design, drawing, neon, True):
        spec = entry[0]
        parts = entry[1]
        at = boss_point(spec.x, spec.y)
        bottom = math.inf
        top = -math.inf
        for layer in [parts.hull, parts.flesh]:
            ys = layer.geometry.positions
            for k in range(1, len(ys), 3):
                bottom = min(bottom, ys[k])
                top = max(top, ys[k])
        if bottom < math.inf:
            # Up into the part, so it meets its underside wherever that is.
            result.append([at[0], at[2], bottom + (top - bottom) * 0.4, spec.radius])
    ring = _field(drawing, "ring")
    if ring != None:
        # The ring turns about the centre: a pylon there holds it up.
        result.append(_ring_support(collect_parts(ring)["parts"]))
    return result


def _ring_support(parts: Any) -> list[Any]:
    """Return the support of a ring drawn by `parts`: at the centre, under its lowest point.

    A third of its reach wide.
    """
    bottom = math.inf
    reach = 0.0
    for layer in [parts.hull, parts.flesh]:
        ps = layer.geometry.positions
        for k in range(0, len(ps), 3):
            bottom = min(bottom, ps[k + 1])
            reach = max(reach, math.hypot(ps[k], ps[k + 2]))
    return [0, 0, bottom if bottom < math.inf else 0, reach / 3]


def _limb_builder(design: Any, scene: Any, neon: Rgb, look: Any) -> Any:
    """Return the builder of a limb's model (see `BossLimbs`), flashing with its owner."""

    def build(limb: str, draw: Any) -> Any:
        model = build_enemy_model(
            design.id + "-" + limb + "-limb", scene, neon, draw, look["breath"]
        )
        return FlashGroup(model, look["flash"])

    return build


def build_body(
    design: Any, drawing: Any, root: Any, look: Any, core_draw: Any = None
) -> dict[str, Any]:
    """Return the core body and its turret on `root`, and the ring that turns (BOSS-34).

    The core is drawn by `core_draw`, else by the drawing's core; the ring turns with the boss's
    spin.
    """
    if core_draw == None:
        core_draw = drawing.core
    flash = look["flash"]
    neon = look["neon"]
    name = design.id
    scene = root.getScene()
    core_model = build_enemy_model(name + "-core", scene, neon, core_draw, look["breath"])
    core_model.root.parent = root
    core_turret = build_turret(design, "core", drawing, core_model.root, neon, look["breath"])
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
        "ring_node": ring_node,
        "ring": ring,
    }


def build_part(design: Any, spec: Any, drawing: Any, frame: Any, look: Any) -> PartView:
    """Return the model and smoke of one part, on `frame`.

    The frame is the boss, its turning ring or a joint.
    """
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
    spot = new_transform_node(name + "-" + spec.id + "-spot", scene)
    hang(spot, at, frame)
    smoke = build_smoke(name + "-" + spec.id, spec.radius, scene, spot)
    reveal = None
    if opt(spec, "reveal", None) != None:
        slides = _weapon_slides(design, spec, weapon, model.root, turret, look)
        reveal = build_reveal(design, spec, model.root, slides)
    return PartView(FlashGroup(model, flash), turret, smoke, reveal)


def _weapon_slides(
    design: Any, spec: Any, weapon: Any, holder: Any, turret: Any, look: Any
) -> list[Slide]:
    """Return what slides out of a hidden weapon as it unfolds: its barrel, cells, orb.

    Tube or doors (a model of its own each on `holder`), or its turret.
    """
    if weapon == None:
        return []
    if turret != None:
        p = turret.pivot.position
        return [Slide(turret.pivot, [p.x, p.y, p.z], [0, 1, 0], turret_slide(weapon))]
    result: list[Slide] = []
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

    Nothing once destroyed (BOSS-18, D-225).
    """
    destroyed = part.destroyed
    if part.hidden and view.reveal == None:
        # Retired (D-228): it has left the fight.
        set_enabled(view.group.model.root, False)
        set_enabled(view.smoke.node, False)
        return
    set_enabled(view.group.model.root, not destroyed)
    smoking = not destroyed and part.health < part.max_health * BOSS_LOOK.smoke.below
    set_enabled(view.smoke.node, smoking)
    if destroyed:
        return
    view.group.model.sync(lit, dt)
    show_turret(view.turret, part.turret, lit, dt)
    view.group.show(part.since_hit)
    if smoking:
        view.smoke.step(dt)
