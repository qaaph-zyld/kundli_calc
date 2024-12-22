from datetime import datetime
from typing import Dict, Any, Optional
import swisseph as swe

class EnhancedAyanamsaManager:
    def __init__(self):
        self.correction_factors = {
            'Lahiri': {'base': 23.85, 'annual_precession': 50.27},
            'Raman': {'base': 22.37, 'annual_precession': 50.27},
            'KP': {'base': 23.67, 'annual_precession': 50.27},
            'Krishnamurti': {'base': 23.71, 'annual_precession': 50.27},
            'Yukteshwar': {'base': 22.64, 'annual_precession': 50.27}
        }
        
        self.swe_ayanamsa_mapping = {
            'Lahiri': swe.SIDM_LAHIRI,
            'Raman': swe.SIDM_RAMAN,
            'KP': swe.SIDM_KRISHNAMURTI,  # KP uses Krishnamurti
            'Krishnamurti': swe.SIDM_KRISHNAMURTI,
            'Yukteshwar': swe.SIDM_YUKTESHWAR
        }
        
        self.historical_corrections = {
            'pre_1900': self._apply_pre1900_correction,
            'post_1900': self._apply_post1900_correction,
            'modern': self._apply_modern_correction
        }
    
    def _apply_pre1900_correction(self, value: float, year: int) -> float:
        """Apply correction for dates before 1900"""
        year_diff = 1900 - year
        correction = 0.000237 * year_diff  # Historical correction factor
        return value + correction
    
    def _apply_post1900_correction(self, value: float, year: int) -> float:
        """Apply correction for dates between 1900 and 2000"""
        year_diff = year - 1900
        correction = 0.000238 * year_diff  # Modern correction factor
        return value + correction
    
    def _apply_modern_correction(self, value: float, year: int) -> float:
        """Apply correction for dates after 2000"""
        year_diff = year - 2000
        correction = 0.000242 * year_diff  # Contemporary correction factor
        return value + correction
    
    def _get_correction_method(self, year: int):
        """Get the appropriate correction method based on the year"""
        if year < 1900:
            return self.historical_corrections['pre_1900']
        elif year < 2000:
            return self.historical_corrections['post_1900']
        else:
            return self.historical_corrections['modern']
    
    def _apply_nutation_correction(self, jd: float) -> float:
        """Apply nutation correction to the ayanamsa value"""
        nutation = swe.nutation(jd)
        return nutation[0]  # Return nutation in longitude
    
    def _apply_precession_adjustment(self, base_value: float, date: datetime) -> float:
        """Apply precession adjustment based on the date"""
        year_diff = date.year - 2000  # Reference epoch
        precession_rate = 50.27  # Precession rate in arc seconds per year
        adjustment = (precession_rate * year_diff) / 3600  # Convert to degrees
        return base_value + adjustment
    
    def _apply_correction_pipeline(
        self,
        base_ayanamsa: float,
        date: datetime,
        annual_precession: float
    ) -> float:
        """
        Apply the complete correction pipeline to the ayanamsa value
        """
        # Get Julian Day for the date
        jd = swe.julday(date.year, date.month, date.day, 
                       date.hour + date.minute/60.0 + date.second/3600.0)
        
        # Apply basic precession
        value = self._apply_precession_adjustment(base_ayanamsa, date)
        
        # Apply historical correction
        correction_method = self._get_correction_method(date.year)
        value = correction_method(value, date.year)
        
        # Apply nutation correction
        nutation = self._apply_nutation_correction(jd)
        value += nutation
        
        return value
    
    def _final_precision_adjustment(self, value: float) -> float:
        """Apply final precision adjustment to the ayanamsa value"""
        return round(value, 6)  # 6 decimal places for arc-second precision
    
    def calculate_precise_ayanamsa(
        self,
        date: datetime,
        system: str = 'Lahiri'
    ) -> float:
        """
        Calculate precise ayanamsa value for the given date and system
        
        Args:
            date: The date and time for calculation
            system: The ayanamsa system to use (Lahiri, Raman, KP, etc.)
            
        Returns:
            float: The precise ayanamsa value in degrees
        """
        if system not in self.correction_factors:
            raise ValueError(f"Unsupported ayanamsa system: {system}")
        
        # Get base values for the system
        base_ayanamsa = self.correction_factors[system]['base']
        annual_precession = self.correction_factors[system]['annual_precession']
        
        # Apply the complete correction pipeline
        corrected_value = self._apply_correction_pipeline(
            base_ayanamsa,
            date,
            annual_precession
        )
        
        # Set the ayanamsa system in Swiss Ephemeris
        swe.set_sid_mode(self.swe_ayanamsa_mapping[system])
        
        # Apply final precision adjustment
        return self._final_precision_adjustment(corrected_value)
    
    def get_available_systems(self) -> Dict[str, Dict[str, float]]:
        """Get all available ayanamsa systems and their base values"""
        return self.correction_factors
