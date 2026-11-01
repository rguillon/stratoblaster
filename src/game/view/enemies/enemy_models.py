"""One model per enemy model key (`EnemyStats.model`): the kinds of specs/enemies/*.md, each
generated in code (ENM-34, GFX-ART-01)"""

from game.view.enemies.carrier_model import build_carrier  # noqa: E402
from game.view.enemies.elite_models import ELITE_MODELS  # noqa: E402
from game.view.enemies.heavy_beetle_models import (  # noqa: E402
    build_bulwark,
    build_splitter,
    build_splitter_pod,
)
from game.view.enemies.heavy_enemy_models import (  # noqa: E402
    build_lancer,
    build_rocketeer,
    build_spinner,
)
from game.view.enemies.small_enemy_models import (  # noqa: E402
    build_gnat,
    build_hornet,
    build_scout,
    build_strafer,
    build_weaver,
)
from game.view.enemies.veteran_models import VETERAN_MODELS  # noqa: E402

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
for _key, _model in VETERAN_MODELS.items():
    ENEMY_MODELS[_key] = _model
for _key, _model in ELITE_MODELS.items():
    ENEMY_MODELS[_key] = _model
