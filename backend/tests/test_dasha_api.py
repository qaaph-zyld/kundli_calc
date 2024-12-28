"""
Tests for Dasha API endpoints
"""
from datetime import datetime
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_calculate_vimshottari_dasha():
    # Test successful calculation
    response = client.post(
        "/dasha/vimshottari",
        json={
            "birth_date": "2000-01-01T12:00:00",
            "moon_longitude": 0.0
        }
    )
    assert response.status_code == 200
    result = response.json()
    
    # Verify response structure
    assert "birth_nakshatra" in result
    assert "balance" in result
    assert "periods" in result
    assert len(result["periods"]) == 9
    
    # Test invalid moon longitude
    response = client.post(
        "/dasha/vimshottari",
        json={
            "birth_date": "2000-01-01T12:00:00",
            "moon_longitude": 400.0
        }
    )
    assert response.status_code == 400
    
    # Test invalid date format
    response = client.post(
        "/dasha/vimshottari",
        json={
            "birth_date": "invalid-date",
            "moon_longitude": 0.0
        }
    )
    assert response.status_code == 422

def test_get_current_dasha():
    # Test successful calculation
    response = client.get(
        "/dasha/current",
        params={
            "birth_date": "2000-01-01T12:00:00",
            "moon_longitude": 0.0
        }
    )
    assert response.status_code == 200
    result = response.json()
    
    # Verify response structure
    assert "mahadasha" in result
    assert "antardasha" in result
    assert "pratyantardasha" in result
    
    # Verify current periods are found
    assert result["mahadasha"] is not None
    assert result["antardasha"] is not None
    assert result["pratyantardasha"] is not None
    
    # Test invalid moon longitude
    response = client.get(
        "/dasha/current",
        params={
            "birth_date": "2000-01-01T12:00:00",
            "moon_longitude": 400.0
        }
    )
    assert response.status_code == 400
    
    # Test invalid date format
    response = client.get(
        "/dasha/current",
        params={
            "birth_date": "invalid-date",
            "moon_longitude": 0.0
        }
    )
    assert response.status_code == 422
    
    # Test future birth date
    response = client.get(
        "/dasha/current",
        params={
            "birth_date": "2025-01-01T12:00:00",
            "moon_longitude": 0.0
        }
    )
    assert response.status_code == 400
    assert "No active dasha period found" in response.json()["detail"]

def test_interpret_dasha_period():
    # Test mahadasha only
    response = client.post(
        "/api/v1/dasha/interpret",
        json={
            "main_planet": "Sun"
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert "main_effects" in result
    assert len(result["main_effects"]) > 0
    
    # Test mahadasha and antardasha
    response = client.post(
        "/api/v1/dasha/interpret",
        json={
            "main_planet": "Sun",
            "sub_planet": "Moon"
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert "main_effects" in result
    assert "sub_effects" in result
    assert "combinations" in result
    assert len(result["combinations"]) > 0
    
    # Test all three levels
    response = client.post(
        "/api/v1/dasha/interpret",
        json={
            "main_planet": "Sun",
            "sub_planet": "Moon",
            "prat_planet": "Mars"
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert "main_effects" in result
    assert "sub_effects" in result
    assert "prat_effects" in result
    assert "combinations" in result
    
    # Test invalid planet
    response = client.post(
        "/api/v1/dasha/interpret",
        json={
            "main_planet": "Invalid"
        }
    )
    assert response.status_code == 200  # Should return empty effects but not fail
    result = response.json()
    assert len(result["main_effects"]) == 0

def test_calculate_dasha_yogas():
    # Test with Raja Yoga combination
    response = client.post(
        "/api/v1/dasha/yoga",
        json={
            "main_planet": "Sun",
            "sub_planet": "Jupiter",
            "planet_positions": {
                "Sun": 120.0,
                "Jupiter": 90.0
            }
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert "active_yogas" in result
    assert "predictions" in result
    assert len(result["active_yogas"]) > 0
    assert len(result["predictions"]) > 0
    
    # Test with no yoga combination
    response = client.post(
        "/api/v1/dasha/yoga",
        json={
            "main_planet": "Mars",
            "sub_planet": "Rahu",
            "planet_positions": {
                "Mars": 120.0,
                "Rahu": 90.0
            }
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert len(result["active_yogas"]) == 0
    assert len(result["predictions"]) == 0
    
    # Test with three planets
    response = client.post(
        "/api/v1/dasha/yoga",
        json={
            "main_planet": "Sun",
            "sub_planet": "Jupiter",
            "prat_planet": "Venus",
            "planet_positions": {
                "Sun": 120.0,
                "Jupiter": 90.0,
                "Venus": 180.0
            }
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert len(result["active_yogas"]) > 0
    assert len(result["predictions"]) > 0
    
    # Test with invalid planet
    response = client.post(
        "/api/v1/dasha/yoga",
        json={
            "main_planet": "Invalid",
            "sub_planet": "Jupiter",
            "planet_positions": {
                "Invalid": 120.0,
                "Jupiter": 90.0
            }
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert len(result["active_yogas"]) == 0
    
    # Test with invalid planet positions
    response = client.post(
        "/api/v1/dasha/yoga",
        json={
            "main_planet": "Sun",
            "sub_planet": "Jupiter",
            "planet_positions": {
                "Sun": -30.0,  # Invalid longitude
                "Jupiter": 400.0  # Invalid longitude
            }
        }
    )
    assert response.status_code == 200  # Should not fail, just return no yogas
    result = response.json()
    assert len(result["active_yogas"]) > 0  # Still finds yoga based on planet names
