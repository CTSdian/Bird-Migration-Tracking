from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data.csv"
TRACKING_DATA_PATH = ROOT / "Bird_Tracking_Data"
STATIONARY_MIN_CONSECUTIVE_POINTS = 6
FALLBACK_DATA_PATHS = [
    ROOT / "bird_migration.csv",
    ROOT / "bird_migartion.csv",
]
REQUIRED_COLUMNS = {"id", "route_code", "species", "gps_xx", "gps_yy"}
PREDICTION_EXPERIMENT_SPECIES = ("Barn Swallow", "Osprey")

COUNTRY_ALIASES: Dict[str, str] = {
    "united states": "United States of America",
    "usa": "United States of America",
    "u s a": "United States of America",
    "us": "United States of America",
    "u s": "United States of America",
    "uk": "United Kingdom",
    "u k": "United Kingdom",
    "great britain": "United Kingdom",
    "england": "United Kingdom",
    "scotland": "United Kingdom",
    "wales": "United Kingdom",
    "northern ireland": "United Kingdom",
    "czech republic": "Czechia",
    "macedonia": "North Macedonia",
    "swaziland": "Eswatini",
    "palestina": "Palestine",
    "republic of serbia": "Serbia",
    "timor leste": "East Timor",
    "timor leste democratic republic": "East Timor",
    "timor leste dem rep": "East Timor",
    "cape verde": "Cabo Verde",
    "cote d ivoire": "Ivory Coast",
    "cote divoire": "Ivory Coast",
    "ivory coast": "Ivory Coast",
    "burma": "Myanmar",
    "persia": "Iran",
    "ussr": "Russia",
    "soviet union": "Russia",
    "zaire": "Democratic Republic of the Congo",
    "dr congo": "Democratic Republic of the Congo",
    "congo kinshasa": "Democratic Republic of the Congo",
    "democratic republic of congo": "Democratic Republic of the Congo",
    "democratic republic of the congo": "Democratic Republic of the Congo",
    "congo brazzaville": "Republic of the Congo",
    "republic of congo": "Republic of the Congo",
    "the gambia": "Gambia",
    "gambia the": "Gambia",
    "guinea bissau": "Guinea-Bissau",
    "sao tome and principe": "Sao Tome and Principe",
    "libyan arab jamahiriya": "Libya",
    "united republic of tanzania": "Tanzania",
    "tanzania united republic of": "Tanzania",
    "bolivia plurinational state of": "Bolivia",
    "venezuela bolivarian republic of": "Venezuela",
    "brasil": "Brazil",
    "argentine republic": "Argentina",
    "falkland islands": "Falkland Islands",
    "greenland denmark": "Greenland",
    # African countries and variations
    "djibouti": "Djibouti",
    "mauritius": "Mauritius",
    "seychelles": "Seychelles",
    "comoros": "Comoros",
    "cote d ivoire": "Ivory Coast",
    "cote divoire": "Ivory Coast",
    "ivory coast": "Ivory Coast",
    "cabo verde": "Cabo Verde",
    "south sudan": "South Sudan",
    "western sahara": "Western Sahara",
    "reunion": "Reunion",
    "mayotte": "Mayotte",
    "canary islands": "Spain",
    "madeira": "Portugal",
    "republic of cameroon": "Cameroon",
    "republic of gabon": "Gabon",
    "republic of equatorial guinea": "Equatorial Guinea",
    "central african republic": "Central African Republic",
    "republic of south sudan": "South Sudan",
    "republic of burundi": "Burundi",
    "republic of rwanda": "Rwanda",
    "republic of djibouti": "Djibouti",
    "republic of mauritius": "Mauritius",
    "somali republic": "Somalia",
    "united kingdom of tanzania": "Tanzania",
    "curacao": "Curacao",
}

