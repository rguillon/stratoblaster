# Copyright (c) 2026 Renaud Guillon
"""Bootstrap only (ENG-10): create the engine and start the app.

`index.html` calls `main()` once the page has loaded.

`E2E` is set by the build: `make e2e-build` compiles with the Transcrypt symbol `e2e`, which keeps
the `__pragma__("ifdef", "e2e")` blocks (the test API, ENG-52); `make build` drops them. The perf
overlay (ENG-111) is on in e2e builds only.
The debug viewers (ships, shots, enemies, bosses, props) are gone: only the game page is built,
and the dev viewers are inside it (DEV-MENU-02).
"""

from org.transcrypt.stubs.browser import __pragma__, document, window

from app.debug_options import ai_mode, dev_mode, parse_debug_options
from app.page_audio import AudioOptions, PageVisibility
from app.page_fullscreen import PageFullscreen
from app.start_app import AppOptions, start_app
from build_info import APP_COMMIT, APP_VERSION  # The version and commit on the title (ENG-83).
from config.engine import ENGINE_CONFIG
from config.menu import MENU_CONFIG
from game.index import GAME  # The one import of `game/` outside it (ENG-142, ENG-144).
from host.cookie_storage import CookieStorage
from host.webgl_support import has_webgl2
from input.gamepad_menu_input import browser_gamepads
from render.babylon import new_engine
from ui.stage_fit import apply_stage_fit, fit_stage, render_ratio

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module, ENG-153).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")

# isort: split
# __pragma__ ("ifdef", "e2e")
from debug.remote_player import ask_json, install_remote_player
from debug.test_api import install_test_api

# __pragma__ ("endif")

E2E = False
__pragma__("ifdef", "e2e")
E2E = True
__pragma__("endif")
DEV_BUILD = False


def show_fatal(message: str) -> None:
    """Show `message` in the #fatal element, if the page has one."""
    el = document.getElementById("fatal")
    if el:
        el.textContent = message
        el.hidden = False


def reload_page() -> None:
    """Reload the page: the reload button of the lost graphics context's message (UI-LOAD-07)."""
    window.location.reload()


def show_context_lost() -> None:
    """UI-LOAD-07: the lost graphics context's message over the page, with a reload button.

    The button reloads the page (ENG-110).
    """
    el = document.getElementById("fatal")
    if not el:
        return
    # `show_fatal` replaces the element's content, so a button is not added twice.
    # The texts record is read by its camelCase keys, as in app/menu_view_builder.py.
    texts: Any = GAME.texts
    show_fatal(texts.contextLost)
    el.style.flexDirection = "column"
    el.style.gap = "16px"
    button = document.createElement("button")
    button.textContent = texts.reload
    button.onclick = reload_page
    el.appendChild(button)


class PageError(Exception):
    """The page lacks an element the app needs."""


def element(element_id: str) -> Any:
    """Return the element called `element_id`; raises when the page lacks it."""
    el = document.getElementById(element_id)
    if not el:
        raise PageError("#" + element_id + " not found")
    return el


# The browser helpers below are raw JavaScript (ENG-158).
def audio_context_available() -> bool:
    """Whether the browser has Web Audio (AUD-ENGINE-04)."""
    __pragma__("js", "{}", "return typeof AudioContext === 'function';")
    return False


def new_audio_context() -> object:
    """Return a new Web Audio context. Only called during a user gesture (AUD-ENGINE-03)."""
    __pragma__("js", "{}", "return new AudioContext();")
    return None


def audio_can_start() -> bool:
    """Whether the page's user activation lets audio start (AUD-ENGINE-03); true when unknown."""
    __pragma__("js", "{}", "var a = navigator.userActivation; return a ? a.isActive : true;")
    return True


def fetch_sample(sample_name: str) -> object:
    """Return a promise of the bytes of the sound `sample_name` (`sfx/<name>.ogg`, AUD-ENGINE-01).

    `.mp3` where the browser cannot play Ogg Vorbis. A failed request rejects the promise.
    """
    __pragma__(
        "js",
        "{}",
        "var ogg = new Audio().canPlayType('audio/ogg; codecs=vorbis') !== '';"
        "return fetch('sfx/' + sample_name + (ogg ? '.ogg' : '.mp3')).then(function (r) {"
        "if (!r.ok) { throw new Error('sfx ' + sample_name + ': ' + r.status); }"
        "return r.arrayBuffer(); });",
    )
    return None


def browser_audio() -> AudioOptions:
    """Web Audio, if the browser has it (AUD-ENGINE-04).

    The context is only created during a user gesture that lets audio start, so no autoplay
    warning is shown.
    """
    if not audio_context_available():
        return AudioOptions(None, None)
    return AudioOptions(new_audio_context, audio_can_start, fetch_sample)


def start_interval(tick: Any, seconds: float) -> Any:
    """Run `tick` every `seconds` (the music scheduler, AUD-ENGINE-05). Returns the stopper."""
    __pragma__(
        "js",
        "{}",
        "var id = setInterval(tick, seconds * 1000); return function () { clearInterval(id); };",
    )
    return None


def next_frame() -> Any:
    """Return a promise that resolves at the next animation frame."""
    __pragma__(
        "js",
        "{}",
        "return new Promise(function (resolve) {"
        " requestAnimationFrame(function () { resolve(); }); });",
    )
    return None


