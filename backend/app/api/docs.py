"""API Documentation Module

This module contains the OpenAPI documentation for the Kundli Calculator API.
"""

from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI

def custom_openapi(app: FastAPI):
    """Generate custom OpenAPI schema for the API."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Kundli Calculator API",
        version="1.0.0",
        description="""
        A comprehensive API for Vedic astrology calculations and birth chart generation.
        
        Features:
        - Accurate astronomical calculations using Swiss Ephemeris
        - Support for multiple ayanamsa systems
        - House system calculations
        - Nakshatra and planetary position calculations
        - Divisional chart support
        """,
        routes=app.routes,
    )

    # Add authentication scheme
    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }

    # Add example requests
    openapi_schema["info"]["x-logo"] = {
        "url": "https://example.com/logo.png"  # Replace with actual logo URL
    }

    # Add tags metadata
    openapi_schema["tags"] = [
        {
            "name": "Charts",
            "description": "Operations for calculating and managing birth charts"
        },
        {
            "name": "Horoscope",
            "description": "Operations for horoscope analysis and predictions"
        }
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema
