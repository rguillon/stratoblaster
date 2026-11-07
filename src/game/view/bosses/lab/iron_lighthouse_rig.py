# Copyright (c) 2026 Renaud Guillon
"""MB-IRON-LIGHTHOUSE-04, MB-IRON-LIGHTHOUSE-06: the Iron Lighthouse's rig.

Logical pixels, nose +Z, Y up. What moves that the fight does not need: the four propellers under
its rim spin (harder as it transforms, its leaves dropping open: it strains to stay up), and the
lens in its lantern revolves, two flares of light sweeping round its gallery like a lighthouse's
beams (faster once it has transformed). Nothing here is hit or fires: the lamp's laser is a mount
of the design (BOSS-58).
"""

import math

from game.config.bosses.lab.iron_lighthouse import (
    GALLERY,
    HOOP_LIFT,
    LANTERN_R,
    LANTERN_TOP,
    PROP_OUT,
    PROP_R,
    PROPS,
    TOWER_AT,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_reveal import ease, share
from game.view.bosses.final_boss_greebles import SHADE
from game.view.bosses.lab.iron_lighthouse_parts import N
from game.view.enemies.enemy_mesh import build_enemy_model
from render.babylon import new_transform_node
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


DEG = math.pi / 180
# The propellers: blades a propeller, their spin (radians a second) at rest and flat out.
BLADES = 4
SPIN = 11.0
SPIN_FAST = 24.0
# The lens: its turn (radians a second) at rest and once it has transformed; its flares' reach out
# from the lantern and their height.
LENS_TURN = 1.3
LENS_FAST = 2.6
FLARE_OUT = 15
FLARE_H = GALLERY + 3.4


def _blades(p: Any) -> None:
    """Draw a propeller round its centre (model origin): a hub and four pitched blades."""
    for k in range(BLADES):
        a = k * math.pi * 2 / BLADES
        q = [math.cos(a) * (PROP_R - 1) / 2, 0, math.sin(a) * (PROP_R - 1) / 2]
        p.bare.box([2.2, 0.4, PROP_R - 1], SHADE["light"], Placement(q, math.pi / 2 - a, 0, 0.3))
        tip = [math.cos(a) * (PROP_R - 1.6), 0.45, math.sin(a) * (PROP_R - 1.6)]
        p.neon.box([1.8, 0.12, 0.9], N, Placement(tip, math.pi / 2 - a))
    p.hull.cylinder(1.6, 1.2, 8, SHADE["mid"], Placement([0, -0.3, 0]), 1.1)


def _lens(p: Any) -> None:
    """Draw the revolving lens (model origin at the lantern's centre, at the gallery's floor).

    Brass-dark prism slats round the lamp, two bull's-eye panels facing out either way, and a flare
    of light out of each: a flat wedge of lamp-yellow over the gallery rail.
    """
    for k in range(8):
        a = k * math.pi / 4 + math.pi / 8
        q = [math.cos(a) * (LANTERN_R - 1), 1.2, math.sin(a) * (LANTERN_R - 1)]
        p.hull.box(
            [1.4, LANTERN_TOP - GALLERY - 2.6, 0.4], SHADE["light"], Placement(q, math.pi / 2 - a)
        )
    for s in [-1, 1]:
        eye = [s * (LANTERN_R - 0.6), 2.4, 0]
        p.neon.cylinder(1.5, 0.5, 8, N, Placement(eye, 0, 0, s * math.pi / 2))
        h = FLARE_H - GALLERY
        near = LANTERN_R + 0.4
        far = FLARE_OUT
        corners = [
            [s * near, h, -0.7],
            [s * far, h, -2.6],
            [s * far, h, 2.6],
            [s * near, h, 0.7],
        ]
        p.neon.face(corners, N)
        p.neon.face([corners[3 - k] for k in range(4)], N)


class LighthouseRig:
    """The Iron Lighthouse's propellers and revolving lens (see the module)."""

    def __init__(self, props: list[list[Any]], lens: list[Any]) -> None:
        # Per propeller: `[spin node, model]`; the lens: `[node, model]`.
        self.props = props
        self.lens = lens
        self.clock = 0.0

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Spin the propellers and turn the lens for `boss` (None: at rest)."""
        self.clock += dt
        strain = 0.0
        done = False
        if boss != None:
            done = boss.form >= 1
            if boss.transforming_into == 1:
                strain = ease(share(boss.transform, [0, 0.5]))
            elif done:
                strain = 0.6
        speed = SPIN + (SPIN_FAST - SPIN) * strain
        for prop in self.props:
            prop[0].rotation.y = (prop[0].rotation.y + speed * dt) % (math.pi * 2)
            prop[1].sync(lit, dt)
        turn = LENS_FAST if done else LENS_TURN
        self.lens[0].rotation.y = (self.lens[0].rotation.y + turn * dt) % (math.pi * 2)
        self.lens[1].sync(lit, dt)


def _model(name: str, root: Any, at: Vec3, draw: Any, neon: Any, breath: Any) -> list[Any]:
    """Return `[node, model]`: a model drawn by `draw` on a node of `root` at `at` (model)."""
    scene = root.getScene()
    node = new_transform_node(name, scene)
    node.parent = root
    node.position.set(at[0], at[1], at[2])
    model = build_enemy_model(name, scene, neon, draw, breath)
    model.root.parent = node
    return [node, model]


def build_lighthouse_rig(root: Any, neon: Any, breath: Any) -> LighthouseRig:
    """Return the Iron Lighthouse's rig on `root` (the boss model's)."""
    props: list[list[Any]] = []
    for i in range(len(PROPS)):
        a = PROPS[i] * DEG
        at = boss_point(PROP_OUT * math.cos(a), PROP_OUT * math.sin(a), HOOP_LIFT)
        prop = _model("iron-lighthouse-prop-" + str(i), root, at, _blades, neon, breath)
        prop[0].rotation.y = i * 0.6
        props.append(prop)
    centre = boss_point(TOWER_AT[0], TOWER_AT[1], GALLERY)
    lens = _model("iron-lighthouse-lens", root, centre, _lens, neon, breath)
    return LighthouseRig(props, lens)


def rig_triangles(_unfold: float) -> list[Any]:
    """Return the rig's triangles for the wholeness check (BOSS-52): none.

    The propellers spin inside their ducts, the lens inside its lantern (its flares are light).
    """
    return []
