from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from .api.endpoints import charts, health, birth_charts, horoscope
from .core.config import settings

app = FastAPI(
    title="South Indian Kundli Calculator",
    description="""
    A web service for calculating Vedic birth charts in South Indian style.
    
    Features:
    * Calculate planetary positions using Swiss Ephemeris
    * Generate South Indian style birth charts
    * Calculate aspects between planets
    * Determine nakshatras for all planets
    * Redis caching for improved performance
    * PostgreSQL database for storing birth charts
    """,
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    horoscope.router,
    prefix="/api",
    tags=["horoscope"]
)

app.include_router(
    charts.router,
    prefix="/api/v1/charts",
    tags=["charts"]
)

app.include_router(
    birth_charts.router,
    prefix="/api/v1/birth-charts",
    tags=["birth-charts"]
)

app.include_router(
    health.router,
    prefix="/api/v1/health",
    tags=["health"]
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }
    
    # Add tags metadata
    openapi_schema["tags"] = [
        {
            "name": "charts",
            "description": "Operations for calculating and retrieving birth charts"
        },
        {
            "name": "birth-charts",
            "description": "CRUD operations for managing stored birth charts"
        },
        {
            "name": "health",
            "description": "API health check endpoints"
        },
        {
            "name": "horoscope",
            "description": "Operations for calculating and retrieving horoscopes"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/")
async def root():
    """
    Root endpoint returning API information and links to documentation.
    """
    return {
        "message": "Welcome to the South Indian Kundli Calculator API",
        "version": app.version,
        "documentation": {
            "swagger": "/api/docs",
            "redoc": "/api/redoc",
            "openapi_json": "/api/openapi.json"
        }
    }
