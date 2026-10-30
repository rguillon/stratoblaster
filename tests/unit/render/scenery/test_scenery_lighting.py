"""Unit tests of `src/render/scenery/scenery_lighting.py`."""

from types import SimpleNamespace

import pytest
from helpers.render_fakes import FakeLight, FakeSettable, FakeVector, patch_babylon

from core.scenery.atmosphere import Ambient, Atmosphere, Fog, Sky, Sun
from core.scenery.sky_look import CLEAR
from render.scenery import scenery_lighting
from render.scenery.scenery_lighting import (
    SceneryLights,
    apply_atmosphere,
    light_scenery,
    snapped_light_position,
    sun_direction,
)


@pytest.fixture(autouse=True)
def _babylon(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_babylon(monkeypatch, scenery_lighting)


def _atmosphere(elevation: float = 90, azimuth: float = 0) -> Atmosphere:
    return Atmosphere(
        Sun(elevation, azimuth, (1.0, 0.9, 0.8), 2.0, 0.5),
        Sky((0.2, 0.4, 0.6), [], 1.0),
        Ambient((0.1, 0.2, 0.3), (0.4, 0.5, 0.6), 0.7),
        Fog(50, 300),
        [],
        0,
        CLEAR,
        0,
        0,
    )


def _scene() -> SimpleNamespace:
    return SimpleNamespace(
        clearColor=FakeSettable(0, 0, 0, 1),
        fogColor=FakeSettable(0, 0, 0),
        fogStart=0,
        fogEnd=0,
    )


def test_the_sun_shines_from_its_elevation_and_azimuth() -> None:
    down = sun_direction(90, 0)
    assert (down.x, down.y, down.z) == pytest.approx((0, -1, 0), abs=1e-9)
    # On the horizon, straight ahead: the light travels towards -Z.
    ahead = sun_direction(0, 0)
    assert (ahead.x, ahead.y, ahead.z) == pytest.approx((0, 0, -1), abs=1e-9)


def test_an_azimuth_of_ninety_degrees_lights_from_the_side_of_positive_x() -> None:
    side = sun_direction(0, 90)
    assert side.x == pytest.approx(-1)
    assert side.z == pytest.approx(0, abs=1e-9)


def test_apply_atmosphere_sets_the_haze_fog_and_ambient_light() -> None:
    scene = _scene()
    lights = SceneryLights(FakeLight("sun"), FakeLight("ambient"))
    apply_atmosphere(scene, lights, _atmosphere())

    assert scene.clearColor.values == (0.2, 0.4, 0.6, 1)
    assert scene.fogColor.values == (0.2, 0.4, 0.6)
    assert (scene.fogStart, scene.fogEnd) == (50, 300)
    assert lights.ambient.diffuse.values == (0.1, 0.2, 0.3)
    assert lights.ambient.groundColor.values == (0.4, 0.5, 0.6)
    assert lights.ambient.intensity == 0.7


def test_apply_atmosphere_sets_the_sun_direction_colour_and_strength() -> None:
    scene = _scene()
    lights = SceneryLights(FakeLight("sun"), FakeLight("ambient"))
    apply_atmosphere(scene, lights, _atmosphere(elevation=90, azimuth=0))

    assert lights.sun.direction.y == pytest.approx(-1)
    assert lights.sun.diffuse.values == (1.0, 0.9, 0.8)
    assert lights.sun.specular.values == (1.0, 0.9, 0.8)
    assert lights.sun.intensity == 2.0


def test_light_scenery_creates_both_lights_and_lights_the_scene() -> None:
    scene = _scene()
    lights = light_scenery(scene, _atmosphere())
    assert scene.fogMode == 2
    assert lights.ambient.specular.values == (0, 0, 0)
    assert lights.sun.intensity == 2.0
    assert scene.fogEnd == 300


def test_a_snapped_light_sits_back_from_its_target_by_the_distance() -> None:
    # Looking straight down, the light has no texel plane to snap in: it sits above the target.
    light = snapped_light_position(FakeVector(0, -1, 0), FakeVector(0, 0, 0), 10, 1)
    assert (light.x, light.y, light.z) == pytest.approx((0, 10, 0), abs=1e-9)


def test_targets_that_differ_only_along_the_light_keep_the_same_shadow_grid() -> None:
    # Moving the target along the light changes nothing across it, so the light only slides
    # along its own direction: the shadow map does not move by a texel.
    direction = FakeVector(0.3, -1, 0.2)
    forward = direction.normalizeToNew()
    first = snapped_light_position(direction, FakeVector(0.1, 0, 0.1), 10, 1)
    second = snapped_light_position(direction, forward.scale(3).add(FakeVector(0.1, 0, 0.1)), 10, 1)
    shift = first.subtract(second)
    assert (shift.x, shift.y, shift.z) == pytest.approx(
        (-3 * forward.x, -3 * forward.y, -3 * forward.z)
    )


def test_a_target_a_whole_texel_away_moves_the_light() -> None:
    direction = FakeVector(0.3, -1, 0.2)
    still = snapped_light_position(direction, FakeVector(0, 0, 0), 10, 1)
    moved = snapped_light_position(direction, FakeVector(5, 0, 0), 10, 1)
    assert (moved.x, moved.y, moved.z) != pytest.approx((still.x, still.y, still.z))
