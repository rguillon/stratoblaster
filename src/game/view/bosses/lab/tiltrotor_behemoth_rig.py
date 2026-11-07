# Copyright (c) 2026 Renaud Guillon
"""FB-TILTROTOR-BEHEMOTH-05, -10, -11: the Tiltrotor Behemoth's view rig.

Logical pixels, nose +Z, Y up. Visual only: the sim knows nothing of it (no part, no muzzle).

- Its rotor nacelles (`tiltrotor_behemoth_nacelle`), standing in their wingtip cradles, the rotors
  turning. At its first transformation each morphs into a turbine cannon, step by step: the rotor
  spins down to a stop, its blades fold back along the nacelle, the nacelle tilts forward in its
  cradle; as the cannon part takes over (drawn as the same tilted nacelle, its blades folded) it
  slides in along the wing's leading edge onto its sponson, its spinner's petals opening like a
  flower round the cannon's turret, which then rises out of it.
- Its wings' leading-edge slats, riding the outer wing halves: once the halves have stowed along
  the fuselage at its second transformation, they flip up into walls along the stowed wing.
- Its rear ramp, hanging open under the tail; at its second transformation it swings up shut.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.tiltrotor_behemoth import (
    CANNON_AT,
    CANNON_FROM,
    CENTRE_X,
    CHORD,
    NACELLE_AT,
    NACELLE_H,
    NACELLE_LENGTH,
    OUTER_H,
    TAIL,
    TILTROTOR_BEHEMOTH,
    WING_TIP_X,
)
from game.config.bosses.moving_regions import motion_value
from game.view.bosses.boss_armour import place
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_reveal import ease, share
from game.view.bosses.lab.tiltrotor_behemoth_nacelle import (
    BLADE_FOLD,
    BLADE_ROOT,
    BLADE_TURNS,
    HUB_HEIGHT,
    HUB_Y,
    NOSE_Y,
    PETAL_BASE,
    PETAL_LEAN,
    PETAL_OPEN,
    PETAL_TURNS,
    draw_blade,
    draw_body,
    draw_petal,
    drawn,
    flat,
    nacelle_layers,
    petal_layers,
    posed,
)
from game.view.bosses.region_motion import node_pose, progress
from game.view.bosses.world_1_organic_kit import M
from game.view.enemies.enemy_mesh import build_enemy_model
from render.babylon import new_transform_node, set_enabled
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["tiltrotor-behemoth"]
QUARTER = math.pi / 2
THIRD = 2 * math.pi / 3
# The rotors' spin (radians a second).
SPIN = 7
# Of the first transformation: the rotors spinning down, the blades folding, the nacelles tilting
# (done as the cannons take over, `BOSS_LOOK.reveal.swing[0]`), the petals opening.
SPIN_DOWN = [0, 0.14]
FOLD = [0.1, 0.26]
TILT = [0.22, 0.4]
PETALS = [0.45, 0.7]
# Of the second: the slats flipping up once the wing halves have stowed, the ramp shutting.
SLATS = [0.6, 0.8]
RAMP = [0.72, 0.95]
# The slats: along each outer wing's leading edge `[x0, x1]`, their depth and thickness.
SLAT_X = [CENTRE_X + 2.5, WING_TIP_X - 2]
SLAT_DEPTH = 4.6
SLAT_THICK = 0.8
# The ramp: its hinge's height at the roof's end, its width and length.
RAMP_H = 8.6
RAMP_WIDTH = 22
RAMP_LENGTH = 14


def phase(boss: Any, form: int) -> float:
    """Return how far transformation `form` has gone for `boss` (None: not yet), 0 to 1."""
    if boss == None:
        return 0
    if boss.form >= form:
        return 1
    if boss.transforming_into != form:
        return 0
    value: float = boss.transform
    return value


def pivots() -> list[Vec3]:
    """Return the nacelles' pivots (model space): right, then left."""
    return [
        boss_point(NACELLE_AT[0], NACELLE_AT[1], NACELLE_H),
        boss_point(-NACELLE_AT[0], NACELLE_AT[1], NACELLE_H),
    ]