PROVINCE_ALIASES: Dict[str, str] = {
    "nei mongol": "Inner Mongolia",
    "xizang": "Tibet",
    "primor ye": "Primorskiy Kray",
    "chukot": "Chukotka",
    "sakha": "Sakha Republic",
    "khabarovsk": "Khabarovskiy Kray",
    "alsace": "Grand Est",
    "champagne ardenne": "Grand Est",
    "lorraine": "Grand Est",
    "aquitaine": "Nouvelle-Aquitaine",
    "limousin": "Nouvelle-Aquitaine",
    "poitou charentes": "Nouvelle-Aquitaine",
    "auvergne": "Auvergne-Rhone-Alpes",
    "rhone alpes": "Auvergne-Rhone-Alpes",
    "basse normandie": "Normandie",
    "haute normandie": "Normandie",
    "franche comte": "Bourgogne-Franche-Comte",
    "bourgogne": "Bourgogne-Franche-Comte",
    "languedoc roussillon": "Occitanie",
    "midi pyrenees": "Occitanie",
    "nord pas de calais": "Hauts-de-France",
    "picardie": "Hauts-de-France",
    "chaouia ouardigha": "Casablanca-Settat",
    "doukkala abda": "Casablanca-Settat",
    "gharb chrarda beni hssen": "Fes-Meknes",
    "grand casablanca": "Casablanca-Settat",
    "guelmim es semara": "Guelmim-Oued Noun",
    "la youne boujdour sakia el hamra": "Laayoune-Sakia El Hamra",
    "marrakech tensift al haouz": "Marrakech-Safi",
    "meknes tafilalet": "Fes-Meknes",
    "rabat sale zemmour zaer": "Rabat-Sale-Kenitra",
    "souss massa draa": "Souss-Massa",
    "tadla azilal": "Beni Mellal-Khenifra",
    "tanger tetouan": "Tanger-Tetouan-Al Hoceima",
    "taza al hoceima taounate": "Tanger-Tetouan-Al Hoceima",
    "ben arous tunis sud": "Ben Arous",
    "nct of delhi": "Delhi",
    "d c": "District of Columbia",
    "county durham": "Durham",
    "michoacan": "Michoacan",
    "al qahirah": "Cairo",
    "al isma iliyah": "Ismailia",
    "as suways": "Suez",
    "cataluna": "Catalonia",
    "catalunaa": "Catalonia",
    "england": "England",
    "scotland": "Scotland",
    "wales": "Wales",
    "northern ireland": "Northern Ireland",
}


def _read_csv_with_fallback_encodings(path: Path) -> pd.DataFrame:
    encodings = ["utf-8", "utf-8-sig", "latin1"]
    last_error: Optional[Exception] = None

    for encoding in encodings:
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError as error:
            last_error = error

    if last_error is not None:
        raise last_error

    return pd.read_csv(path)


def _sort_time_components(month: int, day: int, hour: int, minute: int, second: int) -> int:
    return (((month * 31) + day) * 24 + hour) * 3600 + minute * 60 + second


def _read_tracking_csv(path: Path) -> pd.DataFrame:
    df = _read_csv_with_fallback_encodings(path)
    df.columns = [str(column).strip().lower() for column in df.columns]
    return df


def _get_tracking_identifier(row: pd.Series) -> Optional[str]:
    for column in ["individual-local-identifier", "tag-local-identifier", "event-id"]:
        value = row.get(column)
        if pd.notna(value) and str(value).strip():
            return str(value).strip()
    return None


def _get_tracking_timestamp_parts(value: object) -> Optional[Dict[str, object]]:
    if pd.isna(value):
        return None

    timestamp = pd.to_datetime(value, errors="coerce")
    if pd.isna(timestamp):
        return None

    month = int(timestamp.month)
    day = int(timestamp.day)
    hour = int(timestamp.hour)
    minute = int(timestamp.minute)
    second = int(timestamp.second)
    return {
        "year": int(timestamp.year),
        "timestamp": timestamp.strftime("%m-%d %H:%M:%S"),
        "month": month,
        "day": day,
        "hour": hour,
        "minute": minute,
        "second": second,
        "sort_order": _sort_time_components(month, day, hour, minute, second),
    }


def _make_tracking_individual_key(identifier: str, year: int) -> str:
    return f"{identifier} ({year})"


def _remove_stationary_points(track_points: List[Dict[str, object]], min_consecutive_points: int = STATIONARY_MIN_CONSECUTIVE_POINTS) -> List[Dict[str, object]]:
    if len(track_points) < min_consecutive_points:
        return track_points

    filtered: List[Dict[str, object]] = []
    index = 0
    total = len(track_points)
    while index < total:
        current = track_points[index]
        run_end = index + 1
        while run_end < total:
            candidate = track_points[run_end]
            if (
                float(candidate["latitude"]) == float(current["latitude"])
                and float(candidate["longitude"]) == float(current["longitude"])
            ):
                run_end += 1
                continue
            break

        run_length = run_end - index
        if run_length >= min_consecutive_points:
            filtered.append(current)
        else:
            filtered.extend(track_points[index:run_end])

        index = run_end

    return filtered


def _iter_species_csv_files(species_dir: Path) -> List[Path]:
    if not species_dir.exists() or not species_dir.is_dir():
        return []

    # Use recursive, case-insensitive discovery so newly added files are automatically included.
    return sorted(path for path in species_dir.rglob("*") if path.is_file() and path.suffix.lower() == ".csv")


def _tracking_data_signature() -> str:
    if not TRACKING_DATA_PATH.exists():
        return "missing"

    file_count = 0
    latest_mtime_ns = 0
    for path in TRACKING_DATA_PATH.rglob("*"):
        if not path.is_file() or path.suffix.lower() != ".csv":
            continue
        file_count += 1
        mtime_ns = path.stat().st_mtime_ns
        if mtime_ns > latest_mtime_ns:
            latest_mtime_ns = mtime_ns

    return f"{file_count}:{latest_mtime_ns}"


