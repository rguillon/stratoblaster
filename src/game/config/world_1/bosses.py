"""The bosses of each World 1 level (WLD-1-26, BOSS-01)

Each level has a mini boss at the middle of the level and a final boss at its end, by boss kind id.
No new wave starts in the `quietSeconds` before each of them (`quiet_before_boss`). `runout` is how
many seconds of extra ground (at the level's speed) are drawn past the level's end: the scenery gets
ahead of the level during the fights by about each fight's time x its ground speed factor, and the
final fight keeps scrolling (GAME-LEVEL-08).
"""

from game.config.record import record

WORLD_1_BOSSES = record(
    {
        # Each level's mini boss, final boss and runout: LVL-1-1-12, LVL-1-1-13, LVL-1-1-14.
        "1-1": {"mini": "reef-warden", "final": "storm-petrel", "runout": 150},
        # LVL-1-2-12, LVL-1-2-13, LVL-1-2-14.
        "1-2": {"mini": "breakwater", "final": "gull-mothership", "runout": 80},
        # LVL-1-3-12, LVL-1-3-13, LVL-1-3-14.
        "1-3": {"mini": "dust-devil", "final": "mesa-fortress", "runout": 30},
        # LVL-1-4-12, LVL-1-4-13, LVL-1-4-14.
        "1-4": {"mini": "scorpion", "final": "refinery-titan", "runout": 70},
        # LVL-1-5-12, LVL-1-5-13, LVL-1-5-14.
        "1-5": {"mini": "sentinel", "final": "overlord", "runout": 75},
    }
)

# Where the mini boss comes, as a share of the level's length (`mini_boss_at`): the middle of
# every level (GAME-LEVEL-04).
MINI_BOSS_AT = 0.5

# Seconds before each boss without a new wave (`quiet_before_boss`, GAME-LEVEL-05).
QUIET_BEFORE_BOSS = 10