def docked_fronts(i: int) -> list[Vec3]:
    """Return nacelle `i`'s nose (model space) docked on its sponson, and slid out to the wingtip.

    As the cannon part's nose moves (its root slides from `CANNON_FROM` to `CANNON_AT`).
    """
    side = 1 if i == 0 else -1
    lead = NACELLE_LENGTH + 3 - NOSE_Y
    end = boss_point(side * CANNON_AT[0], CANNON_AT[1] + lead, NACELLE_H)
    start = boss_point(side * CANNON_FROM[0], CANNON_FROM[1] + lead, NACELLE_H)
    return [end, start]


def wing_region(side: str) -> Any:
    """Return the outer wing half `side` (`right` or `left`)'s moving region (the design's)."""
    for region in TILTROTOR_BEHEMOTH.armour:
        if region.id == "wing-" + side:
            return region
    return None


def slat_hinge(i: int) -> Vec3:
    """Return slat `i`'s hinge (model space, its wing as drawn): along its leading edge, on top."""
    side = 1 if i == 0 else -1
    return boss_point(side * (SLAT_X[0] + SLAT_X[1]) / 2, CHORD[0], OUTER_H[1])


def ramp_hinge() -> Vec3:
    """Return the ramp's hinge (model space): across the roof's end, low."""
    return boss_point(0, TAIL, RAMP_H)


def draw_slat(p: Any) -> None:
    """Draw a slat lying back from its hinge (along local -Z), a lit strip along its far edge."""
    length = SLAT_X[1] - SLAT_X[0]
    p.hull.box([length, SLAT_THICK, SLAT_DEPTH], M.panel, Placement([0, 0, -SLAT_DEPTH / 2]))
    p.neon.box([length - 2, 0.3, 0.5], N, Placement([0, SLAT_THICK, -SLAT_DEPTH + 0.5]))
    for k in range(5):
        x = -length / 2 + 3 + k * (length - 6) / 4
        p.bare.box(
            [0.6, SLAT_THICK + 0.3, SLAT_DEPTH - 1], M.dark, Placement([x, 0, -SLAT_DEPTH / 2])
        )


def draw_ramp(p: Any) -> None:
    """Draw the ramp standing shut up local Y from its hinge: treads and lit edges."""
    p.hull.box([RAMP_WIDTH, RAMP_LENGTH, 1.2], M.base, Placement([0, 0, -0.6]))
    for side in [-1, 1]:
        p.neon.box(
            [0.5, RAMP_LENGTH - 1, 0.4], N, Placement([side * (RAMP_WIDTH / 2 - 0.6), 0.5, -1.4])
        )
    for k in range(4):
        p.bare.box([RAMP_WIDTH - 3, 0.6, 0.4], M.dark, Placement([0, 2 + k * 3.2, -1.4]))


