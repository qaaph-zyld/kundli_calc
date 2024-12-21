from dataclasses import dataclass
from datetime import datetime
import swisseph as swe

@dataclass
class Location:
    latitude: float
    longitude: float
    altitude: float = 0

class AstronomicalCalculator:
    def __init__(self, ayanamsa: int = swe.SIDM_LAHIRI):
        self.ayanamsa = ayanamsa
        swe.set_sid_mode(ayanamsa)
    
    def calculate_planetary_positions(
        self, 
        datetime_utc: datetime,
        location: Location
    ) -> dict:
        julian_day = swe.julday(
            datetime_utc.year,
            datetime_utc.month,
            datetime_utc.day,
            datetime_utc.hour + datetime_utc.minute/60.0
        )
        
        planets = {
            'Sun': swe.SUN,
            'Moon': swe.MOON,
            'Mars': swe.MARS,
            'Mercury': swe.MERCURY,
            'Jupiter': swe.JUPITER,
            'Venus': swe.VENUS,
            'Saturn': swe.SATURN,
            'Rahu': swe.MEAN_NODE,  # North Node
            'Ketu': None  # South Node (calculated from Rahu)
        }
        
        positions = {}
        for planet, planet_id in planets.items():
            if planet == 'Ketu':
                # Ketu is exactly opposite to Rahu
                rahu_pos = positions['Rahu']['longitude']
                ketu_pos = (rahu_pos + 180) % 360
                positions['Ketu'] = {'longitude': ketu_pos}
                continue
                
            flags = swe.FLG_SWIEPH | swe.FLG_SPEED
            result = swe.calc_ut(julian_day, planet_id, flags)
            
            positions[planet] = {
                'longitude': result[0][0],
                'latitude': result[0][1],
                'distance': result[0][2],
                'speed': result[0][3]
            }
        
        return positions
