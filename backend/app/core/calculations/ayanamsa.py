import logging
from datetime import datetime
import swisseph as swe

class EnhancedAyanamsaManager:
    """Enhanced Ayanamsa Manager with precise calculations"""
    
    def __init__(self):
        """Initialize the ayanamsa manager"""
        # Configure logging
        self.logger = logging.getLogger(__name__)
        
        # Define supported ayanamsa systems
        self.ayanamsa_systems = {
            'LAHIRI': swe.SIDM_LAHIRI,
            'RAMAN': swe.SIDM_RAMAN,
            'KRISHNAMURTI': swe.SIDM_KRISHNAMURTI,
            'DJWHAL_KHUL': swe.SIDM_DJWHAL_KHUL,
            'YUKTESHWAR': swe.SIDM_YUKTESHWAR,
            'JN_BHASIN': swe.SIDM_JN_BHASIN,
            'BABYL_KUGLER1': swe.SIDM_BABYL_KUGLER1,
            'BABYL_KUGLER2': swe.SIDM_BABYL_KUGLER2,
            'BABYL_KUGLER3': swe.SIDM_BABYL_KUGLER3,
            'BABYL_HUBER': swe.SIDM_BABYL_HUBER,
            'BABYL_ETPSC': swe.SIDM_BABYL_ETPSC,
            'ALDEBARAN_15TAU': swe.SIDM_ALDEBARAN_15TAU,
            'HIPPARCHOS': swe.SIDM_HIPPARCHOS,
            'SASSANIAN': swe.SIDM_SASSANIAN,
            'GALCENT_0SAG': swe.SIDM_GALCENT_0SAG,
            'J2000': swe.SIDM_J2000,
            'J1900': swe.SIDM_J1900,
            'B1950': swe.SIDM_B1950,
            'SURYASIDDHANTA': swe.SIDM_SURYASIDDHANTA,
            'SURYASIDDHANTA_MSUN': swe.SIDM_SURYASIDDHANTA_MSUN,
            'ARYABHATA': swe.SIDM_ARYABHATA,
            'ARYABHATA_MSUN': swe.SIDM_ARYABHATA_MSUN,
            'SS_REVATI': swe.SIDM_SS_REVATI,
            'SS_CITRA': swe.SIDM_SS_CITRA,
            'TRUE_CITRA': swe.SIDM_TRUE_CITRA,
            'TRUE_REVATI': swe.SIDM_TRUE_REVATI,
            'TRUE_PUSHYA': swe.SIDM_TRUE_PUSHYA,
            'GALCENT_RGILBRAND': swe.SIDM_GALCENT_RGILBRAND,
            'GALEQU_IAU1958': swe.SIDM_GALEQU_IAU1958,
            'GALEQU_TRUE': swe.SIDM_GALEQU_TRUE,
            'GALEQU_MULA': swe.SIDM_GALEQU_MULA,
            'GALALIGN_MARDYKS': swe.SIDM_GALALIGN_MARDYKS,
            'TRUE_MULA': swe.SIDM_TRUE_MULA,
            'GALCENT_MULA_WILHELM': swe.SIDM_GALCENT_MULA_WILHELM,
            'ARYABHATA_522': swe.SIDM_ARYABHATA_522,
            'BABYL_BRITTON': swe.SIDM_BABYL_BRITTON,
            'TRUE_SHEORAN': swe.SIDM_TRUE_SHEORAN,
            'GALCENT_COCHRANE': swe.SIDM_GALCENT_COCHRANE,
            'GALEQU_FIORENZA': swe.SIDM_GALEQU_FIORENZA,
            'VALENS_MOON': swe.SIDM_VALENS_MOON,
            'LAHIRI_1940': swe.SIDM_LAHIRI_1940,
            'LAHIRI_VP285': swe.SIDM_LAHIRI_VP285,
            'KRISHNAMURTI_VP291': swe.SIDM_KRISHNAMURTI_VP291,
            'LAHIRI_ICRC': swe.SIDM_LAHIRI_ICRC
        }
        
        # Define base values for each system at J2000
        self.base_values = {
            'LAHIRI': 23.853,
            'RAMAN': 23.853,
            'KRISHNAMURTI': 23.853,
            'DJWHAL_KHUL': 23.853,
            'YUKTESHWAR': 23.853,
            'JN_BHASIN': 23.853
        }
        
        # Annual precession rate in arc seconds
        self.precession_rate = 50.27  # IAU 2006 value
        
        # Define J2000 epoch
        self.j2000_epoch = datetime(2000, 1, 1, 12, 0)  # For datetime comparisons
        self.j2000_jd = 2451545.0  # JD for January 1, 2000, 12:00 TT
        
        # Flag to enable or disable nutation correction
        self.include_nutation = True
    
    def calculate_precise_ayanamsa(self, date: datetime, system: str = 'LAHIRI', apply_nutation: bool = True) -> float:
        """Calculate precise ayanamsa value for a given date and system"""
        if system not in self.ayanamsa_systems:
            raise ValueError(f"Unsupported ayanamsa system: {system}")
        
        jd = self._to_julian_day(date)
        
        # Set sidereal mode based on the selected ayanamsa system
        swe.set_sid_mode(self.ayanamsa_systems[system])
        
        # Get base ayanamsa value
        ayanamsa = swe.get_ayanamsa_ut(jd)
        
        # Add nutation correction if enabled
        if apply_nutation:
            nutation = self._calculate_nutation(jd)
            ayanamsa += nutation
        
        return round(ayanamsa, 6)

    def _to_julian_day(self, date: datetime) -> float:
        """Calculate Julian Day from datetime"""
        return swe.julday(
            date.year,
            date.month,
            date.day,
            date.hour + date.minute/60.0 + date.second/3600.0
        )

    def _calculate_nutation(self, jd: float) -> float:
        """Calculate nutation in longitude"""
        try:
            # Get nutation in longitude from Swiss Ephemeris
            nut_long, nut_obl = swe.nutation(jd)
            return nut_long / 3600.0  # Convert from arcseconds to degrees
        except Exception as e:
            self.logger.error(f"Error calculating nutation: {str(e)}")
            return 0.0

    def _get_nutation(self, jd: float) -> float:
        """Alias for _calculate_nutation for test compatibility"""
        return self._calculate_nutation(jd)

    def _apply_historical_correction(self, value: float, datetime_utc: datetime) -> float:
        """Alias for _calculate_historical_correction for test compatibility"""
        return value + self._calculate_historical_correction(datetime_utc)

    def _calculate_historical_correction(self, datetime_utc: datetime) -> float:
        """Apply historical correction for dates before J2000"""
        if datetime_utc < self.j2000_epoch:
            years_before_j2000 = (self.j2000_epoch - datetime_utc).days / 365.25
            correction = years_before_j2000 * 0.0001  # Small correction factor
            return -round(correction, 6)
        return 0.0
