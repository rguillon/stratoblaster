# Copyright (c) 2026 Renaud Guillon
"""The three models of the bosses' gun mounts (BOSS-58): a gun, a laser and a missile block.

Drawn from the numbers the game fires them from (`game/config/bosses/boss_guns.py`), with the
enemies' weapons: each gun barrel recoils as it fires (WPN-03, `basic_parts.model_barrel`), a laser
is the enemies' emitter (WPN-06) and a missile port the enemies' (WPN-07), its rocket reloading.

Model space of a boss: logical pixels, +Y up, its nose at +Z (`boss_limbs.boss_point`); a mount is
drawn round its pivot as it is at rest (its turret's node turns it).
"""

import math

from game.config.bosses.boss_guns import (
    GUN_SHAPE,
    MISSILE_BLOCK,
    axis_height,
    barrel_angles,
    barrel_root,
    mount_muzzles,
    port_spots,
)
from game.config.enemy_look import ENEMY_LOOK
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.mini_boss_shapes import QUARTER, TURRET_DOME
from game.view.enemies.basic_parts import model_barrel
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


H = ENEMY_LOOK.hull
DEG = math.pi / 180
# A barrel's charge cap at its tip, model units (`model_barrel`'s).
CAP = 0.8


def _base(p: Any, mount: Any, neon: Any) -> None:
    """Add a mount's base: a faceted dome (a turret's, or a fixed gun's) with a neon ring round it.

    A rotor's is a squat hub, a fixed laser's a low collar.
    """
    size = mount.size
    at = boss_point(mount.at[0], mount.at[1], mount.height)
    place = Placement(at, math.pi / 8)
    if mount.layout == "ring":
        p.hull.cylinder(size, size * GUN_SHAPE.domeHeight, 10, H.panel, Placement(at), size * 0.85)
        top = boss_point(mount.at[0], mount.at[1], mount.height + size * GUN_SHAPE.domeHeight)
        p.neon.ring(size * 0.55, size * 0.1, 10, neon, Placement(top))
        return
    if mount.kind == "laser" and not mount.turret:
        p.hull.cylinder(size, size * 0.6, 6, H.dark, place, size * 0.8)
        return
    dome = [[q[0] * size, q[1] * size * GUN_SHAPE.domeHeight * 2] for q in TURRET_DOME]
    p.hull.lathe(dome, 8, H.panel, place)
    p.neon.ring(size * 0.88, size * 0.08, 8, neon, Placement([at[0], at[1] + size * 0.05, at[2]]))


# A mortar's cradle (`style` `mortar`): its facets round (a big gun: `sides`), how far its pedestal
# goes down into what it stands on (`foot`, px), then shares of its `size` or its bore: its
# turntable's height, the cheeks' thickness and how far they rise over the barrel's axis, the gap
# between the barrel and a cheek, how far back the breech and the cheeks reach, and the trunnion
# pin's radius.
MORTAR: dict[str, Any] = {
    "sides": 16,
    "foot": 3,
    "table": 0.2,
    "cheek": 0.22,
    "cheekRise": 0.35,
    "gap": 0.12,
    "breech": 1.08,
    "back": 0.55,
    "pin": 0.3,
}


def _mortar_base(p: Any, mount: Any, neon: Any) -> None:
    """Add a mortar's base: a low turntable, the barrel's breech in a saddle between two cheeks.

    A trunnion pin across them through the breech, so the barrel rests in its cradle.
    """
    size = mount.size
    bore = mount.bore
    k = MORTAR
    at = boss_point(mount.at[0], mount.at[1], mount.height)
    yaw = barrel_angles(mount)[0] * DEG
    sx = math.sin(yaw)
    sz = math.cos(yaw)

    def local(u: float, v: float, h: float) -> Vec3:
        # `u` along the barrel, `v` across it (the model's +X at rest), `h` up from the base.
        return [at[0] + u * sx + v * sz, at[1] + h, at[2] + u * sz - v * sx]

    table = size * k["table"]
    n = k["sides"]
    foot = k["foot"]
    p.hull.cylinder(size * 0.8, foot, n, H.dark, Placement(local(0, 0, -foot)))
    p.hull.cylinder(size, table, n, H.panel, Placement(at), size * 0.92)
    p.neon.ring(size * 0.9, size * 0.06, n, neon, Placement(local(0, 0, table)))
    axis = axis_height(mount) - mount.height
    root = barrel_root(mount)
    breech = bore * k["breech"]
    back = -size * k["back"]
    # The breech, from behind the pin to the barrel's root, and the saddle under it.
    p.hull.cylinder(
        breech, root - back + 0.8, n, H.dark, Placement(local(back, 0, axis), yaw, QUARTER), bore
    )
    saddle = axis - table
    p.hull.box(
        [breech * 1.5, saddle, root - back],
        H.panel,
        Placement(local((root + back) / 2, 0, table), yaw),
    )
    # The cheeks, either side of the breech, and the pin across them.
    thick = size * k["cheek"]
    side = breech + size * k["gap"] + thick / 2
    rise = axis + bore * k["cheekRise"] - table
    for s in [-1, 1]:
        p.hull.box(
            [thick, rise, root - back + 1],
            H.panel,
            Placement(local((root + back) / 2, s * side, table), yaw),
        )
    pin = size * k["pin"]
    p.hull.cylinder(
        pin,
        side * 2 + thick,
        n,
        H.dark,
        Placement(local(0, -side - thick / 2, axis), yaw + math.pi / 2, QUARTER),
    )
    for s in [-1, 1]:
        p.neon.cylinder(
            pin * 0.6,
            0.3,
            n,
            neon,
            Placement(
                local(0, s * (side + thick / 2) + (0 if s > 0 else -0.3), axis),
                yaw + math.pi / 2,
                QUARTER,
            ),
        )