class BehemothRig:
    """The nacelles (tilt, hub, blade and fold nodes), their spinners, the slats and the ramp."""

    def __init__(self, nodes: Any, models: list[Any]) -> None:
        self.tilts = nodes["tilts"]
        self.hubs = nodes["hubs"]
        self.folds = nodes["folds"]
        self.noses = nodes["noses"]
        self.spinners = nodes["spinners"]
        self.petals = nodes["petals"]
        self.followers = nodes["followers"]
        self.slats = nodes["slats"]
        self.ramp = nodes["ramp"]
        self.regions = [wing_region("right"), wing_region("left")]
        self.models = models
        self.spin = [0.0, 0.0]
        # The hub's turn as the rotors started spinning down, and where they stop.
        self.stop_from = [0.0, 0.0]
        self.stop_at = [0.0, 0.0]
        self.stopping = False

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Pose the nacelles, spinners, slats and ramp for the boss, and sync their models."""
        t1 = phase(boss, 1)
        self._spin(t1, dt)
        fold = ease(share(t1, FOLD)) * BLADE_FOLD
        tilt = ease(share(t1, TILT)) * QUARTER
        swap = BOSS_LOOK.reveal.swing
        rotor = t1 < swap[0]
        petals = -PETAL_LEAN + (PETAL_OPEN + PETAL_LEAN) * ease(share(t1, PETALS))
        slide = ease(share(t1, swap))
        for i in range(2):
            set_enabled(self.tilts[i], rotor)
            self.tilts[i].rotation.x = tilt
            self.hubs[i].rotation.y = self.spin[i] if i == 0 else -self.spin[i]
            for k in range(len(BLADE_TURNS)):
                self.folds[i * len(BLADE_TURNS) + k].rotation.x = fold
            self._nose(boss, i, rotor, tilt, slide)
            for k in range(len(PETAL_TURNS)):
                self.petals[i * len(PETAL_TURNS) + k].rotation.x = petals
        self._wings(boss)
        self.ramp.rotation.x = -(1 - ease(share(phase(boss, 2), RAMP))) * QUARTER
        for model in self.models:
            model.sync(lit, dt)

    def _spin(self, t1: float, dt: float) -> None:
        """Turn the rotors (the left one the other way): spinning, then easing to a stop.

        They stop with a blade where the folded blades of the cannon parts are, as it morphs.
        """
        if t1 <= 0:
            self.stopping = False
            for i in range(2):
                self.spin[i] = (self.spin[i] + SPIN * dt) % (2 * math.pi)
            return
        if t1 >= 1:
            self.spin = [0.0, 0.0]
            return
        if not self.stopping:
            self.stopping = True
            for i in range(2):
                start = self.spin[i]
                ahead = THIRD - start % THIRD
                if ahead < 1:
                    ahead += THIRD
                self.stop_from[i] = start
                self.stop_at[i] = start + ahead
        k = share(t1, SPIN_DOWN)
        out = 1 - (1 - k) * (1 - k)
        for i in range(2):
            self.spin[i] = self.stop_from[i] + (self.stop_at[i] - self.stop_from[i]) * out

    def _nose(self, boss: Any, i: int, rotor: bool, tilt: float, slide: float) -> None:
        """Put nacelle `i`'s spinner on its nose: on the standing or tilting nacelle.

        Else on the cannon part as it slides in (hidden once the cannon is gone).
        """
        nose = self.noses[i]
        if rotor:
            at = pivots()[i]
            nose.position.set(
                at[0], at[1] + NOSE_Y * math.cos(tilt), at[2] + NOSE_Y * math.sin(tilt)
            )
            nose.rotation.set(tilt, 0, 0)
            self.spinners[i].rotation.y = self.spin[i] if i == 0 else -self.spin[i]
            set_enabled(nose, True)
            return
        ends = docked_fronts(i)
        k = 1 - slide
        nose.position.set(
            ends[0][0] + (ends[1][0] - ends[0][0]) * k,
            ends[0][1],
            ends[0][2] + (ends[1][2] - ends[0][2]) * k,
        )
        nose.rotation.set(QUARTER, 0, 0)
        self.spinners[i].rotation.y = 0
        set_enabled(nose, _cannon_stands(boss, i))

    def _wings(self, boss: Any) -> None:
        """Move the slats with their wing halves, and flip them up once the halves have stowed."""
        flip = ease(share(phase(boss, 2), SLATS)) * QUARTER
        for i in range(2):
            region = self.regions[i]
            motion = region.motion
            place(
                self.followers[i], node_pose(motion, motion_value(motion, progress(region, boss)))
            )
            self.slats[i].rotation.x = flip


def _cannon_stands(boss: Any, i: int) -> bool:
    """Whether cannon `i` (0: right) stands on `boss` (True with no boss)."""
    if boss == None or boss.parts == None:
        return True
    name = "cannon-right" if i == 0 else "cannon-left"
    for part in boss.parts:
        if part.spec.id == name:
            return not part.destroyed
    return True


def _node(name: str, parent: Any, at: Vec3) -> Any:
    node = new_transform_node(name, parent.getScene())
    node.parent = parent
    node.position.set(at[0], at[1], at[2])
    return node


def _hang(name: str, node: Any, draw: Any, look: list[Any], models: list[Any]) -> None:
    model = build_enemy_model(name, node.getScene(), look[0], draw, look[1])
    model.root.parent = node
    models.append(model)


def _nacelle(i: int, root: Any, look: list[Any], nodes: Any, models: list[Any]) -> None:
    """Build nacelle `i` (0: right): its tilt node, body, hub, blades and its spinner's petals."""
    name = "tiltrotor-behemoth-nacelle-" + str(i)
    tilt = _node(name, root, pivots()[i])
    _hang(name + "-body", tilt, draw_body, look, models)
    hub = _node(name + "-hub", tilt, [0, HUB_Y + HUB_HEIGHT / 2, 0])
    for k in range(len(BLADE_TURNS)):
        turn = _node(name + "-blade-" + str(k), hub, [0, 0, 0])
        turn.rotation.y = BLADE_TURNS[k]
        fold = _node(name + "-fold-" + str(k), turn, [0, 0, BLADE_ROOT])
        _hang(name + "-blade-" + str(k), fold, draw_blade, look, models)
        nodes["folds"].append(fold)
    nose = _node(name + "-nose", root, [0, 0, 0])
    spinner = _node(name + "-spinner", nose, [0, 0, 0])
    for k in range(len(PETAL_TURNS)):
        turn = _node(name + "-petal-" + str(k), spinner, [0, 0, 0])
        turn.rotation.y = PETAL_TURNS[k]
        hinge = _node(name + "-hinge-" + str(k), turn, [0, 0, PETAL_BASE])
        hinge.rotation.x = -PETAL_LEAN
        _hang(name + "-petal-" + str(k), hinge, draw_petal, look, models)
        nodes["petals"].append(hinge)
    nodes["tilts"].append(tilt)
    nodes["hubs"].append(hub)
    nodes["noses"].append(nose)
    nodes["spinners"].append(spinner)


