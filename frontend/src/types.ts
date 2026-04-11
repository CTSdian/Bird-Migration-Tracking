export interface SpeciesSummary {
  species: string;
  common_name?: string;
  order?: string;
}

export interface MigrationPoint {
  id: number;
  route_code?: number;
  node?: string;
  order?: string;
  family?: string;
  genus?: string;
  common_name?: string;
  species?: string;
  species_authority?: string;
  migration_type?: string;
  iucn_red_list?: string;
  start_year?: number;
  start_month?: number;
  end_year?: number;
  end_month?: number;
  sensor_types?: string;
  continent?: number;
  country?: string;
  province?: string;
  gps_xx?: number;
  gps_yy?: number;
  migration_pattern?: number;
  migration_route?: number;
  references?: string;
  publish_time?: number;
  doi?: string;
  predicted?: boolean;
  sequence_index?: number;
  estimated_year?: number;
  estimated_month?: number;
}

export interface RouteGroup {
  routeId: number;
  routeCode: number;
  origin?: MigrationPoint;
  destination?: MigrationPoint;
  points: MigrationPoint[];
}

export interface GroupSummary {
  key: string;
  label: string;
  description?: string;
  species_count: number;
  route_count: number;
  point_count: number;
}

export interface PredictionsResponse {
  species: string;
  points: MigrationPoint[];
}
