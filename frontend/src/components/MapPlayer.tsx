import { useEffect, useMemo, useState } from 'react';
import { Circle, MapContainer, Marker, Polyline, Popup, TileLayer, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { fetchTemperature } from '../services/api';
import type { MigrationPoint, RouteGroup } from '../types';

const DefaultIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.5/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.5/dist/images/marker-shadow.png',
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  iconSize: [25, 41],
  shadowSize: [41, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

function safePoint(point: MigrationPoint): [number, number] {
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

function getTemperatureColor(temperature: number): string {
  const value = Math.max(-30, Math.min(45, temperature));
  const ratio = (value + 30) / 75;
  const red = Math.round(255 * ratio);
  const blue = Math.round(255 * (1 - ratio));
  const green = Math.round(80 + 80 * (1 - Math.abs(ratio - 0.5) * 2));
  return `rgb(${red}, ${green}, ${blue})`;
}

interface MapPlayerProps {
  routeGroups: RouteGroup[];
  activeRouteGroup: RouteGroup | null;
  baseColor: string;
  onRouteSelect?: (routeId: number) => void;
}

function RouteFocus({ routeGroup }: { routeGroup: RouteGroup | null }) {
  const map = useMap();

  useEffect(() => {
    if (!routeGroup) return;
    const coords = routeGroup.points
      .map(safePoint)
      .filter(([lat, lon]) => lat !== 0 && lon !== 0);
    if (coords.length === 0) return;
    const bounds = L.latLngBounds(coords);
    map.fitBounds(bounds, { padding: [50, 50], maxZoom: 7 });
  }, [routeGroup, map]);

  return null;
}

export default function MapPlayer({ routeGroups, activeRouteGroup, baseColor, onRouteSelect }: MapPlayerProps) {
  const [activeIndex, setActiveIndex] = useState(0);
  const [temperature, setTemperature] = useState<number | null>(null);
  const [temperatureLoading, setTemperatureLoading] = useState(false);
  const [temperatureError, setTemperatureError] = useState<string | null>(null);

  const activePoints = activeRouteGroup?.points ?? [];
  const activePoint = activePoints[activeIndex] ?? null;

  useEffect(() => {
    setActiveIndex(0);
  }, [activeRouteGroup]);

  useEffect(() => {
    if (!activePoint || activePoint.gps_xx == null || activePoint.gps_yy == null || activePoint.estimated_year == null || activePoint.estimated_month == null) {
      setTemperature(null);
      setTemperatureError(null);
      setTemperatureLoading(false);
      return;
    }

    setTemperatureLoading(true);
    setTemperatureError(null);

    fetchTemperature(activePoint.gps_yy, activePoint.gps_xx, activePoint.estimated_year, activePoint.estimated_month)
      .then((result) => setTemperature(result.temperature))
      .catch((err) => {
        setTemperature(null);
        setTemperatureError(err.message);
      })
      .finally(() => setTemperatureLoading(false));
  }, [activePoint]);

  const center = useMemo(() => {
    const allPoints = routeGroups.flatMap((group) => group.points.map(safePoint));
    return allPoints.length > 0 ? allPoints[0] : [20, 0];
  }, [routeGroups]);

  const pinIcon = useMemo(
    () =>
      L.divIcon({
        className: 'custom-pin-icon',
        html: `<span style="background:${baseColor}"></span>`,
        iconSize: [28, 40],
        iconAnchor: [14, 40],
        popupAnchor: [0, -36],
      }),
    [baseColor]
  );

  const routePolylines = useMemo(
    () =>
      routeGroups.map((group) => {
        const coords = group.points.map(safePoint).filter(([lat, lon]) => lat !== 0 && lon !== 0);
        return {
          routeId: group.routeId,
          routeCode: group.routeCode,
          positions: coords.length > 2 ? smoothCoordinates(coords, 2) : coords,
          isActive: group.routeId === activeRouteGroup?.routeId,
          color: baseColor,
        };
      }),
    [routeGroups, activeRouteGroup, baseColor]
  );

  const mapZoom = routePolylines.some((poly) => poly.positions.length > 0) ? 4 : 2;

  return (
    <div className="map-player">
      <MapContainer center={center} zoom={mapZoom} minZoom={3} scrollWheelZoom={true} className="map-container">
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap contributors"
        />
        <RouteFocus routeGroup={activeRouteGroup} />
        {temperature != null && activePoint && activePoint.gps_xx != null && activePoint.gps_yy != null && (
          <>
            {[100000, 200000, 320000].map((radius, index) => (
              <Circle
                key={radius}
                center={safePoint(activePoint)}
                radius={radius}
                pathOptions={{
                  color: getTemperatureColor(temperature),
                  fillColor: getTemperatureColor(temperature),
                  fillOpacity: 0.12 - index * 0.03,
                  weight: 0,
                }}
              />
            ))}
          </>
        )}
        {routePolylines.map((poly) => (
          <Polyline
            key={poly.routeId}
            positions={poly.positions}
            eventHandlers={{
              click: () => onRouteSelect?.(poly.routeId),
            }}
            pathOptions={{
              color: poly.color,
              weight: poly.isActive ? 5 : 3,
              opacity: poly.isActive ? 0.95 : 0.65,
              smoothFactor: 1.0,
              interactive: true,
            }}
          />
        ))}
        {activePoint && activePoint.gps_xx != null && activePoint.gps_yy != null && (
          <Marker position={safePoint(activePoint)} icon={pinIcon}>
            <Popup>
              <div>
                <strong>{activePoint.node ?? 'Route point'}</strong>
                <div>{activePoint.country ?? ''}</div>
                <div>
                  {activePoint.gps_yy?.toFixed(4)}, {activePoint.gps_xx?.toFixed(4)}
                </div>
              </div>
            </Popup>
          </Marker>
        )}
      </MapContainer>

      {activePoints.length > 0 ? (
        <div className="timeline-panel">
          <div className="timeline-header">
            <strong>Route {activeRouteGroup?.routeId}</strong>
            <span>{activeRouteGroup?.origin?.node ?? 'Unknown'} → {activeRouteGroup?.destination?.node ?? 'Unknown'}</span>
          </div>
          <label htmlFor="position-slider">Timeline position</label>
          <input
            id="position-slider"
            type="range"
            min={0}
            max={activePoints.length - 1}
            value={activeIndex}
            onChange={(event) => setActiveIndex(Number(event.target.value))}
          />
          <div className="timeline-meta">
            <span>Step {activeIndex + 1} / {activePoints.length}</span>
            <span>
              {activePoint?.start_year ?? '-'} / {activePoint?.start_month ?? '-'}
            </span>
          </div>
          <div className="temperature-panel">
            {temperatureLoading ? (
              'Loading estimated temperature…'
            ) : temperature != null ? (
              `Estimated temperature: ${temperature.toFixed(1)}°C`
            ) : temperatureError ? (
              temperatureError
            ) : (
              'Estimated temperature data is not available for this waypoint.'
            )}
          </div>
        </div>
      ) : (
        <div className="timeline-empty">Select a route to inspect its timeline.</div>
      )}
    </div>
  );
}
