# Copyright (c) 2026 Renaud Guillon
"""Where each array of a round of play lies in the shared rollout file, in pure Python (D-301).

The learner and the inference server (CPython) see the file as numpy arrays (`rollout.py`); the
workers (PyPy, no numpy) write into it through `memoryview`s of an `mmap` (`play_worker.py`). Both
work out the same layout from here. Each array is `(name, format, shape)`, `format` a `struct`
code: `e` float16, `f` float32, `q` int64, `?` bool.
"""

from ai.sight import FIELD_COLS, FIELD_ROWS, FOVEA_SIZE, N_CHANNELS, N_STATE

ITEM_SIZE = {"e": 2, "f": 4, "q": 8, "?": 1}
ALIGN = 64

# What a rollout holds for each decision of each episode: (T, E, *shape).
STEP_ARRAYS: tuple[tuple[str, str, tuple[int, ...]], ...] = (
    ("field", "e", (N_CHANNELS, FIELD_ROWS, FIELD_COLS)),
    ("fovea", "e", (N_CHANNELS, FOVEA_SIZE, FOVEA_SIZE)),
    ("state", "f", (N_STATE,)),
    ("actions", "q", (3,)),
    ("log_probs", "f", ()),
    ("values", "f", ()),
    ("rewards", "f", ()),
    ("dones", "?", ()),
    ("starts", "?", ()),
)

# What a rollout holds for each episode after its last decision, for the inference server to
# work out the value of the round's end from (D-298): (E, *shape).
NEXT_ARRAYS: tuple[tuple[str, str, tuple[int, ...]], ...] = (
    ("next_field", "e", (N_CHANNELS, FIELD_ROWS, FIELD_COLS)),
    ("next_fovea", "e", (N_CHANNELS, FOVEA_SIZE, FOVEA_SIZE)),
    ("next_state", "f", (N_STATE,)),
    ("next_starts", "?", ()),
)


def _count(shape: tuple[int, ...]) -> int:
    count = 1
    for size in shape:
        count *= size
    return count


class Layout:
    """The arrays of a rollout of `steps` decisions of `envs` episodes, and where each starts.

    `arrays`: name -> (format, full shape, byte offset); `size`: the file's size in bytes.
    """

    def __init__(self, steps: int, envs: int, hidden: int) -> None:
        self.steps = steps
        self.envs = envs
        self.hidden = hidden
        entries: list[tuple[str, str, tuple[int, ...]]] = [
            (name, fmt, (steps, envs, *shape)) for name, fmt, shape in STEP_ARRAYS
        ]
        entries.append(("memories", "f", (steps, envs, hidden)))
        entries.append(("last_values", "f", (envs,)))
        entries.extend((name, fmt, (envs, *shape)) for name, fmt, shape in NEXT_ARRAYS)
        self.arrays: dict[str, tuple[str, tuple[int, ...], int]] = {}
        size = 0
        for name, fmt, shape in entries:
            self.arrays[name] = (fmt, shape, size)
            nbytes = _count(shape) * ITEM_SIZE[fmt]
            size += (nbytes + ALIGN - 1) // ALIGN * ALIGN
        self.size = size

    def nbytes(self, name: str) -> int:
        fmt, shape, _ = self.arrays[name]
        return _count(shape) * ITEM_SIZE[fmt]

    def index(self, name: str, *at: int) -> int:
        """Return the item index (in units of the array's format) of `at`'s first item.

        `at` indexes the leading dimensions (`(t, e)` of a step array, `(e,)` of a next one).
        """
        fmt, shape, offset = self.arrays[name]
        flat = 0
        for i, value in enumerate(at):
            flat = flat * shape[i] + value
        return offset // ITEM_SIZE[fmt] + flat * _count(shape[len(at) :])
