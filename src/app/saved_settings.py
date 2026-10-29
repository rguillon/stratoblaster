"""The volume settings kept between visits, ported from `app/saved-settings.ts` (P12-R04, D-010).
Keys are prefixed with the game's id.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from host.key_value_storage import KeyValueStorage  # noqa: E402

__pragma__("noskip")

from app.settings_menu import Volumes  # noqa: E402


class SettingKeys:
    """The storage keys of the two volumes."""

    def __init__(self, music: str, sfx: str) -> None:
        self.music = music
        self.sfx = sfx


def saved_setting_keys(game_id: str) -> SettingKeys:
    return SettingKeys(game_id + "_music_volume", game_id + "_sfx_volume")


def parse_volume(raw: str | None, max_step: int, fallback: int) -> int:
    """A stored volume step: anything but a whole number from 0 to `max_step` reads as
    `fallback`.
    """
    text = "" if raw is None else _trimmed(raw)
    if not _is_step_text(text):
        return fallback
    step = _number_of(text)
    return step if step <= max_step else fallback


def _trimmed(raw: str) -> str:
    __pragma__("js", "{}", "return raw.trim();")
    return ""


def _is_step_text(text: str) -> bool:
    # /^\d{1,2}$/
    __pragma__("js", "{}", "return /^\\d{1,2}$/.test(text);")
    return False


def _number_of(text: str) -> int:
    __pragma__("js", "{}", "return Number(text);")
    return 0


def load_volumes(
    storage: KeyValueStorage, game_id: str, max_step: int, defaults: Volumes
) -> Volumes:
    """The saved volumes, or the defaults where nothing valid is saved (P12-R04)."""
    keys = saved_setting_keys(game_id)
    return Volumes(
        parse_volume(storage.get(keys.music), max_step, defaults.music),
        parse_volume(storage.get(keys.sfx), max_step, defaults.sfx),
    )


def save_volumes(storage: KeyValueStorage, game_id: str, volumes: Volumes) -> None:
    """Saves both volumes (on every change, P12-R04)."""
    keys = saved_setting_keys(game_id)
    storage.set(keys.music, str(volumes.music))
    storage.set(keys.sfx, str(volumes.sfx))
