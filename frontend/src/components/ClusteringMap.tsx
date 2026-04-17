import { useMemo } from 'react';
import { MapContainer, Polyline, TileLayer } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { ClusteredRoutePoint } from '../types';

function safePoint(point: ClusteredRoutePoint): [number, number] {
  return [point.gps_yy ?? 0, point.gps_xx ?? 0];
}

function smoothCoordinates(coordinates: [number, number][], iterations = 1): [number, number][] {
  let result = coordinates;
  for (let k = 0; k < iterations; k++) {
    const next: [number, number][] = [];
    for (let i = 0; i < result.length - 1; i++) {
      const [y1, x1] = result[i];
      const [y2, x2] = result[i + 1];
      next.push([y1, x1]);
      next.push([y1 * 0.75 + y2 * 0.25, x1 * 0.75 + x2 * 0.25]);
      next.push([y1 * 0.25 + y2 * 0.75, x1 * 0.25 + x2 * 0.75]);
    }
    next.push(result[result.length - 1]);
    result = next;
  }
  return result;
}

const clusterColors: Record<number, string> = {
  1: '#0ea5e9',
  2: '#f97316',
  3: '#22c55e',
};

interface ClusteringMapProps {
  points: ClusteredRoutePoint[];
  selectedCluster: number | 'all';
}

export default function ClusteringMap({ points, selectedCluster }: ClusteringMapProps) {
  const filtered = useMemo(() => {
    if (selectedCluster === 'all') return points;
    return points.filter((point) => point.cluster_id === selectedCluster);
  }, [points, selectedCluster]);

  const routePolylines = useMemo(() => {
    const groups = new Map<string, ClusteredRoutePoint[]>();
    filtered.forEach((point) => {
      if (!groups.has(point.route_key)) {
        groups.set(point.route_key, []);
      }
      groups.get(point.route_key)!.push(point);
    });

    return Array.from(groups.values()).map((route) => {
      const ordered = [...route].sort((a, b) => (a.sequence_index ?? 0) - (b.sequence_index ?? 0));
      const coords = ordered.map(safePoint).filter(([lat, lon]) => lat !== 0 && lon !== 0);
      return {
        clusterId: ordered[0]?.cluster_id ?? 1,
        positions: coords.length > 2 ? smoothCoordinates(coords, 1) : coords,
      };
    });
  }, [filtered]);

  return (
    <MapContainer center={[20, 0]} zoom={2} minZoom={2} scrollWheelZoom={true} className="map-container">
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; OpenStreetMap contributors"
      />
      {routePolylines.map((poly, index) => (
        <Polyline
          key={`${poly.clusterId}-${index}`}
          positions={poly.positions}
          pathOptions={{
            color: clusterColors[poly.clusterId] ?? '#64748b',
            weight: 2.5,
            opacity: 0.4,
            smoothFactor: 1.0,
          }}
        />
      ))}
    </MapContainer>
  );
}
