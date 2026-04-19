from typing import Dict, List, Optional

from pydantic import BaseModel


class MigrationPoint(BaseModel):
    id: int
    route_code: Optional[int] = None
    node: Optional[str] = None
    order: Optional[str] = None
    family: Optional[str] = None
    genus: Optional[str] = None
    common_name: Optional[str] = None
    species: Optional[str] = None
    species_authority: Optional[str] = None
    migration_type: Optional[str] = None
    iucn_red_list: Optional[str] = None
    start_year: Optional[int] = None
    start_month: Optional[int] = None
    end_year: Optional[int] = None
    end_month: Optional[int] = None
    sensor_types: Optional[str] = None
    continent: Optional[int] = None
    country: Optional[str] = None
    province: Optional[str] = None
    gps_xx: Optional[float] = None
    gps_yy: Optional[float] = None
    migration_pattern: Optional[int] = None
    migration_route: Optional[int] = None
    references: Optional[str] = None
    publish_time: Optional[int] = None
    doi: Optional[str] = None
    predicted: Optional[bool] = False
    sequence_index: Optional[int] = None
    estimated_year: Optional[int] = None
    estimated_month: Optional[int] = None


class ClusteredMigrationPoint(MigrationPoint):
    route_key: str
    cluster_id: int


class SpeciesSummary(BaseModel):
    species: str
    common_name: Optional[str]
    order: Optional[str]


class GroupSummary(BaseModel):
    key: str
    label: str
    description: Optional[str]
    species_count: int
    route_count: int
    point_count: int


class PredictionsResponse(BaseModel):
    species: str
    points: List[MigrationPoint]


class PredictionDatasetSummary(BaseModel):
    sample_count: int
    feature_count: int
    species_counts: Dict[str, int]


class PredictionConfusionMatrix(BaseModel):
    true_negative: int
    false_positive: int
    false_negative: int
    true_positive: int


class PredictionMethodResult(BaseModel):
    name: str
    category: str
    accuracy: float
    balanced_accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: Optional[float] = None
    confusion_matrix: PredictionConfusionMatrix
    notes: Optional[str] = None


class PredictionFeatureScore(BaseModel):
    feature: str
    score: float


class PredictionFeatureDefinition(BaseModel):
    feature: str
    plain_language: str
    calculation: str


class SpeciesFeatureProfile(BaseModel):
    species: str
    individual_count: int
    mean_daily_distance_km: float
    mean_latitude: float
    mean_longitude: float


class PredictionExperimentResponse(BaseModel):
    title: str
    species_used: List[str]
    dataset: PredictionDatasetSummary
    methods: List[PredictionMethodResult]
    best_method: str
    top_features: List[PredictionFeatureScore]
    feature_definitions: List[PredictionFeatureDefinition]
    travel_distance_method: str
    season_assignment_method: str
    evaluation_protocol: str
    species_profiles: List[SpeciesFeatureProfile]
    report: str


class RouteAreaCount(BaseModel):
    country: str
    province: Optional[str] = None
    count: int


class RouteAggregationSummary(BaseModel):
    node_count: int
    country_count: int
    state_count: int
    origin_count: int
    destination_count: int
    avg_migration_months: float


class RouteAggregationResponse(BaseModel):
    counts: List[RouteAreaCount]
    summary: RouteAggregationSummary


class TrackingSpeciesSummary(BaseModel):
    species: str
    csv_count: int
    individual_count: int
    point_count: int
    removed_point_count: int = 0


class TrackingPoint(BaseModel):
    identifier: str
    timestamp: str
    sort_order: int
    longitude: float
    latitude: float
    study_name: Optional[str] = None


class TrackingResponse(BaseModel):
    species: str
    individual_count: int
    point_count: int
    removed_point_count: int = 0
    points: List[TrackingPoint]


class TrackingReportTotals(BaseModel):
    species_count: int
    csv_count: int
    individual_count: int
    point_count: int
    removed_point_count: int


class TrackingReportResponse(BaseModel):
    totals: TrackingReportTotals
    species: List[TrackingSpeciesSummary]
