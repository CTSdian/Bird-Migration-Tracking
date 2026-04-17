import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score, silhouette_score
from sklearn.preprocessing import StandardScaler

DATA_PATH = "data.csv"


def haversine_km(lat1, lon1, lat2, lon2):
    radius_km = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * radius_km * np.arcsin(np.sqrt(a))


def bearing_deg(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    y = np.sin(dlon) * np.cos(lat2)
    x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dlon)
    return (np.degrees(np.arctan2(y, x)) + 360) % 360


def load_and_prepare_points(path: str) -> pd.DataFrame:
    raw = pd.read_csv(path)
    column_map = {
        "ID": "id",
        "Migratory route codes": "route_code",
        "Bird species": "species",
        "Migration start year": "start_year",
        "Migration start month": "start_month",
        "Migration end year": "end_year",
        "Migration end month": "end_month",
        "GPS_xx": "lon",
        "GPS_yy": "lat",
        "Migration patterns (1 = Intercontinental migration, 2 = Intracontinental migration)": "migration_pattern",
    }
    points = raw.rename(columns={k: v for k, v in column_map.items() if k in raw.columns})
    points = points[points["lat"].notna() & points["lon"].notna()].copy()
    return points


def build_route_features(points: pd.DataFrame) -> pd.DataFrame:
    rows = []
    grouped = points.groupby(["species", "route_code"], dropna=True)

    for (species, route_code), group in grouped:
        group = group.sort_values("id")
        if len(group) < 3:
            continue

        lat = group["lat"].to_numpy(float)
        lon = group["lon"].to_numpy(float)
        step = haversine_km(lat[:-1], lon[:-1], lat[1:], lon[1:])

        total_distance = float(np.nansum(step))
        displacement = float(haversine_km(lat[0], lon[0], lat[-1], lon[-1]))
        straightness = float(displacement / (total_distance + 1e-9))

        bearings = bearing_deg(lat[:-1], lon[:-1], lat[1:], lon[1:])
        turns = np.abs((np.diff(bearings) + 180) % 360 - 180)

        sy = group["start_year"].ffill().bfill().iloc[0] if group["start_year"].notna().any() else np.nan
        sm = group["start_month"].ffill().bfill().iloc[0] if group["start_month"].notna().any() else np.nan
        ey = group["end_year"].ffill().bfill().iloc[-1] if group["end_year"].notna().any() else np.nan
        em = group["end_month"].ffill().bfill().iloc[-1] if group["end_month"].notna().any() else np.nan
        duration = (ey * 12 + em) - (sy * 12 + sm) if np.isfinite(sy) and np.isfinite(sm) and np.isfinite(ey) and np.isfinite(em) else np.nan

        rows.append(
            {
                "species": species,
                "route_code": int(route_code),
                "n_points": len(group),
                "total_distance_km": total_distance,
                "log_total_dist": np.log1p(total_distance),
                "displacement_km": displacement,
                "straightness": straightness,
                "mean_step_km": float(np.nanmean(step)),
                "turn_mean_deg": float(np.nanmean(turns)) if len(turns) > 0 else 0.0,
                "turn_std_deg": float(np.nanstd(turns)) if len(turns) > 0 else 0.0,
                "duration_months": float(duration) if np.isfinite(duration) else np.nan,
                "intercontinental_flag": int((group["migration_pattern"] == 1).mean() >= 0.5) if group["migration_pattern"].notna().any() else np.nan,
            }
        )

    routes = pd.DataFrame(rows).replace([np.inf, -np.inf], np.nan)
    routes = routes.dropna(subset=["log_total_dist", "straightness", "mean_step_km", "turn_mean_deg", "turn_std_deg"])
    return routes


def evaluate_models(x_scaled: np.ndarray) -> pd.DataFrame:
    rows = []
    for k in range(2, 8):
        km = KMeans(n_clusters=k, n_init=30, random_state=42)
        labels_km = km.fit_predict(x_scaled)
        rows.append(
            {
                "method": "kmeans",
                "k": k,
                "silhouette": silhouette_score(x_scaled, labels_km),
                "calinski_harabasz": calinski_harabasz_score(x_scaled, labels_km),
                "davies_bouldin": davies_bouldin_score(x_scaled, labels_km),
            }
        )

        hc = AgglomerativeClustering(n_clusters=k, linkage="ward")
        labels_hc = hc.fit_predict(x_scaled)
        rows.append(
            {
                "method": "hierarchical",
                "k": k,
                "silhouette": silhouette_score(x_scaled, labels_hc),
                "calinski_harabasz": calinski_harabasz_score(x_scaled, labels_hc),
                "davies_bouldin": davies_bouldin_score(x_scaled, labels_hc),
            }
        )

    return pd.DataFrame(rows)


def summarize_clusters(routes: pd.DataFrame, labels: np.ndarray) -> pd.DataFrame:
    frame = routes.copy()
    frame["cluster"] = labels
    summary = frame.groupby("cluster").agg(
        routes=("species", "size"),
        mean_total_km=("total_distance_km", "mean"),
        mean_straightness=("straightness", "mean"),
        mean_n_points=("n_points", "mean"),
        mean_turn_deg=("turn_mean_deg", "mean"),
        mean_duration_months=("duration_months", "mean"),
        intercontinental_ratio=("intercontinental_flag", "mean"),
    )
    return summary.round(3)


def run():
    points = load_and_prepare_points(DATA_PATH)
    routes = build_route_features(points)

    feature_columns = [
        "n_points",
        "log_total_dist",
        "straightness",
        "mean_step_km",
        "turn_mean_deg",
        "turn_std_deg",
    ]
    x_scaled = StandardScaler().fit_transform(routes[feature_columns])

    metrics = evaluate_models(x_scaled)
    print("Route samples:", len(routes))
    print("\nMetrics by method and k:")
    print(metrics.sort_values(["method", "k"]).to_string(index=False))

    # Interpretability-focused run with k=3 for both methods.
    for method in ["kmeans", "hierarchical"]:
        if method == "kmeans":
            model = KMeans(n_clusters=3, n_init=30, random_state=42)
        else:
            model = AgglomerativeClustering(n_clusters=3, linkage="ward")

        labels = model.fit_predict(x_scaled)
        sil = silhouette_score(x_scaled, labels)
        print(f"\n{method} k=3 silhouette={sil:.3f}")
        print("cluster sizes:", pd.Series(labels).value_counts().sort_index().to_dict())
        print(summarize_clusters(routes, labels).to_string())


if __name__ == "__main__":
    run()
