"""The first enemy kinds (P05-R01 to P05-R12), and every enemy kind of the game, ported from
`game/sim/enemy-kinds.ts`.
"""

from org.transcrypt.stubs.browser import __pragma__

from core.entities.enemy import EnemyKindDefinition
from core.math.rng import random_in
from game.config.enemies import ENEMY_CONFIG as C
from game.config.enemies import ENEMY_SPAWN_MARGIN as MARGIN
from game.sim.elite_kinds import ELITE_KINDS
from game.sim.enemies.bulwark import Bulwark
from game.sim.enemies.carrier import Carrier
from game.sim.enemies.enemy_helpers import (
    clamp_entry,
    coin,
    pick_x,
    playfield_path,
    top_x,
)
from game.sim.enemies.gnat import Gnat
from game.sim.enemies.hornet import Hornet, hornet_options
from game.sim.enemies.lancer import Lancer
from game.sim.enemies.rocketeer import Rocketeer
from game.sim.enemies.scout import Scout
from game.sim.enemies.spinner import Spinner
from game.sim.enemies.splitter import Splitter
from game.sim.enemies.strafer import Strafer
from game.sim.enemies.weaver import Weaver
from game.sim.veteran_kinds import VETERAN_KINDS

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from core.entities.enemy import Enemy, EnemySpawnArea  # noqa: E402

__pragma__("noskip")


def _top(area: EnemySpawnArea) -> float:
    """Just above the top edge."""
    return area.height + MARGIN


def _coin(area: EnemySpawnArea) -> bool:
    return coin(area.random)


def _entry_x(area: EnemySpawnArea, range_: tuple[float, float]) -> float:
    """X where a kind comes in from the top: the wave's entry (P06-R07), or random in `range_`,
    both taken across the area's `top_range` (phase 6 review).
    """
    entry = area.entry
    if entry is not None and entry.side == "top":
        return top_x(area, clamp_entry(entry.position))
    return pick_x(area.random, range_, area)


def _mirror_for(area: EnemySpawnArea, start_x: float) -> bool:
    """Whether to mirror a path that starts at `start_x` (a fraction of the width): towards the
    wave's entry when it has one, at random otherwise.
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
    """A side pass comes from the entry's side, at its height; at random otherwise. Returns
    whether it comes from the left, and its height.
    """
    entry = area.entry
    if entry is not None and entry.side != "top":
        return (entry.side == "left", clamp_entry(entry.position) * area.height)
    return (_coin(area), height_fraction * area.height)


def _spawn_gnat(area: EnemySpawnArea) -> list[Enemy]:
    path = playfield_path(C.gnat.path, area, _mirror_for(area, C.gnat.path[0][0]))
    return [Gnat(path, i * C.gnat.groupDelay) for i in range(C.gnat.groupSize)]


def _spawn_hornet(area: EnemySpawnArea) -> list[Enemy]:
    x = _entry_x(area, C.hornet.xRange)
    return [Hornet(x, _top(area), hornet_options(C.hornet, C.hornet.stopFraction * area.height))]


def _spawn_scout(area: EnemySpawnArea) -> list[Enemy]:
    return [Scout(_entry_x(area, C.scout.xRange), _top(area))]


def _spawn_strafer(area: EnemySpawnArea) -> list[Enemy]:
    left, y = side_pass(area, C.strafer.heightFraction)
    x = -MARGIN if left else area.width + MARGIN
    return [Strafer(x, y, "left" if left else "right")]


def _spawn_weaver(area: EnemySpawnArea) -> list[Enemy]:
    return [Weaver(_entry_x(area, C.weaver.xRange), _top(area))]


def _spawn_spinner(area: EnemySpawnArea) -> list[Enemy]:
    stop_y = random_in(area.random, C.spinner.stopRange[0], C.spinner.stopRange[1]) * area.height
    return [Spinner(_entry_x(area, C.spinner.xRange), _top(area), stop_y)]


def _spawn_lancer(area: EnemySpawnArea) -> list[Enemy]:
    x = _entry_x(area, C.lancer.xRange)
    return [Lancer(x, _top(area), C.lancer.stopFraction * area.height)]


def _spawn_rocketeer(area: EnemySpawnArea) -> list[Enemy]:
    return [Rocketeer(_entry_x(area, C.rocketeer.xRange), _top(area))]


def _spawn_bulwark(area: EnemySpawnArea) -> list[Enemy]:
    x = _entry_x(area, C.bulwark.xRange)
    return [Bulwark(x, _top(area), C.bulwark.stopFraction * area.height)]


def _spawn_splitter(area: EnemySpawnArea) -> list[Enemy]:
    mirror = _mirror_for(area, C.splitter.path[0][0])
    return [Splitter(playfield_path(C.splitter.path, area, mirror))]


def _spawn_carrier(area: EnemySpawnArea) -> list[Enemy]:
    return [Carrier(_entry_x(area, C.carrier.xRange), _top(area))]


def _first_kinds() -> list[EnemyKindDefinition]:
    """The 11 first enemy kinds of P05 (P05-R01 to P05-R12), in the order of the spec."""
    return [
        EnemyKindDefinition("gnat", "Gnat", _spawn_gnat),
        EnemyKindDefinition("hornet", "Hornet", _spawn_hornet),
        EnemyKindDefinition("scout", "Scout", _spawn_scout),
        EnemyKindDefinition("strafer", "Strafer", _spawn_strafer),
        EnemyKindDefinition("weaver", "Weaver", _spawn_weaver),
        EnemyKindDefinition("spinner", "Spinner", _spawn_spinner),
        EnemyKindDefinition("lancer", "Lancer", _spawn_lancer),
        EnemyKindDefinition("rocketeer", "Rocketeer", _spawn_rocketeer),
        EnemyKindDefinition("bulwark", "Bulwark", _spawn_bulwark),
        EnemyKindDefinition("splitter", "Splitter", _spawn_splitter),
        EnemyKindDefinition("carrier", "Carrier", _spawn_carrier),
    ]


FIRST_KINDS = _first_kinds()


def _all_kinds() -> list[EnemyKindDefinition]:
    """Every enemy kind of P05: the first eleven, then the veteran and elite kinds (P05-R24)."""
    kinds: list[EnemyKindDefinition] = []
    kinds.extend(FIRST_KINDS)
    kinds.extend(VETERAN_KINDS)
    kinds.extend(ELITE_KINDS)
    return kinds


ENEMY_KINDS = _all_kinds()
