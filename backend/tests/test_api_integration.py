from fastapi.testclient import TestClient
from datetime import datetime
import pytest
from unittest.mock import Mock, patch
from app.main import app
from app.core.calculations.astronomical import AstronomicalCalculator, Location
from app.core.calculations.ayanamsa import EnhancedAyanamsaManager
from app.core.calculations.divisional import EnhancedDivisionalChartEngine
from app.core.calculations.strength import EnhancedPlanetaryStrengthEngine
from app.core.calculations.aspects import EnhancedAspectCalculator
from app.core.calculations.house_analysis import EnhancedHouseAnalysisEngine

client = TestClient(app)

@pytest.fixture
def mock_calculation_engines():
    with patch('app.api.endpoints.horoscope.AstronomicalCalculator') as mock_astro, \
         patch('app.api.endpoints.horoscope.EnhancedAyanamsaManager') as mock_ayanamsa, \
         patch('app.api.endpoints.horoscope.EnhancedDivisionalChartEngine') as mock_divisional, \
         patch('app.api.endpoints.horoscope.EnhancedPlanetaryStrengthEngine') as mock_strength, \
         patch('app.api.endpoints.horoscope.EnhancedAspectCalculator') as mock_aspect, \
         patch('app.api.endpoints.horoscope.EnhancedHouseAnalysisEngine') as mock_house:

        # Configure mock responses
        mock_astro_instance = Mock()
        mock_astro_instance.calculate_planetary_positions.return_value = {
            'Sun': {'longitude': 280.5, 'latitude': 0.0, 'speed': {'degrees_per_day': 1.0, 'is_retrograde': False, 'relative_speed': 1.0}, 'distance': 1.0},
            'Moon': {'longitude': 120.3, 'latitude': 5.0, 'speed': {'degrees_per_day': 13.0, 'is_retrograde': False, 'relative_speed': 1.0}, 'distance': 1.0},
            'Ascendant': {'longitude': 90.0, 'latitude': 0.0, 'speed': {'degrees_per_day': 0.0, 'is_retrograde': False, 'relative_speed': 0.0}, 'distance': 0.0}
        }
        mock_astro.return_value = mock_astro_instance

        mock_ayanamsa_instance = Mock()
        mock_ayanamsa_instance.calculate_precise_ayanamsa.return_value = 24.0
        mock_ayanamsa.return_value = mock_ayanamsa_instance

        mock_divisional_instance = Mock()
        mock_divisional_instance.calculate_all_divisions.return_value = {
            'D1': {'longitude': 280.5},
            'D9': {'longitude': 120.3}
        }
        mock_divisional.return_value = mock_divisional_instance

        mock_strength_instance = Mock()
        mock_strength_instance.calculate_complete_strengths.return_value = {
            'Sun': 75.5,
            'Moon': 82.3
        }
        mock_strength.return_value = mock_strength_instance

        mock_aspect_instance = Mock()
        mock_aspect_instance.calculate_aspects.return_value = [
            {'planet1': 'Sun', 'planet2': 'Moon', 'aspect_type': 'Trine', 'strength': 0.8}
        ]
        mock_aspect.return_value = mock_aspect_instance

        mock_house_instance = Mock()
        mock_house_instance.analyze_house.return_value = {
            'strength': 85.5,
            'occupants': ['Sun'],
            'aspects': []
        }
        mock_house.return_value = mock_house_instance

        yield {
            'astro': mock_astro,
            'ayanamsa': mock_ayanamsa,
            'divisional': mock_divisional,
            'strength': mock_strength,
            'aspect': mock_aspect,
            'house': mock_house
        }

