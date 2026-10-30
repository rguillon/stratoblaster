"""The data of a scrolling level (P04-R01, P04-R06, P07-R03): `core/scenery/scenery_level.py`."""

import pytest
from level_builders import flat, make_level, section, street_grid

from core.scenery.scenery_level import (
    layout_sections,
    level_duration,
    level_length,
    runout_start,
    with_runout,
)


def test_p04_r01_sections_are_laid_end_to_end_from_zero() -> None:
    level = make_level([section("a", 10, flat()), section("b", 5, flat())], speed=100.0)
    placed = layout_sections(level)
    assert [(p.start, p.end) for p in placed] == [(0.0, 1000.0), (1000.0, 1500.0)]
    assert placed[1].section.name == "b"


def test_p04_r01_a_level_needs_sections_speed_and_lengths() -> None:
    with pytest.raises(ValueError):
        layout_sections(make_level([]))
    with pytest.raises(ValueError):
        layout_sections(make_level([section("a", 10, flat())], speed=0.0))
    with pytest.raises(ValueError):
        layout_sections(make_level([section("a", 0.0, flat())]))


def test_p04_r06_the_duration_and_length_add_up_the_sections() -> None:
    level = make_level([section("a", 10, flat()), section("b", 5, flat())], speed=100.0)
    assert level_duration(level) == pytest.approx(15.0)
    assert level_length(level) == pytest.approx(1500.0)


def test_p07_r03_a_runout_extends_the_last_section_and_adds_up() -> None:
    level = make_level([section("a", 10, flat()), section("b", 5, flat())], speed=100.0)
    assert with_runout(level, 0.0) is level
    extended = with_runout(level, 30.0)
    assert extended.runout == pytest.approx(30.0)
    assert [s.seconds for s in extended.sections] == [10.0, 35.0]
    assert level_duration(extended) == pytest.approx(45.0)
    again = with_runout(extended, 20.0)
    assert again.runout == pytest.approx(50.0)
    # The level it was made from is as it was.
    assert level.runout is None and level.sections[1].seconds == 5.0


def test_p07_r03_the_runout_starts_where_its_seconds_begin() -> None:
    level = make_level([section("a", 10, flat()), section("b", 5, flat())], speed=100.0)
    assert runout_start(level) is None
    assert runout_start(with_runout(level, 0.0)) is None
    # The runout is the last 30 seconds: it starts where the level stopped before it.
    assert runout_start(with_runout(level, 30.0)) == pytest.approx(1500.0)


def test_a_runout_keeps_the_fields_of_the_last_section() -> None:
    streets = street_grid()
    last = section("b", 5, flat(), streets=streets, building_density=0.7)
    extended = with_runout(make_level([section("a", 10, flat()), last]), 3.0)
    copy = extended.sections[1]
    assert copy.streets is streets
    assert copy.building_density == 0.7
    assert copy.seconds == pytest.approx(8.0)


def test_with_runout_of_a_level_without_sections_is_the_same_level() -> None:
    empty = make_level([])
    assert with_runout(empty, 10.0) is empty


def test_the_terrain_and_prop_data_records_keep_their_fields() -> None:
    from core.scenery.scenery_level import (  # noqa: PLC0415
        BlockFill,
        CarRules,
        Drift,
        FloatRules,
        HamletRules,
        Landmark,
        Loners,
        Meander,
        PropGroupRule,
        PropKindRule,
        PropLine,
        Sea,
        TileRules,
    )

    drift = Drift(2.0, 3.0, 4.0)
    assert (drift.x, drift.z, drift.period) == (2.0, 3.0, 4.0)
    kind = PropKindRule("k", 1.0, 2.0, (0.5, 1.0), drift=drift)
    assert kind.drift is drift
    floating = FloatRules(40.0, 2, 5.0, [kind])
    assert (floating.cell_size, floating.per_cell, floating.depth) == (40.0, 2, 5.0)
    line = PropLine("pipe", Meander(0.0, 1.0, 2.0), 30.0, 4.0, 0.2, over_water=True)
    assert (line.kind, line.spacing, line.over_water) == ("pipe", 30.0, True)
    landmark = Landmark("dam", 100.0, (5.0, 5.0), on_water=True)
    assert (landmark.kind, landmark.z, landmark.on_water) == ("dam", 100.0, True)
    group = PropGroupRule("g", 2.0, [kind])
    assert (group.id, group.weight, group.kinds) == ("g", 2.0, [kind])
    loners = Loners(50.0, 0.1, 6.0)
    assert (loners.cell, loners.chance, loners.clearance) == (50.0, 0.1, 6.0)
    hamlets = HamletRules((100.0, 200.0), (3.0, 5.0), 40.0, 8.0, 6.0)
    assert (hamlets.radius, hamlets.gap, hamlets.clearance) == (40.0, 8.0, 6.0)
    cars = CarRules(["car"], 0.2, 1.0, 1.5, 12.0, (10.0, 20.0), sidewalk=3.0)
    assert (cars.length_, cars.sidewalk, cars.kinds) == (12.0, 3.0, ["car"])
    assert TileRules(24.0, 4.0).sidewalk == 4.0
    assert Sea(12.0).level == 12.0
    block = BlockFill(["p1"], (1.0, 2.0), (3.0, 4.0))
    assert (block.podiums, block.podium_height, block.towers) == (["p1"], (1.0, 2.0), (3.0, 4.0))
