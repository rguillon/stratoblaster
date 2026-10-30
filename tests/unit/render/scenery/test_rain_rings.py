"""Unit tests of `src/render/scenery/rain_rings.py`."""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import FakeNode, FakeScene, patch_babylon
from helpers.sample_level import sample_atmosphere

from config.weather import WEATHER_KINDS
from core.scenery.atmosphere import Weather
from render.scenery import rain_rings
from render.scenery.rain_rings import LIFT, RINGS_ALPHA_INDEX, RainRings, RingsFrame


class _Material:
    """A rings material: the frames it was driven with."""

    def __init__(self, rings: Any) -> None:
        self.rings = rings
        self.material = "rings-of-" + str(rings.color)
        self.frames: list[RingsFrame] = []

    def set(self, frame: RingsFrame) -> None:
        self.frames.append(frame)


@pytest.fixture(autouse=True)
def _babylon(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_babylon(monkeypatch, rain_rings)
    monkeypatch.setattr(rain_rings, "create_ground_sized", _ground)


def _ground(label: str, width: float, height: float, scene: Any) -> FakeNode:
    node = scene.add_node(label, is_mesh=True)
    node.size = (width, height)
    return node


def _rings(kinds: Any = WEATHER_KINDS) -> tuple[RainRings, list[_Material]]:
    made: list[_Material] = []

    def factory(scene: Any, rings: Any) -> _Material:
        material = _Material(rings)
        made.append(material)
        return material

    layer = RainRings(FakeScene(), factory, (5.0, 40.0, 30.0), kinds)
    return layer, made


def _weather(kind: str, strength: float) -> Any:
    atmosphere = sample_atmosphere()
    atmosphere.weather = Weather(kind, strength)
    return atmosphere


def test_the_rings_plane_lies_a_little_above_the_water_and_starts_hidden() -> None:
    layer, _ = _rings()
    assert layer._plane.position.y == pytest.approx(5.0 + LIFT)
    assert layer._plane.size == (40.0, 30.0)
    assert layer._plane.isPickable is False
    assert layer._plane.alphaIndex == RINGS_ALPHA_INDEX
    assert layer._plane.enabled is False
    assert layer.shown == 0


def test_rain_rings_show_at_its_strength_on_the_plane_centred_at_z() -> None:
    layer, made = _rings()
    layer.update(_weather("rain", 0.5), (2.0, 77.0, True))
    assert layer.shown == pytest.approx(0.5)
    assert layer._plane.enabled is True
    assert layer._plane.position.z == 77.0
    assert layer._plane.material == made[0].material


def test_the_material_is_driven_with_the_time_strength_and_fog_of_the_frame() -> None:
    layer, made = _rings()
    atmosphere = _weather("rain", 0.5)
    layer.update(atmosphere, (2.0, 77.0, True))
    frame = made[0].frames[-1]
    assert frame.time == 2.0
    assert frame.strength == pytest.approx(0.5)
    assert frame.fog.color == atmosphere.sky.haze
    assert (frame.fog.start, frame.fog.end) == (atmosphere.fog.start, atmosphere.fog.end)


def test_the_rings_of_a_kind_are_made_by_the_factory_once_and_reused() -> None:
    layer, made = _rings()
    layer.update(_weather("rain", 0.5), (0, 0, True))
    layer.update(_weather("rain", 0.8), (1, 0, True))
    assert len(made) == 1
    assert made[0].rings is WEATHER_KINDS["rain"].rings
    assert [f.strength for f in made[0].frames] == [pytest.approx(0.5), pytest.approx(0.8)]


def test_the_strength_is_kept_between_zero_and_one() -> None:
    layer, _ = _rings()
    layer.update(_weather("rain", 3.0), (0, 0, True))
    assert layer.shown == 1
    layer.update(_weather("rain", -1.0), (0, 0, True))
    assert layer.shown == 0


def test_no_rings_are_shown_while_the_water_is_hidden() -> None:
    layer, made = _rings()
    layer.update(_weather("rain", 0.9), (0, 0, False))
    assert layer.shown == 0
    assert layer._plane.enabled is False
    assert made == []


def test_a_weather_without_rings_shows_none() -> None:
    layer, made = _rings()
    layer.update(_weather("snow", 1.0), (0, 0, True))
    assert layer.shown == 0
    assert layer._plane.enabled is False
    assert made == []


def test_a_weather_of_no_strength_shows_no_rings() -> None:
    layer, _ = _rings()
    layer.update(_weather("rain", 0), (0, 0, True))
    assert layer.shown == 0
    assert layer._plane.enabled is False


def test_an_unknown_weather_kind_shows_no_rings() -> None:
    layer, made = _rings()
    layer.update(_weather("hail", 1.0), (0, 0, True))
    assert layer.shown == 0
    assert made == []


def test_the_rings_of_a_custom_set_of_kinds_come_from_that_set() -> None:
    rings = SimpleNamespace(color=(1, 0, 0), alpha=0.5)
    kinds = {"hail": SimpleNamespace(rings=rings)}
    layer, made = _rings(kinds)
    layer.update(_weather("hail", 1.0), (0, 0, True))
    assert layer.shown == 1
    assert made[0].rings is rings


def test_a_kind_with_no_rings_in_a_custom_set_shows_none() -> None:
    layer, _ = _rings({"hail": SimpleNamespace(rings=None)})
    layer.update(_weather("hail", 1.0), (0, 0, True))
    assert layer.shown == 0