@lru_cache(maxsize=4)
def _get_tracking_species_list_cached(_signature: str) -> List[Dict[str, object]]:
    if not TRACKING_DATA_PATH.exists():
        return []

    summaries: List[Dict[str, object]] = []
    for species_dir in sorted(path for path in TRACKING_DATA_PATH.iterdir() if path.is_dir()):
        csv_files = _iter_species_csv_files(species_dir)

        summaries.append(
            {
                "species": species_dir.name,
                "csv_count": len(csv_files),
                # Keep this endpoint fast; detailed counts are served by /api/tracking/points and /api/tracking/report.
                "individual_count": 0,
                "point_count": 0,
                "removed_point_count": 0,
            }
        )

    return summaries


def get_tracking_species_list() -> List[Dict[str, object]]:
    return _get_tracking_species_list_cached(_tracking_data_signature())


@lru_cache(maxsize=128)
def _get_tracking_points_cached(species_name: str, _signature: str) -> Dict[str, object]:
    species_dir = TRACKING_DATA_PATH / species_name
    if not species_dir.exists() or not species_dir.is_dir():
        return {
            "species": species_name,
            "individual_count": 0,
            "point_count": 0,
            "removed_point_count": 0,
            "points": [],
        }

    identifiers = set()
    grouped_points: Dict[str, List[Dict[str, object]]] = {}

    for csv_file in _iter_species_csv_files(species_dir):
        df = _read_tracking_csv(csv_file)
        required = {"timestamp", "location-long", "location-lat"}
        if not required.issubset(df.columns):
            continue

        filtered = df.loc[df["location-long"].notna() & df["location-lat"].notna()].copy()
        if filtered.empty:
            continue

        filtered["location-long"] = pd.to_numeric(filtered["location-long"], errors="coerce")
        filtered["location-lat"] = pd.to_numeric(filtered["location-lat"], errors="coerce")
        filtered = filtered.loc[filtered["location-long"].notna() & filtered["location-lat"].notna()]

        timestamps = pd.to_datetime(filtered["timestamp"], errors="coerce")
        filtered = filtered.loc[timestamps.notna()].copy()
        timestamps = timestamps.loc[timestamps.notna()]
        if filtered.empty:
            continue

        identifier_series: Optional[pd.Series] = None
        for column in ["individual-local-identifier", "tag-local-identifier", "event-id"]:
            if column not in filtered.columns:
                continue
            values = filtered[column].astype(str).str.strip()
            values = values.where(filtered[column].notna() & (values != ""))
            identifier_series = values if identifier_series is None else identifier_series.fillna(values)

        if identifier_series is None:
            continue

        filtered = filtered.assign(_identifier_raw=identifier_series)
        filtered = filtered.loc[filtered["_identifier_raw"].notna()].copy()
        timestamps = timestamps.loc[filtered.index]
        if filtered.empty:
            continue

        years = timestamps.dt.year.astype(int)
        months = timestamps.dt.month.astype(int)
        days = timestamps.dt.day.astype(int)
        hours = timestamps.dt.hour.astype(int)
        minutes = timestamps.dt.minute.astype(int)
        seconds = timestamps.dt.second.astype(int)
        sort_orders = (((months * 31) + days) * 24 + hours) * 3600 + minutes * 60 + seconds
        timestamp_texts = timestamps.dt.strftime("%m-%d %H:%M:%S")
        individual_keys = filtered["_identifier_raw"].astype(str) + " (" + years.astype(str) + ")"
        study_names = (
            filtered["study-name"].astype(str).str.strip().where(filtered["study-name"].notna())
            if "study-name" in filtered.columns
            else pd.Series([None] * len(filtered), index=filtered.index)
        )

        for individual_key, timestamp_text, sort_order, lon, lat, study_name in zip(
            individual_keys.tolist(),
            timestamp_texts.tolist(),
            sort_orders.astype(int).tolist(),
            filtered["location-long"].astype(float).tolist(),
            filtered["location-lat"].astype(float).tolist(),
            study_names.tolist(),
        ):
            identifiers.add(individual_key)
            grouped_points.setdefault(individual_key, []).append(
                {
                    "identifier": individual_key,
                    "timestamp": timestamp_text,
                    "sort_order": int(sort_order),
                    "longitude": float(lon),
                    "latitude": float(lat),
                    "study_name": study_name,
                }
            )

    filtered_points: List[Dict[str, object]] = []
    for track_points in grouped_points.values():
        track_points.sort(key=lambda item: (item["sort_order"], item["timestamp"]))
        filtered_points.extend(_remove_stationary_points(track_points))

    filtered_points.sort(key=lambda item: (item["sort_order"], item["identifier"], item["timestamp"]))
    original_count = sum(len(track_points) for track_points in grouped_points.values())
    removed_point_count = original_count - len(filtered_points)

    return {
        "species": species_name,
        "individual_count": len(identifiers),
        "point_count": len(filtered_points),
        "removed_point_count": removed_point_count,
        "points": filtered_points,
    }


def get_tracking_points(species_name: str) -> Dict[str, object]:
    return _get_tracking_points_cached(species_name, _tracking_data_signature())


