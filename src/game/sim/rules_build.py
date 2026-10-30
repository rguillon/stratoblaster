"""Builds the core rules of the player's hull, bombs and bonuses, and of the boss fights (GD-20,
GD-32, P07, P11) from their config records. The config keeps the TypeScript's camelCase shape;
`core/` takes snake_case attributes. Mapping rules are in `config_build.py`.
"""

from org.transcrypt.stubs.browser import __pragma__

from core.systems.bonus_world import BonusChance, BonusRules, LifeAndBomb
from core.systems.boss_fights import BossFightRules
from core.systems.player_bombs import BombRules
from core.systems.player_hull import HullDamage, HullRules
from game.sim.config_build import opt

__pragma__("skip")
from typing import Any  # noqa: E402

# A config record (`game/config/record.py`), typed as Any there.
ConfigRecord = Any
__pragma__("noskip")


def hull_rules(config: ConfigRecord) -> HullRules:
    """What hurts the player, and its lives (GD-20..GD-22)."""
    damage = config.damage
    return HullRules(
        config.lives,
        config.invincibleSeconds,
        config.hitRadius,
        HullDamage(damage.bullet, damage.missile, damage.laser, damage.collision),
        config.ramDamage,
        opt(config.maxLives),
    )


def bomb_rules(config: ConfigRecord) -> BombRules:
    """The player's bombs (GD-32, P11-R05)."""
    return BombRules(config.start, config.damage, config.seconds, opt(config.max))


def _life_and_bomb(pair: ConfigRecord) -> LifeAndBomb:
    return LifeAndBomb(pair.life, pair.bomb)


def bonus_rules(config: ConfigRecord) -> BonusRules:
    """Bonuses dropped by destroyed enemies (GD-31, P11-R07)."""
    chance = config.chance
    special = opt(config.special)
    overflow = opt(config.overflowPoints)
    return BonusRules(
        BonusChance(chance.perHealth, chance["min"], chance["max"]),
        config.fallSpeed,
        config.pickupRadius,
        None if special is None else _life_and_bomb(special),
        None if overflow is None else _life_and_bomb(overflow),
    )


def boss_fight_rules(config: ConfigRecord) -> BossFightRules:
    """How boss fights go: the speed ease and the health bar fill (P07-R02, R03)."""
    return BossFightRules(config.speedEaseSeconds, config.barFillSeconds)
