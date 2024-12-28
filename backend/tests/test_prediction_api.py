"""
Tests for Prediction API endpoints
"""
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_calculate_muhurta():
    # Test successful calculation
    response = client.post(
        "/api/v1/prediction/muhurta/calculate",
        json={
            "datetime_utc": "2024-12-27T08:00:00",
            "activity_type": "business",
            "planet_positions": {
                "sun": 270.0,
                "moon": 120.0,
                "mars": 180.0,
                "mercury": 240.0,
                "jupiter": 300.0,
                "venus": 30.0,
                "saturn": 150.0
            },
            "planet_strengths": {
                "sun": 0.7,
                "moon": 0.8,
                "mars": 0.6,
                "mercury": 0.75,
                "jupiter": 0.8,
                "venus": 0.7,
                "saturn": 0.5
            }
        }
    )
    assert response.status_code == 200
    result = response.json()
    
    # Verify response structure
    assert "datetime" in result
    assert "activity" in result
    assert "suitability_score" in result
    assert "is_suitable" in result
    assert "tithi" in result
    assert "nakshatra" in result
    assert "current_muhurta" in result
    assert "is_auspicious_muhurta" in result
    assert "planetary_analysis" in result
    assert "recommended_muhurtas" in result
    
    # Test invalid activity type
    response = client.post(
        "/api/v1/prediction/muhurta/calculate",
        json={
            "datetime_utc": "2024-12-27T08:00:00",
            "activity_type": "invalid",
            "planet_positions": {
                "sun": 270.0,
                "moon": 120.0
            },
            "planet_strengths": {
                "sun": 0.7,
                "moon": 0.8
            }
        }
    )
    assert response.status_code == 422
    
    # Test invalid datetime
    response = client.post(
        "/api/v1/prediction/muhurta/calculate",
        json={
            "datetime_utc": "invalid",
            "activity_type": "business",
            "planet_positions": {
                "sun": 270.0,
                "moon": 120.0
            },
            "planet_strengths": {
                "sun": 0.7,
                "moon": 0.8
            }
        }
    )
    assert response.status_code == 422

def test_find_next_suitable_time():
    # Test successful search
    response = client.post(
        "/api/v1/prediction/muhurta/next-suitable",
        json={
            "datetime_utc": "2024-12-27T08:00:00",
            "activity_type": "business",
            "planet_positions": {
                "sun": 270.0,
                "moon": 120.0,
                "mars": 180.0,
                "mercury": 240.0,
                "jupiter": 300.0,
                "venus": 30.0,
                "saturn": 150.0
            },
            "planet_strengths": {
                "sun": 0.7,
                "moon": 0.8,
                "mars": 0.6,
                "mercury": 0.75,
                "jupiter": 0.8,
                "venus": 0.7,
                "saturn": 0.5
            },
            "max_days": 7
        }
    )
    assert response.status_code == 200
    result = response.json()
    
    # Verify response structure
    assert "datetime" in result
    assert "activity" in result
    assert "suitability_score" in result
    assert "is_suitable" in result
    assert result["is_suitable"] == True
    
    # Test invalid max_days
    response = client.post(
        "/api/v1/prediction/muhurta/next-suitable",
        json={
            "datetime_utc": "2024-12-27T08:00:00",
            "activity_type": "business",
            "planet_positions": {
                "sun": 270.0,
                "moon": 120.0
            },
            "planet_strengths": {
                "sun": 0.7,
                "moon": 0.8
            },
            "max_days": 31  # Too many days
        }
    )
    assert response.status_code == 422

def test_analyze_transit_period():
    # Test successful analysis
    start_time = datetime(2024, 12, 27, 8, 0)
    end_time = start_time + timedelta(days=1)
    
    response = client.post(
        "/api/v1/prediction/transit/analyze",
        json={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "planet": "jupiter",
            "natal_position": 0.0,
            "transit_positions": [
                {
                    "time": start_time.isoformat(),
                    "position": "0.0"
                },
                {
                    "time": (start_time + timedelta(hours=12)).isoformat(),
                    "position": "120.0"
                },
                {
                    "time": end_time.isoformat(),
                    "position": "240.0"
                }
            ]
        }
    )
    assert response.status_code == 200
    result = response.json()
    
    # Verify response structure
    assert "period" in result
    assert "planet" in result
    assert "natal_position" in result
    assert "aspects" in result
    assert "strength" in result
    assert "overall_effect" in result
    
    # Test invalid planet
    response = client.post(
        "/api/v1/prediction/transit/analyze",
        json={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "planet": "invalid",
            "natal_position": 0.0,
            "transit_positions": [
                {
                    "time": start_time.isoformat(),
                    "position": "0.0"
                }
            ]
        }
    )
    assert response.status_code == 422
    
    # Test invalid position
    response = client.post(
        "/api/v1/prediction/transit/analyze",
        json={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "planet": "jupiter",
            "natal_position": 400.0,  # Invalid position
            "transit_positions": [
                {
                    "time": start_time.isoformat(),
                    "position": "0.0"
                }
            ]
        }
    )
    assert response.status_code == 422