@lru_cache(maxsize=4)
def _get_tracking_report_cached(signature: str) -> Dict[str, object]:
    if not TRACKING_DATA_PATH.exists():
        return {
            "totals": {
                "species_count": 0,
                "csv_count": 0,
                "individual_count": 0,
                "point_count": 0,
                "removed_point_count": 0,
            },
            "species": [],
        }

    species_rows: List[Dict[str, object]] = []
    for species_dir in sorted(path for path in TRACKING_DATA_PATH.iterdir() if path.is_dir()):
        species_name = species_dir.name
        csv_count = len(_iter_species_csv_files(species_dir))
        data = _get_tracking_points_cached(species_name, signature)
        species_rows.append(
            {
                "species": species_name,
                "csv_count": csv_count,
                "individual_count": int(data.get("individual_count", 0)),
                "point_count": int(data.get("point_count", 0)),
                "removed_point_count": int(data.get("removed_point_count", 0)),
            }
        )

    totals = {
        "species_count": len(species_rows),
        "csv_count": int(sum(int(row.get("csv_count", 0)) for row in species_rows)),
        "individual_count": int(sum(int(row.get("individual_count", 0)) for row in species_rows)),
        "point_count": int(sum(int(row.get("point_count", 0)) for row in species_rows)),
        "removed_point_count": int(sum(int(row.get("removed_point_count", 0)) for row in species_rows)),
    }

    species = sorted(
        [
            {
                "species": str(row.get("species", "")),
                "csv_count": int(row.get("csv_count", 0)),
                "individual_count": int(row.get("individual_count", 0)),
                "point_count": int(row.get("point_count", 0)),
                "removed_point_count": int(row.get("removed_point_count", 0)),
            }
            for row in species_rows
        ],
        key=lambda row: row["species"],
    )

    return {
        "totals": totals,
        "species": species,
    }


def get_tracking_report() -> Dict[str, object]:
    return _get_tracking_report_cached(_tracking_data_signature())


def normalize_geo_name(value: object) -> str:
    if not isinstance(value, str):
        return ""

    # Fix common encoding corruptions (UTF-8 mojibake from Windows-1252 → UTF-8 issues)
    text = value.strip()
    encoding_fixes = {
        "¨ª": "í",   # í (from mojibake)
        "¨¢": "á",   # á
        "¨±": "ñ",   # ñ
        "¨©": "é",   # é
        "¨®": "ò",   # ò
        "¨¤": "à",   # à
        "¨§": "ç",   # ç
        "¨¯": "ô",   # ô
        "¨³": "ó",   # ó
        "¨¹": "ù",   # ù
        "¨º": "ú",   # ú
        "¨°": "ö",   # ö
        "¨¨": "è",   # è
        "¨«": "ê",   # ê
        "¨¼": "ü",   # ü
        "¨¶": "æ",   # æ
        "?": "",     # Remove question mark placeholders
    }
    for broken, fixed in encoding_fixes.items():
        text = text.replace(broken, fixed)

    return (
        text
        .lower()
        .replace("&", " and ")
        .encode("ascii", "ignore")
        .decode("ascii")
    )


def _normalize_token_string(value: str) -> str:
    return " ".join("".join(ch if ch.isalnum() else " " for ch in value).split())


def standardize_country_name(value: object) -> Optional[str]:
    normalized = _normalize_token_string(normalize_geo_name(value))
    if not normalized:
        return None
    return COUNTRY_ALIASES.get(normalized, str(value).strip())


def standardize_province_name(value: object) -> Optional[str]:
    normalized = _normalize_token_string(normalize_geo_name(value))
    if not normalized:
        return None
    return PROVINCE_ALIASES.get(normalized, str(value).strip())

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
    candidate_paths = [DATA_PATH, *FALLBACK_DATA_PATHS]
    last_error: Optional[Exception] = None

    for path in candidate_paths:
        if not path.exists():
            continue

        try:
            df = _read_csv_with_fallback_encodings(path)
            df = normalize_columns(df)
            missing = REQUIRED_COLUMNS - set(df.columns)
            if missing:
                continue

            df = df.loc[df["gps_xx"].notna() & df["gps_yy"].notna()]
            return df
        except Exception as error:
            last_error = error

    if last_error is not None:
        raise RuntimeError(f"Unable to load a valid migration dataset: {last_error}") from last_error

    searched = ", ".join(str(path.name) for path in candidate_paths)
    raise FileNotFoundError(f"No valid migration dataset found. Checked: {searched}")


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


def get_route_points(species_name: Optional[str] = None) -> List[Dict]:
    df = load_data()
    if species_name and species_name.strip():
        filtered = df[df["species"].str.lower() == species_name.strip().lower()]
    else:
        filtered = df

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
            clean_record = _sanitize_record(record)
            clean_record["sequence_index"] = idx
            all_records.append(clean_record)

    # Sort all records by route_code then sequence_index; missing route_code goes last.
    all_records.sort(
        key=lambda x: (
            x["route_code"] is None,
            x["route_code"] if x["route_code"] is not None else 0,
            x["sequence_index"],
        )
    )
    return all_records


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius_km = 6371.0
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2.0) ** 2
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    return float(earth_radius_km * c)


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return float(numerator / denominator)


