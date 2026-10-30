"""Hand-made scenery levels for the tests of `core/scenery/`. The game's own configs do not import
under CPython (their records are plain dicts), so the tests build the small levels they need here.
Every default is a neutral value: flat ground, no slope limit, no sea."""

from core.scenery.scenery_level import (
    Dual,
    Junction,
    MeanderRange,
    PropRules,
    Relief,
    RoadRules,
    SceneryLevel,
    StreetGrid,
    TerrainSection,
    TileRules,
)


def flat(base: float = 10.0) -> Relief:
    """Ground at exactly `base` everywhere."""
    return Relief(base, 0.0, 1 / 400, 3, "smooth")


def hills(base: float = 50.0, amplitude: float = 30.0, max_height: float | None = None) -> Relief:
    """Rolling smooth ground from `base - amplitude` to `base + amplitude`."""
    return Relief(base, amplitude, 1 / 400, 3, "smooth", max_height)


def street_grid(links: float = 0.55) -> StreetGrid:
    return StreetGrid((60.0, 110.0), (70.0, 130.0), links)


def section(
    name: str = "s",
    seconds: float = 10.0,
    relief: Relief | None = None,
    **options: object,
) -> TerrainSection:
    """A terrain section; `options` are the optional fields of `TerrainSection` (`streets`, ...)."""
    return TerrainSection(
        name,
        seconds,
        relief if relief is not None else flat(),
        options.pop("building_density", 0.5),  # type: ignore[arg-type]
        options.pop("tree_density", 0.2),  # type: ignore[arg-type]
        **options,  # type: ignore[arg-type]
    )


def road_rules(**overrides: object) -> RoadRules:
    values: dict[str, object] = {
        "main_roads": 2,
        "spread": 200.0,
        "meander": MeanderRange((40.0, 80.0), (600.0, 900.0)),
        "cross_spacing": (250.0, 400.0),
        "cross_bend": 60.0,
        "main_width": 24.0,
        "cross_width": 12.0,
        "dual": Dual(48.0, 1, 0.2),
        "junction": Junction(30.0, 60.0),
        "offscreen_x": 300.0,
        "turn_rate": 0.1,
        "min_height": -1e9,
        "max_slope": 1e9,
        "min_run": 3,
        "step": 10.0,
        "slot_spacing": 40.0,
        "setback": 4.0,
    }
    values.update(overrides)
    return RoadRules(**values)  # type: ignore[arg-type]


def prop_rules(**overrides: object) -> PropRules:
    values: dict[str, object] = {
        "cell_size": 40.0,
        "tree_clearance": 6.0,
        "max_slope": 0.5,
        "tree_max_slope": 0.8,
        "min_height": -1e9,
        "zone_frequency": 0.002,
        "groups": [],
        "trees": [],
        "trees_per_cell": 1,
    }
    values.update(overrides)
    return PropRules(**values)  # type: ignore[arg-type]


def make_level(
    sections: list[TerrainSection],
    *,
    seed: int = 7,
    speed: float = 100.0,
    transition: float = 0.0,
    roads: RoadRules | None = None,
    props: PropRules | None = None,
    runout: float | None = None,
) -> SceneryLevel:
    return SceneryLevel(
        "test",
        "Test level",
        seed,
        speed,
        transition,
        sections,
        roads if roads is not None else road_rules(),
        props if props is not None else prop_rules(),
        None,
        runout,
    )


def tile_rules() -> TileRules:
    """Tiles 24 units a side: a one-lane street is one tile wide (`road_rules` widths fit)."""
    return TileRules(24.0, 4.0)


# Sample points spread over a level, for comparing two heights or two networks.
SAMPLE_XS = (-150.0, -40.0, 0.0, 33.0, 120.0)
SAMPLE_ZS = (-20.0, 0.0, 55.5, 300.0, 999.0)
SAMPLE_POINTS = [(x, z) for x in SAMPLE_XS for z in SAMPLE_ZS]
