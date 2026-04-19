import { useMemo } from 'react';
import DensityMap from './DensityMap';
import type { ClusteredRoutePoint } from '../types';

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

  const baseColor = selectedCluster === 'all' ? '#0f766e' : clusterColors[selectedCluster] ?? '#0f766e';

  return <DensityMap points={filtered} baseColor={baseColor} emptyMessage="No clustered route nodes are available for this filter." />;
}
