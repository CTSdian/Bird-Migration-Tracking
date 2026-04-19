from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from .data_loader import (
    get_clustered_route_points,
    get_prediction_route,
    get_route_aggregated_counts,
    get_route_points,
    get_species_discrimination_report,
    get_species_list,
    get_temperature_for_location,
    get_tracking_points,
    get_tracking_report,
    get_tracking_species_list,
)
from .schemas import ClusteredMigrationPoint, MigrationPoint, PredictionExperimentResponse, PredictionsResponse, RouteAggregationResponse, SpeciesSummary, TrackingReportResponse, TrackingResponse, TrackingSpeciesSummary

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


@app.get("/api/tracking/species", response_model=List[TrackingSpeciesSummary])
def list_tracking_species() -> List[TrackingSpeciesSummary]:
    return [TrackingSpeciesSummary(**item) for item in get_tracking_species_list()]


@app.get("/api/tracking/report", response_model=TrackingReportResponse)
def read_tracking_report() -> TrackingReportResponse:
    return TrackingReportResponse(**get_tracking_report())


@app.get("/api/tracking/points", response_model=TrackingResponse)
def read_tracking_points(species: str = Query(..., description="Tracking species folder name")) -> TrackingResponse:
    data = get_tracking_points(species)
    if not data["points"]:
        raise HTTPException(status_code=404, detail=f"Tracking species '{species}' not found.")
    return TrackingResponse(**data)


@app.get("/api/routes", response_model=List[MigrationPoint])
def read_route_points(species: Optional[str] = Query(None, description="Scientific name of the bird species")) -> List[MigrationPoint]:
    points = get_route_points(species)
    if species and not points:
        raise HTTPException(status_code=404, detail=f"Species '{species}' not found.")
    return points


@app.get("/api/routes/aggregated", response_model=RouteAggregationResponse)
def read_route_aggregated_counts(species: Optional[str] = Query(None, description="Scientific name of the bird species")) -> RouteAggregationResponse:
    data = get_route_aggregated_counts(species)
    if species and not data["counts"]:
        raise HTTPException(status_code=404, detail=f"Species '{species}' not found.")
    return RouteAggregationResponse(**data)


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


@app.get("/api/predictions/experiments", response_model=PredictionExperimentResponse)
def read_prediction_experiments() -> PredictionExperimentResponse:
    return PredictionExperimentResponse(**get_species_discrimination_report())
