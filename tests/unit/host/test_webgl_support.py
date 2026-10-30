"""Unit tests of `src/host/webgl_support.py`."""

from unittest.mock import MagicMock

from host.webgl_support import has_webgl2


def test_eng06_webgl2_context_present_means_supported() -> None:
    canvas = MagicMock()
    canvas.getContext.return_value = object()
    assert has_webgl2(lambda: canvas) is True
    canvas.getContext.assert_called_once_with("webgl2")


def test_eng06_no_webgl2_context_means_unsupported() -> None:
    canvas = MagicMock()
    canvas.getContext.return_value = None
    assert has_webgl2(lambda: canvas) is False


def test_eng06_a_failure_while_creating_the_canvas_means_unsupported() -> None:
    def fail() -> object:
        raise RuntimeError("no canvas")

    assert has_webgl2(fail) is False  # type: ignore[arg-type]
