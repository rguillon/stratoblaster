# Copyright (c) 2026 Renaud Guillon
"""Game screen overlay: the level played (UI-HUD-06), the touch fire button.

The drag area over the playfield, the pause menu while paused (UI-PAUSE-07) and the "Level complete"
panel at the end (UI-OVER-01).
"""

from ui.screens.elements import element, tap_listener
from ui.screens.pause_panel import pause_panel

# isort: split
# __pragma__ ("skip")
from collections.abc import Callable
from typing import Any

from ui.menu_view import GameScreenView, LevelChoices, LevelCompleteView
from ui.screens.screen_handlers import ScreenHandlers

# __pragma__ ("noskip")


def _choice_row(doc: Any, choices: LevelChoices, handlers: ScreenHandlers) -> Any:
    """Continue or level select (UI-OVER-06): a tap selects a choice, a second tap confirms it."""
    row = element(doc, "div", "level-complete-choices")
    for i, label in enumerate(choices.labels):
        selected = " selected" if i == choices.selected else ""
        choice = element(doc, "div", "menu-entry level-complete-choice" + selected, label)
        choice.setAttribute("role", "button")
        choice.dataset.index = str(i)
        choice.addEventListener("click", tap_listener(handlers.on_tap, i))
        row.append(choice)
    return row


def _level_complete(doc: Any, complete: LevelCompleteView, handlers: ScreenHandlers) -> Any:
    """Return the "Level complete" (or "Game over") panel (UI-OVER-01).

    Tapping it goes on, like Confirm (UI-OVER-03). After the mini boss, a game over offers its two
    choices instead (UI-OVER-06).
    """
    over = " game-over" if complete.over else ""
    choices = complete.choices
    selected = "" if choices else " menu-entry selected"
    panel = element(doc, "div", "level-complete" + over + selected)
    panel.append(
        element(doc, "div", "level-complete-heading", complete.heading),
        element(doc, "div", "level-complete-level", complete.level),
        element(doc, "div", "level-complete-enemies", complete.enemies),
        element(doc, "div", "level-complete-score", complete.score),
    )
    if complete.new_high_score:
        panel.append(element(doc, "div", "level-complete-high-score", complete.new_high_score))
    if choices:
        panel.append(_choice_row(doc, choices, handlers))
        return panel
    panel.setAttribute("role", "button")
    panel.dataset.index = "0"
    panel.append(element(doc, "div", "menu-hint", complete.hint))
    panel.addEventListener("click", tap_listener(handlers.on_tap, 0))
    return panel


def _press(on_fire: Callable[[bool], None] | None, held: bool) -> Callable[[Any], None]:
    """Return a pointer listener of the fire button: stops the event, then reports `held`."""

    def handler(event: Any) -> None:
        event.stopPropagation()
        if on_fire is not None:
            on_fire(held)

    return handler


def _fire_button(doc: Any, label: str, handlers: ScreenHandlers) -> Any:
    """Return the touch fire button: shoots while pressed (GAME-CTRL-05, UI-HUD-10)."""
    button = element(doc, "div", "game-fire", label)
    button.setAttribute("role", "button")
    button.addEventListener("pointerdown", _press(handlers.on_fire, True))
    for event_type in ["pointerup", "pointercancel", "pointerleave"]:
        button.addEventListener(event_type, _press(handlers.on_fire, False))
    return button


def _drag_area(root: Any, handlers: ScreenHandlers) -> None:
    """Drag anywhere to fly (GAME-CTRL-04).

    Pointer moves while a finger or button is down are passed on as screen pixel offsets.
    """
    # The last pointer position, `[x, y]`, or None while nothing is down.
    last: list[Any] = [None]

    def on_down(event: Any) -> None:
        last[0] = [event.clientX, event.clientY]

    def on_move(event: Any) -> None:
        if last[0] is None:
            return
        if handlers.on_drag is not None:
            handlers.on_drag(event.clientX - last[0][0], event.clientY - last[0][1])
        last[0] = [event.clientX, event.clientY]

    def on_up(_event: Any) -> None:
        last[0] = None

    root.addEventListener("pointerdown", on_down)
    root.addEventListener("pointermove", on_move)
    for event_type in ["pointerup", "pointercancel"]:
        root.addEventListener(event_type, on_up)


def render_game_screen(doc: Any, view: GameScreenView, handlers: ScreenHandlers) -> Any:
    """Return the overlay of the game screen.

    The fire button shows only while the level is played (no pause button since D-251: the
    keyboard and the gamepad pause, UI-PAUSE-01). The HUD is drawn by `GameHud`, which updates
    every frame.
    """
    root = element(doc, "div", "menu-screen game-screen")
    # No Back button over the playfield (UI-HUD-09): the level is left from the pause menu.
    root.append(element(doc, "div", "game-level", view.level))
    if view.complete:
        root.append(_level_complete(doc, view.complete, handlers))
    elif view.paused:
        root.append(pause_panel(doc, view.paused, view.selected, handlers))
    else:
        root.append(_fire_button(doc, view.fire, handlers))
        _drag_area(root, handlers)
    return root
