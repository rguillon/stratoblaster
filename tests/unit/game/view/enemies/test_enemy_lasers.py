# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/enemy_lasers.py`."""

from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest
from helpers.babylon_stub import stub_babylon

from core.math.color import fold_into_family
from game.config.boss_look import BOSS_LOOK
from game.config.enemy_look import ENEMY_LOOK, laser_palette
from game.config.readability import READABILITY
from game.view.enemies import enemy_lasers as el
from render import node_pool
from render.node_adopter import ON_TOP_ALPHA_INDEX


def test_gfx_shot_18_a_laser_colour_is_its_boss_neon_folded_into_the_shots_family() -> None:
    """Also GFX-READ-06 and BOSS-32: each boss's lasers in its own colour."""
    color = el.color_of("scorpion")
    assert len(color) == 3
    # The folded colour keeps the neon's brightness, but moves its hue into the shots' family.
    neon = BOSS_LOOK.neon["scorpion"]
    assert max(color) == pytest.approx(max(neon), abs=1e-6)


def test_a_style_without_a_boss_neon_takes_the_laser_look_colour(monkeypatch: Any) -> None:
    monkeypatch.setitem(BOSS_LOOK.neon, "bare-style", None)
    folded = fold_into_family(el.LOOK.color, READABILITY.families.enemyShot)
    assert el.color_of("bare-style") == pytest.approx(folded)


def test_gfx_shot_16_contrast_warning_is_a_white_core_then_the_colour_then_dark_edges() -> None:
    color = [0.5, 0.0, 1.0]
    t = ENEMY_LOOK.contrast.warningCore
    warning = el.contrast_warning(color)
    assert len(warning) == 4
    # The core is lifted towards white by warningCore.
    assert warning[0] == pytest.approx([0.5 + 0.5 * t, t, 1.0])
    assert warning[1] == pytest.approx(color)
    assert warning[2] == pytest.approx([0.25, 0, 0.5])
    assert warning[3] == pytest.approx([0, 0, 0])


def test_sync_warnings_shows_one_line_per_warning_and_blinks_its_width(monkeypatch: Any) -> None:
    monkeypatch.setattr(el.LOOK.warning, "blinkHz", 1.0, raising=False)
    meshes = [MagicMock() for _ in range(2)]
    pool = MagicMock()
    pool.show.return_value = meshes
    warnings = [
        SimpleNamespace(x=1.0, y=2.0, heading=0.5, length=10.0),
        SimpleNamespace(x=3.0, y=4.0, heading=0.0, length=5.0),
    ]
    # At a time when the blink is on (sin > 0), the lines are drawn at full width.
    el.sync_warnings(pool, warnings, time=0.25, width=2.0)
    pool.show.assert_called_once_with(2)
    meshes[0].position.set.assert_called_once_with(1.0, 2.0, -0.8)
    meshes[0].rotation.z = -0.5
    meshes[0].scaling.set.assert_called_once_with(2.0, 10.0, 1)
    meshes[1].scaling.set.assert_called_once_with(2.0, 5.0, 1)


