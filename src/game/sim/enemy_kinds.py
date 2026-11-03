# Copyright (c) 2026 Renaud Guillon
"""The basic enemy kinds, and every enemy kind of the game (ENM-01).

The kinds live in the game, the engine knows enemies only as abstractions (ENM-04); none of their
gameplay depends on their look (ENM-46).
"""

from core.entities.enemy import EnemyKindDefinition
from core.math.rng import random_in
from game.config.enemies import ENEMY_CONFIG as C
from game.config.enemies import ENEMY_SPAWN_MARGIN as MARGIN
from game.config.enemy_broodmother import BROODMOTHER_CONFIG
from game.config.enemy_harrier import HARRIER_CONFIG
from game.config.enemy_hatchery import HATCHERY_CONFIG
from game.config.enemy_prism import PRISM_CONFIG
from game.config.enemy_sweeper import SWEEPER_CONFIG
from game.config.enemy_tiers import all_kinds, tier_of
from game.sim.elite_kinds import ELITE_KINDS
from game.sim.enemies.broodmother import Broodmother
from game.sim.enemies.carrier import Carrier
from game.sim.enemies.enemy_helpers import (
    clamp_entry,
    coin,
    pick_x,
    top_x,
)
from game.sim.enemies.harrier import Harrier
from game.sim.enemies.hatchery import Hatchery
from game.sim.enemies.hornet import Hornet, hornet_options
from game.sim.enemies.lancer import Lancer
from game.sim.enemies.prism import Prism
from game.sim.enemies.rocketeer import Rocketeer
from game.sim.enemies.scout import Scout
from game.sim.enemies.spinner import Spinner
from game.sim.enemies.splitter import Splitter
from game.sim.enemies.strafer import Strafer
from game.sim.enemies.sweeper import Sweeper
from game.sim.veteran_kinds import VETERAN_KINDS

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from core.entities.enemy import Enemy, EnemySpawnArea

# __pragma__ ("noskip")


def _top(area: EnemySpawnArea) -> float:
    """Just above the top edge, where a kind's group comes in (ENM-07)."""
    return area.height + MARGIN


def _coin(area: EnemySpawnArea) -> bool:
    return coin(area.random)


def _entry_x(area: EnemySpawnArea, range_: tuple[float, float]) -> float:
    """X where a kind comes in from the top: the wave's entry (ENM-08), or random in `range_`.

    Both taken across the area's `top_range` (phase 6 review).
    """
    entry = area.entry
    if entry is not None and entry.side == "top":
        return top_x(area, clamp_entry(entry.position))
    return pick_x(area.random, range_, area)


def _mirror_for(area: EnemySpawnArea, start_x: float) -> bool:
    """Whether to mirror a path that starts at `start_x` (a fraction of the width).

    Towards the wave's entry when it has one, at random otherwise.
    """
    entry = area.entry
    if entry is None:
        return _coin(area)
    if entry.side == "left":
        at = 0.0
    elif entry.side == "right":
        at = 1.0
    else:
        at = entry.position
    return abs(1 - start_x - at) < abs(start_x - at)


def side_pass(area: EnemySpawnArea, height_fraction: float) -> tuple[bool, float]:
    """Return a side pass comes from the entry's side, at its height; at random otherwise.

    Returns whether it comes from the left, and its height.
    """
    entry = area.entry
    if entry is not None and entry.side != "top":
        return (entry.side == "left", clamp_entry(entry.position) * area.height)
    return (_coin(area), height_fraction * area.height)


def _spawn_hornet(area: EnemySpawnArea) -> list[Enemy]:
    x = _entry_x(area, C.hornet.xRange)
    return [Hornet(x, _top(area), hornet_options(C.hornet, C.hornet.stopFraction * area.height))]


def _spawn_scout(area: EnemySpawnArea) -> list[Enemy]:
    return [Scout(_entry_x(area, C.scout.xRange), _top(area))]


def _spawn_strafer(area: EnemySpawnArea) -> list[Enemy]:
    left, y = side_pass(area, C.strafer.heightFraction)
    x = -MARGIN if left else area.width + MARGIN
    return [Strafer(x, y, "left" if left else "right")]


