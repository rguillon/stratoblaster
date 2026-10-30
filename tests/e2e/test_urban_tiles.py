"""e2e: districts on a grid of tiles, with the grid drawn (`tiles=1`, P15-R10)."""

import pytest
from e2e.menu_helpers import game_state, matches, open_debug, wait_for_level_time
from playwright.sync_api import Page, expect


@pytest.mark.parametrize("level_id", ["1-5", "2-5", "3-3", "4-5"])
def test_p15_r10_tiles_1_plays_over_its_districts_with_the_grid_drawn(
    page: Page, level_id: str
) -> None:
    open_debug(page, f"?level={level_id}&t=200&tiles=1")
    wait_for_level_time(page, 200.1)
    assert matches(game_state(page)["game"], {"levelId": level_id, "phase": "playing"})
    expect(page.locator("#fatal")).to_be_hidden()
