"""What keeps the playfield readable (phase 14)

Each kind of gameplay object has a colour family no other uses (P14-R02); the ground is dimmed
under a dark veil (P14-R01); and the thresholds the readability check measures (P14-R03..R08).
Hues in degrees, colours linear RGB 0..1, sizes in logical pixels, times in seconds.
"""

from game.config.record import record

READABILITY = record(
    {
        # P14-R02 (reviewer, 2026-10-27): one hue range per kind of object, none overlapping. Pale
        # colours (sand, beige; under `minSaturation`) read as no colour and belong to none.
        # Reviewer, 2026-11-01 (D-231): enemies and bosses bright yellow or bright green, no more
        # pink (were violet, magenta and blood red); the bonuses violet (were green) and the enemy
        # shots orange to amber (were orange to yellow), to keep clear of them.
        "families": {
            # Player ship accents and player shots: cyan to ice blue (GD-61).
            "player": {"from": 180, "to": 235, "minSaturation": 0.5},
            # Enemy and boss neon: bright yellow or bright green (`enemyHues`).
            "enemy": {"from": 60, "to": 140, "minSaturation": 0.5},
            # Enemy bullets, missiles and lasers: orange to amber, round a white-hot core.
            "enemyShot": {"from": 15, "to": 48, "minSaturation": 0.5},
            # Bonuses: blue violet to purple; their shapes tell the kinds apart.
            "pickup": {"from": 250, "to": 295, "minSaturation": 0.5},
        },
        # D-231 (reviewer, 2026-11-01: "bright shade of yellow OR bright shade of green", no khaki
        # in between): every enemy's and boss's neon takes the nearest of these hues (degrees),
        # keeping its brightness: red, orange and magenta neon turns yellow, cyan and blue green.
        "enemyHues": [60, 125],
        # D-231 (reviewer, 2026-11-01: no khaki, no pink): the shades of the enemies' bodies (hull
        # and flesh) keep their colour in this hue window (moss greens, teals, ice blues); out of
        # it (yellows, olives, browns, reds, pinks) they are greyed to `maxSaturation` at most, so
        # an enemy's yellow or green is its lights'.
        "enemyBody": {"from": 100, "to": 250, "maxSaturation": 0.1},
        # P14-R01, per world: the share of their colour the ground, the shores, the water, the
        # roads and the props keep (reviewer, 2026-10-28: in place of a dark veil over the
        # background).
        "tones": {
            "world1": 0.55,
            # Snow and ice: the brightest ground.
            "world2": 0.45,
            "world3": 0.45,
            # D-162: lower, as the props stretched to whole tiles cover more of the ground.
            "world4": 0.55,
        },
        # P14-R01: the ground's brightest pixels (relative luminance), but for a share of the
        # screen.
        "backgroundMaxLuminance": 0.35,
        "backgroundBrightPixelBudget": 0.02,
        # P14-R03, R04: contrast ratio of a ship's outline with the ground round it.
        "minObjectContrast": 3,
        # P14-R05, R06: contrast ratio of an enemy bullet's core with what is round it.
        "minBulletContrast": 4.5,
        # P14-R05: an enemy bullet's smallest drawn diameter.
        "minEnemyBulletSize": 6,
        # P14-R06: the player shots' strength (additive opacity).
        "playerShotMaxOpacity": 0.7,
        # P14-R08: the contrast a player shot keeps with the ground, toned down (R06 sets no
        # contrast for them: they only must still show).
        "minPlayerShotContrast": 2,
        # P14-R07: an explosion's largest share of the screen, and how long it may last.
        "effectMaxScreenShare": 0.15,
        "effectMaxDuration": 0.6,
        # P14-R03: the player ship's glowing edge trim, its built-in rim light (no hitbox marker:
        # reviewer, 2026-10-30, D-194): colour, and width and offset out from the edges in logical
        # pixels.
        "playerTrim": {"color": [0.3, 0.9, 1], "width": 0.9, "offset": 0.1},
        # P14-R04: the enemies' trim is their neon colour `whiten` of the way to white (set for the
        # violet and magenta neon of before D-231, too dark alone on a dark ground), times
        # `strength` (above 1: the trim goes through the scene's tone mapping, which the rim it
        # replaces skipped); width and offset in logical pixels.
        "enemyTrim": {"whiten": 0.25, "strength": 2.6, "width": 1.4, "offset": 0.1},
        # Reviewer, 2026-10-28: the light on the ships', enemies' and bosses' metal, as factors on
        # the direct light (sun, lamps) and on the sky's reflections, so they stand out brighter.
        "hullLight": {"direct": 1.8, "environment": 1.8},
        # The enemy missiles' rim (P14-R05): width in logical pixels, and strength.
        "outline": {"width": 0.9, "intensity": 1.2},
    }
)
