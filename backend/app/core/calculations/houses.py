from datetime import datetime
import swisseph as swe
from .astronomical import Location

class HouseCalculator:
    def __init__(self, house_system: str = 'P'):
        """
        Initialize house calculator with specified house system.
        Default is Placidus ('P'). Other options:
        - 'K': Koch
        - 'O': Porphyrius
        - 'R': Regiomontanus
        - 'C': Campanus
        - 'E': Equal
        - 'W': Whole sign
        """
        self.house_system = house_system
        
    def calculate_houses(
        self,
        datetime_utc: datetime,
        location: Location
    ) -> dict:
        """Calculate house cusps and angles for given time and location."""
        julian_day = swe.julday(
            datetime_utc.year,
            datetime_utc.month,
            datetime_utc.day,
            datetime_utc.hour + datetime_utc.minute/60.0
        )
        
        # Calculate houses
        houses = swe.houses(
            julian_day,
            location.latitude,
            location.longitude,
            bytes(self.house_system, 'utf-8')
        )
        
        # Extract house cusps and angles
        house_cusps = list(houses[0])  # Convert from tuple to list
        ascendant = houses[1][0]  # Ascendant
        midheaven = houses[1][1]  # Midheaven (MC)
        armc = houses[1][2]  # ARMC
        vertex = houses[1][3]  # Vertex
        
        return {
            'cusps': house_cusps,
            'ascendant': ascendant,
            'midheaven': midheaven,
            'armc': armc,
            'vertex': vertex
        }