def test_sync_warnings_draws_the_lines_at_half_width_while_the_blink_is_off(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(el.LOOK.warning, "blinkHz", 1.0, raising=False)
    mesh = MagicMock()
    pool = MagicMock()
    pool.show.return_value = [mesh]
    el.sync_warnings(pool, [SimpleNamespace(x=0, y=0, heading=0, length=4)], time=0.75, width=2.0)
    mesh.scaling.set.assert_called_once_with(1.0, 4, 1)


def test_sync_warnings_leaves_spare_pooled_lines_alone() -> None:
    mesh = MagicMock()
    pool = MagicMock()
    pool.show.return_value = [mesh]
    el.sync_warnings(pool, [], time=0.0, width=1.0)
    mesh.position.set.assert_not_called()
    mesh.scaling.set.assert_not_called()


def test_gfx_read_11_with_warning_swaps_the_warning_colours_and_keeps_the_rest() -> None:
    base = laser_palette([1.0, 0.0, 0.0])
    warning = [[1.0, 1.0, 1.0], [0.0, 0.0, 0.0]]
    palette = el.with_warning(base, warning)
    assert palette.warning == warning
    assert palette.beam == base.beam
    assert palette.emitter == base.emitter
    # The base palette is left as it was.
    assert base.warning != warning


class _Pool:
    """A node pool stand-in: the counts shown, the meshes made, and whether it was disposed."""

    def __init__(self, extra: int = 0) -> None:
        self.extra = extra
        self.meshes: list[Any] = []
        self.shown: list[int] = []
        self.disposed = False

    def show(self, count: int) -> list[Any]:
        self.shown.append(count)
        while len(self.meshes) < count + self.extra:
            self.meshes.append(MagicMock(name="mesh"))
        return self.meshes[: count + self.extra]

    def dispose(self) -> None:
        self.disposed = True


def test_a_laser_pool_clones_its_template_named_after_it(monkeypatch: Any) -> None:
    stub_babylon(monkeypatch, el, node_pool)
    monkeypatch.setattr(el, "node_name", lambda node: node.label)
    template = MagicMock()
    template.label = "enemy-laser-beam-red"
    pool = el.pool_of(template)
    shown = pool.show(2)
    assert template.clone.call_args_list == [
        (("enemy-laser-beam-red-0",),),
        (("enemy-laser-beam-red-1",),),
    ]
    assert shown == [template.clone.return_value, template.clone.return_value]


@pytest.fixture
def made(monkeypatch: Any) -> list[SimpleNamespace]:
    """Record the templates `lasers_of` makes, with the colours of their geometry."""
    templates: list[SimpleNamespace] = []

    def additive(name: str, geo: Any, scene: Any, on_top: bool = False) -> Any:
        mesh = MagicMock(name=name)
        templates.append(SimpleNamespace(name=name, geo=geo, scene=scene, on_top=on_top, mesh=mesh))
        return mesh

    monkeypatch.setattr(el, "additive_template", additive)
    monkeypatch.setattr(el, "build_glow_bar", lambda colors: ("bar", colors))
    monkeypatch.setattr(el, "build_glow_disc", lambda segments, colors: ("disc", segments, colors))
    monkeypatch.setattr(el, "pool_of", lambda template: ("pool", template))
    return templates


@pytest.mark.parametrize("contrast", [False, True])
def test_gfx_shot_17_a_style_has_a_warning_a_beam_and_a_flare_in_its_colour(
    made: list[SimpleNamespace], contrast: bool
) -> None:
    """Also GFX-READ-11 (a white-cored warning line in the contrast look) and GFX-READ-13."""
    pools = el.lasers_of("scene", "scorpion", contrast)
    names = [t.name for t in made]
    assert names == [
        "enemy-laser-warning-scorpion",
        "enemy-laser-beam-scorpion",
        "enemy-laser-emitter-scorpion",
    ]
    # Drawn over the models, over the player's shots and under the bullets.
    assert all(t.on_top is True and t.scene == "scene" for t in made)
    assert all(t.mesh.alphaIndex == ON_TOP_ALPHA_INDEX for t in made)
    palette = laser_palette(el.color_of("scorpion"))
    warning = el.contrast_warning(el.color_of("scorpion")) if contrast else palette.warning
    assert made[0].geo == ("bar", warning)
    assert made[1].geo == ("bar", palette.beam)
    assert made[2].geo == ("disc", el.LOOK.flare.segments, palette.emitter)
    assert pools.templates == [t.mesh for t in made]
    assert pools.warning == ("pool", made[0].mesh)
    assert pools.beam == ("pool", made[1].mesh)
    assert pools.emitter == ("pool", made[2].mesh)


def _beam(x: float, y: float, heading: float, length: float, width: float) -> Any:
    return SimpleNamespace(
        x=x, y=y, heading=heading, length=length, spec=SimpleNamespace(width=width)
    )


def test_gfx_shot_17_each_beam_is_drawn_with_a_flare_at_its_base(monkeypatch: Any) -> None:
    # No flicker: the beam and the flare at their resting size.
    monkeypatch.setattr(el, "flicker", lambda _time, _phase, _hz: 0)
    pools = el.LaserPools(_Pool(extra=1), _Pool(extra=1), _Pool(extra=1), [])
    el.sync_beams(pools, [_beam(1.0, 2.0, 0.25, 50.0, 4.0)], 0.0)
    assert pools.beam.shown == [1]
    assert pools.emitter.shown == [1]
    beam = pools.beam.meshes[0]
    beam.position.set.assert_called_once_with(1.0, 2.0, -0.9)
    assert beam.rotation.z == pytest.approx(-0.25)
    beam.scaling.set.assert_called_once_with(4.0 * el.LOOK.beam.glowWidth, 50.0, 1)
    flare = el.LOOK.flare
    r = flare.radius * (flare.baseScale + 4.0 / flare.widthDivisor)
    emitter = pools.emitter.meshes[0]
    emitter.position.set.assert_called_once_with(1.0, 2.0, -1.2)
    assert emitter.rotation.z == pytest.approx(-0.25)
    emitter.scaling.set.assert_called_once_with(
        pytest.approx(r), pytest.approx(r * flare.stretch), 1
    )
    # The spare pooled meshes are left alone.
    pools.beam.meshes[1].position.set.assert_not_called()
    pools.emitter.meshes[1].position.set.assert_not_called()


def test_gfx_shot_17_the_beam_flickers_and_its_flare_pulses(monkeypatch: Any) -> None:
    monkeypatch.setattr(el, "flicker", lambda _time, _phase, _hz: 1)
    pools = el.LaserPools(_Pool(), _Pool(), _Pool(), [])
    el.sync_beams(pools, [_beam(0.0, 0.0, 0.0, 10.0, 2.0)], 1.0)
    width = pools.beam.meshes[0].scaling.set.call_args.args[0]
    assert width == pytest.approx(2.0 * el.LOOK.beam.glowWidth * (1 + el.LOOK.beam.flicker))
    flare = el.LOOK.flare
    r = flare.radius * (flare.baseScale + 2.0 / flare.widthDivisor) * (1 + flare.pulse)
    assert pools.emitter.meshes[0].scaling.set.call_args.args[0] == pytest.approx(r)


def _laser(style: str, phase: str) -> Any:
    return SimpleNamespace(spec=SimpleNamespace(style=style), phase=phase)


@pytest.fixture
def lasers(monkeypatch: Any) -> SimpleNamespace:
    """`EnemyLasers` with its pools and drawing recorded."""
    calls = SimpleNamespace(made=[], warnings=[], beams=[])

    def lasers_of(scene: Any, style: str, contrast: bool) -> Any:
        calls.made.append((scene, style, contrast))
        return el.LaserPools(
            _Pool(), _Pool(), _Pool(), [MagicMock(name=style + "-" + str(i)) for i in range(3)]
        )

    def warnings(pool: Any, lines: list[Any], time: float, width: float) -> None:
        calls.warnings.append((pool, lines, time, width))

    def beams(pools: Any, lines: list[Any], time: float) -> None:
        calls.beams.append((pools, lines, time))

    monkeypatch.setattr(el, "lasers_of", lasers_of)
    monkeypatch.setattr(el, "sync_warnings", warnings)
    monkeypatch.setattr(el, "sync_beams", beams)
    return calls


def test_gfx_shot_16_the_lasers_start_with_no_style_drawn() -> None:
    lasers = el.EnemyLasers("scene")
    assert lasers.scene == "scene"
    assert lasers.contrast is False
    assert lasers.style_names == []
    assert lasers.pools == {}


@pytest.mark.parametrize("contrast", [False, True])
def test_gfx_shot_16_each_style_draws_its_warnings_then_its_beams(
    lasers: SimpleNamespace, contrast: bool
) -> None:
    """Also GFX-READ-11: in the contrast look the warning lines are wider."""
    enemy_lasers = el.EnemyLasers("scene", contrast)
    warn = _laser("scorpion", "warning")
    fire = _laser("scorpion", "firing")
    other = _laser("lancer", "firing")
    enemy_lasers.sync([warn, fire, other], 2.0)
    assert enemy_lasers.style_names == ["scorpion", "lancer"]
    assert lasers.made == [("scene", "scorpion", contrast), ("scene", "lancer", contrast)]
    scale = ENEMY_LOOK.contrast.warningWidth if contrast else 1
    scorpion = enemy_lasers.pools["scorpion"]
    lancer = enemy_lasers.pools["lancer"]
    width = el.LOOK.warning.width * scale
    assert lasers.warnings == [
        (scorpion.warning, [warn], 2.0, width),
        (lancer.warning, [], 2.0, width),
    ]
    assert lasers.beams == [(scorpion, [fire], 2.0), (lancer, [other], 2.0)]


def test_gfx_shot_16_a_style_seen_before_keeps_its_pools(lasers: SimpleNamespace) -> None:
    enemy_lasers = el.EnemyLasers("scene")
    enemy_lasers.sync([_laser("scorpion", "warning")], 0.0)
    pools = enemy_lasers.pools["scorpion"]
    enemy_lasers.sync([_laser("scorpion", "firing")], 0.1)
    assert len(lasers.made) == 1
    assert enemy_lasers.pools["scorpion"] is pools
    # A style with no laser this frame still clears what it drew last frame.
    enemy_lasers.sync([], 0.2)
    assert lasers.warnings[-1] == (pools.warning, [], 0.2, el.LOOK.warning.width)
    assert lasers.beams[-1] == (pools, [], 0.2)


@pytest.mark.usefixtures("lasers")
def test_the_lasers_dispose_every_pool_and_template_of_every_style() -> None:
    enemy_lasers = el.EnemyLasers("scene")
    enemy_lasers.sync([_laser("scorpion", "warning"), _laser("lancer", "firing")], 0.0)
    all_pools = list(enemy_lasers.pools.values())
    enemy_lasers.dispose()
    for pools in all_pools:
        assert pools.warning.disposed
        assert pools.beam.disposed
        assert pools.emitter.disposed
        for template in pools.templates:
            template.dispose.assert_called_once()
    assert enemy_lasers.style_names == []
    assert enemy_lasers.pools == {}
