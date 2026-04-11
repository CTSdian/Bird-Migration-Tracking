import type { MigrationPoint, PredictionsResponse, SpeciesSummary } from '../types';

const API_BASE = '/api';

export async function fetchSpeciesList(): Promise<SpeciesSummary[]> {
  const response = await fetch(`${API_BASE}/species`);
  if (!response.ok) {
    throw new Error('Failed to load species list');
  }
  return response.json();
}

export async function fetchRoutePoints(species: string): Promise<MigrationPoint[]> {
  const response = await fetch(`${API_BASE}/routes?species=${encodeURIComponent(species)}`);
  if (!response.ok) {
    throw new Error('Failed to load route points');
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
