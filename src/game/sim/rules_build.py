# Copyright (c) 2026 Renaud Guillon
"""Builds the core rules of the player's hull, bombs and bonuses, and of the boss fights.

The rules are specified in `specs/gameplay/lives-and-damage.md`, `bombs.md`, `bonuses.md` and
`level-flow.md`, and built from their config records. The config keeps camelCase keys; `core/` takes
snake_case attributes. Mapping rules are in `config_build.py`.
"""

from core.systems.bonus_world import BonusChance, BonusRules, HealRules, LifeAndBomb
from core.systems.boss_fights import BossFightRules
from core.systems.player_bombs import BombRules
from core.systems.player_hull import HullDamage, HullRules
from game.sim.config_build import opt

# isort: split
# __pragma__ ("skip")
from typing import Any

# A config record (`game/config/record.py`), typed as Any there.
ConfigRecord = Any
# __pragma__ ("noskip")


def hull_rules(config: ConfigRecord) -> HullRules:
    """Return what hurts the player, and its lives (GAME-LIFE-02, GAME-LIFE-03, GAME-LIFE-07)."""
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
    """Return the player's bombs (GAME-BOMB-01, GAME-BOMB-04)."""
    return BombRules(config.start, config.damage, config.seconds, opt(config.max))


def _life_and_bomb(pair: ConfigRecord) -> LifeAndBomb:
    return LifeAndBomb(pair.life, pair.bomb)


def bonus_rules(config: ConfigRecord) -> BonusRules:
    """Bonuses dropped by destroyed enemies (GAME-BONUS-02, GAME-BONUS-03, GAME-BONUS-11)."""
    chance = config.chance
    special = opt(config.special)
    overflow = opt(config.overflowPoints)
    heal = opt(config.heal)
    return BonusRules(
        BonusChance(chance.perHealth, chance["min"], chance["max"]),
        config.fallSpeed,
        config.pickupRadius,
        None if special is None else _life_and_bomb(special),
        None if overflow is None else _life_and_bomb(overflow),
        None if heal is None else HealRules(heal.share, heal.amount),
    )


def boss_fight_rules(config: ConfigRecord) -> BossFightRules:
    """How boss fights go: the speed ease and the health bar fill (GAME-LEVEL-07, UI-HUD-14)."""
    return BossFightRules(config.speedEaseSeconds, config.barFillSeconds)
