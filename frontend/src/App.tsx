import { useEffect, useMemo, useState } from 'react';
import { fetchClusteredRoutePoints, fetchRoutePoints, fetchSpeciesList } from './services/api';
import type { ClusteredRoutePoint, MigrationPoint, RouteGroup, SpeciesSummary } from './types';
import ClusteringMap from './components/ClusteringMap';
import MapPlayer from './components/MapPlayer';

const speciesColors = ['#1d4ed8', '#16a34a', '#c026d3', '#f59e0b', '#db2777', '#0ea5e9'];

function getSpeciesColor(species: string): string {
  if (!species) return speciesColors[0];
  const sum = species.split('').reduce((acc, ch) => acc + ch.charCodeAt(0), 0);
  return speciesColors[sum % speciesColors.length];
}

function buildRouteGroups(points: MigrationPoint[]): RouteGroup[] {
  const groups = new Map<number, { points: MigrationPoint[]; firstIndex: number }>();

  points.forEach((point, index) => {
    const routeCode = point.route_code ?? -1;
    if (!groups.has(routeCode)) {
      groups.set(routeCode, { points: [], firstIndex: index });
    }
    groups.get(routeCode)!.points.push(point);
  });

  return Array.from(groups.entries())
    .sort(([, a], [, b]) => a.firstIndex - b.firstIndex)
    .map(([routeCode, group], index) => {
      const orderedPoints = group.points.sort((a, b) => (a.id ?? 0) - (b.id ?? 0));
      const origin = orderedPoints.find((p) => p.node?.toLowerCase().includes('origin')) ?? orderedPoints[0];
      const destination = orderedPoints.find((p) => p.node?.toLowerCase().includes('destination')) ?? orderedPoints[orderedPoints.length - 1];
      return {
        routeId: index + 1,
        routeCode,
        origin,
        destination,
        points: orderedPoints,
      };
    });
}

