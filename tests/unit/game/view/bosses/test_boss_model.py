# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/boss_model.py`."""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.boss_wholeness import boss_states, loose_pieces
from helpers.bosses_top_fakes import FakeNode, patch_models

from core.entities.boss import Boss
from game.config.boss_look import BOSS_LOOK
from game.config.bosses.boss_kit import part
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, tail_cannon
from game.config.bosses.moving_regions import moving_region, slide, swing
from game.config.record import record
from game.sim.boss_kinds import BOSS_DESIGNS
from game.view.bosses import boss_armour, boss_limbs, boss_model
from game.view.bosses.boss_limbs import JointFrame
from game.view.bosses.boss_model import (
    FlashGroup,
    _field,
    _point_of,
    build_body,
    build_boss_model,
    build_part,
    build_turret,
    strobe,
)
from render.geometry.mesh_triangles import triangles
from render.geometry.solids import Placement, SolidBuilder


def test_field_reads_a_present_key_and_is_none_for_a_missing_one_or_no_object() -> None:
    assert _field({"a": 1}, "a") == 1
    assert _field({"a": 1}, "b") is None
    assert _field(None, "a") is None


def test_point_of_is_a_playfield_point_in_model_space_with_an_optional_height() -> None:
    assert _point_of([3, 4]) == [-3, 0, -4]
    assert _point_of([3, 4, 2]) == [-3, 2, -4]


def test_strobe_of_a_plain_stand_in_is_its_own_charge() -> None:
    assert strobe(SimpleNamespace(charge=0.7)) == 0.7


class _FakeBoss(Boss):
    """A boss whose lights only read its pause, rage and charge (no stats are needed for them)."""

    def __init__(self, pause: float = 0.0, rage: float = 0.0, charge: float = 0.25) -> None:
        self.pause = pause
        self.rage = rage
        self.charge = charge


def _boss(pause: Any = 0.0, rage: Any = 0.0, charge: Any = 0.25) -> Any:
    return _FakeBoss(pause, rage, charge)


def test_boss_22_a_calm_boss_shows_its_own_charge() -> None:
    boss = _boss(charge=0.25)
    assert strobe(boss) == 0.25


def test_stage_change_strobes_the_lights_at_the_stage_strobe_rate() -> None:
    """BOSS-22: the charge lights strobe through the pause after a lost part."""
    hz = BOSS_LOOK.stageStrobeHz
    boss = _boss(pause=1.0)
    # The light is on in the first half of each strobe period and off in the second.
    on = strobe(boss)
    boss.pause = 1.5 / (hz * 2)
    off = strobe(boss)
    assert on == 1
    assert off == 0


def test_rage_flickers_between_full_and_the_dim_level() -> None:
    """BOSS-27: an angry boss's charge lights flicker down to their dim level."""
    hz = BOSS_LOOK.rageFlicker.hz
    dim = BOSS_LOOK.rageFlicker.dim
    boss = _boss(rage=0.0)
    boss.rage = 0.0 + 1e-9  # angry, just starting its cycle: full
    assert strobe(boss) == 1
    boss.rage = 1.5 / (hz * 2)  # the second half of a cycle: dimmed
    assert strobe(boss) == dim


def test_flash_group_lights_its_body_hulls_white_for_a_moment_after_a_hit(monkeypatch: Any) -> None:
    """BOSS-17: a part or the core that is hit flashes white for a moment."""
    body = SimpleNamespace(material="body-mat", useVertexColors=True)
    other = SimpleNamespace(material="other", useVertexColors=True)
    body_material = SimpleNamespace(name="enemy-hull")
    other_material = SimpleNamespace(name="charge")
    body.material = body_material
    other.material = other_material
    monkeypatch.setattr(boss_model, "child_meshes", lambda _root, _direct: [body, other])
    monkeypatch.setattr(boss_model, "node_name", lambda node: node.name)
    model = SimpleNamespace(root=object())
    group = FlashGroup(model, flash="FLASH")
    group.show(since_hit=0.0)
    assert body.material == "FLASH"
    assert body.useVertexColors is False
    # Only the body's hulls are flashed.
    assert other.material is other_material
    group.show(since_hit=BOSS_LOOK.flash.seconds + 1)
    assert body.material is body_material
    assert body.useVertexColors is True


