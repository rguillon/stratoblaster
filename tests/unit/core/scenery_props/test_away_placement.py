"""Lone buildings and hamlets away from the roads (`core.scenery.away_placement`), placed on a fake
site: the placer's own tests (`test_prop_placement.py`) cover them on a real level."""

import math

import pytest
from sample_level import flat

from core.scenery.away_placement import (
    AWAY_MARGIN,
    BUILDING_TRIES,
    Building,
    Candidate,
    ZSpan,
    _round,
    _standalone,
    place_hamlets,
    place_loners,
)
from core.scenery.ground_boxes import PropPlacement
from core.scenery.scenery_level import (
    HamletRules,
    Loners,
    PropGroupRule,
    PropKindRule,
    StreetGrid,
    TerrainSection,
)


def kind(footprint: float = 3, frontage: float | None = None) -> PropKindRule:
    return PropKindRule("house", 1, footprint, [1, 1], frontage=frontage)


class FakeSite:
    """A site of a flat level: every spot is clear of the roads and flat unless told otherwise.
    `add` keeps the buildings apart by their boxes and the gap, as the placer does."""

    def __init__(
        self,
        section: TerrainSection | None = None,
        group: PropGroupRule | None = None,
        clear: bool = True,
        ground: bool = True,
        accept: bool = True,
    ) -> None:
        self.length_ = 1000.0
        self.offscreen_x = 400.0
        self.seed = 3
        self.section = section if section is not None else flat("open", 10, 0)
        self.group = group if group is not None else PropGroupRule("g", 1, [kind()])
        self.clear = clear
        self.ground_ok = ground
        self.accept = accept
        self.added: list[Building] = []
        self.group_calls = 0

    def section_at(self, z: float) -> TerrainSection:
        return self.section

    def group_at(self, x: float, z: float, section: TerrainSection) -> PropGroupRule | None:
        self.group_calls += 1
        return self.group

    def clear_of_roads(self, x: float, z: float, clearance: float) -> bool:
        return self.clear

    def ground(self, x: float, z: float, radius: float) -> float | None:
        return 0.0 if self.ground_ok else None

    def add(self, building: Building, gap: float | None) -> bool:
        if not self.accept:
            return False
        self.added.append(building)
        return True


HAMLETS = HamletRules(spacing=[100, 100], buildings=[3, 3], radius=20, gap=2, clearance=1)


def test_round_is_javascripts_math_round() -> None:
    assert _round(2.5) == 3
    assert _round(2.4) == 2
    assert _round(-0.5) == 0


def test_standalone_turns_square_plans_by_their_frontage() -> None:
    site = FakeSite()
    c = Candidate(kind(footprint=8, frontage=5), 10, 20, 0.0, 1.0)
    building = _standalone(site, c, 1)
    assert building is not None
    assert building.half_x == pytest.approx(5)
    assert building.placement.y == 0
    turned = Candidate(kind(footprint=8, frontage=5), 10, 20, math.pi / 4, 2)
    rotated = _standalone(site, turned, 1)
    assert rotated is not None
    assert rotated.half_x == pytest.approx(10 * (math.cos(math.pi / 4) + math.sin(math.pi / 4)))


def test_standalone_keeps_the_footprint_circle_for_other_plans() -> None:
    building = _standalone(FakeSite(), Candidate(kind(3), 0, 0, 1.0, 1.0), 1)
    assert building is not None
    assert (building.half_x, building.half_z) == (3, 3)


def test_standalone_refuses_roads_and_steep_ground() -> None:
    assert _standalone(FakeSite(clear=False), Candidate(kind(), 0, 0, 0, 1), 1) is None
    assert _standalone(FakeSite(ground=False), Candidate(kind(), 0, 0, 0, 1), 1) is None


def test_hamlets_stand_in_their_span_only() -> None:
    site = FakeSite()
    place_hamlets(site, HAMLETS, ZSpan(-math.inf, math.inf))
    everything = len(site.added)
    site = FakeSite()
    place_hamlets(site, HAMLETS, ZSpan(0, 1))
    assert everything > 0
    assert 0 < len(site.added) < everything


def test_hamlets_have_their_buildings_of_one_group() -> None:
    site = FakeSite()
    place_hamlets(site, HAMLETS, ZSpan(-math.inf, math.inf))
    assert len(site.added) % 3 == 0
    assert {b.placement.kind for b in site.added} == {"house"}


def test_hamlets_are_placed_again_the_same_way() -> None:
    first = FakeSite()
    place_hamlets(first, HAMLETS, ZSpan(-math.inf, math.inf))
    second = FakeSite()
    place_hamlets(second, HAMLETS, ZSpan(-math.inf, math.inf))
    assert [(b.placement.x, b.placement.z) for b in first.added] == [
        (b.placement.x, b.placement.z) for b in second.added
    ]


