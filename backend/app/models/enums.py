"""Enums for astrological calculations."""
from enum import Enum, auto


class Planet(Enum):
    """Planets used in astrological calculations."""
    SUN = 0
    MOON = 1
    MARS = 2
    MERCURY = 3
    JUPITER = 4
    VENUS = 5
    SATURN = 6
    RAHU = 7
    KETU = 8


class House(Enum):
    """Houses in astrological chart."""
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4
    FIFTH = 5
    SIXTH = 6
    SEVENTH = 7
    EIGHTH = 8
    NINTH = 9
    TENTH = 10
    ELEVENTH = 11
    TWELFTH = 12


class Aspect(Enum):
    """Planetary aspects."""
    CONJUNCTION = 0
    SEXTILE = 60
    SQUARE = 90
    TRINE = 120
    OPPOSITION = 180

    @property
    def angle(self) -> float:
        """Get the aspect angle in degrees."""
        return self.value
