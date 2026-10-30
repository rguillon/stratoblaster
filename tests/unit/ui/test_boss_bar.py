"""Unit tests of `src/ui/boss_bar.py`."""

import pytest
from helpers.dom import FakeDocument

from ui.boss_bar import BossBar, BossBarFrame


def make_bar() -> tuple[BossBar, FakeDocument]:
    doc = FakeDocument()
    return BossBar(doc, doc.createElement("div")), doc


def test_p07_r02_the_bar_is_hidden_while_no_boss_is_fought() -> None:
    bar, _ = make_bar()
    assert bar.root.hidden is True
    bar.update(None)
    assert bar.root.hidden is True


def test_p07_r02_the_bar_shows_the_boss_kind_name_and_health() -> None:
    bar, _ = make_bar()
    bar.update(BossBarFrame("Warden", "BOSS", 0.5, []))
    assert bar.root.hidden is False
    assert bar.root.querySelector(".boss-rank").textContent == "BOSS"
    assert bar.root.querySelector(".boss-name").textContent == "Warden"
    assert bar.root.querySelector(".boss-fill").style.height == "50.0%"


def test_p07_r02_each_part_of_the_boss_has_a_notch_at_its_share() -> None:
    bar, _ = make_bar()
    bar.update(BossBarFrame("Warden", "MINI BOSS", 0.8, [0.25, 0.5]))
    notches = bar.root.querySelectorAll(".boss-notch")
    assert [notch.style.bottom for notch in notches] == ["25.0%", "50.0%"]


def test_p07_r02_the_notches_are_rebuilt_only_when_they_move() -> None:
    bar, _ = make_bar()
    bar.update(BossBarFrame("Warden", "BOSS", 0.8, [0.25]))
    first = bar.root.querySelector(".boss-notch")
    bar.update(BossBarFrame("Warden", "BOSS", 0.7, [0.25]))
    assert bar.root.querySelector(".boss-notch") is first
    bar.update(BossBarFrame("Warden", "BOSS", 0.6, [0.5]))
    assert bar.root.querySelector(".boss-notch") is not first
    assert bar.root.querySelector(".boss-notch").style.bottom == "50.0%"


@pytest.mark.xfail(
    strict=True,
    reason="BUG: BossBar.update returns early when the name and share are unchanged, so a "
    "notch that moves on its own is not drawn (src/ui/boss_bar.py)",
)
def test_p07_r02_a_notch_that_moves_alone_is_drawn() -> None:
    bar, _ = make_bar()
    bar.update(BossBarFrame("Warden", "BOSS", 0.7, [0.25]))
    bar.update(BossBarFrame("Warden", "BOSS", 0.7, [0.5]))
    assert bar.root.querySelector(".boss-notch").style.bottom == "50.0%"


def test_p07_r02_the_share_is_kept_between_zero_and_one() -> None:
    bar, _ = make_bar()
    bar.update(BossBarFrame("Warden", "BOSS", 1.7, []))
    assert bar.root.querySelector(".boss-fill").style.height == "100.0%"


def test_p07_r02_an_unchanged_frame_does_not_touch_the_page() -> None:
    bar, _ = make_bar()
    bar.update(BossBarFrame("Warden", "BOSS", 0.5, []))
    name = bar.root.querySelector(".boss-name")
    name.textContent = "edited elsewhere"
    bar.update(BossBarFrame("Warden", "BOSS", 0.5, []))
    assert name.textContent == "edited elsewhere"


def test_p07_r02_the_bar_hides_again_when_the_boss_is_gone() -> None:
    bar, _ = make_bar()
    bar.update(BossBarFrame("Warden", "BOSS", 0.5, []))
    bar.update(None)
    assert bar.root.hidden is True
