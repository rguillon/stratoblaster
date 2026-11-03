# Copyright (c) 2026 Renaud Guillon
"""One model per enemy model key (`EnemyStats.model`): the kinds of specs/enemies/*.md.

Each is generated in code (ENM-34, GFX-ART-01).
"""

from game.view.enemies.carrier_model import build_carrier
from game.view.enemies.elite_models import ELITE_MODELS
from game.view.enemies.heavy_beetle_models import (
    build_splitter,
    build_splitter_pod,
)
from game.view.enemies.heavy_enemy_models import (
    build_lancer,
    build_rocketeer,
    build_spinner,
)
from game.view.enemies.small_enemy_models import (
    build_hornet,
    build_scout,
    build_strafer,
)
from game.view.enemies.tier2_harrier_model import build_harrier
from game.view.enemies.tier2_hatchery_model import build_hatchery
from game.view.enemies.tier2_sweeper_model import build_sweeper
from game.view.enemies.veteran_models import VETERAN_MODELS

ENEMY_MODELS = {
    "hornet": build_hornet,
    "scout": build_scout,
    "strafer": build_strafer,
    "spinner": build_spinner,
    "lancer": build_lancer,
    "rocketeer": build_rocketeer,
    "splitter": build_splitter,
    "splitter-pod": build_splitter_pod,
    "carrier": build_carrier,
    "harrier": build_harrier,
    "sweeper": build_sweeper,
    "hatchery": build_hatchery,
}
# `...VETERAN_MODELS, ...ELITE_MODELS`: the veteran and elite models follow.
ENEMY_MODELS.update(VETERAN_MODELS)
ENEMY_MODELS.update(ELITE_MODELS)
