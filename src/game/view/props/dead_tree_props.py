"""Dead trees of the desert (D-214), drawn as imposters

Sizes in model units, standing on Y = 0. Bare, bleached wood: limbs forking into smaller ones
(`render/geometry/branches.py`), each shaded its own way. The levels draw a picture of each baked
from these models (`imposter_bake_visual`), as they do the living trees (D-212). Each also has a
stand-in, its trunk and main limbs in a few facets, that only casts its shadow.
"""

import math

from game.view.props.tree_geometry import tree_geometry
from render.geometry.branches import Branching, branch, limb
from render.geometry.solids import SolidBuilder
from render.scenery.scenery_look import PropGeometry

# Sun-bleached wood, grey wood, wood charred dark, and the dry stems of a brush.
BLEACHED = [0.84, 0.78, 0.68]
GREY = [0.74, 0.71, 0.66]
CHARRED = [0.46, 0.4, 0.35]
BRUSH = [0.8, 0.66, 0.46]

# A spreading tree: three limbs off the trunk, forking three times, reaching up and out.
SPREADING = Branching(3, 0.75, 0.68, 1, 0.35, 0.15, 0.65, 0.08)
# The short branches off a dead pine's trunk, drooping, forking once.
WHORL = Branching(2, 0.5, 0.5, 0.9, 0.4, -0.15, 0.6, 0.08)
# The lowest rings of a dead pine whose whole branches fork once.
FORKED_WHORLS = 4
# A brush: thin stems forking into twigs, up and out.
TWIGS = Branching(3, 0.6, 0.6, 0.9, 0.5, 0.1, 0.6, 0.12)


def dead_oak() -> PropGeometry:
    """A dead broad tree: a short leaning trunk forking into bare limbs, up and out."""
    s = SolidBuilder()
    shadow = SolidBuilder()
    branch(s, [0, 0, 0], [0.05, 1, 0.03], [3.2, 0.6], 3, SPREADING, BLEACHED, 7)
    # Its trunk and main limbs: the same seed, forking once.
    branch(shadow, [0, 0, 0], [0.05, 1, 0.03], [3.2, 0.6], 1, SPREADING, BLEACHED, 7)
    return tree_geometry(s, shadow)


def dead_pine() -> PropGeometry:
    """A dead conifer: a tall straight trunk broken at the top, rings of short drooping branches
    round it, shorter and more often broken going up."""
    s = SolidBuilder()
    shadow = SolidBuilder()
    top = [0.12, 9.6, 0.05]
    limb(s, [0, 0, 0], top, [0.36, 0.07], 6, GREY)
    limb(shadow, [0, 0, 0], top, [0.36, 0.07], 3, GREY)
    whorls = 8
    for k in range(whorls):
        up = k / whorls
        y = 1.8 + k * 1.0
        at = [top[0] * y / top[1], y, top[2] * y / top[1]]
        for n in range(3):
            seed = 90 + k * 3 + n
            a = (n / 3 + k * 0.37) * math.pi * 2
            # Some branches broke off short.
            broken = 0.4 if (k + n) % 3 == 0 else 1
            length = 1.9 * (1 - up * 0.7) * broken
            out = [math.cos(a), -0.25, math.sin(a)]
            depth = 1 if broken == 1 and k < FORKED_WHORLS else 0
            branch(s, at, out, [length, 0.15 * (1 - up * 0.5)], depth, WHORL, GREY, seed)
    return tree_geometry(s, shadow)


def snag() -> PropGeometry:
    """A snag: a thick trunk snapped off, charred, splinters on its broken top, one limb left and
    the stub of another."""
    s = SolidBuilder()
    shadow = SolidBuilder()
    top = [0.25, 4.2, 0.1]
    limb(s, [0, 0, 0], top, [0.62, 0.44], 7, CHARRED)
    limb(shadow, [0, 0, 0], top, [0.62, 0.44], 3, CHARRED)
    for k in range(3):
        a = k * 2.1 + 0.3
        foot = [top[0] + math.cos(a) * 0.3, top[1], top[2] + math.sin(a) * 0.3]
        tip = [foot[0] + math.cos(a) * 0.15, foot[1] + 0.5 + k * 0.35, foot[2] + math.sin(a) * 0.15]
        limb(s, foot, tip, [0.14, 0], 3, CHARRED)
    branch(s, [0.12, 2.8, 0.05], [1, 0.9, 0.2], [2.4, 0.3], 2, SPREADING, CHARRED, 51)
    branch(shadow, [0.12, 2.8, 0.05], [1, 0.9, 0.2], [2.4, 0.3], 0, SPREADING, CHARRED, 51)
    limb(s, [0.1, 1.9, 0], [-0.7, 2.3, -0.3], [0.2, 0.12], 4, CHARRED)
    return tree_geometry(s, shadow)


def dead_bush() -> PropGeometry:
    """A dry brush: a tangle of thin stems from one root, forking into twigs."""
    s = SolidBuilder()
    shadow = SolidBuilder()
    stems = 7
    for k in range(stems):
        a = (k / stems) * math.pi * 2 + 0.4
        lean = 0.55 + (k % 3) * 0.2
        out = [math.cos(a) * lean, 1, math.sin(a) * lean]
        branch(s, [0, 0, 0], out, [1.5, 0.14], 2, TWIGS, BRUSH, 70 + k)
        branch(shadow, [0, 0, 0], out, [1.5, 0.14], 0, TWIGS, BRUSH, 70 + k)
    return tree_geometry(s, shadow)
