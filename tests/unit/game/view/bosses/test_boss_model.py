"""Unit tests of `src/game/view/bosses/boss_model.py`."""

from types import SimpleNamespace

from core.entities.boss import Boss
from game.config.boss_look import BOSS_LOOK
from game.view.bosses import boss_model
from game.view.bosses.boss_model import FlashGroup, _field, _point_of, strobe


def test_field_reads_a_present_key_and_is_none_for_a_missing_one_or_no_object():
    assert _field({"a": 1}, "a") == 1
    assert _field({"a": 1}, "b") is None
    assert _field(None, "a") is None


def test_point_of_is_a_playfield_point_in_model_space_with_an_optional_height():
    assert _point_of([3, 4]) == [-3, 0, -4]
    assert _point_of([3, 4, 2]) == [-3, 2, -4]


def test_strobe_of_a_plain_stand_in_is_its_own_charge():
    assert strobe(SimpleNamespace(charge=0.7)) == 0.7


class _FakeBoss(Boss):
    """A boss whose lights only read its pause, rage and charge (no stats are needed for them)."""

    def __init__(self, pause: float = 0.0, rage: float = 0.0, charge: float = 0.25) -> None:
        self.pause = pause
        self.rage = rage
        self.charge = charge


def _boss(pause=0.0, rage=0.0, charge=0.25):
    return _FakeBoss(pause, rage, charge)


def test_p07_r04_a_calm_boss_shows_its_own_charge():
    boss = _boss(charge=0.25)
    assert strobe(boss) == 0.25


def test_stage_change_strobes_the_lights_at_the_stage_strobe_rate():
    hz = BOSS_LOOK.stageStrobeHz
    boss = _boss(pause=1.0)
    # The light is on in the first half of each strobe period and off in the second.
    on = strobe(boss)
    boss.pause = 1.5 / (hz * 2)
    off = strobe(boss)
    assert on == 1
    assert off == 0


def test_rage_flickers_between_full_and_the_dim_level():
    hz = BOSS_LOOK.rageFlicker.hz
    dim = BOSS_LOOK.rageFlicker.dim
    boss = _boss(rage=0.0)
    boss.rage = 0.0 + 1e-9  # angry, just starting its cycle: full
    assert strobe(boss) == 1
    boss.rage = 1.5 / (hz * 2)  # the second half of a cycle: dimmed
    assert strobe(boss) == dim


def test_flash_group_lights_its_body_hulls_white_for_a_moment_after_a_hit(monkeypatch):
    body = SimpleNamespace(material="body-mat", useVertexColors=True)
    other = SimpleNamespace(material="other", useVertexColors=True)
    body_material = SimpleNamespace(name="enemy-hull")
    other_material = SimpleNamespace(name="charge")
    body.material = body_material
    other.material = other_material
    monkeypatch.setattr(boss_model, "child_meshes", lambda root, direct: [body, other])
    monkeypatch.setattr(boss_model, "node_name", lambda node: node.name)
    model = SimpleNamespace(root=object())
    group = FlashGroup(model, flash="FLASH")
    group.show(since_hit=0.0)
    assert body.material == "FLASH" and body.useVertexColors is False
    # Only the body's hulls are flashed.
    assert other.material is other_material
    group.show(since_hit=BOSS_LOOK.flash.seconds + 1)
    assert body.material is body_material and body.useVertexColors is True
