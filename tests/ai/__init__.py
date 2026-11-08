# Copyright (c) 2026 Renaud Guillon
"""The AI player: a neural network that learns to play the game, then rates its levels.

Pure Python: it runs the game's own simulation (`src/core/`, `src/game/sim/`) with no browser and
no JavaScript. The workers that play the games run under PyPy, whose JIT plays them about five
times faster than CPython (D-301); the brain learns and decides under CPython, with PyTorch.
`make learn` trains the brain, `make rate` rates the difficulty of each level with it. The brain
is saved under `data/` at the repo root.

Importing this package puts `src/` and Transcrypt's browser stubs (`org`) on the path, as the unit
tests' conftest does, so the game's modules import as they do under pytest. Under PyPy, where
Transcrypt is not installed, the stubs are where `TRANSCRYPT_STUBS` says (the learner sets it).
"""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
DATA = REPO_ROOT / "data"
STUBS_VARIABLE = "TRANSCRYPT_STUBS"


def transcrypt_stubs() -> str:
    """Return the folder of Transcrypt's modules (`org.transcrypt.stubs`), '' when unknown."""
    try:
        import transcrypt  # noqa: PLC0415  # not installed under PyPy
    except ImportError:
        return os.environ.get(STUBS_VARIABLE, "")
    return str(Path(next(iter(transcrypt.__path__))).resolve() / "modules")


if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
_STUBS = transcrypt_stubs()
if _STUBS and _STUBS not in sys.path:
    sys.path.append(_STUBS)
