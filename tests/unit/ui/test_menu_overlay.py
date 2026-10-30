"""Unit tests of `src/ui/menu_overlay.py`."""

from types import SimpleNamespace

from helpers.dom import FakeDocument, FakeEvent

from input.menu_action import MenuSelect, MenuSet
from ui.menu_overlay import MenuOverlay, MenuOverlayOptions
from ui.menu_view import (
    DevMenuView,
    DevViewerView,
    GameScreenView,
    LevelOption,
    LevelSelectView,
    LoadingView,
    SettingsView,
    SliderView,
    TitleView,
)


class FakeTouch:
    def __init__(self) -> None:
        self.fired: list[bool] = []
        self.drags: list[tuple[float, float]] = []

    def fire(self, held: bool) -> None:
        self.fired.append(held)

    def drag(self, dx: float, dy: float) -> None:
        self.drags.append((dx, dy))


def title(selected: int = 0) -> TitleView:
    return TitleView("STRATO", "High", 0, "Start", "Settings", selected, "hint", "1.0", "abc")


def make_overlay(
    touch: FakeTouch | None = None,
) -> tuple[MenuOverlay, FakeDocument, object, list]:
    doc = FakeDocument()
    root = doc.createElement("div")
    root.offsetWidth = 100
    root.rect.width = 100
    commands: list = []
    overlay = MenuOverlay(doc, root, commands.append, MenuOverlayOptions(0.25), touch)
    return overlay, doc, root, commands


def test_p01_r15_a_new_screen_fades_in_over_the_transition_time() -> None:
    overlay, _, root, _ = make_overlay()
    overlay.show(title())
    screen = root.children[0]
    assert screen.dataset.screen == "title"
    assert screen.classList.contains("menu-enter")
    assert screen.style.animationDuration == "0.25s"


def test_p01_r15_a_loading_screen_does_not_fade_in() -> None:
    overlay, _, root, _ = make_overlay()
    overlay.show(LoadingView("Loading", 0.1))
    assert not root.children[0].classList.contains("menu-enter")


def test_p01_r13_showing_a_new_view_replaces_the_old_screen() -> None:
    overlay, _, root, _ = make_overlay()
    overlay.show(title())
    overlay.show(title(selected=1))
    assert len(root.children) == 1
    assert root.children[0].querySelector(".title-settings").classList.contains("selected")
    assert overlay.view is not None
    assert overlay.view.selected == 1


def test_p01_r15_the_same_screen_again_does_not_fade_in_again() -> None:
    overlay, _, root, _ = make_overlay()
    overlay.show(title())
    root.children[0].classList.remove("menu-enter")
    overlay.show(title(selected=1))
    assert not root.children[0].classList.contains("menu-enter")


def test_p01_r11_tapping_the_selected_entry_confirms_and_another_selects_it() -> None:
    overlay, _, root, commands = make_overlay()
    overlay.show(title(selected=0))
    root.children[0].querySelector(".title-start").fire("click")
    root.children[0].querySelector(".title-settings").fire("click")
    assert commands[0] == "confirm"
    assert isinstance(commands[1], MenuSelect)
    assert commands[1].select == 1


def test_p01_r11_the_back_button_sends_back() -> None:
    overlay, _, root, commands = make_overlay()
    overlay.show(
        LevelSelectView("Levels", "hint", "Back", 0, 1, [LevelOption("1", False)], "Locked")
    )
    root.children[0].querySelector(".menu-back").fire("click")
    assert commands == ["back"]


def test_p06_r02_the_touch_fire_button_reports_press_and_release() -> None:
    touch = FakeTouch()
    overlay, _, root, _ = make_overlay(touch)
    overlay.show(GameScreenView("Level 1", "FIRE", "II", None, None, 0))
    fire = root.children[0].querySelector(".game-fire")
    fire.fire("pointerdown")
    fire.fire("pointerup")
    assert touch.fired == [True, False]


def test_p06_r02_a_drag_is_passed_on_in_logical_pixels_with_y_up() -> None:
    touch = FakeTouch()
    overlay, _, root, _ = make_overlay(touch)
    root.rect.width = 200  # the overlay is drawn at twice its logical size
    overlay.show(GameScreenView("Level 1", "FIRE", "II", None, None, 0))
    playfield = root.children[0]
    playfield.fire("pointerdown", FakeEvent(x=10, y=10))
    playfield.fire("pointermove", FakeEvent(x=30, y=0))
    assert touch.drags == [(10.0, 5.0)]


def test_p01_r07_the_game_pause_button_sends_pause() -> None:
    overlay, _, root, commands = make_overlay()
    overlay.show(GameScreenView("Level 1", "FIRE", "II", None, None, 0))
    root.children[0].querySelector(".game-pause").fire("click")
    assert commands == ["pause"]


def test_p12_r04_a_slider_is_set_by_its_value_under_the_pointer() -> None:
    overlay, _, root, commands = make_overlay()
    overlay.show(SettingsView("Settings", "hint", "Back", 0, [SliderView("Music", 0, 10)], False))
    bar = root.children[0].querySelector(".slider-bar")
    bar.rect.left = 0
    bar.rect.width = 100
    bar.fire("pointerdown", FakeEvent(x=50))
    assert len(commands) == 1
    assert isinstance(commands[0], MenuSet)
    assert (commands[0].set, commands[0].value) == (0, 5)


def test_p01_r07_a_locked_pick_shakes_the_selected_entry_and_shows_the_text() -> None:
    overlay, _, root, _ = make_overlay()
    overlay.show(
        LevelSelectView("Levels", "hint", "Back", 0, 1, [LevelOption("2", True)], "Locked")
    )
    overlay.shake_selected("Locked: finish level 1")
    screen = root.children[0]
    assert screen.querySelector(".menu-entry.selected").classList.contains("shake")
    assert screen.querySelector(".menu-status").textContent == "Locked: finish level 1"


def test_p01_r07_shaking_with_nothing_shown_does_nothing() -> None:
    overlay, _, _, _ = make_overlay()
    overlay.shake_selected("Locked")


def test_p13_r01_dispose_removes_the_screen_and_forgets_the_view() -> None:
    overlay, _, root, _ = make_overlay()
    overlay.show(title())
    overlay.dispose()
    assert root.children == []
    assert overlay.view is None


def test_p01_r13_a_title_logo_is_fitted_to_the_page() -> None:
    overlay, _, root, _ = make_overlay()
    overlay.show(title())
    logo = root.children[0].querySelector(".title-name")
    assert logo is not None
    assert logo.style.fontSize == ""


def test_d199_the_dev_screens_render_and_the_wheel_reaches_its_handler() -> None:
    doc = FakeDocument()
    root = doc.createElement("div")
    wheels: list[float] = []
    overlay = MenuOverlay(doc, root, [].append, MenuOverlayOptions(0.25), None, wheels.append)
    assert overlay.root is root
    overlay.show(DevMenuView("Dev", "hint", "Back", 0, ["Ships"]))
    assert root.querySelector(".dev-screen") is not None
    overlay.show(DevViewerView("Ships", "hint", "Back", 0, "Alpha", "1 / 3", False))
    screen = root.querySelector(".dev-viewer-screen")
    screen.fire("wheel", SimpleNamespace(deltaY=-100, preventDefault=lambda: None))
    assert wheels == [-100]
