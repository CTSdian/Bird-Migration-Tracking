# Clustering Experiments on Bird Migration Routes

## Goal
Group migration routes into behaviorally meaningful types using unsupervised learning.

## Dataset and Unit of Analysis
- Source: `data.csv`
- Raw rows: 42,844 waypoint records
- Route-level samples used for clustering: 1,437 routes
- Route key: (`species`, `route_code`)

## Features (per route)
- `n_points`: number of waypoints in route
- `total_distance_km`: cumulative geodesic distance along route
- `straightness`: net displacement / total distance
- `mean_step_km`: average segment length
- `turn_mean_deg`, `turn_std_deg`: directional variability
- `duration_months`: coarse route time span from start/end month-year
- `intercontinental_flag`: majority flag from migration pattern labels

For clustering input, the model used:
- `n_points`, `log_total_dist`, `straightness`, `mean_step_km`, `turn_mean_deg`, `turn_std_deg`

## Methods
- K-means (`k=2..7`, `n_init=30`, `random_state=42`)
- Hierarchical agglomerative clustering (Ward linkage, `k=2..7`)

Evaluation metrics:
- Silhouette score (higher is better)
- Calinski-Harabasz score (higher is better)
- Davies-Bouldin score (lower is better)

## Model Selection Snapshot
Best silhouette by method during sweep (`k=2..7`):
- K-means: `k=5` (silhouette = `0.321`)
- Hierarchical: `k=2` (silhouette = `0.312`)

Interpretability-focused run with `k=3` also produced coherent behavioral groups and is useful for product design.

## Interpretable k=3 Results
### K-means (`k=3`, silhouette = `0.303`)
Cluster profile (means):
- Cluster A (794 routes):
  - mean distance about 6,432 km
  - straightness about 0.609
  - mean waypoints about 22.6
  - turn mean about 74.6 degrees
  - intercontinental ratio about 0.475
- Cluster B (266 routes):
  - mean distance about 20,728 km
  - straightness about 0.304
  - mean waypoints about 81.8
  - turn mean about 97.9 degrees
  - intercontinental ratio about 0.752
- Cluster C (377 routes):
  - mean distance about 2,773 km
  - straightness about 0.850
  - mean waypoints about 8.2
  - turn mean about 45.1 degrees
  - intercontinental ratio about 0.138

### Hierarchical (`k=3`, silhouette = `0.264`)
The same three behavior types appeared with slightly different boundaries:
- short and very straight routes
- long and highly sinuous routes
- medium routes with mixed behavior

## Suggested Behavioral Labels
Based on k=3 patterns:
1. Long-distance, flexible/complex
- Very long distance
- Lower straightness and high turning
- Mostly intercontinental

2. Medium-distance, mixed stability
- Intermediate distance and geometry
- Mixed intercontinental/intracontinental

3. Short-distance, stable/direct
- Short routes
- High straightness and low turning
- Mostly intracontinental

These align well with your intuition:
- long-distance and stable/flexible dimensions are both captured
- short and flexible/stable differences emerge clearly
- some routes form a high-variability cluster without a single clear directional pattern

## Practical Recommendation
- If the goal is pure compactness/separation, start with K-means `k=5`.
- If the goal is explainability in the UI, start with `k=3` labels:
  1. Long-distance flexible/complex
  2. Medium-distance mixed
  3. Short-distance stable/direct

## Reproducibility
Run:

```bash
.venv/Scripts/python.exe analysis/clustering_experiments.py
```

## Notes and Limitations
- Route order is approximated by `ID` sorting.
- Some species have multiple route trajectories mixed under a route code.
- Temporal precision is coarse (month-year only), so seasonality-driven clustering is limited.
- Next iteration can include trajectory embedding, DTW distance, or HDBSCAN for non-spherical clusters.
