"""Bootstrap only (ENG-10), ported from `main.ts`: create the engine and start the app.

`index.html` calls `main()` once the page has loaded. Each page of the game (the game itself and
the debug viewers) is chosen by its path (`app/route.py`).

Build-time flags of the TypeScript build (`__E2E__`, `import.meta.env.DEV`) are constants here:
the Python port has no e2e build yet (ENG-52), and the perf overlay (ENG-111) is off.
"""

from org.transcrypt.stubs.browser import __pragma__, document, window

from app.debug_options import parse_debug_options
from app.page_audio import AudioOptions, PageVisibility
from app.route import redirect_of, resolve_route
from app.start_app import AppOptions, start_app
from app.start_boss_viewer import start_boss_viewer
from app.start_enemy_viewer import EnemyViewerOptions, start_enemy_viewer
from app.start_prop_viewer import PropViewerOptions, start_prop_viewer
from app.start_ship_viewer import ShipCaptions, ShipViewerOptions, start_ship_viewer
from app.start_shot_viewer import ShotViewerOptions, start_shot_viewer
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

E2E = False
DEV_BUILD = False
# The version and short commit hash on the title screen (ENG-83): the Makefile does not inject
# them yet, so they are fixed here.
APP_VERSION = "0.0.0"
APP_COMMIT = "unknown"


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


def fit_canvas_stage(engine: Any) -> None:
    """Keeps the canvas box at the game's aspect ratio, centred in the window."""
    stage = element("stage")

    def fit() -> None:
        box = fit_stage(window.innerWidth, window.innerHeight, GAME.screen)
        stage.style.left = str(box.left) + "px"
        stage.style.top = str(box.top) + "px"
        stage.style.width = str(box.width) + "px"
        stage.style.height = str(box.height) + "px"
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
        # P13-R03: the worker is off for now (D-177): level data cannot cross the worker
        # boundary yet, so the grounds are generated on the main thread.
        False,
        not E2E,
        browser_audio(),
        browser_gamepads(window.navigator),
        window,
        PageVisibility(document, document_hidden),
        start_interval,
    )
    start_app(engine, GAME, options)


def start_ship_viewer_page(engine: Any) -> None:
    """The player ships page (P01 viewers)."""
    window.addEventListener("resize", lambda: engine.resize())  # noqa: PLW0108 (keeps the receiver)
    start_ship_viewer(
        engine,
        GAME,
        ShipViewerOptions(True, ShipCaptions(document, document.body), None),
    )


def start_shot_viewer_page(engine: Any) -> None:
    """The player shots page."""
    fit_canvas_stage(engine)
    start_shot_viewer(
        engine,
        GAME,
        ShotViewerOptions(
            True,
            document,
            element("panel"),
            document.body,
            window,
            None,
            not E2E,
        ),
    )


def start_enemy_viewer_page(engine: Any) -> None:
    """The enemies page."""
    fit_canvas_stage(engine)
    start_enemy_viewer(
        engine,
        GAME,
        EnemyViewerOptions(True, document, element("panel"), document.body, window, None, not E2E),
    )


def start_boss_viewer_page(engine: Any) -> None:
    """The bosses page."""
    fit_canvas_stage(engine)
    start_boss_viewer(
        engine,
        GAME,
        EnemyViewerOptions(True, document, element("panel"), document.body, window, None, not E2E),
    )


def start_prop_viewer_page(engine: Any) -> None:
    """The props page."""
    window.addEventListener("resize", lambda: engine.resize())  # noqa: PLW0108 (keeps the receiver)
    start_prop_viewer(
        engine,
        GAME,
        PropViewerOptions(True, document, element("panel"), window, not E2E),
    )


def start_page(route: str, engine: Any) -> None:
    """Starts the page `route` names (the TypeScript `START` table)."""
    if route == "game":
        start_game(engine)
    elif route == "player-ship-viewer":
        start_ship_viewer_page(engine)
    elif route == "player-shots-viewer":
        start_shot_viewer_page(engine)
    elif route == "enemy-viewer":
        start_enemy_viewer_page(engine)
    elif route == "boss-viewer":
        start_boss_viewer_page(engine)
    else:
        start_prop_viewer_page(engine)


def main() -> None:
    """Runs the page: redirects, the WebGL check, the engine, then the page's app."""
    redirect = redirect_of(window.location.pathname)
    if redirect:
        window.location.replace(redirect + window.location.search)
        return
    canvas: Any = document.getElementById("game-canvas")
    if not is_canvas(canvas):
        raise Exception("#game-canvas not found")
    if not has_webgl2(lambda: document.createElement("canvas")):
        show_fatal(GAME.texts.unsupported)
        return
    antialias = True
    # Antialiasing on; `adaptToDeviceRatio` off and `stencil` on, as in the TypeScript (render/).
    engine = new_engine(canvas, antialias)
    engine.setHardwareScalingLevel(1 / pixel_ratio())
    engine.onContextLostObservable.add(
        lambda: show_fatal("The graphics context was lost. Please reload the page.")
    )
    start_page(resolve_route(window.location.pathname), engine)


def is_canvas(el: Any) -> bool:
    """Whether `el` is an HTMLCanvasElement."""
    __pragma__("js", "{}", "return el instanceof HTMLCanvasElement;")
    return False
