import { useEffect, useMemo, useState } from 'react';
import { fetchRoutePoints, fetchSpeciesList } from './services/api';
import type { MigrationPoint, RouteGroup, SpeciesSummary } from './types';
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
  const [speciesList, setSpeciesList] = useState<SpeciesSummary[]>([]);
  const [selectedSpecies, setSelectedSpecies] = useState<string>('');
  const [routePoints, setRoutePoints] = useState<MigrationPoint[]>([]);
  const [activeRouteId, setActiveRouteId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

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

  return (
    <div className="app-shell">
      <header className="hero">
        <div>
          <h1>Bird Migration Visualizer</h1>
          <p>
            Explore historical migration routes and prediction previews for species in the dataset.
            Use the timeline slider to inspect where the bird is at each stage.
          </p>
        </div>
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
      </header>

      {error && <div className="alert">{error}</div>}
      {loading && <div className="alert">Loading route data...</div>}

      <main className="content-grid">
        <section className="map-card">
          <MapPlayer
            routeGroups={routeGroups}
            activeRouteGroup={activeRouteGroup}
            baseColor={baseColor}
            onRouteSelect={(id) => setActiveRouteId(id)}
          />
        </section>
        <section className="info-card">
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
        </section>
      </main>
    </div>
  );
}

export default App;
