# Copyright (c) 2026 Renaud Guillon
"""Whether a colour belongs to one of the reserved colour families (GFX-READ-04).

The tests check the game's colours against `READABILITY.families` with it.
"""

from core.math.color import ColorFamily, Rgb, hue_saturation


def in_family(color: Rgb, family: ColorFamily) -> bool:
    """Whether `color` is in `family`: its hue in the family's range, saturated enough.

    `from` > `to` wraps past 0; greys and whites belong to no family.
    """
    hue, saturation = hue_saturation(color)
    span = (family["to"] - family["from"] + 360) % 360
    offset = (hue - family["from"] + 360) % 360
    return saturation >= family["minSaturation"] and offset <= span
