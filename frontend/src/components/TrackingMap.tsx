import { useEffect, useMemo, useState } from 'react';
import { CircleMarker, MapContainer, Popup, TileLayer, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { TrackingPoint } from '../types';

type TrackingMapProps = {
  species: string;
  points: TrackingPoint[];
  emptyMessage?: string;
};

type VisibleTrack = {
  identifier: string;
  color: string;
  latest: TrackingPoint;
};

type TimelineFrame = {
  sortOrder: number;
  label: string;
};

const SECONDS_PER_DAY = 24 * 3600;
const TRACKING_YEAR_SECONDS = 12 * 31 * SECONDS_PER_DAY;
const ACTIVE_WINDOW_SECONDS = 31 * SECONDS_PER_DAY;

const DAYS_PER_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

function fitTrackingBounds(points: TrackingPoint[], map: L.Map) {
  if (points.length === 0) {
    return;
  }

  const bounds = L.latLngBounds(points.map((point) => [point.latitude, point.longitude] as [number, number]));
  map.fitBounds(bounds, { padding: [40, 40], maxZoom: 6 });
}

function TrackingBounds({ points }: { points: TrackingPoint[] }) {
  const map = useMap();

  useEffect(() => {
    fitTrackingBounds(points, map);
  }, [map, points]);

  return null;
}

function colorForSpecies(species: string): string {
  const palette = ['#0f766e', '#2563eb', '#dc2626', '#7c3aed', '#f59e0b', '#0891b2', '#65a30d', '#db2777'];
  const total = species.split('').reduce((sum, character) => sum + character.charCodeAt(0), 0);
  return palette[total % palette.length];
}

function toSortOrder(month: number, day: number, hour = 0, minute = 0, second = 0): number {
  return (((month * 31) + day) * 24 + hour) * 3600 + minute * 60 + second;
}

function buildAnnualTimelineFrames(): TimelineFrame[] {
  const frames: TimelineFrame[] = [];
  for (let month = 1; month <= 12; month += 1) {
    const daysInMonth = DAYS_PER_MONTH[month - 1];
    for (let day = 1; day <= daysInMonth; day += 1) {
      const monthText = month.toString().padStart(2, '0');
      const dayText = day.toString().padStart(2, '0');
      frames.push({
        sortOrder: toSortOrder(month, day, 0, 0, 0),
        label: `${monthText}-${dayText} 00:00:00`,
      });
    }
  }
  return frames;
}

function elapsedSincePoint(currentSortOrder: number, pointSortOrder: number): number {
  if (currentSortOrder >= pointSortOrder) {
    return currentSortOrder - pointSortOrder;
  }
  return currentSortOrder + (TRACKING_YEAR_SECONDS - pointSortOrder);
}

export default function TrackingMap({ species, points, emptyMessage = 'No tracking points are available.' }: TrackingMapProps) {
  const TARGET_CYCLE_MS = 20_000;
  const MIN_FRAME_DELAY_MS = 16;
  const timeline = useMemo(() => buildAnnualTimelineFrames(), []);
  const [frameIndex, setFrameIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const speciesColor = useMemo(() => colorForSpecies(species), [species]);

  const groupedTracks = useMemo(() => {
    const grouped = new Map<string, TrackingPoint[]>();
    points.forEach((point) => {
      if (!grouped.has(point.identifier)) {
        grouped.set(point.identifier, []);
      }
      grouped.get(point.identifier)?.push(point);
    });

    grouped.forEach((trackPoints) => {
      trackPoints.sort((left, right) => left.sort_order - right.sort_order);
    });

    return grouped;
  }, [points]);

  const playbackConfig = useMemo(() => {
    const timelineLength = timeline.length;
    if (timelineLength <= 1) {
      return { frameStep: 1, frameDelayMs: TARGET_CYCLE_MS };
    }

    // Ensure a full yearly cycle finishes in ~20s, even for very dense timelines.
    const frameStep = Math.max(1, Math.ceil((timelineLength * MIN_FRAME_DELAY_MS) / TARGET_CYCLE_MS));
    const ticksPerCycle = Math.max(1, Math.ceil(timelineLength / frameStep));
    const frameDelayMs = Math.max(MIN_FRAME_DELAY_MS, Math.floor(TARGET_CYCLE_MS / ticksPerCycle));

    return { frameStep, frameDelayMs };
  }, [timeline.length]);

  useEffect(() => {
    setFrameIndex(0);
    setIsPlaying(points.length > 0 && timeline.length > 0);
  }, [points, timeline.length]);

  useEffect(() => {
    if (!isPlaying || timeline.length <= 1) {
      return;
    }

    const timer = window.setInterval(() => {
      setFrameIndex((current) => {
        return (current + playbackConfig.frameStep) % timeline.length;
      });
    }, playbackConfig.frameDelayMs);

    return () => window.clearInterval(timer);
  }, [isPlaying, playbackConfig.frameDelayMs, playbackConfig.frameStep, timeline.length]);

  const activeFrame = timeline[frameIndex] ?? null;
  const activeSortOrder = activeFrame?.sortOrder ?? null;

  const visibleTracks = useMemo(() => {
    if (activeSortOrder == null) {
      return [] as VisibleTrack[];
    }

    return Array.from(groupedTracks.entries())
      .map(([identifier, trackPoints]) => {
        if (trackPoints.length === 0) {
          return null;
        }

        let low = 0;
        let high = trackPoints.length - 1;
        let bestIndex = -1;
        while (low <= high) {
          const mid = Math.floor((low + high) / 2);
          if (trackPoints[mid].sort_order <= activeSortOrder) {
            bestIndex = mid;
            low = mid + 1;
          } else {
            high = mid - 1;
          }
        }

        const latest = bestIndex >= 0 ? trackPoints[bestIndex] : trackPoints[trackPoints.length - 1];
        const elapsed = elapsedSincePoint(activeSortOrder, latest.sort_order);
        if (elapsed > ACTIVE_WINDOW_SECONDS) {
          return null;
        }

        return {
          identifier,
          color: speciesColor,
          latest,
        };
      })
      .filter((track): track is VisibleTrack => track !== null);
  }, [activeSortOrder, groupedTracks, speciesColor]);

  const currentLabel = useMemo(() => {
    if (activeFrame == null) {
      return 'Waiting for tracking data';
    }
    return activeFrame.label;
  }, [activeFrame]);

  return (
    <div className="tracking-shell">
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
        <TrackingBounds points={points} />
        {visibleTracks.map((track) => (
          <CircleMarker
            key={`${track.identifier}-latest`}
            center={[track.latest.latitude, track.latest.longitude]}
            radius={5}
            pathOptions={{ color: '#ffffff', weight: 2, fillColor: track.color, fillOpacity: 1 }}
          >
            <Popup>
              <div className="density-popup">
                <strong>{track.identifier}</strong>
                <div>{track.latest.timestamp}</div>
                {track.latest.study_name && <div>{track.latest.study_name}</div>}
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
      <div className="tracking-panel">
        <div className="tracking-panel-header">
          <strong>Tracking Playback</strong>
          <button type="button" className="tracking-toggle" onClick={() => setIsPlaying((current) => !current)}>
            {isPlaying ? 'Pause' : 'Play'}
          </button>
        </div>
        <div className="tracking-progress">
          <span>{currentLabel}</span>
          <span>{timeline.length > 0 ? `Annual loop: ${frameIndex + 1}/${timeline.length}` : 'Annual loop: 0/0'}</span>
        </div>
        <input
          type="range"
          min={0}
          max={Math.max(timeline.length - 1, 0)}
          value={Math.min(frameIndex, Math.max(timeline.length - 1, 0))}
          onChange={(event) => {
            setFrameIndex(Number(event.target.value));
            setIsPlaying(false);
          }}
          disabled={timeline.length === 0}
        />
        <p className="density-scale-note">
          {points.length > 0
            ? 'Tracks are grouped by bird identifier and replayed as a repeating annual timeline (01-01 to 12-31, month-day-time order). Only individuals with data within one month of the current timestamp are shown.'
            : emptyMessage}
        </p>
      </div>
    </div>
  );
}
