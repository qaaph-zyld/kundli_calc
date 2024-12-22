import pytest
from datetime import datetime
import swisseph as swe
from app.core.calculations.astronomical import AstronomicalCalculator, Location, DataProcessor

@pytest.fixture
def astro_calc():
    return AstronomicalCalculator()

@pytest.fixture
def test_location():
    return Location(
        latitude=28.6139,  # New Delhi
        longitude=77.2090,
        altitude=216
    )

@pytest.fixture
def test_datetime():
    return datetime(2024, 1, 1, 12, 0, 0)  # Noon on Jan 1, 2024

class TestAstronomicalCalculator:
    def test_initialization(self, astro_calc):
        """Test proper initialization of calculator"""
        assert astro_calc.ayanamsa == swe.SIDM_LAHIRI
        assert 'precision_level' in astro_calc.ephemeris_config
        assert 'calculation_mode' in astro_calc.ephemeris_config
        assert 'coordinate_system' in astro_calc.ephemeris_config
        assert 'error_handling' in astro_calc.ephemeris_config
    
    def test_planetary_positions(self, astro_calc, test_location, test_datetime):
        """Test calculation of planetary positions"""
        positions = astro_calc.calculate_planetary_positions(
            test_datetime,
            test_location
        )
        
        # Verify all required planets are present
        required_planets = {
            'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter',
            'Venus', 'Saturn', 'Rahu', 'Ketu'
        }
        assert all(planet in positions for planet in required_planets)
        
        # Verify position data structure
        for planet, data in positions.items():
            assert 'longitude' in data
            assert 'latitude' in data
            assert 'distance' in data
            assert 'speed' in data
            
            # Verify value ranges
            assert 0 <= data['longitude'] < 360
            assert -90 <= data['latitude'] <= 90
            assert data['distance'] > 0
    
    def test_topocentric_calculation(self, astro_calc, test_location, test_datetime):
        """Test topocentric corrections"""
        # Calculate with and without topocentric correction
        astro_calc.advanced_settings['topocentric'] = True
        topo_positions = astro_calc.calculate_planetary_positions(
            test_datetime,
            test_location
        )
        
        astro_calc.advanced_settings['topocentric'] = False
        geo_positions = astro_calc.calculate_planetary_positions(
            test_datetime,
            test_location
        )
        
        # Verify differences in positions
        # Moon should show most significant difference
        moon_diff = abs(
            topo_positions['Moon']['longitude'] - 
            geo_positions['Moon']['longitude']
        )
        assert moon_diff > 0  # Should be some difference
        
    def test_true_node_calculation(self, astro_calc, test_location, test_datetime):
        """Test true node vs mean node calculation"""
        # Calculate with true node
        astro_calc.advanced_settings['true_node'] = True
        true_positions = astro_calc.calculate_planetary_positions(
            test_datetime,
            test_location
        )
        
        # Calculate with mean node
        astro_calc.advanced_settings['true_node'] = False
        mean_positions = astro_calc.calculate_planetary_positions(
            test_datetime,
            test_location
        )
        
        # Verify difference in Rahu position
        rahu_diff = abs(
            true_positions['Rahu']['longitude'] - 
            mean_positions['Rahu']['longitude']
        )
        assert rahu_diff > 0  # Should be some difference
    
    def test_speed_calculations(self, astro_calc, test_location, test_datetime):
        """Test planetary speed calculations"""
        positions = astro_calc.calculate_planetary_positions(
            test_datetime,
            test_location
        )
        
        # Verify speed ranges for each planet
        speed_ranges = {
            'Sun': (0.95, 1.02),     # Approx 1° per day
            'Moon': (12.0, 15.0),    # Approx 13° per day
            'Mars': (-0.5, 0.8),     # Can be retrograde
            'Mercury': (-1.5, 2.2),  # Can be retrograde
            'Jupiter': (-0.2, 0.2),  # Can be retrograde
            'Venus': (-1.2, 1.2),    # Can be retrograde
            'Saturn': (-0.1, 0.1)    # Can be retrograde
        }
        
        for planet, (min_speed, max_speed) in speed_ranges.items():
            if planet in positions:
                assert min_speed <= positions[planet]['speed'] <= max_speed
    
    def test_ketu_calculation(self, astro_calc, test_location, test_datetime):
        """Test Ketu calculation (opposite to Rahu)"""
        positions = astro_calc.calculate_planetary_positions(
            test_datetime,
            test_location
        )
        
        # Verify Ketu is exactly opposite to Rahu
        rahu_pos = positions['Rahu']['longitude']
        ketu_pos = positions['Ketu']['longitude']
        
        # Calculate the angular difference
        diff = abs(rahu_pos - ketu_pos)
        if diff > 180:
            diff = 360 - diff
            
        assert abs(diff - 180) < 0.000001  # Should be exactly 180° apart

class TestDataProcessor:
    def test_precision_rules(self):
        """Test precision rules for different types of values"""
        processor = DataProcessor()
        
        # Test coordinate precision (6 decimal places)
        coord_value = processor._apply_precision_rules(123.4567891234, 'coordinate')
        assert abs(coord_value - 123.456789) < 0.0000001
        
        # Test time precision (6 decimal places)
        time_value = processor._apply_precision_rules(12.3456789123, 'time')
        assert abs(time_value - 12.345679) < 0.0000001
        
        # Test distance precision (8 decimal places)
        dist_value = processor._apply_precision_rules(1.23456789123, 'distance')
        assert abs(dist_value - 1.23456789) < 0.000000001
    
    def test_invalid_precision_type(self):
        """Test handling of invalid precision type"""
        processor = DataProcessor()
        value = 123.456789
        
        # Should return original value for invalid type
        result = processor._apply_precision_rules(value, 'invalid_type')
        assert result == value
