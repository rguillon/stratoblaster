"""Unit tests of `src/app/listen_controls.py`."""
# keys go to the level's debug keys first.

from unittest.mock import MagicMock

from app.listen_controls import listen_controls


class FakeKeyEvent(dict):
    """A keyboard event: `code`, and `type` read like a JavaScript object's key."""

    def __init__(self, code: str, kind: str) -> None:
        super().__init__(type=kind)
        self.code = code


def test_p06_r02_with_no_target_nothing_listens_and_stopping_is_harmless() -> None:
    stop = listen_controls(None, MagicMock(), lambda: None)
    stop()


def test_p06_r02_keys_go_to_the_controls_when_no_debug_key_takes_them() -> None:
    controls = MagicMock()
    target = MagicMock()
    listen_controls(target, controls, lambda: None)
    on_key = target.addEventListener.call_args_list[0].args[1]
    on_key(FakeKeyEvent("Space", "keydown"))
    controls.key.assert_called_once_with("Space", True)


def test_p06_r02_a_key_up_is_passed_on_as_released() -> None:
    controls = MagicMock()
    target = MagicMock()
    listen_controls(target, controls, lambda: None)
    on_key = target.addEventListener.call_args_list[1].args[1]
    on_key(FakeKeyEvent("KeyE", "keyup"))
    controls.key.assert_called_once_with("KeyE", False)


def test_p06_r02_a_debug_key_of_the_level_takes_its_keys_first() -> None:
    controls = MagicMock()
    level = MagicMock()
    level.debug_key.return_value = True
    target = MagicMock()
    listen_controls(target, controls, lambda: level)
    on_key = target.addEventListener.call_args_list[0].args[1]
    on_key(FakeKeyEvent("KeyT", "keydown"))
    level.debug_key.assert_called_once_with("KeyT", True)
    controls.key.assert_not_called()


def test_p06_r02_the_debug_key_refusal_falls_through_to_the_controls() -> None:
    controls = MagicMock()
    level = MagicMock()
    level.debug_key.return_value = False
    target = MagicMock()
    listen_controls(target, controls, lambda: level)
    on_key = target.addEventListener.call_args_list[0].args[1]
    on_key(FakeKeyEvent("KeyT", "keydown"))
    controls.key.assert_called_once_with("KeyT", True)


def test_p06_r02_losing_the_focus_lets_go_of_the_controls() -> None:
    controls = MagicMock()
    target = MagicMock()
    listen_controls(target, controls, lambda: None)
    on_blur = target.addEventListener.call_args_list[2].args[1]
    on_blur()
    controls.clear.assert_called_once()


def test_p06_r02_stopping_removes_the_three_listeners() -> None:
    target = MagicMock()
    stop = listen_controls(target, MagicMock(), lambda: None)
    stop()
    assert target.removeEventListener.call_count == 3
    kinds = [call.args[0] for call in target.removeEventListener.call_args_list]
    assert kinds == ["keydown", "keyup", "blur"]
