"""Astronomical calculations module."""
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import swisseph as swe
from app.core.cache.calculation_cache import CalculationCache
from app.core.config.settings import settings
from app.models.enums import Planet, House, Aspect
from app.models.location import Location


class AstronomicalCalculator:
    """Astronomical calculator using Swiss Ephemeris."""

    def __init__(self):
        """Initialize calculator with Swiss Ephemeris path and cache."""
        # Set ephemeris path
        swe.set_ephe_path(settings.EPHEMERIS_PATH)
        
        # Initialize cache with reasonable size limits
        self._cache = CalculationCache(max_size=500)
        
        # Map planet enums to Swiss Ephemeris constants
        self._planet_map = {
            Planet.SUN: swe.SUN,
            Planet.MOON: swe.MOON,
            Planet.MARS: swe.MARS,
            Planet.MERCURY: swe.MERCURY,
            Planet.JUPITER: swe.JUPITER,
            Planet.VENUS: swe.VENUS,
            Planet.SATURN: swe.SATURN,
            Planet.RAHU: swe.MEAN_NODE,  # Using mean node for Rahu
            Planet.KETU: swe.MEAN_NODE,  # Will calculate Ketu from Rahu
        }

    def _julian_day(self, date: datetime) -> float:
        """Convert datetime to Julian day."""
        return swe.julday(
            date.year,
            date.month,
            date.day,
            date.hour + date.minute/60.0 + date.second/3600.0
        )

    def calculate_planet_position(
        self,
        date: datetime,
        planet: Planet,
        location: Optional[Location] = None
    ) -> Dict[str, float]:
        """Calculate position of a planet."""
        jd = self._julian_day(date)
        
        # Generate cache key
        cache_key = self._cache.generate_key(date, planet.value)
        cached_result = self._cache.get(cache_key)
        if cached_result:
            return cached_result

        # Calculate position
        if planet == Planet.KETU:
            # Ketu is 180° opposite to Rahu
            rahu_pos = self.calculate_planet_position(date, Planet.RAHU, location)
            position = (rahu_pos["longitude"] + 180) % 360
            speed = -rahu_pos["speed"]  # Opposite direction
        else:
            # Calculate using Swiss Ephemeris
            flags = swe.FLG_SWIEPH
            if location:
                # Use topocentric positions if location provided
                flags |= swe.FLG_TOPOCTR
                swe.set_topo(
                    location.latitude,
                    location.longitude,
                    location.altitude or 0
                )
            
            result = swe.calc_ut(jd, self._planet_map[planet], flags)
            position = result[0][0]  # Longitude
            speed = result[3]  # Daily motion

        # Store result
        result = {
            "longitude": position,
            "speed": speed,
            "is_retrograde": speed < 0
        }
        
        self._cache.set(cache_key, result)
        return result

    def calculate_house_cusps(
        self,
        date: datetime,
        location: Location,
        system: str = "P"
    ) -> List[float]:
        """Calculate house cusps using specified system."""
        jd = self._julian_day(date)
        
        # Generate cache key
        cache_key = self._cache.generate_key(
            date,
            location.latitude,
            location.longitude,
            system
        )
        cached_result = self._cache.get(cache_key)
        if cached_result:
            return cached_result

        # Calculate cusps
        cusps, ascmc = swe.houses_ex(
            jd,
            location.latitude,
            location.longitude,
            bytes(system, "utf-8")
        )
        
        # Store and return results
        result = list(cusps[1:13])  # Only need the 12 house cusps
        self._cache.set(cache_key, result)
        return result

    def calculate_aspect(
        self,
        pos1: float,
        pos2: float,
        orb: float = 1.0
    ) -> Optional[Aspect]:
        """Calculate aspect between two positions."""
        # Calculate shortest angular distance
        diff = abs((pos1 - pos2 + 180) % 360 - 180)
        
        # Check each aspect type
        for aspect in Aspect:
            if abs(diff - aspect.angle) <= orb:
                return aspect
        
        return None

    def calculate_aspects(
        self,
        positions: Dict[Planet, float],
        orb: float = 1.0
    ) -> List[Tuple[Planet, Planet, Aspect]]:
        """Calculate all aspects between planets."""
        aspects = []
        planets = list(positions.keys())
        
        for i, p1 in enumerate(planets):
            for p2 in planets[i+1:]:
                aspect = self.calculate_aspect(
                    positions[p1],
                    positions[p2],
                    orb
                )
                if aspect:
                    aspects.append((p1, p2, aspect))
        
        return aspects

    def get_house(self, longitude: float, cusps: List[float]) -> House:
        """Determine house from longitude and cusps."""
        for i in range(12):
            next_i = (i + 1) % 12
            if cusps[next_i] < cusps[i]:  # Cusp crosses 0°
                if longitude >= cusps[i] or longitude < cusps[next_i]:
                    return House(i + 1)
            elif cusps[i] <= longitude < cusps[next_i]:
                return House(i + 1)
        
        # Fallback (shouldn't happen with valid data)
        return House(1)

    def calculate_planetary_positions(
        self,
        date: datetime,
        location: Optional[Location] = None
    ) -> Dict[Planet, Dict[str, float]]:
        """Calculate positions for all planets."""
        positions = {}
        for planet in Planet:
            positions[planet] = self.calculate_planet_position(
                date,
                planet,
                location
            )
        return positions
