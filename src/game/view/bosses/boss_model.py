"""Builds the model of a boss (P07-R05) from its drawing: its
core body, its parts on their own nodes (each flashing white when hit, smoking under half health,
gone once destroyed), its turrets and limbs, and an optional ring turning with
the boss's spin.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.entities.boss import Boss  # noqa: E402
from game.config.boss_look import BOSS_LOOK  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
from game.config.record import concat, record
from game.view.bosses.boss_armour import LAYERS, build_armour, cut_armour  # noqa: E402
from game.view.bosses.boss_damage import build_smoke, effect_materials  # noqa: E402
from game.view.bosses.boss_limbs import (  # noqa: E402
    ORIGIN,
    BossLimbs,
    JointFrames,
    boss_point,
    hang,
)
from game.view.bosses.boss_reveal import Slide, build_reveal  # noqa: E402
from game.view.bosses.boss_stems import stems_drawing, stems_for  # noqa: E402
from game.view.bosses.hidden_weapon_shapes import (  # noqa: E402
    turret_slide,
    weapon_drawing,
    weapon_slides,
    weapon_turret_drawing,
)
from game.view.enemies.enemy_materials import BODY_MATERIALS  # noqa: E402
from game.view.enemies.enemy_mesh import (  # noqa: E402
    BuiltEnemyModel,
    build_enemy_model,
    collect_parts,
)
from game.view.enemies.living_motion import new_breath  # noqa: E402
from game.view.enemies.organic_parts import opt  # noqa: E402
from render.babylon import (  # noqa: E402
    child_meshes,
    new_transform_node,
    node_name,
    set_enabled,
)
from render.edge_trim_mesh import set_trim_group  # noqa: E402
from render.geometry.shatter import triangles  # noqa: E402

__pragma__("skip")
from typing import Any  # noqa: E402

type Rgb = Any
type Vec3 = list[Any]
__pragma__("noskip")


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
    weapon = _field(_field(design, "weapons"), piece)
    if draw == None and weapon != None:  # noqa: E711
        # A hidden weapon's turret, drawn from its look (`hidden_weapon_shapes`).
        draw = weapon_turret_drawing(weapon, neon)
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
    """The pieces of one part: its model (and turret) and its smoke."""

    def __init__(self, group: Any, turret: Any, smoke: Any, reveal: Any = None) -> None:
        self.group = group
        self.turret = turret
        self.smoke = smoke
        # How it comes out as the boss transforms, if it is hidden at first (`boss_reveal`).
        self.reveal = reveal


def build_boss_model(design: Any, scene: Any, neon: Rgb, drawing: Any) -> BuiltEnemyModel:
    """Builds the model of a boss (P07-R05) from `drawing`, in the colour `neon`: its core body, its
    parts on their own nodes (each flashing white when hit, smoking under half health, replaced by
    gone once destroyed), and an optional ring turning with the boss's spin."""
    name = design.id
    # A drawing is an object literal of functions: its fields read as attributes (`drawing.core`).
    drawing = record(drawing)
    flash = effect_materials(scene)["flash"]
    root = new_transform_node(name, scene)
    # P16-R07: its core, parts and limbs breathe as one creature.
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
    armour = _armour_views(design, drawing, cut, root, look)
    rig = _rig_view(drawing, root, look)
    _build_stems(design, drawing, cut, root, look)
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
        for view in concat(armour, rig):
            view.show(boss if is_boss else None, enemy, dt)
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
                if view.reveal != None:  # noqa: E711
                    view.reveal.show(boss.form, boss.transforming_into, boss.transform)

    return BuiltEnemyModel(root, sync)


def _rig_view(drawing: Any, root: Any, look: Any) -> list[Any]:
    """The boss's rig of its own (D-228: the Scorpion's tail, posed as it transforms), if it has
    one: a list of none or one view."""
    rig = _field(drawing, "rig")
    if rig == None:  # noqa: E711
        return []
    return [rig.build(root, look["neon"], look["breath"])]


def _build_stems(design: Any, drawing: Any, cut: Any, root: Any, look: Any) -> None:
    """The stems holding the boss's loose pieces to it (D-227), a model on `root`, if any."""
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
    """The design's armour regions cut out of its core's drawing (`cut_armour`), if it has any."""
    regions = _field(design, "armour")
    if regions == None or len(regions) == 0:  # noqa: E711
        return None
    return cut_armour(drawing.core, regions)


def _armour_views(design: Any, drawing: Any, cut: Any, root: Any, look: Any) -> list[Any]:
    """The views of the armour regions `cut` (none when it is None), flashing with the core."""
    if cut is None:
        return []
    flash = look["flash"]

    def flash_of(model: Any) -> FlashGroup:
        return FlashGroup(model, flash)

    supports = part_supports(design, drawing, look["neon"])
    return build_armour(design, cut, root, look["neon"], look["breath"], flash_of, supports)


