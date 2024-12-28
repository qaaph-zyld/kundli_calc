"""
Tests for Shadbala API endpoints
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_calculate_shadbala():
    # Test successful calculation
    response = client.post(
        "/api/v1/shadbala/calculate",
        json={
            "planet": "jupiter",
            "position": 95.0,
            "house": 4,
            "is_day": True,
            "aspects": [
                {
                    "type": "trine",
                    "angle": 120.0
                },
                {
                    "type": "square",
                    "angle": 90.0
                }
            ],
            "planet_positions": {
                "sun": 30.0,
                "moon": 60.0,
                "mars": 90.0,
                "mercury": 120.0,
                "jupiter": 95.0,
                "venus": 150.0,
                "saturn": 180.0
            }
        }
    )
    assert response.status_code == 200
    result = response.json()
    
    # Verify response structure
    assert "planet" in result
    assert "total_strength" in result
    assert "components" in result
    assert "interpretation" in result
    
    # Verify components
    components = result["components"]
    assert "sthana_bala" in components
    assert "dig_bala" in components
    assert "kala_bala" in components
    assert "chesta_bala" in components
    assert "naisargika_bala" in components
    assert "drik_bala" in components
    
    # Test invalid planet
    response = client.post(
        "/api/v1/shadbala/calculate",
        json={
            "planet": "invalid",
            "position": 95.0,
            "house": 4,
            "is_day": True,
            "aspects": [],
            "planet_positions": {
                "sun": 30.0,
                "moon": 60.0
            }
        }
    )
    assert response.status_code == 422
    
    # Test invalid position
    response = client.post(
        "/api/v1/shadbala/calculate",
        json={
            "planet": "jupiter",
            "position": 400.0,  # Invalid position
            "house": 4,
            "is_day": True,
            "aspects": [],
            "planet_positions": {
                "sun": 30.0,
                "moon": 60.0
            }
        }
    )
    assert response.status_code == 422
    
    # Test invalid house
    response = client.post(
        "/api/v1/shadbala/calculate",
        json={
            "planet": "jupiter",
            "position": 95.0,
            "house": 13,  # Invalid house
            "is_day": True,
            "aspects": [],
            "planet_positions": {
                "sun": 30.0,
                "moon": 60.0
            }
        }
    )
    assert response.status_code == 422

def test_analyze_all_planets():
    # Test successful analysis
    response = client.post(
        "/api/v1/shadbala/analyze",
        json={
            "birth_time_is_day": True,
            "planet_positions": {
                "sun": 30.0,
                "moon": 60.0,
                "mars": 90.0,
                "mercury": 120.0,
                "jupiter": 95.0,
                "venus": 150.0,
                "saturn": 180.0
            },
            "aspects": {
                "jupiter": [
                    {
                        "type": "trine",
                        "angle": 120.0
                    }
                ],
                "sun": [
                    {
                        "type": "square",
                        "angle": 90.0
                    }
                ]
            },
            "house_positions": {
                "sun": 1,
                "moon": 2,
                "mars": 3,
                "mercury": 4,
                "jupiter": 4,
                "venus": 5,
                "saturn": 6
            }
        }
    )
    assert response.status_code == 200
    result = response.json()
    
    # Verify response structure
    assert "planets" in result
    assert "chart_analysis" in result
    
    # Verify planets analysis
    planets = result["planets"]
    assert len(planets) == 7  # All planets should be analyzed
    for planet_data in planets.values():
        assert "total_strength" in planet_data
        assert "components" in planet_data
        assert "interpretation" in planet_data
    
    # Verify chart analysis
    chart_analysis = result["chart_analysis"]
    assert "total_strength" in chart_analysis
    assert "average_strength" in chart_analysis
    assert "interpretation" in chart_analysis
    
    # Test missing house position
    response = client.post(
        "/api/v1/shadbala/analyze",
        json={
            "birth_time_is_day": True,
            "planet_positions": {
                "sun": 30.0,
                "moon": 60.0
            },
            "aspects": {},
            "house_positions": {
                "sun": 1
                # Missing moon house position
            }
        }
    )
    assert response.status_code == 400
    assert "Missing house position" in response.json()["detail"]
    
    # Test invalid aspect type
    response = client.post(
        "/api/v1/shadbala/analyze",
        json={
            "birth_time_is_day": True,
            "planet_positions": {
                "sun": 30.0,
                "moon": 60.0
            },
            "aspects": {
                "sun": [
                    {
                        "type": "invalid",  # Invalid aspect type
                        "angle": 90.0
                    }
                ]
            },
            "house_positions": {
                "sun": 1,
                "moon": 2
            }
        }
    )
    assert response.status_code == 422