# BOSS-52 (D-254): every boss model is one object, at rest and after each of its transformations: no
# piece of it hangs in the air (its parts and weapons, its armour and frames, its rig). The game
# draws no stem or pylon of its own any more: the bosses whose drawings do not hold yet are strict
# expected failures (ENG-163), struck off as they are migrated.
NOT_HELD_YET = {
    "storm-petrel",
    "gull-mothership",
    "mesa-fortress",
    "floe-breaker",
    "narwhal",
    "harbour-kraken",
    "snow-owl",
    "avalanche",
    "glacier-colossus",
    "ice-queen",
    "boreal-citadel",
    "dam-breaker",
    "jaguar",
    "steam-dreadnought",
    "ash-wraith",
    "obsidian-golem",
    "foundry-ark",
    "ember-herald",
}


def _held(design: Any) -> Any:
    if design.id in NOT_HELD_YET:
        return pytest.param(
            design,
            id=design.id,
            marks=pytest.mark.xfail(strict=True, reason="loose pieces, not redrawn yet (D-254)"),
        )
    return pytest.param(design, id=design.id)


@pytest.mark.parametrize("design", [_held(d) for d in BOSS_DESIGNS])
def test_boss_52_the_boss_holds_together_in_every_state(design: Any) -> None:
    mp = pytest.MonkeyPatch()
    try:
        states = boss_states(design.id, design, mp)
    finally:
        mp.undo()
    for form, tris in enumerate(states):
        assert loose_pieces(tris, 0) == [], f"after transformation {form}"


# The model as built (BOSS-47) on fake nodes, from a small hand-made boss: a deck with a fuselage,
# a light hanging over it; standing parts (one with a turret), a part on a joint with its limb, an
# orbiting one, hidden weapons (a gatling with its turret, a lance with its barrel, an orb riding a
# moving hatch, a cannon on a rig), a ring, a rig, an armour region that bursts off and two that
# move (BOSS-45), each drawn as a plate over the deck. Model space is mirrored: a config point
# (x, y) is model (-x, -y) in XZ.

GREY = [0.5, 0.5, 0.5]
NEON = [1.0, 0.0, 1.0]


def _deck(p: Any) -> None:
    """Draw the core: a deck, a fuselage on it, a light over the deck and a muzzle."""
    p.hull.box([80, 4, 40], GREY, Placement([0, -2, 0]))
    p.flesh.box([12, 6, 40], GREY, Placement([0, 2, 0]))
    p.neon.box([3, 1, 3], GREY, Placement([20, 8, -15]))
    p.muzzle([0, 4, 20])


def _deck_alone(p: Any) -> None:
    p.hull.box([80, 4, 40], GREY, Placement([0, -2, 0]))


def _pod(p: Any, at: Any) -> None:
    p.hull.box([6, 4, 6], GREY, Placement([at[0], 0, at[2]]))


def _light(p: Any, at: Any) -> None:
    """Draw a part in neon alone (no hull or flesh: nothing for a pylon to meet)."""
    p.neon.box([3, 1, 3], GREY, Placement([at[0], 3, at[2]]))


def _turret_drawing(p: Any, at: Any) -> None:
    p.hull.box([3, 2, 3], GREY, Placement([at[0], 4, at[2]]))
    p.muzzle([at[0], 5, at[2] + 3])


def _limb(p: Any) -> None:
    p.hull.box([4, 2, 10], GREY, Placement([40, 0, 0]))


def _ring(p: Any) -> None:
    p.hull.box([6, 2, 6], GREY, Placement([0, -6, 35]))


def _wings_armour(p: Any) -> None:
    """Draw the wings' armour: a plate over the deck (config x 25..38 is model x -38..-25)."""
    p.hull.box([13, 2, 20], GREY, Placement([-31.5, 1, 0]))


def _hatch_armour(p: Any) -> None:
    p.hull.box([16, 2, 10], GREY, Placement([0, 1, -13]))


def _flap_armour(p: Any) -> None:
    p.hull.box([8, 2, 10], GREY, Placement([16, 1, 13]))


class _RigView:
    """A rig's view: the boss it was shown for, each frame."""

    def __init__(self) -> None:
        self.shown: list[Any] = []

    def show(self, boss: Any, _lit: Any, _dt: float) -> None:
        self.shown.append(boss)


class _Rig:
    """A rig (D-228): a box on the deck, built as a view of its own."""

    def __init__(self) -> None:
        self.view = _RigView()
        self.built_on: Any = None

    def build(self, root: Any, _neon: Any, _breath: Any) -> _RigView:
        self.built_on = root
        return self.view

    def triangles(self, _unfold: float) -> list[Any]:
        b = SolidBuilder()
        b.box([4, 2, 4], GREY, Placement([0, 2, -30]))
        return triangles(b.geometry)


