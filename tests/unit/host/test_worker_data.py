"""Unit tests of `src/host/worker_data.py`."""
# . `to_plain` copies the data in JavaScript (`__pragma__("js")`), which CPython does not run: the
# copy itself is not checked here (it is exercised by the browser's worker messages).

from host.worker_data import to_plain


def test_p13_r03_to_plain_is_a_callable_for_the_worker_messages() -> None:
    assert callable(to_plain)
