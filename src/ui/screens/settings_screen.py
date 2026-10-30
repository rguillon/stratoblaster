"""Settings screen (P12-R04), ported from `ui/screens/settings-screen.ts`: the Music and Sound
effects sliders. Over a paused level, the playfield shows dimmed behind it."""

from org.transcrypt.stubs.browser import __pragma__, window

__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any  # noqa: E402

from ui.menu_view import SettingsView, SliderView  # noqa: E402
from ui.screens.screen_handlers import ScreenHandlers  # noqa: E402

__pragma__("noskip")

from ui.screens.elements import back_button, element, entry  # noqa: E402


def _value_at(track: Any, client_x: float, max_value: int) -> float:
    """The slider value under a pointer at `client_x` over `track`: its nearest step."""
    box = track.getBoundingClientRect()
    if box.width <= 0:
        return 0
    share = window.Math.min(1, window.Math.max(0, (client_x - box.left) / box.width))
    return float(window.Math.round(share * max_value))


def _slider_bar(doc: Any, slider: SliderView) -> Any:
    """A bar of `max` cells, the first `value` of them lit, like the settings sketch."""
    bar = element(doc, "div", "slider-bar")
    for i in range(slider.max):
        bar.append(element(doc, "span", "slider-cell on" if i < slider.value else "slider-cell"))
    return bar


def _clear_flag(flag: list[bool]) -> Callable[[Any], None]:
    def handler(_event: Any) -> None:
        flag[0] = False

    return handler


def _drag_to_set(bar: Any, index: int, max_value: int, handlers: ScreenHandlers) -> None:
    """Tapping or dragging on the bar sets the slider (P12-R04)."""
    dragging = [False]

    def set_value(event: Any) -> None:
        if handlers.on_set is not None:
            handlers.on_set(index, _value_at(bar, event.clientX, max_value))

    def on_down(event: Any) -> None:
        dragging[0] = True
        event.stopPropagation()
        set_value(event)

    def on_move(event: Any) -> None:
        if dragging[0]:
            set_value(event)

    bar.addEventListener("pointerdown", on_down)
    bar.addEventListener("pointermove", on_move)
    for event_type in ["pointerup", "pointercancel", "pointerleave"]:
        bar.addEventListener(event_type, _clear_flag(dragging))

    # The row's own click would select it again: the bar already did.
    def on_click(event: Any) -> None:
        event.stopPropagation()

    bar.addEventListener("click", on_click)


def _slider_row(
    doc: Any, slider: SliderView, index: int, selected: bool, handlers: ScreenHandlers
) -> Any:
    row = entry(doc, "settings-slider", index, selected, handlers.on_tap)
    row.setAttribute("role", "slider")
    row.setAttribute("aria-label", slider.label)
    row.setAttribute("aria-valuemin", "0")
    row.setAttribute("aria-valuemax", str(slider.max))
    row.setAttribute("aria-valuenow", str(slider.value))
    bar = _slider_bar(doc, slider)
    _drag_to_set(bar, index, slider.max, handlers)
    row.append(
        element(doc, "span", "slider-label", slider.label),
        bar,
        element(doc, "span", "slider-value", str(slider.value)),
    )
    return row


def render_settings_screen(doc: Any, view: SettingsView, handlers: ScreenHandlers) -> Any:
    """Renders the settings screen (P12-R04)."""
    over = " over-level" if view.over_level else ""
    root = element(doc, "div", "menu-screen settings-screen" + over)
    sliders = element(doc, "div", "settings-list")
    for i, slider in enumerate(view.sliders):
        sliders.append(_slider_row(doc, slider, i, i == view.selected, handlers))
    root.append(
        back_button(doc, view.back, handlers.on_back),
        element(doc, "h2", "menu-heading", view.heading),
        sliders,
        element(doc, "div", "menu-hint", view.hint),
    )
    return root
