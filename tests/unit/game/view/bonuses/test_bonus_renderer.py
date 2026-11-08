# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bonuses/bonus_renderer.py`."""

import math
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest
from helpers.babylon_stub import stub_babylon

from game.config.bonus_look import BONUS_LOOK as LOOK
from game.view.bonuses import bonus_renderer
from game.view.bonuses.bonus_renderer import (
    KINDS,
    Flash,
    KindPools,
    create_bonus_renderer,
    kind_templates,
    ring,
    sync_flashes,
    sync_kind,
)
from render import node_pool

# The template maker and the JavaScript-only helpers as the module defines them: the `templates`
# fixture replaces them in every test.
_OPAQUE_TEMPLATE = bonus_renderer.opaque_template
_JS_ONLY = {
    "_bonus_renderer": bonus_renderer._bonus_renderer,
    "_badge_colors": bonus_renderer._badge_colors,
}

# The renderer draws with its templates and Babylon stubbed in every test.
pytestmark = pytest.mark.usefixtures("templates")


@pytest.fixture
def templates(monkeypatch: Any) -> Any:
    """Every template the renderer makes (its clones are MagicMocks too)."""
    made = []

    def make(name: Any, _geo: Any, _scene: Any) -> Any:
        made.append(MagicMock(name=name))
        return made[-1]

    stub_babylon(monkeypatch, bonus_renderer, node_pool)
    monkeypatch.setattr(bonus_renderer, "additive_template", make)
    monkeypatch.setattr(bonus_renderer, "opaque_template", make)
    monkeypatch.setattr(bonus_renderer, "node_name", lambda _node: "template")
    return made


@pytest.fixture
def scene() -> Any:
    return MagicMock(name="scene")


def bonus(kind: Any = "weapon", x: Any = 10.0, y: Any = 20.0, age: Any = 0.0) -> Any:
    return SimpleNamespace(kind=kind, x=x, y=y, age=age)


def test_game_bonus_01_four_kinds_of_bonus_are_drawn() -> None:
    assert KINDS == ["weapon", "life", "bomb", "heal"]


def test_gfx_fx_12_each_kind_has_a_badge_and_a_halo_template(scene: Any, monkeypatch: Any) -> None:
    made = {}

    def record(name: Any, geo: Any, _scene: Any) -> Any:
        made[name] = geo
        return MagicMock(name=name)

    monkeypatch.setattr(bonus_renderer, "additive_template", record)
    templates = kind_templates(scene)
    assert set(templates) == {"weapon", "life", "bomb", "heal"}
    assert all(len(pair) == 2 for pair in templates.values())
    assert set(made) == {"bonus-halo", "bonus-glow-life", "bonus-glow-bomb", "bonus-glow-heal"}


