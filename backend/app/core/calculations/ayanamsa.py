"""Enhanced Ayanamsa Manager with precise calculations and performance monitoring"""

import logging
import time
from datetime import datetime
import swisseph as swe
from functools import lru_cache, wraps
from typing import Dict, Optional, Any, List, Set
from app.core.validation.ayanamsa_validator import AyanamsaValidator, AyanamsaValidationError
from app.core.monitoring.ayanamsa_monitor import AyanamsaMonitor
from app.core.cache import CalculationCache

def profile_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        logging.info(f"{func.__name__} execution time: {execution_time:.3f}ms")
        return result
    return wrapper

class EnhancedAyanamsaManager:
    """Enhanced Ayanamsa Manager with precise calculations and performance monitoring"""
    
    def __init__(self):
        """Initialize the ayanamsa manager with monitoring"""
        # Initialize validation system
        self._validator = AyanamsaValidator()
        self._monitor = AyanamsaMonitor()
        
        # Define supported ayanamsa systems with their characteristics
        self.ayanamsa_systems = {
            'LAHIRI': {
                'id': swe.SIDM_LAHIRI,
                'historical_correction': 0.0,
                'annual_precession': 50.27  # arcseconds per year
            },
            'RAMAN': {
                'id': swe.SIDM_RAMAN,
                'historical_correction': 0.15,
                'annual_precession': 50.27
            },
            'KRISHNAMURTI': {
                'id': swe.SIDM_KRISHNAMURTI,
                'historical_correction': 0.25,
                'annual_precession': 50.27
            },
            'YUKTESHWAR': {
                'id': swe.SIDM_YUKTESHWAR,
                'historical_correction': -0.12,
                'annual_precession': 50.27
            },
            'JN_BHASIN': {
                'id': swe.SIDM_JN_BHASIN,
                'historical_correction': 0.18,
                'annual_precession': 50.27
            }
        }
        
        # Performance optimization settings
        self._cache = CalculationCache(l1_size=50, l2_size=500)
        self.include_nutation = True
        self.precision = 4  # decimal places
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        
        # Define J2000 epoch
        self.j2000_epoch = datetime(2000, 1, 1, 12, 0)  # For datetime comparisons
        self.j2000_jd = 2451545.0  # JD for January 1, 2000, 12:00 TT
        
        # Flag to enable or disable nutation correction
        self.include_nutation = True
        
        # Expose supported systems
        self.supported_systems = set(self.ayanamsa_systems.keys())
    
    def _init_system_mappings(self):
        """Initialize system ID mappings with validation"""
        for system, config in self.ayanamsa_systems.items():
            self._system_cache[system] = config['id']
    
    @lru_cache(maxsize=128)
    def calculate_precise_ayanamsa(self, date: datetime, system: str = 'LAHIRI', apply_nutation: bool = True) -> float:
        """Calculate precise ayanamsa value with monitoring"""
        try:
            with self._monitor.track_calculation():
                return self._calculate_precise_ayanamsa(date=date, system=system, apply_nutation=apply_nutation)
        except Exception as e:
            self.logger.error(f"Ayanamsa calculation failed: {str(e)}")
            raise
    
    @profile_performance
    def _calculate_precise_ayanamsa(self, date: datetime, system: str = 'LAHIRI', apply_nutation: bool = True) -> float:
        """Internal method for ayanamsa calculation with enhanced precision"""
        # Validate inputs
        if system not in self.ayanamsa_systems:
            raise ValueError(f"Invalid ayanamsa system: {system}")
        
        try:
            jd = self._to_julian_day(date)
            system_config = self.ayanamsa_systems[system]
            
            # Set ayanamsa system
            swe.set_sid_mode(system_config['id'])
            
            # Calculate base ayanamsa
            ayanamsa = float(swe.get_ayanamsa_ut(jd))  # Ensure float type
            
            # Apply historical correction if any
            ayanamsa += float(system_config['historical_correction'])
            
            # Apply nutation if requested
            if apply_nutation and self.include_nutation:
                nutation = float(self._calculate_nutation(jd))
                ayanamsa += nutation / 3600.0  # Convert arcseconds to degrees
            
            # Apply precession correction
            years_since_j2000 = (jd - 2451545.0) / 365.25
            precession_correction = (float(system_config['annual_precession']) * 
                                   years_since_j2000) / 3600.0
            ayanamsa += precession_correction
            
            return round(ayanamsa, self.precision)
            
        except Exception as e:
            self.logger.error(f"Calculation error: {str(e)}")
            raise RuntimeError(f"Failed to calculate ayanamsa: {str(e)}")
    
    @lru_cache(maxsize=32)
    def _calculate_nutation(self, jd: float) -> float:
        """Calculate nutation with minimal caching for memory efficiency"""
        nutation_long, _ = swe.nutation(jd)
        return nutation_long  # Return nutation in arcseconds
    
    @staticmethod
    def _to_julian_day(date: datetime) -> float:
        """Convert datetime to Julian Day with high precision"""
        return swe.julday(
            date.year,
            date.month,
            date.day,
            date.hour + date.minute/60.0 + date.second/3600.0
        )
    
    def validate_system(self, system: str) -> bool:
        """Validate ayanamsa system name"""
        return system in self.ayanamsa_systems
    
    def get_system_info(self, system: str) -> Dict[str, Any]:
        """Get detailed information about an ayanamsa system"""
        if not self.validate_system(system):
            raise ValueError(f"Invalid ayanamsa system: {system}")
            
        return {
            'name': system,
            'historical_correction': self.ayanamsa_systems[system]['historical_correction'],
            'annual_precession': self.ayanamsa_systems[system]['annual_precession']
        }
    
    def get_available_systems(self) -> List[str]:
        """Get list of supported ayanamsa systems"""
        return list(self.ayanamsa_systems.keys())
    
    def compare_systems(self, date: datetime) -> Dict[str, float]:
        """Compare ayanamsa values across different systems"""
        return {
            system: self.calculate_precise_ayanamsa(date, system)
            for system in self.ayanamsa_systems
        }

    def get_monitoring_metrics(self) -> Dict[str, Any]:
        """Get current monitoring metrics."""
        return self._monitor.get_metrics()

