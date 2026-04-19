import { useEffect, useMemo, useState } from 'react';
import { fetchPredictionExperiments, fetchRouteAggregates, fetchRoutePoints, fetchSpeciesList, fetchTrackingPoints, fetchTrackingReport, fetchTrackingSpeciesList } from './services/api';
import type { MigrationPoint, PredictionExperimentResponse, RouteAggregationResponse, SpeciesSummary, TrackingReportResponse, TrackingResponse, TrackingSpeciesSummary } from './types';
import DensityMap from './components/DensityMap';
import TrackingMap from './components/TrackingMap';
import { standardizePointGeoNames } from './utils/geoStandardization';

const ALL_SPECIES_VALUE = '__all_species__';

const speciesColors = ['#1d4ed8', '#16a34a', '#c026d3', '#f59e0b', '#db2777', '#0ea5e9'];

function getSpeciesColor(species: string): string {
  if (!species) return speciesColors[0];
  const sum = species.split('').reduce((acc, ch) => acc + ch.charCodeAt(0), 0);
  return speciesColors[sum % speciesColors.length];
}

interface MigrationStats {
  nodeCount: number;
  countryCount: number;
  stateCount: number;
  originCount: number;
  destinationCount: number;
  avgMigrationMonths: number;
}

function calculateMigrationStats(points: MigrationPoint[]): MigrationStats {
  if (points.length === 0) {
    return { nodeCount: 0, countryCount: 0, stateCount: 0, originCount: 0, destinationCount: 0, avgMigrationMonths: 0 };
  }

  const countries = new Set<string>();
  const states = new Set<string>();
  const origins = new Set<string>();
  const destinations = new Set<string>();
  let totalMonths = 0;
  let monthCount = 0;

  points.forEach((point) => {
    if (point.country) countries.add(point.country);
    if (point.province) states.add(point.province);
    if (point.node?.toLowerCase().includes('origin')) {
      origins.add(`${point.country}::${point.province}`);
    }
    if (point.node?.toLowerCase().includes('destination')) {
      destinations.add(`${point.country}::${point.province}`);
    }

    if (point.start_month != null && point.estimated_month != null) {
      let monthDiff = (point.estimated_month - point.start_month) % 12;
      if (monthDiff < 0) monthDiff += 12;
      totalMonths += monthDiff;
      monthCount++;
    }
  });

  return {
    nodeCount: points.length,
    countryCount: countries.size,
    stateCount: states.size,
    originCount: origins.size,
    destinationCount: destinations.size,
    avgMigrationMonths: monthCount > 0 ? totalMonths / monthCount : 0,
  };
}

