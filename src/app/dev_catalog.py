"""What each dev viewer lists (D-199): the player ships, the enemy kinds, the boss kinds, the props
the levels stand on their ground and their cars (D-209), and the levels, in the game's order. The
props are gathered by the game's prop groups (D-202), as the TypeScript `props/` page showed them.
"""

from org.transcrypt.stubs.browser import __pragma__

from config.dev_viewer import DEV_VIEWERS
from render.scenery.prop_field import level_prop_kinds

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


# The group of the props in none of the game's prop groups (D-202).
OTHER_GROUP = "Other"


class DevItem:
    """One item of a dev viewer: its `id` (ship, kind, prop or level id), the `label` shown, the
    level it is shown over (`host`: a prop stands on the first level that has it), the `group`
    it is listed in ("": none; D-202), and the `scale` a prop is drawn at (D-209: the cars')."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self, id: str, label: str, host: str, group: str = "", scale: float = 1
    ) -> None:
        self.id = id
        self.label = label
        self.host = host
        self.group = group
        self.scale = scale


def _first_level(game: Any) -> str:
    levels = game.game_levels
    if len(levels) == 0:
        raise ValueError("The game has no level")
    first: str = levels[0].id
    return first


def _level_label(game: Any, level_id: str) -> str:
    for entry in game.levels.levels:
        if entry.id == level_id:
            label: str = entry.label
            return label
    return level_id


def _prop_groups(game: Any) -> list[Any]:
    """The game's prop groups (`PropGroup`s), none when its view names none."""
    scenery = game.view.scenery
    if "propGroups" not in scenery or scenery["propGroups"] is None:
        return []
    groups: list[Any] = scenery["propGroups"]
    return groups


def car_kinds(scenery: Any) -> list[str]:
    """The kinds of car driving on the roads of the scenery level `scenery` (D-209)."""
    cars = scenery.props.cars
    if cars is None:
        return []
    kinds: list[str] = list(cars.kinds)
    return kinds


def car_scale(scenery: Any) -> float:
    """The scale the cars of the scenery level `scenery` are drawn at (D-209)."""
    scale: float = scenery.props.cars.scale
    return scale


def _props(game: Any) -> list[DevItem]:
    """The props of every level's ground and its cars (D-209), each over the first level that has
    it, so it has its world's tone; gathered by the game's prop groups, in their order, then the
    props in none of them (D-202)."""
    hosts: dict[str, str] = {}
    scales: dict[str, float] = {}
    kinds: list[str] = []
    for level in game.game_levels:
        level_kinds = level_prop_kinds(level.scenery)
        cars = car_kinds(level.scenery)
        level_kinds.extend(cars)
        for kind in level_kinds:
            if kind not in kinds:
                kinds.append(kind)
                hosts[kind] = level.id
                scales[kind] = car_scale(level.scenery) if kind in cars else 1
    items: list[DevItem] = []
    listed: list[str] = []
    for group in _prop_groups(game):
        for kind in group.ids:
            if kind in kinds and kind not in listed:
                listed.append(kind)
                items.append(DevItem(kind, kind, hosts[kind], group.label, scales[kind]))
    for kind in kinds:
        if kind not in listed:
            items.append(DevItem(kind, kind, hosts[kind], OTHER_GROUP, scales[kind]))
    return items


def dev_items(game: Any, viewer: str) -> list[DevItem]:
    """The items the dev viewer `viewer` (one of `DEV_VIEWERS`) shows."""
    host = _first_level(game)
    if viewer == "ships":
        return [DevItem(ship.id, ship.name, host) for ship in game.player_ships.ships]
    if viewer == "enemies":
        return [DevItem(kind.id, kind.name, host) for kind in game.enemy_kinds]
    if viewer == "bosses":
        kinds = game.boss_kinds if game.boss_kinds is not None else []
        return [DevItem(kind.id, kind.name, host) for kind in kinds]
    if viewer == "props":
        return _props(game)
    if viewer == "levels":
        return [
            DevItem(level.id, _level_label(game, level.id), level.id) for level in game.game_levels
        ]
    raise ValueError('No dev viewer "' + viewer + '"')


def dev_catalog(game: Any) -> dict[str, list[DevItem]]:
    """The items of every dev viewer, by viewer id."""
    catalog: dict[str, list[DevItem]] = {}
    for viewer in DEV_VIEWERS:
        catalog[viewer] = dev_items(game, viewer)
    return catalog


def dev_groups(catalog: dict[str, list[DevItem]]) -> dict[str, list[str]]:
    """The group of each viewer's items ("": none; D-202)."""
    groups: dict[str, list[str]] = {}
    for viewer in DEV_VIEWERS:
        groups[viewer] = [item.group for item in catalog[viewer]]
    return groups


def dev_labels(catalog: dict[str, list[DevItem]]) -> dict[str, list[str]]:
    """The labels of each viewer's items (what the menu shows)."""
    labels: dict[str, list[str]] = {}
    for viewer in DEV_VIEWERS:
        labels[viewer] = [item.label for item in catalog[viewer]]
    return labels
