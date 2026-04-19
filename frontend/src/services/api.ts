import type {
  ClusteredRoutePoint,
  MigrationPoint,
  PredictionExperimentResponse,
  PredictionsResponse,
  RouteAggregationResponse,
  SpeciesSummary,
  TrackingReportResponse,
  TrackingResponse,
  TrackingSpeciesSummary,
} from '../types';

const API_BASE = '/api';

export async function fetchSpeciesList(): Promise<SpeciesSummary[]> {
  const response = await fetch(`${API_BASE}/species`);
  if (!response.ok) {
    throw new Error('Failed to load species list');
  }
  return response.json();
}

export async function fetchRoutePoints(species?: string): Promise<MigrationPoint[]> {
  const query = species ? `?species=${encodeURIComponent(species)}` : '';
  const response = await fetch(`${API_BASE}/routes${query}`);
  if (!response.ok) {
    throw new Error('Failed to load route points');
  }
  return response.json();
}

export async function fetchRouteAggregates(species?: string): Promise<RouteAggregationResponse> {
  const query = species ? `?species=${encodeURIComponent(species)}` : '';
  const response = await fetch(`${API_BASE}/routes/aggregated${query}`);
  if (!response.ok) {
    throw new Error('Failed to load aggregated route points');
  }
  return response.json();
}

export async function fetchTrackingSpeciesList(): Promise<TrackingSpeciesSummary[]> {
  const response = await fetch(`${API_BASE}/tracking/species`);
  if (!response.ok) {
    throw new Error('Failed to load tracking species');
  }
  return response.json();
}

export async function fetchTrackingPoints(species: string): Promise<TrackingResponse> {
  const response = await fetch(`${API_BASE}/tracking/points?species=${encodeURIComponent(species)}`);
  if (!response.ok) {
    throw new Error('Failed to load tracking points');
  }
  return response.json();
}

export async function fetchTrackingReport(): Promise<TrackingReportResponse> {
  const response = await fetch(`${API_BASE}/tracking/report`);
  if (!response.ok) {
    throw new Error('Failed to load tracking report');
  }
  return response.json();
}

export async function fetchPredictionExperiments(): Promise<PredictionExperimentResponse> {
  const response = await fetch(`${API_BASE}/predictions/experiments`);
  if (!response.ok) {
    throw new Error('Failed to load prediction experiments');
  }
  return response.json();
}

export async function fetchTemperature(latitude: number, longitude: number, year: number, month: number): Promise<{ temperature: number }> {
  const response = await fetch(
    `${API_BASE}/temperature?latitude=${encodeURIComponent(latitude)}&longitude=${encodeURIComponent(longitude)}&year=${encodeURIComponent(year)}&month=${encodeURIComponent(month)}`
  );
  if (!response.ok) {
    throw new Error('Failed to load temperature data');
  }
  return response.json();
}

export async function fetchClusteredRoutePoints(): Promise<ClusteredRoutePoint[]> {
  const response = await fetch(`${API_BASE}/clustering/routes`);
  if (!response.ok) {
    throw new Error('Failed to load clustering routes');
  }
  return response.json();
}
