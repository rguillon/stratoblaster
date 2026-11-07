# Copyright (c) 2026 Renaud Guillon
"""The gun mounts of the bosses: every bullet, laser and missile leaves one (BOSS-23, BOSS-58).

Three models for all of them, as for the enemies' weapons (WPN-01 to WPN-07):

- `gun`: a turret dome (or a fixed base) and its barrels, each recoiling as it fires. Its barrels
  are side by side, parallel (`gap` px apart), taking turns: a turret fires a fan one bullet at a
  time, turning across it (a sweep); or they are all round a hub (`ring`: a rotor, one barrel per
  bullet of its rings).
- `laser`: a laser emitter's hexagonal barrel, its coils and its lens (WPN-06), on a turret or not.
- `missile`: a block of hexagonal missile ports (WPN-07), the missiles launched straight up.

A mount is a record: `id`, `piece` (the part id or `core` it is on: it goes with it), `kind`,
`at` (its pivot, px from the boss's centre, X right, Y up, its nose at -Y), `height` (its base's
height above the playfield), `turret` (it turns the way it fires next, BOSS-29), `restDeg` (where
it points at rest, degrees from the boss's nose, positive towards its right: the screen's left),
and its sizes. The boss's model draws it from the same numbers (`view/bosses/boss_gun_models.py`),
so the barrels the player sees are where the shots leave from, and the way they go.
"""

import math

from game.config.record import record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


DEG = math.pi / 180

KINDS = ["gun", "laser", "missile"]
# Barrels side by side are at least this many bores apart (centre to centre).
MIN_GAP = 2.6
LAYOUTS = ["fan", "ring"]

# Shares of a mount's `size` (its dome's radius): its barrels' axis is `axis` of it above its base,
# their roots `root` of it out from its pivot (`hubRoot` round a rotor's hub).
GUN_SHAPE = record({"axis": 0.38, "root": 0.45, "hubRoot": 0.8, "domeHeight": 0.5})

# A missile mount's ports, for the boss missiles (`boss_kit.MISSILE`, hit radius `missile`):
# `pitch` px between two ports' centres, each standing `well` px high on the block, the block
# `wall` px past the outer ones and `depth` px deep under them.
MISSILE_BLOCK = record({"pitch": 6.4, "well": 4.5, "wall": 1.6, "depth": 3, "missile": 5})


def _known(mount: Any) -> None:
    if mount.kind not in KINDS:
        raise ValueError('Unknown boss mount kind "' + mount.kind + '"')


def gun_mount(mount_id: str, piece: str, at: list[Any], height: float, options: Any) -> Any:
    """Return a gun mount (see the module's doc) on `piece`, its pivot at `at`, `height` high.

    `options`: `size` (the dome's radius), `barrels` (how many), `bore` and `length` (each
    barrel's), and optionally `layout` ("fan" for barrels side by side, or "ring"), `gap`, `restDeg`
    and `turret` (true by default: a fixed mount points `restDeg` for good), `trim` (whether its
    barrels have an edge trim: by default only a single barrel's has, not a row's or a rotor's),
    `style` (`dome`, by default, or `mortar`: a single fat barrel in a cradle on a turntable) and
    `axis` (its barrels' axis height, a share of `size` over its base; `GUN_SHAPE.axis` by default).
    Barrels side by side are at least `MIN_GAP` bores apart, and the dome covers their row.
    """
    o = record(options)
    layout = o.layout if o.layout != None else "fan"
    if layout not in LAYOUTS:
        raise ValueError('Unknown gun layout "' + layout + '"')
    gap = o.gap if o.gap != None else 0
    size = o.size
    if layout == "fan" and o.barrels > 1:
        gap = max(gap, o.bore * MIN_GAP)
        size = max(size, (o.barrels - 1) * gap / 2 + o.bore * 1.6)
    return record({
        "id": mount_id,
        "piece": piece,
        "kind": "gun",
        "at": [at[0], at[1]],
        "height": height,
        "size": size,
        "barrels": o.barrels,
        "bore": o.bore,
        "length": o.length,
        "layout": layout,
        "gap": gap,
        "restDeg": o.restDeg if o.restDeg != None else 0,
        "turret": o.turret is not False,
        "trim": o.trim if o.trim != None else o.barrels <= 1,
        "style": o.style if o.style != None else "dome",
        "axis": o.axis if o.axis != None else GUN_SHAPE.axis,
    })


