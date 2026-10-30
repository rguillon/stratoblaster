"""The browser around the game (P12-R03, P12-R05, P12-R11): the
first gesture unlocks the audio, a hidden page pauses the level and silences the audio, and a
timer schedules the music. `listen_to_page` returns a function that stops listening.

`PageOptions` is a plain class; its fields are None when omitted.
Targets are DOM-like objects with `addEventListener` and `removeEventListener`.
"""

from org.transcrypt.stubs.browser import __pragma__

from app.game_audio import GameAudio, GameAudioOptions
from config.audio import AUDIO_CONFIG

__pragma__("skip")
from typing import Any  # noqa: E402

from app.menu_controller import MenuController  # noqa: E402
from input.gamepad_menu_input import GamepadSource  # noqa: E402

__pragma__("noskip")

# The page's gesture events: any of them unlocks the audio (P12-R05).
GESTURE_EVENTS = ["keydown", "pointerdown", "pointerup", "touchend"]


class AudioOptions:
    """`PageOptions.audio`: how to create the Web Audio context (`GameAudioOptions` without the
    screen width and clock, which the app supplies)."""

    def __init__(self, create_context: Any | None, can_start: Any | None) -> None:
        # Creates the Web Audio context. Silent when None.
        self.create_context = create_context
        # Whether the page may start audio now. Always when None.
        self.can_start = can_start


class PageVisibility:
    """`PageOptions.visibility`: the target whose `visibilitychange` event is heard, and whether
    the page is hidden now."""

    def __init__(self, target: Any, hidden: Any) -> None:
        self.target = target
        self.hidden = hidden


class PageOptions:
    """The app's options about the page around it."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        audio: AudioOptions | None,
        gamepads: GamepadSource | None,
        gesture_target: Any | None,
        visibility: PageVisibility | None,
        every: Any | None,
    ) -> None:
        # Audio (P12-R05): how to create the Web Audio context. Silent when None.
        self.audio = audio
        # Connected gamepads. No gamepad when None.
        self.gamepads = gamepads
        # Where key presses, taps and clicks are heard to unlock the audio (P12-R05). The
        # gamepads' buttons unlock it too. None when omitted.
        self.gesture_target = gesture_target
        # The page's visibility (P12-R03, P12-R11): the level pauses and the audio goes quiet.
        self.visibility = visibility
        # Runs `tick` every `seconds` until the returned function is called (the music scheduler).
        self.every = every


class Ticker:
    """A frame split in two, as `start-app` runs it: `simulate(dt_seconds)` then `render()`."""

    def __init__(self, simulate: Any, render: Any) -> None:
        self.simulate = simulate
        self.render = render


def gamepad_pressed(gamepads: GamepadSource | None) -> bool:
    """Any button down on any gamepad: a user gesture."""
    if gamepads is None:
        return False
    for pad in gamepads():
        if pad is None:
            continue
        for button in pad.buttons:
            if button.pressed:
                return True
    return False


def listen_to_page(options: PageOptions, menu: MenuController, audio: GameAudio) -> Any:
    """Listens to the page (see the module doc). Returns the function that stops listening."""
    stops: list[Any] = []

    def unlock() -> None:
        audio.unlock()

    gestures = options.gesture_target
    for event_type in GESTURE_EVENTS:
        if gestures is not None:
            gestures.addEventListener(event_type, unlock)
        stops.append(_remover(gestures, event_type, unlock))
    visibility = options.visibility
    if visibility is not None:
        on_visibility = _visibility_listener(visibility, menu, audio)
        visibility.target.addEventListener("visibilitychange", on_visibility)
        stops.append(_remover(visibility.target, "visibilitychange", on_visibility))
    every = options.every
    if every is not None:
        stops.append(every(_updater(audio), AUDIO_CONFIG.schedule_interval_seconds))

    def stop_all() -> None:
        for stop in stops:
            stop()

    return stop_all


def _remover(target: Any | None, event_type: str, listener: Any) -> Any:
    """A function that removes `listener` from `target`, if there is one."""

    def remove() -> None:
        if target is not None:
            target.removeEventListener(event_type, listener)

    return remove


def _visibility_listener(visibility: PageVisibility, menu: MenuController, audio: GameAudio) -> Any:
    def on_visibility() -> None:
        hidden = visibility.hidden()
        if hidden:
            menu.pause()
        audio.set_hidden(hidden)

    return on_visibility


def _updater(audio: GameAudio) -> Any:
    def tick() -> None:
        audio.update()

    return tick


def create_app_audio(game: Any, options: PageOptions) -> "AppAudio":
    """The game's audio (P12-R05), on the app's own clock (the sound effect limits count in game
    time, P12-R10), and the frame wrapper that unlocks it on a gamepad button and schedules the
    music after each frame. Returns an object with `audio` and `with_audio(ticker)`.
    """
    # One-element list: the clock's state, read and written by the closures (no `nonlocal`).
    elapsed = [0.0]
    audio_options = options.audio
    create_context = audio_options.create_context if audio_options is not None else None
    can_start = audio_options.can_start if audio_options is not None else None
    audio = GameAudio(
        game.view.audio,
        GameAudioOptions(create_context, can_start, _clock_of(elapsed), game.screen.width),
    )
    return AppAudio(audio, _frame_wrapper(audio, options, elapsed))


class AppAudio:
    """What `create_app_audio` returns: the audio and the frame wrapper."""

    def __init__(self, audio: GameAudio, with_audio: Any) -> None:
        self.audio = audio
        self.with_audio = with_audio


def _clock_of(elapsed: list[float]) -> Any:
    def clock() -> float:
        return elapsed[0]

    return clock


def _frame_wrapper(audio: GameAudio, options: PageOptions, elapsed: list[float]) -> Any:
    def with_audio(ticker: Ticker) -> Ticker:
        def simulate(dt: float) -> None:
            elapsed[0] = elapsed[0] + max(0, dt)
            if gamepad_pressed(options.gamepads):
                audio.unlock()
            ticker.simulate(dt)
            audio.update()

        return Ticker(simulate, ticker.render)

    return with_audio
