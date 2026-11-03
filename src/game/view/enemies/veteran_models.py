# Copyright (c) 2026 Renaud Guillon
"""One model per veteran model key: the Wasp, Mortar, Mantis, Phantom and Minelayer.

They are in specs/enemies/*.md, with more armour and limbs than the basic kinds (ENM-02,
GFX-ART-16).
"""

from game.view.enemies.veteran_heavy_models import build_mortar
from game.view.enemies.veteran_small_models import build_phantom, build_wasp

VETERAN_MODELS = {
    "wasp": build_wasp,
    "mortar": build_mortar,
    "phantom": build_phantom,
}
