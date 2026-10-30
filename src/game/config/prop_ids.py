"""Ids of the props the worlds share, ported from `config/prop-ids.ts`.

Trees, bushes, an antenna mast and two homes (P04-R04).
"""

from game.config.record import record

PROP_IDS = record(
    {
        "antenna": "antenna-mast",
        "cubeHome": "cube-home",
        "domeHome": "dome-home",
        "deadTree": "dead-tree",
        "forkedTree": "forked-tree",
        "conifer": "conifer",
        "broadleaf": "broadleaf-tree",
        "bush": "bush",
    }
)
