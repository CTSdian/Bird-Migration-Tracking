import json
import urllib.request
import pandas as pd
import re
from pathlib import Path
from collections import defaultdict

# Load aggregated counts
from backend.data_loader import get_route_aggregated_counts

print("Loading aggregated counts...")
agg_counts = get_route_aggregated_counts(None)
print(f"Loaded: {len(agg_counts)} entries")

# Show first few entries
print("\nFirst 5 entries:")
for i, (key, count) in enumerate(list(agg_counts.items())[:5]):
    print(f"  {key}: {count}")

# Analyze structure of keys
sample_keys = list(agg_counts.keys())[:10]
print(f"\nSample keys structure: {sample_keys[:3]}")
