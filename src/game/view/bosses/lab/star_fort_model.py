# Copyright (c) 2026 Renaud Guillon
"""FB-STAR-FORT-01 to FB-STAR-FORT-04: the Star Fort, the Lab's L-25 final boss.

Logical pixels, nose +Z, Y up (towards the camera). A gigantic flying star fort seen from above: a
slab of floating rock ringed by a moat of glowing energy, on it a five-pointed Vauban fortress,
its scarped platform at the parade ground's height, its nose and side bastions filled up to the
ramparts, its curtains' ramparts, a ravelin's earthwork in front of each forward curtain, barracks
and the rotor's pit on the parade ground. Its rear bastions and keep are moving pieces, its
flagstones and shutters armour, its pylons, redoubts, cavalier and gatehouse parts
(`star_fort_parts`); the moat's energy and the keep's pinnacle are its rig (`star_fort_rig`).
A machine, not a creature (user request, 2026-11-06).
"""

import math

from game.config.bosses.lab.star_fort import (
    BASTIONS,
    CURTAIN_GUN,
    FLANK,
    KEEP_AT,
    KEEP_R,
    LASER_AT,
    MOAT,
    MOAT_H,
    NOSE_GUN,
    PARADE,
    RAVELIN_DEG,
    RAVELIN_TOP,
    ROCK_TOP,
    ROTOR_AT,
    SIDE_GUN,
    SIDE_MORTAR_GUN,
    STAR_FORT,
    WALL_TOP,
    bastion_outline,
    polar,
    ravelin_outline,
)
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.star_fort_parts import (
    EARTH,
    PAVE,
    SCARP,
    SLATE,
    STONE,
    N,
    bar,
    cavalier,
    flagstones,
    gatehouse,
    hatch,
    hatch_frame,
    keep,
    outline_of,
    parapet,
    pt,
    pylon,
    rear_bastion,
    redoubt,
    scarped,
)
from game.view.bosses.lab.star_fort_rig import build_fort_rig, fort_triangles
from game.view.bosses.mini_boss_greebles import lamps
from game.view.bosses.world_1_organic_kit import M
from render.geometry.rocks import rough_chunk
from render.geometry.rough import Roughness
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# The rear bastions' capitals (moving pieces, drawn on their own).
REAR = [144, -144]
# The rock slab: its rim's radius at each of `ROCK_SIDES` corners (a rough, lumpy outline).
ROCK_SIDES = 20
ROCK_RIM = [81, 77, 83, 79, 76, 82, 80, 85, 78, 81, 77, 83, 80, 76, 82, 79, 84, 78, 81, 77]
# Its rampart's width along the curtains.
RAMPART = 5.5


def _rear(capital: float) -> bool:
    return capital in REAR


def _star() -> list[list[float]]:
    """Return the fort's platform outline: every bastion but the rear ones (their gorges)."""
    points: list[list[float]] = []
    for capital in [0, 72, 144, 216, 288]:
        c = capital if capital <= 180 else capital - 360
        if _rear(c):
            points.append(polar(FLANK[0], c - FLANK[1]))
            points.append(polar(FLANK[0], c + FLANK[1]))
        else:
            points.extend(bastion_outline(c))
    return points


def _curtains() -> list[list[list[float]]]:
    """Return each curtain's outer edge, `[from, to]`, going round."""
    caps = [0, 72, 144, 216, 288]
    result: list[list[list[float]]] = []
    for k in range(5):
        a = caps[k] + FLANK[1]
        b = caps[(k + 1) % 5] + (360 if k == 4 else 0) - FLANK[1]
        result.append([polar(FLANK[0], a), polar(FLANK[0], b)])
    return result


def _rock(p: Any) -> None:
    """Draw the slab of floating rock under it, its rim lumpy, tapering away beneath."""
    rim = []
    for k in range(ROCK_SIDES):
        a = 360 * k / ROCK_SIDES + 4
        rim.append(polar(ROCK_RIM[k], a))
    p.hull.bevel_slab(outline_of(rim), [-20, -4, ROCK_TOP], [26, 1.2], SCARP, None, EARTH)
    for k in range(9):
        at = polar(ROCK_RIM[k * 2] - 1.5, 360 * k * 2 / ROCK_SIDES + 4)
        rough_chunk(
            p.flesh,
            [4 + k % 3, 3, 4],
            6,
            SCARP,
            Roughness(0.25, 0.15, 0.3, k + 3),
            Placement(pt(at[0], at[1], ROCK_TOP - 1)),
        )
    # The moat: a dark channel, its energy lit in it.
    for k in range(24):
        a0 = 15 * k
        a1 = a0 + 15
        channel = [
            polar(MOAT[0] - 1.5, a0),
            polar(MOAT[1] + 1.5, a0),
            polar(MOAT[1] + 1.5, a1),
            polar(MOAT[0] - 1.5, a1),
        ]
        p.bare.slab(outline_of(channel), [ROCK_TOP - 0.2, ROCK_TOP + 0.4], M.dark)
        band = [polar(MOAT[0], a0), polar(MOAT[1], a0), polar(MOAT[1], a1), polar(MOAT[0], a1)]
        p.neon.slab(outline_of(band), [MOAT_H - 0.4, MOAT_H - 0.1], N)


