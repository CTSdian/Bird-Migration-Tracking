import json
import urllib.request
import pandas as pd
import re
from pathlib import Path

# Load aggregated counts
from backend.data_loader import get_route_aggregated_counts

# Get aggregated counts
agg_counts = get_route_aggregated_counts(None)
print("Aggregated counts loaded:", len(agg_counts), "entries")

# Sample of aggregated counts
print("\nSample of aggregated counts:")
for i, (key, count) in enumerate(list(agg_counts.items())[:10]):
    print(f"  {key}: {count}")
    if i >= 4:
        break
