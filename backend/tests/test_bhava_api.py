"""
Tests for Bhava API endpoints
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_analyze_bhava_chart():
    # Test successful analysis
    response = client.post(
        "/api/v1/bhava/analyze",
        json={
            "planet_positions": {
                "Sun": 30.0,
                "Moon": 60.0,
                "Mars": 90.0,
                "Mercury": 120.0,
                "Jupiter": 150.0,
                "Venus": 180.0,
                "Saturn": 210.0
            },
            "aspects": {
                "Jupiter": [1, 5, 7, 9],
                "Mars": [4, 7, 8],
                "Saturn": [3, 7, 10]
            }
        }
    )
    assert response.status_code == 200
    result = response.json()
    
    # Verify response structure
    assert "house_analysis" in result
    assert "strongest_house" in result
    assert "weakest_house" in result
    assert "chart_balance" in result
    
    # Verify house analysis
    house_analysis = result["house_analysis"]
    assert len(house_analysis) == 12
    for house_data in house_analysis.values():
        assert "strength" in house_data
        assert "significations" in house_data
        assert "occupants" in house_data
        assert "aspects" in house_data
        assert "lord" in house_data
    
    # Test invalid planet
    response = client.post(
        "/api/v1/bhava/analyze",
        json={
            "planet_positions": {
                "Invalid": 30.0,
                "Moon": 60.0
            },
            "aspects": {
                "Jupiter": [1, 5, 7, 9]
            }
        }
    )
    assert response.status_code == 422
    
    # Test invalid position
    response = client.post(
        "/api/v1/bhava/analyze",
        json={
            "planet_positions": {
                "Sun": 400.0,
                "Moon": 60.0
            },
            "aspects": {
                "Jupiter": [1, 5, 7, 9]
            }
        }
    )
    assert response.status_code == 422

def test_analyze_house():
    # Test successful analysis
    response = client.post(
        "/api/v1/bhava/house/1",
        json={
            "planet_positions": {
                "Sun": 30.0,
                "Moon": 60.0,
                "Mars": 90.0,
                "Mercury": 120.0,
                "Jupiter": 150.0,
                "Venus": 180.0,
                "Saturn": 210.0
            },
            "aspects": {
                "Jupiter": [1, 5, 7, 9],
                "Mars": [4, 7, 8],
                "Saturn": [3, 7, 10]
            }
        }
    )
    assert response.status_code == 200
    result = response.json()
    
    # Verify response structure
    assert "house_number" in result
    assert "analysis" in result
    
    analysis = result["analysis"]
    assert "strength" in analysis
    assert "significations" in analysis
    assert "occupants" in analysis
    assert "aspects" in analysis
    assert "lord" in analysis
    assert "relationships" in analysis
    
    # Test invalid house number
    response = client.post(
        "/api/v1/bhava/house/13",
        json={
            "planet_positions": {
                "Sun": 30.0,
                "Moon": 60.0
            },
            "aspects": {
                "Jupiter": [1, 5, 7, 9]
            }
        }
    )
    assert response.status_code == 400
    assert "Invalid house number" in response.json()["detail"]
    
    # Test invalid aspects
    response = client.post(
        "/api/v1/bhava/house/1",
        json={
            "planet_positions": {
                "Sun": 30.0,
                "Moon": 60.0
            },
            "aspects": {
                "Jupiter": [1, 13, 14]  # Invalid house numbers
            }
        }
    )
    assert response.status_code == 422
