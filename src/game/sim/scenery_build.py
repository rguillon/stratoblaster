"""Builds the core scenery of a level (P04, P06, P15) from its config record: the terrain sections,
roads, props and sea that `core/scenery/scenery_level.py` and the road network read. The config
keeps the TypeScript's camelCase shape; `core/` takes snake_case attributes, and an omitted optional
field is None. Mapping rules are in `config_build.py`.
"""

from org.transcrypt.stubs.browser import __pragma__

from core.scenery.scenery_level import (
    BlockFill,
    Boulevard,
    CarRules,
    Channel,
    Crevasses,
    Drift,
    Dual,
    Dunes,
    Flatten,
    FloatRules,
    HamletRules,
    Junction,
    Lakes,
    Landmark,
    Loners,
    Meander,
    MeanderRange,
    NoCrossings,
    PropGroupRule,
    PropKindRule,
    PropLine,
    PropRules,
    Relief,
    RoadRules,
    SceneryLevel,
    Sea,
    Shore,
    StreetGrid,
    Surface,
    TerrainSection,
    TileRules,
)
from game.sim.config_build import mapped, maybe, opt

__pragma__("skip")
from typing import Any  # noqa: E402

# A config record (`game/config/record.py`), typed as Any there.
ConfigRecord = Any
__pragma__("noskip")


def _meander(meander: ConfigRecord) -> Meander:
    return Meander(meander.x, meander.amplitude, meander.wavelength)


def _relief(relief: ConfigRecord) -> Relief:
    return Relief(
        relief.base,
        relief.amplitude,
        relief.frequency,
        relief.octaves,
        relief.style,
        opt(relief.maxHeight),
    )


def _flatten(flatten: ConfigRecord) -> Flatten:
    return Flatten(
        _meander(flatten.path),
        flatten.halfWidth,
        flatten.edge,
        flatten.height,
        flatten.roughness,
    )


def _channel(channel: ConfigRecord) -> Channel:
    return Channel(_meander(channel.path), channel.halfWidth, channel.wall, channel.floor)


def _shore(shore: ConfigRecord) -> Shore:
    return Shore(_meander(shore.path), shore.landSide, shore.width, shore.seabed)


def _dunes(dunes: ConfigRecord) -> Dunes:
    return Dunes(dunes.height, dunes.wavelength, dunes.angleDeg, dunes.warp)


def _lakes(lakes: ConfigRecord) -> Lakes:
    return Lakes(lakes.spacing, lakes.chance, lakes.radius, lakes.level, lakes.edge)


def _crevasses(crevasses: ConfigRecord) -> Crevasses:
    return Crevasses(
        crevasses.spacing,
        crevasses.width,
        crevasses.depth,
        crevasses.angleDeg,
        crevasses.warp,
        crevasses.share,
    )


def _surface(surface: ConfigRecord) -> Surface:
    return Surface(opt(surface.lush), opt(surface.paved), opt(surface.sandy))


def _street_grid(streets: ConfigRecord) -> StreetGrid:
    return StreetGrid(streets.rows, streets.columns, streets.links)


def _block_fill(blocks: ConfigRecord) -> BlockFill:
    return BlockFill(blocks.podiums, blocks.podiumHeight, blocks.towers)


def _section(section: ConfigRecord) -> TerrainSection:
    return TerrainSection(
        section["name"],
        section.seconds,
        _relief(section.relief),
        section.buildingDensity,
        section.treeDensity,
        maybe(section.flatten, _flatten),
        maybe(section.channel, _channel),
        maybe(section.shore, _shore),
        maybe(section.dunes, _dunes),
        maybe(section.lakes, _lakes),
        maybe(section.crevasses, _crevasses),
        opt(section.floatDensity),
        maybe(section.surface, _surface),
        opt(section.trees),
        opt(section.groups),
        maybe(section.streets, _street_grid),
        maybe(section.blocks, _block_fill),
    )


def _drift(drift: ConfigRecord) -> Drift:
    return Drift(drift.x, drift.z, drift.period)


def _prop_kind(kind: ConfigRecord) -> PropKindRule:
    return PropKindRule(
        kind.id,
        kind.weight,
        kind.footprint,
        kind.scale,
        opt(kind.frontage),
        maybe(kind.drift, _drift),
        opt(kind.tiles),
    )


def _float_rules(floating: ConfigRecord) -> FloatRules:
    return FloatRules(
        floating.cellSize,
        floating.perCell,
        floating.depth,
        mapped(floating.kinds, _prop_kind),
    )