function App() {
  const [page, setPage] = useState<'map' | 'clustering'>('map');
  const [speciesList, setSpeciesList] = useState<SpeciesSummary[]>([]);
  const [selectedSpecies, setSelectedSpecies] = useState<string>('');
  const [routePoints, setRoutePoints] = useState<MigrationPoint[]>([]);
  const [activeRouteId, setActiveRouteId] = useState<number | null>(null);
  const [clusteredPoints, setClusteredPoints] = useState<ClusteredRoutePoint[]>([]);
  const [selectedCluster, setSelectedCluster] = useState<number | 'all'>('all');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [clusteringLoading, setClusteringLoading] = useState(false);

  useEffect(() => {
    fetchSpeciesList()
      .then(setSpeciesList)
      .catch(() => setError('Unable to load species list'));
  }, []);

  useEffect(() => {
    if (!selectedSpecies) {
      setRoutePoints([]);
      setActiveRouteId(null);
      return;
    }

    setLoading(true);
    setError(null);

    fetchRoutePoints(selectedSpecies)
      .then((route) => {
        setRoutePoints(route);
      })
      .catch((err) => {
        setError(err.message);
        setRoutePoints([]);
      })
      .finally(() => setLoading(false));
  }, [selectedSpecies]);

  useEffect(() => {
    if (page !== 'clustering' || clusteredPoints.length > 0) {
      return;
    }

    setClusteringLoading(true);
    setError(null);

    fetchClusteredRoutePoints()
      .then((points) => setClusteredPoints(points))
      .catch((err) => setError(err.message))
      .finally(() => setClusteringLoading(false));
  }, [page, clusteredPoints.length]);

  const routeGroups = useMemo(() => buildRouteGroups(routePoints), [routePoints]);

  useEffect(() => {
    if (routeGroups.length > 0) {
      setActiveRouteId((current) => current ?? routeGroups[0].routeId);
    } else {
      setActiveRouteId(null);
    }
  }, [routeGroups]);

  const baseColor = useMemo(() => getSpeciesColor(selectedSpecies), [selectedSpecies]);
  const activeRouteGroup = routeGroups.find((group) => group.routeId === activeRouteId) ?? routeGroups[0] ?? null;

  const clusterStats = useMemo(() => {
    const routeMap = new Map<string, number>();
    clusteredPoints.forEach((point) => {
      if (!routeMap.has(point.route_key)) {
        routeMap.set(point.route_key, point.cluster_id);
      }
    });

    const counts = { all: routeMap.size, 1: 0, 2: 0, 3: 0 };
    routeMap.forEach((clusterId) => {
      if (clusterId === 1 || clusterId === 2 || clusterId === 3) {
        counts[clusterId] += 1;
      }
    });
    return counts;
  }, [clusteredPoints]);

  return (
    <div className="app-shell">
      <header className="hero">
        <div>
          <h1>Bird Migration Visualizer</h1>
          <p>
            Explore migration patterns in two views: detailed species routes in Map and behavior groups in Clustering.
          </p>
        </div>
        <div className="top-nav" role="tablist" aria-label="Main navigation">
          <button
            type="button"
            role="tab"
            aria-selected={page === 'map'}
            className={`nav-tab ${page === 'map' ? 'active' : ''}`}
            onClick={() => setPage('map')}
          >
            Map
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={page === 'clustering'}
            className={`nav-tab ${page === 'clustering' ? 'active' : ''}`}
            onClick={() => setPage('clustering')}
          >
            Clustering
          </button>
        </div>
        {page === 'map' ? (
        <div className="controls">
          <label htmlFor="species-select">Choose a bird species</label>
          <select
            id="species-select"
            value={selectedSpecies}
            onChange={(event) => setSelectedSpecies(event.target.value)}
          >
            <option value="">Select species</option>
            {speciesList.map((item) => (
              <option key={item.species} value={item.species}>
                {item.common_name ?? item.species} ({item.species})
              </option>
            ))}
          </select>
        </div>
        ) : (
          <div className="controls">
            <label htmlFor="cluster-select">Show clusters</label>
            <select
              id="cluster-select"
              value={selectedCluster}
              onChange={(event) => {
                const value = event.target.value;
                setSelectedCluster(value === 'all' ? 'all' : Number(value));
              }}
            >
              <option value="all">All clusters ({clusterStats.all} routes)</option>
              <option value="1">Cluster 1 ({clusterStats[1]} routes)</option>
              <option value="2">Cluster 2 ({clusterStats[2]} routes)</option>
              <option value="3">Cluster 3 ({clusterStats[3]} routes)</option>
            </select>
          </div>
        )}
      </header>

      {error && <div className="alert">{error}</div>}
      {page === 'map' && loading && <div className="alert">Loading route data...</div>}
      {page === 'clustering' && clusteringLoading && <div className="alert">Loading clustering data...</div>}

      <main className="content-grid">
        <section className="map-card">
          {page === 'map' ? (
            <MapPlayer
              routeGroups={routeGroups}
              activeRouteGroup={activeRouteGroup}
              baseColor={baseColor}
              onRouteSelect={(id) => setActiveRouteId(id)}
            />
          ) : (
            <ClusteringMap points={clusteredPoints} selectedCluster={selectedCluster} />
          )}
        </section>
        <section className="info-card">
          {page === 'map' ? (
            <>
              <h2>Route summary</h2>
              {selectedSpecies ? (
                routeGroups.length > 0 ? (
                  <>
                    <div className="route-summary">
                      <p>{routePoints.length} recorded migration points loaded.</p>
                      <p>{routeGroups.length} separate route{routeGroups.length > 1 ? 's' : ''} detected for this species.</p>
                    </div>

                    <div className="route-list">
                      {routeGroups.map((group) => (
                        <button
                          key={group.routeId}
                          type="button"
                          className={`route-card ${group.routeId === activeRouteId ? 'active' : ''}`}
                          onClick={() => setActiveRouteId(group.routeId)}
                        >
                          <div className="route-card-header">
                            <span>Route {group.routeId}</span>
                            <span>{group.points.length} points</span>
                          </div>
                          <div className="route-card-body">
                            <div><strong>Origin:</strong> {group.origin?.node ?? 'Unknown'}</div>
                            <div><strong>Destination:</strong> {group.destination?.node ?? 'Unknown'}</div>
                          </div>
                        </button>
                      ))}
                    </div>
                  </>
                ) : (
                  <p>No route information found for this species.</p>
                )
              ) : (
                <p>Select a species to load migration routes.</p>
              )}
            </>
          ) : (
            <>
              <h2>Clustering summary</h2>
              <div className="route-summary">
                <p>Routes are grouped with k-means (k=3) based on distance, straightness, and turning behavior.</p>
                <p>Use the filter above to inspect all clusters together or each cluster independently.</p>
              </div>
              <div className="cluster-legend">
                <div><span className="legend-dot cluster-1" />Cluster 1: medium-distance mixed stability</div>
                <div><span className="legend-dot cluster-2" />Cluster 2: long-distance flexible/complex</div>
                <div><span className="legend-dot cluster-3" />Cluster 3: short-distance stable/direct</div>
              </div>
            </>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
