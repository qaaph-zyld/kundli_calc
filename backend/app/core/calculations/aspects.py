from typing import Dict, List, Tuple
from dataclasses import dataclass
import math

@dataclass
class Aspect:
    name: str
    angle: float
    orb: float
    is_major: bool

class AspectCalculator:
    ASPECTS = {
        "Conjunction": Aspect("Conjunction", 0, 10, True),
        "Opposition": Aspect("Opposition", 180, 10, True),
        "Trine": Aspect("Trine", 120, 8, True),
        "Square": Aspect("Square", 90, 8, True),
        "Sextile": Aspect("Sextile", 60, 6, True),
        "Semisextile": Aspect("Semisextile", 30, 2, False),
        "Quincunx": Aspect("Quincunx", 150, 3, False),
        "Semisquare": Aspect("Semisquare", 45, 2, False),
        "Sesquiquadrate": Aspect("Sesquiquadrate", 135, 2, False)
    }
    
    @staticmethod
    def calculate_aspects(
        planetary_positions: Dict[str, Dict[str, float]]
    ) -> List[Dict]:
        """Calculate aspects between planets."""
        aspects = []
        planets = list(planetary_positions.keys())
        
        for i, planet1 in enumerate(planets):
            for planet2 in planets[i+1:]:
                long1 = planetary_positions[planet1]["longitude"]
                long2 = planetary_positions[planet2]["longitude"]
                
                # Calculate the angular difference
                diff = abs(long1 - long2)
                if diff > 180:
                    diff = 360 - diff
                
                # Check for aspects
                for aspect in AspectCalculator.ASPECTS.values():
                    if abs(diff - aspect.angle) <= aspect.orb:
                        aspects.append({
                            "planet1": planet1,
                            "planet2": planet2,
                            "aspect": aspect.name,
                            "angle": aspect.angle,
                            "orb": round(abs(diff - aspect.angle), 2),
                            "is_major": aspect.is_major,
                            "is_applying": AspectCalculator._is_applying(
                                planetary_positions[planet1],
                                planetary_positions[planet2]
                            )
                        })
        
        return aspects
    
    @staticmethod
    def _is_applying(planet1: Dict[str, float], planet2: Dict[str, float]) -> bool:
        """Determine if aspect is applying or separating."""
        if "speed" not in planet1 or "speed" not in planet2:
            return False
            
        relative_speed = planet1["speed"] - planet2["speed"]
        return relative_speed < 0  # Applying if relative speed is negative
