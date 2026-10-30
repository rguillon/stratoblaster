"""Shared set-up of the Python unit tests (ENG-40): CPython runs the modules of `src/`, which import
Transcrypt's browser stubs (`org.transcrypt.stubs.browser`). The stubs' folder comes last on the
path, so the standard library (`re`, `copy`, ...) is still found first."""

import sys
from pathlib import Path

import transcrypt

_STUBS = Path(next(iter(transcrypt.__path__))).resolve() / "modules"
if str(_STUBS) not in sys.path:
    sys.path.append(str(_STUBS))
