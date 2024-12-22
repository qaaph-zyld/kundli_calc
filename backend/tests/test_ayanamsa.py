import pytest
from datetime import datetime
from app.core.calculations.ayanamsa import EnhancedAyanamsaManager

@pytest.fixture
def ayanamsa_manager():
    return EnhancedAyanamsaManager()

@pytest.fixture
def test_datetime():
    return datetime(2024, 1, 1, 12, 0, 0)  # Noon on Jan 1, 2024

class TestAyanamsaCalculations:
    def test_lahiri_ayanamsa(self, ayanamsa_manager, test_datetime):
        """Test Lahiri ayanamsa calculation"""
        ayanamsa = ayanamsa_manager.calculate_precise_ayanamsa(
            test_datetime,
            "Lahiri"
        )
        # Lahiri ayanamsa for 2024 should be around 24°
        assert 23.5 <= ayanamsa <= 24.5
    
    def test_raman_ayanamsa(self, ayanamsa_manager, test_datetime):
        """Test Raman ayanamsa calculation"""
        ayanamsa = ayanamsa_manager.calculate_precise_ayanamsa(
            test_datetime,
            "Raman"
        )
        # Raman ayanamsa should be slightly different from Lahiri
        assert 23.5 <= ayanamsa <= 24.5
        
        # Compare with Lahiri
        lahiri = ayanamsa_manager.calculate_precise_ayanamsa(
            test_datetime,
            "Lahiri"
        )
        assert abs(ayanamsa - lahiri) < 0.5  # Should be close but not identical
    
    def test_krishnamurti_ayanamsa(self, ayanamsa_manager, test_datetime):
        """Test Krishnamurti ayanamsa calculation"""
        ayanamsa = ayanamsa_manager.calculate_precise_ayanamsa(
            test_datetime,
            "Krishnamurti"
        )
        # Krishnamurti ayanamsa should be close to Lahiri
        assert 23.5 <= ayanamsa <= 24.5
        
        # Compare with Lahiri
        lahiri = ayanamsa_manager.calculate_precise_ayanamsa(
            test_datetime,
            "Lahiri"
        )
        assert abs(ayanamsa - lahiri) < 0.5
    
    def test_yukteshwar_ayanamsa(self, ayanamsa_manager, test_datetime):
        """Test Yukteshwar ayanamsa calculation"""
        ayanamsa = ayanamsa_manager.calculate_precise_ayanamsa(
            test_datetime,
            "Yukteshwar"
        )
        # Yukteshwar ayanamsa should be within reasonable range
        assert 23.0 <= ayanamsa <= 24.5
    
    def test_historical_ayanamsa(self, ayanamsa_manager):
        """Test ayanamsa calculation for historical date"""
        historical_date = datetime(1900, 1, 1, 12, 0, 0)
        ayanamsa = ayanamsa_manager.calculate_precise_ayanamsa(
            historical_date,
            "Lahiri"
        )
        # Ayanamsa should be less for historical date
        assert 20.0 <= ayanamsa <= 22.0
    
    def test_future_ayanamsa(self, ayanamsa_manager):
        """Test ayanamsa calculation for future date"""
        future_date = datetime(2050, 1, 1, 12, 0, 0)
        ayanamsa = ayanamsa_manager.calculate_precise_ayanamsa(
            future_date,
            "Lahiri"
        )
        # Ayanamsa should be more for future date
        assert 24.5 <= ayanamsa <= 26.0
    
    def test_invalid_ayanamsa_system(self, ayanamsa_manager, test_datetime):
        """Test handling of invalid ayanamsa system"""
        with pytest.raises(ValueError):
            ayanamsa_manager.calculate_precise_ayanamsa(
                test_datetime,
                "InvalidSystem"
            )
    
    def test_ayanamsa_precision(self, ayanamsa_manager, test_datetime):
        """Test precision of ayanamsa calculation"""
        ayanamsa = ayanamsa_manager.calculate_precise_ayanamsa(
            test_datetime,
            "Lahiri"
        )
        # Should have at least 6 decimal places precision
        decimal_str = str(ayanamsa - int(ayanamsa))[2:]
        assert len(decimal_str) >= 6
    
    def test_nutation_correction(self, ayanamsa_manager, test_datetime):
        """Test nutation correction in ayanamsa calculation"""
        # Calculate with and without nutation correction
        with_nutation = ayanamsa_manager.calculate_precise_ayanamsa(
            test_datetime,
            "Lahiri",
            apply_nutation=True
        )
        
        without_nutation = ayanamsa_manager.calculate_precise_ayanamsa(
            test_datetime,
            "Lahiri",
            apply_nutation=False
        )
        
        # There should be a small difference
        assert abs(with_nutation - without_nutation) < 0.02  # Max nutation effect
    
    def test_precession_calculation(self, ayanamsa_manager):
        """Test precession calculation over time"""
        date1 = datetime(2000, 1, 1, 12, 0, 0)
        date2 = datetime(2100, 1, 1, 12, 0, 0)
        
        ayanamsa1 = ayanamsa_manager.calculate_precise_ayanamsa(
            date1,
            "Lahiri"
        )
        ayanamsa2 = ayanamsa_manager.calculate_precise_ayanamsa(
            date2,
            "Lahiri"
        )
        
        # Precession rate should be approximately 50.3 arcseconds per year
        # Over 100 years ≈ 1.4 degrees
        diff = ayanamsa2 - ayanamsa1
        assert 1.3 <= diff <= 1.5
