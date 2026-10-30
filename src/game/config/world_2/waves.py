"""The wave scripts of World 2 (P08-R08, R09), ported from `config/world-2/waves.ts`.

Each level cycles through its own phrases: a beat every `gap` seconds (from `gap[0]` at the start to
`gap[1]` at the end, so the level fills up as it goes), each beat the next phrase of the cycle, its
groups growing by `growth` over the level (so the second half carries more enemy HP). Beats are
written in seconds, as World 1's, and turned into distances at the level's ground speed; the World 1
filler (D-051) fills the lulls. A phrase is `[kind, groups, seconds between groups, side, position
(0..1), spread]`.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.record import concat, record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


# A phrase is `[kind, groups, seconds between groups, side, position, spread]`.
PHRASE_LENGTH = 5


def compose_beats(plan: Any) -> list[Any]:
    """The beats of `plan`, deterministic."""
    beats = []
    span = plan["to"] - plan["from"]
    t = plan["from"]
    i = 0
    while t <= plan["to"] and len(plan["phrases"]) > 0:
        phrase = plan["phrases"][i % len(plan["phrases"])]
        kind = phrase[0]
        count = phrase[1]
        interval = phrase[2]
        side = phrase[3]
        position = phrase[4]
        has_spread = len(phrase) > PHRASE_LENGTH
        grown = max(1, math.floor(count * (1 + (plan["growth"] * (t - plan["from"])) / span) + 0.5))
        head = [math.floor(t * 10 + 0.5) / 10, kind, grown, interval, side, position]
        if has_spread:
            beats.append(concat(head, [phrase[5]]))
        else:
            beats.append(head)
        t = t + (plan["gap"][0] + ((plan["gap"][1] - plan["gap"][0]) * (t - plan["from"])) / span)
        i = i + 1
    return beats


# 2-1: Gnats, Hornets, Scouts, Strafers and Weavers over the dunes (P08-R08).
PLAN_2_1 = record(
    {
        "from": 4,
        "to": 292,
        "gap": [6.5, 4.8],
        "growth": 0.6,
        "phrases": [
            ["scout", 3, 1.2, "top", 0.25, 0.25],
            ["weaver", 3, 1.4, "top", 0.3, 0.2],
            ["strafer", 2, 1.6, "left", 0.8],
            ["hornet", 4, 0.8, "top", 0.15, 0.23],
            ["gnat", 2, 2, "top", 0.3, 0.4],
            ["scout", 4, 1, "top", 0.2, 0.2],
            ["strafer", 2, 1.6, "right", 0.78],
            ["weaver", 3, 1.2, "top", 0.6, -0.2],
        ],
    }
)

# 2-2: the 2-1 kinds plus Splitters and Lancers, over the mines and mesas.
PLAN_2_2 = record(
    {
        "from": 4,
        "to": 292,
        "gap": [5.4, 3.9],
        "growth": 0.6,
        "phrases": [
            ["scout", 3, 1.2, "top", 0.25, 0.25],
            ["splitter", 2, 2, "top", 0.3, 0.4],
            ["weaver", 3, 1.2, "top", 0.3, 0.2],
            ["lancer", 2, 2.5, "top", 0.25, 0.5],
            ["strafer", 2, 1.5, "left", 0.8],
            ["hornet", 4, 0.8, "top", 0.15, 0.23],
            ["splitter", 2, 2, "top", 0.7, -0.4],
            ["gnat", 2, 2, "top", 0.3, 0.4],
            ["lancer", 2, 2, "top", 0.3, 0.4],
            ["strafer", 2, 1.5, "right", 0.78],
        ],
    }
)

# 2-3: every kind, with Carrier and Spinner groups over the tundra.
PLAN_2_3 = record(
    {
        "from": 4,
        "to": 292,
        "gap": [6.6, 5],
        "growth": 0.6,
        "phrases": [
            ["spinner", 2, 2.5, "top", 0.3, 0.4],
            ["scout", 4, 1, "top", 0.15, 0.23],
            ["carrier", 1, 0, "top", 0.5],
            ["weaver", 3, 1.2, "top", 0.3, 0.2],
            ["spinner", 2, 2.5, "top", 0.7, -0.4],
            ["splitter", 2, 2, "top", 0.3, 0.4],
            ["lancer", 2, 2, "top", 0.25, 0.5],
            ["spinner", 1, 0, "top", 0.5],
            ["rocketeer", 1, 0, "top", 0.5],
            ["strafer", 2, 1.5, "left", 0.8],
            ["hornet", 4, 0.7, "top", 0.1, 0.2],
            ["bulwark", 1, 0, "top", 0.5],
            ["gnat", 2, 2, "top", 0.3, 0.4],
        ],
    }
)

# 2-4: every kind, with Rocketeers and Bulwarks in the blizzard.
PLAN_2_4 = record(
    {
        "from": 4,
        "to": 292,
        "gap": [4.8, 3.4],
        "growth": 0.6,
        "phrases": [
            ["rocketeer", 2, 2.5, "top", 0.3, 0.4],
            ["scout", 4, 1, "top", 0.15, 0.23],
            ["bulwark", 1, 0, "top", 0.5],
            ["weaver", 3, 1.2, "top", 0.3, 0.2],
            ["rocketeer", 2, 2, "top", 0.7, -0.4],
            ["spinner", 2, 2.5, "top", 0.3, 0.4],
            ["bulwark", 1, 0, "top", 0.35],
            ["lancer", 2, 2, "top", 0.25, 0.5],
            ["splitter", 2, 2, "top", 0.3, 0.4],
            ["carrier", 1, 0, "top", 0.5],
            ["strafer", 3, 1.5, "right", 0.8],
            ["hornet", 5, 0.7, "top", 0.1, 0.2],
            ["gnat", 2, 2, "top", 0.3, 0.4],
        ],
    }
)

# 2-5: every kind, the heaviest mixes: Bulwarks and Carriers together.
PLAN_2_5 = record(
    {
        "from": 4,
        "to": 292,
        "gap": [5, 3.6],
        "growth": 0.6,
        "phrases": [
            ["bulwark", 1, 0, "top", 0.35],
            ["carrier", 1, 0, "top", 0.65],
            ["scout", 4, 1, "top", 0.15, 0.23],
            ["rocketeer", 2, 2, "top", 0.3, 0.4],
            ["lancer", 3, 1.5, "top", 0.2, 0.3],
            ["spinner", 2, 2.5, "top", 0.7, -0.4],
            ["bulwark", 2, 3, "top", 0.3, 0.4],
            ["weaver", 4, 1, "top", 0.2, 0.2],
            ["splitter", 3, 1.5, "top", 0.2, 0.3],
            ["carrier", 1, 0, "top", 0.4],
            ["strafer", 3, 1.5, "left", 0.8],
            ["hornet", 5, 0.6, "top", 0.1, 0.2],
            ["gnat", 3, 1.5, "top", 0.2, 0.3],
        ],
    }
)

# The filler of each level (D-051), from the kinds the level may use (P08-R08).
WORLD_2_FILLERS = record(
    {
        "2-1": {"kinds": ["hornet", "scout", "gnat", "weaver"], "maxGap": [3.4, 2.3]},
        "2-2": {"kinds": ["hornet", "gnat", "weaver", "scout", "splitter"], "maxGap": [3.2, 2.1]},
        "2-3": {
            "kinds": ["gnat", "weaver", "hornet", "scout", "splitter", "spinner"],
            "maxGap": [3, 2],
        },
        "2-4": {
            "kinds": ["gnat", "weaver", "hornet", "scout", "splitter", "spinner"],
            "maxGap": [2.9, 1.8],
        },
        "2-5": {
            "kinds": ["gnat", "weaver", "hornet", "scout", "splitter", "spinner"],
            "maxGap": [2.8, 1.6],
        },
    }
)
