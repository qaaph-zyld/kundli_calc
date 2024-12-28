"""Test configuration module."""
import os
import sys
from unittest.mock import Mock

# Set test environment before importing any modules
os.environ["ENV"] = "test"

import pytest
from sqlalchemy.orm import Session
from app.core.database import get_db, init_test_db, cleanup_test_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment."""
    # Initialize test database
    init_test_db()
    
    yield
    
    # Clean up test database
    cleanup_test_db()


@pytest.fixture
def db() -> Session:
    """Get database session."""
    db = next(get_db())
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture(autouse=True)
def mock_swisseph():
    """Mock swisseph module."""
    class MockSwisseph:
        """Mock swisseph class."""
        def __init__(self):
            """Initialize mock swisseph."""
            self.MOON = 1
            self.SUN = 0
            self.MARS = 4
            self.MERCURY = 2
            self.JUPITER = 5
            self.VENUS = 3
            self.SATURN = 6
            self.TRUE_NODE = 11
            self.MEAN_NODE = 10
            self.MEAN_APOG = 12
            self.CHIRON = 15
            self.PHOLUS = 16
            self.CERES = 17
            self.PALLAS = 18
            self.JUNO = 19
            self.VESTA = 20
            
            # Flags
            self.FLG_SWIEPH = 2
            self.FLG_SPEED = 256
            self.FLG_TOPOCTR = 32768
            
            # Sidereal modes
            self.SIDM_LAHIRI = 1
            self.SIDM_RAMAN = 3
            self.SIDM_USHASHASHI = 4
            self.SIDM_KRISHNAMURTI = 5
            
            # House systems
            self.HOUSES_PLACIDUS = b'P'
            self.HOUSES_KOCH = b'K'
            self.HOUSES_PORPHYRIUS = b'O'
            self.HOUSES_REGIOMONTANUS = b'R'
            self.HOUSES_CAMPANUS = b'C'
            self.HOUSES_EQUAL = b'E'
            self.HOUSES_VEHLOW = b'V'
            self.HOUSES_MERIDIAN = b'X'
            self.HOUSES_HORIZONTAL = b'H'
            self.HOUSES_POLICH_PAGE = b'T'
            self.HOUSES_ALCABITIUS = b'B'
            self.HOUSES_MORINUS = b'M'
            self.HOUSES_WHOLE_SIGN = b'W'
            self.HOUSES_AXIAL = b'A'
            self.HOUSES_EQUAL_2 = b'D'
            self.HOUSES_EQUAL_3 = b'N'
            self.HOUSES_CARTER = b'F'
            self.HOUSES_SUNSHINE = b'U'
            self.HOUSES_SAVARD = b'G'
            self.HOUSES_PISA = b'I'
            self.HOUSES_GAUQUELIN = b'L'
            self.HOUSES_KRUSINSKI = b'Y'
        
        def swe_set_ephe_path(self, path):
            """Mock set ephemeris path."""
            pass
        
        def swe_set_sid_mode(self, mode, t0=0, ayan_t0=0):
            """Mock set sidereal mode."""
            pass
        
        def swe_calc_ut(self, julday, planet, flags):
            """Mock calculate planet position."""
            return [[0, 0, 0, 0, 0, 0], 0]
        
        def swe_houses_ex(self, julday, lat, lon, hsys):
            """Mock calculate houses."""
            return [[0] * 36, [0] * 10, [0] * 6]
        
        def swe_julday(self, year, month, day, hour):
            """Mock calculate Julian day."""
            return 0.0
        
        def swe_revjul(self, julday, gregflag=1):
            """Mock reverse Julian day."""
            return [2000, 1, 1, 0.0]
        
        def swe_calc(self, julday, planet, flags):
            """Mock calculate planet position."""
            return [[0, 0, 0, 0, 0, 0], 0]
        
        def swe_close(self):
            """Mock close ephemeris."""
            pass
    
    # Create mock module
    mock_swe = MockSwisseph()
    sys.modules["swisseph"] = mock_swe
    yield mock_swe
    del sys.modules["swisseph"]