def _enceinte(p: Any) -> None:
    """Draw the fort (FB-STAR-FORT-02): its scarped platform, bastions, curtains and ravelins."""
    star = _star()
    scarped(p, star, [ROCK_TOP - 0.3, PARADE], SCARP, PAVE)
    for capital in BASTIONS:
        if _rear(capital):
            continue
        pts = bastion_outline(capital)
        p.hull.slab(outline_of(pts), [PARADE - 0.2, WALL_TOP], STONE)
        parapet(p, pts, WALL_TOP, capital == 0)
        lamps(p.neon, [pt(pts[2][0] * 0.9, pts[2][1] * 0.9, WALL_TOP + 0.2)], 1.2, N)
    for edge in _curtains():
        a = edge[0]
        b = edge[1]
        k = (FLANK[0] - RAMPART) / FLANK[0]
        strip = [a, b, [b[0] * k, b[1] * k], [a[0] * k, a[1] * k]]
        p.hull.slab(outline_of(strip), [PARADE - 0.2, WALL_TOP], STONE)
        parapet(p, [a, b], WALL_TOP, False)
    for side in [-1, 1]:
        pts = ravelin_outline(side * RAVELIN_DEG)
        scarped(p, pts, [ROCK_TOP - 0.3, RAVELIN_TOP], SCARP, STONE)
        parapet(p, [pts[0], pts[1], pts[2]], RAVELIN_TOP, True)


def _parade(p: Any) -> None:
    """Draw the parade ground's buildings: barracks, the rotor's pit, the keep's footing."""
    for side in [-1, 1]:
        at = polar(21, side * 40)
        yaw = side * 40 * math.pi / 180
        p.hull.box([11, 3.4, 4.4], STONE, Placement(pt(at[0], at[1], PARADE), yaw), SLATE)
        p.neon.box([9, 0.5, 0.3], N, Placement(pt(at[0], at[1], PARADE + 1.6), yaw))
        well = polar(16, side * 115)
        p.hull.cylinder(2, 1.2, 8, STONE, Placement(pt(well[0], well[1], PARADE)))
    pit = pt(ROTOR_AT[0], ROTOR_AT[1], PARADE - 0.3)
    p.hull.cylinder(6.4, 0.6, 8, M.dark, Placement(pit, math.pi / 8))
    foot = pt(KEEP_AT[0], KEEP_AT[1], PARADE - 0.3)
    p.hull.cylinder(KEEP_R + 2.2, 0.6, 8, SCARP, Placement(foot, math.pi / 8))
    p.neon.ring(KEEP_R + 2.25, 0.3, 8, N, Placement([foot[0], PARADE + 0.1, foot[2]], math.pi / 8))
    # Paths from the gates of the bastions to the keep.
    for capital in [0, 72, -72]:
        start = polar(14, capital)
        bar(p.bare, [start[0], start[1], PARADE + 0.05], polar(30, capital), [2.4, 0.1], SLATE)


def _gun(gun: list[float], side: float) -> list[float]:
    return [side * gun[0], gun[1]]


def _hatches() -> Any:
    """Return the drawings of the shutters over its embrasures and of what they leave."""
    result: Any = {}
    for name_gun in [
        ["nose", NOSE_GUN],
        ["side", SIDE_GUN],
        ["mortar", SIDE_MORTAR_GUN],
        ["curtain", CURTAIN_GUN],
    ]:
        name: Any = name_gun[0]
        gun: Any = name_gun[1]
        for side_name in [["left", -1], ["right", 1]]:
            at = _gun(gun, -1 if side_name[0] == "left" else 1)
            result[name + "-" + side_name[0] + "-hatch"] = {
                "whole": hatch(at, WALL_TOP),
                "frame": hatch_frame(at, WALL_TOP),
            }
    result["salient-laser-hatch"] = {
        "whole": hatch(LASER_AT, WALL_TOP),
        "frame": hatch_frame(LASER_AT, WALL_TOP),
    }
    result["rotor-hatch"] = {
        "whole": hatch(ROTOR_AT, PARADE),
        "frame": hatch_frame(ROTOR_AT, PARADE),
    }
    return result


def build_star_fort(scene: Any) -> Any:
    """FB-STAR-FORT-01, FB-STAR-FORT-04: the Star Fort.

    A five-pointed star fort about 5.5 L across on its rock, rose lights (shown yellow): its
    cavalier's turret, its ravelins' guns and its embrasures (their mounts, drawn by
    `build_boss_model`, BOSS-58). Its rear bastions swing out, then its keep rises, as it
    transforms (FB-STAR-FORT-10, FB-STAR-FORT-11).
    """

    def core(p: Any) -> None:
        _rock(p)
        _enceinte(p)
        _parade(p)

    armour = _hatches()
    armour["bastion-right"] = {"whole": rear_bastion(1)}
    armour["bastion-left"] = {"whole": rear_bastion(-1)}
    armour["keep"] = {"whole": keep}
    armour["flagstones"] = {"whole": flagstones}
    return build_boss_model(
        STAR_FORT,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "pylon-left": pylon,
                "pylon-right": pylon,
                "ravelin-left": redoubt,
                "ravelin-right": redoubt,
                "cavalier": cavalier,
                "gatehouse": gatehouse,
            },
            "rig": {"build": build_fort_rig, "triangles": fort_triangles},
            "armour": armour,
        },
    )
