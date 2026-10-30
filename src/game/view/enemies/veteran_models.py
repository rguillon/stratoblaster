"""One model per veteran model key (P05-R14 to P05-R18)"""

from game.view.enemies.veteran_heavy_models import build_minelayer, build_mortar  # noqa: E402
from game.view.enemies.veteran_mantis_model import build_mantis  # noqa: E402
from game.view.enemies.veteran_small_models import build_phantom, build_wasp  # noqa: E402

VETERAN_MODELS = {
    "wasp": build_wasp,
    "mortar": build_mortar,
    "mantis": build_mantis,
    "phantom": build_phantom,
    "minelayer": build_minelayer,
}
