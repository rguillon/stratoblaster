# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/scenery/terrain_blend_plugin_visual.py`: the terrain's blend plugin.

What its hooks give Babylon (GFX-TERRAIN-08, GFX-TERRAIN-17): the define, the samplers, the
uniforms and the shader code, and the values bound for each sub-mesh. The JavaScript objects are
dicts (`helpers.js_shims`), the uniform buffer a fake that records what is bound.
"""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers import js_shims
from helpers.render_looks import BLACK, GREY, WHITE, make_look

from render.scenery import terrain_blend_plugin_visual as plugin
from render.scenery.scenery_kit import GroundTransform
from render.scenery.scenery_look import LavaEdge, LushDetail
from render.scenery.terrain_blend_plugin_visual import (
    BEFORE_FOG,
    FRAGMENT_DEFINITIONS,
    SAMPLERS,
    UNIFORMS,
    UPDATE_DIFFUSE,
    TerrainBlendOwner,
    TerrainBlendState,
    TerrainTextures,
    new_terrain_blend_plugin,
)

TEXTURES = TerrainTextures("low", "ground", "steep", "high", "lush", "paved", "sand", "noise")


class FakeUbo:
    """The material's uniform buffer: the values and textures bound, by name."""

    def __init__(self) -> None:
        self.values: dict[str, tuple[float, ...]] = {}
        self.textures: dict[str, Any] = {}

    def updateFloat4(self, name: str, x: float, y: float, z: float, w: float) -> None:
        self.values[name] = (x, y, z, w)

    def updateFloat3(self, name: str, x: float, y: float, z: float) -> None:
        self.values[name] = (x, y, z)

    def setTexture(self, name: str, texture: Any) -> None:
        self.textures[name] = texture


class Samplers(list):  # type: ignore[type-arg]
    """A JavaScript array of sampler names."""

    def push(self, name: str) -> None:
        self.append(name)


