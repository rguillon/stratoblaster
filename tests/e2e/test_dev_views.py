# Copyright (c) 2026 Renaud Guillon
"""e2e: the enemies and bosses viewers' view buttons (specs/dev/dev-menu.md DEV-MENU-21).

Model, wireframe and game view: each button switches the view, and the viewer keeps running (the
game view steps a real enemy world, firing and moving, with no error on the page).
"""

import pytest
from e2e.menu_helpers import expect_state, send_action
from e2e.test_dev_audio import open_dev_menu
from playwright.sync_api import Page, expect

VIEWERS = [("enemies", 1), ("bosses", 2)]


@pytest.mark.parametrize(("viewer", "downs"), VIEWERS)
def test_dev_menu_21_the_view_buttons_switch_between_model_wireframe_and_game_view(
    page: Page, viewer: str, downs: int
) -> None:
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    open_dev_menu(page)
    for _ in range(downs):
        send_action(page, "down")
    expect_state(page, {"screen": "dev", "selectedId": viewer})
    send_action(page, "confirm")
    expect_state(page, {"screen": "dev-viewer", "selection": 0})
    buttons = page.locator(".dev-modes .dev-mode")
    expect(buttons).to_have_text(["Model", "Wireframe", "Game view"])
    expect(buttons.nth(0)).to_have_class("menu-entry dev-mode selected")
    for k in (1, 2, 0):
        buttons.nth(k).click()
        expect(page.locator(".dev-modes .dev-mode.selected")).to_have_text(
            ["Model", "Wireframe", "Game view"][k]
        )
        # A second of the view running.
        page.wait_for_timeout(1000)
    assert errors == []
