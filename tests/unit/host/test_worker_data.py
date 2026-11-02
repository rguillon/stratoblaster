# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/host/worker_data.py`."""
# . `to_plain` copies the data in JavaScript (`__pragma__("js")`), which CPython does not run: the
# copy itself is not checked here (it is exercised by the browser's worker messages).

from types import SimpleNamespace

import pytest

from host.worker_data import to_plain


def test_eng_164_to_plain_is_a_callable_for_the_worker_messages() -> None:
    assert callable(to_plain)


@pytest.mark.parametrize("value", [None, 3, [1, 2], {"a": 1}, SimpleNamespace(level=1)])
def test_eng_164_to_plain_is_javascript_only(value: object) -> None:
    """The copy is the `__pragma__("js")` body: CPython runs the placeholder, which is None."""
    assert to_plain(value) is None
