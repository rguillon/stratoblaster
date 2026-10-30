"""Unit tests of `src/app/dev_groups.py` (D-202: a dev viewer's items in groups)."""

from app.dev_groups import group_jump, group_of, group_starts


def test_d202_each_run_of_one_group_starts_a_group() -> None:
    assert group_starts(["a", "a", "b", "c", "c"]) == [0, 2, 3]
    assert group_starts([]) == []
    assert group_starts(["", ""]) == [0]


def test_d202_an_item_is_in_the_last_group_started_at_or_before_it() -> None:
    starts = [0, 2, 3]
    assert [group_of(starts, i) for i in range(5)] == [0, 0, 1, 2, 2]


def test_d202_a_jump_goes_to_the_first_item_of_the_next_or_previous_group_round_the_list() -> None:
    starts = [0, 2, 3]
    assert group_jump(starts, 1, 1) == 2
    assert group_jump(starts, 4, 1) == 0
    assert group_jump(starts, 1, -1) == 3
    assert group_jump(starts, 4, -1) == 2
