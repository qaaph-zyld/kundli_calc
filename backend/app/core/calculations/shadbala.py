"""Shadbala calculation module."""
from typing import Dict, List, Optional
import math


class ShadbalaSystem:
    """Shadbala calculation system."""

    def __init__(self):
        """Initialize Shadbala system."""
        self.planet_strengths = {
            'Sun': 60,
            'Moon': 51,
            'Mars': 28,
            'Mercury': 34,
            'Jupiter': 20,
            'Venus': 50,
            'Saturn': 40
        }

        self.house_strengths = {
            1: 10, 2: 8, 3: 6, 4: 4, 5: 2, 6: 0,
            7: 10, 8: 8, 9: 6, 10: 4, 11: 2, 12: 0
        }

        self.aspect_strengths = {
            'conjunction': 1.0,
            'sextile': 0.5,
            'square': -0.5,
            'trine': 0.75,
            'opposition': -1.0
        }

    def calculate_sthan_bala(self, house: int) -> float:
        """Calculate positional strength."""
        return self.house_strengths.get(house, 0)

    def calculate_dig_bala(self, planet: str, house: int) -> float:
        """Calculate directional strength."""
        dig_bala_map = {
            'Sun': {10: 1.0, 7: -1.0},
            'Moon': {4: 1.0, 10: -1.0},
            'Mars': {1: 1.0, 7: -1.0},
            'Mercury': {7: 1.0, 1: -1.0},
            'Jupiter': {1: 1.0, 7: -1.0},
            'Venus': {4: 1.0, 10: -1.0},
            'Saturn': {7: 1.0, 1: -1.0}
        }
        return dig_bala_map.get(planet, {}).get(house, 0)

    def calculate_chesta_bala(self, planet: str, speed: float) -> float:
        """Calculate motional strength."""
        # Normalize speed to a value between 0 and 1
        abs_speed = abs(speed)
        max_speed = {
            'Sun': 1.0,
            'Moon': 13.0,
            'Mars': 0.5,
            'Mercury': 1.5,
            'Jupiter': 0.2,
            'Venus': 1.2,
            'Saturn': 0.1
        }.get(planet, 1.0)
        
        normalized_speed = min(abs_speed / max_speed, 1.0)
        return normalized_speed * self.planet_strengths[planet]

    def calculate_aspect_bala(self, aspects: List[Dict]) -> float:
        """Calculate aspectual strength."""
        total_strength = 0
        for aspect in aspects:
            strength = self.aspect_strengths.get(aspect['type'], 0)
            total_strength += strength
        return total_strength

    def calculate_shadbala(
        self,
        planet: str,
        house: int,
        speed: float,
        aspects: List[Dict],
        is_day: bool
    ) -> Dict:
        """Calculate total Shadbala strength."""
        sthan_bala = self.calculate_sthan_bala(house)
        dig_bala = self.calculate_dig_bala(planet, house)
        chesta_bala = self.calculate_chesta_bala(planet, speed)
        aspect_bala = self.calculate_aspect_bala(aspects)

        # Day/Night strength
        kala_bala = 1.0 if is_day else -1.0
        if planet in ['Moon', 'Venus', 'Saturn']:
            kala_bala *= -1  # These planets are stronger at night

        total_strength = (
            sthan_bala +
            dig_bala +
            chesta_bala +
            aspect_bala +
            kala_bala
        ) * self.planet_strengths[planet]

        return {
            'total_strength': total_strength,
            'sthan_bala': sthan_bala,
            'dig_bala': dig_bala,
            'chesta_bala': chesta_bala,
            'aspect_bala': aspect_bala,
            'kala_bala': kala_bala
        }