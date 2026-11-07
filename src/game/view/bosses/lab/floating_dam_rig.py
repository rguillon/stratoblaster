# Copyright (c) 2026 Renaud Guillon
"""FB-FLOATING-DAM-02, FB-FLOATING-DAM-12: the Floating Dam's rig (what the fight does not need).

Logical pixels, nose +Z, Y up. Its four lift fans spin in their ducts under the wall's back (faster
while it transforms); once the spillway's cover has burst, a torrent of light pours down the
stepped chute into the basin (D-228's custom rigs, BOSS-46). Nothing here is hit or fires.
"""

import math

from game.config.bosses.lab.floating_dam import BASIN, CREST_Y, NOTCH, WEIR_TOP, crest_y
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.lab.floating_dam_parts import N
from game.view.bosses.world_1_organic_kit import M
from game.view.enemies.enemy_mesh import build_enemy_model
from render.babylon import new_transform_node, set_enabled
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# The lift fans' centres (config) under the wall's back, and their spin (radians a second).
FAN_AT = [  # type: list[list[float]]
    [-78, crest_y(78) + 16],
    [-40, crest_y(40) + 16],
    [40, crest_y(40) + 16],
    [78, crest_y(78) + 16],
]
SPIN = [5.0, 14.0]
# The torrent: its stripes' pitch down the chute (model), how fast they run, and the share of the
# second transformation it starts at (the cover has burst by then).
PITCH = 3.8
RUN = 9.0
POURS_AT = 0.5


def _model(name: str, root: Any, draw: Any, neon: Any, breath: Any) -> list[Any]:
    """Return `[node, model]`: a model drawn by `draw` (model space) on a node of `root`."""
    scene = root.getScene()
    node = new_transform_node(name, scene)
    node.parent = root
    model = build_enemy_model(name, scene, neon, draw, breath)
    model.root.parent = node
    return [node, model]


def _draw_rotor(p: Any) -> None:
    """Draw a lift fan's rotor round the origin: a hub and six blades, their tips lit."""
    p.hull.cylinder(2, 1.6, 6, M.panel, Placement([0, 0, 0]))
    for k in range(6):
        a = k * math.pi / 3
        q = [math.sin(a) * 4.4, 0.4, math.cos(a) * 4.4]
        p.hull.box([1.6, 0.4, 5.4], M.base, Placement(q, a, 0, 0.35))
        p.neon.box([1.2, 0.3, 0.6], N, Placement([math.sin(a) * 7, 0.5, math.cos(a) * 7], a))


def _draw_torrent(p: Any) -> None:
    """Draw the torrent's stripes down the chute and over the basin (as at the start of a run)."""
    for k in range(5):
        d = 6.4 + k * PITCH
        h = WEIR_TOP - (k + 1) * 3.2 + 0.25 if k < 4 else BASIN[2] + 0.25
        q = boss_point(0, CREST_Y - d, h)
        p.neon.box([2 * NOTCH - 3, 0.2, 1.1], N, Placement(q))


class DamRig:
    """The Floating Dam's lift fans and torrent (see the module)."""

    def __init__(self, fans: list[list[Any]], torrent: list[Any]) -> None:
        self.fans = fans
        self.torrent = torrent
        self.clock = 0.0
        self.turn = 0.0

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Spin the fans and run the torrent for `boss` (None: at rest)."""
        self.clock += dt
        busy = boss != None and boss.transforming_into > 0
        self.turn += SPIN[1 if busy else 0] * dt
        for k in range(len(self.fans)):
            fan = self.fans[k]
            fan[0].rotation.y = self.turn * (1 if k % 2 == 0 else -1)
            fan[1].sync(lit, dt)
        pours = False
        if boss != None:
            pours = boss.form >= 2 or (boss.transforming_into == 2 and boss.transform >= POURS_AT)
        set_enabled(self.torrent[0], pours)
        if pours:
            run = (self.clock * RUN) % PITCH
            self.torrent[0].position.set(0, 0, run)
            self.torrent[1].sync(lit, dt)


def build_dam_rig(root: Any, neon: Any, breath: Any) -> DamRig:
    """Return the Floating Dam's rig on `root` (the boss model's)."""
    fans: list[list[Any]] = []
    for k in range(len(FAN_AT)):
        f = FAN_AT[k]
        view = _model("floating-dam-fan-" + str(k), root, _draw_rotor, neon, breath)
        q = boss_point(f[0], f[1], -3)
        view[0].position.set(q[0], q[1], q[2])
        fans.append(view)
    torrent = _model("floating-dam-torrent", root, _draw_torrent, neon, breath)
    set_enabled(torrent[0], False)
    return DamRig(fans, torrent)


def rig_triangles(_unfold: float) -> list[Any]:
    """Return the rig's triangles for the wholeness check (BOSS-52): none.

    Its rotors spin in the core's ducts; the torrent lies on the chute's steps.
    """
    return []