def _feature_definitions() -> List[Dict[str, str]]:
    return [
        {
            "feature": "point_count",
            "plain_language": "Number of valid tracking points for one individual-year track.",
            "calculation": "count(valid points after coordinate/timestamp cleaning)",
        },
        {
            "feature": "mean_latitude",
            "plain_language": "Average latitude of the individual track.",
            "calculation": "mean(latitude_i)",
        },
        {
            "feature": "mean_longitude",
            "plain_language": "Average longitude of the individual track.",
            "calculation": "mean(longitude_i)",
        },
        {
            "feature": "range_latitude",
            "plain_language": "Total north-south span of the track.",
            "calculation": "max(latitude_i) - min(latitude_i)",
        },
        {
            "feature": "range_longitude",
            "plain_language": "Total east-west span of the track.",
            "calculation": "max(longitude_i) - min(longitude_i)",
        },
        {
            "feature": "total_distance_km",
            "plain_language": "Total travel distance along the observed path.",
            "calculation": "sum(Haversine(point_{i-1}, point_i)) for i=2..n",
        },
        {
            "feature": "mean_step_distance_km",
            "plain_language": "Average distance between consecutive observations.",
            "calculation": "total_distance_km / (point_count - 1)",
        },
        {
            "feature": "daily_distance_km",
            "plain_language": "Distance normalized by observed time span (flight capability proxy).",
            "calculation": "total_distance_km / max((max(sort_order)-min(sort_order))/86400, 1)",
        },
        {
            "feature": "winter_mean_latitude",
            "plain_language": "Typical winter latitude.",
            "calculation": "mean(latitude_i where month in {12,1,2})",
        },
        {
            "feature": "summer_mean_latitude",
            "plain_language": "Typical summer latitude.",
            "calculation": "mean(latitude_i where month in {6,7,8})",
        },
        {
            "feature": "seasonal_latitude_shift",
            "plain_language": "Seasonal migration shift in latitude.",
            "calculation": "summer_mean_latitude - winter_mean_latitude",
        },
    ]


def _travel_distance_methodology_text() -> str:
    return (
        "Travel distance is computed from consecutive GPS points using the Haversine formula. "
        "For points (lat1, lon1) and (lat2, lon2), with Earth radius R=6371 km: "
        "d = 2R * atan2(sqrt(a), sqrt(1-a)), where a = sin^2((lat2-lat1)/2) + cos(lat1)*cos(lat2)*sin^2((lon2-lon1)/2). "
        "Total distance is the sum of all step distances in chronological order."
    )


def _season_assignment_methodology_text() -> str:
    return (
        "Seasons are assigned from month parsed from each timestamp string (MM-DD HH:MM:SS). "
        "Winter = {12, 1, 2}, Summer = {6, 7, 8}. "
        "If an individual has no points in a target season, we fall back to the track-wide mean latitude for that season-specific feature."
    )


def _evaluation_protocol_text() -> str:
    return (
        "Evaluation uses 5-fold stratified cross-validation with shuffle=True and random_state=42. "
        "Samples are not grouped by raw bird identifier during validation; each individual-year sample is split directly into folds. "
        "Methods are compared using out-of-fold Accuracy, Balanced Accuracy, Precision, Recall, F1, ROC/AUC, and confusion matrix. "
        "Best method is selected by highest F1, then Accuracy as tie-breaker."
    )


def _cross_validated_method_result(
    name: str,
    category: str,
    x_all: np.ndarray,
    y_all: np.ndarray,
    splitter: StratifiedKFold,
    notes: str,
) -> Dict[str, Any]:
    y_pred = np.zeros_like(y_all)
    y_score = np.zeros(y_all.shape[0], dtype=float)

    for train_index, test_index in splitter.split(x_all, y_all):
        x_train = x_all[train_index]
        x_test = x_all[test_index]
        y_train = y_all[train_index]

        if name == "Cosine Prototype":
            model = _CosinePrototypeClassifier().fit(x_train, y_train)
            y_pred[test_index] = model.predict(x_test)
            y_score[test_index] = model.predict_score(x_test, positive_label=1)
        elif name == "Logistic Regression":
            scaler = StandardScaler()
            x_train_scaled = scaler.fit_transform(x_train)
            x_test_scaled = scaler.transform(x_test)
            model = LogisticRegression(random_state=42, max_iter=1200)
            model.fit(x_train_scaled, y_train)
            y_pred[test_index] = model.predict(x_test_scaled)
            y_score[test_index] = model.predict_proba(x_test_scaled)[:, 1]
        elif name == "Random Forest":
            model = RandomForestClassifier(
                n_estimators=350,
                random_state=42,
                min_samples_leaf=2,
                class_weight="balanced",
            )
            model.fit(x_train, y_train)
            y_pred[test_index] = model.predict(x_test)
            y_score[test_index] = model.predict_proba(x_test)[:, 1]
        else:
            raise ValueError(f"Unsupported method: {name}")

    return _evaluate_binary_method(
        name=name,
        category=category,
        y_test=y_all,
        y_pred=y_pred,
        y_score=y_score,
        notes=notes,
    )


