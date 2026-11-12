# Copyright (c) 2026 Renaud Guillon
"""Shared set-up of the Python unit tests (ENG-40).

CPython runs the modules of `src/` (ENG-160), which import Transcrypt's browser stubs
(`org.transcrypt.stubs.browser`). The stubs' folder comes last on the path, so the standard library
(`re`, `copy`, ...) is still found first.
"""

import sys
from pathlib import Path

import pytest
import transcrypt

_STUBS = Path(next(iter(transcrypt.__path__))).resolve() / "modules"
if str(_STUBS) not in sys.path:
    sys.path.append(str(_STUBS))

# After the stubs' folder joins the path: the render modules import them.
from helpers.render_fakes import FakeWeakMap  # noqa: E402

from render import model_animation  # noqa: E402


@pytest.fixture(autouse=True)
def _model_inputs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Give each test a fresh WeakMap of model inputs: `INPUTS` is made without Babylon."""
    monkeypatch.setattr(model_animation, "INPUTS", FakeWeakMap())
