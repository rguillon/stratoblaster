# Copyright (c) 2026 Renaud Guillon
"""The groups of a dev viewer's items (DEV-MENU-06, D-202): runs of items of the same group.

Which Up and Down jump between and the caption counts in.
"""


def group_starts(groups: list[str]) -> list[int]:
    """Where each run of items of the same group starts (D-202): `groups` is each item's group."""
    return [i for i in range(len(groups)) if i == 0 or groups[i] != groups[i - 1]]


def group_of(starts: list[int], index: int) -> int:
    """Which group (index into `starts`) item `index` is in."""
    found = 0
    for g in range(len(starts)):
        if starts[g] <= index:
            found = g
    return found


def group_jump(starts: list[int], index: int, step: int) -> int:
    """Return the first item of the group `step` groups from item `index`'s, round the list.

    `step` is 1 or -1.
    """
    count = len(starts)
    return starts[(group_of(starts, index) + step + count) % count]