def _extract_tracking_features(points: List[Dict[str, object]]) -> Optional[Dict[str, float]]:
    if len(points) < 2:
        return None

    sorted_points = sorted(points, key=lambda item: (int(item["sort_order"]), str(item["timestamp"])))
    latitudes = np.array([float(item["latitude"]) for item in sorted_points], dtype=float)
    longitudes = np.array([float(item["longitude"]) for item in sorted_points], dtype=float)
    sort_orders = np.array([int(item["sort_order"]) for item in sorted_points], dtype=int)

    months: List[int] = []
    for item in sorted_points:
        timestamp = str(item.get("timestamp") or "")
        try:
            months.append(int(timestamp[:2]))
        except (TypeError, ValueError):
            months.append(1)

    total_distance_km = 0.0
    for index in range(1, len(sorted_points)):
        total_distance_km += _haversine_km(
            float(sorted_points[index - 1]["latitude"]),
            float(sorted_points[index - 1]["longitude"]),
            float(sorted_points[index]["latitude"]),
            float(sorted_points[index]["longitude"]),
        )

    span_seconds = float(max(0, int(sort_orders.max()) - int(sort_orders.min())))
    span_days = max(span_seconds / 86400.0, 1.0)

    winter_mask = np.array([month in {12, 1, 2} for month in months], dtype=bool)
    summer_mask = np.array([month in {6, 7, 8} for month in months], dtype=bool)
    winter_mean_lat = float(np.mean(latitudes[winter_mask])) if np.any(winter_mask) else float(np.mean(latitudes))
    summer_mean_lat = float(np.mean(latitudes[summer_mask])) if np.any(summer_mask) else float(np.mean(latitudes))

    feature_values = {
        "point_count": float(len(sorted_points)),
        "mean_latitude": float(np.mean(latitudes)),
        "mean_longitude": float(np.mean(longitudes)),
        "range_latitude": float(np.max(latitudes) - np.min(latitudes)),
        "range_longitude": float(np.max(longitudes) - np.min(longitudes)),
        "total_distance_km": total_distance_km,
        "mean_step_distance_km": _safe_ratio(total_distance_km, len(sorted_points) - 1),
        "daily_distance_km": _safe_ratio(total_distance_km, span_days),
        "winter_mean_latitude": winter_mean_lat,
        "summer_mean_latitude": summer_mean_lat,
        "seasonal_latitude_shift": summer_mean_lat - winter_mean_lat,
    }

    return feature_values


