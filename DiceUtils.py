from __future__ import annotations
from collections import Counter
import itertools
import random
from typing import Iterable, Iterator

class Dice:
    def __init__(self, sides: int, count: int=1):
        self.count = count
        self.sides = sides
    
    @property
    def count(self) -> int:
        """Number of dice

        Returns:
            int: number of dice
        """
        return self._count
    
    @count.setter
    def count(self, count: int):
        """Number of dice

        Args:
            count (int): number of dice

        Raises:
            TypeError: not an int
            ValueError: not 1 or higher
        """
        if not isinstance(count, int):
            raise TypeError(f"count was {type(count).__name__}, expected int.")
        if count < 1:
            raise ValueError(f"count was {count}, expected sides > 0.")
        self._count = count
    
    @property
    def sides(self) -> int:
        """Dice sides

        Returns:
            int: dice sides
        """
        return self._sides
    
    @property
    def stats_min(self) -> int:
        """Lowest possible result of the dice pool (all dice roll 1).

        Returns:
            int: lowest possible result
        """
        return self.count
    
    @property
    def stats_max(self) -> int:
        """Highest possible result of the dice pool (all dice roll max faces).

        Returns:
            int: highest possible result
        """
        return self.sides * self.count
    
    @property
    def stats_range(self) -> int:
        """Difference between the maximum and minimum values

        Returns:
            int: difference
        """
        return self.stats_max - self.stats_min

    @property
    def stats_midpoint(self) -> int:
        """Theoretical midpoint value of all dice pool results.

        Returns:
            int: midpoint
        """
        return (self.stats_min + self.stats_max) // 2
    
    @property
    def stats_mean(self) -> float:
        """Theoretical mean value of all dice pool results.

        Returns:
            float: mean
        """
        return (self.stats_min + self.stats_max) / 2
    
    @property
    def stats_median(self) -> float:
        """Theoretical median value of all dice pool results.

        Returns:
            float: median
        """
        counts = self.stats_counts
        rolls = tuple(counts)
        n = len(rolls)
        nm = n // 2
        if n % 2 == 0:
            return (rolls[nm] + rolls[nm + 1]) / 2
        return rolls[nm]
    
    @property
    def stats_counts(self) -> Counter[int]:
        """Calculates potential dice totals using iterative combinations

        Returns:
            Counter[int]: results
        """
        counts = Counter(range(1, self.sides + 1))
        for _ in range(self.count - 1):
            new_counts = Counter()
            for total, freq in counts.items():
                for face in range(1, self.sides + 1):
                    new_counts[total + face] += freq
            counts = new_counts
        return counts
    
    @property
    def stats_mode(self) -> int:
        """Calculates most common dice total

        Returns:
            int: mode result
        """
        counts = self.stats_counts
        return counts.most_common(1)[0][0]
    
    @sides.setter
    def sides(self, sides: int):
        """Dice sides

        Args:
            sides (int): dice sides

        Raises:
            TypeError: not an int
            ValueError: not 1 or higher
        """
        if not isinstance(sides, int):
            raise TypeError(f"sides was {type(sides).__name__}, expected int.")
        if sides < 1:
            raise ValueError(f"sides was {sides}, expected sides > 0.")
        self._sides = sides
        
    def roll_one(self) -> int:
        """Roll a single dice in the pool

        Returns:
            int: roll result
        """
        return random.randint(1, self.sides)    
    
    def roll_iter(self) -> Iterator[int]:
        """Roll the dice in the pool

        Returns:
            int: roll result

        Yields:
            Iterator[int]: all roll results
        """
        return (self.roll_one() for _ in range(self.count))
    
    def roll_all(self) -> int:
        """Roll then total the dice in the pool

        Returns:
            int: sum of all rolls
        """
        return sum(self.roll_iter()) 
        
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
        return self.count == other.count and self.sides == other.sides
    
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
        return f'Dice(count={self.count},sides={self.sides})'
    
    def __str__(self) -> str:
        return f'{self.count}d{self.sides}'
    
class DiceUtils:
    @staticmethod
    def d4(count=1) -> Dice:
        return Dice(4, count)
    
    @staticmethod
    def d6(count=1) -> Dice:
        return Dice(6, count)
    
    @staticmethod
    def d8(count=1) -> Dice:
        return Dice(8, count)
    
    @staticmethod
    def d10(count=1) -> Dice:
        return Dice(10, count)
    
    @staticmethod
    def d12(count=1) -> Dice:
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
        """Rolls a die repeatedly. Stops when it rolls lower than its maximum.

        Args:
            die (Dice): _description_
            max_explosions (int, optional): _description_. Defaults to -1.

        Raises:
            ValueError: _description_

        Yields:
            Iterator[int]: _description_
        """
        if die.sides <= 1 and max_explosions == -1:
            raise ValueError("Cannot explode a 1-sided die without a max_explosions limit.")
        
        explosions = 0
        while max_explosions == -1 or explosions < max_explosions:
            roll = die()
            yield roll
            explosions += 1
            if roll < die.sides:
                break
    
    @staticmethod
    def roll_exploding_list(die: Dice, max_explosions: int = -1) -> list[int]:
        #"""Rolls a single die and explodes if the maximum value is rolled. 
        #High speed, minimal boiler plate and reusable result."""
        if die.sides <= 1 and max_explosions == -1:
            raise ValueError("Cannot explode a 1-sided die without a max_explosions limit.")
        
        rolls = []
        while max_explosions == -1 or len(rolls) < max_explosions:
            rolls.append(roll := die.roll_one())
            if roll < die.sides:
                break
        return rolls
    
    @classmethod
    def roll_percentile(cls) -> int:
        # Semantically distinct from a d100
        result = random.randrange(0, 10) + random.randrange(0, 100, 10)
        return 100 if result == 0 else result

dice = Dice(4, 2)        
print(dice())