def test_horoscope_endpoint_basic(mock_calculation_engines):
    """Test basic horoscope calculation endpoint"""
    test_data = {
        "datetime_utc": "2024-01-01T12:00:00",
        "latitude": 28.6139,  # New Delhi
        "longitude": 77.2090,
        "altitude": 0,
        "ayanamsa_system": "LAHIRI"
    }
    
    response = client.post("/api/v1/horoscope/calculate", json=test_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "planetary_positions" in data
    assert "ayanamsa_value" in data
    assert "divisional_charts" in data
    assert "planetary_strengths" in data
    assert "aspects" in data
    assert "house_analysis" in data

def test_horoscope_invalid_date():
    """Test error handling for invalid date"""
    test_data = {
        "datetime_utc": "invalid_date",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "altitude": 0,
        "ayanamsa_system": "LAHIRI"
    }
    
    response = client.post("/api/v1/horoscope/calculate", json=test_data)
    assert response.status_code == 422  # Validation error

def test_horoscope_invalid_coordinates():
    """Test error handling for invalid coordinates"""
    test_data = {
        "datetime_utc": "2024-01-01T12:00:00",
        "latitude": 91,  # Invalid latitude
        "longitude": 181,  # Invalid longitude
        "altitude": 0,
        "ayanamsa_system": "LAHIRI"
    }
    
    response = client.post("/api/v1/horoscope/calculate", json=test_data)
    assert response.status_code == 422

def test_horoscope_invalid_ayanamsa():
    """Test error handling for invalid ayanamsa system"""
    test_data = {
        "datetime_utc": "2024-01-01T12:00:00",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "altitude": 0,
        "ayanamsa_system": "INVALID_SYSTEM"
    }
    
    response = client.post("/api/v1/horoscope/calculate", json=test_data)
    assert response.status_code == 422
    error_detail = response.json()
    assert isinstance(error_detail["detail"], list)
    assert any("Invalid ayanamsa system" in error["msg"] for error in error_detail["detail"])

def test_horoscope_response_format(mock_calculation_engines):
    """Test response format validation"""
    test_data = {
        "datetime_utc": "2024-01-01T12:00:00",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "altitude": 0,
        "ayanamsa_system": "LAHIRI"
    }
    
    response = client.post("/api/v1/horoscope/calculate", json=test_data)
    assert response.status_code == 200
    
    data = response.json()
    
    # Validate planetary positions
    assert isinstance(data["planetary_positions"], dict)
    for planet, details in data["planetary_positions"].items():
        assert "longitude" in details
        assert "latitude" in details
        assert "speed" in details
        assert isinstance(details["longitude"], float)
        assert isinstance(details["latitude"], float)
        assert isinstance(details["speed"], dict)
        assert "degrees_per_day" in details["speed"]
        assert "is_retrograde" in details["speed"]
        assert "relative_speed" in details["speed"]
    
    # Validate ayanamsa value
    assert isinstance(data["ayanamsa_value"], float)
    assert 23 <= data["ayanamsa_value"] <= 25  # Reasonable range for Lahiri
    
    # Validate divisional charts
    assert isinstance(data["divisional_charts"], dict)
    
    # Validate planetary strengths
    assert isinstance(data["planetary_strengths"], dict)
    for planet, strength in data["planetary_strengths"].items():
        assert isinstance(strength, float)
        assert 0 <= strength <= 100  # Strength should be percentage
    
    # Validate aspects
    assert isinstance(data["aspects"], list)
    
    # Validate house analysis
    assert isinstance(data["house_analysis"], dict)
    for house, analysis in data["house_analysis"].items():
        assert isinstance(analysis, dict)
        assert "strength" in analysis
        assert 0 <= analysis["strength"] <= 100

def test_horoscope_calculation_accuracy(mock_calculation_engines):
    """Test accuracy of horoscope calculations"""
    # Test data for New Delhi on J2000 epoch
    test_data = {
        "datetime_utc": "2000-01-01T12:00:00",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "altitude": 0,
        "ayanamsa_system": "LAHIRI"
    }
    
    response = client.post("/api/v1/horoscope/calculate", json=test_data)
    assert response.status_code == 200
    
    data = response.json()
    
    # Verify Sun position (approximate for J2000)
    sun_pos = data["planetary_positions"]["Sun"]["longitude"]
    assert 255 <= sun_pos <= 285  # Sun's position in early January
    
    # Verify ayanamsa value for J2000
    assert abs(data["ayanamsa_value"] - 23.85) < 0.5  # Lahiri ayanamsa at J2000

def test_horoscope_divisional_charts(mock_calculation_engines):
    """Test divisional chart calculations"""
    test_data = {
        "datetime_utc": "2024-01-01T12:00:00",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "altitude": 0,
        "ayanamsa_system": "LAHIRI",
        "divisional_charts": ["D1", "D9"]  # Rashi and Navamsa
    }
    
    response = client.post("/api/v1/horoscope/calculate", json=test_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "D1" in data["divisional_charts"]
    assert "D9" in data["divisional_charts"]
    
    # Verify D1 chart
    d1_chart = data["divisional_charts"]["D1"]
    assert isinstance(d1_chart, dict)
    assert len(d1_chart) > 0
    
    # Verify D9 chart
    d9_chart = data["divisional_charts"]["D9"]
    assert isinstance(d9_chart, dict)
    assert len(d9_chart) > 0
