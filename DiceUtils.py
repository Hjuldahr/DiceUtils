from __future__ import annotations
import bisect
from collections import Counter
from itertools import accumulate
import random
from typing import Iterator

class Dice:
    def __init__(self, faces: int, count: int=1):
        """Stochastic dice

        Args:
            faces (int): Dice faces
            count (int, optional): Number of dice. Defaults to 1.
        """
        self.count = count
        self.faces = faces
        self._is_stats_stale = False
    
    @property
    def count(self) -> int:
        """Number of dice.

        Returns:
            int: number of dice
        """
        return self._count
    
    @count.setter
    def count(self, count: int):
        """Number of dice. Intended for internal use.

        Args:
            count (int): number of dice

        Raises:
            TypeError: not an int
            ValueError: not 1 or higher
        """
        if not isinstance(count, int):
            raise TypeError(f"count was {type(count).__name__}, expected int.")
        if count < 1:
            raise ValueError(f"count was {count}, expected faces > 0.")
        self._count = count
        self._is_stats_stale = True
    
    @property
    def faces(self) -> int:
        """Dice faces.

        Returns:
            int: dice faces
        """
        return self._faces
    
    @faces.setter
    def faces(self, faces: int):
        """Dice faces. Intended for internal use.

        Args:
            faces (int): dice faces

        Raises:
            TypeError: not an int
            ValueError: not 1 or higher
        """
        if not isinstance(faces, int):
            raise TypeError(f"faces was {type(faces).__name__}, expected int.")
        if faces < 1:
            raise ValueError(f"faces was {faces}, expected faces > 0.")
        self._faces = faces
        self._is_stats_stale = True
    
    def _check_stats(self):
        if self._is_stats_stale:
            self._update_stats()
    
    def _update_stats(self):
        self._stats_min = self.count
        self._stats_max = self.faces * self.count
        self._stats_range = self._stats_max - self._stats_min
        self._stats_mid = (self._stats_min + self._stats_max) // 2
        self._stats_mean = (self._stats_min + self._stats_max) / 2

        counts = Counter(range(1, self.faces + 1))
        for _ in range(self.count - 1):
            new_counts = Counter()
            for total, freq in counts.items():
                for face in range(1, self.faces + 1):
                    new_counts[total + face] += freq
            counts = new_counts

        self._stats_mode = counts.most_common(1)[0][0]

        rolls = sorted(counts.items())          # [(roll, freq), ...]
        freqs = [freq for _, freq in rolls]
        cum = list(accumulate(freqs))
        total = cum[-1]

        def nth(n):
            idx = bisect.bisect_right(cum, n)
            return rolls[idx][0]

        if total % 2:
            self._stats_median = nth(total // 2)
        else:
            self._stats_median = (nth(total // 2 - 1) + nth(total // 2)) / 2
            
        self._is_stats_stale = False

    @property
    def stats_min(self) -> int:
        """Lowest possible result of the dice pool (all dice roll 1).

        Returns:
            int: lowest possible result
        """
        self._check_stats()
        return self._stats_min
    
    @property
    def stats_max(self) -> int:
        """Highest possible result of the dice pool (all dice roll max faces).

        Returns:
            int: highest possible result
        """
        self._check_stats()
        return self._stats_max
    
    @property
    def stats_range(self) -> int:
        """Difference between the maximum and minimum values

        Returns:
            int: difference
        """
        self._check_stats()
        return self._stats_range

    @property
    def stats_midpoint(self) -> int:
        """Theoretical midpoint value of all dice pool results.

        Returns:
            int: midpoint
        """
        self._check_stats()
        return self._stats_mid
    
    @property
    def stats_mean(self) -> float:
        """Theoretical mean value of all dice pool results.

        Returns:
            float: mean
        """
        self._check_stats()
        return self._stats_mean
    
    @property
    def stats_median(self) -> float:
        """Theoretical median value of all dice pool results.

        Returns:
            float: median
        """
        self._check_stats()
        return self._stats_median
    
    @property
    def stats_mode(self) -> int:
        """Calculates most common dice total

        Returns:
            int: mode result
        """
        self._check_stats()
        return self._stats_mode
        
    def roll_one(self) -> int:
        """Roll a single dice in the pool

        Returns:
            int: roll result
        """
        return random.randint(1, self.faces) if self.faces > 1 else 1    
    
    def roll_iter(self) -> Iterator[int]:
        """Roll the dice in the pool

        Returns:
            int: roll result

        Yields:
            Iterator[int]: all roll results
        """
        return (self.roll_one() for _ in range(self.count)) if self.faces > 1 else (1 for _ in range(self.count))
    
    def roll_all(self) -> int:
        """Roll then total the dice in the pool

        Returns:
            int: sum of all rolls
        """
        return sum(self.roll_iter()) if self.faces > 1 else self.count
        
    def roll(self) -> int:
        """Chooses between Dice.roll_one() or Dice.roll_all() depending on dice pool size

        Returns:
            int: roll result or sum of all rolls
        """
        if self.count == 1:
            return self.roll_one()
        return self.roll_all()
        
    def __call__(self) -> int:
        """Convenience method for Dice.roll()

        Returns:
            int: roll result or sum of all rolls
        """
        return self.roll()
    
    @staticmethod
    def _resolve(other: Dice | int | float) -> int | float:
        if isinstance(other, (int, float)):
            return other
        if isinstance(other, Dice):
            return other.roll()
        return NotImplemented
    
    def __add__(self, other: Dice | int | float) -> int | float:
        return self.roll() + self._resolve(other)
    
    def __radd__(self, other):
        return self.__add__(other)
    
    def __sub__(self, other: Dice | int | float) -> int | float:
        return self.roll() - self._resolve(other)
    
    def __rsub__(self, other: Dice | int | float) -> int | float:
        return self._resolve(other) - self.roll()
    
    def __mul__(self, other: Dice | int | float) -> int | float:
        return self.roll() * self._resolve(other)
    
    def __rmul__(self, other: Dice | int | float) -> int | float:
        return self.__mul__(other)
    
    def __truediv__(self, other: Dice | int | float) -> float:
        return self.roll() / self._resolve(other)
    
    def __rtruediv__(self, other: Dice | int | float) -> float:
        return self._resolve(other) / self.roll()
    
    def __floordiv__(self, other: Dice | int | float) -> int | float:
        return self.roll() // self._resolve(other)
    
    def __rfloordiv__(self, other: Dice | int | float) -> int | float:
        return self._resolve(other) // self.roll()
    
    def __eq__(self, other: Dice | int | float) -> bool:
        return self.roll() == self._resolve(other)
    
    def matches(self, other: Dice) -> bool:
        """Structural comparison between two Dice

        Args:
            other (Dice): dice being matched

        Returns:
            bool: equivelance
        """
        if not isinstance(other, Dice): 
            raise TypeError(f"other was {type(other).__name__}, expected; Dice")
        return self.count == other.count and self.faces == other.faces
    
    def roll_against(self, other: Dice | int | float) -> int:
        """This is a stochastic comparison helper. Not meant for stable ordering.\n

        Args:
            other (Dice | int | float): value being compared

        Returns:
            int: sign\n
            • 1: self >  other\n
            • 0: self == other\n
            • -1: self < other
        """
        roll = self.roll()
        value = self._resolve(other)
        if roll < value:
            return -1
        if roll > value:
            return 1
        return 0
    
    def __lt__(self, other: Dice | int | float) -> bool:
        return self.roll() < self._resolve(other)
    
    def __le__(self, other: Dice | int | float) -> bool:
        return self.roll() <= self._resolve(other)
    
    def __gt__(self, other: Dice | int | float) -> bool:
        return self.roll() > self._resolve(other)
    
    def __ge__(self, other: Dice | int | float) -> bool:
        return self.roll() >= self._resolve(other)
    
    def __iter__(self) -> Iterator[int]:
        return self.roll_iter()
    
    def __repr__(self) -> str:
        return f'Dice(count={self.count},faces={self.faces})'
    
    def __str__(self) -> str:
        return f'{self.count}d{self.faces}'
    
class DiceUtils:
    @staticmethod
    def d4(count=1) -> Dice:
        """Factory method for d4s

        Args:
            count (int, optional): Number of dice. Defaults to 1.

        Returns:
            Dice: d4s
        """
        return Dice(4, count)
    
    @staticmethod
    def d6(count=1) -> Dice:
        """Factory method for d6s

        Args:
            count (int, optional): Number of dice. Defaults to 1.

        Returns:
            Dice: d6s
        """
        return Dice(6, count)
    
    @staticmethod
    def d8(count=1) -> Dice:
        """Factory method for d8s

        Args:
            count (int, optional): Number of dice. Defaults to 1.

        Returns:
            Dice: d8s
        """
        return Dice(8, count)
    
    @staticmethod
    def d10(count=1) -> Dice:
        """Factory method for d10s

        Args:
            count (int, optional): Number of dice. Defaults to 1.

        Returns:
            Dice: d10s
        """
        return Dice(10, count)
    
    @staticmethod
    def d12(count=1) -> Dice:
        """Factory method for d12s

        Args:
            count (int, optional): Number of dice. Defaults to 1.

        Returns:
            Dice: d12s
        """
        return Dice(12, count)
    
    @staticmethod
    def d20(count=1) -> Dice:
        return Dice(20, count)
    
    @staticmethod
    def d100(count=1) -> Dice:
        return Dice(100, count)
    
    @classmethod
    def roll_advantage(cls) -> int:
        """Rolls 2d20 and takes the highest result

        Returns:
            int: highest from 2d20
        """
        return max(cls.d20(2))    
    
    @classmethod
    def roll_disadvantage(cls) -> int:
        """Rolls 2d20 and takes the lowest result

        Returns:
            int: lowest from 2d20
        """
        return min(cls.d20(2))  

    @staticmethod
    def roll_exploding_iter(die: Dice, max_explosions: int = -1) -> Iterator[int]:
        """Rolls a single die iteratively. Stops when it rolls lower than its maximum.\n
        Yields infinitely if attempting to roll a single faced die without an explosion limit.

        Args:
            die (Dice): Die being rolled
            max_explosions (int, optional): Explosion limit or -1 if unlimited. Defaults to -1.

        Raises:
            ValueError: Attempted to use a dice pool instead of a single die

        Returns:
            int | float: Current dice roll or infinity

        Yields:
            Iterator[int]: Dice roller
        """
        if die.count != 1:
            raise ValueError(f"Die had a count of {die.count}, expected count of 1.")

        if die.sides == 1:
            if max_explosions < 0:
                while True:
                    yield 1
            else:
                for _ in range(max_explosions):
                    yield 1
            return

        explosions = 0
        while max_explosions < 0 or explosions < max_explosions:
            roll = die()
            yield roll
            explosions += 1
            if roll < die.faces:
                return
    
    #"""Rolls a single die and explodes if the maximum value is rolled. 
        #High speed, minimal boiler plate and reusable result."""
    @staticmethod
    def roll_exploding_list(die: Dice, max_explosions: int = -1) -> list[int] | None:
        """Rolls a die repeatedly. Stops when it rolls lower than its maximum.
        Returns None if attempting to roll a single faced die without an explosion limit.

        Args:
            die (Dice): Dice type used
            max_explosions (int, optional): Explosion limit or -1 if unlimited. Defaults to -1.

        Raises:
            ValueError: Attempted to use a dice pool instead of a single die

        Returns:
            list[int] | None: Sequence of rolls or None if unbounded
        """
        if die.count != 1:
            raise ValueError(f"Die had a count of {die.count}, expected count of 1.")
        
        if die.sides == 1:
            if max_explosions < 0:
                return None
            else:
                return [1] * max_explosions
        
        rolls = []
        while max_explosions < 0 or len(rolls) < max_explosions:
            rolls.append(roll := die.roll_one())
            if roll < die.faces:
                break
        return rolls
    
    @classmethod
    def roll_percentile(cls) -> int:
        # Semantically distinct from a d100
        result = random.randrange(0, 10) + random.randrange(0, 100, 10)
        return 100 if result == 0 else result

dice = Dice(4, 2)        
print(dice())