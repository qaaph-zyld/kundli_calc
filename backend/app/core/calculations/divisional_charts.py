"""
Divisional Chart Engine (D1-D60) Implementation
PGF Protocol: VCI_001
Gate: GATE_3
Version: 1.0.0
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging
from dataclasses import dataclass
import swisseph as swe
from .astronomical import AstronomicalCalculator
from ..cache.calculation_cache import CalculationCache
from ..metrics.performance_metrics import MetricsTimer, metrics

logger = logging.getLogger(__name__)

@dataclass
class DivisionalChart:
    """Represents a divisional chart with all planetary positions"""
    division: int  # D1-D60
    planets: Dict[str, float]  # Planet name to longitude mapping
    houses: List[float]  # House cusps
    ayanamsa: float
    timestamp: datetime
    location: Dict[str, float]  # Latitude, longitude, altitude

class DivisionalChartEngine:
    """Enhanced engine for calculating divisional charts with high precision"""
    
    def __init__(self, cache: Optional[CalculationCache] = None):
        """Initialize the divisional chart engine"""
        self.calculator = AstronomicalCalculator()
        self.cache = cache or CalculationCache()
        self.default_location = {"lat": 28.6139, "lon": 77.2090, "alt": 0.0}  # New Delhi
        
        # Division specific calculations
        self.division_map = {
            1: self._calculate_rashi,      # D1 - Rashi
            2: self._calculate_hora,       # D2 - Hora
            3: self._calculate_drekkana,   # D3 - Drekkana
            4: self._calculate_chaturthamsa,# D4 - Chaturthamsa
            7: self._calculate_saptamsa,   # D7 - Saptamsa
            9: self._calculate_navamsa,    # D9 - Navamsa
            10: self._calculate_dasamsa,   # D10 - Dasamsa
            12: self._calculate_dwadasamsa,# D12 - Dwadasamsa
            16: self._calculate_shodasamsa,# D16 - Shodasamsa
            20: self._calculate_vimshamsa, # D20 - Vimshamsa
            24: self._calculate_chaturvimshamsa,# D24 - Chaturvimshamsa
            27: self._calculate_nakshatramsa,# D27 - Nakshatramsa
            30: self._calculate_trimsamsa, # D30 - Trimsamsa
            40: self._calculate_khavedamsa,# D40 - Khavedamsa
            45: self._calculate_akshavedamsa,# D45 - Akshavedamsa
            60: self._calculate_shashtyamsa # D60 - Shashtyamsa
        }
    
    def calculate_chart(self, date: datetime, division: int, location: Optional[Dict[str, float]] = None) -> DivisionalChart:
        """Calculate divisional chart for given date and division"""
        with MetricsTimer(metrics, f"divisional_chart_d{division}"):
            # Use provided location or default
            chart_location = location or self.default_location
            
            # Check cache first
            cache_key = f"D{division}_{date.isoformat()}_{chart_location['lat']}_{chart_location['lon']}"
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Calculate base planetary positions
            planets = self.calculator.calculate_planetary_positions(date, chart_location)
            houses = self.calculator.calculate_house_cusps(date, chart_location)
            ayanamsa = self.calculator.get_ayanamsa(date)
            
            # Apply divisional calculation
            if division not in self.division_map:
                raise ValueError(f"Unsupported division D{division}")
            
            divisional_positions = self.division_map[division](planets)
            
            chart = DivisionalChart(
                division=division,
                planets=divisional_positions,
                houses=houses,
                ayanamsa=ayanamsa,
                timestamp=date,
                location=chart_location
            )
            
            # Cache result
            self.cache.set(cache_key, chart)
            return chart
    
    def _normalize_longitude(self, longitude: float) -> float:
        """Normalize longitude to 0-360 range"""
        return longitude % 360
    
    def _calculate_rashi(self, planets: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """D1 chart - Same as birth chart"""
        return {planet: self._normalize_longitude(pos['longitude']) 
                for planet, pos in planets.items()}
    
    def _calculate_hora(self, planets: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """D2 chart - Based on odd/even degrees"""
        result = {}
        for planet, pos in planets.items():
            longitude = pos['longitude']
            degree = longitude % 30
            rashi = longitude // 30
            hora = 0 if degree < 15 else 15
            result[planet] = (rashi * 30) + hora
        return result
    
    def _calculate_drekkana(self, planets: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """D3 chart - Divide each sign into 3 parts"""
        result = {}
        for planet, pos in planets.items():
            longitude = pos['longitude']
            sign = int(longitude / 30)
            degree = longitude % 30
            drekkana = int(degree / 10)
            result[planet] = ((sign * 3 + drekkana) * 10) % 360
        return result
    
    def _calculate_navamsa(self, planets: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """D9 chart - Divide each sign into 9 parts"""
        result = {}
        for planet, pos in planets.items():
            longitude = pos['longitude']
            sign = int(longitude / 30)
            degree = longitude % 30
            navamsa = int(degree * 9 / 30)
            result[planet] = ((sign * 9 + navamsa) * 40) % 360
        return result
    
    def _calculate_chaturthamsa(self, planets: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """D4 chart - Divide each sign into 4 parts"""
        result = {}
        for planet, pos in planets.items():
            longitude = pos['longitude']
            sign = int(longitude / 30)
            degree = longitude % 30
            part = int(degree * 4 / 30)
            result[planet] = ((sign * 4 + part) * 7.5) % 360
        return result
    
    def _calculate_saptamsa(self, planets: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """D7 chart - Divide each sign into 7 parts"""
        result = {}
        for planet, pos in planets.items():
            longitude = pos['longitude']
            sign = int(longitude / 30)
            degree = longitude % 30
            part = int(degree * 7 / 30)
            result[planet] = ((sign * 7 + part) * (360/84)) % 360
        return result
    
    def _calculate_dasamsa(self, planets: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """D10 chart - Divide each sign into 10 parts"""
        result = {}
        for planet, pos in planets.items():
            longitude = pos['longitude']
            sign = int(longitude / 30)
            degree = longitude % 30
            part = int(degree * 10 / 30)
            result[planet] = ((sign * 10 + part) * 3) % 360
        return result
    
    def _calculate_dwadasamsa(self, planets: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """D12 chart - Divide each sign into 12 parts"""
        result = {}
        for planet, pos in planets.items():
            longitude = pos['longitude']
            sign = int(longitude / 30)
            degree = longitude % 30
            part = int(degree * 12 / 30)
            result[planet] = ((sign * 12 + part) * 2.5) % 360
        return result
    
    def _calculate_shodasamsa(self, planets: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """D16 chart - Divide each sign into 16 parts"""
        result = {}
        for planet, pos in planets.items():
            longitude = pos['longitude']
            sign = int(longitude / 30)
            degree = longitude % 30
            part = int(degree * 16 / 30)
            result[planet] = ((sign * 16 + part) * (360/192)) % 360
        return result
    
    def _calculate_vimshamsa(self, planets: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """D20 chart - Divide each sign into 20 parts"""
        result = {}
        for planet, pos in planets.items():
            longitude = pos['longitude']
            sign = int(longitude / 30)
            degree = longitude % 30
            part = int(degree * 20 / 30)
            result[planet] = ((sign * 20 + part) * (360/240)) % 360
        return result
    
    def _calculate_chaturvimshamsa(self, planets: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """D24 chart - Divide each sign into 24 parts"""
        result = {}
        for planet, pos in planets.items():
            longitude = pos['longitude']
            sign = int(longitude / 30)
            degree = longitude % 30
            part = int(degree * 24 / 30)
            result[planet] = ((sign * 24 + part) * (360/288)) % 360
        return result
    
    def _calculate_nakshatramsa(self, planets: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """D27 chart - Based on Nakshatras"""
        result = {}
        for planet, pos in planets.items():
            longitude = pos['longitude']
            nakshatra = int(longitude * 27 / 360)
            result[planet] = (nakshatra * (360/27)) % 360
        return result
    
    def _calculate_trimsamsa(self, planets: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """D30 chart - Divide each sign into 30 parts"""
        result = {}
        for planet, pos in planets.items():
            longitude = pos['longitude']
            sign = int(longitude / 30)
            degree = longitude % 30
            part = int(degree * 30 / 30)
            result[planet] = ((sign * 30 + part) * (360/360)) % 360
        return result
    
    def _calculate_khavedamsa(self, planets: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """D40 chart - Divide each sign into 40 parts"""
        result = {}
        for planet, pos in planets.items():
            longitude = pos['longitude']
            sign = int(longitude / 30)
            degree = longitude % 30
            part = int(degree * 40 / 30)
            result[planet] = ((sign * 40 + part) * (360/480)) % 360
        return result
    
    def _calculate_akshavedamsa(self, planets: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """D45 chart - Divide each sign into 45 parts"""
        result = {}
        for planet, pos in planets.items():
            longitude = pos['longitude']
            sign = int(longitude / 30)
            degree = longitude % 30
            part = int(degree * 45 / 30)
            result[planet] = ((sign * 45 + part) * (360/540)) % 360
        return result
    
    def _calculate_shashtyamsa(self, planets: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """D60 chart - Divide each sign into 60 parts"""
        result = {}
        for planet, pos in planets.items():
            longitude = pos['longitude']
            sign = int(longitude / 30)
            degree = longitude % 30
            part = int(degree * 60 / 30)
            result[planet] = ((sign * 60 + part) * (360/720)) % 360
        return result
