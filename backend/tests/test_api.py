from fastapi.testclient import TestClient
from datetime import datetime
from decimal import Decimal
import pytest

def test_calculate_chart(client: TestClient, mocker):
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

    def mock_houses(jd, lat, lon, hsys):
        cusps = [Decimal('30.0'), Decimal('60.0'), Decimal('90.0'), Decimal('120.0'), 
                Decimal('150.0'), Decimal('180.0'), Decimal('210.0'), Decimal('240.0'), 
                Decimal('270.0'), Decimal('300.0'), Decimal('330.0'), Decimal('360.0')]
        ascmc = [Decimal('0.0'), Decimal('90.0'), Decimal('180.0'), Decimal('270.0')]  # Asc, MC, Armc, Vertex
        return (cusps, ascmc)

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
    
    # Mock the calculation functions
    mocker.patch('swisseph.calc_ut', side_effect=mock_calc_ut)
    mocker.patch('swisseph.set_topo')
    mocker.patch('swisseph.houses', side_effect=mock_houses)
    mocker.patch('swisseph.set_sid_mode')

    # Mock aspect calculation
    mocker.patch('app.core.calculations.aspects.EnhancedAspectCalculator.calculate_aspects', return_value=[])

    # Mock the planetary positions calculation to return Decimal values
    def mock_calculate_planetary_positions(date, location):
        return {
            'Sun': {'longitude': Decimal('60.0'), 'latitude': Decimal('0.0'), 'distance': Decimal('0.0'), 'speed': Decimal('1.0')},
            'Moon': {'longitude': Decimal('120.0'), 'latitude': Decimal('0.0'), 'distance': Decimal('0.0'), 'speed': Decimal('1.0')},
            'Mars': {'longitude': Decimal('180.0'), 'latitude': Decimal('0.0'), 'distance': Decimal('0.0'), 'speed': Decimal('1.0')},
            'Mercury': {'longitude': Decimal('240.0'), 'latitude': Decimal('0.0'), 'distance': Decimal('0.0'), 'speed': Decimal('1.0')},
            'Jupiter': {'longitude': Decimal('300.0'), 'latitude': Decimal('0.0'), 'distance': Decimal('0.0'), 'speed': Decimal('1.0')},
            'Venus': {'longitude': Decimal('330.0'), 'latitude': Decimal('0.0'), 'distance': Decimal('0.0'), 'speed': Decimal('1.0')},
            'Saturn': {'longitude': Decimal('30.0'), 'latitude': Decimal('0.0'), 'distance': Decimal('0.0'), 'speed': Decimal('1.0')},
            'Rahu': {'longitude': Decimal('150.0'), 'latitude': Decimal('0.0'), 'distance': Decimal('0.0'), 'speed': Decimal('0.0')},
            'Ketu': {'longitude': Decimal('270.0'), 'latitude': Decimal('0.0'), 'distance': Decimal('0.0'), 'speed': Decimal('0.0')}
        }

    mocker.patch('app.core.calculations.astronomical.AstronomicalCalculator.calculate_planetary_positions', side_effect=mock_calculate_planetary_positions)

    # Mock house calculation
    def mock_calculate_houses(datetime_utc, location):
        return {
            'cusps': [Decimal('30.0'), Decimal('60.0'), Decimal('90.0'), Decimal('120.0'), 
                    Decimal('150.0'), Decimal('180.0'), Decimal('210.0'), Decimal('240.0'), 
                    Decimal('270.0'), Decimal('300.0'), Decimal('330.0'), Decimal('360.0')],
            'ascendant': Decimal('0.0'),
            'midheaven': Decimal('90.0'),
            'armc': Decimal('180.0'),
            'vertex': Decimal('270.0')
        }

    mocker.patch('app.core.calculations.houses.HouseCalculator.calculate_houses', side_effect=mock_calculate_houses)
        
    # Mock ayanamsa value
    mocker.patch('app.core.calculations.astronomical.AstronomicalCalculator.get_ayanamsa_value', return_value=Decimal('24.0'))
        
    # Mock swisseph.get_ayanamsa_ut
    mocker.patch('swisseph.get_ayanamsa_ut', return_value=24.0)

    response = client.post(
        "/api/v1/charts/calculate",
        params={
            "date_time": "2024-01-01T12:00:00Z",
            "latitude": "13.0827",
            "longitude": "80.2707",
            "altitude": "0",
            "ayanamsa": "1",
            "house_system": "P"
        }
    )
    
    assert response.status_code == 200, f"Response: {response.json()}"
    data = response.json()
    assert "planetary_positions" in data
    assert "houses" in data

def test_invalid_coordinates(client: TestClient):
    response = client.post(
        "/api/v1/charts/calculate",
        params={
            "date_time": "2024-01-01T12:00:00Z",
            "latitude": "91",  # Invalid latitude
            "longitude": "80.2707",
            "altitude": "0",
            "ayanamsa": "1",
            "house_system": "P"
        }
    )
    
    assert response.status_code == 422  # Pydantic validation error
    error_detail = response.json()
    assert "detail" in error_detail
    assert any("latitude" in str(error).lower() for error in error_detail["detail"])
