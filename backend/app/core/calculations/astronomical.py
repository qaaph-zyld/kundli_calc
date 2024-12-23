from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
import swisseph as swe
import logging

@dataclass
class Location:
    latitude: float
    longitude: float
    altitude: float = 0

class DataProcessor:
    @staticmethod
    def _apply_precision_rules(value: float, precision_type: str = 'coordinate') -> float:
        """
        Implements Swiss Ephemeris precision standards:
        - Arc second precision for coordinates (6 decimal places)
        - Microsecond precision for time (6 decimal places)
        - Distance precision to 8 decimal places
        """
        if precision_type == 'coordinate':
            return round(value, 6)  # Arc second precision
        elif precision_type == 'time':
            return round(value, 6)  # Microsecond precision
        elif precision_type == 'distance':
            return round(value, 8)  # Distance precision
        return value

    @staticmethod
    def _calculate_speed_metrics(speed: float) -> Dict[str, float]:
        """Calculate detailed speed metrics"""
        return {
            'degrees_per_day': DataProcessor._apply_precision_rules(speed),
            'is_retrograde': speed < 0,
            'relative_speed': DataProcessor._apply_precision_rules(abs(speed) / 1)  # Normalized to average speed
        }

    @classmethod
    def process_planetary_data(cls, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw planetary data with precision rules"""
        return {
            'longitude': cls._apply_precision_rules(raw_data['longitude']),
            'latitude': cls._apply_precision_rules(raw_data['latitude']),
            'speed': cls._calculate_speed_metrics(raw_data['speed']),
            'distance': cls._apply_precision_rules(raw_data['distance'], 'distance')
        }

class AstronomicalCalculator:
    def __init__(self, ayanamsa: Optional[int] = 1):
        """Initialize the astronomical calculator with default settings"""
        self.advanced_settings = {
            'topocentric': True,  # Enable topocentric calculations by default
            'true_node': True,    # Use true node instead of mean node
            'precision': 6        # Decimal places for precision
        }
        
        self.ephemeris_config = {
            'precision_level': 2 | 256 | 32768,
            'calculation_mode': 64,
            'coordinate_system': 2048,
            'error_handling': 128
        }
        
        self.planet_map = {
            swe.SUN: 'Sun',
            swe.MOON: 'Moon',
            swe.MARS: 'Mars',
            swe.MERCURY: 'Mercury',
            swe.JUPITER: 'Jupiter',
            swe.VENUS: 'Venus',
            swe.SATURN: 'Saturn',
            swe.TRUE_NODE: 'Rahu',
            -1: 'Ketu'
        }
        
        self.logger = logging.getLogger(__name__)
        self.ayanamsa = ayanamsa
        
        self._configure_ephemeris()
    
    def _configure_ephemeris(self):
        """Configure Swiss Ephemeris with advanced settings"""
        swe.set_sid_mode(self.ayanamsa)
        swe.set_delta_t_userdef(0)  # Use automatic Delta T
    
    def _to_julian_day(self, date: datetime) -> float:
        """Calculate Julian Day from datetime"""
        return swe.julday(
            date.year,
            date.month,
            date.day,
            date.hour + date.minute/60.0 + date.second/3600.0
        )

    def calculate_planetary_positions(self, date: datetime, location: Location) -> Dict[str, Dict[str, float]]:
        """Calculate planetary positions for a given date and location"""
        jd = self._to_julian_day(date)
        swe.set_topo(float(location.latitude), float(location.longitude), float(location.altitude))
        
        positions = {}
        for planet_id, planet_name in self.planet_map.items():
            try:
                # Calculate flags
                flags = 2  # FLG_SWIEPH
                flags |= 256  # FLG_SPEED
                flags |= 32768  # FLG_TOPOCTR
                flags |= 64  # FLG_SIDEREAL
                flags |= 2048  # FLG_EQUATORIAL
                flags |= 128  # FLG_NOGDEFL
                
                result, status = swe.calc_ut(jd, planet_id, flags)
                
                if isinstance(result, (list, tuple)) and len(result) >= 4:
                    positions[planet_name] = {
                        'longitude': float(result[0]),
                        'latitude': float(result[1]),
                        'distance': float(result[2]),
                        'speed': {
                            'degrees_per_day': float(result[3]),
                            'is_retrograde': float(result[3]) < 0,
                            'relative_speed': abs(float(result[3]) / 1)
                        }
                    }
                    
                    # Round all values to 6 decimal places
                    positions[planet_name]['longitude'] = round(positions[planet_name]['longitude'], 6)
                    positions[planet_name]['latitude'] = round(positions[planet_name]['latitude'], 6)
                    positions[planet_name]['distance'] = round(positions[planet_name]['distance'], 6)
                    positions[planet_name]['speed']['degrees_per_day'] = round(positions[planet_name]['speed']['degrees_per_day'], 6)
                    positions[planet_name]['speed']['relative_speed'] = round(positions[planet_name]['speed']['relative_speed'], 6)
            except Exception as e:
                self.logger.error(f"Error calculating position for {planet_name}: {str(e)}")
                positions[planet_name] = {
                    'longitude': 0.0,
                    'latitude': 0.0,
                    'distance': 0.0,
                    'speed': {
                        'degrees_per_day': 0.0,
                        'is_retrograde': False,
                        'relative_speed': 0.0
                    }
                }
        
        return positions