def _probe_design() -> Any:
    gat = hidden_weapon("gat", "gatling", [15, -15], 5, 100, 1, "probe", 0)
    lance = hidden_weapon("lance", "lance", [15, 15], 4, 100, 1, "probe", 0)
    rider = hidden_weapon("rider", "orb", [0, 22], 4, 100, 1, "probe", 0)
    tail = tail_cannon("tail", [0, 30], 4, 100, 1, 0)
    hatch = moving_region(
        "hatch",
        1,
        [[-8, 8], [8, 8], [8, 18], [-8, 18]],
        slide([[0, 0, 0], [0, 10, 0]]),
        "shell",
        None,
        False,
    )
    flap = moving_region(
        "flap",
        1,
        [[-20, -18], [-12, -18], [-12, -8], [-20, -8]],
        swing([-16, -13, 0], "up", [0, 30]),
        None,
        None,
        False,
    )
    parts = [
        part("plain", [-30, -15], 5, 100),
        part("bare", [30, -15], 5, 100),
        part("arm", [-45, 0], 5, 100, {"joint": "shoulder"}),
        part("blade", [0, -35], 4, 100, {"orbits": True}),
        part("shown", [-30, 15], 4, 100, {"reveal": 1}),
        gat.part,
        lance.part,
        rider.part,
        tail.part,
    ]
    return record({
        "id": "probe",
        "stats": {"parts": parts, "joints": {"shoulder": {"x": -40, "y": 0}}},
        "guns": {
            "core": {"gun": [[0, -14, 6]], "turret": [0, -10]},
            "plain": {"gun": [[-30, -19, 6]], "turret": [-30, -15]},
            "gat": gat.guns,
            "lance": lance.guns,
            "rider": rider.guns,
            "tail": tail.guns,
        },
        "weapons": {"gat": gat.look, "lance": lance.look, "rider": rider.look, "tail": tail.look},
        "armour": [
            armour_region("wings", 1, [[25, -10], [38, -10], [38, 10], [25, 10]], "wing"),
            hatch[0],
            flap[0],
        ],
    })


def _probe_drawing(rig: _Rig) -> dict[str, Any]:
    return {
        "core": _deck,
        "parts": {"plain": _pod, "bare": _light, "arm": _pod, "blade": _pod, "shown": _pod},
        "turrets": {"core": _turret_drawing, "plain": _turret_drawing},
        "limbs": {"shoulder": {"draw": _limb, "part": "arm"}},
        "ring": _ring,
        "rig": {"build": rig.build, "triangles": rig.triangles},
        "armour": {
            "wings": {"whole": _wings_armour},
            "hatch": {"whole": _hatch_armour},
            "flap": {"whole": _flap_armour},
        },
    }


class _Smoke:
    """A part's smoke: its node, and the steps it drifted by."""

    def __init__(self, name: str, scene: Any, parent: Any) -> None:
        self.node = FakeNode(name + "-smoke", scene)
        self.node.parent = parent
        self.steps: list[float] = []

    def step(self, dt: float) -> None:
        self.steps.append(dt)


