from functools import lru_cache
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data.csv"

COLUMN_MAP = {
    "ID": "id",
    "Migratory route codes": "route_code",
    "Migration nodes": "node",
    "Bird orders": "order",
    "Bird families": "family",
    "Bird genera": "genus",
    "English Name": "common_name",
    "Bird species": "species",
    "Species Authority": "species_authority",
    "Migration type": "migration_type",
    "The IUCN Red List (2023)": "iucn_red_list",
    "Migration start year": "start_year",
    "Migration start month": "start_month",
    "Migration end year": "end_year",
    "Migration end month": "end_month",
    "Sensor types": "sensor_types",
    "Continents (1 = North America, 2 = South America, 3 = Europe, 4 = Africa, 5 = Asia, 6 = Oceania)": "continent",
    "Countries": "country",
    "Provinces": "province",
    "GPS_xx": "gps_xx",
    "GPS_yy": "gps_yy",
    "Migration patterns (1 = Intercontinental migration, 2 = Intracontinental migration)": "migration_pattern",
    "Migration routes (1 = North America→North America, 2 = South America→South America, 3 = Europe→Europe, 4 = Africa→Africa, 5 = Asia→Asia, 6 = Oceania→Oceania, 7 = Europe→Africa, 8 = Africa→Europe, 9 = North America→South America, 10 = South America→North America, 11 = Europe→Asia, 12 = Asia→Europe, 13 = Asia→Africa, 14 = Africa→Asia, 15 = Europe→North America, 16 = North America→Europe, 17 = Asia→Oceania, 18 = Oceania→Asia, 19 = North America→Oceania, 20 = Oceania→North America, 21 = North America→Asia)": "migration_route",    "migration_routes_(1_=_north_america↔north_america,_2_=_south_america↔south_america,_3_=_europe↔europe,_4_=_africa↔africa,_5_=_asia↔asia,_6_=_oceania↔oceania,_7_=_europe→africa,_8_=_africa→europe,_9_=_north_america→south_america,_10_=_south_america→north_america,_11_=_europe→asia,_12_=_asia→europe,_13_=_asia→africa,_14_=_africa→asia,_15_=_europe→north_america,_16_=_north_america→europe,_17_=_asia→oceania,_18_=_oceania→asia,_19_=_north_america→oceania,_20_=_oceania→north_america,_21_=_north_america→asia)": "migration_route",    "References": "references",
    "Publish time": "publish_time",
    "DOI": "doi",
}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed = df.rename(columns={k: v for k, v in COLUMN_MAP.items() if k in df.columns})
    for column in list(renamed.columns):
        if "migration routes" in column.lower():
            renamed = renamed.rename(columns={column: "migration_route"})
    normalized = {
        column: column.strip().lower().replace(" ", "_")
        for column in renamed.columns
    }
    renamed = renamed.rename(columns=normalized)
    return renamed


def _estimate_point_time(points: List[Dict], start_year: int, start_month: int, end_year: int, end_month: int) -> List[Dict]:
    if not points:
        return points

    # Calculate total months span
    total_months = (end_year - start_year) * 12 + (end_month - start_month)
    if total_months <= 0:
        # If no span, use start time for all
        for point in points:
            point["estimated_year"] = start_year
            point["estimated_month"] = start_month
        return points

    n = len(points)
    for i, point in enumerate(points):
        if n == 1:
            months_elapsed = 0
        else:
            months_elapsed = int(i * total_months / (n - 1))

        est_year = start_year + months_elapsed // 12
        est_month = start_month + months_elapsed % 12
        if est_month > 12:
            est_month -= 12
            est_year += 1

        point["estimated_year"] = est_year
        point["estimated_month"] = est_month

    return points


@lru_cache()
def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Data file not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    df = normalize_columns(df)
    df = df.loc[df["gps_xx"].notna() & df["gps_yy"].notna()]
    return df