def test_hamlets_skip_streets_and_sections_without_buildings() -> None:
    grid = TerrainSection(
        "grid", 10, flat("grid", 10, 0).relief, 1, 1, streets=StreetGrid([50, 60], [50, 60], 1)
    )
    empty = TerrainSection("empty", 10, flat("empty", 10, 0).relief, 0, 1)
    for section in (grid, empty):
        site = FakeSite(section=section)
        place_hamlets(site, HAMLETS, ZSpan(-math.inf, math.inf))
        assert site.added == []


def test_hamlets_need_a_centre_clear_of_the_roads_on_flat_ground() -> None:
    place = FakeSite(clear=False)
    place_hamlets(place, HAMLETS, ZSpan(-math.inf, math.inf))
    assert place.added == []
    flat_ground_missing = FakeSite(ground=False)
    place_hamlets(flat_ground_missing, HAMLETS, ZSpan(-math.inf, math.inf))
    assert flat_ground_missing.added == []


def test_hamlets_need_a_group_that_allows_them_there() -> None:
    site = FakeSite(group=PropGroupRule("none", 1, []))
    site.group_at = lambda x, z, section: None  # type: ignore[method-assign]
    place_hamlets(site, HAMLETS, ZSpan(-math.inf, math.inf))
    assert site.added == []


def test_hamlets_stop_when_a_group_has_no_kinds() -> None:
    site = FakeSite(group=PropGroupRule("empty", 1, []))
    place_hamlets(site, HAMLETS, ZSpan(-math.inf, math.inf))
    assert site.added == []


def test_hamlets_try_again_when_buildings_do_not_fit() -> None:
    site = FakeSite(accept=False)
    place_hamlets(site, HAMLETS, ZSpan(-math.inf, math.inf))
    assert site.added == []
    # Each hamlet tries BUILDING_TRIES buildings per building wanted, and no more.
    assert site.group_calls <= 6 * BUILDING_TRIES * 3


def test_loners_are_one_chance_per_cell_inside_the_span() -> None:
    site = FakeSite()
    place_loners(site, Loners(100, 1, 1), ZSpan(0, 300))
    assert site.added
    assert all(0 <= b.placement.z < 300 for b in site.added)


def test_loners_need_the_chance_and_a_section_with_buildings() -> None:
    site = FakeSite()
    place_loners(site, Loners(100, 0, 1), ZSpan(0, 300))
    assert site.added == []
    site = FakeSite(section=TerrainSection("g", 10, flat("g", 10, 0).relief, 0, 1))
    place_loners(site, Loners(100, 1, 1), ZSpan(0, 300))
    assert site.added == []
    grid = TerrainSection(
        "grid", 10, flat("g", 10, 0).relief, 1, 1, streets=StreetGrid([50, 60], [50, 60], 1)
    )
    site = FakeSite(section=grid)
    place_loners(site, Loners(100, 1, 1), ZSpan(0, 300))
    assert site.added == []


def test_loners_need_a_kind_of_their_group() -> None:
    site = FakeSite(group=PropGroupRule("empty", 1, []))
    place_loners(site, Loners(100, 1, 1), ZSpan(0, 300))
    assert site.added == []
    site = FakeSite()
    site.group_at = lambda x, z, section: None  # type: ignore[method-assign]
    place_loners(site, Loners(100, 1, 1), ZSpan(0, 300))
    assert site.added == []


def test_loners_are_refused_when_they_do_not_fit() -> None:
    site = FakeSite(accept=False)
    place_loners(site, Loners(100, 1, 1), ZSpan(0, 300))
    assert site.added == []


def test_loners_keep_to_the_span_of_the_chunk() -> None:
    site = FakeSite()
    place_loners(site, Loners(100, 1, 1), ZSpan(100, 200))
    assert site.added
    assert all(100 <= b.placement.z < 200 for b in site.added)
    # Cells of 70 straddle the span: their loners outside it are left for the chunk they are in.
    straddling = FakeSite()
    place_loners(straddling, Loners(70, 1, 1), ZSpan(100, 200))
    assert straddling.added
    assert all(100 <= b.placement.z < 200 for b in straddling.added)


def test_away_margin_is_the_reach_past_the_level() -> None:
    assert AWAY_MARGIN == 400


@pytest.mark.xfail(
    strict=True,
    raises=OverflowError,
    reason="place_loners floors an infinite span (the first and last chunks): math.floor(-inf) "
    "raises in CPython (away_placement.py); Transcrypt's Math.floor does not",
)
def test_loners_take_an_unbounded_span_as_the_first_chunk_does() -> None:
    site = FakeSite()
    place_loners(site, Loners(100, 1, 1), ZSpan(-math.inf, 300))
    assert site.added


def test_placement_is_a_plain_record() -> None:
    p = PropPlacement("house", 1, 2, 3, 0.5, 1)
    b = Building(p, 4, 5)
    assert (b.placement, b.half_x, b.half_z) == (p, 4, 5)
