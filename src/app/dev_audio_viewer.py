# Copyright (c) 2026 Renaud Guillon
"""The dev sounds and music viewers (DEV-MENU-19, DEV-MENU-20): the item picked plays.

A viewer of the dev menu with no scene: a button per sound or per track, and the one picked plays
as in game, through the game's audio. Opening the viewer plays nothing: a sound or a track plays
when the menu moves to another item, or when the item shown is confirmed again (the flow flips
its toggle). The status line names what plays; the music viewer adds the track's time.
"""

from app.dev_catalog import music_request
from app.dev_viewer import clock_text
from config.dev_viewer import DEV_MUSIC_VIEWER
from config.dev_viewer import DEV_VIEWER_CONFIG as CFG

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from app.dev_catalog import DevItem
from app.game_audio import GameAudio

# __pragma__ ("noskip")


class DevAudioViewer:
    """One audio viewer (`viewer`, one of `DEV_AUDIO_VIEWERS`) and its `items`.

    They play through `audio`, the game's.
    """

    def __init__(self, audio: GameAudio, viewer: str, items: list[DevItem]) -> None:
        self._audio = audio
        self.viewer = viewer
        self._items = items
        # The item and toggle the menu showed last; None before the viewer is shown.
        self._index = 0
        self._toggle: bool | None = None
        # The name of the last sound played, if any (the sounds viewer's status).
        self._played: str | None = None

    @property
    def status(self) -> str:
        """The status line (DEV-MENU-05): what plays, with its time for the music."""
        if self.viewer == DEV_MUSIC_VIEWER:
            track = self._audio.state.music
            if track is None:
                return ""
            return CFG.texts.playing + track + " · " + clock_text(self._audio.music.position)
        return CFG.texts.playing + self._played if self._played is not None else ""

    def show(self, index: int, toggle: bool) -> None:
        """Show the item the menu picked, and its toggle; play it when either changed."""
        if len(self._items) == 0:
            return
        index = max(0, min(index, len(self._items) - 1))
        changed = self._toggle is not None and (index != self._index or toggle != self._toggle)
        self._index = index
        self._toggle = toggle
        if changed:
            self._play(self._items[index])

    def _play(self, item: DevItem) -> None:
        if self.viewer == DEV_MUSIC_VIEWER:
            self._audio.play_music(music_request(item.id))
        else:
            self._played = self._audio.play_cue(item.id)

    def dispose(self) -> None:
        """Stop the looping sound played, if any; the menus' music takes over on its own."""
        self._audio.stop_cue()
