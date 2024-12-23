from datetime import datetime
import swisseph as swe
from decimal import Decimal
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
            float(location.latitude),
            float(location.longitude),
            bytes(self.house_system, 'utf-8')
        )
        
        # Extract house cusps and angles and convert to Decimal
        house_cusps = [Decimal(str(cusp)) for cusp in houses[0]]
        ascendant = Decimal(str(houses[1][0]))  # Ascendant
        midheaven = Decimal(str(houses[1][1]))  # Midheaven (MC)
        armc = Decimal(str(houses[1][2]))  # ARMC
        vertex = Decimal(str(houses[1][3]))  # Vertex
        
        return {
            'cusps': house_cusps,
            'ascendant': ascendant,
            'midheaven': midheaven,
            'armc': armc,
            'vertex': vertex
        }