def test_gfx_fx_11_a_ring_is_a_black_disc_with_a_coloured_rim() -> None:
    geo = ring(8, [1.0, 0.5, 0.0])
    rgb = {tuple(geo.colors[4 * i : 4 * i + 3]) for i in range(len(geo.colors) // 4)}
    assert (1.0, 0.5, 0.0) in rgb
    assert (0.0, 0.0, 0.0) in rgb
    # The centre, then one ring of 8 vertices per colour after the first: 8 rings.
    assert len(geo.colors) // 4 == 1 + 8 * 8


@pytest.mark.usefixtures("scene")
def test_gfx_fx_11_sync_kind_swings_each_badge_and_pulses_its_halo() -> None:
    badges = MagicMock()
    halos = MagicMock()
    badge_meshes = [MagicMock(), MagicMock()]
    halo_meshes = [MagicMock(), MagicMock()]
    badges.show.return_value = badge_meshes
    halos.show.return_value = halo_meshes
    sync_kind(KindPools(badges, halos), [bonus(x=1, y=2, age=0.25), bonus(x=3, y=4, age=0)])
    badges.show.assert_called_once_with(2)
    halos.show.assert_called_once_with(2)
    first = badge_meshes[0]
    first.position.set.assert_called_once_with(1, 2, LOOK.depth)
    expected_swing = LOOK.swing.amplitude * math.sin(2 * math.pi * LOOK.swing.hz * 0.25)
    assert first.rotation.y == pytest.approx(expected_swing)
    second = badge_meshes[1]
    assert second.rotation.y == pytest.approx(0)
    pulse = 1 + LOOK.halo.pulse * math.sin(2 * math.pi * LOOK.halo.pulseHz * 0)
    halo_meshes[1].scaling.set.assert_called_once_with(
        LOOK.size * LOOK.halo.size * pulse, LOOK.size * LOOK.halo.size * pulse, 1
    )


@pytest.mark.usefixtures("scene")
def test_gfx_fx_11_sync_kind_skips_a_pool_slot_without_a_bonus() -> None:
    badges = MagicMock()
    halos = MagicMock()
    mesh = MagicMock()
    shown = MagicMock()
    badges.show.return_value = [shown, mesh]
    halos.show.return_value = [MagicMock(), MagicMock()]
    sync_kind(KindPools(badges, halos), [bonus(), None])
    shown.position.set.assert_called_once()
    mesh.position.set.assert_not_called()


@pytest.mark.usefixtures("scene")
def test_gfx_fx_13_a_pickup_starts_a_flash_that_fades_and_grows() -> None:
    rings = MagicMock()
    mesh = MagicMock()
    rings.show.return_value = [mesh]
    flashes = []
    sync_flashes(rings, flashes, [SimpleNamespace(x=5, y=6)], 0.0)
    assert len(flashes) == 1
    rings.show.assert_called_with(1)
    # Just picked: small (its radius is at least 5 % of the full size), fully visible.
    t0 = 0.0
    radius0 = LOOK.size * LOOK.flash.size * math.sqrt(max(t0, 0.05))
    mesh.scaling.set.assert_called_with(radius0, radius0, 1)
    assert mesh.visibility == pytest.approx(1)


@pytest.mark.usefixtures("scene")
def test_gfx_fx_13_flashes_die_after_their_life() -> None:
    rings = MagicMock()
    rings.show.return_value = []
    flashes = [Flash(0, 0, 0.0)]
    sync_flashes(rings, flashes, [], LOOK.flash.life)
    assert flashes == []


@pytest.mark.usefixtures("scene")
def test_gfx_fx_13_flashes_outlive_a_frame_before_their_life() -> None:
    rings = MagicMock()
    rings.show.return_value = []
    flashes = [Flash(0, 0, 0.0)]
    sync_flashes(rings, flashes, [], LOOK.flash.life / 2)
    assert len(flashes) == 1
    assert flashes[0].age == pytest.approx(LOOK.flash.life / 2)


def test_gfx_fx_11_the_renderer_draws_the_bonuses_of_each_kind(scene: Any) -> None:
    renderer = create_bonus_renderer(scene)
    frame = SimpleNamespace(
        bonuses=[bonus("weapon"), bonus("life"), bonus("bomb"), bonus("life")],
        picked=[SimpleNamespace(x=1, y=2)],
        dt_seconds=0.016,
    )
    renderer["sync"](frame)


def test_gfx_fx_11_the_renderer_disposes_every_template_it_made(scene: Any, templates: Any) -> None:
    renderer = create_bonus_renderer(scene)
    renderer["dispose"]()
    # Six kind templates (badge and halo of three kinds), the flash ring.
    assert len(templates) == 9
    assert all(t.dispose.called for t in templates)


def test_the_renderer_and_badge_objects_are_made_in_javascript_only() -> None:
    """Both are JavaScript object literals; CPython runs only their placeholders: None.

    The `templates` fixture puts Python stand-ins in their place: the originals are kept here.
    """
    assert _JS_ONLY["_bonus_renderer"](lambda _frame: None, lambda: None) is None
    assert _JS_ONLY["_badge_colors"]([1, 1, 1], [0, 0, 0], [1, 0, 0], 0.2) is None


def test_gfx_fx_11_a_badge_template_is_unlit_opaque_double_sided_and_hidden(
    monkeypatch: Any, scene: Any
) -> None:
    mesh = MagicMock(name="mesh")
    material = MagicMock(name="material")
    applied: list[Any] = []
    monkeypatch.setattr(bonus_renderer, "new_mesh", lambda _name, _scene: mesh)
    monkeypatch.setattr(bonus_renderer, "new_standard_material", lambda _name, _scene: material)
    monkeypatch.setattr(bonus_renderer, "vertex_data_of", lambda *args: ("data", *args))
    monkeypatch.setattr(
        bonus_renderer, "apply_vertex_data", lambda data, target: applied.append((data, target))
    )
    monkeypatch.setattr(bonus_renderer, "color3", lambda r, g, b: (r, g, b))
    monkeypatch.setattr(bonus_renderer, "color3_black", lambda: (0, 0, 0))
    geo = SimpleNamespace(positions=[0, 0, 0], indices=[0], colors=[1, 0, 0, 1])
    assert _OPAQUE_TEMPLATE("bonus-badge", geo, scene) is mesh
    assert applied == [(("data", [0, 0, 0], [0], None, [1, 0, 0, 1]), mesh)]
    assert mesh.material is material
    # Unlit, so it glows; both sides show as it spins.
    assert material.emissiveColor == (1, 1, 1)
    assert material.diffuseColor == (0, 0, 0)
    assert material.specularColor == (0, 0, 0)
    assert material.disableLighting is True
    assert material.backFaceCulling is False
    assert mesh.isPickable is False
    mesh.setEnabled.assert_called_once_with(False)
