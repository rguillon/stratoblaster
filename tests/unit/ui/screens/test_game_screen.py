# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/ui/screens/game_screen.py`."""

from helpers.dom import FakeDocument, FakeEvent

from ui.menu_view import GameScreenView, LevelChoices, LevelCompleteView, PauseView
from ui.screens.game_screen import render_game_screen
from ui.screens.screen_handlers import ScreenHandlers


def handlers(
    taps: list[int] | None = None,
    fires: list[bool] | None = None,
    drags: list[tuple[float, float]] | None = None,
) -> ScreenHandlers:
    return ScreenHandlers(
        (taps if taps is not None else []).append,
        lambda: None,
        (fires if fires is not None else []).append,
        (lambda dx, dy: drags.append((dx, dy))) if drags is not None else None,
    )


def render(view: GameScreenView, h: ScreenHandlers) -> object:
    return render_game_screen(FakeDocument(), view, h)


def test_ui_hud_09_the_playfield_shows_the_level_and_the_fire_button_only() -> None:
    """No Back button over the playfield, no pause button (D-251). Also UI-HUD-06."""
    root = render(GameScreenView("Level 2", "FIRE", None, None, 0), handlers())
    assert root.className == "menu-screen game-screen"
    assert root.querySelector(".game-level").textContent == "Level 2"
    assert root.querySelector(".game-fire").textContent == "FIRE"
    assert root.querySelector(".game-pause") is None
    assert root.querySelector(".menu-back") is None


def test_game_ctrl_05_the_fire_button_reports_press_and_release_and_stops_the_event() -> None:
    fires: list[bool] = []
    root = render(GameScreenView("Level 2", "FIRE", None, None, 0), handlers(fires=fires))
    fire = root.querySelector(".game-fire")
    event = FakeEvent()
    fire.fire("pointerdown", event)
    fire.fire("pointerleave")
    assert fires == [True, False]
    assert event.stopped is True


def test_game_ctrl_04_dragging_the_playfield_reports_the_pointer_offsets() -> None:
    drags: list[tuple[float, float]] = []
    root = render(GameScreenView("Level 2", "FIRE", None, None, 0), handlers(drags=drags))
    root.fire("pointermove", FakeEvent(x=5, y=5))  # not down: nothing
    root.fire("pointerdown", FakeEvent(x=10, y=10))
    root.fire("pointermove", FakeEvent(x=13, y=7))
    root.fire("pointerup")
    root.fire("pointermove", FakeEvent(x=20, y=20))
    assert drags == [(3, -3)]


def test_ui_over_01_the_level_complete_panel_replaces_the_controls_and_taps_go_on() -> None:
    """Also UI-OVER-03 (a tap goes on)."""
    taps: list[int] = []
    complete = LevelCompleteView(
        "Level complete",
        over=False,
        level="Level 2",
        enemies="5/5",
        score="1200",
        hint="Tap to go on",
    )
    root = render(GameScreenView("Level 2", "FIRE", complete, None, 0), handlers(taps=taps))
    assert root.querySelector(".game-fire") is None
    panel = root.querySelector(".level-complete")
    assert panel.querySelector(".level-complete-heading").textContent == "Level complete"
    assert panel.querySelector(".level-complete-score").textContent == "1200"
    assert panel.querySelector(".level-complete-high-score") is None
    assert panel.querySelector(".menu-hint").textContent == "Tap to go on"
    assert panel.classList.contains("menu-entry")
    panel.fire("click")
    assert taps == [0]


def test_ui_over_06_a_game_over_with_choices_shows_the_choices_not_a_tap_to_go_on() -> None:
    taps: list[int] = []
    choices = LevelChoices(["Continue", "Level select"], 1)
    complete = LevelCompleteView(
        "Game over",
        over=True,
        level="Mini boss",
        enemies="4/5",
        score="300",
        hint="",
        new_high_score="New high score",
        choices=choices,
    )
    root = render(GameScreenView("Mini boss", "", complete, None, 0), handlers(taps=taps))
    panel = root.querySelector(".level-complete")
    assert panel.classList.contains("game-over")
    assert panel.querySelector(".level-complete-high-score").textContent == "New high score"
    buttons = panel.querySelectorAll(".level-complete-choice")
    assert [button.textContent for button in buttons] == ["Continue", "Level select"]
    assert buttons[1].classList.contains("selected")
    buttons[0].fire("click")
    assert taps == [0]


def test_ui_pause_07_a_paused_level_shows_the_pause_panel_only() -> None:
    paused = PauseView("Paused", ["Resume", "Leave"], "hint")
    root = render(GameScreenView("Level 2", "FIRE", None, paused, 1), handlers())
    assert root.querySelector(".pause-panel") is not None
    assert root.querySelector(".game-fire") is None


def test_game_ctrl_04_without_touch_handlers_the_buttons_and_drags_only_stop_their_events() -> None:
    """Also GAME-CTRL-05: nothing listens to the fire button."""
    taps: list[int] = []
    root = render(
        GameScreenView("Level 2", "FIRE", None, None, 0),
        ScreenHandlers(taps.append, lambda: None),
    )
    press = FakeEvent()
    root.querySelector(".game-fire").fire("pointerdown", press)
    root.fire("pointerdown", FakeEvent(x=10, y=10))
    root.fire("pointermove", FakeEvent(x=13, y=7))
    root.fire("pointermove", FakeEvent(x=20, y=20))
    assert press.stopped is True
    assert taps == []
