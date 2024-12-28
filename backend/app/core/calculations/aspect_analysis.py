"""
Aspect Analysis System Implementation
PGF Protocol: VCI_001
Gate: GATE_3
Version: 1.0.0
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import math

class AspectType(Enum):
    """Types of aspects in Vedic astrology"""
    FULL = "full"      # Full aspect (100% strength)
    THREE_QUARTER = "three_quarter"  # 75% strength
    HALF = "half"      # Half aspect (50% strength)
    QUARTER = "quarter"  # Quarter aspect (25% strength)

@dataclass
class AspectInfluence:
    """Represents the influence of an aspect"""
    aspect_type: AspectType
    strength: float
    is_beneficial: bool
    special_effects: Optional[List[str]] = None

class AspectAnalyzer:
    """Analyzes planetary aspects according to Vedic principles"""
    
    def __init__(self):
        # Define standard planetary aspects
        self.standard_aspects = {
            'Sun': [7],           # 7th house aspect
            'Moon': [7],          # 7th house aspect
            'Mars': [4, 7, 8],    # 4th, 7th, 8th aspects
            'Mercury': [7],       # 7th house aspect
            'Jupiter': [5, 7, 9], # 5th, 7th, 9th aspects
            'Venus': [7],         # 7th house aspect
            'Saturn': [3, 7, 10]  # 3rd, 7th, 10th aspects
        }
        
        # Define aspect strengths
        self.aspect_strengths = {
            AspectType.FULL: 1.0,
            AspectType.THREE_QUARTER: 0.75,
            AspectType.HALF: 0.5,
            AspectType.QUARTER: 0.25
        }
        
        # Define natural relationships
        self.natural_relationships = {
            'Sun': {
                'friends': ['Moon', 'Mars', 'Jupiter'],
                'enemies': ['Saturn', 'Venus'],
                'neutral': ['Mercury']
            },
            'Moon': {
                'friends': ['Sun', 'Mercury'],
                'enemies': ['Saturn'],
                'neutral': ['Mars', 'Jupiter', 'Venus']
            }
            # Add other planetary relationships
        }
    
    def calculate_aspect_influence(
        self,
        aspecting_planet: str,
        aspected_planet: str,
        houses_between: int
    ) -> Optional[AspectInfluence]:
        """Calculate the influence of an aspect between two planets"""
        
        # Check if aspect exists
        if houses_between not in self.standard_aspects.get(aspecting_planet, []):
            return None
            
        # Determine aspect type and base strength
        aspect_type = self._determine_aspect_type(aspecting_planet, houses_between)
        base_strength = self.aspect_strengths[aspect_type]
        
        # Apply relationship modifications
        relationship_factor = self._calculate_relationship_factor(
            aspecting_planet, aspected_planet
        )
        
        # Calculate final strength
        final_strength = base_strength * relationship_factor
        
        # Determine if aspect is beneficial
        is_beneficial = self._is_aspect_beneficial(
            aspecting_planet, aspected_planet, houses_between
        )
        
        # Check for special effects
        special_effects = self._check_special_effects(
            aspecting_planet, aspected_planet, houses_between
        )
        
        return AspectInfluence(
            aspect_type=aspect_type,
            strength=final_strength,
            is_beneficial=is_beneficial,
            special_effects=special_effects
        )
    
    def calculate_all_aspects(
        self,
        planet_positions: Dict[str, Dict[str, Any]]
    ) -> Dict[Tuple[str, str], AspectInfluence]:
        """Calculate all aspects between planets"""
        aspects = {}
        planets = list(planet_positions.keys())
        
        for i, p1 in enumerate(planets):
            for p2 in planets[i+1:]:
                houses_between = self._calculate_houses_between(
                    planet_positions[p1]['longitude'],
                    planet_positions[p2]['longitude']
                )
                reverse_houses = self._calculate_houses_between(
                    planet_positions[p2]['longitude'],
                    planet_positions[p1]['longitude']
                )
                
                # Check aspects in both directions
                aspect1 = self.calculate_aspect_influence(p1, p2, houses_between)
                aspect2 = self.calculate_aspect_influence(p2, p1, reverse_houses)
                
                if aspect1:
                    aspects[(p1, p2)] = aspect1
                if aspect2:
                    aspects[(p2, p1)] = aspect2
        
        return aspects
    
    def _determine_aspect_type(self, planet: str, houses: int) -> AspectType:
        """Determine the type of aspect based on planet and houses"""
        if houses == 7:  # 7th house aspect is always full
            return AspectType.FULL
        elif planet in ['Jupiter', 'Saturn'] and houses in [3, 5, 9, 10]:
            return AspectType.THREE_QUARTER
        elif planet == 'Mars' and houses in [4, 8]:
            return AspectType.HALF
        else:
            return AspectType.QUARTER
    
    def _calculate_relationship_factor(self, planet1: str, planet2: str) -> float:
        """Calculate relationship factor between planets"""
        relationships = self.natural_relationships.get(planet1, {})
        
        if planet2 in relationships.get('friends', []):
            return 1.1  # 10% boost for friendly planets
        elif planet2 in relationships.get('enemies', []):
            return 0.9  # 10% reduction for enemy planets
        else:
            return 1.0  # Neutral relationship
    
    def _is_aspect_beneficial(
        self,
        aspecting_planet: str,
        aspected_planet: str,
        houses: int
    ) -> bool:
        """Determine if an aspect is beneficial"""
        # Implement logic for beneficial aspect determination
        # This is a simplified version
        if aspecting_planet in ['Jupiter', 'Venus', 'Mercury']:
            return True
        elif aspecting_planet in ['Saturn', 'Mars'] and houses in [3, 10]:
            return True
        else:
            return False
    
    def _check_special_effects(
        self,
        aspecting_planet: str,
        aspected_planet: str,
        houses: int
    ) -> List[str]:
        """Check for special effects of the aspect"""
        effects = []
        
        # Check for special combinations
        if aspecting_planet == 'Jupiter' and aspected_planet == 'Moon':
            effects.append('Gaja-Kesari Yoga')
        elif aspecting_planet == 'Jupiter' and aspected_planet == 'Venus':
            effects.append('Wealth Enhancement')
            
        return effects if effects else None
    
    def _calculate_houses_between(
        self,
        longitude1: float,
        longitude2: float
    ) -> int:
        """Calculate number of houses between two planetary positions"""
        # Normalize longitudes to 0-360 range
        lon1 = longitude1 % 360
        lon2 = longitude2 % 360
        
        # Calculate difference considering wrap-around
        diff = (lon2 - lon1) % 360
        
        # Convert to houses (1-12)
        houses = int(diff / 30) + 1
        
        # Handle wrap-around case
        if houses > 12:
            houses = houses % 12
        
        return houses
