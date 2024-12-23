import pytest
from datetime import datetime
from decimal import Decimal
from app.core.calculations.astronomical import AstronomicalCalculator, Location

def test_astronomical_calculator_initialization():
    calc = AstronomicalCalculator()
    assert calc is not None
    assert hasattr(calc, 'ephemeris_config')
    assert hasattr(calc, 'advanced_settings')

def test_planetary_positions_calculation(mocker):
    # Mock swisseph functions
    def mock_calc_ut(jd, planet_id, flags):
        # Return different values for each planet
        positions = {
            0: [60.0, 0.0, 0.0, 1.0],  # Sun
            1: [120.0, 0.0, 0.0, 1.0],  # Moon
            2: [180.0, 0.0, 0.0, 1.0],  # Mars
            3: [240.0, 0.0, 0.0, 1.0],  # Mercury
            4: [300.0, 0.0, 0.0, 1.0],  # Jupiter
            5: [330.0, 0.0, 0.0, 1.0],  # Venus
            6: [30.0, 0.0, 0.0, 1.0],   # Saturn
            10: [150.0, 0.0, 0.0, 1.0], # Mean Node (Rahu)
            11: [270.0, 0.0, 0.0, 1.0]  # Mean Apogee (Ketu)
        }
        return (positions.get(planet_id, [0.0, 0.0, 0.0, 0.0]), 0)

    # Mock the planet IDs
    mocker.patch('swisseph.SUN', 0)
    mocker.patch('swisseph.MOON', 1)
    mocker.patch('swisseph.MARS', 2)
    mocker.patch('swisseph.MERCURY', 3)
    mocker.patch('swisseph.JUPITER', 4)
    mocker.patch('swisseph.VENUS', 5)
    mocker.patch('swisseph.SATURN', 6)
    mocker.patch('swisseph.MEAN_NODE', 10)
    mocker.patch('swisseph.MEAN_APOG', 11)
    
    # Mock the calculation function
    mocker.patch('swisseph.calc_ut', side_effect=mock_calc_ut)
    mocker.patch('swisseph.set_topo')

    calc = AstronomicalCalculator()
    test_date = datetime(2024, 1, 1, 12, 0)
    test_location = Location(
        latitude=Decimal('28.6139'),
        longitude=Decimal('77.2090'),
        altitude=Decimal('0')
    )  # New Delhi

    positions = calc.calculate_planetary_positions(test_date, test_location)

    # Verify all required planets are present
    required_planets = {'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu'}
    assert all(planet in positions for planet in required_planets)

    # Verify position format
    for planet in required_planets:
        assert 'longitude' in positions[planet]
        assert 'latitude' in positions[planet]
        assert 'distance' in positions[planet]
        assert 'speed' in positions[planet]
        assert isinstance(positions[planet]['longitude'], float)
        assert isinstance(positions[planet]['latitude'], float)
        assert isinstance(positions[planet]['distance'], float)

