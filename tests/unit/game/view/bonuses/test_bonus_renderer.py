"""Unit tests of `src/game/view/bonuses/bonus_renderer.py`."""

import math
from types import SimpleNamespace
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


@pytest.fixture
def templates(monkeypatch):
    """Every template the renderer makes (its clones are MagicMocks too)."""
    made = []

    def make(name, geo, scene_):
        made.append(MagicMock(name=name))
        return made[-1]

    stub_babylon(monkeypatch, bonus_renderer, node_pool)
    monkeypatch.setattr(bonus_renderer, "additive_template", make)
    monkeypatch.setattr(bonus_renderer, "opaque_template", make)
    monkeypatch.setattr(bonus_renderer, "node_name", lambda node: "template")
    return made


@pytest.fixture
def scene(templates):
    return MagicMock(name="scene")


def bonus(kind="weapon", x=10.0, y=20.0, age=0.0):
    return SimpleNamespace(kind=kind, x=x, y=y, age=age)


def test_p11_r07_three_kinds_of_bonus_are_drawn():
    assert KINDS == ["weapon", "life", "bomb"]


def test_p11_r07_each_kind_has_a_badge_and_a_halo_template(scene, monkeypatch):
    made = {}

    def record(name, geo, scene_):
        made[name] = geo
        return MagicMock(name=name)

    monkeypatch.setattr(bonus_renderer, "additive_template", record)
    templates = kind_templates(scene)
    assert set(templates) == {"weapon", "life", "bomb"}
    assert all(len(pair) == 2 for pair in templates.values())
    assert set(made) == {"bonus-halo", "bonus-glow-life", "bonus-glow-bomb"}


def test_p11_r07_a_ring_is_a_black_disc_with_a_coloured_rim():
    geo = ring(8, [1.0, 0.5, 0.0])
    rgb = {tuple(geo.colors[4 * i : 4 * i + 3]) for i in range(len(geo.colors) // 4)}
    assert (1.0, 0.5, 0.0) in rgb
    assert (0.0, 0.0, 0.0) in rgb
    # The centre, then one ring of 8 vertices per colour after the first: 8 rings.
    assert len(geo.colors) // 4 == 1 + 8 * 8


def test_p11_r07_sync_kind_swings_each_badge_and_pulses_its_halo(scene):
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


def test_p11_r07_sync_kind_skips_a_pool_slot_without_a_bonus(scene):
    badges = MagicMock()
    halos = MagicMock()
    mesh = MagicMock()
    shown = MagicMock()
    badges.show.return_value = [shown, mesh]
    halos.show.return_value = [MagicMock(), MagicMock()]
    sync_kind(KindPools(badges, halos), [bonus(), None])
    shown.position.set.assert_called_once()
    mesh.position.set.assert_not_called()


def test_p11_r07_a_pickup_starts_a_flash_that_fades_and_grows(scene):
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


def test_p11_r07_flashes_die_after_their_life(scene):
    rings = MagicMock()
    rings.show.return_value = []
    flashes = [Flash(0, 0, 0.0)]
    sync_flashes(rings, flashes, [], LOOK.flash.life)
    assert flashes == []


def test_p11_r07_flashes_outlive_a_frame_before_their_life(scene):
    rings = MagicMock()
    rings.show.return_value = []
    flashes = [Flash(0, 0, 0.0)]
    sync_flashes(rings, flashes, [], LOOK.flash.life / 2)
    assert len(flashes) == 1
    assert flashes[0].age == pytest.approx(LOOK.flash.life / 2)


def test_p11_r07_the_renderer_draws_the_bonuses_of_each_kind(scene):
    renderer = create_bonus_renderer(scene)
    frame = SimpleNamespace(
        bonuses=[bonus("weapon"), bonus("life"), bonus("bomb"), bonus("life")],
        picked=[SimpleNamespace(x=1, y=2)],
        dt_seconds=0.016,
    )
    renderer["sync"](frame)


def test_p11_r07_the_renderer_disposes_every_template_it_made(scene, templates):
    renderer = create_bonus_renderer(scene)
    renderer["dispose"]()
    # Six kind templates (badge and halo of three kinds), the flash ring.
    assert len(templates) == 7
    assert all(t.dispose.called for t in templates)
