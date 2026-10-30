"""Unit tests of `src/app/page_audio.py`."""
# (P12-R03, P12-R05, P12-R11): the page around the game.

from unittest.mock import MagicMock

from helpers.gamepads import FakeGamepad

from app.page_audio import (
    GESTURE_EVENTS,
    AudioOptions,
    PageOptions,
    PageVisibility,
    Ticker,
    create_app_audio,
    gamepad_pressed,
    listen_to_page,
)
from config.audio import AUDIO_CONFIG


def page(**overrides: object) -> PageOptions:
    values: dict[str, object] = {
        "audio": None,
        "gamepads": None,
        "gesture_target": None,
        "visibility": None,
        "every": None,
    }
    values.update(overrides)
    return PageOptions(*values.values())  # type: ignore[arg-type]


def test_p12_r05_any_key_tap_or_button_is_a_gesture_that_unlocks_the_audio() -> None:
    target = MagicMock()
    audio = MagicMock()
    stop = listen_to_page(page(gesture_target=target), MagicMock(), audio)
    for event_type in GESTURE_EVENTS:
        call = [c for c in target.addEventListener.call_args_list if c.args[0] == event_type]
        assert len(call) == 1
        call[0].args[1]()
    assert audio.unlock.call_count == len(GESTURE_EVENTS)
    stop()
    assert target.removeEventListener.call_count == len(GESTURE_EVENTS)


def test_p12_r03_hiding_the_page_pauses_the_level_and_silences_the_audio() -> None:
    hidden = {"value": False}
    page_target = MagicMock()
    menu = MagicMock()
    audio = MagicMock()
    listen_to_page(
        page(visibility=PageVisibility(page_target, lambda: hidden["value"])),
        menu,
        audio,
    )
    on_visibility = page_target.addEventListener.call_args.args[1]
    hidden["value"] = True
    on_visibility()
    menu.pause.assert_called_once()
    audio.set_hidden.assert_called_with(True)


def test_p12_r11_showing_the_page_again_brings_the_sound_back_but_does_not_resume() -> None:
    hidden = {"value": False}
    page_target = MagicMock()
    menu = MagicMock()
    audio = MagicMock()
    listen_to_page(
        page(visibility=PageVisibility(page_target, lambda: hidden["value"])),
        menu,
        audio,
    )
    on_visibility = page_target.addEventListener.call_args.args[1]
    on_visibility()
    menu.pause.assert_not_called()
    audio.set_hidden.assert_called_with(False)


def test_p12_r05_the_music_scheduler_runs_on_the_timer_until_stopped() -> None:
    timer = MagicMock(return_value=lambda: None)
    audio = MagicMock()
    stop = listen_to_page(page(every=timer), MagicMock(), audio)
    timer.assert_called_once()
    tick, interval = timer.call_args.args
    assert interval == AUDIO_CONFIG.schedule_interval_seconds
    tick()
    audio.update.assert_called_once()
    stop()


def test_p12_r05_nothing_listens_when_the_page_gives_no_targets() -> None:
    audio = MagicMock()
    stop = listen_to_page(page(), MagicMock(), audio)
    stop()
    audio.unlock.assert_not_called()


def test_p12_r05_a_pressed_gamepad_button_is_a_gesture() -> None:
    assert gamepad_pressed(None) is False
    assert gamepad_pressed(lambda: [None, FakeGamepad()]) is False
    assert gamepad_pressed(lambda: [FakeGamepad().press(3)]) is True


def test_p12_r05_the_audio_is_created_from_the_game_and_unlocked_by_a_gamepad_button() -> None:
    game = MagicMock()
    game.view.audio = MagicMock(name="bindings")
    game.screen.width = 320
    created: list = []

    def create() -> object:
        created.append(True)
        return MagicMock()

    options = page(
        audio=AudioOptions(create, None),
        gamepads=lambda: [FakeGamepad().press(0)],
    )
    app_audio = create_app_audio(game, options)
    assert app_audio.audio is not None
    inner = Ticker(MagicMock(), MagicMock())
    wrapped = app_audio.with_audio(inner)
    wrapped.simulate(0.1)
    assert created  # the gamepad button unlocked the audio on the frame
    assert wrapped.render is inner.render


def test_p12_r05_the_frame_wrapper_runs_the_frame_then_schedules_the_music() -> None:
    game = MagicMock()
    game.screen.width = 320
    app_audio = create_app_audio(game, page())
    simulate = MagicMock()
    inner = Ticker(simulate, MagicMock())
    wrapped = app_audio.with_audio(inner)
    wrapped.simulate(0.25)
    simulate.assert_called_once_with(0.25)
