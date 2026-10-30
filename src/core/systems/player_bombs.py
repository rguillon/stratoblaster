"""The player's bombs (GD-32, P11-R05)"""

INFINITY = float("Infinity")


class BombRules:
    """The bomb rules.

    `start`: bombs at the start of a level, after a Continue, and the least after a lost life.
    `damage`: damage each enemy and boss piece on screen takes, once, when a bomb goes off.
    `seconds`: seconds a bomb lasts: no other bomb can go off meanwhile, the enemy shots keep
    being cleared and the player cannot be hurt.
    `max`: most bombs the player can have with bomb bonuses (P11-R07); no limit when None.
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
    """A bomb going off, for the visuals: where the ship was when it went off, and how long it has
    been going off (`age`) out of `seconds`.
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
    """The bombs left and the bomb going off (P11-R05): one goes off per press while some are left
    and none is active; lives lost top them back up to the starting count. Pure.
    """

    def __init__(self, rules: BombRules, count: float | None = None) -> None:
        """Starts with `count` bombs: the rules' start, or those kept from the level before."""
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
        """Sets a bomb off at (`x`, `y`) if one is left and none is active; returns whether it
        did."""
        if self.count <= 0 or self._active is not None:
            return False
        self.count -= 1
        self.fired += 1
        self._active = _BombState(x, y)
        return True

    def add(self) -> bool:
        """A bomb bonus (P11-R07): one more bomb, up to the most if any. Returns whether it was
        added.
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
        """Counts down the bomb going off, if any."""
        bomb = self._active
        if bomb is None:
            return
        bomb.age += dt
        if bomb.age >= self.rules.seconds:
            self._active = None
