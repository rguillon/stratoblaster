# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/app/dev_audio_viewer.py` (DEV-MENU-19, DEV-MENU-20).

The dev sounds and music viewers.
"""

from types import SimpleNamespace
from typing import Any

from app.dev_audio_viewer import DevAudioViewer
from app.dev_catalog import DevItem
from config.dev_viewer import DEV_VIEWER_CONFIG as CFG


class FakeAudio:
    """The game's audio: what it was asked to play, and what plays."""

    def __init__(self) -> None:
        self.cues: list[str] = []
        self.requests: list[tuple[str, str | None, str | None]] = []
        self.stops = 0
        self.track: str | None = None
        self.music = SimpleNamespace(position=72.5)

    @property
    def state(self) -> Any:
        return SimpleNamespace(music=self.track)

    def play_cue(self, cue: str) -> str | None:
        self.cues.append(cue)
        return None if cue == "silent" else cue + "-sound"

    def play_music(self, request: Any) -> str | None:
        self.requests.append((request.kind, request.level_id, request.jingle))
        self.track = "level-" + str(request.level_id)
        return self.track

    def stop_cue(self) -> None:
        self.stops += 1


def items(*ids: str) -> list[DevItem]:
    return [DevItem(item_id, item_id, "1-1") for item_id in ids]


def test_dev_menu_19_opening_the_viewer_plays_nothing_moving_or_confirming_plays() -> None:
    audio = FakeAudio()
    viewer = DevAudioViewer(audio, "sounds", items("hit", "fire:guns", "silent"))  # type: ignore[arg-type]
    viewer.show(1, True)
    assert audio.cues == []
    assert viewer.status == ""
    viewer.show(1, True)
    viewer.show(0, True)
    assert audio.cues == ["hit"]
    assert viewer.status == "Playing: hit-sound"
    # Confirm flips the toggle: the same item plays again.
    viewer.show(0, False)
    assert audio.cues == ["hit", "hit"]
    viewer.show(2, False)
    assert viewer.status == ""
    # An index past the list is the last item: nothing changed, nothing plays again.
    viewer.show(9, False)
    assert audio.cues == ["hit", "hit", "silent"]
    viewer.dispose()
    assert audio.stops == 1


def test_dev_menu_20_the_music_viewer_plays_the_request_of_the_item_and_shows_its_time() -> None:
    audio = FakeAudio()
    viewer = DevAudioViewer(audio, "music", items("menu", "level:2-3", "jingle:over"))  # type: ignore[arg-type]
    assert viewer.status == ""
    viewer.show(0, True)
    viewer.show(1, True)
    assert audio.requests == [("level", "2-3", None)]
    assert viewer.status == "Playing: level-2-3 · 1:12"
    viewer.show(2, True)
    assert audio.requests[-1] == ("jingle", None, "over")


def test_dev_menu_19_a_viewer_with_no_item_plays_nothing() -> None:
    audio = FakeAudio()
    viewer = DevAudioViewer(audio, "sounds", [])  # type: ignore[arg-type]
    viewer.show(0, True)
    viewer.show(0, False)
    assert audio.cues == []


def test_dev_menu_19_a_sound_button_held_repeats_its_sound_until_let_go() -> None:
    audio = FakeAudio()
    viewer = DevAudioViewer(audio, "sounds", items("hit", "bomb"))  # type: ignore[arg-type]
    viewer.show(1, True)
    viewer.frame(1.0)
    assert audio.cues == []
    viewer.hold(True)
    viewer.frame(CFG.hold_delay - 0.01)
    assert audio.cues == []
    viewer.frame(0.02)
    assert audio.cues == ["bomb"]
    viewer.frame(CFG.hold_interval / 2)
    assert audio.cues == ["bomb"]
    viewer.frame(CFG.hold_interval / 2)
    assert audio.cues == ["bomb", "bomb"]
    viewer.hold(False)
    viewer.frame(1.0)
    assert audio.cues == ["bomb", "bomb"]
    # Let go by disposing it.
    viewer.hold(True)
    viewer.dispose()
    viewer.frame(1.0)
    assert audio.cues == ["bomb", "bomb"]


def test_dev_menu_20_a_music_button_held_plays_its_track_once() -> None:
    audio = FakeAudio()
    viewer = DevAudioViewer(audio, "music", items("menu", "level:1-1"))  # type: ignore[arg-type]
    viewer.show(0, True)
    viewer.show(1, True)
    viewer.hold(True)
    viewer.frame(5.0)
    assert len(audio.requests) == 1


def test_dev_menu_19_holding_with_no_item_plays_nothing() -> None:
    audio = FakeAudio()
    viewer = DevAudioViewer(audio, "sounds", [])  # type: ignore[arg-type]
    viewer.hold(True)
    viewer.frame(5.0)
    assert audio.cues == []