def draw_gun(p: Any, mount: Any, first: int, neon: Any) -> None:
    """Add a gun mount: its base and its barrels, barrel k recoiling as `Enemy.barrels[first + k]`.

    Each barrel ends at the muzzle its shots leave from, pointing the way they go. A mortar's barrel
    comes out of its breech, with no housing of its own.
    """
    mortar = mount.style == "mortar"
    if mortar:
        _mortar_base(p, mount, neon)
    else:
        _base(p, mount, neon)
    muzzles = mount_muzzles(mount)
    angles = barrel_angles(mount)
    length = max(1.0, mount.length - CAP)
    for k in range(len(muzzles)):
        m = muzzles[k]
        tip = boss_point(m[0], m[1], m[2])
        model_barrel(
            p,
            tip,
            angles[k] * DEG,
            length,
            first + k,
            mount.bore,
            False,
            None,
            True,
            not mortar,
            mount.trim is not False,
            MORTAR["sides"] if mortar else 5,
        )


def draw_laser(p: Any, mount: Any, neon: Any) -> None:
    """Add a laser mount: its base, and its emitter's barrel, coils and lens (WPN-06)."""
    _base(p, mount, neon)
    m = mount_muzzles(mount)[0]
    tip = boss_point(m[0], m[1], m[2])
    p.muzzle(tip, "laser", "forward", mount.bore, None, True, mount.length, m[3] * DEG)


def draw_missiles(p: Any, mount: Any, first: int, _neon: Any) -> None:
    """Add a missile mount: a block, its ports on it, port k's rocket `Enemy.launchers[first + k]`.

    Each port stands on the block, its mouth where the missiles leave (WPN-07).
    """
    spots = port_spots(mount)
    half = MISSILE_BLOCK.pitch / 2 + MISSILE_BLOCK.wall
    xs = [s[0] for s in spots]
    ys = [s[1] for s in spots]
    left = min(xs) - half
    right = max(xs) + half
    near = min(ys) - half
    far = max(ys) + half
    outline = [
        [-left, -near],
        [-right, -near],
        [-right, -far],
        [-left, -far],
    ]
    low = mount.height - MISSILE_BLOCK.depth
    p.hull.bevel_slab(outline, [low, mount.height - 0.6, mount.height], [0, 0.6], H.panel)
    for k in range(len(spots)):
        foot = boss_point(spots[k][0], spots[k][1], mount.height)
        p.muzzle(foot, "missile", "up", MISSILE_BLOCK.missile, first + k, True, MISSILE_BLOCK.well)


def draw_mount(p: Any, mount: Any, first: int, neon: Any) -> None:
    """Add a mount of any kind (see `draw_gun`, `draw_laser`, `draw_missiles`)."""
    if mount.kind == "gun":
        draw_gun(p, mount, first, neon)
    elif mount.kind == "laser":
        draw_laser(p, mount, neon)
    else:
        draw_missiles(p, mount, first, neon)


# A destroyed weapon's stump: its base's share of the mount's size, and its height.
STUMP = {"radius": 0.75, "height": 0.3, "missileRadius": 5.5}
# The charred top of a stump.
CHARRED = [0.03, 0.025, 0.02]


def draw_stump(p: Any, mount: Any) -> None:
    """Add the stump a destroyed weapon leaves where its mount stood (BOSS-18).

    A squat dark collar, its top charred.
    """
    if mount.kind == "missile":
        radius = STUMP["missileRadius"]
        height = MISSILE_BLOCK.depth * 0.6
        base = mount.height - MISSILE_BLOCK.depth
    else:
        radius = mount.size * STUMP["radius"]
        height = mount.size * STUMP["height"]
        base = mount.height
    at = boss_point(mount.at[0], mount.at[1], base)
    p.hull.cylinder(radius, height, 7, H.dark, Placement(at, math.pi / 7), radius * 0.8)
    top = boss_point(mount.at[0], mount.at[1], base + height + 0.02)
    p.bare.lathe([[radius * 0.78, 0], [0, 0]], 7, CHARRED, Placement(top, math.pi / 7))