GROUP_DEFINITIONS = [
    {
        "key": "all",
        "label": "All species",
        "description": "Show every migration path in the dataset.",
    },
    {
        "key": "intercontinental",
        "label": "Intercontinental migration",
        "description": "Routes that cross continents.",
        "pattern_values": [1],
    },
    {
        "key": "intracontinental",
        "label": "Intracontinental migration",
        "description": "Routes that stay within a single continent.",
        "pattern_values": [2],
    },
    {
        "key": "within_north_america",
        "label": "Within North America",
        "description": "Routes that start and end within North America.",
        "route_values": [1],
    },
    {
        "key": "within_south_america",
        "label": "Within South America",
        "description": "Routes that start and end within South America.",
        "route_values": [2],
    },
    {
        "key": "within_europe",
        "label": "Within Europe",
        "description": "Routes that start and end within Europe.",
        "route_values": [3],
    },
    {
        "key": "within_africa",
        "label": "Within Africa",
        "description": "Routes that start and end within Africa.",
        "route_values": [4],
    },
    {
        "key": "within_asia",
        "label": "Within Asia",
        "description": "Routes that start and end within Asia.",
        "route_values": [5],
    },
    {
        "key": "within_oceania",
        "label": "Within Oceania",
        "description": "Routes that start and end within Oceania.",
        "route_values": [6],
    },
    {
        "key": "europe_africa",
        "label": "Europe ↔ Africa",
        "description": "Routes connecting Europe and Africa.",
        "route_values": [7, 8],
    },
    {
        "key": "north_south_america",
        "label": "North America ↔ South America",
        "description": "Routes connecting North and South America.",
        "route_values": [9, 10],
    },
    {
        "key": "europe_asia",
        "label": "Europe ↔ Asia",
        "description": "Routes connecting Europe and Asia.",
        "route_values": [11, 12],
    },
    {
        "key": "asia_africa",
        "label": "Asia ↔ Africa",
        "description": "Routes connecting Asia and Africa.",
        "route_values": [13, 14],
    },
    {
        "key": "north_america_europe",
        "label": "North America ↔ Europe",
        "description": "Routes connecting North America and Europe.",
        "route_values": [15, 16],
    },
    {
        "key": "asia_oceania",
        "label": "Asia ↔ Oceania",
        "description": "Routes connecting Asia and Oceania.",
        "route_values": [17, 18],
    },
    {
        "key": "north_america_oceania",
        "label": "North America ↔ Oceania",
        "description": "Routes connecting North America and Oceania.",
        "route_values": [19, 20],
    },
    {
        "key": "north_america_asia",
        "label": "North America → Asia",
        "description": "Routes connecting North America and Asia.",
        "route_values": [21],
    },
]


def _row_matches_group(row: pd.Series, group_key: str) -> bool:
    if group_key == "all":
        return True

    group = next((item for item in GROUP_DEFINITIONS if item["key"] == group_key), None)
    if group is None:
        return False

    if "pattern_values" in group:
        if int(row["migration_pattern"]) not in group["pattern_values"]:
            return False

    if "route_values" in group:
        if int(row["migration_route"]) not in group["route_values"]:
            return False

    return True


def _group_filter(df: pd.DataFrame, group_key: str) -> pd.Series:
    if group_key == "all":
        return pd.Series([True] * len(df), index=df.index)

    group = next((item for item in GROUP_DEFINITIONS if item["key"] == group_key), None)
    if group is None:
        return pd.Series([False] * len(df), index=df.index)

    mask = pd.Series([True] * len(df), index=df.index)
    if "pattern_values" in group:
        mask &= df["migration_pattern"].isin(group["pattern_values"])
    if "route_values" in group:
        mask &= df["migration_route"].isin(group["route_values"])
    return mask


import calendar
import json
import urllib.error
import urllib.parse
import urllib.request


@lru_cache()
def get_species_list() -> List[Dict[str, str]]:
    df = load_data()
    unique_species = (
        df[["species", "common_name", "order"]]
        .drop_duplicates(subset=["species"])
        .sort_values(by=["common_name", "species"])
    )
    return [
        {
            "species": str(row["species"]),
            "common_name": str(row["common_name"]),
            "order": str(row["order"]),
        }
        for _, row in unique_species.iterrows()
    ]


def _temperature_query_url(latitude: float, longitude: float, year: int, month: int) -> str:
    last_day = calendar.monthrange(year, month)[1]
    start_date = f"{year:04d}-{month:02d}-01"
    end_date = f"{year:04d}-{month:02d}-{last_day:02d}"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_mean",
        "timezone": "UTC",
    }
    return "https://archive-api.open-meteo.com/v1/archive?" + urllib.parse.urlencode(params)


@lru_cache()
def get_temperature_for_location(latitude: float, longitude: float, year: int, month: int) -> float | None:
    try:
        url = _temperature_query_url(latitude, longitude, year, month)
        with urllib.request.urlopen(url, timeout=20) as response:
            data = json.load(response)
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError):
        return None

    daily = data.get("daily", {})
    values = daily.get("temperature_2m_mean") or []
    if not values:
        return None

    temperatures = [float(value) for value in values if value is not None]
    if not temperatures:
        return None

    return sum(temperatures) / len(temperatures)