class AyanamsaSystem:
    """
    Implements multiple ayanamsa calculation systems
    """
    
    # Ayanamsa values for different systems at J2000.0
    base_values = {
        'lahiri': 23.85,      # Lahiri or Chitrapaksha
        'raman': 22.50,       # N.C. Lahiri / K.S. Krishnamurti
        'krishnamurti': 23.0, # K.S. Krishnamurti
        'fagan_bradley': 24.0, # Fagan-Bradley
        'yukteshwar': 22.0,   # Sri Yukteshwar
        'sassanian': 22.0,    # Sassanian or Persian
        'aldebaran': 23.0,    # True Aldebaran at 15° Taurus
        'galactic': 23.0      # Galactic Center at 0° Sagittarius
    }
    
    # Annual precession rates
    annual_precession = {
        'lahiri': 50.2388475,
        'raman': 50.2388475,
        'krishnamurti': 50.2388475,
        'fagan_bradley': 50.2388475,
        'yukteshwar': 50.2388475,
        'sassanian': 50.2388475,
        'aldebaran': 50.2388475,
        'galactic': 50.2388475
    }
    
    @classmethod
    def calculate_ayanamsa(cls,
                          date: datetime,
                          system: str = 'lahiri') -> float:
        """
        Calculate ayanamsa value for given date and system
        
        Args:
            date: Date for calculation
            system: Ayanamsa system to use
            
        Returns:
            Ayanamsa value in degrees
        """
        if system.lower() not in cls.base_values:
            raise ValueError(f"Unsupported ayanamsa system: {system}")
            
        # Get J2000.0 epoch
        j2000 = datetime(2000, 1, 1, 12, 0)
        
        # Calculate years from J2000.0
        years = (date - j2000).total_seconds() / (365.25 * 24 * 3600)
        
        # Get base value and annual precession
        base = cls.base_values[system.lower()]
        precession = cls.annual_precession[system.lower()]
        
        # Calculate ayanamsa
        ayanamsa = base + (precession * years / 3600)
        
        return ayanamsa
    
    @classmethod
    def apply_ayanamsa(cls,
                      tropical_position: float,
                      ayanamsa: float) -> float:
        """
        Convert tropical position to sidereal using ayanamsa
        
        Args:
            tropical_position: Position in tropical zodiac
            ayanamsa: Ayanamsa value to apply
            
        Returns:
            Position in sidereal zodiac
        """
        sidereal = tropical_position - ayanamsa
        
        # Normalize to 0-360 range
        while sidereal < 0:
            sidereal += 360
        while sidereal >= 360:
            sidereal -= 360
            
        return sidereal
    
    @classmethod
    def get_available_systems(cls) -> Dict[str, Dict[str, any]]:
        """Get information about available ayanamsa systems"""
        return {
            'lahiri': {
                'name': 'Lahiri / Chitrapaksha',
                'description': 'Official ayanamsa of Indian government',
                'base_value': cls.base_values['lahiri']
            },
            'raman': {
                'name': 'Raman / N.C. Lahiri',
                'description': 'Used by many Indian astrologers',
                'base_value': cls.base_values['raman']
            },
            'krishnamurti': {
                'name': 'K.S. Krishnamurti',
                'description': 'KP system ayanamsa',
                'base_value': cls.base_values['krishnamurti']
            },
            'fagan_bradley': {
                'name': 'Fagan-Bradley',
                'description': 'Western sidereal astrology',
                'base_value': cls.base_values['fagan_bradley']
            },
            'yukteshwar': {
                'name': 'Sri Yukteshwar',
                'description': 'Based on ancient calculations',
                'base_value': cls.base_values['yukteshwar']
            },
            'sassanian': {
                'name': 'Sassanian / Persian',
                'description': 'Used in Persian astrology',
                'base_value': cls.base_values['sassanian']
            },
            'aldebaran': {
                'name': 'True Aldebaran',
                'description': 'Based on fixed star Aldebaran',
                'base_value': cls.base_values['aldebaran']
            },
            'galactic': {
                'name': 'Galactic Center',
                'description': 'Based on galactic center alignment',
                'base_value': cls.base_values['galactic']
            }
        }
    
    @classmethod
    def convert_all_positions(cls,
                            positions: Dict[str, float],
                            date: datetime,
                            system: str = 'lahiri') -> Dict[str, float]:
        """
        Convert all planetary positions from tropical to sidereal
        
        Args:
            positions: Dictionary of tropical positions
            date: Date for ayanamsa calculation
            system: Ayanamsa system to use
            
        Returns:
            Dictionary of sidereal positions
        """
        ayanamsa = cls.calculate_ayanamsa(date, system)
        return {
            planet: cls.apply_ayanamsa(pos, ayanamsa)
            for planet, pos in positions.items()
        }
