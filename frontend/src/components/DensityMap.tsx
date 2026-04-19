import { useEffect, useMemo, useState, type CSSProperties } from 'react';
import { Circle, CircleMarker, GeoJSON, MapContainer, Popup, TileLayer, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { normalizeGeoName } from '../utils/geoStandardization';
import type { RouteAreaCount } from '../types';

type DensityPoint = {
  gps_xx?: number;
  gps_yy?: number;
  country?: string;
  province?: string;
  node?: string;
};

type DensityRing = {
  radius: number;
  color: string;
  opacity: number;
};

type GeoJsonFeature = {
  type: 'Feature';
  properties: Record<string, unknown>;
  geometry: GeoJSON.Geometry;
};

type GeoJsonCollection = {
  type: 'FeatureCollection';
  features: GeoJsonFeature[];
};

type CountedFeature = GeoJsonFeature & {
  count: number;
  label: string;
  parentLabel?: string;
};

interface DensityMapProps<T extends DensityPoint> {
  points: T[];
  aggregatedAreas?: RouteAreaCount[];
  baseColor: string;
  highlightedPoint?: T | null;
  highlightRings?: DensityRing[];
  emptyMessage?: string;
}

const COUNTRY_URL = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson';
const ADMIN1_URL = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_1_states_provinces.geojson';

function isValidCoordinate(latitude?: number, longitude?: number): latitude is number {
  return latitude != null && longitude != null && Number.isFinite(latitude) && Number.isFinite(longitude);
}

function buildFeatureCandidates(feature: GeoJsonFeature): string[] {
  const values = [
    feature.properties.NAME,
    feature.properties.name,
    feature.properties.NAME_EN,
    feature.properties.name_en,
    feature.properties.NAME_ALT,
    feature.properties.name_alt,
    feature.properties.WOE_NAME,
    feature.properties.woe_name,
    feature.properties.ABBREV,
    feature.properties.abbrev,
    feature.properties.POSTAL,
    feature.properties.postal,
  ];

  return Array.from(new Set(values.map(normalizeGeoName).filter(Boolean)));
}

function getFeatureCountry(feature: GeoJsonFeature): string {
  return normalizeGeoName(
    feature.properties.ADMIN ??
    feature.properties.admin ??
    feature.properties.geonunit ??
    feature.properties.GEOUNIT ??
    feature.properties.geounit ??
    feature.properties.name
  );
}

function getCountryFeatureNames(feature: GeoJsonFeature): string[] {
  const values = [
    feature.properties.ADMIN,
    feature.properties.admin,
    feature.properties.NAME,
    feature.properties.name,
    feature.properties.NAME_EN,
    feature.properties.name_en,
    feature.properties.GEOUNIT,
    feature.properties.geounit,
    feature.properties.SUBUNIT,
    feature.properties.subunit,
    feature.properties.BRK_NAME,
    feature.properties.brk_name,
    feature.properties.FORMAL_EN,
    feature.properties.formal_en,
  ];

  return Array.from(new Set(values.map(normalizeGeoName).filter(Boolean)));
}

function makeAreaLabel(feature: GeoJsonFeature): string {
  const values = [feature.properties.NAME_EN, feature.properties.name_en, feature.properties.NAME, feature.properties.name, feature.properties.ADMIN, feature.properties.admin, feature.properties.GEOUNIT, feature.properties.geonunit];
  const label = values.find((value) => typeof value === 'string' && value.trim().length > 0);
  return typeof label === 'string' ? label : 'Unknown area';
}

function makeParentLabel(feature: GeoJsonFeature): string | undefined {
  const value = feature.properties.ADMIN ?? feature.properties.admin ?? feature.properties.GEOUNIT ?? feature.properties.geounit;
  return typeof value === 'string' && value.trim().length > 0 ? value : undefined;
}

function hexToRgb(hex: string): [number, number, number] {
  const normalized = hex.replace('#', '');
  const value = normalized.length === 3
    ? normalized
        .split('')
        .map((char) => `${char}${char}`)
        .join('')
    : normalized;
  const parsed = Number.parseInt(value, 16);
  return [(parsed >> 16) & 255, (parsed >> 8) & 255, parsed & 255];
}

function mixColor(baseColor: string, ratio: number): string {
  const [red, green, blue] = hexToRgb(baseColor);
  const weight = Math.max(0.18, Math.min(1, ratio));
  const mix = (channel: number) => Math.round(247 + (channel - 247) * weight);
  return `rgb(${mix(red)}, ${mix(green)}, ${mix(blue)})`;
}

function DensityBounds({ positions, highlightedPoint }: { positions: [number, number][]; highlightedPoint?: DensityPoint | null }) {
  const map = useMap();

  useEffect(() => {
    const boundsPoints = [...positions];
    if (highlightedPoint && isValidCoordinate(highlightedPoint.gps_yy, highlightedPoint.gps_xx)) {
      boundsPoints.push([highlightedPoint.gps_yy, highlightedPoint.gps_xx]);
    }

    if (boundsPoints.length === 0) {
      return;
    }

    if (boundsPoints.length === 1) {
      map.setView(boundsPoints[0], 4);
      return;
    }

    map.fitBounds(L.latLngBounds(boundsPoints), { padding: [40, 40], maxZoom: 6 });
  }, [highlightedPoint, map, positions]);

  return null;
}

export default function DensityMap<T extends DensityPoint>({
  points,
  aggregatedAreas,
  baseColor,
  highlightedPoint,
  highlightRings = [],
  emptyMessage = 'No geographic blocks available for this selection.',
}: DensityMapProps<T>) {
  const [countryBoundaries, setCountryBoundaries] = useState<GeoJsonCollection | null>(null);
  const [adminBoundaries, setAdminBoundaries] = useState<GeoJsonCollection | null>(null);
  const [boundaryError, setBoundaryError] = useState<string | null>(null);
  const [boundariesLoading, setBoundariesLoading] = useState(true);

  useEffect(() => {
    const abortController = new AbortController();

    async function loadBoundaries() {
      setBoundariesLoading(true);
      setBoundaryError(null);

      try {
        const [countryResponse, adminResponse] = await Promise.all([
          fetch(COUNTRY_URL, { signal: abortController.signal }),
          fetch(ADMIN1_URL, { signal: abortController.signal }),
        ]);

        if (!countryResponse.ok || !adminResponse.ok) {
          throw new Error('Boundary download failed');
        }

        const [countryJson, adminJson] = (await Promise.all([countryResponse.json(), adminResponse.json()])) as [GeoJsonCollection, GeoJsonCollection];
        setCountryBoundaries(countryJson);
        setAdminBoundaries(adminJson);
      } catch (error) {
        if ((error as Error).name === 'AbortError') {
          return;
        }
        setBoundaryError('Unable to load polygon boundaries for the choropleth view.');
      } finally {
        setBoundariesLoading(false);
      }
    }

    void loadBoundaries();
    return () => abortController.abort();
  }, []);

  const aggregatedCounts = useMemo(() => {
    const provinceCounts = new Map<string, number>();
    const countryCounts = new Map<string, number>();
    const positions: [number, number][] = [];

    if (aggregatedAreas && aggregatedAreas.length > 0) {
      aggregatedAreas.forEach((area) => {
        const country = normalizeGeoName(area.country);
        const region = normalizeGeoName(area.province);
        if (!country || area.count <= 0) {
          return;
        }

        if (region) {
          const key = `${country}::${region}`;
          provinceCounts.set(key, (provinceCounts.get(key) ?? 0) + area.count);
          return;
        }

        countryCounts.set(country, (countryCounts.get(country) ?? 0) + area.count);
      });
    } else {
      points.forEach((point) => {
        if (isValidCoordinate(point.gps_yy, point.gps_xx)) {
          positions.push([point.gps_yy, point.gps_xx]);
        }

        const country = normalizeGeoName(point.country);
        const region = normalizeGeoName(point.province);
        if (!country) {
          return;
        }

        if (region) {
          const key = `${country}::${region}`;
          provinceCounts.set(key, (provinceCounts.get(key) ?? 0) + 1);
          return;
        }

        countryCounts.set(country, (countryCounts.get(country) ?? 0) + 1);
      });
    }

    return { provinceCounts, countryCounts, positions };
  }, [aggregatedAreas, points]);

  const choroplethFeatures = useMemo(() => {
    if (!countryBoundaries || !adminBoundaries) {
      return { countries: [] as CountedFeature[], regions: [] as CountedFeature[], unmatchedRegionCount: aggregatedCounts.provinceCounts.size };
    }

    const matchedRegionKeys = new Set<string>();

    const regions = adminBoundaries.features
      .map((feature) => {
        const country = getFeatureCountry(feature);
        const count = buildFeatureCandidates(feature).reduce((sum, candidate) => {
          if (!candidate) {
            return sum;
          }

          const key = `${country}::${candidate}`;
          const value = aggregatedCounts.provinceCounts.get(key) ?? 0;
          if (value > 0) {
            matchedRegionKeys.add(key);
          }
          return sum + value;
        }, 0);

        if (count <= 0) {
          return null;
        }

        return {
          ...feature,
          count,
          label: makeAreaLabel(feature),
          parentLabel: makeParentLabel(feature),
        } satisfies CountedFeature;
      })
      .filter((feature): feature is CountedFeature => feature != null);

    const countryFallback = new Map(aggregatedCounts.countryCounts);
    aggregatedCounts.provinceCounts.forEach((count, key) => {
      if (!matchedRegionKeys.has(key)) {
        const [country] = key.split('::');
        countryFallback.set(country, (countryFallback.get(country) ?? 0) + count);
      }
    });

    const countries = countryBoundaries.features
      .map((feature) => {
        const count = getCountryFeatureNames(feature).reduce((sum, candidate) => sum + (countryFallback.get(candidate) ?? 0), 0);
        if (count <= 0) {
          return null;
        }

        return {
          ...feature,
          count,
          label: makeAreaLabel(feature),
        } satisfies CountedFeature;
      })
      .filter((feature): feature is CountedFeature => feature != null);

    return {
      countries,
      regions,
      unmatchedRegionCount: Array.from(aggregatedCounts.provinceCounts.keys()).filter((key) => !matchedRegionKeys.has(key)).length,
    };
  }, [adminBoundaries, aggregatedCounts.countryCounts, aggregatedCounts.provinceCounts, countryBoundaries]);

  const positions = aggregatedCounts.positions;

  const stats = useMemo(() => {
    const counts = [...choroplethFeatures.countries, ...choroplethFeatures.regions].map((feature) => feature.count);
    if (counts.length === 0) {
      return { min: 0, max: 0 };
    }

    return {
      min: Math.min(...counts),
      max: Math.max(...counts),
    };
  }, [choroplethFeatures.countries, choroplethFeatures.regions]);

  const getFillColor = (count: number) => {
    if (count <= 0 || stats.max === 0) {
      return '#f8fafc';
    }

    const minLog = Math.log1p(stats.min);
    const maxLog = Math.log1p(stats.max);
    const range = Math.max(maxLog - minLog, 1e-9);
    const intensity = (Math.log1p(count) - minLog) / range;
    return mixColor(baseColor, intensity);
  };

  const countryStyle = (feature?: GeoJsonFeature) => {
    const counted = feature as CountedFeature | undefined;
    const count = counted?.count ?? 0;
    return {
      color: '#cbd5e1',
      weight: 0.8,
      fillColor: getFillColor(count),
      fillOpacity: count > 0 ? 0.86 : 0.18,
    };
  };

  const regionStyle = (feature?: GeoJsonFeature) => {
    const counted = feature as CountedFeature | undefined;
    const count = counted?.count ?? 0;
    return {
      color: '#ffffff',
      weight: 1.1,
      fillColor: getFillColor(count),
      fillOpacity: count > 0 ? 0.94 : 0,
    };
  };

  const onEachFeature = (feature: GeoJsonFeature, layer: L.Layer) => {
    const counted = feature as CountedFeature;
    if (!counted.count || !(layer as L.Path & { bindPopup?: (content: string) => void }).bindPopup) {
      return;
    }

    const parentLine = counted.parentLabel ? `<div>${counted.parentLabel}</div>` : '';
    (layer as L.Path & { bindPopup: (content: string) => void }).bindPopup(
      `<div class="density-popup"><strong>${counted.label}</strong>${parentLine}</div>`
    );
  };

  return (
    <div className="density-map-shell">
      <MapContainer
        center={[20, 0]}
        zoom={2}
        minZoom={2}
        scrollWheelZoom={true}
        worldCopyJump={true}
        className="map-container"
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
          attribution="&copy; OpenStreetMap contributors &copy; CARTO"
          noWrap={false}
        />
        <DensityBounds positions={positions} highlightedPoint={highlightedPoint} />
        {choroplethFeatures.countries.map((feature, index) => (
          <GeoJSON key={`country-${feature.label}-${index}`} data={feature as GeoJSON.GeoJsonObject} style={countryStyle} onEachFeature={onEachFeature} />
        ))}
        {choroplethFeatures.regions.map((feature, index) => (
          <GeoJSON key={`region-${feature.label}-${index}`} data={feature as GeoJSON.GeoJsonObject} style={regionStyle} onEachFeature={onEachFeature} />
        ))}
        {highlightedPoint && isValidCoordinate(highlightedPoint.gps_yy, highlightedPoint.gps_xx) && (
          <>
            {highlightRings.map((ring) => (
              <Circle
                key={`${ring.radius}-${ring.color}`}
                center={[highlightedPoint.gps_yy, highlightedPoint.gps_xx]}
                radius={ring.radius}
                pathOptions={{
                  color: ring.color,
                  fillColor: ring.color,
                  fillOpacity: ring.opacity,
                  weight: 0,
                }}
              />
            ))}
            <CircleMarker
              center={[highlightedPoint.gps_yy, highlightedPoint.gps_xx]}
              radius={8}
              pathOptions={{
                color: '#ffffff',
                fillColor: '#0f172a',
                fillOpacity: 1,
                weight: 3,
              }}
            >
              <Popup>
                <div className="density-popup">
                  <strong>{highlightedPoint.node ?? highlightedPoint.province ?? highlightedPoint.country ?? 'Selected point'}</strong>
                  <div>{highlightedPoint.province ?? highlightedPoint.country ?? 'Unknown area'}</div>
                  {highlightedPoint.province && highlightedPoint.country && highlightedPoint.province !== highlightedPoint.country && (
                    <div>{highlightedPoint.country}</div>
                  )}
                </div>
              </Popup>
            </CircleMarker>
          </>
        )}
      </MapContainer>
      <div className="density-scale" aria-live="polite">
        <div className="density-scale-header">
          <strong>Travel Density</strong>
        </div>
        <div className="density-scale-bar" style={{ '--density-base': baseColor } as CSSProperties} />
        <div className="density-scale-labels">
        </div>
        <p className="density-scale-note">
          {choroplethFeatures.regions.length + choroplethFeatures.countries.length > 0
            ? `Darker areas represent higher travel density.`
            : emptyMessage}
        </p>
      </div>
    </div>
  );
}