@pytest.fixture(autouse=True)
def _js(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(plugin, "js_object", js_shims.js_object)
    monkeypatch.setattr(plugin, "js_set", js_shims.js_set)


def _owner(state: TerrainBlendState | None = None) -> TerrainBlendOwner:
    return TerrainBlendOwner(make_look().terrain, TEXTURES, state or TerrainBlendState(3, True, 7))


def _bound(state: TerrainBlendState) -> FakeUbo:
    ubo = FakeUbo()
    _owner(state).bind_for_sub_mesh(ubo)
    return ubo


def test_a_blend_state_is_water_drawn_as_it_is_by_default() -> None:
    state = TerrainBlendState(3, True, 7)
    assert (state.sea_level, state.sea_enabled, state.time) == (3, True, 7)
    assert (state.lava, state.ground) == (None, None)


def test_gfx_terrain_08_the_plugin_turns_the_material_into_a_terrain_material(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    made: list[tuple[Any, ...]] = []
    monkeypatch.setattr(plugin, "new_material_plugin", lambda *args: made.append(args) or "plugin")
    state = TerrainBlendState(0, False, 0)
    look = make_look().terrain
    assert new_terrain_blend_plugin("material", look, TEXTURES, state) == "plugin"
    [(material, owner, *rest)] = made
    assert material == "material"
    assert rest == ["TerrainBlend", 200, "TERRAIN_BLEND", "TerrainBlendPlugin"]
    assert isinstance(owner, TerrainBlendOwner)
    assert (owner._look, owner._textures, owner._state) == (look, TEXTURES, state)


def test_gfx_terrain_08_the_plugin_sets_its_define() -> None:
    defines = SimpleNamespace(TERRAIN_BLEND=False)
    _owner().prepare_defines(defines)
    assert defines.TERRAIN_BLEND is True


def test_gfx_terrain_08_the_plugin_adds_a_sampler_per_texture() -> None:
    samplers = Samplers(["diffuseSampler"])
    _owner().get_samplers(samplers)
    assert samplers == ["diffuseSampler", *SAMPLERS]


def test_gfx_terrain_08_the_uniforms_are_in_the_buffer_and_declared_in_the_shader() -> None:
    uniforms = _owner().get_uniforms()
    assert uniforms["ubo"] == [{"name": n, "size": s, "type": t} for n, s, t in UNIFORMS]
    fragment = uniforms["fragment"].split("\n")
    assert fragment[0] == "#ifdef TERRAIN_BLEND"
    assert fragment[1] == "uniform vec4 terrainHeights;"
    assert fragment[4] == "uniform vec3 terrainTintA;"
    assert fragment[-1] == "#endif"
    assert len(fragment) == len(UNIFORMS) + 2


def test_gfx_terrain_08_only_the_fragment_shader_gets_code() -> None:
    assert _owner().get_custom_code("vertex") is None
    assert _owner().get_custom_code("fragment") == {
        "CUSTOM_FRAGMENT_DEFINITIONS": FRAGMENT_DEFINITIONS,
        "CUSTOM_FRAGMENT_UPDATE_DIFFUSE": UPDATE_DIFFUSE,
        "CUSTOM_FRAGMENT_BEFORE_FOG": BEFORE_FOG,
    }


def test_gfx_terrain_09_the_surface_scale_is_written_into_the_shader_text() -> None:
    assert "@SURFACE_SCALE@" not in FRAGMENT_DEFINITIONS
    assert "uniform sampler2D terrainNoise;" in FRAGMENT_DEFINITIONS


def test_gfx_terrain_08_the_blend_heights_slopes_and_scales_are_bound() -> None:
    values = _bound(TerrainBlendState(3, True, 7)).values
    assert values["terrainHeights"] == (0, 20, 2, 0)
    assert values["terrainSlope"] == (0.5, 1, 0, 0)
    assert values["terrainScale"] == (1 / 32, 1 / 16, 1 / 8, 0)
    assert values["terrainTintA"] == WHITE
    assert values["terrainTintB"] == GREY


def test_gfx_terrain_09_without_lush_detail_the_grass_is_bound_flat() -> None:
    values = _bound(TerrainBlendState(3, True, 7)).values
    assert values["terrainLushTintA"] == (1, 1, 1)
    assert values["terrainLushTintB"] == (1, 1, 1)
    assert values["terrainLushDetail"][2] == 0


def test_gfx_terrain_09_the_lush_detail_is_bound_from_the_look() -> None:
    terrain = make_look().terrain
    terrain.lushDetail = LushDetail((WHITE, GREY), 400, 25, 0.3)
    ubo = FakeUbo()
    TerrainBlendOwner(terrain, TEXTURES, TerrainBlendState(3, True, 7)).bind_for_sub_mesh(ubo)
    values = ubo.values
    assert values["terrainLushTintA"] == WHITE
    assert values["terrainLushTintB"] == GREY
    assert values["terrainLushDetail"] == (1 / 400, 1 / 25, 0.3, 0)
    assert "terrainLushDetail" in FRAGMENT_DEFINITIONS


def test_gfx_water_04_the_shore_is_bound_from_the_look() -> None:
    values = _bound(TerrainBlendState(3, True, 7)).values
    assert values["terrainSand"] == (*GREY, 2)
    assert values["terrainShallow"] == (*GREY, 10)
    assert values["terrainDeep"] == BLACK
    assert values["terrainFoam"] == (*WHITE, 1)
    # Spacing, speed, reach; then the lava's cracks (1 by water).
    assert values["terrainSurf"] == (4, 1, 2, 1)


def test_gfx_water_02_by_water_the_sea_is_bound_without_lava_or_ground_frame() -> None:
    values = _bound(TerrainBlendState(3, True, 7)).values
    assert values["terrainSea"] == (3, 1, 7, 0)
    assert values["terrainLava"] == (0, 0, 0, 1)
    assert values["terrainGroundFrame"] == (1, 0, 0, 0)


def test_gfx_terrain_17_by_lava_the_rock_glows_and_the_ground_frame_is_bound() -> None:
    lava = SimpleNamespace(edge=LavaEdge((1, 0.5, 0), 3, 6))
    values = _bound(TerrainBlendState(-2, False, 4, lava, GroundTransform(2, 50))).values
    assert values["terrainSea"] == (-2, 0, 4, 1)
    assert values["terrainLava"] == (1, 0.5, 0, 3)
    assert values["terrainSurf"][3] == 6
    assert values["terrainGroundFrame"] == (2, 50, 0, 0)


def test_gfx_terrain_08_each_texture_is_bound_to_its_sampler() -> None:
    textures = _bound(TerrainBlendState(3, True, 7)).textures
    assert list(textures.values()) == [
        "low",
        "ground",
        "steep",
        "high",
        "lush",
        "paved",
        "sand",
        "noise",
    ]
    assert list(textures) == SAMPLERS