function App() {
  const [page, setPage] = useState<'map' | 'tracking' | 'prediction'>('map');
  const [speciesList, setSpeciesList] = useState<SpeciesSummary[]>([]);
  const [selectedSpecies, setSelectedSpecies] = useState<string>(ALL_SPECIES_VALUE);
  const [routePoints, setRoutePoints] = useState<MigrationPoint[]>([]);
  const [allSpeciesAggregates, setAllSpeciesAggregates] = useState<RouteAggregationResponse | null>(null);
  const [trackingSpeciesList, setTrackingSpeciesList] = useState<TrackingSpeciesSummary[]>([]);
  const [trackingReport, setTrackingReport] = useState<TrackingReportResponse | null>(null);
  const [predictionReport, setPredictionReport] = useState<PredictionExperimentResponse | null>(null);
  const [selectedTrackingSpecies, setSelectedTrackingSpecies] = useState<string>('');
  const [trackingData, setTrackingData] = useState<TrackingResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSpeciesList()
      .then(setSpeciesList)
      .catch(() => setError('Unable to load species list'));

    fetchTrackingSpeciesList()
      .then((items) => {
        setTrackingSpeciesList(items);
        if (items.length > 0) {
          setSelectedTrackingSpecies(items[0].species);
        }
      })
      .catch(() => setError('Unable to load tracking species list'));
  }, []);

  useEffect(() => {
    if (page !== 'tracking' || trackingReport) {
      return;
    }

    fetchTrackingReport()
      .then(setTrackingReport)
      .catch(() => {
        // Keep tracking playback usable even if report aggregation fails.
      });
  }, [page, trackingReport]);

  useEffect(() => {
    if (page !== 'prediction' || predictionReport) {
      return;
    }

    fetchPredictionExperiments()
      .then(setPredictionReport)
      .catch((err) => {
        setError(err.message);
      });
  }, [page, predictionReport]);

  useEffect(() => {
    setLoading(true);
    setError(null);

    if (selectedSpecies === ALL_SPECIES_VALUE) {
      fetchRouteAggregates()
        .then((aggregates) => {
          setAllSpeciesAggregates(aggregates);
          setRoutePoints([]);
        })
        .catch((err) => {
          setError(err.message);
          setAllSpeciesAggregates(null);
          setRoutePoints([]);
        })
        .finally(() => setLoading(false));
      return;
    }

    fetchRoutePoints(selectedSpecies)
      .then((route) => {
        setRoutePoints(route.map((point) => standardizePointGeoNames(point)));
        setAllSpeciesAggregates(null);
      })
      .catch((err) => {
        setError(err.message);
        setRoutePoints([]);
        setAllSpeciesAggregates(null);
      })
      .finally(() => setLoading(false));
  }, [selectedSpecies]);

  useEffect(() => {
    if (page !== 'tracking' || !selectedTrackingSpecies) {
      return;
    }

    setLoading(true);
    setError(null);

    fetchTrackingPoints(selectedTrackingSpecies)
      .then((response) => setTrackingData(response))
      .catch((err) => {
        setError(err.message);
        setTrackingData(null);
      })
      .finally(() => setLoading(false));
  }, [page, selectedTrackingSpecies]);

  const baseColor = useMemo(() => getSpeciesColor(selectedSpecies), [selectedSpecies]);
  const migrationStats = useMemo(() => calculateMigrationStats(routePoints), [routePoints]);
  const summary = selectedSpecies === ALL_SPECIES_VALUE && allSpeciesAggregates
    ? {
        nodeCount: allSpeciesAggregates.summary.node_count,
        countryCount: allSpeciesAggregates.summary.country_count,
        stateCount: allSpeciesAggregates.summary.state_count,
        originCount: allSpeciesAggregates.summary.origin_count,
        destinationCount: allSpeciesAggregates.summary.destination_count,
        avgMigrationMonths: allSpeciesAggregates.summary.avg_migration_months,
      }
    : migrationStats;
  const selectedTrackingSummary = useMemo(
    () => trackingSpeciesList.find((item) => item.species === selectedTrackingSpecies) ?? null,
    [selectedTrackingSpecies, trackingSpeciesList]
  );

  return (
    <div className="app-shell">
      <header className="hero">
        <div>
          <h1>Bird Migration Visualizer</h1>
          <p>
            Explore migration density through real geographic polygons, or replay timestamped movement traces from the tracking datasets.
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
            aria-selected={page === 'tracking'}
            className={`nav-tab ${page === 'tracking' ? 'active' : ''}`}
            onClick={() => setPage('tracking')}
          >
            Tracking
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={page === 'prediction'}
            className={`nav-tab ${page === 'prediction' ? 'active' : ''}`}
            onClick={() => setPage('prediction')}
          >
            Prediction
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
              <option value={ALL_SPECIES_VALUE}>All species</option>
              {speciesList.map((item) => (
                <option key={item.species} value={item.species}>
                  {item.common_name ?? item.species} ({item.species})
                </option>
              ))}
            </select>
          </div>
        ) : page === 'tracking' ? (
          <div className="controls">
            <label htmlFor="tracking-species-select">Choose a tracking species</label>
            <select
              id="tracking-species-select"
              value={selectedTrackingSpecies}
              onChange={(event) => setSelectedTrackingSpecies(event.target.value)}
            >
              {trackingSpeciesList.map((item) => (
                <option key={item.species} value={item.species}>
                  {item.species}
                </option>
              ))}
            </select>
          </div>
        ) : (
          <div className="controls">
            <label>Experiment species</label>
            <select disabled value="Barn Swallow + Osprey">
              <option>Barn Swallow + Osprey</option>
            </select>
          </div>
        )}
      </header>

      {error && <div className="alert">{error}</div>}
      {loading && <div className="alert">{page === 'tracking' ? 'Loading tracking data...' : 'Loading route data...'}</div>}

      <main className="content-grid">
        <section className="map-card">
          {page === 'map' ? (
            <DensityMap
              points={routePoints}
              aggregatedAreas={selectedSpecies === ALL_SPECIES_VALUE ? allSpeciesAggregates?.counts : undefined}
              baseColor={baseColor}
              emptyMessage="No migration nodes available for this species."
            />
          ) : page === 'tracking' ? (
            <TrackingMap
              species={selectedTrackingSpecies}
              points={trackingData?.points ?? []}
              emptyMessage="No tracking points are available for this species."
            />
          ) : (
            <div className="prediction-panel">
              <h2>{predictionReport?.title ?? 'Species Discrimination Experiments'}</h2>
              {predictionReport ? (
                <>
                  <p className="prediction-intro">{predictionReport.report}</p>
                  <div className="prediction-methodology">
                    <h3>How travel distance is calculated</h3>
                    <p>{predictionReport.travel_distance_method}</p>
                    <h3>How seasons are assigned</h3>
                    <p>{predictionReport.season_assignment_method}</p>
                    <h3>How model performance is evaluated</h3>
                    <p>{predictionReport.evaluation_protocol}</p>
                  </div>
                  <div className="prediction-validation-steps">
                    <h3>How 5-fold cross-validation works</h3>
                    <div className="prediction-validation-step">
                      <strong>Step 1.</strong>
                      <span>The full dataset is split into 5 approximately equal folds, while keeping the Barn Swallow/Osprey class balance similar in each fold.</span>
                    </div>
                    <div className="prediction-validation-step">
                      <strong>Step 2.</strong>
                      <span>For each round, 4 folds are used for training and the remaining 1 fold is used for testing.</span>
                    </div>
                    <div className="prediction-validation-step">
                      <strong>Step 3.</strong>
                      <span>This process repeats 5 times, so every sample is used for testing exactly once and for training 4 times.</span>
                    </div>
                    <div className="prediction-validation-step">
                      <strong>Step 4.</strong>
                      <span>The predictions from all 5 test folds are combined into one out-of-fold result set.</span>
                    </div>
                    <div className="prediction-validation-step">
                      <strong>Step 5.</strong>
                      <span>Accuracy, F1, and ROC/AUC are computed from that combined out-of-fold result, giving a more stable estimate than a single train/test split.</span>
                    </div>
                  </div>
                  <div className="prediction-method-table">
                    <div className="prediction-row prediction-head">
                      <span>Method</span>
                      <span>Type</span>
                      <span>Accuracy</span>
                      <span>F1</span>
                      <span>ROC/AUC</span>
                    </div>
                    {predictionReport.methods.map((method) => (
                      <div key={method.name} className={`prediction-row ${method.name === predictionReport.best_method ? 'best' : ''}`}>
                        <span>{method.name}</span>
                        <span>{method.category}</span>
                        <span>{method.accuracy.toFixed(3)}</span>
                        <span>{method.f1.toFixed(3)}</span>
                        <span>{method.roc_auc != null ? method.roc_auc.toFixed(3) : 'N/A'}</span>
                      </div>
                    ))}
                  </div>
                  <div className="prediction-method-notes">
                    <h3>How each method makes predictions</h3>
                    {predictionReport.methods.map((method) => (
                      <div key={`${method.name}-note`} className="prediction-method-note-card">
                        <div className="prediction-method-note-title">{method.name}</div>
                        <div className="prediction-method-note-text">{method.notes ?? 'No method explanation provided.'}</div>
                      </div>
                    ))}
                  </div>
                  <div className="prediction-features-detail">
                    <h3>All engineered features ({predictionReport.feature_definitions.length})</h3>
                    {predictionReport.feature_definitions.map((item) => (
                      <div key={item.feature} className="prediction-feature-card">
                        <div className="prediction-feature-name">{item.feature}</div>
                        <div className="prediction-feature-plain">{item.plain_language}</div>
                        <div className="prediction-feature-formula">{item.calculation}</div>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <p>Loading experiment report...</p>
              )}
            </div>
          )}
        </section>
        <section className="info-card">
          {page === 'map' ? (
            <>
              <h2>Migration summary</h2>
              {selectedSpecies ? (
                summary.nodeCount > 0 ? (
                  <div className="migration-stats">
                    <div className="stat-item">
                      <span className="stat-label">Total recorded nodes:</span>
                      <span className="stat-value">{summary.nodeCount}</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Countries traversed:</span>
                      <span className="stat-value">{summary.countryCount}</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">States/provinces:</span>
                      <span className="stat-value">{summary.stateCount}</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Origin points:</span>
                      <span className="stat-value">{summary.originCount}</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Destination points:</span>
                      <span className="stat-value">{summary.destinationCount}</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Avg. migration duration:</span>
                      <span className="stat-value">{summary.avgMigrationMonths.toFixed(1)} months</span>
                    </div>
                    <p className="stat-description">
                      The map shows migration density aggregated into real geographic polygons (states, provinces, and countries). Darker colors indicate higher concentration of migration activity.
                    </p>
                  </div>
                ) : (
                  <p>No migration data available for this species.</p>
                )
              ) : (
                <p>Select a species to view its migration density map and statistics.</p>
              )}
            </>
          ) : page === 'tracking' ? (
            <>
              <h2>Tracking summary</h2>
              {selectedTrackingSummary && trackingData ? (
                <div className="migration-stats">
                  <div className="stat-item">
                    <span className="stat-label">Tracking CSV files:</span>
                    <span className="stat-value">{selectedTrackingSummary.csv_count}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Tracked individuals:</span>
                    <span className="stat-value">{trackingData.individual_count}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Tracking points:</span>
                    <span className="stat-value">{trackingData.point_count}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Playback order:</span>
                    <span className="stat-value">Month-Day-Time</span>
                  </div>
                  {trackingReport && (
                    <>
                      <div className="stat-item">
                        <span className="stat-label">All species in report:</span>
                        <span className="stat-value">{trackingReport.totals.species_count}</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">All tracked individuals:</span>
                        <span className="stat-value">{trackingReport.totals.individual_count}</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">All tracking points:</span>
                        <span className="stat-value">{trackingReport.totals.point_count}</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">All removed stationary points:</span>
                        <span className="stat-value">{trackingReport.totals.removed_point_count}</span>
                      </div>
                    </>
                  )}
                  <p className="stat-description">
                    The tracking page replays all individuals for the selected species as a repeating annual timeline (from 01-01 to 12-31) using month-day-time order. Long stationary runs at identical coordinates are condensed before rendering.
                  </p>
                </div>
              ) : (
                <p>Select a tracking species to replay its movement traces.</p>
              )}
            </>
          ) : (
            <>
              <h2>Prediction report</h2>
              {predictionReport ? (
                <div className="migration-stats">
                  <div className="stat-item">
                    <span className="stat-label">Experiment samples:</span>
                    <span className="stat-value">{predictionReport.dataset.sample_count}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Engineered features:</span>
                    <span className="stat-value">{predictionReport.dataset.feature_count}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Best method:</span>
                    <span className="stat-value">{predictionReport.best_method}</span>
                  </div>

                  {predictionReport.species_profiles.map((profile) => (
                    <div key={profile.species} className="prediction-profile">
                      <h3>{profile.species}</h3>
                      <div>Individuals: {profile.individual_count}</div>
                      <div>Mean daily distance: {profile.mean_daily_distance_km.toFixed(1)} km/day</div>
                      <div>Mean location: ({profile.mean_latitude.toFixed(1)}, {profile.mean_longitude.toFixed(1)})</div>
                    </div>
                  ))}

                  <div className="prediction-feature-list">
                    <h3>Top discriminative features</h3>
                    {predictionReport.top_features.slice(0, 6).map((item) => (
                      <div key={item.feature} className="stat-item">
                        <span className="stat-label">{item.feature}</span>
                        <span className="stat-value">{item.score.toFixed(3)}</span>
                      </div>
                    ))}
                  </div>
                  <p className="stat-description">
                    Audience note: the full feature definitions and formulas are shown in the left Prediction panel, including the Haversine travel-distance computation and seasonal assignment rules.
                  </p>
                </div>
              ) : (
                <p>The experiment report will appear after data is loaded.</p>
              )}
            </>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
