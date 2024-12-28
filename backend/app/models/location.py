"""Location model for astrological calculations."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Location:
    """Location data for astrological calculations."""
    latitude: float
    longitude: float
    altitude: Optional[float] = 0

    def __post_init__(self):
        """Validate location data."""
        if not -90 <= self.latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90 degrees")
        if not -180 <= self.longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180 degrees")
        if self.altitude is not None and self.altitude < 0:
            raise ValueError("Altitude cannot be negative")
