"""How this game's enemies (and bosses), their shots and their explosions look"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.config.readability import READABILITY  # noqa: E402
from game.view.bosses.boss_models import BOSS_MODELS  # noqa: E402
from game.view.enemies.blast_renderer import create_blast_renderer  # noqa: E402
from game.view.enemies.enemy_models import ENEMY_MODELS  # noqa: E402
from game.view.enemies.enemy_shot_renderer import create_enemy_shot_renderer  # noqa: E402
from game.view.enemies.living_motion import set_living_motion  # noqa: E402
from render.edge_trim_mesh import add_edge_trim  # noqa: E402
from render.geometry.edge_trim import TrimOptions  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402 (after the Transcrypt skip block, ENG-153)

__pragma__("noskip")


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


def trimmed(build: Any) -> Any:
    """A model factory that gives the whole model `build` makes its glowing edge trim (GFX-TRIM-06),
    so it stands out from the ground (ENM-47, GFX-READ-09): each hull asks for one in its rim
    colour, and the model's meshes hide each other's inner edges."""
    look = READABILITY.enemyTrim
    options = TrimOptions(look.width, look.offset)

    def build_trimmed(scene: Any) -> Any:
        model = build(scene)
        add_edge_trim(model.root, options)
        return model

    return build_trimmed


def merged_models() -> dict[str, object]:
    """`{ ...ENEMY_MODELS, ...BOSS_MODELS }`, each trimmed (GFX-TRIM-01): a boss model wins over
    an enemy with the same key."""
    models: dict[str, object] = {}
    for key, model in ENEMY_MODELS.items():
        models[key] = trimmed(model)
    for key, model in BOSS_MODELS.items():
        models[key] = trimmed(model)
    return models


# The models of the enemies other enemies send out (PERF-21: built with every level's own): the
# Carriers' and the bosses' Gnats, the bosses' Hornets, the Splitters' pods and the Hives' Wasps.
CHILD_MODELS = ["gnat", "hornet", "splitter-pod", "wasp"]

# How this game's enemies look. `set_living_motion` holds the living motion (ENM-42) still, a
# debug toggle.
ENEMY_BINDINGS = EnemyBindingsHandle(
    merged_models(),
    create_enemy_shot_renderer,
    create_blast_renderer,
    ENEMY_LOOK.glow,
    set_living_motion,
    CHILD_MODELS,
)
