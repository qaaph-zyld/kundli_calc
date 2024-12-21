from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.endpoints import charts

app = FastAPI(
    title="South Indian Kundli Calculator",
    description="A web service for calculating Vedic birth charts in South Indian style",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    charts.router,
    prefix="/api/v1/charts",
    tags=["charts"]
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the South Indian Kundli Calculator API",
        "version": "0.1.0",
        "docs_url": "/docs"
    }