def _standing_parts(design: Any, drawing: Any, neon: Rgb, hidden: bool) -> list[Any]:
    """The parts standing on the boss (not on joints, not orbiting; the hidden ones too when
    `hidden`), each `[spec, parts]`: its drawing's parts at its spot (`collect_parts`)."""
    result: list[Any] = []
    weapons = _field(design, "weapons")
    for spec in design.stats.parts:
        if opt(spec, "joint", None) != None or opt(spec, "orbits", False):  # noqa: E711
            continue
        if not hidden and opt(spec, "reveal", None) != None:  # noqa: E711
            continue
        weapon = _field(weapons, spec.id)
        if weapon != None and _field(weapon, "rig"):  # noqa: E711
            # On a rig (D-228), not standing on the boss.
            continue
        draw = _field(drawing.parts, spec.id)
        if draw == None and weapon != None:  # noqa: E711
            draw = weapon_drawing(weapon, neon)
        if draw == None:  # noqa: E711
            continue
        at = boss_point(spec.x, spec.y)
        result.append([spec, collect_parts(_part_builder(draw, at))["parts"]])
    return result


def rest_stems(design: Any, drawing: Any, cut: Any, neon: Rgb) -> list[Any]:
    """What holds the boss's loose pieces to it at rest (`boss_stems.stems_for`): its core (with
    its armour on) and the parts standing on it."""
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
            for region in cut.regions:
                tris.extend(region[layer])
    for entry in _standing_parts(design, drawing, neon, False):
        for layer in LAYERS:
            tris.extend(triangles(getattr(entry[1], layer).geometry))
    rig = _field(drawing, "rig")
    if rig != None:  # noqa: E711
        # Its rig at rest stays on through every transformation (D-228).
        at_rest = rig.triangles(0)
        tris.extend(at_rest)
        lasting.extend(at_rest)
    return stems_for(tris, lasting)


def part_supports(design: Any, drawing: Any, neon: Rgb) -> list[Any]:
    """Where the parts stand on the boss (D-227), `[x, z, height, width]` in model space: under
    each part's spot, how high a pylon must reach to meet it (into its lower half), its radius.
    Parts on joints or orbiting are left out."""
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
    if ring != None:  # noqa: E711
        # The ring turns about the centre: a pylon there holds it up.
        result.append(_ring_support(collect_parts(ring)["parts"]))
    return result


def _ring_support(parts: Any) -> list[Any]:
    """The support of a ring drawn by `parts`: at the centre, under its lowest point, a third of
    its reach wide."""
    bottom = math.inf
    reach = 0.0
    for layer in [parts.hull, parts.flesh]:
        ps = layer.geometry.positions
        for k in range(0, len(ps), 3):
            bottom = min(bottom, ps[k + 1])
            reach = max(reach, math.hypot(ps[k], ps[k + 2]))
    return [0, 0, bottom if bottom < math.inf else 0, reach / 3]


def _limb_builder(design: Any, scene: Any, neon: Rgb, look: Any) -> Any:
    """The builder of a limb's model (see `BossLimbs`), flashing with its owner."""

    def build(limb: str, draw: Any) -> Any:
        model = build_enemy_model(
            design.id + "-" + limb + "-limb", scene, neon, draw, look["breath"]
        )
        return FlashGroup(model, look["flash"])

    return build


def build_body(
    design: Any, drawing: Any, root: Any, look: Any, core_draw: Any = None
) -> dict[str, Any]:
    """The core body (drawn by `core_draw`, else the drawing's core) and its turret on `root`, and
    the ring turning with the boss's spin."""
    if core_draw == None:  # noqa: E711
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
    """The model and smoke of one part, on `frame` (the boss, its turning ring or a
    joint)."""
    flash = look["flash"]
    neon = look["neon"]
    name = design.id
    scene = frame.node.getScene()
    draw = _field(drawing.parts, spec.id)
    weapon = _field(_field(design, "weapons"), spec.id)
    if draw == None and weapon != None:  # noqa: E711
        # A hidden weapon, drawn from its look (`hidden_weapon_shapes`).
        draw = weapon_drawing(weapon, neon)
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
    # Trimmed along its own outline, wherever it sits on the hull (P14-R04).
    set_trim_group(model.root)
    turret = build_turret(design, spec.id, drawing, model.root, neon, look["breath"])
    spot = new_transform_node(name + "-" + spec.id + "-spot", scene)
    hang(spot, at, frame)
    smoke = build_smoke(name + "-" + spec.id, spec.radius, scene, spot)
    reveal = None
    if opt(spec, "reveal", None) != None:  # noqa: E711
        slides = _weapon_slides(design, spec, weapon, model.root, turret, look)
        reveal = build_reveal(design, spec, model.root, slides)
    return PartView(FlashGroup(model, flash), turret, smoke, reveal)


def _weapon_slides(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    design: Any, spec: Any, weapon: Any, holder: Any, turret: Any, look: Any
) -> list[Slide]:
    """What slides out of a hidden weapon as it unfolds: its barrel, cells, orb, tube or doors (a
    model of its own each on `holder`), or its turret."""
    if weapon == None:  # noqa: E711
        return []
    if turret != None:  # noqa: E711
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
    """A part: its model while it stands (flashing, smoking), nothing once destroyed (D-225)."""
    destroyed = part.destroyed
    if part.hidden and view.reveal == None:  # noqa: E711
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
