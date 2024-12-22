import pytest
from app.core.calculations.divisional import EnhancedDivisionalChartEngine

@pytest.fixture
def divisional_engine():
    return EnhancedDivisionalChartEngine()

class TestDivisionalCalculations:
    def test_d1_chart(self, divisional_engine):
        """Test D1 (Rashi) chart calculation"""
        longitude = 45.5  # In Taurus
        divisions = ['D1']
        result = divisional_engine.calculate_all_divisions(longitude, divisions)
        
        assert 'D1' in result
        assert 30 <= result['D1'] < 60  # Should be in Taurus (30-60 degrees)
        assert abs(result['D1'] - longitude) < 0.000001
    
    def test_d9_chart(self, divisional_engine):
        """Test D9 (Navamsa) chart calculation"""
        longitude = 45.5  # In Taurus
        divisions = ['D9']
        result = divisional_engine.calculate_all_divisions(longitude, divisions)
        
        assert 'D9' in result
        assert 0 <= result['D9'] < 360
        # Verify correct navamsa calculation
        expected_navamsa = ((45.5 % 30) * 9 / 30 + 120) % 360  # Formula for Taurus
        assert abs(result['D9'] - expected_navamsa) < 0.000001
    
    def test_d12_chart(self, divisional_engine):
        """Test D12 (Dwadasamsa) chart calculation"""
        longitude = 45.5  # In Taurus
        divisions = ['D12']
        result = divisional_engine.calculate_all_divisions(longitude, divisions)
        
        assert 'D12' in result
        assert 0 <= result['D12'] < 360
        # Verify correct dwadasamsa calculation
        expected_d12 = ((45.5 % 30) * 12 / 30 + 30) % 360  # Formula for Taurus
        assert abs(result['D12'] - expected_d12) < 0.000001
    
    def test_d30_chart(self, divisional_engine):
        """Test D30 (Trimshamsa) chart calculation"""
        longitude = 45.5  # In Taurus
        divisions = ['D30']
        result = divisional_engine.calculate_all_divisions(longitude, divisions)
        
        assert 'D30' in result
        assert 0 <= result['D30'] < 360
    
    def test_multiple_divisions(self, divisional_engine):
        """Test calculation of multiple divisional charts"""
        longitude = 45.5
        divisions = ['D1', 'D9', 'D12', 'D30']
        result = divisional_engine.calculate_all_divisions(longitude, divisions)
        
        assert all(div in result for div in divisions)
        assert all(0 <= result[div] < 360 for div in divisions)
    
    def test_invalid_division(self, divisional_engine):
        """Test handling of invalid division request"""
        longitude = 45.5
        divisions = ['D1', 'InvalidDiv']
        
        with pytest.raises(ValueError):
            divisional_engine.calculate_all_divisions(longitude, divisions)
    
    def test_boundary_conditions(self, divisional_engine):
        """Test calculations at zodiac boundaries"""
        # Test at 0 degrees (Aries starting point)
        result_start = divisional_engine.calculate_all_divisions(0, ['D1', 'D9'])
        assert result_start['D1'] == 0
        assert result_start['D9'] == 0
        
        # Test at 359.99... degrees (end of Pisces)
        result_end = divisional_engine.calculate_all_divisions(359.99999, ['D1', 'D9'])
        assert 359 <= result_end['D1'] < 360
        assert 0 <= result_end['D9'] < 360
    
    def test_special_divisional_rules(self, divisional_engine):
        """Test special rules for divisional charts"""
        # Test odd sign special rule for D9
        leo_long = 135.5  # In Leo (odd sign)
        result_leo = divisional_engine.calculate_all_divisions(leo_long, ['D9'])
        
        # Test even sign special rule for D9
        virgo_long = 155.5  # In Virgo (even sign)
        result_virgo = divisional_engine.calculate_all_divisions(virgo_long, ['D9'])
        
        assert result_leo['D9'] != result_virgo['D9']
    
    def test_pada_calculation(self, divisional_engine):
        """Test pada (quarter) calculations"""
        longitude = 45.5  # In Taurus
        result = divisional_engine.calculate_pada(longitude)
        
        assert 1 <= result <= 4  # Pada should be between 1 and 4
    
    def test_precision_maintenance(self, divisional_engine):
        """Test precision maintenance in calculations"""
        longitude = 45.5432198  # High precision input
        divisions = ['D1', 'D9', 'D12']
        result = divisional_engine.calculate_all_divisions(longitude, divisions)
        
        # Verify precision is maintained
        for div in divisions:
            decimal_str = str(result[div] - int(result[div]))[2:]
            assert len(decimal_str) >= 6  # Should maintain at least 6 decimal places