def _prop_line(line: ConfigRecord) -> PropLine:
    return PropLine(
        line.kind,
        _meander(line.path),
        line.spacing,
        line.footprint,
        line.maxSlope,
        opt(line.sections),
        opt(line.overWater),
        maybe(line.drift, _drift),
    )


def _landmark(landmark: ConfigRecord) -> Landmark:
    return Landmark(
        landmark.kind,
        landmark.z,
        landmark.footprint,
        opt(landmark.x),
        maybe(landmark.path, _meander),
        opt(landmark.rotation),
        opt(landmark.scale),
        opt(landmark.onWater),
    )


def _group(group: ConfigRecord) -> PropGroupRule:
    return PropGroupRule(group.id, group.weight, mapped(group.kinds, _prop_kind))


def _loners(loners: ConfigRecord) -> Loners:
    return Loners(loners.cell, loners.chance, loners.clearance)


def _hamlets(hamlets: ConfigRecord) -> HamletRules:
    return HamletRules(
        hamlets.spacing,
        hamlets.buildings,
        hamlets.radius,
        hamlets.gap,
        hamlets.clearance,
    )


def _cars(cars: ConfigRecord) -> CarRules:
    return CarRules(
        cars.kinds,
        cars.density,
        cars.lift,
        cars.scale,
        cars["length"],
        cars.speed,
        opt(cars.sidewalk),
    )


def _props(props: ConfigRecord) -> PropRules:
    return PropRules(
        props.cellSize,
        props.treeClearance,
        props.maxSlope,
        props.treeMaxSlope,
        props.minHeight,
        props.zoneFrequency,
        mapped(props.groups, _group),
        mapped(props.trees, _prop_kind),
        props.treesPerCell,
        maybe(props.cars, _cars),
        maybe(props.loners, _loners),
        maybe(props.hamlets, _hamlets),
        maybe(props.floating, _float_rules),
        maybe(props.lines, _lines),
        maybe(props.landmarks, _landmarks),
        maybe(props.lots, _lots),
    )


def _lines(lines: ConfigRecord) -> list[PropLine]:
    return mapped(lines, _prop_line)


def _landmarks(landmarks: ConfigRecord) -> list[Landmark]:
    return mapped(landmarks, _landmark)


def _lots(lots: ConfigRecord) -> list[PropKindRule]:
    return mapped(lots, _prop_kind)


def _boulevards(boulevards: ConfigRecord) -> list[Boulevard]:
    return mapped(boulevards, _boulevard)


def _sea(sea: ConfigRecord) -> Sea:
    return Sea(sea.level)


def _tiles(tiles: ConfigRecord) -> TileRules:
    return TileRules(tiles.size, tiles.sidewalk)


def _boulevard(boulevard: ConfigRecord) -> Boulevard:
    return Boulevard(boulevard.lanes, boulevard.width, boulevard.share)


def _dual(dual: ConfigRecord) -> Dual:
    return Dual(dual.width, dual.mainRoads, dual.avenues)


def _junction(junction: ConfigRecord) -> Junction:
    return Junction(junction.width, junction["length"])


def _no_crossings(no_crossings: ConfigRecord) -> NoCrossings:
    return NoCrossings(no_crossings.gap)


def _roads(roads: ConfigRecord) -> RoadRules:
    meander = roads.meander
    return RoadRules(
        roads.mainRoads,
        roads.spread,
        MeanderRange(meander.amplitude, meander.wavelength),
        roads.crossSpacing,
        roads.crossBend,
        roads.mainWidth,
        roads.crossWidth,
        _dual(roads.dual),
        _junction(roads.junction),
        roads.offscreenX,
        roads.turnRate,
        roads.minHeight,
        roads.maxSlope,
        roads.minRun,
        roads.step,
        roads.slotSpacing,
        roads.setback,
        maybe(roads.boulevards, _boulevards),
        maybe(roads.noCrossings, _no_crossings),
        maybe(roads.tiles, _tiles),
    )


def scenery_level(config: ConfigRecord) -> SceneryLevel:
    """The scenery of a level, as `core/` reads it (P04)."""
    return SceneryLevel(
        config.id,
        config["name"],
        config.seed,
        config.scrollSpeed,
        config.transition,
        mapped(config.sections, _section),
        _roads(config.roads),
        _props(config.props),
        maybe(config.sea, _sea),
        None,
    )