def _spawn_spinner(area: EnemySpawnArea) -> list[Enemy]:
    stop_y = random_in(area.random, C.spinner.stopRange[0], C.spinner.stopRange[1]) * area.height
    return [Spinner(_entry_x(area, C.spinner.xRange), _top(area), stop_y)]


def _spawn_lancer(area: EnemySpawnArea) -> list[Enemy]:
    x = _entry_x(area, C.lancer.xRange)
    return [Lancer(x, _top(area), C.lancer.stopFraction * area.height)]


def _spawn_rocketeer(area: EnemySpawnArea) -> list[Enemy]:
    return [Rocketeer(_entry_x(area, C.rocketeer.xRange), _top(area))]


def _spawn_splitter(area: EnemySpawnArea) -> list[Enemy]:
    x = _entry_x(area, C.splitter.xRange)
    return [Splitter(x, _top(area), C.splitter.stopFraction * area.height)]


def _spawn_carrier(area: EnemySpawnArea) -> list[Enemy]:
    return [Carrier(_entry_x(area, C.carrier.xRange), _top(area))]


def _spawn_harrier(area: EnemySpawnArea) -> list[Enemy]:
    x = _entry_x(area, HARRIER_CONFIG.xRange)
    return [Harrier(x, _top(area), HARRIER_CONFIG.stopFraction * area.height)]


def _spawn_sweeper(area: EnemySpawnArea) -> list[Enemy]:
    x = _entry_x(area, SWEEPER_CONFIG.xRange)
    return [Sweeper(x, _top(area), SWEEPER_CONFIG.stopFraction * area.height)]


def _spawn_hatchery(area: EnemySpawnArea) -> list[Enemy]:
    return [Hatchery(_entry_x(area, HATCHERY_CONFIG.xRange), _top(area))]


def _spawn_prism(area: EnemySpawnArea) -> list[Enemy]:
    x = _entry_x(area, PRISM_CONFIG.xRange)
    return [Prism(x, _top(area), PRISM_CONFIG.stopFraction * area.height)]


def _spawn_broodmother(area: EnemySpawnArea) -> list[Enemy]:
    return [Broodmother(_entry_x(area, BROODMOTHER_CONFIG.xRange), _top(area))]


def _first_kinds() -> list[EnemyKindDefinition]:
    """Return the basic kinds still kept as they were (ENM-01)."""
    return [
        EnemyKindDefinition("hornet", "Hornet", _spawn_hornet),
        EnemyKindDefinition("scout", "Scout", _spawn_scout),
        EnemyKindDefinition("strafer", "Strafer", _spawn_strafer),
        EnemyKindDefinition("spinner", "Spinner", _spawn_spinner),
        EnemyKindDefinition("lancer", "Lancer", _spawn_lancer),
        EnemyKindDefinition("rocketeer", "Rocketeer", _spawn_rocketeer),
        EnemyKindDefinition("splitter", "Splitter", _spawn_splitter),
        EnemyKindDefinition("carrier", "Carrier", _spawn_carrier),
        EnemyKindDefinition("harrier", "Harrier", _spawn_harrier),
        EnemyKindDefinition("sweeper", "Sweeper", _spawn_sweeper),
        EnemyKindDefinition("hatchery", "Hatchery", _spawn_hatchery),
        EnemyKindDefinition("prism", "Prism", _spawn_prism),
        EnemyKindDefinition("broodmother", "Broodmother", _spawn_broodmother),
    ]


FIRST_KINDS = _first_kinds()


def _all_kinds() -> list[EnemyKindDefinition]:
    """Every enemy kind of the game, tier 1 first, each tier in the order of its roles (ENM-01)."""
    by_id: dict[str, EnemyKindDefinition] = {}
    for group in [FIRST_KINDS, VETERAN_KINDS, ELITE_KINDS]:
        for kind in group:
            by_id[kind.id] = kind
    ordered = [by_id[kind_id] for kind_id in all_kinds() if kind_id in by_id]
    for kind in ordered:
        # ENM-02: the dev viewer lists the kinds tier by tier.
        kind.group = "Tier " + str(tier_of(kind.id))
    return ordered


ENEMY_KINDS = _all_kinds()