def _build_species_discrimination_dataset(species_names: Tuple[str, str]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for species in species_names:
        response = get_tracking_points(species)
        grouped: Dict[str, List[Dict[str, object]]] = {}
        for point in response.get("points", []):
            identifier = str(point.get("identifier") or "")
            if not identifier:
                continue
            grouped.setdefault(identifier, []).append(point)

        for identifier, individual_points in grouped.items():
            features = _extract_tracking_features(individual_points)
            if not features:
                continue
            rows.append({
                "species": species,
                "identifier": identifier,
                **features,
            })

    return pd.DataFrame(rows)


class _CosinePrototypeClassifier:
    def __init__(self) -> None:
        self._prototypes: Dict[int, np.ndarray] = {}

    def fit(self, x_train: np.ndarray, y_train: np.ndarray) -> "_CosinePrototypeClassifier":
        for label in np.unique(y_train):
            prototype = x_train[y_train == label].mean(axis=0)
            norm = float(np.linalg.norm(prototype))
            self._prototypes[int(label)] = prototype / norm if norm > 0 else prototype
        return self

    def predict(self, x_data: np.ndarray) -> np.ndarray:
        labels = sorted(self._prototypes.keys())
        predictions: List[int] = []
        for row in x_data:
            row_norm = float(np.linalg.norm(row))
            unit_row = row / row_norm if row_norm > 0 else row
            similarities = [float(np.dot(unit_row, self._prototypes[label])) for label in labels]
            predictions.append(labels[int(np.argmax(similarities))])
        return np.array(predictions, dtype=int)

    def predict_score(self, x_data: np.ndarray, positive_label: int) -> np.ndarray:
        labels = sorted(self._prototypes.keys())
        if len(labels) != 2:
            return np.zeros(x_data.shape[0], dtype=float)
        negative_label = labels[0] if labels[0] != positive_label else labels[1]
        scores: List[float] = []
        for row in x_data:
            row_norm = float(np.linalg.norm(row))
            unit_row = row / row_norm if row_norm > 0 else row
            pos_sim = float(np.dot(unit_row, self._prototypes[positive_label]))
            neg_sim = float(np.dot(unit_row, self._prototypes[negative_label]))
            scores.append(float((pos_sim - neg_sim + 1.0) / 2.0))
        return np.array(scores, dtype=float)


def _evaluate_binary_method(
    name: str,
    category: str,
    y_test: np.ndarray,
    y_pred: np.ndarray,
    y_score: Optional[np.ndarray] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred, labels=[0, 1]).ravel()
    roc_auc: Optional[float] = None
    if y_score is not None:
        try:
            roc_auc = float(roc_auc_score(y_test, y_score))
        except ValueError:
            roc_auc = None

    return {
        "name": name,
        "category": category,
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "roc_auc": roc_auc,
        "confusion_matrix": {
            "true_negative": int(tn),
            "false_positive": int(fp),
            "false_negative": int(fn),
            "true_positive": int(tp),
        },
        "notes": notes,
    }


@lru_cache(maxsize=4)
def _get_species_discrimination_report_cached(signature: str) -> Dict[str, Any]:
    del signature
    species_pair = PREDICTION_EXPERIMENT_SPECIES
    dataset = _build_species_discrimination_dataset(species_pair)

    if dataset.empty:
        return {
            "title": "Barn Swallow vs Osprey Tracking Discrimination",
            "species_used": list(species_pair),
            "dataset": {
                "sample_count": 0,
                "feature_count": 0,
                "species_counts": {},
            },
            "methods": [],
            "best_method": "N/A",
            "top_features": [],
            "feature_definitions": _feature_definitions(),
            "travel_distance_method": _travel_distance_methodology_text(),
            "season_assignment_method": _season_assignment_methodology_text(),
            "evaluation_protocol": _evaluation_protocol_text(),
            "species_profiles": [],
            "report": "No usable tracking samples were found for the requested species.",
        }

    feature_names = [column for column in dataset.columns if column not in {"species", "identifier"}]
    x_all = dataset[feature_names].to_numpy(dtype=float)
    y_all = (dataset["species"] == species_pair[1]).astype(int).to_numpy(dtype=int)

    species_counts = {
        species_pair[0]: int((dataset["species"] == species_pair[0]).sum()),
        species_pair[1]: int((dataset["species"] == species_pair[1]).sum()),
    }

    if len(np.unique(y_all)) < 2 or len(y_all) < 10:
        return {
            "title": "Barn Swallow vs Osprey Tracking Discrimination",
            "species_used": list(species_pair),
            "dataset": {
                "sample_count": int(len(dataset)),
                "feature_count": int(len(feature_names)),
                "species_counts": species_counts,
            },
            "methods": [],
            "best_method": "N/A",
            "top_features": [],
            "feature_definitions": _feature_definitions(),
            "travel_distance_method": _travel_distance_methodology_text(),
            "season_assignment_method": _season_assignment_methodology_text(),
            "evaluation_protocol": _evaluation_protocol_text(),
            "species_profiles": [],
            "report": "Dataset is too small or contains only one class after preprocessing.",
        }

    min_class_count = int(min(species_counts.values())) if species_counts else 0
    if min_class_count < 5:
        return {
            "title": "Barn Swallow vs Osprey Tracking Discrimination",
            "species_used": list(species_pair),
            "dataset": {
                "sample_count": int(len(dataset)),
                "feature_count": int(len(feature_names)),
                "species_counts": species_counts,
            },
            "methods": [],
            "best_method": "N/A",
            "top_features": [],
            "feature_definitions": _feature_definitions(),
            "travel_distance_method": _travel_distance_methodology_text(),
            "season_assignment_method": _season_assignment_methodology_text(),
            "evaluation_protocol": _evaluation_protocol_text(),
            "species_profiles": [],
            "report": "At least 5 samples per species are required for 5-fold validation.",
        }

    splitter = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    methods: List[Dict[str, Any]] = []
    methods.append(
        _cross_validated_method_result(
            name="Cosine Prototype",
            category="Simple",
            x_all=x_all,
            y_all=y_all,
            splitter=splitter,
            notes=(
                "Training step: compute one prototype vector (class mean) per species, then normalize to unit length. "
                "Prediction step: normalize the new individual's feature vector and compute cosine similarity to both prototypes; choose the higher similarity. "
                "Score shown for ROC AUC is a normalized similarity gap between the two species."
            ),
        )
    )
    methods.append(
        _cross_validated_method_result(
            name="Logistic Regression",
            category="Machine Learning",
            x_all=x_all,
            y_all=y_all,
            splitter=splitter,
            notes=(
                "Features are standardized first (z-score) using training-set mean and standard deviation. "
                "Model learns a weighted linear combination z = w·x + b and converts it to probability with sigmoid(z). "
                "Prediction uses threshold 0.5: probability >= 0.5 predicts Osprey, otherwise Barn Swallow."
            ),
        )
    )
    methods.append(
        _cross_validated_method_result(
            name="Random Forest",
            category="Machine Learning",
            x_all=x_all,
            y_all=y_all,
            splitter=splitter,
            notes=(
                "Model trains many decision trees on bootstrapped samples with feature sub-sampling at each split. "
                "Each tree votes for one species based on nonlinear rules (for example, seasonal latitude shift + travel-distance interactions). "
                "Final prediction is majority vote across trees; probability is the fraction of trees voting Osprey."
            ),
        )
    )

    methods.sort(key=lambda row: (row["f1"], row["accuracy"]), reverse=True)
    best_method = methods[0]["name"] if methods else "N/A"

    class_means = dataset.groupby("species")[feature_names].mean(numeric_only=True)
    if species_pair[0] in class_means.index and species_pair[1] in class_means.index:
        mean_diff = (class_means.loc[species_pair[1]] - class_means.loc[species_pair[0]]).abs()
        top_features = [
            {
                "feature": str(name),
                "score": float(score),
            }
            for name, score in mean_diff.sort_values(ascending=False).head(8).items()
        ]
    else:
        top_features = []

    profiles: List[Dict[str, Any]] = []
    for species in species_pair:
        subset = dataset.loc[dataset["species"] == species]
        if subset.empty:
            continue
        profiles.append(
            {
                "species": species,
                "individual_count": int(len(subset)),
                "mean_daily_distance_km": float(subset["daily_distance_km"].mean()),
                "mean_latitude": float(subset["mean_latitude"].mean()),
                "mean_longitude": float(subset["mean_longitude"].mean()),
            }
        )

    report_lines = [
        "This experiment distinguishes Barn Swallow vs Osprey using per-individual tracking features.",
        f"Dataset: {len(dataset)} individual tracks with {len(feature_names)} engineered features.",
        f"Best method under 5-fold stratified validation: {best_method}.",
        "Validation does not group samples by raw bird identifier; individual-year samples are split directly across folds.",
        "Simple prototype methods are included as baselines to compare against ML models.",
        "Feature engineering combines movement-capability proxies and seasonal latitude behavior.",
    ]

    if top_features:
        top_text = ", ".join(f"{item['feature']} ({item['score']:.3f})" for item in top_features[:5])
        report_lines.append(f"Most discriminative features: {top_text}.")

    return {
        "title": "Barn Swallow vs Osprey Tracking Discrimination",
        "species_used": list(species_pair),
        "dataset": {
            "sample_count": int(len(dataset)),
            "feature_count": int(len(feature_names)),
            "species_counts": species_counts,
        },
        "methods": methods,
        "best_method": best_method,
        "top_features": top_features,
        "feature_definitions": _feature_definitions(),
        "travel_distance_method": _travel_distance_methodology_text(),
        "season_assignment_method": _season_assignment_methodology_text(),
        "evaluation_protocol": _evaluation_protocol_text(),
        "species_profiles": profiles,
        "report": "\n".join(report_lines),
    }


def get_species_discrimination_report() -> Dict[str, Any]:
    return _get_species_discrimination_report_cached(_tracking_data_signature())


def get_prediction_route(species_name: str) -> List[Dict]:
    route = get_route_points(species_name)
    return [
        {**point, "predicted": True, "sequence_index": idx}
        for idx, point in enumerate(route)
    ]


@lru_cache(maxsize=256)
def get_route_aggregated_counts(species_name: Optional[str] = None) -> Dict:
    points = get_route_points(species_name)
    if not points:
        return {
            "counts": [],
            "summary": {
                "node_count": 0,
                "country_count": 0,
                "state_count": 0,
                "origin_count": 0,
                "destination_count": 0,
                "avg_migration_months": 0.0,
            },
        }

    area_counts: Dict[tuple[str, Optional[str]], int] = {}
    countries = set()
    states = set()
    origins = set()
    destinations = set()
    month_total = 0.0
    month_count = 0

    for point in points:
        country = standardize_country_name(point.get("country"))
        province = standardize_province_name(point.get("province"))
        if country:
            countries.add(country)
            key = (country, province if province else None)
            area_counts[key] = area_counts.get(key, 0) + 1
        if province:
            states.add(province)

        node = str(point.get("node") or "").lower()
        if "origin" in node:
            origins.add((country, province))
        if "destination" in node:
            destinations.add((country, province))

        start_month = point.get("start_month")
        estimated_month = point.get("estimated_month")
        if isinstance(start_month, (int, float)) and isinstance(estimated_month, (int, float)):
            diff = int(estimated_month) - int(start_month)
            diff = diff % 12
            month_total += diff
            month_count += 1

    counts = [
        {
            "country": country,
            "province": province,
            "count": count,
        }
        for (country, province), count in area_counts.items()
        if country
    ]

    counts.sort(key=lambda item: item["count"], reverse=True)

    return {
        "counts": counts,
        "summary": {
            "node_count": len(points),
            "country_count": len(countries),
            "state_count": len(states),
            "origin_count": len(origins),
            "destination_count": len(destinations),
            "avg_migration_months": (month_total / month_count) if month_count > 0 else 0.0,
        },
    }


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
