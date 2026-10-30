"""Bootstrap only (ENG-10): create the engine and start the app.

`index.html` calls `main()` once the page has loaded.

`E2E` is set by the build: `make e2e-build` compiles with the Transcrypt symbol `e2e`, which keeps
the `__pragma__("ifdef", "e2e")` blocks (the test API, ENG-52); `make build` drops them. The perf
overlay (ENG-111) is on in e2e builds only.
The debug viewers (ships, shots, enemies, bosses, props) are gone: only the game page is built.
"""

from org.transcrypt.stubs.browser import __pragma__, document, window

from app.debug_options import dev_mode, parse_debug_options
from app.page_audio import AudioOptions, PageVisibility
from app.start_app import AppOptions, start_app
from build_info import APP_COMMIT, APP_VERSION  # The version and commit on the title (ENG-83).
from config.engine import ENGINE_CONFIG
from config.menu import MENU_CONFIG
from game.index import GAME
from host.cookie_storage import CookieStorage
from host.webgl_support import has_webgl2
from input.gamepad_menu_input import browser_gamepads
from render.babylon import new_engine
from ui.stage_fit import apply_stage_fit, fit_stage

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

__pragma__("ifdef", "e2e")
from debug.test_api import install_test_api  # noqa: E402

__pragma__("endif")

E2E = False
__pragma__("ifdef", "e2e")
E2E = True
__pragma__("endif")
DEV_BUILD = False


def show_fatal(message: str) -> None:
    """Shows `message` in the #fatal element, if the page has one."""
    el = document.getElementById("fatal")
    if el:
        el.textContent = message
        el.hidden = False


def element(element_id: str) -> Any:
    """The element called `element_id`; raises when the page lacks it."""
    el = document.getElementById(element_id)
    if not el:
        raise Exception("#" + element_id + " not found")
    return el


def audio_context_available() -> bool:
    """Whether the browser has Web Audio (P12-R05)."""
    __pragma__("js", "{}", "return typeof AudioContext === 'function';")
    return False


def new_audio_context() -> object:
    """A new Web Audio context. Only called during a user gesture (P12-R05)."""
    __pragma__("js", "{}", "return new AudioContext();")
    return None


def audio_can_start() -> bool:
    """Whether the page's user activation lets audio start (P12-R05); true when unknown."""
    __pragma__("js", "{}", "var a = navigator.userActivation; return a ? a.isActive : true;")
    return True


def browser_audio() -> AudioOptions:
    """Web Audio, if the browser has it (P12-R05): the context is only created during a user
    gesture that lets audio start, so no autoplay warning is shown."""
    if not audio_context_available():
        return AudioOptions(None, None)
    return AudioOptions(new_audio_context, audio_can_start)


def start_interval(tick: Any, seconds: float) -> Any:
    """Runs `tick` every `seconds` (the music scheduler, P12-R05). Returns the stopper."""
    __pragma__(
        "js",
        "{}",
        "var id = setInterval(tick, seconds * 1000); return function () { clearInterval(id); };",
    )
    return None


def next_frame() -> Any:
    """A promise that resolves at the next animation frame."""
    __pragma__(
        "js",
        "{}",
        "return new Promise(function (resolve) {"
        " requestAnimationFrame(function () { resolve(); }); });",
    )
    return None


def document_hidden() -> bool:
    """Whether the page is hidden now (P12-R03)."""
    hidden: bool = document.visibilityState == "hidden"
    return hidden


def pixel_ratio() -> float:
    """The device pixel ratio, capped (ENGINE_CONFIG.max_device_pixel_ratio)."""
    ratio: float = window.devicePixelRatio
    cap: float = ENGINE_CONFIG.max_device_pixel_ratio
    if ratio < cap:
        return ratio
    return cap


def fit_to_window(engine: Any, stage: Any, overlay: Any) -> None:
    """Keeps the stage and the menu overlay fitted to the window."""

    def fit() -> None:
        apply_stage_fit(
            stage,
            overlay,
            fit_stage(window.innerWidth, window.innerHeight, GAME.screen),
            GAME.screen,
        )
        engine.resize()

    window.addEventListener("resize", fit)
    fit()


def start_game(engine: Any) -> None:
    """The game page: the menu, the levels and the audio."""
    document.title = GAME.title
    overlay = element("menu")
    fit_to_window(engine, element("stage"), overlay)
    debug = parse_debug_options(window.location.search)
    options = AppOptions(
        True,
        document,
        overlay,
        CookieStorage(document, MENU_CONFIG.cookie_max_age_days),
        next_frame,
        # e2e builds have no render loop: the tests step the app (ENG-52).
        not E2E,
        APP_VERSION,
        APP_COMMIT,
        window,
        debug,
        document.body if debug else None,
        None,
        # The perf overlay (F3) in dev and e2e builds only (ENG-111).
        document.body if DEV_BUILD or E2E else None,
        # P13-R03: levels load in steps, behind a loading screen.
        True,
        # P13-R04: shaders compiled while a level loads; not in e2e builds (ENG-52).
        not E2E,
        # P13-R03: the highlighted level is prepared in a worker, and built ahead (D-178).
        True,
        not E2E,
        browser_audio(),
        browser_gamepads(window.navigator),
        window,
        PageVisibility(document, document_hidden),
        start_interval,
        # D-199: the Dev entry of the title screen, with `?dev` in the URL.
        dev_mode(window.location.search),
    )
    app = start_app(engine, GAME, options)
    __pragma__("ifdef", "e2e")
    install_test_api(window, app)
    __pragma__("endif")


def main() -> None:
    """Runs the game page: the WebGL check, the engine, then the app."""
    canvas: Any = document.getElementById("game-canvas")
    if not is_canvas(canvas):
        raise Exception("#game-canvas not found")
    if not has_webgl2(lambda: document.createElement("canvas")):
        show_fatal(GAME.texts.unsupported)
        return
    # Antialiasing on; `adaptToDeviceRatio` off and `stencil` on. e2e builds draw fewer pixels,
    # without multisampling (ENGINE_CONFIG.e2e, D-075).
    e2e = ENGINE_CONFIG.e2e
    antialias = e2e.antialias if E2E else True
    engine = new_engine(canvas, antialias)
    engine.setHardwareScalingLevel(1 / (pixel_ratio() * (e2e.render_scale if E2E else 1)))
    engine.onContextLostObservable.add(
        lambda: show_fatal("The graphics context was lost. Please reload the page.")
    )
    start_game(engine)


def is_canvas(el: Any) -> bool:
    """Whether `el` is an HTMLCanvasElement."""
    __pragma__("js", "{}", "return el instanceof HTMLCanvasElement;")
    return False