def test_topocentric_calculation(mocker):
    # Mock the planet IDs
    mocker.patch('swisseph.SUN', 0)
    mocker.patch('swisseph.MOON', 1)
    mocker.patch('swisseph.MARS', 2)
    mocker.patch('swisseph.MERCURY', 3)
    mocker.patch('swisseph.JUPITER', 4)
    mocker.patch('swisseph.VENUS', 5)
    mocker.patch('swisseph.SATURN', 6)
    mocker.patch('swisseph.MEAN_NODE', 10)
    mocker.patch('swisseph.MEAN_APOG', 11)

    calc = AstronomicalCalculator()
    test_date = datetime(2024, 1, 1, 12, 0)

    # Test two different locations
    delhi = Location(
        latitude=Decimal('28.6139'),
        longitude=Decimal('77.2090'),
        altitude=Decimal('0')
    )
    new_york = Location(
        latitude=Decimal('40.7128'),
        longitude=Decimal('-74.0060'),
        altitude=Decimal('0')
    )

    # Track the current location for mocking
    current_location = {'lat': 0, 'lon': 0}

    # Mock swisseph functions
    def mock_set_topo(lat, lon, alt):
        current_location['lat'] = lat
        current_location['lon'] = lon

    def mock_calc_ut(jd, planet_id, flags):
        # Return different values for each planet based on location
        if planet_id == 1:  # Moon
            if abs(current_location['lat'] - float(delhi.latitude)) < 0.0001:
                return ([120.5, 10.0, 0.0, 0.5], 0)
            elif abs(current_location['lat'] - float(new_york.latitude)) < 0.0001:
                return ([121.2, 10.0, 0.0, 0.5], 0)
        # Return standard values for other planets
        positions = {
            0: [60.0, 0.0, 0.0, 1.0],  # Sun
            2: [180.0, 0.0, 0.0, 1.0],  # Mars
            3: [240.0, 0.0, 0.0, 1.0],  # Mercury
            4: [300.0, 0.0, 0.0, 1.0],  # Jupiter
            5: [330.0, 0.0, 0.0, 1.0],  # Venus
            6: [30.0, 0.0, 0.0, 1.0],   # Saturn
            10: [150.0, 0.0, 0.0, 1.0], # Mean Node (Rahu)
            11: [270.0, 0.0, 0.0, 1.0]  # Mean Apogee (Ketu)
        }
        return (positions.get(planet_id, [0.0, 0.0, 0.0, 0.0]), 0)

    # Mock the functions with proper argument capture
    mocker.patch('swisseph.set_topo', side_effect=mock_set_topo)
    mocker.patch('swisseph.calc_ut', side_effect=mock_calc_ut)

    delhi_positions = calc.calculate_planetary_positions(test_date, delhi)
    ny_positions = calc.calculate_planetary_positions(test_date, new_york)

    # Debug output
    print(f"Delhi Moon longitude: {delhi_positions['Moon']['longitude']}")
    print(f"NY Moon longitude: {ny_positions['Moon']['longitude']}")

    # Positions should be slightly different due to topocentric correction
    assert abs(float(delhi_positions['Moon']['longitude']) - float(ny_positions['Moon']['longitude'])) > 0.1

def test_speed_calculations(mocker):
    calc = AstronomicalCalculator()
    test_date = datetime(2024, 1, 1, 12, 0)
    location = Location(
        latitude=Decimal('0'), 
        longitude=Decimal('0'),
        altitude=Decimal('0')
    )
    
    def mock_calc_ut(jd, planet_id, flags):
        return [0, 0, 0, 0.5], []
    
    mocker.patch('swisseph.calc_ut', side_effect=mock_calc_ut)
    mocker.patch('swisseph.get_planet_name', return_value='')
    
    positions = calc.calculate_planetary_positions(test_date, location)
    
    # Verify speed metrics
    for planet, data in positions.items():
        speed_data = data['speed']
        assert 'degrees_per_day' in speed_data
        assert 'is_retrograde' in speed_data
        assert 'relative_speed' in speed_data
        assert isinstance(speed_data['degrees_per_day'], float)
        assert isinstance(speed_data['is_retrograde'], bool)
        assert isinstance(speed_data['relative_speed'], float)

def test_precision_and_rounding(mocker):
    calc = AstronomicalCalculator()
    test_date = datetime(2024, 1, 1, 12, 0)
    location = Location(
        latitude=Decimal('0'), 
        longitude=Decimal('0'),
        altitude=Decimal('0')
    )
    
    def mock_calc_ut(jd, planet_id, flags):
        return [123.456789, -1.234567, 1.234567, 0.987654], []
    
    mocker.patch('swisseph.calc_ut', side_effect=mock_calc_ut)
    mocker.patch('swisseph.get_planet_name', return_value='')
    
    positions = calc.calculate_planetary_positions(test_date, location)
    
    # Check precision of calculations
    for planet, data in positions.items():
        # Longitude should have 6 decimal places
        assert len(str(data['longitude']).split('.')[-1]) <= 6
        # Speed should have appropriate precision
        assert len(str(data['speed']['degrees_per_day']).split('.')[-1]) <= 6

def test_error_handling():
    calc = AstronomicalCalculator()
    future_date = datetime(2100, 1, 1, 12, 0)  # Far future date
    location = Location(
        latitude=Decimal('0'), 
        longitude=Decimal('0'),
        altitude=Decimal('0')
    )
    
    # Should still calculate without raising errors
    positions = calc.calculate_planetary_positions(future_date, location)
    assert positions is not None
    
    # Test invalid location
    invalid_location = Location(
        latitude=Decimal('91'), 
        longitude=Decimal('181'),
        altitude=Decimal('0')
    )  # Invalid coordinates
    positions = calc.calculate_planetary_positions(datetime.now(), invalid_location)
    assert positions is not None  # Should handle invalid input gracefully
