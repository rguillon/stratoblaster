# Copyright (c) 2026 Renaud Guillon
"""The AI player: a neural network that learns to play the game, then rates its levels.

Pure Python: it runs the game's own simulation (`src/core/`, `src/game/sim/`) in CPython, as fast
as the CPU goes, with no browser and no JavaScript. `make learn` trains the brain, `make rate`
rates the difficulty of each level with it. The brain is saved under `data/` at the repo root.

Importing this package puts `src/` and Transcrypt's browser stubs (`org`) on the path, as the unit
tests' conftest does, so the game's modules import as they do under pytest.
"""

import sys
from pathlib import Path

import transcrypt

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
DATA = REPO_ROOT / "data"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
_STUBS = Path(next(iter(transcrypt.__path__))).resolve() / "modules"
if str(_STUBS) not in sys.path:
    sys.path.append(str(_STUBS))
