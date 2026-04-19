import json
from backend.data_loader import get_route_aggregated_counts

# Load aggregated counts
agg_counts = get_route_aggregated_counts(None)
print(f"Loaded {len(agg_counts)} entries")
for k, v in agg_counts.items():
    print(f"\nKey: {k}")
    print(f"Type: {type(v)}")
    if isinstance(v, dict):
        print(f"Dict entries: {len(v)}")
        for i, (sk, sv) in enumerate(list(v.items())[:5]):
            print(f"  {sk}: {sv}")
    elif isinstance(v, list):
        print(f"List length: {len(v)}")
        print(f"First item: {v[0] if v else None}")
