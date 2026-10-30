"""One model per elite model key (P05-R19 to P05-R23)"""

from game.view.enemies.elite_hive_model import build_hive  # noqa: E402
from game.view.enemies.elite_hydra_model import build_hydra  # noqa: E402
from game.view.enemies.elite_juggernaut_model import build_juggernaut  # noqa: E402
from game.view.enemies.elite_orbiter_model import build_orbiter  # noqa: E402
from game.view.enemies.elite_scissor_model import build_scissor  # noqa: E402

ELITE_MODELS = {
    "hydra": build_hydra,
    "orbiter": build_orbiter,
    "scissor": build_scissor,
    "juggernaut": build_juggernaut,
    "hive": build_hive,
}
