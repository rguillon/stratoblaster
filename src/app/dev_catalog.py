"""What each dev viewer lists (D-199): the player ships, the enemy kinds, the boss kinds, the props
the levels stand on their ground, and the levels, in the game's order.
"""

from org.transcrypt.stubs.browser import __pragma__

from config.dev_viewer import DEV_VIEWERS
from render.scenery.prop_field import level_prop_kinds

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


class DevItem:
    """One item of a dev viewer: its `id` (ship, kind, prop or level id), the `label` shown, and
    the level it is shown over (`host`: a prop stands on the first level that has it)."""

    def __init__(self, id: str, label: str, host: str) -> None:
        self.id = id
        self.label = label
        self.host = host


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


def _props(game: Any) -> list[DevItem]:
    """The props of every level's ground (not their cars), each over the first level that has it,
    so it is lit and drawn as there."""
    items: list[DevItem] = []
    seen: list[str] = []
    for level in game.game_levels:
        for kind in level_prop_kinds(level.scenery):
            if kind not in seen:
                seen.append(kind)
                items.append(DevItem(kind, kind, level.id))
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


def dev_labels(catalog: dict[str, list[DevItem]]) -> dict[str, list[str]]:
    """The labels of each viewer's items (what the menu shows)."""
    labels: dict[str, list[str]] = {}
    for viewer in DEV_VIEWERS:
        labels[viewer] = [item.label for item in catalog[viewer]]
    return labels
