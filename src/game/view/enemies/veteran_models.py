"""One model per veteran model key: the Wasp, Mortar, Mantis, Phantom and Minelayer
(specs/enemies/*.md), with more armour and limbs than the basic kinds (ENM-02, GFX-ART-16)"""

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
