"""Unit tests of `src/ui/stats_tile.py`."""

from helpers.dom import FakeDocument

from ui.stats_tile import RenderStats, StatsTile


def test_p13_r01_the_tile_shows_the_frame_rate_and_the_polygons() -> None:
    doc = FakeDocument()
    parent = doc.createElement("div")
    tile = StatsTile(doc, parent, 0.5)
    assert tile.root.parentElement is parent
    tile.update(0.0, RenderStats(59.6, 1234))
    assert tile.root.querySelector(".stats-fps").textContent == "FPS: 60"
    assert tile.root.querySelector(".stats-polygons").textContent == "Polygons: 1,234"


def test_p13_r01_the_numbers_change_only_every_refresh_interval() -> None:
    doc = FakeDocument()
    tile = StatsTile(doc, doc.createElement("div"), 0.5)
    tile.update(0.0, RenderStats(60, 10))
    tile.update(0.2, RenderStats(30, 20))
    fps = tile.root.querySelector(".stats-fps")
    assert fps.textContent == "FPS: 60"
    tile.update(0.4, RenderStats(30, 20))
    assert fps.textContent == "FPS: 30"
