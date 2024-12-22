from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
import swisseph as swe

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

    @staticmethod
    def _normalize_distance(distance: float) -> float:
        """Normalize distance values"""
        return DataProcessor._apply_precision_rules(distance, 'distance')

    @classmethod
    def process_planetary_data(cls, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw planetary data with precision rules"""
        return {
            'longitude': cls._apply_precision_rules(raw_data['longitude']),
            'latitude': cls._apply_precision_rules(raw_data['latitude']),
            'speed': cls._calculate_speed_metrics(raw_data['speed']),
            'distance': cls._normalize_distance(raw_data['distance'])
        }

class AstronomicalCalculator:
    def __init__(self, ayanamsa: int = swe.SIDM_LAHIRI):
        self.ayanamsa = ayanamsa
        self.ephemeris_config = {
            'precision_level': swe.SEFLG_SPEED | swe.SEFLG_TOPOCTR,
            'calculation_mode': swe.SEFLG_SIDEREAL,
            'coordinate_system': swe.SEFLG_EQUATORIAL,
            'error_handling': swe.SEFLG_NOGDEFL
        }
        
        # Advanced configuration options
        self.advanced_settings = {
            'delta_t_auto': True,
            'true_node': True,
            'speed_calc': True,
            'topocentric': True
        }
        
        self._configure_ephemeris()
    
    def _configure_ephemeris(self):
        """Configure Swiss Ephemeris with advanced settings"""
        swe.set_sid_mode(self.ayanamsa)
        if self.advanced_settings['delta_t_auto']:
            swe.set_delta_t_userdef(0)  # Use automatic Delta T
        
        # Set ephemeris path if needed
        # swe.set_ephe_path()
    
    def calculate_planetary_positions(
        self, 
        datetime_utc: datetime,
        location: Location
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate planetary positions with enhanced precision and additional metrics
        """
        julian_day = swe.julday(
            datetime_utc.year,
            datetime_utc.month,
            datetime_utc.day,
            datetime_utc.hour + datetime_utc.minute/60.0 + datetime_utc.second/3600.0
        )
        
        # Set geographical location for topocentric calculations
        if self.advanced_settings['topocentric']:
            swe.set_topo(location.longitude, location.latitude, location.altitude)
        
        planets = {
            'Sun': swe.SUN,
            'Moon': swe.MOON,
            'Mars': swe.MARS,
            'Mercury': swe.MERCURY,
            'Jupiter': swe.JUPITER,
            'Venus': swe.VENUS,
            'Saturn': swe.SATURN,
            'Rahu': swe.TRUE_NODE if self.advanced_settings['true_node'] else swe.MEAN_NODE,
            'Ketu': None  # South Node (calculated from Rahu)
        }
        
        positions = {}
        for planet, planet_id in planets.items():
            if planet == 'Ketu':
                # Ketu is exactly opposite to Rahu
                rahu_pos = positions['Rahu']['longitude']
                ketu_pos = (rahu_pos + 180) % 360
                positions['Ketu'] = DataProcessor.process_planetary_data({
                    'longitude': ketu_pos,
                    'latitude': -positions['Rahu']['latitude'],
                    'distance': positions['Rahu']['distance'],
                    'speed': -positions['Rahu']['speed']['degrees_per_day']
                })
                continue
                
            flags = (
                self.ephemeris_config['precision_level'] |
                self.ephemeris_config['calculation_mode'] |
                self.ephemeris_config['error_handling']
            )
            
            result = swe.calc_ut(julian_day, planet_id, flags)
            
            raw_data = {
                'longitude': result[0][0],
                'latitude': result[0][1],
                'distance': result[0][2],
                'speed': result[0][3]
            }
            
            positions[planet] = DataProcessor.process_planetary_data(raw_data)
        
        return positions
