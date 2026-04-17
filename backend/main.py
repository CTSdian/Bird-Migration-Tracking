from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from .data_loader import (
    get_clustered_route_points,
    get_prediction_route,
    get_route_points,
    get_species_list,
    get_temperature_for_location,
)
from .schemas import ClusteredMigrationPoint, MigrationPoint, PredictionsResponse, SpeciesSummary

app = FastAPI(
    title="Bird Migration Predictor",
    description="Backend API for bird migration route visualization and prediction.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/species", response_model=List[SpeciesSummary])
def list_species() -> List[SpeciesSummary]:
    return get_species_list()


@app.get("/api/routes", response_model=List[MigrationPoint])
def read_route_points(species: str = Query(..., description="Scientific name of the bird species")) -> List[MigrationPoint]:
    points = get_route_points(species)
    if not points:
        raise HTTPException(status_code=404, detail=f"Species '{species}' not found.")
    return points


@app.get("/api/clustering/routes", response_model=List[ClusteredMigrationPoint])
def read_clustered_route_points() -> List[ClusteredMigrationPoint]:
    points = get_clustered_route_points()
    if not points:
        raise HTTPException(status_code=404, detail="No clustered route points available.")
    return points


@app.get("/api/temperature")
def read_temperature(
    latitude: float = Query(..., description="Latitude for temperature lookup"),
    longitude: float = Query(..., description="Longitude for temperature lookup"),
    year: int = Query(..., description="Year for temperature lookup"),
    month: int = Query(..., description="Month for temperature lookup"),
) -> dict:
    temperature = get_temperature_for_location(latitude, longitude, year, month)
    if temperature is None:
        raise HTTPException(status_code=404, detail="Temperature data unavailable for the requested point.")
    return {"temperature": round(temperature, 2)}


@app.get("/api/predictions", response_model=PredictionsResponse)
def predict_route(species: str = Query(..., description="Scientific name of the bird species")) -> PredictionsResponse:
    points = get_prediction_route(species)
    if not points:
        raise HTTPException(status_code=404, detail=f"Species '{species}' not found.")
    return PredictionsResponse(species=species, points=points)
