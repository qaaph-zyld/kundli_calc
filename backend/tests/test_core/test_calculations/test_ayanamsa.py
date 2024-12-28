"""Test ayanamsa calculations."""
import pytest
from datetime import datetime
from app.core.calculations.ayanamsa import EnhancedAyanamsaManager


@pytest.fixture
def ayanamsa_manager():
    """Get ayanamsa manager instance."""
    return EnhancedAyanamsaManager()


def test_calculate_precise_ayanamsa(ayanamsa_manager):
    """Test ayanamsa calculation."""
    # Test case: J2000.0 epoch
    dt = datetime(2000, 1, 1, 12, 0)
    ayanamsa = ayanamsa_manager.calculate_precise_ayanamsa(dt)
    assert isinstance(ayanamsa, float)
    # Lahiri ayanamsa at J2000.0 should be approximately 23.85 degrees
    assert abs(ayanamsa - 23.85) < 0.1


def test_supported_systems(ayanamsa_manager):
    """Test supported ayanamsa systems."""
    systems = ayanamsa_manager.supported_systems
    assert isinstance(systems, set)
    assert "LAHIRI" in systems
    assert "RAMAN" in systems
    assert "KRISHNAMURTI" in systems


def test_invalid_system(ayanamsa_manager):
    """Test invalid ayanamsa system."""
    dt = datetime(2000, 1, 1, 12, 0)
    with pytest.raises(ValueError):
        ayanamsa_manager.calculate_precise_ayanamsa(dt, system="INVALID")