def build_behemoth_rig(root: Any, neon: Any, breath: Any) -> BehemothRig:
    """Return the rig on `root` (the boss model's)."""
    look = [neon, breath]
    models: list[Any] = []
    nodes: Any = {
        "tilts": [],
        "hubs": [],
        "folds": [],
        "noses": [],
        "spinners": [],
        "petals": [],
        "followers": [],
        "slats": [],
    }
    for i in range(2):
        _nacelle(i, root, look, nodes, models)
        follower = _node("tiltrotor-behemoth-wing-" + str(i), root, [0, 0, 0])
        slat = _node("tiltrotor-behemoth-slat-" + str(i), follower, slat_hinge(i))
        _hang("tiltrotor-behemoth-slat-" + str(i), slat, draw_slat, look, models)
        nodes["followers"].append(follower)
        nodes["slats"].append(slat)
    ramp = _node("tiltrotor-behemoth-ramp", root, ramp_hinge())
    ramp.rotation.x = -QUARTER
    _hang("tiltrotor-behemoth-ramp", ramp, draw_ramp, look, models)
    nodes["ramp"] = ramp
    return BehemothRig(nodes, models)


def behemoth_triangles(unfold: float) -> list[Any]:
    """Return the rig's triangles (model space): at rest (0), or once the rotors are cannons (1).

    At rest: the standing nacelles, their spinners and the slats on the spread wings. Once the
    nacelles have become the cannon parts, only the open petals on their noses (the slats ride the
    wing halves, which have stowed by the second transformation: left out).
    """
    result: list[Any] = []
    ramp = flat(posed(drawn(draw_ramp), ramp_hinge(), [-QUARTER, 0, 0]))
    result.extend(ramp)
    if unfold >= 1:
        for i in range(2):
            front = docked_fronts(i)[0]
            result.extend(
                flat(
                    posed(
                        petal_layers(1, 0), [front[0], front[1], front[2] - NOSE_Y], [QUARTER, 0, 0]
                    )
                )
            )
        return result
    body = nacelle_layers(0)
    petals = petal_layers(0, 0)
    slat = drawn(draw_slat)
    for i in range(2):
        at = pivots()[i]
        result.extend(flat(posed(body, at, [0, 0, 0])))
        result.extend(flat(posed(petals, at, [0, 0, 0])))
        result.extend(flat(posed(slat, slat_hinge(i), [0, 0, 0])))
    return result
