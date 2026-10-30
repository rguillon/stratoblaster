"""Shared set-up of the e2e tests (ENG-50 to ENG-53): Playwright (Python, Chromium) on the e2e
build in `dist-e2e/` (`make e2e-build`), served on a free local port for the whole session.

- `base_url`: the server's address; `page.goto("./")` opens the game;
- the Transcrypt browser stubs are on the path, so a test can read the game's config (`src/`);
- every test fails on a browser console error or an uncaught exception (ENG-53), and on any
  warning from the audio (an autoplay warning, a context that could not start, P12-R05).
"""

import sys
import threading
from collections.abc import Iterator
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import pytest
import transcrypt
from playwright.sync_api import ConsoleMessage, Error, Page

_STUBS = Path(next(iter(transcrypt.__path__))).resolve() / "modules"
if str(_STUBS) not in sys.path:
    sys.path.append(str(_STUBS))

DIST = Path(__file__).resolve().parents[2] / "dist-e2e"
AUDIO_WARNING = ("audio", "autoplay")


class QuietHandler(SimpleHTTPRequestHandler):
    """Serves `dist-e2e/` without logging every request."""

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        pass


@pytest.fixture(scope="session")
def base_url() -> Iterator[str]:
    if not (DIST / "index.html").is_file():
        pytest.exit("dist-e2e/ is missing: run `make e2e-build` (or `make e2e`)", returncode=1)
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(DIST)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}/"
    server.shutdown()
    server.server_close()


@pytest.fixture(autouse=True)
def console_errors(page: Page) -> Iterator[list[str]]:
    """ENG-53: the console errors and uncaught exceptions of the test; it fails on any."""
    errors: list[str] = []

    def on_console(message: ConsoleMessage) -> None:
        text = message.text
        audio = message.type == "warning" and any(w in text.lower() for w in AUDIO_WARNING)
        if message.type == "error" or audio:
            errors.append(text)

    def on_page_error(error: Error) -> None:
        errors.append(error.message)

    page.on("console", on_console)
    page.on("pageerror", on_page_error)
    yield errors
    assert errors == [], "browser console errors"
