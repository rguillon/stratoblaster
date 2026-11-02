# Copyright (c) 2026 Renaud Guillon
"""What each dev viewer lists (D-199): the player ships, the enemy kinds, the boss kinds.

The props the levels stand on their ground and their cars (D-209), and the levels, in the game's
order. The props are gathered by the game's prop groups (D-202), as the Dev menu's props viewer
shows them. The sounds (one per cue, DEV-MENU-19) and the music (every track the game plays, each
once, DEV-MENU-20): a music item's id names its request (`menu`, `level:1-1`, `boss:1-1`,
`jingle:complete`), and `music_request` reads it back.
"""

from audio.audio_bindings import MusicRequest
from config.dev_viewer import DEV_VIEWERS
from render.scenery.prop_field import level_prop_kinds

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# The group of the props in none of the game's prop groups (D-202).
OTHER_GROUP = "Other"

# The music viewer's groups, by the kind of request (DEV-MENU-20).
MUSIC_GROUPS = {"menu": "Menu", "level": "Levels", "boss": "Bosses", "jingle": "Jingles"}
# The jingles a game may play (`audio_bindings.Jingle`), in the viewer's order.
JINGLES = ["complete", "over", "checkpoint"]


class DevItem:
    """One item of a dev viewer: its `id` (ship, kind, prop or level id), the `label` shown.

    The level it is shown over (`host`: a prop stands on the first level that has it), the `group`
    it is listed in ("": none; D-202), and the `scale` a prop is drawn at (D-209: the cars').
    """

    def __init__(self, id_: str, label: str, host: str, group: str = "", scale: float = 1) -> None:
        self.id = id_
        self.label = label
        self.host = host
        self.group = group
        self.scale = scale


def _first_level(game: Any) -> str:
    levels = game.game_levels
    if len(levels) == 0:
        msg = "The game has no level"
        raise ValueError(msg)
    first: str = levels[0].id
    return first


def _level_label(game: Any, level_id: str) -> str:
    for entry in game.levels.levels:
        if entry.id == level_id:
            label: str = entry.label
            return label
    return level_id


def _prop_groups(game: Any) -> list[Any]:
    """Return the game's prop groups (`PropGroup`s), none when its view names none."""
    scenery = game.view.scenery
    if "propGroups" not in scenery or scenery["propGroups"] is None:
        return []
    groups: list[Any] = scenery["propGroups"]
    return groups


def car_kinds(scenery: Any) -> list[str]:
    """Return the kinds of car driving on the roads of the scenery level `scenery` (D-209)."""
    cars = scenery.props.cars
    if cars is None:
        return []
    kinds: list[str] = list(cars.kinds)
    return kinds


def car_scale(scenery: Any) -> float:
    """Return the scale the cars of the scenery level `scenery` are drawn at (D-209)."""
    scale: float = scenery.props.cars.scale
    return scale


def _props(game: Any) -> list[DevItem]:
    """Return the props of every level's ground and its cars (D-209).

    Each over the first level that has it, so it has its world's tone; gathered by the game's prop
    groups, in their order, then the props in none of them (D-202).
    """
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
    items.extend([
        DevItem(kind, kind, hosts[kind], OTHER_GROUP, scales[kind])
        for kind in kinds
        if kind not in listed
    ])
    return items


def _sounds(game: Any) -> list[DevItem]:
    """Return the game's sound effects (DEV-MENU-19): one item per cue, in the game's order."""
    bindings = game.view.audio
    if bindings is None:
        return []
    host = _first_level(game)
    return [DevItem(cue, cue, host) for cue in bindings.sounds.keys()]


def music_item_id(request: MusicRequest) -> str:
    """Return the id of the music item of `request`: its kind, then its level or jingle."""
    if request.kind == "menu":
        return "menu"
    if request.kind == "jingle":
        return "jingle:" + (request.jingle or "")
    return request.kind + ":" + (request.level_id or "")


