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

export interface ClusteredRoutePoint extends MigrationPoint {
  route_key: string;
  cluster_id: number;
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

export interface PredictionDatasetSummary {
  sample_count: number;
  feature_count: number;
  species_counts: Record<string, number>;
}

export interface PredictionConfusionMatrix {
  true_negative: number;
  false_positive: number;
  false_negative: number;
  true_positive: number;
}

export interface PredictionMethodResult {
  name: string;
  category: string;
  accuracy: number;
  balanced_accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  roc_auc?: number;
  confusion_matrix: PredictionConfusionMatrix;
  notes?: string;
}

export interface PredictionFeatureScore {
  feature: string;
  score: number;
}

export interface PredictionFeatureDefinition {
  feature: string;
  plain_language: string;
  calculation: string;
}

export interface SpeciesFeatureProfile {
  species: string;
  individual_count: number;
  mean_daily_distance_km: number;
  mean_latitude: number;
  mean_longitude: number;
}

export interface PredictionExperimentResponse {
  title: string;
  species_used: string[];
  dataset: PredictionDatasetSummary;
  methods: PredictionMethodResult[];
  best_method: string;
  top_features: PredictionFeatureScore[];
  feature_definitions: PredictionFeatureDefinition[];
  travel_distance_method: string;
  season_assignment_method: string;
  evaluation_protocol: string;
  species_profiles: SpeciesFeatureProfile[];
  report: string;
}

export interface RouteAreaCount {
  country: string;
  province?: string;
  count: number;
}

export interface RouteAggregationSummary {
  node_count: number;
  country_count: number;
  state_count: number;
  origin_count: number;
  destination_count: number;
  avg_migration_months: number;
}

export interface RouteAggregationResponse {
  counts: RouteAreaCount[];
  summary: RouteAggregationSummary;
}

export interface TrackingSpeciesSummary {
  species: string;
  csv_count: number;
  individual_count: number;
  point_count: number;
  removed_point_count: number;
}

export interface TrackingPoint {
  identifier: string;
  timestamp: string;
  sort_order: number;
  longitude: number;
  latitude: number;
  study_name?: string;
}

export interface TrackingResponse {
  species: string;
  individual_count: number;
  point_count: number;
  removed_point_count: number;
  points: TrackingPoint[];
}

export interface TrackingReportTotals {
  species_count: number;
  csv_count: number;
  individual_count: number;
  point_count: number;
  removed_point_count: number;
}

export interface TrackingReportResponse {
  totals: TrackingReportTotals;
  species: TrackingSpeciesSummary[];
}
