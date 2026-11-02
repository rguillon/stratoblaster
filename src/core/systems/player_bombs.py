# Copyright (c) 2026 Renaud Guillon
"""The player's bombs (`specs/gameplay/bombs.md`)."""

INFINITY = float("Infinity")


class BombRules:
    """The bomb rules.

    `start`: bombs at the start of a level, after a Continue, and the least after a lost life.
    `damage`: damage each enemy and boss piece on screen takes, once, when a bomb goes off.
    `seconds`: seconds a bomb lasts: no other bomb can go off meanwhile, the enemy shots keep
    being cleared and the player cannot be hurt.
    `max`: most bombs the player can have with bomb bonuses (GAME-BONUS-10); no limit when None.
    """

    def __init__(
        self,
        start: float,
        damage: float,
        seconds: float,
        max_bombs: float | None = None,
    ) -> None:
        self.start = start
        self.damage = damage
        self.seconds = seconds
        self.max = max_bombs


class ActiveBomb:
    """A bomb going off, for the visuals.

    Where the ship was when it went off, and how long it has been going off (`age`) out of
    `seconds`.
    """

    def __init__(self, x: float, y: float, age: float, seconds: float) -> None:
        self.x = x
        self.y = y
        self.age = age
        self.seconds = seconds


class _BombState:
    """The bomb going off, while it does."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.age = 0.0


class PlayerBombs:
    """The bombs left (GAME-BOMB-01) and the bomb going off.

    One goes off per press while some are left and none is active (GAME-BOMB-03); lives lost top
    them back up to the starting count (GAME-BOMB-02). Pure.
    """

    def __init__(self, rules: BombRules, count: float | None = None) -> None:
        """Start with `count` bombs: the rules' start, or those kept from the level before."""
        self.rules = rules
        self.count = rules.start if count is None else count
        self._active: _BombState | None = None
        # Bombs gone off since the level started.
        self.fired = 0

    @property
    def active(self) -> ActiveBomb | None:
        """The bomb going off, if any."""
        bomb = self._active
        if bomb is None:
            return None
        return ActiveBomb(bomb.x, bomb.y, bomb.age, self.rules.seconds)

    def fire(self, x: float, y: float) -> bool:
        """Set a bomb off at (`x`, `y`) if one is left and none is active.

        Returns whether it did.
        """
        if self.count <= 0 or self._active is not None:
            return False
        self.count -= 1
        self.fired += 1
        self._active = _BombState(x, y)
        return True

    def add(self) -> bool:
        """Return a bomb bonus (GAME-BONUS-09): one more bomb, up to the most if any.

        Returns whether it was added.
        """
        most = self.rules.max if self.rules.max is not None else INFINITY
        if self.count >= most:
            return False
        self.count += 1
        return True

    def refill(self) -> None:
        """After a lost life: back up to the starting count if fewer are left."""
        self.count = max(self.count, self.rules.start)

    def step(self, dt: float) -> None:
        """Count down the bomb going off, if any."""
        bomb = self._active
        if bomb is None:
            return
        bomb.age += dt
        if bomb.age >= self.rules.seconds:
            self._active = None