def music_request(item_id: str) -> MusicRequest:
    """Return the music request a music item's id names (see `music_item_id`)."""
    parts = item_id.split(":")
    kind = parts[0]
    argument = parts[1] if len(parts) > 1 else None
    if kind == "jingle":
        return MusicRequest(kind, None, argument)
    return MusicRequest(kind, argument, None)


def _music_requests(game: Any) -> list[MusicRequest]:
    """Every music the engine may ask the game for: the menu's, each level's and its boss's.

    Then the jingles.
    """
    requests = [MusicRequest("menu", None, None)]
    requests.extend([MusicRequest("level", level.id, None) for level in game.game_levels])
    requests.extend([MusicRequest("boss", level.id, None) for level in game.game_levels])
    requests.extend([MusicRequest("jingle", None, jingle) for jingle in JINGLES])
    return requests


def _music(game: Any) -> list[DevItem]:
    """Return the tracks the game plays (DEV-MENU-20), each once, labelled by its id.

    Several levels share a boss track: the first level's request lists it. A request the game has
    no track for is left out.
    """
    bindings = game.view.audio
    if bindings is None:
        return []
    host = _first_level(game)
    items: list[DevItem] = []
    listed: list[str] = []
    for request in _music_requests(game):
        track = bindings.music(request)
        if track is None or track.id in listed:
            continue
        listed.append(track.id)
        items.append(DevItem(music_item_id(request), track.id, host, MUSIC_GROUPS[request.kind]))
    return items


def _simple_items(game: Any, viewer: str) -> list[DevItem] | None:
    """Return the items of a viewer listed straight from the game's data, or None for the others."""
    host = _first_level(game)
    if viewer == "ships":
        return [DevItem(ship.id, ship.name, host) for ship in game.player_ships.ships]
    if viewer == "enemies":
        return [DevItem(kind.id, kind.name, host) for kind in game.enemy_kinds]
    if viewer == "bosses":
        kinds = game.boss_kinds if game.boss_kinds is not None else []
        return [DevItem(kind.id, kind.name, host) for kind in kinds]
    if viewer == "levels":
        return [
            DevItem(level.id, _level_label(game, level.id), level.id) for level in game.game_levels
        ]
    return None


def dev_items(game: Any, viewer: str) -> list[DevItem]:
    """Return the items the dev viewer `viewer` (one of `DEV_VIEWERS`) shows.

    The ships (DEV-MENU-12), the enemy kinds (DEV-MENU-13), the boss kinds (DEV-MENU-14), the props
    of the levels' ground (DEV-MENU-15), the levels (DEV-MENU-18), the sounds (DEV-MENU-19) and the
    music (DEV-MENU-20).
    """
    items = _simple_items(game, viewer)
    if items is not None:
        return items
    if viewer == "props":
        return _props(game)
    if viewer == "sounds":
        return _sounds(game)
    if viewer == "music":
        return _music(game)
    raise ValueError('No dev viewer "' + viewer + '"')


def dev_catalog(game: Any) -> dict[str, list[DevItem]]:
    """Return the items of every dev viewer, by viewer id."""
    catalog: dict[str, list[DevItem]] = {}
    for viewer in DEV_VIEWERS:
        catalog[viewer] = dev_items(game, viewer)
    return catalog


def dev_groups(catalog: dict[str, list[DevItem]]) -> dict[str, list[str]]:
    """Return the group of each viewer's items ("": none; D-202)."""
    groups: dict[str, list[str]] = {}
    for viewer in DEV_VIEWERS:
        groups[viewer] = [item.group for item in catalog[viewer]]
    return groups


def dev_labels(catalog: dict[str, list[DevItem]]) -> dict[str, list[str]]:
    """Return the labels of each viewer's items (what the menu shows)."""
    labels: dict[str, list[str]] = {}
    for viewer in DEV_VIEWERS:
        labels[viewer] = [item.label for item in catalog[viewer]]
    return labels
