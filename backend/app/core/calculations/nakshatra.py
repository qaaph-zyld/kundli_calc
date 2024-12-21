from typing import Dict, Tuple
import math

class NakshatraCalculator:
    NAKSHATRAS = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
        "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
        "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
        "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ]
    
    NAKSHATRA_LORDS = [
        "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn",
        "Mercury", "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter",
        "Saturn", "Mercury", "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
        "Jupiter", "Saturn", "Mercury"
    ]
    
    @staticmethod
    def calculate_nakshatra(longitude: float) -> Dict[str, any]:
        """Calculate nakshatra details for given longitude."""
        # Each nakshatra is 13°20' (13.33333... degrees)
        nakshatra_length = 360 / 27
        
        # Calculate nakshatra number (0-26)
        nakshatra_num = math.floor(longitude / nakshatra_length)
        
        # Calculate pada (quarter) within nakshatra
        position_in_nakshatra = longitude % nakshatra_length
        pada = math.floor(position_in_nakshatra / (nakshatra_length / 4)) + 1
        
        # Calculate degrees traversed in nakshatra
        degrees_traversed = position_in_nakshatra
        
        return {
            "number": nakshatra_num + 1,
            "name": NakshatraCalculator.NAKSHATRAS[nakshatra_num],
            "lord": NakshatraCalculator.NAKSHATRA_LORDS[nakshatra_num],
            "pada": pada,
            "degrees_traversed": round(degrees_traversed, 2),
            "total_degrees": round(nakshatra_length, 2)
        }
    
    @staticmethod
    def calculate_all_nakshatras(
        planetary_positions: Dict[str, Dict[str, float]]
    ) -> Dict[str, Dict]:
        """Calculate nakshatras for all planets."""
        return {
            planet: NakshatraCalculator.calculate_nakshatra(data["longitude"])
            for planet, data in planetary_positions.items()
        }
