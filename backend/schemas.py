from typing import List, Optional

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
