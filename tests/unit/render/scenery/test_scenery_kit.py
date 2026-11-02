# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/scenery/scenery_kit.py`: the props and roads materials, the plain kit.

The materials are fakes that keep what is set on them; the colours are `FakeSettable`s.
"""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import FakeSettable, patch_babylon
from helpers.render_looks import GREY, make_look

from render.scenery import scenery_kit
from render.scenery.scenery_kit import (
    LIGHTS_Z_OFFSET,
    CloudState,
    FogState,
    PlainCloudMaterial,
    PlainMaterial,
    PlainSceneryKit,
    PropMaterials,
    SceneryKitContext,
    SceneryKitFrame,
    SeaSize,
    create_plain_scenery_kit,
    create_prop_materials,
    create_road_material,
    set_ground_lights,
)
from render.scenery.scenery_look import SeaLook, SeaNormalMap


class FakeMaterial:
    """A `StandardMaterial`: its name, and the fields set on it."""

    def __init__(self, name: str, scene: Any) -> None:
        self.name = name
        self.scene = scene


@pytest.fixture(autouse=True)
def _babylon(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_babylon(monkeypatch, scenery_kit)
    monkeypatch.setattr(scenery_kit, "new_standard_material", FakeMaterial)
    monkeypatch.setattr(
        scenery_kit,
        "is_instance_of",
        lambda value, name: name == "StandardMaterial" and isinstance(value, FakeMaterial),
    )


def _values(color: Any) -> tuple[float, ...]:
    settable: FakeSettable = color
    return settable.values


def _lava_look() -> Any:
    lava = SimpleNamespace(glow=(1, 0.4, 0.1))
    sea = SeaLook((0.2, 0, 0), 0.6, 0.1, 0.5, SeaNormalMap(64, 4, 2, 0.3), 16, (0.1, 0.1), lava)
    return make_look(sea=sea)


def _cloud(coverage: float) -> CloudState:
    return CloudState(coverage, 0.7, (0.9, 0.8, 0.7), GREY, FogState(GREY, 10, 100), 0, 0)


def test_a_frame_is_drawn_as_it_is_unless_given_a_ground_transform() -> None:
    frame = SceneryKitFrame(1.5, "camera", True, "atmosphere")
    assert (frame.time, frame.camera_position, frame.sea_enabled) == (1.5, "camera", True)
    assert frame.atmosphere == "atmosphere"
    assert frame.ground is None


def test_d210_the_props_have_no_windows_unless_the_real_kit_sets_them() -> None:
    materials = PropMaterials("structure", "lights")
    assert (materials.structure, materials.lights, materials.windows) == (
        "structure",
        "lights",
        None,
    )


def test_gfx_read_02_the_props_structure_is_toned_by_the_world() -> None:
    plain = create_prop_materials("scene", make_look())
    toned = create_prop_materials("scene", make_look(tone=0.7))
    # No tone: full brightness.
    assert _values(plain.structure.diffuseColor) == (1, 1, 1)
    assert _values(toned.structure.diffuseColor) == (0.7, 0.7, 0.7)
    assert _values(toned.structure.specularColor) == (0.3, 0.3, 0.3)
    assert toned.structure.name == "prop-structure"


def test_gfx_bldg_16_the_props_lights_glow_unlit_pulled_towards_the_camera() -> None:
    lights = create_prop_materials("scene", make_look()).lights
    assert lights.name == "prop-lights"
    assert _values(lights.emissiveColor) == (1, 1, 1)
    assert _values(lights.diffuseColor) == (0, 0, 0)
    assert _values(lights.specularColor) == (0, 0, 0)
    assert lights.disableLighting
    assert lights.zOffset == LIGHTS_Z_OFFSET


def test_gfx_sky_08_the_ground_lights_set_the_glow_of_lights_and_windows() -> None:
    materials = create_prop_materials("scene", make_look())
    materials.windows = FakeMaterial("windows", "scene")
    materials.windows.emissiveColor = FakeSettable(0, 0, 0)
    set_ground_lights(materials, 0.25)
    assert _values(materials.lights.emissiveColor) == (0.25, 0.25, 0.25)
    assert _values(materials.windows.emissiveColor) == (0.25, 0.25, 0.25)


def test_gfx_sky_08_materials_that_are_not_standard_keep_their_glow() -> None:
    other = SimpleNamespace(emissiveColor=FakeSettable(1, 1, 1))
    set_ground_lights(PropMaterials("structure", other, None), 0)
    assert _values(other.emissiveColor) == (1, 1, 1)


def test_the_roads_are_lit_see_through_ribbons_pulled_towards_the_camera() -> None:
    roads = create_road_material("scene")
    assert roads.name == "roads"
    assert _values(roads.diffuseColor) == (1, 1, 1)
    assert _values(roads.specularColor) == (0, 0, 0)
    assert roads.backFaceCulling is False
    assert roads.zOffset == -2
    assert roads.disableDepthWrite


def test_the_plain_kit_has_flat_materials_in_the_looks_colours() -> None:
    look = make_look()
    kit = create_plain_scenery_kit("scene", SceneryKitContext(look, "sun", 0, SeaSize(10, 20), 1))
    assert kit.sea.name == "sea"
    assert _values(kit.sea.diffuseColor) == GREY
    assert _values(kit.sea.specularColor) == (0, 0, 0)
    assert kit.sea.alpha == 0.8
    assert kit.terrain.name == "terrain"
    assert _values(kit.terrain.diffuseColor) == look.terrain.ground.colors[1]
    assert kit.roads.name == "roads"
    assert kit.props.structure.name == "prop-structure"
    assert kit.terrain.scene == "scene"


def test_the_plain_lava_glows_by_itself_opaque() -> None:
    sea = PlainSceneryKit("scene", _lava_look()).sea
    assert sea.alpha == 1
    assert _values(sea.emissiveColor) == (1, 0.4, 0.1)
    assert sea.disableLighting


@pytest.mark.parametrize(
    ("factory", "label"), [("weather", "weather"), ("rings", "rain-rings"), ("plume", "plume")]
)
def test_the_plain_weather_rings_and_plume_are_flat_see_through_materials(
    factory: str, label: str
) -> None:
    kit = PlainSceneryKit("scene", make_look())
    made = getattr(kit, factory)("scene", SimpleNamespace(color=(0.1, 0.2, 0.3), alpha=0.4))
    assert isinstance(made, PlainMaterial)
    assert made.material.name == label
    assert _values(made.material.diffuseColor) == (0.1, 0.2, 0.3)
    assert made.material.alpha == 0.4
    # Nothing to drive frame by frame.
    made.set("frame")
    assert made.material.alpha == 0.4


def test_a_plain_cloud_layer_is_opaque_while_it_covers_the_sky() -> None:
    kit = PlainSceneryKit("scene", make_look())
    cloud = kit.cloud(SimpleNamespace(altitude=120, color=(1, 1, 1)))
    assert isinstance(cloud, PlainCloudMaterial)
    assert cloud.material.name == "cloud-120"
    cloud.material.diffuseColor = FakeSettable(1, 1, 1)
    cloud.set(_cloud(0.5))
    assert cloud.material.alpha == 0.7
    assert _values(cloud.material.diffuseColor) == (0.9, 0.8, 0.7)
    cloud.set(_cloud(0))
    assert cloud.material.alpha == 0


def test_d211_the_plain_kit_draws_the_props_without_imposters() -> None:
    assert PlainSceneryKit("scene", make_look()).imposter_atlas("look", 3) is None


def test_the_plain_aurora_is_a_faint_green_veil() -> None:
    aurora = PlainSceneryKit("scene", make_look()).aurora()
    assert aurora.material.name == "aurora"
    assert _values(aurora.material.diffuseColor) == (0.2, 1, 0.5)
    assert aurora.material.alpha == 0.3


def test_the_plain_kit_casts_no_shadow() -> None:
    kit = PlainSceneryKit("scene", make_look())
    mesh = SimpleNamespace()
    kit.add_shadow_caster(mesh)
    assert vars(mesh) == {}


def test_gfx_sky_08_each_frame_the_plain_kit_sets_the_ground_lights() -> None:
    kit = PlainSceneryKit("scene", make_look())
    atmosphere = SimpleNamespace(ground_lights=0.6)
    kit.update(SceneryKitFrame(0, None, False, atmosphere))
    assert _values(kit.props.lights.emissiveColor) == (0.6, 0.6, 0.6)
