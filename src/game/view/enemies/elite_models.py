# Copyright (c) 2026 Renaud Guillon
"""One model per elite model key: the Hydra, Orbiter, Scissor, Juggernaut and Hive.

They are more armoured and complex than the veterans (specs/enemies/*.md, ENM-02, GFX-ART-16).
"""

from game.view.enemies.elite_hive_model import build_hive
from game.view.enemies.elite_hydra_model import build_hydra
from game.view.enemies.elite_juggernaut_model import build_juggernaut
from game.view.enemies.elite_orbiter_model import build_orbiter
from game.view.enemies.elite_scissor_model import build_scissor

ELITE_MODELS = {
    "hydra": build_hydra,
    "orbiter": build_orbiter,
    "scissor": build_scissor,
    "juggernaut": build_juggernaut,
    "hive": build_hive,
}
