from fastapi.testclient import TestClient
from datetime import datetime

def test_calculate_chart(client: TestClient):
    response = client.post(
        "/api/v1/charts/calculate",
        json={
            "date_time": "2024-01-01T12:00:00Z",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "time_zone": "Asia/Kolkata",
            "ayanamsa": 1
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "planetary_positions" in data
    assert "houses" in data

def test_invalid_coordinates(client: TestClient):
    response = client.post(
        "/api/v1/charts/calculate",
        json={
            "date_time": "2024-01-01T12:00:00Z",
            "latitude": 91,  # Invalid latitude
            "longitude": 80.2707,
            "time_zone": "Asia/Kolkata",
            "ayanamsa": 1
        }
    )
    
    assert response.status_code == 400