def laser_mount(mount_id: str, piece: str, at: list[Any], height: float, options: Any) -> Any:
    """Return a laser mount on `piece`: its emitter's barrel `length` long, `bore` round.

    `options`: `size` (its dome's radius, or its base's when fixed), `bore`, `length`, and
    optionally `restDeg` and `turret` (false by default: a laser points `restDeg`, down the screen,
    unless it is on a turret that follows the player, BOSS-31).
    """
    o = record(options)
    return record({
        "id": mount_id,
        "piece": piece,
        "kind": "laser",
        "at": [at[0], at[1]],
        "height": height,
        "size": o.size,
        "barrels": 1,
        "bore": o.bore,
        "length": o.length,
        "layout": "fan",
        "gap": 0,
        "restDeg": o.restDeg if o.restDeg != None else 0,
        "turret": o.turret is True,
    })


def missile_mount(mount_id: str, piece: str, at: list[Any], height: float, ports: int) -> Any:
    """Return a missile mount on `piece`: a block of `ports` ports in two columns.

    The block's top at `height`, centred on `at`, its ports standing on it (`MISSILE_BLOCK`). One
    port (a single silo) is a column of its own.
    """
    return record({
        "id": mount_id,
        "piece": piece,
        "kind": "missile",
        "at": [at[0], at[1]],
        "height": height,
        "barrels": ports,
        "turret": False,
        "restDeg": 0,
    })


def barrel_angles(mount: Any) -> list[float]:
    """Return the way each barrel of a gun mount points at rest, degrees from the boss's nose."""
    n = mount.barrels
    rest = mount.restDeg
    if mount.layout == "ring":
        return [rest + (360 * k) / n for k in range(n)]
    return [rest for _k in range(n)]


def barrel_across(mount: Any) -> list[float]:
    """Return how far across each barrel of a gun mount is from its pivot (its `gap`s)."""
    n = mount.barrels
    if mount.layout == "ring":
        return [0 for _k in range(n)]
    return [(k - (n - 1) / 2) * mount.gap for k in range(n)]


def barrel_root(mount: Any) -> float:
    """Return how far from a gun mount's pivot its barrels start (in its dome, round its hub)."""
    share: float = GUN_SHAPE.hubRoot if mount.layout == "ring" else GUN_SHAPE.root
    return float(mount.size * share)


def axis_height(mount: Any) -> float:
    """Return the height of a gun or laser mount's barrels' axis above the playfield."""
    share = mount.axis if mount.axis != None else GUN_SHAPE.axis
    return float(mount.height + mount.size * share)


def along(at: list[Any], angle_deg: float, distance: float, across: float) -> list[float]:
    """Return the point `distance` from `at` the way `angle_deg` points, `across` to its side.

    Degrees from the boss's nose (down the screen, -Y), positive towards its right (the screen's
    left, -X); `across` is towards the barrel's own left (the screen's +X for one pointing down).
    """
    a = angle_deg * DEG
    dx = -math.sin(a)
    dy = -math.cos(a)
    return [at[0] + dx * distance - dy * across, at[1] + dy * distance + dx * across]


def port_spots(mount: Any) -> list[list[float]]:
    """Return the centres of a missile mount's ports, `[x, y]`, in two columns, front row first."""
    n = mount.barrels
    pitch = MISSILE_BLOCK.pitch
    if n == 1:
        return [[mount.at[0], mount.at[1]]]
    rows = math.ceil(n / 2)
    result: list[list[float]] = []
    for k in range(n):
        row = math.floor(k / 2)
        col = k % 2
        x = mount.at[0] + (col - 0.5) * pitch
        y = mount.at[1] - (row - (rows - 1) / 2) * pitch
        result.append([x, y])
    return result


def mount_muzzles(mount: Any) -> list[list[float]]:
    """Return where a mount's shots leave from, at rest: one `[x, y, height, angle°]` per barrel.

    A gun's barrels' tips and the way each points; a laser's lens; a missile mount's ports
    (`[x, y, height]`: its missiles go straight up first).
    """
    _known(mount)
    if mount.kind == "missile":
        top = mount.height + MISSILE_BLOCK.well
        return [[spot[0], spot[1], top] for spot in port_spots(mount)]
    reach = barrel_root(mount) + mount.length
    h = axis_height(mount)
    result: list[list[float]] = []
    angles = barrel_angles(mount)
    across = barrel_across(mount)
    for k in range(len(angles)):
        tip = along(mount.at, angles[k], reach, across[k])
        result.append([tip[0], tip[1], h, angles[k]])
    return result


def mount_order(mounts: list[Any]) -> list[int]:
    """Return the index of each mount's first barrel among the boss's (`Enemy.barrels`).

    Or of its first port among its launchers (`Enemy.launchers`): gun barrels and missile ports
    are numbered in the order of the mounts, each kind on its own; a laser's is its lens (0).
    """
    guns = 0
    ports = 0
    result: list[int] = []
    for mount in mounts:
        if mount.kind == "gun":
            result.append(guns)
            guns += mount.barrels
        elif mount.kind == "missile":
            result.append(ports)
            ports += mount.barrels
        else:
            result.append(0)
    return result
