"""
Tests for Ashtakavarga API endpoints
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_calculate_ashtakavarga():
    # Test successful calculation
    response = client.post(
        "/api/v1/ashtakavarga/calculate",
        json={
            "planet_positions": {
                "Sun": 1,
                "Moon": 4,
                "Mars": 7,
                "Mercury": 2,
                "Jupiter": 5,
                "Venus": 3,
                "Saturn": 8
            }
        }
    )
    assert response.status_code == 200
    result = response.json()
    
    # Verify response structure
    assert "sarvashtakavarga" in result
    assert "planet_analysis" in result
    assert "strong_houses" in result
    
    # Verify sarvashtakavarga data
    sarva = result["sarvashtakavarga"]
    assert all(planet in sarva for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"])
    assert all(len(bindus) == 12 for bindus in sarva.values())
    
    # Verify planet analysis
    analysis = result["planet_analysis"]
    assert all(planet in analysis for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"])
    for planet_data in analysis.values():
        assert "strength" in planet_data
        assert "favorable_houses" in planet_data
        assert "unfavorable_houses" in planet_data
        assert "recommendations" in planet_data
    
    # Test invalid planet
    response = client.post(
        "/api/v1/ashtakavarga/calculate",
        json={
            "planet_positions": {
                "Invalid": 1,
                "Moon": 4
            }
        }
    )
    assert response.status_code == 422
    
    # Test invalid house number
    response = client.post(
        "/api/v1/ashtakavarga/calculate",
        json={
            "planet_positions": {
                "Sun": 13,
                "Moon": 4
            }
        }
    )
    assert response.status_code == 422

def test_analyze_planet():
    # Test successful analysis
    response = client.post(
        "/api/v1/ashtakavarga/analyze_planet?planet=Sun",
        json={
            "planet_positions": {
                "Sun": 1,
                "Moon": 4,
                "Mars": 7,
                "Mercury": 2,
                "Jupiter": 5,
                "Venus": 3,
                "Saturn": 8
            }
        }
    )
    assert response.status_code == 200
    result = response.json()
    
    # Verify response structure
    assert "planet" in result
    assert "analysis" in result
    assert "bindus_per_house" in result
    
    # Verify analysis data
    analysis = result["analysis"]
    assert "strength" in analysis
    assert "favorable_houses" in analysis
    assert "unfavorable_houses" in analysis
    assert "recommendations" in analysis
    
    # Verify bindus data
    assert len(result["bindus_per_house"]) == 12
    
    # Test invalid planet
    response = client.post(
        "/api/v1/ashtakavarga/analyze_planet?planet=Invalid",
        json={
            "planet_positions": {
                "Sun": 1,
                "Moon": 4
            }
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert result["analysis"]["strength"] == 0
    assert len(result["bindus_per_house"]) == 0
    
    # Test invalid house number
    response = client.post(
        "/api/v1/ashtakavarga/analyze_planet?planet=Sun",
        json={
            "planet_positions": {
                "Sun": 13,
                "Moon": 4
            }
        }
    )
    assert response.status_code == 422
