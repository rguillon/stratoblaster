"""e2e: the menu fits the window, marks the selection and has large touch targets (P01-R11,
P01-R13)."""

import pytest
from e2e.menu_helpers import expect_state, open_game, poll
from playwright.sync_api import Page, expect


@pytest.mark.parametrize(("width", "height"), [(800, 600), (1920, 1080), (390, 844)])
def test_p01_r13_the_menu_is_fully_visible_not_cropped_not_stretched(
    page: Page, width: int, height: int
) -> None:
    page.set_viewport_size({"width": width, "height": height})
    open_game(page)
    for selector in ["#stage", "#menu"]:
        box = page.locator(selector).bounding_box()
        assert box, f"{selector} has no box"
        assert box["x"] >= 0
        assert box["y"] >= 0
        assert box["x"] + box["width"] <= width + 1
        assert box["y"] + box["height"] <= height + 1
        assert box["width"] / box["height"] == pytest.approx(480 / 640, abs=0.005)
        assert max(box["width"] / width, box["height"] / height) > 0.99
    expect(page.locator(".title-version")).to_be_in_viewport(ratio=1)


def test_p01_r13_the_menu_follows_window_resizes(page: Page) -> None:
    page.set_viewport_size({"width": 800, "height": 600})
    open_game(page)
    page.set_viewport_size({"width": 390, "height": 844})

    def width() -> float:
        box = page.locator("#menu").bounding_box()
        return box["width"] if box else 0

    poll(width, lambda w: abs(w - 390) < 0.5, timeout=5000)


def test_p01_r13_the_selected_entry_is_marked_by_more_than_colour(page: Page) -> None:
    open_game(page)

    def marker(selector: str, pseudo: str, prop: str) -> str:
        value: str = page.locator(selector).evaluate(
            "(el, [p, prop]) => getComputedStyle(el, p || null).getPropertyValue(prop)",
            [pseudo, prop],
        )
        return value

    assert "▶" in marker(".title-start.selected", "::before", "content")
    page.locator(".title-start").click()
    expect_state(page, {"screen": "ship-select"})
    assert marker(".ship-card.selected", "::before", "visibility") == "visible"
    assert marker(".ship-card:not(.selected) >> nth=0", "::before", "visibility") == "hidden"
    page.locator(".ship-card.selected").click()
    expect_state(page, {"screen": "level-select"})
    assert marker(".level-cell.selected", "", "outline-style") == "dashed"


def test_p01_r11_touch_targets_are_at_least_44_css_px_on_a_phone(page: Page) -> None:
    page.set_viewport_size({"width": 390, "height": 844})
    open_game(page)
    page.locator(".title-start").click()
    expect_state(page, {"screen": "ship-select"})
    page.locator(".ship-card.selected").click()
    expect_state(page, {"screen": "level-select"})
    for target in page.locator(".menu-entry, .menu-back").all():
        box = target.bounding_box()
        assert box
        assert box["width"] >= 44
        assert box["height"] >= 44
