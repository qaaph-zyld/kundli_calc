"""Main application module."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from .api.endpoints import charts, health, birth_charts, horoscope, dasha, ashtakavarga, bhava, prediction, shadbala, ayanamsa
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
    allow_origins=settings.BACKEND_CORS_ORIGINS,
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
    dasha.router,
    prefix="/api/v1/dasha",
    tags=["dasha"]
)

app.include_router(
    ashtakavarga.router,
    prefix="/api/v1/ashtakavarga",
    tags=["ashtakavarga"]
)

app.include_router(
    bhava.router,
    prefix="/api/v1/bhava",
    tags=["bhava"]
)

app.include_router(
    prediction.router,
    prefix="/api/v1/prediction",
    tags=["prediction"]
)

app.include_router(
    shadbala.router,
    prefix="/api/v1/shadbala",
    tags=["shadbala"]
)

app.include_router(
    ayanamsa.router,
    prefix="/api/v1/ayanamsa",
    tags=["ayanamsa"]
)

app.include_router(
    health.router,
    prefix="/api/v1/health",
    tags=["health"]
)


def custom_openapi():
    """Customize OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to South Indian Kundli Calculator API",
        "version": app.version,
        "docs_url": app.docs_url
    }
