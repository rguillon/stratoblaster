"""The groups of a dev viewer's items (D-202): runs of items of the same group, which Up and Down
jump between and the caption counts in.
"""


def group_starts(groups: list[str]) -> list[int]:
    """Where each run of items of the same group starts (D-202): `groups` is each item's group."""
    starts: list[int] = []
    for i in range(len(groups)):
        if i == 0 or groups[i] != groups[i - 1]:
            starts.append(i)
    return starts


def group_of(starts: list[int], index: int) -> int:
    """Which group (index into `starts`) item `index` is in."""
    found = 0
    for g in range(len(starts)):
        if starts[g] <= index:
            found = g
    return found


def group_jump(starts: list[int], index: int, step: int) -> int:
    """The first item of the group `step` (1 or -1) groups from item `index`'s, round the list."""
    count = len(starts)
    return starts[(group_of(starts, index) + step + count) % count]
