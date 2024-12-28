"""
Yoga Calculator Implementation
PGF Protocol: VCI_001
Gate: GATE_3
Version: 1.0.0

This module implements the Yoga calculation system according to Vedic astrology principles.
It identifies and analyzes various yoga formations in a horoscope, including:
- Raj Yoga (Royal combinations)
- Dhana Yoga (Wealth combinations)
- Vipreet Raja Yoga (Reversal combinations)
- Pancha Mahapurusha Yoga (Five great person combinations)
- Gajakesari Yoga (Elephant-Lion combination)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum

class YogaType(Enum):
    """Types of Vedic yogas"""
    RAJ = "raj"                   # Royal combinations
    DHANA = "dhana"              # Wealth combinations
    VIPREET = "vipreet"          # Reversal combinations
    MAHAPURUSHA = "mahapurusha"  # Great person combinations
    KESARI = "kesari"            # Elephant-Lion combination
    BUDHA_ADITYA = "budha_aditya"  # Mercury-Sun combination
    NEECH_BHANG = "neech_bhang"    # Cancellation of debilitation

@dataclass
class YogaResult:
    """Represents a detected yoga in the horoscope"""
    yoga_type: YogaType
    strength: float  # 0-100
    planets_involved: List[str]
    houses_involved: List[int]
    description: str
    effects: List[str]
    is_complete: bool  # Whether all required conditions are met

class YogaCalculator:
    """Calculates and analyzes yoga formations in a horoscope"""
    
    def __init__(self):
        # Define house lordships
        self.house_lords = {
            1: "Mars",      # Aries
            2: "Venus",     # Taurus
            3: "Mercury",   # Gemini
            4: "Moon",      # Cancer
            5: "Sun",       # Leo
            6: "Mercury",   # Virgo
            7: "Venus",     # Libra
            8: "Mars",      # Scorpio
            9: "Jupiter",   # Sagittarius
            10: "Saturn",   # Capricorn
            11: "Saturn",   # Aquarius
            12: "Jupiter"   # Pisces
        }
        
        # Define planet relationships
        self.planet_relationships = {
            "Sun": {
                "friends": ["Moon", "Mars", "Jupiter"],
                "enemies": ["Venus", "Saturn"],
                "neutral": ["Mercury"]
            },
            "Moon": {
                "friends": ["Sun", "Mercury"],
                "enemies": ["Saturn"],
                "neutral": ["Mars", "Jupiter", "Venus"]
            },
            "Mars": {
                "friends": ["Sun", "Moon", "Jupiter"],
                "enemies": ["Mercury"],
                "neutral": ["Venus", "Saturn"]
            },
            "Mercury": {
                "friends": ["Sun", "Venus"],
                "enemies": ["Moon"],
                "neutral": ["Mars", "Jupiter", "Saturn"]
            },
            "Jupiter": {
                "friends": ["Sun", "Moon", "Mars"],
                "enemies": ["Mercury", "Venus"],
                "neutral": ["Saturn"]
            },
            "Venus": {
                "friends": ["Mercury", "Saturn"],
                "enemies": ["Sun", "Moon"],
                "neutral": ["Mars", "Jupiter"]
            },
            "Saturn": {
                "friends": ["Mercury", "Venus"],
                "enemies": ["Sun", "Moon", "Mars"],
                "neutral": ["Jupiter"]
            }
        }
        
        # Define Mahapurusha yoga conditions
        self.mahapurusha_conditions = {
            "Mars": [1, 4, 7, 10],      # Ruchaka Yoga
            "Mercury": [1, 4, 7, 10],   # Bhadra Yoga
            "Jupiter": [1, 4, 7, 10],   # Hamsa Yoga
            "Venus": [1, 4, 7, 10],     # Malavya Yoga
            "Saturn": [1, 4, 7, 10]     # Sasa Yoga
        }
    
    def calculate_raj_yoga(
        self,
        planet_positions: Dict[str, Dict[str, float]],
        house_positions: Dict[int, List[str]]
    ) -> List[YogaResult]:
        """Calculate Raj Yoga formations"""
        raj_yogas = []
        
        # Check for lords of trine houses (1, 5, 9) in quadrant houses (1, 4, 7, 10)
        trine_houses = {1, 5, 9}
        quadrant_houses = {1, 4, 7, 10}
        
        for trine in trine_houses:
            trine_lord = self.house_lords[trine]
            trine_lord_house = self._get_planet_house(trine_lord, planet_positions)
            
            if trine_lord_house in quadrant_houses:
                # Calculate strength based on planet's dignity and house position
                strength = self._calculate_yoga_strength(
                    trine_lord,
                    trine_lord_house,
                    planet_positions
                )
                
                raj_yogas.append(YogaResult(
                    yoga_type=YogaType.RAJ,
                    strength=strength,
                    planets_involved=[trine_lord],
                    houses_involved=[trine, trine_lord_house],
                    description=f"Lord of {trine} house in {trine_lord_house} house",
                    effects=["Authority", "Leadership", "Success"],
                    is_complete=True
                ))
        
        return raj_yogas
    
    def calculate_dhana_yoga(
        self,
        planet_positions: Dict[str, Dict[str, float]],
        house_positions: Dict[int, List[str]]
    ) -> List[YogaResult]:
        """Calculate Dhana (wealth) Yoga formations"""
        dhana_yogas = []
        
        # Check for 2nd and 11th house lords' positions
        wealth_houses = {2, 11}
        beneficial_houses = {1, 2, 4, 5, 9, 11}
        
        for house in wealth_houses:
            lord = self.house_lords[house]
            lord_house = self._get_planet_house(lord, planet_positions)
            
            if lord_house in beneficial_houses:
                strength = self._calculate_yoga_strength(
                    lord,
                    lord_house,
                    planet_positions
                )
                
                dhana_yogas.append(YogaResult(
                    yoga_type=YogaType.DHANA,
                    strength=strength,
                    planets_involved=[lord],
                    houses_involved=[house, lord_house],
                    description=f"Lord of {house} house in {lord_house} house",
                    effects=["Financial gains", "Material prosperity", "Wealth"],
                    is_complete=True
                ))
        
        return dhana_yogas
    
    def calculate_mahapurusha_yoga(
        self,
        planet_positions: Dict[str, Dict[str, float]]
    ) -> List[YogaResult]:
        """Calculate Pancha Mahapurusha Yoga formations"""
        mahapurusha_yogas = []
        
        for planet, houses in self.mahapurusha_conditions.items():
            planet_house = self._get_planet_house(planet, planet_positions)
            
            if planet_house in houses:
                # Check if planet is in own sign or exaltation
                dignity = self._get_planet_dignity(planet, planet_positions)
                if dignity in ['own', 'exalted']:
                    strength = self._calculate_yoga_strength(
                        planet,
                        planet_house,
                        planet_positions
                    )
                    
                    yoga_name = {
                        "Mars": "Ruchaka",
                        "Mercury": "Bhadra",
                        "Jupiter": "Hamsa",
                        "Venus": "Malavya",
                        "Saturn": "Sasa"
                    }[planet]
                    
                    mahapurusha_yogas.append(YogaResult(
                        yoga_type=YogaType.MAHAPURUSHA,
                        strength=strength,
                        planets_involved=[planet],
                        houses_involved=[planet_house],
                        description=f"{yoga_name} Yoga by {planet} in {planet_house} house",
                        effects=["Great personality", "Success", "Leadership"],
                        is_complete=True
                    ))
        
        return mahapurusha_yogas
    
    def _get_planet_house(
        self,
        planet: str,
        planet_positions: Dict[str, Dict[str, float]]
    ) -> int:
        """Get the house occupied by a planet"""
        longitude = planet_positions[planet]['longitude']
        return (int(longitude / 30) + 1)
    
    def _get_planet_dignity(
        self,
        planet: str,
        planet_positions: Dict[str, Dict[str, float]]
    ) -> str:
        """Get the dignity status of a planet"""
        # This is a simplified version. In reality, we would check:
        # - Exaltation/debilitation points
        # - Own sign
        # - Friendly/enemy signs
        return planet_positions[planet].get('dignity', 'neutral')
    
    def _calculate_yoga_strength(
        self,
        planet: str,
        house: int,
        planet_positions: Dict[str, Dict[str, float]]
    ) -> float:
        """Calculate the strength of a yoga formation"""
        base_strength = 70  # Base strength
        
        # Modify based on dignity
        dignity_factor = {
            'exalted': 1.3,
            'own': 1.2,
            'friend': 1.1,
            'neutral': 1.0,
            'enemy': 0.9,
            'debilitated': 0.7
        }
        
        dignity = self._get_planet_dignity(planet, planet_positions)
        strength = base_strength * dignity_factor[dignity]
        
        # Modify based on house position
        if house in {1, 4, 7, 10}:  # Kendra (angular) houses
            strength *= 1.2
        elif house in {5, 9}:  # Trikona (trine) houses
            strength *= 1.1
        elif house in {3, 6, 11}:  # Upachaya (growth) houses
            strength *= 1.05
        elif house in {6, 8, 12}:  # Dusthana (malefic) houses
            strength *= 0.8
        
        return min(100, strength)  # Cap at 100