def _probe_scene(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    """Patch the boss model's Babylon helpers with fakes; return the builder and the smokes made."""
    builder = patch_models(monkeypatch, boss_model, boss_armour, boss_limbs)
    smokes: dict[str, _Smoke] = {}

    def smoke(name: str, _radius: float, scene: Any, parent: Any) -> _Smoke:
        smokes[name] = _Smoke(name, scene, parent)
        return smokes[name]

    monkeypatch.setattr(boss_model, "build_smoke", smoke)
    monkeypatch.setattr(boss_model, "effect_materials", lambda _scene: {"flash": "FLASH"})
    monkeypatch.setattr(boss_model, "child_meshes", lambda node, _direct: list(node.meshes))
    monkeypatch.setattr(boss_model, "node_name", lambda named: named.name)
    trimmed: list[Any] = []
    monkeypatch.setattr(boss_model, "set_trim_group", trimmed.append)
    return SimpleNamespace(builder=builder, smokes=smokes, trimmed=trimmed, scene=object())


@pytest.fixture
def probe(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    """Return the probe boss's model, built on fake nodes."""
    scene = _probe_scene(monkeypatch)
    rig = _Rig()
    design = _probe_design()
    scene.model = build_boss_model(design, scene.scene, NEON, _probe_drawing(rig))
    scene.design = design
    scene.rig = rig
    return scene


def _part_state(**fields: Any) -> SimpleNamespace:
    state = {
        "destroyed": False,
        "hidden": False,
        "health": 100.0,
        "max_health": 100.0,
        "since_hit": 10.0,
        "turret": None,
    }
    state.update(fields)
    return SimpleNamespace(**state)


class _LiveBoss(Boss):
    """A boss as the view reads it: its pose, form, core and parts (no stats are needed)."""

    def __init__(self, parts: list[Any], form: int = 0, transform: float = 0.0) -> None:
        self.pause = 0.0
        self.rage = 0.0
        self.charge = 0.5
        self.roll = 0.2
        self.spin = 1.5
        self.form = form
        self.state = "fighting" if transform == 0 else "transforming"
        self.transform = transform
        self.core = SimpleNamespace(turret=SimpleNamespace(aim=0.7), since_hit=0.0)
        self.parts = parts
        self.joints = SimpleNamespace(angle=lambda _joint: 0.4)


def _live_parts(**states: Any) -> list[Any]:
    """Return the probe boss's parts in order, each as given by name (else standing whole)."""
    ids = ["plain", "bare", "arm", "blade", "shown", "gat", "lance", "rider", "tail"]
    return [states.get(i, _part_state()) for i in ids]


def test_boss_47_the_model_builds_its_core_parts_turrets_limbs_ring_and_armour(
    probe: Any,
) -> None:
    models = probe.builder.models
    for name in [
        "probe-core",
        "probe-ringbody",
        "probe-core-turret",
        "probe-plain-turret",
        "probe-gat-turret",
        "probe-shoulder-limb",
        "probe-lance-slide-0",
        "probe-armour-wings",
        "probe-armour-wings-chunk-0",
        "probe-armour-wings-frame-floor",
        "probe-armour-hatch-frame-ribs",
        "probe-armour-flap",
    ]:
        assert name in models, name
    for spec in probe.design.stats.parts:
        assert "probe-" + spec.id in models
    # A moving region without a frame leaves none; the orb and the lance have no turret.
    assert "probe-armour-flap-frame-floor" not in models
    assert "probe-rider-turret" not in models
    assert "probe-lance-turret" not in models
    # The core is drawn as it is, with its muzzle; the armour is drawn over it.
    assert probe.builder.drawn["probe-core"]["muzzles"] == [[[0, 4, 20], "gun"]]
    assert probe.builder.faces("probe-core") == 12
    assert probe.builder.faces("probe-armour-wings") == 12
    # Each part is trimmed along its own outline (BOSS-48).
    assert [n.name for n in probe.trimmed][:2] == ["probe-plain", "probe-bare"]


def test_boss_47_parts_hang_on_the_boss_its_ring_their_joint_or_the_piece_they_ride(
    probe: Any,
) -> None:
    models = probe.builder.models
    root = models["probe-core"].root.parent
    assert root.name == "probe"
    assert models["probe-plain"].root.parent is root
    assert models["probe-blade"].root.parent.name == "probe-ring"
    assert models["probe-arm"].root.parent.name == "probe-shoulder-joint"
    # D-230: the orb rides the moving hatch, on its carrier.
    assert models["probe-rider"].root.parent.name == "probe-hatch-carrier"
    assert models["probe-shoulder-limb"].root.parent.name == "probe-shoulder-joint"
    # The core's turret turns about its pivot, the turret model drawn back round it.
    turret = models["probe-core-turret"].root
    assert turret.parent.name == "probe-core-pivot"
    assert turret.parent.position.xyz() == [0, 0, 10]
    assert turret.position.xyz() == [0, 0, -10]
    assert probe.rig.built_on is root


def test_boss_17_boss_22_a_live_boss_rolls_spins_aims_flashes_and_smokes(probe: Any) -> None:
    models = probe.builder.models
    parts = _live_parts(
        plain=_part_state(health=10.0, since_hit=0.0, turret=SimpleNamespace(aim=-0.3)),
        bare=_part_state(destroyed=True),
        blade=_part_state(hidden=True),
    )
    # A boss with more parts than its model: the extra one has nothing to show.
    boss = _LiveBoss([*parts, _part_state()])
    probe.model.sync(boss, 0.05)
    root = models["probe-core"].root.parent
    assert root.rotation.z == 0.2
    assert models["probe-ringbody"].root.parent.rotation.y == 1.5
    assert models["probe-core-turret"].root.parent.rotation.y == 0.7
    assert models["probe-core"].synced == [({"charge": 0.5}, 0.05)]
    # The core and its ring flash white: hit just now (BOSS-17).
    assert models["probe-core"].root.meshes[0].material == "FLASH"
    assert models["probe-ringbody"].root.meshes[0].material == "FLASH"
    # A damaged part flashes, smokes and aims its turret.
    plain = models["probe-plain"].root
    assert plain.enabled is True
    assert plain.meshes[0].material == "FLASH"
    assert models["probe-plain-turret"].root.parent.rotation.y == -0.3
    assert probe.smokes["probe-plain"].node.enabled is True
    assert probe.smokes["probe-plain"].steps == [0.05]
    # A destroyed part leaves nothing (BOSS-18, D-225); a retired one has left (D-228).
    assert models["probe-bare"].root.enabled is False
    assert probe.smokes["probe-bare"].node.enabled is False
    assert models["probe-blade"].root.enabled is False
    assert probe.smokes["probe-blade"].node.enabled is False
    # A whole part neither smokes nor flashes.
    assert probe.smokes["probe-arm"].node.enabled is False
    assert models["probe-arm"].root.meshes[0].material.name == "enemy-hull"
    assert models["probe-arm"].root.meshes[0].useVertexColors is True
    assert models["probe-shoulder-limb"].synced
    assert probe.rig.view.shown == [boss]


def test_boss_38_hidden_weapons_stay_folded_away_until_the_boss_transforms(probe: Any) -> None:
    models = probe.builder.models
    probe.model.sync(_LiveBoss(_live_parts()), 0.05)
    for piece in ["shown", "gat", "lance", "rider", "tail"]:
        assert models["probe-" + piece].root.enabled is False, piece
    probe.model.sync(_LiveBoss(_live_parts(), form=1), 0.05)
    for piece in ["shown", "gat", "lance", "rider", "tail"]:
        assert models["probe-" + piece].root.enabled is True, piece


def test_a_stand_in_is_shown_at_rest_with_its_own_charge(probe: Any) -> None:
    models = probe.builder.models
    probe.model.sync(SimpleNamespace(charge=0.3), 0.1)
    assert models["probe-core"].synced == [({"charge": 0.3}, 0.1)]
    assert models["probe-ringbody"].synced == [({"charge": 0.3}, 0.1)]
    assert models["probe-core-turret"].root.parent.rotation.y == 0
    assert models["probe-core-turret"].synced
    # Its parts are left as they are; its armour is on, its rig at rest.
    assert models["probe-plain"].synced == []
    assert models["probe-armour-wings"].root.enabled is True
    assert probe.rig.view.shown == [None]


def test_a_boss_without_armour_ring_or_rig_is_its_core_and_parts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scene = _probe_scene(monkeypatch)
    design = record({"id": "lone", "stats": {"parts": [part("plain", [-30, -15], 5, 100)]}})
    drawing = {"core": _deck_alone, "parts": {"plain": _pod}}
    model = build_boss_model(design, scene.scene, NEON, drawing)
    assert sorted(scene.builder.models) == ["lone-core", "lone-plain"]
    model.sync(_LiveBoss([_part_state(health=10.0)]), 0.05)
    assert scene.smokes["lone-plain"].steps == [0.05]


def test_a_turret_drawn_without_its_gun_turret_or_the_other_way_round_is_an_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """BOSS-29: a turret needs both its pivot (the gun's `turret`) and its drawing."""
    _probe_scene(monkeypatch)
    holder = FakeNode("holder", "scene")
    drawn_only = record({"id": "odd", "guns": {}})
    with pytest.raises(ValueError, match='Boss "odd": "core" needs a turret and its drawing'):
        build_turret(
            drawn_only, "core", record({"turrets": {"core": _turret_drawing}}), holder, NEON, None
        )
    pivot_only = record({"id": "odd", "guns": {"core": {"turret": [0, -10]}}})
    with pytest.raises(ValueError, match="needs a turret and its drawing"):
        build_turret(pivot_only, "core", record({}), holder, NEON, None)


def test_a_part_with_no_drawing_and_no_weapon_look_is_an_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _probe_scene(monkeypatch)
    design = record({"id": "odd", "stats": {"parts": [part("ghost", [0, 0], 4, 100)]}})
    frame = JointFrame(FakeNode("odd", "scene"), [0, 0, 0])
    look = {"flash": "FLASH", "neon": NEON, "breath": None}
    with pytest.raises(ValueError, match='Boss "odd" has no drawing for its part "ghost"'):
        build_part(design, design.stats.parts[0], record({"parts": {}}), frame, look)


def test_the_body_is_drawn_by_the_drawing_core(monkeypatch: pytest.MonkeyPatch) -> None:
    scene = _probe_scene(monkeypatch)
    design = record({"id": "odd", "guns": {}})
    root = FakeNode("odd", "scene")
    look = {"flash": "FLASH", "neon": NEON, "breath": None}
    body = build_body(design, record({"core": _deck_alone}), root, look)
    assert body["ring"] is None
    assert body["core_turret"] is None
    assert body["core"].model.root.parent is root
    assert scene.builder.faces("odd-core") == 12
