# Copyright (c) 2026 Renaud Guillon
"""One model per enemy model key (`EnemyStats.model`): the kinds of specs/enemies/*.md.

Each is generated in code (ENM-34, GFX-ART-01).
"""

from game.view.enemies.carrier_model import build_carrier
from game.view.enemies.elite_models import ELITE_MODELS
from game.view.enemies.heavy_beetle_models import (
    build_bulwark,
    build_splitter,
    build_splitter_pod,
)
from game.view.enemies.heavy_enemy_models import (
    build_lancer,
    build_rocketeer,
    build_spinner,
)
from game.view.enemies.small_enemy_models import (
    build_gnat,
    build_hornet,
    build_scout,
    build_strafer,
    build_weaver,
)
from game.view.enemies.veteran_models import VETERAN_MODELS

ENEMY_MODELS = {
    "gnat": build_gnat,
    "hornet": build_hornet,
    "scout": build_scout,
    "strafer": build_strafer,
    "weaver": build_weaver,
    "spinner": build_spinner,
    "lancer": build_lancer,
    "rocketeer": build_rocketeer,
    "bulwark": build_bulwark,
    "splitter": build_splitter,
    "splitter-pod": build_splitter_pod,
    "carrier": build_carrier,
}
# `...VETERAN_MODELS, ...ELITE_MODELS`: the veteran and elite models follow.
ENEMY_MODELS.update(VETERAN_MODELS)
ENEMY_MODELS.update(ELITE_MODELS)
