"""Unit tests of `src/ui/screens/loading_screen.py`."""

import pytest
from helpers.dom import FakeDocument

from ui.menu_view import LoadingView
from ui.screens.loading_screen import render_loading_screen


@pytest.mark.parametrize(
    ("progress", "percent"),
    [(0.0, "0 %"), (0.5, "50 %"), (0.333, "33 %"), (1.0, "100 %"), (2.0, "100 %"), (-1, "0 %")],
)
def test_p01_r02_the_progress_bar_shows_the_clamped_percentage(
    progress: float, percent: str
) -> None:
    root = render_loading_screen(FakeDocument(), LoadingView("Loading", progress))
    assert root.querySelector(".loading-percent").textContent == percent
    assert root.querySelector(".loading-fill").style.width == percent.split(maxsplit=1)[0] + "%"


def test_p01_r02_the_bar_is_a_progressbar_with_its_range_and_value() -> None:
    root = render_loading_screen(FakeDocument(), LoadingView("Loading", 0.25))
    bar = root.querySelector(".loading-bar")
    assert bar.getAttribute("role") == "progressbar"
    assert bar.getAttribute("aria-valuemin") == "0"
    assert bar.getAttribute("aria-valuemax") == "100"
    assert bar.getAttribute("aria-valuenow") == "25"


def test_p01_r02_the_loading_text_is_shown() -> None:
    root = render_loading_screen(FakeDocument(), LoadingView("Building the level", 0.1))
    assert root.querySelector(".loading-text").textContent == "Building the level"
