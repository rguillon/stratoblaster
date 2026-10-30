"""Unit tests of `src/render/scenery/scenery_stage.py`: its small pure helpers. The stage itself
builds Babylon meshes and runs in the browser."""

from types import SimpleNamespace

from render.scenery.scenery_kit import SceneryKitContext, SeaSize
from render.scenery.scenery_stage import _concat, _kit_context, _props_of, _sky_placement
from render.scenery.sky_layers import SkyPlacement


def test_concat_joins_two_sequences_into_a_new_list() -> None:
    first = [1, 2]
    second = (3,)
    joined = _concat(first, second)
    assert joined == [1, 2, 3]
    assert joined is not first


def test_concat_of_nothing_is_empty() -> None:
    assert _concat([], []) == []


def test_the_kit_context_carries_the_sea_size() -> None:
    context = _kit_context("look", "sun", 3.0, 400, 300, 9)
    assert isinstance(context, SceneryKitContext)
    assert context.look == "look"
    assert context.sea_level == 3.0
    assert context.sun == "sun"
    assert isinstance(context.sea_size, SeaSize)
    assert (context.sea_size.width, context.sea_size.length_) == (400, 300)
    assert context.seed == 9


def test_the_sky_placement_keeps_its_callbacks_and_margin() -> None:
    placement = _sky_placement(len, abs, 100, 20)
    assert isinstance(placement, SkyPlacement)
    assert placement.flight_altitude == 100


def test_the_props_materials_are_the_kit_props() -> None:
    kit = SimpleNamespace(props="materials")
    assert _props_of(kit) == "materials"