def get_route_points(species_name: str) -> List[Dict]:
    df = load_data()
    filtered = df[df["species"].str.lower() == species_name.strip().lower()]
    if filtered.empty:
        return []

    all_records = []
    for route_code, group in filtered.groupby("route_code"):
        # Get migration start/end for this route
        start_year = int(group["start_year"].iloc[0])
        start_month = int(group["start_month"].iloc[0])
        end_year = int(group["end_year"].iloc[0])
        end_month = int(group["end_month"].iloc[0])

        records = group.sort_values(by="id").to_dict(orient="records")
        records = _estimate_point_time(records, start_year, start_month, end_year, end_month)
        for idx, record in enumerate(records):
            record["sequence_index"] = idx
        all_records.extend(records)

    # Sort all records by route_code then sequence_index
    all_records.sort(key=lambda x: (x["route_code"], x["sequence_index"]))
    return all_records


def get_prediction_route(species_name: str) -> List[Dict]:
    route = get_route_points(species_name)
    return [
        {**point, "predicted": True, "sequence_index": idx}
        for idx, point in enumerate(route)
    ]


def _haversine_km(lat1, lon1, lat2, lon2):
    radius_km = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * radius_km * np.arcsin(np.sqrt(a))


def _bearing_deg(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    y = np.sin(dlon) * np.cos(lat2)
    x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dlon)
    return (np.degrees(np.arctan2(y, x)) + 360) % 360


def _sanitize_record(record: Dict) -> Dict:
    clean = {}
    for key, value in record.items():
        clean[key] = None if pd.isna(value) else value
    return clean


@lru_cache()
def get_clustered_route_points() -> List[Dict]:
    df = load_data()
    route_rows = []

    for (species, route_code), group in df.groupby(["species", "route_code"], dropna=True):
        group = group.sort_values("id")
        if len(group) < 3:
            continue

        lat = group["gps_yy"].to_numpy(float)
        lon = group["gps_xx"].to_numpy(float)
        step = _haversine_km(lat[:-1], lon[:-1], lat[1:], lon[1:])
        total_distance = float(np.nansum(step))
        displacement = float(_haversine_km(lat[0], lon[0], lat[-1], lon[-1]))
        straightness = float(displacement / (total_distance + 1e-9))

        bearings = _bearing_deg(lat[:-1], lon[:-1], lat[1:], lon[1:])
        turns = np.abs((np.diff(bearings) + 180) % 360 - 180)

        route_rows.append(
            {
                "species": species,
                "route_code": int(route_code),
                "n_points": len(group),
                "log_total_dist": np.log1p(total_distance),
                "straightness": straightness,
                "mean_step_km": float(np.nanmean(step)),
                "turn_mean_deg": float(np.nanmean(turns)) if len(turns) > 0 else 0.0,
                "turn_std_deg": float(np.nanstd(turns)) if len(turns) > 0 else 0.0,
            }
        )

    route_df = pd.DataFrame(route_rows)
    if route_df.empty:
        return []

    feature_columns = [
        "n_points",
        "log_total_dist",
        "straightness",
        "mean_step_km",
        "turn_mean_deg",
        "turn_std_deg",
    ]
    x_scaled = StandardScaler().fit_transform(route_df[feature_columns])
    labels = KMeans(n_clusters=3, n_init=30, random_state=42).fit_predict(x_scaled)

    label_map: Dict[tuple[str, int], int] = {}
    for idx, row in route_df.iterrows():
        label_map[(str(row["species"]), int(row["route_code"]))] = int(labels[idx]) + 1

    clustered_records: List[Dict] = []
    for (species, route_code), group in df.groupby(["species", "route_code"], dropna=True):
        key = (str(species), int(route_code))
        cluster_id = label_map.get(key)
        if cluster_id is None:
            continue

        points = group.sort_values("id").to_dict(orient="records")
        route_key = f"{species}::{int(route_code)}"
        for idx, record in enumerate(points):
            record = _sanitize_record(record)
            record["route_key"] = route_key
            record["cluster_id"] = cluster_id
            record["sequence_index"] = idx
            clustered_records.append(record)

    clustered_records.sort(key=lambda x: (x["cluster_id"], x["route_key"], x["sequence_index"]))
    return clustered_records
