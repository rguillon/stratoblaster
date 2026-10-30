"""The keys of the enemies page (P05-R11), ported from `app/enemy-viewer-keys.ts`."""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any  # noqa: E402

from ui.enemy_viewer_panel import EnemyViewerSelection  # noqa: E402

__pragma__("noskip")

# The keys of the enemies page (P05-R11).


class ShortcutCounts:
    """How many enemy kinds and player weapons the shortcuts cycle through."""

    def __init__(self, kinds: int, weapons: int) -> None:
        self.kinds = kinds
        self.weapons = weapons


def _wrap(i: int, n: int) -> int:
    """`(i + n) % max(1, n)`: an index cycling through `n` items."""
    return (i + n) % max(1, n)


def _next_kind(s: EnemyViewerSelection, counts: ShortcutCounts) -> dict[str, Any]:
    return {"kind": _wrap(s.kind + 1, counts.kinds)}


def _previous_kind(s: EnemyViewerSelection, counts: ShortcutCounts) -> dict[str, Any]:
    return {"kind": _wrap(s.kind - 1, counts.kinds)}


def _model_view(s: EnemyViewerSelection, counts: ShortcutCounts) -> dict[str, Any]:
    return {"view": "behaviour" if s.view == "model" else "model"}


def _wireframe_view(s: EnemyViewerSelection, counts: ShortcutCounts) -> dict[str, Any]:
    return {"view": "behaviour" if s.view == "wireframe" else "wireframe"}


def _next_weapon(s: EnemyViewerSelection, counts: ShortcutCounts) -> dict[str, Any]:
    return {"weapon": _wrap(s.weapon + 1, counts.weapons), "level": 1}


def _fire(s: EnemyViewerSelection, counts: ShortcutCounts) -> dict[str, Any]:
    return {"fire": not s.fire}


def _pause(s: EnemyViewerSelection, counts: ShortcutCounts) -> dict[str, Any]:
    return {"paused": not s.paused}


def _living(s: EnemyViewerSelection, counts: ShortcutCounts) -> dict[str, Any]:
    return {"living": not s.living}


def _hitbox(s: EnemyViewerSelection, counts: ShortcutCounts) -> dict[str, Any]:
    return {"hitbox": not s.hitbox}


# Keyed by the lower-case key (a dict: a missing key gives None, see `shortcut`).
_CHANGES = {  # type: dict[str, Callable[[EnemyViewerSelection, ShortcutCounts], dict[str, Any]]]
    "n": _next_kind,
    "b": _previous_kind,
    "m": _model_view,
    "v": _wireframe_view,
    "x": _next_weapon,
    "f": _fire,
    "p": _pause,
    "l": _living,
    "h": _hitbox,
}


def shortcut(key: str, s: EnemyViewerSelection, counts: ShortcutCounts) -> dict[str, Any] | None:
    """Shortcuts: N / B next / previous enemy, M model, V wireframe, X weapon, 1-9 level, F, P, L,
    H. Returns the change of the selection, or None for a key that is not one."""
    k = key.lower()
    if len(k) == 1 and k >= "1" and k <= "9":
        return {"level": int(k)}
    builder = _CHANGES.get(k)
    if builder is None:
        return None
    return builder(s, counts)


# In the model and wireframe views, ← / → (by key position) show the previous / next enemy.
SWITCH_KEYS = {"ArrowLeft": -1, "ArrowRight": 1}

HELP = (
    "Move: arrows / WASD · N / B: next / previous enemy · M: model · V: wireframe (← / →: switch "
    "enemy) · X: weapon · 1-5: level · F: fire · P: pause · L: motion · H: hitbox"
)


def listen_to_keys(target: Any, viewer: Any) -> Callable[[], None]:
    """Sends `target`'s key presses to `viewer` (and lets go of held keys when it loses focus).
    Returns what stops listening. `target` may be None (no keyboard)."""

    def on_key(event: Any) -> None:
        viewer.key(event.key, event.code, event["type"] == "keydown")

    def on_blur(_event: Any) -> None:
        viewer.held.clear()

    if target:
        target.addEventListener("keydown", on_key)
        target.addEventListener("keyup", on_key)
        target.addEventListener("blur", on_blur)

    def stop() -> None:
        if target:
            target.removeEventListener("keydown", on_key)
            target.removeEventListener("keyup", on_key)
            target.removeEventListener("blur", on_blur)

    return stop
