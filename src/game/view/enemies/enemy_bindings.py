"""How this game's enemies (and bosses, P07), their shots and their explosions look (P05)"""

from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.view.bosses.boss_models import BOSS_MODELS  # noqa: E402
from game.view.enemies.blast_renderer import create_blast_renderer  # noqa: E402
from game.view.enemies.enemy_models import ENEMY_MODELS  # noqa: E402
from game.view.enemies.enemy_shot_renderer import create_enemy_shot_renderer  # noqa: E402
from game.view.enemies.living_motion import set_living_motion  # noqa: E402


class EnemyBindingsHandle:
    """The enemy bindings."""

    def __init__(
        self,
        models: dict[str, object],
        shots: object,
        blasts: object,
        glow: object,
        set_idle: object,
        child_models: list[str],
    ):
        self.models = models
        self.child_models = child_models
        self.shots = shots
        self.blasts = blasts
        self.glow = glow
        self.setIdleMotion = set_idle


def merged_models() -> dict[str, object]:
    """`{ ...ENEMY_MODELS, ...BOSS_MODELS }`: a boss model wins over an enemy with the same key."""
    models: dict[str, object] = {}
    for key, model in ENEMY_MODELS.items():
        models[key] = model
    for key, model in BOSS_MODELS.items():
        models[key] = model
    return models


# The models of the enemies other enemies send out (P13-R03: built with every level's own): the
# Carriers' and the bosses' Gnats, the bosses' Hornets, the Splitters' pods and the Hives' Wasps.
CHILD_MODELS = ["gnat", "hornet", "splitter-pod", "wasp"]

# How this game's enemies look (P05). P16-R10: the debug pages pause the living motion (P16-R07).
ENEMY_BINDINGS = EnemyBindingsHandle(
    merged_models(),
    create_enemy_shot_renderer,
    create_blast_renderer,
    ENEMY_LOOK.glow,
    set_living_motion,
    CHILD_MODELS,
)