def document_hidden() -> bool:
    """Whether the page is hidden now (UI-PAUSE-11; the window's `blur` is heard too)."""
    hidden: bool = document.visibilityState == "hidden"
    return hidden


def pixel_ratio() -> float:
    """Return the device pixel ratio, capped (ENGINE_CONFIG.max_device_pixel_ratio)."""
    ratio: float = window.devicePixelRatio
    cap: float = ENGINE_CONFIG.max_device_pixel_ratio
    if ratio < cap:
        return ratio
    return cap


def fit_to_window(engine: Any, stage: Any, overlay: Any, draw_scale: float) -> None:
    """Keep the stage and the menu overlay fitted to the window (ENG-110, GAME-SCREEN-02).

    Covers UI-LOOK-02 too. The canvas draws `draw_scale` times the pixels of the stage (1, or
    less in e2e builds), capped at `ENGINE_CONFIG.max_render_scale` pixels per logical pixel
    (D-250): the hardware scaling level follows the fit, so a resize keeps the cap.
    """

    def fit() -> None:
        stage_fit = fit_stage(window.innerWidth, window.innerHeight, GAME.screen)
        apply_stage_fit(stage, overlay, stage_fit, GAME.screen)
        ratio = render_ratio(pixel_ratio(), stage_fit, ENGINE_CONFIG.max_render_scale)
        engine.setHardwareScalingLevel(1 / (ratio * draw_scale))
        engine.resize()

    window.addEventListener("resize", fit)
    fit()


def tested() -> bool:
    """Whether the tests step the app: an e2e build, unless the AI player plays it (D-266).

    `?ai` runs the e2e build in real time, as the production game, with its test API on.
    """
    return E2E and not ai_mode(window.location.search)


def start_game(engine: Any, draw_scale: float) -> None:
    """Start the game page: the menu, the levels and the audio."""
    stepped = tested()
    document.title = GAME.title
    overlay = element("menu")
    fit_to_window(engine, element("stage"), overlay, draw_scale)
    # The URL's debug options, in every build (DEV-OPT-01, DEV-OPT-07).
    debug = parse_debug_options(window.location.search)
    options = AppOptions(
        True,
        document,
        overlay,
        CookieStorage(document, MENU_CONFIG.cookie_max_age_days),
        next_frame,
        # e2e builds have no render loop: the tests step the app (ENG-52, ENG-58, DEV-API-08).
        not stepped,
        APP_VERSION,
        APP_COMMIT,
        window,
        debug,
        # The debug FPS / polygons tile: in debug mode, or shown with its key (D-212).
        document.body,
        None,
        # The perf overlay (F3) in dev and e2e builds only (ENG-111, DEV-PERF-03).
        document.body if DEV_BUILD or E2E else None,
        # PERF-09, PERF-10: levels load in steps, behind a loading screen.
        True,
        # PERF-20: shaders compiled while a level loads; not in e2e builds (ENG-52, DEV-API-10).
        not stepped,
        # PERF-12, PERF-13: the highlighted level is prepared in a worker, and built ahead
        # (D-178); not built ahead in e2e builds (DEV-API-10).
        True,
        not stepped,
        browser_audio(),
        browser_gamepads(window.navigator),
        window,
        PageVisibility(document, document_hidden, window),
        start_interval,
        # DEV-MENU-01 (D-199): the Dev entry of the title screen, with `?dev` in the URL.
        dev_mode(window.location.search),
        # UI-TITLE-11: the title's Full screen entry.
        PageFullscreen(document),
    )
    app = start_app(engine, GAME, options)
    __pragma__("ifdef", "e2e")
    install_test_api(window, app)
    # D-266: the AI player of `make serve-ai`, with `?ai` in the URL.
    if not stepped:
        install_remote_player(app, start_interval, ask_json)
    __pragma__("endif")


def main() -> None:
    """Run the game page: the WebGL check, the engine, then the app."""
    canvas: Any = document.getElementById("game-canvas")
    if not is_canvas(canvas):
        msg = "#game-canvas not found"
        raise PageError(msg)
    # UI-LOAD-01 (ENG-06): without WebGL2, a friendly message (UI-LOAD-02) shows instead of the
    # menu, with no error.
    if not has_webgl2(lambda: document.createElement("canvas")):
        show_fatal(GAME.texts.unsupported)
        return
    # Antialiasing on; `adaptToDeviceRatio` off and `stencil` on. e2e builds draw fewer pixels,
    # without multisampling (ENGINE_CONFIG.e2e, D-075).
    e2e = ENGINE_CONFIG.e2e
    stepped = tested()
    antialias = e2e.antialias if stepped else True
    engine = new_engine(canvas, antialias)
    # UI-LOAD-07: a lost WebGL context asks the player to reload, with a button (ENG-110).
    engine.onContextLostObservable.add(show_context_lost)
    # The pixels drawn per stage pixel: set with the fit (D-250).
    start_game(engine, e2e.render_scale if stepped else 1)


def is_canvas(el: Any) -> bool:
    """Whether `el` is an HTMLCanvasElement."""
    __pragma__("js", "{}", "return el instanceof HTMLCanvasElement;")
    return False
