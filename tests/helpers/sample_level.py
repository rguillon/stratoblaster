"""A tiny scenery level for the placement tests: the parts of
the placers read. Two flat sections of 10 s at 20 units/s, a sea,
one straight main road along X = 0, straight paths every 100 units out to X = +-100 (off screen),
and two prop kinds."""

from core.scenery.scenery_level import (
    Dual,
    Junction,
    Meander,
    MeanderRange,
    PropGroupRule,
    PropKindRule,
    PropRules,
    Relief,
    RoadRules,
    SceneryLevel,
    Sea,
    TerrainSection,
)


def flat(name: str, seconds: float, base: float) -> TerrainSection:
    """A section of smooth, gentle relief around `base`."""
    relief = Relief(base, 2, 1 / 100, 2, "smooth")
    return TerrainSection(name, seconds, relief, building_density=1, tree_density=1)


def sample_roads(**overrides: object) -> RoadRules:
    """The road rules of the sample: one straight main road, paths every 100 units."""
    values: dict[str, object] = {
        "main_roads": 1,
        "spread": 0,
        "meander": MeanderRange([0, 0], [100, 100]),
        "cross_spacing": [100, 100],
        "cross_bend": 0,
        "main_width": 6,
        "cross_width": 4,
        "dual": Dual(12, 0, 0),
        "junction": Junction(8, 10),
        "offscreen_x": 100,
        "turn_rate": 0.1,
        "min_height": 1,
        "max_slope": 0.5,
        "min_run": 3,
        "step": 5,
        "slot_spacing": 20,
        "setback": 1,
    }
    values.update(overrides)
    return RoadRules(**values)  # type: ignore[arg-type]


def block_kind(**overrides: object) -> PropKindRule:
    """A building kind: a 5-unit footprint, unit scale."""
    values: dict[str, object] = {"id": "block", "weight": 1, "footprint": 5, "scale": [1, 1]}
    values.update(overrides)
    return PropKindRule(**values)  # type: ignore[arg-type]


def stick_kind(**overrides: object) -> PropKindRule:
    """A tree kind: a 1-unit footprint, scale 1 to 2."""
    values: dict[str, object] = {"id": "stick", "weight": 1, "footprint": 1, "scale": [1, 2]}
    values.update(overrides)
    return PropKindRule(**values)  # type: ignore[arg-type]


def sample_props(**overrides: object) -> PropRules:
    """The prop rules of the sample: one building group, one tree kind, two trees per cell."""
    values: dict[str, object] = {
        "cell_size": 40,
        "tree_clearance": 1,
        "max_slope": 0.5,
        "tree_max_slope": 1,
        "min_height": 1,
        "zone_frequency": 1 / 200,
        "groups": [PropGroupRule("blocks", 1, [block_kind()])],
        "trees": [stick_kind()],
        "trees_per_cell": 2,
    }
    values.update(overrides)
    return PropRules(**values)  # type: ignore[arg-type]


def sample_level(
    sections: list[TerrainSection] | None = None,
    roads: RoadRules | None = None,
    props: PropRules | None = None,
    seed: int = 7,
) -> SceneryLevel:
    """The sample level, with optional replacements of its sections, roads and props."""
    return SceneryLevel(
        id="sample-ground",
        name="Sample ground",
        seed=seed,
        scroll_speed=20,
        transition=40,
        sections=sections if sections is not None else [flat("low", 10, 10), flat("high", 10, 30)],
        roads=roads if roads is not None else sample_roads(),
        props=props if props is not None else sample_props(),
        sea=Sea(0),
    )


__all__ = ["Meander", "flat", "sample_level", "sample_props", "sample_roads"]


def sample_atmosphere(lightning: float = 0.0, haze: tuple[float, float, float] = (0.5, 0.5, 0.6)):
    """A plain atmosphere for the look and lightning tests: one sky stop pair, no clouds."""
    from core.scenery.atmosphere import (  # noqa: PLC0415 (a helper of the tests)
        Ambient,
        Atmosphere,
        Fog,
        Sky,
        SkyStop,
        Sun,
        Weather,
    )

    return Atmosphere(
        Sun(45, 0, (1, 1, 1), 1, 0.5),
        Sky(haze, [SkyStop(-1, (0, 0, 0)), SkyStop(1, (1, 1, 1))], 1),
        Ambient((1, 1, 1), (0.2, 0.2, 0.2), 0.5),
        Fog(100, 1000),
        [],
        0.0,
        Weather("snow", 0),
        0.0,
        lightning,
    )
